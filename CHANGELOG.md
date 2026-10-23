# CHANGELOG — Rag-Proyectos

## 2026-10-22 — fix/gold-solutionscars

### Added

- Reintento único en `embed_consulta` ante timeout o 5xx de Jina. Un 4xx
  no se reintenta.
- Circuito de Jina por fallos: 429 abre enseguida; timeout o 5xx recién
  al tercero dentro de 60 s. Un fallo aislado ya no apaga el canal denso.
- `/api/health` expone `dense_error_origen` (`timeout`, `status_429` o
  `status_5xx`) además de `dense_error`. El origen se guarda también en la
  clave de Redis del circuito.
- Tests para el circuito, el reintento, el TTL de Redis, el origen en
  health y la prioridad de la introducción.

### Changed

- `EMBED_TIMEOUT` pasa de 3.0 a 6.0 s y `JINA_CIRCUIT_SECONDS` de 600 a
  90 s.
- `_contiene_que_es` se generaliza en `_pide_panorama` para «qué es»,
  «cómo funciona», «qué hace», «para qué sirve», «contame de/sobre» y
  «de qué se trata». `_indice_intro` sigue usando la función vieja.
- `jina_en_pausa` ya no rearma la pausa local por la duración completa
  cuando la clave de Redis existe: manda el TTL que le queda a Redis.

### Fixed

- El canal denso dejaba de aportar durante 10 minutos por un solo timeout.
- «¿Cómo funciona STELLA?» y «¿Para qué sirve STELLA?» devuelven primero
  la introducción, no la tabla de §3.1 ni las FAQ de la luz o la sesión.
- Cada fallo de Jina loguea status y latencia, nunca la key.

### Files

- `app/main.py`
- `app/ratelimit.py`
- `rag/config.py`
- `rag/embeddings.py`
- `rag/hybrid.py`
- `tests/test_embeddings.py`
- `tests/test_health.py`
- `tests/test_ratelimit.py`
- `tests/test_retriever.py`

### Tests

`131 passed, 1 skipped`. El gold no baja: tuning BM25 hit@3 36/44 y hit@5
38/44; test BM25 hit@3 36/44 y hit@5 38/44, igual que antes del cambio.

## 2026-10-13 — fix/gold-solutionscars

### Changed

- En «¿Sirve para facturar?» de SolutionsCars, el texto arranca con
  las frases «¿sirve para facturar?», «¿factura con AFIP?» y «¿hace
  facturas?».
- Reingesta con la API de Jina: 454 chunks, dim 768, origen `api`.
  STELLA 201, SolutionsCars 118, RioDent 65, portafolio-web 70.
- `MIN_BM25_TOP3` sigue en 36 y `MIN_HYBRID_TOP3` en 41. El set de
  medición pasa de 45 a 44 positivas. `MIN_TOP1_SCORE` sigue en 2.0.

### Fixed

- El gold de SolutionsCars ya no pregunta «¿cómo hago un pedido?».
  El taller no tiene pedidos a proveedores. No pasó a las negativas:
  la misma frase sigue en el gold de otros proyectos, y la sección
  del documento todavía la responde, así que la búsqueda no vuelve
  vacía.

### Files

- `corpus/solutionscars/solutionscars.md`
- `data/gold_test.json`
- `data/chunks.jsonl`
- `data/index.faiss`
- `data/corpus.sha256`
- `data/ingest_meta.json`
- `tests/test_gold.py`

### Tests

`118 passed, 1 skipped`. Umbral del gate: 2.0. Las negativas del gold
siguen vacías.

hit@3 por proyecto, antes y después.

| proyecto | tuning BM25 | test BM25 | tuning híbrida | test híbrida |
|---|---|---|---|---|
| stella | 12/14 → 12/14 | 18/19 → 18/19 | 14/14 → 14/14 | 19/19 → 19/19 |
| solutionscars | 9/13 → 10/13 | 9/11 → 9/10 | 13/13 → 13/13 | 10/11 → 10/10 |
| laboratorio-riodent | 4/7 → 4/7 | 2/6 → 2/6 | 5/7 → 5/7 | 5/6 → 5/6 |
| portafolio-web | 7/7 → 7/7 | 4/6 → 4/6 | 7/7 → 7/7 | 4/6 → 4/6 |
| todos | 3/3 → 3/3 | 3/3 → 3/3 | 3/3 → 3/3 | 3/3 → 3/3 |
| total | 35/44 → 36/44 | 36/45 → 36/44 | 42/44 → 42/44 | 41/45 → 41/44 |

hit@5 por proyecto, antes y después.

