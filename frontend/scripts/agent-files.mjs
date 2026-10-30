// Machine-readable companions to the prerendered catalog, matching MuseCards'
// agent access: markdown twins of indexable pages, llms.txt, an Atom feed of
// new publications, an OpenAPI description of the public API, an RFC 9727 API
// catalog, and a robots.txt that states the crawler policy as content signals.
import { publicationDate } from '../src/lib/seo.js'
import { ABOUT_SECTIONS } from '../src/lib/about.js'
import { bookAnswers, bookFactSummary, catalogCounts, CATALOG_DEFINITION, longDate, profileFactSummary } from '../src/lib/book-answers.js'
import { editionListings, formatPrice, priceLabel } from '../src/lib/price-policy.js'
import { CATALOG_LANGUAGES, languagePath } from '../src/lib/catalog-languages.js'
import { GUIDES } from '../src/lib/guides.js'

const SUMMARY = 'Source-backed catalog of model, idol, influencer and celebrity photobooks and magazine issues: works, physical and digital editions, publishers, featured people, and source-linked retail offers, marketplace asking prices and confirmed completed sales. Many records are gravure photobooks; some are intended for adult readers.'
const NOTES = [
  'Retail prices, marketplace asking prices, auction bids, and confirmed completed sales are different observations. An ended listing alone is not a completed sale.',
  'Prices keep their original currency and observation date. They are not valuations or guarantees of current availability; check the linked source.',
  'A work is a photobook or magazine issue; each edition records its own format, publisher, publication date, language and ISBN. Physical and digital editions are separate.',
  'Magazine issues credit cover models separately from other featured people.',
  'Facts that are not recorded are unknown, not absent. Catalog coverage is incomplete.',
]

