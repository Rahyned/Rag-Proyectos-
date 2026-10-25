"""Imprime hit@3 y hit@5 del gold, por proyecto, para BM25 y la híbrida.

Si `EMBEDDINGS_PROVIDER` está definida, se respeta (por ejemplo `off` para
medir solo BM25). Si no, con `CF_ACCOUNT_ID` y `CF_API_TOKEN` usa
Cloudflare; si no, con `JINA_API_KEY` usa Jina; sin ninguna, apaga el
denso: el modelo local (ONNX) no se carga.

La eval activa `CF_USAGE_SCOPE=eval`: cupo y circuito propios
(`eval:cloudflare:*`, `CF_EVAL_DAILY_BUDGET`, default 1500), sin tocar el
cupo de producción ni el del reranker.

`--rerank` agrega la comparación del gold de test: RRF solo, reranker en
modo `replace` y `fuse` con pesos 0.3/0.5/0.7, cada uno con `RERANK_TOP_N`
10 y 20, siempre con top 3 y top 5. Los resultados del reranker se cachean
por (consulta, pool), así la matriz completa gasta una llamada por consulta
y por `RERANK_TOP_N` (tamaño del gold × 2), no una por tabla. Necesita
`CF_ACCOUNT_ID` y `CF_API_TOKEN`; sin credenciales la comparación se omite
(no se inventan números). Con `--rerank` también imprime el corte `v1`
(los 44 casos viejos) frente al gold completo.

`--solo-top10` implica `--rerank` y deja solo `top_n=10` (una llamada de
rerank por consulta del gold de test). Al inicio imprime el cupo de eval y
una estimación de llamadas a Cloudflare (embeddings + rerank).

`--fallos` lista las positivas del gold de test donde la híbrida no acierta
en top 3: pregunta, chunk esperado, top 5 BM25 / denso / RRF (rank + score).

`--rrf-grid` prueba pesos BM25:denso (1:1, 1.5:1, 2:1, 3:1) y k de RRF
(30, 60, 100) sobre tuning y test. Reusa embeddings en caché (una llamada
por pregunta). También activa `CF_USAGE_SCOPE=eval`.
"""

from __future__ import annotations

import os
import sys
from collections import defaultdict
from collections.abc import MutableMapping, Sequence
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def default_embeddings_provider(
    environ: MutableMapping[str, str] | None = None,
) -> str:
    """Elige el provider cuando `EMBEDDINGS_PROVIDER` no está seteada.

    Cloudflare gana si hay cuenta y token; si no, Jina con `JINA_API_KEY`;
    sin credenciales, `off` (solo BM25, sin ONNX local).
    """
    env = os.environ if environ is None else environ
    if env.get("CF_ACCOUNT_ID", "").strip() and env.get("CF_API_TOKEN", "").strip():
        return "cloudflare"
    if env.get("JINA_API_KEY", "").strip():
        return "api"
    return "off"


def top_ns_rerank(solo_top10: bool) -> tuple[int, ...]:
    """Tamaños de pool a medir con el reranker."""
    return (10,) if solo_top10 else (20, 10)


# Pesos BM25:denso y k a explorar con --rrf-grid.
RRF_WEIGHTS = ((1.0, 1.0), (1.5, 1.0), (2.0, 1.0), (3.0, 1.0))
RRF_KS = (30, 60, 100)


@dataclass(frozen=True)
class Flags:
    rerank: bool = False
    solo_top10: bool = False
    fallos: bool = False
    rrf_grid: bool = False


def flags_cli(argv: Sequence[str] | None = None) -> Flags:
    """Parsea flags de `sys.argv` (o `argv`)."""
    args = list(sys.argv[1:] if argv is None else argv)
    solo_top10 = "--solo-top10" in args or "--solo-rerank-top10" in args
    return Flags(
        rerank="--rerank" in args or solo_top10,
        solo_top10=solo_top10,
        fallos="--fallos" in args,
        rrf_grid="--rrf-grid" in args,
    )


