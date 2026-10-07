# Taiwan digital photobook distribution — inspected 2026-10-06

Digital editions are distributed by multiple authorized stores. Prices below
are retail offers observed through the actual Taiwan book worker, not prices
paid in completed transactions. Promotions can change.

| Model / edition | Store | Public item | Observed TWD price | Edition note |
| --- | --- | --- | ---: | --- |
| 吳元元 / 元來有你 | BOOK☆WALKER | https://www.bookwalker.com.tw/product/39045 | 218 | 含影音; ISBN 9789571094663 |
| 吳元元 / 元來有你 | Kobo Taiwan | https://www.kobo.com/tw/zh/ebook/Fst-eku40jCuuvydW8wGaQ | 276 | 含影音; 尖端出版 |
| 林襄 / 襄水II | BOOK☆WALKER | https://www.bookwalker.com.tw/product/238917 | 292 | Video inclusion unspecified |
| 林襄 / 襄水II | Kobo Taiwan | https://www.kobo.com/tw/zh/ebook/ii-mizuki | 369 | Video inclusion unspecified |
| 張雅涵 / 涵氧女孩 | BOOK☆WALKER | https://www.bookwalker.com.tw/product/160120 | 312 | Video inclusion unspecified |
| 張雅涵 / 涵氧女孩 | Readmoo | https://readmoo.com/book/210267280000101 | 395 | Explicit 無影片 |
| 張雅涵 / 涵氧女孩 | Kobo Taiwan | https://www.kobo.com/tw/zh/ebook/wlOqRz7qzzKU_ymKeFTsCQ | 395 | Video inclusion unspecified |
| 瑟七 / 微澀．微瑟 | Pubu | https://www.pubu.com.tw/ebook/690306 | 350 | 含影音; ISBN 9786264555029 |

The repeated names/titles establish overlapping distribution, not guaranteed
identical content. Publisher/distributor labels differ across some stores;
with-video, without-video and unspecified versions must remain distinct until
verified. Each store's listing is stored separately by source and external ID.
Curated edition links are retained on subsequent imports; no automatic merge
based on similar titles was introduced. Kobo's Book ID is not treated as ISBN.

## Code changes

- Re-enabled Taiwan BOOK☆WALKER and Readmoo for digital catalog/current-price
  collection. Added Pubu and Kobo Taiwan browser adapters and source seeds.
- Digital retail jobs accept catalog_discovery, active_discovery and
  listing_detail only. Physical retail jobs and digital sold jobs are rejected
  by both the worker and backend enqueue/lease policy. Imported completed-sale
  observations from digital retailers are rejected.
- Read selected native offer panels, avoiding coupon reductions, recommendation
  prices and incorrect unavailability from EPUB download restrictions.
- Extract authors for model searches whose titles omit names, e.g. 涵氧女孩;
  verify requested model names on selected details before accepting offers.
- Normalize Pubu/Kobo tracking URLs; reject foreign Kobo store URLs and Pubu
  media/non-book routes. Preserve editionVariant, ISBN and publisher fields in
  imported listings where available.
- Store availability uses selected purchase controls/schema. `priceType=digital`
  denotes the current retail offer, never a completed-sale price.

Pubu hides some sensitive search results from anonymous visitors. Its public
瑟七 page was verified; the 元來有你 search did not expose a qualifying public
item link, and no observation was invented. HyRead presented Cloudflare
verification and remains skipped. Physical retail stores and Japan retail
sources remain excluded.

## Expanded platform coverage

The following additional storefronts were implemented and checked with the
actual Taiwan photobook worker on 2026-10-06:

