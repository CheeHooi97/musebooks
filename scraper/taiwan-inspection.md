> Current policy: physical retail scraping remains excluded. Authorized Taiwan digital retail offers are supported for catalog, availability and current prices; digital sold-price scraping is unsupported. See digital-taiwan-inspection.md for verified stores and editions.

# Taiwan scraper verification — 2026-10-05

Public browser checks exercised search discovery, product details, normalization,
availability and price extraction. No records were imported into the database.

All changes apply to the book pipeline: `scraper/photobook_worker.py`, its
`taiwan_photobook_worker.py` entrypoint, and the MuseBooks backend. The API runner
invokes `photobook_worker.py`. Legacy `scraper_worker/` trading-card workers are
unchanged and are not used by the book job runner.

| Source | Active listings | Sold listings | Seed configuration |
| --- | --- | --- | --- |
| Ruten | Verified physical listing `22637632325045`, TWD 680; preorder availability | Explicit transaction evidence and final price required; general keyword sold-history search remains unverified | Enabled |
| Yahoo Taiwan | Verified physical listing `101752226580`, TWD 1,400 | Live completed book auction `101740043019` verified at TWD 150; general keyword sold-history search remains unverified | Enabled |
| BOOK☆WALKER Taiwan | Verified digital listings `238917` and `238918`, TWD 292 each | Retail storefront; no public completed-transaction feed | Enabled for catalog/active/detail |
| Readmoo | Verified digital listing `210373743000101`, TWD 369 | Retail storefront; no public completed-transaction feed | Enabled for catalog/active/detail |
| Books.com.tw | Search works, but sampled details redirected to member login | Retail storefront; no public completed-transaction feed | Disabled/blocked; skipped |
| Shopee Taiwan | Traffic/login verification prevented collection | Verification required; skipped | Disabled/blocked; skipped |

Seed settings apply when the backend next runs its existing seed routine. This
inspection does not restart the backend or modify the running database.

## Fixes and checks

- Small candidate limits scan beyond navigation; image alt text supplies titles.
  Books.com.tw tracking URLs preserve product IDs.
- BOOK☆WALKER's public form and single-book toggle were inspected: search uses
  `w` without `series_display`. Explicit `series_display=0` rendered a 404.
  Readmoo uses `q`; Yahoo pagination uses the observed `pg` key.
- Hydration and availability controls are checked before reporting empty results.
  Login/traffic and age gates are skipped. Restricted details do not discard
  public listings; an entirely blocked batch is reported as blocked.
- Taiwan sale-price labels take precedence over coupon, shipping and paper list
  prices. Book observations preserve TWD currency and source item identities.
- Sold records require completed-transaction evidence and a final sale price.
  Stock exhaustion, auction ending, seller instructions, sales counts and an
  active asking price are insufficient. Book jobs select active/sold behavior
  through their `operation` field.
- The API requires an exact public completed-item URL or closed-listing search URL
  for Ruten/Yahoo sold jobs, rejecting unverified keyword jobs before retries.
  Retail sold jobs fail explicitly because these stores do not publish such history.

All 32 Python book-worker/adapter tests pass; backend catalog/database checks pass.

## Live sold verification

The actual `taiwan_photobook_worker.py` entrypoint was invoked over JSON stdin
on 2026-10-05; its JSON batch output was checked. This validates collection and
normalization, not database ingestion.

- Yahoo `https://tw.bid.yahoo.com/item/101740043019`: selected book category
  `圖書與雜誌 / 影視娛樂 / 寫真集 / 女藝人`, auction ended 2026-05-01,
  named winning bidder and closing-price DOM field `$150`. Worker returned one
  physical observation, `status=completed`, `priceMinor=15000`, `currency=TWD`,
  `priceType=auction_hammer`, with no warnings.
- Yahoo `https://tw.bid.yahoo.com/item/101123136880`: 蔡依林寫真集, auction
  ended with `得標者 無`. Worker returned no sold observations and recorded
  `rejected_sold_status_unverified=1`.
- Ruten `https://www.ruten.com.tw/item/22313324017390/`: S.H.E.寫真書,
  removed listing, sold count 1 and historical asking price `$100`. No explicit
  final transaction price. Worker correctly rejected the sold observation.
- Ruten `https://www.ruten.com.tw/item/22637632325045/#history` and its public
  `https://mybid.ruten.com.tw/goods/historymore.php?g=22637632325045` detailed
  purchase-history page were inspected. Six purchases show masked buyer,
  quantity and date; neither page discloses transaction prices. Its current
  `$680–$870` offer range cannot establish prices paid by those buyers.

The live Yahoo check uncovered and fixed missing-colon winner labels, the
`結標價格` label, and joined price/bid-count text (`$1501 次出價` is `$150`
plus one bid). Closing prices are now read from the selected rendered DOM row.
Selected Yahoo breadcrumb categories provide book/subject evidence for titles
that abbreviate `寫真集`. Ended-auction labels override stale InStock metadata.
Auctions without winners and ambiguous final-price text remain rejected.

## Running jobs

Active marketplace:

```json
{"sourceId":"ruten-tw","operation":"active_discovery","request":{"query":"寫真集","format":"physical","fetchDetails":true,"maxPages":2,"humanModelKeywords":["えなこ","Enako"]}}
```

Active digital:

```json
{"sourceId":"readmoo-tw","operation":"active_discovery","request":{"query":"林襄","format":"digital","fetchDetails":true,"maxPages":2,"humanModelKeywords":["林襄"]}}
```