| proyecto | tuning BM25 | test BM25 | tuning híbrida | test híbrida |
|---|---|---|---|---|
| stella | 13/14 → 13/14 | 18/19 → 18/19 | 14/14 → 14/14 | 19/19 → 19/19 |
| solutionscars | 9/13 → 10/13 | 10/11 → 10/10 | 13/13 → 13/13 | 10/11 → 10/10 |
| laboratorio-riodent | 5/7 → 5/7 | 3/6 → 3/6 | 7/7 → 7/7 | 6/6 → 6/6 |
| portafolio-web | 7/7 → 7/7 | 4/6 → 4/6 | 7/7 → 7/7 | 5/6 → 5/6 |
| todos | 3/3 → 3/3 | 3/3 → 3/3 | 3/3 → 3/3 | 3/3 → 3/3 |
| total | 37/44 → 38/44 | 38/45 → 38/44 | 44/44 → 44/44 | 43/45 → 43/44 |

Ningún caso que antes acertaba en hit@3 dejó de acertar. «¿sirve para
facturar?» (SolutionsCars, tuning) pasa a acertar también en BM25. El
top-1 es «¿Sirve para facturar?».

## 2026-10-12 — feat/guias-uso

### Added

- Guía de uso diario en el manual de STELLA y en la ficha de
  SolutionsCars: tareas paso a paso, problemas comunes y preguntas
  frecuentes.
- Treinta preguntas nuevas en el gold, todas con filtro de proyecto.
  Ocho van a tuning y siete a test, por proyecto. Si la misma pregunta
  se repite en dos proyectos, las dos filas quedan en el mismo archivo.
- Un test comprueba que cada sección citada por el gold existe como
  encabezado del markdown de ese documento.

### Changed

- En el manual de STELLA se quitaron detalles internos de mantenimiento
  y de sesión.
- El PDF del manual queda en 59 páginas.
- `scripts/md2pdf.py` imprime con un perfil temporal de Edge para que
  el PDF se escriba aunque el navegador ya esté abierto.
- Reingesta con la API de Jina: 454 chunks, dim 768, origen `api`,
  modelo `jinaai/jina-embeddings-v2-base-es`. STELLA 201, SolutionsCars
  118, RioDent 65, portafolio-web 70.
- `MIN_BM25_TOP3` pasa de 24 a 36 y `MIN_HYBRID_TOP3` de 27 a 41, sobre
  45 positivas de `gold_test`. `MIN_TOP1_SCORE` sigue en 2.0.
- El gold de métodos de pago apunta a la página 27: esa sección se
  corrió una página en el PDF nuevo.

### Fixed

- Donde dos secciones decían lo mismo, quedó una sola, con el
  encabezado que espera el gold. Donde no había duplicado, la sección
  esperada incluye la frase con la que pregunta el usuario.

### Files

- `corpus/stella/manual-stella.md`
- `corpus/stella/manual-stella.pdf`
- `corpus/solutionscars/solutionscars.md`
- `scripts/md2pdf.py`
- `data/chunks.jsonl`
- `data/index.faiss`
- `data/corpus.sha256`
- `data/ingest_meta.json`
- `data/gold_tuning.json`
- `data/gold_test.json`
- `tests/test_gold.py`

### Tests

`118 passed, 1 skipped`. Umbral del gate: 2.0. Las negativas del gold
siguen vacías.

hit@3 por proyecto, antes y después. El después suma las 30 preguntas
nuevas.

| proyecto | tuning BM25 | test BM25 | tuning híbrida | test híbrida |
|---|---|---|---|---|
| stella | 6/6 → 12/14 | 12/12 → 18/19 | 6/6 → 14/14 | 12/12 → 19/19 |
| solutionscars | 4/5 → 9/13 | 3/4 → 9/11 | 5/5 → 13/13 | 3/4 → 10/11 |
| laboratorio-riodent | 4/7 → 4/7 | 2/6 → 2/6 | 5/7 → 5/7 | 5/6 → 5/6 |
| portafolio-web | 7/7 → 7/7 | 4/6 → 4/6 | 7/7 → 7/7 | 4/6 → 4/6 |
| todos | 3/3 → 3/3 | 3/3 → 3/3 | 3/3 → 3/3 | 3/3 → 3/3 |
| total | 24/28 → 35/44 | 24/31 → 36/45 | 26/28 → 42/44 | 27/31 → 41/45 |

hit@5 por proyecto, antes y después.

