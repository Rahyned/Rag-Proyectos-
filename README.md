# Rag-Proyectos

Asistente RAG multi-documento sobre la documentación de los proyectos del
portafolio. Responde preguntas sobre el *manual de STELLA* con citas de página
navegables; con el tiempo cada proyecto nuevo (SolutionsCars, Oak,
Butterflies…) agrega su propio documento al corpus sin rediseñar nada.

**En producción** (fases 0–7 completadas):

- Directo: <https://rag-proyectos.vercel.app>
- Desde el portafolio (mismo dominio):
  <https://portafolio-web-three-gamma.vercel.app/asistente/>

![Demo: pregunta sobre una orden de compra con citas de página](docs/demo.gif)

## Cómo funciona

```
Pregunta → FAISS (embeddings ONNX locales) + BM25 → RRF → top-k
         → modo fragmentos (citas, 0 tokens)  ─┐
         → modo Gemini (respuesta redactada)  ─┴→ UI con chips "p. N"
```

- **Retrieval 100% local**: `fastembed` (int8, ~40 MB) + `faiss-cpu`, sin
  torch, sin llamadas externas para buscar.
- **Generación opcional**: si hay `LLM_API_KEY` (Gemini) redacta la respuesta
  con las citas; si no — o si falla — responde con los fragmentos crudos y
  sus páginas. El asistente **nunca queda roto**.
- **Citas navegables**: cada respuesta muestra `📄 Manual STELLA, p. N` y la
  UI abre `manual-stella.pdf#page=N`.

## Stack

| Capa | Tecnología |
|------|------------|
| API | FastAPI + SSE (`/api/chat`), Swagger en `/docs` |
| Retrieval | Híbrido: FAISS + BM25 + RRF (portado de `instructor-LSA`) |
| Embeddings | `jinaai/jina-embeddings-v2-base-es` (768d) vía fastembed (ONNX) |
| Generación | Opcional: Gemini u OpenAI-compatible por env vars `LLM_*` |
| UI | React 19 + Vite 8 + oxlint (ES, sin TypeScript) |
| Tests | pytest (API + gold set ~25 preguntas con doc+page) |
| CI | GitHub Actions (pytest en push/PR) |
| Deploy | Vercel: services `web` + `api` en un proyecto + proxy del portafolio |

## Estructura

```
corpus/     fuentes y PDFs (manual-stella.pdf)
data/       índice FAISS + chunks (commiteado, reindexable)
scripts/    md2pdf + ingest (page-aware)
rag/        motor: loader, chunker, embeddings, BM25, RRF, RAGService
app/        FastAPI: /api/health, /api/chat (SSE), /api/sources
api/        wrapper ASGI de Vercel (normaliza /asistente/api/*)
tests/      pytest: API + retrieval (gold set)
client/     React: chat con chips de cita, ES-only en v1
docs/       GIF del README
.github/    CI
```

## Desarrollo

```bash
# API (Python 3.12+)
python -m venv venv
venv\Scripts\pip install -r requirements.txt   # o: uv sync
venv\Scripts\uvicorn app.main:app --reload     # http://localhost:8000

# UI
cd client
npm install
npm run dev        # http://localhost:5173 (proxy /api -> :8000)

# Tests (0 tokens)
venv\Scripts\python -m pytest
```

## Variables de entorno

Ver `.env.example`:

| Var | Rol |
|-----|-----|
| `LLM_BASE_URL` | OpenAI-compatible (Gemini: `.../v1beta/openai`) |
| `LLM_MODEL` | ej. `gemini-3.8-flash` |
| `LLM_API_KEY` | nunca commiteada; si falta → modo fragmentos |
| `RAG_DENSE` | `0` apaga el canal denso; en Vercel arranca apagado (`1` lo fuerza) |

## Deploy (Vercel)

`vercel.json` usa el modo **services**: un proyecto con dos servicios.

| Servicio | Raíz | Qué sirve |
|----------|------|-----------|
| `web` | `client/` | UI Vite con `VITE_BASE=/asistente/`; rewrite interno `/asistente/(.*)` → `/$1` |
| `api` | `.` | FastAPI vía `api/rag_api.py` (wrapper ASGI, `maxDuration` 60) |

Rewrites del proyecto, en orden: `/asistente/api/*` → `api`, `/api/*` →
`api`, `/asistente/*` → `web`, `/*` → `web`.

Detalles que importan:

1. **El wrapper `api/rag_api.py` normaliza el prefijo**: las rutas
   `/asistente/api/chat` llegan como tal y se reescriben a `/api/chat` en
   ASGI antes de que FastAPI enrute (el `request.path` transform de services
   no se aplicó; se resolvió en el wrapper, con tests).
2. **uv en el build**: Vercel ejecuta `uv lock`, que exige `[project]` en
   `pyproject.toml`; `uv.lock` está commiteado.
3. El `prebuild` de `client/` copia `corpus/*.pdf` a `client/public/corpus/`,
   así las citas `#page=N` abren el PDF desde el CDN.
4. Env vars opcionales en el dashboard: `LLM_API_KEY` (+ `LLM_MODEL`,
   `LLM_BASE_URL`) para el modo respuesta sintética.
5. En Vercel el retrieval arranca en **BM25** (sin descarga de modelo en
   frío); `RAG_DENSE=1` habilita el híbrido si querés asumir esa descarga.
6. Nunca roto: sin key → fragmentos; sin modelo → BM25; sin índice → 503
   claro en la API (los tests lo cubren).
7. **Proxy del portafolio** (repo `Portafolio-web`): su `client/vercel.json`
   manda `/asistente/*` a `https://rag-proyectos.vercel.app/*`, y la ficha
   STELLA tiene el botón **🤖 ASISTENTE RAG** que entra por ahí.

## Roadmap

| Fase | Entregable | Estado |
|------|------------|--------|
| 0 | Andamiaje: FastAPI + React + CI + tests | ✅ |
| 1 | Manual STELLA (40-60 pág) + PDF + ingest page-aware | ✅ |
| 2 | Motor híbrido (FAISS+BM25+RRF) + gold set | ✅ |
| 3 | `/api/chat` SSE + modos `fragmentos`/`sintetica` | ✅ |
| 4 | UI React: chat + chips de cita `p. N` | ✅ |
| 5 | Deploy Vercel | ✅ |
| 6 | README final + GIF demo | ✅ |
| 7 | Link desde el portafolio (botón en ficha STELLA) | ✅ |
| fut. | Nuevos documentos (otros proyectos) + upload PDFs | ⬜ |
