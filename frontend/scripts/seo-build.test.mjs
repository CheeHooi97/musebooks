import test from 'node:test'
import assert from 'node:assert/strict'
import { aliasRedirect, buildSeo, modelSlug, renderSeo, sitemapXML, stableMediaURLs } from './seo-build.mjs'
import { pageSeo, hasSearchFilters, publicationDate } from '../src/lib/seo.js'
import fs from 'node:fs/promises'
import os from 'node:os'
import path from 'node:path'
import { book, fixtureResponse } from './seo-fixture.mjs'

test('book metadata escapes catalog text and uses the detail canonical', () => {
  const html = renderSeo('<head><title>Old</title><meta name="description" content="old"/></head>', '/books/example', { originalTitle: 'A & B </script>', summary: 'Verified description', coverUrl: 'https://example.com/cover.jpg' })
  assert.equal((html.match(/name="description"/g) || []).length, 1)
  assert.ok(html.includes('https://musebooks.my/books/example'))
  assert.ok(html.includes('BreadcrumbList'))
  assert.ok(!html.includes('A & B </script>'))
  assert.ok(html.includes('og:image'))
  const structuredData = JSON.parse(html.match(/type="application\/ld\+json">([\s\S]*?)<\/script>/)[1])
  assert.equal(structuredData['@graph'][0].name, 'A & B </script>')
})
test('sitemap uses unique absolute URLs', () => {
  const xml = sitemapXML(['/', '/', '/books/example'])
  assert.equal(xml.match(/<url>/g).length, 2)
  assert.ok(xml.includes('<loc>https://musebooks.my/books/example</loc>'))
})
test('unknown pages are excluded from indexing', () => {
  assert.equal(pageSeo('/books/missing').noindex, true)
  assert.equal(pageSeo('/publishers').noindex, false)
})

test('tracking and edition parameters do not exclude a valid book', () => {
  assert.equal(hasSearchFilters('?utm_source=test&edition=first'), false)
  assert.equal(hasSearchFilters('?q=book'), true)
  assert.equal(hasSearchFilters('?format=digital'), true)
  assert.equal(hasSearchFilters('?page=2'), false)
})

test('edition schema preserves publication precision and never invents active sold offers', () => {
  assert.equal(publicationDate(book.editions[0]), '2025')
  const data = pageSeo('/books/test-book', book).structuredData
  const edition = data['@graph'].find(item => item.isbn)
  assert.equal(edition.datePublished, '2025')
  assert.equal(edition.numberOfPages, 96)
  assert.equal(edition.publisher.name, 'Test Publisher')
  assert.ok(!JSON.stringify(data).includes('Offer'))
})

test('magazine schema never invents a periodical and profile lists preserve publication types', () => {
  const issue = { ...book, publicationType: 'magazine_issue' }
  const schema = pageSeo('/books/test-book', issue).structuredData['@graph'][0]
  assert.equal(schema['@type'], 'PublicationIssue')
  assert.equal(schema.isPartOf, undefined)
  const sourced = { ...issue, editions: [{ ...issue.editions[0], seriesName: 'Recorded magazine' }] }
  assert.equal(pageSeo('/books/test-book', sourced).structuredData['@graph'][0].isPartOf.name, 'Recorded magazine')
  const profile = pageSeo('/models/person', null, { name: 'Person', books: [issue] }).structuredData['@graph'][0]
  assert.equal(profile.mainEntity.itemListElement[0].item['@type'], 'PublicationIssue')
})

