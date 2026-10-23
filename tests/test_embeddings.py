"""Embudo de embeddings con httpx falso: sin red, sin keys en los logs."""

import json
import logging

import httpx
import numpy as np
import pytest

from app import ratelimit
from rag.config import CF_EMBED_URL
from rag.embeddings import (CloudflareEmbeddings, EmbedError,
                            JinaEmbeddings)


def _cliente(handler):
    return httpx.Client(transport=httpx.MockTransport(handler))


def _ok(calls, key="jina-test-key"):
    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.headers.get("authorization"))
        assert request.headers["authorization"] == f"Bearer {key}"
        emb = [0.0, 0.0, 1.0]
        return httpx.Response(200, json={"data": [{"index": 0, "embedding": emb}]})
    return handler


def test_embed_timeout_es_configurable(monkeypatch):
    import importlib

    from rag import config as rag_config

    monkeypatch.setenv("EMBED_TIMEOUT_S", "1.5")
    importlib.reload(rag_config)
    assert rag_config.EMBED_TIMEOUT == 1.5

    monkeypatch.setenv("EMBED_TIMEOUT_S", "no-es-numero")
    importlib.reload(rag_config)
    assert rag_config.EMBED_TIMEOUT == 2.0

    monkeypatch.delenv("EMBED_TIMEOUT_S", raising=False)
    importlib.reload(rag_config)
    assert rag_config.EMBED_TIMEOUT == 2.0


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
    ratelimit.reset()

    def error(_request):
        return httpx.Response(503, json={"detail": "caido"})

    jina = JinaEmbeddings(client=_cliente(error))
    with pytest.raises(EmbedError, match="http_error"):
        jina.embed_consulta("hola")
    ratelimit.reset()

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


def test_timeout_pausa_jina_y_no_gasta_cupo(monkeypatch, caplog):
    monkeypatch.setenv("JINA_API_KEY", "jina-test-key")
    monkeypatch.setenv("JINA_DAILY_BUDGET", "1")
    calls = []

    def timeout(_request):
        calls.append(1)
        raise httpx.TimeoutException("lento")

    jina = JinaEmbeddings(client=_cliente(timeout))
    with caplog.at_level(logging.WARNING, logger="rag.embeddings"):
        with pytest.raises(EmbedError, match="timeout"):
            jina.embed_consulta("primera")
        with pytest.raises(EmbedError, match="timeout"):
            jina.embed_consulta("segunda")
    with pytest.raises(EmbedError, match="circuito"):
        jina.embed_consulta("tercera")
    # Sin reintento: el segundo timeout abre el circuito.
    assert calls == [1, 1]
    assert not any(k.startswith("jina:budget:") for k in ratelimit._budget)
    assert "timeout" in " ".join(caplog.messages)
    assert "jina-test-key" not in " ".join(caplog.messages)


def test_un_timeout_aislado_no_abre_el_circuito(monkeypatch):
    monkeypatch.setenv("JINA_API_KEY", "jina-test-key")
    monkeypatch.setenv("JINA_DAILY_BUDGET", "0")

    def timeout(_request):
        raise httpx.TimeoutException("lento")

    jina = JinaEmbeddings(client=_cliente(timeout))
    with pytest.raises(EmbedError, match="timeout"):
        jina.embed_consulta("consulta aislada")
    assert not ratelimit.jina_en_pausa()
    # El origen se ve igual, aunque el circuito todavía no esté abierto.
    assert ratelimit.jina_origen_circuito() == "timeout"


def test_dos_timeouts_en_60s_abren_el_circuito(monkeypatch):
    monkeypatch.setenv("JINA_API_KEY", "jina-test-key")
    monkeypatch.setenv("JINA_DAILY_BUDGET", "0")

    def timeout(_request):
        raise httpx.TimeoutException("lento")

    jina = JinaEmbeddings(client=_cliente(timeout))
    for texto in ("consulta uno", "consulta dos"):
        with pytest.raises(EmbedError, match="timeout"):
            jina.embed_consulta(texto)
    assert ratelimit.jina_en_pausa()
    assert ratelimit.jina_origen_circuito() == "timeout"


