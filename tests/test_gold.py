"""Gold set: la recuperación debe traer la página o la sección esperada.

BM25 corre siempre (sin modelo, apto para CI). La prueba densa/híbrida se
ejecuta con RUN_DENSE_TESTS=1 en la máquina que ya tiene el modelo.
Las negativas (vacio) no entran al conteo de top-3: se afirman aparte.
"""

import json
import os
import re

import pytest

from rag.config import DATA_DIR, EMBED_MODEL, INDEX_PATH, TOP_K
from rag.hybrid import HybridRetriever

GOLD_TEST_PATH = DATA_DIR / "gold_test.json"
GOLD_TUNING_PATH = DATA_DIR / "gold_tuning.json"

PROYECTOS = {
    "stella",
    "solutionscars",
    "laboratorio-riodent",
    "portafolio-web",
    "todos",
}

# El set de medición (gold_test) no se usa para mover el umbral.
# BM25: 36/44. Híbrida contra el índice de la API de Jina: 41/44.
MIN_BM25_TOP3 = 36
MIN_HYBRID_TOP3 = 41


def _gold() -> list[dict]:
    if not GOLD_TEST_PATH.exists():
        pytest.skip("gold_test.json no generado")
    return json.loads(GOLD_TEST_PATH.read_text(encoding="utf-8"))


def _leer(path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def _positivos(entries: list[dict]) -> list[dict]:
    return [entry for entry in entries if not entry.get("vacio")]


def _retriever() -> HybridRetriever:
    if not (GOLD_TEST_PATH.exists() and INDEX_PATH.exists()):
        pytest.skip("índice no generado (corré scripts/ingest.py)")
    return HybridRetriever()


def _ultimo(seccion: str) -> str:
    return (seccion or "").split(" › ")[-1].strip()


def _hit_cubre(hit: dict, spec: dict) -> bool:
    """Una página del PDF o el último tramo de la sección del Markdown."""
    if spec.get("doc_id") and hit.get("doc_id") != spec["doc_id"]:
        return False
    if "page" in spec or "pages" in spec:
        pages = spec.get("pages") or [spec["page"]]
        return hit.get("page") in pages
    secciones = list(spec.get("sections") or [])
    if spec.get("section"):
        secciones.append(spec["section"])
    if not secciones:
        return False
    ultimo = _ultimo(hit.get("seccion") or "")
    texto = hit.get("seccion") or ""
    return any(ultimo == seccion or texto.endswith(seccion) for seccion in secciones)


def _specs(entry: dict) -> list[dict]:
    if entry.get("acepta"):
        return entry["acepta"]
    return [entry]


def _acierto(hits: list[dict], entry: dict, k: int = 3) -> bool:
    if entry.get("vacio"):
        return hits == []
    return any(
        _hit_cubre(hit, spec) for hit in hits[:k] for spec in _specs(entry)
    )


def test_gold_tiene_proyecto_y_los_cortes_no_se_pisan():
    test = _leer(GOLD_TEST_PATH)
    tuning = _leer(GOLD_TUNING_PATH)
    assert test and tuning
    assert all(item["proyecto"] in PROYECTOS for item in test + tuning)
    assert any(item["proyecto"] == "stella" for item in test)
    assert any(item["proyecto"] == "stella" for item in tuning)
    assert not ({item["q"] for item in test} & {item["q"] for item in tuning})
    assert sum(1 for item in test + tuning if item["proyecto"] == "todos") >= 4
    for pid in ("solutionscars", "laboratorio-riodent", "portafolio-web"):
        items = [item for item in test + tuning if item["proyecto"] == pid]
        assert len(items) >= 10, pid
        assert sum(1 for item in items if item.get("vacio")) >= 2, pid


def test_gold_bm25_top3():
    retriever = _retriever()
    gold = _positivos(_gold())
    hits = 0
    for entry in gold:
        encontrados = retriever.bm25(entry["q"], TOP_K, proyecto=entry["proyecto"])
        if _acierto(encontrados, entry):
            hits += 1
    assert hits >= MIN_BM25_TOP3, f"BM25 top3: {hits}/{len(gold)}"


@pytest.mark.skipif(not os.environ.get("RUN_DENSE_TESTS"),
                    reason="requiere modelo de embeddings (RUN_DENSE_TESTS=1)")
def test_gold_hybrid_top3():
    retriever = _retriever()
    if retriever.index.ntotal != retriever._n:
        pytest.skip("índice denso desfasado de chunks.jsonl")
    gold = _positivos(_gold())
    hits = 0
    for entry in gold:
        encontrados = retriever.search(entry["q"], TOP_K, proyecto=entry["proyecto"])
        if _acierto(encontrados, entry):
            hits += 1
    assert hits >= MIN_HYBRID_TOP3, f"híbrida top3: {hits}/{len(gold)}"


def test_gold_negativas_quedan_vacias(monkeypatch):
    """El gate no deja pasar una pregunta ajena al proyecto elegido."""
    monkeypatch.setenv("RAG_DENSE", "0")
    retriever = _retriever()
    vistas = 0
    for path in (GOLD_TEST_PATH, GOLD_TUNING_PATH):
        for entry in _leer(path):
            if not entry.get("vacio"):
                continue
            vistas += 1
            hits = retriever.search(entry["q"], TOP_K, proyecto=entry["proyecto"])
            assert hits == [], (entry["proyecto"], entry["q"], hits[:1])
    assert vistas >= 6


def test_index_matches_chunks():
    if not (INDEX_PATH.exists()):
        pytest.skip("índice no generado")
    import faiss

    from rag.hybrid import load_chunks
    from scripts.ingest import META_PATH

    index = faiss.read_index(str(INDEX_PATH))
    chunks = load_chunks()
    meta = json.loads(META_PATH.read_text(encoding="utf-8"))
    assert index.ntotal == len(chunks)
    assert index.ntotal == meta["n_chunks"]
    assert index.ntotal > 0
    assert index.d == 768
    assert meta["embed_model"] == EMBED_MODEL == "jinaai/jina-embeddings-v2-base-es"


def test_las_secciones_del_gold_existen_como_encabezado():
    """Cada section del gold es un encabezado del markdown de ese documento."""
    from rag.manifiesto import cargar

    titulos_por_doc: dict[str, set[str]] = {}
    for proyecto in cargar()["proyectos"]:
        for doc in proyecto["documentos"]:
            path = doc["path"]
            if path.suffix.lower() != ".md":
                continue
            titulos = set()
            for linea in path.read_text(encoding="utf-8").splitlines():
                match = re.match(r"^#{1,3}\s+(.+?)\s*$", linea)
                if match:
                    titulos.add(match.group(1).strip())
            titulos_por_doc[path.stem] = titulos

    faltan = []
    for path in (GOLD_TUNING_PATH, GOLD_TEST_PATH):
        for entry in _leer(path):
            if entry.get("vacio"):
                continue
            for spec in _specs(entry):
                doc_id = spec.get("doc_id") or entry.get("doc_id")
                secciones = list(spec.get("sections") or [])
                if spec.get("section"):
                    secciones.append(spec["section"])
                if not doc_id or not secciones:
                    continue
                titulos = titulos_por_doc.get(doc_id, set())
                for seccion in secciones:
                    if seccion not in titulos:
                        faltan.append(
                            f"{path.name}: {entry['q']!r} -> {doc_id} / {seccion}"
                        )
    assert not faltan, "\n".join(faltan)
