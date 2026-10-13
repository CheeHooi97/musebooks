# MuseBooks scraper

Read [scraper.md](scraper.md) for the country/marketplace search specification,
physical/digital rules, cited online research, adapter behavior, and live
validation checklist. `../scraper_worker/` is the inspected reference;
implementation lives here.

The production collection path is the Python worker in this `scraper/` folder. It
uses CloakBrowser to inspect rendered marketplace pages and emits normalized
photobook observations for the Go control-plane API. The marketplace side is
browser-only: no eBay, Rakuten, JD, Shopee, Lazada, or other marketplace API is
called.

It deliberately does not bypass login walls, CAPTCHAs, robots restrictions, or anti-bot controls. Marketplace-specific selectors belong in separate Python browser adapters; marketplace SDKs and REST APIs are not part of this worker.

## Install and run

```powershell
python -m pip install -r scraper/requirements.txt
python scraper/run_api_worker.py --worker-id jp-tw-cn-my-01
```

Run the offline adapter contract check without starting a worker or opening a
browser:

```powershell
python scraper/dry_run_marketplaces.py
```

The dry run only builds/validates rendered search and detail URLs. It does not
fetch marketplace pages, create jobs, or ingest records.

The runner claims jobs from the Go API, starts a separate
`photobook_worker.py` process for each job, ingests the batch, and completes or
requeues the job. Configure the API URL and token first:

```powershell
$env:MUSEBOOKS_API_URL = "http://localhost:2001"
$env:SCRAPER_INGEST_TOKEN = "change-me"
python scraper/run_api_worker.py --worker-id jp-tw-cn-my-01
```

Jobs may carry an exact rendered `url`/`searchUrl`; otherwise the source-specific
rules in `marketplace_adapters.py` build a verified consumer route when one is
known. Each job also carries the source allow-list, locale, timezone, adapter
name, requested format, and resumable page cursor. Dynamic/form-driven sources
must submit the exact rendered search URL. Do not add a marketplace SDK or REST
client.

Every accepted observation must identify `format` as either `physical` or
`digital`. Digital observations from a marketplace must also include
`digitalAccess` such as `authorized_store`; file-resale, pirated, and unknown
digital sources are rejected. The Python worker defaults normal photobook
listings to `physical`, recognizes common e-book/PDF markers as `digital`, and
accepts a JSON `format` field for a physical/digital job filter.

For resale price research, use separate `active_discovery` and
`sold_discovery` jobs. These operations automatically require a resale or
auction marketplace source; `marketplaceOnly: true` may still be sent
explicitly for clarity. Active jobs require item-local availability evidence;
sold jobs require explicit sale/winning-price evidence. An ended auction,
current bid, seller sales counter or fixed bookstore price is not a sold
transaction.

The classifier is human-model-only. It accepts model, idol, celebrity, actor,
actress, singer, gravure, influencer and equivalent JP/TW/CN labels. It
rejects photographer/artist monographs and generic photography books even
when `knownPhotobook` or `personKeywords` are supplied. For a title that omits
the role label, pass a verified `humanModelKeywords` (or `modelKeywords`) list;
do not use photographer names in that field.

## API-controlled worker flow

### Japan photobook fields

Japan uses the same discovery/detail/normalization pipeline as Taiwan through
`japan_photobook_worker.py`. The batch's `sourceId` identifies the platform;
each item includes `title`, `url`, `priceMinor`, `currency`, `priceType`, and
`releaseDate`. JPY amounts have no fractional minor units.

`releaseDate` is the book publication date in `YYYY-MM-DD` form. Japanese
detail pages must provide an explicit 発売日/発行日/出版日 label (including
their 年月日 forms), or a typed Book schema publication date. Marketplace
Product `datePublished`, listing dates, observation dates, partial dates,
and conflicting book dates do not establish a release date; it remains empty.
Existing marketplace restrictions and source enablement still apply.

Offline regression checks:

```powershell
python -m unittest discover -s scraper -p 'test_japan.py'
```

Capture a bounded local snapshot across Yahoo Auctions, Yahoo Flea Market, and
Rakuma, using the checked-in source settings and their navigation rate limits:

```powershell
python scraper/run_japan_snapshot.py --output scraper/japan-snapshot --details 10
```

The runner saves per-platform raw captures plus `photobooks.json` and
`photobooks.csv` with platform, title, source URL, JPY price, price basis,
publication date, and observation time. It records source failures and excludes
zero-price results from the summary. Use `--source` to select a platform and
`--query` to search a different title or model. This snapshot does not import
records or upload covers. Bundle prices are whole-listing prices.

