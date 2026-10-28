/**
 * Ballena franca austral — vista desde ARRIBA (planta / dorsal).
 * Columna + ancho + aletas pectorales a ambos lados + flukes en V.
 */

export const RAMP = ' .·:-=+*#%X@8'

/** @typedef {{ x: number, y: number }} Point */

/**
 * @typedef {object} WhalePalette
 * @property {string} body
 * @property {string} ridge     Centro del lomo (más oscuro).
 * @property {string} mid       Banda intermedia.
 * @property {string} edge      Bordes más claros.
 * @property {string} mottled   Manchas suaves del lomo.
 * @property {string} callus
 * @property {string} callusHi  Callosidad más clara.
 * @property {string} fin
 * @property {string} finEdge
 * @property {string} fluke
 * @property {string} flukeNotch
 * @property {[number, number, number]} tint
 */

/**
 * @typedef {object} WhaleVariant
 * @property {string} id
 * @property {string} label
 * @property {number} size
 * @property {number} bulk
 * @property {number} callus
 * @property {WhalePalette} palette
 */

/** @type {WhaleVariant[]} */
export const BALLENA_VARIANTES = [
  {
    id: 'adulta',
    label: 'Adulta gris-azul',
    size: 1.15,
    bulk: 1.0,
    callus: 0.85,
    palette: {
      body: '#5a7a98',
      ridge: '#2e4a68',
      mid: '#6e9aba',
      edge: 'rgba(180, 210, 235, 0.55)',
      mottled: 'rgba(120, 160, 195, 0.4)',
      callus: '#3a556e',
      callusHi: '#a8c8e0',
      fin: '#4a6e90',
      finEdge: '#9ec8e8',
      fluke: '#3a6088',
      flukeNotch: '#1a3550',
      tint: [90, 160, 220],
    },
  },
  {
    id: 'azulada',
    label: 'Adulta azulada',
    size: 1.05,
    bulk: 0.95,
    callus: 0.7,
    palette: {
      body: '#2a7ec8',
      ridge: '#0e4a8a',
      mid: '#3a98e0',
      edge: 'rgba(140, 210, 245, 0.55)',
      mottled: 'rgba(90, 170, 220, 0.4)',
      callus: '#1a5aa0',
      callusHi: '#7ec8f0',
      fin: '#2080d0',
      finEdge: '#70c8f8',
      fluke: '#1868b8',
      flukeNotch: '#0a3868',
      tint: [40, 150, 240],
    },
  },
  {
    id: 'cria',
    label: 'Cría arena',
    size: 0.78,
    bulk: 1.05,
    callus: 0.12,
    palette: {
      body: '#e0a838',
      ridge: '#b87810',
      mid: '#ecc050',
      edge: 'rgba(240, 210, 120, 0.5)',
      mottled: 'rgba(200, 150, 50, 0.4)',
      callus: '#c89020',
      callusHi: '#f0d070',
      fin: '#d89828',
      finEdge: '#f0c858',
      fluke: '#c88820',
      flukeNotch: '#8a6010',
      tint: [235, 170, 45],
    },
  },
  {
    id: 'callosa',
    label: 'Callosa coral',
    size: 1.25,
    bulk: 1.08,
    callus: 1.0,
    palette: {
      body: '#e85868',
      ridge: '#a82838',
      mid: '#f07080',
      edge: 'rgba(240, 160, 175, 0.5)',
      mottled: 'rgba(200, 80, 95, 0.4)',
      callus: '#b03040',
      callusHi: '#f0a0b0',
      fin: '#d84858',
      finEdge: '#ff98a8',
      fluke: '#c83848',
      flukeNotch: '#701820',
      tint: [240, 70, 95],
    },
  },
]

/**
 * @typedef {object} DrawOpts
 * @property {number} [wave]
 * @property {number} [amp]
 * @property {WhaleVariant} [variant]
 */

function spinePoints(joints, wave = 0, amp = 0) {
  /** @type {Point[]} */
  const pts = []
  for (let i = 0; i < joints.length; i++) {
    const j = joints[i]
    const t = i / Math.max(1, joints.length - 1)
    // Ondulación lateral (vista desde arriba): mueve en Y.
    const bend = Math.sin(wave + t * Math.PI * 2) * amp * (1 - t * 0.55)
    pts.push({ x: j.x, y: j.y + bend })
  }
  return pts
}

function tangents(pts) {
  const out = []
  for (let i = 0; i < pts.length; i++) {
    const a = pts[Math.max(0, i - 1)]
    const b = pts[Math.min(pts.length - 1, i + 1)]
    const dx = b.x - a.x
    const dy = b.y - a.y
    const len = Math.hypot(dx, dy) || 1
    out.push({ tx: dx / len, ty: dy / len, nx: -dy / len, ny: dx / len })
  }
  return out
}

