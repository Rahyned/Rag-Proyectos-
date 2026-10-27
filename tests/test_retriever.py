"""Anti-relleno: gate de score, filtro por proyecto y snippet de lectura."""

import json

import pytest

from app.services import rag_service
from rag.config import INDEX_PATH
from rag.hybrid import HybridRetriever, tokenize


def _retriever() -> HybridRetriever:
    if not INDEX_PATH.exists():
        pytest.skip("índice no generado (corré scripts/ingest.py)")
    return HybridRetriever()


def test_gate_bloquea_ajenas_al_manual(monkeypatch):
    """Lo que no está en ningún documento no pasa. Argentina y el cine no salen de STELLA."""
    monkeypatch.setenv("RAG_DENSE", "0")
    retriever = _retriever()
    for query in (
        "recetas de cocina italianas",
        "el hola man",
        "¿cuál es la capital de Noruega?",
    ):
        assert retriever.search(query, 5) == [], query
    # «Argentina» y «películas» aparecen en portafolio-web. En STELLA siguen ajenas.
    for query in ("economía argentina", "películas de terror"):
        assert retriever.search(query, 5, proyecto="stella") == [], query


def test_bm25_bigrama_adyacente_recibe_bonus():
    """Mismo TF y longitud: gana quien tiene el bigrama de la query seguido.

    "agregar un cliente" tokeniza a [agreg, client] (stopwords fuera), así
    que (agreg, client) es adyacente; con los tokens invertidos no lo es.
    """
    from rag.hybrid import BM25_BIGRAM_BONUS, bm25_scores, tokenize

    docs = [tokenize("agregar un cliente"), tokenize("cliente agregar")]
    df: dict[str, int] = {}
    for doc in docs:
        for t in set(doc):
            df[t] = df.get(t, 0) + 1
    scores = bm25_scores("agregar cliente", docs, df, len(docs))
    assert scores[0] > scores[1]
    assert scores[0] - scores[1] == pytest.approx(BM25_BIGRAM_BONUS)


def test_gate_deja_pasar_legitimas(monkeypatch):
    monkeypatch.setenv("RAG_DENSE", "0")
    retriever = _retriever()
    for query in ("¿cómo restauro un backup?", "¿cómo cargo un cliente nuevo?",
                  "¿cómo facturo un comprobante?"):
        assert retriever.search(query, 5), query


def test_enrich_snippet_centra_en_la_query():
    text = "x" * 120 + " el módulo de backup se ejecuta a las 22:00." + "y" * 300
    hits = [{"title": "Manual STELLA", "page": 7, "doc_id": "manual",
             "text": text}]
    [item] = rag_service.enrich(hits, "¿dónde está el backup?")
    assert "backup" in item["snippet"]
    assert item["snippet"].startswith("…")
    assert len(item["snippet"]) <= 202
    assert "Manual STELLA" in item["citation"]
    assert "(pág. 7)" in item["citation"]


def test_enrich_snippet_sin_coincidencia_toma_la_cabecera():
    text = "texto del manual sin ninguna palabra de la consulta. " * 20
    hits = [{"title": "Manual STELLA", "page": 3, "doc_id": "manual",
             "text": text}]
    [item] = rag_service.enrich(hits, "zzzzqqq")
    assert item["snippet"].startswith("texto del manual")
    assert item["snippet"].endswith("…")
    assert not item["snippet"].startswith("…")


def test_el_nombre_no_abre_el_gate(monkeypatch):
    """El nombre del proyecto no alcanza: hace falta otro término del documento."""
    monkeypatch.setenv("RAG_DENSE", "0")
    retriever = _retriever()
    for nombre in ("stella", "solutionscars", "solucars", "riodent", "portafolio"):
        assert retriever.search(f"{nombre} quién ganó el oscar", 5) == [], nombre
    pages = [h["page"] for h in retriever.search("¿Qué es STELLA?", 5)]
    assert 4 in pages[:3]
    gold = json.loads(
        (INDEX_PATH.parent / "gold_test.json").read_text(encoding="utf-8")
    )
    for entry in gold:
        if entry.get("proyecto") != "stella" or entry.get("vacio"):
            continue
        if "page" not in entry and "pages" not in entry:
            continue
        hits = retriever.search(entry["q"], 5, proyecto=entry["proyecto"])
        esperadas = entry.get("pages") or [entry["page"]]
        assert any(h["page"] in esperadas for h in hits[:3]), entry["q"]


