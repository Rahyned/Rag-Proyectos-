import json
import logging
import uuid
from collections.abc import Iterator
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

from rag.config import (CHUNKS_PATH, CORPUS_DIR, INDEX_PATH, dense_enabled,
                        embeddings_provider, rag_rerank)
from rag.manifiesto import ManifiestoError, ids_proyectos, proyectos_publicos

import app.config as config
from app import ratelimit
from app.services import llm, rag_service

log = logging.getLogger("rag.api")

app = FastAPI(title="Rag-Proyectos API", version="0.3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://portafolio-web-three-gamma.vercel.app",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


class _QueryMixin(BaseModel):
    query: str = Field(min_length=2, max_length=500)

    @field_validator("query")
    @classmethod
    def _strip_query(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2:
            raise ValueError("la pregunta debe tener al menos 2 caracteres")
        return v


class _ProyectoMixin(BaseModel):
    # Exactamente un proyecto por consulta: el selector de la UI ya no
    # ofrece «Todos». La validación se hace en el endpoint para responder
    # 400 (no 422) con un mensaje claro.
    proyecto: str | list[str] | None = None


class SearchRequest(_QueryMixin, _ProyectoMixin):
    top_k: int = Field(default=5, ge=1, le=10)


class ChatRequest(_QueryMixin, _ProyectoMixin):
    mode: Literal["fragmentos", "sintetica"] = "fragmentos"
    top_k: int = Field(default=5, ge=1, le=10)


# La síntesis manda pocos fragmentos al LLM aunque el cliente pida más.
# /api/search sigue aceptando hasta 10.
_TOP_K_SINTETICA = 5


def _proyecto_unico(valor: str | list[str] | None) -> str:
    """Exige exactamente un proyecto conocido; si no, responde 400."""
    if isinstance(valor, list):
        proyectos = [v.strip() for v in valor if isinstance(v, str) and v.strip()]
        if len(proyectos) > 1:
            raise HTTPException(
                status_code=400,
                detail="Elegí un solo proyecto por consulta.",
            )
        valor = proyectos[0] if proyectos else None
    if isinstance(valor, str):
        # Un array no es la única forma de mandar varios: «stella,cars».
        proyectos = [p.strip() for p in valor.split(",") if p.strip()]
        if len(proyectos) > 1:
            raise HTTPException(
                status_code=400,
                detail="Elegí un solo proyecto por consulta.",
            )
        valor = proyectos[0] if proyectos else None
    if not valor or valor == "todos":
        raise HTTPException(
            status_code=400,
            detail="Elegí un proyecto para preguntar.",
        )
    try:
        conocidos = ids_proyectos()
    except ManifiestoError as exc:
        log.error("manifiesto inválido: %s", exc)
        raise HTTPException(
            status_code=503, detail="configuración inválida",
        ) from None
    if valor not in conocidos:
        raise HTTPException(
            status_code=400,
            detail=f"Proyecto desconocido: {valor}",
        )
    return valor


def _sse(payload: dict) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


def _hits_or_503(query: str, top_k: int, proyecto: str) -> list[dict]:
    try:
        return rag_service.search(query, top_k, proyecto=proyecto)
    except Exception:  # noqa: BLE001 — al cliente solo id de referencia
        error_id = uuid.uuid4().hex[:8]
        log.exception("retrieval fallo [%s]", error_id)
        raise HTTPException(
            status_code=503,
            detail=f"Recuperación no disponible (ref: {error_id})",
        ) from None


def _index_dim() -> int | None:
    """Dimensión del índice FAISS actual, o None si no se puede leer."""
    try:
        import faiss

        return int(faiss.read_index(str(INDEX_PATH)).d)
    except Exception:  # noqa: BLE001 — health no debe romper por el índice
        return None


@app.get("/api/health")
def health():
    retrievable = CHUNKS_PATH.exists() and INDEX_PATH.exists()
    provider = embeddings_provider()
    origen = (
        ratelimit.cloudflare_origen_circuito()
        if provider == "cloudflare"
        else ratelimit.jina_origen_circuito()
    )
    return {
        "status": "ok" if retrievable else "degraded",
        "retrievable": retrievable,
        "llm": bool(config.llm_api_key()),
        "model": config.llm_model(),
        "dense": dense_enabled(),
        "embeddings": provider,
        "rerank": rag_rerank(),
        "index_dim": _index_dim(),
        "dense_error": rag_service.last_dense_error(),
        "dense_error_origen": origen,
    }


@app.get("/api/proyectos")
def proyectos():
    try:
        return {"proyectos": proyectos_publicos()}
    except ManifiestoError as exc:
        log.error("manifiesto inválido: %s", exc)
        raise HTTPException(
            status_code=503, detail="configuración inválida",
        ) from None


if (Path(CORPUS_DIR)).is_dir():
    app.mount("/corpus", StaticFiles(directory=str(CORPUS_DIR)), name="corpus")


@app.post("/api/search")
def search(body: SearchRequest, request: Request):
    ratelimit.check(request, ratelimit.SEARCH_LIMIT, "search")
    proyecto = _proyecto_unico(body.proyecto)
    return {"hits": _hits_or_503(body.query, body.top_k, proyecto)}


@app.post("/api/chat")
def chat(body: ChatRequest, request: Request):
    ratelimit.check(request, ratelimit.CHAT_LIMIT, "chat")
    proyecto = _proyecto_unico(body.proyecto)
    top_k = body.top_k
    if body.mode == "sintetica":
        top_k = min(top_k, _TOP_K_SINTETICA)
    hits = _hits_or_503(body.query, top_k, proyecto)

    def gen() -> Iterator[str]:
        try:
            yield _sse({"type": "sources", "hits": hits})
            if body.mode == "sintetica":
                if not hits:
                    # Gate vacío: sin contexto no se llama al LLM (evita
                    # alucinaciones y consumo de cuota con queries ajenas
                    # al manual); la UI muestra el estado de "sin resultados".
                    yield _sse({"type": "done", "mode": "fragmentos"})
                    return
                try:
                    for token in llm.stream_answer(body.query, hits):
                        yield _sse({"type": "text", "delta": token})
                except llm.LLMError as exc:
                    log.warning("llm fallback [%s]: %s", exc.reason, exc)
                    yield _sse({"type": "fallback", "reason": exc.reason})
                    yield _sse({"type": "done", "mode": "fragmentos"})
                    return
                yield _sse({"type": "done", "mode": "sintetica"})
            else:
                yield _sse({"type": "done", "mode": "fragmentos"})
        except Exception:  # noqa: BLE001 — nunca cortar el SSE sin cierre
            log.exception("stream fallo inesperado")
            yield _sse({"type": "fallback", "reason": "error"})
            yield _sse({"type": "done", "mode": "fragmentos"})

    return StreamingResponse(
        gen(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/")
def root():
    return {"name": "rag-proyectos", "docs": "/docs"}
