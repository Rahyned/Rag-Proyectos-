import json

import httpx
import pytest

from app import config
from app.services import llm

SSE_OK = (
    'data: {"choices":[{"delta":{"content":"Restaurá desde "}}]}\n\n'
    'data: {"choices":[{"delta":{"content":"Archivo > Backup."}}]}\n\n'
    'data: [DONE]\n\n'
)


class _Ctx:
    def __init__(self, resp: httpx.Response) -> None:
        self._resp = resp

    def __enter__(self) -> httpx.Response:
        return self._resp

    def __exit__(self, *exc) -> bool:
        return False


def make_stream(responses, calls=None):
    """Fake de httpx.stream: `responses` es [(status, body[, headers]), ...]
    por intento."""
    n = {"count": 0}

    def _stream(method, url, **kwargs):
        i = min(n["count"], len(responses) - 1)
        n["count"] += 1
        if calls is not None:
            calls.append({"url": url, "kwargs": kwargs})
        entry = responses[i]
        status, body = entry[0], entry[1]
        headers = entry[2] if len(entry) > 2 else None
        if isinstance(status, Exception):
            raise status
        resp = httpx.Response(
            status,
            text=body if isinstance(body, str) else json.dumps(body),
            headers=headers,
            request=httpx.Request(method, url),
        )
        return _Ctx(resp)

    _stream.calls = n
    return _stream