def test_que_es_stella_incluye_la_introduccion(monkeypatch):
    """«¿Qué es STELLA?» prioriza la introducción aunque el nombre esté en todo el manual."""
    monkeypatch.setenv("RAG_DENSE", "0")
    pages = [h["page"] for h in _retriever().search("¿Qué es STELLA?", 5)]
    assert 4 in pages[:3]


@pytest.mark.parametrize("metodo", ("search", "bm25"))
@pytest.mark.parametrize("consulta", (
    "como funciona stella?",
    "para que sirve stella",
    "¿Qué es STELLA?",
))
def test_panorama_prioriza_la_introduccion(monkeypatch, metodo, consulta):
    """Las preguntas de panorama traen «¿Qué es STELLA?» antes que §3.1."""
    monkeypatch.setenv("RAG_DENSE", "0")
    hits = getattr(_retriever(), metodo)(consulta, 5)
    assert hits, consulta
    assert hits[0]["page"] == 4
    assert "¿Qué es STELLA?" in (hits[0]["seccion"] or "")


def test_que_es_funciona_en_los_cuatro(monkeypatch):
    """«¿Qué es X?» responde en cada proyecto, no solo en STELLA."""
    monkeypatch.setenv("RAG_DENSE", "0")
    retriever = _retriever()
    casos = (
        ("¿Qué es STELLA?", "stella"),
        ("¿Qué es SolutionsCars?", "solutionscars"),
        ("¿Qué es Laboratorio RioDent?", "laboratorio-riodent"),
        ("¿Qué es portafolio-web?", "portafolio-web"),
    )
    for consulta, proyecto in casos:
        hits = retriever.search(consulta, 5)
        assert hits, consulta
        assert hits[0]["proyecto"] == proyecto, consulta
        assert all(h["proyecto"] == proyecto for h in hits), consulta


def test_riodent_no_aparece_si_el_proyecto_es_stella(monkeypatch):
    """El filtro se aplica antes de rankear: un pedido de RioDent no sale de STELLA."""
    monkeypatch.setenv("RAG_DENSE", "0")
    hits = _retriever().search(
        "¿cómo pido la toma de color?", 5, proyecto="stella",
    )
    assert all(h["proyecto"] == "stella" for h in hits)
    assert all(h["doc_id"] != "laboratorio-riodent" for h in hits)


def test_gate_no_vacia_por_nombre_de_otro_proyecto(monkeypatch):
    """Nombres de docs fuera del filtro no apagan el umbral BM25.

    Antes, «RioDent» / «sistemas» matcheaban laboratorio o SolutionsCars,
    se ignoraban en el umbral y `search()` devolvía [] en portafolio-web
    aunque el RRF tuviera la FAQ correcta primera.
    """
    monkeypatch.setenv("RAG_DENSE", "0")
    from tests.test_gold import _acierto, _leer, GOLD_TEST_PATH

    retriever = _retriever()
    gold = {item["q"]: item for item in _leer(GOLD_TEST_PATH)}
    for consulta in (
        "¿qué es RioDent en el portafolio?",
        "¿qué proyectos de sistemas hay?",
    ):
        entry = gold[consulta]
        hits = retriever.search(consulta, 5, proyecto=entry["proyecto"])
        assert hits, consulta
        assert _acierto(hits, entry, k=3), consulta


def test_nombres_en_solo_docs_del_recorte(monkeypatch):
    monkeypatch.setenv("RAG_DENSE", "0")
    retriever = _retriever()
    allowed = retriever._mascara("portafolio-web")
    # Sin filtro: gana laboratorio-riodent. Con filtro: portafolio o nada de lab.
    assert retriever._doc_nombrado("¿qué es RioDent en el portafolio?") == (
        "laboratorio-riodent"
    )
    assert retriever._doc_nombrado(
        "¿qué es RioDent en el portafolio?", allowed,
    ) != "laboratorio-riodent"
    assert "riodent" not in retriever._nombres_en(
        "¿qué es RioDent en el portafolio?", allowed,
    )


def test_aceite_en_riodent_no_se_abre_por_un_sinonimo():
    """«aceite» no dispara un sinónimo que meta vocabulario del laboratorio."""
    from rag.sinonimos import expandir

    pesos = dict(expandir(tokenize("¿cómo cambio el aceite del auto?")))
    assert pesos == {"cambi": 1.0, "aceit": 1.0, "auto": 1.0}


