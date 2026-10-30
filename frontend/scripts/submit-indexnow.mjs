// Submits sitemap URLs to IndexNow (Bing, Yandex, Naver, Seznam). Dry run by
// default; pass --submit to send. The site publishes its key from
// frontend/public/{key}.txt (IndexNow keys are public by design); without
// --key the script uses that file.
// Usage: node scripts/submit-indexnow.mjs [origin] [--key KEY] [--since 2026-10-01] [--submit]
import { readdirSync, readFileSync } from 'node:fs'

const argument = (name) => {
  const index = process.argv.indexOf(name)
  return index > 0 ? process.argv[index + 1] : ''
}
const base = new URL(process.argv[2]?.startsWith('http') ? process.argv[2] : 'https://musebooks.my').origin
const publicDir = new URL('../public/', import.meta.url)
const publishedKey = () => readdirSync(publicDir).filter((name) => /^[0-9a-f]{32}\.txt$/.test(name)).map((name) => readFileSync(new URL(name, publicDir), 'utf8').trim()).find((value, _, all) => all.length === 1) || ''
const key = argument('--key') || process.env.INDEXNOW_KEY || publishedKey()
const since = argument('--since')
const submit = process.argv.includes('--submit')
if (!/^[A-Za-z0-9-]{8,128}$/.test(key)) throw new Error('Pass --key (8-128 letters, digits, or hyphens) or set INDEXNOW_KEY.')

const keyResponse = await fetch(`${base}/${key}.txt`, { signal: AbortSignal.timeout(20000) })
if (!keyResponse.ok || (await keyResponse.text()).trim() !== key) throw new Error(`${base}/${key}.txt does not serve this key; deploy the website with public/${key}.txt first.`)

const decode = (text) => text.replace(/&(amp|lt|gt|quot|apos);/g, (_, entity) => ({ amp: '&', lt: '<', gt: '>', quot: '"', apos: "'" }[entity]))
const entries = []
async function walk(address) {
  const response = await fetch(address, { signal: AbortSignal.timeout(35000) })
  if (!response.ok) throw new Error(`${address}: ${response.status}`)
  const body = await response.text()
  if (/<sitemapindex\b/.test(body)) {
    for (const match of body.matchAll(/<loc>\s*([^<]+?)\s*<\/loc>/g)) await walk(decode(match[1]))
    return
  }
  for (const match of body.matchAll(/<url>([\s\S]*?)<\/url>/g)) {
    const loc = decode(match[1].match(/<loc>\s*([^<]+?)\s*<\/loc>/)?.[1] || '')
    const lastmod = match[1].match(/<lastmod>\s*([^<]+?)\s*<\/lastmod>/)?.[1] || ''
    if (loc) entries.push({ loc, lastmod })
  }
}
await walk(`${base}/sitemap.xml`)

const urls = entries.filter((entry) => !since || (entry.lastmod && entry.lastmod >= since)).map((entry) => entry.loc)
console.log(`${entries.length} sitemap URLs; ${urls.length} selected${since ? ` with lastmod on or after ${since}` : ''}.`)
if (!submit) {
  console.log('Dry run. Re-run with --submit to send them to IndexNow.')
  process.exit(0)
}
const host = new URL(base).host
for (let start = 0; start < urls.length; start += 10000) {
  const urlList = urls.slice(start, start + 10000)
  const response = await fetch('https://api.indexnow.org/indexnow', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json; charset=utf-8' },
    body: JSON.stringify({ host, key, keyLocation: `${base}/${key}.txt`, urlList }),
    signal: AbortSignal.timeout(60000),
  })
  console.log(`Batch ${start / 10000 + 1}: ${urlList.length} URLs → HTTP ${response.status}`)
  if (response.status >= 400) throw new Error(await response.text())
}
