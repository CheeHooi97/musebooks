# Marketplace access research — browser-only plan

The newer [scraper.md](scraper.md) contains the detailed country/marketplace
search research and supersedes this preliminary matrix where they differ.
In particular, Rakuten has both paper and digital discovery surfaces, and
reachability in online research does not establish a working browser adapter.

Research checked 14 September 2026. This is an engineering/access matrix, not
legal advice. Every connector must be re-checked before production scheduling.

Product scope is intentionally limited to two edition formats: `physical`
(a printed, real-world copy) and `digital` (an authorized e-book/digital
photobook sold or distributed by the publisher/store). Do not import trading
cards, photo cards, posters, calendars, custom/empty albums, merchandise,
pirated files, or unidentified digital downloads.

Use `MY` as the canonical region code for Malaysia. `MLS` is not an ISO 3166
country code; if it means Malaysia in an upstream worker, map it to `MY` at the
API boundary and keep the marketplace ID separate.

## Recommended connector order

| Region | Source | Access surface | What the adapter should do | Status |
| --- | --- | --- | --- | --- |
| Global | eBay | Rendered consumer search/detail pages | Browser search/detail adapter; preserve auction vs fixed-price evidence and split active/sold jobs | Browser review |
| JP | Rakuten Books | Rendered consumer bookstore pages | Browser catalog/detail adapter; preserve native JPY and physical format | Browser review |
| CN | JD.com | Rendered consumer search/detail pages | Browser catalog/detail adapter; do not use Open Platform endpoints | Browser review |
| JP | Yahoo! JAPAN Auctions / JDirectItems Auction | Rendered auction pages | Low-rate browser adapter; require visible active/winning-sale evidence; one canonical Yahoo source ID | Review required |
| TW | Books.com.tw | Rendered bookstore pages | Browser catalog/detail adapter; separate printed and authorized e-book products | Review required |
| TW | Yahoo拍賣 Taiwan | Rendered auction/listing pages | Browser active/detail adapter; sold mode only with an exact rendered closed-listing URL and final/winning price | Review required |
| TW | Ruten | Rendered listing pages | Browser active/detail adapter; preserve condition and stock evidence | Review required |
| TW/MY | Shopee | Rendered consumer pages | Browser-only adapter for permitted pages; no seller/partner API | Review required |
| MY | Lazada | Rendered consumer pages | Browser-only adapter for permitted pages; no Open Platform API | Review required |
| JP | Mercari | Public pages with restrictive automation terms | Keep disabled unless written/official access is obtained | Blocked by default |
| CN | Taobao/Tmall, Xianyu | Rendered consumer pages | P3 browser investigation only; no login automation, bypasses, or private endpoints | Not enabled |
| MY | Carousell | Rendered consumer search/detail pages | Browser-only adapter after access review; reject custom albums and unrelated goods | Review required |
| MY | Mudah.my | Rendered classified search/detail pages | Browser active/detail adapter; no public sold-history claim | Review required |

The word “API” below refers only to the MuseBooks control-plane API. It is not
an instruction to call a marketplace API. All source rows are configured with
`accessMethod=browser`; rows marked review should remain unscheduled until the
operator has checked the current source terms and access behavior.

## Resale price modes

The scraper has two separate price-discovery operations:

| Operation | Accept | Do not treat as proof |
| --- | --- | --- |
| `active_discovery` | Item-local buy-now/available/in-stock/current-bid/time-left evidence | A search-card price with no availability, an old recommendation, or a sold badge from another product |
| `sold_discovery` | Explicit `Sold`, `落札`, `成交`, `已售`, winning/final/hammer-price evidence | `Ended`, `已結標`, disappearance, a current bid, seller sales count, or a fixed bookstore amount |

Active and sold resale jobs automatically require a resale/auction marketplace
source; callers may also send `marketplaceOnly=true` explicitly. The worker
rejects configured first-party bookstores, digital stores and used-retailer
reference sources for those modes. The product scope is always human-model
only: model/idol/celebrity/actor/gravure signals are required. Photographer,
artist, documentary and generic photography books are rejected. Exact-title
jobs can set `knownPhotobook=true`, but titles without a role label must also
provide a verified `humanModelKeywords`/`modelKeywords` value. `personKeywords`
and `photographerKeywords` never bypass the human-model gate.

JDirectItems Auction is treated as a Yahoo Auctions access/rebranding/proxy
alias, not a second marketplace inventory. Keep its Yahoo auction ID and
canonical `yahoo-auctions-jp` source identity so the same offer is not counted
twice. BookOff Online, where useful, is a used-retailer asking-price reference,
not a public transaction-history source.

## Normalized adapter contract

The Go API does not know marketplace selectors. It gives a Python adapter a
job envelope:

```json
{
  "job": {
    "id": "scrape-job-...",
    "sourceId": "ruten-tw",
    "operation": "active_discovery",
    "leaseToken": "lease-...",
    "pageCursor": "",
    "request": {
      "query": "寫真集",
      "url": "https://www.ruten.com.tw/find/?q=...",
      "maxPages": 2
    }
  },
  "source": {
    "region": "TW",
    "locale": "zh-TW",
    "timezone": "Asia/Taipei",
    "adapter": "ruten_tw",
    "accessMethod": "browser",
    "capabilities": ["active_discovery", "listing_detail"]
  }
}
```

The adapter submits a batch to `/v1/internal/scrape/batches` with the original
marketplace ID, external listing ID, canonical source URL, native amount and
currency, `format` (`physical` or `digital`), and—when digital—authorized
`digitalAccess` evidence, availability/status evidence, `observationId`, parser
version, and the next cursor. It then calls the completion endpoint. Repeating a batch with
the same observation identity is safe: listings are upserted and observation
history is de-duplicated.

## What the research changed

- Marketplace SDKs and REST clients are intentionally out of scope, even when a
  source offers one. The Python process receives a source-scoped page URL and
  reads only the rendered page through CloakBrowser.
- The Go API validates the source host, leases the job, accepts normalized
  observations, and records parser/status/format evidence. It never proxies a
  marketplace API request.
- Mercari remains blocked because its current platform terms prohibit automated
  extraction; a rendered page being reachable is not sufficient permission.
- Digital results are accepted only when the page and source identify an
  authorized store/publisher/e-book surface. File resellers, piracy,
  torrents, DRM retrieval and unidentified downloads are rejected.

The API stores these findings as source configuration (`accessMethod`,
`accessStatus`, `termsUrl`, `allowedHosts`, `capabilities`, `ratePerMinute`) so
an operator can disable a source without changing adapter code.

The current offline contract check is `python scraper/dry_run_marketplaces.py`.
It validates URL construction and record-ID extraction for eBay, Yahoo Japan,
Yahoo Taiwan, Mudah, Books.com.tw and Rakuten Books without launching
the browser or fetching marketplace pages.

## Operational rules

1. Use the Python CloakBrowser worker against permitted rendered pages only.
   Never use CAPTCHA solving, login/session theft, proxy evasion, marketplace
   SDKs, undocumented private endpoints, or DRM/file retrieval.
2. Treat a challenge/login wall as `blocked`, not as zero listings.
3. Keep source-local timezone for parsing and store UTC in the API.
4. Preserve asking, auction current bid, ended/unavailable and confirmed sold
   as separate status/price evidence; disappearance alone is not a sale. Run
   active and sold discovery as separate jobs.
5. Keep source IDs stable and separate from retrieval/proxy domains. A proxy
   page is not an independent marketplace listing.
