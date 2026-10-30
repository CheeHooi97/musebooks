# MuseBooks security and search alignment with MuseCards

Inspected 30 October 2026 against MuseCards (`D:/Workspace/Go/gravure-model`, musecards.app) at `3d207a5`, including its [security audit](../../gravure-model/docs/security-and-improvements-audit-2026-10-22.md) and the search/agent work since the [23 October MuseBooks review](search-multilingual-audit-2026-10-23.md). Source changes only; nothing was deployed. Production server reads were not permitted from this session, so server-side state is inferred from live public responses.

## Search, answer-engine and agent access (SEO, GEO, AEO, AAO/AXO)

MuseBooks already matched MuseCards on: prerendered HTML for every catalog page; canonical URLs; hreflang editions (`/jp`, `/tw`, `/cn`, `/kr`); sitemap; robots.txt with Content Signals (`search`, `ai-input`, `ai-train`); Markdown twins with `Accept: text/markdown` negotiation and `Link` headers; `llms.txt`/`llms-full.txt`; OpenAPI; RFC 9727 API catalog; Atom feed; visible source-backed Q&A on book pages; real 404s. Live headers confirm the agent-access pieces are deployed.

| Item | MuseCards | MuseBooks change |
| --- | --- | --- |
| FAQPage markup | Visible Q&A also emitted as FAQPage JSON-LD (Bing, answer engines) | Book pages emit FAQPage from the same `bookAnswers()` that renders the visible questions. Test asserts they match. |
| Organization logo | `logo` on Organization | Added (`/apple-touch-icon.png`, 180×180). |
| Edge caching | `public, max-age=60, stale-while-revalidate=86400, stale-if-error=86400` on documents | Same on HTML; Markdown twins add SWR; sitemap/robots/llms/feed add `stale-if-error`. HTML previously had no `Cache-Control`. |
| Media host robots.txt | Worker answers `/robots.txt` (Search Console flagged 403) | Same in `deploy/media-worker`, with a test. Needs `wrangler deploy`. |
| IndexNow | `submit-indexnow.mjs` | Ported as `npm run indexnow`; key published at `frontend/public/b99e80deabc73afa4454eb7f4a7e008b.txt`. Submit after the next deploy. |

Not copied: MuseCards' `SearchAction` (MuseBooks has no stable search-results URL to point at), official `sameAs` accounts (none recorded for MuseBooks), and model-page LCP preload (MuseBooks' app layout is image-free).

## Security

The account system (added 23 October) was already built with MuseCards' audit fixes: OAuth pre-hijack protection, Secure HttpOnly cookie, enumeration-safe registration, login timing equalizer, password reset with session revocation, PKCE-bound mobile OAuth exchange (no token in the callback URL), per-email database lock for code attempts, fail-closed account-management endpoints, hardened systemd unit as a dedicated user, and no ads on account pages.

| MuseCards item | MuseBooks finding | Change |
| --- | --- | --- |
| S2 Go toolchain | Go 1.22; govulncheck: 23 reachable vulnerabilities (stdlib, x/net, x/text, pgx SQL-injection advisory GO-2026-5004) | Go 1.26.10, x/* modules, pgx 5.11, GORM 1.31. govulncheck: 0 reachable. All backend tests pass. |
| S5 Security headers | None live | Snippet with HSTS, nosniff, Referrer-Policy, Permissions-Policy, CSP `frame-ancestors 'self'; base-uri 'self'; object-src 'none'`, `X-Frame-Options: SAMEORIGIN` (not DENY: the site frames `/hilltop-banner.html`). Included in every location that sets its own headers. |
| Real client IP | Echo read the first `X-Forwarded-For` value, which any client can set, so the sign-in rate limit could be bypassed | nginx takes `CF-Connecting-IP` only from Cloudflare ranges (server-level snippet, so it cannot clash with a MuseCards http-level copy); the API trusts `X-Real-IP` only from loopback. Sign-in limits key IPv6 per /64 and share one budget across browser and native paths. |
| Operational APIs | Scraper ingest endpoints were open when `SCRAPER_INGEST_TOKEN` was unset; non-constant-time compare | Fail closed, constant-time. |
| S7 CORS | Echo already refuses to reflect with `*`; still a config trap | Wildcard origins are dropped with a log line. |
| S10 Error text | Outer error handler returned `err.Error()` as `debug` | Logged server-side only. |
| S16 Listen address | Default `:2002` (all interfaces) | Default `127.0.0.1:2002`; production `.env` example already used loopback. |
| CI gates | None | Deploy workflow runs gitleaks (allowlist for import `observationKey` hashes only), `go test`, govulncheck, `npm audit --omit=dev --audit-level=high` before packaging. Current tree passes all four. |
| `.gitignore` | Secret patterns root-relative only | `**/` patterns for `.env*`, service-account keys, `.pem`, `.p8`, keystores. |
| S9 npm | `npm audit --omit=dev`: 0 | No change. |

Not copied: MuseCards' blanket 300 requests/minute `/v1` read limit. The MuseBooks web app loads the whole catalog with parallel paged reads (over 100 requests per home load) and the static build reads the public API, so that limit would throttle normal visitors and deploys. Revisit after the app stops loading the full catalog.

## Needs owner action

- Deploy (push to `main` or run the workflow) to activate headers, real-IP, caching and FAQPage; then `curl -sI https://musebooks.my/` should show the security headers and `Cache-Control`.
- Confirm `SCRAPER_INGEST_TOKEN` is set in `/opt/musebooks/backend/.env` before deploying, or scraper ingestion will now be refused. Also confirm `HTTP_ADDR` there is loopback, and the `.env` is mode 600 (MuseCards S14).
- `wrangler deploy` the media Worker for the robots.txt fix.
- After deploy: `npm run indexnow -- --submit` from `frontend`.
- `backend/storage/serviceAccountKey.json` (untracked, never committed, unused) is the same `support-system-dev` Firebase key MuseCards removed; delete the local copy.
- Search Console property access for musebooks.my is still unverified in this account; Bing Webmaster Tools is the natural next property given FAQPage and IndexNow.
- Error responses still use HTTP 200 with `"error": true` (MuseCards I2); changing it needs coordinated frontend handling.
