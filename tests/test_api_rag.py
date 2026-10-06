"""Tests de la API RAG con un recuperador falso (sin modelo ni red)."""

import json

import httpx
import pytest
from fastapi.testclient import TestClient

import app.config as config
import app.services.llm as llm_mod
from app.main import app
from app.services import rag_service

client = TestClient(app)

FAKE_HITS = [
    {"rank": 1, "score": 0.9, "chunk_id": "manual-stella:p15:1",
     "doc_id": "manual-stella", "title": "Manual STELLA", "page": 15,
     "text": "5.3 Agregar un cliente: completá nombre, mail y lista…",
     "proyecto": "stella", "proyecto_nombre": "STELLA",
     "seccion": "5. Clientes › 5.3 Agregar un cliente",
     "publico": True, "pdf": "stella/manual-stella.pdf", "tipo": "manual"},
    {"rank": 2, "score": 0.4, "chunk_id": "manual-stella:p16:0",
     "doc_id": "manual-stella", "title": "Manual STELLA", "page": 16,
     "text": "5.6 Importar clientes desde Excel…",
     "proyecto": "stella", "proyecto_nombre": "STELLA",
     "seccion": "5. Clientes › 5.6 Importar clientes desde Excel",
     "publico": True, "pdf": "stella/manual-stella.pdf", "tipo": "manual"},
]


class FakeRetriever:
    def __init__(self):
        self.proyecto = None

    def search(self, query, top_k=5, proyecto=None):
        self.proyecto = proyecto
        return FAKE_HITS[:top_k]

    def bm25(self, query, top_k=5, proyecto=None):
        self.proyecto = proyecto
        return FAKE_HITS[:top_k]


@pytest.fixture(autouse=True)
def _fake_retriever():
    rag_service.set_retriever(FakeRetriever())
    yield
    rag_service.set_retriever(None)


def _events(text: str) -> list[dict]:
    return [json.loads(line[5:]) for line in text.split("\n\n")
            if line.startswith("data: ")]


def test_search_ok():
    resp = client.post("/api/search", json={"query": "agregar cliente"})
    assert resp.status_code == 200
    hits = resp.json()["hits"]
    assert hits[0]["page"] == 15
    assert hits[0]["citation"] == (
        "STELLA · Manual STELLA · 5. Clientes › 5.3 Agregar un cliente (pág. 15)"
    )
    assert hits[0]["url"] == "corpus/stella/manual-stella.pdf#page=15"


def test_search_query_corta_rechazada():
    resp = client.post("/api/search", json={"query": ""})
    assert resp.status_code == 422


def test_search_recupera_503_si_falla(monkeypatch):
    def _boom():
        raise RuntimeError("índice roto")
    monkeypatch.setattr(rag_service, "get_retriever", _boom)
    resp = client.post("/api/search", json={"query": "algo"})
    assert resp.status_code == 503


def test_chat_fragmentos():
    resp = client.post("/api/chat", json={
        "query": "agregar cliente", "mode": "fragmentos"})
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/event-stream")
    events = _events(resp.text)
    assert events[0]["type"] == "sources"
    assert events[0]["hits"][0]["page"] == 15
    assert events[-1] == {"type": "done", "mode": "fragmentos"}
    assert not any(e["type"] == "text" for e in events)


def test_chat_sintetica_sin_llm_cae_a_fragmentos(monkeypatch):
    monkeypatch.setattr(config, "llm_api_key", lambda: "")
    resp = client.post("/api/chat", json={
        "query": "agregar cliente", "mode": "sintetica"})
    events = _events(resp.text)
    assert [e["type"] for e in events] == ["sources", "fallback", "done"]
    assert events[1]["reason"] == "no_key"
    assert events[2]["mode"] == "fragmentos"


