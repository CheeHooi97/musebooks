// Serves R2 catalog media and signed marketplace thumbnails behind
// Cloudflare's edge cache. The Go API signs each URL with an HMAC that covers
// the object key and a window-aligned expiry, so a given image keeps one URL
// for a whole window. Browsers and the app can cache that URL, and the edge
// keeps one copy per object, so repeat views skip the source or R2.

// A signature is never valid for longer than two of the API's largest
// windows (7 days each); anything further out was not minted by the API.
const MAX_URL_LIFETIME_SECONDS = 15 * 24 * 60 * 60
// Edge copies are keyed by object path. Catalog objects are written under
// content-addressed or versioned keys, so a long edge lifetime is safe.
const EDGE_CACHE_SECONDS = 30 * 24 * 60 * 60
const LISTING_IMAGE_KEY_PREFIX = 'musebooks/listing-thumbnails/v2/'
const LEGACY_LISTING_IMAGE_KEY_PREFIX = 'musebooks/listing-thumbnails/v1/'
const LISTING_IMAGE_KEY_PREFIXES = [LISTING_IMAGE_KEY_PREFIX, LEGACY_LISTING_IMAGE_KEY_PREFIX]
const LISTING_IMAGE_CACHE_SUFFIX = '?resize=560x560&format=webp&quality=78'
const LISTING_IMAGE_HOSTS = new Set([
  'auctions.c.yimg.jp',
  'auc-pctr.c.yimg.jp',
  'shop.r10s.jp',
  'is1-ssl.mzstatic.com',
  'img.fril.jp',
])

// Image URLs are signed and expire, so crawlers may fetch them; the catalog
// pages that embed them are governed by the main site's robots.txt.
export const ROBOTS_TXT = 'User-agent: *\nAllow: /\n'

const encoder = new TextEncoder()

