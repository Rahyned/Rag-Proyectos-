"""Carga y validación de corpus/manifiesto.json (proyectos y documentos)."""

import json
import re
import unicodedata
from pathlib import Path

from rag.config import CORPUS_DIR

MANIFIESTO_PATH = CORPUS_DIR / "manifiesto.json"

TIPOS = frozenset({"manual", "ficha", "changelog", "readme"})
_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_ACCENT_RE = re.compile(r"[\u0300-\u036f]")

_CAMPOS_PROYECTO = ("id", "nombre", "descripcion", "documentos")
_CAMPOS_DOC = ("archivo", "titulo", "tipo", "publico")

_cache: dict | None = None
_cache_key: tuple | None = None


class ManifiestoError(ValueError):
    """El manifiesto está incompleto o apunta a un archivo que no existe."""


def _plano(text: str) -> str:
    text = unicodedata.normalize("NFD", text.lower())
    return _ACCENT_RE.sub("", text)


def limpiar_cache() -> None:
    global _cache, _cache_key
    _cache = None
    _cache_key = None


def validar(raw: object, corpus_dir: Path = CORPUS_DIR) -> dict:
    """Devuelve el manifiesto normalizado o lanza ManifiestoError."""
    if not isinstance(raw, dict):
        raise ManifiestoError("el manifiesto tiene que ser un objeto JSON")
    if "proyectos" not in raw:
        raise ManifiestoError("falta el campo 'proyectos'")
    proyectos = raw["proyectos"]
    if not isinstance(proyectos, list) or not proyectos:
        raise ManifiestoError("'proyectos' tiene que ser una lista con al menos un proyecto")

    emails = raw.get("emails_publicos", [])
    if not isinstance(emails, list) or not all(isinstance(e, str) for e in emails):
        raise ManifiestoError("'emails_publicos' tiene que ser una lista de strings")

    vistos: set[str] = set()
    salida: list[dict] = []
    for i, proyecto in enumerate(proyectos):
        if not isinstance(proyecto, dict):
            raise ManifiestoError(f"proyectos[{i}] no es un objeto")
        for campo in _CAMPOS_PROYECTO:
            if campo not in proyecto:
                raise ManifiestoError(f"proyectos[{i}] no tiene '{campo}'")
        pid = proyecto["id"]
        if not isinstance(pid, str) or not _ID_RE.match(pid):
            raise ManifiestoError(
                f"proyectos[{i}].id inválido ({pid!r}): usá minúsculas y guiones"
            )
        if pid in vistos:
            raise ManifiestoError(f"id de proyecto duplicado: {pid}")
        vistos.add(pid)
        nombre = proyecto["nombre"]
        descripcion = proyecto["descripcion"]
        if not isinstance(nombre, str) or not nombre.strip():
            raise ManifiestoError(f"el proyecto '{pid}' no tiene 'nombre'")
        if not isinstance(descripcion, str) or not descripcion.strip():
            raise ManifiestoError(f"el proyecto '{pid}' no tiene 'descripcion'")

        url = proyecto.get("url")
        if url is not None and (
            not isinstance(url, str) or not url.startswith(("http://", "https://"))
        ):
            raise ManifiestoError(
                f"el proyecto '{pid}' tiene 'url' inválida (http o https, o null)"
            )

        aliases = proyecto.get("aliases", [])
        if not isinstance(aliases, list) or not all(isinstance(a, str) for a in aliases):
            raise ManifiestoError(f"el proyecto '{pid}' tiene 'aliases' inválidos")
        preguntas = proyecto.get("preguntas", [])
        if not isinstance(preguntas, list) or not all(
            isinstance(p, str) and p.strip() for p in preguntas
        ):
            raise ManifiestoError(f"el proyecto '{pid}' tiene 'preguntas' inválidas")

        docs_raw = proyecto["documentos"]
        if not isinstance(docs_raw, list) or not docs_raw:
            raise ManifiestoError(f"el proyecto '{pid}' no tiene documentos")
        docs: list[dict] = []
        for j, doc in enumerate(docs_raw):
            if not isinstance(doc, dict):
                raise ManifiestoError(f"{pid}.documentos[{j}] no es un objeto")
            for campo in _CAMPOS_DOC:
                if campo not in doc:
                    raise ManifiestoError(
                        f"el documento {j} de '{pid}' no tiene '{campo}'"
                    )
            archivo = doc["archivo"]
            if (
                not isinstance(archivo, str)
                or not archivo
                or "/" in archivo
                or "\\" in archivo
                or archivo.startswith(".")
            ):
                raise ManifiestoError(
                    f"el proyecto '{pid}' tiene 'archivo' inválido ({archivo!r})"
                )
            tipo = doc["tipo"]
            if tipo not in TIPOS:
                raise ManifiestoError(
                    f"{pid}/{archivo}: tipo {tipo!r} no es "
                    "manual, ficha, changelog ni readme"
                )
            if not isinstance(doc["publico"], bool):
                raise ManifiestoError(f"{pid}/{archivo}: 'publico' tiene que ser true o false")
            titulo = doc["titulo"]
            if not isinstance(titulo, str) or not titulo.strip():
                raise ManifiestoError(f"{pid}/{archivo}: falta 'titulo'")
            path = corpus_dir / pid / archivo
            if not path.is_file():
                raise ManifiestoError(f"no existe el archivo {path.relative_to(corpus_dir)}")
            sufijo = path.suffix.lower()
            if sufijo not in (".md", ".pdf"):
                raise ManifiestoError(f"{pid}/{archivo}: solo se ingiere .md o .pdf")
            docs.append({
                "archivo": archivo,
                "titulo": titulo.strip(),
                "tipo": tipo,
                "publico": doc["publico"],
                "path": path,
            })
        salida.append({
            "id": pid,
            "nombre": nombre.strip(),
            "descripcion": descripcion.strip(),
            "url": url,
            "aliases": [a.strip() for a in aliases if a.strip()],
            "preguntas": [p.strip() for p in preguntas],
            "documentos": docs,
        })
    return {
        "emails_publicos": [e.strip().lower() for e in emails if e.strip()],
        "proyectos": salida,
    }


