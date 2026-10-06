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
                        embeddings_provider)
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
    proyecto: str | None = None

    @field_validator("proyecto")
    @classmethod
    def _proyecto(cls, v: str | None) -> str | None:
        if v is None:
            return None
        v = v.strip()
        if not v or v == "todos":
            return "todos" if v == "todos" else None
        try:
            conocidos = ids_proyectos()
        except ManifiestoError as exc:
            raise ValueError(str(exc)) from None
        if v not in conocidos:
            raise ValueError(f"proyecto desconocido: {v}")
        return v


class SearchRequest(_QueryMixin, _ProyectoMixin):
    top_k: int = Field(default=5, ge=1, le=10)


class ChatRequest(_QueryMixin, _ProyectoMixin):
    mode: Literal["fragmentos", "sintetica"] = "fragmentos"
    top_k: int = Field(default=5, ge=1, le=10)


# La síntesis manda pocos fragmentos al LLM aunque el cliente pida más.
# /api/search sigue aceptando hasta 10.
_TOP_K_SINTETICA = 5


def _sse(payload: dict) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


def _hits_or_503(query: str, top_k: int, proyecto: str | None) -> list[dict]:
    try:
        return rag_service.search(query, top_k, proyecto=proyecto)
    except Exception:  # noqa: BLE001 — al cliente solo id de referencia
        error_id = uuid.uuid4().hex[:8]
        log.exception("retrieval fallo [%s]", error_id)
        raise HTTPException(
            status_code=503,
            detail=f"Recuperación no disponible (ref: {error_id})",
        ) from None


@app.get("/api/health")
def health():
    retrievable = CHUNKS_PATH.exists() and INDEX_PATH.exists()
    return {
        "status": "ok" if retrievable else "degraded",
        "retrievable": retrievable,
        "llm": bool(config.llm_api_key()),
        "model": config.llm_model(),
        "dense": dense_enabled(),
        "embeddings": embeddings_provider(),
        "dense_error": rag_service.last_dense_error(),
    }


@app.get("/api/proyectos")
def proyectos():
    try:
        return {"proyectos": proyectos_publicos()}
    except ManifiestoError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from None


if (Path(CORPUS_DIR)).is_dir():
    app.mount("/corpus", StaticFiles(directory=str(CORPUS_DIR)), name="corpus")


@app.post("/api/search")
def search(body: SearchRequest, request: Request):
    ratelimit.check(request, ratelimit.SEARCH_LIMIT, "search")
    return {"hits": _hits_or_503(body.query, body.top_k, body.proyecto)}


@app.post("/api/chat")
def chat(body: ChatRequest, request: Request):
    ratelimit.check(request, ratelimit.CHAT_LIMIT, "chat")
    top_k = body.top_k
    if body.mode == "sintetica":
        top_k = min(top_k, _TOP_K_SINTETICA)
    hits = _hits_or_503(body.query, top_k, body.proyecto)

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
