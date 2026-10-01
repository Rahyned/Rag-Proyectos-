"""Genera corpus/manual-stella.pdf desde corpus/manual-stella.md.

Usa Markdown -> HTML -> impresión headless de Edge/Chrome. El PDF resultante
es la fuente para el ingesta page-aware (scripts/ingest.py).
"""

import shutil
import subprocess
import sys
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "corpus" / "manual-stella.md"
OUT = ROOT / "corpus" / "manual-stella.pdf"
HTML = ROOT / "corpus" / "_manual-stella.html"

CSS = """
@page { size: A4; margin: 22mm 19mm; }
* { box-sizing: border-box; }
body {
  font-family: 'Segoe UI', system-ui, sans-serif;
  font-size: 11pt; line-height: 1.65; color: #1c1c28;
  margin: 0;
}
h1 {
  font-size: 20pt; color: #252850; margin: 0 0 16pt;
  padding-bottom: 7pt; border-bottom: 2.5pt solid #00bcd4;
  page-break-before: always; break-before: page;
}
h1:first-of-type { page-break-before: avoid; break-before: avoid; }
h2 { font-size: 14pt; color: #252850; margin: 18pt 0 7pt; }
h3 { font-size: 12pt; color: #3a3a6a; margin: 14pt 0 5pt; }
p { margin: 0 0 9pt; text-align: justify; }
table {
  border-collapse: collapse; width: 100%; margin: 9pt 0 14pt;
  font-size: 10pt; page-break-inside: auto;
}
th {
  background: #252850; color: #fff; text-align: left;
  padding: 6pt 8pt; font-weight: 600;
}
td { border-bottom: 0.75pt solid #d7d7e2; padding: 5.5pt 8pt; vertical-align: top; }
tr:nth-child(even) td { background: #f4f5fa; }
code, pre {
  font-family: Consolas, 'Courier New', monospace; font-size: 10pt;
}
pre {
  background: #1a1a2e; color: #d8d7e0; padding: 10pt 12pt;
  border-radius: 5pt; overflow: hidden; white-space: pre-wrap;
}
blockquote {
  margin: 10pt 0; padding: 8pt 12pt; background: #fff6e6;
  border-left: 3pt solid #f5a623; color: #5a4200;
}
strong { color: #252850; }
ul, ol { margin: 5pt 0 10pt; padding-left: 22pt; }
li { margin-bottom: 5pt; }
hr { border: none; border-top: 0.75pt solid #d7d7e2; margin: 16pt 0; }
.cover {
  page-break-after: always; break-after: page;
  height: 240mm; text-align: center; padding-top: 70mm;
}
.cover .mark {
  font-size: 14pt; letter-spacing: 6pt; color: #00bcd4;
  text-transform: uppercase; margin-bottom: 18mm;
}
.cover .title {
  font-size: 34pt; font-weight: 700; color: #252850; margin-bottom: 8mm;
}
.cover .sub {
  font-size: 14pt; color: #3a3a6a; margin-bottom: 30mm; line-height: 1.5;
}
.cover .rule {
  width: 60mm; border-top: 3pt solid #00bcd4; margin: 0 auto 14mm;
}
.cover .meta { font-size: 11pt; color: #55556a; line-height: 1.8; }
.cover .legal { font-size: 9pt; color: #8a8a9a; margin-top: 40mm; }
"""

COVER = """
<div class="cover">
  <div class="mark">Sistema de gestión</div>
  <div class="title">STELLA</div>
  <div class="sub">Manual de Usuario<br>Guía completa del laboratorio digital</div>
  <div class="rule"></div>
  <div class="meta">
    Versión 1.6.4<br>
    Edición de septiembre de 2026<br>
    Documentación en español
  </div>
  <div class="legal">Documento generado para el asistente documental &mdash; STELLA</div>
</div>
"""

BROWSERS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]


def find_browser() -> Path:
    for raw in BROWSERS:
        p = Path(raw)
        if p.exists():
            return p
    for name in ("msedge", "chrome", "chromium"):
        found = shutil.which(name)
        if found:
            return Path(found)
    sys.exit("No se encontró Edge ni Chrome para generar el PDF.")


def main() -> None:
    text = SRC.read_text(encoding="utf-8")
    body = markdown.markdown(text, extensions=["tables", "fenced_code"])
    html = (
        "<!doctype html><html lang='es'><head><meta charset='utf-8'>"
        f"<title>Manual STELLA</title><style>{CSS}</style></head>"
        f"<body>{COVER}{body}</body></html>"
    )
    HTML.write_text(html, encoding="utf-8")

    browser = find_browser()
    subprocess.run(
        [
            str(browser),
            "--headless",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--print-to-pdf={OUT}",
            HTML.resolve().as_uri(),
        ],
        check=True,
        capture_output=True,
        timeout=120,
    )
    HTML.unlink(missing_ok=True)

    try:
        from pypdf import PdfReader

        pages = len(PdfReader(str(OUT)).pages)
    except ImportError:
        pages = -1
    print(f"OK -> {OUT} ({pages} páginas)")


if __name__ == "__main__":
    main()