def test_429_abre_el_circuito_enseguida(monkeypatch):
    monkeypatch.setenv("JINA_API_KEY", "jina-test-key")
    monkeypatch.setenv("JINA_DAILY_BUDGET", "0")

    def cuota(_request):
        return httpx.Response(429, json={"detail": "quota"})

    jina = JinaEmbeddings(client=_cliente(cuota))
    with pytest.raises(EmbedError, match="cuota"):
        jina.embed_consulta("hola")
    assert ratelimit.jina_en_pausa()
    assert ratelimit.jina_origen_circuito() == "status_429"


def test_5xx_falla_rapido_sin_reintento(monkeypatch):
    monkeypatch.setenv("JINA_API_KEY", "jina-test-key")
    monkeypatch.setenv("JINA_DAILY_BUDGET", "0")
    llamadas = []

    def handler(_request):
        llamadas.append(1)
        return httpx.Response(503, json={"detail": "caido"})

    jina = JinaEmbeddings(client=_cliente(handler))
    with pytest.raises(EmbedError, match="http_error"):
        jina.embed_consulta("consulta con 5xx")
    assert llamadas == [1]
    assert not ratelimit.jina_en_pausa()
    assert ratelimit.jina_origen_circuito() == "status_5xx"

    # El segundo 5xx en la ventana abre el circuito.
    with pytest.raises(EmbedError, match="http_error"):
        jina.embed_consulta("segunda consulta")
    assert llamadas == [1, 1]
    assert ratelimit.jina_en_pausa()
    assert ratelimit.jina_origen_circuito() == "status_5xx"


def test_4xx_no_abre_el_circuito(monkeypatch):
    monkeypatch.setenv("JINA_API_KEY", "jina-test-key")
    monkeypatch.setenv("JINA_DAILY_BUDGET", "0")
    llamadas = []

    def bad_request(_request):
        llamadas.append(1)
        return httpx.Response(400, json={"detail": "mal pedido"})

    jina = JinaEmbeddings(client=_cliente(bad_request))
    with pytest.raises(EmbedError, match="http_error"):
        jina.embed_consulta("hola")
    assert llamadas == [1]
    assert not ratelimit.jina_en_pausa()
    assert ratelimit.jina_origen_circuito() is None


def test_el_cliente_http_se_reutiliza(monkeypatch):
    monkeypatch.setenv("JINA_API_KEY", "jina-test-key")
    monkeypatch.setenv("JINA_DAILY_BUDGET", "0")
    creados = []

    class _Unico:
        def __init__(self, *args, **kwargs):
            creados.append(self)

        def post(self, *args, **kwargs):
            url = args[0] if args else kwargs.get("url", "https://api.jina.ai")
            return httpx.Response(
                200,
                json={"data": [{"index": 0, "embedding": [0.0, 0.0, 1.0]}]},
                request=httpx.Request("POST", url),
            )

        def close(self):
            pass

    monkeypatch.setattr("rag.embeddings.httpx.Client", _Unico)
    jina = JinaEmbeddings()
    jina.embed_consulta("consulta uno")
    jina.embed_consulta("consulta dos")
    assert len(creados) == 1


def test_status_5xx_queda_en_el_log(monkeypatch, caplog):
    monkeypatch.setenv("JINA_API_KEY", "jina-test-key")
    monkeypatch.setenv("JINA_DAILY_BUDGET", "0")

    def error(_request):
        return httpx.Response(503, json={"detail": "caido"})

    jina = JinaEmbeddings(client=_cliente(error))
    with caplog.at_level(logging.WARNING, logger="rag.embeddings"):
        with pytest.raises(EmbedError, match="http_error"):
            jina.embed_consulta("hola")
    assert "503" in " ".join(caplog.messages)
    assert "jina-test-key" not in " ".join(caplog.messages)


def test_la_pausa_tambien_vive_en_redis(monkeypatch):
    monkeypatch.setenv("UPSTASH_REDIS_REST_URL", "https://example.upstash.io")
    monkeypatch.setenv("UPSTASH_REDIS_REST_TOKEN", "token-falso")
    store = {}

    def pipeline(commands):
        out = []
        for cmd in commands:
            if cmd[0] == "SET":
                store[cmd[1]] = cmd[2]
                out.append({"result": "OK"})
            elif cmd[0] == "GET":
                out.append({"result": store.get(cmd[1])})
            else:
                out.append({"result": 0})
        return out

    monkeypatch.setattr(ratelimit, "_redis_pipeline", pipeline)
    ratelimit.abrir_pausa_jina()
    ratelimit._jina_pause_until = 0.0
    assert store.get("jina:circuit") == "1"
    assert ratelimit.jina_en_pausa()


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


