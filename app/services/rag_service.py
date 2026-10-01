"""Acceso al recuperador híbrido (lazy: el modelo solo se carga al usarlo)."""

from rag.hybrid import HybridRetriever

_retriever: HybridRetriever | None = None


def get_retriever() -> HybridRetriever:
    global _retriever
    if _retriever is None:
        _retriever = HybridRetriever()
    return _retriever


def set_retriever(retriever) -> None:
    """Costura de inyección para tests."""
    global _retriever
    _retriever = retriever


def enrich(hits: list[dict]) -> list[dict]:
    """Agrega cita legible y URL de salto al PDF con página."""
    out = []
    for h in hits:
        item = dict(h)
        item["citation"] = f"📄 {h['title']}, p. {h['page']}"
        item["url"] = f"/corpus/{h['doc_id']}.pdf#page={h['page']}"
        out.append(item)
    return out


def search(query: str, top_k: int = 5) -> list[dict]:
    return enrich(get_retriever().search(query, top_k))