The standard runner uses `scraper/musebooks_api.py` to claim a job, passes
the source configuration to the Python browser adapter, ingests the batch, and
completes the lease:

```powershell
python scraper/run_api_worker.py --worker-id jp-tw-cn-my-01
```

The internal endpoints are:

| Method | Endpoint | Purpose |
| --- | --- | --- |
| POST | `/v1/internal/scrape/jobs` | enqueue a source-scoped adapter request |
| POST | `/v1/internal/scrape/jobs/claim` | atomically lease the next job |
| POST | `/v1/internal/scrape/jobs/{id}/heartbeat` | extend a live lease |
| POST | `/v1/internal/scrape/batches` | upsert listings and append idempotent observations |
| POST | `/v1/internal/scrape/jobs/{id}/complete` | mark success/blocked or requeue after failure |

Send `X-Scraper-Token` on every internal request. A claim response includes the
source's `region`, `locale`, `timezone`, `accessMethod`, `capabilities`,
`adapter`, `allowedHosts`, `accessStatus`, and `ratePerMinute`, plus a lease token that
must be echoed on heartbeats, batches, and completion. The API validates any job
URL against the source allow-list, so adapters should submit the actual source
URL rather than an arbitrary redirect or proxy URL.

Create a browser job by passing a rendered consumer-page URL. For example:

```powershell
$job = @{
  sourceId = "ebay"
  operation = "active_discovery"
  request = @{
    query = "model photobook"
    format = "physical"
    marketplaceOnly = $true
    targetScope = "people"
    humanModelKeywords = @("Example Model")
    fetchDetails = $true
    maxPages = 2
  }
} | ConvertTo-Json -Depth 6

Invoke-RestMethod -Method Post `
  -Uri "http://localhost:2001/v1/internal/scrape/jobs" `
  -Headers @{ "X-Scraper-Token" = $env:SCRAPER_INGEST_TOKEN } `
  -ContentType "application/json" -Body $job
