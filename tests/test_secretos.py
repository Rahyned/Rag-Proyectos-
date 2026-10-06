"""Guardrail de secretos: patrones reales, no la palabra «token» del manual."""

from pathlib import Path

import pytest

from rag.secretos import SecretosError, revisar_nombre, revisar_texto

MANUAL = (
    "La sesión guardada es un token de acceso, no tu contraseña. "
    "Cerrar sesión borra el token recordado."
)


def test_el_manual_habla_de_token_y_no_es_un_secreto():
    revisar_texto(MANUAL, "stella/manual-stella.md", [])


def test_rechaza_clave_privada_token_y_cuit():
    with pytest.raises(SecretosError, match="clave privada"):
        revisar_texto("-----BEGIN PRIVATE KEY-----\nabc", "doc.md", [])
    with pytest.raises(SecretosError, match="clave o un token"):
        revisar_texto("api_key=sk_live_abcdefghijklmnop", "doc.md", [])
    with pytest.raises(SecretosError, match="CUIT"):
        revisar_texto("el CUIT 20-12345678-3 no se publica", "doc.md", [])


def test_email_solo_si_esta_en_la_allowlist():
    revisar_texto("escribí a hola@laboratorio.test", "doc.md", ["hola@laboratorio.test"])
    with pytest.raises(SecretosError, match="email"):
        revisar_texto("escribí a otro@laboratorio.test", "doc.md", ["hola@laboratorio.test"])


def test_nombre_de_archivo_sensible():
    with pytest.raises(SecretosError, match="auditoria"):
        revisar_nombre(Path("informe-auditoría-interna.md"))
    with pytest.raises(SecretosError, match="vulnerabilidad"):
        revisar_nombre(Path("Vulnerabilidad-abierta.pdf"))
