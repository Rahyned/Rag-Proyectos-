"""Entrada de Vercel: expone la FastAPI real bajo /api/*.

Vercel entrega la ruta original (/api/chat) a la función. Si en algún momento
entregara la ruta de destino (/api/rag_api), el query param `p` que agrega el
rewrite restaura el path antes de que FastAPI enrute. Puro ASGI: no interviene
el streaming SSE.
"""

from urllib.parse import parse_qs

from app.main import app as fastapi_app

_DEST = {"/api/rag_api", "/api/rag_api/"}


class _RestoreApiPath:
    def __init__(self, application):
        self._app = application

    async def __call__(self, scope, receive, send):
        if scope.get("type") == "http" and scope.get("path") in _DEST:
            qs = parse_qs(scope.get("query_string", b"").decode("latin-1"))
            sub = qs.get("p", [None])[0]
            if sub:
                new_path = f"/api/{sub}"
                scope["path"] = new_path
                scope["raw_path"] = new_path.encode("utf-8")
        await self._app(scope, receive, send)


app = _RestoreApiPath(fastapi_app)
