# AGENTS.md

Guía para quien (o lo que) toque este repo. El remoto es **público**
(`Rahyned/Rag-Proyectos-`).

## Stack

| Capa | Qué es |
|------|--------|
| API | FastAPI + SSE (`app/main.py`, entrada Vercel `api/rag_api.py`) |
| Retrieval | BM25 + FAISS + RRF (`rag/hybrid.py`). Filtro por proyecto antes de rankear |
| Embeddings | `jinaai/jina-embeddings-v2-base-es` (768d). `local` = fastembed ONNX (~640 MB); `api` = Jina (`JINA_API_KEY`); `off` = solo BM25 |
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

El índice viaja commiteado. Para sumar un proyecto:

1. Carpeta `corpus/<id>/` con los `.md` o `.pdf` (los que empiezan con `_`
   se ignoran). El `id` es el de `corpus/manifiesto.json`.
2. Entrada en el manifiesto: `id`, `nombre`, `descripcion`, `url` opcional,
   `aliases`, `preguntas`, y por documento `archivo`, `titulo`, `tipo`
   (`manual` | `ficha` | `changelog` | `readme`) y `publico`.
3. Si hace falta, casos en `data/gold_tuning.json` (para ajustar) y
   `data/gold_test.json` (para medir), con el campo `proyecto`. No midas con
   el de tuning.
4. `uv run python scripts/ingest.py` — regenera `data/chunks.jsonl`,
   `data/index.faiss`, `data/corpus.sha256` y `data/ingest_meta.json`.
   Default `--provider local` (fastembed). Con `JINA_API_KEY`,
   `uv run python scripts/comparar_embeddings.py` mide el coseno contra la
   API. Si da menos de 0.99, reindexá con `--provider api` para que consulta
   e índice salgan del mismo origen.

No commitear una ingesta con `--sin-embed`: deja chunks e índice
desincronizados. La carpeta del proyecto, el manifiesto, `data/chunks.jsonl`,
`data/index.faiss`, el hash y la meta entran en el mismo commit.

`uv run python scripts/ingest.py --check` valida el manifiesto, corre el
guardrail de secretos y compara el hash. No reindexa. En un PR que toque
`corpus/` lo corre `.github/workflows/corpus.yml`.

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
