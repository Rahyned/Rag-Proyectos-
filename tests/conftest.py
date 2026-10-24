import pytest

from app import ratelimit


@pytest.fixture(autouse=True)
def _reset_ratelimit(monkeypatch):
    # La suite no toca la red: un Redis real en el entorno no puede colarse.
    monkeypatch.delenv("UPSTASH_REDIS_REST_URL", raising=False)
    monkeypatch.delenv("UPSTASH_REDIS_REST_TOKEN", raising=False)
    monkeypatch.delenv("JINA_API_KEY", raising=False)
    monkeypatch.delenv("CF_ACCOUNT_ID", raising=False)
    monkeypatch.delenv("CF_API_TOKEN", raising=False)
    monkeypatch.delenv("EMBEDDINGS_PROVIDER", raising=False)
    monkeypatch.delenv("RERANK_ENABLED", raising=False)
    monkeypatch.delenv("RERANK_TOP_N", raising=False)
    monkeypatch.delenv("RERANK_KEEP", raising=False)
    monkeypatch.delenv("RERANK_MODE", raising=False)
    monkeypatch.delenv("RERANK_WEIGHT", raising=False)
    ratelimit.reset()
    yield
    ratelimit.reset()
