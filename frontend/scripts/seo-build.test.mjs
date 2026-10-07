import test from 'node:test'
import assert from 'node:assert/strict'
import { renderSeo, sitemapXML } from './seo-build.mjs'
import { pageSeo } from '../src/lib/seo.js'

test('book metadata escapes catalog text and uses the detail canonical', () => {
  const html = renderSeo('<head><title>Old</title><meta name="description" content="old"/></head>', '/books/example', { originalTitle: 'A & B </script>', summary: 'Verified description', coverUrl: 'https://example.com/cover.jpg' })
  assert.equal((html.match(/name="description"/g) || []).length, 1)
  assert.ok(html.includes('https://musebooks.my/books/example'))
  assert.ok(html.includes('BreadcrumbList'))
  assert.ok(!html.includes('A & B </script>'))
  assert.ok(html.includes('og:image'))
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
