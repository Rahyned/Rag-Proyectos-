# CHANGELOG — Rag-Proyectos

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
