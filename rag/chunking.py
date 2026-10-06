"""Chunking de PDF (por página) y de Markdown (por encabezados).

El PDF conserva la página para el enlace `#page=N`. El Markdown corta en
`#` / `##` / `###`, no aplana tablas y antepone
«Proyecto › Documento › Sección» al texto que se indexa.
"""

import re
import unicodedata
from dataclasses import asdict, dataclass
from pathlib import Path

from pypdf import PdfReader

from .config import CHUNK_MAX_CHARS, CHUNK_OVERLAP

_SENT_RE = re.compile(r"(?<=[.!?])\s+")
_HEADING_RE = re.compile(r"^(#{1,3})\s+(.+?)\s*$")
_TABLE_RE = re.compile(r"^\s*\|.+\|\s*$")
_SEP_RE = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$")
_ACCENT_RE = re.compile(r"[\u0300-\u036f]")
_TOKEN_PAGINA = re.compile(r"[a-z0-9]{4,}")
MIN_CHUNK_CHARS = 40


@dataclass
class Chunk:
    chunk_id: str
    doc_id: str
    title: str
    page: int | None
    text: str
    proyecto: str = ""
    proyecto_nombre: str = ""
    tipo: str = ""
    seccion: str = ""
    publico: bool = False
    pdf: str | None = None
    url_publica: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def clean_text(text: str) -> str:
    text = text.replace("\u00ad", "").replace("-\n", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_page(text: str, max_chars: int = CHUNK_MAX_CHARS,
               overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Divide el texto de una página en fragmentos; nunca cruza páginas."""
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    pieces: list[str] = []
    current = ""
    for para in paragraphs:
        candidate = f"{current}\n\n{para}" if current else para
        if len(candidate) <= max_chars:
            current = candidate
            continue
        if current:
            pieces.append(current)
        if len(para) <= max_chars:
            current = para
        else:
            sentences = _SENT_RE.split(para)
            current = ""
            for sentence in sentences:
                cand = f"{current} {sentence}".strip() if current else sentence
                if len(cand) <= max_chars:
                    current = cand
                else:
                    if current:
                        pieces.append(current)
                    current = sentence
            continue
    if current:
        pieces.append(current)

    out: list[str] = []
    for piece in pieces:
        if out and overlap > 0:
            tail = out[-1][-overlap:]
            cut = tail.find(" ")
            if cut != -1:
                piece = tail[cut + 1:] + piece
        out.append(piece)
    return out


def extract_pages(pdf_path: Path, doc_id: str, title: str) -> list[dict]:
    reader = PdfReader(str(pdf_path))
    pages = []
    for i, page in enumerate(reader.pages, start=1):
        text = clean_text(page.extract_text() or "")
        if text:
            pages.append({"doc_id": doc_id, "title": title,
                          "page": i, "text": text})
    return pages


def chunk_pdf(pdf_path: Path, doc_id: str, title: str, **meta) -> list[Chunk]:
    chunks: list[Chunk] = []
    for page in extract_pages(pdf_path, doc_id, title):
        for j, piece in enumerate(split_page(page["text"])):
            chunks.append(Chunk(
                chunk_id=f"{doc_id}:p{page['page']}:{j}",
                doc_id=page["doc_id"],
                title=page["title"],
                page=page["page"],
                text=piece,
                **meta,
            ))
    return chunks


def _es_tabla(texto: str) -> bool:
    lineas = [ln for ln in texto.splitlines() if ln.strip()]
    return bool(lineas) and all(_TABLE_RE.match(ln) for ln in lineas)


def _partir_tabla(tabla: str, max_chars: int) -> list[str]:
    """Una tabla entera, o grupos de filas que repiten el encabezado."""
    if len(tabla) <= max_chars:
        return [tabla]
    filas = tabla.splitlines()
    if len(filas) < 3:
        return [tabla]
    resto = filas[1:]
    sep: list[str] = []
    if _SEP_RE.match(resto[0]):
        sep = [resto[0]]
        resto = resto[1:]
    cabeza = "\n".join([filas[0], *sep])
    grupos: list[str] = []
    actual: list[str] = []
    for fila in resto:
        cand_filas = [cabeza, *actual, fila] if actual else [cabeza, fila]
        cand = "\n".join(cand_filas)
        if actual and len(cand) > max_chars:
            grupos.append("\n".join([cabeza, *actual]))
            actual = [fila]
        else:
            actual.append(fila)
    if actual:
        grupos.append("\n".join([cabeza, *actual]))
    return grupos or [tabla]


def _bloques(body: str) -> list[tuple[str, bool]]:
    """Párrafos y tablas. El bool indica si el bloque es una tabla."""
    lineas = body.splitlines()
    bloques: list[tuple[str, bool]] = []
    para: list[str] = []

    def flush_para() -> None:
        texto = "\n".join(para).strip()
        para.clear()
        if texto:
            bloques.append((texto, False))

    i = 0
    while i < len(lineas):
        if _TABLE_RE.match(lineas[i]):
            flush_para()
            tabla: list[str] = []
            while i < len(lineas) and _TABLE_RE.match(lineas[i]):
                tabla.append(lineas[i].rstrip())
                i += 1
            bloques.append(("\n".join(tabla), True))
            continue
        if not lineas[i].strip():
            flush_para()
            i += 1
            continue
        para.append(lineas[i])
        i += 1
    flush_para()
    return bloques


def _empaquetar(bloques: list[tuple[str, bool]], max_chars: int) -> list[str]:
    piezas: list[str] = []
    actual = ""
    for texto, es_tabla in bloques:
        partes = _partir_tabla(texto, max_chars) if es_tabla else [texto]
        for parte in partes:
            if es_tabla:
                if actual:
                    piezas.append(actual)
                    actual = ""
                piezas.append(parte)
                continue
            if len(parte) > max_chars:
                if actual:
                    piezas.append(actual)
                    actual = ""
                for pedazo in split_page(parte, max_chars=max_chars, overlap=0):
                    piezas.append(pedazo)
                continue
            cand = f"{actual}\n\n{parte}" if actual else parte
            if len(cand) <= max_chars:
                actual = cand
            else:
                if actual:
                    piezas.append(actual)
                actual = parte
    if actual:
        piezas.append(actual)
    return piezas


def _fusionar_cortos(piezas: list[str], max_chars: int) -> list[str]:
    """No deja fragmentos de prosa con menos de MIN_CHUNK_CHARS."""
    if not piezas:
        return []
    out: list[str] = []
    for pieza in piezas:
        corta = len(pieza) < MIN_CHUNK_CHARS and not _es_tabla(pieza)
        if out and corta and not _es_tabla(out[-1]):
            out[-1] = f"{out[-1]}\n\n{pieza}"
        elif (
            out
            and len(out[-1]) < MIN_CHUNK_CHARS
            and not _es_tabla(out[-1])
            and not _es_tabla(pieza)
            and len(out[-1]) + 2 + len(pieza) <= max_chars
        ):
            out[-1] = f"{out[-1]}\n\n{pieza}"
        else:
            out.append(pieza)
    i = 0
    while i < len(out) - 1:
        if len(out[i]) < MIN_CHUNK_CHARS and not _es_tabla(out[i]):
            out[i + 1] = f"{out[i]}\n\n{out[i + 1]}"
            out.pop(i)
            continue
        i += 1
    return out


def _secciones(texto: str) -> list[tuple[str, str]]:
    stack: list[tuple[int, str]] = []
    buf: list[str] = []
    out: list[tuple[str, str]] = []

    def ruta() -> str:
        return " › ".join(titulo for _, titulo in stack)

    def flush() -> None:
        body = "\n".join(buf).strip()
        buf.clear()
        if body:
            out.append((ruta(), body))

    for line in texto.splitlines():
        m = _HEADING_RE.match(line)
        if m:
            flush()
            level = len(m.group(1))
            titulo = m.group(2).strip()
            while stack and stack[-1][0] >= level:
                stack.pop()
            stack.append((level, titulo))
            continue
        buf.append(line)
    flush()
    return out


def _prefijo(proyecto_nombre: str, title: str, seccion: str) -> str:
    partes = [proyecto_nombre, title]
    if seccion:
        partes.append(seccion)
    return " › ".join(partes)


def chunk_markdown(texto: str, doc_id: str, title: str, *,
                   proyecto: str, proyecto_nombre: str, tipo: str,
                   publico: bool, pdf: str | None,
                   url_publica: str | None,
                   max_chars: int = CHUNK_MAX_CHARS) -> list[Chunk]:
    """Corta por encabezados. El prefijo se agrega después de asignar páginas."""
    crudos: list[tuple[str, str]] = []
    for seccion, body in _secciones(texto):
        pref = _prefijo(proyecto_nombre, title, seccion)
        presupuesto = max(200, max_chars - len(pref) - 2)
        for pieza in _fusionar_cortos(_empaquetar(_bloques(body), presupuesto), presupuesto):
            crudos.append((seccion, pieza))
    # Un encabezado suelto de menos de 40 caracteres se pega al vecino.
    fusion: list[tuple[str, str]] = []
    for seccion, pieza in crudos:
        if (
            fusion
            and len(pieza) < MIN_CHUNK_CHARS
            and not _es_tabla(pieza)
            and not _es_tabla(fusion[-1][1])
        ):
            ant_sec, ant = fusion[-1]
            fusion[-1] = (ant_sec, f"{ant}\n\n{pieza}")
        else:
            fusion.append((seccion, pieza))
    chunks: list[Chunk] = []
    for n, (seccion, pieza) in enumerate(fusion):
        if len(pieza) < MIN_CHUNK_CHARS and not _es_tabla(pieza):
            continue
        chunks.append(Chunk(
            chunk_id=f"{doc_id}:s{n}",
            doc_id=doc_id,
            title=title,
            page=None,
            text=pieza,
            proyecto=proyecto,
            proyecto_nombre=proyecto_nombre,
            tipo=tipo,
            seccion=seccion,
            publico=publico,
            pdf=pdf,
            url_publica=url_publica,
        ))
    return chunks


def anteponer_ruta(chunks: list[Chunk]) -> None:
    """Agrega «Proyecto › Documento › Sección» al texto indexado."""
    for chunk in chunks:
        pref = _prefijo(chunk.proyecto_nombre, chunk.title, chunk.seccion)
        if not chunk.text.startswith(pref):
            chunk.text = f"{pref}\n\n{chunk.text}"


def _tokens_pagina(texto: str) -> set[str]:
    plano = unicodedata.normalize("NFD", texto.lower())
    plano = _ACCENT_RE.sub("", plano)
    return set(_TOKEN_PAGINA.findall(plano))


def asignar_paginas(chunks: list[Chunk], pdf_path: Path) -> None:
    """Copia la página del PDF cuyo texto más se parece al chunk."""
    paginas = extract_pages(pdf_path, "", "")
    if not paginas:
        return
    preparados = [
        (p["page"], _tokens_pagina(p["text"]))
        for p in paginas
    ]
    for chunk in chunks:
        consulta = chunk.seccion + "\n" + chunk.text
        tokens = _tokens_pagina(consulta)
        if not tokens:
            continue
        mejor_pag = None
        mejor = 0.0
        for page, toks in preparados:
            if not toks:
                continue
            score = len(tokens & toks) / len(tokens)
            if score > mejor:
                mejor = score
                mejor_pag = page
        if mejor_pag is not None and mejor >= 0.2:
            chunk.page = mejor_pag


def reasignar_ids(chunks: list[Chunk]) -> None:
    """`doc:pN:j` cuando hay página (compatible con el manual de STELLA)."""
    contador: dict[tuple, int] = {}
    for chunk in chunks:
        if isinstance(chunk.page, int):
            clave = (chunk.doc_id, chunk.page)
            n = contador.get(clave, 0)
            contador[clave] = n + 1
            chunk.chunk_id = f"{chunk.doc_id}:p{chunk.page}:{n}"
