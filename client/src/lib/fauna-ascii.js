/**
 * Ballena franca austral — vista desde ARRIBA (planta / dorsal).
 * Columna + ancho + aletas pectorales a ambos lados + flukes en V.
 */

export const RAMP = ' .:-=+*#%@'

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
      body: '#7a8a98',
      ridge: '#5a6a78',
      mid: '#8a9aa8',
      edge: 'rgba(210, 220, 230, 0.55)',
      mottled: 'rgba(120, 135, 150, 0.4)',
      callus: '#5a6878',
      callusHi: '#b0bcc8',
      fin: '#6a7a88',
      finEdge: '#a0b0c0',
      fluke: '#607080',
      flukeNotch: '#405060',
      tint: [150, 165, 180],
    },
  },
  {
    id: 'azulada',
    label: 'Adulta azulada',
    size: 1.05,
    bulk: 0.95,
    callus: 0.7,
    palette: {
      body: '#5a8aaa',
      ridge: '#3a6a8a',
      mid: '#6a9aba',
      edge: 'rgba(180, 215, 235, 0.55)',
      mottled: 'rgba(90, 140, 170, 0.35)',
      callus: '#4a7a9a',
      callusHi: '#a0c8e0',
      fin: '#5088a8',
      finEdge: '#90c0d8',
      fluke: '#457898',
      flukeNotch: '#2a5068',
      tint: [110, 165, 200],
    },
  },
  {
    id: 'cria',
    label: 'Cría arena',
    size: 0.78,
    bulk: 1.05,
    callus: 0.12,
    palette: {
      body: '#d4c090',
      ridge: '#b8a070',
      mid: '#e0d0a0',
      edge: 'rgba(255, 248, 220, 0.7)',
      mottled: 'rgba(210, 185, 130, 0.35)',
      callus: '#c0a880',
      callusHi: '#f0e4c0',
      fin: '#d0b880',
      finEdge: '#f0e0b0',
      fluke: '#b89868',
      flukeNotch: '#887048',
      tint: [225, 195, 115],
    },
  },
  {
    id: 'callosa',
    label: 'Callosa coral',
    size: 1.25,
    bulk: 1.08,
    callus: 1.0,
    palette: {
      body: '#c88888',
      ridge: '#a86868',
      mid: '#d89898',
      edge: 'rgba(250, 210, 210, 0.55)',
      mottled: 'rgba(180, 110, 110, 0.35)',
      callus: '#a06060',
      callusHi: '#e8b8b8',
      fin: '#b87878',
      finEdge: '#e0a8a8',
      fluke: '#a86868',
      flukeNotch: '#704040',
      tint: [210, 125, 135],
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
      pecLen: 1.05,
      flukeSpan: 72,
      flukeReach: 44,
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
    pecLen: 1.15,
    flukeSpan: 78,
    flukeReach: 54,
    headR: 18,
  }
}

/** Aletas pectorales hacia los costados (simétricas en planta). */
function drawPectoral(ctx, pec, T, side, len, pal, bodyHalf) {
  const rootIn = bodyHalf * 0.85
  const root = {
    x: pec.x + T.nx * side * rootIn,
    y: pec.y + T.ny * side * rootIn,
  }
  // Casi perpendiculares al cuerpo: se leen como “alas” desde arriba.
  const tip = {
    x: pec.x + T.nx * side * (48 * len) - T.tx * 4 * len,
    y: pec.y + T.ny * side * (48 * len) - T.ty * 4 * len,
  }
  const midFwd = {
    x: pec.x + T.nx * side * (28 * len) + T.tx * 10 * len,
    y: pec.y + T.ny * side * (28 * len) + T.ty * 10 * len,
  }
  const midBack = {
    x: pec.x + T.nx * side * (22 * len) - T.tx * 6 * len,
    y: pec.y + T.ny * side * (22 * len) - T.ty * 6 * len,
  }
  ctx.fillStyle = pal.fin
  ctx.beginPath()
  ctx.moveTo(root.x, root.y)
  ctx.quadraticCurveTo(midFwd.x, midFwd.y, tip.x, tip.y)
  ctx.quadraticCurveTo(midBack.x, midBack.y, root.x, root.y)
  ctx.fill()
  ctx.strokeStyle = pal.finEdge
  ctx.lineWidth = 2
  ctx.stroke()
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

  // Capas simétricas: cuerpo → flancos → cresta central.
  fillBody(ctx, pts, halfW, pal.body)
  fillBody(ctx, pts, halfW.map((w) => w * 0.78), pal.mid)
  fillBody(ctx, pts, halfW.map((w) => w * 0.38), pal.ridge)

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

  // Degradé cola→cabeza sobre el lomo.
  const along = ctx.createLinearGradient(
    pts[0].x, pts[0].y, pts[pts.length - 1].x, pts[pts.length - 1].y,
  )
  along.addColorStop(0, 'rgba(0,0,0,0.25)')
  along.addColorStop(0.5, 'rgba(0,0,0,0)')
  along.addColorStop(1, pal.edge)
  fillBody(ctx, pts, halfW.map((w) => w * 0.7), along)

  // Moteado simétrico.
  ctx.fillStyle = pal.mottled
  for (let i = 1; i < pts.length - 1; i++) {
    for (const s of [-1, 1]) {
      if ((i + (s > 0 ? 0 : 1)) % 2 === 0) continue
      ctx.beginPath()
      ctx.ellipse(
        pts[i].x + T[i].nx * s * halfW[i] * 0.48,
        pts[i].y + T[i].ny * s * halfW[i] * 0.48,
        7 + (i % 3) * 2,
        3.2,
        Math.atan2(T[i].ty, T[i].tx),
        0,
        Math.PI * 2,
      )
      ctx.fill()
    }
  }

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

  const pecI = Math.min(profile.pecAt, pts.length - 1)
  drawPectoral(ctx, pts[pecI], T[pecI], 1, profile.pecLen * bulk, pal, halfW[pecI])
  drawPectoral(ctx, pts[pecI], T[pecI], -1, profile.pecLen * bulk, pal, halfW[pecI])

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
  ctx.fillStyle = pal.fluke
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
  if (isCria) {
    ctx.strokeStyle = pal.flukeNotch
    ctx.lineWidth = 2.5
    ctx.stroke(fluke)
  }
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
