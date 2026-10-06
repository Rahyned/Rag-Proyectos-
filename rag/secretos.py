"""Guardrail de repo público: la ingesta no indexa secretos ni nombres sensibles."""

import re
import unicodedata
from pathlib import Path

_ACCENT_RE = re.compile(r"[\u0300-\u036f]")
_PRIVADA = re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----")
_CUIT = re.compile(r"\b\d{2}-\d{8}-\d\b")
_EMAIL = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
_AWS = re.compile(r"\bAKIA[0-9A-Z]{16}\b")
_SK = re.compile(r"\b(?:sk|pk|rk)_(?:live|test)_[A-Za-z0-9]{8,}\b")
_GH = re.compile(r"\b(?:ghp|gho|github_pat)_[A-Za-z0-9_]{10,}\b")
_HF = re.compile(r"\bhf_[A-Za-z0-9]{10,}\b")
_BEARER = re.compile(r"\bBearer\s+[A-Za-z0-9\-._]{20,}")
_ASIGNACION = re.compile(
    r"(?i)\b(?:api[_-]?key|secret|access[_-]?token|token)\b\s*[:=]\s*['\"]?"
    r"[A-Za-z0-9\-._]{12,}"
)
_JWT = re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{5,}")
_NOMBRE_SENSIBLE = ("auditoria", "vulnerabilidad")


class SecretosError(ValueError):
    """Un documento del corpus no puede publicarse."""


def _plano(text: str) -> str:
    text = unicodedata.normalize("NFD", text.lower())
    return _ACCENT_RE.sub("", text)


def revisar_nombre(path: Path) -> None:
    """Falla si el nombre del archivo habla de auditoría o vulnerabilidades."""
    plano = _plano(path.name)
    for palabra in _NOMBRE_SENSIBLE:
        if palabra in plano:
            raise SecretosError(
                f"{path.name}: el nombre contiene '{palabra}' y no entra al repo público"
            )


def revisar_texto(texto: str, origen: str, emails_publicos: list[str]) -> None:
    """Falla con el motivo, sin repetir el secreto encontrado."""
    permitidos = {e.lower() for e in emails_publicos}
    if _PRIVADA.search(texto):
        raise SecretosError(f"{origen}: se detectó una clave privada")
    if _CUIT.search(texto):
        raise SecretosError(f"{origen}: se detectó un CUIT o CUIL")
    if any(p.search(texto) for p in (_AWS, _SK, _GH, _HF, _BEARER, _ASIGNACION, _JWT)):
        raise SecretosError(f"{origen}: se detectó una clave o un token")
    for email in _EMAIL.findall(texto):
        if email.lower() not in permitidos:
            raise SecretosError(f"{origen}: email fuera de la allowlist del manifiesto")
