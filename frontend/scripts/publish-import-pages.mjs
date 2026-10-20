import fs from 'node:fs/promises'
import path from 'node:path'
import os from 'node:os'
import crypto from 'node:crypto'
import { fileURLToPath } from 'node:url'
import { renderPublishedPage } from './seo-build.mjs'
import { pageMarkdown } from './agent-files.mjs'
import { SITE_URL } from '../src/lib/seo.js'

const escape = value => String(value).replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&apos;' }[char]))
const safeSegment = value => typeof value === 'string' && value.length > 0 && value.length <= 140 && value !== '.' && value !== '..' && !/[\/\\\u0000]/.test(value)
const exists = async file => { try { await fs.access(file); return true } catch (error) { if (error.code === 'ENOENT') return false; throw error } }
const atomicWrite = async (file, bytes) => {
  const temporary = file + '.' + crypto.randomUUID() + '.tmp'
  try { await fs.writeFile(temporary, bytes); await fs.rename(temporary, file) }
  finally { await fs.unlink(temporary).catch(error => { if (error.code !== 'ENOENT') throw error }) }
}

export async function publishImportedPages(outputDir, manifest, { apply = false,
  apiURL = 'http://127.0.0.1:2002', fetcher = fetch, beforeWrite = async () => {} } = {}) {
  if (manifest.schemaVersion !== 1 || !Array.isArray(manifest.bookSlugs) || !manifest.bookSlugs.every(safeSegment)) throw new Error('Invalid verified book manifest')
  if (!Array.isArray(manifest.refreshSlugs) || !manifest.refreshSlugs.every(slug => manifest.bookSlugs.includes(slug))) throw new Error('Invalid refresh scope')
  const root = await fs.realpath(outputDir)
  const template = await fs.readFile(path.join(root, 'index.html'), 'utf8')
  const sitemapFile = path.join(root, 'sitemap.xml')
  const sitemap = await fs.readFile(sitemapFile, 'utf8')
  if (!sitemap.includes('</urlset>')) throw new Error('Invalid existing sitemap')
  const stage = await fs.mkdtemp(path.join(os.tmpdir(), 'musebooks-import-pages-'))
  const plans = [], profiles = new Map(), refresh = new Set(manifest.refreshSlugs)
  const slugs = [...new Set(manifest.bookSlugs)]
  let skipped = 0, backup
  const checkedTarget = async (kind, id) => {
    if (!['books', 'models', 'publishers'].includes(kind) || !safeSegment(id)) throw new Error('Unsafe publication route')
    const parent = path.join(root, kind)
    if (await exists(parent) && await fs.realpath(parent) !== parent) throw new Error('Symlinked publication directory')
    const directory = path.join(parent, id)
    if (await exists(directory) && await fs.realpath(directory) !== directory) throw new Error('Symlinked publication route')
    return path.join(directory, 'index.html')
  }
  const get = async endpoint => {
    const response = await fetcher(apiURL.replace(/\/$/, '') + '/v1/' + endpoint, { signal: AbortSignal.timeout(30000) })
    if (!response.ok) throw new Error(`Published catalog request failed (${response.status}): ${endpoint}`)
    return response.json()
  }
  const plan = async (kind, id, data) => {
    const target = await checkedTarget(kind, id)
    const route = '/' + kind + '/' + encodeURIComponent(id)
    await stageFile(route, target, renderPublishedPage(template, route, data), false)
    // The markdown twin is staged and rolled back with its page.
    await stageFile(route + '.md', path.join(path.dirname(target) + '.md'), pageMarkdown(route, data, SITE_URL), true)
  }
  const stageFile = async (route, target, bytes, markdown) => {
    const old = await exists(target) ? await fs.readFile(target, 'utf8') : null
    if (old === bytes) return
    const staged = path.join(stage, String(plans.length) + (markdown ? '.md' : '.html'))
    await fs.writeFile(staged, bytes)
    plans.push({ route, target, staged, markdown, existed: old !== null, sha256: crypto.createHash('sha256').update(bytes).digest('hex') })
  }
  const touched = []
  try {
    // Stage every route before publishing any bytes; an unavailable book cannot
    // leave a partially updated website. Existing unknown URLs keep HTTP 404.
    for (const slug of slugs) {
      const target = await checkedTarget('books', slug)
      if (!manifest.refreshAll && !refresh.has(slug) && await exists(target)) { skipped++; continue }
      const book = await get('books/' + encodeURIComponent(slug))
      if (book.slug !== slug || !book.originalTitle) throw new Error('Catalog book identity mismatch')
      await plan('books', slug, { book })
      for (const model of book.models || []) profiles.set('models/' + model.id, { kind: 'models', id: model.id })
      for (const edition of book.editions || []) if (edition.publisherProfile?.id) {
        const id = edition.publisherProfile.id
        profiles.set('publishers/' + id, { kind: 'publishers', id })
      }
    }
    for (const { kind, id } of profiles.values()) {
      if (await exists(await checkedTarget(kind, id))) continue
      const profile = await get(kind + '/' + encodeURIComponent(id))
      if (profile.id !== id || !profile.name) throw new Error('Catalog profile identity mismatch')
      const books = []
      let totalPages = 1
      for (let page = 1; page <= totalPages; page++) {
        const result = await get(kind + '/' + encodeURIComponent(id) + '/books?pageSize=50&page=' + page)
        if (!Array.isArray(result.items) || !Number.isInteger(result.totalPages) || result.totalPages < 0) throw new Error('Invalid profile book page')
        totalPages = result.totalPages
        books.push(...result.items)
      }
      await plan(kind, id, { profile: { ...profile, books }, books })
    }
    const routes = [...slugs.map(slug => '/books/' + encodeURIComponent(slug)), ...plans.filter(item => !item.markdown).map(item => item.route)]
    const additions = [...new Set(routes)].filter(route => !sitemap.includes('<loc>https://musebooks.my' + escape(route) + '</loc>'))
    const nextSitemap = sitemap.replace('</urlset>', additions.map(route => '<url><loc>https://musebooks.my' + escape(route) + '</loc></url>').join('') + '</urlset>')
    if (apply && (plans.length || additions.length)) {
      backup = path.resolve(root, '..', '.book-page-backups', crypto.randomUUID())
      await fs.mkdir(backup, { recursive: true, mode: 0o700 })
      await fs.writeFile(path.join(backup, 'manifest.json'), JSON.stringify({ root, plans, sitemapFile }, null, 2))
      for (let index = 0; index < plans.length; index++) {
        const item = plans[index]
        if (item.existed) await fs.copyFile(item.target, path.join(backup, index + '.html'))
        await beforeWrite(item, index)
        await fs.mkdir(path.dirname(item.target), { recursive: true })
        await atomicWrite(item.target, await fs.readFile(item.staged))
        touched.push({ ...item, backup: path.join(backup, index + '.html') })
      }
      await fs.copyFile(sitemapFile, path.join(backup, 'sitemap.xml'))
      await atomicWrite(sitemapFile, nextSitemap)
    }
    return { checkedAt: new Date().toISOString(), mode: apply ? 'applied_verified_catalog_pages' : 'dry_run',
      outputDir: root, requestedBooks: slugs.length, skippedExistingBooks: skipped,
      changedPages: plans.filter(item => !item.markdown).length, newPages: plans.filter(item => !item.markdown && !item.existed).length,
      sitemapAdditions: additions.length, backupDirectory: backup || null,
      pages: plans.map(({ route, sha256 }) => ({ route, sha256 })) }
  } catch (error) {
    for (const item of touched.reverse()) {
      if (item.existed) await atomicWrite(item.target, await fs.readFile(item.backup))
      else await fs.unlink(item.target)
    }
    if (backup && await exists(path.join(backup, 'sitemap.xml'))) await atomicWrite(sitemapFile, await fs.readFile(path.join(backup, 'sitemap.xml')))
    throw error
  } finally {
    if (!path.resolve(stage).startsWith(path.resolve(os.tmpdir()) + path.sep + 'musebooks-import-pages-')) throw new Error('Unsafe staging cleanup path')
    await fs.rm(stage, { recursive: true, force: true })
  }
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const args = process.argv.slice(2)
  const value = key => args[args.indexOf(key) + 1]
  try {
    if (!args.includes('--output-dir') || !args.includes('--manifest')) throw new Error('Output directory and manifest are required')
    const output = await fs.realpath(value('--output-dir'))
    if (!output.startsWith('/var/www/musebooks/releases/')) throw new Error('Production output must be a managed MuseBooks release')
    const manifest = JSON.parse(await fs.readFile(value('--manifest'), 'utf8'))
    const report = await publishImportedPages(output, manifest, { apply: args.includes('--apply'),
      beforeWrite: async () => { if (await fs.realpath(value('--output-dir')) !== output) throw new Error('Active release changed; publication cancelled') } })
    if (args.includes('--report')) await atomicWrite(value('--report'), JSON.stringify(report, null, 2))
    const { pages, ...summary } = report
    console.log(JSON.stringify(summary))
  } catch (error) { console.error(error.message); process.exitCode = 1 }
}
