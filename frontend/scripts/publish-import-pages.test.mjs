import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs/promises'
import os from 'node:os'
import path from 'node:path'
import { publishImportedPages } from './publish-import-pages.mjs'
import { renderPublishedPage } from './seo-build.mjs'

const template = '<html><head><title>Home</title><meta name="description" content="old"/><meta name="robots" content="index"/><link rel="canonical" href="https://musebooks.my/"/><script id="musebooks-seo-jsonld" type="application/ld+json">{}</script><script type="module" src="/assets/current.js"></script></head><body><div id="root"><div>Old home</div></div><script id="musebooks-bootstrap">{}</script></body></html>'
const book = slug => ({ id: slug, slug, originalTitle: 'Book ' + slug, origin: { name: 'Japan' }, models: [], editions: [] })
const manifest = slugs => ({ schemaVersion: 1, bookSlugs: slugs, refreshSlugs: slugs })
const response = data => ({ ok: true, json: async () => data })
async function fixture(callback) {
  const directory = await fs.mkdtemp(path.join(os.tmpdir(), 'import-pages-test-'))
  const root = path.join(directory, 'release')
  await fs.mkdir(root)
  await fs.writeFile(path.join(root, 'index.html'), template)
  await fs.writeFile(path.join(root, 'sitemap.xml'), '<urlset><url><loc>https://musebooks.my/</loc></url></urlset>')
  try { await callback(root) } finally {
    assert.ok(path.resolve(directory).startsWith(path.resolve(os.tmpdir()) + path.sep + 'import-pages-test-'))
    await fs.rm(directory, { recursive: true, force: true })
  }
}

test('built template retains assets and has exactly one current book metadata/bootstrap', () => {
  const html = renderPublishedPage(template, '/books/a', { book: book('a') })
  assert.equal((html.match(/rel="canonical"/g) || []).length, 1)
  assert.equal((html.match(/id="musebooks-seo-jsonld"/g) || []).length, 1)
  assert.equal((html.match(/id="musebooks-bootstrap"/g) || []).length, 1)
  assert.ok(html.includes('/assets/current.js'))
  assert.ok(html.includes('<h1>Book a</h1>'))
  assert.ok(!html.includes('Old home'))
})
test('unavailable verified book aborts before any live route changes', async () => fixture(async root => {
  await assert.rejects(publishImportedPages(root, manifest(['a', 'b']), { apply: true,
    fetcher: async url => url.endsWith('/a') ? response(book('a')) : { ok: false, status: 404 } }), /404/)
  await assert.rejects(fs.access(path.join(root, 'books/a/index.html')))
  assert.ok(!(await fs.readFile(path.join(root, 'sitemap.xml'), 'utf8')).includes('/books/a'))
}))
test('new book publication and sitemap are repeatable without duplicating metadata', async () => fixture(async root => {
  const options = { apply: true, fetcher: async () => response(book('a')) }
  const first = await publishImportedPages(root, manifest(['a']), options)
  assert.equal(first.newPages, 1)
  assert.equal(first.sitemapAdditions, 1)
  const second = await publishImportedPages(root, manifest(['a']), options)
  assert.equal(second.changedPages, 0)
  assert.equal(second.sitemapAdditions, 0)
  assert.ok((await fs.readFile(path.join(root, 'books/a/index.html'), 'utf8')).includes('Book a'))
}))
test('failed publication restores existing pages and does not create later routes', async () => fixture(async root => {
  await fs.mkdir(path.join(root, 'books/a'), { recursive: true })
  await fs.writeFile(path.join(root, 'books/a/index.html'), 'original a')
  await assert.rejects(publishImportedPages(root, manifest(['a', 'b']), { apply: true,
    fetcher: async url => response(book(url.split('/').at(-1))),
    beforeWrite: async (_, index) => { if (index === 1) throw new Error('publication failure') } }), /publication failure/)
  assert.equal(await fs.readFile(path.join(root, 'books/a/index.html'), 'utf8'), 'original a')
  await assert.rejects(fs.access(path.join(root, 'books/b/index.html')))
}))
test('unsafe slugs are rejected before fetching or creating directories', async () => fixture(async root => {
  let fetched = false
  await assert.rejects(publishImportedPages(root, manifest(['../outside']), { fetcher: async () => { fetched = true } }), /Invalid verified/)
  assert.equal(fetched, false)
}))
