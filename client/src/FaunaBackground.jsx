import { useEffect, useRef } from 'react'
import { mountFondo } from './lib/fondo-ascii'

/** Fondo ASCII a pantalla completa (ballena). pointer-events none + aria-hidden. */
export default function FaunaBackground({ dimmed = false, animate = true }) {
  const canvasRef = useRef(null)
  const dimmedRef = useRef(dimmed)
  dimmedRef.current = dimmed

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return undefined
    const engine = mountFondo(canvas, {
      dimmed: () => dimmedRef.current,
      animate,
    })
    return () => engine.destroy()
  }, [animate])

  return (
    <canvas
      ref={canvasRef}
      className="fauna-bg"
      aria-hidden="true"
    />
  )
}
