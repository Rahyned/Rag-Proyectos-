"""Configuración del paquete RAG (rutas y parámetros)."""

import json
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

# Modelo ONNX local. No es necesariamente el del índice: el índice se puede
# haber generado con la API de Jina o con Cloudflare.
LOCAL_EMBED_MODEL = "jinaai/jina-embeddings-v2-base-es"


def _modelo_del_indice() -> str:
    """Modelo con el que se embebió data/index.faiss, leído de la meta.

    Si la meta falta o está rota, cae al modelo local para no romper el
    arranque. Así consulta e índice no quedan desincronizados por una
    constante escrita a mano.
    """
    try:
        meta = json.loads(
            (DATA_DIR / "ingest_meta.json").read_text(encoding="utf-8")
        )
        modelo = meta.get("embed_model")
    except (OSError, ValueError, TypeError):
        return LOCAL_EMBED_MODEL
    if isinstance(modelo, str) and modelo.strip():
        return modelo.strip()
    return LOCAL_EMBED_MODEL


EMBED_MODEL = _modelo_del_indice()
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
    """`local` (fastembed), `api` (Jina), `cloudflare` u `off` (solo BM25).

    `EMBEDDINGS_PROVIDER` gana. Si no está, `RAG_DENSE=0` apaga el denso y
    `RAG_DENSE=1` usa el modelo local. En Vercel, sin ninguna de las dos,
    el default es `cloudflare` (Workers AI no descarga un ONNX de ~640 MB
    en el cold start). Fuera de Vercel el default es `local`.
    """
    raw = os.getenv("EMBEDDINGS_PROVIDER", "").strip().lower()
    if raw in ("local", "api", "cloudflare", "off"):
        return raw
    flag = os.environ.get("RAG_DENSE")
    if flag is not None:
        apagado = flag.strip().lower() in ("0", "false", "no", "")
        return "off" if apagado else "local"
    if os.environ.get("VERCEL") == "1":
        return "cloudflare"
    return "local"


def dense_enabled() -> bool:
    """True si esta consulta va a intentar el canal denso (local o API)."""
    return embeddings_provider() != "off"


def _float_env(name: str, default: float) -> float:
    """Lee un float del entorno; si falta o no es válido, usa el default."""
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        valor = float(raw)
    except ValueError:
        return default
    return valor if valor > 0 else default


def _int_env(name: str, default: int) -> int:
    """Lee un int positivo del entorno; si falta, no es válido o es <= 0, usa el default."""
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        valor = int(raw)
    except ValueError:
        return default
    return valor if valor > 0 else default


def rerank_enabled() -> bool:
    """`RERANK_ENABLED=1|true|si|yes|on` activa el reranker. Default: apagado."""
    raw = os.getenv("RERANK_ENABLED", "").strip().lower()
    return raw in ("1", "true", "si", "sí", "yes", "on")


def rerank_top_n() -> int:
    """Candidatos que recibe el reranker. Vacío o inválido = 20."""
    return _int_env("RERANK_TOP_N", 20)


def rerank_keep() -> int:
    """Hits que sobreviven al reranker (tope del top_k). Vacío o inválido = 5."""
    return _int_env("RERANK_KEEP", 5)


# Modelo servido por la API de Jina. Mismo espacio que el ONNX local si el
# coseno de los mismos textos da ≥ 0.99; si no, el índice se rehace con la API.
JINA_EMBED_MODEL = "jina-embeddings-v2-base-es"
JINA_EMBED_URL = "https://api.jina.ai/v1/embeddings"
# Cloudflare Workers AI: bge-m3 devuelve 1024 dimensiones. El índice se
# normaliza L2 porque usa IndexFlatIP.
CF_EMBED_MODEL = "@cf/baai/bge-m3"
CF_EMBED_URL = (
    "https://api.cloudflare.com/client/v4/accounts/"
    "{account_id}/ai/run/@cf/baai/bge-m3"
)
# Con una API lenta es preferible responder por BM25 antes que esperar de más.
EMBED_TIMEOUT = _float_env("EMBED_TIMEOUT_S", 2.0)
EMBED_CACHE_SIZE = 500

# Reranker de Workers AI: recibe la consulta y los textos candidatos y
# devuelve un score por pasaje. Mismo cupo y credenciales que los embeddings.
CF_RERANK_MODEL = "@cf/baai/bge-reranker-base"
CF_RERANK_URL = (
    "https://api.cloudflare.com/client/v4/accounts/"
    "{account_id}/ai/run/@cf/baai/bge-reranker-base"
)
# Presupuesto de la consulta completa: si el reranker tarda más, se responde
# con el orden del RRF (la latencia no se negocia con el usuario esperando).
RERANK_TIMEOUT = 2.0
