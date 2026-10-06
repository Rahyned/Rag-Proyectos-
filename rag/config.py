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


def embeddings_provider() -> str:
    """`local` (fastembed), `api` (Jina) u `off` (solo BM25).

    `EMBEDDINGS_PROVIDER` gana. Si no está, `RAG_DENSE=0` apaga el denso y
    `RAG_DENSE=1` usa el modelo local. En Vercel, sin ninguna de las dos,
    el default es `api` (el ONNX de ~640 MB no entra en el cold start).
    Fuera de Vercel el default es `local`.
    """
    raw = os.getenv("EMBEDDINGS_PROVIDER", "").strip().lower()
    if raw in ("local", "api", "off"):
        return raw
    flag = os.environ.get("RAG_DENSE")
    if flag is not None:
        apagado = flag.strip().lower() in ("0", "false", "no", "")
        return "off" if apagado else "local"
    if os.environ.get("VERCEL") == "1":
        return "api"
    return "local"


def dense_enabled() -> bool:
    """True si esta consulta va a intentar el canal denso (local o API)."""
    return embeddings_provider() != "off"


# Modelo servido por la API de Jina. Mismo espacio que el ONNX local si el
# coseno de los mismos textos da ≥ 0.99; si no, el índice se rehace con la API.
JINA_EMBED_MODEL = "jina-embeddings-v2-base-es"
JINA_EMBED_URL = "https://api.jina.ai/v1/embeddings"
EMBED_TIMEOUT = 3.0
EMBED_CACHE_SIZE = 500
