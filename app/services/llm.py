"""Generación de respuesta sintética con LLM (compatible OpenAI, opcional).

Proveedor por defecto: Groq (base `LLM_BASE_URL` + `/chat/completions`).
Si no hay LLM_API_KEY o la llamada falla tras los reintentos, se lanza
LLMError y el endpoint cae al modo fragmentos: nunca se rompe la consulta.

`LLMError.reason` es un enum corto (no_key | rate_limited | timeout |
interrupted | upstream) que viaja al front como `fallback.reason`: el
cliente nunca ve el texto crudo de la excepción.

Los reintentos (backoff) solo cubren 5xx/errores de red al iniciar el
stream; una vez que llegaron tokens no se reintenta (no duplicar texto).
429 se reintenta una vez si `Retry-After` cabe en el presupuesto.
"""

import json
import time
from collections.abc import Iterator

import httpx

from app import config, ratelimit

SYSTEM = (
    "Sos el asistente del Manual STELLA, un sistema de gestión para "
    "laboratorios odontológicos. Respondé en español rioplatense (voseo), "
    "claro y breve, usando SOLO la información de los fragmentos del manual "
    "que se te proveen. Citá la fuente entre corchetes al final de cada "
    "afirmación, por ejemplo [Manual STELLA p. 15]. Si la respuesta no está "
    "en los fragmentos, decilo explícitamente SIN citar ninguna fuente y no "
    "inventes datos."
)

MAX_ATTEMPTS = 3
BACKOFF_SECONDS = (0.5, 1.5)
RETRY_STATUS = frozenset({500, 502, 503, 504, 529})
RETRY_AFTER_MAX = 8.0


class LLMError(Exception):
    def __init__(self, message: str, reason: str = "upstream") -> None:
        super().__init__(message)
        self.reason = reason


def build_prompt(question: str, hits: list[dict]) -> str:
    blocks = []
    for h in hits:
        blocks.append(f"[{h['title']} pág. {h['page']}]\n{h['text']}")
    return (
        "Fragmentos del manual:\n\n" + "\n\n---\n\n".join(blocks) +
        f"\n\nPregunta del usuario: {question}"
    )


def _error_detail(resp: httpx.Response) -> str:
    """Detalle corto del cuerpo de error (para diagnóstico en el fallback)."""
    try:
        body = resp.read()
        msg = json.loads(body).get("error", {}).get("message", "")
        return str(msg)[:200]
    except Exception:  # noqa: BLE001 — el detalle es best-effort
        return ""


def _retry_after(resp: httpx.Response) -> float:
    raw = resp.headers.get("retry-after", "")
    try:
        return max(float(raw), 0.1)
    except ValueError:
        return 1.0


def stream_answer(question: str, hits: list[dict]) -> Iterator[str]:
    key = config.llm_api_key()
    if not key:
        raise LLMError("LLM_API_KEY no configurada", reason="no_key")
    if ratelimit.groq_limited():
        raise LLMError(
            "429 recientes de Groq; degradando sin llamar", reason="rate_limited"
        )
    # El cupo se consume recién acá: ni no_key ni el circuito abierto llaman
    # a Groq, y un presupuesto agotado tampoco.
    if not ratelimit.reservar_llamada_llm():
        raise LLMError(
            "presupuesto diario de LLM agotado", reason="rate_limited"
        )

    url = config.llm_base_url().rstrip("/") + "/chat/completions"
    payload = {
        "model": config.llm_model(),
        "stream": True,
        "temperature": 0.2,
        # free de Groq: OTPM 1000 valida usados + max_tokens por minuto;
        # con 400 caben ~4-8 respuestas/min y las típicas son ~150 tokens.
        "max_tokens": 400,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": build_prompt(question, hits)},
        ],
    }
    headers = {"Authorization": f"Bearer {key}"}
    deadline = time.monotonic() + config.llm_timeout()
    last: LLMError | None = None
    wait_override: float | None = None

    for attempt in range(MAX_ATTEMPTS):
        if attempt:
            remaining = deadline - time.monotonic()
            if remaining < 2:
                break
            wait = (wait_override if wait_override is not None
                    else BACKOFF_SECONDS[attempt - 1])
            wait_override = None
            time.sleep(min(wait, max(remaining - 1, 0)))
        started = False
        try:
            timeout = max(deadline - time.monotonic(), 1.0)
            with httpx.stream(
                "POST", url,
                json=payload,
                headers=headers,
                timeout=timeout,
            ) as resp:
                if resp.status_code == 429:
                    ratelimit.note_groq_429()
                    err = LLMError("HTTP 429 rate limit", reason="rate_limited")
                    wait = _retry_after(resp)
                    if wait > RETRY_AFTER_MAX:
                        raise err
                    wait_override = wait
                    last = err
                    continue
                if resp.status_code != 200:
                    detail = _error_detail(resp)
                    err = LLMError(
                        f"HTTP {resp.status_code} {detail}".strip()
                    )
                    if resp.status_code not in RETRY_STATUS:
                        raise err
                    last = err
                    continue
                yielded = False
                for line in resp.iter_lines():
                    if not line.startswith("data:"):
                        continue
                    data = line[5:].strip()
                    if data == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                    except json.JSONDecodeError:
                        continue
                    if "error" in chunk:
                        msg = str(chunk["error"])[:200]
                        raise LLMError(
                            f"stream: {msg}",
                            reason="interrupted" if started else "upstream",
                        )
                    choices = chunk.get("choices") or [{}]
                    delta = (choices[0].get("delta") or {}).get("content") or ""
                    if delta:
                        started = True
                        yielded = True
                        yield delta
                if not yielded:
                    raise LLMError("respuesta vacía del LLM")
                return
        except httpx.TimeoutException as exc:
            if started:
                raise LLMError(str(exc), reason="interrupted") from exc
            last = LLMError(str(exc), reason="timeout")
            continue
        except httpx.HTTPError as exc:
            if started:
                raise LLMError(str(exc), reason="interrupted") from exc
            last = LLMError(str(exc))
            continue

    if last is not None:
        raise last
    raise LLMError("timeout: sin tiempo para responder", reason="timeout")
