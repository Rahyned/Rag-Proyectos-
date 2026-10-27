/**
 * Fondo océano + fauna ASCII (offscreen → muestreo a grilla → celdas).
 */

import {
  ANIMALS,
  ANIMAL_IDS,
  BALLENA_VARIANTES,
  RAMP,
  paintAnimal,
  variantById,
} from './fauna-ascii.js'

export const FPS = 30
export const FRAME_MS = 1000 / FPS
export const ALPHA_THRESHOLD = 24

export function prefersReducedMotion(matchMedia = globalThis.matchMedia) {
  if (typeof matchMedia !== 'function') return false
  try {
    return Boolean(matchMedia('(prefers-reduced-motion: reduce)').matches)
  } catch {
    return false
  }
}

export function cellSizeForWidth(width) {
  if (width < 640) return 16
  if (width < 1024) return 14
  return 12
}

export function animalBudget({ width = 1024, height = 720, reducedMotion = false } = {}) {
  if (reducedMotion) return 1
  // Menos ballenas si el viewport no da para mantener distancia.
  const area = width * height
  if (area < 500_000 || width < 640) return 2
  if (area < 900_000 || width < 1024) return 3
  return 4
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

function brightnessOf(r, g, b) {
  return (r * 0.299 + g * 0.587 + b * 0.114) / 255
}

function rampChar(brightness) {
  // Oscuro → carácter denso; claro → liviano.
  const t = 1 - brightness
  const idx = Math.min(RAMP.length - 1, Math.max(0, Math.round(t * (RAMP.length - 1))))
  return RAMP[idx]
}

/**
 * Rasteriza un actor a un buffer cols×rows (ImageData 1px/celda).
 * Posición decimal + ángulo + ondulación → sin saltos de celda.
 */
function sampleActor(off, sample, actor, cols, rows, cell, t, reduced) {
  const { width: ow, height: oh } = off.canvas
  const octx = off.ctx
  octx.setTransform(1, 0, 0, 1, 0, 0)
  octx.clearRect(0, 0, ow, oh)

  const wave = reduced ? 0 : t * 0.004 + actor.phase
  // Amp moderada: si es alta, la cola ondula fuera del offscreen y se corta.
  const amp = reduced ? 0 : 4.5 * actor.scale

  octx.save()
  octx.translate(ow / 2, oh / 2)
  // El rumbo es el ángulo de nado (vista dorsal); sin flip que invierta la física.
  octx.rotate(actor.angle)
  // Ligero offset hacia la cabeza: deja más margen a los flukes (cola).
  octx.scale(actor.scale, actor.scale)
  octx.translate(18, 0)
  paintAnimal(octx, actor.id, { wave, amp, variant: actor.variant })
  octx.restore()

  // Downsample a cols×rows vía drawImage en canvas 1:1 celdas.
  const sctx = sample.ctx
  sctx.setTransform(1, 0, 0, 1, 0, 0)
  sctx.clearRect(0, 0, cols, rows)

  // Posición del centro del animal en coords de pantalla → celdas.
  const cx = actor.x / cell
  const cy = actor.y / cell
  const srcW = ow
  const srcH = oh
  // El offscreen representa ~ length*scale px; mapeamos a celdas.
  const destW = (srcW / cell) * actor.worldScale
  const destH = (srcH / cell) * actor.worldScale
  sctx.drawImage(
    off.canvas,
    0, 0, srcW, srcH,
    cx - destW / 2, cy - destH / 2, destW, destH,
  )
  return sctx.getImageData(0, 0, cols, rows)
}

function paintOcean(ctx, cssW, cssH, t = 0, reduced = false) {
  // Agua clara tipo referencia: radial celeste, centro luminoso.
  const g = ctx.createRadialGradient(
    cssW * 0.5, cssH * 0.42, 40,
    cssW * 0.5, cssH * 0.5, Math.max(cssW, cssH) * 0.72,
  )
  g.addColorStop(0, '#e8f6fb')
  g.addColorStop(0.35, '#c5e8f2')
  g.addColorStop(0.7, '#9fd4e6')
  g.addColorStop(1, '#6eb8d0')
  ctx.fillStyle = g
  ctx.fillRect(0, 0, cssW, cssH)

  // Ondas muy tenues.
  ctx.save()
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.18)'
  ctx.lineWidth = 1
  for (let i = 0; i < 5; i++) {
    const y0 = cssH * (0.15 + i * 0.16)
    ctx.beginPath()
    for (let x = 0; x <= cssW; x += 8) {
      const y = y0 + Math.sin(x * 0.012 + t * 0.0004 + i) * (reduced ? 2 : 6)
      if (x === 0) ctx.moveTo(x, y)
      else ctx.lineTo(x, y)
    }
    ctx.stroke()
  }
  ctx.restore()

  // Grilla suave (como la referencia).
  const cell = cellSizeForWidth(cssW)
  ctx.strokeStyle = 'rgba(80, 140, 170, 0.07)'
  ctx.lineWidth = 1
  for (let x = 0; x <= cssW; x += cell) {
    ctx.beginPath()
    ctx.moveTo(x + 0.5, 0)
    ctx.lineTo(x + 0.5, cssH)
    ctx.stroke()
  }
  for (let y = 0; y <= cssH; y += cell) {
    ctx.beginPath()
    ctx.moveTo(0, y + 0.5)
    ctx.lineTo(cssW, y + 0.5)
    ctx.stroke()
  }

  // Partículas / espuma a la deriva.
  const driftN = reduced ? 16 : 36
  for (let i = 0; i < driftN; i++) {
    const bx = (i * 97 + (reduced ? 0 : t * (0.008 + (i % 5) * 0.002))) % cssW
    const by = (i * 53 + Math.sin(t * 0.0006 + i) * (reduced ? 0 : 10) + cssH) % cssH
    const r = 0.8 + (i % 4) * 0.55
    ctx.fillStyle = `rgba(255, 255, 255, ${0.28 + (i % 3) * 0.12})`
    ctx.beginPath()
    ctx.arc(bx, by, r, 0, Math.PI * 2)
    ctx.fill()
  }

  // Burbujas ASCII subiendo (se nota el agua).
  const fontPx = Math.max(10, Math.floor(cell * 0.85))
  ctx.font = `${fontPx}px ui-monospace, Consolas, "Courier New", monospace`
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  const bubbles = reduced ? 10 : 22
  for (let i = 0; i < bubbles; i++) {
    const speed = 14 + (i % 5) * 7
    const wobble = reduced ? 0 : Math.sin(t * 0.0012 + i) * 10
    const bx = ((i * 97) % cssW) + wobble
    const by = reduced
      ? (cssH * ((i * 37) % 100)) / 100
      : cssH - ((t * 0.022 * speed + i * 47) % (cssH + 50))
    const ch = i % 4 === 0 ? 'o' : i % 4 === 1 ? '°' : i % 4 === 2 ? '.' : '·'
    ctx.fillStyle = `rgba(255, 255, 255, ${0.28 + (i % 3) * 0.1})`
    ctx.fillText(ch, bx, by)
  }
}

