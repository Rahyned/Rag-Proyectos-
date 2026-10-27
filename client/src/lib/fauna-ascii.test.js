import assert from 'node:assert/strict'
import { describe, it } from 'node:test'
import {
  SPECIES,
  animalCount,
  prefersReducedMotion,
} from './fauna-ascii.js'

describe('fauna-ascii', () => {
  it('incluye las cuatro especies de la costa', () => {
    assert.deepEqual(Object.keys(SPECIES).sort(), [
      'ballena',
      'lobo',
      'pinguino',
      'tonina',
    ])
    for (const spec of Object.values(SPECIES)) {
      assert.ok(spec.frames.length >= 1)
      assert.ok(spec.frames[0].length >= 3)
    }
  })

  it('respeta prefers-reduced-motion', () => {
    assert.equal(
      prefersReducedMotion(() => ({ matches: true })),
      true,
    )
    assert.equal(
      prefersReducedMotion(() => ({ matches: false })),
      false,
    )
    assert.equal(animalCount({ width: 1400, reducedMotion: true }), 2)
  })

  it('dibuja menos animales en celular', () => {
    assert.equal(animalCount({ width: 390, reducedMotion: false }), 3)
    assert.equal(animalCount({ width: 800, reducedMotion: false }), 5)
    assert.equal(animalCount({ width: 1400, reducedMotion: false }), 7)
  })
})
