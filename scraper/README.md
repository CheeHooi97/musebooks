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
`shopee-tw`, `bookwalker-tw`, `readmoo-tw`, `jd-cn`, `taobao-cn`, `xianyu-cn`,
`dangdang-cn`, `carousell-my`, `shopee-my`, `lazada-my`, `bookwalker-jp`, or
`rakuten-books-jp`. Use `MY` for Malaysia; an upstream `MLS` region label
should be normalized to `MY` before selecting a source. The URL, when supplied,
must be the source's permitted rendered page; the worker will reject a
different host.

Use `yahoo-auctions-jp` for JDirectItems Auction as well. The Python adapter
accepts `jdirectitems-auction-jp`/`jdirectmarket` as compatibility aliases, but
the API keeps one canonical Yahoo source and auction ID so one listing is not
counted twice.

See [marketplace-research.md](marketplace-research.md) for the current
browser-only access matrix and review/disabled sources.