function blitSample(ctx, data, cols, rows, cell, alphaMul, tint) {
  const d = data.data
  const fontPx = Math.floor(cell * 0.7)
  ctx.font = `${fontPx}px ui-monospace, Consolas, "Courier New", monospace`
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  const [tr, tg, tb] = tint
  // Más peso al sample → se ven capas, aletas y moteado.
  const tintW = 0.38
  const sampleW = 0.52
  const shadowOx = cell * 0.35
  const shadowOy = cell * 0.45

  // 1) Sombra suave debajo (refuerza la vista desde arriba).
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      const i = (r * cols + c) * 4
      if (d[i + 3] < ALPHA_THRESHOLD) continue
      const alpha = (d[i + 3] / 255) * alphaMul * 0.22
      ctx.fillStyle = `rgba(40, 80, 100, ${alpha})`
      ctx.fillRect(c * cell + shadowOx, r * cell + shadowOy, cell - 1, cell - 1)
    }
  }

  // 2) Baldosas con bandas de tono (oscuro / medio / claro) + carácter.
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      const i = (r * cols + c) * 4
      const a = d[i + 3]
      if (a < ALPHA_THRESHOLD) continue
      const sr = d[i]
      const sg = d[i + 1]
      const sb = d[i + 2]
      const br = brightnessOf(sr, sg, sb)
      // Tres bandas: sombra, cuerpo, highlight (más tonalidades visibles).
      let bandLift
      let bandTint
      if (br < 0.33) {
        bandLift = 0.32 + br * 0.35
        bandTint = 0.85
      } else if (br < 0.62) {
        bandLift = 0.48 + br * 0.35
        bandTint = 1
      } else {
        bandLift = 0.62 + br * 0.35
        bandTint = 1.12
      }
      const rest = Math.max(0, 1 - tintW - sampleW)
      const base = 255 * bandLift
      const tileR = Math.round(
        Math.min(255, base * rest + tr * tintW * bandTint + sr * sampleW),
      )
      const tileG = Math.round(
        Math.min(255, base * rest + tg * tintW * bandTint + sg * sampleW),
      )
      const tileB = Math.round(
        Math.min(255, base * rest + tb * tintW * bandTint + sb * sampleW),
      )
      const x = c * cell
      const y = r * cell
      const alpha = (a / 255) * alphaMul

      ctx.fillStyle = `rgba(${tileR}, ${tileG}, ${tileB}, ${alpha * 0.92})`
      ctx.fillRect(x + 0.5, y + 0.5, cell - 1, cell - 1)
      ctx.strokeStyle = `rgba(255, 255, 255, ${(0.22 + br * 0.28) * alpha})`
      ctx.strokeRect(x + 0.5, y + 0.5, cell - 1, cell - 1)

      const ch = rampChar(br)
      const shade = br < 0.4 ? 55 : br < 0.7 ? 35 : 18
      ctx.fillStyle = `rgba(${Math.max(20, tileR - shade)}, ${Math.max(20, tileG - shade)}, ${Math.max(20, tileB - shade)}, ${Math.min(1, alpha + 0.18)})`
      ctx.fillText(ch, x + cell / 2, y + cell / 2 + 0.5)
    }
  }
}

