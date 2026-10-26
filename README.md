# MuseBooks

MuseBooks is a catalog and discovery site for physical and authorized digital photobooks, plus separately classified magazine issues. It separates a publication work, its editions, and marketplace listings so users can compare the right things.

## Current implementation

- `frontend/` — React + Vite + JavaScript catalog UI, matching MuseCards' frontend stack. Includes models, publishers, active/sold listing ledgers, origin/publication/format filters, edition comparison, local collections, and source links. Magazine issues have their own issue-month and cover-model credits.
- `frontend/` also builds a separate locally bundled Capacitor app for Android and iOS. The native build calls the configured HTTPS API directly; it does not load the website remotely.
- `backend/` — Go + Echo + GORM + PostgreSQL API. It migrates and seeds the catalog, exposes browse endpoints, and provides an authenticated scrape control plane for job leasing, heartbeats, idempotent observation batches, and run completion.
- `scraper/` — Go contract/types and legacy generic collector retained for local smoke tests; it does not call marketplace APIs.
- `scraper/` — Python browser workers follow the `scraper_exp/` stdin/stdout and CloakBrowser pattern. `photobook_worker.py` uses rendered marketplace pages and `run_api_worker.py` leases/ingests jobs through the Go control plane; the existing Go contract code remains in the same folder.

## Run locally

Start PostgreSQL and set the existing `POSTGRES_*` variables in `.env`, then run the API:

```powershell
cd backend
go run .
```

Start the website in another terminal:

```powershell
cd frontend
npm install
npm run dev
```

The Vite development server proxies `/v1/*` to `http://127.0.0.1:2002` by default. Override its proxy target with `VITE_API_PROXY` when needed. Production uses the existing Nginx API proxy or `VITE_API_BASE_URL`. The catalog displays an explicit loading, error, or empty state rather than substituting sample records when the API is unavailable.

See [the Korean-model source map](docs/korean-model-photobook-sources.md) for page-based source research, magazine fields, image-use notes, and the import workflow.

The native mobile app omits catalog photographs and cover images. Book covers use text placeholders, and directories and profiles show text only. The website continues to show images on desktop and mobile browsers.

Rollup is pinned to `4.63.0` because `4.64.1` stalls during tree-shaking for this app. Keep the pin when installing dependencies; tree-shaking remains enabled.

Build and sync the Android/iOS web bundle from `frontend/`:

```powershell
npm run build:mobile
npm run cap:sync
```

The mobile build defaults to `https://musebooks.my` for both API and shared-link origins. Override `VITE_API_BASE_URL` or `VITE_SITE_URL` before building if those deployment origins change. Open a native project with `npm run cap:android` or `npm run cap:ios` after syncing. Android builds require Android Studio/SDK; iOS builds require macOS and Xcode.

## Models, publishers, and listings

- `/models` and `/publishers`: searchable, paginated directories derived from published featured/cover-model credits and edition publishers, with linked catalog records.
- `/active` and `/sold`: searchable, paginated ledgers with source/format filters, original currencies, condition, observation dates, book details, and external source links.
- `/japan`: captured Japanese marketplace listings, with latest listing images and prices, source filters, and active/completed status. Unmatched records stay separate from verified photobook works.
- The homepage also loads Japan marketplace offers under the existing origin, search, format, and availability filters. Offers group by verified work slug or identical normalized listing title; unmatched groups remain explicitly pending and do not create catalog books. Expand a group to compare individual offers by platform. Book counts and offer counts remain separate.
- API: `GET /v1/models`, `/v1/publishers`, `/{models|publishers}/:id/books`, `/v1/listings?status=active|sold`, and `/v1/marketplace-listings?region=JP&status=all|active|completed`. Catalog listing endpoints accept `publicationType=photobook|magazine_issue` where applicable.
- New read paths follow `router → handler → service → repository → database`. Existing scraper ingestion contracts remain intact.
- Sold records require completed physical marketplace status; ended listings and digital retail offers are excluded. The general `/active` and `/sold` ledgers stay edition-linked; the Japan page separately labels and shows unmatched marketplace records.
- Directory identities currently derive from normalized catalog credit names. Alias merging and independently curated person/publisher profiles remain future work.

Implementation and validation notes, including the read-only API preview command, are in [docs/catalog-implementation.md](docs/catalog-implementation.md).

Website and mobile builds write to `frontend/dist/`. The build emits entry files for all public routes so the existing static deployment can serve direct links.

Run the browser-only Python regional worker after installing its dependencies:

```powershell
python -m pip install -r scraper/requirements.txt
python scraper/run_api_worker.py --worker-id jp-tw-cn-my-01
```

Set `MUSEBOOKS_API_URL` and `SCRAPER_INGEST_TOKEN` before running it. The
worker reads only rendered consumer pages supplied by source-scoped jobs; it
does not call eBay, Rakuten, JD, Shopee, Lazada, or any other marketplace API.

## Verification

Accounts support Google sign-in and email/password registration at `/login`
and `/register`. Password accounts must confirm the six-digit emailed code
before signing in. Verification codes expire after 10 minutes, allow five
attempts, and can be resent after one minute. `/forgot-password` sends a
separate reset code valid for 15 minutes; resetting revokes other sessions.
Saved books and preferences remain on the current device.

Configure `SITE_URL`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`,
`GOOGLE_REDIRECT_URL`, `RESEND_API_KEY`, `EMAIL_FROM`, and a separate
`EMAIL_VERIFICATION_SECRET` (32+ random characters) in the backend environment.
Register the exact Google callback URL
`https://musebooks.my/v1/auth/oauth/google/callback` in Google Cloud. The
email sender must be verified in Resend. No provider secrets enter the
frontend build. Google and email registration show an unavailable state until
their configuration exists; verification is never bypassed.

Apply the additive account migration before starting the updated API:
`go run ./cmd/catalog-migrate --apply` from `backend/` with the database owner's
environment. Legacy accounts remain unverified. Duplicate legacy email
addresses must be reconciled before the unique email index can be created.
The deploy workflow does not apply database migrations automatically.

Website sessions use a host-only HttpOnly, SameSite cookie; production cookies
require HTTPS. Native bundles use bearer sessions and open Google in the
system browser, returning through `my.musebooks.app://auth/callback`. The
callback contains a short-lived, single-use exchange code bound to the app's
secret verifier. Session tokens are never put into callback URLs. Rebuild
and sync native projects for the new URL scheme. Legacy `/v1/user` and
`/v1/admin` management routes now require the configured internal scraper
token; signing in does not grant management access.

```powershell
cd backend; go test ./...
cd ../scraper; go test ./...
cd ../frontend; npm run build
```

Read [plan.md](plan.md) for the product boundaries, marketplace strategy, data model, and remaining roadmap.

For the production website setup on musebooks.my, see [DEPLOYMENT.md](DEPLOYMENT.md).


PostgreSQL and application structure follow MuseCards. See [catalog implementation](docs/catalog-implementation.md) for normalized tables, migration commands, shared connection settings, and ownership requirements. Active React/Vite code is under `frontend/src`; obsolete Next.js files and TypeScript application sources have been removed.
