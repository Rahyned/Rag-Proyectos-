"""Cita legible: Proyecto · Documento · Sección (pág. N)."""

from rag.chunking import segmentos_sin_repetir


def formatear_cita(hit: dict) -> str:
    proyecto = (hit.get("proyecto_nombre") or "").strip()
    documento = (hit.get("title") or "").strip()
    seccion = (hit.get("seccion") or "").strip()
    # Mismo criterio que la ruta del chunk: no repetir el nombre seguido.
    planos = segmentos_sin_repetir([p for p in (proyecto, documento, seccion) if p])
    partes: list[str] = []
    resto = list(planos)
    for slot in (proyecto, documento):
        if resto and slot and resto[0] == slot:
            partes.append(resto.pop(0))
        elif resto and slot and " ".join(resto[0].split()).casefold() == " ".join(slot.split()).casefold():
            partes.append(resto.pop(0))
    if resto:
        partes.append(" › ".join(resto))
    cita = " · ".join(partes) if partes else documento or "fuente"
    page = hit.get("page")
    if isinstance(page, int) and page > 0:
        cita += f" (pág. {page})"
    return cita


def url_cita(hit: dict) -> str | None:
    """Enlace solo si el documento es público y hay PDF con página o URL del proyecto."""
    if not hit.get("publico"):
        return None
    pdf = hit.get("pdf")
    page = hit.get("page")
    if pdf and isinstance(page, int) and page > 0:
        return f"corpus/{pdf}#page={page}"
    url = hit.get("url_publica")
    if isinstance(url, str) and url.startswith(("http://", "https://")):
        return url
    return None
