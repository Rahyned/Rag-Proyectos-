"""Configuración del paquete RAG (rutas y parámetros)."""

import os
from pathlib import Path

if os.getenv("VERCEL") == "1":
    # FS del contenedor read-only salvo /tmp: redirigir las descargas del
    # modelo de embeddings (hf_xet escribía fuera del caché y fallaba EROFS).
    os.environ.setdefault("FASTEMBED_CACHE_PATH", "/tmp/fastembed")
    os.environ.setdefault("HF_HOME", "/tmp/fastembed-hf")
    os.environ.setdefault("HF_HUB_DISABLE_XET", "1")

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
# Bonus por bigrama de la query con tokens adyacentes en el documento
# ("agregar un cliente" → agreg|client). Calibrado sobre el gold: con 1.5
# el top3 es 12/12; con < 1.0 la página buena no alcanza a entrar.
BM25_BIGRAM_BONUS = 1.5


def dense_enabled() -> bool:
    """¿Usar el canal denso (modelo + FAISS) en `search`?

    En Vercel arranca apagado (sin descarga de modelo en frío); `RAG_DENSE=1`
    lo fuerza. Fuera de Vercel queda encendido por defecto.
    """
    flag = os.environ.get("RAG_DENSE")
    if flag is not None:
        return flag.strip().lower() not in ("0", "false", "no", "")
    return os.environ.get("VERCEL") != "1"
