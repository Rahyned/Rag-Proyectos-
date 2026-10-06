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
         → gate anti-relleno (score BM25 < 2 → sin respuesta;
           si nombra un documento del manifiesto y hay un término conocido,
           pasa y prioriza la introducción)
         → modo fragmentos (citas, 0 tokens)  ─┐
         → modo sintética (respuesta Groq, top_k efectivo ≤ 5) ─┴→ UI con chips "p. N"
```

- **Retrieval local**: BM25 corre siempre; el canal denso (FAISS +
  `fastembed`, ONNX) es **opcional** y su modelo pesa ~640 MB descargados —
  sin torch y sin llamadas externas, pero **no entra en un cold start de
  Vercel de 60s**: en producción corre BM25 + gate (ver `RAG_DENSE`).
- **Generación opcional**: si hay `LLM_API_KEY` (Groq, API compatible con
  OpenAI, con reintentos ante 5xx) redacta la respuesta con las citas; si no —
  o si falla — responde con los fragmentos crudos y sus páginas. El asistente
  **nunca queda roto**.
- **Citas navegables**: cada respuesta muestra `📄 Manual STELLA, p. N` y la
  UI abre `manual-stella.pdf#page=N`.

## Stack

| Capa | Tecnología |
|------|------------|
| API | FastAPI + SSE (`/api/chat`), Swagger en `/docs` |
| Retrieval | Híbrido: FAISS + BM25 + RRF (portado de `instructor-LSA`) |
| Embeddings | `jinaai/jina-embeddings-v2-base-es` (768d) vía fastembed (ONNX) |
| Generación | Opcional: Groq (compatible OpenAI) por env vars `LLM_*` |
| UI | React 19 + Vite 8 + oxlint (ES, sin TypeScript) |
| Tests | pytest (73 passed, 1 skipped; gold set de 15 preguntas ES) |
| CI | GitHub Actions: pytest con `uv sync --frozen` + oxlint + build del cliente |
| Deploy | Vercel: services `web` + `api` en un proyecto + proxy del portafolio |

## Estructura

```
corpus/     fuentes y PDFs (manual-stella.pdf)
data/       índice FAISS + chunks (commiteado, reindexable)
scripts/    md2pdf + ingest (page-aware)
rag/        motor: loader, chunker, embeddings, BM25, RRF, RAGService
app/        FastAPI: /api/health, /api/chat (SSE), /api/search, rate limit
api/        wrapper ASGI de Vercel (normaliza /asistente/api/*)
tests/      pytest: API + retrieval (gold set)
client/     React: chat con chips de cita, ES-only en v1
docs/       GIF del README
.github/    CI
```

## Desarrollo

```bash
# API (Python 3.12+)
uv sync --frozen                # crea .venv desde uv.lock (o: pip install -r requirements.txt)
uv run uvicorn app.main:app --reload     # http://localhost:8000

# UI
cd client
npm install
npm run dev        # http://localhost:5173 (proxy /api -> :8000)

# Tests (0 tokens)
uv run pytest
```

## Agregar un documento nuevo

El corpus es **repo-first**: los PDFs viven en `corpus/` y el índice viaja
commiteado (el FS de Vercel es read-only, no hay upload en runtime).

1. Soltá el PDF en `corpus/` — el nombre del archivo es el `doc_id`
   (`mi-proyecto.pdf` → `mi-proyecto`). Los que empiezan con `_` se ignoran.
2. Opcional: agregá el título legible en `corpus/manifiesto.json`
   (`{"mi-proyecto": "Proyecto X"}`); sin entrada se usa el nombre del archivo.
3. Ingestá: `uv run python scripts/ingest.py`
   (regenera `data/chunks.jsonl` + `data/index.faiss`; con el modelo ya en
   caché tarda segundos). **No** comitees con `--sin-embed`: deja chunks e
   índice desincronizados.
4. Validá contra **todo** el corpus: `uv run pytest` y
   `RUN_DENSE_TESTS=1 uv run pytest tests/test_gold.py` — el gold y los gates
   anti-relleno cambian de score cuando cambian los idf.
5. Commiteá juntos el PDF, `corpus/manifiesto.json`, `data/chunks.jsonl` e
   `data/index.faiss`, y pusheá: el deploy se dispara solo.

Las citas `📄 <título>, p. N` del chat usan el título del manifiesto y el
link al PDF (`/corpus/<doc_id>.pdf#page=N`) anda solo para documentos que el
`prebuild` copió a `client/public/corpus/`.

## Variables de entorno

Ver `.env.example`:

