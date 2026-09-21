# Photobook marketplace scraping specification

Research date: 2026-09-14. Implementation directory: `scraper/`.
Reference inspected: `../scraper_worker/worker.py`, its regional entrypoints,
`catalog_worker.py`, and the existing photobook collector and API runner.

This document covers every currently seeded marketplace in JP, TW, CN, MY and
global eBay, plus relevant expansion sources. It specifies browser-page
collection using Python/CloakBrowser. Only the MuseBooks job/ingest service is
called as an API. Collect listing metadata and source links, not book files.

## Evidence and implementation status

- **Observed** means a first-party search/category/product page was available
  through online research. Search-engine snapshots may be older than this date.
- **Reference** means the route or pagination rule exists in `scraper_worker`;
  it has not been validated against a live browser during this research.
- **Candidate** means a proposed route or workflow still needs confirmation.
- **Unavailable in research** means the research tool returned no usable page;
  it does not establish that a browser scraper cannot access the site.

A direct CloakBrowser smoke run was completed on 2026-09-14 against the
browser-only worker. It reached eBay, Yahoo Auctions, Mercari, Rakuma, Yahoo
Flea Market, Rakuten Books, BOOK☆WALKER Japan/Taiwan and other configured
surfaces, but reachability varied by source and several returned challenges or
empty/SPA pages. This was not a PostgreSQL ingestion test and does not grant
permission to enable a source. The adapter rules below remain executable
routing and identity guards, not a claim that every source is currently
reachable or permitted. Do not invent CSS selectors from search snippets.
Capture actual rendered product cards before committing selectors or enabling
scheduled collection.

## Scope and search vocabulary

| Region | Physical discovery queries | Digital discovery queries | Locale / timezone / currency |
| --- | --- | --- | --- |
| JP | `{model} 写真集`, `{model} フォトブック`, `{model} 電子写真集`, `{ISBN}` | `{model} 電子写真集`, `{model} デジタル写真集` on an authorized store | ja-JP / Asia/Tokyo / JPY |
| TW | `{model} 寫真集`, `{model} 寫真書`, `{model} 電子寫真集`, `{ISBN}` | `{model} 數位寫真`, `{model} 電子寫真集` on an authorized store | zh-TW / Asia/Taipei / TWD |
| CN | `{model} 写真集`, `{model} 写真书`, `{model} 电子写真集`, `{ISBN}` | `{model} 电子写真集`, `{model} 电子书` on an authorized store | zh-CN / Asia/Shanghai / CNY |
| MY | `{model} photobook`, `{model} photo book`, `{model} ebook`, `{ISBN}` | `{model} ebook`, `{model} digital photobook` on an authorized store | en-MY / Asia/Kuala_Lumpur / MYR |
| Global | `{title} photobook`, `{ISBN}`, native-language title aliases | Exact title plus `ebook`, only with verified digital seller provenance | Source currency; do not assume USD from `$` alone |

Run aliases as separate searches and union by listing identity. Do not send all
synonyms as one AND query. Preserve original names and accents; normalize
Unicode for matching, and percent-encode query values once. Match exact-title
or ISBN discoveries even when the title does not contain a photobook keyword;
for those jobs, pass `knownPhotobook=true` with `expectedTitle`/`titleAliases` or
`isbn`, and also pass a verified `humanModelKeywords`/`modelKeywords` value.
`knownPhotobook` only relaxes the book-format word check; it never bypasses the
human-model gate. Store marketplace region separately from the publication's
origin.

Use `MY` for Malaysia. `MLS` was used conversationally for Malaysia; source IDs
remain the canonical marketplace IDs, while the Python currency fallback also
accepts an upstream `MLS` region value.

## Marketplace-first price collection

For resale pricing, create two independent jobs for the same title. Do not
mix asking/current-bid values with completed-sale values:

```json
{
  "sourceId": "ebay",
  "operation": "active_discovery",
  "request": {
    "query": "Example Model photobook",
    "format": "physical",
    "marketplaceOnly": true,
    "targetScope": "people",
    "humanModelKeywords": ["Example Model"],
    "fetchDetails": true
  }
}
```

Use the same request with `operation: "sold_discovery"` for historical sales.
The eBay adapter adds the rendered completed/sold filters; Yahoo Auctions uses
its closed-search surface; Mercari uses its sold-out filter. The worker accepts
an active observation only with item-local availability evidence and accepts a
sold observation only with explicit sale evidence such as `Sold`, `落札`,
`成交`, `已售` or a winning/final price. `Ended`/`已結標` by itself is not a
sale. This prevents an auction's current bid or an unsold expired listing from
becoming a historical price.

