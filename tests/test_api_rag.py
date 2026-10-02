"""Tests de la API RAG con un recuperador falso (sin modelo ni red)."""

import json

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
     "text": "5.3 Agregar un cliente: completá nombre, mail y lista…"},
    {"rank": 2, "score": 0.4, "chunk_id": "manual-stella:p16:0",
     "doc_id": "manual-stella", "title": "Manual STELLA", "page": 16,
     "text": "5.6 Importar clientes desde Excel…"},
]


class FakeRetriever:
    def search(self, query, top_k=5):
        return FAKE_HITS[:top_k]

    def bm25(self, query, top_k=5):
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
    assert hits[0]["citation"] == "📄 Manual STELLA, p. 15"
    assert hits[0]["url"] == "/corpus/manual-stella.pdf#page=15"


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
        def search(self, query, top_k=5):
            return []

        def bm25(self, query, top_k=5):
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
    assert "Manual STELLA pág. 15" in prompt
    assert "Manual STELLA pág. 16" in prompt
    assert "¿cómo?" in prompt
