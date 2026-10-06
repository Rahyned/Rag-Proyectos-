"""Anti-relleno: gate de score, filtro por proyecto y snippet de lectura."""

import json

import pytest

from app.services import rag_service
from rag.config import INDEX_PATH
from rag.hybrid import HybridRetriever, tokenize


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


def test_bm25_bigrama_adyacente_recibe_bonus():
    """Mismo TF y longitud: gana quien tiene el bigrama de la query seguido.

    "agregar un cliente" tokeniza a [agreg, client] (stopwords fuera), así
    que (agreg, client) es adyacente; con los tokens invertidos no lo es.
    """
    from rag.hybrid import BM25_BIGRAM_BONUS, bm25_scores, tokenize

    docs = [tokenize("agregar un cliente"), tokenize("cliente agregar")]
    df: dict[str, int] = {}
    for doc in docs:
        for t in set(doc):
            df[t] = df.get(t, 0) + 1
    scores = bm25_scores("agregar cliente", docs, df, len(docs))
    assert scores[0] > scores[1]
    assert scores[0] - scores[1] == pytest.approx(BM25_BIGRAM_BONUS)


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
    assert "Manual STELLA" in item["citation"]
    assert "(pág. 7)" in item["citation"]


def test_enrich_snippet_sin_coincidencia_toma_la_cabecera():
    text = "texto del manual sin ninguna palabra de la consulta. " * 20
    hits = [{"title": "Manual STELLA", "page": 3, "doc_id": "manual",
             "text": text}]
    [item] = rag_service.enrich(hits, "zzzzqqq")
    assert item["snippet"].startswith("texto del manual")
    assert item["snippet"].endswith("…")
    assert not item["snippet"].startswith("…")


def test_el_nombre_no_abre_el_gate(monkeypatch):
    """«stella» solo no alcanza: hace falta otro término del manual."""
    monkeypatch.setenv("RAG_DENSE", "0")
    retriever = _retriever()
    assert retriever.search("stella quién ganó el oscar", 5) == []
    pages = [h["page"] for h in retriever.search("¿Qué es STELLA?", 5)]
    assert 4 in pages[:3]
    gold = json.loads(
        (INDEX_PATH.parent / "gold_test.json").read_text(encoding="utf-8")
    )
    for entry in gold:
        hits = retriever.search(entry["q"], 5)
        esperadas = entry.get("pages") or [entry["page"]]
        assert any(h["page"] in esperadas for h in hits[:3]), entry["q"]


def test_que_es_stella_incluye_la_introduccion(monkeypatch):
    """«¿Qué es STELLA?» prioriza la introducción aunque el nombre esté en todo el manual."""
    monkeypatch.setenv("RAG_DENSE", "0")
    pages = [h["page"] for h in _retriever().search("¿Qué es STELLA?", 5)]
    assert 4 in pages[:3]


def test_copia_de_seguridad_trae_la_pagina_de_backups(monkeypatch):
    monkeypatch.setenv("RAG_DENSE", "0")
    pages = [h["page"] for h in _retriever().search(
        "¿Cómo hago una copia de seguridad?", 5)]
    assert 31 in pages[:3]


def test_cobrarle_a_un_dentista_trae_cuentas_corrientes(monkeypatch):
    """Pág. 26 abre «9. Cuentas corrientes»: debe, haber, saldo y el cobro."""
    monkeypatch.setenv("RAG_DENSE", "0")
    hits = _retriever().search("quiero cobrarle a un dentista", 5)
    assert hits
    assert 26 in [h["page"] for h in hits[:5]]


def test_expandir_sinonimo_pesa_menos_que_el_original():
    from rag.sinonimos import PESO_SINONIMO, expandir

    pesos = dict(expandir(tokenize("dentista")))
    assert pesos["dentist"] == 1.0
    assert pesos["odontolog"] == PESO_SINONIMO
    copia = dict(expandir(tokenize("¿Cómo hago una copia de seguridad?")))
    assert copia["copi"] == 1.0
    assert copia["backup"] == PESO_SINONIMO


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
    assert "STELLA" in hits[0]["citation"]


def test_filtra_y_detecta_proyecto(monkeypatch, tmp_path):
    """El metadato se aplica antes de rankear; si no hay selector, mira la pregunta."""
    import faiss
    import numpy as np

    monkeypatch.setenv("RAG_DENSE", "0")
    texto = "alta de un cliente nuevo en el laboratorio con lista de precios"
    filas = []
    for proyecto, nombre in (("stella", "STELLA"), ("cars", "SolutionsCars")):
        filas.append({
            "chunk_id": f"{proyecto}:p1:0",
            "doc_id": proyecto,
            "title": nombre,
            "page": 1,
            "text": texto,
            "proyecto": proyecto,
            "proyecto_nombre": nombre,
            "seccion": "Clientes",
            "publico": proyecto == "stella",
            "tipo": "ficha",
        })
    path = tmp_path / "chunks.jsonl"
    path.write_text(
        "\n".join(json.dumps(f, ensure_ascii=False) for f in filas) + "\n",
        encoding="utf-8",
    )
    index = faiss.IndexFlatIP(4)
    index.add(np.ones((2, 4), dtype=np.float32))
    faiss.write_index(index, str(tmp_path / "index.faiss"))
    retriever = HybridRetriever(path, tmp_path / "index.faiss")
    solo = retriever.search("agregar un cliente nuevo", 5, proyecto="stella")
    assert solo and {h["proyecto"] for h in solo} == {"stella"}
    detectado = retriever.search("agregar un cliente nuevo en STELLA", 5)
    assert detectado and {h["proyecto"] for h in detectado} == {"stella"}
    cita = rag_service.enrich(solo, "cliente")[0]
    assert cita["url"] is None
    assert cita["citation"] == "STELLA · STELLA · Clientes (pág. 1)"
