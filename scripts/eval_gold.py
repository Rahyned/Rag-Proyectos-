"""Imprime hit@3 y hit@5 del gold, por proyecto, para BM25 y la híbrida.

Si `EMBEDDINGS_PROVIDER` está definida, se respeta (por ejemplo `off` para
medir solo BM25). Si no, con `JINA_API_KEY` usa Jina y sin key apaga el
denso: el modelo local (ONNX) no se carga.

`--rerank` agrega la comparación del gold de test: RRF solo, reranker en
modo `replace` y `fuse` con pesos 0.3/0.5/0.7, cada uno con `RERANK_TOP_N`
10 y 20, siempre con top 3 y top 5. Los resultados del reranker se cachean
por (consulta, pool), así la matriz completa gasta una llamada por consulta
y por `RERANK_TOP_N` (tamaño del gold × 2), no una por tabla. Necesita
`CF_ACCOUNT_ID` y `CF_API_TOKEN`; sin credenciales la comparación se omite
(no se inventan números). Con `--rerank` también imprime el corte `v1`
(los 44 casos viejos) frente al gold completo.
"""

from __future__ import annotations

import os
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Antes de importar rag: fuera de Vercel el default es el ONNX local.
if not os.environ.get("EMBEDDINGS_PROVIDER", "").strip():
    if os.environ.get("JINA_API_KEY"):
        os.environ["EMBEDDINGS_PROVIDER"] = "api"
    else:
        os.environ["EMBEDDINGS_PROVIDER"] = "off"

from app import config as app_config  # noqa: E402
from rag.config import TOP_K  # noqa: E402
from tests.test_gold import (  # noqa: E402
    GOLD_TEST_PATH,
    GOLD_TUNING_PATH,
    _acierto,
    _leer,
    _positivos,
    _retriever,
    _ultimo,
)

CASOS = (
    "toma de color",
    "cuánto sale una página web",
    "cómo hago un pedido al laboratorio",
    "qué tiene el portafolio",
    "¿cómo hago una copia de seguridad?",
)


def _por_proyecto(entries: list[dict]) -> dict[str, list[dict]]:
    grupos: dict[str, list[dict]] = defaultdict(list)
    for entry in entries:
        grupos[entry["proyecto"]].append(entry)
    return grupos


def _tabla(retriever, entries: list[dict], metodo: str) -> None:
    positivos = _positivos(entries)
    print(f"  {metodo}")
    print(f"  {'proyecto':<22} {'n':>4} {'hit@3':>8} {'hit@5':>8}")
    total3 = total5 = n = 0
    buscar = retriever.bm25 if metodo == "bm25" else retriever.search
    for proyecto, items in _por_proyecto(positivos).items():
        h3 = h5 = 0
        for entry in items:
            hits = buscar(entry["q"], TOP_K, proyecto=entry["proyecto"])
            h3 += int(_acierto(hits, entry, k=3))
            h5 += int(_acierto(hits, entry, k=5))
        print(f"  {proyecto:<22} {len(items):>4} {h3:>8} {h5:>8}")
        total3 += h3
        total5 += h5
        n += len(items)
    print(f"  {'TOTAL':<22} {n:>4} {total3:>8} {total5:>8}")


def _negativas(retriever, entries: list[dict], etiqueta: str) -> None:
    malas = []
    for entry in entries:
        if not entry.get("vacio"):
            continue
        hits = retriever.search(entry["q"], TOP_K, proyecto=entry["proyecto"])
        if hits:
            primero = hits[0]
            malas.append(
                f"    {entry['proyecto']}: {entry['q']!r} -> "
                f"{primero.get('doc_id')} / {_ultimo(primero.get('seccion') or '')}"
            )
    print(f"  negativas no vacías ({etiqueta}): {len(malas)}")
    for linea in malas:
        print(linea)


def _casos(retriever) -> None:
    test = {item["q"]: item for item in _leer(GOLD_TEST_PATH)}
    print("  casos de producción (primer resultado BM25)")
    for q in CASOS:
        entry = test[q]
        hits = retriever.bm25(q, TOP_K, proyecto=entry["proyecto"])
        if not hits:
            print(f"    {q!r} -> (vacio)")
            continue
        primero = hits[0]
        ok3 = _acierto(hits, entry, k=3)
        ok5 = _acierto(hits, entry, k=5)
        donde = primero.get("seccion") or f"(pag. {primero.get('page')})"
        print(
            f"    {q!r} -> {primero.get('proyecto')} / {donde}"
            f"  hit@3={ok3} hit@5={ok5}"
        )
        for i, hit in enumerate(hits, start=1):
            lugar = hit.get("seccion") or f"(pag. {hit.get('page')})"
            print(f"      {i}. {hit.get('proyecto')} / {lugar}")


_TOP_NS = (20, 10)
_PESOS_FUSE = (0.3, 0.5, 0.7)
_RERANK_VARS = (
    "RERANK_ENABLED", "RERANK_MODE", "RERANK_WEIGHT", "RERANK_TOP_N",
)


