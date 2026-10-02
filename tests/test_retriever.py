"""Anti-relleno: gate de score y snippet de lectura."""

import pytest

from app.services import rag_service
from rag.config import INDEX_PATH
from rag.hybrid import HybridRetriever


def _retriever() -> HybridRetriever:
    if not INDEX_PATH.exists():
        pytest.skip("índice no generado (corré scripts/ingest.py)")
    return HybridRetriever()


def test_gate_bloquea_ajenas_al_manual(monkeypatch):
    monkeypatch.setenv("RAG_DENSE", "0")
    retriever = _retriever()
    for query in ("recetas de cocina italianas", "películas de terror",
                  "economía argentina", "el hola man"):
        assert retriever.search(query, 5) == [], query


def test_gate_deja_pasar_legitimas(monkeypatch):
    monkeypatch.setenv("RAG_DENSE", "0")
    retriever = _retriever()
    for query in ("¿cómo restauro un backup?", "¿cómo cargo un cliente nuevo?",
                  "¿cómo facturo un comprobante?"):
        assert retriever.search(query, 5), query


def test_enrich_snippet_centra_en_la_query():
    text = "x" * 120 + " el módulo de backup se ejecuta a las 22:00." + "y" * 300
    hits = [{"title": "Manual STELLA", "page": 7, "doc_id": "manual",
             "text": text}]
    [item] = rag_service.enrich(hits, "¿dónde está el backup?")
    assert "backup" in item["snippet"]
    assert item["snippet"].startswith("…")
    assert len(item["snippet"]) <= 202
    assert item["citation"] == "📄 Manual STELLA, p. 7"


def test_enrich_snippet_sin_coincidencia_toma_la_cabecera():
    text = "texto del manual sin ninguna palabra de la consulta. " * 20
    hits = [{"title": "Manual STELLA", "page": 3, "doc_id": "manual",
             "text": text}]
    [item] = rag_service.enrich(hits, "zzzzqqq")
    assert item["snippet"].startswith("texto del manual")
    assert item["snippet"].endswith("…")
    assert not item["snippet"].startswith("…")


def test_search_real_agrega_snippet(monkeypatch):
    monkeypatch.setenv("RAG_DENSE", "0")
    if not INDEX_PATH.exists():
        pytest.skip("índice no generado")
    rag_service.set_retriever(HybridRetriever())
    try:
        hits = rag_service.search("¿cómo cargo un cliente nuevo?", 3)
    finally:
        rag_service.set_retriever(None)
    assert hits
    assert "cliente" in hits[0]["snippet"]
