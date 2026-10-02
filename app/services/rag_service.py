"""Acceso al recuperador híbrido (lazy: el modelo solo se carga al usarlo)."""

import re
import unicodedata

from rag import hybrid as _hybrid
from rag.hybrid import HybridRetriever

_retriever: HybridRetriever | None = None

_ACCENT_RE = re.compile(r"[̀-ͯ]")
_PATH_RE = re.compile(r"(?:[A-Za-z]:\\[^\s\"'<>|]+|(?:/[\w.-]+)+)")
_SNIPPET_LEN = 200
_SNIPPET_BEFORE = 80


def get_retriever() -> HybridRetriever:
    global _retriever
    if _retriever is None:
        _retriever = HybridRetriever()
    return _retriever


def set_retriever(retriever) -> None:
    """Costura de inyección para tests."""
    global _retriever
    _retriever = retriever


def enrich(hits: list[dict], query: str = "") -> list[dict]:
    """Agrega cita legible, URL de salto al PDF y snippet de lectura."""
    out = []
    for h in hits:
        item = dict(h)
        item["citation"] = f"📄 {h['title']}, p. {h['page']}"
        item["url"] = f"/corpus/{h['doc_id']}.pdf#page={h['page']}"
        item["snippet"] = _snippet(h["text"], query)
        out.append(item)
    return out


def _norm(text: str) -> str:
    return _ACCENT_RE.sub("", unicodedata.normalize("NFD", text.lower()))


def _snippet(text: str, query: str) -> str:
    """Ventana de ~200 chars centrada en la palabra de la query más larga
    que aparezca en el fragmento; sin coincidencia, la cabecera del texto."""
    flat = re.sub(r"\s+", " ", text).strip()
    norm = _norm(flat)
    words = set(re.findall(r"[a-z0-9]{4,}", _norm(query)))
    pos = next((norm.find(w) for w in sorted(words, key=len, reverse=True)
                if w in norm), 0)
    start = max(0, pos - _SNIPPET_BEFORE)
    end = min(len(flat), start + _SNIPPET_LEN)
    snip = flat[start:end]
    if start > 0:
        snip = "…" + snip
    if end < len(flat):
        snip += "…"
    return snip


def last_dense_error() -> str | None:
    """Último error denso, saneado: rutas locales fuera (viaja al cliente
    vía /api/health)."""
    err = _hybrid.LAST_DENSE_ERROR
    if err is None:
        return None
    return _PATH_RE.sub("<ruta>", err)[:200]


def search(query: str, top_k: int = 5) -> list[dict]:
    return enrich(get_retriever().search(query, top_k), query)