/** Offscreen amplio: cuerpo + flukes + rotación + ondulación sin clip. */
const OFFSCREEN = 600

function makeOffscreen(size = OFFSCREEN) {
  const canvas = document.createElement('canvas')
  canvas.width = size
  canvas.height = size
  return { canvas, ctx: canvas.getContext('2d', { willReadFrequently: true }) }
}

/** Radio personal en px de pantalla (mitad cuerpo + flukes + holgura). */
function personalR(a) {
  return 110 * a.scale + 80
}

function pairMinDist(a, b) {
  return personalR(a) + personalR(b) + 56
}

function makeSample(cols, rows) {
  const canvas = document.createElement('canvas')
  canvas.width = cols
  canvas.height = rows
  return {
    canvas,
    ctx: canvas.getContext('2d', { willReadFrequently: true, alpha: true }),
  }
}

function normAngle(a) {
  while (a > Math.PI) a -= Math.PI * 2
  while (a < -Math.PI) a += Math.PI * 2
  return a
}

function spawnWhale(rand, cssW, cssH, layer, variantId) {
  const variant = variantById(
    variantId ?? BALLENA_VARIANTES[Math.floor(rand() * BALLENA_VARIANTES.length)].id,
  )
  const layerScale = layer === 0 ? 1.15 : layer === 1 ? 0.95 : 0.72
  const scale = variant.size * layerScale * (0.9 + rand() * 0.2)
  const baseSpeed = (22 + rand() * 28) / (layer + 1) * (variant.id === 'cria' ? 1.2 : 1)
  const pad = 36
  return {
    id: 'ballena',
    variant: variant.id,
    // Toda la ventana es zona de nado.
    x: pad + rand() * Math.max(40, cssW - pad * 2),
    y: pad + rand() * Math.max(40, cssH - pad * 2),
    angle: rand() * Math.PI * 2,
    heading: rand() * Math.PI * 2,
    turnRate: 0.35 + rand() * 0.55,
    scale,
    worldScale: 1,
    speed: baseSpeed,
    baseSpeed,
    layer,
    phase: rand() * Math.PI * 2,
    wanderIn: 1.5 + rand() * 3.5,
    outTime: 0,
    alphaMul: layer === 0 ? 0.38 : layer === 1 ? 0.58 : 0.88,
    tint: variant.palette.tint,
  }
}

/**
 * Nado natural: deambular, girar, evitar bordes y no pisarse entre sí.
 * @param {ReturnType<typeof spawnWhale>} a
 * @param {ReturnType<typeof spawnWhale>[]} others
 */