def estimar_llamadas_cloudflare(
    *,
    provider: str,
    rerank: bool,
    top_ns: Sequence[int],
    n_consultas_embed: int,
    n_consultas_rerank: int,
) -> tuple[int, int, int]:
    """Estima (embeddings, rerank, total) de llamadas a Cloudflare.

    Embeddings: una por consulta distinta del gold (tuning + test) si el
    provider es `cloudflare`; el cache de consulta evita repetir. `--fallos`
    y `--rrf-grid` reusan ese cache. Rerank: una por consulta positiva del
    gold de test y por cada `top_n` (cache por consulta×pool).
    """
    embeds = n_consultas_embed if provider == "cloudflare" else 0
    reranks = n_consultas_rerank * len(tuple(top_ns)) if rerank else 0
    return embeds, reranks, embeds + reranks


# Antes de importar rag: sin provider explícito no se carga el ONNX local.
if not os.environ.get("EMBEDDINGS_PROVIDER", "").strip():
    os.environ["EMBEDDINGS_PROVIDER"] = default_embeddings_provider()

from app import config as app_config  # noqa: E402
from rag.config import RRF_K, TOP_K  # noqa: E402
from tests.test_gold import (  # noqa: E402
    GOLD_TEST_PATH,
    GOLD_TUNING_PATH,
    _acierto,
    _leer,
    _positivos,
    _retriever,
    _specs,
    _ultimo,
)

CASOS = (
    "toma de color",
    "cuánto sale una página web",
    "cómo hago un pedido al laboratorio",
    "qué tiene el portafolio",
    "¿cómo hago una copia de seguridad?",
)

_PESOS_FUSE = (0.3, 0.5, 0.7)
_RERANK_VARS = (
    "RAG_RERANK", "RAG_RERANK_WEIGHT", "RERANK_TOP_N",
    # Compat: si el entorno traía las viejas, se restauran al salir.
    "RERANK_ENABLED", "RERANK_MODE", "RERANK_WEIGHT",
)


def _por_proyecto(entries: list[dict]) -> dict[str, list[dict]]:
    grupos: dict[str, list[dict]] = defaultdict(list)
    for entry in entries:
        grupos[entry["proyecto"]].append(entry)
    return grupos


def _tabla(retriever, entries: list[dict], metodo: str) -> None:
    positivos = _positivos(entries)
    print(f"  {metodo}")
    print(f"  {'proyecto':<22} {'n':>4} {'hit@3':>8} {'hit@5':>8}")
    total3 = total5 = n = 0
    buscar = retriever.bm25 if metodo == "bm25" else retriever.search
    for proyecto, items in _por_proyecto(positivos).items():
        h3 = h5 = 0
        for entry in items:
            hits = buscar(entry["q"], TOP_K, proyecto=entry["proyecto"])
            h3 += int(_acierto(hits, entry, k=3))
            h5 += int(_acierto(hits, entry, k=5))
        print(f"  {proyecto:<22} {len(items):>4} {h3:>8} {h5:>8}")
        total3 += h3
        total5 += h5
        n += len(items)
    print(f"  {'TOTAL':<22} {n:>4} {total3:>8} {total5:>8}")


def _negativas(retriever, entries: list[dict], etiqueta: str) -> None:
    malas = []
    for entry in entries:
        if not entry.get("vacio"):
            continue
        hits = retriever.search(entry["q"], TOP_K, proyecto=entry["proyecto"])
        if hits:
            primero = hits[0]
            malas.append(
                f"    {entry['proyecto']}: {entry['q']!r} -> "
                f"{primero.get('doc_id')} / {_ultimo(primero.get('seccion') or '')}"
            )
    print(f"  negativas no vacías ({etiqueta}): {len(malas)}")
    for linea in malas:
        print(linea)


def _casos(retriever) -> None:
    test = {item["q"]: item for item in _leer(GOLD_TEST_PATH)}
    print("  casos de producción (primer resultado BM25)")
    for q in CASOS:
        entry = test[q]
        hits = retriever.bm25(q, TOP_K, proyecto=entry["proyecto"])
        if not hits:
            print(f"    {q!r} -> (vacio)")
            continue
        primero = hits[0]
        ok3 = _acierto(hits, entry, k=3)
        ok5 = _acierto(hits, entry, k=5)
        donde = primero.get("seccion") or f"(pag. {primero.get('page')})"
        print(
            f"    {q!r} -> {primero.get('proyecto')} / {donde}"
            f"  hit@3={ok3} hit@5={ok5}"
        )
        for i, hit in enumerate(hits, start=1):
            lugar = hit.get("seccion") or f"(pag. {hit.get('page')})"
            print(f"      {i}. {hit.get('proyecto')} / {lugar}")