export default {
  async fetch(request, env, ctx) {
    if (request.method !== 'GET' && request.method !== 'HEAD') {
      return plain(405, 'Method Not Allowed', { Allow: 'GET, HEAD' })
    }
    const url = new URL(request.url)
    // As in MuseCards: crawlers fetch robots.txt before any image. Answering it
    // here keeps that request from failing the signature check, which Search
    // Console reports as a critical robots.txt error for the media host.
    if (url.pathname === '/robots.txt') {
      return new Response(request.method === 'HEAD' ? null : ROBOTS_TXT, {
        headers: { 'Content-Type': 'text/plain; charset=utf-8', 'Cache-Control': 'public, max-age=86400' },
      })
    }
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

    if (LISTING_IMAGE_KEY_PREFIXES.some((prefix) => key.startsWith(prefix))) {
      return serveListingImage(request, url, key, exp, env, ctx)
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

async function serveListingImage(request, url, key, exp, env, ctx) {
  const source = listingImageSourceURL(key)
  if (!source) return plain(404, 'Not Found')

  const cacheKey = new Request(`${url.origin}/${key}${LISTING_IMAGE_CACHE_SUFFIX}`, { method: 'GET' })
  const cache = caches.default
  let cached = await cache.match(cacheKey)
  const cacheStatus = cached ? 'HIT' : 'MISS'
  let optimized = true
  if (!cached) {
    const thumbnailKey = await listingThumbnailObjectKey(source)
    let stored
    try {
      stored = await env.MEDIA_BUCKET.get(thumbnailKey)
    } catch {
      // R2 lookup failures should not make an otherwise reachable source blank.
      stored = null
    }

    if (stored) {
      const headers = new Headers()
      stored.writeHttpMetadata(headers)
      headers.set('ETag', stored.httpEtag)
      headers.set('Cache-Control', `public, max-age=${EDGE_CACHE_SECONDS}`)
      cached = new Response(stored.body, { status: 200, headers })
    } else {
      let image
      try {
        image = await fetchListingImage(source, true)
        if (!isImageResponse(image)) {
          // Keep source images visible if a host or a format cannot be resized.
          image = await fetchListingImage(source, false)
          optimized = false
        }
      } catch {
        return plain(502, 'Image Unavailable')
      }
      if (!isImageResponse(image)) return plain(502, 'Image Unavailable')

      // Clone before handing the stream to the edge response. Both R2 and
      // Cache API need their own readable stream for background persistence.
      const persistedImage = optimized ? image.clone() : null
      const headers = new Headers(image.headers)
      headers.delete('ETag')
      headers.set('Cache-Control', `public, max-age=${EDGE_CACHE_SECONDS}`)
      headers.set('X-Content-Type-Options', 'nosniff')
      cached = new Response(image.body, { status: 200, headers })
      if (optimized) {
        // Persist one transformed copy so a cold visit from another Cloudflare
        // region can read the small R2 thumbnail instead of re-fetching Yahoo.
        ctx.waitUntil(env.MEDIA_BUCKET.put(thumbnailKey, persistedImage.body, {
          httpMetadata: { contentType: 'image/webp', cacheControl: `public, max-age=${EDGE_CACHE_SECONDS}` },
        }).catch(() => {}))
        ctx.waitUntil(cache.put(cacheKey, cached.clone()))
      }
      // A failed transform fallback may be large; do not keep it at the edge.
    }
    if (stored) ctx.waitUntil(cache.put(cacheKey, cached.clone()))
  }

  const headers = new Headers(cached.headers)
  headers.set('Cache-Control', `public, max-age=${Math.max(0, exp - Math.floor(Date.now() / 1000))}, immutable`)
  headers.set('X-Content-Type-Options', 'nosniff')
  headers.set('X-Media-Cache', cacheStatus)
  headers.set('X-Media-Optimized', optimized ? 'webp-560' : 'source')
  return new Response(request.method === 'HEAD' ? null : cached.body, { status: 200, headers })
}

async function listingThumbnailObjectKey(source) {
  const digest = new Uint8Array(await crypto.subtle.digest('SHA-256', encoder.encode(source)))
  const hash = Array.from(digest, (byte) => byte.toString(16).padStart(2, '0')).join('')
  return `musebooks/thumbs/listing-v2/${hash}.webp`
}

async function fetchListingImage(source, resize) {
  let current = new URL(source)
  for (let redirects = 0; redirects <= 3; redirects += 1) {
    const options = { redirect: 'manual' }
    if (resize) {
      options.cf = { image: { width: 560, height: 560, fit: 'scale-down', quality: 78, format: 'webp' } }
    }
    const response = await fetch(new Request(current.toString(), {
      headers: { Accept: 'image/avif,image/webp,image/*,*/*;q=0.8' },
    }), options)
    if (![301, 302, 303, 307, 308].includes(response.status)) return response
    const location = response.headers.get('Location')
    if (!location || redirects === 3) return null
    current = new URL(location, current)
    if (!isAllowedListingImageURL(current)) return null
  }
  return null
}

function isImageResponse(response) {
  return Boolean(response?.ok && response.headers.get('Content-Type')?.toLowerCase().startsWith('image/'))
}

function isAllowedListingImageURL(url) {
  return url.protocol === 'https:' && !url.username && !url.password && !url.port &&
    LISTING_IMAGE_HOSTS.has(url.hostname.toLowerCase()) && /\.(jpe?g|png|webp)$/i.test(url.pathname)
}

export function listingImageSourceURL(key) {
  const prefix = LISTING_IMAGE_KEY_PREFIXES.find((candidate) => key.startsWith(candidate))
  if (!prefix) return ''
  const encoded = key.slice(prefix.length)
  if (!encoded || encoded.includes('/') || !/^[A-Za-z0-9_-]+$/.test(encoded)) return ''
  let source
  try {
    source = new TextDecoder().decode(decodeBase64URL(encoded))
    if (source.length > 4096 || !isAllowedListingImageURL(new URL(source))) return ''
    if (source.includes('#')) return ''
  } catch {
    return ''
  }
  return source
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
  return decodeBase64URL(value)
}

function decodeBase64URL(value) {
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
