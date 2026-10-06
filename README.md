# Rag-Proyectos

Asistente RAG sobre la documentación de los proyectos del portafolio
(STELLA y los que se sumen). Cada cita indica proyecto, documento y sección;
si el documento es público y hay PDF, el enlace abre la página.

**En producción** (fases 0–7 completadas):

- Directo: <https://rag-proyectos.vercel.app>
- Desde el portafolio (mismo dominio):
  <https://portafolio-web-three-gamma.vercel.app/asistente/>

![Demo: pregunta sobre una orden de compra con citas de página](docs/demo.gif)

## Cómo funciona

```
Pregunta → (filtro de proyecto) → FAISS + BM25 → RRF → top-k
         → gate anti-relleno (score BM25 < 2 sobre el subconjunto → sin respuesta;
           si nombra un documento y hay un término conocido, pasa y prioriza
           la introducción; «¿Qué es X?» también la prioriza)
         → modo fragmentos (citas, 0 tokens)  ─┐
         → modo sintética (respuesta Groq, top_k efectivo ≤ 5) ─┴→ UI
```

- **Retrieval**: BM25 corre siempre. El canal denso usa el índice FAISS de
  `jina-embeddings-v2-base-es` (768d). En una máquina de desarrollo los
  vectores salen de fastembed (ONNX, ~640 MB). En Vercel no entra ese
  archivo: `EMBEDDINGS_PROVIDER=api` pide el mismo modelo a Jina
  (`JINA_API_KEY`, timeout 3 s). Si falta la key, hay 4xx/5xx, se agota
  `JINA_DAILY_BUDGET` o se vence el timeout, la consulta sigue en BM25.
- **Generación opcional**: si hay `LLM_API_KEY` (Groq, API compatible con
  OpenAI, con reintentos ante 5xx) redacta la respuesta con las citas; si no —
  o si falla — responde con los fragmentos crudos y sus páginas. El asistente
  **nunca queda roto**.
- **Citas**: `Proyecto · Documento · Sección (pág. N)`. El enlace al PDF
  solo aparece si el documento es público y tiene página.

## Stack

| Capa | Tecnología |
|------|------------|
| API | FastAPI + SSE (`/api/chat`), Swagger en `/docs` |
| Retrieval | Híbrido: FAISS + BM25 + RRF (portado de `instructor-LSA`) |
| Embeddings | `jina-embeddings-v2-base-es` (768d): fastembed local o API de Jina |
| Generación | Opcional: Groq (compatible OpenAI) por env vars `LLM_*` |
| UI | React 19 + Vite 8 + oxlint (ES, sin TypeScript) |
| Tests | pytest (89 passed, 1 skipped; gold_test de 10 preguntas ES) |
| CI | GitHub Actions: pytest con `uv sync --frozen` + oxlint + build del cliente |
| Deploy | Vercel: services `web` + `api` en un proyecto + proxy del portafolio |

## Estructura