def test_chat_sintetica_ok(monkeypatch):
    monkeypatch.setattr(llm_mod, "stream_answer",
                        lambda q, h: iter(["Según el ", "manual."]))
    resp = client.post("/api/chat", json={
        "query": "agregar cliente", "mode": "sintetica"})
    events = _events(resp.text)
    assert [e["type"] for e in events] == \
        ["sources", "text", "text", "done"]
    assert events[1]["delta"] + events[2]["delta"] == "Según el manual."
    assert events[-1] == {"type": "done", "mode": "sintetica"}


def test_chat_sintetica_error_llm_cae_a_fragmentos(monkeypatch):
    def _fail(q, h):
        yield from ()
        raise llm_mod.LLMError("boom")
    monkeypatch.setattr(llm_mod, "stream_answer", _fail)
    resp = client.post("/api/chat", json={
        "query": "agregar cliente", "mode": "sintetica"})
    events = _events(resp.text)
    assert [e["type"] for e in events] == ["sources", "fallback", "done"]
    assert events[1]["reason"] == "upstream"
    assert events[2]["mode"] == "fragmentos"


def test_chat_sintetica_reason_se_propaga(monkeypatch):
    def _fail(q, h):
        yield from ()
        raise llm_mod.LLMError("x", reason="rate_limited")
    monkeypatch.setattr(llm_mod, "stream_answer", _fail)
    resp = client.post("/api/chat", json={
        "query": "agregar cliente", "mode": "sintetica"})
    events = _events(resp.text)
    assert events[1]["reason"] == "rate_limited"


def test_chat_sintetica_sin_fragmentos_no_llama_al_llm(monkeypatch):
    class EmptyRetriever:
        def search(self, query, top_k=5, proyecto=None):
            return []

        def bm25(self, query, top_k=5, proyecto=None):
            return []

    rag_service.set_retriever(EmptyRetriever())
    llamados = []

    def _llm(q, h):
        llamados.append(1)
        return iter([])

    monkeypatch.setattr(llm_mod, "stream_answer", _llm)
    resp = client.post("/api/chat", json={
        "query": "algo que no existe", "mode": "sintetica"})
    events = _events(resp.text)
    assert [e["type"] for e in events] == ["sources", "done"]
    assert events[1] == {"type": "done", "mode": "fragmentos"}
    assert llamados == []


def test_chat_excepcion_inesperada_cierra_el_stream(monkeypatch):
    def _boom(q, h):
        raise ValueError("rara")
        yield  # pragma: no cover — lo hace generador
    monkeypatch.setattr(llm_mod, "stream_answer", _boom)
    resp = client.post("/api/chat", json={
        "query": "agregar cliente", "mode": "sintetica"})
    events = _events(resp.text)
    assert [e["type"] for e in events] == ["sources", "fallback", "done"]
    assert events[1]["reason"] == "error"


def test_query_solo_espacios_rechazada():
    resp = client.post("/api/search", json={"query": "   "})
    assert resp.status_code == 422


def test_503_no_fuga_internos(monkeypatch):
    def _boom():
        raise RuntimeError("C:\\Users\\secreto\\chunks.jsonl no existe")
    monkeypatch.setattr(rag_service, "get_retriever", _boom)
    resp = client.post("/api/search", json={"query": "algo"})
    assert resp.status_code == 503
    assert "secreto" not in resp.text
    assert "Recuperación no disponible" in resp.json()["detail"]
    assert "ref:" in resp.json()["detail"]


def test_sintetica_limita_top_k_y_search_no(monkeypatch):
    monkeypatch.setattr(config, "llm_api_key", lambda: "")
    vistos = []

    class _Recorder:
        def search(self, query, top_k=5, proyecto=None):
            vistos.append(top_k)
            return FAKE_HITS[:top_k]

        def bm25(self, query, top_k=5, proyecto=None):
            return FAKE_HITS[:top_k]

    rag_service.set_retriever(_Recorder())
    client.post("/api/chat", json={
        "query": "agregar cliente", "mode": "sintetica", "top_k": 10})
    client.post("/api/chat", json={
        "query": "agregar cliente", "mode": "fragmentos", "top_k": 10})
    client.post("/api/search", json={"query": "agregar cliente", "top_k": 10})
    assert vistos == [5, 10, 10]


