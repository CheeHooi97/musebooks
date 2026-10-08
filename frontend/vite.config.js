import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'node:fs'
import path from 'node:path'
import { buildSeo } from './scripts/seo-build.mjs'

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
      if (!mobileBuild) { await buildSeo(outputDir, { siteURL }); return }
      const html = fs.readFileSync(path.join(outputDir, 'index.html'), 'utf8')
      for (const route of ['models', 'publishers', 'active', 'sold', 'privacy-policy', 'about']) {
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
