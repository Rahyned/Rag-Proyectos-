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
# 429 de una API de embeddings abre el circuito enseguida; timeout/5xx recién
# a los 2 en 60 s. Jina y Cloudflare tienen estado y claves separados.
DENSE_FAIL_TRIP = 2
DENSE_FAIL_WINDOW_SECONDS = 60.0
# La pausa dura lo mismo en memoria y en Redis: la siguiente consulta no
# vuelve a esperar el timeout.
DENSE_CIRCUIT_SECONDS = 90
JINA_FAIL_TRIP = DENSE_FAIL_TRIP
JINA_FAIL_WINDOW_SECONDS = DENSE_FAIL_WINDOW_SECONDS
JINA_CIRCUIT_SECONDS = DENSE_CIRCUIT_SECONDS
CLOUDFLARE_FAIL_TRIP = DENSE_FAIL_TRIP
CLOUDFLARE_FAIL_WINDOW_SECONDS = DENSE_FAIL_WINDOW_SECONDS
CLOUDFLARE_CIRCUIT_SECONDS = DENSE_CIRCUIT_SECONDS
_JINA_CIRCUIT_KEY = "jina:circuit"
# Último origen visto, aunque el circuito todavía no se haya abierto. Lo lee
# /api/health en cualquier instancia.
_JINA_LAST_ERROR_KEY = "jina:last_error"
_CLOUDFLARE_CIRCUIT_KEY = "cloudflare:circuit"
_CLOUDFLARE_LAST_ERROR_KEY = "cloudflare:last_error"
_DENSE_ORIGENES = frozenset(("timeout", "status_429", "status_5xx"))
_JINA_ORIGENES = _DENSE_ORIGENES

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
_jina_pause_until = 0.0
_jina_fallos: deque[float] = deque(maxlen=64)
_jina_origen: str | None = None
_cloudflare_pause_until = 0.0
_cloudflare_fallos: deque[float] = deque(maxlen=64)
_cloudflare_origen: str | None = None


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


def _leer_cupo_redis(prefix: str) -> int:
    key = _budget_key(prefix)
    data = _redis_pipeline([["GET", key]])
    raw = data[0]["result"]
    if raw is None:
        return 0
    return int(raw)


def _leer_cupo_memoria(prefix: str) -> int:
    key = _budget_key(prefix)
    with _lock:
        return int(_budget.get(key, 0))


def _cupo_disponible(prefix: str, budget: int) -> bool:
    """True si todavía entra una llamada. No incrementa el contador."""
    if budget == 0:
        return True
    if _redis_configured():
        try:
            return _leer_cupo_redis(prefix) < budget
        except Exception as exc:  # noqa: BLE001 — fail-open al cupo local
            log.warning(
                "Redis no disponible (%s); cupo de %s en memoria", exc, prefix
            )
    return _leer_cupo_memoria(prefix) < budget


def _anotar_redis(prefix: str) -> None:
    key = _budget_key(prefix)
    _redis_pipeline([
        ["INCR", key],
        ["EXPIRE", key, _BUDGET_TTL_SECONDS],
    ])


def _anotar_memoria(prefix: str) -> None:
    key = _budget_key(prefix)
    marca = f"{prefix}:budget:"
    with _lock:
        for dia in [k for k in _budget if k.startswith(marca) and k != key]:
            del _budget[dia]
        _budget[key] = _budget.get(key, 0) + 1


def _anotar(prefix: str, budget: int) -> None:
    """Suma una llamada que ya respondió bien. 0 = ilimitado, no incrementa."""
    if budget == 0:
        return
    if _redis_configured():
        try:
            _anotar_redis(prefix)
            return
        except Exception as exc:  # noqa: BLE001
            log.warning(
                "Redis no disponible (%s); cupo de %s en memoria", exc, prefix
            )
    _anotar_memoria(prefix)


def puede_llamar_cloudflare() -> bool:
    """True si el cupo diario de Cloudflare todavía no se agotó. No lo descuenta."""
    return _cupo_disponible("cloudflare", config.cf_daily_budget())


def anotar_llamada_cloudflare() -> None:
    """Descuenta una llamada a Cloudflare que respondió OK."""
    _anotar("cloudflare", config.cf_daily_budget())


def puede_llamar_jina() -> bool:
    """True si el cupo diario todavía no se agotó. No lo descuenta."""
    return _cupo_disponible("jina", config.jina_daily_budget())