def _cliente_cloudflare(handler):
    return httpx.Client(transport=httpx.MockTransport(handler))


def _configurar_cloudflare(monkeypatch, budget: str = "0") -> None:
    monkeypatch.setenv("CF_ACCOUNT_ID", "cuenta-test")
    monkeypatch.setenv("CF_API_TOKEN", "cf-test-token")
    monkeypatch.setenv("CF_DAILY_BUDGET", budget)


def test_cloudflare_parsea_result_data_y_normaliza(monkeypatch):
    _configurar_cloudflare(monkeypatch)
    llamadas = []

    def handler(request: httpx.Request) -> httpx.Response:
        llamadas.append(request)
        assert json.loads(request.content) == {"text": ["uno", "dos"]}
        assert str(request.url) == CF_EMBED_URL.format(account_id="cuenta-test")
        assert request.headers["authorization"] == "Bearer cf-test-token"
        return httpx.Response(200, json={
            "success": True,
            "result": {"data": [[3.0, 4.0], [0.0, 5.0]]},
        })

    cf = CloudflareEmbeddings(client=_cliente_cloudflare(handler))
    vectores = cf.embed_lote(["uno", "dos"])
    assert len(llamadas) == 1
    assert vectores.shape == (2, 2)
    assert np.allclose(vectores[0], [0.6, 0.8])
    assert np.allclose(np.linalg.norm(vectores, axis=1), 1.0)


def test_cloudflare_ingesta_en_lotes_de_50(monkeypatch):
    _configurar_cloudflare(monkeypatch)
    lotes = []

    def handler(request: httpx.Request) -> httpx.Response:
        textos = json.loads(request.content)["text"]
        lotes.append(len(textos))
        return httpx.Response(200, json={
            "success": True,
            "result": {"data": [[1.0, 0.0] for _ in textos]},
        })

    cf = CloudflareEmbeddings(client=_cliente_cloudflare(handler))
    vectores = cf.embed_lote([f"texto {i}" for i in range(120)])
    assert lotes == [50, 50, 20]
    assert vectores.shape == (120, 2)


def test_cloudflare_sin_key_no_llama(monkeypatch):
    monkeypatch.delenv("CF_ACCOUNT_ID", raising=False)
    monkeypatch.delenv("CF_API_TOKEN", raising=False)
    llamadas = []

    def handler(_request):
        llamadas.append(1)
        return httpx.Response(200, json={"result": {"data": []}})

    cf = CloudflareEmbeddings(client=_cliente_cloudflare(handler))
    with pytest.raises(EmbedError, match="sin_key"):
        cf.embed_consulta("hola")
    assert llamadas == []


def test_cloudflare_timeout_es_embederror(monkeypatch):
    _configurar_cloudflare(monkeypatch)

    def timeout(_request):
        raise httpx.TimeoutException("lento")

    cf = CloudflareEmbeddings(client=_cliente_cloudflare(timeout))
    with pytest.raises(EmbedError, match="timeout"):
        cf.embed_consulta("hola")
    assert not ratelimit.cloudflare_en_pausa()
    assert ratelimit.cloudflare_origen_circuito() == "timeout"


def test_cloudflare_cache_no_repite_la_red(monkeypatch):
    _configurar_cloudflare(monkeypatch, budget="10")
    llamadas = []

    def handler(_request):
        llamadas.append(1)
        return httpx.Response(200, json={
            "success": True,
            "result": {"data": [[1.0, 0.0]]},
        })

    cf = CloudflareEmbeddings(client=_cliente_cloudflare(handler))
    primero = cf.embed_consulta("mismo texto")
    segundo = cf.embed_consulta("mismo texto")
    assert len(llamadas) == 1
    assert primero.shape == (1, 2)
    assert np.allclose(primero, segundo)