function updateSwim(a, dt, cssW, cssH, t, rand, others = []) {
  const dtSec = dt / 1000
  a.wanderIn -= dtSec

  if (a.wanderIn <= 0) {
    a.heading = normAngle(a.heading + (rand() - 0.5) * 1.8)
    a.wanderIn = 2 + rand() * 5
    a.speed = a.baseSpeed * (0.75 + rand() * 0.5)
  }

  // Separación suave: virar hacia afuera (mezcla, no reemplazo brusco).
  let sepX = 0
  let sepY = 0
  let sepN = 0
  for (const o of others) {
    if (o === a) continue
    const dx = a.x - o.x
    const dy = a.y - o.y
    const dist = Math.hypot(dx, dy) || 0.01
    const minDist = pairMinDist(a, o)
    if (dist < minDist) {
      const push = ((minDist - dist) / minDist) ** 1.2
      sepX += (dx / dist) * push
      sepY += (dy / dist) * push
      sepN++
    }
  }
  if (sepN > 0) {
    const sepHeading = Math.atan2(sepY, sepX)
    const w = 0.75
    a.heading = Math.atan2(
      Math.sin(a.heading) * (1 - w) + Math.sin(sepHeading) * w,
      Math.cos(a.heading) * (1 - w) + Math.cos(sepHeading) * w,
    )
    a.wanderIn = Math.min(a.wanderIn, 0.5)
    a.speed = Math.max(a.baseSpeed * 1.05, a.speed * 1.05)
  }

  // Asoman un poco; si están fuera, vuelven rápido (poco tiempo off-screen).
  const overflow = Math.min(90, personalR(a) * 0.38)
  const cornerZone = 140 + a.scale * 40
  const nearL = a.x < cornerZone
  const nearR = a.x > cssW - cornerZone
  const nearT = a.y < cornerZone
  const nearB = a.y > cssH - cornerZone
  const inCorner = (nearL || nearR) && (nearT || nearB)

  // Evitar esquinas: rumbo claro al centro (evita quedar trabadas oscilando).
  if (inCorner) {
    const cx = cssW * 0.5
    const cy = cssH * 0.5
    const toCenter = Math.atan2(cy - a.y, cx - a.x)
    // Sesgo tangencial estable por ballena para no ir siempre al mismo punto.
    const tangent = toCenter + (a.phase % 2 < 1 ? 0.55 : -0.55)
    const w = 0.7
    a.heading = Math.atan2(
      Math.sin(a.heading) * (1 - w) + Math.sin(tangent) * w,
      Math.cos(a.heading) * (1 - w) + Math.cos(tangent) * w,
    )
    a.speed = Math.max(a.baseSpeed * 1.2, a.speed)
    a.wanderIn = Math.min(a.wanderIn, 0.4)
  }

  const outX = a.x < 0 ? -a.x : a.x > cssW ? a.x - cssW : 0
  const outY = a.y < 0 ? -a.y : a.y > cssH ? a.y - cssH : 0
  const outside = outX > 0 || outY > 0
  if (outside) {
    a.outTime = (a.outTime ?? 0) + dtSec
    // Si está fuera en esquina, priorizar centro; si no, eje del borde.
    const toward = inCorner
      ? Math.atan2(cssH * 0.5 - a.y, cssW * 0.5 - a.x)
      : Math.atan2(
        a.y < 0 ? 1 : a.y > cssH ? -1 : Math.sin(a.angle) * 0.2,
        a.x < 0 ? 1 : a.x > cssW ? -1 : Math.cos(a.angle) * 0.2,
      )
    const depth = Math.min(1, Math.max(outX, outY) / Math.max(1, overflow))
    const w = Math.min(0.95, 0.55 + a.outTime * 0.9 + depth * 0.35 + (inCorner ? 0.2 : 0))
    a.heading = Math.atan2(
      Math.sin(a.heading) * (1 - w) + Math.sin(toward) * w,
      Math.cos(a.heading) * (1 - w) + Math.cos(toward) * w,
    )
    a.speed = Math.max(a.baseSpeed * 1.15, a.speed)
  } else {
    a.outTime = 0
  }

  let diff = normAngle(a.heading - a.angle)
  const maxTurn = a.turnRate * dtSec * (
    inCorner ? 3.6 : outside ? 3.2 : sepN > 0 ? 2.2 : 1
  )
  if (Math.abs(diff) > maxTurn) diff = Math.sign(diff) * maxTurn
  a.angle = normAngle(a.angle + diff)

  a.x += Math.cos(a.angle) * a.speed * dtSec
  a.y += Math.sin(a.angle) * a.speed * dtSec
  a.y += Math.sin(t * 0.0007 + a.phase) * 0.12

  // Tope: pico corto fuera; en esquina, menos overhang para no trabarse.
  const maxOut = inCorner ? overflow * 0.35 : overflow
  a.x = Math.min(cssW + maxOut, Math.max(-maxOut, a.x))
  a.y = Math.min(cssH + maxOut, Math.max(-maxOut, a.y))
}

