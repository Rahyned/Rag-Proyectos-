# Rag-Proyectos

Asistente RAG multi-documento sobre la documentación de los proyectos del
portafolio. **Fase 1**: responde preguntas sobre el *manual de STELLA* con
citas de página; con el tiempo cada proyecto nuevo (SolutionsCars, Oak,
Butterflies…) agrega su propio documento al corpus sin rediseñar nada.

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
| Embeddings | `intfloat/multilingual-e5-small` vía fastembed (ONNX int8) |
| Generación | Opcional: Gemini u OpenAI-compatible por env vars `LLM_*` |
| UI | React 19 + Vite 8 + oxlint (ES, sin TypeScript) |
| Tests | pytest (API + gold set ~25 preguntas con doc+page) |
| CI | GitHub Actions (pytest en push/PR) |
| Deploy | Vercel (API + estáticos en un proyecto, bundle < 500 MB) |

## Estructura

```
corpus/     fuentes y PDFs (manual-stella.pdf)
data/       índice FAISS + chunks (commiteado, reindexable)
scripts/    md2pdf + ingest (page-aware)
rag/        motor: loader, chunker, embeddings, BM25, RRF, RAGService
app/        FastAPI: /api/health, /api/chat (SSE), /api/sources
tests/      pytest: API + retrieval (gold set)
client/     React: chat con chips de cita, ES-only en v1
.github/    CI
```

## Desarrollo

```bash
# API (Python 3.12+)
python -m venv venv
venv\Scripts\pip install -r requirements.txt
venv\Scripts\uvicorn app.main:app --reload     # http://localhost:8000

# UI
cd client
npm install
npm run dev        # http://localhost:5173 (proxy /api -> :8000)

# Tests (0 tokens)
pytest
```

## Variables de entorno

Ver `.env.example`:

| Var | Rol |
|-----|-----|
| `LLM_MODE` | `gemini` · `none` (forzar modo fragmentos) |
| `LLM_BASE_URL` | OpenAI-compatible (Gemini: `.../v1beta/openai`) |
| `LLM_MODEL` | ej. `gemini-3.8-flash` |
| `LLM_API_KEY` | nunca commiteada; si falta → modo fragmentos |

## Roadmap

| Fase | Entregable | Estado |
|------|------------|--------|
| 0 | Andamiaje: FastAPI + React + CI + tests | ✅ |
| 1 | Manual STELLA (40-60 pág) + PDF + ingest page-aware | 🔄 en curso |
| 2 | Motor híbrido (FAISS+BM25+RRF) + gold set | ⬜ |
| 3 | `/api/chat` SSE + modos `gemini`/`none` + rate limit | ⬜ |
| 4 | UI React: chat + chips de cita `p. N` | ⬜ |
| 5 | Deploy Vercel | ⬜ |
| 6 | README final + GIF demo | ⬜ |
| 7 | (opcional) Link desde el portafolio | ⬜ |
| fut. | Nuevos documentos (otros proyectos) + upload PDFs | ⬜ |
