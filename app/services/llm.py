"""Generación de respuesta sintética con LLM (Gemini vía HTTP, opcional).

Si no hay LLM_API_KEY o la llamada falla, se lanza LLMError y el endpoint
cae al modo fragmentos: nunca se rompe la consulta.
"""

import json
from collections.abc import Iterator

import httpx

from app import config

SYSTEM = (
    "Sos el asistente del Manual STELLA, un sistema de gestión para "
    "laboratorios odontológicos. Respondé en español rioplatense (voseo), "
    "claro y breve, usando SOLO la información de los fragmentos del manual "
    "que se te proveen. Citá la fuente entre corchetes al final de cada "
    "afirmación, por ejemplo [Manual STELLA p. 15]. Si la respuesta no está "
    "en los fragmentos, decilo explícitamente y no inventes datos."
)


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


def stream_answer(question: str, hits: list[dict]) -> Iterator[str]:
    key = config.llm_api_key()
    if not key:
        raise LLMError("LLM_API_KEY no configurada")

    payload = {
        "systemInstruction": {"parts": [{"text": SYSTEM}]},
        "contents": [{"role": "user",
                      "parts": [{"text": build_prompt(question, hits)}]}],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 1024},
    }
    url = f"{config.llm_base_url()}/models/{config.llm_model()}:streamGenerateContent"
    try:
        with httpx.stream(
            "POST", url,
            params={"alt": "sse", "key": key},
            json=payload,
            timeout=config.llm_timeout(),
        ) as resp:
            resp.raise_for_status()
            yielded = False
            for line in resp.iter_lines():
                if not line.startswith("data:"):
                    continue
                try:
                    data = json.loads(line[5:].strip())
                except json.JSONDecodeError:
                    continue
                for part in data.get("candidates", [{}])[0].get(
                        "content", {}).get("parts", []):
                    text = part.get("text", "")
                    if text:
                        yielded = True
                        yield text
            if not yielded:
                raise LLMError("respuesta vacía del LLM")
    except (httpx.HTTPError, KeyError) as exc:
        raise LLMError(str(exc)) from exc
