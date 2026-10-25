"""Helpers de scripts/eval_gold.py (sin red)."""

from unittest.mock import MagicMock, patch

import pytest

from scripts.eval_gold import (
    _comparar_reranker,
    _configurar_rerank,
    default_embeddings_provider,
    estimar_llamadas_cloudflare,
    flags_cli,
    top_ns_rerank,
)
from rag.config import rag_rerank, rag_rerank_weight


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
    "argv, rerank, solo",
    [
        ([], False, False),
        (["--rerank"], True, False),
        (["--solo-top10"], True, True),
        (["--rerank", "--solo-top10"], True, True),
        (["--solo-rerank-top10"], True, True),
    ],
)
def test_flags_cli(argv, rerank, solo):
    assert flags_cli(argv) == (rerank, solo)


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
