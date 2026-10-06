import assert from 'node:assert/strict'
import test from 'node:test'

import { renderMarkdown } from './markdown.js'

test('no inyecta HTML crudo', () => {
  const html = renderMarkdown('<script>alert(1)</script><img src=x onerror=alert(1)>')
  assert.equal(html.includes('<script'), false)
  assert.equal(html.includes('<img'), false)
  assert.equal(html.includes('onerror'), true)
  assert.match(html, /&lt;script&gt;/)
})

test('deja pasar negrita y un enlace http', () => {
  const html = renderMarkdown('**hola** y [sitio](https://example.com/a)')
  assert.match(html, /<strong>hola<\/strong>/)
  assert.match(html, /href="https:\/\/example.com\/a"/)
})

test('un enlace javascript no se vuelve href', () => {
  const html = renderMarkdown('[x](javascript:alert(1))')
  assert.equal(html.includes('href='), false)
  assert.equal(html.includes('<a'), false)
  assert.match(html, /javascript:alert/)
})