/**
 * Empuje duro simétrico: garantiza distancia mínima siempre (varios pases).
 * @param {ReturnType<typeof spawnWhale>[]} actors
 */
function resolveOverlaps(actors, cssW, cssH, passes = 4) {
  for (let pass = 0; pass < passes; pass++) {
    for (let i = 0; i < actors.length; i++) {
      for (let j = i + 1; j < actors.length; j++) {
        const a = actors[i]
        const b = actors[j]
        const dx = a.x - b.x
        const dy = a.y - b.y
        const dist = Math.hypot(dx, dy) || 0.01
        const min = pairMinDist(a, b)
        if (dist < min) {
          const push = (min - dist) / 2
          const ux = dx / dist
          const uy = dy / dist
          a.x += ux * push
          a.y += uy * push
          b.x -= ux * push
          b.y -= uy * push
        }
      }
    }
    // Pueden asomarse poco; no se clavan al borde interior.
    for (const a of actors) {
      const overflow = Math.min(90, personalR(a) * 0.38)
      a.x = Math.min(cssW + overflow, Math.max(-overflow, a.x))
      a.y = Math.min(cssH + overflow, Math.max(-overflow, a.y))
    }
  }
}

/** Coloca actores sin solaparse al nacer / al redimensionar. */
function spaceActors(actors, cssW, cssH) {
  resolveOverlaps(actors, cssW, cssH, 12)
}

/**
 * Preview: variantes quietas (catálogo) o varias nadando.
 * @param {HTMLCanvasElement} canvas
 * @param {{ moving?: boolean }} [opts]
 */
export function paintPreview(canvas, opts = {}) {
  const moving = Boolean(opts.moving)
  const dpr = Math.min(window.devicePixelRatio || 1, 2)
  const cssW = Math.max(canvas.clientWidth || 900, 640)
  const cssH = Math.max(canvas.clientHeight || (moving ? 420 : 560), 360)
  canvas.width = Math.floor(cssW * dpr)
  canvas.height = Math.floor(cssH * dpr)
  canvas.style.width = `${cssW}px`
  canvas.style.height = `${cssH}px`
  const ctx = canvas.getContext('2d')
  if (!ctx) return null
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0)

  const cell = cellSizeForWidth(cssW)
  const cols = Math.ceil(cssW / cell)
  const rows = Math.ceil(cssH / cell)
  const off = makeOffscreen()
  const sample = makeSample(cols, rows)

  /** @type {ReturnType<typeof spawnWhale>[]} */
  let actors
  const rng = mulberry32(99)
  if (moving) {
    actors = BALLENA_VARIANTES.map((v, i) => {
      const a = spawnWhale(rng, cssW, cssH, i % 3, v.id)
      a.x = cssW * (0.18 + (i % 2) * 0.5)
      a.y = cssH * (0.28 + Math.floor(i / 2) * 0.4)
      a.alphaMul = 0.85
      return a
    })
    spaceActors(actors, cssW, cssH)
  } else {
    actors = BALLENA_VARIANTES.map((v, i) => {
      const col = i % 2
      const row = Math.floor(i / 2)
      return {
        id: 'ballena',
        variant: v.id,
        x: cssW * (0.28 + col * 0.48),
        y: cssH * (0.28 + row * 0.48),
        angle: -0.2 + i * 0.15,
        heading: -0.2 + i * 0.15,
        turnRate: 0.4,
        scale: v.size * 0.95,
        worldScale: 1,
        speed: 0,
        baseSpeed: 0,
        layer: 2,
        phase: i,
        wanderIn: 99,
        alphaMul: 0.92,
        tint: v.palette.tint,
      }
    })
  }

  let raf = 0
  let last = 0
  let acc = 0
  const t0 = performance.now()
  let alive = true

  function frame(now) {
    if (!alive) return
    if (!last) last = now
    acc += now - last
    last = now
    if (acc < FRAME_MS && moving) {
      raf = requestAnimationFrame(frame)
      return
    }
    const dt = Math.min(acc, FRAME_MS * 2)
    acc = 0
    const t = now - t0
    if (moving) {
      for (const a of actors) updateSwim(a, dt, cssW, cssH, t, rng, actors)
      resolveOverlaps(actors, cssW, cssH, 4)
    }
    paintOcean(ctx, cssW, cssH, t, !moving)
    if (!moving) {
      ctx.fillStyle = 'rgba(255,255,255,0.92)'
      ctx.font = '600 13px system-ui, sans-serif'
      for (let i = 0; i < BALLENA_VARIANTES.length; i++) {
        const v = BALLENA_VARIANTES[i]
        const col = i % 2
        const row = Math.floor(i / 2)
        ctx.fillText(
          v.label,
          cssW * (0.28 + col * 0.48) - 40,
          cssH * (0.28 + row * 0.48) - 70,
        )
      }
    }
    for (const a of actors) {
      const data = sampleActor(off, sample, a, cols, rows, cell, t, !moving)
      blitSample(ctx, data, cols, rows, cell, a.alphaMul, a.tint)
    }
    if (moving) raf = requestAnimationFrame(frame)
  }

  raf = requestAnimationFrame(frame)
  return {
    destroy() {
      alive = false
      cancelAnimationFrame(raf)
    },
  }
}

