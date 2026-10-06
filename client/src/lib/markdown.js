const ESCAPES = {
  '&': '&amp;',
  '<': '&lt;',
  '>': '&gt;',
  '"': '&quot;',
}

export function escapeHtml(text) {
  return String(text).replace(/[&<>"]/g, (ch) => ESCAPES[ch])
}

function inline(escaped) {
  let html = escaped.replace(/`([^`]+)`/g, '<code>$1</code>')
  html = html.replace(
    /\[([^\]]+)\]\((https?:\/\/[^\s)]+|\/(?!\/)[^\s)]+)\)/g,
    (_, text, url) => `<a href="${url}" target="_blank" rel="noreferrer">${text}</a>`,
  )
  html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
  html = html.replace(/(^|[^*])\*([^*\n]+)\*/g, '$1<em>$2</em>')
  return html
}

/** Markdown mínimo. El HTML crudo queda escapado: no hay script ni atributos. */
export function renderMarkdown(source) {
  const escaped = escapeHtml(source ?? '')
  const lines = escaped.split('\n')
  const blocks = []
  let list = []
  let para = []

  const flushPara = () => {
    if (!para.length) return
    blocks.push(`<p>${inline(para.join(' '))}</p>`)
    para = []
  }
  const flushList = () => {
    if (!list.length) return
    const items = list.map((item) => `<li>${inline(item)}</li>`).join('')
    blocks.push(`<ul>${items}</ul>`)
    list = []
  }

  for (const line of lines) {
    const item = /^- (.+)$/.exec(line)
    if (item) {
      flushPara()
      list.push(item[1])
      continue
    }
    flushList()
    if (!line.trim()) {
      flushPara()
      continue
    }
    para.push(line.trim())
  }
  flushList()
  flushPara()
  return blocks.join('')
}