const oneLine = value => String(value ?? '').replace(/\s+/g, ' ').trim()
const text = value => oneLine(value).replace(/([\\`*_[\]<>])/g, '\\$1')
const link = (label, url) => `[${text(label)}](${String(url).replace(/[()\s]/g, char => `%${char.charCodeAt(0).toString(16).toUpperCase().padStart(2, '0')}`)})`
const safeURL = value => /^https?:\/\//i.test(value || '') ? value : ''
const xml = value => oneLine(value).replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&apos;' }[char]))

export function markdownURL(pageURL, siteURL) {
  return pageURL === `${siteURL}/` || pageURL === siteURL ? `${siteURL}/index.md` : `${pageURL}.md`
}

// Newest first by the latest recorded publication date of any edition.
export function newestBooks(books, limit) {
  const dated = books.map(book => ({ book, date: (book.editions || []).map(publicationDate).filter(Boolean).sort().at(-1) || '' })).filter(item => item.date)
  return dated.sort((a, b) => b.date.localeCompare(a.date) || a.book.slug.localeCompare(b.book.slug)).slice(0, limit)
}

const bookURL = (siteURL, book) => `${siteURL}/books/${encodeURIComponent(book.slug)}`
const bookLine = (siteURL, book) => `- ${link(book.originalTitle, bookURL(siteURL, book))}${book.englishTitle && book.englishTitle !== book.originalTitle ? ` — ${text(book.englishTitle)}` : ''}`
const facts = pairs => pairs.filter(([, value]) => value).map(([label, value]) => `- ${label}: ${text(value)}`)

function bookMarkdown(book, siteURL) {
  const lines = [`# ${text(book.originalTitle)}`, '', `Source: ${bookURL(siteURL, book)}`, '']
  if (book.englishTitle) lines.push(`English title: ${text(book.englishTitle)}`, '')
  lines.push(text(bookFactSummary(book)), '')
  if (book.summary) lines.push(text(book.summary), '')
  const people = book.publicationType === 'magazine_issue' && book.coverModels?.length ? book.coverModels : book.models || []
  if (people.length) lines.push(`## ${book.publicationType === 'magazine_issue' ? 'Cover models' : 'Featured people'}`, '', ...people.map(person => `- ${link(person.name, `${siteURL}/models/${encodeURIComponent(person.id)}`)}`), '')
  const answers = bookAnswers(book)
  if (answers.length) lines.push('## Questions', '', ...answers.flatMap(({ question, answer }) => [`### ${text(question)}`, '', text(answer), '']))
  lines.push('## Editions', '')
  for (const edition of book.editions || []) {
    lines.push(`### ${text(edition.editionLabel || 'Edition')}`, '')
    lines.push(...facts([['Format', edition.format], ['Series', edition.seriesName], ['Publisher', edition.publisher], ['Published', publicationDate(edition)], ['ISBN', edition.isbn], ['Language', edition.language], ['Pages', edition.pageCount], ['Dimensions', edition.dimensions], ['Market', edition.editionMarket], ['Photographer', book.photographer], ['Origin', book.origin?.name]]))
    if (edition.publisherProfile?.id) lines.push(`- Publisher profile: ${link(edition.publisherProfile.name, `${siteURL}/publishers/${encodeURIComponent(edition.publisherProfile.id)}`)}`)
    if (safeURL(edition.metadataSourceUrl)) lines.push(`- Metadata source: ${edition.metadataSourceUrl}`)
    lines.push('')
    if (edition.contentSummary) lines.push(text(edition.contentSummary), '')
    const listings = editionListings({ ...edition, listings: edition.listings || [] })
    if (listings.length) {
      lines.push('#### Source-backed prices', '', 'Original currencies. Availability reflects the last recorded observation.', '')
      lines.push(...listings.map(item => `- ${text(item.source?.name)}: ${priceLabel(edition, item)}, ${formatPrice(item.priceMinor, item.currency)}. ${text(item.condition || 'Condition not recorded')}. Observed ${item.observedAt ? longDate(item.observedAt.slice(0, 10)) : 'date not recorded'}.${safeURL(item.url) ? ` ${link('View source', item.url)}` : ''}`), '')
    }
  }
  return lines
}

export function pageMarkdown(route, { book, profile, books = [], profiles = [], listings = [], totals = {} } = {}, siteURL) {
  const url = route === '/' ? `${siteURL}/` : `${siteURL}${route}`
  let lines
  if (book) {
    lines = bookMarkdown(book, siteURL)
  } else if (profile) {
    lines = [`# ${text(profile.name)}`, '', `Source: ${url}`, '', text(profileFactSummary(profile, route.startsWith('/models/') ? 'models' : 'publishers', books)), '', ...facts([['Original name', profile.originalName], ['English name', profile.englishName], ['Also recorded as', profile.aliases]])]
    if (safeURL(profile.officialUrl)) lines.push(`- Profile source: ${profile.officialUrl}`)
    lines.push('', `## Publications (${books.length})`, '', ...books.map(item => bookLine(siteURL, item)))
  } else if (route === '/') {
    lines = ['# MuseBooks photobook and magazine catalog', '', `Source: ${url}`, '', CATALOG_DEFINITION, '', catalogCounts(books, totals.models, totals.publishers), '', '## Newest publications', '',
      ...newestBooks(books, 100).map(({ book, date }) => `${bookLine(siteURL, book)} — ${date}`), '', `Every catalog page is listed in ${siteURL}/sitemap.xml.`]
  } else if (route === '/books') {
    lines = ['# Browse photobooks and magazine issues', '', `Source: ${url}`, '', ...books.map(item => bookLine(siteURL, item))]
  } else if (route === '/models' || route === '/publishers') {
    lines = [`# ${route === '/models' ? 'Models & featured people' : 'Photobook publishers'}`, '', `Source: ${url}`, '', ...profiles.map(entry => `- ${link(entry.name, `${siteURL}${route}/${encodeURIComponent(entry.id)}`)}`)]
  } else if (route === '/active' || route === '/sold') {
    lines = [`# ${route === '/active' ? 'Active photobook listings' : 'Sold photobook listings'}`, '', `Source: ${url}`, '',
      route === '/sold' ? 'Confirmed completed physical marketplace sales. Ended offers are separate.' : 'Available at the last recorded observation; check the source before purchasing.', '',
      ...listings.map(item => `- ${link(item.workTitle, `${siteURL}/books/${encodeURIComponent(item.workSlug)}`)} — ${text(item.editionLabel)}, ${text(item.source?.name)}, ${formatPrice(item.priceMinor, item.currency)}, ${text(item.condition || 'Condition not recorded')}. Observed ${item.observedAt ? longDate(item.observedAt.slice(0, 10)) : 'date not recorded'}.${safeURL(item.url) ? ` ${link('View source', item.url)}` : ''}`)]
  } else if (GUIDES[route]) {
    const guide = GUIDES[route].en
    lines = [`# ${guide.title}`, '', `Source: ${url}`, '', guide.description, '', ...guide.sections.flatMap(([title, body]) => [`## ${title}`, '', body, ''])]
  } else if (route === '/about') {
    lines = ['# About MuseBooks', '', `Source: ${url}`, '', ...(books.length ? [catalogCounts(books, totals.models, totals.publishers), ''] : []), ...ABOUT_SECTIONS.flatMap(([title, body]) => [`## ${title}`, '', body, ''])]
  } else if (route === '/japan') {
    lines = ['# Japan marketplace listings', '', `Source: ${url}`, '', 'A snapshot from Yahoo! JAPAN Auctions, Yahoo! Flea Market, and Rakuma. Captured bids, fixed asks, and completed prices are shown separately. Bundle prices apply to the whole listing. Unmatched records are shown separately from verified catalog books. Open a source listing to check its current status.']
  } else if (route === '/privacy-policy') {
    lines = ['# Privacy Policy', '', `Source: ${url}`, '', 'MuseBooks stores saved collections and interface preferences in browser storage on your device. The website uses Google Analytics and displays third-party advertising, which is excluded from the Android and iOS apps. For privacy questions, email musecards67@gmail.com.']
  } else {
    return ''
  }
  return `${lines.join('\n').replace(/\n{3,}/g, '\n\n').trim()}\n`
}

function llmsHeader(siteURL, { books, models, publishers }) {
  return [
    '# MuseBooks', '', `> ${SUMMARY}`, '',
    `The catalog records ${books.length} publications, ${models.length} featured people and ${publishers.length} publishers.`, '',
    '## Key pages',
    `- [About and methodology](${siteURL}/about): scope, record types, sources, price definitions and corrections`,
    `- [Catalog](${siteURL}/): every photobook and magazine issue`,
    `- [Models](${siteURL}/models): featured people and cover models`,
    `- [Publishers](${siteURL}/publishers): photobook and magazine publishers`,
    `- [Active listings](${siteURL}/active): offers available at the last observation`,
    `- [Sold listings](${siteURL}/sold): confirmed completed physical sales`,
    `- [Japan marketplace](${siteURL}/japan): Yahoo! JAPAN Auctions, Yahoo! Flea Market and Rakuma snapshot`, '',
    '## Catalog languages',
    ...CATALOG_LANGUAGES.filter(item => item.segment).map(item => `- [${item.label}](${siteURL}${languagePath('/', item.code)}): translated catalog, publication, model and publisher documents; append .md for Markdown.`),
    '- Publication titles and bibliographic facts retain their recorded language. Detailed prices and sales comparisons are linked in English.', '',
    '## URL patterns',
    `- Publication: ${siteURL}/books/{slug}`,
    `- Featured person: ${siteURL}/models/{id}`,
    `- Publisher: ${siteURL}/publishers/{id}`,
    `- Every indexable URL: ${siteURL}/sitemap.xml`,
    `- Markdown version of any indexable page: append .md, for example ${siteURL}/books/{slug}.md (home page: ${siteURL}/index.md). Requests sent with Accept: text/markdown receive it at the page URL.`, '',
    '## Machine-readable access',
    `- [Public catalog API (OpenAPI 3.1)](${siteURL}/openapi.json): read-only JSON for publications, editions, featured people, publishers and listings`,
    `- [New publications feed (Atom)](${siteURL}/feed.xml): the 50 most recent publications by publication date`,
    `- [Full reference text](${siteURL}/llms-full.txt): this file plus the methodology`,
    `- [API catalog](${siteURL}/.well-known/api-catalog): RFC 9727 linkset`, '',
    '## Notes for AI systems', ...NOTES.map(note => `- ${note}`), '',
  ]
}

export function llmsTxt(siteURL, catalog) {
  return [...llmsHeader(siteURL, catalog), '## Newest publications', ...newestBooks(catalog.books, 30).map(({ book, date }) => `${bookLine(siteURL, book)} — ${date}`), ''].join('\n')
}

export function llmsFullTxt(siteURL, catalog) {
  return [...llmsHeader(siteURL, catalog), '## Methodology', '', ...ABOUT_SECTIONS.flatMap(([title, body]) => [`### ${title}`, '', body, '']),
    '## Privacy', '', 'Saved collections and preferences stay in browser storage on the visitor\'s device. The website uses Google Analytics and third-party advertising; the apps exclude ads.', '',
    '## Corrections', '', 'Email musecards67@gmail.com with the MuseBooks page URL, the affected edition or listing, and a supporting publisher or retailer source.', ''].join('\n')
}

export function atomFeed(siteURL, books, now = new Date()) {
  const entries = newestBooks(books, 50).map(({ book, date }) => {
    const url = bookURL(siteURL, book)
    const publisher = (book.editions || []).find(edition => edition.publisher)?.publisher
    const stamp = `${date.length === 4 ? `${date}-01-01` : date.length === 7 ? `${date}-01` : date}T00:00:00Z`
    return `<entry><title>${xml(book.originalTitle + (publisher ? ` · ${publisher}` : ''))}</title><id>${xml(url)}</id><link href="${xml(url)}" rel="alternate" type="text/html"/><published>${stamp}</published><updated>${stamp}</updated><summary>${xml(bookFactSummary(book))}</summary></entry>`
  })
  return `<?xml version="1.0" encoding="UTF-8"?>\n<feed xmlns="http://www.w3.org/2005/Atom"><title>MuseBooks — New photobooks and magazine issues</title><subtitle>Cataloged publications by publication date, newest first.</subtitle><id>${siteURL}/feed.xml</id><updated>${now.toISOString().replace(/\.\d+Z$/, 'Z')}</updated><author><name>MuseBooks</name></author><link href="${siteURL}/feed.xml" rel="self" type="application/atom+xml"/><link href="${siteURL}/" rel="alternate" type="text/html"/>${entries.join('')}</feed>\n`
}

export function apiCatalog(siteURL) {
  return `${JSON.stringify({ linkset: [{
    anchor: `${siteURL}/v1`,
    'service-desc': [{ href: `${siteURL}/openapi.json`, type: 'application/vnd.oai.openapi+json' }],
    'service-doc': [{ href: `${siteURL}/llms.txt`, type: 'text/plain' }, { href: `${siteURL}/about`, type: 'text/html' }],
  }] }, null, 2)}\n`
}

export function robotsTxt(siteURL) {
  return `# AI crawler policy (same as MuseCards, decided 2026-10-11): answer-engine and
# training crawlers such as GPTBot, ClaudeBot, PerplexityBot, Google-Extended and
# CCBot follow the same rules as search engines, so public catalog records can be
# cited. A summary for AI systems is published at /llms.txt.
#
# Content signals (https://contentsignals.org) state the same policy in
# machine-readable form: search indexing, answer-time use (ai-input), and model
# training (ai-train) are all permitted for public catalog records.

User-agent: *
Content-Signal: search=yes, ai-input=yes, ai-train=yes
Allow: /
Disallow: /v1/

# Public read endpoints used to render catalog documents and their images.
Allow: /v1/books
Allow: /v1/editions/
Allow: /v1/models
Allow: /v1/publishers
Allow: /v1/listings
Allow: /v1/marketplace-listings
Allow: /v1/origins
Allow: /v1/sources
Allow: /v1/catalog/media/redirect

Sitemap: ${siteURL}/sitemap.xml
`
}

const page = { type: 'object', required: ['items', 'total', 'totalPages', 'page', 'pageSize'], properties: { items: { type: 'array', items: {} }, total: { type: 'integer' }, totalPages: { type: 'integer' }, page: { type: 'integer' }, pageSize: { type: 'integer', maximum: 50 } } }
const pageOf = ref => ({ ...page, properties: { ...page.properties, items: { type: 'array', items: { $ref: ref } } } })
const query = (name, description, schema = { type: 'string' }) => ({ name, in: 'query', required: false, description, schema })
const pathId = description => ({ name: 'id', in: 'path', required: true, description, schema: { type: 'string' } })
const paging = [query('page', 'Page number, starting at 1.', { type: 'integer', minimum: 1, default: 1 }), query('pageSize', 'Results per page.', { type: 'integer', minimum: 1, maximum: 50, default: 24 })]
const ok = (description, schema) => ({ 200: { description, content: { 'application/json': { schema } } } })
const get = (summary, parameters, responses) => ({ get: { summary, parameters, responses: { ...responses, 404: { description: 'Not found.' } } } })

export function openAPI(siteURL) {
  const directoryBooks = (kind, label) => get(`Publications for one ${label}`, [pathId(`${label} ID`), ...paging, query('format', 'physical or digital.'), query('publicationType', 'photobook or magazine_issue.'), query('language', 'Edition language, such as ja.'), query('year', 'Publication year.')], ok('Publications', pageOf('#/components/schemas/Book')))
  return `${JSON.stringify({
    openapi: '3.1.0',
    info: { title: 'MuseBooks public catalog API', version: '1', description: 'Read-only catalog of photobooks and magazine issues, their editions, featured people, publishers, and source-linked listings. Prices keep their original currency; asking prices and completed sales are distinguished by status and priceCategory.', contact: { email: 'musecards67@gmail.com' } },
    servers: [{ url: siteURL }],
    paths: {
      '/v1/books': get('Search publications', [query('q', 'Title, person or publisher text.'), query('origin', 'Origin country code, such as JP.'), query('publicationType', 'photobook or magazine_issue.'), query('format', 'physical or digital.'), query('language', 'Edition language.'), query('availability', 'Only publications with a listing in this status: active or completed.'), query('year', 'Publication year.'), ...paging], ok('Publications', pageOf('#/components/schemas/Book'))),
      '/v1/books/{id}': get('One publication with editions and listings', [pathId('Publication slug or ID')], ok('Publication', { $ref: '#/components/schemas/Book' })),
      '/v1/editions/{id}': get('One edition', [pathId('Edition ID')], ok('Edition', { $ref: '#/components/schemas/Edition' })),
      '/v1/models': get('Featured people', [query('q', 'Name text.'), ...paging], ok('People', pageOf('#/components/schemas/Profile'))),
      '/v1/models/{id}': get('One featured person', [pathId('Person ID')], ok('Person', { $ref: '#/components/schemas/Profile' })),
      '/v1/models/{id}/books': directoryBooks('models', 'person'),
      '/v1/publishers': get('Publishers', [query('q', 'Name text.'), ...paging], ok('Publishers', pageOf('#/components/schemas/Profile'))),
      '/v1/publishers/{id}': get('One publisher', [pathId('Publisher ID')], ok('Publisher', { $ref: '#/components/schemas/Profile' })),
      '/v1/publishers/{id}/books': directoryBooks('publishers', 'publisher'),
      '/v1/listings': get('Catalog-matched listings', [query('status', 'active (default) or sold.'), query('format', 'physical or digital.'), query('source', 'Source ID.'), query('model', 'Person ID.'), query('publisher', 'Publisher ID.'), query('q', 'Title text.'), ...paging], ok('Listings', pageOf('#/components/schemas/Listing'))),
      '/v1/marketplace-listings': get('Marketplace snapshot, including unmatched listings', [query('region', 'Two-letter region, such as JP.'), query('status', 'all (default), active or sold.'), query('scope', 'offers to exclude completed sales.'), query('format', 'physical or digital.'), query('source', 'Source ID.'), ...paging], ok('Listings', pageOf('#/components/schemas/Listing'))),
      '/v1/origins': get('Origins with catalog records', [], ok('Origins', { type: 'array', items: { type: 'object', properties: { code: { type: 'string' }, name: { type: 'string' }, nativeName: { type: 'string' } } } })),
      '/v1/sources': get('Retail and marketplace sources', [], ok('Sources', { type: 'array', items: { $ref: '#/components/schemas/Source' } })),
      '/v1/catalog/media/redirect': { get: { summary: 'Stable image URL', description: 'Redirects to a cached, signed image URL for a catalog cover. The redirect target expires; this URL does not.', parameters: [{ ...query('source', 'Image URL as stored in the catalog.'), required: true }], responses: { 307: { description: 'Redirect to the image.' }, 404: { description: 'Not a catalog image.' } } } },
    },
    components: { schemas: {
      Source: { type: 'object', properties: { id: { type: 'string' }, name: { type: 'string' }, region: { type: 'string' }, kind: { type: 'string', description: 'bookstore, digital_store, marketplace, auction, flea_market, ...' }, photobookFormat: { type: 'string' } } },
      Listing: { type: 'object', properties: { id: { type: 'string' }, url: { type: 'string', format: 'uri' }, title: { type: 'string' }, format: { type: 'string' }, status: { type: 'string', enum: ['active', 'ended', 'completed', 'unknown'], description: 'completed means a confirmed completed sale; ended alone is not a sale.' }, priceMinor: { type: 'integer', description: 'Price in minor units of currency (JPY and KRW have none).' }, currency: { type: 'string' }, priceType: { type: 'string' }, priceCategory: { type: 'string', description: 'physical_retail, digital_retail or marketplace_asking.' }, condition: { type: 'string' }, shippingText: { type: 'string' }, observedAt: { type: 'string', format: 'date-time' }, lastSeenAt: { type: 'string', format: 'date-time' }, source: { $ref: '#/components/schemas/Source' } } },
      Edition: { type: 'object', properties: { id: { type: 'string' }, editionLabel: { type: 'string' }, seriesName: { type: 'string' }, format: { type: 'string', enum: ['physical', 'digital'] }, publisher: { type: 'string' }, releaseDate: { type: 'string', format: 'date-time' }, releasePrecision: { type: 'string', enum: ['day', 'month', 'year'] }, isbn: { type: 'string' }, language: { type: 'string' }, pageCount: { type: 'integer' }, dimensions: { type: 'string' }, editionMarket: { type: 'string' }, metadataSourceUrl: { type: 'string', format: 'uri' }, coverUrl: { type: 'string', format: 'uri' }, listings: { type: 'array', items: { $ref: '#/components/schemas/Listing' } } } },
      Book: { type: 'object', properties: { id: { type: 'string' }, slug: { type: 'string' }, originalTitle: { type: 'string' }, englishTitle: { type: 'string' }, summary: { type: 'string' }, publicationType: { type: 'string', enum: ['photobook', 'magazine_issue'] }, photographer: { type: 'string' }, coverUrl: { type: 'string', format: 'uri' }, origin: { type: 'object', properties: { code: { type: 'string' }, name: { type: 'string' } } }, models: { type: 'array', items: { type: 'object', properties: { id: { type: 'string' }, name: { type: 'string' } } } }, editions: { type: 'array', items: { $ref: '#/components/schemas/Edition' } } } },
      Profile: { type: 'object', properties: { id: { type: 'string' }, name: { type: 'string' }, originalName: { type: 'string' }, englishName: { type: 'string' }, officialUrl: { type: 'string', format: 'uri' }, coverUrl: { type: 'string', format: 'uri' }, workCount: { type: 'integer' }, editionCount: { type: 'integer' } } },
    } },
  }, null, 2)}\n`
}
