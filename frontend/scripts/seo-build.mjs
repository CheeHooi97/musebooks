import fs from 'node:fs/promises'
import path from 'node:path'
import { createHash } from 'node:crypto'
import { isCorruptText, pageSeo, SITE_URL, normalizeSiteURL } from '../src/lib/seo.js'
import { renderContent, json } from './seo-content.mjs'
import { apiCatalog, atomFeed, llmsFullTxt, llmsTxt, markdownURL, newestBooks, openAPI, pageMarkdown, robotsTxt } from './agent-files.mjs'
import { CATALOG_LANGUAGES, hasLanguageEditions, languageAlternates, languagePath } from '../src/lib/catalog-languages.js'
import { renderLocalizedCatalog, localizedMarkdown } from './localized-catalog.mjs'
import { homeSummary } from '../src/lib/catalog.js'
import { GUIDES } from '../src/lib/guides.js'

const escape = value => String(value).replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&apos;' }[char]))
// The API returns R2 images as media Worker URLs whose signature expires, but
// prerendered HTML lives until the next deploy. Point those images at the
// API redirect, which signs a fresh URL on every request.
const MEDIA_HOSTS = (process.env.SEO_MEDIA_HOSTS || 'media.musebooks.my,img.musecards.my').split(',').map(host => host.trim().toLowerCase()).filter(Boolean)
export function stableMediaURLs(value, siteURL = SITE_URL) {
  if (Array.isArray(value)) return value.map(item => stableMediaURLs(item, siteURL))
  if (value && typeof value === 'object') return Object.fromEntries(Object.entries(value).map(([key, item]) => [key, stableMediaURLs(item, siteURL)]))
  if (typeof value !== 'string' || !value.startsWith('https://')) return value
  let parsed
  try { parsed = new URL(value) } catch { return value }
  if (!MEDIA_HOSTS.includes(parsed.hostname.toLowerCase())) return value
  parsed.search = ''
  return `${normalizeSiteURL(siteURL)}/v1/catalog/media/redirect?${new URLSearchParams({ source: parsed.href })}`
}
export function renderSeo(html, pathname, book, profile, siteURL = SITE_URL) {
  const seo = pageSeo(pathname, book, profile, siteURL)
  const meta = (key, value, attribute = 'name') => `<meta ${attribute}="${key}" content="${escape(value)}"/>`
  const tags = [meta('description', seo.description), meta('robots', seo.noindex ? 'noindex,follow' : 'index,follow,max-image-preview:large'), `<link rel="canonical" href="${escape(seo.url)}"/>`,
    ...(seo.noindex ? [] : languageAlternates(pathname, siteURL).map(item => `<link rel="alternate" hreflang="${item.code}" href="${escape(item.url)}"/>`)),
    ...(seo.noindex ? [] : [`<link rel="alternate" type="text/markdown" href="${escape(markdownURL(seo.url, siteURL))}"/>`]),
    ...Object.entries({ title: seo.title, description: seo.description, url: seo.url, type: 'website', site_name: 'MuseBooks', ...(seo.image ? { image: seo.image } : {}) }).map(([key, value]) => meta(`og:${key}`, value, 'property')),
    ...Object.entries({ card: seo.image ? 'summary_large_image' : 'summary', title: seo.title, description: seo.description, ...(seo.image ? { image: seo.image } : {}) }).map(([key, value]) => meta(`twitter:${key}`, value)),
    `<script id="musebooks-seo-jsonld" type="application/ld+json">${json(seo.structuredData)}</script>`].join('\n')
  return html.replace(/<title>[\s\S]*?<\/title>/, () => `<title>${escape(seo.title)}</title>`).replace(/<meta name="description"[^>]*\/?\s*>/, '').replace('</head>', () => `${tags}\n</head>`)
}
// Profile slugs are "model-" + sha256 of the lower-cased name (CatalogIdentity in the API).
export const modelSlug = name => `model-${createHash('sha256').update(String(name).trim().toLowerCase()).digest('hex')}`
export function aliasRedirect(url, name) {
  return `<!doctype html><html lang="en"><head><meta charset="utf-8"/><title>${escape(name)} — MuseBooks</title><meta name="robots" content="noindex,follow"/><link rel="canonical" href="${escape(url)}"/><meta http-equiv="refresh" content="0;url=${escape(url)}"/><script>location.replace(${json(url)})</script></head><body><p>This profile moved to <a href="${escape(url)}">${escape(name)}</a>.</p></body></html>\n`
}
export function sitemapXML(paths, siteURL = SITE_URL, lastmods = new Map()) {
  return `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${[...new Set(paths)].map(route => `<url><loc>${escape(siteURL + route)}</loc>${lastmods.get(route) ? `<lastmod>${lastmods.get(route)}</lastmod>` : ''}</url>`).join('')}</urlset>\n`
}
export function renderPublishedPage(template, route, data = {}, siteURL = SITE_URL) {
  if (!template.includes('<div id="root">') || !template.includes('</body>')) throw new Error('Invalid built page template')
  data = stableMediaURLs(data, siteURL)
  const clean = template
    .replace(/<script\b[^>]*id=["']musebooks-seo-jsonld["'][^>]*>[\s\S]*?<\/script>/gi, '')
    .replace(/<meta\b[^>]*(?:name=["'](?:description|robots|twitter:[^"']+)["']|property=["']og:[^"']+["'])[^>]*>/gi, '')
    .replace(/<link\b[^>]*rel=["']canonical["'][^>]*>/gi, '')
    .replace(/<link\b[^>]*type=["']text\/markdown["'][^>]*>/gi, '')
    .replace(/<link\b[^>]*hreflang=["'][^"']+["'][^>]*>/gi, '')
    .replace(/(<div id="root">)[\s\S]*(<\/body>)/, '$1</div>$2')
  const bootstrap = data.book ? `<script id="musebooks-bootstrap" type="application/json">${json({ book: data.book })}</script>` : ''
  return renderSeo(clean, route, data.book, data.profile, siteURL)
    .replace('<div id="root"></div>', () => `<div id="root">${renderContent(route, data)}</div>${bootstrap}`)
}
export async function buildSeo(outputDir, { fetcher = fetch, apiURL = process.env.SEO_API_URL || 'https://musebooks.my', siteURL = SITE_URL } = {}) {
  siteURL = normalizeSiteURL(siteURL)
  const template = await fs.readFile(path.join(outputDir, 'index.html'), 'utf8')
  const api = apiURL.replace(/\/$/, '')
  const loadAll = async endpoint => {
    const items = new Map()
    let totalPages = 1
    for (let page = 1; page <= totalPages; page++) {
      const response = await fetcher(`${api}/v1/${endpoint}${endpoint.includes('?') ? '&' : '?'}pageSize=50&page=${page}`, { signal: AbortSignal.timeout(30000) })
      if (!response.ok) throw new Error(`SEO ${endpoint} request failed: ${response.status}`)
      const data = await response.json()
      if (!Array.isArray(data.items) || !Number.isInteger(data.totalPages) || data.totalPages < 0) throw new Error(`Invalid SEO ${endpoint} response`)
      totalPages = data.totalPages
      for (const item of stableMediaURLs(data.items, siteURL)) {
        const identity = endpoint === 'books' ? item.slug : item.id
        if (!identity) throw new Error(`SEO ${endpoint} record missing identity`)
        items.set(identity, item)
      }
    }
    return [...items.values()]
  }
  const [books, models, publishers, active, sold] = await Promise.all([
    loadAll('books'), loadAll('models'), loadAll('publishers'), loadAll('listings?status=active'), loadAll('listings?status=sold'),
  ])
  const routes = []
  // The date a record last changed, only where the API reports one.
  const lastmods = new Map()
  const hidden = new Set()
  const changed = list => list.map(item => String(item.updatedAt || '').slice(0, 10)).filter(Boolean).sort().at(-1)
  const write = async (route, data = {}) => {
    const parts = route.slice(1).split('/').filter(Boolean).map(decodeURIComponent)
    if (!route.startsWith('/') || parts.length > 2 || parts.some(part => part === '.' || part === '..' || /[\/\\\u0000]/.test(part))) throw new Error(`Unsafe SEO route: ${route}`)
    if (routes.includes(route)) throw new Error(`Duplicate SEO route: ${route}`)
    routes.push(route)
    const damaged = isCorruptText(data.book?.originalTitle) || isCorruptText(data.profile?.name)
    if (damaged) hidden.add(route)
    const lastmod = data.book ? changed([data.book]) : data.profile ? changed(data.books || []) : ''
    if (lastmod) lastmods.set(route, lastmod)
    // Nginx resolves decoded URI paths. Keep encoded URLs, decoded disk names.
    const directory = path.join(outputDir, ...parts)
    const bootstrap = data.book ? `<script id="musebooks-bootstrap" type="application/json">${json({ book: data.book })}</script>` : ''
    const html = renderSeo(template, route, data.book, data.profile, siteURL).replace('<div id="root"></div>', () => `<div id="root">${renderContent(route, data)}</div>${bootstrap}`)
    await fs.mkdir(directory, { recursive: true })
    await fs.writeFile(path.join(directory, 'index.html'), html)
    // Markdown twin beside the page directory: /about -> /about.md, / -> /index.md.
    const markdown = route === '/404' ? '' : pageMarkdown(route, data, siteURL)
    if (markdown) await fs.writeFile(parts.length ? path.join(outputDir, ...parts.slice(0, -1), `${parts.at(-1)}.md`) : path.join(outputDir, 'index.md'), markdown)
    if (hasLanguageEditions(route)) {
      for (const language of CATALOG_LANGUAGES.filter(item => item.segment)) {
        const localized = languagePath(route, language.code)
        const localizedParts = [language.segment, ...parts]
        await fs.mkdir(path.join(outputDir, ...localizedParts), { recursive: true })
        await fs.writeFile(path.join(outputDir, ...localizedParts, 'index.html'), renderLocalizedCatalog(template, route, data, language.code, siteURL))
        await fs.writeFile(path.join(outputDir, ...localizedParts.slice(0, -1), `${localizedParts.at(-1)}.md`), localizedMarkdown(route, data, language.code, siteURL))
        routes.push(localized)
        if (damaged) hidden.add(localized)
        if (lastmod) lastmods.set(localized, lastmod)
      }
    }
  }
  await write('/', { books, totals: { models: models.length, publishers: publishers.length } })
  await write('/books', { books })
  await write('/saved')
  for (const route of ['/login', '/register', '/verify-email', '/forgot-password', '/reset-password', '/account']) await write(route)
  await write('/models', { profiles: models })
  await write('/publishers', { profiles: publishers })
  await write('/active', { listings: active })
  await write('/sold', { listings: sold })
  await write('/japan')
  for (const route of Object.keys(GUIDES)) await write(route)
  await write('/about', { books, totals: { models: models.length, publishers: publishers.length } })
  await write('/privacy-policy')
  for (const [kind, profiles] of [['models', models], ['publishers', publishers]]) {
    for (const profile of profiles) {
      if (!profile.id || !profile.name) throw new Error(`Invalid ${kind} profile`)
      const related = books.filter(book => kind === 'models' ? [...(book.models || []), ...(book.coverModels || [])].some(model => model.id === profile.id) : book.editions?.some(edition => edition.publisherProfile?.id === profile.id))
      await write(`/${kind}/${encodeURIComponent(profile.id)}`, { profile: { ...profile, books: related }, books: related })
    }
  }
  const byPerson = new Map()
  for (const { book } of newestBooks(books, books.length)) {
    for (const person of book.models || []) byPerson.set(person.id, [...(byPerson.get(person.id) || []), book])
  }
  for (const book of books) {
    if (!book.slug || !book.originalTitle) throw new Error('Catalog record missing a slug or title')
    const person = (book.models || []).find(item => (byPerson.get(item.id) || []).some(other => other.slug !== book.slug))
    const related = person ? { person, books: byPerson.get(person.id).filter(other => other.slug !== book.slug).slice(0, 6) } : undefined
    await write(`/books/${encodeURIComponent(book.slug)}`, { book, related })
  }
  // Names merged into a model (person_aliases) keep their old profile URLs as
  // redirects to the canonical profile; they stay out of the sitemap.
  const aliasRoutes = new Set()
  for (const profile of models) {
    for (const alias of String(profile.aliases || '').split(',').map(name => name.trim()).filter(Boolean)) {
      const slug = modelSlug(alias)
      const route = `/models/${slug}`
      if (slug === profile.id || routes.includes(route) || aliasRoutes.has(route)) continue
      aliasRoutes.add(route)
      await fs.mkdir(path.join(outputDir, 'models', slug), { recursive: true })
      await fs.writeFile(path.join(outputDir, 'models', slug, 'index.html'), aliasRedirect(`${siteURL}/models/${encodeURIComponent(profile.id)}`, profile.name))
    }
  }
  await write('/404')
  await fs.writeFile(path.join(outputDir, '404.html'), await fs.readFile(path.join(outputDir, '404/index.html')))
  const privateRoutes = new Set(['/404', '/saved', '/login', '/register', '/verify-email', '/forgot-password', '/reset-password', '/account'])
  await fs.writeFile(path.join(outputDir, 'sitemap.xml'), sitemapXML(routes.filter(route => !privateRoutes.has(route) && !hidden.has(route)), siteURL, lastmods))
  await fs.writeFile(path.join(outputDir, 'robots.txt'), robotsTxt(siteURL))
  await fs.writeFile(path.join(outputDir, 'home.json'), JSON.stringify(homeSummary(books, newestBooks(books, 8).map(item => item.book))))
  const catalog = { books, models, publishers }
  await fs.writeFile(path.join(outputDir, 'llms.txt'), llmsTxt(siteURL, catalog))
  await fs.writeFile(path.join(outputDir, 'llms-full.txt'), llmsFullTxt(siteURL, catalog))
  await fs.writeFile(path.join(outputDir, 'feed.xml'), atomFeed(siteURL, books))
  await fs.writeFile(path.join(outputDir, 'openapi.json'), openAPI(siteURL))
  await fs.mkdir(path.join(outputDir, '.well-known'), { recursive: true })
  await fs.writeFile(path.join(outputDir, '.well-known', 'api-catalog'), apiCatalog(siteURL))
  console.log(`SEO: rendered ${books.length} photobook pages and ${routes.length - 1} sitemap URLs`)
}
