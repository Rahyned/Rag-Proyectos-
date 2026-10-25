"""Default de EMBEDDINGS_PROVIDER en scripts/eval_gold.py."""

import pytest

from scripts.eval_gold import default_embeddings_provider


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
        ({}, "off"),
    ],
)
def test_default_embeddings_provider(env, esperado):
    assert default_embeddings_provider(env) == esperado
