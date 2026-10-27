import { useEffect, useRef } from 'react'
import { mountFauna } from './lib/fauna-ascii'

/** Fondo a pantalla completa; no recibe clics ni anuncia a lectores de pantalla. */
export default function FaunaBackground({ dimmed = false }) {
  const canvasRef = useRef(null)
  const dimmedRef = useRef(dimmed)
  dimmedRef.current = dimmed

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return undefined
    const engine = mountFauna(canvas, { dimmed: () => dimmedRef.current })
    return () => engine.destroy()
  }, [])

  return (
    <canvas
      ref={canvasRef}
      className="fauna-bg"
      aria-hidden="true"
    />
  )
}
