"""Recuperación híbrida: BM25 (léxica) + FAISS (densa) fusionadas con RRF.

Port de la estrategia usada en instructor-LSA, adaptada a metadatos
multi-documento con página.
"""

import json
import logging
import re
import unicodedata
from pathlib import Path

import faiss
import numpy as np

from .config import (BM25_B, BM25_BIGRAM_BONUS, BM25_K1, CHUNKS_PATH,
                     EMBED_MODEL, INDEX_PATH, RRF_K, TOP_K, dense_enabled)
from .embeddings import EmbedError, crear_embedder
from .manifiesto import ManifiestoError, cargar, detectar_proyecto
from .sinonimos import expandir

log = logging.getLogger("rag.hybrid")

_ACCENT_RE = re.compile(r"[\u0300-\u036f]")
_TOKEN_RE = re.compile(r"[a-z0-9]+")
_PLURAL_SUF = ("es", "as", "os", "s")
_VERB_SUF = ("ando", "iendo", "ado", "ido", "ar", "er", "ir")

# Funcionales en español: se descartan antes de stemmear para que no inflen
# el idf ni empujen resultados de relleno en consultas genéricas.
_STOPWORDS = frozenset("""
el la los las un una unos unas de del y o a ante bajo con contra desde durante
en entre hacia hasta para por segun sin sobre tras e que se su sus lo le les
mi tu es son al ya no si como cual cuando cuanto donde quien esta hay
""".split())

# Umbral de score BM25 del mejor hit, medido DESPUÉS de filtrar por proyecto.
# Con un solo proyecto el subconjunto es el manual de STELLA, el mismo corpus
# con el que se calibró 2.0: las consultas del manual quedan por encima y las
# ajenas (sin términos en el vocabulario) caen a 0. En «todos» el idf baja
# cuando se sumen documentos, pero el gate no se sube: un umbral más alto
# descartaría preguntas legítimas de un proyecto chico. El nombre del
# proyecto o del documento, con algún término de df>0, sigue abriendo el
# gate y prioriza la introducción.
MIN_TOP1_SCORE = 2.0

# Palabras del título que no identifican al documento ("Manual STELLA" → stella).
_GENERICOS_NOMBRE = frozenset(
    "manual guia usuario documento documentacion".split()
)

# Último error del canal denso visto en este proceso (lo expone /api/health).
LAST_DENSE_ERROR: str | None = None


def _stem(token: str) -> str:
    t = token
    for suf in _PLURAL_SUF:
        if len(t) >= 5 and t.endswith(suf) and len(t) - len(suf) >= 3:
            t = t[: -len(suf)]
            break
    for suf in _VERB_SUF:
        if len(t) >= 5 and t.endswith(suf) and len(t) - len(suf) >= 3:
            t = t[: -len(suf)]
            break
    if len(t) > 4 and t.endswith(("o", "a", "e")):
        t = t[:-1]
    return t


def tokenize(text: str) -> list[str]:
    text = unicodedata.normalize("NFD", text.lower())
    text = _ACCENT_RE.sub("", text)
    return [_stem(t) for t in _TOKEN_RE.findall(text) if t not in _STOPWORDS]


def bm25_scores(query: str, tokens_per_doc: list[list[str]],
                df: dict[str, int], n_docs: int,
                k1: float = BM25_K1, b: float = BM25_B) -> np.ndarray:
    q_tokens = tokenize(query)
    # El original pesa 1.0; el sinónimo (dentista→odontólogo, etc.) pesa menos.
    ponderados = expandir(q_tokens)
    doc_lens = np.array([len(t) for t in tokens_per_doc], dtype=np.float32)
    avgdl = doc_lens.mean() if len(doc_lens) else 1.0
    scores = np.zeros(n_docs, dtype=np.float32)
    for t, peso in ponderados:
        if t not in df:
            continue
        idf = np.log((n_docs - df[t] + 0.5) / (df[t] + 0.5) + 1.0)
        for i, doc_tokens in enumerate(tokens_per_doc):
            tf = doc_tokens.count(t)
            denom = tf + k1 * (1 - b + b * doc_lens[i] / avgdl)
            scores[i] += peso * idf * (tf * (k1 + 1)) / denom
    # Proximidad: un bigrama consecutivo de la query ("agregar un cliente",
    # tras quitar stopwords → agreg|client) es señal de frase, no de palabras
    # sueltas que coinciden por azar en otra página. Sin esto, la query de
    # "agregar un cliente" la ganaba una página de precios por nombrar
    # "pedido nuevo" + "todo el sistema" + "cliente".
    pairs = list(zip(q_tokens, q_tokens[1:]))
    if pairs:
        for i, doc_tokens in enumerate(tokens_per_doc):
            adj = set(zip(doc_tokens, doc_tokens[1:]))
            hits = sum(1 for p in pairs if p in adj)
            if hits:
                scores[i] += BM25_BIGRAM_BONUS * hits
    return scores