def _configurar_rerank(*, enabled: bool, mode: str = "fuse",
                       peso: float = 0.5, top_n: int = 20) -> None:
    # Pisa RAG_RERANK del entorno: --rerank mide todas las configs igual.
    os.environ["RAG_RERANK"] = mode if enabled else "off"
    os.environ["RAG_RERANK_WEIGHT"] = str(peso)
    os.environ["RERANK_TOP_N"] = str(top_n)
    # Evita que RERANK_ENABLED viejo pelee con RAG_RERANK=off.
    os.environ.pop("RERANK_ENABLED", None)
    os.environ.pop("RERANK_MODE", None)
    os.environ.pop("RERANK_WEIGHT", None)


def _resumen_gold(retriever, entries: list[dict], metodo: str) -> None:
    """Corta el gold por `v1` y completo: una fila por corte, top 3/5."""
    v1 = [entry for entry in entries if entry.get("v1")]
    buscar = retriever.bm25 if metodo == "bm25" else retriever.search
    cortes = (
        (f"v1 ({len(v1)})", v1),
        (f"completo ({len(entries)})", entries),
    )
    for etiqueta, subset in cortes:
        positivos = _positivos(subset)
        h3 = h5 = 0
        for entry in positivos:
            hits = buscar(entry["q"], TOP_K, proyecto=entry["proyecto"])
            h3 += int(_acierto(hits, entry, k=3))
            h5 += int(_acierto(hits, entry, k=5))
        print(f"  {etiqueta:<18} {len(positivos):>4} {h3:>8} {h5:>8}")


def _comparar_reranker(retriever, entries: list[dict],
                       timeout: float = 20.0,
                       top_ns: Sequence[int] = (20, 10)) -> None:
    """Mide el gold con RRF solo, replace y fuse (pesos × top_n)."""
    print("\ntest — con y sin reranker (top 3 / top 5)")
    previo = {name: os.environ.get(name) for name in _RERANK_VARS}
    try:
        print("  gold viejo vs nuevo")
        print(f"  {'corte':<14} {'n':>4} {'hit@3':>8} {'hit@5':>8}")
        _configurar_rerank(enabled=False)
        print("  RRF solo")
        _resumen_gold(retriever, entries, "search")
        primer_top = 10 if 10 in top_ns else top_ns[0]
        _configurar_rerank(enabled=True, mode="fuse", peso=0.5, top_n=primer_top)
        print(f"  fuse 0.5 · top_n={primer_top}")
        _resumen_gold(retriever, entries, "search")
        _configurar_rerank(enabled=False)
        _tabla(retriever, entries, "RRF solo")
        # Igual que EMBED_TIMEOUT: la medición prioriza calidad, no latencia.
        reranker = getattr(retriever, "_reranker", None)
        if reranker is not None:
            reranker.timeout = timeout
        for top_n in top_ns:
            _configurar_rerank(enabled=True, mode="replace", top_n=top_n)
            _tabla(retriever, entries, f"reranker replace · top_n={top_n}")
            for peso in _PESOS_FUSE:
                _configurar_rerank(
                    enabled=True, mode="fuse", peso=peso, top_n=top_n,
                )
                _tabla(retriever, entries, f"fuse {peso} · top_n={top_n}")
    finally:
        for name, valor in previo.items():
            if valor is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = valor


def _formato_esperado(entry: dict) -> str:
    """Texto corto del chunk/página que el gold acepta."""
    partes = []
    for spec in _specs(entry):
        doc = spec.get("doc_id") or entry.get("doc_id") or "?"
        if "page" in spec or "pages" in spec:
            pages = spec.get("pages") or [spec["page"]]
            partes.append(f"{doc} pág. {','.join(str(p) for p in pages)}")
            continue
        secciones = list(spec.get("sections") or [])
        if spec.get("section"):
            secciones.append(spec["section"])
        if secciones:
            partes.append(f"{doc} / {' | '.join(secciones)}")
        else:
            partes.append(str(doc))
    return " · ".join(partes) if partes else "(sin especificación)"