`marketplaceOnly: true` rejects configured fixed-price bookstores and digital
stores, including Rakuten Books, BOOK☆WALKER, Books.com.tw, Readmoo, JD,
Dangdang, Suruga-ya and Mandarake. Those sources may still be used for edition
discovery or fixed-price reference data, but they are not the primary resale
price sample.

The photobook classifier is human-model-only. It requires a product-local
model/person signal such as `model`, `idol`, `celebrity`, `actor`, `actress`,
`gravure`, `グラビア`, `模特`, or `偶像`. A title without that role label may
only pass when the job supplies a verified `humanModelKeywords` or
`modelKeywords` value. Photographer/artist monographs, documentary/street
photography books and generic photography collections are excluded, including
when `knownPhotobook` or `personKeywords` is present.
`targetScope` is retained for request compatibility but is narrowed to
`people` by the worker.

### Marketplace source priority

| Priority | Source | Region | Active price | Sold price | Notes |
| --- | --- | --- | --- | --- | --- |
| P0 | eBay — `ebay` | Global | Yes | Yes | Best initial cross-border source; preserve fixed, Buy It Now and auction evidence separately. |
| P0 | Yahoo! JAPAN Auctions — `yahoo-auctions-jp` | JP | Yes | Yes | The strongest Japanese auction source; closed results still require explicit winning/sale evidence. |
| P1 | Mercari Japan — `mercari-jp` | JP | Yes | Limited/yes when sold-out evidence is rendered | Keep disabled until access/terms review; browser reachability is not permission. |
| P1 | Rakuma — `rakuma` | JP | Yes | Usually item/seller evidence, not a complete public sale history | Good extra active-market sample; validate sold labels before using historical prices. |
| P1 | Yahoo! Flea Market — `yahoo-furima-jp` | JP | Yes | Limited | Use for active inventory unless a public sold surface is verified. |
| P1 | Yahoo拍賣 — `yahoo-tw` | TW | Yes | Requires an exact rendered closed-listing URL and visible final/winning price | The active keyword route is implemented; the source remains disabled pending browser/access review. `已結標` alone is not proof of a sale. |
| P1 | Xianyu/Goofish — `xianyu-cn` | CN | Yes | Limited | Strong second-hand candidate, but public web search/detail routes need browser validation. |
| P1 | Kongfz/孔夫子旧书网 — `kongfz-cn` | CN | Yes | Requires an exact rendered active/sold surface and visible final/winning price | Detail identity and host allow-list are implemented; keyword search is intentionally form-driven and the source remains disabled pending browser/access review. |
| P1 | Carousell — `carousell-my` | MY | Yes | Limited | Useful active local inventory; public historical sold prices are not a dependable baseline. |
| P1 | Mudah.my — `mudah-my` | MY | Yes | No verified public sold history | The active keyword route and ad-ID extraction are implemented; it is classified/recommerce inventory, not an auction-history source, and remains disabled pending browser/access review. |
| P2 | Ruten / Shopee / Taobao / Lazada | TW/CN/MY | Yes | Usually no reliable public sold history | Good supplementary active offers; inspect variant/stock because cards, posters, vouchers and printing services are common. |

`JDirectItems Auction` is not a second inventory source to add beside Yahoo
Auctions. It is a Yahoo auction access/rebranding/proxy surface (often reached
through an overseas buying service). The adapter accepts the aliases
`jdirectitems-auction-jp` and `jdirectmarket`, but routes to the canonical
Yahoo Auctions identity and keeps the Yahoo auction ID for deduplication. Do
not ingest both names as separate offers.

BookOff Online is a useful optional used-retailer comparison source, but it is
not a C2C marketplace and its displayed amount is an asking price. Keep it out
of `marketplaceOnly` sold-price jobs unless the product is explicitly being
used as a used-retail reference rather than a transaction-history observation.

### Decide what the product actually is

1. Accept a published printed photobook or an authorized digital photobook.
   ISBN helps edition matching but is not mandatory for independent publications.
2. Reject blank albums, photocard binders, printing services, print vouchers,
   posters/cards sold alone, magazines sold only for a photobook-related feature,
   photography tutorials, and illustration-only artbooks.
3. `写真集 + ポストカード付き` can be a real book with a bonus. Do not reject
   every title containing a card/poster word. `特典のみ`, `本なし`, or a clear
   card-only listing should be rejected. Ambiguous bundles require review.
4. The selected book must be about or feature a human model/person; a
   photographer-led or landscape/street-photography book is out of scope.
