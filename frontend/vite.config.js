import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'node:fs'
import path from 'node:path'

let outputDir = 'dist'

export default defineConfig({
  plugins: [react(), {
    name: 'static-route-entries',
    configResolved(config) {
      outputDir = config.build.outDir
    },
    closeBundle() {
      const html = fs.readFileSync(path.join(outputDir, 'index.html'), 'utf8')
      for (const route of ['models', 'publishers', 'active', 'sold', 'privacy-policy']) {
        fs.mkdirSync(path.join(outputDir, route), { recursive: true })
        fs.writeFileSync(path.join(outputDir, route, 'index.html'), html)
      }
    },
  }],
  base: '/',
  server: {
    port: 4173,
    strictPort: true,
    proxy: {
      '/v1': {
        target: process.env.VITE_API_PROXY || 'http://127.0.0.1:2002',
        changeOrigin: true,
      },
    },
  },
})
