"""API de Jina con httpx falso: sin red, sin key en los logs."""

import logging

import httpx
import numpy as np
import pytest

from rag.embeddings import EmbedError, JinaEmbeddings


def _cliente(handler):
    return httpx.Client(transport=httpx.MockTransport(handler))


def _ok(calls, key="jina-test-key"):
    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.headers.get("authorization"))
        assert request.headers["authorization"] == f"Bearer {key}"
        emb = [0.0, 0.0, 1.0]
        return httpx.Response(200, json={"data": [{"index": 0, "embedding": emb}]})
    return handler


def test_jina_con_key_y_cache(monkeypatch):
    monkeypatch.setenv("JINA_API_KEY", "jina-test-key")
    monkeypatch.setenv("JINA_DAILY_BUDGET", "10")
    calls = []
    jina = JinaEmbeddings(client=_cliente(_ok(calls)))
    primero = jina.embed_consulta("mismo texto")
    segundo = jina.embed_consulta("mismo texto")
    assert len(calls) == 1
    assert primero.shape == (1, 3)
    assert np.allclose(primero, segundo)


def test_sin_key_no_llama(monkeypatch):
    monkeypatch.delenv("JINA_API_KEY", raising=False)
    calls = []

    def handler(_request):
        calls.append(1)
        return httpx.Response(200, json={"data": []})

    jina = JinaEmbeddings(client=_cliente(handler))
    with pytest.raises(EmbedError, match="sin_key"):
        jina.embed_consulta("hola")
    assert calls == []


def test_timeout_y_error_http(monkeypatch):
    monkeypatch.setenv("JINA_API_KEY", "jina-test-key")
    monkeypatch.setenv("JINA_DAILY_BUDGET", "0")

    def timeout(_request):
        raise httpx.TimeoutException("lento")

    jina = JinaEmbeddings(client=_cliente(timeout))
    with pytest.raises(EmbedError, match="timeout"):
        jina.embed_consulta("hola")

    def error(_request):
        return httpx.Response(503, json={"detail": "caido"})

    jina = JinaEmbeddings(client=_cliente(error))
    with pytest.raises(EmbedError, match="http_error"):
        jina.embed_consulta("hola")

    def cuota(_request):
        return httpx.Response(429, json={"detail": "quota"})

    jina = JinaEmbeddings(client=_cliente(cuota))
    with pytest.raises(EmbedError, match="cuota"):
        jina.embed_consulta("hola")


def test_presupuesto_agotado_no_llama(monkeypatch):
    monkeypatch.setenv("JINA_API_KEY", "jina-test-key")
    monkeypatch.setenv("JINA_DAILY_BUDGET", "1")
    calls = []
    jina = JinaEmbeddings(client=_cliente(_ok(calls)))
    jina.embed_consulta("primera consulta distinta")
    with pytest.raises(EmbedError, match="presupuesto"):
        jina.embed_consulta("segunda consulta distinta")
    assert len(calls) == 1


def test_log_de_fallback_no_incluye_la_key(monkeypatch, tmp_path, caplog):
    import faiss

    from rag.hybrid import HybridRetriever

    monkeypatch.setenv("EMBEDDINGS_PROVIDER", "api")
    monkeypatch.setenv("JINA_API_KEY", "jina-super-secreta")
    chunks = tmp_path / "chunks.jsonl"
    chunks.write_text(
        '{"chunk_id":"a:p1:0","doc_id":"a","title":"A","page":1,'
        '"text":"como agregar un cliente nuevo en el laboratorio",'
        '"proyecto":"stella","proyecto_nombre":"STELLA","seccion":"Clientes",'
        '"publico":true,"tipo":"manual"}\n',
        encoding="utf-8",
    )
    index = faiss.IndexFlatIP(4)
    index.add(np.ones((1, 4), dtype=np.float32))
    faiss.write_index(index, str(tmp_path / "index.faiss"))

    class Roto:
        def embed_consulta(self, _texto):
            raise EmbedError("timeout")

    retriever = HybridRetriever(
        chunks, tmp_path / "index.faiss", embedder=Roto(),
    )
    with caplog.at_level(logging.WARNING):
        hits = retriever.search("agregar un cliente nuevo", 3, proyecto="stella")
    assert hits
    assert hits[0]["engine"] == "bm25"
    texto = " ".join(caplog.messages)
    assert "timeout" in texto
    assert "jina-super-secreta" not in texto