```
corpus/     corpus/<proyecto>/*.(md|pdf) y manifiesto.json
data/       índice FAISS, chunks, hash del corpus (commiteado)
scripts/    md2pdf + ingest (markdown por encabezados, PDF por página)
rag/        manifiesto, chunker, embeddings, BM25, RRF, guardrail
app/        FastAPI: /api/health, /api/proyectos, /api/chat, /api/search
api/        wrapper ASGI de Vercel (normaliza /asistente/api/*)
tests/      pytest: API + retrieval (gold_test) + secretos + embeddings
client/     React: selector de proyecto, markdown seguro, citas
docs/       GIF del README
.github/    CI y chequeo de corpus en PRs
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

## Sumar un proyecto

El corpus es **repo-first**: los archivos viven en `corpus/<proyecto>/` y el
índice viaja commiteado (el FS de Vercel es read-only, no hay upload en runtime).

1. Creá `corpus/<id>/` y dejá ahí los `.md` o `.pdf`. Los que empiezan con `_`
   se ignoran. Un `.md` puede tener al lado un `.pdf` con el mismo nombre: el
   markdown se indexa y el PDF solo sirve para el enlace de página.
2. Sumá el proyecto a `corpus/manifiesto.json`: `id`, `nombre`, `descripcion`,
   `url` opcional, `aliases`, `preguntas`, y por documento `archivo`, `titulo`,
   `tipo` (`manual`, `ficha`, `changelog` o `readme`) y `publico`.
   Los emails que el documento puede mencionar van en `emails_publicos`.
   La ingesta falla si falta un campo, si el archivo no está, o si el texto
   tiene claves, tokens, `BEGIN PRIVATE KEY`, CUIT/CUIL, un email fuera de la
   allowlist, o si el nombre del archivo dice «auditoría» o «vulnerabilidad».
3. Si ya hay texto para evaluar, agregá casos con `proyecto` en
   `data/gold_tuning.json` (para ajustar) y dejá `data/gold_test.json` para
   medir. No uses el de tuning como resultado.
4. Ingestá: `uv run python scripts/ingest.py`
   (regenera `data/chunks.jsonl`, `data/index.faiss`, `data/corpus.sha256` y
   `data/ingest_meta.json`). **No** comitees con `--sin-embed`.
5. Validá: `uv run pytest` y, con el modelo local,
   `RUN_DENSE_TESTS=1 uv run pytest tests/test_gold.py`.
6. Commiteá juntos la carpeta, el manifiesto, los chunks, el índice, el hash
   y la meta.

`uv run python scripts/ingest.py --check` no reindexa: valida el manifiesto,
el guardrail y que el hash del corpus coincida con el de la última ingesta.
En un PR que toque `corpus/` lo corre `.github/workflows/corpus.yml`.

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
| `EMBEDDINGS_PROVIDER` | `local` (fastembed), `api` (Jina) u `off` (solo BM25). Si no está, `RAG_DENSE=0` apaga el denso; en Vercel sin ninguna de las dos el default es `api` |
| `JINA_API_KEY` | key de `https://api.jina.ai/v1/embeddings` para `jina-embeddings-v2-base-es`. Nunca commiteada. Sin key, la consulta cae a BM25 |
| `JINA_DAILY_BUDGET` | llamadas a Jina por día UTC (default `300`; `0` = ilimitado). Las consultas repetidas salen de un cache en memoria (500) y no consumen cupo |
| `RAG_DENSE` | compatibilidad: `0` apaga el denso y `1` usa el modelo local, solo si `EMBEDDINGS_PROVIDER` no está definida |
| `FASTEMBED_CACHE_PATH` | caché de descarga del modelo local (en Vercel, `rag/config.py` la fuerza a `/tmp`) |

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
3. El `prebuild` de `client/` copia los PDF de `corpus/` (incluso en
   subcarpetas) a `client/public/corpus/`, así las citas `#page=N` abren el
   PDF desde el CDN.
4. Env vars en el dashboard **con scope Production** (las de Preview no
   aplican al dominio de producción): `LLM_API_KEY`, `LLM_BASE_URL`,
   `LLM_MODEL`, `EMBEDDINGS_PROVIDER=api` y `JINA_API_KEY`. Si quedó
   `RAG_DENSE=0` de antes, `EMBEDDINGS_PROVIDER` lo pisa. Sin la key de Jina
   el denso cae a BM25 y la consulta no se rompe.
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

`JINA_DAILY_BUDGET` usa la misma idea con la clave `jina:budget:YYYY-MM-DD`.
Si el cupo está agotado, falta `JINA_API_KEY`, Jina responde 4xx/5xx o tarda
más de 3 s, la búsqueda sigue en BM25. El log anota el motivo (`sin_key`,
`presupuesto`, `cuota`, `http_error`, `timeout`) y nunca la key. Un cache LRU
de 500 consultas repetidas no vuelve a llamar a Jina.

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