| Store / source ID | Verified digital item | Observed price | Capability / status |
| --- | --- | ---: | --- |
| Hami / `hami-tw` | [元元 吳婕安寫真書數位版](https://www.hamibook.com.tw/book/0100345610) | TWD 254 | Active price; model keyword discovery verified |
| Google Play / `google-play-books-tw` | [與你襄遇（含影音）](https://play.google.com/store/books/details?id=NoArEAAAQBAJ&hl=zh_TW&gl=TW) | TWD 203 | Active price; model keyword discovery verified |
| momoBOOK / `momo-books-tw` | [與你襄遇（含影音）](https://www.momoshop.com.tw/product/12583611) | TWD 263 | Active price; model keyword discovery verified |
| PChome / `pchome-books-tw` | [HyRead 涵氧女孩](https://24h.pchome.com.tw/books/prod/DJBR5E-D900IO5U9) | TWD 395 | Active price; model keyword discovery also found the Readmoo 無影片 offer |
| Yahoo Shopping / `yahoo-shopping-books-tw` | [元來有你 Readmoo 電子書](https://tw.buy.yahoo.com/gdsale/元來有你-Sandy-吳元元寫真書-Readmoo-11285372.html) | TWD 221 | Active price; model keyword discovery verified; separate from Yahoo Auctions |
| 金石堂 / `kingstone-books-tw` | [襄水II](https://www.kingstone.com.tw/basic/2800000212957/) | TWD 369 | Active price; keyword discovery also returned 與你襄遇 at TWD 299 |
| 博客來 / `books-com-tw` | [與你襄遇（含影音）](https://www.books.com.tw/products/E050091990) | TWD 299 | Active detail verified in this run; source re-enabled for ebooks only |
| TAAZE / `taaze-books-tw` | [涵氧女孩（不含影片）](https://m.taaze.tw/do/mobile/single.aspx?pid=14100093289) | TWD 395 | Catalog/detail price verified; availability unknown, no active capability |
| Apple Books US / `apple-books-us` | [雅涵Kimi 個人寫真書](https://books.apple.com/us/book/id6760949828) | USD 26.99 | Catalog/detail price verified; availability unknown, no active capability |

Hami keyword discovery also returned 元來有你 at TWD 235. momo keyword
discovery returned 襄水II at TWD 324. Prices reflect current single-item offers;
coupon prices and multi-item checkout discounts are not substituted.

Apple's Taiwan storefront adapter (`apple-books-tw`) is implemented but disabled:
the inspected title did not expose a Taiwan offer. Its US offer is stored under
an independent source in USD, never relabelled as TWD. HyRead (`hyread-tw`) also
has an exact-detail adapter but remains disabled because of verification.

The old udn storefront now redirects to its
[Readmoo integration announcement](https://reading.udn.com/act/notice/).
It is covered through Readmoo rather than a scraper for retired udn product URLs.
MyBook is now distributed as momoBOOK; see its
[official app listing](https://apps.apple.com/us/app/momobook/id406123921).
No duplicate legacy storefront was enabled.

TAAZE, Apple and HyRead require an exact public ebook URL or an operator-supplied
verified search URL; their default search routes are not guessed. Mixed retailers
require selected title/schema ebook evidence, independent of ebook navigation
or recommendations elsewhere on the page. Google URLs preserve the Taiwan store
selection. Redirects to another book/store region and foreign currencies are
rejected. Missing image attributes no longer cause default browser lookup waits.

Coverage means the identified public platforms and verified examples above;
it does not imply every Taiwanese model or edition is available on every store.

## Running

Restart the backend to apply migrations, source seeds and new request policy.
The worker reads the updated Python code on subsequent runs. No live database
was changed or browser observations imported during this inspection.

`taiwan_digital_targets.json` contains 35 ready-to-enqueue starter requests:
three model names across eleven Taiwan stores, plus exact catalog-detail requests
for 張雅涵 on TAAZE and Apple US. Alias names and digital format are supplied.
They are request templates, not scheduled jobs.

75 scraper tests and the full backend `go test ./...` suite pass. Actual live runs
verified direct details and keyword discovery on the stores above. A positive
Pubu public-detail check passed after fixing availability detection. Public
search results can be incomplete due to store visibility restrictions.
Kobo keyword discovery for 張雅涵 also returned 涵氧女孩 at TWD 395 after
selecting the native synopsis and author metadata for relevance checks.
