"""Reranker con httpx falso: sin red, sin keys en los logs.

El pool híbrido se reordena y, ante cualquier fallo (error, timeout,
presupuesto agotado o circuito), la respuesta sigue con el orden del RRF.
"""

import json
import logging
import os

import faiss
import httpx
import numpy as np
import pytest

from app import ratelimit
from rag import rerank as rerank_mod
from rag.config import (CF_RERANK_URL, rag_rerank, rag_rerank_weight,
                        rerank_enabled)
from rag.hybrid import HybridRetriever
from rag.rerank import CloudflareReranker, RerankError

FILAS = [
    ("stella:p1:0", "agregar un cliente nuevo en el laboratorio"),
    ("stella:p2:1", "facturar un comprobante con afip"),
    ("stella:p3:2", "restaurar un backup de la base de datos"),
]
QUERY = "agregar un cliente nuevo en el laboratorio"


@pytest.mark.parametrize(
    "env, esperado",
    [
        ({}, "off"),
        ({"RAG_RERANK": "off"}, "off"),
        ({"RAG_RERANK": "fuse"}, "fuse"),
        ({"RAG_RERANK": "replace"}, "replace"),
        ({"RAG_RERANK": "raro"}, "off"),
        ({"RERANK_ENABLED": "1"}, "fuse"),
        ({"RERANK_ENABLED": "1", "RERANK_MODE": "replace"}, "replace"),
        ({"RAG_RERANK": "off", "RERANK_ENABLED": "1"}, "off"),
    ],
)
def test_rag_rerank_default_off(monkeypatch, env, esperado):
    for key, valor in env.items():
        monkeypatch.setenv(key, valor)
    assert rag_rerank() == esperado
    assert rerank_enabled() is (esperado != "off")


def test_rag_rerank_weight(monkeypatch):
    assert rag_rerank_weight() == 0.5
    monkeypatch.setenv("RAG_RERANK_WEIGHT", "0.7")
    assert rag_rerank_weight() == 0.7
    monkeypatch.delenv("RAG_RERANK_WEIGHT", raising=False)
    monkeypatch.setenv("RERANK_WEIGHT", "0.3")
    assert rag_rerank_weight() == 0.3


class EmbedderFijo:
    """El índice tiene e0, e1 y e2: la consulta siempre cae en e0."""

    def embed_consulta(self, _texto):
        return np.array([[1.0, 0.0, 0.0, 0.0]], dtype=np.float32)


class RerankerFalso:
    def __init__(self, error: RerankError | None = None) -> None:
        self.error = error
        self.llamadas: list[list[str]] = []

    def reordenar(self, _query, hits):
        self.llamadas.append([hit["chunk_id"] for hit in hits])
        if self.error is not None:
            raise self.error
        salida = []
        for rank, hit in enumerate(reversed(hits), start=1):
            item = dict(hit)
            item["rank"] = rank
            item["engine"] = "hibrida+rerank"
            salida.append(item)
        return salida


def _retriever(tmp_path, reranker=None) -> HybridRetriever:
    filas = [
        {
            "chunk_id": chunk_id,
            "doc_id": "stella",
            "title": "STELLA",
            "page": n,
            "text": texto,
            "proyecto": "stella",
            "proyecto_nombre": "STELLA",
            "seccion": "Sección",
            "publico": True,
            "tipo": "manual",
        }
        for n, (chunk_id, texto) in enumerate(FILAS, start=1)
    ]
    chunks = tmp_path / "chunks.jsonl"
    chunks.write_text(
        "\n".join(json.dumps(fila, ensure_ascii=False) for fila in filas) + "\n",
        encoding="utf-8",
    )
    index = faiss.IndexFlatIP(4)
    index.add(np.eye(3, 4, dtype=np.float32))
    index_path = tmp_path / "index.faiss"
    faiss.write_index(index, str(index_path))
    return HybridRetriever(
        chunks, index_path, embedder=EmbedderFijo(), reranker=reranker,
    )


def _baseline(tmp_path, monkeypatch) -> list[dict]:
    """Orden del RRF, con el reranker apagado y sin tocar el flag del test."""
    previo = os.environ.get("RERANK_ENABLED")
    monkeypatch.setenv("RERANK_ENABLED", "0")
    try:
        return _retriever(tmp_path).search(QUERY, 3, proyecto="stella")
    finally:
        if previo is None:
            monkeypatch.delenv("RERANK_ENABLED", raising=False)
        else:
            monkeypatch.setenv("RERANK_ENABLED", previo)


