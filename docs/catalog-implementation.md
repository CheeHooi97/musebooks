# Models, publishers, and market listings

Implemented on 7 October 2026, following MuseCards/gravure-model's React/Vite frontend and layered Go API conventions.

## Available features

- Model/featured-person and publisher directories with search, pagination, counts, representative photobook covers, and book drill-down.
- Active and sold listing ledgers with source and format filtering, search, original prices/currencies, edition context, condition, observation dates, and source links.
- Directory drill-down links to listings filtered by that model or publisher.
- Public routes `/models`, `/publishers`, `/active`, and `/sold`, with static route entry files in `frontend/dist/`.
- Preserved photobook browse, edition comparison, local saved collection, privacy page, theme settings, and Capacitor integration. Browse loads all catalog pages rather than only the first 50 works.
- New read paths use router → handler → service → repository. Existing work/edition/listing identities and worker ingestion remain compatible.

Directories now read persisted people/work_people and companies/editions relationships. The migration backfills existing credits and preserves stable directory IDs and all work, edition, listing, observation, and account records. It also adds markets, product_lines, marketplaces, catalog_media, listing_matches, active_listings, and sold_listings, following MuseCards' domain structure. Existing photobook-specific works and editions remain canonical. Triggers keep identity links and listing snapshots synchronized with existing importer/worker writes. React/Vite application code lives under frontend/src; obsolete Next.js files and TypeScript application sources have been removed.

Public listings must belong to a published work and a non-superseded, compatible edition. Unmatched listings remain outside these ledgers. Sold means completed physical marketplace status; ended offers and digital retail are excluded. Prices describe the recorded observation, not a guarantee of current availability.

## Validation

- `go test ./...` passed, including directory counting and sold/ended/digital classification cases.
- React/Vite JavaScript production build passed.
- The separately bundled Capacitor web build passed. Native Android/iOS compilation and device testing were not run.
- Browser interaction checks passed on all four screens using explicit QA fixtures; no fixture records are included in application source or production fallbacks.
- Desktop (1440 × 1000) and mobile (390 × 844) screenshots were inspected. Directory drill-down, listing format selection, links, and error recovery were checked; no runtime errors or mobile page overflow were observed.
- Browser plugin was not available; checks used the existing Playwright installation from the reference project.
- PostgreSQL settings match MuseCards, preserving the separate musebooks database. Using the existing server administration key, ownership of MuseBooks public tables and sequences was transferred to tcguser, and schema USAGE/CREATE was granted. The normalized migration and application grants were applied successfully. Existing data was preserved. Live directory/listing reads and UPDATE permission were verified (the UPDATE test was rolled back). Backend tests passed. Legacy credits longer than 240 characters are preserved in text columns.
- The opt-in PostgreSQL integration test creates a temporary database using that same account, migrates twice, verifies persisted directories, preserved records, listing transitions and sold history, and then removes only its test database.

## Schema application

The API uses plural GORM account tables and shared connection pooling. Startup migrations default to disabled; startup checks require the versioned schema. From backend/, inspect with go run ./cmd/catalog-migrate. The tcguser account now owns the catalog tables. Apply future migrations with go run ./cmd/catalog-migrate -apply -grant-app-role tcguser using the normal POSTGRES_* settings. The runtime keeps the same MuseCards account.

The migration is transactional and additive, renames legacy singular account tables when safe, preserves original catalog IDs, and records its applied version. An ended listing is never converted into a sale. Reactivating an offer preserves its earlier completed physical sale snapshot. Digital retail is excluded from sold comparables.

## Read-only API preview

From `backend/`, run `go run ./cmd/catalog-preview`. It binds to `127.0.0.1:2001`, exposes catalog read endpoints, and sets PostgreSQL's default transactions to read-only. It does not run startup migrations or seed data.

Account synchronization, curated person/publisher profile management, and protected catalog administration are later specification items, outside this immediate models/publishers/listings implementation.


See [MuseCards alignment](musecards-alignment.md) for the source and server comparison.