def test_detecta_alias_de_los_proyectos_nuevos():
    from rag.manifiesto import detectar_proyecto, limpiar_cache

    limpiar_cache()
    assert detectar_proyecto("¿qué onda con solucars?") == "solutionscars"
    assert detectar_proyecto("en soluciones cars cómo facturo") == "solutionscars"
    assert detectar_proyecto("el sistema del taller y la caja") == "solutionscars"
    assert detectar_proyecto("en rio dent dónde queda") == "laboratorio-riodent"
    assert detectar_proyecto("el laboratorio") == "laboratorio-riodent"
    assert detectar_proyecto("mirá lautaro.dev") == "portafolio-web"
    assert detectar_proyecto("la página de lautaro") == "portafolio-web"
    assert detectar_proyecto("abrí el portafolio") == "portafolio-web"


def test_copia_de_seguridad_trae_backup_o_faq(monkeypatch):
    """La sección en el léxico prioriza la FAQ; el capítulo de backups sigue cerca."""
    monkeypatch.setenv("RAG_DENSE", "0")
    hits = _retriever().search("¿Cómo hago una copia de seguridad?", 5)
    assert hits
    top3 = hits[:3]
    pages = [h["page"] for h in top3]
    secciones = [(h.get("seccion") or "").lower() for h in top3]
    assert (
        31 in pages
        or any("copia de seguridad" in s for s in secciones)
    )
    assert 31 in [h["page"] for h in hits[:5]]


def test_cobrarle_a_un_dentista_trae_cuentas_corrientes(monkeypatch):
    """Pág. 26 abre «9. Cuentas corrientes»: debe, haber, saldo y el cobro."""
    monkeypatch.setenv("RAG_DENSE", "0")
    hits = _retriever().search("quiero cobrarle a un dentista", 5)
    assert hits
    assert 26 in [h["page"] for h in hits[:5]]


def test_expandir_sinonimo_pesa_menos_que_el_original():
    from rag.sinonimos import PESO_SINONIMO, expandir

    pesos = dict(expandir(tokenize("dentista")))
    assert pesos["dentist"] == 1.0
    assert pesos["odontolog"] == PESO_SINONIMO
    copia = dict(expandir(tokenize("¿Cómo hago una copia de seguridad?")))
    assert copia["copi"] == 1.0
    assert copia["backup"] == PESO_SINONIMO


def test_sinonimos_de_precio_pedido_color_y_factura():
    from rag.sinonimos import PESO_SINONIMO, expandir

    def pesos(q: str) -> dict[str, float]:
        return dict(expandir(tokenize(q)))

    sale = pesos("cuánto sale")
    assert sale["sale"] == 1.0
    assert sale["preci"] == PESO_SINONIMO
    assert sale["presupuest"] == PESO_SINONIMO
    assert pesos("cuánto cuesta")["preci"] == PESO_SINONIMO
    assert pesos("tarifa")["presupuest"] == PESO_SINONIMO
    assert pesos("precio")["presupuest"] == PESO_SINONIMO
    assert pesos("presupuesto")["preci"] == PESO_SINONIMO
    assert pesos("precio")["preci"] == 1.0

    encargo = pesos("quiero encargar un trabajo")
    assert encargo["orden"] == PESO_SINONIMO
    assert "trabaj" not in encargo or encargo["trabaj"] == 1.0
    assert pesos("pedido")["orden"] == PESO_SINONIMO
    assert "ped" not in pesos("quiero encargar un trabajo")
    copias = pesos("copias")
    assert copias["copi"] == 1.0
    assert copias["backup"] == PESO_SINONIMO

    color = pesos("colorimetría")
    assert color["toma"] == PESO_SINONIMO
    assert color["color"] == PESO_SINONIMO
    assert pesos("color dental")["toma"] == PESO_SINONIMO
    assert pesos("tono")["color"] == PESO_SINONIMO

    factura = pesos("facturar con afip")
    assert factura["factur"] == 1.0
    assert factura["comprobant"] == PESO_SINONIMO
    assert pesos("facturación")["factur"] == PESO_SINONIMO
    assert "cae" not in factura


def test_agregar_un_cliente_no_se_reescribe():
    from rag.sinonimos import expandir

    pesos = dict(expandir(tokenize("agregar un cliente")))
    assert pesos == {"agreg": 1.0, "client": 1.0}


def test_texto_lexico_saca_la_cabecera_y_suma_la_seccion():
    from rag.hybrid import texto_lexico

    texto = "STELLA › Manual STELLA › Clientes\n\nAgregar un cliente nuevo."
    salida = texto_lexico(texto, "Manual STELLA › Clientes")
    assert salida.startswith("Manual STELLA › Clientes\n")
    assert "STELLA › Manual STELLA" not in salida
    assert "Agregar un cliente nuevo." in salida
    assert texto_lexico(texto) == "Agregar un cliente nuevo."