Sold jobs use `operation: "sold_discovery"` and `request.url` for a public
completed item, or `request.searchUrl` for public closed-listing results. Sale
evidence and final price are verified on those pages. Yahoo's public completed
auction path is live-verified as above. Ruten's sampled public history does not
expose final prices, so priced sold coverage there remains unverified.

Verified Yahoo request (worker input):

```json
{"sourceId":"yahoo-tw","source":{"id":"yahoo-tw","kind":"marketplace","region":"TW","allowedFormats":["physical"],"allowedHosts":["tw.bid.yahoo.com"]},"operation":"sold_discovery","url":"https://tw.bid.yahoo.com/item/101740043019","format":"physical","maxCandidates":1,"maxDetailPages":1}
```

## Ruten sold reinspection — 2026-10-06

Ran the actual `taiwan_photobook_worker.py` against public book details
`22313324017390` (S.H.E.) and `22637632325045` (Enako). Both completed browser
collection, returned zero sold observations and explicitly reported
`soldVerification=unverified` with `rejected_sold_status_unverified=1`.
These are successful negative checks, not verified sales.

Reopened the Enako listing's visible detailed-purchase-history link:
https://mybid.ruten.com.tw/goods/historymore.php?g=22637632325045
Its six public rows contain buyer, quantity and timestamp, with no transaction
price column. A current offer or a sales counter cannot establish the amount
paid by any one buyer. No usable public priced transaction feed was found in
this inspection. Public sold support remains conditional on an exact detail
page showing both selected-item completed-transaction evidence and a labelled
final price; generic sold keyword search remains unverified.

Fixed transaction-status checks to use the selected detail body rather than
search-card text. Cancelled/uncompleted transactions override positive sale
labels. Added explicit Ruten sold-verification diagnostics and warnings so an
empty batch is not mistaken for successful sold-price verification. Added
regression coverage for all three behaviors. Retail exclusions remain in force.

To verify a positive Ruten sale, provide a public book detail whose native
transaction panel exposes completed-sale evidence and its final price, then
run the regional worker with `operation=sold_discovery` and that exact `url`.
Authenticated order data would require a separate authorized integration;
public purchase-history rows alone cannot fill the missing price.

## Ruten public ended auctions confirmed — 2026-10-06

The broader inspection found public auction closing-bid data beyond fixed-price
photobooks. Ruten's official anniversary event links these completed auctions:
https://pub.ruten.com.tw/ruten20th/bid.html

| Public auction | Closing bid (TWD) | Native evidence |
| --- | ---: | --- |
| https://www.ruten.com.tw/item/62634000007143/ — 阿啾與小狗子的吐槽同萌 (book) | 3,660 | 競標結束, masked winner, closing time 2026/08/26 |
| https://www.ruten.com.tw/item/62634000007132/ — 胖虎 figurine | 667 | 競標結束, masked winner, closing time 2026/08/26 |
| https://www.ruten.com.tw/item/62632000006915/ — 阿啾軍旅同萌 (book) | 400 | 競標結束, masked winner, closing time 2026/08/14 |

All three native detail panels rendered anonymously in the browser. The label
remains `目前出價` after closing; a completed auction plus an actual masked
winner establishes it as the final winning bid. This does not independently
prove payment or delivery. The event includes ended lots with zero prices too,
so the ended badge alone must never establish a sale.

Updated the parser for this observed auction layout: masked winners plus ended
status qualify; current bid is accepted as closing price only for that verified
layout. Seller prose after `商品詳情` is excluded. Regression checks reject
ongoing auctions, absent winners, starting prices and seller-prose winners.
54 tests pass; the status parser also recognizes all three captured live pages.

Conclusion: Ruten DOES expose public completed-auction winning prices, including
books. The earlier fixed-price purchase-history limitation still applies.
These examples are ordinary books/collectibles, not proof of a sold photobook;
photobook filtering remains intact and general completed-auction search is
still unverified. Exact auction detail URLs can supply data when the item
matches the book worker's photobook scope.

## Automatic Ruten auction-index discovery — 2026-10-06

Ruten `sold_discovery` jobs now accept a keyword without an exact item URL.
The default adapter opens the verified public anniversary completed-auction
index, scans its rendered item links, canonicalizes legacy `/item/show?ID`
links, filters locally for the query and human-model photobook scope, then
verifies each qualifying selected detail's ended status, winner and final bid.
Non-book, ongoing and unrelated cards are filtered before detail limits.
The fixed index does not use invented page-number URLs. Exact detail/search
URLs remain supported. Seed hosts now include `pub.ruten.com.tw`; the exact
trusted default index also works with older source host settings.

Live default-path test with query `寫真集` scanned 73 public auction links,
found zero qualifying human-model photobooks, loaded one index page and
returned no fabricated sold observations. Diagnostics explicitly expose
`soldDiscoveryMethod=public_auction_index`, `auctionIndexCandidates=73`,
`soldVerification=unverified`, and no next cursor. This verifies discovery
execution, not a positive sold-photobook record. Coverage remains limited to
linked event lots; there is still no verified complete site-wide sold search.

Example enqueue payload (backend restart needed for the new validation rule):
```json
{"sourceId":"ruten-tw","operation":"sold_discovery","request":{"query":"寫真集","format":"physical","fetchDetails":true,"maxDetailPages":20}}
```

57 scraper tests pass, including automatic discovery-to-detail acceptance,
keyword/scope filtering and legacy-link normalization. Retail sources remain
excluded. Earlier statements requiring exact URLs are superseded for Ruten by
this bounded default discovery path; Yahoo Taiwan still requires explicit URLs.
