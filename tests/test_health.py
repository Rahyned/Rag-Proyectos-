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