def test_es_glosario_mira_la_seccion():
    from rag.hybrid import _es_glosario

    assert _es_glosario({"seccion": "Laboratorio RioDent › Glosario › Cadetería"})
    assert not _es_glosario(
        {"seccion": "Laboratorio RioDent › Preguntas frecuentes › ¿Hacen envíos?"}
    )


def test_glosario_peso_default_y_validacion(monkeypatch):
    from rag.config import glosario_peso

    monkeypatch.delenv("GLOSARIO_PESO", raising=False)
    assert glosario_peso() == 0.5
    monkeypatch.setenv("GLOSARIO_PESO", "0.8")
    assert glosario_peso() == 0.8
    for malo in ("", "abc", "-0.1", "1.1"):
        monkeypatch.setenv("GLOSARIO_PESO", malo)
        assert glosario_peso() == 0.5
    monkeypatch.setenv("GLOSARIO_PESO", "1")
    assert glosario_peso() == 1.0


def test_peso_glosario_demota_solo_el_glosario(monkeypatch):
    import numpy as np

    from rag.hybrid import HybridRetriever

    monkeypatch.setenv("GLOSARIO_PESO", "0.5")
    retriever = HybridRetriever.__new__(HybridRetriever)
    retriever._glosario_idx = [0]
    salida = retriever._peso_glosario(np.array([1.0, 1.0], dtype=np.float32))
    assert salida.tolist() == [0.5, 1.0]
    monkeypatch.setenv("GLOSARIO_PESO", "1")
    salida = retriever._peso_glosario(np.array([1.0, 1.0], dtype=np.float32))
    assert salida.tolist() == [1.0, 1.0]


def test_search_real_agrega_snippet(monkeypatch):
    monkeypatch.setenv("RAG_DENSE", "0")
    if not INDEX_PATH.exists():
        pytest.skip("índice no generado")
    rag_service.set_retriever(HybridRetriever())
    try:
        hits = rag_service.search("¿cómo cargo un cliente nuevo?", 3)
    finally:
        rag_service.set_retriever(None)
    assert hits
    assert "cliente" in hits[0]["snippet"]
    assert "STELLA" in hits[0]["citation"]


def _indice_y_chunks(tmp_path, dims: int):
    import faiss
    import numpy as np

    fila = {
        "chunk_id": "stella:p1:0",
        "doc_id": "stella",
        "title": "STELLA",
        "page": 1,
        "text": "agregar un cliente nuevo en el laboratorio",
        "proyecto": "stella",
        "proyecto_nombre": "STELLA",
        "seccion": "Clientes",
        "publico": True,
        "tipo": "manual",
    }
    chunks = tmp_path / "chunks.jsonl"
    chunks.write_text(json.dumps(fila, ensure_ascii=False) + "\n",
                      encoding="utf-8")
    index = faiss.IndexFlatIP(dims)
    vector = np.ones((1, dims), dtype=np.float32)
    index.add(vector / np.linalg.norm(vector))
    index_path = tmp_path / "index.faiss"
    faiss.write_index(index, str(index_path))
    return chunks, index_path


def test_search_hibrida_con_embedder_de_1024(monkeypatch, tmp_path):
    import numpy as np

    monkeypatch.setenv("EMBEDDINGS_PROVIDER", "cloudflare")
    chunks, index_path = _indice_y_chunks(tmp_path, 1024)

    class Fake1024:
        def embed_consulta(self, _texto):
            vector = np.ones((1, 1024), dtype=np.float32)
            return vector / np.linalg.norm(vector)

    retriever = HybridRetriever(chunks, index_path, embedder=Fake1024())
    hits = retriever.search("agregar un cliente nuevo", 3, proyecto="stella")
    assert hits
    assert hits[0]["engine"] == "hibrida"


def test_dimension_distinta_cae_a_bm25(monkeypatch, tmp_path):
    import numpy as np

    monkeypatch.setenv("EMBEDDINGS_PROVIDER", "cloudflare")
    chunks, index_path = _indice_y_chunks(tmp_path, 1024)

    class Fake768:
        def embed_consulta(self, _texto):
            vector = np.ones((1, 768), dtype=np.float32)
            return vector / np.linalg.norm(vector)

    retriever = HybridRetriever(chunks, index_path, embedder=Fake768())
    hits = retriever.search("agregar un cliente nuevo", 3, proyecto="stella")
    assert hits
    assert hits[0]["engine"] == "bm25"
    assert retriever._dense_error == "dimension"


