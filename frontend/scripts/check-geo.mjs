// Read-only HTTP checks of deployed SEO, GEO and agent access, matching
// MuseCards' check:geo. No account or cookies required.
//   npm run check:geo -- https://musebooks.my [book-slug]
import assert from 'node:assert/strict'
import { robotsAllows } from './robots-access.mjs'

const base = new URL(process.argv[2] || 'https://musebooks.my').origin
const read = async (path, headers = {}) => {
  const response = await fetch(base + path, { headers, redirect: 'manual', signal: AbortSignal.timeout(20000) })
  assert.equal(response.status, 200, `${path} returned ${response.status}`)
  return { response, text: await response.text() }
}

const [robots, sitemap, llms, feed, openapi, catalog] = await Promise.all(['/robots.txt', '/sitemap.xml', '/llms.txt', '/feed.xml', '/openapi.json', '/.well-known/api-catalog'].map(path => read(path)))
const slug = process.argv[3] || decodeURIComponent(sitemap.text.match(/<loc>[^<]*\/books\/([^<]+)<\/loc>/)?.[1] || '')
assert.ok(slug, 'No book URL in the sitemap')
const bookPath = `/books/${encodeURIComponent(slug)}`

// Initial HTML answers, for crawlers that do not run JavaScript.
for (const agent of [undefined, 'OAI-SearchBot', 'ClaudeBot', 'PerplexityBot']) {
  const page = await read(bookPath, agent ? { 'User-Agent': agent } : {})
  assert.ok(page.text.includes('class="book-questions"'), `${agent || 'browser'}: missing initial HTML answers`)
  assert.ok(!/<meta[^>]+name="robots"[^>]+content="[^"]*noindex/i.test(page.text), 'Book page is noindex')
  assert.ok(page.text.includes('type="text/markdown"'), 'Missing markdown alternate link')
  const graph = JSON.parse(page.text.match(/<script id="musebooks-seo-jsonld" type="application\/ld\+json">([\s\S]*?)<\/script>/)?.[1] || '{}')['@graph'] || []
  assert.ok(graph.some(node => ['Book', 'PublicationIssue'].includes(node['@type'])), 'Missing Book structured data')
  if (!agent) {
    const link = page.response.headers.get('link') || ''
    assert.ok(link.includes(`${bookPath}.md>; rel="alternate"; type="text/markdown"`) && link.includes('rel="api-catalog"'), `Link header: ${link}`)
    assert.match(page.response.headers.get('vary') || '', /accept/i, 'Missing Vary: Accept')
  }
}

// Markdown twin, directly and by content negotiation.
const twin = await read(`${bookPath}.md`)
assert.match(twin.response.headers.get('content-type') || '', /^text\/markdown/, 'Markdown twin type')
assert.ok(twin.text.includes(`Source: ${base}${bookPath}`), 'Markdown twin source line')
const negotiated = await read(bookPath, { Accept: 'text/markdown, text/html;q=0.9' })
assert.match(negotiated.response.headers.get('content-type') || '', /^text\/markdown/, 'Accept: text/markdown negotiation')
assert.match((await read('/index.md')).text, /^# MuseBooks/, 'Home markdown twin')

// Discovery files.
assert.match(robots.text, /^Content-Signal: search=yes, ai-input=yes, ai-train=yes$/m, 'Missing content signals')
assert.ok(robots.text.includes(`Sitemap: ${base}/sitemap.xml`), 'Missing sitemap discovery')
for (const agent of ['Googlebot', 'Bingbot', 'OAI-SearchBot', 'GPTBot', 'PerplexityBot', 'Claude-SearchBot', 'ClaudeBot']) {
  for (const path of ['/', '/about', '/models', '/publishers', '/active', '/sold', bookPath, `${bookPath}.md`, '/llms.txt', '/v1/catalog/media/redirect?source=x']) {
    assert.ok(robotsAllows(robots.text, agent, path), `${agent} is blocked by robots.txt at ${path}`)
  }
}
assert.match(llms.text, /^# MuseBooks\n\n> /, 'llms.txt heading')
assert.match(feed.response.headers.get('content-type') || '', /atom\+xml/, 'Feed type')
assert.ok(feed.text.includes('<entry>'), 'Feed has no entries')
assert.equal(JSON.parse(openapi.text).openapi, '3.1.0', 'OpenAPI version')
assert.match(catalog.response.headers.get('content-type') || '', /^application\/linkset\+json/, 'API catalog type')
assert.equal(JSON.parse(catalog.text).linkset[0]['service-desc'][0].href, `${base}/openapi.json`, 'API catalog service-desc')

console.log(`GEO checks passed for ${base} (sample ${bookPath}). A User-Agent probe does not verify bot IP access or predict AI citations.`)