def _cliente(handler) -> httpx.Client:
    return httpx.Client(transport=httpx.MockTransport(handler))


def _configurar_cloudflare(monkeypatch, budget: str = "0") -> None:
    monkeypatch.setenv("CF_ACCOUNT_ID", "cuenta-test")
    monkeypatch.setenv("CF_API_TOKEN", "cf-test-token")
    # Cupo propio del reranker; embeddings de prod no se tocan.
    monkeypatch.setenv("CF_RERANK_DAILY_BUDGET", budget)
    monkeypatch.setenv("CF_DAILY_BUDGET", "0")


def _respuesta(scores: list[float]) -> httpx.Response:
    return httpx.Response(200, json={
        "success": True,
        "result": {
            "response": [
                {"id": i, "score": score} for i, score in enumerate(scores)
            ],
        },
    })


def test_reranker_mockeado_reordena_el_pool(tmp_path, monkeypatch):
    monkeypatch.setenv("RERANK_ENABLED", "1")
    monkeypatch.setenv("RERANK_MODE", "replace")
    monkeypatch.setenv("RERANK_TOP_N", "3")
    monkeypatch.setenv("RERANK_KEEP", "2")
    fake = RerankerFalso()
    retriever = _retriever(tmp_path, reranker=fake)

    hits = retriever.search(QUERY, 2, proyecto="stella")

    # El pool es el top del RRF (3 candidatos) y el reranker deja 2.
    assert len(fake.llamadas) == 1
    assert len(fake.llamadas[0]) == 3
    assert [hit["rank"] for hit in hits] == [1, 2]
    assert hits[0]["engine"] == "hibrida+rerank"
    assert hits[0]["chunk_id"] == fake.llamadas[0][-1]


def test_fuse_es_el_modo_por_defecto(tmp_path, monkeypatch):
    monkeypatch.setenv("RERANK_ENABLED", "1")
    fake = RerankerFalso()
    hits = _retriever(tmp_path, reranker=fake).search(
        QUERY, 3, proyecto="stella",
    )
    assert fake.llamadas
    assert all(hit["engine"] == "hibrida+fuse" for hit in hits)


def test_fuse_peso_cero_es_el_orden_rrf(tmp_path, monkeypatch):
    monkeypatch.setenv("RERANK_ENABLED", "1")
    esperado = _baseline(tmp_path, monkeypatch)
    monkeypatch.setenv("RERANK_MODE", "fuse")
    monkeypatch.setenv("RERANK_WEIGHT", "0")
    fake = RerankerFalso()

    hits = _retriever(tmp_path, reranker=fake).search(
        QUERY, 3, proyecto="stella",
    )

    # El reranker se consultó, pero el peso 0 no le deja mover nada.
    assert fake.llamadas
    assert [hit["chunk_id"] for hit in hits] == [
        hit["chunk_id"] for hit in esperado
    ]


def test_fuse_peso_uno_es_el_orden_del_reranker(tmp_path, monkeypatch):
    monkeypatch.setenv("RERANK_ENABLED", "1")
    monkeypatch.setenv("RERANK_MODE", "fuse")
    monkeypatch.setenv("RERANK_WEIGHT", "1")
    fake = RerankerFalso()

    hits = _retriever(tmp_path, reranker=fake).search(
        QUERY, 3, proyecto="stella",
    )

    assert [hit["chunk_id"] for hit in hits] == list(
        reversed(fake.llamadas[0])
    )


def test_fuse_peso_medio_mezcla_los_dos_ordenes(tmp_path, monkeypatch):
    monkeypatch.setenv("RERANK_ENABLED", "1")
    esperado = _baseline(tmp_path, monkeypatch)
    monkeypatch.setenv("RERANK_MODE", "fuse")
    monkeypatch.setenv("RERANK_WEIGHT", "0.5")

    hits = _retriever(tmp_path, reranker=RerankerFalso()).search(
        QUERY, 3, proyecto="stella",
    )

    # RRF = [A, B, C]; reranker = [C, B, A]. A 0.5, A y C empatan y B
    # (segundo en ambos) cae al final: gana el orden del RRF en el empate.
    assert [hit["chunk_id"] for hit in hits] == [
        esperado[0]["chunk_id"],
        esperado[2]["chunk_id"],
        esperado[1]["chunk_id"],
    ]


