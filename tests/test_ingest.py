"""Manifiesto multi-proyecto y hash del corpus."""

import json

import pytest

from rag.config import CHUNKS_PATH
from rag.manifiesto import MANIFIESTO_PATH, ManifiestoError, cargar, limpiar_cache, validar
from scripts.ingest import HASH_PATH, META_PATH, hash_corpus


def test_manifiesto_real_lista_stella():
    limpiar_cache()
    data = cargar()
    ids = [p["id"] for p in data["proyectos"]]
    assert ids == [
        "stella", "solutionscars", "laboratorio-riodent", "portafolio-web",
    ]
    assert data["emails_publicos"] == ["riodentlab@gmail.com"]
    stella = next(p for p in data["proyectos"] if p["id"] == "stella")
    assert stella["nombre"] == "STELLA"
    assert stella["documentos"][0]["titulo"] == "Manual STELLA"
    assert stella["documentos"][0]["tipo"] == "manual"
    assert stella["documentos"][0]["publico"] is True
    assert stella["preguntas"]
    cars = next(p for p in data["proyectos"] if p["id"] == "solutionscars")
    assert cars["nombre"] == "SolutionsCars"
    assert cars["url"] is None
    assert cars["documentos"][0]["tipo"] == "ficha"
    assert cars["documentos"][0]["publico"] is True
    assert len(cars["preguntas"]) == 3
    riodent = next(p for p in data["proyectos"] if p["id"] == "laboratorio-riodent")
    assert riodent["url"] == "https://www.riodent.com.ar"
    assert riodent["documentos"][0]["tipo"] == "ficha"
    assert len(riodent["preguntas"]) == 3
    portafolio = next(p for p in data["proyectos"] if p["id"] == "portafolio-web")
    assert portafolio["nombre"] == "portafolio-web"
    assert portafolio["url"] == "https://portafolio-web-three-gamma.vercel.app"
    assert portafolio["documentos"][0]["tipo"] == "ficha"
    assert len(portafolio["preguntas"]) == 3


def test_manifiesto_falta_campo(tmp_path):
    corpus = tmp_path / "corpus"
    (corpus / "demo").mkdir(parents=True)
    (corpus / "demo" / "nota.md").write_text("# Hola\n\nTexto largo del documento.\n", encoding="utf-8")
    raw = {"proyectos": [{
        "id": "demo",
        "nombre": "Demo",
        "documentos": [{
            "archivo": "nota.md",
            "titulo": "Nota",
            "tipo": "readme",
            "publico": True,
        }],
    }]}
    with pytest.raises(ManifiestoError, match="descripcion"):
        validar(raw, corpus)


def test_manifiesto_archivo_inexistente(tmp_path):
    raw = {"proyectos": [{
        "id": "demo",
        "nombre": "Demo",
        "descripcion": "Una ficha.",
        "documentos": [{
            "archivo": "no-esta.md",
            "titulo": "Nota",
            "tipo": "readme",
            "publico": True,
        }],
    }]}
    with pytest.raises(ManifiestoError, match="no existe"):
        validar(raw, tmp_path)


def test_hash_de_corpus_esta_al_dia():
    """El hash guardado al ingerir tiene que coincidir con corpus/."""
    assert MANIFIESTO_PATH.is_file()
    assert HASH_PATH.is_file(), "falta data/corpus.sha256: corré scripts/ingest.py"
    digest = hash_corpus()
    assert HASH_PATH.read_text(encoding="utf-8").strip() == digest
    meta = json.loads(META_PATH.read_text(encoding="utf-8"))
    assert meta["corpus_sha256"] == digest
    lineas = [ln for ln in CHUNKS_PATH.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(lineas) == meta["n_chunks"]
    assert meta["embed_model"]
