# CHANGELOG — Rag-Proyectos

## 2026-10-06 — feat/multi-proyecto

### Added

- Corpus por proyecto: `corpus/<id>/<documento>.(md|pdf)` y manifiesto con
  `id`, `nombre`, `descripcion`, `url` opcional, `aliases`, `preguntas` y, por
  documento, `archivo`, `titulo`, `tipo` y `publico`. La carga falla con el
  campo o el archivo que falta.
- Ingesta de Markdown por encabezados (`#`, `##`, `###`), con la ruta
  «Proyecto › Documento › Sección» al frente de cada chunk, tope de tamaño por
  párrafos, sin fragmentos de prosa de menos de 40 caracteres y sin aplanar
  tablas. El PDF hermano solo asigna la página del enlace.
- Guardrail de repo público: la ingesta corta si hay clave, token, `BEGIN
  PRIVATE KEY`, CUIT/CUIL, un email fuera de `emails_publicos`, o si el nombre
  del archivo dice «auditoría» o «vulnerabilidad».
- `EMBEDDINGS_PROVIDER=local|api|off`. `api` llama a Jina
  (`jina-embeddings-v2-base-es`, el mismo modelo del índice) con `httpx`.
  Timeout 3 s, cache LRU de 500 consultas y cupo `JINA_DAILY_BUDGET`
  (`jina:budget:YYYY-MM-DD`, mismo Redis o memoria que el de Groq). Sin key,
  con 4xx/5xx, con el cupo agotado o con timeout, la consulta sigue en BM25 y
  el log guarda solo el motivo.
- `/api/chat` y `/api/search` aceptan `proyecto` (id o `todos`). `/api/proyectos`
  alimenta el selector. Si el cliente no manda proyecto, se detecta por nombre
  o alias.
- `data/gold_tuning.json` y `data/gold_test.json`, con campo `proyecto`.
  Workflow `.github/workflows/corpus.yml`: en un PR que toca `corpus/` valida
  el manifiesto, el guardrail y el hash, sin reindexar.
- Render de Markdown en el cliente (negrita, listas, código, enlaces http).
  El HTML crudo queda escapado. No hay dependencia nueva: `httpx` ya estaba.

### Changed

- El manual de STELLA vive en `corpus/stella/`. Los ids siguen
  `manual-stella:pN:j` cuando hay página. El prompt ya no está atado a un
  solo manual: se arma con los proyectos del manifiesto y cita
  «Proyecto · Documento · Sección (pág. N)».
- El gate `MIN_TOP1_SCORE` sigue en **2.0**. Corre después de filtrar por
  proyecto, así que con un solo proyecto el subconjunto es el mismo manual
  con el que se calibró. Medido de nuevo sobre estos chunks: «¿cómo agrego un
  cliente?» queda en ~6.2 y «receta de pizza» / «quién ganó el oscar» en 0.
  Subirlo descartaría preguntas cortas de un proyecto chico cuando haya más
  documentos en «todos». «¿Qué es STELLA?» prioriza la introducción aunque el
  nombre esté repartido por todo el manual.
- La sección 3.3 (atajos) queda citada en la pág. 12, donde sigue el
  procedimiento; el gold de tuning acepta 12 y 11. Ese caso no entra en
  `gold_test`.
- BM25 no tokeniza la línea de ruta: si no, el nombre del proyecto tendría
  idf 0. La ruta sí entra en el texto que se embebe y en el que ve el modelo.
- El índice de esta rama se generó con fastembed (`origen: local`, 113
  vectores, dim 768). No había `JINA_API_KEY` en el entorno, así que no se
  pudo comparar el coseno contra la API. Si al comparar da menos de 0.99,
  hay que reindexar con `scripts/ingest.py --provider api`.

### Fixed

- Hallazgo M4: el Markdown ya no se indexa como texto plano de PDF; se corta
  por estructura.
- Hallazgo M2: la respuesta sintética se muestra como Markdown escapado, no
  como texto con asteriscos.

### Files

- `corpus/stella/`, `corpus/manifiesto.json`, `scripts/comparar_embeddings.py`,
  `rag/manifiesto.py`,
  `rag/secretos.py`, `rag/citas.py`, `rag/chunking.py`, `rag/embeddings.py`,
  `rag/hybrid.py`, `rag/config.py`, `scripts/ingest.py`, `scripts/md2pdf.py`
- `app/main.py`, `app/config.py`, `app/ratelimit.py`, `app/services/llm.py`,
  `app/services/rag_service.py`
