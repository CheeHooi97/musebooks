import fs from 'node:fs/promises'
import path from 'node:path'
import { pageSeo, SITE_URL } from '../src/lib/seo.js'

const escape = value => String(value).replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&apos;' }[char]))
export function renderSeo(html, pathname, book, profile) {
  const seo = pageSeo(pathname, book, profile)
  const meta = (key, value, attribute = 'name') => `<meta ${attribute}="${key}" content="${escape(value)}"/>`
  const tags = [meta('description', seo.description), meta('robots', 'index,follow,max-image-preview:large'), `<link rel="canonical" href="${escape(seo.url)}"/>`,
    ...Object.entries({ title: seo.title, description: seo.description, url: seo.url, type: 'website', site_name: 'MuseBooks', ...(seo.image ? { image: seo.image } : {}) }).map(([key, value]) => meta(`og:${key}`, value, 'property')),
    ...Object.entries({ card: seo.image ? 'summary_large_image' : 'summary', title: seo.title, description: seo.description, ...(seo.image ? { image: seo.image } : {}) }).map(([key, value]) => meta(`twitter:${key}`, value)),
    `<script id="musebooks-seo-jsonld" type="application/ld+json">${JSON.stringify(seo.structuredData).replace(/</g, '\\u003c')}</script>`].join('\n')
  return html.replace(/<title>[\s\S]*?<\/title>/, `<title>${escape(seo.title)}</title>`).replace(/<meta name="description"[^>]*\/?\s*>/, '').replace('</head>', `${tags}\n</head>`)
}
export function sitemapXML(paths) {
  return `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${[...new Set(paths)].map(route => `<url><loc>${escape(SITE_URL + route)}</loc></url>`).join('')}</urlset>\n`
}
export async function buildSeo(outputDir) {
  const template = await fs.readFile(path.join(outputDir, 'index.html'), 'utf8')
  const api = (process.env.SEO_API_URL || 'https://musebooks.my').replace(/\/$/, '')
  const load = async page => {
    const response = await fetch(`${api}/v1/books?pageSize=50&page=${page}`, { signal: AbortSignal.timeout(30000) })
    if (!response.ok) throw new Error(`SEO catalog request failed: ${response.status}`)
    const data = await response.json()
    if (!Array.isArray(data.items) || !Number.isInteger(data.totalPages)) throw new Error('Invalid SEO catalog response')
    return data
  }
  const first = await load(1)
  const books = [...first.items]
  for (let page = 2; page <= first.totalPages; page++) books.push(...(await load(page)).items)
  const routes = ['/', '/models', '/publishers', '/active', '/sold', '/privacy-policy']
  for (const kind of ['models', 'publishers']) {
    let page = 1
    let totalPages = 1
    do {
      const response = await fetch(`${api}/v1/${kind}?pageSize=50&page=${page}`, { signal: AbortSignal.timeout(30000) })
      if (!response.ok) throw new Error(`SEO ${kind} request failed: ${response.status}`)
      const data = await response.json()
      if (!Array.isArray(data.items) || !Number.isInteger(data.totalPages)) throw new Error(`Invalid ${kind} directory response`)
      totalPages = data.totalPages
      for (const profile of data.items) {
        const route = `/${kind}/${encodeURIComponent(profile.id)}`
        routes.push(route)
        const directory = path.join(outputDir, kind, encodeURIComponent(profile.id))
        await fs.mkdir(directory, { recursive: true })
        await fs.writeFile(path.join(directory, 'index.html'), renderSeo(template, route, undefined, profile))
      }
      page++
    } while (page <= totalPages)
  }
  for (const book of books) {
    if (!book.slug || !book.originalTitle) throw new Error('Catalog record missing a slug or title')
    const route = `/books/${encodeURIComponent(book.slug)}`
    routes.push(route)
    const directory = path.join(outputDir, 'books', encodeURIComponent(book.slug))
    await fs.mkdir(directory, { recursive: true })
    await fs.writeFile(path.join(directory, 'index.html'), renderSeo(template, route, book))
  }
  for (const route of routes.filter(route => !route.startsWith('/books/') && route.split('/').length <= 2)) {
    const directory = path.join(outputDir, route.slice(1))
    await fs.mkdir(directory, { recursive: true })
    await fs.writeFile(path.join(directory, 'index.html'), renderSeo(template, route))
  }
  await fs.writeFile(path.join(outputDir, 'sitemap.xml'), sitemapXML(routes))
  await fs.writeFile(path.join(outputDir, 'robots.txt'), `User-agent: *\nAllow: /\nDisallow: /v1/\n\nSitemap: ${SITE_URL}/sitemap.xml\n`)
  console.log(`SEO: generated ${books.length} photobook pages and ${routes.length} sitemap URLs`)
}
