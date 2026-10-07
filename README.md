# MuseBooks

MuseBooks is a catalog and discovery site for physical and authorized digital photobooks from Japan, Taiwan, China, Malaysia, and additional origins over time. It separates a publication work, its editions, and marketplace listings so users can compare the right things.

## Current implementation

- `frontend/` — React + Vite + JavaScript catalog UI, matching MuseCards' frontend stack. Includes models, publishers, active/sold listing ledgers, origin/format filters, edition comparison, local collections, and source links. Application pages are in `frontend/src/pages/`.
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

Build and sync the Android/iOS web bundle from `frontend/`:

```powershell
npm run build:mobile
npm run cap:sync
```

The mobile build defaults to `https://musebooks.my` for both API and shared-link origins. Override `VITE_API_BASE_URL` or `VITE_SITE_URL` before building if those deployment origins change. Open a native project with `npm run cap:android` or `npm run cap:ios` after syncing. Android builds require Android Studio/SDK; iOS builds require macOS and Xcode.

## Models, publishers, and listings

- `/models` and `/publishers`: searchable, paginated directories derived from published work credits and edition publishers, with linked photobooks.
- `/active` and `/sold`: searchable, paginated ledgers with source/format filters, original currencies, condition, observation dates, book details, and external source links.
- API: `GET /v1/models`, `/v1/publishers`, `/{models|publishers}/:id/books`, and `/v1/listings?status=active|sold`. All accept pagination; directories and listings accept `q`. Listings also accept `source`, `format`, `model`, and `publisher`.
- New read paths follow `router → handler → service → repository → database`. Existing scraper ingestion contracts remain intact.
- Sold records require completed physical marketplace status; ended listings and digital retail offers are excluded. Unmatched listings remain outside the public ledger until linked to a published work and compatible edition.
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

```powershell
cd backend; go test ./...
cd ../scraper; go test ./...
cd ../frontend; npm run build
```

Read [plan.md](plan.md) for the product boundaries, marketplace strategy, data model, and remaining roadmap.

For the production website setup on musebooks.my, see [DEPLOYMENT.md](DEPLOYMENT.md).


PostgreSQL and application structure follow MuseCards. See [catalog implementation](docs/catalog-implementation.md) for normalized tables, migration commands, shared connection settings, and ownership requirements. Active React/Vite code is under `frontend/src`; obsolete Next.js files and TypeScript application sources have been removed.