def test_filtra_por_proyecto_sin_detectar(monkeypatch, tmp_path):
    """El metadato se aplica antes de rankear y ya no se adivina del texto."""
    import faiss
    import numpy as np

    monkeypatch.setenv("RAG_DENSE", "0")
    texto = "alta de un cliente nuevo en el laboratorio con lista de precios"
    filas = []
    for proyecto, nombre in (("stella", "STELLA"), ("cars", "SolutionsCars")):
        filas.append({
            "chunk_id": f"{proyecto}:p1:0",
            "doc_id": proyecto,
            "title": nombre,
            "page": 1,
            "text": texto,
            "proyecto": proyecto,
            "proyecto_nombre": nombre,
            "seccion": "Clientes",
            "publico": proyecto == "stella",
            "tipo": "ficha",
        })
    path = tmp_path / "chunks.jsonl"
    path.write_text(
        "\n".join(json.dumps(f, ensure_ascii=False) for f in filas) + "\n",
        encoding="utf-8",
    )
    index = faiss.IndexFlatIP(4)
    index.add(np.ones((2, 4), dtype=np.float32))
    faiss.write_index(index, str(tmp_path / "index.faiss"))
    retriever = HybridRetriever(path, tmp_path / "index.faiss")
    solo = retriever.search("agregar un cliente nuevo", 5, proyecto="stella")
    assert solo and {h["proyecto"] for h in solo} == {"stella"}
    # Sin proyecto la máscara deja todo el corpus (ya no se adivina del texto).
    assert retriever._mascara(None).all()
    assert list(retriever._mascara("stella")) == [True, False]
    # bm25 (sin gate) ve ambos; nombrar STELLA en la pregunta no recorta.
    ambos = retriever.bm25("agregar un cliente nuevo en STELLA", 5)
    assert {h["proyecto"] for h in ambos} == {"stella", "cars"}
    cita = rag_service.enrich(solo, "cliente")[0]
    assert cita["url"] is None
    assert cita["citation"] == "STELLA · Clientes (pág. 1)"


def test_proyecto_elegido_nunca_devuelve_otro(monkeypatch):
    """Con el índice real, el filtro se aplica antes de rankear."""
    monkeypatch.setenv("RAG_DENSE", "0")
    retriever = _retriever()
    for proyecto, consulta in (
        ("stella", "¿cómo agrego un cliente nuevo?"),
        ("solutionscars", "¿cómo agrego un cliente nuevo?"),
        ("laboratorio-riodent", "¿cómo pido la toma de color?"),
        ("portafolio-web", "¿qué proyectos hiciste?"),
    ):
        hits = retriever.search(consulta, 5, proyecto=proyecto)
        assert all(h["proyecto"] == proyecto for h in hits), proyecto


def test_gate_sigue_activo_con_filtro(monkeypatch, tmp_path):
    """Un término del otro proyecto no abre el gate del proyecto elegido."""
    import faiss
    import numpy as np

    monkeypatch.setenv("RAG_DENSE", "0")
    filas = [
        {
            "chunk_id": "stella:p1:0",
            "doc_id": "stella",
            "title": "STELLA",
            "page": 1,
            "text": "alta de un cliente y facturación",
            "proyecto": "stella",
            "proyecto_nombre": "STELLA",
            "seccion": "Clientes",
            "publico": True,
            "tipo": "manual",
        },
        {
            "chunk_id": "cars:p1:0",
            "doc_id": "cars",
            "title": "SolutionsCars",
            "page": 1,
            "text": "cambiar bujías del carburador",
            "proyecto": "cars",
            "proyecto_nombre": "SolutionsCars",
            "seccion": "Taller",
            "publico": True,
            "tipo": "manual",
        },
    ]
    path = tmp_path / "chunks.jsonl"
    path.write_text(
        "\n".join(json.dumps(f, ensure_ascii=False) for f in filas) + "\n",
        encoding="utf-8",
    )
    index = faiss.IndexFlatIP(4)
    index.add(np.ones((2, 4), dtype=np.float32))
    faiss.write_index(index, str(tmp_path / "index.faiss"))
    retriever = HybridRetriever(path, tmp_path / "index.faiss")

    assert retriever.search(
        "cambiar bujías del carburador", 5, proyecto="stella",
    ) == []
    hits = retriever.search(
        "cambiar bujías del carburador", 5, proyecto="cars",
    )
    assert hits and {h["proyecto"] for h in hits} == {"cars"}
