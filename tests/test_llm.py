import json

import httpx
import pytest

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
    """Fake de httpx.stream: `responses` es [(status, body), ...] por intento."""
    n = {"count": 0}

    def _stream(method, url, **kwargs):
        i = min(n["count"], len(responses) - 1)
        n["count"] += 1
        if calls is not None:
            calls.append({"url": url, "kwargs": kwargs})
        status, body = responses[i]
        if isinstance(status, Exception):
            raise status
        resp = httpx.Response(
            status,
            text=body if isinstance(body, str) else json.dumps(body),
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
