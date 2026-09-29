import { useEffect, useState } from 'react'

export default function App() {
  const [health, setHealth] = useState('...')

  useEffect(() => {
    fetch('/api/health')
      .then((r) => r.json())
      .then((d) => setHealth(d.status))
      .catch(() => setHealth('sin API'))
  }, [])

  return (
    <main>
      <h1>Rag-Proyectos</h1>
      <p>Asistente RAG del portafolio — Fase 0</p>
      <p>API: {health}</p>
    </main>
  )
}
