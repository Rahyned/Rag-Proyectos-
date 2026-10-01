"""Configuración de la API (variables de entorno, todas opcionales)."""

import os


def llm_api_key() -> str:
    return os.getenv("LLM_API_KEY", "")


def llm_model() -> str:
    return os.getenv("LLM_MODEL", "gemini-2.0-flash")


def llm_base_url() -> str:
    return os.getenv(
        "LLM_BASE_URL",
        "https://generativelanguage.googleapis.com/v1beta",
    )


def llm_timeout() -> float:
    return float(os.getenv("LLM_TIMEOUT", "60"))