def _configurar_rerank(*, enabled: bool, mode: str = "fuse",
                       peso: float = 0.5, top_n: int = 20) -> None:
    os.environ["RERANK_ENABLED"] = "1" if enabled else "0"
    os.environ["RERANK_MODE"] = mode
    os.environ["RERANK_WEIGHT"] = str(peso)
    os.environ["RERANK_TOP_N"] = str(top_n)


def _resumen_gold(retriever, entries: list[dict], metodo: str) -> None:
    """Corta el gold por `v1` y completo: una fila por corte, top 3/5."""
    v1 = [entry for entry in entries if entry.get("v1")]
    buscar = retriever.bm25 if metodo == "bm25" else retriever.search
    cortes = (
        (f"v1 ({len(v1)})", v1),
        (f"completo ({len(entries)})", entries),
    )
    for etiqueta, subset in cortes:
        positivos = _positivos(subset)
        h3 = h5 = 0
        for entry in positivos:
            hits = buscar(entry["q"], TOP_K, proyecto=entry["proyecto"])
            h3 += int(_acierto(hits, entry, k=3))
            h5 += int(_acierto(hits, entry, k=5))
        print(f"  {etiqueta:<18} {len(positivos):>4} {h3:>8} {h5:>8}")


def _comparar_reranker(retriever, entries: list[dict],
                       timeout: float = 20.0) -> None:
    """Mide el gold con RRF solo, replace y fuse (pesos × top_n)."""
    print("\ntest — con y sin reranker (top 3 / top 5)")
    previo = {name: os.environ.get(name) for name in _RERANK_VARS}
    try:
        print("  gold viejo vs nuevo")
        print(f"  {'corte':<14} {'n':>4} {'hit@3':>8} {'hit@5':>8}")
        _configurar_rerank(enabled=False)
        print("  RRF solo")
        _resumen_gold(retriever, entries, "search")
        _configurar_rerank(enabled=True, mode="fuse", peso=0.5, top_n=10)
        print("  fuse 0.5 · top_n=10")
        _resumen_gold(retriever, entries, "search")
        _configurar_rerank(enabled=False)
        _tabla(retriever, entries, "RRF solo")
        # Igual que EMBED_TIMEOUT: la medición prioriza calidad, no latencia.
        reranker = getattr(retriever, "_reranker", None)
        if reranker is not None:
            reranker.timeout = timeout
        for top_n in _TOP_NS:
            _configurar_rerank(enabled=True, mode="replace", top_n=top_n)
            _tabla(retriever, entries, f"reranker replace · top_n={top_n}")
            for peso in _PESOS_FUSE:
                _configurar_rerank(
                    enabled=True, mode="fuse", peso=peso, top_n=top_n,
                )
                _tabla(retriever, entries, f"fuse {peso} · top_n={top_n}")
    finally:
        for name, valor in previo.items():
            if valor is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = valor


def main() -> None:
    hibrida = os.environ.get("EMBEDDINGS_PROVIDER", "").strip().lower() != "off"
    comparar = "--rerank" in sys.argv[1:]
    if hibrida:
        import rag.embeddings as embeddings

        # La medición no usa el timeout de 3s de una consulta en producción:
        # si vence, el circuito se abre y el resto de la tabla cae a BM25.
        embeddings.EMBED_TIMEOUT = 20.0
    print("denso:", "hibrida (API)" if hibrida else "apagado, solo BM25")
    # Las tablas de siempre son el baseline RRF: el reranker solo se paga
    # con --rerank, y ahí el cache reutiliza las llamadas entre configuraciones.
    os.environ["RERANK_ENABLED"] = "0"
    if comparar and not hibrida:
        print("reranker: el denso está apagado; no hay híbrida que reordenar")
        comparar = False
    if comparar and not (app_config.cf_account_id() and app_config.cf_api_token()):
        print(
            "reranker: faltan CF_ACCOUNT_ID y CF_API_TOKEN; "
            "se omite la comparación con y sin reranker"
        )
        comparar = False
    retriever = _retriever()
    for etiqueta, path in (("tuning", GOLD_TUNING_PATH),
                           ("test", GOLD_TEST_PATH)):
        entries = _leer(path)
        print(f"\n{etiqueta}")
        _tabla(retriever, entries, "bm25")
        if hibrida:
            _tabla(retriever, entries, "hibrida")
        _negativas(retriever, entries, etiqueta)
    test_entries = _leer(GOLD_TEST_PATH)
    print("\ntest — corte v1 vs completo (top 3 / top 5)")
    print(f"  {'corte':<18} {'n':>4} {'hit@3':>8} {'hit@5':>8}")
    print("  bm25")
    _resumen_gold(retriever, test_entries, "bm25")
    if hibrida:
        print("  hibrida")
        _resumen_gold(retriever, test_entries, "search")
    if comparar:
        _comparar_reranker(retriever, test_entries)
    print()
    _casos(retriever)


if __name__ == "__main__":
    main()
