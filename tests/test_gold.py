"""Gold set: la recuperación debe traer la página esperada.

BM25 corre siempre (sin modelo, apto para CI). La prueba densa/híbrida se
ejecuta con RUN_DENSE_TESTS=1 en la máquina que ya tiene el modelo.
"""

import json
import os

import pytest

from rag.config import DATA_DIR, INDEX_PATH, TOP_K
from rag.hybrid import HybridRetriever

GOLD_TEST_PATH = DATA_DIR / "gold_test.json"
GOLD_TUNING_PATH = DATA_DIR / "gold_tuning.json"

# El set de medición (gold_test) no se usa para mover el umbral.
# 10/10 en BM25; la híbrida mantiene el piso histórico de 8 sobre este corte.
MIN_BM25_TOP3 = 10
MIN_HYBRID_TOP3 = 8


def _gold() -> list[dict]:
    if not GOLD_TEST_PATH.exists():
        pytest.skip("gold_test.json no generado")
    return json.loads(GOLD_TEST_PATH.read_text(encoding="utf-8"))


def _retriever() -> HybridRetriever:
    if not (GOLD_TEST_PATH.exists() and INDEX_PATH.exists()):
        pytest.skip("índice no generado (corré scripts/ingest.py)")
    return HybridRetriever()


def test_gold_tiene_proyecto_y_los_cortes_no_se_pisan():
    test = json.loads(GOLD_TEST_PATH.read_text(encoding="utf-8"))
    tuning = json.loads(GOLD_TUNING_PATH.read_text(encoding="utf-8"))
    assert test and tuning
    assert all(item["proyecto"] == "stella" for item in test + tuning)
    assert not ({item["q"] for item in test} & {item["q"] for item in tuning})


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
