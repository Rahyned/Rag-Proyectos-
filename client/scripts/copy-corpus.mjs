import { cpSync, mkdirSync, readdirSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))
const src = join(here, '..', '..', 'corpus')
const dest = join(here, '..', 'public', 'corpus')

mkdirSync(dest, { recursive: true })
let copied = 0
for (const name of readdirSync(src)) {
  if (name.toLowerCase().endsWith('.pdf')) {
    cpSync(join(src, name), join(dest, name))
    copied += 1
  }
}
console.log(`corpus: ${copied} PDF -> client/public/corpus`)
