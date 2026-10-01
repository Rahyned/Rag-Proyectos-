"""Extracción de texto por página y chunking page-aware.

Cada chunk conserva (doc_id, título, página) para que las citas apunten a
`documento.pdf#page=N`.
"""

import re
from dataclasses import asdict, dataclass
from pathlib import Path

from pypdf import PdfReader

from .config import CHUNK_MAX_CHARS, CHUNK_OVERLAP

_SENT_RE = re.compile(r"(?<=[.!?])\s+")


@dataclass
class Chunk:
    chunk_id: str
    doc_id: str
    title: str
    page: int
    text: str

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


def chunk_pdf(pdf_path: Path, doc_id: str, title: str) -> list[Chunk]:
    chunks: list[Chunk] = []
    for page in extract_pages(pdf_path, doc_id, title):
        for j, piece in enumerate(split_page(page["text"])):
            chunks.append(Chunk(
                chunk_id=f"{doc_id}:p{page['page']}:{j}",
                doc_id=page["doc_id"],
                title=page["title"],
                page=page["page"],
                text=piece,
            ))
    return chunks