def anotar_llamada_jina() -> None:
    """Descuenta una llamada a Jina que respondió OK."""
    _anotar("jina", config.jina_daily_budget())


def _guardar_origen_jina(origen: str) -> None:
    """Recuerda el último fallo en memoria y en Redis, sin abrir el circuito.

    Se guarda desde el primer fallo para que /api/health muestre
    dense_error_origen aunque todavía no se hayan juntado los 2 fallos.
    """
    global _jina_origen
    with _lock:
        _jina_origen = origen
    if not _redis_configured():
        return
    try:
        _redis_pipeline([[
            "SET", _JINA_LAST_ERROR_KEY, origen,
            "EX", JINA_CIRCUIT_SECONDS,
        ]])
    except Exception as exc:  # noqa: BLE001
        log.warning("no se pudo guardar el origen de jina en Redis (%s)", exc)


def jina_en_pausa() -> bool:
    """True si un fallo reciente dejó la API en pausa (memoria o Upstash).

    Si la clave existe en Redis, no se rearma la pausa local: manda el TTL
    que le queda a Redis, no una ventana nueva de JINA_CIRCUIT_SECONDS.
    """
    global _jina_origen
    now = time.monotonic()
    with _lock:
        if now < _jina_pause_until:
            return True
    if not _redis_configured():
        return False
    try:
        data = _redis_pipeline([["GET", _JINA_CIRCUIT_KEY]])
    except Exception as exc:  # noqa: BLE001 — sin Redis, vale la memoria
        log.warning("Redis no disponible (%s); circuito de jina en memoria", exc)
        return False
    valor = data[0]["result"]
    if valor in _JINA_ORIGENES:
        # Otra instancia abrió el circuito: el origen viaja en la clave.
        with _lock:
            _jina_origen = valor
    return bool(valor)


def abrir_pausa_jina(origen: str | None = None) -> None:
    """Pausa Jina JINA_CIRCUIT_SECONDS. La próxima consulta no espera el timeout.

    `origen` es el motivo que abrió el circuito (timeout, status_429 o
    status_5xx); /api/health lo expone como dense_error_origen.
    """
    global _jina_pause_until
    if origen:
        _guardar_origen_jina(origen)
    hasta = time.monotonic() + JINA_CIRCUIT_SECONDS
    with _lock:
        _jina_pause_until = hasta
    if not _redis_configured():
        return
    try:
        _redis_pipeline([[
            "SET", _JINA_CIRCUIT_KEY, origen or "1",
            "EX", JINA_CIRCUIT_SECONDS,
        ]])
    except Exception as exc:  # noqa: BLE001
        log.warning("no se pudo abrir el circuito de jina en Redis (%s)", exc)


def anotar_fallo_jina(origen: str) -> None:
    """Registra un fallo de Jina y abre el circuito cuando corresponde.

    Un 429 abre enseguida. Un timeout o un 5xx abre al segundo dentro de
    JINA_FAIL_WINDOW_SECONDS: el primer fallo no corta el canal denso pero
    sí queda registrado como dense_error_origen.
    """
    if origen == "status_429":
        abrir_pausa_jina(origen)
        return
    now = time.monotonic()
    with _lock:
        while (
            _jina_fallos
            and now - _jina_fallos[0] > JINA_FAIL_WINDOW_SECONDS
        ):
            _jina_fallos.popleft()
        _jina_fallos.append(now)
        abrir = len(_jina_fallos) >= JINA_FAIL_TRIP
        if abrir:
            _jina_fallos.clear()
    if abrir:
        abrir_pausa_jina(origen)
    else:
        _guardar_origen_jina(origen)


def jina_origen_circuito() -> str | None:
    """Último motivo denso (timeout / status_429 / status_5xx).

    Primero la memoria de esta instancia; si no hay, la clave que comparten
    todas las instancias en Redis.
    """
    with _lock:
        local = _jina_origen
    if local in _JINA_ORIGENES:
        return local
    if not _redis_configured():
        return None
    try:
        data = _redis_pipeline([["GET", _JINA_LAST_ERROR_KEY]])
    except Exception as exc:  # noqa: BLE001 — sin Redis, vale la memoria
        log.warning("Redis no disponible (%s); origen de jina en memoria", exc)
        return None
    valor = data[0]["result"] if data else None
    return valor if valor in _JINA_ORIGENES else None


