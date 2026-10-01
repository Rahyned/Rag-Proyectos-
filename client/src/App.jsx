import { useEffect, useRef, useState } from 'react'
import { streamChat } from './lib/api'

const EJEMPLOS = [
  '¿Cómo agrego un cliente nuevo?',
  '¿Cómo restauro un backup?',
  '¿Cuánto es el descuento de clientes?',
]

let nextId = 1

export default function App() {
  const [mode, setMode] = useState('fragmentos')
  const [input, setInput] = useState('')
  const [busy, setBusy] = useState(false)
  const [messages, setMessages] = useState([])
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function send(query) {
    const text = query.trim()
    if (!text || busy) return
    const botId = nextId++
    setMessages((ms) => [
      ...ms,
      { id: nextId++, role: 'user', text },
      { id: botId, role: 'assistant', text: '', hits: [], fallback: null, pending: true },
    ])
    setInput('')
    setBusy(true)
    const patch = (fn) =>
      setMessages((ms) => ms.map((m) => (m.id === botId ? fn(m) : m)))
    try {
      await streamChat({
        query: text,
        mode,
        onSources: (hits) => patch((m) => ({ ...m, hits })),
        onText: (delta) => patch((m) => ({ ...m, text: m.text + delta })),
        onFallback: (reason) => patch((m) => ({ ...m, fallback: reason })),
        onDone: () => patch((m) => ({ ...m, pending: false })),
      })
      patch((m) => ({ ...m, pending: false }))
    } catch (err) {
      patch((m) => ({ ...m, pending: false, error: err.message }))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>Asistente del Manual STELLA</h1>
          <p className="sub">Consultá el manual de gestión para laboratorios dentales</p>
        </div>
        <div className="modes" role="radiogroup" aria-label="Modo de respuesta">
          {[
            ['fragmentos', 'Fragmentos'],
            ['sintetica', 'Respuesta sintética'],
          ].map(([value, label]) => (
            <button
              key={value}
              type="button"
              role="radio"
              aria-checked={mode === value}
              className={mode === value ? 'mode on' : 'mode'}
              onClick={() => setMode(value)}
            >
              {label}
            </button>
          ))}
        </div>
      </header>

      <section className="chat">
        {messages.length === 0 && (
          <div className="empty">
            <p>Hacé una pregunta sobre el manual. Cada respuesta cita la página exacta del PDF.</p>
            <div className="chips">
              {EJEMPLOS.map((q) => (
                <button key={q} type="button" className="chip" onClick={() => send(q)}>
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m) =>
          m.role === 'user' ? (
            <div key={m.id} className="msg user">
              {m.text}
            </div>
          ) : (
            <div key={m.id} className="msg bot">
              {m.fallback && (
                <p className="notice">
                  Respuesta sintética no disponible (sin LLM configurado); te dejo los
                  fragmentos del manual.
                </p>
              )}
              {m.text && <p className="answer">{m.text}</p>}
              {m.error && <p className="error">{m.error}</p>}
              {m.pending && !m.text && !m.error && <p className="pending">Buscando en el manual…</p>}

              {m.hits.length > 0 && (
                <ul className="sources">
                  {m.hits.map((h) => (
                    <li key={h.chunk_id}>
                      <a
                        className="cite"
                        href={`${import.meta.env.BASE_URL}corpus/${h.doc_id}.pdf#page=${h.page}`}
                        target="_blank"
                        rel="noreferrer"
                      >
                        {h.citation}
                      </a>
                      <span className="snippet">
                        {h.text.length > 220 ? `${h.text.slice(0, 220).trim()}…` : h.text}
                      </span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          ),
        )}
        <div ref={bottomRef} />
      </section>

      <footer>
        <form onSubmit={(e) => { e.preventDefault(); send(input) }}>
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ej.: ¿cómo cargo un trabajo nuevo?"
            maxLength={500}
            aria-label="Tu pregunta"
          />
          <button type="submit" disabled={busy || !input.trim()}>
            {busy ? '…' : 'Consultar'}
          </button>
        </form>
      </footer>
    </div>
  )
}
