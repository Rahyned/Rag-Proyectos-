"""Ingesta multi-proyecto: corpus/<proyecto>/*.(md|pdf) -> chunks + FAISS.

Uso:
  python scripts/ingest.py [--sin-embed] [--provider local|api|cloudflare]
  python scripts/ingest.py --limit 3 --provider cloudflare
    prueba los primeros N chunks y no escribe chunks, índice ni meta.
  python scripts/ingest.py --check
    valida el manifiesto, corre el guardrail de secretos y compara el hash
    del corpus con el que quedó guardado al ingerir. No reindexa.
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from rag.chunking import (anteponer_ruta, asignar_paginas, chunk_markdown,  # noqa: E402
                          chunk_pdf, reasignar_ids)
from rag.config import (CF_EMBED_MODEL, CHUNKS_PATH, CORPUS_DIR,  # noqa: E402
                        DATA_DIR, INDEX_PATH, JINA_EMBED_MODEL,
                        LOCAL_EMBED_MODEL)
from rag.manifiesto import ManifiestoError, cargar, limpiar_cache  # noqa: E402
from rag.secretos import SecretosError, revisar_nombre, revisar_texto  # noqa: E402

META_PATH = DATA_DIR / "ingest_meta.json"
HASH_PATH = DATA_DIR / "corpus.sha256"


def hash_corpus(corpus_dir: Path = CORPUS_DIR) -> str:
    """Hash estable de los archivos del corpus (sin los que empiezan con _)."""
    digest = hashlib.sha256()
    archivos = []
    for path in corpus_dir.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(corpus_dir)
        if any(parte.startswith("_") for parte in rel.parts):
            continue
        archivos.append((rel.as_posix(), path))
    for rel, path in sorted(archivos):
        digest.update(rel.encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _rel(path: Path) -> str:
    return path.relative_to(CORPUS_DIR).as_posix()


def revisar_documento(path: Path, emails: list[str]) -> None:
    revisar_nombre(path)
    origen = _rel(path)
    if path.suffix.lower() == ".md":
        revisar_texto(path.read_text(encoding="utf-8"), origen, emails)
        return
    from pypdf import PdfReader

    texto = "\n".join(
        (pagina.extract_text() or "") for pagina in PdfReader(str(path)).pages
    )
    revisar_texto(texto, origen, emails)
    crudo = path.read_bytes()
    if b"PRIVATE KEY" in crudo:
        raise SecretosError(f"{origen}: se detectó una clave privada")


def construir_chunks() -> list:
    limpiar_cache()
    data = cargar()
    emails = data["emails_publicos"]
    chunks = []
    for proyecto in data["proyectos"]:
        for doc in proyecto["documentos"]:
            path: Path = doc["path"]
            revisar_documento(path, emails)
            doc_id = path.stem
            pdf_rel = None
            if path.suffix.lower() == ".pdf":
                pdf_rel = _rel(path)
            else:
                hermano = path.with_suffix(".pdf")
                if hermano.is_file():
                    pdf_rel = _rel(hermano)
                    revisar_documento(hermano, emails)
            meta = dict(
                proyecto=proyecto["id"],
                proyecto_nombre=proyecto["nombre"],
                tipo=doc["tipo"],
                publico=doc["publico"],
                pdf=pdf_rel,
                url_publica=proyecto["url"],
            )
            if path.suffix.lower() == ".md":
                texto = path.read_text(encoding="utf-8")
                nuevos = chunk_markdown(
                    texto, doc_id, doc["titulo"], **meta,
                )
                if pdf_rel:
                    asignar_paginas(nuevos, CORPUS_DIR / pdf_rel)
            else:
                nuevos = chunk_pdf(path, doc_id, doc["titulo"], **meta)
                for chunk in nuevos:
                    chunk.proyecto = proyecto["id"]
                    chunk.proyecto_nombre = proyecto["nombre"]
                    chunk.tipo = doc["tipo"]
                    chunk.publico = doc["publico"]
                    chunk.pdf = pdf_rel
                    chunk.url_publica = proyecto["url"]
            reasignar_ids(nuevos)
            anteponer_ruta(nuevos)
            chunks.extend(nuevos)
            paginas = [c.page for c in nuevos if isinstance(c.page, int)]
            rango = f"{min(paginas)}-{max(paginas)}" if paginas else "sin página"
            print(f"{_rel(path)}: {len(nuevos)} chunks, páginas {rango}")
    if not chunks:
        raise ManifiestoError("el manifiesto no produjo chunks")
    return chunks


def escribir_chunks(chunks: list) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    with open(CHUNKS_PATH, "w", encoding="utf-8", newline="\n") as f:
        for chunk in chunks:
            f.write(json.dumps(chunk.to_dict(), ensure_ascii=False) + "\n")
    print(f"OK -> {CHUNKS_PATH} ({len(chunks)} chunks)")


def escribir_meta(n_chunks: int, origen: str, embed_model: str,
                  dims: int) -> None:
    digest = hash_corpus()
    HASH_PATH.write_text(digest + "\n", encoding="utf-8", newline="\n")
    META_PATH.write_text(json.dumps({
        "corpus_sha256": digest,
        "n_chunks": n_chunks,
        "embed_model": embed_model,
        "dims": dims,
        "origen": origen,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def chequear() -> None:
    """Valida manifiesto, secretos y que el índice de chunks siga al corpus."""
    construir_chunks()
    if not HASH_PATH.is_file() or not META_PATH.is_file():
        sys.exit("falta data/corpus.sha256 o data/ingest_meta.json: corré la ingesta")
    digest = hash_corpus()
    guardado = HASH_PATH.read_text(encoding="utf-8").strip()
    if digest != guardado:
        sys.exit(
            "data/chunks.jsonl no está al día con corpus/: "
            "el hash cambió, volvé a correr scripts/ingest.py"
        )
    meta = json.loads(META_PATH.read_text(encoding="utf-8"))
    if meta.get("corpus_sha256") != digest:
        sys.exit("data/ingest_meta.json no coincide con el hash del corpus")
    lineas = [
        ln for ln in CHUNKS_PATH.read_text(encoding="utf-8").splitlines() if ln.strip()
    ]
    if len(lineas) != meta.get("n_chunks"):
        sys.exit(
            f"chunks.jsonl tiene {len(lineas)} líneas y la ingesta guardó "
            f"{meta.get('n_chunks')}"
        )
    import faiss

    if not INDEX_PATH.is_file():
        sys.exit("falta data/index.faiss")
    index = faiss.read_index(str(INDEX_PATH))
    if index.ntotal != len(lineas):
        sys.exit(
            f"index.faiss tiene {index.ntotal} vectores y chunks.jsonl {len(lineas)}"
        )
    print(f"OK corpus {digest[:12]} ({len(lineas)} chunks)")


def embedir(chunks: list, provider: str, dry_run: bool = False) -> None:
    from rag.embeddings import (CloudflareEmbeddings, JinaEmbeddings,
                                LocalEmbeddings)

    if provider == "cloudflare":
        modelo = CloudflareEmbeddings()
        origen = "cloudflare"
        embed_model = CF_EMBED_MODEL
    elif provider == "api":
        modelo = JinaEmbeddings()
        origen = "api"
        embed_model = JINA_EMBED_MODEL
    elif provider == "local":
        modelo = LocalEmbeddings()
        origen = "local"
        embed_model = LOCAL_EMBED_MODEL
    else:
        sys.exit(f"provider desconocido: {provider}")

    vectores = modelo.embed_lote([c.text for c in chunks])
    dims = int(vectores.shape[1])
    if dry_run:
        print(
            f"OK dry run -> {len(chunks)} chunks, dim={dims}, {origen} "
            "(sin escribir chunks, índice ni meta)"
        )
        return

    import faiss

    index = faiss.IndexFlatIP(dims)
    index.add(np.ascontiguousarray(vectores))
    faiss.write_index(index, str(INDEX_PATH))
    escribir_meta(len(chunks), origen, embed_model, dims)
    print(f"OK -> {INDEX_PATH} ({index.ntotal} vectores, dim={dims}, {origen})")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sin-embed", action="store_true",
                        help="Solo extraer chunks, sin generar el índice")
    parser.add_argument(
        "--provider", choices=("local", "api", "cloudflare"), default="local",
        help="De dónde salen los vectores del índice",
    )
    parser.add_argument(
        "--limit", type=int, metavar="N",
        help=("Procesa solo los primeros N chunks y no escribe chunks, "
              "índice ni meta (dry run)"),
    )
    parser.add_argument("--check", action="store_true",
                        help="Valida manifiesto, secretos y hash; no reindexa")
    args = parser.parse_args()
    if args.limit is not None and args.limit <= 0:
        sys.exit("--limit debe ser un entero mayor que 0")

    try:
        if args.check:
            chequear()
            return
        chunks = construir_chunks()
    except (ManifiestoError, SecretosError) as exc:
        sys.exit(str(exc))

    if args.limit is not None:
        chunks = chunks[:args.limit]
        if args.sin_embed:
            print(
                f"dry run -> {len(chunks)} chunks "
                "(sin escribir chunks, índice ni meta)"
            )
            return
        embedir(chunks, args.provider, dry_run=True)
        return

    escribir_chunks(chunks)
    if args.sin_embed:
        print("sin índice: no commitees esta ingesta")
        return
    embedir(chunks, args.provider)


if __name__ == "__main__":
    main()
