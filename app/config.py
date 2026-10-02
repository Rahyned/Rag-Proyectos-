"""Configuración de la API (variables de entorno, todas opcionales)."""

import os


def llm_api_key() -> str:
    return os.getenv("LLM_API_KEY", "")


def llm_model() -> str:
    return os.getenv("LLM_MODEL", "qwen/qwen3.8-27b")


def llm_base_url() -> str:
    return os.getenv(
        "LLM_BASE_URL",
        "https://api.groq.com/openai/v1",
    )


def llm_timeout() -> float:
    # Presupuesto total de reintentos; debe dejar margen bajo maxDuration=60s.
    return float(os.getenv("LLM_TIMEOUT", "45"))
