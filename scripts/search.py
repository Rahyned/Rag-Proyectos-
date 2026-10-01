"""Prueba rápida de recuperación desde la terminal.

Uso:  python scripts/search.py "cómo cargo un cliente" [--bm25] [-k 5]
"""

import argparse
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from rag.hybrid import HybridRetriever  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("--bm25", action="store_true",
                        help="Solo léxico (no descarga el modelo)")
    parser.add_argument("-k", type=int, default=5)
    args = parser.parse_args()

    retriever = HybridRetriever()
    hits = (retriever.bm25(args.query, args.k) if args.bm25
            else retriever.search(args.query, args.k))
    if not hits:
        print("Sin resultados.")
        return
    for h in hits:
        print(f"#{h['rank']} [score={h['score']:.4f}] "
              f"{h['title']} · pág. {h['page']} ({h['chunk_id']})")
        print("   " + h["text"][:200].replace("\n", " ") + "…\n")


if __name__ == "__main__":
    main()
