# MuseBooks implementation plan

Status: implementation baseline, 13 September 2026. The first frontend, Postgres catalog API, and generic Playwright scraper vertical slice are now implemented; production marketplace adapters, account sync, mobile, and live collection migration remain planned.

## Product direction

MuseBooks is a discovery and collection website for physical and digital photobooks from Japan, Taiwan, China, Malaysia, and additional origins over time. Users find a title or featured person, compare editions, discover purchase options across marketplaces, and save books to a wishlist or personal collection.

Initial assumption: MuseBooks catalogs publications and links to external sellers. Hosting purchased digital books, building a reader, accepting payments, and operating a resale marketplace are separate future projects. Digital coverage means legitimate publication metadata, authorized previews, storefront availability, and purchase links.

Use four product areas: **frontend**, **mobile**, **backend**, and **scraper**. Build frontend, backend, and scraper first. Mobile remains a planned API consumer.

### Essential distinctions

- A work is the photobook title; an edition is a particular physical or digital release; a listing is a seller's offer for that edition.
- Publication origin, edition market, language, featured person's nationality, seller location, and marketplace region are different fields. A Japanese book sold in Malaysia remains a Japanese-origin work.
- A physical first edition, translated edition, digital edition, signed copy, and bundle must not collapse into one price comparison. Signed condition and included bonuses can be listing attributes; publisher-issued limited releases can be editions.
- Digital availability is not transferable ownership. Do not treat unofficial file resales as equivalent to an authorized digital storefront.
- An asking price, current auction bid, buy-now price, and confirmed sold price are different observations. A disappeared listing is not proof of a sale.
- Unknown information stays unknown, with a source and review status. Do not infer origin solely from a seller's country or an edition solely from a title match.

### Initial scope

Include published photography books, creator/model/idol photobooks, and documented independent releases. Start with Japanese and Traditional Chinese metadata plus English navigation; accept Simplified Chinese and Malay titles from day one. Store original scripts and aliases rather than replacing them with translations.

Exclude custom photo-printing services, empty albums, standalone trading cards, unrelated merchandise, and unauthorized digital copies. Mixed bundles require explicit labeling. These exclusions matter because broad searches for “photobook” produce many unrelated products.

## 1. Frontend — website, current priority

### Recommended stack

