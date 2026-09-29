# Rag-Proyectos

Asistente RAG ( Retrieval-Augmented Generation ) sobre la documentación de los
proyectos del portafolio. Hoy responde sobre el **manual de STELLA**; el
diseño es multi-documento: cada proyecto nuevo agrega su PDF al corpus.

## Stack

| Capa | Tecnología |
|------|------------|
| API | FastAPI (SSE streaming, `/docs`) |
| Retrieval | Híbrido: FAISS (embeddings ONNX con fastembed) + BM25 + RRF |
| Generación | Opcional: Gemini vía `LLM_API_KEY` (modo `fragmentos` sin key) |
| UI | React 19 + Vite |
| Tests | pytest (gold set de recuperación + API) |
| Deploy | Vercel (API + estáticos en un proyecto) |

## Desarrollo

```bash
# API
python -m venv venv
venv\Scripts\pip install -r requirements.txt
venv\Scripts\uvicorn app.main:app --reload

# UI
cd client
npm install
npm run dev        # http://localhost:5173 (proxy /api -> :8000)

# Tests
pytest
```

## Variables de entorno

Ver `.env.example`. Sin `LLM_API_KEY` el asistente responde con fragmentos
citados (páginas del manual) en vez de una respuesta redactada.
