"""Tests unitarios del chunking, tokenizado y fusión RRF (sin modelo)."""

from rag.chunking import Chunk, clean_text, split_page
from rag.hybrid import bm25_scores, rrf, tokenize


def test_clean_text_join_hyphen_and_spaces():
    text = "prime-\nra línea    con  espacios\n\n\n\nsegunda"
    out = clean_text(text)
    assert "primera línea con espacios" in out
    assert "\n\n\n" not in out


def test_split_page_respects_max_chars():
    text = " ".join(f"Oración número {i} del fragmento." for i in range(80))
    pieces = split_page(text, max_chars=200, overlap=40)
    assert len(pieces) > 1
    assert all(len(p) <= 200 + 40 for p in pieces)
    assert all(p.strip() for p in pieces)


def test_split_page_never_crosses_page():
    text = "Párrafo corto.\n\nOtro párrafo corto."
    assert split_page(text, max_chars=1200) == [text]


def test_stem_unifies_conjugations():
    assert tokenize("agrego") == tokenize("agregar")
    assert tokenize("clientes") == tokenize("cliente")
    assert tokenize("restauro") == tokenize("restaurar")
    assert tokenize("trabajos") == tokenize("trabajo")


def test_tokenize_strips_accents():
    assert tokenize("Corrección") == ["correccion"]


def test_bm25_ranks_relevant_chunk_higher():
    docs = [
        tokenize("cómo agregar un cliente nuevo con lista de precios"),
        tokenize("informe mensual de producción del laboratorio"),
    ]
    df = {}
    for tokens in docs:
        for t in set(tokens):
            df[t] = df.get(t, 0) + 1
    scores = bm25_scores("agregar cliente", docs, df, len(docs))
    assert scores[0] > scores[1]


def test_rrf_favors_documents_ranked_by_both_signals():
    import numpy as np

    dense = np.array([0.9, 0.5, 0.1], dtype=np.float32)
    lex = np.array([0.8, 0.6, 0.0], dtype=np.float32)
    combined = rrf(dense, lex)
    assert combined.argmax() == 0


def test_chunk_dataclass_roundtrip():
    c = Chunk("d:p1:0", "d", "Doc", 1, "texto")
    data = c.to_dict()
    assert data["chunk_id"] == "d:p1:0"
    assert data["page"] == 1
    assert data["proyecto"] == ""
    assert data["publico"] is False


def test_markdown_corta_por_encabezados_y_no_aplana_tablas():
    from rag.chunking import MIN_CHUNK_CHARS, chunk_markdown

    md = """# Guia

## Alta de clientes

Esta seccion explica como dar de alta un cliente nuevo en el laboratorio con todos los campos obligatorios del formulario.

## Precios

| Rubro | Precio |
| --- | --- |
| Corona | 1000 |
| Puente | 2000 |

### Nota breve

ok
"""
    chunks = chunk_markdown(
        md, "guia", "Guia del proyecto",
        proyecto="cars", proyecto_nombre="SolutionsCars", tipo="ficha",
        publico=True, pdf=None, url_publica=None,
    )
    from rag.chunking import anteponer_ruta
    anteponer_ruta(chunks)
    textos = [c.text for c in chunks]
    assert any("Alta de clientes" in c.seccion for c in chunks)
    assert any(c.seccion.startswith("Guia › Alta") for c in chunks)
    tabla = next(c for c in chunks if "| Rubro | Precio |" in c.text)
    assert "| Corona | 1000 |" in tabla.text
    assert "SolutionsCars › Guia del proyecto ›" in tabla.text
    prosa = [c for c in chunks if "| Rubro |" not in c.text]
    assert prosa
    assert all(len(c.text.split("\n\n", 1)[-1]) >= MIN_CHUNK_CHARS or " › " in c.text
               for c in prosa)
    assert not any(c.text.strip() == "ok" for c in chunks)