| Var | Rol |
|-----|-----|
| `LLM_API_KEY` | clave Groq; nunca commiteada; si falta → modo fragmentos |
| `LLM_BASE_URL` | OpenAI-compatible (default: `https://api.groq.com/openai/v1`) |
| `LLM_MODEL` | default `qwen/qwen3.8-27b` (tope free: 1000 tokens de salida/min) |
| `LLM_TIMEOUT` | presupuesto total de reintentos en segundos (default `45`) |
| `LLM_DAILY_BUDGET` | llamadas a Groq por día UTC (default `300`; `0` = ilimitado). Vacío en `.env` usa el default |
| `UPSTASH_REDIS_REST_URL` | opcional. Base REST de Upstash. Si falta (o Redis falla) el rate limit y el cupo quedan en memoria |
| `UPSTASH_REDIS_REST_TOKEN` | opcional. Token del REST. Nunca commiteado |
| `RAG_DENSE` | `0` (default en Vercel) apaga el denso; `1` lo fuerza — pero jina-v2-es pesa ~640 MB y no baja en un cold start de 60s |
| `FASTEMBED_CACHE_PATH` | caché de descarga del modelo (en Vercel, `rag/config.py` la fuerza a `/tmp`) |

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
4. Env vars en el dashboard **con scope Production** (las de Preview no
   aplican al dominio de producción): `LLM_API_KEY`, `LLM_BASE_URL`,
   `LLM_MODEL` y `RAG_DENSE=0` (denso apagado: el modelo de 640 MB no baja
   en el cold start; el híbrido queda para una máquina con caché o un
   modelo cuantizado chico, ver roadmap).
5. `/api/health` expone `status` (`ok`/`degraded`), `retrievable` (índice y
   chunks presentes), `llm` (key presente), `model`, `dense` y
   `dense_error` (último fallo del canal denso, con rutas saneadas), para
   saber en caliente si el denso cayó a BM25 y por qué.
6. El aviso de build *"`api/` directory will not be built because services
   are configured"* es **esperado** con el modo services: `api/` entra por el
   rewrite, no como build standalone.
7. Nunca roto: sin key → fragmentos; sin modelo → BM25; query ajena al
   manual → "no encontré nada" (gate de score); sin índice → 503 claro en la
   API (los tests lo cubren).
8. **Proxy del portafolio** (repo `Portafolio-web`): su `client/vercel.json`
   manda `/asistente/*` a `https://rag-proyectos.vercel.app/*`, y la ficha
   STELLA tiene el botón **🤖 ASISTENTE RAG** que entra por ahí.
9. **Headers de seguridad** (ambos `vercel.json`): en el RAG, CSP estricta
   (`script-src 'self'`, sin hosts externos) + `nosniff`, `SAMEORIGIN`,
   `Referrer-Policy` y `Permissions-Policy`; el portafolio lleva las mismas
   sin CSP (usa Google Fonts).
10. **Límites y errores**: ver la sección de abajo. Circuito ante 429s de
    Groq (3 en 60s → degrada sin llamar al proveedor), 429 del LLM se
    reintenta solo si `Retry-After` cabe en el presupuesto, y todo error
    viaja al cliente como `reason` de la enumeración (`no_key | rate_limited |
    timeout | interrupted | upstream | error`) — nunca `str(exc)` (los 503
    llevan solo un `error_id` de 8 caracteres en el log).

### Límites

El limiter de la app es por IP y por endpoint (`chat` 10/min, `search`
60/min → 429 con `Retry-After`). Si existen `UPSTASH_REDIS_REST_URL` y
`UPSTASH_REDIS_REST_TOKEN`, la ventana es fija de 60 s en Upstash Redis REST
(`INCR` + `EXPIRE`, clave `rl:{endpoint}:{ip}:{ventana}`). Si las vars no
están o Redis falla, se usa el contador en memoria de esa instancia y la
consulta sigue: nunca se rompe por Redis.

En Vercel Hobby hay varias instancias y el plan deja **una** regla de
firewall. Además del limiter de la app, este paso es **manual** en el
dashboard:

1. Proyecto → **Firewall** → **Rate Limiting** → Add Rule.
2. Una sola regla (Hobby: máximo 1), ventana **fija**, clave **IP**.
3. Aplicarla a `/api/chat` y `/asistente/api/chat`.
4. Ejemplo: **10 requests / 60 s** → acción **429**.

`LLM_DAILY_BUDGET` (default 300, `0` = ilimitado) corta las llamadas a Groq
por día UTC. El contador es `llm:budget:YYYY-MM-DD` en Redis (TTL 2 días) o
en memoria si no hay Redis. Al pasarse, `/api/chat` en modo sintética emite
`fallback` con `reason=rate_limited` y no llama al proveedor. En sintética el
`top_k` efectivo queda en 5 aunque el cliente pida más; `/api/search` sigue
hasta 10.

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
| 8 | LLM Groq + anti-relleno (stopwords, gate, snippet) + health con flags | ✅ |
| 9 | Hardening: rate limit, errores saneados, cancelación en la UI, headers, CI con uv/oxlint/build | ✅ |
| 10 | Gap semántico BM25: bonus de proximidad por bigrama → gold 12/12 | ✅ |
| 11 | Workflow repo-first para nuevos documentos (corpus/ + manifiesto + ingest) | ✅ |
| fut. | Modelo de embeddings cuantizado bundleado → denso en Vercel | ⬜ |
| fut. | Upload en runtime (endpoint + Vercel Blob), si algún día hace falta | ⬜ |