def test_presupuesto_agotado_evento_fallback(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.setenv("LLM_DAILY_BUDGET", "1")
    calls = []

    class _Ctx:
        def __init__(self, resp: httpx.Response) -> None:
            self._resp = resp

        def __enter__(self) -> httpx.Response:
            return self._resp

        def __exit__(self, *_exc) -> bool:
            return False

    def _stream(method, url, **_kwargs):
        calls.append(url)
        body = (
            'data: {"choices":[{"delta":{"content":"ok"}}]}\n\n'
            "data: [DONE]\n\n"
        )
        resp = httpx.Response(
            200, text=body, request=httpx.Request(method, url),
        )
        return _Ctx(resp)

    monkeypatch.setattr(llm_mod.httpx, "stream", _stream)
    body = {"query": "agregar cliente", "mode": "sintetica"}
    primero = _events(client.post("/api/chat", json=body).text)
    segundo = _events(client.post("/api/chat", json=body).text)
    assert primero[-1] == {"type": "done", "mode": "sintetica"}
    assert any(
        e.get("type") == "fallback" and e.get("reason") == "rate_limited"
        for e in segundo
    )
    assert len(calls) == 1


def test_rate_limit_chat_429():
    body = {"query": "agregar cliente", "mode": "fragmentos"}
    resp = None
    for _ in range(11):
        resp = client.post("/api/chat", json=body)
    assert resp.status_code == 429
    assert "Retry-After" in resp.headers
    assert "Demasiadas" in resp.json()["detail"]


def test_prompt_incluye_paginas():
    prompt = llm_mod.build_prompt("¿cómo?", FAKE_HITS)
    assert "STELLA · Manual STELLA · 5. Clientes › 5.3 Agregar un cliente (pág. 15)" in prompt
    assert "5.6 Importar clientes desde Excel (pág. 16)" in prompt
    assert "¿cómo?" in prompt
    sistema = llm_mod.system_prompt()
    assert "contexto recuperado" in sistema
    assert "STELLA" in sistema


def test_search_filtra_proyecto_desconocido():
    resp = client.post("/api/search", json={"query": "agregar cliente", "proyecto": "no-existe"})
    assert resp.status_code == 422


def test_search_pasa_el_proyecto(monkeypatch):
    visto = {}

    class _R:
        def search(self, query, top_k=5, proyecto=None):
            visto["proyecto"] = proyecto
            return FAKE_HITS[:top_k]

    rag_service.set_retriever(_R())
    resp = client.post("/api/search", json={"query": "agregar cliente", "proyecto": "stella"})
    assert resp.status_code == 200
    assert visto["proyecto"] == "stella"


def test_manifiesto_roto_no_muestra_la_ruta(monkeypatch, caplog):
    import logging

    from rag.manifiesto import ManifiestoError

    def boom():
        raise ManifiestoError("no existe el archivo corpus/stella/secreto.md")

    monkeypatch.setattr("app.main.ids_proyectos", boom)
    monkeypatch.setattr("app.main.proyectos_publicos", boom)
    with caplog.at_level(logging.ERROR, logger="rag.api"):
        busqueda = client.post(
            "/api/search",
            json={"query": "agregar cliente", "proyecto": "stella"},
        )
        lista = client.get("/api/proyectos")
    assert busqueda.status_code == 422
    assert lista.status_code == 503
    for resp in (busqueda, lista):
        assert "configuración inválida" in resp.text
        assert "corpus/" not in resp.text
        assert "secreto.md" not in resp.text
    assert "corpus/stella/secreto.md" in " ".join(caplog.messages)


def test_proyectos_lista_stella():
    resp = client.get("/api/proyectos")
    assert resp.status_code == 200
    ids = [p["id"] for p in resp.json()["proyectos"]]
    assert "stella" in ids
    assert "emails_publicos" not in resp.text
