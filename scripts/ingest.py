"""Ingesta page-aware: corpus/*.pdf -> chunks.jsonl + FAISS.

Uso:  python scripts/ingest.py [--sin-embed]  (solo chunks, sin modelo)
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from rag.chunking import chunk_pdf  # noqa: E402
from rag.config import (CHUNKS_PATH, CORPUS_DIR, DATA_DIR,  # noqa: E402
                        EMBED_MODEL, INDEX_PATH)

TITLES = {
    "manual-stella": "Manual STELLA",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sin-embed", action="store_true",
                        help="Solo extraer chunks, sin generar el índice")
    args = parser.parse_args()

    pdfs = sorted(p for p in CORPUS_DIR.glob("*.pdf")
                  if not p.name.startswith("_"))
    if not pdfs:
        sys.exit(f"No hay PDFs en {CORPUS_DIR}")

    DATA_DIR.mkdir(exist_ok=True)
    all_chunks = []
    for pdf in pdfs:
        doc_id = pdf.stem
        title = TITLES.get(doc_id, doc_id)
        chunks = chunk_pdf(pdf, doc_id, title)
        all_chunks.extend(chunks)
        pages = {c.page for c in chunks}
        print(f"{pdf.name}: {len(chunks)} chunks, páginas {min(pages)}-{max(pages)}")

    with open(CHUNKS_PATH, "w", encoding="utf-8") as f:
        for chunk in all_chunks:
            f.write(json.dumps(chunk.to_dict(), ensure_ascii=False) + "\n")
    print(f"OK -> {CHUNKS_PATH} ({len(all_chunks)} chunks)")

    if args.sin_embed:
        return

    from fastembed import TextEmbedding

    model = TextEmbedding(model_name=EMBED_MODEL)
    texts = [c.text for c in all_chunks]
    vectors = np.asarray(list(model.embed(texts)), dtype=np.float32)
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    vectors = vectors / np.clip(norms, 1e-9, None)

    import faiss

    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)
    faiss.write_index(index, str(INDEX_PATH))
    print(f"OK -> {INDEX_PATH} ({index.ntotal} vectores, dim={vectors.shape[1]})")


if __name__ == "__main__":
    main()
