"""Rate limit por IP y cupo diario de llamadas al LLM.

Backend distribuido opcional (Upstash Redis REST, ventana fija de 60 s) si
existen UPSTASH_REDIS_REST_URL y UPSTASH_REDIS_REST_TOKEN. Si no están, o
Redis falla, se usa el limiter en memoria de esta instancia: la consulta no
se corta por un Redis caído.

El mapa en memoria desaloja las IPs que hace más que no se ven y olvida los
hits vencidos. No se vacía entero: un overflow no le perdona el cupo a quien
ya estaba al límite.
"""

import logging
import threading
import time
from collections import defaultdict, deque
from datetime import datetime, timezone

import httpx
from fastapi import HTTPException, Request

import app.config as config

log = logging.getLogger("rag.ratelimit")

WINDOW_SECONDS = 60.0
CHAT_LIMIT = 10       # /api/chat (reserva max_tokens por llamada)
SEARCH_LIMIT = 60     # /api/search (barato: solo BM25)
_MAX_IPS = 10_000

# 429s recientes de Groq → circuito abierto.
GROQ_TRIP = 3
GROQ_WINDOW_SECONDS = 60.0

# La clave de la ventana fija vive un poco más que la ventana, para que el
# INCR de los últimos segundos no expire antes del cambio de bucket.
_RL_TTL_SECONDS = int(WINDOW_SECONDS) * 2
# El cupo es por día UTC; 2 días cubre la fecha aunque la última llamada
# haya sido cerca de la medianoche.
_BUDGET_TTL_SECONDS = 2 * 24 * 60 * 60

_IP_HEADERS = (
    "x-vercel-forwarded-for",
    "x-real-ip",
    "x-forwarded-for",
)

_lock = threading.Lock()
_hits: dict[str, deque[float]] = defaultdict(deque)
_groq_429: deque[float] = deque(maxlen=64)
_budget: dict[str, int] = {}


def client_ip(request: Request) -> str:
    """IP real detrás de Vercel: el header propio primero, luego los genéricos."""
    for name in _IP_HEADERS:
        raw = request.headers.get(name, "")
        if raw and raw.strip():
            return raw.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _redis_url() -> str:
    return config.upstash_redis_rest_url()


def _redis_token() -> str:
    return config.upstash_redis_rest_token()


def _redis_configured() -> bool:
    return bool(_redis_url() and _redis_token())


def _budget_key(prefix: str = "llm", moment: datetime | None = None) -> str:
    dia = (moment or datetime.now(timezone.utc)).strftime("%Y-%m-%d")
    return f"{prefix}:budget:{dia}"


def _redis_pipeline(commands: list) -> list:
    url = _redis_url().rstrip("/") + "/pipeline"
    resp = httpx.post(
        url,
        json=commands,
        headers={"Authorization": f"Bearer {_redis_token()}"},
        timeout=2.0,
    )
    resp.raise_for_status()
    data = resp.json()
    if not isinstance(data, list) or len(data) != len(commands):
        raise RuntimeError("respuesta Redis inesperada")
    for item in data:
        if not isinstance(item, dict) or "result" not in item or item.get("error"):
            detalle = item.get("error") if isinstance(item, dict) else data
            raise RuntimeError(str(detalle)[:200])
    return data


def _ventana() -> int:
    return int(time.time() // WINDOW_SECONDS)


def _check_redis(endpoint: str, ip: str, limit: int) -> None:
    """Ventana fija. Lanza HTTPException si se pasa del cupo; si no, retorna."""
    key = f"rl:{endpoint}:{ip}:{_ventana()}"
    data = _redis_pipeline([
        ["INCR", key],
        ["EXPIRE", key, _RL_TTL_SECONDS],
    ])
    count = int(data[0]["result"])
    if count > limit:
        restante = WINDOW_SECONDS - (time.time() % WINDOW_SECONDS)
        retry = max(1, int(restante) + 1)
        raise HTTPException(
            status_code=429,
            detail="Demasiadas consultas. Probá de nuevo en un minuto.",
            headers={"Retry-After": str(retry)},
        )


def _purge_expired(now: float) -> None:
    vacias = []
    for key, q in _hits.items():
        while q and now - q[0] > WINDOW_SECONDS:
            q.popleft()
        if not q:
            vacias.append(key)
    for key in vacias:
        del _hits[key]


def _evacuar(now: float) -> None:
    """Saca hits vencidos y, si sigue lleno, las IPs que hace más que no pegan."""
    if len(_hits) <= _MAX_IPS:
        return
    _purge_expired(now)
    while len(_hits) > _MAX_IPS:
        vieja = min(
            _hits,
            key=lambda k: _hits[k][-1] if _hits[k] else -1.0,
        )
        del _hits[vieja]


def _check_memory(endpoint: str, ip: str, limit: int) -> None:
    now = time.monotonic()
    key = f"{endpoint}:{ip}"
    with _lock:
        q = _hits[key]
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
        _evacuar(now)


def check(request: Request, limit: int, endpoint: str = "api") -> None:
    """429 + Retry-After al exceder la ventana. Redis si está; si no, memoria."""
    ip = client_ip(request)
    if _redis_configured():
        try:
            _check_redis(endpoint, ip, limit)
            return
        except HTTPException:
            raise
        except Exception as exc:  # noqa: BLE001 — fail-open al limiter local
            log.warning("Redis no disponible (%s); rate limit en memoria", exc)
    _check_memory(endpoint, ip, limit)


def _reservar_redis(prefix: str, budget: int) -> bool:
    key = _budget_key(prefix)
    data = _redis_pipeline([
        ["INCR", key],
        ["EXPIRE", key, _BUDGET_TTL_SECONDS],
    ])
    n = int(data[0]["result"])
    if n > budget:
        # El INCR ya corrió pero esta llamada no sale: se revierte.
        try:
            _redis_pipeline([["DECR", key]])
        except Exception as exc:  # noqa: BLE001 — el rechazo igual vale
            log.warning("no se pudo revertir el cupo de %s (%s)", prefix, exc)
        return False
    return True


def _reservar_memoria(prefix: str, budget: int) -> bool:
    key = _budget_key(prefix)
    marca = f"{prefix}:budget:"
    with _lock:
        for dia in [k for k in _budget if k.startswith(marca) and k != key]:
            del _budget[dia]
        n = _budget.get(key, 0)
        if n >= budget:
            return False
        _budget[key] = n + 1
        return True


def _reservar(prefix: str, budget: int) -> bool:
    """True si esta llamada puede salir (y el cupo queda consumido).

    0 = ilimitado, no incrementa. Si Redis falla, el cupo sigue en memoria.
    """
    if budget == 0:
        return True
    if _redis_configured():
        try:
            return _reservar_redis(prefix, budget)
        except Exception as exc:  # noqa: BLE001 — mismo fail-open que el rate limit
            log.warning(
                "Redis no disponible (%s); cupo de %s en memoria", exc, prefix
            )
    return _reservar_memoria(prefix, budget)


def reservar_llamada_llm() -> bool:
    """True si esta llamada puede ir a Groq."""
    return _reservar("llm", config.llm_daily_budget())


def reservar_llamada_jina() -> bool:
    """True si esta consulta puede pegarle a la API de embeddings."""
    return _reservar("jina", config.jina_daily_budget())


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
        _budget.clear()
