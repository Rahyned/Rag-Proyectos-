"""Proveedor de embeddings: Cloudflare, Jina, fastembed local, o apagado.

`cloudflare` usa Workers AI (`@cf/baai/bge-m3`, 1024d) y `api` usa Jina
(`jina-embeddings-v2-base-es`, 768d). Si falta la key, se agota el cupo, la
API responde 4xx/5xx o tarda más de 2 s, `EmbedError` lleva solo el motivo:
el retriever cae a BM25. Un 429 abre la pausa enseguida; un timeout o un 5xx
recién a los 2 fallos en 60 s. El cupo diario solo baja cuando la llamada
responde OK. Jina y Cloudflare tienen cupo y circuito separados.
"""

import json
import logging
import threading
import time
from collections import OrderedDict

import httpx
import numpy as np

from app import config as app_config
from app import ratelimit
from rag.config import (CF_EMBED_MODEL, CF_EMBED_URL, EMBED_CACHE_SIZE,
                        EMBED_TIMEOUT, JINA_EMBED_MODEL, JINA_EMBED_URL,
                        LOCAL_EMBED_MODEL, embeddings_provider)

log = logging.getLogger("rag.embeddings")


class EmbedError(Exception):
    """Fallo del canal denso. `motivo` es un código corto, nunca la key."""

    def __init__(self, motivo: str) -> None:
        super().__init__(motivo)
        self.motivo = motivo


def _loguear_fallo(proveedor: str, motivo: str, inicio: float) -> None:
    """Status y latencia de cada fallo. La key nunca entra al log."""
    latencia = (time.monotonic() - inicio) * 1000
    log.warning("%s fallo: %s (%.0f ms)", proveedor, motivo, latencia)


MAX_DETALLE_ERROR = 500


def _detalle_error_cloudflare(resp: httpx.Response, account: str,
                              token: str) -> str:
    """Cuerpo útil de un 4xx/5xx de Cloudflare, sin secretos y truncado.

    Prioriza `errors[].code/message`; si no hay JSON, usa el texto plano.
    """
    try:
        cuerpo = resp.json()
    except ValueError:
        texto = resp.text or ""
    else:
        errores = cuerpo.get("errors") if isinstance(cuerpo, dict) else None
        if isinstance(errores, list) and errores:
            partes = []
            for error in errores:
                if not isinstance(error, dict):
                    partes.append(str(error))
                    continue
                code = error.get("code")
                mensaje = error.get("message") or error.get("detail") or ""
                if code is not None:
                    partes.append(f"{code}: {mensaje}")
                else:
                    partes.append(str(mensaje))
            texto = " | ".join(partes)
        else:
            texto = json.dumps(cuerpo, ensure_ascii=False)
    texto = " ".join(str(texto).split())
    for secreto, etiqueta in ((token, "[token]"), (account, "[cuenta]")):
        if secreto:
            texto = texto.replace(secreto, etiqueta)
    return texto[:MAX_DETALLE_ERROR]


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
            self._model = TextEmbedding(model_name=LOCAL_EMBED_MODEL)
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
        # Sin reintento: si Jina tarda o falla, se responde por BM25 ya.
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
            _loguear_fallo("jina", "timeout", inicio)
            ratelimit.anotar_fallo_jina("timeout")
            raise EmbedError("timeout") from None
        except httpx.HTTPStatusError as exc:
            code = exc.response.status_code
            origen = (
                "status_429" if code == 429
                else "status_5xx" if code >= 500
                else None
            )
            _loguear_fallo("jina", f"status {code}", inicio)
            if origen:
                ratelimit.anotar_fallo_jina(origen)
            if code in (402, 429):
                raise EmbedError("cuota") from None
            raise EmbedError("http_error") from None
        except (httpx.HTTPError, ValueError):
            _loguear_fallo("jina", "http_error", inicio)
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


