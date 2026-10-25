"""Helpers de scripts/eval_gold.py (sin red)."""

from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from scripts.eval_gold import (
    Flags,
    RRF_KS,
    RRF_WEIGHTS,
    _cache_canales,
    _comparar_reranker,
    _configurar_rerank,
    _formato_esperado,
    _hit_counts,
    default_embeddings_provider,
    estimar_llamadas_cloudflare,
    flags_cli,
    top_ns_rerank,
)
from rag.config import rag_rerank, rag_rerank_weight
from rag.hybrid import rrf


@pytest.mark.parametrize(
    "env, esperado",
    [
        (
            {"CF_ACCOUNT_ID": "cuenta", "CF_API_TOKEN": "token"},
            "cloudflare",
        ),
        (
            {
                "CF_ACCOUNT_ID": "cuenta",
                "CF_API_TOKEN": "token",
                "JINA_API_KEY": "jina",
            },
            "cloudflare",
        ),
        ({"JINA_API_KEY": "jina"}, "api"),
        ({"CF_ACCOUNT_ID": "cuenta"}, "off"),
        ({"CF_API_TOKEN": "token"}, "off"),
        ({"CF_ACCOUNT_ID": "  ", "CF_API_TOKEN": "token"}, "off"),
        ({}, "off"),
    ],
)
def test_default_embeddings_provider(env, esperado):
    assert default_embeddings_provider(env) == esperado


def test_top_ns_rerank():
    assert top_ns_rerank(False) == (20, 10)
    assert top_ns_rerank(True) == (10,)


@pytest.mark.parametrize(
    "argv, esperado",
    [
        ([], Flags()),
        (["--rerank"], Flags(rerank=True)),
        (["--solo-top10"], Flags(rerank=True, solo_top10=True)),
        (["--rerank", "--solo-top10"], Flags(rerank=True, solo_top10=True)),
        (["--solo-rerank-top10"], Flags(rerank=True, solo_top10=True)),
        (["--fallos"], Flags(fallos=True)),
        (["--rrf-grid"], Flags(rrf_grid=True)),
        (["--fallos", "--rrf-grid"], Flags(fallos=True, rrf_grid=True)),
    ],
)
def test_flags_cli(argv, esperado):
    assert flags_cli(argv) == esperado


@pytest.mark.parametrize(
    "kwargs, esperado",
    [
        (
            {
                "provider": "cloudflare",
                "rerank": True,
                "top_ns": (20, 10),
                "n_consultas_embed": 152,
                "n_consultas_rerank": 100,
            },
            (152, 200, 352),
        ),
        (
            {
                "provider": "cloudflare",
                "rerank": True,
                "top_ns": (10,),
                "n_consultas_embed": 152,
                "n_consultas_rerank": 100,
            },
            (152, 100, 252),
        ),
        (
            {
                "provider": "api",
                "rerank": True,
                "top_ns": (20, 10),
                "n_consultas_embed": 152,
                "n_consultas_rerank": 100,
            },
            (0, 200, 200),
        ),
        (
            {
                "provider": "cloudflare",
                "rerank": False,
                "top_ns": (20, 10),
                "n_consultas_embed": 152,
                "n_consultas_rerank": 100,
            },
            (152, 0, 152),
        ),
        (
            {
                "provider": "off",
                "rerank": False,
                "top_ns": (),
                "n_consultas_embed": 152,
                "n_consultas_rerank": 100,
            },
            (0, 0, 0),
        ),
    ],
)
def test_estimar_llamadas_cloudflare(kwargs, esperado):
    assert estimar_llamadas_cloudflare(**kwargs) == esperado


def test_comparar_reranker_solo_top10_no_configura_top20():
    """Con top_ns=(10,) no pide RERANK_TOP_N=20."""
    tops: list[int] = []

    def capturar(**kwargs):
        if kwargs.get("enabled"):
            tops.append(kwargs["top_n"])

    entries = [{"q": "hola", "proyecto": "stella", "v1": True, "section": "x"}]
    with patch("scripts.eval_gold._configurar_rerank", side_effect=capturar), \
         patch("scripts.eval_gold._tabla"), \
         patch("scripts.eval_gold._resumen_gold"):
        _comparar_reranker(MagicMock(), entries, top_ns=(10,))

    assert 20 not in tops
    assert tops.count(10) >= 1


