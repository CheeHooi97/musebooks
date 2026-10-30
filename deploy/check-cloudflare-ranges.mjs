// Read-only: compares deplo./musebooks-cloudflare-real-ip.conf with Cloudflare's
// published proxy ranges. Exits 1 when the config needs updating.
import { readFile } from 'node:fs/promises'

const config = await readFile(new URL('./musebooks-cloudflare-real-ip.conf', import.meta.url), 'utf8')
const configured = new Set([...config.matchAll(/^set_real_ip_from\s+([^;\s]+);/gm)].map((match) => match[1]))
const response = await fetch('https://api.cloudflare.com/client/v4/ips', { signal: AbortSignal.timeout(15000) })
const body = await response.json()
if (!response.ok || !body.success) throw new Error(`Cloudflare IP API failed: HTTP ${response.status}`)
const published = new Set([...body.result.ipv4_cidrs, ...body.result.ipv6_cidrs])

const missing = [...published].filter((range) => !configured.has(range))
const stale = [...configured].filter((range) => !published.has(range))
if (missing.length || stale.length) {
  if (missing.length) console.log(`Add: ${missing.join(', ')}`)
  if (stale.length) console.log(`Remove: ${stale.join(', ')}`)
  process.exit(1)
}
console.log(`musebooks-cloudflare-real-ip.conf matches Cloudflare's ${published.size} published ranges.`)