class CloudflareEmbeddings:
    """Embeddings de Workers AI. La ingesta va en lotes de 20.

    El cache y el cupo aplican a consultas, no al lote de ingesta. El
    circuito y el presupuesto son propios (`cloudflare:*`), separados de Jina.
    """

    MODEL = CF_EMBED_MODEL
    # bge-m3 tiene 60k tokens por request. 20 textos de hasta 4000 caracteres
    # (~2000 tokens en español) dejan margen; `truncate_inputs` cubre el
    # límite exacto por texto que aplique Cloudflare.
    BATCH_SIZE = 20
    MAX_TEXTO_CHARS = 4000

    def __init__(self, client: httpx.Client | None = None,
                 cache_size: int = EMBED_CACHE_SIZE) -> None:
        self._client = client
        self._cache_size = cache_size
        self._cache: OrderedDict[str, np.ndarray] = OrderedDict()
        self._lock = threading.Lock()

    def embed_lote(self, textos: list[str], timeout: float = 60.0) -> np.ndarray:
        """Lote de ingesta: sin cache y sin el cupo diario de consultas."""
        if not textos:
            return np.empty((0, 0), dtype=np.float32)
        partes = [
            self._pedir(textos[i:i + self.BATCH_SIZE], timeout)
            for i in range(0, len(textos), self.BATCH_SIZE)
        ]
        return np.vstack(partes)

    def embed_consulta(self, texto: str) -> np.ndarray:
        with self._lock:
            guardado = self._cache.get(texto)
            if guardado is not None:
                self._cache.move_to_end(texto)
                return guardado.reshape(1, -1).copy()
        if not app_config.cf_account_id() or not app_config.cf_api_token():
            raise EmbedError("sin_key")
        if ratelimit.cloudflare_en_pausa():
            raise EmbedError("circuito")
        if not ratelimit.puede_llamar_cloudflare():
            raise EmbedError("presupuesto")
        # Sin reintento: si Cloudflare tarda o falla, se responde por BM25 ya.
        matriz = self._pedir([texto], EMBED_TIMEOUT)
        ratelimit.anotar_llamada_cloudflare()
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
        account = app_config.cf_account_id()
        token = app_config.cf_api_token()
        if not account or not token:
            raise EmbedError("sin_key")
        url = CF_EMBED_URL.format(account_id=account)
        client = self._http()
        inicio = time.monotonic()
        try:
            resp = client.post(
                url,
                json={
                    "text": [texto[:self.MAX_TEXTO_CHARS] for texto in textos],
                    "truncate_inputs": True,
                },
                headers={"Authorization": f"Bearer {token}"},
                timeout=timeout,
            )
            resp.raise_for_status()
            cuerpo = resp.json()
        except EmbedError:
            raise
        except httpx.TimeoutException:
            _loguear_fallo("cloudflare", "timeout", inicio)
            ratelimit.anotar_fallo_cloudflare("timeout")
            raise EmbedError("timeout") from None
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
            _loguear_fallo("cloudflare", motivo, inicio)
            if origen:
                ratelimit.anotar_fallo_cloudflare(origen)
            if code in (402, 429):
                raise EmbedError("cuota") from None
            raise EmbedError("http_error") from None
        except (httpx.HTTPError, ValueError):
            _loguear_fallo("cloudflare", "http_error", inicio)
            raise EmbedError("http_error") from None
        if not isinstance(cuerpo, dict) or cuerpo.get("success") is False:
            raise EmbedError("http_error")
        result = cuerpo.get("result")
        data = result.get("data") if isinstance(result, dict) else None
        if not isinstance(data, list) or len(data) != len(textos):
            raise EmbedError("http_error")
        try:
            return _matriz([list(vector) for vector in data])
        except (TypeError, ValueError):
            raise EmbedError("http_error") from None


def crear_embedder():
    """None si el denso está apagado."""
    modo = embeddings_provider()
    if modo == "off":
        return None
    if modo == "cloudflare":
        return CloudflareEmbeddings()
    if modo == "api":
        return JinaEmbeddings()
    if modo == "local":
        return LocalEmbeddings()
    raise EmbedError("http_error")
