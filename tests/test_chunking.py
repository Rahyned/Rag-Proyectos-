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
    assert c.to_dict() == {"chunk_id": "d:p1:0", "doc_id": "d",
                           "title": "Doc", "page": 1, "text": "texto"}
