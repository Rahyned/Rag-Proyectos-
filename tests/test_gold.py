"""Gold set: la recuperación debe traer la página esperada.

BM25 corre siempre (sin modelo, apto para CI). La prueba densa/híbrida se
ejecuta con RUN_DENSE_TESTS=1 en la máquina que ya tiene el modelo.
"""

import json
import os

import pytest

from rag.config import GOLD_PATH, INDEX_PATH, TOP_K
from rag.hybrid import HybridRetriever

# Con el bonus de proximidad (BM25_BIGRAM_BONUS) ambos canales dan 12/12.
MIN_BM25_TOP3 = 12
MIN_HYBRID_TOP3 = 12


def _gold() -> list[dict]:
    if not GOLD_PATH.exists():
        pytest.skip("gold_set.json no generado")
    return json.loads(GOLD_PATH.read_text(encoding="utf-8"))


def _retriever() -> HybridRetriever:
    if not (GOLD_PATH.exists() and INDEX_PATH.exists()):
        pytest.skip("índice no generado (corré scripts/ingest.py)")
    return HybridRetriever()


def _expected(entry: dict) -> list[int]:
    return entry.get("pages") or [entry["page"]]


def test_gold_bm25_top3():
    retriever = _retriever()
    hits = 0
    for entry in _gold():
        pages = [h["page"] for h in retriever.bm25(entry["q"], TOP_K)]
        if any(p in pages[:3] for p in _expected(entry)):
            hits += 1
    assert hits >= MIN_BM25_TOP3, f"BM25 top3: {hits}/{len(_gold())}"


@pytest.mark.skipif(not os.environ.get("RUN_DENSE_TESTS"),
                    reason="requiere modelo de embeddings (RUN_DENSE_TESTS=1)")
def test_gold_hybrid_top3():
    retriever = _retriever()
    gold = _gold()
    hits = 0
    for entry in gold:
        pages = [h["page"] for h in retriever.search(entry["q"], TOP_K)]
        if any(p in pages[:3] for p in _expected(entry)):
            hits += 1
    assert hits >= MIN_HYBRID_TOP3, f"híbrida top3: {hits}/{len(gold)}"


def test_index_matches_chunks():
    if not (INDEX_PATH.exists()):
        pytest.skip("índice no generado")
    import faiss

    from rag.hybrid import load_chunks

    index = faiss.read_index(str(INDEX_PATH))
    assert index.ntotal == len(load_chunks())
    assert index.ntotal > 0
