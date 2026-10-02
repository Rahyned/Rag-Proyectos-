"""Rate limiting en memoria por instancia (serverless) + circuito de 429.

No es un control global de cuota: cada contenedor de Vercel tiene la suya,
pero un loop desde una sola IP queda frenado igual. Además, si Groq devuelve
429 varias veces seguidas, el circuito se abre y `stream_answer` degrada a
fragmentos sin gastar un llamado más.
"""

import threading
import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request

WINDOW_SECONDS = 60.0
CHAT_LIMIT = 10       # /api/chat (reserva max_tokens por llamada)
SEARCH_LIMIT = 60     # /api/search (barato: solo BM25)
_MAX_IPS = 10_000

# 429s recientes de Groq → circuito abierto.
GROQ_TRIP = 3
GROQ_WINDOW_SECONDS = 60.0

_lock = threading.Lock()
_hits: dict[str, deque[float]] = defaultdict(deque)
_groq_429: deque[float] = deque(maxlen=64)


def client_ip(request: Request) -> str:
    fwd = request.headers.get("x-forwarded-for", "")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def check(request: Request, limit: int) -> None:
    """Ventana deslizante por IP; 429 + Retry-After al excederla."""
    now = time.monotonic()
    ip = client_ip(request)
    with _lock:
        q = _hits[ip]
        while q and now - q[0] > WINDOW_SECONDS:
            q.popleft()
        if len(q) >= limit:
            oldest = q[0] if q else now
            retry = max(1, int(WINDOW_SECONDS - (now - oldest)) + 1)
            raise HTTPException(
                status_code=429,
                detail="Demasiadas consultas. Probá de nuevo en un minuto.",
                headers={"Retry-After": str(retry)},
            )
        q.append(now)
        if len(_hits) > _MAX_IPS:
            _hits.clear()


def note_groq_429() -> None:
    with _lock:
        _groq_429.append(time.monotonic())


def groq_limited() -> bool:
    now = time.monotonic()
    with _lock:
        while _groq_429 and now - _groq_429[0] > GROQ_WINDOW_SECONDS:
            _groq_429.popleft()
        return len(_groq_429) >= GROQ_TRIP


def reset() -> None:
    """Solo para tests."""
    with _lock:
        _hits.clear()
        _groq_429.clear()
