# MuseBooks

MuseBooks is a catalog and discovery site for physical and authorized digital photobooks from Japan, Taiwan, China, Malaysia, and additional origins over time. It separates a publication work, its editions, and marketplace listings so users can compare the right things.

## Current implementation

- `frontend/` — Next.js App Router + React + TypeScript catalog UI with origin, format, language, availability, search, edition comparison, collection persistence, and source links.
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

The frontend uses `http://localhost:2001` as the default API origin and falls back to seeded preview data when the API is unavailable. Override it with `API_ORIGIN` when needed.

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
