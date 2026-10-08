import test from 'node:test'
import assert from 'node:assert/strict'
import { buildSeo, renderSeo, sitemapXML } from './seo-build.mjs'
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
    assert.match(sitemap, /https:\/\/canonical.example\/about/)
    assert.ok(!sitemap.includes('/404'))
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