test('static build emits facts, citations, links, safe bootstrap and consistent origin', async () => {
  const directory = await fs.mkdtemp(path.join(os.tmpdir(), 'musebooks-seo-'))
  try {
    await fs.writeFile(path.join(directory, 'index.html'), '<html><head><title>Old</title></head><body><div id="root"></div></body></html>')
    const fetcher = async url => {
      const value = fixtureResponse(url)
      return { ok: value !== null, status: value ? 200 : 404, json: async () => value }
    }
    await buildSeo(directory, { fetcher, apiURL: 'https://fixture.example', siteURL: 'https://canonical.example/' })
    const html = await fs.readFile(path.join(directory, 'books/test-book/index.html'), 'utf8')
    assert.match(html, /<h1>Test Photobook<\/h1>/)
    assert.match(html, /9780000000002/)
    assert.match(html, /https:\/\/example.com\/metadata/)
    assert.match(html, /Observed 2026-10-01/)
    assert.match(html, /href="\/models\/test-person"/)
    assert.match(html, /href="\/publishers\/test-publisher"/)
    assert.match(html, /https:\/\/canonical.example\/books\/test-book/)
    assert.match(html, /id="musebooks-bootstrap"/)
    const profileHtml = await fs.readFile(path.join(directory, 'models/test-person/index.html'), 'utf8')
    assert.match(profileHtml, /href="\/books\/test-book"/)
    const sitemap = await fs.readFile(path.join(directory, 'sitemap.xml'), 'utf8')
    for (const route of ['/login', '/register', '/verify-email', '/forgot-password', '/reset-password', '/account']) {
      const accountHTML = await fs.readFile(path.join(directory, route.slice(1), 'index.html'), 'utf8')
      assert.equal(pageSeo(route).noindex, true)
      assert.match(accountHTML, /noindex,follow/)
      assert.ok(!accountHTML.includes('Publication not found'))
      assert.ok(!sitemap.includes(`https://canonical.example${route}<`))
    }
    assert.match(sitemap, /https:\/\/canonical.example\/books\/test-book/)
    assert.match(sitemap, /https:\/\/canonical.example\/models\/test-person/)
    assert.match(sitemap, /https:\/\/canonical.example\/about/)
    assert.ok(!sitemap.includes('/404'))
    // Answers and agent access, matching MuseCards.
    assert.match(html, /<h3>How much does Test Photobook cost\?<\/h3><p>The lowest recorded active offer is ¥ 2,500/)
    assert.ok(html.includes('<link rel="alternate" type="text/markdown" href="https://canonical.example/books/test-book.md"/>'))
    const markdown = await fs.readFile(path.join(directory, 'books/test-book.md'), 'utf8')
    assert.match(markdown, /^# Test Photobook\n\nSource: https:\/\/canonical.example\/books\/test-book\n/)
    assert.match(markdown, /### Who is featured in Test Photobook\?\n\nTest Person\./)
    assert.match(markdown, /- ISBN: 9780000000002/)
    assert.match(await fs.readFile(path.join(directory, 'index.md'), 'utf8'), /\[Test Photobook\]\(https:\/\/canonical.example\/books\/test-book\) — 2025/)
    assert.match(await fs.readFile(path.join(directory, 'about.md'), 'utf8'), /## Prices and completed sales/)
    await assert.rejects(fs.access(path.join(directory, '404.md')))
    const robotsText = await fs.readFile(path.join(directory, 'robots.txt'), 'utf8')
    assert.match(robotsText, /^Content-Signal: search=yes, ai-input=yes, ai-train=yes$/m)
    assert.match(robotsText, /^Allow: \/v1\/catalog\/media\/redirect$/m)
    assert.match(robotsText, /^Sitemap: https:\/\/canonical.example\/sitemap.xml$/m)
    const llms = await fs.readFile(path.join(directory, 'llms.txt'), 'utf8')
    assert.match(llms, /^# MuseBooks\n\n> /)
    assert.match(llms, /The catalog records 1 publications, 1 featured people and 1 publishers\./)
    assert.match(llms, /An ended listing alone is not a completed sale\./)
    assert.match(await fs.readFile(path.join(directory, 'llms-full.txt'), 'utf8'), /### Works, editions, and listings/)
    const feed = await fs.readFile(path.join(directory, 'feed.xml'), 'utf8')
    assert.match(feed, /<entry><title>Test Photobook · Test Publisher<\/title><id>https:\/\/canonical.example\/books\/test-book<\/id>.*<published>2025-01-01T00:00:00Z<\/published>/)
    const openapi = JSON.parse(await fs.readFile(path.join(directory, 'openapi.json'), 'utf8'))
    assert.equal(openapi.servers[0].url, 'https://canonical.example')
    assert.ok(openapi.paths['/v1/books/{id}'] && openapi.paths['/v1/listings'])
    const linkset = JSON.parse(await fs.readFile(path.join(directory, '.well-known/api-catalog'), 'utf8'))
    assert.equal(linkset.linkset[0]['service-desc'][0].href, 'https://canonical.example/openapi.json')
    assert.match(await fs.readFile(path.join(directory, '404.html'), 'utf8'), /noindex,follow/)
    const robots = await fs.readFile(path.join(directory, 'robots.txt'), 'utf8')
    assert.match(robots, /Disallow: \/v1\//)
    assert.match(robots, /Allow: \/v1\/books/)
    await fs.writeFile(path.join(directory, 'index.html'), '<html><head><title>Old</title></head><body><div id="root"></div></body></html>')
    const unicodeBook = { ...book, slug: '写真集', originalTitle: '写真集' }
    await buildSeo(directory, { apiURL: 'https://fixture.example', fetcher: async url => ({ ok: true, json: async () => {
      const result = fixtureResponse(url)
      return new URL(url).pathname === '/v1/books' ? { ...result, items: [unicodeBook] } : result
    } }) })
    const unicodeHTML = await fs.readFile(path.join(directory, 'books/写真集/index.html'), 'utf8')
    assert.match(unicodeHTML, /<h1>写真集<\/h1>/)
    assert.ok(unicodeHTML.includes(encodeURIComponent('写真集')))
  } finally {
    await fs.rm(directory, { recursive: true, force: true })
  }
})

test('unsafe catalog text cannot inject scripts into body or bootstrap', async () => {
  const { renderContent, json } = await import('./seo-content.mjs')
  const unsafe = { ...book, originalTitle: '</script><script>alert(1)</script>', editions: [{ ...book.editions[0], metadataSourceUrl: 'javascript:alert(1)' }] }
  assert.ok(!renderContent('/books/test-book', { book: unsafe }).includes('<script>'))
  assert.ok(!renderContent('/books/test-book', { book: unsafe }).includes('javascript:'))
  assert.ok(!json({ book: unsafe }).includes('</script>'))
  const specialTitle = { ...book, originalTitle: 'A $& $` $\' title', englishTitle: '' }
  const head = renderSeo('<head><title>Old</title></head>', '/books/test-book', specialTitle)
  assert.match(head, /A \$&amp;/)
  assert.ok(!head.includes('<title>Old</title>'))
})

test('overlapping catalog pages render each identity once with its latest facts', async () => {
  const directory = await fs.mkdtemp(path.join(os.tmpdir(), 'musebooks-seo-overlap-'))
  try {
    await fs.writeFile(path.join(directory, 'index.html'), '<html><head><title>Old</title></head><body><div id="root"></div></body></html>')
    await buildSeo(directory, { fetcher: async url => ({ ok: true, json: async () => {
      const result = fixtureResponse(url)
      const parsed = new URL(url)
      if (parsed.pathname === '/v1/models') return { ...result, totalPages: 2, items: result.items.map(item => ({ ...item, name: parsed.searchParams.get('page') === '2' ? 'Updated Person' : item.name })) }
      return result
    } }) })
    const sitemap = await fs.readFile(path.join(directory, 'sitemap.xml'), 'utf8')
    assert.equal((sitemap.match(/<loc>https:\/\/musebooks.my\/models\/test-person<\/loc>/g) || []).length, 1)
    assert.match(await fs.readFile(path.join(directory, 'models/test-person/index.html'), 'utf8'), /Updated Person/)
  } finally {
    await fs.rm(directory, { recursive: true, force: true })
  }
})

test('prerendered R2 images use the stable media redirect', () => {
  const data = stableMediaURLs({ book: { coverUrl: 'https://media.musebooks.my/musebooks/covers/a.jpg?exp=1&sig=x', editions: [{ coverUrl: 'https://img.musecards.my/musebooks/covers/b.jpg' }], other: 'https://example.com/c.jpg' } }, 'https://musebooks.my')
  assert.equal(data.book.coverUrl, 'https://musebooks.my/v1/catalog/media/redirect?source=https%3A%2F%2Fmedia.musebooks.my%2Fmusebooks%2Fcovers%2Fa.jpg')
  assert.equal(data.book.editions[0].coverUrl, 'https://musebooks.my/v1/catalog/media/redirect?source=https%3A%2F%2Fimg.musecards.my%2Fmusebooks%2Fcovers%2Fb.jpg')
  assert.equal(data.book.other, 'https://example.com/c.jpg')
})

test('merged alias profiles redirect to the canonical model without being indexed', () => {
  // Same identity as the API's CatalogIdentity for 岸明日香.
  assert.equal(modelSlug(' 岸明日香 '), 'model-dcded0848f57acaa3afb43a6f3361ca8e7123f97d8d9a624556163f744b163a5')
  const html = aliasRedirect('https://musebooks.my/models/model-abc', 'A & B</script>')
  assert.match(html, /noindex,follow/)
  assert.match(html, /rel="canonical" href="https:\/\/musebooks.my\/models\/model-abc"/)
  assert.doesNotMatch(html, /<\/script>"/)
  assert.match(html, /A &amp; B&lt;\/script&gt;/)
})
