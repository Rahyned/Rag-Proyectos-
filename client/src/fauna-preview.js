import { paintPreview } from './lib/fondo-ascii.js'

const engines = [
  paintPreview(document.getElementById('still'), { moving: false }),
  paintPreview(document.getElementById('move'), { moving: true }),
]

window.addEventListener('beforeunload', () => {
  for (const e of engines) e?.destroy()
})
