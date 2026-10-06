import pytest

from app import ratelimit


@pytest.fixture(autouse=True)
def _reset_ratelimit(monkeypatch):
    # La suite no toca la red: un Redis real en el entorno no puede colarse.
    monkeypatch.delenv("UPSTASH_REDIS_REST_URL", raising=False)
    monkeypatch.delenv("UPSTASH_REDIS_REST_TOKEN", raising=False)
    ratelimit.reset()
    yield
    ratelimit.reset()
