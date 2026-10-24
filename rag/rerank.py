"""Reranker de Cloudflare Workers AI (`@cf/baai/bge-reranker-base`).

Reordena los candidatos que devuelve la búsqueda híbrida. Comparte las
credenciales, el cupo diario (`CF_DAILY_BUDGET`) y el circuito de los
embeddings de Cloudflare: es la misma API y no puede gastar de más. Si falta
la key, el cupo está agotado, el circuito está abierto, la API falla o tarda
más de `RERANK_TIMEOUT`, `RerankError` lleva solo el motivo y el retriever
sigue con el orden del RRF.
"""

import logging
import threading
import time

import httpx

from app import config as app_config
from app import ratelimit
from rag.config import CF_RERANK_MODEL, CF_RERANK_URL, RERANK_TIMEOUT
from rag.embeddings import _detalle_error_cloudflare

log = logging.getLogger("rag.rerank")

MAX_TEXTO_CHARS = 4000


class RerankError(Exception):
    """Fallo del reranker. `motivo` es un código corto, nunca la key."""

    def __init__(self, motivo: str) -> None:
        super().__init__(motivo)
        self.motivo = motivo


def _ahora() -> float:
    """Reloj monotónico aislado para poder simular latencia en tests."""
    return time.monotonic()


def _loguear_fallo(motivo: str, inicio: float) -> None:
    """Status y latencia de cada fallo. La key nunca entra al log."""
    latencia = (_ahora() - inicio) * 1000
    log.warning("rerank fallo: %s (%.0f ms)", motivo, latencia)


def _puntajes(cuerpo, n: int) -> list[float]:
    """Extrae un score por contexto desde `result.response`.

    Cada fila trae `id` (índice del contexto en el pedido) y `score`. Se
    exige una fila por contexto: una respuesta incompleta no reordena nada.
    """
    result = cuerpo.get("result") if isinstance(cuerpo, dict) else None
    filas = result.get("response") if isinstance(result, dict) else None
    if not isinstance(filas, list) or len(filas) != n:
        raise RerankError("http_error")
    puntajes: list[float | None] = [None] * n
    for fila in filas:
        if not isinstance(fila, dict):
            raise RerankError("http_error")
        indice = fila.get("id")
        score = fila.get("score")
        if (
            not isinstance(indice, int)
            or not 0 <= indice < n
            or isinstance(score, bool)
            or not isinstance(score, (int, float))
        ):
            raise RerankError("http_error")
        puntajes[indice] = float(score)
    if any(score is None for score in puntajes):
        raise RerankError("http_error")
    return [float(score) for score in puntajes]


def _reordenar(hits: list[dict], puntajes: list[float]) -> list[dict]:
    """Orden estable por score: ante empate manda el orden del RRF."""
    orden = sorted(range(len(hits)), key=lambda i: (-puntajes[i], i))
    salida = []
    for rank, i in enumerate(orden, start=1):
        item = dict(hits[i])
        item["rank"] = rank
        item["rerank_score"] = puntajes[i]
        item["engine"] = "hibrida+rerank"
        salida.append(item)
    return salida


class CloudflareReranker:
    """Un solo cliente con keep-alive, igual que `CloudflareEmbeddings`."""

    MODEL = CF_RERANK_MODEL

    def __init__(self, client: httpx.Client | None = None,
                 timeout: float = RERANK_TIMEOUT) -> None:
        self._client = client
        self.timeout = timeout
        self._lock = threading.Lock()

    def _http(self) -> httpx.Client:
        """El cliente inyectado en tests no se reemplaza."""
        if self._client is not None:
            return self._client
        with self._lock:
            if self._client is None:
                self._client = httpx.Client()
            return self._client

    def reordenar(self, query: str, hits: list[dict]) -> list[dict]:
        """Devuelve los hits reordenados por relevancia. Puede lanzar `RerankError`."""
        if len(hits) < 2:
            return [dict(hit) for hit in hits]
        account = app_config.cf_account_id()
        token = app_config.cf_api_token()
        if not account or not token:
            raise RerankError("sin_key")
        if ratelimit.cloudflare_en_pausa():
            raise RerankError("circuito")
        if not ratelimit.puede_llamar_cloudflare():
            raise RerankError("presupuesto")
        url = CF_RERANK_URL.format(account_id=account)
        contexts = [
            {"text": (hit.get("text") or "")[:MAX_TEXTO_CHARS]}
            for hit in hits
        ]
        inicio = _ahora()
        try:
            resp = self._http().post(
                url,
                json={"query": query, "contexts": contexts},
                headers={"Authorization": f"Bearer {token}"},
                timeout=self.timeout,
            )
            resp.raise_for_status()
            cuerpo = resp.json()
        except RerankError:
            raise
        except httpx.TimeoutException:
            _loguear_fallo("timeout", inicio)
            ratelimit.anotar_fallo_cloudflare("timeout")
            raise RerankError("timeout") from None
        except httpx.HTTPStatusError as exc:
            code = exc.response.status_code
            origen = (
                "status_429" if code == 429
                else "status_5xx" if code >= 500
                else None
            )
            detalle = _detalle_error_cloudflare(exc.response, account, token)
            motivo = f"status {code}"
            if detalle:
                motivo = f"{motivo} {detalle}"
            _loguear_fallo(motivo, inicio)
            if origen:
                ratelimit.anotar_fallo_cloudflare(origen)
            if code in (402, 429):
                raise RerankError("cuota") from None
            raise RerankError("http_error") from None
        except (httpx.HTTPError, ValueError):
            _loguear_fallo("http_error", inicio)
            raise RerankError("http_error") from None
        if not isinstance(cuerpo, dict) or cuerpo.get("success") is False:
            raise RerankError("http_error")
        puntajes = _puntajes(cuerpo, len(hits))
        # La llamada ya salió: cuenta contra el cupo aunque después se
        # descarte por lenta. Nunca se gasta más de lo reservado.
        ratelimit.anotar_llamada_cloudflare()
        if _ahora() - inicio > self.timeout:
            _loguear_fallo("timeout", inicio)
            raise RerankError("timeout")
        return _reordenar(hits, puntajes)