def test_fuse_respeta_keep(tmp_path, monkeypatch):
    monkeypatch.setenv("RERANK_ENABLED", "1")
    monkeypatch.setenv("RERANK_MODE", "fuse")
    monkeypatch.setenv("RERANK_KEEP", "2")

    hits = _retriever(tmp_path, reranker=RerankerFalso()).search(
        QUERY, 3, proyecto="stella",
    )

    assert len(hits) == 2


def test_modo_y_peso_del_entorno(monkeypatch):
    from rag import config as rag_config

    assert rag_config.rag_rerank() == "off"
    assert rag_config.rerank_mode() == "fuse"
    assert rag_config.rerank_weight() == 0.5

    monkeypatch.setenv("RAG_RERANK", "replace")
    assert rag_config.rerank_mode() == "replace"
    monkeypatch.setenv("RAG_RERANK", "raro")
    assert rag_config.rag_rerank() == "off"
    assert rag_config.rerank_mode() == "fuse"

    for valor in ("0", "0.3", "1"):
        monkeypatch.setenv("RAG_RERANK_WEIGHT", valor)
        assert rag_config.rerank_weight() == float(valor)
    for valor in ("-0.1", "1.1", "no-es-numero"):
        monkeypatch.setenv("RAG_RERANK_WEIGHT", valor)
        assert rag_config.rerank_weight() == 0.5


@pytest.mark.parametrize(
    "motivo", ["http_error", "timeout", "presupuesto", "circuito", "sin_key"]
)
def test_fallo_del_reranker_cae_al_rrf(tmp_path, monkeypatch, caplog, motivo):
    monkeypatch.setenv("RERANK_ENABLED", "1")
    esperado = _baseline(tmp_path, monkeypatch)
    fake = RerankerFalso(error=RerankError(motivo))
    retriever = _retriever(tmp_path, reranker=fake)

    with caplog.at_level(logging.WARNING, logger="rag.hybrid"):
        hits = retriever.search(QUERY, 3, proyecto="stella")

    assert [hit["chunk_id"] for hit in hits] == [
        hit["chunk_id"] for hit in esperado
    ]
    assert [hit["rank"] for hit in hits] == [1, 2, 3]
    assert all(hit["engine"] == "hibrida" for hit in hits)
    assert motivo in " ".join(caplog.messages)


def test_un_error_inesperado_tampoco_rompe(tmp_path, monkeypatch, caplog):
    monkeypatch.setenv("RERANK_ENABLED", "1")
    esperado = _baseline(tmp_path, monkeypatch)

    class Roto:
        def reordenar(self, _query, _hits):
            raise RuntimeError("boom")

    retriever = _retriever(tmp_path, reranker=Roto())
    with caplog.at_level(logging.WARNING, logger="rag.hybrid"):
        hits = retriever.search(QUERY, 3, proyecto="stella")
    assert [hit["chunk_id"] for hit in hits] == [
        hit["chunk_id"] for hit in esperado
    ]
    assert "boom" in " ".join(caplog.messages)


def test_con_rerank_apagado_el_comportamiento_es_el_de_hoy(tmp_path, monkeypatch):
    monkeypatch.setenv("RERANK_ENABLED", "0")
    fake = RerankerFalso()
    retriever = _retriever(tmp_path, reranker=fake)

    hits = retriever.search(QUERY, 3, proyecto="stella")

    assert fake.llamadas == []
    assert [hit["engine"] for hit in hits] == ["hibrida"] * len(hits)
    assert [hit["rank"] for hit in hits] == [1, 2, 3]


def test_cloudflare_reordena_por_score(monkeypatch):
    _configurar_cloudflare(monkeypatch)
    pedidos = []

    def handler(request: httpx.Request) -> httpx.Response:
        pedidos.append(request)
        cuerpo = json.loads(request.content)
        assert cuerpo["query"] == QUERY
        assert [c["text"] for c in cuerpo["contexts"]] == [
            texto for _, texto in FILAS
        ]
        assert str(request.url) == CF_RERANK_URL.format(account_id="cuenta-test")
        assert request.headers["authorization"] == "Bearer cf-test-token"
        return _respuesta([0.1, 0.9, 0.5])

    hits = [
        {"chunk_id": chunk_id, "text": texto}
        for chunk_id, texto in FILAS
    ]
    salida = CloudflareReranker(client=_cliente(handler)).reordenar(QUERY, hits)

    assert len(pedidos) == 1
    assert [hit["chunk_id"] for hit in salida] == [
        "stella:p2:1", "stella:p3:2", "stella:p1:0",
    ]
    assert [hit["rank"] for hit in salida] == [1, 2, 3]
    assert [hit["rerank_score"] for hit in salida] == [0.9, 0.5, 0.1]


