"""Rate limit: IP, Redis opcional y desalojo sin reset global. Sin red."""

import httpx
import pytest
from fastapi import HTTPException
from starlette.requests import Request

from app import ratelimit


def _request(headers: dict[str, str] | None = None, host: str = "8.8.8.8") -> Request:
    raw = [(k.lower().encode(), v.encode()) for k, v in (headers or {}).items()]
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "POST",
        "scheme": "http",
        "path": "/api/chat",
        "raw_path": b"/api/chat",
        "query_string": b"",
        "headers": raw,
        "client": (host, 1234),
        "server": ("test", 80),
    }
    return Request(scope)


def _redis_ok(payload):
    def _post(url, json=None, headers=None, timeout=None):
        _post.calls.append({"url": url, "json": json, "headers": headers})
        return httpx.Response(
            200,
            json=payload,
            request=httpx.Request("POST", url),
        )

    _post.calls = []
    return _post


def _activar_redis(monkeypatch):
    monkeypatch.setenv("UPSTASH_REDIS_REST_URL", "https://fake.upstash.io")
    monkeypatch.setenv("UPSTASH_REDIS_REST_TOKEN", "token-secreto")


@pytest.mark.parametrize("headers,esperado", [
    ({
        "x-vercel-forwarded-for": "3.3.3.3",
        "x-real-ip": "2.2.2.2",
        "x-forwarded-for": "1.1.1.1",
    }, "3.3.3.3"),
    ({"x-real-ip": "2.2.2.2", "x-forwarded-for": "1.1.1.1"}, "2.2.2.2"),
    ({"x-forwarded-for": "1.1.1.1, 9.9.9.9"}, "1.1.1.1"),
    ({}, "8.8.8.8"),
])
def test_prioridad_de_headers_de_ip(headers, esperado):
    assert ratelimit.client_ip(_request(headers)) == esperado


def test_redis_incr_y_expire_cuando_hay_env(monkeypatch):
    _activar_redis(monkeypatch)
    momento = 1_700_000_100
    monkeypatch.setattr(ratelimit.time, "time", lambda: momento)
    post = _redis_ok([{"result": 1}, {"result": 1}])
    monkeypatch.setattr(ratelimit.httpx, "post", post)
    ratelimit.check(_request({"x-real-ip": "203.0.113.9"}), 10, "chat")
    [llamada] = post.calls
    assert llamada["url"] == "https://fake.upstash.io/pipeline"
    assert llamada["headers"]["Authorization"] == "Bearer token-secreto"
    ventana = int(momento // ratelimit.WINDOW_SECONDS)
    assert llamada["json"][0] == ["INCR", f"rl:chat:203.0.113.9:{ventana}"]
    assert llamada["json"][1][0] == "EXPIRE"
    assert llamada["json"][1][1] == f"rl:chat:203.0.113.9:{ventana}"
    assert llamada["json"][1][2] == int(ratelimit.WINDOW_SECONDS) * 2
    assert not ratelimit._hits


def test_redis_sobre_el_cupo_responde_429(monkeypatch):
    _activar_redis(monkeypatch)
    post = _redis_ok([{"result": 11}, {"result": 1}])
    monkeypatch.setattr(ratelimit.httpx, "post", post)
    with pytest.raises(HTTPException) as exc:
        ratelimit.check(_request({"x-real-ip": "203.0.113.4"}), 10, "chat")
    assert exc.value.status_code == 429
    assert exc.value.headers["Retry-After"]
    assert not ratelimit._hits


def test_redis_caido_cae_al_limiter_en_memoria(monkeypatch):
    _activar_redis(monkeypatch)
    intentos = {"n": 0}

    def _post(*_a, **_k):
        intentos["n"] += 1
        raise httpx.ConnectError("down")

    monkeypatch.setattr(ratelimit.httpx, "post", _post)
    req = _request({"x-real-ip": "198.51.100.7"})
    for _ in range(10):
        ratelimit.check(req, 10, "chat")
    with pytest.raises(HTTPException) as exc:
        ratelimit.check(req, 10, "chat")
    assert exc.value.status_code == 429
    assert intentos["n"] == 11
    assert len(ratelimit._hits["chat:198.51.100.7"]) == 10


def test_ip_activa_no_se_reinicia_al_desalojar(monkeypatch):
    """Llenar el mapa no hace _hits.clear(): la IP que sigue pegando queda al límite."""
    monkeypatch.setattr(ratelimit, "_MAX_IPS", 2)
    ratelimit.check(_request({"x-real-ip": "10.0.0.1"}), 10, "chat")
    agresor = _request({"x-real-ip": "10.9.9.9"})
    for _ in range(10):
        ratelimit.check(agresor, 10, "chat")
    ratelimit.check(_request({"x-real-ip": "10.0.0.3"}), 10, "chat")
    assert "chat:10.0.0.1" not in ratelimit._hits
    assert len(ratelimit._hits["chat:10.9.9.9"]) == 10
    with pytest.raises(HTTPException) as exc:
        ratelimit.check(agresor, 10, "chat")
    assert exc.value.status_code == 429


def test_hits_viejos_expiran_en_la_ventana(monkeypatch):
    req = _request({"x-real-ip": "10.2.2.2"})
    for _ in range(10):
        ratelimit.check(req, 10, "chat")
    q = ratelimit._hits["chat:10.2.2.2"]
    for i in range(len(q)):
        q[i] -= ratelimit.WINDOW_SECONDS + 1
    ratelimit.check(req, 10, "chat")
    assert len(ratelimit._hits["chat:10.2.2.2"]) == 1