def cargar(path: Path = MANIFIESTO_PATH) -> dict:
    global _cache, _cache_key
    if not path.is_file():
        raise ManifiestoError(f"no existe el manifiesto: {path}")
    stat = path.stat()
    key = (str(path.resolve()), stat.st_mtime_ns, stat.st_size)
    if _cache is not None and _cache_key == key:
        return _cache
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ManifiestoError(f"manifiesto JSON inválido: {exc}") from exc
    data = validar(raw, path.parent)
    _cache = data
    _cache_key = key
    return data


def proyectos_publicos() -> list[dict]:
    """Campos que puede ver el cliente (sin la allowlist de emails)."""
    salida = []
    for p in cargar()["proyectos"]:
        salida.append({
            "id": p["id"],
            "nombre": p["nombre"],
            "descripcion": p["descripcion"],
            "url": p["url"],
            "preguntas": p["preguntas"],
        })
    return salida


def ids_proyectos() -> set[str]:
    return {p["id"] for p in cargar()["proyectos"]}


def detectar_proyecto(consulta: str) -> str | None:
    """Id del proyecto nombrado en la pregunta, o None si no hay uno claro."""
    plano = _plano(consulta)
    mejor: str | None = None
    mejor_len = 0
    for proyecto in cargar()["proyectos"]:
        aliases = [proyecto["id"], proyecto["nombre"], *proyecto["aliases"]]
        for alias in aliases:
            a = _plano(alias).strip()
            if len(a) < 3:
                continue
            if " " in a:
                ok = a in plano
            else:
                ok = re.search(rf"\b{re.escape(a)}\b", plano) is not None
            if ok and len(a) > mejor_len:
                mejor = proyecto["id"]
                mejor_len = len(a)
    return mejor
