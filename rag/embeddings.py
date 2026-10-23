"""Proveedor de embeddings: fastembed local, API de Jina, o apagado.

`api` usa el mismo modelo que el índice (`jina-embeddings-v2-base-es`).
Si falta la key, se agota el cupo, la API responde 4xx/5xx o tarda más de
6 s, `EmbedError` lleva solo el motivo: el retriever cae a BM25.
Un 429 abre la pausa de Jina enseguida; un timeout o un 5xx recién a los
3 fallos en 60 s. El cupo diario solo baja cuando la llamada responde OK.
"""

import logging
import threading
import time
from collections import OrderedDict

import httpx
import numpy as np

from app import config as app_config
from app import ratelimit
from rag.config import (EMBED_CACHE_SIZE, EMBED_MODEL, EMBED_TIMEOUT,
                        JINA_EMBED_MODEL, JINA_EMBED_URL, embeddings_provider)

log = logging.getLogger("rag.embeddings")


class EmbedError(Exception):
    """Fallo del canal denso. `motivo` es un código corto, nunca la key."""

    def __init__(self, motivo: str, reintentable: bool = False) -> None:
        super().__init__(motivo)
        self.motivo = motivo
        self.reintentable = reintentable


def _loguear_fallo(motivo: str, inicio: float) -> None:
    """Status y latencia de cada fallo. La key nunca entra al log."""
    latencia = (time.monotonic() - inicio) * 1000
    log.warning("jina fallo: %s (%.0f ms)", motivo, latencia)


def normalizar(vectors: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    return vectors / np.clip(norms, 1e-9, None)


def _matriz(vectores: list) -> np.ndarray:
    matriz = np.asarray(vectores, dtype=np.float32)
    if matriz.ndim != 2 or matriz.shape[0] == 0:
        raise EmbedError("http_error")
    return normalizar(matriz)


class LocalEmbeddings:
    """Modelo ONNX actual. Sirve para ingesta y para desarrollo."""

    def __init__(self) -> None:
        self._model = None

    def _modelo(self):
        if self._model is None:
            from fastembed import TextEmbedding
            self._model = TextEmbedding(model_name=EMBED_MODEL)
        return self._model

    def embed_lote(self, textos: list[str]) -> np.ndarray:
        vectores = list(self._modelo().embed(textos))
        return _matriz(vectores)

    def embed_consulta(self, texto: str) -> np.ndarray:
        return self.embed_lote([texto])


class JinaEmbeddings:
    """Embeddings por HTTP. El cache y el cupo aplican a consultas, no al lote."""

    def __init__(self, client: httpx.Client | None = None,
                 cache_size: int = EMBED_CACHE_SIZE) -> None:
        self._client = client
        self._cache_size = cache_size
        self._cache: OrderedDict[str, np.ndarray] = OrderedDict()
        self._lock = threading.Lock()

    def embed_lote(self, textos: list[str], timeout: float = 60.0) -> np.ndarray:
        """Lote de ingesta: sin cache y sin el cupo diario de consultas."""
        return self._pedir(textos, timeout)

    def embed_consulta(self, texto: str) -> np.ndarray:
        with self._lock:
            guardado = self._cache.get(texto)
            if guardado is not None:
                self._cache.move_to_end(texto)
                return guardado.reshape(1, -1).copy()
        if not app_config.jina_api_key():
            raise EmbedError("sin_key")
        if ratelimit.jina_en_pausa():
            raise EmbedError("circuito")
        if not ratelimit.puede_llamar_jina():
            raise EmbedError("presupuesto")
        try:
            matriz = self._pedir([texto], EMBED_TIMEOUT)
        except EmbedError as exc:
            # Un timeout o un 5xx se reintenta una vez; un 4xx no.
            if not exc.reintentable or ratelimit.jina_en_pausa():
                raise
            matriz = self._pedir([texto], EMBED_TIMEOUT)
        ratelimit.anotar_llamada_jina()
        with self._lock:
            self._cache[texto] = matriz[0].copy()
            self._cache.move_to_end(texto)
            while len(self._cache) > self._cache_size:
                self._cache.popitem(last=False)
        return matriz

    def _http(self) -> httpx.Client:
        """Un solo cliente con keep-alive. El inyectado en tests no se reemplaza."""
        if self._client is not None:
            return self._client
        with self._lock:
            if self._client is None:
                self._client = httpx.Client()
            return self._client

    def _pedir(self, textos: list[str], timeout: float) -> np.ndarray:
        key = app_config.jina_api_key()
        if not key:
            raise EmbedError("sin_key")
        payload = {
            "model": JINA_EMBED_MODEL,
            "input": textos,
            "normalized": True,
        }
        client = self._http()
        inicio = time.monotonic()
        try:
            resp = client.post(
                JINA_EMBED_URL,
                json=payload,
                headers={"Authorization": f"Bearer {key}"},
                timeout=timeout,
            )
            resp.raise_for_status()
            cuerpo = resp.json()
        except EmbedError:
            raise
        except httpx.TimeoutException:
            _loguear_fallo("timeout", inicio)
            ratelimit.anotar_fallo_jina("timeout")
            raise EmbedError("timeout", reintentable=True) from None
        except httpx.HTTPStatusError as exc:
            code = exc.response.status_code
            origen = (
                "status_429" if code == 429
                else "status_5xx" if code >= 500
                else None
            )
            _loguear_fallo(f"status {code}", inicio)
            if origen:
                ratelimit.anotar_fallo_jina(origen)
            if code in (402, 429):
                raise EmbedError("cuota") from None
            raise EmbedError("http_error", reintentable=code >= 500) from None
        except (httpx.HTTPError, ValueError):
            _loguear_fallo("http_error", inicio)
            raise EmbedError("http_error") from None
        data = cuerpo.get("data") if isinstance(cuerpo, dict) else None
        if not isinstance(data, list) or len(data) != len(textos):
            raise EmbedError("http_error")
        ordenados = sorted(data, key=lambda item: item.get("index", 0))
        try:
            vectores = [item["embedding"] for item in ordenados]
        except (KeyError, TypeError):
            raise EmbedError("http_error") from None
        return _matriz(vectores)


def crear_embedder():
    """None si el denso está apagado."""
    modo = embeddings_provider()
    if modo == "off":
        return None
    if modo == "api":
        return JinaEmbeddings()
    if modo == "local":
        return LocalEmbeddings()
    raise EmbedError("http_error")
