import assert from 'node:assert/strict'
import { describe, it, mock } from 'node:test'
import { elegirProyecto, puedeConsultar } from './consulta.js'
import { streamChat } from './api.js'

describe('puedeConsultar', () => {
  it('exige proyecto y texto', () => {
    assert.equal(puedeConsultar('', 'hola'), false)
    assert.equal(puedeConsultar('stella', ''), false)
    assert.equal(puedeConsultar('stella', '   '), false)
    assert.equal(puedeConsultar('stella', 'hola'), true)
  })

  it('bloquea mientras busy', () => {
    assert.equal(puedeConsultar('stella', 'hola', true), false)
  })
})

describe('elegir proyecto habilita Consultar y viaja en la query', () => {
  it('al elegir stella, Consultar queda listo con texto', () => {
    const antes = elegirProyecto('', '¿cómo agrego un cliente?')
    assert.equal(antes.listo, false)
    const despues = elegirProyecto('stella', '¿cómo agrego un cliente?')
    assert.equal(despues.proyecto, 'stella')
    assert.equal(despues.listo, true)
  })

  it('streamChat manda el proyecto elegido en el body', async () => {
    const bodies = []
    mock.method(globalThis, 'fetch', async (_url, opts) => {
      bodies.push(JSON.parse(opts.body))
      const stream = new ReadableStream({
        start(controller) {
          controller.enqueue(
            new TextEncoder().encode('data: {"type":"done","mode":"fragmentos"}\n\n'),
          )
          controller.close()
        },
      })
      return {
        ok: true,
        body: stream,
        json: async () => ({}),
      }
    })
    try {
      const elegido = elegirProyecto('stella', 'agregar cliente')
      assert.equal(elegido.listo, true)
      await streamChat({
        query: 'agregar cliente',
        mode: 'fragmentos',
        proyecto: elegido.proyecto,
        onSources() {},
        onText() {},
        onFallback() {},
        onDone() {},
      })
      assert.equal(bodies.length, 1)
      assert.equal(bodies[0].proyecto, 'stella')
      assert.equal(bodies[0].query, 'agregar cliente')
    } finally {
      mock.restoreAll()
    }
  })
})