def rrf(dense: np.ndarray, lex: np.ndarray, k: int = RRF_K) -> np.ndarray:
    r_dense = np.argsort(np.argsort(-dense)).astype(np.float32) + 1
    r_lex = np.argsort(np.argsort(-lex)).astype(np.float32) + 1
    return 1.0 / (k + r_dense) + 1.0 / (k + r_lex)


def texto_lexico(text: str) -> str:
    """BM25 no tokeniza la ruta «Proyecto › Documento › Sección».

    Si entrara, el nombre del proyecto tendría idf 0 (está en todos los
    chunks) y alargaría cada documento. La ruta sigue en el texto que se
    embebe y en el que ve el modelo.
    """
    cabeza, sep, resto = text.partition("\n\n")
    if sep and " › " in cabeza:
        return resto
    return text


def load_chunks(path: Path = CHUNKS_PATH) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def _plano(text: str) -> str:
    text = unicodedata.normalize("NFD", text.lower())
    return _ACCENT_RE.sub("", text)


def _documentos() -> dict[str, dict]:
    """doc_id → título y tokens que identifican al documento o su proyecto."""
    docs: dict[str, dict] = {}
    try:
        data = cargar()
    except ManifiestoError:
        return docs
    genericos = set(tokenize(" ".join(_GENERICOS_NOMBRE)))
    for proyecto in data["proyectos"]:
        extra = tokenize(proyecto["nombre"]) + tokenize(
            proyecto["id"].replace("-", " ")
        )
        for alias in proyecto["aliases"]:
            extra += tokenize(alias)
        for doc in proyecto["documentos"]:
            doc_id = Path(doc["archivo"]).stem
            nombres = set(tokenize(doc_id.replace("-", " ")))
            nombres |= set(tokenize(doc["titulo"]))
            nombres |= set(extra)
            nombres -= genericos
            docs[doc_id] = {
                "title": doc["titulo"],
                "nombres": {t for t in nombres if len(t) >= 4},
                "proyecto": proyecto["id"],
            }
    return docs


def _contiene_que_es(text: str, title: str) -> bool:
    """True si el chunk es la sección «¿Qué es <título>?» (o una palabra del título)."""
    plano = _plano(text)
    palabras = [
        p for p in _TOKEN_RE.findall(_plano(title))
        if p not in _GENERICOS_NOMBRE and len(p) >= 4
    ]
    for palabra in palabras:
        if re.search(rf"que es {re.escape(palabra)}\b", plano):
            return True
    return False