def test_empate_conserva_el_orden_del_rrf(monkeypatch):
    _configurar_cloudflare(monkeypatch)

    def handler(_request):
        return _respuesta([0.5, 0.5, 0.5])

    hits = [{"chunk_id": chunk_id, "text": texto} for chunk_id, texto in FILAS]
    salida = CloudflareReranker(client=_cliente(handler)).reordenar(QUERY, hits)
    assert [hit["chunk_id"] for hit in salida] == [
        chunk_id for chunk_id, _ in FILAS
    ]


def test_la_llamada_consume_el_cupo_de_rerank(monkeypatch):
    _configurar_cloudflare(monkeypatch, budget="1")
    reranker = CloudflareReranker(client=_cliente(lambda _r: _respuesta([1, 0, 0])))
    hits = [{"chunk_id": chunk_id, "text": texto} for chunk_id, texto in FILAS]
    reranker.reordenar(QUERY, hits)
    assert not ratelimit.puede_llamar_rerank()
    assert ratelimit.puede_llamar_cloudflare()


def test_el_cache_evita_repetir_la_llamada(monkeypatch):
    _configurar_cloudflare(monkeypatch, budget="2")
    llamadas = []

    def handler(_request):
        llamadas.append(1)
        return _respuesta([0.1, 0.9, 0.5])

    hits = [{"chunk_id": chunk_id, "text": texto} for chunk_id, texto in FILAS]
    reranker = CloudflareReranker(client=_cliente(handler))
    primera = reranker.reordenar(QUERY, hits)
    segunda = reranker.reordenar(QUERY, hits)

    assert len(llamadas) == 1
    assert [hit["chunk_id"] for hit in primera] == [
        hit["chunk_id"] for hit in segunda
    ]
    # Queda 1 de los 2 del cupo: la segunda salió del cache.
    assert ratelimit.puede_llamar_rerank()


def test_el_cache_responde_aunque_el_cupo_este_agotado(monkeypatch):
    _configurar_cloudflare(monkeypatch, budget="1")
    llamadas = []

    def handler(_request):
        llamadas.append(1)
        return _respuesta([0.1, 0.9, 0.5])

    hits = [{"chunk_id": chunk_id, "text": texto} for chunk_id, texto in FILAS]
    reranker = CloudflareReranker(client=_cliente(handler))
    primera = reranker.reordenar(QUERY, hits)
    assert not ratelimit.puede_llamar_rerank()

    segunda = reranker.reordenar(QUERY, hits)

    assert len(llamadas) == 1
    assert [hit["chunk_id"] for hit in primera] == [
        hit["chunk_id"] for hit in segunda
    ]


def test_presupuesto_agotado_no_llama(monkeypatch):
    _configurar_cloudflare(monkeypatch, budget="1")
    ratelimit.anotar_llamada_rerank()
    llamadas = []

    def handler(_request):
        llamadas.append(1)
        return _respuesta([1, 0, 0])

    hits = [{"chunk_id": chunk_id, "text": texto} for chunk_id, texto in FILAS]
    with pytest.raises(RerankError, match="presupuesto"):
        CloudflareReranker(client=_cliente(handler)).reordenar(QUERY, hits)
    assert llamadas == []


def test_sin_credenciales_no_llama(monkeypatch):
    llamadas = []

    def handler(_request):
        llamadas.append(1)
        return _respuesta([1, 0, 0])

    hits = [{"chunk_id": chunk_id, "text": texto} for chunk_id, texto in FILAS]
    with pytest.raises(RerankError, match="sin_key"):
        CloudflareReranker(client=_cliente(handler)).reordenar(QUERY, hits)
    assert llamadas == []


