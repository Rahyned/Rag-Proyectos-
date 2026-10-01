"""La entrada de Vercel restaura el path original y expone la app ASGI."""

import asyncio
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _load_entry():
    spec = importlib.util.spec_from_file_location(
        "rag_api_entry", ROOT / "api" / "rag_api.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _run(cls, path, query=b""):
    seen = {}

    async def inner_app(scope, receive, send):
        seen["path"] = scope["path"]

    async def noop(*args):
        return None

    scope = {"type": "http", "path": path, "query_string": query}
    asyncio.run(cls(inner_app)(scope, noop, noop))
    return seen["path"]


def test_app_es_asgi():
    mod = _load_entry()
    assert callable(mod.app)


def test_restaura_path_de_destino():
    mod = _load_entry()
    seen = _run(mod._RestoreApiPath, "/api/rag_api", b"p=chat")
    assert seen == "/api/chat"


def test_no_toca_ruta_original():
    mod = _load_entry()
    seen = _run(mod._RestoreApiPath, "/api/chat", b"p=chat")
    assert seen == "/api/chat"