def _guardar_origen_cloudflare(origen: str) -> None:
    """Recuerda el último fallo de Cloudflare en memoria y en Redis."""
    global _cloudflare_origen
    with _lock:
        _cloudflare_origen = origen
    if not _redis_configured():
        return
    try:
        _redis_pipeline([[
            "SET", _CLOUDFLARE_LAST_ERROR_KEY, origen,
            "EX", CLOUDFLARE_CIRCUIT_SECONDS,
        ]])
    except Exception as exc:  # noqa: BLE001
        log.warning(
            "no se pudo guardar el origen de cloudflare en Redis (%s)", exc
        )


def cloudflare_en_pausa() -> bool:
    """True si un fallo reciente dejó Cloudflare en pausa (memoria o Upstash)."""
    global _cloudflare_origen
    now = time.monotonic()
    with _lock:
        if now < _cloudflare_pause_until:
            return True
    if not _redis_configured():
        return False
    try:
        data = _redis_pipeline([["GET", _CLOUDFLARE_CIRCUIT_KEY]])
    except Exception as exc:  # noqa: BLE001 — sin Redis, vale la memoria
        log.warning(
            "Redis no disponible (%s); circuito de cloudflare en memoria", exc
        )
        return False
    valor = data[0]["result"]
    if valor in _DENSE_ORIGENES:
        # Otra instancia abrió el circuito: el origen viaja en la clave.
        with _lock:
            _cloudflare_origen = valor
    return bool(valor)


def abrir_pausa_cloudflare(origen: str | None = None) -> None:
    """Pausa Cloudflare CLOUDFLARE_CIRCUIT_SECONDS."""
    global _cloudflare_pause_until
    if origen:
        _guardar_origen_cloudflare(origen)
    hasta = time.monotonic() + CLOUDFLARE_CIRCUIT_SECONDS
    with _lock:
        _cloudflare_pause_until = hasta
    if not _redis_configured():
        return
    try:
        _redis_pipeline([[
            "SET", _CLOUDFLARE_CIRCUIT_KEY, origen or "1",
            "EX", CLOUDFLARE_CIRCUIT_SECONDS,
        ]])
    except Exception as exc:  # noqa: BLE001
        log.warning(
            "no se pudo abrir el circuito de cloudflare en Redis (%s)", exc
        )


def anotar_fallo_cloudflare(origen: str) -> None:
    """Registra un fallo de Cloudflare y abre el circuito cuando corresponde.

    Un 429 abre enseguida. Un timeout o un 5xx abre al segundo dentro de
    CLOUDFLARE_FAIL_WINDOW_SECONDS; el primer fallo solo queda registrado
    como origen.
    """
    if origen == "status_429":
        abrir_pausa_cloudflare(origen)
        return
    now = time.monotonic()
    with _lock:
        while (
            _cloudflare_fallos
            and now - _cloudflare_fallos[0] > CLOUDFLARE_FAIL_WINDOW_SECONDS
        ):
            _cloudflare_fallos.popleft()
        _cloudflare_fallos.append(now)
        abrir = len(_cloudflare_fallos) >= CLOUDFLARE_FAIL_TRIP
        if abrir:
            _cloudflare_fallos.clear()
    if abrir:
        abrir_pausa_cloudflare(origen)
    else:
        _guardar_origen_cloudflare(origen)


def cloudflare_origen_circuito() -> str | None:
    """Último motivo denso de Cloudflare (timeout / status_429 / status_5xx)."""
    with _lock:
        local = _cloudflare_origen
    if local in _DENSE_ORIGENES:
        return local
    if not _redis_configured():
        return None
    try:
        data = _redis_pipeline([["GET", _CLOUDFLARE_LAST_ERROR_KEY]])
    except Exception as exc:  # noqa: BLE001 — sin Redis, vale la memoria
        log.warning(
            "Redis no disponible (%s); origen de cloudflare en memoria", exc
        )
        return None
    valor = data[0]["result"] if data else None
    return valor if valor in _DENSE_ORIGENES else None


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
    global _jina_pause_until, _jina_origen
    global _cloudflare_pause_until, _cloudflare_origen
    with _lock:
        _hits.clear()
        _groq_429.clear()
        _budget.clear()
        _jina_fallos.clear()
        _jina_pause_until = 0.0
        _jina_origen = None
        _cloudflare_fallos.clear()
        _cloudflare_pause_until = 0.0
        _cloudflare_origen = None
