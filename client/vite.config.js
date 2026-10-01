import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

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
})
