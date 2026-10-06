"""Cita legible: Proyecto · Documento · Sección (pág. N)."""


def formatear_cita(hit: dict) -> str:
    proyecto = (hit.get("proyecto_nombre") or "").strip()
    documento = (hit.get("title") or "").strip()
    seccion = (hit.get("seccion") or "").strip()
    partes = [p for p in (proyecto, documento, seccion) if p]
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
