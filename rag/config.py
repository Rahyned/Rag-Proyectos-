"""Configuración del paquete RAG (rutas y parámetros)."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORPUS_DIR = ROOT / "corpus"
DATA_DIR = ROOT / "data"

CHUNKS_PATH = DATA_DIR / "chunks.jsonl"
INDEX_PATH = DATA_DIR / "index.faiss"
GOLD_PATH = DATA_DIR / "gold_set.json"

EMBED_MODEL = "jinaai/jina-embeddings-v2-base-es"
CHUNK_MAX_CHARS = 1200
CHUNK_OVERLAP = 150

TOP_K = 5
DENSE_POOL_FACTOR = 3
RRF_K = 60
BM25_K1 = 1.5
BM25_B = 0.75