5. A CD album's “photobook version” is not automatically a standalone photobook.
   Accept only if the sold object includes the actual book and the catalog can
   represent the bundle correctly; otherwise retain it for review.
6. Digital vouchers, video access codes, camera manuals mentioning “digital”,
   and a site's navigation link to e-books do not prove digital book format.
7. Infer format from the selected product/variant, category and description,
   never the whole page's recommendation widgets. If ambiguous, defer the item.
8. A seller writing “official” is not sufficient authorization evidence. Verify
   publisher/store identity before accepting downloadable or reader-access editions.

## Japan — JP

### Yahoo! JAPAN Auctions — `yahoo-auctions-jp`

**Observed:** [photobook category 21604](https://auctions.yahoo.co.jp/list4/21604-catlist.html)
and [closed photobook category](https://auctions.yahoo.co.jp/closedsearch/closedsearch/21604).
Use physical discovery; do not interpret resale file listings as authorized e-books.

**Reference search:** `https://auctions.yahoo.co.jp/search/search?p={encoded_query}`.
Prefer the photobook category plus title/person keywords. Keep active and
completed searches separate. The reference builds closed keyword searches at
`/closedsearch/closedsearch/{encoded_query}/0/`; confirm the rendered search
heading and per-item sale evidence before using that route.

**Reference pagination:** `b=((page-1)*page_size)+1`, `n=page_size`.
At size 50, pages 1 and 2 begin at `b=1` and `b=51`. `page=2` is insufficient.
Accept detail links shaped `/jp/auction/{auction_id}` and use that ID.

Extract the product title, condition, shipping, current bid, buy-now amount,
bid count and ending time separately. A current bid is not a completed price.
Only explicit winning-price and sale evidence may become a sold observation;
an ended auction without a buyer remains ended/unknown. Parse local dates in JST.
Fixture requirement: active auction with both prices, ended-unsold auction,
and completed auction with visible final price/date.

### Mercari Japan — `mercari-jp`

**Observed:** [keyword search](https://jp.mercari.com/search?keyword=%E5%86%99%E7%9C%9F%E9%9B%86)
and [talent photobook category 10117](https://jp.mercari.com/search?category_id=10117).
The result surface includes an on-sale filter and unrelated bonus-only goods.
Do not reuse the reference's trading-card category 7325.

**Reference search:** `/search?keyword={encoded_query}&status=on_sale`.
The reference uses `sold_out` for sold-only searches and `page_token=v1:N`
for later pages. Treat the token shape as unverified: follow the actual Next
control when available and stop on repeated listing IDs.

**Reference detail paths:** `/item/{id}` and `/shops/product/{id}`; keep their
identities distinct. Extract item-local sold badge, condition and shipping payer.
Use physical only; a title mentioning digital does not authorize a file resale.
Existing backend configuration blocks this source. This document does not
change that setting or establish permission to collect it.

### Rakuten Books / Kobo — `rakuten-books-jp`

**Observed physical:** [books category 001013](https://books.rakuten.co.jp/search?g=001013).
**Observed digital:** [e-book category 101915](https://books.rakuten.co.jp/search?g=101915&l-id=search-l-price-0).
These are consumer pages, not API routes. Start separate format jobs from each
category, add a keyword using the rendered search form, and capture its result URL.

Physical search includes stock/preorder and release filters. Digital results
label the e-book edition and can link to a paper counterpart. Do not import that
counterpart's price as the e-book price. Follow actual pagination links and keep
genre, keyword and sort state; numeric page parameters have not been verified here.

Resolve detail IDs from actual product links; keep ISBN separate from a store's
internal product number. Extract publisher, release date, binding/page count,
format, tax-inclusive price and preorder/stock evidence from the selected edition.
The current seed allows only physical: digital jobs need `allowedFormats` updated
or a dedicated Kobo source after adapter validation.

### BOOK☆WALKER Japan — `bookwalker-jp`

**Observed:** [photobook new releases](https://bookwalker.jp/new/?qcat=8),
[artbook/photobook landing page](https://bookwalker.jp/tcl59/), and
[store help confirming electronic delivery](https://help.bookwalker.jp/faq/2837).
Use the photobook new-release category for discovery, then the rendered search
form for a person/title. The combined artbook landing page needs extra relevance
filtering. The store sells digital books; it does not ship a physical copy.

Follow rendered numbered/Next links, retaining the category. Resolve product
identity from the actual detail URL, commonly a `de...` identifier. A series
card is not one edition: expand it into individual books. Extract model/author,
photographer, publisher/label, release date and the current book price. Store
reader access as digital without assuming PDF/EPUB download availability.

### Japan expansion sources from the reference

| Source | Search evidence and format | Browser adapter requirements |
| --- | --- | --- |
| Rakuma — `rakuma` | [Observed photobook search](https://fril.jp/s?query=%E5%86%99%E7%9C%9F%E9%9B%86); physical | Reference uses `fril.jp/s?query={q}` and `item.fril.jp/{id}`. Allow search and detail hosts separately; follow observed Next links; inspect sold badge and bonus-only descriptions. |
| Yahoo! Flea Market — `yahoo-furima-jp` | [Observed hashtag search](https://paypayfleamarket.yahoo.co.jp/hashtag/%E5%86%99%E7%9C%9F%E9%9B%86); physical | Reference keyword route `/search/{q}` and detail `/item/{id}`. A [later hashtag page](https://paypayfleamarket.yahoo.co.jp/hashtag/%E5%86%99%E7%9C%9F%E9%9B%86?page=6) is indexed, but do not assume the keyword page shares its pagination. |
| Suruga-ya — `surugaya` | [Observed book category](https://www.suruga-ya.jp/search?category=70008&search_word=); primarily physical | Current observed search uses `search_word`, unlike the reference's `keyword`. Use book category 70008, not calendar category 100201. Distinguish store used/new prices and third-party offers. A “digital photobook” category label alone does not prove online delivery. |
| Mandarake — `mandarake` | [Store photobook announcement](https://www.mandarake.co.jp/dir/sby/deep/2024/06/24/deephaneame.html); physical | Reference `/order/listPage/list?keyword={q}&lang=en` is not live-validated. Detail identity uses the `itemCode` query value; taking the last path segment `item` merges unrelated products. Follow actual stock/detail links. |

These expansion sources are not currently seeded. Implement and validate their
source configuration before enqueueing their jobs.

## Taiwan — TW

### Books.com.tw — `books-com-tw`

**Observed:** [search for 寫真集](https://search.books.com.tw/search/query/key/%E5%AF%AB%E7%9C%9F%E9%9B%86/cat/all)
offers separate book, magazine and e-book filters. Both formats are discoverable.
Search route: `https://search.books.com.tw/search/query/key/{encoded_query}/cat/all`.
Select the physical or e-book filter through the page and record the resulting
URL; filter codes and pagination are not asserted here.

**Host fix required:** search uses `search.books.com.tw`; detail pages use
`www.books.com.tw/products/{id}`. The current seed allows only the latter, so
search jobs cannot run until the search host is added. Preserve M/E/other product
prefixes exactly; verify format on the page rather than relying only on a prefix.

The [physical product example](https://www.books.com.tw/products/M010047280)
establishes a printed photobook surface. Japanese imports may be classified as
magazines, so reject periodicals by product evidence rather than blanket category
exclusion. Extract ISBN, publisher, publication date, language, selected format,
price and availability. Follow visible pagination; keep separate edition records.

### Ruten — `ruten-tw`

**Observed:** [photobook product](https://www.ruten.com.tw/item/22613330948551/).
**Reference search:** `https://www.ruten.com.tw/find/?q={encoded_query}`;
pagination `p=1`, `p=2`, etc. Accept `/item/{id}` product links rather than store,
category, question or advertisement links. Use physical discovery by default.

Extract TWD price, selected variant, condition, shipping, stock and preorder
state. The observed product has conflicting condition wording and an invalid
Infinity price in an uninitialized purchase widget: preserve the conflict and
reject non-finite widget amounts. `銷售` is a cumulative sales count, not proof
that the current listing is unavailable. Marketplace location is not book origin.
Digital candidates need independently verified store/publisher provenance.

### Shopee Taiwan — `shopee-tw`

**Observed:** [寫真書 result surface](https://shopee.tw/list/%E5%AF%AB%E7%9C%9F%E6%9B%B8).
**Reference search:** `https://shopee.tw/search?keyword={encoded_query}`.
Reference pagination is zero-based `page=0`, `page=1`; validate with changed
product IDs or use visible page controls. Native queries plus exact book titles
are preferable to broad English “photobook”.

Reference detail patterns: `/product/{shop_id}/{item_id}` or a slug ending
`-i.{shop_id}.{item_id}`. Preserve the pair as identity. Inspect the selected
variant: the cheapest variant may be a poster or card instead of the book.
Extract price, variant, stock/preorder, condition, shipping and seller. A sales
counter does not mean sold out. Digital coverage is unverified; printing vouchers
and seller file bundles are not digital book editions. Challenge/login pages
must return blocked instead of a successful empty batch.

### Yahoo拍賣 Taiwan — `yahoo-tw`

**Observed:** the [official Yahoo拍賣 search surface](https://tw.bid.yahoo.com/)
has a 圖書/影音/文具 category and supports both 直購 (direct purchase) and
競標 (bidding) listings. Its [official buying guide](https://tw.bid.yahoo.com/help/new_auc/itempage/buyMethod.html)
describes both purchase modes, and the [advanced search](https://tw.bid.yahoo.com/tw/show/searchoptions)
exposes used-item, direct-purchase, bidding and international-shipping filters.

This is a strong Taiwan addition for physical copies. The adapter now uses the
observed `/search/auction/product?p={query}` active route and recognizes the
numeric `/item/{id}` detail URL. Sold discovery deliberately requires the exact
closed-listing URL captured from the rendered UI; `已結標` means closed and must
not be stored as sold unless the detail shows a winning bid or final price. The
source is seeded but disabled pending browser/access review. Keep it distinct
from JP Yahoo Auctions even though both are Yahoo-branded.

### Taiwan digital expansion

| Source | Evidence | Search and records strategy |
| --- | --- | --- |
| BOOK☆WALKER Taiwan — proposed `bookwalker-tw` | [Observed detailed search](https://www.bookwalker.com.tw/index.php/search?detail=1) on the electronic-book store | Use the search form with title/person/寫真集 and retain its exact submitted URL. A guessed `/search?w=...` request was unavailable during research; do not call it verified. Follow book links, not series aggregation; capture digital edition and publisher metadata. |
| Readmoo — proposed `readmoo-tw` | [First-party category navigation](https://console.readmoo.com/welcome) includes 寫真集 | Start on the consumer store and select that category or search by title. The candidate `/search/keyword?q={q}` could not be opened in research. Confirm the actual form action and detail IDs before implementation. Do not scrape account/console data; the linked page is only coverage evidence. |

Neither expansion source is currently in the backend seed. Use TWD and
Asia/Taipei when those are actually the displayed currency/local dates; keep
Japanese originals and translated editions separate.

## China — CN

### JD.com — `jd-cn`

**Observed:** [photography collection discovery page](https://www.jd.com/hprm/17131578432011484457.html)
and a [photobook product with an opaque detail ID](https://item.jd.com/product/RT2I_8PwoffDScStU0L3LA.html).
The candidate search URL `https://search.jd.com/Search?keyword={q}&enc=utf-8`
was unavailable in the research tool. Confirm it through the consumer search form.

Search for 摄影集, 摄影作品集 or an exact title/ISBN; exclude photography technique
manuals and custom albums. Use physical as the first implementation scope.
Authorized digital photobook coverage was not established by this research.
Follow visible Next controls; do not assume that adding `page=2` advances results.

Support both numeric `/{sku}.html` and observed `/product/{opaque_id}.html`
detail routes. If a verified SKU is unavailable, retain the opaque identity and
canonical URL; never synthesize a numeric SKU. Extract selected SKU/variant,
publisher/ISBN, binding, displayed price, stock and seller/store identity.
Membership and coupon prices are conditional, not the default offer.
Add `www.jd.com` only if the discovery/category surface is intentionally used;
the existing seed's search/detail hosts do not include it.

### Taobao / Tmall — `taobao-cn`

**Candidate, not verified:** `https://s.taobao.com/search?q={encoded_query}`.
The research request returned no usable page and targeted search did not produce
usable first-party photobook evidence. Do not substitute affiliate aggregators
or undocumented search endpoints as evidence of working browser access.

Start with exact title/ISBN plus 写真集 or 摄影集. Use the rendered books/category
and physical variant filters where available. Exclude 定制/冲印 services,
binders and digital-file sellers. Digital availability remains unverified.
Candidate detail routes include `item.taobao.com/item.htm?id={id}` and
`detail.tmall.com/item.htm?id={id}`; capture actual links before accepting them.
The `id` query value is essential; the path `item.htm` is not an item identity.

Follow Next controls only after the result list renders. Preserve seller,
variant and displayed stock/price; do not take the cheapest non-book option.
Tmall's detail host is absent from the current seed, despite the combined source
name. It requires explicit configuration and testing. Login-only results remain
blocked; no credentials or private API workaround is part of this plan.

### Xianyu — `xianyu-cn`

**Observed:** the current [first-party web entry](https://www.goofish.com/) exposes
search navigation. A public photobook results page was not established.
The current seed points to `2.taobao.com`; do not assume it is the usable current
search surface. Confirm actual navigation and add the observed consumer hosts.

Proposed workflow: type an exact title or `{person} 写真集` in the visible search,
capture the result URL and item links, then inspect physical condition, included
pages, shipping and item availability. Digital book coverage remains unverified.
Avoid reusing anonymous seller “PDF/网盘” claims as publication evidence.

Pagination and detail-ID shape remain unverified. Implement them only after a
browser fixture identifies actual product links and controls. Keep deleted,
unavailable and sold separate. Do not use an app/private endpoint to compensate
for an unavailable public result list.

### Kongfz / 孔夫子旧书网 — `kongfz-cn`

**Observed:** [Kongfz](https://www.kongfz.com/?locale=en) is a Chinese C2C
second-hand book and collectibles platform with separate 在售 (active), 已售
(sold) and 在线拍卖 sections. The [about page](https://www.kongfz.com/help/aboutus.php)
describes its shop and auction marketplaces, which makes it a better candidate
for out-of-print photography books than JD's normal retail results.

The source is now seeded as `kongfz-cn` and the Python adapter recognizes the
public `book.kongfz.com/{shop_id}/{item_id}/` detail shape. Keyword discovery
is intentionally form-driven: supply the exact rendered search/category URL
captured by the browser rather than guessing a query endpoint. For ordinary
shop listings, record asking price as active inventory; for auction history,
require a final winning price and do not infer a sale from an ended lot. It is
still disabled pending browser/access review.

### Zhuanzhuan / 转转 — candidate secondary CN source

The [official Zhuanzhuan site](https://www.zhuanzhuan.com/) presents a
second-hand marketplace with platform-guaranteed transactions, and its
published coverage includes books. It is worth a later active-inventory
adapter, but the public web page is SPA-driven and no reliable public sold
history route was established. Keep it below Kongfz/Xianyu until a rendered
search/detail fixture is available.

### Dangdang — proposed `dangdang-cn`

**Observed:** [advanced search](https://search.dangdang.com/advsearch) has paper/e-book
selection and title, author, publisher and ISBN fields; the
[photography category](https://category.dangdang.com/cp01.07.05.00.00.00-as8589934592%3A8589934753.html)
includes physical photography collections. Use the form's selected medium and
capture the submitted URL. A digital search control proves the control exists,
not that the same physical title has an electronic edition.

For physical records, follow `product.dangdang.com/{id}.html` links, keep the
actual offer price separate from list price, and extract publisher/ISBN/stock.
Use the observed Next link. Exclude instruction manuals and illustration-only
collections. Digital photobook availability and routes need a product fixture.
This expansion source is not seeded.

## Malaysia — MY

### Carousell Malaysia — `carousell-my`

**Observed:** [consumer home/search](https://www.carousell.com.my/) and an
[example custom-printing service](https://www.carousell.com.my/p/custom-photobook-161479041/).
The candidate `/photobook/q/` search could not be opened by the research tool.
Use the visible search form with `{person} photobook`, an exact title or ISBN,
then retain its actual URL. Broad “photobook” is noisy.

Use physical discovery. Candidate detail pattern `/p/{slug}-{listing_id}/`;
confirm the ID against the page before normalizing. Follow visible pagination
or load-more controls and deduplicate IDs after each load. Reject services
asking the buyer to upload their own photographs. Capture book condition,
seller location, delivery/meetup, included contents and listing-local stock/sold
evidence. Keep RM amount in MYR; sold counts or seller reviews are unrelated.
Authorized digital book coverage is unverified.

### Shopee Malaysia — `shopee-my`

**Observed search:** [photobook keyword results](https://shopee.com.my/search?keyword=photobook).
The page includes printing products and vouchers. A
[specific product URL](https://shopee.com.my/Stray-Kids-Photobook-Kpop-Album-80pages-ATE-ROCK-STAR-i.67848659.1313959815)
establishes the shop/item link pattern, not publisher authenticity.

Use `https://shopee.com.my/search?keyword={encoded_query}` and title/person
queries. Reuse Taiwan's shop/item identity logic. Applying its zero-based page
rule to Malaysia is a hypothesis until two distinct pages are observed.
Reject printing credit, e-vouchers, photo prints and empty albums; “digital
delivery” of a voucher does not make it a digital photobook.

Inspect each selected variant and shipping/stock state. MYR 39.90 is 3990 minor
units. Require a standalone book or a reviewed book-containing bundle.
Use the same blocked-page behavior as the Taiwan adapter.

### Lazada Malaysia — `lazada-my`

**Observed:** [Photobook Malaysia voucher category](https://pages.lazada.com.my/shop-home-digital-vouchers/photobook-my/)
and [printing search landing page](https://www.lazada.com.my/tag/photo-book-printing/).
These establish important exclusions, not authorized digital editions.
The candidate `https://www.lazada.com.my/catalog/?q={encoded_query}` returned no
usable page in research; capture the live search form and result links first.

Search an exact title/person rather than the brand “Photobook Malaysia”.
Candidate detail pattern `/products/{slug}-i{item_id}-s{sku_id}.html`;
confirm actual links and preserve selected SKU separately from item identity.
Follow observed Next controls; do not invent private pagination parameters.
Reject vouchers and printing services, distinguish album bundles from real book
copies, and extract MYR price/variant, seller and stock evidence.
Digital photobook coverage remains unverified.

### Mudah.my — `mudah-my`

**Observed:** [Mudah.my](https://www.mudah.my/) describes itself as a Malaysian
recommerce marketplace for new and used items and lists
Music/Movies/Books/Magazines plus Hobby & Collectibles categories. It is a
useful additional active-inventory source for local copies of photography
books. It is classified-ad style rather than a public auction-history source,
so do not add a sold-discovery job until a public sold-state/detail route is
verified. The source is now seeded as `mudah-my`; the adapter uses the observed
`/malaysia/all?q={query}` active route and extracts the numeric ID from
`/{slug}-{ad_id}.htm`. It remains disabled pending browser/access review. Do
not create a sold-discovery job: no verified public sold-history route was
found.

### Malaysia publisher/creator stores

No specific local publisher digital-photobook adapter was verified in this
research. Add stores individually using their real catalog/search form, product
identity and publisher provenance. The fact that a store ships to Malaysia is
not evidence that a work originated there. Do not create a generic “MY digital”
feed from marketplace voucher searches.

## Global — eBay (`ebay`)

**Observed:** [store photobook results](https://www.ebay.com/str/goodsstore07/Photo-Book/_i.html?store_cat=30563592018)
contain books, CD bundles and digital-code bundles. **Reference search:**
`https://www.ebay.com/sch/i.html?_nkw={encoded_query}`. Use book-related filters
selected in the current UI plus exact title/ISBN; a seller-defined store category
does not guarantee the product is a standalone book.

**Reference pagination:** `_pgn=1`, `_pgn=2`, `_ipg={page_size}`.
Reference sold discovery adds `LH_Complete=1&LH_Sold=1`; verify visible sold
evidence before accepting price history. Detail URLs may be `/itm/{id}` or
`/itm/{slug}/{id}`. Extract the actual numeric item ID and preserve variation
selection when relevant; do not use the slug as identity.

Read selected format, condition, shipping, item location, asking/current bid
and confirmed sale price separately. `Digital code + book` is a bundle, not
necessarily an e-book. Digital-only discovery needs verified publisher/seller
provenance. Preserve the page's explicit currency; `$` alone is ambiguous.

## Reference behavior to carry into `scraper/`

| Reference function / behavior | Required adaptation |
| --- | --- |
| `main`, UTF-8 streams, `redirect_stdout` | One JSON request on stdin, diagnostics on stderr, one batch JSON on stdout. Keep regional entrypoints thin. |
| `build_search_url` | Source-specific consumer routes, separate physical/digital jobs, query aliases; use the evidence levels above. |
| `with_marketplace_page`, `with_yahoo_page` | Source-specific cursor/page rules. Never append a universal `page` parameter. |
| `is_marketplace_result_url` | Filter product links before opening details. Otherwise navigation/recommendation links consume the detail budget. |
| `stream_active_query_pages` | Detect repeated product-ID fingerprints and no new IDs; checkpoint each completed page. |
| Render readiness and challenge checks | Wait for product cards or a verified empty state; distinguish blocked, parse failure and true empty. |
| Active/detail/completed collectors | Require item-local evidence. An active discovery job does not prove every item is active. |
| `catalog_worker` operation separation | Keep edition discovery and listing refresh separate; do not import trading-card checklists or watermark tools. |

The reference also contains Korea and proxy adapters. Their presence is not
proof of current photobook support. Korea and additional proxy marketplaces are
outside the JP/TW/CN/MY implementation scope of this document; do a separate
coverage/route validation before adding them.

### Record contract

The reference's raw names map to MuseBooks as follows. Do not send old card
records directly to the photobook ingest endpoint.

| Reference record | MuseBooks observation | Rule |
| --- | --- | --- |
| `externalListingId` | `externalId` | Source item identity, never ISBN or a shared path segment |
| `originalUrl` | `url` | Actual marketplace product URL |
| `retrievalUrl`, `dataProviderCode` | Adapter diagnostics/provenance | Preserve separately if a retrieval intermediary is ever used |
| `originalPriceAmount`, `originalCurrencyCode` | `priceMinor`, `currency` | Decimal conversion: JPY ×1; TWD/CNY/MYR/USD ×100 |
| `saleType`, `statusEvidence` | `status`, `statusEvidence` | Map to supported lifecycle values based on evidence |
| `sourceCapturedAt` | `observedAt` | UTC collection time, not release or sale time |
| `soldAt` / `endedAt` | `sourceTimestamp` + precision | Only when explicit; retain the event meaning |
| `imageReferences` | `imageUrl` | A usable cover URL, not a stringified image array |
| Card relevance/model fields | `format`, edition matching | Replace with publication/format evidence |

Use `jobId`, `workerId`, `leaseToken`, `sourceId`, `parserVersion`, `retrievedAt`,
`items`, `warnings`, `diagnostics`, `nextCursor` and `hasMore` in the batch.
The existing API does not yet ingest ISBN/publisher/page-count candidate fields;
edition enrichment needs a deliberate schema/contract extension. Do not silently
pretend those fields were saved by the current batch endpoint.

## Implemented worker behavior and remaining live validation

The production implementation in this folder now covers the engineering gaps
identified during research:

1. **Marketplace dispatch:** `marketplace_adapters.py` resolves the stable
   source ID/adapter name and supplies source-specific consumer search routes,
   detail-link predicates, pagination parameters, and external-ID extraction.
2. **Pagination:** the worker honors `pageCursor`, exact `pageUrls`, and the
   reference rules for Yahoo Auctions, eBay, Mercari, Ruten, Shopee, JD and
   Lazada. It checks rendered Next controls, compares product-link fingerprints,
   resumes a partially inspected result page when the detail budget is reached,
   returns `nextCursor`, and the API runner requeues a successful page when
   `hasMore` is true. Successful page checkpoints reset the per-page retry
   counter, so `maxAttempts` still limits failures without truncating a long
   crawl.
3. **Formats and relevance:** digital/physical inference is product-local,
   bonus postcards are allowed only when attached to a photobook, and empty
   albums, card-only goods, printing services, vouchers and unrelated merch are
   rejected. Ambiguous album/artbook labels need stronger human-model evidence.
4. **Price and identity:** structured product prices win over page text and are
   parsed with `Decimal`; non-finite values are ignored. Marketplace-specific
   IDs are required, including query IDs for Taobao/Tmall and `itemCode`-style
   IDs for Mandarake where present. ISBN is not used as offer identity.
5. **Lifecycle and provenance:** active/ended/completed/unknown states require
   visible evidence, and an active auction is not reported as a hammer price.
   Digital access is authorized only for configured first-party/e-book sources;
   arbitrary “official” seller text is not sufficient.
6. **Runtime and source safety:** the worker enforces the source rate budget for
   search/detail navigations, treats challenge pages as blocked, rejects
   out-of-scope redirects, and records detail failures instead of silently
   accepting an unverified partial detail record.

These changes make the adapter contract executable, but they do not constitute
live validation for every marketplace. Before enabling a source, capture the
current rendered URL/filters, at least two result pages, three detail pages, a
challenge page, and the failure cases in the validation sequence below. The
seed's review/disabled status is intentional and must not be treated as proof
that a source is reachable or permitted.

## Validation sequence for each adapter

1. Capture one actual query/form result URL, current category/format selection,
   two pages or load-more windows, and at least three product details.
2. Preserve a minimal rendered fixture with product-local title, price, format,
   identity and availability evidence. Avoid freezing prices as current facts.
3. Include real failure cases: bonus-only item, book with bonus, empty album,
   printing voucher, ambiguous digital code, wrong variant, missing price,
   challenge, and changed/deleted product.
4. Verify page two produces new source IDs; repeated content stops with a
   reason. Restart after a committed page and confirm the checkpoint resumes.
5. Verify one normalized batch against the MuseBooks API, including duplicate
   retry, lease ownership and maximum 500 observations per batch. Larger
   crawls must split batches; current max-pages × candidates can exceed that cap.
6. Record browser/adapter version, tested date, source hosts, observed pagination
   and known limitations alongside the fixture. Only then label the adapter
   live-validated. A blocked source can still have tested fixture parsing.

For the user's resale-price objective, the recommended implementation order is
eBay and Yahoo Auctions first; then Mercari/Rakuma/Yahoo Flea after access
review; then Taiwan Yahoo拍賣, Ruten and Shopee; then Kongfz/Xianyu and
Carousell/Mudah. Keep Rakuten Books and BOOK☆WALKER as edition/digital
reference sources, not the primary resale-price feed. This order is an
engineering judgment based on the cited marketplace evidence, not a guarantee
of access or complete regional coverage.