| proyecto | tuning BM25 | test BM25 | tuning híbrida | test híbrida |
|---|---|---|---|---|
| stella | 6/6 → 13/14 | 12/12 → 18/19 | 6/6 → 14/14 | 12/12 → 19/19 |
| solutionscars | 5/5 → 9/13 | 3/4 → 10/11 | 5/5 → 13/13 | 3/4 → 10/11 |
| laboratorio-riodent | 5/7 → 5/7 | 3/6 → 3/6 | 7/7 → 7/7 | 6/6 → 6/6 |
| portafolio-web | 7/7 → 7/7 | 4/6 → 4/6 | 7/7 → 7/7 | 5/6 → 5/6 |
| todos | 3/3 → 3/3 | 3/3 → 3/3 | 3/3 → 3/3 | 3/3 → 3/3 |
| total | 26/28 → 37/44 | 25/31 → 38/45 | 28/28 → 44/44 | 29/31 → 43/45 |

Pendientes, las dos ya fallaban en el índice anterior:

- «¿sirve para facturar?» (SolutionsCars, tuning) no tiene hit@3 en
  BM25. El top-1 es «¿Puedo imprimir sin guardar?». La híbrida acierta,
  con top-1 «¿Sirve para facturar?».
- «¿cómo hago un pedido?» (SolutionsCars, test) no tiene hit@3 en BM25
  ni en la híbrida. El top-1 de BM25 es «¿Olvidé la contraseña, qué
  hago?». El de la híbrida es «Cómo recibo un auto en SolutionsCars».

## 2026-10-11 — fix/ruta-y-sinonimos

### Added

- Cinco consultas que fallaron en producción, en `gold_test`, y cinco
  variantes distintas en `gold_tuning` (precio, pedido, colorimetría y
  respaldo). No comparten el texto de la pregunta.
- `scripts/eval_gold.py` imprime hit@3 y hit@5 por proyecto, para BM25 y
  para la híbrida, en tuning y en test, y las negativas que no vuelven
  vacías. Sin `JINA_API_KEY` mide solo BM25.

### Changed

- La ruta del chunk y la cita colapsan segmentos consecutivos iguales
  (sin distinguir mayúsculas ni espacios de más). `chunk.seccion` no se
  toca. STELLA sigue «STELLA › Manual STELLA › …» porque esos nombres no
  son el mismo.
- Sinónimos de un solo sentido, peso 0.5: «cuánto sale / cuesta / tarifa /
  costo» aporta precio y presupuesto; precio y presupuesto se apuntan
  entre sí; encargo y «pedir un trabajo» aportan orden; pedido aporta
  orden; colorimetría, color dental y tono aportan «toma de color»; la
  regla de factura suma facturar, facturación, AFIP y ARCA. «copias»
  entra en la regla de backup. El stem de «copias» es el de «copia».
- Reingesta con la API de Jina: 316 chunks, dim 768, origen `api`.
  STELLA 113, SolutionsCars 68, RioDent 65, portafolio-web 70. El hash
  del corpus no cambió.
- El umbral sigue en 2.0. De 1.0 a 2.25 el tuning no se mueve y no hay
  falsos positivos. Desde 2.50 cae portafolio-web.

### Fixed

- La cita de una ficha ya no repite el nombre del proyecto cuando el
  título y el H1 son el mismo texto.

### Files

- `rag/chunking.py`
- `rag/citas.py`
- `rag/sinonimos.py`
- `scripts/eval_gold.py`
- `scripts/ingest.py`
- `tests/test_chunking.py`
- `tests/test_retriever.py`
- `tests/test_gold.py`
- `data/gold_tuning.json`
- `data/gold_test.json`
- `data/chunks.jsonl`
- `data/index.faiss`
- `data/ingest_meta.json`

### Tests

`117 passed, 1 skipped`. Umbral del gate: 2.0.

La línea base es solo BM25: en ese momento no había `JINA_API_KEY`.
hit@3 por proyecto, antes y después.

| proyecto | tuning BM25 | test BM25 | tuning híbrida | test híbrida |
|---|---|---|---|---|
| stella | 6/6 → 6/6 | 12/12 → 12/12 | — → 6/6 | — → 12/12 |
| solutionscars | 4/5 → 4/5 | 3/4 → 3/4 | — → 5/5 | — → 3/4 |
| laboratorio-riodent | 4/7 → 4/7 | 3/6 → 2/6 | — → 5/7 | — → 5/6 |
| portafolio-web | 6/7 → 7/7 | 4/6 → 4/6 | — → 7/7 | — → 4/6 |
| todos | 3/3 → 3/3 | 3/3 → 3/3 | — → 3/3 | — → 3/3 |

`MIN_BM25_TOP3` queda en 24 y `MIN_HYBRID_TOP3` en 27, sobre 31 positivas
de `gold_test`. Las negativas del gold siguen vacías.

## 2026-10-11 — feat/corpus-multiproyecto

### Added

- Tres fichas en el corpus: SolutionsCars, Laboratorio RioDent
  (`https://www.riodent.com.ar`) y portafolio-web
  (`https://portafolio-web-three-gamma.vercel.app`), con alias y tres
  preguntas de ejemplo cada una.
