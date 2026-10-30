# Media Worker

Serves MuseBooks R2 images from `media.musebooks.my` through Cloudflare's edge
cache. Same design as MuseCards' `media.musecards.my`; both read the shared
`musecards` bucket, and this Worker only serves keys under `musebooks/`.

The Worker also serves HMAC-signed listing-image URLs from an exact host
allowlist. It creates 560px WebP thumbnails with Cloudflare Images and caches
successful variants at the edge, instead of sending the browser to large
marketplace originals. The Go signer and Worker host allowlists must stay in
sync. If a transform is unavailable, the Worker falls back to the original
image so listings remain visible.

Catalog rows store covers on the old public hostname
(`https://img.musecards.my/musebooks/...`), which no longer serves objects.
The Go API rewrites those URLs at response time into Worker URLs signed with
an HMAC over the object key and an expiry aligned to a window (default 24
hours). Every request in the same window gets the same URL, so:

- browsers and the Android app cache the image (`Cache-Control: immutable`
  until the signature expires),
- Cloudflare's edge keeps one copy per object (keyed by path, after the
  signature is checked), so repeat views from anyone skip R2 entirely,
- prerendered pages and social previews use `/v1/catalog/media/redirect`,
  which signs a fresh URL on each request and is cached for a third of a window.

Without `CLOUDFLARE_R2_MEDIA_BASE_URL` the API returns stored URLs unchanged.

## Deploy

1. Generate a secret and deploy the Worker (the custom domain is created on
   first deploy; `musebooks.my` must be on the same Cloudflare account):

   ```bash
   openssl rand -base64 48
   cd deploy/media-worker
   npx wrangler@4 login   # must be the account that owns musebooks.my
   npx wrangler@4 secret put MEDIA_SIGNING_SECRET
   npx wrangler@4 deploy
   ```

2. Add to the API server's `.env` and restart it:

   ```
   CLOUDFLARE_R2_PUBLIC_BASE_URL=https://img.musecards.my
   CLOUDFLARE_R2_MEDIA_BASE_URL=https://media.musebooks.my
   CLOUDFLARE_R2_MEDIA_SIGNING_SECRET=<same secret>
   CLOUDFLARE_R2_MEDIA_URL_WINDOW_SECONDS=86400
   ```

3. Rebuild and deploy the frontend so prerendered pages use the redirect.

4. Check: a `coverUrl` from `/v1/books` loads from `media.musebooks.my`, and a
   second request for it shows `x-media-cache: HIT`.

Marketplace transforms use Cloudflare Images' unique-transformation quota:
the Free plan includes 5,000 unique transforms per month. Above that, new
transforms fall back to the original source; the edge still serves already
cached thumbnails.

Rotating the secret: update both sides together. URLs signed with the old
secret return 403 until clients refetch the API.

## Test

```bash
npm test
```

The signature vector in `src/index.test.js` is shared with
`backend/storage/media_test.go`, so a change to either side's signing breaks
one of the two tests.