function fillBody(ctx, pts, halfW, fill) {
  const T = tangents(pts)
  ctx.beginPath()
  for (let i = 0; i < pts.length; i++) {
    const x = pts[i].x + T[i].nx * halfW[i]
    const y = pts[i].y + T[i].ny * halfW[i]
    if (i === 0) ctx.moveTo(x, y)
    else ctx.lineTo(x, y)
  }
  for (let i = pts.length - 1; i >= 0; i--) {
    const x = pts[i].x - T[i].nx * halfW[i]
    const y = pts[i].y - T[i].ny * halfW[i]
    ctx.lineTo(x, y)
  }
  ctx.closePath()
  ctx.fillStyle = fill
  ctx.fill()
}

function variantById(id) {
  return BALLENA_VARIANTES.find((v) => v.id === id) ?? BALLENA_VARIANTES[0]
}

/**
 * Perfil CENITAL (planta): anchos = izquierda/derecha del eje,
 * nunca alto de costado. Cuerpo ovalado y ancho.
 */
function whaleProfile(variantId) {
  if (variantId === 'cria') {
    return {
      joints: [
        { x: -90, y: 0 },
        { x: -65, y: 0 },
        { x: -30, y: 0 },
        { x: 5, y: 0 },
        { x: 40, y: 0 },
        { x: 72, y: 0 },
        { x: 100, y: 0 },
        { x: 118, y: 0 },
      ],
      // Bien panzona en planta.
      halfW: [8, 22, 40, 46, 44, 36, 28, 16],
      pecAt: 3,
      pecLen: 1.35,
      flukeSpan: 78,
      flukeReach: 52,
      headR: 22,
    }
  }
  return {
    joints: [
      { x: -150, y: 0 },
      { x: -110, y: 0 },
      { x: -60, y: 0 },
      { x: -10, y: 0 },
      { x: 40, y: 0 },
      { x: 90, y: 0 },
      { x: 128, y: 0 },
      { x: 158, y: 0 },
    ],
    // Oval dorsal ancho (franca austral vista desde arriba).
    halfW: [7, 20, 38, 46, 44, 36, 26, 14],
    pecAt: 3,
    pecLen: 1.45,
    flukeSpan: 86,
    flukeReach: 62,
    headR: 18,
  }
}

/**
 * Aletas pectorales bien abiertas (planta): se leen como paletas laterales
 * tras el downsample a baldosas ASCII.
 */
function drawPectoral(ctx, pec, T, side, len, pal, bodyHalf) {
  const rootIn = bodyHalf * 0.72
  const reach = 68 * len
  const root = {
    x: pec.x + T.nx * side * rootIn,
    y: pec.y + T.ny * side * rootIn,
  }
  const tip = {
    x: pec.x + T.nx * side * reach - T.tx * 8 * len,
    y: pec.y + T.ny * side * reach - T.ty * 8 * len,
  }
  const midFwd = {
    x: pec.x + T.nx * side * (reach * 0.55) + T.tx * 22 * len,
    y: pec.y + T.ny * side * (reach * 0.55) + T.ty * 22 * len,
  }
  const midBack = {
    x: pec.x + T.nx * side * (reach * 0.48) - T.tx * 18 * len,
    y: pec.y + T.ny * side * (reach * 0.48) - T.ty * 18 * len,
  }
  const path = new Path2D()
  path.moveTo(root.x, root.y)
  path.quadraticCurveTo(midFwd.x, midFwd.y, tip.x, tip.y)
  path.quadraticCurveTo(midBack.x, midBack.y, root.x, root.y)

  // Relleno base + degradé raíz→punta (más tonos).
  const grad = ctx.createLinearGradient(root.x, root.y, tip.x, tip.y)
  grad.addColorStop(0, pal.fin)
  grad.addColorStop(0.45, pal.mid)
  grad.addColorStop(1, pal.finEdge)
  ctx.fillStyle = grad
  ctx.fill(path)
  // Nervio central más claro.
  ctx.strokeStyle = pal.edge
  ctx.lineWidth = 3.5
  ctx.beginPath()
  ctx.moveTo(root.x, root.y)
  ctx.lineTo(
    pec.x + T.nx * side * (reach * 0.78) - T.tx * 4 * len,
    pec.y + T.ny * side * (reach * 0.78) - T.ty * 4 * len,
  )
  ctx.stroke()
  ctx.strokeStyle = pal.finEdge
  ctx.lineWidth = 2.5
  ctx.stroke(path)
}

