import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'node:fs'
import path from 'node:path'
import { buildSeo } from './scripts/seo-build.mjs'

// Each release gets a new service worker, so open pages are offered the update.
export function stampServiceWorker(dir, build = `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`) {
  const file = path.join(dir, 'sw.js')
  const source = fs.readFileSync(file, 'utf8')
  if (!source.includes('__MUSEBOOKS_BUILD__')) throw new Error('sw.js has no build stamp placeholder')
  fs.writeFileSync(file, source.replace('__MUSEBOOKS_BUILD__', build))
  return build
}

let outputDir = 'dist'
let mobileBuild = false
let siteURL = 'https://musebooks.my'

export default defineConfig({
  plugins: [react(), {
    name: 'static-route-entries',
    configResolved(config) {
      outputDir = path.resolve(config.root, config.build.outDir)
      siteURL = (config.env.VITE_SITE_URL || siteURL).replace(/\/+$/, "")
      mobileBuild = config.mode === 'mobile' || process.env.VITE_APP_TARGET === 'mobile'
    },
    transformIndexHtml(html) {
      return mobileBuild ? html.replace(/<!-- Google tag \(gtag.js\) -->[\s\S]*?<!-- End Google tag -->\s*/, '') : html
    },
    async closeBundle() {
      if (!mobileBuild) { stampServiceWorker(outputDir); await buildSeo(outputDir, { siteURL }); return }
      const html = fs.readFileSync(path.join(outputDir, 'index.html'), 'utf8')
      for (const route of ['books', 'models', 'publishers', 'active', 'sold', 'japan', 'saved', 'privacy-policy', 'about', 'login', 'register', 'verify-email', 'forgot-password', 'reset-password', 'account']) {
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
