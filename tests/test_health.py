from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert isinstance(data["llm"], bool)
    assert data["model"]
    assert isinstance(data["dense"], bool)
    assert data["dense_error"] is None or isinstance(data["dense_error"], str)


def test_root():
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["name"] == "rag-proyectos"
