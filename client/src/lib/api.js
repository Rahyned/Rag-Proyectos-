export async function streamChat({
  query,
  mode,
  signal,
  onSources,
  onText,
  onFallback,
  onDone,
}) {
  const resp = await fetch(`${import.meta.env.BASE_URL}api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, mode }),
    signal,
  })
  if (!resp.ok) {
    let detail = `API ${resp.status}`
    try {
      const body = await resp.json()
      const d = body.detail
      if (typeof d === 'string') detail = d
      else if (Array.isArray(d) && d[0]?.msg) detail = d[0].msg
    } catch {
      /* respuesta sin JSON */
    }
    throw new Error(detail)
  }

  const reader = resp.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  let sawDone = false
  const dispatch = (line) => {
    if (!line.startsWith('data: ')) return
    let evt
    try {
      evt = JSON.parse(line.slice(6))
    } catch {
      return /* línea SSE malformada: no tirar abajo todo el stream */
    }
    if (evt.type === 'sources') onSources(evt.hits)
    else if (evt.type === 'text') onText(evt.delta)
    else if (evt.type === 'fallback') onFallback(evt.reason)
    else if (evt.type === 'done') {
      sawDone = true
      onDone(evt.mode)
    }
  }

  for (;;) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    let idx
    while ((idx = buffer.indexOf('\n\n')) !== -1) {
      const block = buffer.slice(0, idx)
      buffer = buffer.slice(idx + 2)
      block.split('\n').forEach(dispatch)
    }
  }
  if (!sawDone) {
    throw new Error('La conexión se interrumpió: la respuesta quedó incompleta.')
  }
}
