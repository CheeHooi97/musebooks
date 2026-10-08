import fs from 'node:fs/promises'
import path from 'node:path'
import { pageSeo, SITE_URL, normalizeSiteURL } from '../src/lib/seo.js'
import { renderContent, json } from './seo-content.mjs'

const escape = value => String(value).replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&apos;' }[char]))
export function renderSeo(html, pathname, book, profile, siteURL = SITE_URL) {
  const seo = pageSeo(pathname, book, profile, siteURL)
  const meta = (key, value, attribute = 'name') => `<meta ${attribute}="${key}" content="${escape(value)}"/>`
  const tags = [meta('description', seo.description), meta('robots', seo.noindex ? 'noindex,follow' : 'index,follow,max-image-preview:large'), `<link rel="canonical" href="${escape(seo.url)}"/>`,
    ...Object.entries({ title: seo.title, description: seo.description, url: seo.url, type: 'website', site_name: 'MuseBooks', ...(seo.image ? { image: seo.image } : {}) }).map(([key, value]) => meta(`og:${key}`, value, 'property')),
    ...Object.entries({ card: seo.image ? 'summary_large_image' : 'summary', title: seo.title, description: seo.description, ...(seo.image ? { image: seo.image } : {}) }).map(([key, value]) => meta(`twitter:${key}`, value)),
    `<script id="musebooks-seo-jsonld" type="application/ld+json">${json(seo.structuredData)}</script>`].join('\n')
  return html.replace(/<title>[\s\S]*?<\/title>/, () => `<title>${escape(seo.title)}</title>`).replace(/<meta name="description"[^>]*\/?\s*>/, '').replace('</head>', () => `${tags}\n</head>`)
}
export function sitemapXML(paths, siteURL = SITE_URL) {
  return `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${[...new Set(paths)].map(route => `<url><loc>${escape(siteURL + route)}</loc></url>`).join('')}</urlset>\n`
}
export async function buildSeo(outputDir, { fetcher = fetch, apiURL = process.env.SEO_API_URL || 'https://musebooks.my', siteURL = SITE_URL } = {}) {
  siteURL = normalizeSiteURL(siteURL)
  const template = await fs.readFile(path.join(outputDir, 'index.html'), 'utf8')
  const api = apiURL.replace(/\/$/, '')
  const loadAll = async endpoint => {
    const items = []
    let totalPages = 1
    for (let page = 1; page <= totalPages; page++) {
      const response = await fetcher(`${api}/v1/${endpoint}${endpoint.includes('?') ? '&' : '?'}pageSize=50&page=${page}`, { signal: AbortSignal.timeout(30000) })
      if (!response.ok) throw new Error(`SEO ${endpoint} request failed: ${response.status}`)
      const data = await response.json()
      if (!Array.isArray(data.items) || !Number.isInteger(data.totalPages) || data.totalPages < 0) throw new Error(`Invalid SEO ${endpoint} response`)
      totalPages = data.totalPages
      items.push(...data.items)
    }
    return items
  }
  const [books, models, publishers, active, sold] = await Promise.all([
    loadAll('books'), loadAll('models'), loadAll('publishers'), loadAll('listings?status=active'), loadAll('listings?status=sold'),
  ])
  const routes = []
  const write = async (route, data = {}) => {
    const parts = route.slice(1).split('/').filter(Boolean).map(decodeURIComponent)
    if (!route.startsWith('/') || parts.length > 2 || parts.some(part => part === '.' || part === '..' || /[\/\\\u0000]/.test(part))) throw new Error(`Unsafe SEO route: ${route}`)
    if (routes.includes(route)) throw new Error(`Duplicate SEO route: ${route}`)
    routes.push(route)
    // Nginx resolves decoded URI paths. Keep encoded URLs, decoded disk names.
    const directory = path.join(outputDir, ...parts)
    const bootstrap = data.book ? `<script id="musebooks-bootstrap" type="application/json">${json({ book: data.book })}</script>` : ''
    const html = renderSeo(template, route, data.book, data.profile, siteURL).replace('<div id="root"></div>', () => `<div id="root">${renderContent(route, data)}</div>${bootstrap}`)
    await fs.mkdir(directory, { recursive: true })
    await fs.writeFile(path.join(directory, 'index.html'), html)
  }
  await write('/', { books })
  await write('/models', { profiles: models })
  await write('/publishers', { profiles: publishers })
  await write('/active', { listings: active })
  await write('/sold', { listings: sold })
  await write('/about')
  await write('/privacy-policy')
  for (const [kind, profiles] of [['models', models], ['publishers', publishers]]) {
    for (const profile of profiles) {
      if (!profile.id || !profile.name) throw new Error(`Invalid ${kind} profile`)
      const related = books.filter(book => kind === 'models' ? book.models?.some(model => model.id === profile.id) : book.editions?.some(edition => edition.publisherProfile?.id === profile.id))
      await write(`/${kind}/${encodeURIComponent(profile.id)}`, { profile: { ...profile, books: related }, books: related })
    }
  }
  for (const book of books) {
    if (!book.slug || !book.originalTitle) throw new Error('Catalog record missing a slug or title')
    await write(`/books/${encodeURIComponent(book.slug)}`, { book })
  }
  await write('/404')
  await fs.writeFile(path.join(outputDir, '404.html'), await fs.readFile(path.join(outputDir, '404/index.html')))
  await fs.writeFile(path.join(outputDir, 'sitemap.xml'), sitemapXML(routes.filter(route => route !== '/404'), siteURL))
  await fs.writeFile(path.join(outputDir, 'robots.txt'), `User-agent: *\nAllow: /\nDisallow: /v1/\nAllow: /v1/books\nAllow: /v1/models\nAllow: /v1/publishers\nAllow: /v1/listings\nAllow: /v1/origins\nAllow: /v1/sources\n\nSitemap: ${siteURL}/sitemap.xml\n`)
  console.log(`SEO: rendered ${books.length} photobook pages and ${routes.length - 1} sitemap URLs`)
}