- `riodentlab@gmail.com` en `emails_publicos`. Es el contacto público del
  laboratorio.
- Gold de ajuste y de medición para los cuatro proyectos, con preguntas
  vagas, por alias, «¿Qué es X?», negativas y dos consultas con
  `proyecto: todos`. El Markdown se evalúa por sección, no por página.

### Changed

- El índice se rehízo con la API de Jina (`jina-embeddings-v2-base-es`,
  318 vectores, dim 768). STELLA 113, SolutionsCars 69, RioDent 66,
  portafolio-web 70.
- El umbral del gate sigue en 2.0. Entre 1.0 y 3.0 STELLA queda 6/6 y las
  negativas del gold vuelven vacías. En 3.25 se cae «quiero cobrarle a un
  dentista».
- `MIN_BM25_TOP3` pasa a 24 y `MIN_HYBRID_TOP3` a 23, medidos en
  `gold_test` (26 positivas).

### Fixed

- En la ficha de portafolio-web se sacó del historial el 8 y el 9 de
  octubre de 2026, y «¿Hay videos?» responde solo que hoy no hay video
  cargado. «5 de octubre» y «Slot» nombran el proyecto.
- En SolutionsCars, la calidad queda descrita como una suite de tests
  automáticos.

### Files

- `corpus/manifiesto.json`
- `corpus/solutionscars/solutionscars.md`
- `corpus/laboratorio-riodent/laboratorio-riodent.md`
- `corpus/portafolio-web/portafolio-web.md`
- `data/chunks.jsonl`, `data/index.faiss`, `data/corpus.sha256`,
  `data/ingest_meta.json`
- `data/gold_tuning.json`, `data/gold_test.json`
- `tests/test_gold.py`, `tests/test_retriever.py`, `tests/test_ingest.py`,
  `tests/test_api_rag.py`, `tests/test_secretos.py`
- `CHANGELOG.md`

### Tests

110 passed, 1 skipped

Gate sobre `gold_tuning`, de 1.00 a 3.00: STELLA 6/6, SolutionsCars 4/5,
RioDent 4/5, portafolio-web 5/5, todos 2/2, falsos positivos 0. En 3.25
STELLA baja a 5/6.

Top-3 en `gold_test`:

| Proyecto | BM25 | Híbrida |
|---|---|---|
| STELLA | 12/12 | 12/12 |
| SolutionsCars | 3/4 | 3/4 |
| RioDent | 3/4 | 3/4 |
| portafolio-web | 4/4 | 3/4 |
| todos | 2/2 | 2/2 |
| Total | 24/26 | 23/26 |

## 2026-10-06 — fix/post-merge-2026-10-06

### Added

- Pausa de Jina de 10 minutos tras un timeout, un 5xx o un 429. Vive en
  memoria y, si hay Upstash, en `jina:circuit`. Mientras dura, la consulta
  va a BM25 sin esperar el timeout.
- Redirect permanente de `/asistente/corpus/manual-stella.pdf` a
  `/asistente/corpus/stella/manual-stella.pdf`.
- En el README, cómo correr `scripts/comparar_embeddings.py` con la key en
  el entorno: coseno mínimo 0.99, o reindexar con `--provider api`.

### Changed

- `JINA_DAILY_BUDGET` se descuenta solo cuando la llamada responde OK. El
  cliente HTTP de Jina se reutiliza (keep-alive) en vez de abrirse por
  consulta. El log de un fallo deja el status o `timeout`, sin la key.
- El gate ya no cuenta el nombre del documento ni del proyecto como término.
  Ese nombre sale del puntaje del umbral y hace falta al menos otra palabra
  con df>0. «¿Qué es STELLA?» sigue priorizando la introducción por su
  camino propio. El umbral sigue en 2.0.

### Fixed

- El guardrail no veía asignaciones después de `_` (`LLM_API_KEY`,
  `JINA_API_KEY`, `UPSTASH_REDIS_REST_TOKEN`). Ahora también corta `gsk_`,
  `jina_`, `sk-` / `sk-proj-`, `AIza` y un valor asignado a un nombre Upstash.
- Un manifiesto inválido le responde al cliente «configuración inválida».
  La ruta queda solo en el log.

### Files

- `rag/secretos.py`, `rag/embeddings.py`, `rag/hybrid.py`, `app/ratelimit.py`,
  `app/main.py`, `vercel.json`
- `tests/test_secretos.py`, `tests/test_embeddings.py`, `tests/test_retriever.py`,
  `tests/test_api_rag.py`
- `README.md`, `CHANGELOG.md`

### Tests

105 passed, 1 skipped

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