- `client/src/App.jsx`, `client/src/lib/markdown.js`, `client/src/lib/api.js`,
  `client/scripts/copy-corpus.mjs`
- `data/chunks.jsonl`, `data/index.faiss`, `data/corpus.sha256`,
  `data/ingest_meta.json`, `data/gold_set.json`, `data/gold_test.json`,
  `data/gold_tuning.json`
- `tests/`, `.github/workflows/corpus.yml`, `.env.example`, `README.md`,
  `AGENTS.md`, `CHANGELOG.md`

### Tests

89 passed, 1 skipped

## 2026-10-05 — fix/auditoria-2026-10-05

### Added

- Rate limit distribuido opcional con Upstash Redis REST (`httpx`, sin
  dependencias nuevas): `INCR` + `EXPIRE` en `rl:{endpoint}:{ip}:{ventana}`
  cuando existen `UPSTASH_REDIS_REST_URL` y `UPSTASH_REDIS_REST_TOKEN`.
- Presupuesto diario de llamadas a Groq: `LLM_DAILY_BUDGET` (default 300,
  `0` = ilimitado), contador `llm:budget:YYYY-MM-DD` UTC con TTL de 2 días.
- Diccionario de sinónimos ES del dominio (`rag/sinonimos.py`), con peso
  0.5 del idf sobre el término original.
- Gate léxico por nombre de documento del manifiesto: si la consulta lo
  nombra y hay un término con df>0, no se descarta y se prioriza el chunk
  de introducción («¿Qué es STELLA?» en este corpus).
- `AGENTS.md` y este changelog. Paso manual de Rate Limiting en el Firewall
  de Vercel documentado en el README (Deploy / Límites).

### Changed

- En modo `sintetica` el `top_k` efectivo queda en 5; `/api/search` sigue
  hasta 10.
- La IP sale de `x-vercel-forwarded-for`, después `x-real-ip`, después
  `x-forwarded-for`, después `request.client`.
- El mapa en memoria desaloja las IPs que hace más que no se ven y olvida
  hits vencidos. `BM25_BIGRAM_BONUS` y `MIN_TOP1_SCORE` no se tocaron.
- Gold set de 12 a 15 preguntas (las tres nuevas también entran en el top3
  de BM25).

### Fixed

- El rate limit de producción no frenaba: vivía en memoria por instancia y,
  al pasar de 10.000 IPs, un `_hits.clear()` reiniciaba a todos.
- Falsos negativos del gate: «¿Qué es STELLA?» (pág. 4), «¿Cómo hago una
  copia de seguridad?» (pág. 31) y «quiero cobrarle a un dentista» (pág. 26,
  cuentas corrientes). Las consultas ajenas al manual siguen en `[]`.
- Con el cupo de LLM agotado, `stream_answer` responde
  `rate_limited` sin llamar a Groq. El contador solo sube cuando la llamada
  sale de verdad.

### Files

- `app/ratelimit.py`, `app/config.py`, `app/main.py`, `app/services/llm.py`
- `rag/hybrid.py`, `rag/sinonimos.py`
- `tests/test_ratelimit.py`, `tests/test_llm.py`, `tests/test_api_rag.py`,
  `tests/test_retriever.py`, `tests/test_gold.py`, `tests/conftest.py`
- `data/gold_set.json`, `.env.example`, `README.md`, `AGENTS.md`,
  `CHANGELOG.md`

### Tests

73 passed, 1 skipped

## 2026-09-29 a 2026-10-02 — Fases 0–11

- **2026-09-29.** Andamiaje FastAPI + React + CI, y README con la descripción
  multi-documento.
- **2026-09-30.** Manual STELLA en español y generador de PDF page-aware;
  ingesta y recuperación híbrida BM25+FAISS con RRF; búsqueda y chat SSE
  (fragmentos / fallback); UI React con citas; config de Vercel, entrada ASGI
  y degradación a BM25.
- **2026-10-01.** Deploy en modo services con base `/asistente/`, wrapper que
  normaliza el prefijo, y README con el estado del deploy y el GIF.
- **2026-10-02.** Groq con reintentos ante 5xx; stopwords, gate anti-relleno
  y snippet; health con flags; rate limit en memoria, errores saneados y 429
  con `Retry-After`; UI con cancelación, errores legibles y accesibilidad;
  headers de seguridad y CI con uv/oxlint/build; bonus de proximidad BM25 por
  bigrama (gold 12/12); workflow repo-first con manifiesto de títulos.