class HybridRetriever:
    def __init__(self, chunks_path: Path = CHUNKS_PATH,
                 index_path: Path = INDEX_PATH,
                 embed_model: str = EMBED_MODEL,
                 embedder=None):
        self.chunks = load_chunks(chunks_path)
        self.index = faiss.read_index(str(index_path))
        self._tokens_per_doc = [tokenize(texto_lexico(c["text"])) for c in self.chunks]
        self._df: dict[str, int] = {}
        for tokens in self._tokens_per_doc:
            for t in set(tokens):
                self._df[t] = self._df.get(t, 0) + 1
        self._n = len(self.chunks)
        self._model_name = embed_model
        # None explícito arma el proveedor según el entorno; un objeto lo inyecta.
        self._embedder = crear_embedder() if embedder is None else embedder
        self._dense_error: str | None = None

    def _mascara(self, proyecto: str | None, query: str) -> np.ndarray:
        """Índices del proyecto pedido, detectado, o de todo el corpus."""
        pid = proyecto
        if pid is None:
            try:
                pid = detectar_proyecto(query)
            except ManifiestoError:
                pid = None
        if not pid or pid == "todos":
            return np.ones(self._n, dtype=bool)
        return np.array(
            [c.get("proyecto") == pid for c in self.chunks], dtype=bool
        )

    def _lex(self, query: str, allowed: np.ndarray) -> np.ndarray:
        """BM25 solo sobre el subconjunto: el idf no lo diluyen otros proyectos."""
        idx = np.flatnonzero(allowed)
        scores = np.zeros(self._n, dtype=np.float32)
        if len(idx) == 0:
            return scores
        tokens = [self._tokens_per_doc[i] for i in idx]
        df: dict[str, int] = {}
        for toks in tokens:
            for t in set(toks):
                df[t] = df.get(t, 0) + 1
        sub = bm25_scores(query, tokens, df, len(tokens))
        scores[idx] = sub
        return scores

    def bm25(self, query: str, top_k: int = TOP_K,
             proyecto: str | None = None) -> list[dict]:
        allowed = self._mascara(proyecto, query)
        scores = self._lex(query, allowed)
        doc_id = self._doc_nombrado(query)
        if (
            doc_id
            and self._doc_en(doc_id, allowed)
            and _contiene_que_es(query, _documentos().get(doc_id, {}).get("title", ""))
        ):
            return self._hits_priorizando_intro(scores, top_k, doc_id)
        return self._hits(scores, top_k, engine="bm25")

    def search(self, query: str, top_k: int = TOP_K,
               proyecto: str | None = None) -> list[dict]:
        """Híbrida (RRF) con degradación segura a BM25.

        Nunca lanza por problemas del canal denso: sin key, con la API caída,
        con timeout o con el modelo local roto, responde igual con lo léxico.
        """
        allowed = self._mascara(proyecto, query)
        lex = self._lex(query, allowed)
        top1 = float(lex.max()) if lex.size else 0.0
        doc_id = self._doc_nombrado(query)
        if (
            doc_id
            and self._doc_en(doc_id, allowed)
            and _contiene_que_es(query, _documentos().get(doc_id, {}).get("title", ""))
        ):
            # «¿Qué es X?» prioriza la introducción aunque el término X esté
            # en casi todo el manual y el BM25 no la ponga primera.
            return self._hits_priorizando_intro(lex, top_k, doc_id)
        if top1 < MIN_TOP1_SCORE:
            if doc_id and self._doc_en(doc_id, allowed) and self._tiene_termino(query, allowed):
                return self._hits_priorizando_intro(lex, top_k, doc_id)
            return []
        global LAST_DENSE_ERROR
        if (
            dense_enabled()
            and self._embedder is not None
            and self._dense_error is None
        ):
            try:
                return self._search_hybrid(query, top_k, allowed, lex)
            except EmbedError as exc:
                LAST_DENSE_ERROR = exc.motivo
                log.warning(
                    "embeddings no disponible (%s); usando BM25", exc.motivo
                )
                # La descarga local no se reintenta (tardaría ~50s por consulta).
                # Los fallos de la API sí: un timeout o un 429 pueden ser puntuales.
                if exc.motivo == "dimension" or type(self._embedder).__name__ == "LocalEmbeddings":
                    self._dense_error = exc.motivo
            except Exception as exc:  # noqa: BLE001 — degradar es lo correcto
                msg = str(exc)[:200]
                self._dense_error = msg
                LAST_DENSE_ERROR = msg
                log.warning("embeddings no disponible (error); usando BM25")
        return self._hits(lex, top_k, engine="bm25")

    def _vector_consulta(self, query: str) -> np.ndarray:
        vec = self._embedder.embed_consulta(query)
        arr = np.asarray(vec, dtype=np.float32)
        if arr.ndim == 1:
            arr = arr.reshape(1, -1)
        if arr.shape[1] != self.index.d:
            raise EmbedError("dimension")
        return arr

    def _search_hybrid(self, query: str, top_k: int, allowed: np.ndarray,
                       lex: np.ndarray) -> list[dict]:
        sub = np.flatnonzero(allowed)
        if len(sub) == 0:
            return []
        dense_vec = self._vector_consulta(query)
        # El ranking denso se arma solo con los chunks del proyecto: un vecino
        # de otro proyecto no le puede sacar el lugar.
        _, idx = self.index.search(dense_vec, self._n)
        dense = np.zeros(self._n, dtype=np.float32)
        permitidos = set(int(i) for i in sub)
        rango = 0
        for i in idx[0]:
            i = int(i)
            if i in permitidos:
                dense[i] = 1.0 / (1.0 + rango)
                rango += 1
        combinado = np.zeros(self._n, dtype=np.float32)
        combinado[sub] = rrf(dense[sub], lex[sub])
        return self._hits(combinado, top_k, engine="hibrida")

    def _doc_nombrado(self, query: str) -> str | None:
        tokens = set(tokenize(query))
        for doc_id, meta in _documentos().items():
            if tokens & meta["nombres"]:
                return doc_id
        return None

    def _doc_en(self, doc_id: str, allowed: np.ndarray) -> bool:
        return any(
            bool(allowed[i]) and self.chunks[i].get("doc_id") == doc_id
            for i in range(self._n)
        )

    def _tiene_termino(self, query: str, allowed: np.ndarray) -> bool:
        df: dict[str, int] = {}
        for i in np.flatnonzero(allowed):
            for t in set(self._tokens_per_doc[int(i)]):
                df[t] = df.get(t, 0) + 1
        return any(df.get(t, 0) > 0 for t in tokenize(query))

    def _indice_intro(self, doc_id: str) -> int | None:
        title = _documentos().get(doc_id, {}).get("title", "")
        indices = [i for i, c in enumerate(self.chunks) if c["doc_id"] == doc_id]
        for i in indices:
            if title and _contiene_que_es(self.chunks[i]["text"], title):
                return i
        largos = [i for i in indices if len(self.chunks[i]["text"]) > 40]
        if not largos:
            return indices[0] if indices else None
        return min(
            largos,
            key=lambda i: (self.chunks[i].get("page") or 10**9, i),
        )

    def _hit_en(self, i: int, rank: int, score: float, engine: str) -> dict:
        return self._armar(self.chunks[i], rank, score, engine)

    def _hits_priorizando_intro(self, scores: np.ndarray, top_k: int,
                                doc_id: str) -> list[dict]:
        """El chunk «¿Qué es <título>?» va primero; el resto sigue el BM25."""
        intro_i = self._indice_intro(doc_id)
        base = self._hits(scores, top_k, engine="bm25")
        if intro_i is None:
            return base
        intro_score = float(scores[intro_i])
        if intro_score <= 0:
            intro_score = 1e-3
        intro = self._hit_en(intro_i, 1, intro_score, "bm25")
        resto = [h for h in base if h["chunk_id"] != intro["chunk_id"]]
        merged = [intro, *resto][:top_k]
        for n, hit in enumerate(merged, start=1):
            hit["rank"] = n
        return merged

    def _hits(self, scores: np.ndarray, top_k: int, engine: str) -> list[dict]:
        order = np.argsort(-scores)[:top_k]
        hits = []
        for rank, i in enumerate(order):
            if scores[i] <= 0:
                continue
            hits.append(self._armar(
                self.chunks[int(i)], rank + 1, float(scores[i]), engine
            ))
        return hits

    @staticmethod
    def _armar(chunk: dict, rank: int, score: float, engine: str) -> dict:
        return {
            "rank": rank,
            "score": score,
            "engine": engine,
            "chunk_id": chunk["chunk_id"],
            "doc_id": chunk["doc_id"],
            "title": chunk["title"],
            "page": chunk.get("page"),
            "text": chunk["text"],
            "proyecto": chunk.get("proyecto", ""),
            "proyecto_nombre": chunk.get("proyecto_nombre", ""),
            "tipo": chunk.get("tipo", ""),
            "seccion": chunk.get("seccion", ""),
            "publico": bool(chunk.get("publico")),
            "pdf": chunk.get("pdf"),
            "url_publica": chunk.get("url_publica"),
        }
