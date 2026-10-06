"""Recuperación híbrida: BM25 (léxica) + FAISS (densa) fusionadas con RRF.

Port de la estrategia usada en instructor-LSA, adaptada a metadatos
multi-documento con página.
"""

import json
import re
import sys
import unicodedata
from pathlib import Path

import faiss
import numpy as np

from .config import (BM25_B, BM25_BIGRAM_BONUS, BM25_K1, CHUNKS_PATH,
                     CORPUS_DIR, DENSE_POOL_FACTOR,
                     EMBED_MODEL, INDEX_PATH, RRF_K, TOP_K, dense_enabled)
from .sinonimos import expandir

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

# Umbral de score BM25 del mejor hit: calibrado sobre este corpus con los
# stopwords activos y el bonus de proximidad. Consultas legítimas del manual
# quedan ≥ 4.0 y consultas ajenas (recetas, películas…) ni siquiera tienen
# términos en el vocabulario → 0.0 → sin respuesta.
# Además del umbral, una consulta que nombra un documento del manifiesto y
# tiene algún término con df>0 no se descarta: se prioriza su introducción.
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


def load_chunks(path: Path = CHUNKS_PATH) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def _plano(text: str) -> str:
    text = unicodedata.normalize("NFD", text.lower())
    return _ACCENT_RE.sub("", text)


_manifiesto_cache: dict[str, dict] | None = None


def _documentos() -> dict[str, dict]:
    """doc_id → título y tokens que identifican al documento (sin genéricos)."""
    global _manifiesto_cache
    if _manifiesto_cache is not None:
        return _manifiesto_cache
    path = CORPUS_DIR / "manifiesto.json"
    docs: dict[str, dict] = {}
    if path.exists():
        raw = json.loads(path.read_text(encoding="utf-8"))
        genericos = set(tokenize(" ".join(_GENERICOS_NOMBRE)))
        for doc_id, title in raw.items():
            nombres = set(tokenize(str(doc_id).replace("-", " ")))
            nombres |= set(tokenize(str(title)))
            nombres -= genericos
            docs[str(doc_id)] = {
                "title": str(title),
                "nombres": {t for t in nombres if len(t) >= 4},
            }
    _manifiesto_cache = docs
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
                 embed_model: str = EMBED_MODEL):
        self.chunks = load_chunks(chunks_path)
        self.index = faiss.read_index(str(index_path))
        self._tokens_per_doc = [tokenize(c["text"]) for c in self.chunks]
        self._df: dict[str, int] = {}
        for tokens in self._tokens_per_doc:
            for t in set(tokens):
                self._df[t] = self._df.get(t, 0) + 1
        self._n = len(self.chunks)
        self._model_name = embed_model
        self._model = None
        self._dense_error: str | None = None

    @property
    def _embedding(self):
        if self._model is None:
            from fastembed import TextEmbedding
            self._model = TextEmbedding(model_name=self._model_name)
        return self._model

    def _embed(self, texts: list[str]) -> np.ndarray:
        vectors = list(self._embedding.embed(texts))
        m = np.asarray(vectors, dtype=np.float32)
        norms = np.linalg.norm(m, axis=1, keepdims=True)
        return m / np.clip(norms, 1e-9, None)

    def bm25(self, query: str, top_k: int = TOP_K) -> list[dict]:
        scores = bm25_scores(query, self._tokens_per_doc, self._df, self._n)
        return self._hits(scores, top_k, engine="bm25")

    def search(self, query: str, top_k: int = TOP_K) -> list[dict]:
        """Híbrida (RRF) con degradación segura a BM25.

        Nunca lanza por problemas del canal denso: sin modelo, con la descarga
        caída o con el índice roto, responde igual con lo léxico.
        """
        lex = bm25_scores(query, self._tokens_per_doc, self._df, self._n)
        top1 = float(lex.max()) if lex.size else 0.0
        if top1 < MIN_TOP1_SCORE:
            doc_id = self._doc_nombrado(query)
            if doc_id and self._tiene_termino_conocido(query):
                return self._hits_priorizando_intro(lex, top_k, doc_id)
            return []  # ninguna palabra de la query calza con el manual
        global LAST_DENSE_ERROR
        if dense_enabled() and self._dense_error is None:
            try:
                return self._search_hybrid(query, top_k)
            except Exception as exc:  # noqa: BLE001 — degradar es lo correcto
                # Un solo intento por proceso: si la descarga falló, no
                # reintentar en cada query (costaría ~50s por consulta).
                self._dense_error = str(exc)[:200]
                LAST_DENSE_ERROR = self._dense_error
                print(f"[rag] denso no disponible ({exc}); usando BM25",
                      file=sys.stderr)
        return self.bm25(query, top_k)

    def _search_hybrid(self, query: str, top_k: int) -> list[dict]:
        pool = min(top_k * DENSE_POOL_FACTOR, self._n)
        dense_vec = self._embed([query])
        _, idx = self.index.search(dense_vec, pool)
        dense = np.zeros(self._n, dtype=np.float32)
        for rank, i in enumerate(idx[0]):
            if i >= 0:
                dense[i] = 1.0 / (1.0 + rank)
        lex = bm25_scores(query, self._tokens_per_doc, self._df, self._n)
        combined = rrf(dense, lex)
        return self._hits(combined, top_k, engine="hibrida")

    def _doc_nombrado(self, query: str) -> str | None:
        tokens = set(tokenize(query))
        for doc_id, meta in _documentos().items():
            if tokens & meta["nombres"]:
                return doc_id
        return None

    def _tiene_termino_conocido(self, query: str) -> bool:
        return any(self._df.get(t, 0) > 0 for t in tokenize(query))

    def _indice_intro(self, doc_id: str) -> int | None:
        title = _documentos().get(doc_id, {}).get("title", "")
        indices = [i for i, c in enumerate(self.chunks) if c["doc_id"] == doc_id]
        for i in indices:
            if title and _contiene_que_es(self.chunks[i]["text"], title):
                return i
        largos = [i for i in indices if len(self.chunks[i]["text"]) > 40]
        if not largos:
            return indices[0] if indices else None
        return min(largos, key=lambda i: (self.chunks[i]["page"], i))

    def _hit_en(self, i: int, rank: int, score: float, engine: str) -> dict:
        chunk = self.chunks[i]
        return {
            "rank": rank,
            "score": score,
            "engine": engine,
            "chunk_id": chunk["chunk_id"],
            "doc_id": chunk["doc_id"],
            "title": chunk["title"],
            "page": chunk["page"],
            "text": chunk["text"],
        }

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
            chunk = self.chunks[int(i)]
            hits.append({
                "rank": rank + 1,
                "score": float(scores[i]),
                "engine": engine,
                "chunk_id": chunk["chunk_id"],
                "doc_id": chunk["doc_id"],
                "title": chunk["title"],
                "page": chunk["page"],
                "text": chunk["text"],
            })
        return hits