def _env(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.setenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")
    monkeypatch.setenv("LLM_MODEL", "qwen/qwen3.8-27b")
    monkeypatch.setenv("LLM_TIMEOUT", "45")


HITS = [{"title": "Manual STELLA", "page": 7, "text": "Archivo > Backup."}]


def test_stream_ok(monkeypatch):
    _env(monkeypatch)
    calls = []
    monkeypatch.setattr(llm.httpx, "stream", make_stream([(200, SSE_OK)], calls))
    out = "".join(llm.stream_answer("¿Cómo restauro?", HITS))
    assert out == "Restaurá desde Archivo > Backup."
    assert len(calls) == 1
    assert calls[0]["url"] == "https://api.groq.com/openai/v1/chat/completions"
    assert calls[0]["kwargs"]["headers"]["Authorization"] == "Bearer test-key"
    body = calls[0]["kwargs"]["json"]
    assert body["stream"] is True
    assert body["model"] == "qwen/qwen3.8-27b"
    assert body["messages"][0]["role"] == "system"
    assert "[Manual STELLA pág. 7]" in body["messages"][1]["content"]


def test_retry_on_503_then_ok(monkeypatch):
    _env(monkeypatch)
    monkeypatch.setattr(llm.time, "sleep", lambda _s: None)
    calls = []
    responses = [
        (503, {"error": {"message": "overloaded"}}),
        (200, SSE_OK),
    ]
    monkeypatch.setattr(llm.httpx, "stream", make_stream(responses, calls))
    out = "".join(llm.stream_answer("¿Cómo restauro?", HITS))
    assert out.startswith("Restaurá desde")
    assert len(calls) == 2


def test_401_no_retry(monkeypatch):
    _env(monkeypatch)
    calls = []
    responses = [(401, {"error": {"message": "invalid key"}})]
    monkeypatch.setattr(llm.httpx, "stream", make_stream(responses, calls))
    with pytest.raises(llm.LLMError, match="HTTP 401"):
        "".join(llm.stream_answer("hola", HITS))
    assert len(calls) == 1


def test_network_error_retries(monkeypatch):
    _env(monkeypatch)
    monkeypatch.setattr(llm.time, "sleep", lambda _s: None)
    calls = []
    responses = [
        (httpx.ConnectError("boom"), ()),
        (200, SSE_OK),
    ]
    monkeypatch.setattr(llm.httpx, "stream", make_stream(responses, calls))
    out = "".join(llm.stream_answer("hola", HITS))
    assert out.startswith("Restaurá")
    assert len(calls) == 2


def test_missing_key(monkeypatch):
    _env(monkeypatch)
    monkeypatch.setenv("LLM_API_KEY", "")
    calls = []
    monkeypatch.setattr(llm.httpx, "stream", make_stream([(200, SSE_OK)], calls))
    with pytest.raises(llm.LLMError, match="no configurada"):
        "".join(llm.stream_answer("hola", HITS))
    assert len(calls) == 0


def test_empty_answer(monkeypatch):
    _env(monkeypatch)
    calls = []
    responses = [(200, "data: [DONE]\n\n")]
    monkeypatch.setattr(llm.httpx, "stream", make_stream(responses, calls))
    with pytest.raises(llm.LLMError, match="vacía"):
        "".join(llm.stream_answer("hola", HITS))
    assert len(calls) == 1


def test_429_reintenta_respetando_retry_after(monkeypatch):
    _env(monkeypatch)
    sleeps = []
    monkeypatch.setattr(llm.time, "sleep", lambda s: sleeps.append(s))
    calls = []
    responses = [
        (429, {"error": {"message": "rate limited"}},
         {"retry-after": "2"}),
        (200, SSE_OK),
    ]
    monkeypatch.setattr(llm.httpx, "stream", make_stream(responses, calls))
    out = "".join(llm.stream_answer("hola", HITS))
    assert out.startswith("Restaurá")
    assert len(calls) == 2
    assert sleeps and abs(sleeps[0] - 2) < 0.01


def test_429_espera_larga_no_reintenta(monkeypatch):
    _env(monkeypatch)
    calls = []
    responses = [
        (429, {"error": {"message": "rate limited"}},
         {"retry-after": "30"}),
    ]
    monkeypatch.setattr(llm.httpx, "stream", make_stream(responses, calls))
    with pytest.raises(llm.LLMError) as excinfo:
        "".join(llm.stream_answer("hola", HITS))
    assert excinfo.value.reason == "rate_limited"
    assert len(calls) == 1


def test_circuito_429_no_llama_al_proveedor(monkeypatch):
    _env(monkeypatch)
    for _ in range(3):
        llm.ratelimit.note_groq_429()
    calls = []
    monkeypatch.setattr(llm.httpx, "stream", make_stream([(200, SSE_OK)], calls))
    with pytest.raises(llm.LLMError) as excinfo:
        "".join(llm.stream_answer("hola", HITS))
    assert excinfo.value.reason == "rate_limited"
    assert len(calls) == 0
    # El circuito corta antes de reservar cupo: no se incrementa el presupuesto.
    assert llm.ratelimit._budget == {}


def test_missing_key_reason(monkeypatch):
    _env(monkeypatch)
    monkeypatch.setenv("LLM_API_KEY", "")
    with pytest.raises(llm.LLMError) as excinfo:
        "".join(llm.stream_answer("hola", HITS))
    assert excinfo.value.reason == "no_key"


def test_presupuesto_agotado_no_llama_al_proveedor(monkeypatch):
    _env(monkeypatch)
    monkeypatch.setenv("LLM_DAILY_BUDGET", "1")
    calls = []
    monkeypatch.setattr(llm.httpx, "stream", make_stream([(200, SSE_OK)], calls))
    assert "".join(llm.stream_answer("hola", HITS)).startswith("Restaurá")
    with pytest.raises(llm.LLMError) as excinfo:
        "".join(llm.stream_answer("hola", HITS))
    assert excinfo.value.reason == "rate_limited"
    assert len(calls) == 1


def test_sin_key_no_gasta_presupuesto(monkeypatch):
    _env(monkeypatch)
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("LLM_DAILY_BUDGET", "1")
    with pytest.raises(llm.LLMError) as excinfo:
        "".join(llm.stream_answer("hola", HITS))
    assert excinfo.value.reason == "no_key"
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    calls = []
    monkeypatch.setattr(llm.httpx, "stream", make_stream([(200, SSE_OK)], calls))
    assert "".join(llm.stream_answer("hola", HITS)).startswith("Restaurá")
    assert len(calls) == 1


def test_presupuesto_redis_agotado_no_llama(monkeypatch):
    _env(monkeypatch)
    monkeypatch.setenv("LLM_DAILY_BUDGET", "300")
    monkeypatch.setenv("UPSTASH_REDIS_REST_URL", "https://fake.upstash.io")
    monkeypatch.setenv("UPSTASH_REDIS_REST_TOKEN", "token")
    posts = []

    def _post(url, json=None, **_k):
        posts.append(json)
        if json[0][0] == "DECR":
            payload = [{"result": 300}]
        else:
            payload = [{"result": 301}, {"result": 1}]
        return httpx.Response(
            200, json=payload, request=httpx.Request("POST", url),
        )

    monkeypatch.setattr(llm.ratelimit.httpx, "post", _post)
    calls = []
    monkeypatch.setattr(llm.httpx, "stream", make_stream([(200, SSE_OK)], calls))
    with pytest.raises(llm.LLMError) as excinfo:
        "".join(llm.stream_answer("hola", HITS))
    assert excinfo.value.reason == "rate_limited"
    assert calls == []
    assert posts[0][0][0] == "INCR"
    assert posts[0][0][1].startswith("llm:budget:")
    assert posts[0][1] == ["EXPIRE", posts[0][0][1], 2 * 24 * 60 * 60]
    assert posts[1][0][0] == "DECR"


def test_presupuesto_redis_falla_usa_memoria(monkeypatch):
    _env(monkeypatch)
    monkeypatch.setenv("LLM_DAILY_BUDGET", "1")
    monkeypatch.setenv("UPSTASH_REDIS_REST_URL", "https://fake.upstash.io")
    monkeypatch.setenv("UPSTASH_REDIS_REST_TOKEN", "token")

    def _post(*_a, **_k):
        raise httpx.ConnectError("down")

    monkeypatch.setattr(llm.ratelimit.httpx, "post", _post)
    calls = []
    monkeypatch.setattr(llm.httpx, "stream", make_stream([(200, SSE_OK)], calls))
    assert "".join(llm.stream_answer("hola", HITS)).startswith("Restaurá")
    with pytest.raises(llm.LLMError) as excinfo:
        "".join(llm.stream_answer("hola", HITS))
    assert excinfo.value.reason == "rate_limited"
    assert len(calls) == 1


def test_budget_vacio_o_invalido_usa_default(monkeypatch):
    monkeypatch.delenv("LLM_DAILY_BUDGET", raising=False)
    assert config.llm_daily_budget() == 300
    monkeypatch.setenv("LLM_DAILY_BUDGET", "")
    assert config.llm_daily_budget() == 300
    monkeypatch.setenv("LLM_DAILY_BUDGET", "no")
    assert config.llm_daily_budget() == 300
    monkeypatch.setenv("LLM_DAILY_BUDGET", "0")
    assert config.llm_daily_budget() == 0
    monkeypatch.setenv("LLM_DAILY_BUDGET", "-4")
    assert config.llm_daily_budget() == 300


def test_timeout_invalido_usa_default(monkeypatch):
    monkeypatch.setenv("LLM_TIMEOUT", "45s")
    assert config.llm_timeout() == 45.0
    monkeypatch.setenv("LLM_TIMEOUT", "-3")
    assert config.llm_timeout() == 45.0


def test_timeout_de_red_reason_timeout(monkeypatch):
    _env(monkeypatch)
    monkeypatch.setattr(llm.time, "sleep", lambda _s: None)
    calls = []
    responses = [
        (httpx.ReadTimeout("slow"), ()),
        (httpx.ReadTimeout("slow"), ()),
        (httpx.ReadTimeout("slow"), ()),
    ]
    monkeypatch.setattr(llm.httpx, "stream", make_stream(responses, calls))
    with pytest.raises(llm.LLMError) as excinfo:
        "".join(llm.stream_answer("hola", HITS))
    assert excinfo.value.reason == "timeout"
    assert len(calls) == 3