Use **Next.js App Router + React + TypeScript**, with Tailwind CSS and accessible reusable components. This recommendation fits a searchable public catalog plus interactive filters, collections, and administration. Server rendering provides readable initial catalog pages; client components handle controls and account interactions. Next.js documents this split in its [Server and Client Components guide](https://nextjs.org/docs/app/getting-started/server-and-client-components).

Astro would be a reasonable choice for a mostly editorial site, while a client-only Vite SPA would suit an internal tool. Next.js is the proposed choice for MuseBooks' combined catalog and account experience. Go remains the business API: do not duplicate catalog rules or database access in Next.js.

### MVP pages

| Page | Required behavior |
| --- | --- |
| Home | Recent releases, browse by origin, physical/digital entry points, search |
| Catalog `/books` | Filter by origin, format, language, creator, release year and availability; shareable URL state; pagination |
| Work `/books/[slug]` | Original title, aliases, people, publisher, cover, release metadata, edition selector and source attribution |
| Edition detail | Exact format, ISBN if present, language, release date, page count if known, bonuses and available listings |
| Listings | Seller/source link, native price and currency, condition, shipping information, status, observed time; separate auction and fixed-price views |
| Person `/people/[slug]` | Names and aliases, roles such as photographer or featured person, associated works |
| Origin `/origins/[code]` | Curated entry to that origin, including clear empty states before data is available |
| My collection / wishlist | Sign in, save/remove editions, mark physical/digital ownership without uploading book files |
| Admin | Review candidate works, match listings, correct metadata, merge duplicates, inspect jobs and source health |

### Website behavior and design

- Use a cover-led, readable catalog with consistent image ratios, restrained color, and prominent titles. Mobile web must work from the first milestone.
- Include both physical and digital editions in navigation; never imply that a digital-only release has a physical counterpart.
- Show original currency first. Optional conversion is an estimate with exchange-rate timestamp. Unknown shipping/tax is not zero and must not produce a misleading “cheapest delivered” label.
- Label last checked time and stale/unavailable offers. Source failures should leave the catalog usable.
- Use Unicode-aware search, ISBN lookup, and alias matching. Test Japanese, Traditional/Simplified Chinese, Latin names, and mixed-script titles.
- Add canonical URLs, sitemaps, metadata, and structured data only for facts present in the catalog. Avoid indexing every filter combination.
- Provide keyboard operation, visible focus, meaningful alt text, accessible forms, loading states, empty states, retry states, and account permission errors.
- Cache public catalog responses with an explicit freshness policy. Keep personalized collections and admin responses out of shared caches.

### Website acceptance criteria

With the Go API running, a visitor can search a seeded title, filter editions by format/origin, inspect provenance and prices, and open the correct external listing. An authenticated user can save an edition. An administrator can approve an unmatched candidate. Verify these journeys on desktop and a narrow mobile viewport, including slow/failed API responses.

## 2. Mobile — deferred

Reserve `mobile/` as a separate application boundary. Start with responsive web; a native app is not needed for initial launch.

Later evaluate React Native/Expo because the website team will already use React and TypeScript. Share generated API types, validation contracts where appropriate, and design tokens; do not assume web components can be copied directly.

Future scope: collection browsing, wishlist, release/price notifications, ISBN barcode lookup, deep links and optional offline collection metadata. Keep digital reading and file storage out of this scope until licensing and delivery are separately designed.

Begin mobile implementation only after the catalog API and account flows are stable and website usage demonstrates a need. Any age-sensitive catalog scope must be reviewed before app-store distribution.

## 3. Backend — Go, current priority

### Existing repository baseline

The current code is under `backend/`, using Go, Echo, GORM and PostgreSQL. Existing code provides a user/admin scaffold, not a photobook catalog. `backend/database/migrate.go` currently migrates User and Admin only. `backend/middleware/middleware.go` passes requests through without authenticating them, so current administration cannot be treated as protected.

Build on the Go scaffold, review its handlers and repositories, and add real authentication/authorization before exposing write endpoints. Adopt a supported Go toolchain during implementation and verify dependency compatibility instead of retaining an old version by default.

### Service boundaries

- Go API owns catalog identity, edition matching, validation, accounts, collections and all writes to canonical data.
- PostgreSQL stores canonical data, source observations and durable scrape jobs.
- Scrapers run as separate Go processes/containers and submit authenticated observation batches. They do not write directly to canonical catalog tables.
- Object storage holds permitted covers and limited diagnostic artifacts with source attribution and retention rules.
- Begin with PostgreSQL search and a PostgreSQL-backed job queue. Add a dedicated search engine or Redis only when measured workload requires it.
- Maintain a versioned OpenAPI contract for website, later mobile, and scraper ingestion.

### Proposed data model

| Entity | Main fields / purpose |
| --- | --- |
| works | ID, slug, original title, aliases, description, origin codes, classification, review status |
| editions | Work ID, format, language, edition market, publisher, release date and precision, ISBN nullable, page count nullable, edition label |
| people / work_people | Original name, aliases, association role; many people per work |
| publishers | Name, aliases, official website |
| sources | Marketplace/store identity, adapter, region/locale/timezone, capabilities, access method, allowed hosts, access status, enabled state, review date and rate budget |
| listings | Source ID + external ID, canonical URL, nullable edition ID, title, seller location, condition, bundle/bonus attributes, status and last-seen time |
| listing_observations | Listing ID, observation time, native amount/currency, price type, source evidence, source timestamp, timestamp precision |
| source_records | Raw normalized input, content hash, parser version, retrieval URL, provenance and matching outcome |
| edition_sources | Edition-to-source metadata links and field-level provenance |
| assets | URL/storage key, source, permitted usage, image role and retrieval time |
| collections / wishlists | User ID, edition ID, ownership/wishlist state and private notes |
| scrape_jobs / scrape_runs | Operation, query, source, lease, attempt count, cursor, result counts, errors, timestamps |
| review_items / audit_events | Ambiguous matches, corrections, approvals and actor history |

Use decimal money or exact minor units with currency-specific precision, never floating-point prices. Store event times in UTC while preserving the source timezone. Publication dates may have only a year or month; do not fabricate a precise day.

Add unique constraints for `(source_id, external_id)` and observation idempotency keys. Index edition joins, source/status queries, release filters, and job readiness/lease fields. ISBN is useful but not mandatory; digital and independent editions may lack one.

Use versioned SQL migrations for deployment. Separate development AutoMigrate from production migrations, back up before changes, and provide a restore procedure. Existing MySQL data transfer is outside this plan; the current PostgreSQL setup does not itself move old data.

### Proposed API

Public: `GET /v1/books`, `/v1/books/{id}`, `/v1/editions/{id}`, `/v1/editions/{id}/listings`, `/v1/people/{id}`, `/v1/origins`, `/v1/sources`.

Account: sign-in/session endpoints and authenticated collection/wishlist CRUD. Use secure HTTP-only cookies for website sessions, CSRF protection for cookie-authenticated mutations, and an explicit future mobile authentication flow.

Admin: candidate review, edition matching/merging, source configuration, scrape job submission and run inspection. Require roles and audit changes.

Internal: leased job claim/heartbeat/completion and idempotent observation-batch ingestion. Authenticate workers separately from users. Validate source URLs against allowed hosts; prevent arbitrary job URLs from reaching private/internal network addresses.

All list APIs need pagination, documented filters, stable sorting and consistent errors. Apply sensible request limits and timeouts. Return provenance and freshness fields so the UI can show uncertainty accurately.

The implemented scrape control plane uses `POST /v1/internal/scrape/jobs` to enqueue a source-specific request, `POST /v1/internal/scrape/jobs/claim` to atomically lease work, `POST /v1/internal/scrape/jobs/{id}/heartbeat` to extend a lease, `POST /v1/internal/scrape/batches` to upsert listings and append idempotent observation history, and `POST /v1/internal/scrape/jobs/{id}/complete` to finish or requeue a run. A claim returns the source's region, locale, timezone, access method, capabilities, allowed hosts, rate budget and access status so Python adapters do not need hard-coded regional policy.

### Backend acceptance criteria

Importing the same batch twice creates no duplicate listings or observations. Matching can be reviewed and corrected without losing provenance. An ordinary user cannot modify sources or another user's collection. A worker crash does not lose a leased job. Database migration and restore procedures are exercised against disposable test databases.

## 4. Scraper — Go + Chromium, current priority

### Browser choice and reference findings

Assumption: “openwright” means **Playwright**. Use the community-maintained [`playwright-community/playwright-go`](https://github.com/playwright-community/playwright-go) binding with Chromium. Pin the Go binding and matching browser/driver installation together in the worker image. This is a community Go binding, so include a compatibility smoke test when upgrading.

`scraper_exp/` is the unchanged Python reference folder. Its older `worker.py`
remains a trading-card reference and is not used for photobooks. The production
`scraper/photobook_worker.py` follows its stdin/stdout, browser isolation,
diagnostics, pagination and regional-process pattern while accepting only
physical or authorized digital photobooks. `scraper/run_api_worker.py` connects
that process to the Go lease/ingest API. `catalog_worker.py` remains separate
for discovery/checklist/media experiments.

| Reference | Plan for MuseBooks |
| --- | --- |
| `worker.py`: JSON input/output, stderr progress | Preserve machine-readable batch contracts in `photobook_worker.py`; keep the card classifier out of this catalog |
| Pagination, repeated-page fingerprints and source IDs | Port the design, add durable page checkpoints and bounded work |
| Active/sold/detail reconciliation | Preserve the separation; record evidence instead of guessing sold status |
| Platform aliases and Doorzo origin mapping | Persist original marketplace identity separately from retrieval/proxy source; deduplicate the same original listing |
| `japan_active_worker.py` and its tests | Port timezone boundary tests; use configurable lookback so an outage does not miss earlier listings |
| Taiwan/Korea wrappers | Replace region-only wrappers with source adapters plus locale/timezone configuration |
| Trading-card relevance regexes and checklist processing | Replace with photobook classification and edition matching; exclude TCG-only processing |
| OCR/media/watermark scripts | Defer OCR unless needed for metadata; do not carry watermark-removal behavior into catalog media handling |

An alias or parser in the reference is evidence of implementation intent, not proof that the live source is accessible today. No live marketplace scraping was tested for this plan.

### Source strategy and marketplace shortlist

Separate publisher/bookstore metadata from marketplace offers. The collection
path is intentionally browser-only: Python adapters in `scraper/` use
CloakBrowser against permitted rendered pages. The Go API is only the job
control plane and normalized-ingest API; it must not call marketplace APIs.
Each source needs a short discovery spike covering current terms/access,
representative photobook pages, fields, pagination, availability signals, and
expected maintenance before enabling scheduled collection.

The table is a candidate list, not a promise of automated access. “P1” is first evaluation wave, “P2” is expansion, “P3” is later investigation.

| Market | Candidate sources | Intended data | Proposed route and priority |
| --- | --- | --- | --- |
| Global | eBay | Physical offers, auction/fixed price, seller location | Browser consumer-page adapter, P1; verify production eligibility and quotas. Sold history is separate and not an MVP dependency |
| Japan resale | Yahoo! JAPAN Auctions | Physical auctions, bids, end times; completion evidence when available | Evaluate rendered-page adapter from reference, P1; do not assume legacy API availability |
| Japan resale | Mercari Japan | Physical fixed-price offers and explicit availability evidence | Keep blocked until an official/written access path exists; no browser bypass |
| Japan resale | Rakuma, Yahoo! Flea Market | Additional physical resale inventory | Reference-inspired rendered adapters after access review, P2 |
| Japan specialist shops | Mandarake, Suruga-ya | Used/rare editions and shop stock | Metadata and offer-page evaluation, P2 |
| Japan retail | Publisher sites, Rakuten Books, Amazon Japan | Edition metadata, releases, retail offers | Python browser adapters for permitted rendered pages, P2; no unrestricted Amazon scraping assumed |
| Japan digital | BOOK WALKER Japan; publisher digital stores | Digital editions, publisher/release metadata and official purchase links | P1 metadata pilot; authorized feed/page access only, no book-file download |
| Taiwan | Books.com.tw, publisher sites | Physical and digital edition metadata | P1 metadata pilot; access review before collection |
| Taiwan resale | Ruten, Shopee Taiwan | Physical offers, condition and stock evidence | Browser-only evaluation: Ruten P1; Shopee P2, subject to access review |
| Taiwan digital | Readmoo, BOOK WALKER Taiwan | Authorized digital offers and edition records | Candidate investigation P2 |
| China retail | JD, Dangdang, publisher stores | Physical publication metadata and official offers | Candidate investigation P2; browser access and terms must be verified |
| China marketplace | Taobao/Tmall, Xianyu | Retail/resale offers and independent editions | P3; validate accessible surfaces and authorized access before committing engineering time |
| China digital | Publisher-authorized stores, eligible JD/Dangdang digital catalogs | Verified digital editions where present | P2 investigation; validate actual photobook coverage, avoid unofficial download sellers |
| Malaysia | Carousell Malaysia, Shopee Malaysia, Lazada Malaysia | Local resale/retail offers and shipping context | Browser-only evaluation P2/P3 depending on access |
| Malaysia origin | Local publishers and creator-owned stores | Local-origin works, physical releases and legitimate digital releases | P1 editorial/manual seed plus permission-based feed outreach; local marketplace location is insufficient evidence of origin |
| Later origins | Korea and other markets | Additional editions and resale offers | P3; reference Bunjang/Naver/Karrot names are leads, not launch commitments |
| Cross-border discovery | Doorzo and similar proxy stores | Discovery links to original marketplace listings | Optional later connector with permitted access; do not count proxy copies as independent offers |

Evidence informing this shortlist (reviewed for source discovery only; none
of these marketplace APIs is called by the implementation):

- eBay documents current listing search through its [Browse API](https://developer.ebay.com/api-docs/buy/api-browse.html). Its [developer questionnaire](https://partnernetwork.ebay.com/page/developer-questionnaire) says Marketplace Insights access cannot be granted upon request; do not promise sold-price coverage through it.
- BOOK WALKER has a [photobook category](https://bookwalker.jp/tcl59/), making it a concrete digital-catalog candidate.
- Books.com.tw has both a [physical photobook example](https://www.books.com.tw/products/M010106733) and a [digital photobook example](https://www.books.com.tw/products/E050116880). These establish catalog relevance, not scraping permission.
- Ruten has [photobook listings](https://www.ruten.com.tw/item/22613330948551/), and Carousell Malaysia has a [photo-book search surface](https://www.carousell.com.my/photo-book/q/). Classification must remove custom albums and unrelated products.
- China candidates and several expansion sources remain unverified for coverage/access in this research. Keep them on the evaluation backlog rather than promising initial connectors.

### Collection pipeline

`source configuration → scheduled job → Python browser discovery → page batches → normalization → deduplication → edition matching → review/approval → published catalog and offers`

1. A scheduler creates bounded jobs by source, operation, query/alias set, region and lookback window.
2. `scraper/run_api_worker.py` leases a job, starts an isolated
   `photobook_worker.py` process, and passes the source-scoped rendered URL.
   Limit concurrency per source and globally.
3. An adapter discovers items and fetches details only when needed. Prefer reliable structured page data where available; use tested DOM extraction as fallback.
4. Each batch includes job/source IDs, original external IDs/URLs, retrieval time, native price/currency, format candidates, status evidence, warnings, parser version and next cursor.
5. The backend validates and commits the batch with its checkpoint. Retries use the same idempotency key.
6. Match by strong edition evidence first: ISBN or verified source-product links, then title/person/publisher/date/format signals. Put ambiguous or bundle matches in a review queue. Cover similarity alone is insufficient.
7. Schedule reconciliation for known active offers separately from new-listing discovery. Record confirmed unavailable, unknown and sold as distinct outcomes.

### Operations and safeguards

- Operations: `catalog_discovery`, `active_discovery`, `listing_detail`, `listing_reconcile`; `sold_discovery` only for sources with explicit reliable evidence.
- Start with conservative, configurable schedules such as daily catalog discovery and several-hour listing refreshes, subject to source limits. These are starting targets, not source permissions or freshness guarantees.
- Use timeouts, bounded pages/items/runtime, retry with backoff for transient errors, and a circuit breaker for repeated failures. Treat a challenge or login wall as blocked, not as an empty result page.
- Use lease expiry and heartbeat recovery. Detect repeated pagination cursors/fingerprints, report partial completion, and resume from a committed checkpoint.
- Prevent launches from overwhelming RAM; measure browser memory and throughput during the first connector spike. Keep browser failures isolated from the API process.
- Track discovered/accepted/rejected/unmatched counts, last successful run, duration, blocked rate, stale listings and parse failures per source.
- Store redacted diagnostic snapshots only when useful, with short retention. Do not log credentials/cookies or indiscriminately archive seller personal data.
- Collect permitted metadata and cover/preview assets, preserve attribution and watermarks, and link to the original source. Do not bypass account, CAPTCHA, paywall or DRM restrictions.

### Scraper acceptance criteria

Fixture tests cover title/price/format extraction, Japanese and Chinese dates, missing ISBNs, bundles, false photobook matches, sold-vs-ended evidence and repeat pages. Integration tests prove duplicate-batch safety, worker restart/resume and source failures. A small permitted live smoke test verifies each enabled connector before scheduling it.

## Repository and deployment layout

```text
musebooks/
  plan.md
  frontend/             # Next.js website and admin UI
  mobile/               # Reserved; deferred implementation
  backend/              # Existing Go API; migrations and API contract
  scraper/              # New Go module, worker CLI, adapters and fixtures
  scraper/              # Go contracts plus Python CloakBrowser workers
  scraper_exp/          # Unchanged Python reference experiments
  deploy/               # Local compose setup and deployment configuration
  docs/                 # Source evaluations and operational procedures
```

Keep API and scraper modules separately runnable. Generate client contracts from the backend API schema rather than sharing database structs. Local development should support website, API, PostgreSQL and an optional scraper container. Deploy API and worker separately so Chromium load cannot exhaust web capacity. Add health/readiness checks, backups, structured logs and an operational source-disable switch.

## Delivery sequence

Estimates below are indicative for one experienced developer, excluding source approval delays. Adjust after the first live adapter spike.

| Milestone | Deliverable | Exit condition | Indicative effort |
| --- | --- | --- | --- |
| 0. Foundation and source spikes | Confirm catalog scope, choose stack, inspect 3–4 sources, seed edition examples across JP/TW/CN/MY | Document access decision and sample fields for each source; include physical and digital examples | 3–5 days |
| 1. Catalog vertical slice | Go schema/migrations/API + Next.js home/search/detail + manual seed import | User can find a book and distinguish editions; admin access protected | 1–2 weeks |
| 2. First automated source | Go worker, durable jobs, eBay API if access available or one approved browser source | Repeated import and interrupted-job recovery work; offers appear on website | 1–2 weeks |
| 3. Japan/Taiwan and digital pilot | Evaluate Yahoo/Mercari, add the next approved connector and a publisher/bookstore metadata source | Measured matching quality; both digital and physical catalog represented | 1–2 weeks |
| 4. Launch polish | Collection/wishlist, review UI, freshness labels, monitoring, SEO/accessibility and deployment | Core journeys pass; restore tested; blocked sources visible to admin | About 1 week |
| 5. Regional expansion | China/Malaysia automated sources, deeper price history and optional alerts | Each new adapter passes its own access, quality and operational gates | After MVP |
| 6. Mobile | Native client based on stable API | Separate product decision after website validation | Deferred |

China and Malaysia belong in the schema, navigation and curated launch dataset even if automated coverage arrives later. If a source blocks integration, keep its connector disabled and proceed with manual/authorized imports and another approved source. Do not hold the website hostage to one marketplace.

### MVP launch checklist

- [ ] Physical and digital editions can be distinguished and independently saved.
- [ ] All four requested origins are supported, with accurate origin provenance.
- [ ] Search, filters, details and external purchase links work on desktop/mobile web.
- [ ] At least one automated source runs reliably; other sources clearly show manual/pending coverage.
- [ ] Reimporting data produces no duplicates; uncertain matches can be reviewed.
- [ ] Prices retain currency/type; unknown sold prices and shipping remain unknown.
- [ ] Admin and worker endpoints enforce authorization.
- [ ] Interrupted jobs recover; blocked sources do not erase offers or mark them sold.
- [ ] Backups, migrations, logging, health checks and source disable controls are documented.

## Decisions to confirm during implementation

Working defaults are Next.js, Playwright-Go/Chromium, catalog-plus-external-links, English interface with original-script metadata, and mobile deferred. Confirm whether the catalog includes all photography books or primarily creator/model photobooks; whether age-restricted publications belong in launch scope; and whether the chosen PostgreSQL database is dedicated to MuseBooks before applying migrations. Source access and image reuse need source-specific decisions, recorded with each adapter.

The next concrete task is milestone 0 followed by the catalog vertical slice: define work/edition/listing contracts, seed a small representative catalog, and build the website against the Go API before expanding scraper coverage.
