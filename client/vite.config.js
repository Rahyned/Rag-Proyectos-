import { resolve } from 'node:path'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const root = import.meta.dirname

export default defineConfig({
  plugins: [react()],
  // Vercel (portfolio) la sirve bajo /asistente/; local queda en /
  base: process.env.VITE_BASE || '/',
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
      '/corpus': 'http://localhost:8000',
    },
  },
  build: {
    rollupOptions: {
      input: {
        main: resolve(root, 'index.html'),
        'fauna-preview': resolve(root, 'fauna-preview.html'),
      },
    },
  },
})
