import assert from 'node:assert/strict'
import { describe, it } from 'node:test'
import { puedeConsultar } from './consulta.js'

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
