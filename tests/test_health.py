from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] in ("ok", "degraded")
    assert isinstance(data["retrievable"], bool)
    assert isinstance(data["llm"], bool)
    assert data["model"]
    assert isinstance(data["dense"], bool)
    assert data["dense_error"] is None or isinstance(data["dense_error"], str)
    assert data["dense_error_origen"] is None or isinstance(
        data["dense_error_origen"], str
    )


def test_health_expone_el_origen_del_circuito(monkeypatch):
    from app import ratelimit

    monkeypatch.setenv("EMBEDDINGS_PROVIDER", "local")
    ratelimit.abrir_pausa_jina("status_429")
    data = client.get("/api/health").json()
    assert data["dense_error_origen"] == "status_429"


def test_health_expone_el_origen_tras_un_timeout(monkeypatch):
    from app import ratelimit

    monkeypatch.setenv("EMBEDDINGS_PROVIDER", "local")
    ratelimit.anotar_fallo_jina("timeout")
    data = client.get("/api/health").json()
    assert data["dense_error_origen"] == "timeout"
    assert not ratelimit.jina_en_pausa()


def test_health_muestra_cloudflare_y_la_dimension_del_indice(monkeypatch):
    import faiss

    from rag.config import INDEX_PATH

    monkeypatch.setenv("EMBEDDINGS_PROVIDER", "cloudflare")
    data = client.get("/api/health").json()
    assert data["embeddings"] == "cloudflare"
    assert data["index_dim"] == faiss.read_index(str(INDEX_PATH)).d


def test_health_muestra_el_origen_de_cloudflare(monkeypatch):
    from app import ratelimit

    monkeypatch.setenv("EMBEDDINGS_PROVIDER", "cloudflare")
    ratelimit.abrir_pausa_cloudflare("status_429")
    data = client.get("/api/health").json()
    assert data["dense_error_origen"] == "status_429"
    assert data["embeddings"] == "cloudflare"


def test_health_sin_paths_locales(monkeypatch):
    from app.services import rag_service
    monkeypatch.setattr(
        rag_service._hybrid, "LAST_DENSE_ERROR",
        "falló en /tmp/fastembed/cache/model.onnx",
    )
    data = client.get("/api/health").json()
    assert "/tmp" not in data["dense_error"]
    assert "<ruta>" in data["dense_error"]


def test_root():
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["name"] == "rag-proyectos"
