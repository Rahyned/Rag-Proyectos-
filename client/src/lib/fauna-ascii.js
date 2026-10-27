/**
 * Fondos ASCII de fauna de la costa argentina (canvas, sin dependencias).
 * Frames en grises; la UI va encima con vidrio / halo.
 */

export const FPS = 30
export const FRAME_MS = 1000 / FPS

/** Formas por especie: cada frame es un array de líneas ASCII. */
export const SPECIES = {
  ballena: {
    tint: 'rgba(90, 110, 140, 0.55)',
    frames: [
      [
        '            .--.              ',
        '      .----\'    `----.        ',
        '   .-\'   @@######@@   `-.     ',
        '  /   @@@@##########@@@@  \\   ',
        ' (  @@@@@############@@@@@ )  ',
        '  \\@@@@@##############@@@@@/  ',
        '   `@@@@@############@@@@@\'   ',
        '     `@@@@########@@@@\'  ~~   ',
        '       `\'\'\'\'----\'\'\'\'          ',
      ],
      [
        '             .--.             ',
        '       .----\'    `----.       ',
        '    .-\'   @@######@@   `-.    ',
        '   /   @@@@##########@@@@  \\  ',
        '  (  @@@@@############@@@@@ ) ',
        '   \\@@@@@##############@@@@@/ ',
        '    `@@@@@############@@@@@\'  ',
        '  ~~  `@@@@########@@@@\'      ',
        '        `\'\'\'\'----\'\'\'\'         ',
      ],
    ],
  },
  lobo: {
    tint: 'rgba(120, 100, 80, 0.5)',
    frames: [
      [
        '      .-.                     ',
        '     (o o)   __               ',
        '      \\_/  _/@@\\_             ',
        '       |  /@@@@@@\\            ',
        '       |_/@@@@@@@@\\___        ',
        '         \\@@@@@@@@@@@/        ',
        '          \\@@@@@@@@@/         ',
        '           `--.__.--\'         ',
      ],
      [
        '       .-.                    ',
        '      (o o)  __               ',
        '       \\_/ _/@@\\_             ',
        '        | /@@@@@@\\            ',
        '      __|_/@@@@@@@@\\___       ',
        '         \\@@@@@@@@@@@/        ',
        '          \\@@@@@@@@@/         ',
        '           `--.__.--\'         ',
      ],
    ],
  },
  pinguino: {
    tint: 'rgba(70, 90, 120, 0.55)',
    frames: [
      [
        '      .--.                    ',
        '     /@@@@\\                   ',
        '    |@o  o@|                  ',
        '    |@@@@@@|                  ',
        '    |@::::@|                  ',
        '    |@@@@@@|                  ',
        '     \\@@@@/                   ',
        '      |  |                    ',
        '     /_  _\\                   ',
      ],
      [
        '      .--.                    ',
        '     /@@@@\\                   ',
        '    |@o  o@|                  ',
        '    |@@@@@@|                  ',
        '    |@::::@|                  ',
        '    |@@@@@@|                  ',
        '     \\@@@@/                   ',
        '      |  |                    ',
        '      /_  _\\                  ',
      ],
    ],
  },
  tonina: {
    tint: 'rgba(80, 80, 90, 0.55)',
    frames: [
      [
        '         .                      ',
        '    .---\' \\                     ',
        '   / ##@@  \\__.                 ',
        '  <  #####@@@@ `-.              ',
        '   \\ ##@@....@@@@/              ',
        '    `\'\'\'\'\'----\'\'\'               ',
      ],
      [
        '          .                     ',
        '     .---\' \\                    ',
        '    / ##@@  \\__.                ',
        '   <  #####@@@@ `-.             ',
        '    \\ ##@@....@@@@/             ',
        '     `\'\'\'\'\'----\'\'\'              ',
      ],
    ],
  },
}

const SPECIES_IDS = Object.keys(SPECIES)

export function prefersReducedMotion(matchMedia = globalThis.matchMedia) {
  if (typeof matchMedia !== 'function') return false
  try {
    return Boolean(matchMedia('(prefers-reduced-motion: reduce)').matches)
  } catch {
    return false
  }
}

/** Cuántos animales dibujar según viewport y a11y. */
export function animalCount({ width = 1024, reducedMotion = false } = {}) {
  if (reducedMotion) return 2
  if (width < 640) return 3
  if (width < 1024) return 5
  return 7
}

function mulberry32(seed) {
  let t = seed >>> 0
  return () => {
    t += 0x6d2b79f5
    let r = Math.imul(t ^ (t >>> 15), 1 | t)
    r ^= r + Math.imul(r ^ (r >>> 7), 61 | r)
    return ((r ^ (r >>> 14)) >>> 0) / 4294967296
  }
}

function spawnAnimal(rand, width, height, index) {
  const id = SPECIES_IDS[index % SPECIES_IDS.length]
  const dir = rand() < 0.5 ? 1 : -1
  const speed = 12 + rand() * 28
  const scale = 0.7 + rand() * 0.7
  const y = 40 + rand() * Math.max(80, height - 120)
  const x = dir > 0 ? -180 - rand() * 200 : width + 40 + rand() * 200
  return {
    id,
    dir,
    speed,
    scale,
    x,
    y,
    frame: 0,
    frameAcc: rand() * 400,
    opacity: 0.35 + rand() * 0.35,
  }
}

