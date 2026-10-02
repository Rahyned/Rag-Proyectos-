"""Generación de respuesta sintética con LLM (compatible OpenAI, opcional).

Proveedor por defecto: Groq (base `LLM_BASE_URL` + `/chat/completions`).
Si no hay LLM_API_KEY o la llamada falla tras los reintentos, se lanza
LLMError y el endpoint cae al modo fragmentos: nunca se rompe la consulta.

Los reintentos (backoff) solo cubren 5xx/errores de red al iniciar el
stream; una vez que llegaron tokens no se reintenta (no duplicar texto).
"""

import json
import time
from collections.abc import Iterator

import httpx

from app import config

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


class LLMError(Exception):
    pass


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


def stream_answer(question: str, hits: list[dict]) -> Iterator[str]:
    key = config.llm_api_key()
    if not key:
        raise LLMError("LLM_API_KEY no configurada")

    url = config.llm_base_url().rstrip("/") + "/chat/completions"
    payload = {
        "model": config.llm_model(),
        "stream": True,
        "temperature": 0.2,
        "max_tokens": 800,  # tope free de Groq para qwen3.8-27b: 1000 OTPM
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": build_prompt(question, hits)},
        ],
    }
    headers = {"Authorization": f"Bearer {key}"}
    deadline = time.monotonic() + config.llm_timeout()
    last: LLMError | None = None

    for attempt in range(MAX_ATTEMPTS):
        if attempt:
            remaining = deadline - time.monotonic()
            if remaining < 2:
                break
            time.sleep(min(BACKOFF_SECONDS[attempt - 1], max(remaining - 1, 0)))
        started = False
        try:
            timeout = max(deadline - time.monotonic(), 1.0)
            with httpx.stream(
                "POST", url,
                json=payload,
                headers=headers,
                timeout=timeout,
            ) as resp:
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
                        raise LLMError(f"stream: {msg}")
                    choices = chunk.get("choices") or [{}]
                    delta = (choices[0].get("delta") or {}).get("content") or ""
                    if delta:
                        started = True
                        yielded = True
                        yield delta
                if not yielded:
                    raise LLMError("respuesta vacía del LLM")
                return
        except httpx.HTTPError as exc:
            if started:
                raise LLMError(str(exc)) from exc
            last = LLMError(str(exc))
            continue

    raise LLMError(str(last) if last else "sin respuesta del LLM")
