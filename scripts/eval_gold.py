"""Imprime hit@3 y hit@5 del gold, por proyecto, para BM25 y la híbrida.

Si `EMBEDDINGS_PROVIDER` está definida, se respeta (por ejemplo `off` para
medir solo BM25). Si no, con `JINA_API_KEY` usa Jina y sin key apaga el
denso: el modelo local (ONNX) no se carga.
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


def main() -> None:
    hibrida = os.environ.get("EMBEDDINGS_PROVIDER", "").strip().lower() != "off"
    if hibrida:
        import rag.embeddings as embeddings

        # La medición no usa el timeout de 3s de una consulta en producción:
        # si vence, el circuito se abre y el resto de la tabla cae a BM25.
        embeddings.EMBED_TIMEOUT = 20.0
    print("denso:", "hibrida (API)" if hibrida else "apagado, solo BM25")
    retriever = _retriever()
    for etiqueta, path in (("tuning", GOLD_TUNING_PATH), ("test", GOLD_TEST_PATH)):
        entries = _leer(path)
        print(f"\n{etiqueta}")
        _tabla(retriever, entries, "bm25")
        if hibrida:
            _tabla(retriever, entries, "hibrida")
        _negativas(retriever, entries, etiqueta)
    print()
    _casos(retriever)


if __name__ == "__main__":
    main()
