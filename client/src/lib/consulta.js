/** ¿Se puede enviar la pregunta con el selector actual? */
export function puedeConsultar(proyecto, texto, busy = false) {
  return Boolean(proyecto && String(texto).trim() && !busy)
}

/**
 * Aplica la elección del selector. Ignora el placeholder vacío.
 * @returns {{ proyecto: string, listo: boolean }}
 */
export function elegirProyecto(proyectoId, texto = '', busy = false) {
  const proyecto = proyectoId && proyectoId !== 'todos' ? String(proyectoId) : ''
  return {
    proyecto,
    listo: puedeConsultar(proyecto, texto, busy),
  }
}