/**
 * Fondo a pantalla completa (solo ballenas).
 * @param {HTMLCanvasElement} canvas
 * @param {{ dimmed?: () => boolean, seed?: number, animate?: boolean }} [opts]
 */
export function mountFondo(canvas, opts = {}) {
  const ctx = canvas.getContext('2d')
  if (!ctx) return { destroy() {} }

  const animate = opts.animate !== false
  const rand = mulberry32(opts.seed ?? 42)
  let actors = []
  let off = makeOffscreen()
  let sample = null
  let cell = 12
  let cols = 0
  let rows = 0
  let cssW = 0
  let cssH = 0
  let raf = 0
  let last = 0
  let acc = 0
  let t0 = performance.now()
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
    cssW = window.innerWidth
    cssH = window.innerHeight
    canvas.width = Math.floor(cssW * dpr)
    canvas.height = Math.floor(cssH * dpr)
    canvas.style.width = `${cssW}px`
    canvas.style.height = `${cssH}px`
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
    cell = cellSizeForWidth(cssW)
    cols = Math.ceil(cssW / cell)
    rows = Math.ceil(cssH / cell)
    sample = makeSample(cols, rows)
    const n = animalBudget({ width: cssW, height: cssH, reducedMotion: reduced })
    actors = Array.from({ length: n }, (_, i) => {
      const vid = BALLENA_VARIANTES[i % BALLENA_VARIANTES.length].id
      return spawnWhale(rand, cssW, cssH, i % 3, vid)
    })
    spaceActors(actors, cssW, cssH)
    if (!animate || reduced) {
      const v = BALLENA_VARIANTES[0]
      actors = [{
        id: 'ballena',
        variant: v.id,
        x: cssW * 0.5,
        y: cssH * 0.55,
        angle: -0.2,
        heading: -0.2,
        turnRate: 0.4,
        scale: v.size,
        worldScale: 1,
        speed: 0,
        baseSpeed: 0,
        layer: 2,
        phase: 0,
        wanderIn: 99,
        alphaMul: 0.75,
        tint: v.palette.tint,
      }]
    }
    paint(0)
  }

  function paint(t) {
    paintOcean(ctx, cssW, cssH, t, reduced || !animate)
    if (opts.dimmed?.()) {
      ctx.fillStyle = 'rgba(110, 170, 190, 0.25)'
      ctx.fillRect(0, 0, cssW, cssH)
    }
    const sorted = [...actors].sort((a, b) => a.layer - b.layer)
    for (const a of sorted) {
      const data = sampleActor(off, sample, a, cols, rows, cell, t, reduced || !animate)
      blitSample(ctx, data, cols, rows, cell, a.alphaMul, a.tint)
    }
  }

  function tick(now) {
    if (!running) return
    if (!last) last = now
    acc += now - last
    last = now
    if (acc >= FRAME_MS) {
      const dt = Math.min(acc, FRAME_MS * 2)
      acc = 0
      const t = now - t0
      if (animate && !reduced) {
        for (const a of actors) updateSwim(a, dt, cssW, cssH, t, rand, actors)
        resolveOverlaps(actors, cssW, cssH, 4)
      }
      paint(t)
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

export { ANIMALS, ANIMAL_IDS, BALLENA_VARIANTES }
