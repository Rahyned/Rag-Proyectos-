import assert from 'node:assert/strict'
import { describe, it } from 'node:test'
import { ANIMALS, ANIMAL_IDS, BALLENA_VARIANTES, RAMP } from './fauna-ascii.js'
import { animalBudget, cellSizeForWidth, prefersReducedMotion } from './fondo-ascii.js'

describe('fauna-ascii ballena', () => {
  it('exporta solo la ballena franca con draw vectorial', () => {
    assert.deepEqual(ANIMAL_IDS, ['ballena'])
    const b = ANIMALS.ballena
    assert.equal(b.nombre, 'Ballena franca austral')
    assert.equal(typeof b.draw, 'function')
    assert.ok(b.length > 0)
    assert.ok(b.scale > 0)
  })

  it('tiene variantes de tamaño y color distintas', () => {
    assert.ok(BALLENA_VARIANTES.length >= 4)
    const sizes = new Set(BALLENA_VARIANTES.map((v) => v.size))
    const bodies = new Set(BALLENA_VARIANTES.map((v) => v.palette.body))
    assert.ok(sizes.size >= 3, 'tamaños distintos')
    assert.ok(bodies.size >= 3, 'colores de cuerpo distintos')
    for (const v of BALLENA_VARIANTES) {
      assert.equal(v.palette.tint.length, 3)
      assert.ok(v.callus >= 0 && v.callus <= 1)
    }
  })

  it('rampa ASCII y helpers de fondo', () => {
    assert.equal(RAMP, ' .:-=+*#%@')
    assert.equal(prefersReducedMotion(() => ({ matches: true })), true)
    assert.equal(cellSizeForWidth(390), 16)
    assert.equal(cellSizeForWidth(1400), 12)
    assert.equal(animalBudget({ width: 390, reducedMotion: false }), 2)
    assert.equal(animalBudget({ width: 1400, height: 900, reducedMotion: false }), 4)
    assert.equal(animalBudget({ width: 1400, reducedMotion: true }), 1)
  })
})
