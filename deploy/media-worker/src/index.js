// Serves R2 catalog media behind Cloudflare's edge cache. The Go API signs
// each URL with an HMAC that covers the object key and a window-aligned
// expiry, so a given image keeps one URL for a whole window. Browsers and the
// native app can cache that URL, and the edge keeps one copy per object, so a
// repeat view never reaches R2 or the API.

// A signature is never valid for longer than two of the API's largest
// windows (7 days each); anything further out was not minted by the API.
const MAX_URL_LIFETIME_SECONDS = 15 * 24 * 60 * 60
// Edge copies are keyed by object path. Catalog objects are written under
// content-addressed or versioned keys, so a long edge lifetime is safe.
const EDGE_CACHE_SECONDS = 30 * 24 * 60 * 60

const encoder = new TextEncoder()

export default {
  async fetch(request, env, ctx) {
    if (request.method !== 'GET' && request.method !== 'HEAD') {
      return plain(405, 'Method Not Allowed', { Allow: 'GET, HEAD' })
    }
    const url = new URL(request.url)
    const key = objectKeyFromPath(url.pathname)
    if (!key || !key.startsWith(env.KEY_PREFIX || '')) return plain(404, 'Not Found')

    const now = Math.floor(Date.now() / 1000)
    const exp = Number(url.searchParams.get('exp'))
    if (!Number.isSafeInteger(exp) || exp <= now || exp - now > MAX_URL_LIFETIME_SECONDS) {
      return plain(403, 'Expired')
    }
    if (!(await verifySignature(env.MEDIA_SIGNING_SECRET, key, exp, url.searchParams.get('sig')))) {
      return plain(403, 'Forbidden')
    }

    // The signature is checked before the cache is consulted, so keying the
    // edge copy by path alone never serves an object without a valid URL.
    const cacheKey = new Request(`${url.origin}${url.pathname}`, { method: 'GET' })
    const cache = caches.default
    let cached = await cache.match(cacheKey)
    const cacheStatus = cached ? 'HIT' : 'MISS'
    if (!cached) {
      const object = await env.MEDIA_BUCKET.get(key)
      if (!object) return plain(404, 'Not Found')
      const headers = new Headers()
      object.writeHttpMetadata(headers)
      headers.set('ETag', object.httpEtag)
      headers.set('Cache-Control', `public, max-age=${EDGE_CACHE_SECONDS}`)
      cached = new Response(object.body, { headers })
      ctx.waitUntil(cache.put(cacheKey, cached.clone()))
    }

    const headers = new Headers(cached.headers)
    // A browser copy lives exactly as long as its signature does.
    headers.set('Cache-Control', `public, max-age=${exp - now}, immutable`)
    headers.set('X-Content-Type-Options', 'nosniff')
    headers.set('X-Media-Cache', cacheStatus)
    const etag = headers.get('ETag')
    if (etag && request.headers.get('If-None-Match') === etag) {
      return new Response(null, { status: 304, headers })
    }
    return new Response(request.method === 'HEAD' ? null : cached.body, { status: 200, headers })
  },
}

// objectKeyFromPath mirrors the Go API's object key rules so a URL can only
// name a key the API could have signed.
export function objectKeyFromPath(pathname) {
  let segments
  try {
    segments = pathname.split('/').filter(Boolean).map(decodeURIComponent)
  } catch {
    return ''
  }
  if (!segments.length) return ''
  for (const segment of segments) {
    if (segment === '.' || segment === '..' || segment.includes('/') || segment.includes('\\')) return ''
  }
  return segments.join('/')
}

export async function verifySignature(secret, key, exp, signature) {
  if (!secret || !signature) return false
  let provided
  try {
    provided = base64URLDecode(signature)
  } catch {
    return false
  }
  const cryptoKey = await crypto.subtle.importKey('raw', encoder.encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['verify'])
  return crypto.subtle.verify('HMAC', cryptoKey, provided, encoder.encode(`${key}\n${exp}`))
}

function base64URLDecode(value) {
  const normalized = value.replace(/-/g, '+').replace(/_/g, '/')
  const binary = atob(normalized + '='.repeat((4 - (normalized.length % 4)) % 4))
  return Uint8Array.from(binary, (char) => char.charCodeAt(0))
}

function plain(status, body, extra = {}) {
  return new Response(body, {
    status,
    headers: { 'Content-Type': 'text/plain; charset=utf-8', 'Cache-Control': 'no-store', ...extra },
  })
}
