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

from .config import (BM25_B, BM25_K1, CHUNKS_PATH, DENSE_POOL_FACTOR,
                     EMBED_MODEL, INDEX_PATH, RRF_K, TOP_K, dense_enabled)

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
# stopwords activos. Consultas legítimas del manual quedan ≥ 2.85 y consultas
# ajenas al manual (recetas, películas, economía) ≤ 0.95 → sin respuesta.
MIN_TOP1_SCORE = 2.0

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
    doc_lens = np.array([len(t) for t in tokens_per_doc], dtype=np.float32)
    avgdl = doc_lens.mean() if len(doc_lens) else 1.0
    scores = np.zeros(n_docs, dtype=np.float32)
    for t in q_tokens:
        if t not in df:
            continue
        idf = np.log((n_docs - df[t] + 0.5) / (df[t] + 0.5) + 1.0)
        for i, doc_tokens in enumerate(tokens_per_doc):
            tf = doc_tokens.count(t)
            denom = tf + k1 * (1 - b + b * doc_lens[i] / avgdl)
            scores[i] += idf * (tf * (k1 + 1)) / denom
    return scores


def rrf(dense: np.ndarray, lex: np.ndarray, k: int = RRF_K) -> np.ndarray:
    r_dense = np.argsort(np.argsort(-dense)).astype(np.float32) + 1
    r_lex = np.argsort(np.argsort(-lex)).astype(np.float32) + 1
    return 1.0 / (k + r_dense) + 1.0 / (k + r_lex)


def load_chunks(path: Path = CHUNKS_PATH) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


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
