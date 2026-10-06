# AGENTS.md

Guía para quien (o lo que) toque este repo. El remoto es **público**
(`Rahyned/Rag-Proyectos-`).

## Stack

| Capa | Qué es |
|------|--------|
| API | FastAPI + SSE (`app/main.py`, entrada Vercel `api/rag_api.py`) |
| Retrieval | BM25 + FAISS + RRF (`rag/hybrid.py`). En Vercel el denso arranca apagado |
| Embeddings | `jinaai/jina-embeddings-v2-base-es` vía fastembed (ONNX, ~640 MB) |
| Generación | Groq, API compatible con OpenAI (`app/services/llm.py`). Sin key → fragmentos |
| UI | React 19 + Vite 8 + oxlint, en `client/` (español, sin TypeScript) |
| Deploy | Vercel services: `web` (`client/`) + `api` (raíz), base `/asistente/` |

## Tests

```bash
uv run pytest
```

El gold denso (modelo de embeddings) no corre en CI. En una máquina que ya
tiene el modelo:

```bash
# PowerShell
$env:RUN_DENSE_TESTS = "1"; uv run pytest tests/test_gold.py

# bash
RUN_DENSE_TESTS=1 uv run pytest tests/test_gold.py
```

Cliente: `cd client; npm run lint; npm run build`.

## Corpus

El índice viaja commiteado. Para sumar un documento:

1. PDF en `corpus/` (el nombre del archivo es el `doc_id`; los que empiezan
   con `_` se ignoran).
2. Título legible en `corpus/manifiesto.json`.
3. `uv run python scripts/ingest.py` — regenera `data/chunks.jsonl` y
   `data/index.faiss`.

No commitear una ingesta con `--sin-embed`: deja chunks e índice
desincronizados. El PDF, el manifiesto, `data/chunks.jsonl` y
`data/index.faiss` entran en el mismo commit.

## Git

Los commits se hacen en local. **No hay push desde el agente**: Lautaro lo
hace desde PowerShell. Mensajes en Conventional Commits, en español
(`fix(api): …`, `fix(rag): …`, `docs: …`).

Repo público: nunca commitear `.env`, `LLM_API_KEY`,
`UPSTASH_REDIS_REST_TOKEN` ni ninguna otra clave. `.env.example` queda con
los valores vacíos.

## Pull requests

Toda PR suma una entrada arriba de todo en `CHANGELOG.md`, formato STELLA:
título `# CHANGELOG — Rag-Proyectos`, lo más nuevo primero, encabezado
`## YYYY-MM-DD — rama`, y subsecciones `### Added`, `### Changed`,
`### Fixed`, `### Files`, `### Tests`. En Tests va la cifra real de
`uv run pytest` (`N passed, M skipped`).