function drawGrid(ctx, width, height) {
  ctx.save()
  ctx.strokeStyle = 'rgba(180, 185, 200, 0.28)'
  ctx.lineWidth = 1
  const step = 28
  for (let x = 0; x <= width; x += step) {
    ctx.beginPath()
    ctx.moveTo(x + 0.5, 0)
    ctx.lineTo(x + 0.5, height)
    ctx.stroke()
  }
  for (let y = 0; y <= height; y += step) {
    ctx.beginPath()
    ctx.moveTo(0, y + 0.5)
    ctx.lineTo(width, y + 0.5)
    ctx.stroke()
  }
  ctx.restore()
}

function drawAnimal(ctx, animal) {
  const spec = SPECIES[animal.id]
  const frames = spec.frames
  const lines = frames[animal.frame % frames.length]
  const fontSize = Math.round(11 * animal.scale)
  ctx.save()
  ctx.font = `${fontSize}px ui-monospace, Consolas, monospace`
  ctx.textBaseline = 'top'
  ctx.fillStyle = spec.tint.replace(/[\d.]+\)$/, `${animal.opacity})`)
  const lineH = fontSize * 1.05
  const maxW = Math.max(...lines.map((l) => l.length)) * fontSize * 0.6
  ctx.translate(animal.x, animal.y)
  if (animal.dir < 0) {
    ctx.scale(-1, 1)
    ctx.translate(-maxW, 0)
  }
  for (let i = 0; i < lines.length; i++) {
    ctx.fillText(lines[i], 0, i * lineH)
  }
  ctx.restore()
}

/**
 * Monta el loop sobre un <canvas>. Devuelve { destroy }.
 * @param {HTMLCanvasElement} canvas
 * @param {{ dimmed?: () => boolean, seed?: number }} [opts]
 */
export function mountFauna(canvas, opts = {}) {
  const ctx = canvas.getContext('2d')
  if (!ctx) return { destroy() {} }

  const rand = mulberry32(opts.seed ?? 20261027)
  let animals = []
  let raf = 0
  let last = 0
  let acc = 0
  let reduced = prefersReducedMotion()
  let running = true

  const mq = typeof matchMedia === 'function'
    ? matchMedia('(prefers-reduced-motion: reduce)')
    : null

  const onMotion = () => {
    reduced = prefersReducedMotion()
    resize()
  }
  mq?.addEventListener?.('change', onMotion)

  const onVis = () => {
    if (document.hidden) {
      running = false
      cancelAnimationFrame(raf)
      raf = 0
    } else {
      running = true
      last = performance.now()
      raf = requestAnimationFrame(tick)
    }
  }
  document.addEventListener('visibilitychange', onVis)

  function resize() {
    const dpr = Math.min(window.devicePixelRatio || 1, 2)
    const w = window.innerWidth
    const h = window.innerHeight
    canvas.width = Math.floor(w * dpr)
    canvas.height = Math.floor(h * dpr)
    canvas.style.width = `${w}px`
    canvas.style.height = `${h}px`
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
    const n = animalCount({ width: w, reducedMotion: reduced })
    animals = Array.from({ length: n }, (_, i) => spawnAnimal(rand, w, h, i))
    paint(0)
  }

  function paint(dt) {
    const w = window.innerWidth
    const h = window.innerHeight
    const dimmed = opts.dimmed?.() ?? false
    ctx.clearRect(0, 0, w, h)
    ctx.fillStyle = dimmed ? '#eef0f6' : '#f4f5fa'
    ctx.fillRect(0, 0, w, h)
    drawGrid(ctx, w, h)
    ctx.globalAlpha = dimmed ? 0.35 : 0.85
    for (const a of animals) {
      if (!reduced) {
        a.x += a.dir * a.speed * (dt / 1000)
        a.frameAcc += dt
        if (a.frameAcc > 380) {
          a.frameAcc = 0
          a.frame = (a.frame + 1) % SPECIES[a.id].frames.length
        }
        const maxW = 220 * a.scale
        if (a.dir > 0 && a.x > w + 40) a.x = -maxW - 40
        if (a.dir < 0 && a.x < -maxW - 40) a.x = w + 40
      }
      drawAnimal(ctx, a)
    }
    ctx.globalAlpha = 1
  }

  function tick(now) {
    if (!running) return
    if (!last) last = now
    const raw = now - last
    last = now
    acc += raw
    if (acc >= FRAME_MS) {
      const dt = Math.min(acc, FRAME_MS * 2)
      acc = 0
      paint(reduced ? 0 : dt)
    }
    raf = requestAnimationFrame(tick)
  }

  window.addEventListener('resize', resize)
  resize()
  if (!document.hidden) {
    last = performance.now()
    raf = requestAnimationFrame(tick)
  }

  return {
    destroy() {
      running = false
      cancelAnimationFrame(raf)
      window.removeEventListener('resize', resize)
      document.removeEventListener('visibilitychange', onVis)
      mq?.removeEventListener?.('change', onMotion)
    },
  }
}
