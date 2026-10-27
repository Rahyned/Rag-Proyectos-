/** ¿Se puede enviar la pregunta con el selector actual? */
export function puedeConsultar(proyecto, texto, busy = false) {
  return Boolean(proyecto && String(texto).trim() && !busy)
}
