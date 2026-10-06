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


@pytest.mark.parametrize("texto", [
    "LLM_API_KEY=abcdefghijklmno1",
    "JINA_API_KEY=abcdefghijklmno1",
    "UPSTASH_REDIS_REST_TOKEN=abcdefghijklmno1",
    "gsk_" + "a" * 20,
    "jina_" + "b" * 20,
    "sk-" + "c" * 20,
    "sk-proj-" + "d" * 20,
    "AIza" + "e" * 35,
    "UPSTASH=" + "f" * 22,
])
def test_bloquea_claves_falsas(texto):
    with pytest.raises(SecretosError, match="clave o un token"):
        revisar_texto(texto, "doc.md", [])


def test_el_corpus_actual_no_dispara_el_guardrail():
    from pypdf import PdfReader

    from rag.config import CORPUS_DIR
    from rag.manifiesto import cargar

    emails = cargar()["emails_publicos"]
    archivos = [
        p for p in CORPUS_DIR.rglob("*")
        if p.is_file() and not p.name.startswith("_")
    ]
    assert archivos
    for path in archivos:
        revisar_nombre(path)
        if path.suffix.lower() == ".md":
            revisar_texto(path.read_text(encoding="utf-8"), path.name, emails)
        elif path.suffix.lower() == ".pdf":
            texto = "\n".join(
                (pagina.extract_text() or "") for pagina in PdfReader(str(path)).pages
            )
            revisar_texto(texto, path.name, emails)


def test_nombre_de_archivo_sensible():
    with pytest.raises(SecretosError, match="auditoria"):
        revisar_nombre(Path("informe-auditoría-interna.md"))
    with pytest.raises(SecretosError, match="vulnerabilidad"):
        revisar_nombre(Path("Vulnerabilidad-abierta.pdf"))
