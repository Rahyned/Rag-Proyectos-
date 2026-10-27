import { useEffect, useRef, useState } from 'react'
import FaunaBackground from './FaunaBackground'
import { fetchProyectos, streamChat } from './lib/api'
import { elegirProyecto, puedeConsultar } from './lib/consulta'
import { renderMarkdown } from './lib/markdown'

const EJEMPLOS = [
  '¿Cómo agrego un cliente nuevo?',
  '¿Cómo restauro un backup?',
  '¿Cuánto es el descuento de clientes?',
]

const FALLBACK_TEXT = {
  no_key: 'Respuesta sintética no disponible (sin LLM configurado); te dejo los fragmentos recuperados.',
  rate_limited: 'El modelo está saturado ahora; te dejo los fragmentos recuperados.',
  timeout: 'El modelo tardó demasiado; te dejo los fragmentos recuperados.',
  interrupted: 'La respuesta se cortó a mitad de camino; revisá los fragmentos recuperados.',
  upstream: 'Respuesta sintética no disponible por un problema del modelo; te dejo los fragmentos recuperados.',
  error: 'Hubo un error inesperado; te dejo los fragmentos recuperados.',
}

const REQUEST_TIMEOUT_MS = 60000

let nextId = 1

export default function App() {
  const [mode, setMode] = useState('sintetica')
  const [proyecto, setProyecto] = useState('')
  const [proyectos, setProyectos] = useState([])
  const [proyectosError, setProyectosError] = useState('')
  const [input, setInput] = useState('')
  const [busy, setBusy] = useState(false)
  const [messages, setMessages] = useState([])
  const [announce, setAnnounce] = useState('')
  const chatRef = useRef(null)
  const ctrlRef = useRef(null)

  function cargarProyectos() {
    setProyectosError('')
    fetchProyectos()
      .then((lista) => {
        setProyectos(lista)
        setProyectosError('')
      })
      .catch((err) => {
        setProyectos([])
        setProyecto('')
        setProyectosError(err.message || 'No se pudieron cargar los proyectos.')
      })
  }

  useEffect(() => {
    cargarProyectos()
  }, [])

  const actual = proyectos.find((p) => p.id === proyecto)
  const ejemplos = actual?.preguntas?.length ? actual.preguntas : EJEMPLOS
  const listo = puedeConsultar(proyecto, input, busy)
  const conversando = messages.length > 0

  useEffect(() => {
    const el = chatRef.current
    if (!el) return
    const dist = el.scrollHeight - el.scrollTop - el.clientHeight
    if (dist < 80) el.scrollTop = el.scrollHeight
  }, [messages])

  async function send(query) {
    const text = query.trim()
    if (!puedeConsultar(proyecto, text, busy)) return
    const botId = nextId++
    setMessages((ms) => [
      ...ms,
      { id: nextId++, role: 'user', text },
      { id: botId, role: 'assistant', text: '', hits: [], fallback: null, pending: true },
    ])
    setInput('')
    setBusy(true)
    setAnnounce('')
    const patch = (fn) =>
      setMessages((ms) => ms.map((m) => (m.id === botId ? fn(m) : m)))

    const ctrl = new AbortController()
    ctrlRef.current = ctrl
    let timedOut = false
    const timer = setTimeout(() => {
      timedOut = true
      ctrl.abort()
    }, REQUEST_TIMEOUT_MS)
    let finalText = ''
    try {
      await streamChat({
        query: text,
        mode,
        proyecto,
        signal: ctrl.signal,
        onSources: (hits) => patch((m) => ({ ...m, hits })),
        onText: (delta) => {
          finalText += delta
          patch((m) => ({ ...m, text: m.text + delta }))
        },
        onFallback: (reason) => patch((m) => ({ ...m, fallback: reason })),
        onDone: () => patch((m) => ({ ...m, pending: false })),
      })
      patch((m) => ({ ...m, pending: false }))
      if (finalText) setAnnounce(finalText)
    } catch (err) {
      const msg = timedOut
        ? 'El modelo tardó demasiado en responder: se cortó la consulta.'
        : err.name === 'AbortError'
          ? 'Consulta cancelada.'
          : err.message || 'Error inesperado.'
      patch((m) => ({ ...m, pending: false, error: msg }))
    } finally {
      clearTimeout(timer)
      ctrlRef.current = null
      setBusy(false)
    }
  }

  return (
    <div className={`shell ${conversando ? 'shell-chat' : 'shell-hero'}`}>
      <FaunaBackground dimmed={conversando} animate />

      <div className="hoja">
        <header className="hoja-head halo-title">
          <h1>¿Qué querés saber?</h1>
          <p className="sub">
            {actual
              ? actual.descripcion
              : 'Elegí un proyecto y hacé tu pregunta. Cada cita indica el documento y la sección.'}
          </p>
        </header>

        <div
          className="modes"
          role="radiogroup"
          aria-label="Modo de respuesta"
          onKeyDown={(e) => {
            if (e.key !== 'ArrowLeft' && e.key !== 'ArrowRight') return
            e.preventDefault()
            setMode((m) => (m === 'sintetica' ? 'fragmentos' : 'sintetica'))
          }}
        >
          {[
            ['sintetica', 'Respuesta sintética'],
            ['fragmentos', 'Fragmentos'],
          ].map(([value, label]) => (
            <button
              key={value}
              type="button"
              role="radio"
              aria-checked={mode === value}
              tabIndex={mode === value ? 0 : -1}
              className={mode === value ? 'mode on' : 'mode'}
              onClick={() => setMode(value)}
            >
              {label}
            </button>
          ))}
        </div>

        <div className="proyecto">
          <label htmlFor="proyecto">Proyecto</label>
          <select
            id="proyecto"
            value={proyecto}
            disabled={proyectos.length === 0}
            onChange={(e) => {
              const next = elegirProyecto(e.target.value, input, busy)
              setProyecto(next.proyecto)
            }}
            required
          >
            <option value="">
              {proyectos.length === 0 ? 'Cargando proyectos…' : 'Elegí un proyecto…'}
            </option>
            {proyectos.map((p) => (
              <option key={p.id} value={p.id}>{p.nombre}</option>
            ))}
          </select>
          {proyectosError ? (
            <p className="aviso-proyecto" role="alert">
              {proyectosError}{' '}
              <button type="button" className="linkish" onClick={cargarProyectos}>
                Reintentar
              </button>
            </p>
          ) : !proyecto ? (
            <p className="aviso-proyecto" role="status">
              Elegí un proyecto para preguntar
            </p>
          ) : null}
        </div>

        <div className="chips">
          {ejemplos.map((q) => (
            <button
              key={q}
              type="button"
              className="chip"
              disabled={!proyecto || busy}
              onClick={() => send(q)}
            >
              {q}
            </button>
          ))}
        </div>

        {conversando && (
          <main className="chat" ref={chatRef}>
            <div className="sr-only" aria-live="polite">
              {announce}
            </div>
            {messages.map((m) =>
              m.role === 'user' ? (
                <div key={m.id} className="msg user">
                  {m.text}
                </div>
              ) : (
                <div key={m.id} className="msg bot">
                  {m.fallback && (
                    <p className="notice">
                      {FALLBACK_TEXT[m.fallback] ?? FALLBACK_TEXT.error}
                    </p>
                  )}
                  {m.text && (
                    <div
                      className="answer"
                      dangerouslySetInnerHTML={{ __html: renderMarkdown(m.text) }}
                    />
                  )}
                  {m.error && (
                    <p className="error" role="alert">
                      {m.error}
                    </p>
                  )}
                  {m.pending && !m.text && !m.error && (
                    <p className="pending" role="status">
                      Buscando…
                    </p>
                  )}
                  {!m.pending && !m.text && !m.error && !m.fallback && m.hits.length === 0 && (
                    <p className="notice">
                      No encontré información sobre esa pregunta. ¿Podés reformularla?
                    </p>
                  )}
                  {m.hits.length > 0 && (
                    <ul className="sources">
                      {m.hits.map((h) => (
                        <li key={h.chunk_id}>
                          {h.url ? (
                            <a
                              className="cite"
                              href={h.url.startsWith('http') ? h.url : `${import.meta.env.BASE_URL}${h.url}`}
                              target="_blank"
                              rel="noreferrer"
                            >
                              {h.citation}
                            </a>
                          ) : (
                            <span className="cite estatica">{h.citation}</span>
                          )}
                          <span className="snippet">
                            {h.snippet ?? h.text.slice(0, 220)}
                          </span>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              ),
            )}
          </main>
        )}

        <div className="composer-shell halo-input">
          <form
            className="composer"
            onSubmit={(e) => { e.preventDefault(); send(input) }}
          >
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ej.: ¿cómo cargo un trabajo nuevo?"
              minLength={2}
              maxLength={500}
              aria-label="Tu pregunta"
            />
            {busy ? (
              <button
                type="button"
                className="stop"
                onClick={() => ctrlRef.current?.abort()}
              >
                ■ Detener
              </button>
            ) : (
              <button type="submit" disabled={!listo}>
                Consultar
              </button>
            )}
          </form>
        </div>
      </div>
    </div>
  )
}
