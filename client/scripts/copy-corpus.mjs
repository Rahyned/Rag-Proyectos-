import { cpSync, mkdirSync, readdirSync, statSync } from 'node:fs'
import { dirname, join, relative } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))
const src = join(here, '..', '..', 'corpus')
const dest = join(here, '..', 'public', 'corpus')

function copiar(dir) {
  let n = 0
  for (const name of readdirSync(dir)) {
    if (name.startsWith('_')) continue
    const path = join(dir, name)
    if (statSync(path).isDirectory()) {
      n += copiar(path)
      continue
    }
    if (!name.toLowerCase().endsWith('.pdf')) continue
    const rel = relative(src, path)
    const target = join(dest, rel)
    mkdirSync(dirname(target), { recursive: true })
    cpSync(path, target)
    n += 1
  }
  return n
}

mkdirSync(dest, { recursive: true })
const copied = copiar(src)
console.log(`corpus: ${copied} PDF -> client/public/corpus`)
