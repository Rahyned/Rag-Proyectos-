import json
from collections.abc import Iterator
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.services import llm, rag_service

app = FastAPI(title="Rag-Proyectos API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


class SearchRequest(BaseModel):
    query: str = Field(min_length=2, max_length=500)
    top_k: int = Field(default=5, ge=1, le=10)


class ChatRequest(BaseModel):
    query: str = Field(min_length=2, max_length=500)
    mode: Literal["fragmentos", "sintetica"] = "fragmentos"
    top_k: int = Field(default=5, ge=1, le=10)


def _sse(payload: dict) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


def _hits_or_503(query: str, top_k: int) -> list[dict]:
    try:
        return rag_service.search(query, top_k)
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Recuperación no disponible: {exc}",
        ) from exc


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/search")
def search(body: SearchRequest):
    return {"hits": _hits_or_503(body.query, body.top_k)}


@app.post("/api/chat")
def chat(body: ChatRequest):
    hits = _hits_or_503(body.query, body.top_k)

    def gen() -> Iterator[str]:
        yield _sse({"type": "sources", "hits": hits})
        if body.mode == "sintetica":
            try:
                for token in llm.stream_answer(body.query, hits):
                    yield _sse({"type": "text", "delta": token})
            except llm.LLMError as exc:
                yield _sse({"type": "fallback", "reason": str(exc)})
                yield _sse({"type": "done", "mode": "fragmentos"})
                return
            yield _sse({"type": "done", "mode": "sintetica"})
        else:
            yield _sse({"type": "done", "mode": "fragmentos"})

    return StreamingResponse(
        gen(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/")
def root():
    return {"name": "rag-proyectos", "docs": "/docs"}
