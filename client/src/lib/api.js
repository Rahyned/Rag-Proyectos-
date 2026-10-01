export async function streamChat({ query, mode, onSources, onText, onFallback, onDone }) {
  const resp = await fetch(`${import.meta.env.BASE_URL}api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, mode }),
  })
  if (!resp.ok) {
    let detail = `API ${resp.status}`
    try {
      const body = await resp.json()
      if (body.detail) detail = body.detail
    } catch {
      /* respuesta sin JSON */
    }
    throw new Error(detail)
  }

  const reader = resp.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  const dispatch = (line) => {
    if (!line.startsWith('data: ')) return
    const evt = JSON.parse(line.slice(6))
    if (evt.type === 'sources') onSources(evt.hits)
    else if (evt.type === 'text') onText(evt.delta)
    else if (evt.type === 'fallback') onFallback(evt.reason)
    else if (evt.type === 'done') onDone(evt.mode)
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
}