```

Use the same envelope with `yahoo-auctions-jp`, `mercari-jp`, `rakuma`,
`yahoo-furima-jp`, `surugaya`, `mandarake`, `books-com-tw`, `ruten-tw`,
`shopee-tw`, `yahoo-tw`, `bookwalker-tw`, `readmoo-tw`, `jd-cn`, `taobao-cn`,
`xianyu-cn`, `dangdang-cn`, `carousell-my`, `shopee-my`,
`lazada-my`, `mudah-my`, `bookwalker-jp`, or `rakuten-books-jp`. Use `MY` for
Malaysia; an upstream `MLS` region label
should be normalized to `MY` before selecting a source. The URL, when supplied,
must be the source's permitted rendered page; the worker will reject a
different host.

Use `yahoo-auctions-jp` for JDirectItems Auction as well. The Python adapter
accepts `jdirectitems-auction-jp`/`jdirectmarket` as compatibility aliases, but
the API keeps one canonical Yahoo source and auction ID so one listing is not
counted twice.

## Resume Japan models from MuseCards

The read-only `gravure_model` export is stored in
`japan-models/musecards-models.json`. Run `prepare_japan_model_queue.py` after
refreshing that export; it updates names and aliases while retaining queue
state and existing captures. This selects people associated with Japan-market
releases; it does not infer nationality.

```powershell
python scraper/prepare_japan_model_queue.py
python scraper/run_japan_model_queue.py --source physical
python scraper/run_japan_model_queue.py --source grajapa
python scraper/run_japan_model_queue.py --source kobo
python scraper/run_japan_model_queue.py --source wani
```

Each source queue owns an OS file lock. Independent sources can run together;
a second queue for the same source is rejected. Completed queries are retained.
Failed searches/details and missing name queries remain pending. Physical
completion is checked per platform and query, including relevance-limited
stops. Repeated source failures stop the queue with checkpoints intact. Use
`--dry-run` to inspect pending models or `--limit 1` for a bounded retry.

Collectors and newly launched queues use `capture_checkpoint.save_json` to
stage JSON beside its destination, then replace it atomically. Brief Windows
file locks receive bounded retries; a permanent failure preserves the last
valid checkpoint and remains an error. Staging names are unique to each write.

Physical captures retain qualifying failed product pages in `pendingDetails`,
independently of pagination. They retry each pending public detail once after
the model's search pass and remain incomplete while any detail is unresolved.
Recovered details retain offers and cached evidence; a completed rejection
also resolves its pending page. Legacy recovery uses retained model-matching
candidate evidence. Search coverage is restored only after its pending details
are resolved, and failed searches are never cleared by detail recovery.

Reviewed physical/digital publication relationships are stored in
`japan-cross-format-identities.json`, with publisher ISBN and store format-pair
evidence. The work repair retains every source edition and price. The homepage
shows one verified publication card with separate paper/e-book price panels;
unmatched titles keep their format boundaries.

Build the import tools from `backend`, then return to the repository root:

```powershell
go build -o ../.tmp/japan-catalog-import-v2.exe ./cmd/catalog-import
go build -o ../.tmp/japan-work-repair.exe ./cmd/japan-work-repair
go build -o ../.tmp/verify-japan-import.exe ./cmd/japan-import-verify
```

```powershell
python scraper/import_japan_model_captures.py
python scraper/import_japan_model_captures.py --apply
```

The apply workflow reads current database ownership, extends exact
model/title/publisher work identities, requires a passing capture-quality audit,
validates and applies the repair, imports
offers transactionally, saves content-hash checkpoints, and verifies prices,
formats, media and edition-to-work ownership. Partly imported groups retain the
existing work ID. Source editions, seller offers and observations remain
separate. Title qualifiers and volumes are retained; ambiguous products remain
unmerged. An import failure leaves its database transaction unapplied.

For explicitly authorized automatic imports while queues run, use
`watch_japan_model_imports.py --collector-pid <confirmed-pid> --interval 300`,
repeating `--collector-pid` for each main and serialized retry queue. The watcher
holds an exclusive lock, imports changed captures, and verifies database readback
after each batch. It stops after three consecutive failures and performs a final
import once all attached queues exit. Its interval is the delay between completed
batches; a large transaction may take longer than five minutes. Captures and
content-hash checkpoints remain available if the watcher stops.
If the local public IP changes outside the database allowlist, supply
`--database-ssh-host root@<existing-server> --database-ssh-key <existing-key>`.
The watcher forwards localhost port 4187 to the server's existing localhost
PostgreSQL listener, verifies the known SSH host key, and overrides host/port
only for its import child process. It retains database credentials and TLS mode,
does not change access rules, reconnects a terminated tunnel before the next
batch, and closes its managed connection when it exits.

Add `--publish-pages` to the SSH-configured watcher to publish working detail
routes after each verified database batch. The private server helper must be
installed at `/opt/musebooks/japan-import-pages`; it uses the repository's SEO
renderer and existing deployed assets. It stages changed book pages, creates
missing linked model/publisher profiles, retains rollback backups, and updates
the sitemap. Unverified records are never publication targets. Failed refresh
scopes remain in `japan-models/page-publication-pending.json` for retry even when
the database transaction already committed. The report is
`japan-models/page-publication-verification.json`.

For a bounded route repair, run `publish_japan_import_pages.py --ssh-host
<verified-production-host> --ssh-key <existing-key> --refresh-all` for a dry run,
then add `--apply` to publish the verified snapshot. This command holds the
import lock and requires cumulative database verification to pass first.

`npm run verify:japan-homepage-live` from `frontend` checks model search,
format filters and the expected shared work IDs against every live Japan offer
page. `japan-models/REPORT.md` reports captures, imports and unresolved searches
separately.

Kobo name coverage requires the photobook genre, not a broad author query.
Publisher queues keep the remaining pagination URLs per name so interrupted
searches resume at the unvisited page. Physical batches retain source timing
across page-sized jobs and preserve public render-failure evidence. Explicit
Yahoo zero-result messages terminate normally; blank/loading or blocked
documents remain failures.

Derived date normalization also applies to preserved model captures: a
retailer's release date is a `storeReleaseDate`, not proof of the original
publication date. Raw captures stay unchanged.

`python scraper/audit_japan_model_captures.py` audits the generated snapshot
and grouping proposal without database changes. It checks prices, currency,
digital authorization, covers, catalog/media ownership and shared offers,
retaining explicit preview exclusions.

Standalone digital photo books under magazine brands are accepted after all
other exclusions are rechecked. Obsolete magazine rejections remain pending
until reassessed. Both `collect_model_kobo.py --offline` and
`collect_model_digital.py --offline` reuse saved product evidence without
launching a browser. Incomplete queries, uncaptured details and pagination
stalls stay pending. Observation timestamps remain those of the saved evidence.

See [marketplace-research.md](marketplace-research.md) for the current
browser-only access matrix and review/disabled sources.