def _linea_hit(hit: dict) -> str:
    lugar = hit.get("seccion") or f"(pag. {hit.get('page')})"
    return (
        f"    {hit['rank']}. score={hit['score']:.4f}  "
        f"{hit.get('proyecto')} / {lugar}  [{hit.get('chunk_id')}]"
    )


def _imprimir_canal(nombre: str, hits: list[dict]) -> None:
    print(f"  {nombre} (top {len(hits)})")
    if not hits:
        print("    (vacío)")
        return
    for hit in hits:
        print(_linea_hit(hit))


def _cache_canales(retriever, entries: list[dict]) -> dict[tuple, tuple | None]:
    """Una embebidura por (q, proyecto); reusa el cache del embedder."""
    cache: dict[tuple, tuple | None] = {}
    for entry in entries:
        clave = (entry["q"], entry["proyecto"])
        if clave in cache:
            continue
        cache[clave] = retriever.scores_canales(
            entry["q"], proyecto=entry["proyecto"],
        )
    return cache


def _hit_counts(retriever, entries: list[dict], cache: dict,
                *, k_rrf: int, w_lex: float, w_dense: float
                ) -> tuple[int, int, int]:
    """(n, hit@3, hit@5) con RRF ponderado sobre scores cacheados."""
    positivos = _positivos(entries)
    h3 = h5 = 0
    for entry in positivos:
        scores = cache.get((entry["q"], entry["proyecto"]))
        if scores is None:
            continue
        lex, dense, allowed = scores
        hits = retriever.hits_rrf(
            lex, dense, allowed, top_k=TOP_K,
            k=k_rrf, w_lex=w_lex, w_dense=w_dense,
        )
        h3 += int(_acierto(hits, entry, k=3))
        h5 += int(_acierto(hits, entry, k=5))
    return len(positivos), h3, h5


def _imprimir_fallos(retriever, entries: list[dict]) -> None:
    """Preguntas del gold donde la híbrida (RRF default) falla en top 3."""
    print("\nfallos híbrida (top 3)")
    n_fallos = 0
    for entry in _positivos(entries):
        hibrida = retriever.search(entry["q"], TOP_K, proyecto=entry["proyecto"])
        if _acierto(hibrida, entry, k=3):
            continue
        n_fallos += 1
        print(f"\n  [{entry['proyecto']}] {entry['q']!r}")
        print(f"  esperado: {_formato_esperado(entry)}")
        bm25 = retriever.bm25(entry["q"], 5, proyecto=entry["proyecto"])
        scores = retriever.scores_canales(entry["q"], proyecto=entry["proyecto"])
        if scores is None:
            _imprimir_canal("BM25", bm25)
            print("  denso / RRF: canal denso no disponible")
            continue
        lex, dense, allowed = scores
        denso = retriever._hits(dense, 5, engine="denso")
        rrf_hits = retriever.hits_rrf(
            lex, dense, allowed, top_k=5, k=RRF_K, w_lex=1.0, w_dense=1.0,
        )
        _imprimir_canal("BM25", bm25)
        _imprimir_canal("denso", denso)
        _imprimir_canal("RRF 1:1 k=60", rrf_hits)
    print(f"\n  total fallos top3: {n_fallos}")


def _rrf_grid(retriever, tuning: list[dict], test: list[dict]) -> None:
    """Grilla de pesos BM25:denso × k; una embebidura por pregunta."""
    print("\nrrf-grid (BM25:denso × k)")
    print(
        f"  {'peso':<10} {'k':>4}  "
        f"{'tun@3':>7} {'tun@5':>7}  "
        f"{'test@3':>7} {'test@5':>7}"
    )
    unidos = list(tuning) + list(test)
    cache = _cache_canales(retriever, unidos)
    disponibles = sum(1 for v in cache.values() if v is not None)
    print(f"  canales listos: {disponibles}/{len(cache)} consultas (1 embed c/u)")
    for w_lex, w_dense in RRF_WEIGHTS:
        etiqueta = f"{w_lex:g}:{w_dense:g}"
        for k_rrf in RRF_KS:
            n_t, t3, t5 = _hit_counts(
                retriever, tuning, cache,
                k_rrf=k_rrf, w_lex=w_lex, w_dense=w_dense,
            )
            n_e, e3, e5 = _hit_counts(
                retriever, test, cache,
                k_rrf=k_rrf, w_lex=w_lex, w_dense=w_dense,
            )
            print(
                f"  {etiqueta:<10} {k_rrf:>4}  "
                f"{t3:>3}/{n_t:<3} {t5:>3}/{n_t:<3}  "
                f"{e3:>3}/{n_e:<3} {e5:>3}/{n_e:<3}"
            )