def test_timeout_no_gasta_cupo(monkeypatch):
    _configurar_cloudflare(monkeypatch, budget="1")

    def timeout(_request):
        raise httpx.TimeoutException("lento")

    hits = [{"chunk_id": chunk_id, "text": texto} for chunk_id, texto in FILAS]
    with pytest.raises(RerankError, match="timeout"):
        CloudflareReranker(client=_cliente(timeout)).reordenar(QUERY, hits)
    assert ratelimit.puede_llamar_rerank()
    assert ratelimit.rerank_origen_circuito() == "timeout"
    assert not ratelimit.cloudflare_en_pausa()


def test_respuesta_lenta_se_descarta(monkeypatch):
    _configurar_cloudflare(monkeypatch, budget="1")
    reloj = iter([0.0, 3.0, 3.0])
    monkeypatch.setattr(rerank_mod, "_ahora", lambda: next(reloj))

    hits = [{"chunk_id": chunk_id, "text": texto} for chunk_id, texto in FILAS]
    reranker = CloudflareReranker(client=_cliente(lambda _r: _respuesta([1, 0, 0])))
    with pytest.raises(RerankError, match="timeout"):
        reranker.reordenar(QUERY, hits)
    # La llamada salió y respondió: el cupo se descuenta igual.
    assert not ratelimit.puede_llamar_rerank()
    assert ratelimit.puede_llamar_cloudflare()


@pytest.mark.parametrize("code, motivo", [(503, "http_error"), (429, "cuota")])
def test_errores_http_no_reordenan(monkeypatch, code, motivo):
    _configurar_cloudflare(monkeypatch, budget="1")

    def error(_request):
        return httpx.Response(code, json={"errors": [{"code": 1, "message": "x"}]})

    hits = [{"chunk_id": chunk_id, "text": texto} for chunk_id, texto in FILAS]
    with pytest.raises(RerankError, match=motivo):
        CloudflareReranker(client=_cliente(error)).reordenar(QUERY, hits)
    assert ratelimit.puede_llamar_rerank()
    if code == 429:
        assert ratelimit.rerank_en_pausa()
        assert ratelimit.rerank_origen_circuito() == "status_429"
        assert not ratelimit.cloudflare_en_pausa()


def test_respuesta_incompleta_es_error(monkeypatch):
    _configurar_cloudflare(monkeypatch, budget="1")

    def handler(_request):
        return httpx.Response(200, json={
            "success": True,
            "result": {"response": [{"id": 0, "score": 0.9}]},
        })

    hits = [{"chunk_id": chunk_id, "text": texto} for chunk_id, texto in FILAS]
    with pytest.raises(RerankError, match="http_error"):
        CloudflareReranker(client=_cliente(handler)).reordenar(QUERY, hits)


def test_el_log_no_incluye_la_key(monkeypatch, caplog):
    _configurar_cloudflare(monkeypatch, budget="1")

    def error(_request):
        return httpx.Response(
            500, json={"errors": [{"code": 1, "message": "cf-test-token"}]},
        )

    hits = [{"chunk_id": chunk_id, "text": texto} for chunk_id, texto in FILAS]
    with caplog.at_level(logging.WARNING, logger="rag.rerank"):
        with pytest.raises(RerankError):
            CloudflareReranker(client=_cliente(error)).reordenar(QUERY, hits)
    assert "cf-test-token" not in " ".join(caplog.messages)


def test_busqueda_cae_al_rrf_con_el_cupo_agotado(tmp_path, monkeypatch, caplog):
    """Integración: el retriever real usa el reranker real, sin tocar la red."""
    monkeypatch.setenv("RERANK_ENABLED", "1")
    esperado = _baseline(tmp_path, monkeypatch)
    _configurar_cloudflare(monkeypatch, budget="1")
    ratelimit.anotar_llamada_rerank()
    llamadas = []

    def handler(_request):
        llamadas.append(1)
        return _respuesta([1, 0, 0])

    reranker = CloudflareReranker(client=_cliente(handler))
    retriever = _retriever(tmp_path, reranker=reranker)
    with caplog.at_level(logging.WARNING, logger="rag.hybrid"):
        hits = retriever.search(QUERY, 3, proyecto="stella")

    assert llamadas == []
    assert [hit["chunk_id"] for hit in hits] == [
        hit["chunk_id"] for hit in esperado
    ]
    assert "presupuesto" in " ".join(caplog.messages)
