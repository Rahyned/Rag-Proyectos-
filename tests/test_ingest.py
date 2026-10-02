"""Manifiesto de títulos del corpus (scripts/ingest.py)."""

import json

from scripts.ingest import MANIFIESTO_PATH, cargar_titulos


def test_cargar_titulos_real():
    """El manifiesto versionado cubre el manual STELLA."""
    assert MANIFIESTO_PATH.exists(), "corpus/manifiesto.json no existe"
    titulos = cargar_titulos()
    assert titulos["manual-stella"] == "Manual STELLA"


def test_cargar_titulos_sin_archivo_devuelve_vacio(tmp_path):
    assert cargar_titulos(tmp_path / "no-existe.json") == {}


def test_cargar_titulos_archivo_nuevo(tmp_path):
    path = tmp_path / "manifiesto.json"
    path.write_text(json.dumps({"otro-doc": "Otro documento"}),
                    encoding="utf-8")
    assert cargar_titulos(path) == {"otro-doc": "Otro documento"}