/** Ballena franca austral — SIEMPRE vista desde arriba (cenital). */
function drawBallena(ctx, opts = {}) {
  const wave = opts.wave ?? 0
  const amp = opts.amp ?? 0
  const v = opts.variant ?? BALLENA_VARIANTES[0]
  const pal = v.palette
  const bulk = v.bulk
  const profile = whaleProfile(v.id)
  const isCria = v.id === 'cria'

  const halfW = profile.halfW.map((w) => w * bulk)
  // Ondulación lateral en el plano (como se ve nadando desde arriba).
  const pts = spinePoints(profile.joints, wave, amp * (isCria ? 0.7 : 1))
  const T = tangents(pts)

  // Capas de tono: borde oscuro → cuerpo → flanco → cresta clara.
  fillBody(ctx, pts, halfW.map((w) => w * 1.06), pal.ridge)
  fillBody(ctx, pts, halfW, pal.body)
  fillBody(ctx, pts, halfW.map((w) => w * 0.82), pal.mid)
  fillBody(ctx, pts, halfW.map((w) => w * 0.48), pal.finEdge)
  fillBody(ctx, pts, halfW.map((w) => w * 0.28), pal.edge)

  // Bordes claros en AMBOS flancos (simetría dorsal, no “panza abajo”).
  for (const s of [-1, 1]) {
    const edgePts = pts.map((p, i) => ({
      x: p.x + T[i].nx * s * halfW[i] * 0.92,
      y: p.y + T[i].ny * s * halfW[i] * 0.92,
    }))
    ctx.strokeStyle = pal.edge
    ctx.lineWidth = 5
    ctx.lineCap = 'round'
    ctx.beginPath()
    edgePts.forEach((p, i) => (i === 0 ? ctx.moveTo(p.x, p.y) : ctx.lineTo(p.x, p.y)))
    ctx.stroke()
  }

  // Degradé cola→cabeza sobre el lomo (más bandas de tono).
  const along = ctx.createLinearGradient(
    pts[0].x, pts[0].y, pts[pts.length - 1].x, pts[pts.length - 1].y,
  )
  along.addColorStop(0, 'rgba(0,0,0,0.28)')
  along.addColorStop(0.28, 'rgba(0,0,0,0.08)')
  along.addColorStop(0.55, 'rgba(255,255,255,0.06)')
  along.addColorStop(0.82, pal.edge)
  along.addColorStop(1, 'rgba(255,255,255,0.2)')
  fillBody(ctx, pts, halfW.map((w) => w * 0.72), along)

  // Moteado denso (varios tamaños / opacidades) → más tonalidades en el sample.
  for (let i = 1; i < pts.length - 1; i++) {
    for (const s of [-1, 1]) {
      const seed = i * 3 + (s > 0 ? 1 : 0)
      ctx.fillStyle = seed % 2 === 0 ? pal.mottled : pal.callus
      ctx.beginPath()
      ctx.ellipse(
        pts[i].x + T[i].nx * s * halfW[i] * (0.35 + (seed % 3) * 0.12),
        pts[i].y + T[i].ny * s * halfW[i] * (0.35 + (seed % 3) * 0.12),
        5 + (seed % 4) * 2.2,
        2.6 + (seed % 3),
        Math.atan2(T[i].ty, T[i].tx),
        0,
        Math.PI * 2,
      )
      ctx.fill()
      if (seed % 3 === 0) {
        ctx.fillStyle = pal.callusHi
        ctx.beginPath()
        ctx.ellipse(
          pts[i].x + T[i].nx * s * halfW[i] * 0.22,
          pts[i].y + T[i].ny * s * halfW[i] * 0.22,
          3.2,
          1.8,
          Math.atan2(T[i].ty, T[i].tx),
          0,
          Math.PI * 2,
        )
        ctx.fill()
      }
    }
  }

  // Aletas pectorales ANTES de la cabeza/cola para que no las tape el downsample.
  const pecI = Math.min(profile.pecAt, pts.length - 1)
  drawPectoral(ctx, pts[pecI], T[pecI], 1, profile.pecLen * bulk, pal, halfW[pecI])
  drawPectoral(ctx, pts[pecI], T[pecI], -1, profile.pecLen * bulk, pal, halfW[pecI])

  // Cabeza redonda centrada en el eje (planta).
  const head = pts[pts.length - 1]
  const hn = T[T.length - 1]
  const headAng = Math.atan2(hn.ty, hn.tx)
  ctx.fillStyle = pal.mid
  ctx.beginPath()
  ctx.ellipse(
    head.x + hn.tx * 6,
    head.y + hn.ty * 6,
    profile.headR * (isCria ? 1.2 : 1) * 1.05,
    profile.headR * bulk,
    headAng,
    0,
    Math.PI * 2,
  )
  ctx.fill()
  // Brillo centrado en el hocico (no a un solo costado).
  ctx.fillStyle = pal.edge
  ctx.beginPath()
  ctx.ellipse(
    head.x + hn.tx * 8,
    head.y + hn.ty * 8,
    profile.headR * 0.4,
    profile.headR * 0.35,
    headAng,
    0,
    Math.PI * 2,
  )
  ctx.fill()

  // Callosidades en el lomo de la cabeza, simétricas izq/der.
  const patches = [
    [8, 0, 5],
    [2, -8, 4],
    [2, 8, 4],
    [14, -5, 3.5],
    [14, 5, 3.5],
    [-2, -6, 3],
    [-2, 6, 3],
    [20, 0, 3.2],
  ]
  const nPatches = Math.round(patches.length * v.callus)
  for (let i = 0; i < nPatches; i++) {
    const [ox, oy, r] = patches[i]
    const cx = head.x + hn.tx * ox + hn.nx * oy
    const cy = head.y + hn.ty * ox + hn.ny * oy
    ctx.fillStyle = pal.callus
    ctx.beginPath()
    ctx.ellipse(cx, cy, r, r * 0.75, headAng, 0, Math.PI * 2)
    ctx.fill()
    ctx.fillStyle = pal.callusHi
    ctx.beginPath()
    ctx.ellipse(cx + hn.tx * 0.8, cy + hn.ty * 0.8, r * 0.35, r * 0.28, headAng, 0, Math.PI * 2)
    ctx.fill()
  }

  // Spiráculos (par dorsal).
  const blow = pts[pts.length - 2]
  const bt = T[T.length - 2]
  ctx.fillStyle = '#111'
  for (const s of [-1, 1]) {
    ctx.beginPath()
    ctx.arc(
      blow.x + bt.nx * s * 5,
      blow.y + bt.ny * s * 5,
      isCria ? 2.4 : 2,
      0, Math.PI * 2,
    )
    ctx.fill()
  }

  // Cola en V / media luna BIEN ABIERTA (marca de vista cenital).
  const tail = pts[0]
  const tt = T[0]
  const span = profile.flukeSpan * bulk
  const reach = profile.flukeReach
  const fluke = new Path2D()
  fluke.moveTo(tail.x + tt.tx * 10, tail.y + tt.ty * 10)
  fluke.quadraticCurveTo(
    tail.x - tt.tx * 6 + tt.nx * span,
    tail.y - tt.ty * 6 + tt.ny * span,
    tail.x - tt.tx * reach + tt.nx * (span * 0.2),
    tail.y - tt.ty * reach + tt.ny * (span * 0.2),
  )
  fluke.quadraticCurveTo(
    tail.x - tt.tx * (reach * 0.5),
    tail.y - tt.ty * (reach * 0.5),
    tail.x - tt.tx * reach - tt.nx * (span * 0.2),
    tail.y - tt.ty * reach - tt.ny * (span * 0.2),
  )
  fluke.quadraticCurveTo(
    tail.x - tt.tx * 6 - tt.nx * span,
    tail.y - tt.ty * 6 - tt.ny * span,
    tail.x + tt.tx * 10,
    tail.y + tt.ty * 10,
  )
  const flukeGrad = ctx.createLinearGradient(
    tail.x, tail.y,
    tail.x - tt.tx * reach, tail.y - tt.ty * reach,
  )
  flukeGrad.addColorStop(0, pal.fluke)
  flukeGrad.addColorStop(0.55, pal.fin)
  flukeGrad.addColorStop(1, pal.flukeNotch)
  ctx.fillStyle = flukeGrad
  ctx.fill(fluke)
  // Muesca central de los flukes (muy legible desde arriba).
  ctx.fillStyle = pal.flukeNotch
  ctx.beginPath()
  ctx.moveTo(tail.x - tt.tx * 4, tail.y - tt.ty * 4)
  ctx.lineTo(
    tail.x - tt.tx * (reach * 0.55) + tt.nx * 8,
    tail.y - tt.ty * (reach * 0.55) + tt.ny * 8,
  )
  ctx.lineTo(
    tail.x - tt.tx * (reach * 0.55) - tt.nx * 8,
    tail.y - tt.ty * (reach * 0.55) - tt.ny * 8,
  )
  ctx.closePath()
  ctx.fill()
  ctx.strokeStyle = pal.finEdge
  ctx.lineWidth = isCria ? 2.5 : 2
  ctx.stroke(fluke)
}

export const ANIMALS = {
  ballena: {
    id: 'ballena',
    nombre: 'Ballena franca austral',
    length: 320,
    scale: 1.2,
    draw: drawBallena,
  },
}

export const ANIMAL_IDS = Object.keys(ANIMALS)

export function paintAnimal(ctx, animalId, opts = {}) {
  const animal = ANIMALS[animalId]
  if (!animal) return
  const variant = typeof opts.variant === 'string'
    ? variantById(opts.variant)
    : (opts.variant ?? BALLENA_VARIANTES[0])
  animal.draw(ctx, { ...opts, variant })
}

export { variantById }