def test_configurar_rerank_pisa_rag_rerank_del_entorno(monkeypatch):
    """--rerank mide fuse/replace aunque producción tenga RAG_RERANK=off."""
    monkeypatch.setenv("RAG_RERANK", "off")
    monkeypatch.setenv("RAG_RERANK_WEIGHT", "0.1")
    _configurar_rerank(enabled=True, mode="fuse", peso=0.7, top_n=10)
    assert rag_rerank() == "fuse"
    assert rag_rerank_weight() == 0.7
    _configurar_rerank(enabled=True, mode="replace", peso=0.5, top_n=10)
    assert rag_rerank() == "replace"
    _configurar_rerank(enabled=False)
    assert rag_rerank() == "off"


def test_formato_esperado_pagina_y_seccion():
    assert "pág. 3" in _formato_esperado({
        "doc_id": "manual", "page": 3, "proyecto": "stella",
    })
    assert "Intro" in _formato_esperado({
        "doc_id": "web", "section": "Intro", "proyecto": "portafolio-web",
    })
    assert "A" in _formato_esperado({
        "proyecto": "todos",
        "acepta": [
            {"doc_id": "a", "section": "A"},
            {"doc_id": "b", "page": 2},
        ],
    })


def test_rrf_con_peso_lexico_mayor_prioriza_bm25():
    dense = np.array([0.9, 0.1], dtype=np.float32)
    lex = np.array([0.1, 0.9], dtype=np.float32)
    assert rrf(dense, lex, w_lex=1.0, w_dense=1.0).argmax() in (0, 1)
    assert rrf(dense, lex, w_lex=3.0, w_dense=1.0).argmax() == 1
    assert rrf(dense, lex, w_lex=1.0, w_dense=3.0).argmax() == 0


def test_rrf_grid_constantes():
    assert RRF_WEIGHTS == ((1.0, 1.0), (1.5, 1.0), (2.0, 1.0), (3.0, 1.0))
    assert RRF_KS == (30, 60, 100)


def test_cache_canales_una_llamada_por_pregunta():
    retriever = MagicMock()
    retriever.scores_canales.side_effect = [
        (np.ones(2), np.ones(2), np.array([True, True])),
        (np.ones(2), np.ones(2), np.array([True, True])),
    ]
    entries = [
        {"q": "hola", "proyecto": "stella"},
        {"q": "hola", "proyecto": "stella"},
        {"q": "chau", "proyecto": "stella"},
    ]
    cache = _cache_canales(retriever, entries)
    assert retriever.scores_canales.call_count == 2
    assert len(cache) == 2


def test_hit_counts_usa_hits_rrf_sin_reembeber():
    retriever = MagicMock()
    retriever.hits_rrf.return_value = [
        {"chunk_id": "a", "doc_id": "d", "seccion": "S", "page": 1},
    ]
    lex = np.array([1.0, 0.0], dtype=np.float32)
    dense = np.array([0.5, 0.5], dtype=np.float32)
    allowed = np.array([True, True])
    cache = {("q", "stella"): (lex, dense, allowed)}
    entries = [{
        "q": "q", "proyecto": "stella", "doc_id": "d", "section": "S",
    }]
    with patch("scripts.eval_gold._acierto", return_value=True):
        n, h3, h5 = _hit_counts(
            retriever, entries, cache, k_rrf=60, w_lex=2.0, w_dense=1.0,
        )
    assert (n, h3, h5) == (1, 1, 1)
    retriever.hits_rrf.assert_called_once()
    kwargs = retriever.hits_rrf.call_args.kwargs
    assert kwargs["k"] == 60
    assert kwargs["w_lex"] == 2.0
    assert kwargs["w_dense"] == 1.0
    retriever.scores_canales.assert_not_called()
