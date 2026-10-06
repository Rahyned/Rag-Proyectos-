"""Compara el coseno entre fastembed y la API de Jina para los mismos textos.

Uso (con JINA_API_KEY en el entorno, sin imprimirla):

    uv run python scripts/comparar_embeddings.py

Si el mínimo es < 0.99, el índice local no es compatible con las consultas
por API: reindexá con `uv run python scripts/ingest.py --provider api`.
"""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from rag.embeddings import JinaEmbeddings, LocalEmbeddings  # noqa: E402

TEXTOS = [
    "STELLA es un sistema de gestión para laboratorios odontológicos.",
    "¿Cómo agrego un cliente nuevo al sistema?",
    "La cuenta corriente registra debe, haber y saldo.",
]


def main() -> None:
    if not os.getenv("JINA_API_KEY", "").strip():
        sys.exit("Falta JINA_API_KEY: no se puede comparar.")
    local = LocalEmbeddings().embed_lote(TEXTOS)
    remoto = JinaEmbeddings().embed_lote(TEXTOS, timeout=30.0)
    if local.shape[1] != remoto.shape[1]:
        sys.exit(f"dimensión distinta: local {local.shape[1]} api {remoto.shape[1]}")
    cosenos = (local * remoto).sum(axis=1)
    for texto, valor in zip(TEXTOS, cosenos):
        print(f"{float(valor):.4f}  {texto[:60]}")
    minimo = float(cosenos.min())
    print(f"mínimo {minimo:.4f}")
    if minimo < 0.99:
        sys.exit("por debajo de 0.99: reindexá con --provider api")
    print("compatible con el índice local")


if __name__ == "__main__":
    main()
