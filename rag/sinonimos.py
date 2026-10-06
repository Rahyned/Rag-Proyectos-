"""Sinónimos del dominio (ES) para expandir la consulta después de tokenize().

Los términos coloquiales ("dentista", "cobrarle", "copia de seguridad") no
están en el manual con esa forma. Cada regla dispara aportes con peso menor
que el término original (ver PESO_SINONIMO en el BM25). Las flechas → son de
un solo sentido para no alterar consultas que ya usan el vocabulario del
manual ("agregar un cliente" no se reescribe).
"""

from __future__ import annotations

# Peso relativo al idf del término original. 1.0 queda reservado al token
# que escribió el usuario.
PESO_SINONIMO = 0.5

# (disparadores, aportes). Frases en español; se tokenizan igual que la query.
# Un disparador de varias palabras tiene que aparecer seguido (ya sin stopwords).
_REGLAS_CRUDAS: tuple[tuple[tuple[str, ...], tuple[str, ...]], ...] = (
    (("dentista",), ("odontólogo",)),
    (
        ("backup", "respaldo", "copia de seguridad"),
        ("backup", "respaldo", "copia de seguridad"),
    ),
    (("cobrar",), ("cobro", "pago", "saldo")),
    (("dar de alta",), ("agregar", "crear")),
    (("contraseña", "clave"), ("contraseña", "clave")),
    (("borrar", "eliminar"), ("borrar", "eliminar")),
    (("factura", "comprobante"), ("factura", "comprobante")),
)

# Tokens de expansión más cortos que esto no aportan (el stem de "crear" cae
# en "cre") y pueden pisar el idf de otra página.
_MIN_TOKEN = 4

_reglas_tok: list[tuple[list[tuple[str, ...]], list[tuple[str, ...]]]] | None = None


def _reglas():
    """Reglas tokenizadas, lazy: evita import circular con rag.hybrid."""
    global _reglas_tok
    if _reglas_tok is None:
        from rag.hybrid import tokenize

        cargadas = []
        for disparadores, aportes in _REGLAS_CRUDAS:
            cargadas.append((
                [tuple(tokenize(frase)) for frase in disparadores],
                [tuple(tokenize(frase)) for frase in aportes],
            ))
        _reglas_tok = cargadas
    return _reglas_tok


def _claves(token: str) -> set[str]:
    """Formas para buscar un disparador.

    tokenize() se come la vocal de un clítico ("cobrarle" → "cobrarl") y la
    regla vive en el infinitivo ("cobrar" → "cobr"). Recuperamos esa base.
    """
    claves = {token}
    if len(token) >= 6 and token[-1] in "lns":
        from rag.hybrid import _stem

        base = token[:-1]
        claves.add(base)
        claves.add(_stem(base))
    return claves


def _aparece(frase: tuple[str, ...], tokens: list[str]) -> bool:
    if not frase:
        return False
    if len(frase) == 1:
        objetivo = frase[0]
        return any(objetivo in _claves(t) for t in tokens)
    n = len(frase)
    return any(tuple(tokens[i:i + n]) == frase for i in range(len(tokens) - n + 1))


def expandir(tokens: list[str]) -> list[tuple[str, float]]:
    """Tokens de la query con peso 1.0 y sinónimos disparados con peso menor.

    El orden original no se toca: el bonus de bigrama sigue mirando solo lo
    que escribió el usuario.
    """
    pesos: dict[str, float] = {t: 1.0 for t in tokens}
    for disparadores, aportes in _reglas():
        if not any(_aparece(frase, tokens) for frase in disparadores):
            continue
        for frase in aportes:
            for tok in frase:
                if len(tok) >= _MIN_TOKEN:
                    pesos.setdefault(tok, PESO_SINONIMO)
    return list(pesos.items())