def main() -> None:
    # Cupo y circuito propios: no gasta CF_DAILY_BUDGET ni rerank:* de prod.
    os.environ["CF_USAGE_SCOPE"] = "eval"
    flags = flags_cli()
    top_ns = top_ns_rerank(flags.solo_top10)
    hibrida = os.environ.get("EMBEDDINGS_PROVIDER", "").strip().lower() != "off"
    provider = os.environ.get("EMBEDDINGS_PROVIDER", "").strip().lower()
    if hibrida:
        import rag.embeddings as embeddings

        # La medición no usa el timeout de 3s de una consulta en producción:
        # si vence, el circuito se abre y el resto de la tabla cae a BM25.
        embeddings.EMBED_TIMEOUT = 20.0
    print("denso:", "hibrida (API)" if hibrida else "apagado, solo BM25")
    print(
        "cupo eval:",
        f"CF_EVAL_DAILY_BUDGET={app_config.cf_eval_daily_budget()}",
        "(claves eval:cloudflare:*)",
    )
    # Las tablas de siempre son el baseline RRF: el reranker solo se paga
    # con --rerank, y ahí el cache reutiliza las llamadas entre configuraciones.
    os.environ["RAG_RERANK"] = "off"
    os.environ.pop("RERANK_ENABLED", None)
    comparar = flags.rerank
    if comparar and not hibrida:
        print("reranker: el denso está apagado; no hay híbrida que reordenar")
        comparar = False
    if comparar and not (app_config.cf_account_id() and app_config.cf_api_token()):
        print(
            "reranker: faltan CF_ACCOUNT_ID y CF_API_TOKEN; "
            "se omite la comparación con y sin reranker"
        )
        comparar = False
    if (flags.fallos or flags.rrf_grid) and not hibrida:
        print("fallos/rrf-grid: el denso está apagado; se omiten")
        flags = Flags(
            rerank=flags.rerank,
            solo_top10=flags.solo_top10,
            fallos=False,
            rrf_grid=False,
        )
    tuning_entries = _leer(GOLD_TUNING_PATH)
    test_entries = _leer(GOLD_TEST_PATH)
    embeds, reranks, total = estimar_llamadas_cloudflare(
        provider=provider,
        rerank=comparar,
        top_ns=top_ns if comparar else (),
        n_consultas_embed=len(tuning_entries) + len(test_entries),
        n_consultas_rerank=len(_positivos(test_entries)),
    )
    extras = []
    if flags.solo_top10 and comparar:
        extras.append("solo top_n=10")
    if flags.fallos or flags.rrf_grid:
        extras.append("fallos/rrf-grid reusan cache de embeddings")
    print(
        f"estimación Cloudflare: ~{embeds} embeddings + ~{reranks} rerank "
        f"= ~{total} llamadas"
        + (f" ({'; '.join(extras)})" if extras else "")
    )
    retriever = _retriever()
    for etiqueta, entries in (("tuning", tuning_entries),
                              ("test", test_entries)):
        print(f"\n{etiqueta}")
        _tabla(retriever, entries, "bm25")
        if hibrida:
            _tabla(retriever, entries, "hibrida")
        _negativas(retriever, entries, etiqueta)
    print("\ntest — corte v1 vs completo (top 3 / top 5)")
    print(f"  {'corte':<18} {'n':>4} {'hit@3':>8} {'hit@5':>8}")
    print("  bm25")
    _resumen_gold(retriever, test_entries, "bm25")
    if hibrida:
        print("  hibrida")
        _resumen_gold(retriever, test_entries, "search")
    if comparar:
        _comparar_reranker(retriever, test_entries, top_ns=top_ns)
    if flags.fallos:
        _imprimir_fallos(retriever, test_entries)
    if flags.rrf_grid:
        _rrf_grid(retriever, tuning_entries, test_entries)
    print()
    _casos(retriever)


if __name__ == "__main__":
    main()
