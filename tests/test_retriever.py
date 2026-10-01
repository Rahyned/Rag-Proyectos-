"""Degradación segura del recuperador: sin modelo / sin dense.

Todos estos tests corren en CI: no descargan embeddings.
"""

from rag import config as rag_config
from rag.hybrid import HybridRetriever


def test_dense_encendido_fuera_de_vercel(monkeypatch):
    monkeypatch.delenv("VERCEL", raising=False)
    monkeypatch.delenv("RAG_DENSE", raising=False)
    assert rag_config.dense_enabled() is True


def test_dense_apagado_en_vercel_salvo_override(monkeypatch):
    monkeypatch.setenv("VERCEL", "1")
    monkeypatch.delenv("RAG_DENSE", raising=False)
    assert rag_config.dense_enabled() is False
    monkeypatch.setenv("RAG_DENSE", "1")
    assert rag_config.dense_enabled() is True


def test_search_sin_dense_es_bm25(monkeypatch):
    monkeypatch.setenv("RAG_DENSE", "0")
    hits = HybridRetriever().search("cómo agrego un cliente nuevo", 3)
    assert hits
    assert all(h["engine"] == "bm25" for h in hits)


def test_search_degrada_a_bm25_si_falla_el_denso(monkeypatch):
    monkeypatch.setenv("RAG_DENSE", "1")
    retriever = HybridRetriever()

    def _boom(texts):
        raise RuntimeError("sin modelo")

    monkeypatch.setattr(retriever, "_embed", _boom)
    hits = retriever.search("cómo agrego un cliente nuevo", 3)
    assert hits
    assert all(h["engine"] == "bm25" for h in hits)
