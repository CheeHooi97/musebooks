import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs/promises'
import os from 'node:os'
import path from 'node:path'
import { buildSeo } from './seo-build.mjs'
import { book, fixtureResponse } from './seo-fixture.mjs'
import { CATALOG_LANGUAGES, languagePath, languageAlternates } from '../src/lib/catalog-languages.js'
import { renderLocalizedCatalog } from './localized-catalog.mjs'

test('language editions publish reciprocal alternates, original facts and markdown at every advertised URL', async () => {
  const directory = await fs.mkdtemp(path.join(os.tmpdir(), 'musebooks-languages-'))
  const origin = 'https://catalog.example'
  try {
    await fs.writeFile(path.join(directory, 'index.html'), '<html lang="en"><head><title>Old</title><script type="module" src="/assets/app.js"></script></head><body><div id="root"></div></body></html>')
    await buildSeo(directory, { siteURL: origin, fetcher: async url => ({ ok: true, json: async () => {
      const result = fixtureResponse(url)
      // Cover-only credits must also populate the person's bibliography.
      return new URL(url).pathname === '/v1/books' ? { ...result, items: result.items.map(book => ({ ...book, models: [], coverModels: book.models, publicationType: 'magazine_issue' })) } : result
    } }) })
    const sitemap = await fs.readFile(path.join(directory, 'sitemap.xml'), 'utf8')
    for (const route of ['/', '/books', '/models', '/publishers', '/books/test-book', '/models/test-person', '/publishers/test-publisher']) {
      for (const language of CATALOG_LANGUAGES) {
        const localRoute = languagePath(route, language.code)
        const html = await fs.readFile(path.join(directory, ...localRoute.split('/').filter(Boolean), 'index.html'), 'utf8')
        assert.match(html, new RegExp(`<html lang="${language.code}">`))
        assert.ok(html.includes(`<link rel="canonical" href="${origin}${localRoute}"/>`))
        assert.ok(sitemap.includes(`<loc>${origin}${localRoute}</loc>`))
        if (route === '/models/test-person') assert.ok(html.includes('/books/test-book'), 'Cover-only publication must appear on the profile')
        for (const alternate of languageAlternates(route, origin)) assert.ok(html.includes(`hreflang="${alternate.code}" href="${alternate.url}"`))
        if (language.segment) {
          assert.ok(!html.includes('/assets/app.js'), 'English router cannot replace a language document')
          assert.ok(html.includes('type="text/markdown"'))
          const markdown = await fs.readFile(path.join(directory, localRoute.slice(1) + '.md'), 'utf8')
          assert.ok(markdown.includes(`${origin}${localRoute}`))
          if (route === '/books/test-book') {
            assert.ok(html.includes('9780000000002'))
            assert.ok(html.includes('https://example.com/metadata'))
            assert.ok(html.includes('2025'))
            const graph = JSON.parse(html.match(/type="application\/ld\+json">(.*?)<\/script>/s)[1])['@graph']
            assert.equal(graph.find(item => item.isbn).inLanguage, 'ja', 'Publication language must remain the recorded language')
            assert.equal(graph.at(-1).inLanguage, language.code)
            assert.ok(!html.includes('"@type":"Offer"'))
          }
        }
      }
    }
    assert.ok(!sitemap.includes('/jp/saved'))
  } finally { await fs.rm(directory, { recursive: true, force: true }) }
})

test('translated catalog text escapes hostile facts and keeps one metadata set when refreshing built HTML', () => {
  const template = '<html><head><title>Old</title><meta name="robots" content="noindex"/><link rel="canonical" href="https://old.example/"/><link rel="alternate" hreflang="en" href="https://old.example/"/><script type="module" src="app.js"></script></head><body><div id="root">Old page</div></body></html>'
  const html = renderLocalizedCatalog(template, '/books/test-book', { book: { ...book, originalTitle: '</script><script>alert(1)</script> $&' } }, 'ja', 'https://catalog.example')
  assert.ok(!html.includes('<script>alert(1)</script>'))
  assert.ok(!html.includes('Old page'))
  assert.equal((html.match(/rel="canonical"/g) || []).length, 1)
  assert.equal((html.match(/name="robots"/g) || []).length, 1)
  assert.equal((html.match(/hreflang="en"/g) || []).length, 2) // head and visible language switch
  assert.ok(html.includes('index,follow,max-image-preview:large'))
  assert.throws(() => languagePath('/', 'unknown'), /Unsupported/)
})

test('magazine language pages retain separately recorded cover credits', () => {
  const html = renderLocalizedCatalog('<html><head></head><body><div id="root"></div></body></html>', '/books/issue', { book: { ...book, publicationType: 'magazine_issue', models: [], coverModels: [{ id: 'cover-person', name: '표지 모델' }] } }, 'ko', 'https://catalog.example')
  assert.ok(html.includes('표지 모델'))
  assert.ok(html.includes('/kr/models/cover-person'))
})
