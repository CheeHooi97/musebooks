# Korean Model Photobooks and MAXIM Issue Sources

Research snapshot: 2026-10-25 (Asia/Singapore). Direct browser rechecks of YES24 pages for BE JOYFUL, 김설화 26, MAXIM B-SIDE #5, MAXIM October 2026 digital, and MAXIM October 2026 print B took place on 2026-10-20 around 11:40–11:45 SGT. The MAXIM January 2026 digital issue was reviewed through the public page reader around 11:53 SGT; that page result reported its source crawl was two days earlier, so it is retained as a stale price/status snapshot pending a live recheck. The MAXIM September 2024 digital issue was reviewed around 11:59 SGT; its page reader reported a crawl from that day. Live YES24 browser checks around 12:06 SGT added MAXIM August 2025 digital and the MAXIM B-cut Party Look pictorial. Checks around 12:12 SGT added MAXIM February 2024 digital and the SANTORINI photobook. Public YES24 page snapshots for Jennie [Solo] Photobook and its Special Edition were reviewed around 12:37–12:41 SGT; both had last-month crawl markers, so price and status are retained as stale observations. The November 2025 MAXIM digital page was checked around 12:45 SGT; its crawl marker was two weeks old. The October 2025 Aladin A/B and S-type list was reviewed at 16:51 SGT, then committed and verified before collection continued. The September 2025 Aladin A/B/S print list was reviewed at 16:56 SGT, then committed and verified before the YES24 digital list. The September 2025 YES24 PDF page was reviewed at 17:00 SGT; its snapshot was crawled last month, so price is last-observed and current availability is unknown. That one-item list was committed and verified before collection continued. These are page observations; an aggregate used-stock count is not a seller-specific offer.

On 2026-10-23 around 21:19 SGT, Aladin's public search-result snapshots for the July 2024 A/B print variants were reviewed. The product-page snapshots carry crawl markers from five to seven months earlier; their list/sale prices are last-observed and current availability is unknown. Exact used-list routes returned cache misses. The two physical editions and retail price observations were added to the manifest, committed to PostgreSQL, and verified before research resumed.

The August 2025 Aladin A/B print list was reviewed at 17:06 SGT, then committed and verified before researching another source. It added two physical editions and seven listing observations.

The July 2025 Aladin A/B print list was reviewed at 17:17 SGT. It added two physical editions and four listing observations: two new-copy prices and two A-type used offers. The stale retail snapshots leave current availability unknown. The batch passed manifest validation, was committed to PostgreSQL, and was verified before the next source list. Aladin's used-series page showed two B-type offers at an aggregate floor of KRW 17,000, without seller-specific details; this is recorded as source context, not as an individual offer.

The June 2025 Aladin A/B print list was reviewed at 17:24 SGT. It added two physical editions and three listing observations: two new-copy prices and one A-type seller inventory row. Aladin's A product page showed one used offer at KRW 13,000, and a seller inventory panel identified kirinji at the same price; no individual offer ID, condition, or seller-item page was exposed. That row is stored with a deterministic source-row key and unknown current status. The batch passed manifest validation, was committed to PostgreSQL, and was verified before the next source list.

The May 2025 Aladin list was reviewed at 17:32 SGT. It added the A print edition and a subscription S-type edition, with seven listing observations: the A new-copy price, five A seller rows, and one completed S-type seller offer. The A seller list is an older snapshot, while a newer product-page snapshot shows an aggregate used floor of KRW 10,000. Seller-row availability is unknown. The S-type listing title identifies May 2025 but its publisher date field says 2024-01-01; the manifest uses the matching A issue's 2025-04-23 date and records that conflict. The batch passed validation, was committed to PostgreSQL, and was verified before the next source list.

The January 2025 Aladin A/B/C print list was reviewed at 17:38 SGT. It added three physical editions and four listing observations: three new-copy prices and one A-type used seller row. Aladin lists 2024-12-23 publication, 192 pages, A4 dimensions, 518g, and last-observed list/sale prices KRW 8,900 / 8,450 for all three types. The snapshots are stale; current new-copy availability is stored as unknown. A seller-inventory snapshot listed kirinji, condition 상, at KRW 20,000 for the A type, with parcel KRW 3,500 or half-price parcel KRW 2,400; current offer availability is unknown. A separate aggregate used-price floor of KRW 19,000 is kept as page context, not an individual offer. Xports identifies 갓세희 as the January cover model. The batch passed manifest validation, was committed to PostgreSQL, and was verified before collection continued. Image reuse permission remains unconfirmed, so cover and gallery image fields stay blank.

The December 2024 Aladin list was reviewed at 17:44 SGT. It added A- and B-type print editions and three listing observations: two new-copy prices and one completed A-type used offer. Both editions are 192-page A4 issues with last-observed list/sale prices KRW 8,900 / 8,450; their Aladin publication dates are 2024-11-01 (A) and 2024-11-21 (B). Current retail availability is unknown. The completed used A-type item was seller 책방 2034, condition 중, KRW 20,000, with parcel shipping KRW 3,500 and half-price parcel KRW 2,400. A contemporaneous report identifies 쥬 as the December cover model. Aladin's C-type series entry points to item 352714443, but its product route returned a cache miss; a reseller identifies that separate C cover as Donald Trump, so it is not staged as a Korean-model cover variant. The A/B batch passed validation, was committed to PostgreSQL, and was verified before collection continued.

The November 2024 Aladin list was reviewed at 17:49 SGT. It added one A-type physical edition and seven listing observations: one new-copy price and six used seller rows. The Aladin product title omits its A/B suffix, but its serial code 9772233427008 and an exact A-type row in the linked seller inventory support recording it as A; no B-type product was verified. The item is 192 pages, A4, 518g, published 2024-10-02, with last-observed list/sale prices KRW 8,900 / 8,450. The six used rows list prices KRW 7,000, 7,000, 10,000, 10,000, 12,000, and 13,000; all are stored with unknown current availability because the inventory snapshot is about four months old. A contemporaneous report identifies 뽀구미 as the November cover model. The batch passed validation, was committed to PostgreSQL, and was verified before collection continued.

The January 2026 MAXIM print listing and Aladin used-inventory page were reviewed around 16:13 SGT. The retail and seller inventory snapshots were crawled about two weeks and two months earlier, respectively. The new-copy page marks the issue sold out; all four listing statuses are stored as unknown and their prices as last-observed. The three exact used item IDs were captured from the seller rows; opening those item routes returned cache misses. The product page exposes a cover image and one gallery image URL, but both image routes returned cache misses and reuse permission is unconfirmed.

Later page-reader checks on 2026-10-20 added the MAXIM July 2024 digital issue around 12:50 SGT and August 2024 digital issue around 12:56 SGT. The July page snapshot was two months old; the August page snapshot was crawled last week. Their prices are last-observed values and availability is unknown. A further check around 13:01 SGT added the June 2024 issue; its page snapshot was five months old, so availability is unknown.

A further page-reader check around 14:42 SGT on 2026-10-20 reviewed the exact YES24 October 2026 print A and B product pages. Both show publication date 2026-09-24, 176 pages, list KRW 9,600, sale KRW 9,120, and current limited-sale purchase controls. The A-type physical edition is staged under the existing October issue. The B-type is documented as a verified product but not staged because its exact cover-model credit is not established; the listed bromide models are not treated as cover credits. The page links expose cover and detail-image URLs, but reuse permission is unconfirmed and the detail-image assets returned cache misses.

The MAXIM publisher-shop discovery page and YES24 magazine-category listings were reviewed around 14:53 SGT. Eleven April–May 2026 model-specific B-cut PDF listings were added from title/model credits, month-level publication dates, and regular list/selling prices. The category snapshots are approximately one to two months old; exact product pages either cache-missed or redirected to an adult check, so the staged availability is unknown and the prices are last-observed.

Around 15:00 SGT, the publisher-shop listing and YES24 magazine-category pages yielded eight more June–July 2026 B-cut PDFs. Each listing names the model and gives a regular price; the category results provide month and show cart/purchase controls. Their detailed product routes cache-missed or redirected to an adult check, so availability remains unknown and prices are last-observed.
## Purpose and collection method

Use public product and publisher pages to find Korean model photobooks and MAXIM magazine issues for MuseBooks. Collection in this project is page-based: read the rendered product page, record its URL and the time checked, and keep the captured facts tied to that source. No third-party API, API key, feed, or API-backed search integration is used.

The evidence below supports manual, low-volume page checks. No source in this pass was verified as approving a scheduled or bulk scraper or reuse of its product images. YES24's robots file does not disallow the direct product-detail route used here, but it explicitly disallows multiple used-shop routes; the terms reviewed do not expressly authorize automated extraction or image reuse. Aladin's terms prohibit commercial use or onward provision of information obtained from the site without prior consent. Kyobo's robots file allows public paths other than its API path, but its terms text did not render in this review, so permission for automated extraction and image reuse remains unknown. MAXIM's official terms page includes a website-terms clause (§13(3)) stating that information obtained through its service may not be used commercially or made available to a third party without the company's prior approval; the terms also restrict sales or advertising use of the service without approval. This describes MAXIM-site terms, not a permission grant for MuseBooks. YES24 page observations remain subject to YES24's separate terms. Keep this collection manual and do not mirror images until the relevant source grants permission.

## Where to look

| Source | Use | Current access and evidence |
| --- | --- | --- |
| [YES24 product details](https://www.yes24.com/) | Exact title, publisher, publication date, list price, displayed sale price, stock label, format, ISBN/ISSN, and an explicit cover-model credit when the detail page provides one. Search model name plus 사진집, 화보집, 포토북, or MAXIM, then open the exact product page. | Direct product pages such as /product/goods/197225466 were manually readable. The [robots file](https://www.yes24.com/robots.txt) does not disallow this direct route, but it disallows UsedShopHub and /24/UsedShop routes. The [service terms](https://www.yes24.com/notice/service.aspx) do not clearly grant automated scraping or commercial reuse of images. Manual checks only until that use is clarified. |
| [YES24 MAXIM partner shop](https://www.yes24.com/Product/PartnerShop/284442) | Discover MAXIM monthly variants and special issues; follow each candidate to its exact product page before recording facts. | Search and partner-shop pages are discovery aids. A result title or related-books carousel is not enough to establish model, date, current stock, or cover credit. |
| [Aladin](https://www.aladin.co.kr/) | Cross-check exact book metadata and inspect individual second-hand listings, including seller, condition, asking price, and availability. | The exact [BE JOYFUL product page](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=77364450) confirms title, authors, publisher, 2016-02-17 date, ISBN, and displayed KRW 19,800 price against KRW 22,000 list; it is marked out of stock. It shows 12 used items, but this pass did not open a seller-specific page. Aladin's [e-book catalog](https://www.aladin.co.kr/m/mbest.aspx?BestType=EBookBestseller&BranchType=9&CID=38820&InKids=0) lists Secret B Vol. 5 Park Eunhye as a PDF from 2020-09 and Vol. 10 Shin Saerom as a PDF from 2022-03; these category captures were used only for bibliographic month/format metadata, not as current price observations. The [Aladin terms](https://www.aladin.co.kr/account/waccount_provision.aspx?pType=1) prohibit commercial use or onward provision of information obtained from the site without prior consent. The robots file could not be reviewed; no automated collection or image reuse. |
| [MAXQ newsroom](https://maxq.kr/) and [Spomax official store](https://spomax.kr/) | Discover the Secret B photobook line and check publisher subject credits, issue format, scheduled print dates, displayed product prices, and store controls. | MAXQ's [Secret B No. 1 article](https://maxq.kr/articles/sikeurit-b-ryusebibakeunhye-hwabojip-yeyakpanmae-opeun) confirms the two subjects and explains that print followed earlier digital releases. Spomax product pages can show an exact item ID and current order controls; this pass manually checked product 5041. Image reuse permission was not established, so these pages are metadata sources only and covers are not mirrored. |
| [RIDI Books](https://ridibooks.com/) | Verify authorized Korean digital photobook editions, including exact product title, release date, file format, page count, and current rental/purchase prices. | The [Secret B + MAXQ Vol. 03 page](https://ridibooks.com/books/3563000148) identifies a 67-page PDF e-book dated 2022-09-23. RIDI's related-series navigation links [Secret B 5호-박은혜](https://ridibooks.com/books/3563000061); Aladin's e-book catalog lists it as a MAXQ International PDF from 2020-09, so its release is stored at month precision and its page count remains unknown. The [Secret B No. 9 page](https://ridibooks.com/books/3563000107) identifies *Secret B 9호-윤나겸* as a 42-page PDF e-book dated 2021-09-28, published by MAXQ International. RIDI's related-series navigation links [Secret B 10호-신새롬](https://ridibooks.com/books/3563000126); Aladin's catalog lists the title as a MAXQ International PDF from 2022-03. The [Secret B No. 16 page](https://ridibooks.com/books/3563000203) identifies a 114-page PDF e-book dated 2024-08-01, published by MAXQ International; its page requires adult verification. Retailer access does not grant permission to copy an e-book or cover image into R2. |
| [ThePower and GlobalEpic launch coverage](https://www.thepowernews.co.kr/) | Verify creator identity, title, announcement date, and scheduled release for creator-led photobooks; use the exact linked product page or cross-checked listing for edition facts. | For 정현's *Young & Beautiful*, contemporary coverage announces an Interpark preorder and 2022-11-30 release. A Bunjang Global resale listing corroborates sealed physical copies and variants but is not a current publisher/retailer record. Press and marketplace access do not grant cover-image reuse permission; no image was mirrored. |
| [Kyobo](https://product.kyobobook.co.kr/) and [Kyobo eBook](https://ebook-product.kyobobook.co.kr/) | Cross-check exact print or authorized digital editions, release dates, and current listed prices. Keep print and eBook releases separate. | The exact [Kyobo BE JOYFUL page](https://product.kyobobook.co.kr/detail/S000001609752) corroborates the title, model/photographer, date, ISBN, page count, and displayed KRW 19,800 price against KRW 22,000 list; it is marked out of stock. Kyobo's [robots file](https://www.kyobobook.co.kr/robots.txt) allows public paths except its API path; the terms text did not render in this review, so no automated collection or image reuse until that is clarified. |
| [National Library of Korea catalogue](https://www.nl.go.kr/) | Search by exact Korean title or ISBN to corroborate bibliographic identity and publication details. | Use the public catalogue page only; no API is part of this workflow. A catalogue cover image still needs separate reuse clearance. Coverage of MAXIM and small-press photobooks is unknown. |
| [MAXIM Korea](https://www.maximkorea.net/) | Discover publisher announcements, MAXIM B-SIDE issues, named cover models, and release dates. | The [current website terms](https://www.maximkorea.net/members/members_law.php) restrict commercial use or third-party provision of service information without prior approval. An official [MAXIM article](https://www.maximkorea.net/cms/contents_view.php?gocate=&number=12370) also carries an unauthorized-reproduction notice. Use MAXIM pages for discovery/corroboration only until written permission covers the intended use; do not copy paid previews or gallery images. |
| [Cupick Korean Models](https://cupick.jp/en/products/jinny-late-summer) | Discover digital photobooks tagged for Korean models; individual pages show title, displayed price, page count, and image links. | The [terms](https://cupick.jp/en/policies/terms-of-service) prohibit automation tools and copying company content beyond personal use. Use as a discovery lead only; do not scrape or reuse product/gallery images for MuseBooks without written permission. |
| [MAXIM publisher archive](https://www.maximkorea.net/magdb/magdb.php?lib=M) | Public publisher cards and exact `magdb_view.php?lib=M&number=...` detail pages provide cover credits, publication dates, ordinary print prices, cover images and public preview panels. | Open the visible cover image in the archive card to reach its actual detail route. Read rendered DOM only; no API/key. The October A/B detail pages are publicly readable without login. Capture exact image `src` values and resolve relative URLs against the page; omit event banners and keep subscriber S artwork separate. Manual source `maxim-korea-manual` stays disabled/review; no reuse license is asserted. |
| [KADOKAWA bibliography](https://www.kadokawa.co.jp/product/322303002121/) | Identify exact print/digital products, release dates, publisher covers and outbound store links. The separate Rondo and Enbukyoku digital pages establish distinct product identities. | Public rendered pages checked manually; print ISBN, dimensions and prices are not copied to digital editions. Cover URLs retain publisher provenance; no reuse license is asserted. |
| [Apple Books Japan](https://books.apple.com/jp/book/id6453688939) | Follow publisher links to exact public storefront pages for displayed ebook prices, digital page counts and file sizes. | Rondo and Enbukyoku public prices were captured on 2026-10-23. Public preview pricing does not establish account/storefront purchase eligibility. Manual source `apple-books-jp-manual` stays disabled/review; [site terms](https://www.apple.com/jp/legal/terms/site.html) are recorded without asserting automation or image permission. |
| Search engines | Generate candidate Korean titles and aliases, then locate the publisher or retailer page. | Discovery only. Search snippets do not establish current price, availability, publication date, or a credited cover model. |


## Permission status and inquiry routes

No exact image in the captured corpus has confirmed reuse approval, and no source has granted MuseBooks blanket automated page extraction permission. Hanmoto offers a conditional asset-level reuse route for books explicitly marked 利用可; Candid is marked permission unknown, as recorded below. A robots.txt allowance for a product-detail path only answers crawler access rules; it does not grant reuse rights. Do not mark a source approved until written permission specifies the allowed pages, collection frequency, fields, attribution, image use, and any storage or hotlink conditions.

| Rights holder / contact route | Verified source | What to ask; current status |
| --- | --- | --- |
| YES24 | The [YES24 customer-center notice](https://www.yes24.com/Mall/Help/Notice) lists `bookinfo@yes24.com` for book/author product inquiries. | Ask whether low-volume page-based metadata collection is permitted and request the rightsholder contact for product covers and detail images. This is a contact route only; no permission has been granted and YES24 may not own the images. |
| MAXIM Korea / 와이미디어 | The official [MAXIM Korea 2025 media kit](https://www.maximkorea.net/board/file/bbs_sm/35/1737531188_1.pdf) lists `ckt@maximkorea.net` for its external-affairs team and a sponsor-use option for shoot materials. MAXIM’s [FAQ](https://www.maximkorea.net/board/board_view.php?board_cate1=&code=bbs_faq&key=&keyfield=&number=82&page=1&sort=) routes business-partnership inquiries to `partner@maximkorea.net`. | Request written MuseBooks-specific permission for page collection and named cover/sample images. The media kit is a partnership route, not a blanket cover-image license. No inquiry has been sent. |
| Standalone photobook publishers / image creators | The captured product pages identify 페이퍼북 and photographer 신혜림 for BE JOYFUL, 아이다호 / 로글(rogle) for 김설화 26, 진한엠앤비 for Password, Password 4 and Password 5, and 북엠 for The Briller. No current official rights contact was verified for these titles. | Ask YES24 for a current publisher/rightsholder contact, then seek permission from the publisher and any separate photographer, model, or agency rightsholder. No image is cleared until the responsible party confirms rights in writing. |
| Korea Open Government License (KOGL) | The [Korea Copyright Commission's KOGL guide](https://www.copyright.or.kr/gov/nuri/rule_info/index.do) describes asset-level public-work licenses, including whether commercial use and modification are allowed. | This can provide permitted supplementary photographs only when the exact asset carries a compatible KOGL mark and its conditions are followed. It does not license commercial photobook covers or MAXIM imagery by default. |

When requesting approval, specify the actual MuseBooks use (catalog display), whether the collection is manual or automated, the expected request interval, direct source pages, fields captured, attribution, image resizing/storage/hotlinking, and takedown handling. No inquiry has been sent on the user's behalf.

### Draft permission request (not sent)

**Subject:** Permission request for Korean model photobook / MAXIM catalog capture and image display

MuseBooks is building a Korean model photobook and MAXIM issue catalog. May we capture factual metadata and retailer-displayed list/current/used prices from the public product-detail pages listed below, without APIs, login-only pages, DRM content, or disallowed used-shop routes? The proposed page rate is at most one request per minute. Please confirm which routes and fields are allowed and any rate, attribution, or retention conditions.

We also request permission to display each item's official cover and any publicly provided product-detail images in MuseBooks, with attribution and a source link. Please specify whether this permits hotlinking or local thumbnail storage, resizing/cropping, commercial or ad-supported display, and the permitted images/territory/term. Please identify any separate photographer, model, agency, or other rightsholder whose approval is required.

**Candidate pages:** Use the current product-detail URLs recorded in `docs/korean-maxim-issue-review.json` under `edition.metadataSourceUrl` and `batch.items[].url`. That manifest is the current review scope for standalone photobooks, MAXIM issues, and MAXIM B-cut pictorials. No request has been sent; this text is a draft for review.

## Verified page captures

### MAXIM October 2026 digital magazine issue

[YES24 product detail](https://www.yes24.com/product/goods/197225466)

| Field | Captured value |
| --- | --- |
| MuseBooks type | magazine_issue |
| Title | 맥심 MAXIM 2026. 10월호 |
| Issue month | 2026-10 |
| Cover-model credit | 미스맥심 쥬 (the product contents explicitly say 표지모델) |
| Publisher | 와이미디어(맥심) |
| Format | Digital PDF with DRM; it is delivered for reading in the YES24 eBook app and is not shipped |
| Release date | 2026-10-01 |
| Pages / identifier | About 182 pages; ISSN 22334270 |
| List price | KRW 5,500 |
| Displayed current selling price | KRW 5,500 |
| Coupon price | KRW 4,950 appeared in the 2026-10-19 capture; it was not verified during the 2026-10-20 recheck, so exclude it from today's current price |
| Availability | 판매중; page also offers purchase and immediate reading |
| Observed | 2026-10-20 around 11:44 SGT |
| Images | The cover asset is `https://image.yes24.com/goods/197225466/XL`. The page does not expose a verified additional product-gallery image. The initial capture retained only URL provenance. The October 23 refresh now links this public cover remotely with source attribution; no pixels are mirrored or reuse license asserted. |

This is a verified issue/cover credit, not a standalone photobook. A staged record is in [korean-maxim-issue-review.json](korean-maxim-issue-review.json). The initial capture left its cover empty. The October 23 refresh adds a remote digital cover; the retailer source remains disabled for automated collection.

### MAXIM January 2026 digital issue #272: 조예린

[YES24 product detail](https://www.yes24.com/product/goods/172104147) · [official MAXIM cover-model announcement](https://www.youtube.com/watch?v=08foa4rTtBE)

The official MAXIM Korea video title identifies issue 272, the January 2026 issue, and cheerleader 조예린 as its cover model. YES24 lists the digital PDF edition with publisher 와이미디어(맥심), release date 2026-01-02, about 165 pages, ISSN 22334270, and list/displayed selling price KRW 5,500. Its extracted page text showed 판매중, but the page reader marked the source as crawled two days before this review. Keep KRW 5,500 as the last observed selling price and availability as unverified until a live page check.

The YES24 cover asset resolves to `https://image.yes24.com/goods/172104147/XL`. The extra image links did not confirm another product-gallery image; one resolved to an unrelated promotional asset. Record the cover URL as provenance only. No image reuse permission was found, so the staged record leaves its cover and media fields blank. This is a digital magazine issue, not a photobook.

### MAXIM August 2025 digital issue: cheerleader 김진아

[YES24 product detail](https://www.yes24.com/product/goods/150381839)

The live YES24 page identifies the August 2025 PDF issue and its contents explicitly label `COVER — CHEER LEADER 김진아`. It lists publisher 와이미디어(맥심), publication date 2025-08-01, about 182 pages, and a 403.62MB DRM PDF. At the browser check around 12:06 SGT on 2026-10-20, the page showed `판매중`, list price KRW 5,500, selling price KRW 5,500, and a separate coupon-benefit price of KRW 4,950. The imported listing records the ordinary selling price; keep the coupon price as a separate page observation.

The product cover is visible on the detail page. No additional product-gallery image was confirmed. Image reuse permission is not established, so the manifest leaves the cover fields blank and does not copy the cover into MuseBooks. This is a dated monthly `magazine_issue` with an explicit cover-model credit.

### MAXIM February 2024 digital issue: 박민정

[YES24 product detail](https://www.yes24.com/product/goods/124866932)

The live YES24 page titles this the February 2024 MAXIM issue with 박민정, and the contents list a `COVER` section naming her. It shows publisher 와이미디어(맥심), release date 2024-02-02, a 64.11MB DRM PDF of about 186 pages, and list/selling price KRW 4,800. The live page check around 12:12 SGT on 2026-10-20 showed `판매중`; its separate coupon-benefit price was KRW 4,320. The reviewed observation records the ordinary selling price.

The product cover is visible on the page; no extra gallery image was confirmed. The cover is not cleared for reuse, so MuseBooks has no cover or media URL for this issue. Catalog it as a dated `magazine_issue` with 박민정 as the explicit cover model.

### MAXIM September 2024 digital issue: Miss Maxim 이연우

[YES24 product detail](https://www.yes24.com/product/goods/133188730) · [contemporaneous cover-model report](https://www.specialtimes.co.kr/news/articleView.html?idxno=401026)

YES24 classifies this as an eBook magazine and identifies Miss Maxim 이연우 under the issue title. Its contents explicitly label a `COVER` section featuring her; the separate report also says model 이연우 covers the September MAXIM issue. The digital PDF edition was released 2024-09-03, is about 186 pages and marked 19+, and showed list/selling price KRW 4,800 with status 판매중 in the page result read around 11:59 SGT on 2026-10-20. The page reader marked its source as crawled today. Treat KRW 4,800 as the active digital offer at that capture; no used offer applies to this digital edition.

The cover asset URL is `https://image.yes24.com/goods/133188730/XL`. The page's extra image links resolved to an unrelated promotional asset, so no additional product-gallery image was confirmed. Keep the direct cover URL as provenance only; image reuse permission is not established and the manifest leaves image fields blank. This record is a `magazine_issue`, not a photobook.

### Standalone model photobook: BE JOYFUL by 이성경

[YES24 print product detail](https://www.yes24.com/product/goods/24448036)

The page classifies this as a photo book and describes 이성경 as a model/actor whose four years of film photographs make up the book. It credits photographer 신혜림. This is a standalone physical photobook, not a MAXIM issue. The page gives publisher 페이퍼북, release date 2016-02-17, ISBN 9788997148615, 248 pages, 890g, and dimensions 200×240×16mm. It shows a list price of KRW 22,000 and displayed sale price of KRW 19,800, but the current page status is 품절, so neither is an active new-copy offer.

The [YG release announcement](https://www.ygfamily.com/ko/news/notice/3365), [Aladin detail page](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=77364450), and [Kyobo detail page](https://product.kyobobook.co.kr/detail/S000001609752) independently corroborate the title and release date. Aladin and Kyobo also show the same list and displayed sale prices and both mark the new copy unavailable. A direct YES24 browser recheck around 11:40 SGT on 2026-10-20 showed 12 used copies from KRW 24,000, down from the earlier same-day display of 15 copies from KRW 24,500. A later public page-reader result showed the older 15-copy / KRW 24,500 figure and was labelled crawled last month. This confirms that indexed page text can lag behind the retailer; preserve only timestamped captures and do not treat either aggregate as a seller-specific offer. The UsedShopHub route was not opened. On 2026-10-19, Aladin showed 12 used items in a summary, also without a seller-specific page.

The YES24 page visibly exposes the cover and one additional detail image, labelled 상세 이미지 1. The direct YES24 assets were resolved as `https://image.yes24.com/momo/TopCate709/MidCate003/70827706.jpg` (cover) and `https://image.yes24.com/momo/TopCate709/MidCate003/70827736.jpg` (detail link). Aladin and Kyobo also show a cover image. Aladin exposed this direct cover-thumbnail URL: `https://image.aladin.co.kr/product/7736/44/cover500/8997148613_1.jpg`. A second Aladin image link resolved to that same asset. At this initial checkpoint the image URLs were retained only as research provenance and image fields were blank. The October 24 Aladin follow-up below now links its exact cover and public publisher-provided collage remotely with source attribution, without asserting reuse permission.

### SANTORINI 산토리니: 고소영

[YES24 product detail](https://www.yes24.com/product/goods/416604)

YES24 identifies this as `고소영 화보집`, classifies it under 사진집 and 연예인 화보집, and names 고소영 as the model and 조세현 as photographer. The edition is published by Dreamax, dated 2003-11-29, ISBN 9788995439500; the page says page count and dimensions are unconfirmed and gives a weight of 1,030g. The product package is described as including five posters and a compilation CD.

At the live browser check around 12:12 SGT on 2026-10-20, YES24 showed list price KRW 27,000, displayed sale price KRW 25,650, and status `품절` with a message that new copies cannot be purchased. The page showed two used items from KRW 55,400, but the link goes to a YES24 UsedShopHub route disallowed by its robots file, so no seller-specific used offer was opened or verified. No active price is attached to the imported edition.

The page shows a product cover; no additional product-gallery images were confirmed. The five posters are part of the product package, not evidence of image-reuse permission. The initial checkpoint left image fields blank; the October 24 follow-up below now links the exact public cover remotely with product-page provenance and no reuse-license assertion.

A separate exact [used-copy detail page](https://www.yes24.com/product/goods/197061338) displayed KRW 11,000, condition 최상, and seller YES24 수영점 F1963 in the 2026-10-19 capture. That page's status was 일시품절, so this is not an active seller offer. The page also links to a used-shop summary route, but YES24 robots disallows the UsedShopHub route; do not open it or treat the summary as seller-specific inventory. No selling price is attached to the staged record.

### Standalone MAXIM-model photobook: 김설화 26

[YES24 product detail](https://www.yes24.com/product/goods/116981923)

The page identifies 김설화 as a MAXIM model, says she debuted through the 2020 Miss Maxim contest, and describes this as her first solo pictorial book. It lists publisher 아이다호, release date 2022-12-05, ISBN 9791198100504, 252 pages, and dimensions 215×270×15mm. The page advertises two randomized cover versions.

The direct YES24 browser recheck around 11:41 SGT on 2026-10-20 showed list price KRW 49,800 and displayed price KRW 44,820, but the status was 일시품절 and the page said a new copy could not currently be purchased. Preserve the two prices as displayed retailer metadata, not as an active offer; no current or seller-specific used offer was verified.

The product image links resolve to `https://image.yes24.com/goods/116981923/XL` and the smaller `https://image.yes24.com/Goods/116981923/S`; these are size variants and do not verify both randomized cover designs. The initial capture's 상세 이미지 link resolved to a YES24 no-image placeholder and left image fields blank. In the October 24 follow-up below, scrolling to the public image section loaded the actual promotional panel. The exact cover and loaded panel are now remotely linked with product-page provenance; reuse permission remains unconfirmed.

### Digital MAXIM B-cut pictorial: 미스맥심 보라

[YES24 product detail](https://www.yes24.com/product/goods/147841865)

The exact title is `맥심B컷(미공개화보) : ‘파티룩’ 미스맥심 보라`. YES24 places it in eBook > 잡지 > 남성 and describes the MAXIM B-cut series as unpublished pictorials. The page identifies publisher 와이미디어(맥심), release date 2025-06-20, a 77.75MB DRM PDF of about 36 pages, and list/selling price KRW 2,900. At the live browser check around 12:06 SGT on 2026-10-20, it showed `판매중` and a separate coupon-benefit price of KRW 2,610.

For MuseBooks, this record is a digital `photobook` with 미스맥심 보라 as the featured model: it is a single-model pictorial, not a dated monthly issue, and the retailer does not provide a monthly issue identity or explicit cover-model credit. This avoids inventing an issue number or marking the model as a cover credit. The product cover is visible on the page, but no additional gallery image was confirmed and image reuse permission is unverified; the record has no cover/media URL.

### MAXIM October 2026 physical B variant

[YES24 product detail](https://www.yes24.com/product/goods/196908938)

The live page recheck around 11:42 SGT on 2026-10-20 showed release date 2026-09-24, 176 pages, displayed list price KRW 9,600 and sale price KRW 9,120, with status 판매중 | 한정판매. YES24 labels 9772233427008 as ISBN13; retain it as a retailer barcode value for this magazine, not as a photobook ISBN. The listing's bonus description names Miss Maxim 조아 and 유디, but does not credit either as the B-variant cover model. Press articles identify 쥬 on the regular October cover and 유디 on a limited October cover ([쥬](https://b2bsell.co.kr/bbs/view/news/S1N18/5602001), [유디](https://www.specialtimes.co.kr/news/articleView.html?idxno=468327)); neither connects its named cover to this exact YES24 B-variant product ID. Keep the B variant as an unlinked research candidate until that mapping is explicit. The page exposes the cover asset `https://image.yes24.com/goods/196908938/XL`; no separately usable product-gallery image was confirmed. Keep the asset URL as provenance only. Do not copy the digital issue's date, price, or cover credit onto this print variant.

### MAXIM B-SIDE #5: 김소희 사진집 [속]

[YES24 product detail](https://www.yes24.com/product/goods/73754823)

The title appears under the magazine category as 맥심 B 사이드 MAXIM B SIDE (계간) : 5호 [2019]. The copy says it is Miss Maxim 김소희's first solo pictorial in the fifth B-SIDE series. Catalog it as a magazine issue, issue month 2019-06 and issue number 5, not as an independent photobook. The direct YES24 browser recheck around 11:42 SGT on 2026-10-20 showed release date 2019-06-10, 164 pages, list price KRW 14,000, displayed price KRW 13,300, and status 절판. Its page summary showed six used items from KRW 10,000; this is a marketplace lead only, not a seller-specific offer. The linked UsedShopHub path is disallowed by YES24 robots and was not opened.

A cover is visible on the detail page. Do not import the displayed historical new-sale price as an active offer.

The YES24 page exposes the direct cover asset `https://image.yes24.com/goods/73754823/XL`. Its “상세 이미지 1” link resolved to a no-image placeholder, so no separate product-gallery image was confirmed. The [Donga release report](https://sports.donga.com/ent/article/all/20190605/95862530/1) explicitly says Kim So-hee appears on the cover and identifies her as the model for the fifth B-SIDE. The live page recheck confirmed the displayed prices and 절판 status listed above. The used-stock summary remains unverified at seller level because its UsedShopHub route is disallowed and no exact seller page was opened. Keep the cover URL for provenance only and leave image fields blank.

### MAXIM B-SIDE #4: 김우현

[MAXIM publisher announcement](https://www.maximkorea.net/cms/contents_view.php?contents_uid=12411)

The publisher announcement identifies 김우현 as the model for the fourth B-SIDE special issue, gives 160 pages, and states 2018-12-05 as the release date. This is a special magazine issue, separate from any standalone 김우현 photobook. The metadata and Aladin observations are now represented in the review manifest; the Aladin source remains `review` with automated collection disabled. MAXIM's terms apply to use of its information and images.

The [MAXIM follow-up article](https://www.maximkorea.net/cms/contents_view.php?contents_uid=12416) confirms the dedicated 160-page 김우현 B-SIDE and release date. The [Aladin product page](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=174507165) labels 김우현 as the cover model and showed a KRW 14,000 list price / KRW 13,300 displayed price, but marked the issue sold out in a stale page snapshot. The YES24 search index showed two used listings in a KRW 23,000–40,000 range; its exact UsedShopHub route is disallowed, so that summary is not a seller-verified offer. A separate Aladin seller page is captured below. Aladin's terms restrict commercial reuse of its information without prior consent. The MAXIM article exposes three images for provenance: `https://www.maximkorea.net/cms/file/201812/editor_1545973108.jpg`, `https://www.maximkorea.net/cms/file/201812/editor_1545973117.jpg`, and `https://www.maximkorea.net/cms/file/201812/editor_1545973127.jpg`. They are article images, not confirmed canonical cover/sample assets; do not use them in MuseBooks without permission.

### Digital Korean-model photobook lead: Jinny — Late Summer

[Cupick product page](https://cupick.jp/en/products/jinny-late-summer)

The page tags Jinny as a Korean model and lists a 60-page digital photobook at JPY 2,000, viewed in the browser after purchase. A publication/release date is not displayed. The page snapshot available during this review was marked as crawled two weeks earlier, so recheck price and availability before treating them as current. The page links a cover asset at `https://cupick.jp/cdn/shop/files/product-126908_2048x2048.jpg?v=1739882500` and product images at `https://cdn.shopify.com/s/files/1/0777/4080/2334/files/0091.jpg?v=1727685152`, `https://cdn.shopify.com/s/files/1/0777/4080/2334/files/0076.jpg?v=1727685152`, and `https://cdn.shopify.com/s/files/1/0777/4080/2334/files/0112.jpg?v=1727685152`. These URLs are research provenance only. Cupick's terms prohibit automated tools and copying company content beyond personal use, so this lead is excluded from the import manifest until the site grants permission.

### Standalone photobook: 우현-아이 화보집

[YES24 product page](https://www.yes24.com/product/goods/106517266) · [YES24 public search result](https://www.yes24.com/Product/Search?query=%EC%9A%B0%ED%98%84+%EC%82%AC%EC%A7%84%EC%A7%91) · [contemporaneous report identifying model 우현 as 김우현](https://www.sportsseoul.com/news/read/715051)

The YES24 public search result, crawled the day before this review, identifies the book as a physical photobook by 김우현 from 우직스타즈, released in December 2021, with list and selling price KRW 180,000; it labels the item `품절`. An older public YES24 mobile search snapshot gives the exact publication date 2021-12-09. The product-detail route leads to an adult verification/login gate, which was not bypassed. The manifest stores the price as last-observed and availability as unknown. Page count, ISBN, cover and gallery images, and a seller-specific used offer were not verified; no image was copied.

## Keep the catalog types and prices separate

- Use publication type photobook for a standalone model photobook and magazine_issue for a dated MAXIM monthly or B-SIDE issue. A model's pictorial inside an issue does not make that issue a standalone book.
- Store issue month separately from the exact edition release date. Keep digital store release dates distinct from print release dates.
- A magazine issue requires an explicit cover-model credit for a model-linked record. Do not infer the cover model from bonus contents, a nearby recommendation, or the monthly issue title.
- Store list price, current sale price, coupon price, used asking price, and completed sale price as separate facts. Keep the source, time observed, seller, condition, availability, and product link with each price.
- Record a used offer only after an exact allowed seller page shows that specific copy. The YES24 used-summary floor for B-SIDE #5 is not a current seller offer.
- Keep the printed issue, any A/B cover variant, and any PDF/eBook edition distinct when the product pages identify separate products.

## Cover and other image handling

A product page showing an image does not by itself grant MuseBooks permission to copy, store, hotlink, or display it. Direct asset URLs were identified for the MAXIM October issue, BE JOYFUL, B-SIDE #5, Cupick's Jinny title, and the MAXIM B-SIDE #4 article, but reuse permission is not established. Product covers are also visible on the newly reviewed August 2025, February 2024, B-cut, and SANTORINI pages, but their direct asset URLs were not recorded and no image is cleared for use. No additional gallery image is ready to use.

Until permission is confirmed, leave Work and Edition cover URLs blank and link the record to its source page. Do not download covers, use MAXIM/BCUT previews, reproduce pages from a DRM PDF, or treat seller listing photos as publisher cover art. After permission is documented, keep the image's original URL, source page, role (cover or sample), and permission/license evidence together. Keep additional sample images separate from the canonical cover.

## Capture fields for future manual page checks

| Field | Rule |
| --- | --- |
| Korean model name | Preserve the exact credited name and the page that verifies it. Add a romanized name only when a reliable source supports the match. |
| Work title and type | Preserve exact title; choose photobook or magazine_issue before recording the item. |
| Issue identity | Issue month, printed issue number, A/B variant, print/digital format, and explicit cover-model credit where applicable. |
| Publication identity | Publisher/imprint, ISBN or ISSN with its correct label, format, page count and dimensions when shown. Never place an ISSN in the ISBN field. |
| Release date | Copy the explicit published/issued date. Keep date precision and source URL; do not substitute search date or crawler date. |
| Price | Currency, list price, ordinary selling price, coupon or promotion, seller-specific used asking price, and completed price as separate fields. |
| Availability | Exact page status such as 판매중, 한정판매, 품절, or 절판, plus observation time. |
| Cover and gallery | Capture only after reuse permission is documented. Store each authorized image's direct URL, source page, role, and license evidence. |
| Provenance | Keep the exact detail-page URL and timestamp for every page-derived observation. Unknown values remain empty with a reason. |

## Search terms

Search each verified Korean model name separately, then open exact detail pages:

- 모델명 사진집
- 모델명 화보집
- 모델명 포토북
- 모델명 단독 화보집
- 모델명 맥심
- 모델명 맥심 B사이드
- site:yes24.com/product/goods 모델명 사진집
- site:yes24.com/product/goods 모델명 화보집
- site:aladin.co.kr/shop/wproduct.aspx 모델명 화보집

Use exact title and ISBN on YES24, Aladin, Kyobo, and the National Library catalogue. Search snippets and related-product carousels are not import evidence.

## MuseBooks implementation notes

MuseBooks distinguishes photobooks from magazine issues and stores issue month, issue number, and cover-model credits. The Korean origin is KR. The migration [20261019_publication_type.sql](../backend/database/migrations/20261019_publication_type.sql) was applied to the configured MuseBooks database on 2026-10-20.

Before the August 2026 addition documented below, the review manifest contained ten records: MAXIM October 2026, January 2026, September 2024, August 2025, and February 2024 digital issues plus MAXIM B-SIDE #5 as `magazine_issue`; BE JOYFUL, 김설화 26, the single-model MAXIM B-cut Party Look pictorial, and SANTORINI are `photobook`. All ten were imported on 2026-10-20. The public catalog verifier completed successfully with 290 physical and 5,363 digital works. Live offers captured today are KRW 5,500 for MAXIM October 2026, KRW 5,500 for MAXIM August 2025, KRW 4,800 for MAXIM September 2024, KRW 4,800 for MAXIM February 2024, and KRW 2,900 for the B-cut pictorial. January retains the last observed KRW 5,500 price but availability is `unknown` because its page result was two days stale. B-SIDE #5, both other print photobooks, and SANTORINI have no verified active new-copy offer; their displayed historical prices and out-of-stock or discontinued states remain source observations, not active listings. The live MAXIM October print B listing was captured at KRW 9,120 with limited-sale status, but remains outside the import manifest because the exact B-variant cover credit is not established.

The importer stores day-, month-, and year-precision release dates at UTC midnight so MuseBooks clients preserve the source calendar date across time zones. The manifest records the reviewed publication dates as UTC calendar dates. The YES24 source remains disabled for automated collection; the importer accepts the reviewed `manual_page_capture` / `manual_browser` observations without enabling scrape jobs. Cover fields and media records remain blank, and direct asset URLs stay as provenance because image reuse rights are not established. Cupick is excluded because its terms prohibit automation and copying content beyond personal use. Korean pages are not added to the existing JP/TW/CN/MY browser worker.


## Additional MAXIM capture: August 2026 digital issue

[YES24 product detail](https://www.yes24.com/product/goods/194622253)

The product page identifies **맥심 MAXIM 2026. 8월호**, an authorized-store DRM PDF by 와이미디어(맥심). It gives a publication date of 2026-07-31, about 181 pages, ISSN 22334270, list price KRW 5,500, selling price KRW 5,500, and a `판매중` label in the page result. Its contents explicitly credit “치어리더 서여진” as the cover model. Keep this as a magazine issue (`issueMonth: 2026-08`), separate from photobooks.

The page result carried a “crawled last month” marker when checked on 2026-10-20, so the manifest records the observed KRW 5,500 price as a page snapshot and availability as unknown until a live browser recheck. The detail page links the cover asset `https://image.yes24.com/goods/194622253/XL`; the image host returned a cache-miss error during inspection. Keep the URL as provenance only. The cover is not cleared for display or local storage, and the record's cover fields remain empty.

## Additional MAXIM capture: September 2026 print B issue

[YES24 product detail](https://www.yes24.com/product/goods/195411512) · [Xports News report quoting the model's Instagram post](https://www.xportsnews.com/article/2189343)

YES24 identifies **맥심 MAXIM B형 (월간) : 9월 [2026]** as a print magazine issue. Its product page gives 2026-08-25 as the release date, about 176 pages, barcode `9772233427008`, list price KRW 9,600, and displayed sale price KRW 9,120. The page snapshot also says `판매중 | 한정판매`, but the result was marked as crawled last month, so current availability is `unknown` pending a live recheck. Treat the barcode as a magazine barcode, not as an ISBN. Do not record a used-market price: no seller-specific used offer was checked.

The page's bonus names Miss Maxim 윤영서 and 한지나 but does not label either as the cover model. Separately, Xports News reports on 2026-08-30 that 윤영서 announced her MAXIM B-type cover on Instagram, quoting her request that readers choose the B-type cover. The page confirms there is an exact September 2026 B-type print product, so the manifest links that model announcement to this edition as a cross-source issue match. The retailer page itself still does not provide a direct cover-model text credit; keep the confidence/source note visible for review.

YES24 displays the cover image on the product page, but a direct asset URL was not verified in this pass. Image-reuse permission is not established, no cover was copied, and no additional product-gallery image is cleared. The reviewed record is `magazine_issue`, separate from a photobook and from other September cover variants. Its manual price observation is in the review manifest; the YES24 source remains disabled for automated scraping.

## Continuation state: 2026-10-20

The review manifest contains fifteen records: nine `magazine_issue` records and six `photobook` edition records, representing five photobook works. All fifteen records were imported into MuseBooks on 2026-10-20. The importer committed the records and price observations. Its public-catalog verifier read back 292 physical and 5,365 digital works, and the read-only catalog endpoint confirmed both Jennie editions under one photobook work and the November 2025 MAXIM issue with their publication types, model credits, release dates, formats, and retailer observations. No retailer API or API key was used.

The August issue is a digital `magazine_issue` with issue month 2026-08, release date 2026-07-31, cover credit “치어리더 서여진,” and a last-observed KRW 5,500 price. Availability remains `unknown` because the YES24 result carried a last-month crawl marker. The September B issue is a physical `magazine_issue` with issue month 2026-09, release date 2026-08-25, cover credit 윤영서 matched across the retailer variant and her reported B-cover announcement, list price KRW 9,600, and last-observed sale price KRW 9,120. Its current availability is also `unknown` because the retailer result is stale. All cover/media fields remain empty pending image rights; the pages display covers, but direct image reuse permission is not established, and no gallery image has been cleared.

The Jennie work has two physical editions: the original dated 2018-11-15 with 72 pages, list price KRW 18,500, and last-observed YES24 price KRW 14,900; and the Special Edition dated 2018-12-11 with 128 pages, list price KRW 30,900, and last-observed price KRW 25,000. Both public catalog observations remain under `retailOffers` with `unknown` availability because their page snapshots were stale. The catalog verifier reported 292 physical and 5,365 digital works after this import. It also reported 1,509 unlinked verified listings and 16 editions with pending covers across the full database; these are catalog-wide counts, not Jennie import errors.

### Jennie [Solo] Photobook

[YES24 original edition](https://www.yes24.com/product/goods/66743901) · [YES24 Special Edition](https://www.yes24.com/product/goods/67292411) · [TIME report on Jennie's Chanel modeling work](https://time.com/5690135/jennie-kim-chanel-show-pfw-20/)

YES24 identifies **제니 (Jennie) - Jennie [Solo] Photobook**, published by YGPLUS / YG Entertainment with a release date of 2018-11-15. Its product specifications include a 72-page photobook, CD, random lyrics postcard, random photocard, and a first-run double-sided poster. YES24 places the original package under CD/LP > K-pop. The linked Special Edition page gives a separate 2018-12-11 release date for a 128-page hardcover photobook with additional Jennie images, stickers, a random postcard, and a random photocard. MuseBooks groups both physical releases as separate editions of one Jennie photobook work; the original package still includes its CD and bonuses.

The YES24 page snapshot returned during the 2026-10-20 review showed list price KRW 18,500 and displayed sale price KRW 14,900 (19% off), with `판매중`. Its crawl marker said last month, so availability is recorded as `unknown`; the amount is a dated new-copy page observation, not a live price guarantee. The page also showed one aggregate used item from KRW 8,320, but no seller-specific used offer was verified, and no used listing was opened. The Special Edition snapshot showed list price KRW 30,900, sale price KRW 25,000 (19% off), and `품절 | 한정판매`; its page was also marked crawled last month, so current availability remains `unknown`.

Both product pages display covers and detailed images, but this review did not establish reuse permission or verify direct asset URLs. The record leaves cover and gallery image fields empty. The TIME source supports Jennie's fashion-model credit; YES24 supports the Korean/English name mapping and photobook details. No API or API key was used.

### Additional MAXIM capture: November 2025 digital issue

[YES24 product detail](https://www.yes24.com/product/goods/162803480)

The YES24 page identifies **맥심 MAXIM 2025. 11월호** as a DRM PDF issue released on 2025-11-01, about 181 pages, ISSN `22334270`. Its contents include a `[COVER]` section naming 강인경. The page snapshot showed list and sale prices of KRW 5,500 and `판매중`; its crawl marker was two weeks old, so the catalog observation keeps availability `unknown`. No used-market price applies to this digital issue.

The product page displays a cover image, but image reuse permission was not established and no asset URL was verified. The catalog's work and edition cover fields remain blank.

## Earlier continuation state before the August 2024 issue import: 2026-10-20

The review manifest now contains sixteen records: ten MAXIM `magazine_issue` editions and six `photobook` editions representing five photobook works. All sixteen records have been imported. The public-catalog verifier reports 292 physical and 5,366 digital works, 1,509 unlinked verified listings, and 17 editions with pending covers across MuseBooks. A read-only database check confirmed the new July 2024 MAXIM work, cover-model credit, digital edition, release date, page count, and KRW 4,800 price observation. No retailer API or API key was used.

### Additional MAXIM capture: July 2024 digital issue — 치어리더 하지원

[YES24 product detail](https://www.yes24.com/product/goods/128598855)

The YES24 detail page identifies **맥심 MAXIM 2024. 7월호** as a DRM PDF released on 2024-07-01. It lists about 186 pages and 461.98 MB. In the contents, the page explicitly labels 치어리더 하지원 under `COVER MODEL`. This record is a digital `magazine_issue` with `issueMonth: 2024-07`; it is not a standalone photobook.

The page snapshot showed a list price and selling price of KRW 4,800 and `판매중`, but its crawl marker was two months old when reviewed at about 12:50 SGT on 2026-10-20. MuseBooks therefore stores KRW 4,800 as the last-observed page price and availability as `unknown`. No seller-specific used offer applies to this digital edition.

The page displays a cover; its direct asset URL is `https://image.yes24.com/goods/128598855/XL`. That URL is provenance only. No reuse permission was established, no cover or gallery image was copied, and the work and edition cover fields remain blank.

### Follow-up discovery leads: MAXIM B-cut pages

The YES24 MAXIM partner shop's new-product area exposed `BIKINI` B-cut leads for 미맥콘참가자 심연, 향지, 박보름, 탑체리, 주빈, 슈, 박서이, 키라, and 소이, with KRW 6,500 displayed in the listing snapshot. Exact product links returned cache-miss errors during this review, so individual release dates, current prices, availability, and detailed contents could not be verified. Treat the listing amounts as discovery snapshots only; do not assume a publication month or format for every result, or use a related-book/bonus-model name as a cover credit. These leads were not imported.

The MAXIM September 2026 digital issue also appeared in the partner shop at KRW 5,500, but its exact YES24 product detail was not retrievable in this review and no cover model was verified from the issue page. It remains a lead only. Continue from the [YES24 MAXIM partner shop](https://www.yes24.com/Product/PartnerShop/284442), then require an exact readable detail page before creating another catalog record.

## Previous continuation state before the June 2024 issue import: 2026-10-20

The review manifest contains seventeen records: eleven MAXIM `magazine_issue` editions and six `photobook` editions representing five photobook works. All seventeen records have been imported. The public-catalog verifier reports 292 physical and 5,367 digital works, 1,509 unlinked verified listings, and 18 editions with pending covers across MuseBooks. Read-only catalog checks confirmed the July and August 2024 MAXIM issue credits, dates, digital formats, page counts, and price observations. No retailer API or API key was used.

### Additional MAXIM capture: August 2024 digital issue — 치어리더 조연주

[YES24 product detail](https://www.yes24.com/product/goods/130023551)

The YES24 page identifies **맥심 MAXIM 2024. 8월호** as a DRM PDF released on 2024-08-01. It lists about 184 pages and 462.99 MB. The title subtitle names 치어리더 조연주, and the contents label her under `[COVER]`. This is a digital `magazine_issue` with `issueMonth: 2024-08`, kept separate from photobooks.

The page snapshot showed list and selling prices of KRW 4,800 and `판매중`. Its crawl marker was last week when reviewed around 12:56 SGT on 2026-10-20, so the record keeps KRW 4,800 as a last-observed value and availability as `unknown`. It is a digital edition; no used seller offer applies.

The detail page links the cover asset `https://image.yes24.com/goods/130023551/XL`. Keep that URL as provenance only. Image reuse permission is not established, no cover or additional gallery image was copied, and the MuseBooks cover fields remain blank.

## Continuation state before the later 2026-10-20 captures

The review manifest contains twenty records: fourteen MAXIM `magazine_issue` editions and six `photobook` editions representing five photobook works. All twenty records have been imported. The public-catalog verifier reports 293 physical and 5,369 digital works, 1,509 unlinked verified listings, and 21 editions with pending covers across MuseBooks. The database contains 5,972 works, 6,637 editions, 8,005 listings, 24 sources, and 8,043 listing observations. Read-only checks confirmed the physical B-SIDE #4 issue and the September 2026 digital issue with their model credits, dates, formats, page counts, and last-observed prices. No retailer API or API key was used.

### Additional MAXIM capture: June 2024 digital issue — 박기량

[YES24 product detail](https://www.yes24.com/product/goods/126982585) · [SportsKhan cover-model report](https://sports.khan.co.kr/article/202405231520003/amp)

YES24 identifies **맥심 MAXIM 2024. 6월호** as a DRM PDF released on 2024-06-05, about 184 pages and 471.27 MB. The contents include `COVER STORY — 박기량의 LAST DANCE`; SportsKhan independently identifies 박기량 as the June 2024 MAXIM cover model. The imported record is a digital `magazine_issue` with `issueMonth: 2024-06`.

The YES24 page showed list and selling prices of KRW 4,800 and `판매중`, but the page-reader snapshot carried a five-month crawl marker. The catalog therefore retains KRW 4,800 as a last-observed price and sets availability to `unknown`. No used seller offer applies to this digital issue.

The page links the cover asset `https://image.yes24.com/goods/126982585/XL`; this is provenance only. Image reuse permission is not established, the cover and any other product images were not copied, and the MuseBooks cover fields remain blank.

### MAXIM B-SIDE #4 print issue — 김우현

[MAXIM publisher report](https://www.maximkorea.net/cms/contents_view.php?contents_uid=12411) · [follow-up publisher report](https://www.maximkorea.net/cms/contents_view.php?contents_uid=12416) · [Aladin product page](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=174507165) · [Aladin seller listing](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=403982117)

The MAXIM publisher identifies this as its fourth B-SIDE special issue and a solo pictorial and essay made with model 김우현. Its report gives a 2018-12-05 release date and 160 pages. The imported record is a physical `magazine_issue` with issue month 2018-12; it is kept in the MAXIM issue series rather than classified as a standalone photobook. The Aladin product title explicitly credits 김우현 on the cover.

Aladin’s public product-page snapshot showed list KRW 14,000, displayed new-copy price KRW 13,300, and 품절; the page result was crawled about three months before this review, so availability is `unknown` and KRW 13,300 is only a last-observed display. A seller-specific used page crawled last week showed one P. J. Stahl offer at KRW 35,000, condition 상, with 바로구매. Because that snapshot was not live-rechecked, availability is `unknown`; KRW 35,000 is stored only as a last-observed asking price. The new and used observations are tied to separate Aladin item IDs in the review manifest.

The source is configured for manual capture only, with access status `review` and automated collection disabled. Aladin’s [terms](https://www.aladin.co.kr/account/waccount_provision.aspx?pType=1) restrict commercial use or onward provision of site information without prior consent, so the price observations are documented with their source and permission status. The publisher article and product page expose images, but no image reuse right was established; no cover or gallery image was copied and both MuseBooks cover fields remain blank.

### MAXIM September 2026 digital issue — 미스맥심 뮤아

[YES24 MAXIM partner shop](https://www.yes24.com/Product/PartnerShop/284442) · [YES24 product detail](https://www.yes24.com/product/goods/195804301) · [Kyobo eBook detail](https://ebook-product.kyobobook.co.kr/dig/epd/ebook/E000013514799)

YES24 identifies **맥심 MAXIM 2026. 9월호** as a DRM PDF and showed KRW 5,500 list/sale price with purchase controls in the partner-shop listing. The exact product detail could not be fetched in this review; the partner-shop page snapshot was about three weeks old, so availability is `unknown` and KRW 5,500 remains a last-observed value. A separate category result displayed a KRW 4,950 coupon amount, which was not verified as a live detail-page offer.

Kyobo’s exact eBook detail page gives a 2026-09-01 digital release, 183 pages, ISSN 25083597, and explicitly labels 미스맥심 뮤아 as `표지모델`. MuseBooks stores the YES24 item as a digital `magazine_issue` with issue month 2026-09. The cover asset remains blank because reuse rights are not established.

### Standalone photobook capture: JISOO [ME] Special Edition

[YES24 product detail](https://www.yes24.com/product/goods/121961075) · [YES24 mobile product detail](https://m.yes24.com/Goods/Detail/121961075) · [BoF 500 index](https://www.businessoffashion.com/bof500/) · [report on JISOO's Models & Muses listing](https://www.allkpop.com/article/2019/09/blackpinks-jisoo-listed-as-a-model-muse-on-business-of-fashion-500-of-2019)

YES24 classifies **지수 (JISOO) - JISOO [ME] PHOTOBOOK [SPECIAL EDITION]** under its 화보집 category. The page identifies JISOO as the photographic subject, publisher YGPLUS / YG Entertainment, release date 2023-09-18, and a 176-page photobook with a 20-piece postcard book and other inclusions. A report of the 2019 BoF 500 listing identifies JISOO in its Models & Muses group; she is also a singer, so MuseBooks stores her as the featured person rather than inventing a cover-model credit.

YES24 displays KRW 39,000 as the selling price. Product-page snapshots show new-copy stock unavailable / 품절, but the most recent indexed snapshot was crawled last week and the mobile snapshot is older. The manifest therefore stores KRW 39,000 as a last-observed page price and current availability as `unknown`; no seller-specific used offer was verified.

The page exposes a cover thumbnail at `https://image.yes24.com/Goods/121961075/S` and a 상세 이미지 link at `https://image.yes24.com/momo/TopCate4277/MidCate008/427677282%281%29.jpg`. Both asset fetches returned cache-miss responses during review, so the additional image content was not verified. These URLs are provenance only. YES24's terms do not establish image-reuse permission; no image was copied or placed in the MuseBooks image fields. The YES24 source remains manual-only with automated collection disabled.

### Standalone photobook capture: Password — Korean senior-model anthology

[YES24 product detail](https://www.yes24.com/product/goods/126289609)

YES24 identifies **Password** as a senior-model photo book by 진한엠앤비, released 2024-04-19. Its table of contents names 18 individual models and a separate event-photo section. The record stores the named subjects in MuseBooks' featured-names field instead of assigning the anthology to one model. The physical edition has 226 pages, dimensions 210×297×20mm, and ISBN 9791129052346.

The YES24 snapshot crawled two weeks before review showed list price KRW 45,000, displayed selling price KRW 42,750, 판매중, and purchase controls. Because that page snapshot is stale, the manifest records KRW 42,750 as last observed and availability as `unknown`; no seller-specific used offer was verified.

The page shows a cover thumbnail at `https://image.yes24.com/goods/126289609/XL`. No additional gallery image was exposed in the reviewed page text. The cover URL is provenance only; no product image was copied or added to MuseBooks because reuse permission is not established. The YES24 source remains manual-only with automated collection disabled.

### Additional Korean senior-model photobooks: The Briller, Password 4, and Password 5

[The Briller](https://www.yes24.com/product/goods/119131898) · [Password 4](https://www.yes24.com/product/goods/143622988) · [Password 5](https://www.yes24.com/product/goods/188880176)

These are separate senior-model photobook works, each with its own title, publication date, ISBN, and named subjects. The Briller (북엠) released 2023-05-24, has 248 pages, ISBN 9791192584027, and was initially captured with17 models; its contents explicitly identify 임민경 as the photographer. The later live Briller refinement below corrects the omitted이지유 subject and the count to18. YES24 showed a KRW 55,000 list price and KRW 49,500 selling price, with 판매중/purchase controls in a snapshot crawled two months before review. The record keeps the amount as last observed and current availability as unknown.

Password 4 (진한엠앤비) released 2025-02-19, has 244 pages, ISBN 9791129057945, and lists 21 models plus event photographs. Its page snapshot crawled two weeks before review showed KRW 77,000 list and KRW 73,150 sale prices with 판매중/purchase controls; current availability is recorded as unknown.

Password 5 (진한엠앤비) released 2026-05-04, has 186 pages, ISBN 9791129064202, and names 14 models alongside event, fashion-week, and documentary sections. Its page snapshot crawled about one month before review showed KRW 75,000 list and KRW 71,250 sale prices with 판매중/purchase controls; current availability is recorded as unknown. No seller-specific used offer was verified for any of these three items.

YES24 displays a cover thumbnail for each product page, but no image-reuse permission was established and no cover or gallery image was copied into MuseBooks. YES24 remains manual-only with automated collection disabled.

### Additional MAXIM capture: January 2024 digital issue — 묘정

[YES24 product detail](https://www.yes24.com/product/goods/124406594)

YES24 identifies **맥심 MAXIM 2024. 1월호 (BEGIN AGAIN)** as a DRM PDF released 2024-01-02, about 185 pages and 48.15 MB. Its contents have a `COVER STORY` naming 묘정. The manifest records her explicit cover credit on a digital `magazine_issue` with issue month `2024-01`.

The page snapshot displayed KRW 4,800 list and selling prices and `판매중`, but the crawler marked it last month. KRW 4,800 is retained as a last-observed page price and availability is `unknown` until a live recheck. No used offer applies to this digital edition. The product page links the cover at `https://image.yes24.com/goods/124406594/XL`; fetching that asset returned a cache-miss response, so the image file itself was not verified. No additional product-gallery image was confirmed. Keep the URL as provenance only; MuseBooks image fields stay blank because reuse permission is not established.

### Additional MAXIM capture: March 2024 digital issue — 이유진 and 이규영

[YES24 product detail](https://www.yes24.com/product/goods/125313325)

YES24 identifies **맥심 MAXIM 2024. 3월호 (이유진/이규영)** as a DRM PDF released 2024-03-06, about 191 pages and 127.62 MB. The contents explicitly label a `COVER` section naming 이유진 and 미스맥심 이규영. Both are recorded as cover models on the digital `magazine_issue`, month `2024-03`.

The page snapshot showed list and selling prices of KRW 4,800 and `판매중`, but its crawl marker was two months old. The record keeps KRW 4,800 as the last-observed price and marks current availability `unknown`. No used offer applies. The product page links the cover at `https://image.yes24.com/goods/125313325/XL`; fetching that asset returned a cache-miss response, so the image file itself was not verified. No additional product-gallery image was confirmed. Keep the URL as provenance only; MuseBooks cover fields are blank because reuse rights remain unconfirmed.

### Additional MAXIM capture: May 2024 digital issue — 바비앙 and 김갑주

[YES24 product detail](https://www.yes24.com/product/goods/126331777)

YES24 identifies **맥심 MAXIM 2024. 5월호** as a DRM PDF released 2024-05-02, about 184 pages and 463.48 MB. The contents explicitly list `COVER MODEL` credits for 미스맥심 바비앙 and 미스맥심 김갑주. Both cover credits are recorded on a digital `magazine_issue`, month `2024-05`.

The page snapshot showed list and selling prices of KRW 4,800 and `판매중`, but its crawl marker was last month. KRW 4,800 is retained as a last-observed price and availability is `unknown`. No used offer applies. The product page links the cover at `https://image.yes24.com/goods/126331777/XL`; fetching that asset returned a cache-miss response, so the image file itself was not verified. No additional product-gallery image was confirmed. Keep the URL as provenance only; MuseBooks does not display the image until reuse permission is established.

### Unresolved MAXIM April 2024 cover variant

[YES24 eBook detail](https://www.yes24.com/product/goods/125759590) · [contemporaneous report naming 감동란](https://www.civilreporter.co.kr/news/articleView.html?idxno=336952) · [contemporaneous report naming 김호영](https://news.nate.com/view/20240329n00274)

YES24 lists **맥심 MAXIM 2024. 4월호 (감동란)**, released 2024-04-01, about 187 pages, and a stale snapshot price of KRW 3,360 sale / KRW 4,800 list. A contemporaneous article says BJ 감동란 appears on the April cover, while another identifies musical actor 김호영 as an April cover. These may be different print cover variants; the YES24 digital page does not expose an explicit `COVER` credit or identify which cover artwork the digital PDF uses. Keep this as a lead rather than assigning one cover person or creating an ambiguous issue record.

The page snapshot also showed `판매중`, but its crawl marker was six months old, so any listed price and availability are stale. A cover is visible on the page; additional gallery assets and reuse rights were not verified.

### Additional MAXIM capture: November 2024 digital issue — 뽀구미

[YES24 product detail](https://www.yes24.com/product/goods/136885088) · [contemporaneous cover report](https://www.stardailynews.co.kr/news/articleView.html?idxno=463122)

YES24 identifies **맥심 MAXIM 2024. 11월호** as a DRM PDF released 2024-11-05, about 184 pages and 492.78 MB. The retailer title names 뽀구미; a contemporaneous report explicitly says she covers the November issue. The imported record stores her as the verified cover model for the digital `magazine_issue`, month `2024-11`.

The page was fetched in this review with a crawl marker of today. It showed `판매중`, KRW 4,800 list and selling prices, and purchase controls, so the observation is recorded active at that page state. No used offer applies. YES24 links the cover at `https://image.yes24.com/goods/136885088/XL`; its image fetch returned a cache miss, so the file itself was not verified. No additional product-gallery image was confirmed. Keep the asset URL as provenance only; image reuse rights are not established.

### Additional MAXIM capture: December 2024 digital issue — 쥬

[YES24 product detail](https://www.yes24.com/product/goods/139856058) · [contemporaneous winner and cover report](https://www.specialtimes.co.kr/news/articleView.html?idxno=412995)

YES24 identifies **맥심 MAXIM 2024. 12월호** as a DRM PDF released 2024-12-02, about 185 pages and 189.55 MB. Its contents open with the `THE WINNER` story. A contemporaneous report says 2024 Miss Maxim winner 쥬 would appear on the December cover; this independent cover credit is stored with the digital `magazine_issue`, month `2024-12`.

The YES24 snapshot showed KRW 4,800 list/selling prices and `판매중`, but the crawler marked it last month. Keep KRW 4,800 as a last-observed price and current availability as `unknown`. No used offer applies. The page links the cover at `https://image.yes24.com/goods/139856058/XL`; asset fetch returned a cache miss. No other product-gallery image was verified, and no image is embedded in MuseBooks without reuse permission.

### Additional MAXIM capture: January 2025 digital issue — 갓세희

[YES24 product detail](https://www.yes24.com/product/goods/141129287)

YES24 identifies **맥심 MAXIM 2025. 1월호** as a DRM PDF released 2025-01-03, about 185 pages and 299.51 MB. Its contents explicitly label `COVER : '갓세희' 편`, so the record credits 갓세희 as cover model on a digital `magazine_issue`, month `2025-01`.

The page snapshot showed KRW 4,800 list/selling prices and `판매중`, but the crawler marked it last month. Availability is therefore `unknown`, with KRW 4,800 retained as the last-observed price. No used offer applies. The page links the cover at `https://image.yes24.com/goods/141129287/XL`; asset fetch returned a cache miss. No additional product-gallery image was verified and the cover remains a provenance URL only.

### Unresolved MAXIM October 2024 cover identity

[YES24 product detail](https://www.yes24.com/product/goods/134021651)

YES24 lists **맥심 MAXIM 2024. 10월호 '미신' 편**, released 2024-10-02, about 186 pages and 193.70 MB. Its page snapshot showed list/selling prices of KRW 4,800 and `판매중`, with a crawl marker last month. The issue contents reviewed here do not explicitly name a cover model, and the page title names only the theme. It remains a lead; no person credit or catalog record was assigned.

## Latest continuation state: 2026-10-20 14:33 Asia/Singapore

### Additional MAXIM capture: February 2025 digital issue — 박근나, 김서아, and 려니

[YES24 product detail](https://www.yes24.com/product/goods/142231472) · [publisher-sourced report](https://press.mtime.co.kr/newsRead.php?no=1004747)

YES24 identifies **맥심 MAXIM 2025. 2월호** as a DRM PDF released 2025-02-05, about 186 pages and 395.09 MB. Its contents place the Mabinogi Heroes feature under `COVER` and name Miss Maxim models 박근나, 김서아, and 려니. The contemporaneous report, sourced to MAXIM publisher 와이미디어, identifies the trio with the February issue cover. All three are linked to this digital `magazine_issue`, month `2025-02`.

The YES24 snapshot showed list and selling prices of KRW 4,800 with sale controls, but its crawl marker was within the last three weeks. The record retains KRW 4,800 as last-observed and keeps availability `unknown` pending a live recheck. No used offer applies to this digital edition. YES24 displays a product cover; it was not copied, and reuse permission remains unconfirmed.

### Additional MAXIM capture: March 2025 digital issue — 우수한

[YES24 product detail](https://www.yes24.com/product/goods/143312098) · [contemporaneous cover report](https://www.stnsports.co.kr/news/articleView.html?idxno=242497)

YES24 identifies **맥심 MAXIM 2025. 3월호 '여사친' 편** as a DRM PDF released 2025-03-05, about 185 pages and 280.27 MB. Its contents explicitly label a `COVER` section naming 치어리더 우수한. STN News independently reports that 우수한 was featured on three March cover designs. She is recorded as the cover model for the digital `magazine_issue`, month `2025-03`.

A YES24 category listing crawled the day before this review displayed KRW 4,800 list and selling prices with cart and direct-purchase controls, so the offer is marked active at that listing snapshot. No used offer applies to this digital edition. The cover remains a provenance-only preview; image-reuse rights are unconfirmed.

### Additional MAXIM capture: May 2025 digital issue — 장은비

[YES24 product detail](https://www.yes24.com/product/goods/146279404) · [official MAXIM Korea cover-model video](https://www.youtube.com/watch?v=yjefuyfsZHg)

YES24 identifies **맥심 MAXIM 2025. 5월호 '동거' 편** as a DRM PDF released 2025-05-07, about 181 pages and 471.42 MB. Its contents feature the YouTuber 장은비 in the `COVER STORY`; an official MAXIM Korea video titled `[Cover Model]` names her. The digital `magazine_issue`, month `2025-05`, credits 장은비.

YES24 showed list and selling prices of KRW 4,800 and purchase controls. The desktop detail snapshot was crawled last month; a mobile listing was crawled four days before this review. KRW 4,800 is stored as last-observed, while availability remains `unknown` pending a fresh product-page check. No used offer applies to this digital edition. Image fields remain blank pending reuse permission.

### MAXIM April 2025 PDF: public listing verified, cover variant unspecified

[YES24 product detail](https://www.yes24.com/product/goods/144441861) · [report naming 하리](https://biz.chosun.com/entertainment/tv/2025/03/24/ILTXLIYRKIET4MKC5VT2BUTLZU/) · [report naming subscription cover 뮤아](https://www.mimint.co.kr/bbs/view/news/S1N18/4757340?page=280&pageblock=271) · [issue page snapshot with B-type cover information](https://www.inven.co.kr/board/webzine/2097/2422154)

The live [YES24 public series page](https://www.yes24.com/product/category/series/017001036?SeriesNumber=231021), reviewed on 2026-10-23 around 22:31 SGT, links exact product 144441861 as **맥심 MAXIM 2025. 4월호 '이불킥' 편**, PDF, publisher 와이미디어(맥심), publication April 2025, ordinary price KRW 4,800 and separate coupon price KRW 4,320. The exact row exposes cart and direct-purchase controls, supporting active status at this public-list observation time. The stored price is the ordinary KRW 4,800. Its detail route still redirects to an adult-login notice; no login, age submission or access bypass was performed.

This YES24 batch initially represented `korea-maxim-2025-04-digital-pdf` on the existing `korea-maxim-2025-04-issue` with month precision. Its public row does not establish a publication day, page count, file size or exact cover variant. The later Aladin batch below refines the shared PDF metadata using a separately attributed retailer assertion. The shared issue retains verified print A/B credits 하리/한지나 and reported subscription-cover credit 뮤아; these do not imply all three appear on this PDF's cover. No used offer applies to the PDF.

The [YES24 capture](korean-maxim-april-2025-yes24-capture.json) preserves the exact public source row and unknowns. The [database report](korean-maxim-april-2025-yes24-db-verification.json) covers the PDF and previously imported print editions/listings and all three issue credits. The public catalog verifier also passed before further collection. No retailer API or catalog image storage was used; image reuse permission remains unconfirmed.

### April 2025 PDF: separate Aladin observation and date refinement

The [Aladin PDF page](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=361617093) snapshot reviewed on 2026-10-23 around 22:35 SGT explicitly gives publication 2025-04-01, publisher 주식회사와이미디어, PDF 147.57 MB, no TTS, and ISSN 22334270. Its crawl-age label is **1.3 years ago**. Browser attachment was unavailable, so Aladin availability stays unknown; KRW 4,800 is last observed, with the separate KRW 4,320 coupon price excluded from ordinary pricing.

The [capture](korean-maxim-april-2025-aladin-pdf-capture.json) preserves that limitation. This adds one source listing to the existing PDF, refines its date to day precision from Aladin, and preserves the earlier YES24 observation. Catalog-edition matching does not claim identical DRM packages. Page count and exact PDF cover remain unresolved. The [database report](korean-maxim-april-2025-aladin-pdf-db-verification.json) covers all April records. Exact read-back and public catalog verification passed before further collection. No retailer API or catalog image storage was used.

### April 2025 subscription S edition: exact Joongna advertisements

[Current exact listing](https://web.joongna.com/product/232133783) · [Older unavailable advertisement](https://web.joongna.com/product/228026820) · [Subscription cover report](https://www.mimint.co.kr/bbs/view/news/S1N18/4757340?page=280&pageblock=271) · [Joongna terms](https://web.joongna.com/terms) · [Post collection/use notice](https://web.joongna.com/post-policy)

Live browser checks on 2026-10-23 around 22:43 SGT identify the current offer as **맥심 263호 한정판 뮤아 25년 4월호 미개봉 새제품**, seller 큐팔이, KRW 29,500 including parcel shipping. Chat/purchase controls support active status at observation time. New/unopened condition and inclusion of all components are seller claims. The cover visibly prints `263 S type`; contemporaneous reporting independently identifies 뮤아 as the April subscriber-cover model. The earlier search result's KRW 30,000 is superseded by the live price.

The older exact advertisement now says the product is no longer sold. A historical page snapshot, labelled four months old, supplies its former KRW 25,000 asking price and free shipping. This is stored as an unavailable/unknown observation, without asserting an actual sale, paid amount or seller identity. Distinct advertisement IDs do not prove two simultaneous copies or a single copy's sale history. The [capture](korean-maxim-april-2025-subscription-capture.json) records both observations and the unverified Aladin related-card lead.

The catalog adds `korea-maxim-2025-04-print-s-subscription` on the existing April `magazine_issue`, with original publication day, page count, dimensions, ISBN and original retail price left unknown. A/B and PDF dates are not copied into S metadata. The shared issue number is refined to 263호 (4월호). The [database report](korean-maxim-april-2025-subscription-db-verification.json) covers every April record and all three issue cover credits. Exact read-back and public catalog verification passed before further collection.

Joongna is registered as `joongna-kr-manual`, `manual_browser`, access `review`, with automated collection disabled. The first read-back caught an importer default enabling a newly created manual source; the importer now preserves the requested disabled flag before creation defaults are applied. Reapplying the manifest and reading the source back confirmed `enabled=false`. Its terms and post-use notice are review references, not a grant of scraping or image-reuse permission. Seller images were inspected for printed edition text; no image is stored or embedded in the catalog. No retailer API, seller contact or purchase was used.

### Additional MAXIM capture: June 2025 digital issue — 첼설아

[YES24 product detail](https://www.yes24.com/product/goods/147167667) · [contemporaneous cover report](https://www.gukjenews.com/news/articleView.html?idxno=3281735) · [YES24 MAXIM series listing](https://m.yes24.com/Category/SeriesGoods/017001036?SeriesNumber=231021)

YES24 lists **맥심 MAXIM 2025. 6월호** as a PDF issue. The mobile series listing gives 2025-06-01 as the eBook date; the exact product detail redirects to an adult-login check, so page count and file size were not captured. A contemporaneous report identifies 첼설아 as the June cover model. She is recorded on a digital `magazine_issue`, month `2025-06`.

The YES24 series listing crawled the day before review showed KRW 4,800 list and selling prices with cart and direct-buy controls; the observation is active at that page snapshot. No used offer applies to this digital issue. Cover imagery was not copied and reuse permission remains unconfirmed.

### Additional MAXIM capture: July 2025 digital issue — E다연

[YES24 product detail](https://www.yes24.com/product/goods/148366163) · [contemporaneous cover report](https://newspatch.co.kr/post/77UnnnI3) · [YES24 MAXIM series listing](https://m.yes24.com/Category/SeriesGoods/017001036?SeriesNumber=231021)

YES24 lists **맥심 MAXIM 2025. 7월호** as a PDF issue with a 2025-07-01 eBook date. The exact product detail redirects to an adult-login check, so page count and file size were not captured. NewsPatch reports that Miss Maxim E다연 was chosen as its solo cover model. She is recorded on a digital `magazine_issue`, month `2025-07`.

The YES24 series listing crawled the day before review showed KRW 4,800 list and selling prices with cart and direct-buy controls; the observation is active at that page snapshot. No used offer applies to this digital issue. Cover imagery was not copied and reuse permission remains unconfirmed.

### Additional MAXIM B-cut captures: October 2026 digital pictorials

[YES24 eBook new-products listing](https://www.yes24.com/product/category/attentionnewproduct?categoryNumber=017001036005) · [mobile new-products listing](https://m.yes24.com/home/new?dispNo=017001036&tab=2) · [MAXIM partner shop](https://www.yes24.com/Product/PartnerShop/284442)

The YES24 rendered listing exposes individual model-specific PDF pictorials. These are cataloged as `photobook` works because each is a separately sold model pictorial, not a dated monthly issue. The listing provided the current catalog date, retail price, coupon benefit where shown, and purchase controls. Exact days are retained only where the mobile listing exposed them; otherwise release precision is month.

| YES24 item | Model | Published | List and regular selling price | Coupon benefit shown |
| --- | --- | --- | ---: | ---: |
| [COSTUME — 차유니](https://www.yes24.com/product/goods/198296872) | 차유니 | 2026-10 (month) | KRW 7,900 | KRW 7,110 |
| [하트쟁취대작전 #2 — 김은지](https://www.yes24.com/product/goods/198033909) | 김은지 | 2026-10 (month) | KRW 8,900 | KRW 8,010 |
| [Watching you #2 — 김서아](https://www.yes24.com/product/goods/197983301) | 김서아 | 2026-10-13 | KRW 9,900 | KRW 8,910 |
| [Sunkissed&Lit #2 — 소은](https://www.yes24.com/product/goods/197957311) | 소은 | 2026-10-12 | KRW 7,900 | KRW 7,110 |
| [Bikini RED&WHITE — 첼설아](https://www.yes24.com/product/goods/197835739) | 첼설아 | 2026-10 (month) | KRW 5,900 | KRW 5,310 |
| [Watching you #1 — 김서아](https://www.yes24.com/product/goods/197766165) | 김서아 | 2026-10 (month) | KRW 8,900 | KRW 8,010 |
| [COSTUME — 주빈](https://www.yes24.com/product/goods/197662022) | 주빈 | 2026-10 (month) | KRW 7,900 | Not captured |
| [Wet in the rain [swimsuit] — 모모리나](https://www.yes24.com/product/goods/197568048) | 모모리나 | 2026-10 (month) | KRW 6,900 | KRW 6,210 |
| [하트쟁취대작전 #1 — 김은지](https://www.yes24.com/product/goods/197367343) | 김은지 | 2026-10 (month) | KRW 8,900 | KRW 8,010 |
| [Sunkissed&Lit #1 — 소은](https://www.yes24.com/product/goods/197329943) | 소은 | 2026-10 (month) | KRW 7,900 | KRW 7,110 |

The retailer displays each regular selling price equal to its listed price; coupon benefits are optional and are recorded in the price evidence rather than treated as the base retail offer. The visible listing had cart and purchase controls, so availability is `active` at the 2026-10-20 snapshot. These are digital PDFs, so no used-market offer applies. The listing displayed cover thumbnails, but the linked detail pages did not render during follow-up; page counts and additional gallery images remain unverified. No cover or gallery image was copied, and the manifest image fields stay blank pending reuse permission.

### Additional MAXIM issue captures: October and December 2025, March and April 2026

The YES24 MAXIM eBook series lists the seven earlier entries as digital PDFs by 와이미디어(맥심), with list and selling prices of KRW 5,500 and a coupon price of KRW 4,950 in the captured listing. That listing snapshot was crawled last month; the detail pages redirected to an age-check page, so availability is `unknown`, prices are last-observed, and page counts or gallery images are not claimed. The February 2026 issue was rechecked live on 2026-10-20; its detail page showed `판매중`, 183 pages, and an exact publication date. Digital editions have no used offer.

| Issue | YES24 product | Cover-model credit | Published | Last-observed list / selling / coupon |
| --- | --- | --- | --- | ---: |
| 2025-10 | [맥심 MAXIM 2025. 10월호](https://www.yes24.com/product/goods/155209805) | 이예빈 — [official MAXIM announcement](https://www.youtube.com/watch?v=UWxwYjL5ujs), issue 269 | Month only | KRW 5,500 / 5,500 / 4,950 |
| 2025-12 | [맥심 MAXIM 2025. 12월호](https://www.yes24.com/product/goods/167547868) | 채솔 — [official MAXIM announcement](https://www.youtube.com/watch?v=zQeNUavxRes), issue 271 | Month only | KRW 5,500 / 5,500 / 4,950 |
| 2026-02 | [맥심 MAXIM 2026. 2월호](https://www.yes24.com/product/goods/176990791) | 리리 (A-type), 첼설아 (B-type), 섹밍 (subscription S-type) — [retailer variant credits](https://www.bananamall.co.kr/shop/view.php?cate=&index_no=2495168), [subscription-cover report](https://www.mimint.co.kr/bbs/view/news/S1N18/5227092) | 2026-02-02 | KRW 5,500 / 5,500 / 4,950 |
| 2026-03 | [맥심 MAXIM 2026. 3월호](https://www.yes24.com/product/goods/180966290) | 김도아 — [Kyobo eBook contents](https://ebook-product.kyobobook.co.kr/dig/epd/ebook/E000012645261) explicitly name her as cover model | 2026-03-01 (Kyobo) | KRW 5,500 / 5,500 / 4,950 |
| 2026-04 | [맥심 MAXIM 2026. 4월호](https://www.yes24.com/product/goods/184354137) | 김나연 — [StarDaily News report](https://news.nate.com/view/20260323n18368), linked from the MAXIM press index | Month only | KRW 5,500 / 5,500 / 4,950 |
| 2026-05 | [맥심 MAXIM 2026. 5월호](https://www.yes24.com/product/goods/188956396) | 채솔 — [Kyobo eBook contents](https://ebook-product.kyobobook.co.kr/dig/epd/ebook/E000012932768) explicitly name her as cover model | 2026-05-01 (Kyobo) | KRW 5,500 / 5,500 / 4,950 |
| 2026-06 | [맥심 MAXIM 2026. 6월호](https://www.yes24.com/product/goods/190792042) | 김우현 — [Kyobo eBook contents](https://ebook-product.kyobobook.co.kr/dig/epd/ebook/E000013081612) explicitly name her as cover model | 2026-06-01 (Kyobo) | KRW 5,500 / 5,500 / 4,950 |
| 2026-07 | [맥심 MAXIM 2026. 7월호](https://www.yes24.com/product/goods/192991630) | 바비앙 — [Kyobo eBook contents](https://ebook-product.kyobobook.co.kr/dig/epd/ebook/E000013195770) explicitly name her as cover model | 2026-07-01 (Kyobo) | KRW 5,500 / 5,500 / 4,950 |

The YES24 series page is the source for product identity, issue month, publisher and pricing. The MAXIM YouTube channel supplies official cover credits for the 2025 issues; Kyobo's contents and contemporaneous reports corroborate the 2026 credits. The February 2026 YES24 detail page gives the exact eBook publication date and price. Its digital cover variant is not specified; the issue-level credits include two retail print covers and one subscription cover. The Aladin pages list print A and B editions, ISBNs, specifications, prices, used-offer floors, and out-of-stock status in stale page snapshots. The Aladin release date (2026-01-21) differs from BananaMall's 2026-01-24 issue date; the manifest keeps the edition-specific Aladin date. Covers and gallery assets remain unembedded because image-reuse permission is unconfirmed.

#### February 2026 print cover editions

Aladin lists separate physical editions for the A and B covers. Its page snapshots are two months old, so new-copy availability remains `unknown`; both pages displayed `품절`. Each displayed list KRW 9,600 and sale KRW 9,120. Aladin showed four used offers starting at KRW 11,860 for A and two starting at KRW 18,000 for B. The used-detail links missed the cache during this review, so those are last-observed offer floors rather than confirmed current offers.

| Edition | Cover model | Published (Aladin) | Aladin item | ISBN | Pages | Last-observed new list / sale | Last-observed used offers |
| --- | --- | --- | --- | --- | ---: | ---: | ---: |
| A type | 리리 | 2026-01-21 | [Aladin A edition](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=384591968) | K952135812 | 176 | KRW 9,600 / 9,120 | 4 offers from KRW 11,860 |
| B type | 첼설아 | 2026-01-21 | [Aladin B edition](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=384590914) | K912135811 | 176 | KRW 9,600 / 9,120 | 2 offers from KRW 18,000 |

#### December 2025 print issue #271: Aladin A/B editions and used offers

[Aladin A-type listing](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=378811191) · [Aladin B-type listing](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=378811761) · [official MAXIM cover announcement](https://www.youtube.com/watch?v=zQeNUavxRes) · [Kyobo December issue listing](https://ebook-product.kyobobook.co.kr/dig/epd/ebook/E000012272622)

Aladin lists A and B print variants with a 2025-11-25 publication date, list price KRW 9,600, sale price KRW 9,120, 176 pages, and 210×297mm dimensions. The A ISBN is K562033906; the B ISBN is K792033906; both list ISSN 2233-4270. Aladin's A-page snapshot was crawled about five months before this review and showed 품절 with a stock-check date of 2025-12-26. The B page snapshot was crawled last month and also showed 품절. Availability is stored as unknown and prices as last-observed. Kyobo lists the domestic print release as 2025-11-27; the manifest keeps the Aladin date on these Aladin editions. MAXIM's official issue-271 video identifies 채솔 as the issue cover model, but the retailer pages do not map the cover art to A or B. Aladin's A page lists a 채솔/김은지 bromide; that supplement credit is not used as variant-specific cover evidence.

The used-offer snapshots were crawled last month. Exact item pages or the seller profile identify these four seller offers; current availability is unknown. The two Kim Minsoo rows use reviewer-assigned source keys because the profile did not expose individual offer URLs.

| Edition | Seller | Condition | Last-observed asking price | Shipping | Aladin offer |
| --- | --- | --- | ---: | --- | --- |
| A | P. J. Stahl | 상 | KRW 30,000 | KRW 3,500 standard / KRW 5,000 remote / KRW 2,400 half-price parcel | [395452695](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=395452695) |
| A | diskplan | 최상 | KRW 25,000 | KRW 3,500 standard / KRW 5,000 remote / KRW 2,400 half-price parcel | [401166086](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=401166086) |
| A | 김민수 | 중 | KRW 6,300 | Not stated on the captured seller row | [seller profile](https://www.aladin.co.kr/shop/usedshop/wshopitem.aspx?sc=786426) |
| B | 김민수 | 최상 | KRW 11,000 | Not stated on the captured seller row | [seller profile](https://www.aladin.co.kr/shop/usedshop/wshopitem.aspx?sc=786426) |

An older diskplan seller sidebar on an unrelated product page mentioned December B at KRW 24,000 and A at KRW 28,000, but did not expose offer URLs or conditions; those mentions remain source notes, not seller listing records. No image was copied because reuse permission is unconfirmed. Both print editions and all six new/used listing observations passed manifest validation, were committed to PostgreSQL, and were read back by the verifier before the next source list began.

#### November 2025 print issue #270: A/B editions and used offers

[Aladin A-type listing](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=374961993) · [Aladin B-type listing](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=374962129) · [official MAXIM issue list](https://www.maximkorea.net/magdb/_ajax_magdb_list.php) · [YES24 November issue contents](https://www.yes24.com/product/goods/162803480)

MAXIM's public issue list identifies issue #270, titled `을의 연애`, with A and B print types for November 2025. Aladin lists both variants with a 2025-10-22 publication date, list price KRW 9,600, sale price KRW 9,120, 176 pages, and 210×297mm dimensions. The A ISBN is K562032614. Aladin's B page labels 9772233427039 as ISBN; this ISSN-based barcode is retained in the edition note and not in the database ISBN field. The A page snapshot was crawled about two weeks before this review and showed 품절 with a last stock-check date of 2025-11-25. The B page snapshot was crawled about four months before this review; an Aladin series snapshot displayed 품절. Availability is stored as unknown and the prices are last-observed. YES24's November digital issue contents explicitly credit 강인경 under COVER. Aladin's A and B pages name different bromide subjects, which does not establish which model appears on each exact print cover.

Aladin's A page reports seven used copies and an aggregate floor of KRW 19,900. That aggregate does not identify seller listings. One exact used offer was captured:

| Edition | Seller | Condition | Last-observed asking price | Shipping | Aladin offer |
| --- | --- | --- | ---: | --- | --- |
| A | diskplan | 최상 | KRW 25,000 | KRW 3,500 standard / KRW 5,000 remote / KRW 2,400 half-price parcel | [401166714](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=401166714) |

A kirinji seller sidebar also mentioned an A copy at KRW 13,000 but exposed no item URL or condition; it remains a source note, not a listing record. No seller-specific B offer with a direct listing or seller-profile URL was verified. The two print editions and three listing observations passed manifest validation, were committed to PostgreSQL, and were read back by the verifier before the next source list. No image was copied because reuse permission is unconfirmed.

#### October 2025 print issue #269: A/B/S variants and used offers

[Aladin A-type listing](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=372908505) · [Aladin B-type listing](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=372908712) · [contemporaneous MAXIM issue announcement](https://newspatch.co.kr/post/rbMzcaLb) · [exact used A offer](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=389172764) · [김민수 seller profile](https://www.aladin.co.kr/shop/usedshop/wshopitem.aspx?sc=786426) · [exact used S offer](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=373213316)

The contemporaneous announcement identifies MAXIM issue #269 and three October cover variants for cheerleader 이예빈: bookstore A/B and subscription S. Aladin lists A and B with a 2025-09-24 publication date, KRW 9,600 list price, KRW 9,120 sale price, 176 pages, and 210×297mm dimensions. A is ISBN K682031345; B is K702031345. Its page snapshots show 품절, so availability is unknown and prices are last-observed. The issue-level digital product and announcement verify 이예빈's cover credit; the source does not provide reusable image permission, so cover and gallery image fields remain blank.

Three used offers were reviewed:

| Edition | Seller | Condition | Last-observed asking price | Status in source snapshot | Aladin record |
| --- | --- | --- | ---: | --- | --- |
| A | 김민수 | 최상 | KRW 19,000 | 판매완료 | [389172764](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=389172764) |
| A | 김민수 | 최상 | KRW 22,000 | seller-profile row; current state unknown | [seller profile](https://www.aladin.co.kr/shop/usedshop/wshopitem.aspx?sc=786426) |
| S subscription | 에스엠 | 최상 | KRW 20,000 | 판매완료 | [373213316](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=373213316) |

The seller-profile A row has no individual item URL or stable offer ID, so the manifest uses a deterministic reviewer-assigned observation ID and keeps availability unknown. The S used page identifies the copy as the subscription S type but its displayed generic new-copy amounts were not adopted as an S-type retail price. No seller-specific B offer was found. These three print editions and five retail/used observations passed manifest validation, were committed to PostgreSQL, and were verified before the September source list began. No product image was copied because reuse permission is unconfirmed.

#### September 2025 print issue #268: A/B/S variants and used offers

[Aladin A-type listing](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=370423688) · [Aladin B-type listing](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=370423986) · [A/B seller profile](https://www.aladin.co.kr/shop/usedshop/wshopitem.aspx?sc=786426) · [completed used B offer](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=387006538) · [completed used S offer](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=370663107) · [Yeo Nabi cover report](https://www.xportsnews.com/article/2052061) · [Cheong-a cover report](https://biz.chosun.com/entertainment/enter_general/2025/08/26/OBUDK4MTEU6BHKGUXK3TYOWMPQ/) · [variant reference](https://www.namu.moe/w/%EB%A7%A5%EC%8B%AC%20%EC%BD%94%EB%A6%AC%EC%95%84/%EC%97%AD%EB%8C%80%20%ED%91%9C%EC%A7%80%20%EB%AA%A8%EB%8D%B8)

The September issue is MAXIM #268, themed `바람기`. Contemporaneous reports identify 여나비 and 청아 as September cover models. The variant reference maps A to 여나비 and B/S subscription to 청아; Aladin's exact S used listing independently names 청아. Aladin dates both A and B to 2025-08-22 and lists KRW 9,600 list / KRW 9,120 sale, 176 pages, and 210×297mm dimensions. A is ISBN K552030031. B's `9772233427039` value appears in the ISBN slot but is treated as an ISSN-based barcode note, not an ISBN. Both new-copy snapshots are stale and show 품절, so current availability is unknown. No cover or gallery image was copied because reuse permission is unconfirmed.

Four seller observations were captured:

| Edition | Seller | Condition | Last-observed asking price | Last-observed status | Aladin record |
| --- | --- | --- | ---: | --- | --- |
| A | 김민수 | Not shown | KRW 14,400 | seller-profile snapshot; current state unknown | [seller profile](https://www.aladin.co.kr/shop/usedshop/wshopitem.aspx?sc=786426) |
| B | 김민수 | Not shown | KRW 11,000 | seller-profile snapshot; current state unknown | [seller profile](https://www.aladin.co.kr/shop/usedshop/wshopitem.aspx?sc=786426) |
| B | 김민수 | 중 | KRW 5,100 | 판매완료; insert missing | [387006538](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=387006538) |
| S subscription | Not shown | 최상 | KRW 13,000 | 판매완료 | [370663107](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=370663107) |

The seller-profile rows have no individual item URL or stable offer ID, so the manifest uses deterministic reviewer-assigned observation IDs; their conditions and current availability remain unknown. Aladin's stale used-series snapshot reported aggregate seller inventory starting from KRW 15,000 for A and KRW 13,000 for B, and a kirinji sidebar mentioned B at KRW 13,000 without a dedicated listing URL or condition; these are retained as source context, not extra seller records. S-type new retail price, page count, dimensions, and ISBN were not verified. These three print editions and six observations passed manifest validation, were committed to PostgreSQL, and were verified before the separate YES24 digital list began.

#### September 2025 YES24 digital issue #268

[YES24 digital product page](https://www.yes24.com/product/goods/152922680)

The YES24 page lists the September 2025 MAXIM PDF with a 2025-09-01 publication date, KRW 5,500 list and sale price, DRM PDF format, 408.84MB file size, and approximately 181 pages. Its cached snapshot was crawled last month and showed 판매중 with purchase controls; current availability remains unknown. The contents name the issue theme `바람기` and list 청아, 여나비, 최세희, and 빛베리. The product contents do not explicitly assign the digital cover to one model; the work links the issue-level cover credits from the contemporaneous September print reports. No cover image was copied because reuse permission is unconfirmed. This YES24 edition and its single price observation passed validation, were committed to PostgreSQL, and were verified before the next source list.

#### August 2025 print issue #267: A/B variants and used offers

[Aladin A-type listing](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=368469856) · [Aladin B-type listing](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=368470307) · [YES24 issue contents](https://www.yes24.com/product/goods/150381839) · [contemporaneous cover report](https://www.xportsnews.com/article/2030590) · [used A offer — 책방 2034](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=385372311) · [completed A offer — kirinji](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=368728646) · [전재원 seller profile](https://www.aladin.co.kr/shop/usedshop/wshopitem.aspx?CID=0&SC=463584) · [used B offer — 김민수](https://www.aladin.co.kr/m/mproduct.aspx?ItemId=384665085&start=clickmp) · [김민수 seller profile](https://www.aladin.co.kr/shop/usedshop/wshopitem.aspx?sc=786426)

Aladin identifies the August issue as MAXIM #267 through its digital series record and lists both print types with a 2025-07-22 publication date, KRW 9,600 list price, KRW 9,120 sale price, 192 pages, and 210×297mm (A4) dimensions. A is ISBN K932030301. B displays 9772233427039 alongside ISSN 2233-4270; that ISSN-based serial barcode is noted but not stored as an ISBN. The A and B inserts name 김진아 with 소은 and 바비앙, respectively. YES24's contents and a contemporaneous report identify cheerleader 김진아 as the issue cover model and say she appears on the A/B covers. The retail snapshots show 품절 and are stale, so current availability remains unknown. No cover or gallery image was copied because reuse permission is unconfirmed.

Five seller observations were captured:

| Edition | Seller | Condition | Last-observed asking price | Status in source snapshot | Aladin record |
| --- | --- | --- | ---: | --- | --- |
| A | 책방 2034 | 중; bromide missing | KRW 24,000 | stale listing; current state unknown | [385372311](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=385372311) |
| A | kirinji | 상 | KRW 15,000 | 판매완료 | [368728646](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=368728646) |
| A | 전재원 | Not shown | KRW 25,000 | seller-profile row; current state unknown | [seller profile](https://www.aladin.co.kr/shop/usedshop/wshopitem.aspx?CID=0&SC=463584) |
| B | 김민수 | 최상 | KRW 17,000 | stale listing; current state unknown | [384665085](https://www.aladin.co.kr/m/mproduct.aspx?ItemId=384665085&start=clickmp) |
| B | 김민수 | 최상 | KRW 18,000 | seller-profile row; current state unknown | [seller profile](https://www.aladin.co.kr/shop/usedshop/wshopitem.aspx?sc=786426) |

The seller-profile rows have no individual item URL or stable offer ID, so deterministic profile keys were used. Aladin also showed an aggregate A-type used-stock floor without seller details; that aggregate is source context, not an individual offer. The A/B editions and seven new/used listing observations passed manifest validation, were committed to PostgreSQL, and were read back by the verifier before another source list began.

#### July 2025 print issue #266: A/B variants and used offers

[Aladin A-type listing](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=366537559) · [Aladin B-type listing](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=366537750) · [contemporaneous cover report](https://m.news.nate.com/view/20250627n21433) · [completed A offer — diskplan](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=388704653) · [김민수 seller inventory](https://www.aladin.co.kr/shop/usedshop/wshopitem.aspx?sc=786426) · [Aladin July used-series snapshot](https://www.aladin.co.kr/m/mseriesitem_used.aspx?srid=1269369)

Aladin lists both July 2025 print types with a 2025-06-23 publication date, KRW 8,900 list price, KRW 8,450 sale price, 192 pages, and 210×297mm (A4) dimensions. A lists serial identifier K642030987. B displays barcode 9772233427039 alongside ISSN 2233-4270; the ISSN-based barcode is not stored as an ISBN. Both variants list a special bromide featuring Miss Maxim E다연 and 쥬. A contemporaneous report identifies E다연 as the July issue cover model. The A page gives a sold-out confirmation date of 2025-07-29; the B page snapshot also shows the new copy sold out. Both retailer snapshots are stale, so current availability is unknown. No cover or gallery image was copied because reuse permission is unconfirmed.

| Edition | Offer | Condition | Last-observed price | Status in source snapshot | Aladin record |
| --- | --- | --- | ---: | --- | --- |
| A | diskplan | 최상 | KRW 15,000 | 판매완료 | [388704653](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=388704653) |
| A | 김민수 seller inventory row | Not shown | KRW 14,000 | stale profile/list snapshot; current state unknown | [seller inventory](https://www.aladin.co.kr/shop/usedshop/wshopitem.aspx?sc=786426) |

Aladin's B-type used-series row reports two offers and an aggregate floor of KRW 17,000 but exposes no seller-specific item in the reviewed capture. That aggregate is not stored as an individual listing. The two print editions and four retail/used observations passed manifest validation, were committed to PostgreSQL, and were verified before collection continued.

#### June 2025 print issue #265: A/B variants and one used seller row

[Aladin A-type listing](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=364595913) · [Aladin B-type listing](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=364596043) · [official MAXIM #265 announcement](https://www.youtube.com/watch?v=Si8Zl7u5ZTg) · [contemporaneous cover report](https://www.msnews.co.kr/news/articleView.html?idxno=794356) · [Aladin A-type used inventory row](https://www.aladin.co.kr/m/mproduct.aspx?ItemId=361927961) · [Aladin June series snapshot](https://www.aladin.co.kr/shop/common/wseriesitem.aspx?SRID=1261798)

Aladin lists both June 2025 print variants with a 2025-05-21 publication date, KRW 8,900 list price, KRW 8,450 sale price, 192 pages, 210×297mm (A4), and 518g. A is ISBN K112039717; B is ISBN K222039717. Their special bromide features Miss Maxim 첼설아, 조아, and 에일리. The official MAXIM announcement identifies the issue as #265, and a contemporaneous report identifies 첼설아 as the June issue cover model. The A page gives a sold-out confirmation date of 2025-06-26; the B page marks distribution ended and the new copy sold out. Both snapshots are stale, so current availability is unknown. No cover or gallery image was copied because reuse permission is unconfirmed.

| Edition | Offer | Condition | Last-observed price | Status in source snapshot | Aladin record |
| --- | --- | --- | ---: | --- | --- |
| A | kirinji seller inventory row | Not shown | KRW 13,000 | stale source row; current state unknown | [inventory context](https://www.aladin.co.kr/m/mproduct.aspx?ItemId=361927961) |

The A-type product page reports one used offer at KRW 13,000, and the seller inventory panel names kirinji at the same price. Aladin exposed no separate offer ID, individual seller-item URL, condition, or shipping detail; the manifest uses a deterministic reviewer-assigned source-row key. The used-listing search also surfaced generic June titles with 2024-06-01 publication metadata; those were not linked to the 2025 #265 issue. The two editions and three retail/seller observations passed manifest validation, were committed to PostgreSQL, and were read back by the verifier before collection continued.

#### May 2025 print issue #264: A type and subscription S type

[Aladin A-type product page](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=362927566) · [Aladin A-type used inventory](https://www.aladin.co.kr/shop/UsedShop/wuseditemall.aspx?ItemId=362927566&start=newproduct) · [Aladin S-type used listing](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=363415774) · [Aladin May series page](https://www.aladin.co.kr/shop/common/wseriesitem.aspx?SRID=1255480) · [YES24 May issue page](https://www.yes24.com/product/goods/146279404) · [publisher's May cover video](https://www.youtube.com/watch?v=yjefuyfsZHg) · [issue-number cross-reference](https://web.joongna.com/product/228570265)

Aladin's May series page lists one new A-type print edition. Its product page gives a 2025-04-23 publication date, KRW 8,900 list price, KRW 8,450 sale price, 192 pages, 210×297mm (A4), 518g, ISBN K912038145, and ISSN 2233-4270. The included bromide features 장은비 and 최세희; the YES24 issue page and publisher video identify 장은비 as the May cover model. The A product snapshot marks the new copy sold out and lists a confirmation date of 2025-05-26. Current availability is unknown. That newer snapshot reports eight used offers at an aggregate floor of KRW 10,000; the aggregate is not imported as a seller listing.

The separate A-type seller-inventory page, crawled about seven months before 2026-10-20, displays five seller rows. Prices and stock status are last-observed; all five are stored with unknown current availability. The page shows purchase controls in its old snapshot but exposes no individual seller-item IDs, so deterministic row keys are used.

| Edition | Seller row | Condition | Last-observed price | Shipping in snapshot | Status in source snapshot |
| --- | --- | --- | ---: | --- | --- |
| A | 김민수 | 상 | KRW 8,500 | KRW 3,500 standard / KRW 2,400 half-price parcel | stale; current state unknown |
| A | kirinji | 상 | KRW 13,000 | KRW 3,500 standard / KRW 2,400 half-price parcel | stale; current state unknown |
| A | diskplan | 최상 | KRW 15,000 | KRW 3,500 standard / KRW 2,400 half-price parcel | stale; current state unknown |
| A | Danielle (row 4) | 최상 | KRW 30,000 | KRW 3,500 standard | stale; current state unknown |
| A | Danielle (row 5) | 최상 | KRW 30,000 | KRW 3,500 standard | stale; current state unknown |

The used-inventory page reports five seller offers; its two Danielle rows have the same displayed condition and price and are retained as separate source rows without separate item IDs. The exact [S-type used offer](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=363415774) identifies a May 2025 subscription issue featuring YouTuber 장은비, seller 에스엠, condition `최상`, price KRW 17,000, and status `판매완료`. Its generic publisher date field says 2024-01-01, conflicting with the explicit May 2025 item title. The manifest records the S type separately, uses the A issue's 2025-04-23 date, and retains the source conflict. The two physical editions and seven retail/seller observations passed manifest validation, were committed to PostgreSQL, and were read back by the verifier before collection continued.

#### January 2026 print issue #272 and seller offers

[Aladin product page](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=382050694) · [Aladin used-inventory page](https://www.aladin.co.kr/shop/UsedShop/wuseditemall.aspx?ItemId=382050694) · [official MAXIM cover announcement](https://www.youtube.com/watch?v=08foa4rTtBE) · [contemporaneous cover report](https://biz.chosun.com/entertainment/tv/2025/12/23/GZSGKZRSGMYGCNJXMM3TMOBRMI/) · [YES24 A-type review/product reference](https://m.yes24.com/Goods/Review/170475321) · [Coupang A-type listing reference](https://www.coupang.com/vp/products/9273375586)

Aladin lists the physical issue under the generic title `맥심 Maxim 2026.1`, with publication date 2025-12-23, 176 pages, dimensions 210×297mm, ISBN K342034812, list price KRW 9,600, and selling price KRW 9,120. Its snapshot shows `품절` and a last stock-check date of 2026-01-26; availability is stored as unknown and the sale amount as last-observed. Kyobo's January issue page gives the physical publication date as 2025-12-26, so the manifest preserves Aladin's retailer-specific date. MAXIM's official announcement and the December 23 cover report identify 조예린 as the issue cover model. Aladin does not state A/B/S in its product title; YES24's review URL and Coupang's listing independently show that an A-type product existed, but they do not identify the generic Aladin record as that exact variant. The database edition therefore keeps the cover variant unspecified rather than inferring a match.

The [Aladin used-inventory snapshot](https://www.aladin.co.kr/shop/UsedShop/wuseditemall.aspx?ItemId=382050694), crawled about two months before 2026-10-20, lists three seller-specific copies. The item-detail routes returned cache misses; seller-row prices and conditions are retained as last-observed, with availability unknown.

| Listing | Seller | Condition | Last-observed asking price | Shipping | Exact Aladin item |
| --- | --- | --- | ---: | --- | --- |
| Used | nowitzki41 | 상 | KRW 10,000 | KRW 3,500 standard / KRW 2,400 half-price parcel | [384541930](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=384541930) |
| Used | kirinji | 상 | KRW 15,000 | KRW 3,500 standard / KRW 2,400 half-price parcel | [384342741](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=384342741) |
| Used | diskplan | 최상 | KRW 20,000 | KRW 3,500 standard / KRW 2,400 half-price parcel | [396511016](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=396511016) |

Aladin's page exposes the [cover image](https://image.aladin.co.kr/product/38205/6/cover500/k342034812_1.jpg) and one [gallery image](https://image.aladin.co.kr/product/38205/6/letslook/K342034812_f.jpg). The image fetches returned cache misses; the URLs are kept here as source leads only. No image was copied because reuse permission is unconfirmed. All four January Aladin listing rows were added to the manifest, validated, committed to PostgreSQL, and verified before another source list was opened.

### Additional MAXIM B-cut captures: August–September 2026

The YES24 eBook new-products category lists these as separate, model-named MAXIM B-cut PDFs, each at KRW 6,500 list and selling price, with cart and purchase controls. The category snapshot was crawled last week; exact detail routes did not yield usable product content in this review, so availability is `unknown`, the price is last-observed, and page counts/gallery images are not claimed. All are digital and have no used-market offer.

| YES24 item | Model | Published | Last-observed list / selling price |
| --- | --- | --- | ---: |
| [BIKINI — 심연](https://www.yes24.com/product/goods/196690200) | 심연 | 2026-09 (month) | KRW 6,500 / 6,500 |
| [BIKINI — 향지](https://www.yes24.com/product/goods/196567432) | 향지 | 2026-09 (month) | KRW 6,500 / 6,500 |
| [BIKINI — 박보름](https://www.yes24.com/product/goods/196505862) | 박보름 | 2026-09 (month) | KRW 6,500 / 6,500 |
| [BIKINI — 탑체리](https://www.yes24.com/product/goods/196332577) | 탑체리 | 2026-09 (month) | KRW 6,500 / 6,500 |
| [BIKINI — 주빈](https://www.yes24.com/product/goods/196258886) | 주빈 | 2026-09 (month) | KRW 6,500 / 6,500 |
| [BIKINI — 슈](https://www.yes24.com/product/goods/196099001) | 슈 | 2026-09 (month) | KRW 6,500 / 6,500 |
| [BIKINI — 박서이](https://www.yes24.com/product/goods/195985443) | 박서이 | 2026-09 (month) | KRW 6,500 / 6,500 |
| [BIKINI — 키라](https://www.yes24.com/product/goods/195835098) | 키라 | 2026-09 (month) | KRW 6,500 / 6,500 |
| [BIKINI — 소이](https://www.yes24.com/product/goods/195743417) | 소이 | 2026-08 (month) | KRW 6,500 / 6,500 |
| [BIKINI — 예나비](https://www.yes24.com/product/goods/195564322) | 예나비 | 2026-08 (month) | KRW 6,500 / 6,500 |
| [BIKINI — 타샤](https://www.yes24.com/product/goods/195423580) | 타샤 | 2026-08 (month) | KRW 6,500 / 6,500 |
| [BIKINI — 수지](https://www.yes24.com/product/goods/195374401) | 수지 | 2026-08 (month) | KRW 6,500 / 6,500 |
| [BIKINI — 슬이](https://www.yes24.com/product/goods/195266553) | 슬이 | 2026-08 (month) | KRW 6,500 / 6,500 |
| [BIKINI — 핫소망](https://www.yes24.com/product/goods/195229803) | 핫소망 | 2026-08 (month) | KRW 6,500 / 6,500 |
| [BIKINI — 김연지](https://www.yes24.com/product/goods/195224106) | 김연지 | 2026-08 (month) | KRW 6,500 / 6,500 |
| [BIKINI — 묘정](https://www.yes24.com/product/goods/195131430) | 묘정 | 2026-08 (month) | KRW 6,500 / 6,500 |

### Additional MAXIM B-cut captures: April–November 2025 and April 2026

The [YES24 MAXIM partner-shop listing](https://www.yes24.com/Product/PartnerShop/284442) names each model and pictorial, shows the publication month, and lists the list and selling prices below. Its page was crawled about three weeks before this review. Detail-page follow-ups returned cache misses or an adult-login check, so availability is `unknown` and these are last-observed prices. The rows identify PDF eBooks; page counts and gallery images were not verified. There is no used-market offer for these digital editions.

| YES24 item | Model | Published | Last-observed list / selling price |
| --- | --- | --- | ---: |
| [Pygmalionism #1 — 이연우](https://www.yes24.com/product/goods/146014884) | 이연우 | 2025-04 (month) | KRW 5,900 / 5,900 |
| [Office wife #1 — 바비앙](https://www.yes24.com/product/goods/166468141) | 바비앙 | 2025-11 (month) | KRW 7,900 / 7,900 |
| [란제리 — 은지](https://www.yes24.com/product/goods/167425315) | 은지 | 2025-11 (month) | KRW 4,900 / 4,900 |
| [비키니 라운드 — 유디](https://www.yes24.com/product/goods/147017456) | 유디 | 2025-05 (month) | KRW 4,500 / 4,500 |
| [남의 남자 — 김갑주](https://www.yes24.com/product/goods/166279483) | 김갑주 | 2025-11 (month) | KRW 7,500 / 7,500 |
| [코스튬 — 김갑주](https://www.yes24.com/product/goods/152616255) | 김갑주 | 2025-08 (month) | KRW 4,500 / 4,500 |
| [란제리 — 에일리](https://www.yes24.com/product/goods/167492098) | 에일리 | 2025-11 (month) | KRW 4,900 / 4,900 |
| [Wet stocking #2 — 은지](https://www.yes24.com/product/goods/185779832) | 은지 | 2026-04 (month) | KRW 6,900 / 6,900 |

The titles and model names are retailer listing credits. No product image was copied because reuse permission is unconfirmed; manifest cover and gallery fields remain blank.

### Additional MAXIM issue capture: December 2018 digital issue — 김소희

[YES24 product detail](https://www.yes24.com/product/goods/67295629)

YES24 identifies **맥심 MAXIM 2018년 12월호** as a DRM PDF published 2018-12-05, with a file size of 73.49 MB. Its contents explicitly identify Miss Maxim 김소희 in the `COVER` feature. The page snapshot is marked as crawled last month; it displayed list and selling prices of KRW 3,800 and `판매중` with purchase controls. Keep KRW 3,800 as last-observed and availability as `unknown` pending a fresh page check. The issue is a `magazine_issue`, not a standalone photobook.

The product page links its cover at [YES24's image asset](https://image.yes24.com/goods/67295629/XL), but the asset fetch returned a cache miss. No separate product-gallery sample was verified. The source image URL is provenance only; no image was copied because reuse permission is unconfirmed.

### Additional MAXIM B-cut captures: April–May 2026 — 조이온

The [YES24 publisher search listing](https://www.yes24.com/Product/Search?company=%EC%A1%B0%EC%9D%B4%EB%AF%B8%EB%94%94%EC%96%B4&domain=ALL&query=%25EC%25A1%25B0%25EC%259D%B4%25EB%25AF%25B8%25EB%2594%2594%25EC%2596%25B4) showed these model-specific PDFs at the dates and regular prices below. That listing snapshot was crawled about three weeks before this review. The product-detail routes returned cache misses, so prices are last-observed, availability is `unknown`, and page counts and gallery imagery are unverified.

| YES24 item | Model | Published | Last-observed list / selling price |
| --- | --- | --- | ---: |
| [Costume — 조이온](https://www.yes24.com/product/goods/188917812) | 조이온 | 2026-04 (month) | KRW 4,500 / 4,500 |
| [Lingerie — 조이온](https://www.yes24.com/product/goods/190305498) | 조이온 | 2026-05 (month) | KRW 7,900 / 7,900 |

No image was copied; the image fields remain blank pending reuse permission.

### MAXIM October 2026 print variants: A staged; B documented

The YES24 A- and B-type product pages were checked around 14:42 SGT on 2026-10-20. Each page specifies a 2026-09-24 publication date, 176 pages, 210×297×15mm size, list price KRW 9,600, sale price KRW 9,120, and limited-sale purchase controls. These are physical magazine_issue editions for the October issue. The new-copy price was captured; no seller-specific used offer was verified.

| Variant | YES24 item | Published | List / selling price | Model-credit handling |
| --- | --- | --- | ---: | --- |
| A type | [맥심 MAXIM A형](https://www.yes24.com/product/goods/196908942) | 2026-09-24 | KRW 9,600 / 9,120 | The product page identifies the variant and names 쥬/조아 for its bromide. The October issue cover credit for 쥬 is independently stated in [Kyobo's issue contents](https://ebook-product.kyobobook.co.kr/dig/epd/sam/E000013637393) and a [contemporaneous cover report](https://m.fortune.ajunews.com/bbs/view/news/S1N17/5602001); the manifest retains this at issue level. |
| B type | [맥심 MAXIM B형](https://www.yes24.com/product/goods/196908938) | 2026-09-24 | KRW 9,600 / 9,120 | The product page names 조아/유디 for the bromide, not as cover models. A separate [report identifies 유디 on a limited-edition cover](https://m.fortune.ajunews.com/bbs/view/news/S1N18/5603407), but does not tie that cover to this YES24 B-type product. This variant stays out of the import manifest until its cover credit is verified. |

The A-type record reuses the existing October magazine_issue work and is staged as physical edition korea-maxim-2026-10-joo-print-a-yes24. YES24's image links resolve to the A cover https://image.yes24.com/goods/196908942/XL and the B cover https://image.yes24.com/goods/196908938/XL. Each page also links one 상세 이미지 1 asset (https://image.yes24.com/momo/TopCate7203/MidCate4/720230347.jpg for A; https://image.yes24.com/momo/TopCate7203/MidCate4/720230330.jpg for B); both detail-image fetches returned cache misses, so their contents were not verified. These URLs are provenance only. No image was copied because reuse permission is unconfirmed.

### Additional MAXIM B-cut PDFs: April–May 2026 listings

The [MAXIM publisher-shop new-products page](https://www.yes24.com/Product/PartnerShop/ProductList?entrNo=284442&pageType=NEW) lists the product titles, model credits, and regular prices. YES24's [April category listing for Snow White Gone Wild](https://www.yes24.com/24/category/SpecialDisplay/017001036?AO=3&PageNumber=8&ParamSortTp=04&SortKind=PR&SortOption=07&TabNo=3), [April listing for Pit-a-pat #3](https://www.yes24.com/24/category/SpecialDisplay/017001036?AO=3&GS=03&PageNumber=1&ParamSortTp=07&SortKind=PR&SortOption=07&TabNo=3), [April listing for Hyerin](https://www.yes24.com/24/category/SpecialDisplay/017001036?AO=4&PageNumber=7&ParamSortTp=04&SortKind=PR&SortOption=07&TabNo=3), and [April listing for Shape of Perfection](https://www.yes24.com/24/category/SpecialDisplay/017001036?AO=3&PageNumber=8&ParamSortTp=04&SortKind=PR&SortOption=07&TabNo=3) show month-level publication dates, list/selling prices, and cart/purchase controls. The [May listing for the four Costume titles](https://www.yes24.com/24/category/SpecialDisplay/017001036?AO=3&GS=03&PageNumber=2&ParamSortTp=04&SortKind=PR&SortOption=05&TabNo=3), [May listing for Jina Up and Living Together](https://www.yes24.com/24/category/SpecialDisplay/017001036?AO=4&GS=03&PageNumber=1&ParamSortTp=07&SortKind=PR&SortOption=07&TabNo=3), and [May listing for Park Jiyeon's pictorial](https://www.yes24.com/24/category/SpecialDisplay/017001036?AO=4&PageNumber=6&ParamSortTp=04&SortKind=PR&SortOption=07&TabNo=3) show the corresponding dates and prices. Those category snapshots were crawled about one to two months before this review. Product-detail routes returned cache misses or an adult-check redirect; current availability could not be confirmed. The figures below are last-observed regular list/selling prices, not verified live quotes. These digital PDFs have no used-copy offers.

| YES24 item | Model | Published | Last-observed list / selling price |
| --- | --- | --- | ---: |
| [Living together #1](https://www.yes24.com/product/goods/189420973) | 장은비 | 2026-05 (month) | KRW 9,900 / 9,900 |
| [농락당하는 여자사람친구 #1](https://www.yes24.com/product/goods/189411825) | 박지연 | 2026-05 (month) | KRW 7,500 / 7,500 |
| [Jina up! #1](https://www.yes24.com/product/goods/189199669) | 김진아 | 2026-05 (month) | KRW 9,900 / 9,900 |
| [Costume](https://www.yes24.com/product/goods/189173480) | 채솔 | 2026-05 (month) | KRW 4,500 / 4,500 |
| [Costume](https://www.yes24.com/product/goods/189110417) | 리리 | 2026-05 (month) | KRW 4,500 / 4,500 |
| [Costume](https://www.yes24.com/product/goods/189080618) | 퓨리 | 2026-05 (month) | KRW 4,500 / 4,500 |
| [Costume](https://www.yes24.com/product/goods/188994445) | 섹밍 | 2026-05 (month) | KRW 4,500 / 4,500 |
| [Snow white gone wild #2](https://www.yes24.com/product/goods/188851025) | 김설화 | 2026-04 (month) | KRW 8,900 / 8,900 |
| [pit-a-pat #3](https://www.yes24.com/product/goods/188757107) | 바비앙 | 2026-04 (month) | KRW 9,900 / 9,900 |
| [일상육덕포인트](https://www.yes24.com/product/goods/188706826) | 혜린 | 2026-04 (month) | KRW 8,500 / 8,500 |
| [Shape of Perfection](https://www.yes24.com/product/goods/187496978) | 이유진 | 2026-04 (month) | KRW 7,900 / 7,900 |

All 11 records are staged as `photobook` digital PDF editions with month precision, exact product IDs, and the explicitly credited model. Availability is `unknown` in the manifest because the item pages could not be freshly verified. The text listings did not expose verifiable cover or gallery images in these captures, and image reuse permission was not established; image fields remain blank.

### Additional MAXIM B-cut PDFs: June–July 2026 listings

The [MAXIM publisher-shop listing](https://www.yes24.com/Product/PartnerShop/ProductList?entrNo=284442&pageType=NEW) supplies the titles, model credits, and regular prices. YES24's category snapshots show the publication month and the same list/selling amount for [Get wet](https://www.yes24.com/24/category/SpecialDisplay/017001036?AO=0&GS=03&PageNumber=1&ParamSortTp=04&SortKind=PR&SortOption=07&TabNo=3), [Christmas and Final](https://www.yes24.com/24/category/SpecialDisplay/017001036?AO=4&FetchSize=40&GS=03&PageNumber=1&ParamSortTp=04&SortKind=PR&SortOption=07&TabNo=3), [Lookbook #1](https://www.yes24.com/24/category/SpecialDisplay/017001036?AO=4&FetchSize=80&GS=03&PageNumber=1&ParamSortTp=04&SortKind=PR&SortOption=07&TabNo=3), [Kiss of darkness](https://www.yes24.com/24/category/SpecialDisplay/017001036?AO=4&PageNumber=2&ParamSortTp=04&SortKind=PR&SortOption=07&TabNo=3), and [Scoop me, paparazzi](https://www.yes24.com/24/category/SpecialDisplay/017001036?AO=4&GS=06&PageNumber=1&ParamSortTp=04&SortKind=PR&SortOption=07&TabNo=3). The [publisher-shop page](https://www.yes24.com/Product/PartnerShop/284442) also lists Lingerie — 애순이 with July 2026 and its price. These snapshots were crawled about one to two months before this review. Prices are last-observed regular list/selling prices; exact product pages could not be freshly verified, so availability is unknown. These digital editions have no used-copy offers.

| YES24 item | Model | Published | Last-observed list / selling price |
| --- | --- | --- | ---: |
| [Get wet [검정젤리]](https://www.yes24.com/product/goods/194622252) | 보라 | 2026-07 (month) | KRW 8,900 / 8,900 |
| [Kiss of darkness [RED]](https://www.yes24.com/product/goods/194339263) | 그린 | 2026-07 (month) | KRW 8,900 / 8,900 |
| [Lookbook #1](https://www.yes24.com/product/goods/194260345) | 박지연 | 2026-07 (month) | KRW 7,900 / 7,900 |
| [Christmas](https://www.yes24.com/product/goods/194167902) | 김은지 | 2026-07 (month) | KRW 9,900 / 9,900 |
| [Final](https://www.yes24.com/product/goods/194005873) | 윤영서 | 2026-07 (month) | KRW 9,900 / 9,900 |
| [Final](https://www.yes24.com/product/goods/193978544) | 애순이 | 2026-07 (month) | KRW 9,900 / 9,900 |
| [Lingerie](https://www.yes24.com/product/goods/193171478) | 애순이 | 2026-07 (month) | KRW 7,900 / 7,900 |
| [Scoop me, paparazzi](https://www.yes24.com/product/goods/191890210) | 이채하 | 2026-06 (month) | KRW 8,900 / 8,900 |

These eight items are staged as `photobook` digital PDF editions with month precision and title-based model credits. Their `availability` is `unknown`; no cover or gallery image was verified and no image was copied.

### Standalone photobook: LISONG in MOROCCO

[YES24 product detail](https://www.yes24.com/product/goods/119542450)

The live product page identifies 리송 as the model/author and 장태규 as photographer. The print edition was published 2023-04-10 by 범비범그루브, with 204 pages and dimensions 220×300×14mm. The page showed a used copy with list price KRW 50,000 and selling price KRW 44,000, condition `최상`, seller-shipped, and KRW 2,500 domestic shipping; purchase controls were present at the 2026-10-20 15:15 SGT capture. This observation is for the used offer. The page separately links a new copy at KRW 45,000 (YES24 item 118534014). No image was copied because reuse permission is unconfirmed.

The separate [new-copy listing](https://www.yes24.com/product/goods/118534014) showed list price KRW 50,000 and selling price KRW 45,000 in a page snapshot crawled last year. The live used-product page linked this item at KRW 45,000 during the 15:15 SGT capture. It is stored as a separate listing on the same edition; availability remains unknown because the new-copy product page could not be freshly refreshed.

### MAXIM September 2026 A-type print issue

[YES24 A-type product page](https://www.yes24.com/product/goods/195411513) · [Kyobo September issue contents](https://ebook-product.kyobobook.co.kr/dig/epd/sam/E000013514799) · [September cover report](https://www.specialtimes.co.kr/news/articleView.html?idxno=453503)

The YES24 product page lists the A-type print issue's publication date as 2026-08-25, 176 pages, dimensions 210×297×15mm, list price KRW 9,600, and selling price KRW 9,120. Its last-crawled snapshot showed `판매중 | 한정판매`; the live refresh returned an exception page, so the manifest records availability as unknown and keeps those amounts as last-observed. The Kyobo contents and September cover report identify 미스맥심 뮤아 on the issue cover; YES24's B-type page plus a contemporaneous report identify 윤영서 on the B cover. Assigning 뮤아 to this A-type is an inference from the issue's A/B pairing, since the A-type page names only the bonus bromide models. No cover or gallery image was copied because reuse permission is unconfirmed.

### MAXIM August 2026 A-type print issue

[YES24 A-type product page](https://www.yes24.com/product/goods/194312142) · [YES24 B-type product page](https://www.yes24.com/product/goods/194312077) · [YES24 August digital contents](https://www.yes24.com/product/goods/194622253) · [Xports cover-model interview](https://www.xportsnews.com/article/2186895)

The A-type product page lists publication date 2026-07-23, 176 pages, dimensions 210×297×15mm, list price KRW 9,600, and selling price KRW 9,120. The search snapshot was crawled about two months before 2026-10-20 and showed `판매중 | 한정판매`; the manifest retains availability as unknown and the price as last-observed. The August digital issue and an interview identify 치어리더 서여진 as the month's cover model, but the A-type product page does not name its cover model, so assigning 서여진 to this print edition is an inference. The B-type item has the same date, prices, and bromide names; its model-to-cover mapping remains unresolved and it was not imported. No cover or gallery image was copied because reuse permission is unconfirmed.

### MAXIM July 2026 A-type print issue

[YES24 A-type product page](https://www.yes24.com/product/goods/192563526) · [YES24 July digital issue](https://www.yes24.com/product/goods/192991630) · [Kyobo July issue contents](https://ebook-product.kyobobook.co.kr/dig/epd/ebook/E000013195770)

The A-type product page lists publication date 2026-06-29, 176 pages, dimensions 210×297×15mm, list price KRW 9,600, and selling price KRW 9,120. The snapshot was crawled about three months before 2026-10-20; the manifest records availability as unknown and the price as last-observed. Kyobo's July issue contents explicitly credit 바비앙 as cover model. The A-type page names 바비앙 and 채솔 for its bromide but does not identify the cover, so assigning 바비앙 to this print variant remains an inference. No image was copied because reuse permission is unconfirmed.

### MAXIM June 2026 A- and B-type print issues

[YES24 A-type product page](https://www.yes24.com/product/goods/189764231) · [YES24 B-type product page](https://www.yes24.com/product/goods/189764229) · [MAXIM publisher issue list](https://www.maximkorea.net/magdb/_ajax_magdb_list.php) · [SportsTimes cover report](https://www.thesportstimes.co.kr/news/articleView.html?idxno=372949)

YES24 lists each print variant with publication date 2026-05-23, 176 pages, dimensions 210×297×15mm, list price KRW 9,600, and selling price KRW 9,120. The A and B items have separate ISBNs, 9772233427008 and 9772233427039. The snapshots were crawled about four months before 2026-10-20, so both listing statuses are stored as unknown and the prices as last-observed. MAXIM's public issue list labels both the June A and B variants as the 김우현 issue; a contemporaneous SportsTimes report identifies 김우현 as the June cover model. No used-copy offer was verified. No cover or gallery image was copied because image reuse permission is unconfirmed.

### MAXIM May 2026 A- and B-type print issues

[YES24 A-type product page](https://www.yes24.com/product/goods/187970269) · [YES24 B-type product page](https://www.yes24.com/product/goods/187970081) · [Kyobo May issue contents](https://ebook-product.kyobobook.co.kr/dig/epd/ebook/E000012932768) · [MAXIM publisher issue list](https://www.maximkorea.net/magdb/_ajax_magdb_list.php)

YES24's indexed product details list publication date 2026-04-23, 176 pages, dimensions 210×297×15mm, list price KRW 9,600, and selling price KRW 9,120 for each variant. The A and B listings have separate item IDs and ISBNs, 9772233427008 and 9772233427039. The indexed snapshots were crawled about five months before 2026-10-20; direct page fetches did not return the product pages, so availability is unknown and prices are last-observed. Kyobo's issue contents explicitly credit 미스맥심 채솔 as the May issue cover model. YES24 lists 제아/채솔 as bonus models but does not give a variant-specific cover credit. No used-copy offer was verified. No cover or gallery image was copied because image reuse permission is unconfirmed.

### MAXIM April 2026 A- and B-type print issues

[Aladin A-type product page](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=388734987) · [Aladin B-type product page](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=388734744) · [Aladin used B-type offer](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=403071639) · [MAXIM publisher issue list](https://www.maximkorea.net/magdb/_ajax_magdb_list.php) · [Kim Na-yeon cover report](https://news.nate.com/view/20260323n18368)

Both Aladin retail pages list publication date 2026-03-23, 176 pages, dimensions 210×297mm, list price KRW 9,600, and selling price KRW 9,120. The A page gives ISBN K902137101 and the B page gives ISBN K522137100. Their snapshots display `품절`; the pages were last crawled about one to two months before 2026-10-20, so availability is recorded as unknown and prices as last-observed. MAXIM's public issue list and a contemporaneous report credit 치어리더 김나연 as the April issue cover model; the Aladin product text names the variant and bonus models but does not map the exact cover art to A or B.

The separate [used B-type offer](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=403071639) showed seller `diskplan`, condition `최상`, asking price KRW 15,000, standard parcel shipping KRW 3,500, and half-price parcel shipping KRW 2,400. Its seller snapshot was crawled about three weeks before 2026-10-20; the manifest keeps availability unknown. This is a used listing attached to the same B-type print edition. No cover or gallery image was copied because image reuse permission is unconfirmed.

### MAXIM March 2026 A- and B-type print issues

[Aladin A-type product page](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=386994077) · [Aladin B-type product page](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=386993826) · [Aladin used A-type offer](https://www.aladin.co.kr/m/mproduct.aspx?ItemId=400841601&start=clickmp) · [Aladin seller profile with B-type offer](https://www.aladin.co.kr/shop/usedshop/wshopitem.aspx?sc=786426) · [MAXIM publisher issue list](https://www.maximkorea.net/magdb/_ajax_magdb_list.php) · [Kyobo March digital contents](https://ebook-product.kyobobook.co.kr/dig/epd/ebook/E000012645261)

Aladin lists both print variants with publication date 2026-02-23, 176 pages, dimensions 210×297mm, list price KRW 9,600, and selling price KRW 9,120. The A-type ISBN is K692136822 and the B-type ISBN is 9772233427039. The source snapshots display `품절` and are not fresh enough to establish current availability, so the database stores status as unknown and the amounts as last-observed. MAXIM identifies this as issue #274 and credits 김도아 at issue level. Aladin names 김도아/손예은 as A-type bromide subjects and 김도아/바비앙 for B-type; it does not identify the exact cover art for either retail variant.

The [specific used A-type offer](https://www.aladin.co.kr/m/mproduct.aspx?ItemId=400841601&start=clickmp) lists seller 김민수, condition `최상`, asking price KRW 13,000, standard parcel KRW 3,500, remote-area parcel KRW 6,200, and half-price parcel KRW 2,400. The [seller profile](https://www.aladin.co.kr/shop/usedshop/wshopitem.aspx?sc=786426) also lists the B-type in condition `최상` at KRW 17,000, with standard parcel KRW 3,500 or half-price parcel KRW 2,400. The profile page did not expose a separate B offer URL in the reviewed capture, so the manifest uses a reviewer-assigned source key for that row and links to the seller profile. A separate [Aladin used-series snapshot](https://www.aladin.co.kr/shop/common/wseriesitem_used.aspx?SRID=1327232) shows multiple A/B seller offers and lower aggregate price floors; those aggregate totals are not imported as individual seller listings. All four product and seller rows are in PostgreSQL before the next source list begins. No cover or gallery image was copied because image reuse permission is unconfirmed.

### MAXIM January 2025 A-, B-, and C-type print issues

[Aladin A-type product](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=354331492) · [Aladin B-type product](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=354331638) · [Aladin C-type product](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=354331864) · [Aladin A-type used inventory](https://www.aladin.co.kr/shop/usedshop/wuseditemall.aspx?itemid=354331492&tabtype=0) · [Xports cover-model report](https://www.xportsnews.com/article/1945868)

Aladin lists all three print variants with publication date 2024-12-23, 192 pages, A4 dimensions (210×297mm), 518g, list price KRW 8,900, and selling price KRW 8,450. The A-type page lists ISBN K232035733. The B- and C-type pages display 9772233427039 and 9772233427046 alongside ISSN 2233-4270; those serial barcodes are not stored as ISBNs. The A and B product snapshots were crawled about 1.4 and 1.2 years before 2026-10-20; the C page was crawled about three weeks before. A and C snapshots display sold-out state, but current availability for all three editions remains unknown. The A product page's aggregate used-price floor of KRW 19,000 is source context, not an individual seller offer.

The older [A-type seller inventory snapshot](https://www.aladin.co.kr/shop/usedshop/wuseditemall.aspx?itemid=354331492&tabtype=0) lists seller kirinji, condition 상, at KRW 20,000, with parcel shipping KRW 3,500 or half-price parcel shipping KRW 2,400. It is retained as one seller-row observation with unknown current availability. Xports identifies creator 갓세희 as the January cover model. The three physical editions and four listings were committed to PostgreSQL and verified before collection continued. No product image was copied; reuse permission is unconfirmed, so cover and gallery fields remain blank.

### MAXIM December 2024 A- and B-type print issues

[Aladin A-type product](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=352713997) · [Aladin B-type product](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=352714285) · [A-type used item](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=388750222) · [A-type seller inventory](https://www.aladin.co.kr/shop/UsedShop/wuseditemall.aspx?ItemId=352713997&start=newproduct) · [December cover-model report](https://www.specialtimes.co.kr/news/articleView.html?idxno=412995)

Aladin lists A and B variants of MAXIM December 2024, issue #259. The A page gives publication date 2024-11-01 and ISBN K932934459; the B page gives 2024-11-21 and displays the ISSN-based code 9772233427039, which is not stored as an ISBN. Both have 192 pages, A4 dimensions (210×297mm), weight 518g, list price KRW 8,900, and selling price KRW 8,450. The snapshots were crawled about five and four months before 2026-10-20 and show sold-out state, so current new-copy availability is unknown. SpecialTimes reports 쥬 as the December cover model.

The exact [used A-type listing](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=388750222) names seller 책방 2034, condition 중, price KRW 20,000, parcel shipping KRW 3,500, remote-area parcel KRW 5,000, and half-price parcel KRW 2,400. It is marked 판매완료 in a snapshot crawled about three months before 2026-10-20.

Aladin's B-type product page links the C-type series item at [Aladin item 352714443](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=352714443), but that exact page route returned a cache miss. A reseller page describes the A/B covers as 쥬 and the C cover as Donald Trump. The C variant is therefore left outside this Korean-model cover batch until its product details and variant cover can be confirmed. No cover image was copied because reuse permission is unconfirmed; image fields remain blank. The two A/B editions and three listing observations were committed to PostgreSQL and verified before the next source list.

### MAXIM November 2024 A-type print issue

[Aladin product page](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=350518501) · [Aladin used inventory](https://www.aladin.co.kr/shop/UsedShop/wuseditemall.aspx?ItemId=350518501&start=newproduct) · [뽀구미 cover-model report](https://www.stardailynews.co.kr/news/articleView.html?idxno=463122)

Aladin's product title is 맥심 Maxim 2024.11 and its exact product page lists publication date 2024-10-02, 192 pages, A4 dimensions (210×297mm), 518g, serial barcode 9772233427008, and ISSN 2233-4270. The barcode is ISSN-based and is not stored as an ISBN. The title omits A/B; its linked used-inventory list includes one explicitly titled A-type row at KRW 13,000, so this item is represented as A type. No separate B-type product was verified. The product page snapshot is about 1.9 years old; its used-inventory snapshot was crawled about four months before 2026-10-20 and lists a KRW 8,900 list price and KRW 8,450 selling price. Current retail and used availability is unknown.

The used inventory displays six seller rows. `도서상태설명필독` lists condition 최상 at KRW 7,000 (parcel KRW 3,500); `선생님용도서` lists 최상 at KRW 7,000 (parcel KRW 3,700); 책방 2034 lists 상 at KRW 10,000 (parcel KRW 3,500 / half-price parcel KRW 2,400); 광화문 lists 중 at KRW 10,000 (parcel KRW 3,000); 전재원 lists 최상 at KRW 12,000 (parcel KRW 3,500 / half-price parcel KRW 2,400); kirinji lists A형, 상, at KRW 13,000 (parcel KRW 3,500 / half-price parcel KRW 2,400). The snapshot exposes no separate seller-item IDs, so row keys are deterministic and current statuses remain unknown. The cover report identifies 뽀구미 as the November model. No product image was copied because reuse permission is unconfirmed. The A-type edition and all seven retail/used observations were committed to PostgreSQL and verified before the next source list.

### MAXIM April 2025 A- and B-type print issues

[Aladin A-type product](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=360998428) · [Aladin B-type product](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=360998557) · [April series](https://www.aladin.co.kr/shop/common/wseriesitem.aspx?SRID=1248264) · [Subscription cover report](https://www.mimint.co.kr/bbs/view/news/S1N18/4757340?page=280&pageblock=271)

Live browser checks on 2026-10-23 around 22:20 SGT confirmed two print variants of the '이불킥' issue, both published 2025-03-21, 192 pages, A4 (210×297mm), 518g and ISSN 2233-4270. ISBNs are A K682038965 and B K782038965. Both show list KRW 8,900, last-displayed sale KRW 8,450 and sold-out/discontinued messaging; current retail availability remains unknown. A advertises the 미스맥심 하리/한지나 poster and B the 미스맥심 한지나/뮤아 poster. Inclusion with individual used copies is unconfirmed.

The product images themselves print `MODEL 미스맥심 하리` on A and `MODEL 미스맥심 한지나` on B. These names were read from the cover text, not inferred from faces or supplement names. A contemporaneous Focus Today report dated 2025-03-26 explicitly identifies 뮤아 with the subscription cover. All three are linked at issue level, with A/B mappings recorded in edition metadata. This Aladin batch did not establish an exact subscription listing; the later Joongna batch above adds it. The shared work is `korea-maxim-2025-04-issue`, classified as `magazine_issue`. The later YES24 public-series batch adds the PDF at month precision and KRW 4,800, while its exact cover variant and page count remain unspecified. The subsequent Aladin snapshot gives an explicit publication day of 2025-04-01, attributed to that source.

The [A-type used list](https://www.aladin.co.kr/shop/UsedShop/wuseditemall.aspx?ItemId=360998428&start=newproduct) has four offers on one page: 김민수 중 KRW 5,500, lee sol 상 KRW 16,500, and P. J. Stahl 상 at KRW 24,000 and KRW 30,000. The [B-type list](https://www.aladin.co.kr/shop/UsedShop/wuseditemall.aspx?ItemId=360998557&start=newproduct) has five: 낭만시인 최상 KRW 18,000; 김민수 최상 KRW 18,000; two distinct Danielle 최상 copies at KRW 30,000 each; and P. J. Stahl 상 KRW 30,000. All nine exact rows expose basket and immediate-purchase controls, supporting active status at observation time. Shipping is parcel KRW 3,300 for lee sol, KRW 3,000 for 낭만시인, and KRW 3,500 for the others; 김민수 and P. J. Stahl also show half-price parcel KRW 2,400.

Four manifest records add the issue work, two print editions and eleven observations (two retail and nine active used). The [capture](korean-maxim-april-2025-capture.json) preserves exact item IDs, seller details, printed-credit evidence and asset provenance; the [database report](korean-maxim-april-2025-db-verification.json) covers every saved record and all three cover credits. Public catalog verification passed before further collection. No retailer API was used. Images were inspected to read credits, with no image stored or embedded in the MuseBooks catalog; reuse permission remains unconfirmed.

### MAXIM March 2025 A-, B- and C-type print issues

[Aladin A-type product](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=358716928) · [Aladin B-type product](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=358717217) · [Aladin C-type product](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=358717482) · [March series](https://www.aladin.co.kr/shop/common/wseriesitem.aspx?SRID=1242202) · [YES24 cover contents](https://www.yes24.com/product/goods/143312098) · [C-type cover report](https://www.newsis.com/view/NISX20250313_0003096828?pc_view=1)

Live browser checks on 2026-10-23 around 22:13 SGT confirmed three print variants, all published 2025-02-21, 192 pages, A4 (210×297mm), 518g, ISSN 2233-4270, list KRW 8,900 and last-displayed sale KRW 8,450. All show sold-out/discontinued messaging, so retail availability remains unknown. A/B ISBNs are K192037788 and K142037788. C displays ISSN-based serial barcode 9772233427046 under an ISBN label; this is retained as provenance, with ISBN left blank. Neither the cover filename nor internal seller-link identifier independently establishes an ISBN.

A/B advertise a 치어리더 우수한/미스맥심 박지연 poster; C advertises a 유튜버 잇섭/치어리더 우수한 poster. Inclusion with individual used copies is unconfirmed. The shared issue retains 우수한's verified COVER credit and adds creator 잇섭: NEWSIS's contemporaneous 2025-03-13 report explicitly identifies him with the C-type cover. The C mapping is recorded in that edition's metadata. His supplement appearance alone was not used to infer a cover credit. The existing PDF edition remains dated 2025-03-05.

Each used inventory has one page. [A](https://www.aladin.co.kr/shop/UsedShop/wuseditemall.aspx?ItemId=358716928&start=newproduct) has ts23ets 최상 KRW 12,500, 전재원 최상 KRW 15,000 and kirinji 상 KRW 15,000. [B](https://www.aladin.co.kr/shop/UsedShop/wuseditemall.aspx?ItemId=358717217&start=newproduct) has 김민수 최상 KRW 23,000. [C](https://www.aladin.co.kr/shop/UsedShop/wuseditemall.aspx?ItemId=358717482&start=newproduct) has Danielle 최상 KRW 50,000. All five rows show basket and immediate-purchase controls, supporting active status at capture time. Shipping is parcel KRW 3,500 throughout; 전재원, kirinji and 김민수 also show half-price parcel KRW 2,400.

A separately reviewed [completed A-type listing](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=370752953) names 김민수, condition 최상, displayed asking price KRW 12,200, parcel KRW 3,500, remote-area KRW 6,200 and half-price parcel KRW 2,400. Its live page explicitly says 판매완료되었습니다. The amount paid and sale date are not shown; KRW 12,200 is preserved as the displayed asking price.

Six manifest records add three print editions and nine observations: three last-displayed retail prices, five active used asking prices and one completed asking price. The [capture](korean-maxim-march-2025-capture.json) retains exact seller-item IDs and asset provenance; the [database report](korean-maxim-march-2025-db-verification.json) covers every March edition/listing and both issue cover credits, including previous digital records. Public catalog verification also passed before further collection. No retailer API or image download was used; cover/gallery reuse permission remains unconfirmed.

### MAXIM February 2025 A-, B- and C-type print issues

[Aladin A-type product](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=356413783) · [Aladin B-type product](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=356413956) · [Aladin C-type product](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=356414163) · [February series](https://www.aladin.co.kr/shop/common/wseriesitem.aspx?SRID=1236135) · [YES24 cover contents](https://www.yes24.com/product/goods/142231472) · [Publisher-sourced cover report](https://press.mtime.co.kr/newsRead.php?no=1004747)

Live browser checks on 2026-10-23 around 22:09 SGT confirmed three print variants, all published 2025-01-22, 192 pages, A4 (210×297mm), 518g, ISSN 2233-4270, list KRW 8,900 and last-displayed sale KRW 8,450. All show sold-out/discontinued messaging; retail availability remains unknown. A/B ISBNs are K282036609 and K222036609. C displays 9772233427046 under an ISBN label, but this is an ISSN-based serial barcode and is retained in provenance only; the C ISBN field is blank. Its image filename is not treated as independent ISBN evidence.

All three advertise the 마비노기 영웅전 X MAXIM 2025 캘린더 supplement. Inclusion with each used copy is unconfirmed. Existing issue-level credits 박근나, 김서아 and 려니 are retained from YES24 COVER contents and the publisher-sourced report without asserting an exact A/B/C mapping. The existing PDF edition remains dated 2025-02-05.

Each live seller inventory has one page. [A](https://www.aladin.co.kr/shop/UsedShop/wuseditemall.aspx?ItemId=356413783&start=newproduct) has one offer: 김민수, 최상, KRW 10,800. [B](https://www.aladin.co.kr/shop/UsedShop/wuseditemall.aspx?ItemId=356413956&start=newproduct) has five: 김민수 상 KRW 10,200; P. J. Stahl 중 KRW 15,000; and three distinct P. J. Stahl 상 copies at KRW 20,000 each. [C](https://www.aladin.co.kr/shop/UsedShop/wuseditemall.aspx?ItemId=356414163&start=newproduct) has 낭만시인 최상 KRW 25,000 and P. J. Stahl 상 KRW 30,000. Shipping is parcel KRW 3,000 for 낭만시인; the other seven offers show parcel KRW 3,500 and half-price parcel KRW 2,400. Basket and immediate-purchase controls support active status at capture time. These are asking prices.

The [capture](korean-maxim-february-2025-capture.json) retains all exact seller-item IDs, conditions, shipping and asset provenance. It also records differences from stale search snapshots without importing stale availability. Six manifest records add three physical editions and eleven observations (three retail and eight active used). The [database read-back](korean-maxim-february-2025-db-verification.json) verifies all month editions/listings, preserved digital records and all three cover credits. The public catalog verifier also passed before further collection. No retailer API or image download was used; cover/gallery reuse permission remains unconfirmed.

### MAXIM January 2024 A- and B-type print issues

[Aladin A-type product](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=330792771) · [Aladin B-type product](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=330792924) · [January series](https://www.aladin.co.kr/shop/common/wseriesitem.aspx?SRID=1159534) · [YES24 cover contents](https://www.yes24.com/product/goods/124406594)

Live browser checks on 2026-10-23 around 22:01 SGT confirmed two print variants of the 'BEGIN AGAIN' issue, published 2023-12-21, each 192 pages, A4 (210×297mm), 518g and ISSN 2233-4270. ISBNs are A K442937502 and B K692937502. List price is KRW 8,900 and last-displayed sale price KRW 8,450. Both product pages show sold-out/discontinued messaging, so the retail price is historical displayed pricing and current availability remains unknown. Both advertise the 2024 신입 미스맥심 달력 supplement. The existing digital edition remains dated 2024-01-02; YES24 explicitly credits 묘정 in COVER, retained at issue level.

The [A-type used inventory](https://www.aladin.co.kr/shop/UsedShop/wuseditemall.aspx?ItemId=330792771&start=newproduct) has eight active offers on one page: SunA 상 KRW 23,000; kirinji 상 KRW 24,000; P. J. Stahl 중 KRW 25,000; 알낳아딘 중고서점 중 KRW 27,900; P. J. Stahl 상 KRW 35,000; two distinct P. J. Stahl 상 copies at KRW 40,000 each; and 알낳아딘 중고서점 상 KRW 74,900. Shipping is parcel KRW 3,000 for the two 알낳아딘 offers; other offers show parcel KRW 3,500 and half-price parcel KRW 2,400. Basket and immediate-purchase controls support active status at observation time. The [B-type used inventory](https://www.aladin.co.kr/shop/UsedShop/wuseditemall.aspx?ItemId=330792924&start=newproduct) is empty. Calendar inclusion in each used copy is unconfirmed.

The [capture](korean-maxim-january-2024-capture.json) records every distinct seller-item ID, condition, price and shipping amount, plus both cover asset URLs as provenance. Three manifest records add two physical editions and ten observations: two last-displayed retail prices and eight active used asking prices. The [database read-back](korean-maxim-january-2024-db-verification.json) covers all January editions/listings, including the previous PDF record, and the sole issue cover credit. No retailer API or image download was used; cover and gallery reuse permission remains unconfirmed.

### MAXIM February 2024 A- and B-type print issues

[Aladin A-type product](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=332752962) · [Aladin B-type product](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=332753150) · [February series](https://www.aladin.co.kr/shop/common/wseriesitem.aspx?SRID=1164543) · [YES24 cover contents](https://www.yes24.com/product/goods/124866932)

Live browser checks on 2026-10-23 around 21:57 SGT confirmed two physical variants featuring 박민정. Both were published 2024-01-22, with 192 pages, A4 dimensions (210×297mm), weight 518g and ISSN 2233-4270. ISBNs are A K102938777 and B K122938777. List price is KRW 8,900 and last-displayed sale price KRW 8,450; both pages say sold out/discontinued, so current retail availability remains unknown. The shared issue retains its existing YES24 digital edition, released 2024-02-02, and sole cover credit 박민정.

The live [A-type used inventory](https://www.aladin.co.kr/shop/UsedShop/wuseditemall.aspx?ItemId=332752962&start=newproduct) is empty. The [B-type inventory](https://www.aladin.co.kr/shop/UsedShop/wuseditemall.aspx?ItemId=332753150&start=newproduct) has one page and one exact [seller offer](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=396473163): 알낳아딘 중고서점, condition 상, asking KRW 59,900, parcel shipping KRW 3,000. Basket and immediate-purchase controls support active status at observation time. Older search snapshots with A at KRW 50,000 or B at KRW 60,000 were superseded by this live check and were not imported.

Three manifest records added two print editions and three price observations: two historical displayed retail prices and one active used offer. The [capture](korean-maxim-february-2024-capture.json) retains exact source URLs and cover asset URLs as provenance. The [database report](korean-maxim-february-2024-db-verification.json) verifies every February edition/listing/observation, including the previous digital record, and the sole issue cover credit. Public catalog verification also passed before further collection. No retailer API was used. Cover/gallery fields remain blank pending image reuse permission.

### MAXIM March 2024 A-, B- and C-type print issues

[Aladin A-type product](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=334832870) · [Aladin B-type product](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=334833428) · [Aladin C-type product](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=334834532) · [March series](https://www.aladin.co.kr/shop/common/wseriesitem.aspx?SRID=1170976) · [YES24 issue cover contents](https://www.yes24.com/product/goods/125313325) · [C-type cover report](https://www.wikitree.co.kr/articles/929660)

Live browser checks on 2026-10-23 around 21:52 SGT confirmed three physical variants of the March '내향인' issue, all 192 pages, A4 (210×297mm), 518g, ISSN 2233-4270, with list price KRW 8,900 and last-displayed sale price KRW 8,450. All three show sold-out/discontinued messaging, so retail availability remains unknown. ISBNs are A K202938155, B K372938155 and C K922938259. Aladin's dates are A 2024-02-21, B 2024-02-01 and C 2024-02-01. These retailer-specific assertions are retained with a conflict note: the contemporaneous C-cover report describes issuance on 2024-02-24, so a single original publication day is unresolved.

The live seller inventories displayed one page each: [A](https://www.aladin.co.kr/shop/UsedShop/wuseditemall.aspx?ItemId=334832870&start=newproduct) had eight active items at KRW 3,000–10,000; [B](https://www.aladin.co.kr/shop/UsedShop/wuseditemall.aspx?ItemId=334833428&start=newproduct) had five at KRW 20,000–35,000; [C](https://www.aladin.co.kr/shop/UsedShop/wuseditemall.aspx?ItemId=334834532&start=newproduct) had one at KRW 23,000. Basket and immediate-purchase controls supported active status at capture time. Distinct item IDs preserve repeated seller/price rows. The [reviewed capture](korean-maxim-march-2024-capture.json) records every exact item, seller, condition and shipping amount.

A separate [completed B-type listing](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=368228558) names seller 김민수, condition 최상, displayed asking amount KRW 16,700, parcel shipping KRW 3,500 (remote-area KRW 6,200) and half-price parcel KRW 2,400. Its live page explicitly says 판매완료되었습니다. No actual paid price or completion date is shown; the asking amount is preserved without treating it as a verified transaction price.

The issue retains YES24's explicit 이유진/이규영 cover credits, and the contemporaneous report adds 김선태 with an explicit C-type identification. All credits remain associated with the shared magazine issue. Six manifest records added three physical editions and 18 observations: three last-displayed retail prices, 14 active used offers and one completed offer. The [database read-back](korean-maxim-march-2024-db-verification.json) verified every new record, preserved the previous digital edition/listing, and checked all three cover credits. The public catalog pagination/format verifier also passed. No retailer API or image download was used; image reuse permission remains unconfirmed.

### MAXIM April 2024 A-, B- and C-type print issues

[Aladin A-type product](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=336663401) · [Aladin B-type product](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=336663898) · [Aladin C-type product](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=336664075) · [April series](https://www.aladin.co.kr/shop/common/wseriesitem.aspx?SRID=1176868) · [SportsDonga cover report via Nate](https://news.nate.com/view/20240329n00274)

Live browser checks on 2026-10-23 around 21:43 SGT confirmed three print variants, each published 2024-03-21, 192 pages, A4 (210×297mm), 518g, ISSN 2233-4270, list price KRW 8,900 and last-displayed sale price KRW 8,450. ISBNs are A K142939734, B K222939734 and C K362939734. All three product pages show sold-out/discontinued messaging, so the stored retail availability is unknown and the price is last displayed. A/B titles explicitly name 감동란. The contemporaneous SportsDonga report identifies 감동란's issue cover and actor 김호영's special cover; both credits stay at issue level without asserting an exact C-type mapping from forum/wiki claims.

The [A used inventory](https://www.aladin.co.kr/shop/UsedShop/wuseditemall.aspx?ItemId=336663401&start=newproduct) showed four distinct active seller rows on one page: SunA, condition 상, KRW 10,000, parcel KRW 3,500 / half-price parcel KRW 2,400 (item 404452422); P. J. Stahl, condition 중, KRW 10,000, the same shipping options (388122227); 알낳아딘 중고서점, condition 중, KRW 28,900, parcel KRW 3,000 (395470496); and 낭만시인, condition 최상, KRW 30,000, parcel KRW 3,000 (402267865). Every row exposed basket and immediate-purchase controls. The [B inventory](https://www.aladin.co.kr/shop/UsedShop/wuseditemall.aspx?ItemId=336663898&start=newproduct) and [C inventory](https://www.aladin.co.kr/shop/UsedShop/wuseditemall.aspx?ItemId=336664075&start=newproduct) each showed zero offers.

The [reviewed capture](korean-maxim-april-2024-capture.json) preserves the exact edition identities, seller prices, conditions, shipping and zero-result checks. Four manifest records added one magazine issue work, three physical editions and seven observations. They were committed to PostgreSQL and the [Aladin database read-back](korean-maxim-april-2024-aladin-db-verification.json) verified every edition, listing, observation and the two cover credits. The public catalog verifier passed before the YES24 source list began. No retailer API was used and no image asset was copied. A MAXIM official-site page-reader search reported robots denial during this review; no alternate access was attempted and no permission-approved automated route was established. Subscription S-type details remain unverified.

### MAXIM April 2024 YES24 digital issue

[YES24 product](https://www.yes24.com/product/goods/125759590)

The live product page checked on 2026-10-23 around 21:47 SGT lists publication date 2024-04-01, DRM PDF format, 241.43MB, approximately 187 pages, regular list and sale price KRW 4,800, and a separate conditional coupon benefit price KRW 4,320. It shows 판매중 and basket, immediate-purchase and immediate-reading controls. The ordinary listing is stored as active at KRW 4,800; the conditional coupon amount is retained as source context. This digital edition uses the same April magazine issue work as the print variants and preserves its own release date and format. Its title names 감동란; the contents identify 김호영 under ICON. The existing issue-level cover credits remain tied to the contemporaneous report.

The [YES24 capture](korean-maxim-april-2024-yes24-capture.json) retains the metadata, prices, availability and the exact cover asset URL `https://image.yes24.com/goods/125759590/XL` as provenance only. Image reuse permission remains unconfirmed; no image was copied and no separate product gallery was verified. The one-item YES24 list was validated and committed after the Aladin batch passed verification. The [combined April database read-back](korean-maxim-april-2024-db-verification.json) verifies all four April editions, eight listings and matching observations, and both cover credits.

### MAXIM May 2024 A- and B-type print issues

[Aladin A-type product](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=338433993) · [Aladin B-type product](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=338434071) · [Aladin May series](https://www.aladin.co.kr/shop/common/wseriesitem.aspx?SRID=1183085) · [A-type used inventory](https://www.aladin.co.kr/shop/UsedShop/wuseditemall.aspx?ItemId=338433993&start=newproduct) · [B-type used inventory](https://www.aladin.co.kr/shop/UsedShop/wuseditemall.aspx?ItemId=338434071&start=newproduct) · [YES24 issue cover credits](https://www.yes24.com/product/goods/126331777)

Live browser checks on 2026-10-23 around 21:37 SGT confirmed two physical variants of the May '남의남자' issue, published 2024-04-23, 192 pages, A4 (210×297mm), 518g, ISSN 2233-4270. The ISBNs are A K702930094 and B K742930094. Both pages display list price KRW 8,900 and last-shown sale price KRW 8,450, with sold-out/discontinued messaging and a static sold-out confirmation date of 2024-05-27. The stored retail availability is unknown; the sale amount does not represent purchasable new stock. The shared issue retains the existing YES24 cover credits for 바비앙 and 김갑주 without inferring an A/B mapping.

The live inventory pages each have one page of offers: 12 A-type seller items priced KRW 25,000–41,000, and seven B-type seller items priced KRW 26,000–50,000. Each row exposes basket and immediate-purchase controls, so these offers are active at the recorded observation time. Distinct external item IDs are preserved for repeated seller/price combinations. Seller, condition, price, shipping and exact item identity for all 19 offers are retained in the [reviewed capture](korean-maxim-may-2024-capture.json). The A sellers are SunA, 전준혁 and 꾸이중고서점; the B sellers are 낭만시인, 허책방, P. J. Stahl, 챔프123, 알낳아딘 중고서점, 전준혁 and 다산.

The batch added two physical editions and 21 price observations (two retail and 19 used). All four manifest records were validated and committed to PostgreSQL. The [direct database verification](korean-maxim-may-2024-db-verification.json) checked each edition's date, ISBN, variant, dimensions and summary; all 21 listing prices/statuses/sellers/shipping fields and matching observation evidence; and the two issue-level cover credits. The public catalog pagination/format verifier also passed before the next source list. No image asset was copied because reuse permission remains unconfirmed.

### MAXIM June 2024 A- and B-type print issues

[Aladin A-type product](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=340037950) · [Aladin B-type product](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=340037425) · [A-type used inventory](https://www.aladin.co.kr/shop/UsedShop/wuseditemall.aspx?ItemId=340037950&start=newproduct) · [B-type used inventory](https://www.aladin.co.kr/shop/UsedShop/wuseditemall.aspx?ItemId=340037425&start=newproduct) · [June cover report](https://sports.khan.co.kr/article/202405231520003/amp)

Live browser checks on 2026-10-23 around 21:28 SGT confirmed the June '누나' issue's two print variants. Both product pages list publication date 2024-05-22, 192 pages, A4 dimensions (210×297mm), weight 518g, list price KRW 8,900 and last-displayed sale price KRW 8,450. ISBNs are A K162931761 and B K732931760, with ISSN 2233-4270. Both pages mark new copies sold out and publisher distribution stopped; current purchasable retail availability remains unknown. The issue-level cover credit is 박기량; the reviewed text does not assign her separately to each A/B cover.

The live A-type used list displayed two seller offers, each with basket and immediate-purchase controls: [P. J. Stahl, item 402003043](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=402003043), condition 상, KRW 24,000, parcel shipping KRW 3,500 or half-price parcel KRW 2,400; and [알낳아딘 중고서점, item 395470697](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=395470697), condition 상, KRW 28,900, parcel shipping KRW 3,000. These seller offers are active as observed, without implying a later availability check. The B-type inventory showed zero offers.

After the user approved the prerequisite `20261023_accounts_v1` migration, the migration applied successfully and all four June records were committed. Direct database read-back checked both editions against the reviewed manifest, all four listing identities/prices/statuses/seller details, their matching observation evidence, and 박기량 as the sole cover credit. The [saved database verification](korean-maxim-june-2024-db-verification.json) records those results. The public-catalog pagination/format verifier also passed before the next source list. No cover or gallery asset was copied; image reuse permission remains unconfirmed.

### MAXIM July 2024 A- and B-type print issues

[Aladin A-type product](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=341828795) · [Aladin B-type product](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=341829652) · [Aladin July used-series snapshot](https://www.aladin.co.kr/shop/common/wseriesitem_used.aspx?SRID=1194090) · [YES24 July digital issue and cover credit](https://www.yes24.com/product/goods/128598855)

Aladin lists A and B print variants published 2024-06-21, each 192 pages, A4 (210×297mm), 518g, with list price KRW 8,900 and last-shown sale price KRW 8,450. The A page lists ISBN K352931311; the B page displays serial code 9772233427039 with ISSN 2233-4270, so that code is not stored as an ISBN. The reviewed Aladin snapshots were crawled about seven months earlier (A) and five months earlier (B), and mark both issues sold out; current availability is unknown. YES24 explicitly credits 치어리더 하지원 as the issue cover model, but the reviewed sources do not textually map her to an individual A/B cover.

Aladin's used-series snapshot showed four A-type items with KRW 30,000 displayed and two B-type items with KRW 70,000 displayed. Exact used-list routes returned cache misses, so seller, condition, current status, and whether those amounts identify individual offers could not be verified; these figures are source context only and were not imported as seller-specific listings. The two new-copy price observations and physical editions were committed to PostgreSQL and verified before collection continued. No image was copied because reuse permission is unconfirmed.

### MAXIM August 2024 A-, B-, and C-type print issues

[Aladin A-type product](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=343564164) · [Aladin B-type product](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=343567095) · [Aladin C-type product](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=343567794) · [Aladin August series](https://www.aladin.co.kr/shop/common/wseriesitem.aspx?srid=1200256) · [YES24 August digital issue and cover credit](https://www.yes24.com/product/goods/130023551) · [Malwang limited-cover report](https://www.wikitree.co.kr/articles/970055)

Aladin lists three print variants. All three product pages list publication date 2024-07-23, 192 pages, A4 dimensions (210×297mm), weight 518g, list price KRW 8,900, and sale price KRW 8,450. The ISBNs are A K122932396, B K252932694, and C K192932701; each page also lists ISSN 2233-4270. At capture, all three pages displayed sold-out/discontinued messaging, including a static last sold-out confirmation date of 2024-08-26. The stored availability is `unknown` and KRW 8,450 is the last displayed price.

YES24 explicitly credits cheerleader 조연주 in the digital issue's COVER section. Wikitree reports a separate 말왕 limited edition, and the Aladin C-type cover image visually matches that report. The catalog stores 말왕 as an additional issue-level cover credit; the product image itself was not copied. The reviewed sources do not textually map the A and B cover images individually.

The live Aladin used-inventory pages showed zero offers for A, B, and C. A separate [B-type seller item](https://www.aladin.co.kr/shop/wproduct.aspx?itemid=375768527&start=clickmp) identifies seller 김민수, condition 상, price KRW 7,100, and shipping KRW 3,500 (remote-area KRW 6,200; half-price parcel KRW 2,400). Its page states that the item was sold; the sale date is not shown, so the observation is stored as completed. The three print editions and all four listing observations were committed to PostgreSQL and verified before stopping. No cover or gallery image was copied because reuse permission is unconfirmed.

### MAXIM September 2024 A- and B-type print issues

[Aladin A-type product](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=345465206) · [Aladin B-type product](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=345465347) · [Aladin September series](https://www.aladin.co.kr/shop/common/wseriesitem.aspx?srid=1206271) · [September cover-model report](https://www.specialtimes.co.kr/news/articleView.html?idxno=401026)

Aladin lists only A and B variants. Both pages give publication date 2024-08-01, 192 pages, A4 dimensions (210×297mm), weight 518g, list price KRW 8,900, and last-observed sale price KRW 8,450. The A page lists ISBN K462933068. The B page displays 9772233427039 with ISSN 2233-4270; that serial barcode is not stored as an ISBN. Stale product snapshots show sold-out status and the series page says publisher distribution has stopped; current availability is unknown.

SpecialTimes identifies 이연우 as the September issue cover model. The reviewed sources do not map her to the individual A/B covers, so the credit remains at issue level. The used-inventory links returned cache misses during review; no seller-specific used offer could be verified. Both print editions and their two retail price observations were committed to PostgreSQL and verified before the next source list. No cover image was copied because reuse permission is unconfirmed.

### MAXIM October 2024 A- and B-type print issues

[Aladin A-type product](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=348023583) · [Aladin B-type product](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=348023860) · [Aladin October series](https://www.aladin.co.kr/m/mseriesitem.aspx?SRID=1211556) · [October cover-model report](https://sports.khan.co.kr/article/202409300955003)

Aladin lists the A and B print variants with publication date 2024-09-24, 192 pages, A4 dimensions (210×297mm), weight 518g, list price KRW 8,900, and last-observed sale price KRW 8,450. The A page lists ISBN K632933320. The B page displays 9772233427039 alongside ISSN 2233-4270; that ISSN-based serial barcode is not stored as an ISBN. The reviewed series page lists only A and B and says publisher distribution has stopped. Product snapshots are stale, so current availability is unknown.

SportsKhan identifies 김나정 as the October 2024 “미신” issue cover model. The evidence does not reliably map her to each A/B cover variant, so the credit is stored at issue level without assigning separate cover images. The B-type used-inventory snapshot showed no used offers; the A-type used page could not be reviewed in this capture, so no seller offer is recorded. The two print editions and two new-copy price observations were committed to PostgreSQL and verified before the next source list. No image was copied because reuse permission is unconfirmed.

### MAXIM October 2024 YES24 digital issue

[YES24 product page](https://www.yes24.com/product/goods/134021651) · [October cover-model report](https://sports.khan.co.kr/article/202409300955003)

YES24 lists the October 2024 issue with publication date 2024-10-02, list and sale price KRW 4,800, DRM-protected PDF format, file size 193.70MB, and about 186 pages. Its snapshot, crawled last month, displayed 판매중 and purchase controls; current availability is stored as unknown and price as last-observed. SportsKhan identifies 김나정 as the issue's cover model. The digital edition and its YES24 price observation were committed to PostgreSQL and verified before the next source list. No cover or gallery image was copied because reuse permission is unconfirmed.

### MAXIM October 2024 Aladin eBook listing

[Aladin eBook product page](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=348823222) · [YES24 digital edition](https://www.yes24.com/product/goods/134021651) · [Aladin eBook terms](https://www.aladin.co.kr/account/waccount_provision.aspx?pType=1)

Aladin lists the October 2024 “미신” PDF eBook at list/sale price KRW 4,800, published 2024-10-02, with a 193.7MB file and ISSN 22334270. Its product-page snapshot is about 1.7 years old and showed eBook purchase controls; current availability is unknown and the price is last-observed. This Aladin row is linked to the same digital edition already listed by YES24, not created as a duplicate edition. The source and one additional price observation were committed to PostgreSQL and verified before the next source list. No image was copied because reuse permission is unconfirmed.

### Pyo Eunji — Rondo (Japanese print photobook)

[Artist-store product](https://pyoeunji.com/en/products/pyoeunji-rondo) · [KADOKAWA bibliography](https://www.kadokawa.co.jp/product/322303002115/) · [capture](korean-photobook-pyo-eunji-rondo-capture.json) · [database verification](korean-photobook-pyo-eunji-rondo-db-verification.json)

| Field | Captured value |
| --- | --- |
| Model / classification | 표은지 / ピョ・ウンジ / Pyo Eunji; Korean model, standalone photobook |
| Title / publisher | ピョ・ウンジ1st写真集 輪舞曲; KADOKAWA |
| Publication | 2023-08-10; Japanese print; ISBN 9784048976268 |
| Physical details | 128 pages; A4; artist-store dimensions 29.7 × 21 × 1 cm |
| Publisher reference list price | JPY 3,300, tax included |
| Live artist-store displayed price | MYR 97.00, tax included; localized currency, without conversion |
| Availability | Unknown: ADD TO CART disabled and members-only restriction visible |
| Images | One cover and three additional public product-image URLs saved in `catalog_media`, attributed to the store page; cover linked to the work, edition and listing |
| Capture method | Public rendered product page and publisher bibliography; no retailer API/key |

The image URLs remain hosted by the source; no pixels were downloaded or mirrored and no reuse license is asserted. Additional images are retained as product images, without claiming that they are interior-page samples. The ordinary book is separate from event tickets, signed variants and digital editions. A separate existing くりえみ＆ピョ・ウンジ collaboration is a future credit-review lead, not a duplicate of Rondo.

The importer now promotes trigger-created skeletal person records and legacy featured credits to the explicitly reviewed identity/source fields. Read-back checks include model provenance, the exact ISBN edition, price/currency, restriction evidence, four remote image rows and the public listing gallery. The manual source remains disabled for scheduled collection.

### Pyo Eunji — two Japan fanclub photobooks

[PHOTO BOOK 2022](https://pyoeunji.com/en/products/pyoeunji-photo-book-2022) · [first fanclub book restock](https://pyoeunji.com/en/products/restock-first-edition-pyo-eunji-photo-book-japan-official-fan-club-only) · [capture](korean-photobook-pyo-eunji-fanclub-capture.json) · [database verification](korean-photobook-pyo-eunji-fanclub-db-verification.json)

| Field | Annual PHOTO BOOK 2022 | First fanclub book |
| --- | --- | --- |
| Model / type | 표은지 / Pyo Eunji; standalone physical photobook | Same model; distinct standalone physical photobook |
| Content / size | December 2021–November 2022 photographs; 150 pages; A4 | Commemorates start of Japan activities; 168 pages; A4 |
| Publication | Unknown; mid-January 2023 is only a historical shipping window | 2022, year precision only; current listing is a restock |
| Live displayed price | MYR 115.00 sale; MYR 141.00 regular | MYR 141.00 |
| Descriptive reference price | JPY 4,800, tax included | JPY 4,800, tax included |
| Availability evidence | Disabled ADD TO CART and members-only notice | Disabled SOLD OUT and members-only notice; old restock prose does not override the control |
| Image references | Visually confirmed cover plus three additional product images | One promotional product image with Sold Out overlay; clean edition cover remains unknown |
| Other gaps | ISBN, publisher imprint and exact publication date unconfirmed | ISBN, publisher imprint and exact publication/restock dates unconfirmed |

Captured from public rendered artist-store pages around 23:01–23:03 SGT on 2026-10-23, without retailer APIs or keys. Prices retain the live localized MYR currency; no JPY conversion is made. The schema's `unknown` listing status retains explicit unavailable/restricted evidence and does not imply a completed sale. Five source-attributed remote image URLs were committed; no pixels were mirrored or reuse license asserted.

Direct database read-back verified two separate works/editions, two store offers, two observations, both model credits, all five image rows and their public listing galleries. It also checked that the annual publication date stayed empty, the first book stayed at year precision, and the first edition did not receive the promotional overlay as a clean cover. Page 1 also contains memberships, water, essay/event bundles and magazine appearances; these were not imported as standalone photobooks. Collection page 2 was subsequently reviewed and the same-content First Visit commemorative cover was imported as a separate edition. The following KADOKAWA publisher batch and Apple Books batch now capture the digital Rondo/Enbukyoku editions and prices, as documented below.

### MAXIM October 2026 — cover and live availability refresh

[YES24 digital page](https://www.yes24.com/product/goods/197225466) · [A-type print route](https://www.yes24.com/product/goods/196908942) · [capture](korean-maxim-october-2026-cover-refresh-capture.json) · [database verification](korean-maxim-october-2026-cover-refresh-db-verification.json)

| Field | Digital PDF | A-type print |
| --- | --- | --- |
| Issue / cover credit | October 2026, No. 281; 미스맥심 쥬 | Same issue-level credit; no newly verified print image |
| Publication | 2026-10-01 | 2026-09-24 from the October 20 capture |
| Pages / file | Approximately 182 pages; PDF(DRM), 591.22MB | 176 pages from the earlier capture |
| Ordinary price | Live list/sale KRW 5,500 | Last visible sale KRW 9,120, list KRW 9,600, observed October 20 at 14:42 SGT; current price not visible |
| Coupon | KRW 4,950 benefit displayed separately; conditional, excluded from ordinary price | Not rechecked |
| Availability | 판매중 and purchase controls visible | Exact route redirects to `Product/Base/ExceptionNotice` and displays `전시제한된 상품입니다.`; availability now unknown |
| Images | One visually inspected public cover linked remotely with source attribution | No print cover; digital image is not assigned to the print edition |

The digital cover is [the main product image](https://image.yes24.com/goods/197225466/XL). The series widget's separate `Noimg_M.gif` is a placeholder and was excluded. No additional product-gallery image was verified and no paid ebook preview or book content was opened. No pixels are mirrored or reuse license asserted. The print restriction was recorded without bypassing it.

This was a metadata/image and availability refresh around 23:08 SGT on 2026-10-23. It appended two observations to the existing issue's two editions/listings; no new issue, edition or listing identity was created. Exact database read-back verified the cover, issue classification/credit, PDF details, ordinary price, print restriction, preserved October 20 history and distinct edition images. Existing manual sources remain disabled/review.

### MAXIM October 2026 — Aladin A/B print list

[Aladin two-item series](https://www.aladin.co.kr/shop/common/wseriesitem.aspx?SRID=1373453) · [A print product](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=402890491) · [B print product](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=402890707) · [capture](korean-maxim-october-2026-aladin-print-capture.json) · [database verification](korean-maxim-october-2026-aladin-print-db-verification.json)

| Field | A print | B print |
| --- | --- | --- |
| Publication shown by Aladin | 2026-09-23; conflicts with existing YES24 2026-09-24 | 2026-09-23 |
| Edition handling | Existing A edition reused; canonical September 24 retained with explicit conflict evidence | New B edition under the same October issue |
| Physical details | 176 pages, A4 210×297mm, 475g | Same |
| Live list / ordinary sale | KRW 9,600 / KRW 9,120 | Same |
| Conditional card benefit | KRW 7,752, excluded from ordinary price | Same |
| Availability | Cart/buy links, quantity control and delivery estimate visible | Same |
| Advertised in-book supplement | 미스맥심 쥬/조아 스페셜 브로마이드 | 미스맥심 조아/유디 스페셜 브로마이드 |
| Cover | [Exact A product image](https://image.aladin.co.kr/product/40289/4/cover500/k412131583_1.jpg) | [Distinct B product image](https://image.aladin.co.kr/product/40289/7/cover500/k432131583_1.jpg) |

Public rendered pages and both covers were reviewed around 23:13–23:14 SGT on 2026-10-23. Aladin's K412131583/K432131583 values are retailer identifiers labeled ISBN on its page; they are retained in evidence, without asserting standards-valid ISBNs. ISSN is 2233-4270. Supplement credits do not by themselves establish the individual B-cover model, whose identity was unverified at that checkpoint. The later publisher batch explicitly identifies 미스맥심 조아; no face recognition is used.

Shipping is charged below KRW 15,000 in book orders, with location-dependent delivery estimates. Separately supplied bonuses are excluded from overseas delivery. No seller-specific used offer or additional gallery image was verified. The two source-attributed cover URLs remain remote; no pixels are mirrored or reuse license asserted.

Both offers and cover references were committed and read back before further collection. Checks verified two active KRW 9,120 listings/observations, one reused A and one new B edition, distinct edition covers, preserved PDF metadata and the separate YES24 A listing's unknown status. There are three editions under the October issue. The existing Aladin manual source remains disabled/review.

### MAXIM October 2026 — publisher offers, cover credits and previews

[Publisher A (386)](https://www.maximkorea.net/magdb/magdb_view.php?lib=M&number=386) · [Publisher B (385)](https://www.maximkorea.net/magdb/magdb_view.php?lib=M&number=385) · [capture](korean-maxim-october-2026-publisher-capture.json) · [database verification](korean-maxim-october-2026-publisher-db-verification.json)

| Field | A print | B print | Subscriber S |
| --- | --- | --- | --- |
| Publisher cover credit | 미스맥심 쥬 | 미스맥심 조아 | Printed cover later verifies 미스맥심 유디 |
| Publication | 2026-09-24, explicitly stated | 2026-09-24, explicitly stated | Unknown; A/B date not copied |
| Ordinary publisher offer | KRW 9,600, enabled cart and quantity control | KRW 9,600, enabled cart and quantity control | No ordinary single-copy price/offer verified |
| Edition handling | Existing A reused | Existing B reused; canonical date refined from retailer September 23 to publisher September 24 | New metadata-only physical S edition, visibly marked No. 281 S type |
| Images | Exact publisher cover + 7 public preview panels | Exact publisher cover + 7 public preview panels | One public publisher S cover |
| Physical specifications | Existing retailer-sourced 176-page/A4 details retained and attributed | Same | Page count, dimensions and ISBN unknown |

The public detail pages were manually reviewed around 23:20–23:24 SGT on 2026-10-23. Their direct cover-credit text resolves the earlier B identity gap without inferring identity from supplement names or faces. Publisher September 24 takes precedence for the canonical A/B date; Aladin's September 23 remains a documented conflicting assertion. Aladin KRW 9,120 offers and the restricted YES24 A listing remain separate observations/listings.

The saved preview assets are public product-description panels. The October 17 event banners, store logos, archive thumbnails, alternate S image and paid B-cut/ebook content were excluded from the A/B galleries. S's cover is advertised under the subscriber-only label on the ordinary publisher page; its exact publication date, page count and ordinary publisher price remain unverified. The following printed-cover check verifies 유디; the following resale batch adds seller asking prices. No A/B facts are copied into those S fields.

The batch adds two publisher offers/observations, one issue-level JoA cover credit and one S metadata edition. It explicitly stores 17 edition-media rows and two listing-cover rows, using 17 distinct publisher image URLs. The database also maintains automatic cover rows. Public gallery responses now deduplicate identical image URLs; exact read-back confirms eight visible images per A/B edition and one for S while preserving provenance rows. No pixels were mirrored or reuse license asserted. Publisher source `maxim-korea-manual` stays disabled/review.

Next publisher checks can use the known public archive and follow actual visible card images. Other months remain discovery leads. S's printed cover credit has now been checked against its public cover asset. Its original publication day and page count still require an S-specific source.

### MAXIM October 2026 — printed S credit and three resale offers

[Printed publisher S cover](https://www.maximkorea.net/magdb/file/386/386_img3_1789949029_1215.jpg) · [credit capture](korean-maxim-october-2026-s-credit-capture.json) · [credit verification](korean-maxim-october-2026-s-credit-db-verification.json) · [resale capture](korean-maxim-october-2026-s-resale-capture.json) · [resale verification](korean-maxim-october-2026-s-resale-db-verification.json)

The full-size public publisher cover explicitly prints `COVER MODEL 미스맥심 유디` and `No.281 S type`. This verifies Yudi's S-cover credit through printed text, without face recognition. The existing canonical `유디` person (`17665`) was reused; the prefix 미스맥심 did not create a duplicate model. This metadata update was committed and verified before the resale list was researched. The issue now has three verified cover credits: 쥬 for A, 조아 for B and 유디 for S.

| Exact advertisement | Seller | Asking price | Shipping | Condition / components |
| --- | --- | --- | --- | --- |
| [233463669](https://web.joongna.com/product/233463669) | 퓨쳐컬쳐 | KRW 18,000 | KRW 5,000 parcel shipping; Korea Post described | Used; no components included |
| [233309433](https://web.joongna.com/product/233309433) | 큐팔이 | KRW 29,500 | Free; CJ대한통운 described | Advertised unopened/unread; all components claimed |
| [232833048](https://web.joongna.com/product/232833048) | 광땡이이 | KRW 30,000 | Free parcel; optional local handover | Advertised new; no components included |

Live exact-page checks around 23:35–23:37 SGT on 2026-10-23 verified all three prices, visible chat/buy controls and seller photos showing No.281 S type. Conditions, completeness and wrapping quality remain seller claims. The three advertisement IDs do not prove simultaneous distinct physical copies. These are asking prices, not completed sale amounts or the ordinary publisher price. Seller photos stay with their listings; the canonical S cover remains the publisher image, and the first seller photo's emoji overlay is preserved.

A two-week-old Bunjang snapshot for product 437909114 described this issue at KRW 8,000. Its live mobile route redirected to a global page titled `Book / 도서`, a generic payment listing with Sold Out controls. Its current identity could not be tied to this magazine, so neither the old KRW price nor unrelated live USD amounts/images were imported. The rejected lead is retained in the capture evidence.

Three offers/observations and three remote seller-photo references were committed in one scoped batch. Exact read-back checked every price, condition, shipping string, image URL and observation. The actual public issue endpoint returns four editions and three cover credits; S has three `marketplace_asking` active listings, no completed-sale or retail offers, and one deduplicated publisher-cover image. S's original release date, page count, dimensions, ISBN and ordinary publisher price remain unknown. No API/key, contact, cart or purchase action was used.

Scoped import files are [the one-record credit update](korean-maxim-october-2026-s-credit-import.json) and [the one-record, three-item resale batch](korean-maxim-october-2026-s-resale-import.json). Import the completed source batch using its scoped file, then read it back before collecting another list. Keep the cumulative review manifest as the ledger; earlier already-committed records need not be reapplied for each new batch.

### Pyo Eunji — First Visit to Japan commemorative cover

[Artist-store product](https://pyoeunji.com/en/products/pyoeunji-first-visit-to-japan-commemorative-edition) · [selected variant](https://pyoeunji.com/en/products/pyoeunji-first-visit-to-japan-commemorative-edition?variant=41660028846262) · [capture](korean-photobook-pyo-eunji-visit-capture.json) · [scoped import](korean-photobook-pyo-eunji-visit-import.json) · [database verification](korean-photobook-pyo-eunji-visit-db-verification.json)

The second artist-store collection page identifies a First Visit to Japan commemorative cover. Its public description snapshot, crawled last month, explicitly says the contents match the original 168-page Japan fanclub photobook and that the renewed cover commemorates the May 2022 first visit. It lists A4 and reference JPY 4,800 including tax. The live page exposes the English commemorative-edition title, current localized price and two cover thumbnails; specification/same-content assertions remain attributed to that store snapshot.

| Field | Captured value |
| --- | --- |
| Work | Existing first Japan fanclub photobook of 표은지 / Pyo Eunji; no duplicate work |
| Edition | First Visit Commemorative Cover; separate physical cover edition, Japanese, Japan market |
| Contents | 168 pages, A4; same contents as original according to artist store |
| Publication | Unknown; May 2022 is the commemorated event, not an inferred release date |
| Live displayed price | MYR 141.00, tax included; no JPY conversion |
| Availability | Disabled SOLD OUT button and members-only notice; catalog status unknown with evidence |
| Images | [Clean cover](https://pyoeunji.com/cdn/shop/products/A___No1_grande.png?v=1724745338) and [Sold Out overlay](https://pyoeunji.com/cdn/shop/files/Sold_Out_1_grande.png?v=1724490231) |

The second public thumbnail visibly prints 日本初来日記念版 and supplies the clean cover. It is the new edition's cover and a representative work cover. The overlay image is retained only as listing promotional provenance; it is not an additional interior sample. The original edition retains its separate 2022 year-precision release and unknown clean cover. The 150-page PHOTO BOOK 2022 annual remains a separate work.

Live checks around 23:42–23:43 SGT on 2026-10-23 were followed by one scoped import and exact database/public-book read-back. The public work has two editions and one featured-model credit, with no magazine issue fields or cover-model role. Checks verified price/currency, restrictions, date precision and both image URLs. Page 2's test product and DVD-only item were excluded from photobooks. No pixels were mirrored or reuse license asserted; the manual artist-store source stays disabled/review.

### Pyo Eunji — KADOKAWA digital Rondo and Enbukyoku

[Publisher capture](korean-photobook-pyo-eunji-digital-publisher-capture.json) · [publisher scoped import](korean-photobook-pyo-eunji-digital-publisher-import.json) · [publisher database verification](korean-photobook-pyo-eunji-digital-publisher-db-verification.json) · [Apple Books capture](korean-photobook-pyo-eunji-apple-capture.json) · [Apple scoped import](korean-photobook-pyo-eunji-apple-import.json) · [Apple database verification](korean-photobook-pyo-eunji-apple-db-verification.json)

| Digital edition | Publisher release | Apple Books displayed price | Apple digital specifications | Cover |
| --- | --- | --- | --- | --- |
| [Rondo / 輪舞曲](https://www.kadokawa.co.jp/product/322303002121/) | 2023-08-10 | [JPY 3,400](https://books.apple.com/jp/book/id6453688939) | 136 pages; 74.7 MB | [Publisher cover](https://cdn.kdkw.jp/cover_1000/322303/322303002121.webp) |
| [All-Other Edition: Enbukyoku / 円舞曲](https://www.kadokawa.co.jp/product/322310001500/) | 2023-11-30 | [JPY 2,200](https://books.apple.com/jp/book/id6472695690) | 104 pages; 116 MB | [Publisher cover](https://cdn.kdkw.jp/cover_1000/322310/322310001500.webp) |

KADOKAWA's public electronic-edition pages were checked around 23:49 SGT on 2026-10-23. Both publication identities, dates and cover references were committed as a two-record metadata batch and verified before the store list was collected. Rondo's digital edition belongs to the existing Rondo work. The separately titled all-other-photo companion Enbukyoku is a separate work, as the publisher describes it as the next chapter. Both reuse the existing 표은지 / Pyo Eunji person and remain Korean-origin photobooks published in Japanese; no magazine fields or cover-model roles are introduced.

The publisher-linked Apple Books Japan pages were then checked around 23:53–23:54 SGT. Each identifies KADOKAWA as publisher and DWANGO Co., Ltd. as seller. Their displayed JPY prices, page counts and file sizes were committed in a separate two-record store batch and read back from PostgreSQL. Prices are zero-decimal JPY, without currency conversion. Both listing statuses are unknown: public preview prices were visible, but account/storefront purchase eligibility was not verified. The underlying file format remains unverified; neither PDF nor EPUB is inferred. Digital ISBNs and dimensions remain blank.

Rondo's physical edition retains ISBN 9784048976268, 128 pages and its existing print metadata. Its publisher reference price JPY 3,300 is distinct from the Apple digital JPY 3,400. Publisher cover URLs supply one deduplicated public gallery image per digital edition; no Apple artwork URL or additional interior image was asserted. Cover references remain remote and attributed, with no mirrored pixels or reuse license asserted.

The publisher-linked [BookWalker Rondo page](https://bookwalker.jp/de716ac532-62e3-4d67-883f-2095a72f4fcb/) displayed a Japan-only purchase restriction and no product price. No priced BookWalker offer was imported and no location/account restriction was bypassed. The Enbukyoku BookWalker link remains an unchecked lead. Exact database/public-book read-back passed for both Apple offers, dates, digital page counts, shared model credit and preserved print edition. The global read-only catalog verifier also passed. Each completed batch was committed and verified before another source list was collected.

### BE JOYFUL — Aladin retail, twelve used offers and public images

[Product page](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=77364450) · [used inventory](https://www.aladin.co.kr/shop/UsedShop/wuseditemall.aspx?ItemId=77364450#maintab&start=newproduct) · [capture](korean-photobook-be-joyful-aladin-capture.json) · [scoped import](korean-photobook-be-joyful-aladin-import.json) · [database verification](korean-photobook-be-joyful-aladin-db-verification.json)

Live public Aladin pages were checked around 00:00–00:06 SGT on 2026-10-24. The product corroborates the existing standalone 이성경 photobook, photographer 신혜림, 페이퍼북 publisher, 2016-02-17 release, ISBN 9788997148615 and 248 pages. Its KRW 22,000 list price and KRW 19,800 displayed discounted amount remain visible, but the page says publisher/manufacturer distribution has stopped and new copies are unavailable. The retail listing is unknown, not a completed marketplace sale. Existing YES24 200×240×16mm dimensions retain attribution; Aladin reports only 200×240mm. Aladin's 770g conflicts with the older YES24 890g assertion and is preserved as source context.

| Exact used item | Seller | Condition claim | Asking KRW | Shipping KRW |
| --- | --- | --- | --- | --- |
| [402503213](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=402503213) | 책방 | 중 | 13,900 | 3,500 |
| [370011137](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=370011137) | 레이 | 상 | 18,000 | 3,300 |
| [391347853](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=391347853) | 봄바람77 | 최상 | 19,500 | 3,000 |
| [351000830](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=351000830) | Cheese | 최상 | 21,000 | 3,500 |
| [398405110](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=398405110) | 소독후 당일발송 | 최상 | 22,000 | 4,000 |
| [395022427](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=395022427) | 철학 | 중 | 22,000 | 3,300 |
| [397325251](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=397325251) | 우리의 계절들 | 상 | 23,000 | 3,500 |
| [399019367](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=399019367) | 준비된서점 | 상 | 25,900 | 6,000 |
| [397032243](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=397032243) | 준비된서점 | 상 | 27,000 | 6,000 |
| [392642408](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=392642408) | 악어친구들 | 중 | 27,000 | 6,000 |
| [290881880](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=290881880) | 바닐라라떼 | 상 | 32,500 | 3,300 |
| [379217457](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=379217457) | 이어서 | 상 | 32,900 | 3,500 parcel / 2,400 half-price parcel |

All twelve seller rows provided exact item links, conditions, prices and cart/buy controls in the live inventory. They are active asking offers at capture; individual item pages and checkout were not inspected. The two 준비된서점 rows remain distinct item IDs. Seller names and shop URLs are preserved in observation evidence and capture JSON. Aggregate inventory floors do not add another offer, and no amount is asserted as a completed sale.

The exact [cover](https://image.aladin.co.kr/product/7736/44/cover500/8997148613_1.jpg) and one [publisher-provided public promotional collage](https://image.aladin.co.kr/img/img_content/8997148613_01.jpg) are linked with product-page attribution in both edition and retail-listing galleries. The collage is one 700×2476 image containing multiple photographs, not multiple independently captured samples. Its page `src` used HTTP; the same HTTPS address was opened and verified. No paid preview viewer, image mirroring or licensing claim was involved. Aladin remains a disabled/review manual source.

One scoped record with thirteen offers/observations and four explicit media rows across two image URLs was committed to PostgreSQL, then read back field by field. The public book response has one physical edition, one featured-model credit, twelve active `marketplace_asking` offers, one unknown `physical_retail` offer, no completed sales and two deduplicated gallery images. The display mapping now recognizes explicit `[중고]` bookstore seller titles before classifying a price as new-copy retail. Read-back checked 53 existing Aladin used rows: 45 asking and eight completed offers. The global catalog verifier passed before any further source collection.

### 김설화 26 — YES24 retail price, cover and loaded public panel

[Product page](https://www.yes24.com/product/goods/116981923) · [capture](korean-photobook-kim-seolhwa-26-yes24-capture.json) · [scoped import](korean-photobook-kim-seolhwa-26-yes24-import.json) · [database verification](korean-photobook-kim-seolhwa-26-yes24-db-verification.json)

The live public page was reviewed around 00:10–00:11 SGT on 2026-10-24, after the BE JOYFUL source batch had been committed and verified. It corroborates 아이다호 publisher, 2022-12-05 release, ISBN 9791198100504, 252 pages, 900g and 215×270×15mm. The model remains the existing 김설화 featured person. The product credits author 로글(rogle); that credit does not make rogle a featured model or establish a photographer role. The product introduction explicitly calls this 김설화's first standalone photobook following her MAXIM-model debut, so it remains a photobook with no magazine issue fields.

| Field | Captured result |
| --- | --- |
| List / displayed price | KRW 49,800 / KRW 44,820 |
| Availability | 일시품절; new copies cannot currently be purchased. Listing status unknown, not an active offer or completed sale |
| Cover handling | Two designs randomly supplied under one product. Existing `Random cover` edition reused; no separately selectable variants inferred |
| Delivery | YES24 free-shipping label; overseas delivery possible, destination costs/eligibility unverified |
| Cover | [Exact primary product image](https://image.yes24.com/goods/116981923/XL) |
| Other image | [One public promotional panel](https://image.yes24.com/momo/TopCate4082/MidCate009/408189518.jpg) |
| Used offers | No seller-specific row exposed on this product page; disallowed used-shop routes not opened |

The detail image initially returned `Noimg_XL.jpg`. Navigating to the ordinary public 상세 이미지 section loaded the real image; its exact `src` was then captured and the rendered panel inspected. It visibly prints `SeolHwa Kim PHOTO BOOK` and `CHAPTER 1 BLUE`. The one composite panel is not counted as separate interior images or separate cover variants. Generic ads, packing images, placeholder images and unrelated recommendations were excluded.

One scoped record with one price observation and four explicit media rows across two distinct URLs was committed to PostgreSQL. Exact database/public-book read-back passed: existing work, edition and model identity; publication day and specifications; unknown KRW 44,820 retail display; random-cover label; two deduplicated images in each edition/retail gallery; no active resale or completed-sale records. The manual YES24 print source stays disabled/review. Images remain remote and attributed; no pixels were mirrored and no reuse license is asserted.

### SANTORINI — YES24 displayed price, cover and unknown specifications

[Product page](https://www.yes24.com/product/goods/416604) · [capture](korean-photobook-santorini-yes24-capture.json) · [scoped import](korean-photobook-santorini-yes24-import.json) · [database verification](korean-photobook-santorini-yes24-db-verification.json)

The public page was checked around 00:14 SGT on 2026-10-24, after the 김설화 26 batch had been committed and verified. It explicitly credits 고소영 as model and 조세현 as photographer. The existing standalone photobook work, physical edition and featured-model identity were reused. Publisher Dreamax, 2003-11-29 publication and ISBN 9788995439500 are corroborated. Pages and dimensions remain unknown because the retailer labels both unconfirmed; 1,030g is only a captured weight assertion.

| Field | Captured result |
| --- | --- |
| List / displayed price | KRW 27,000 / KRW 25,650 |
| Availability | 품절; current new copies cannot be purchased. Stored as unknown retail availability, not an active or completed offer |
| Cover | [Exact main product image](https://image.yes24.com/momo/TopCate11/MidCate09/1080744.jpg) |
| Other images | None confirmed; packing illustrations, ads and unrelated recommendations excluded |
| Original package | Five 고소영 posters and one compilation album CD; used-copy completeness not inferred |
| Used context | Two items from KRW 55,400 is an aggregate only. Linked UsedShopHub route was not opened or converted into seller-specific offers |
| Delivery | YES24 free-shipping label; overseas destination costs/eligibility unverified |

The single displayed-price observation and cover provenance were committed in one scoped record. Exact database/public-book read-back passed for date, ISBN, unknown page/dimension fields, model/photographer separation and the unavailable KRW 25,650 retail display. Edition and retail galleries each expose one deduplicated cover; no used offers or completed sales were introduced. The manual source remains disabled/review. The cover is a remote reference, with no mirrored pixels or reuse license asserted. Collection stops at this completed batch at the user's request.

### MAXIM November 2026 — publisher A/B offers and subscriber S cover

[A product](https://www.maximkorea.net/magdb/magdb_view.php?lib=M&number=388) · [B product](https://www.maximkorea.net/magdb/magdb_view.php?lib=M&number=387) · [capture](korean-maxim-november-2026-publisher-capture.json) · [scoped import](korean-maxim-november-2026-publisher-import.json) · [database verification](korean-maxim-november-2026-publisher-db-verification.json)

Collection resumed on 2026-10-25 after the saved SANTORINI checkpoint. The live publisher archive now lists November 2026, issue No.282. Visible archive cover cards led to the exact A/B product pages; no route numbers were guessed. Both descriptions explicitly identify `282호 표지모델 치어리더 차영현`. The separate public subscriber cover prints `No.282 S type`, subscriber-only limited edition and `치어리더 차영현`. Credits come from text, not face matching. All three physical cover editions belong to one November magazine issue, with one canonical 차영현 cover-model credit and no standalone photobook or featured-model role.

| Field | A print | B print | Subscriber S print |
| --- | --- | --- | --- |
| Issue month / number | 2026-11 / 282 | 2026-11 / 282 | 2026-11 / 282 |
| Explicit cover model | 차영현 | 차영현 | 차영현, printed on cover |
| Publication day | 2026-10-24 | 2026-10-24 | Unknown; A/B day not copied |
| Ordinary publisher price | KRW 9,600 | KRW 9,600 | Unknown; no ordinary single-copy offer imported |
| Availability at capture | Active; quantity field and enabled cart | Active; quantity field and enabled cart | Metadata only; subscriber-only artwork/link |
| Advertised bromides | 차영현 / 박수민 | 차영현 / 지니 | Not independently verified |
| Public gallery | Exact cover + seven preview panels | Exact cover + seven preview panels | Exact cover only |
| Pages / dimensions / ISBN | Unknown | Unknown | Unknown |

Live checks around 12:49–12:50 SGT on 2026-10-25 recorded the two ordinary publisher prices and quantity/cart controls without logging in, adding to a cart or checking out. Delivery charges were not stated on the reviewed pages. The lineup and bromide names 지니, 박수민, 소은 and 첼설아 do not become additional cover credits. No October page count, dimensions or identifiers were copied into the new issue.

The [A cover](https://www.maximkorea.net/magdb/file/388/388_img_1792453511_1215.jpg), [B cover](https://www.maximkorea.net/magdb/file/387/387_img_1792453351_1215.jpg) and [S cover](https://www.maximkorea.net/magdb/file/388/388_img3_1792453512_1215.jpg) are exact publisher image URLs. Seven public product-preview panels per A/B were opened and visually checked, including the final panel mapping all three covers to issue282. Title-only heading graphics, store logos, archive thumbnails, duplicate B-page S artwork and unrelated banners were excluded. These are public product images, not a paid magazine reader or B-cut extraction. References remain remote and source-attributed; no pixels were mirrored or reuse license asserted.

The three-record batch was committed to PostgreSQL before any further source list was collected. It adds one issue work, three print editions, two retail listings/observations and 19 explicit media rows across 17 distinct URLs. Exact database/public-issue read-back passed for every metadata field, price, observation evidence, shared credit and image provenance. Public galleries deduplicate automatic covers to eight A images, eight B images and one S image. S has no listing, release day or inferred ordinary price. Publisher source `maxim-korea-manual` remains disabled/review, and the global read-only catalog verifier passed.

The full database's digital total is now 5,022 rather than the preceding checkpoint's 5,450. A separate database update marked exactly 428 Japanese works superseded on October24 around 22:08–22:09 SGT. At that checkpoint, the scope audit confirmed all 110 Korean ledger works were present and published; the later September correction below consolidates one split issue. The new November batch only adds a Korean magazine issue and physical cover editions; older verification reports retain their historical totals.

### MAXIM November 2026 — Aladin A/B prices and print specifications

[A retailer product](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=404910497) · [B retailer product](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=404910553) · [capture](korean-maxim-november-2026-aladin-print-capture.json) · [scoped import](korean-maxim-november-2026-aladin-print-import.json) · [database verification](korean-maxim-november-2026-aladin-print-db-verification.json)

After the publisher batch was committed and verified, the live Aladin search for `맥심 2026 11` returned two exact print products. Their detail pages were reviewed around 12:56 SGT on 2026-10-25. Existing November A/B editions and the publisher-verified 차영현 cover credit were reused. No additional work, edition or cover-model identity was created.

| Field | A print | B print |
| --- | --- | --- |
| Aladin product ID | 404910497 | 404910553 |
| List / ordinary selling price | KRW 9,600 / KRW 9,120 | KRW 9,600 / KRW 9,120 |
| Availability | Active; quantity/cart/buy controls and current delivery estimate | Active; quantity/cart/buy controls and current delivery estimate |
| Aladin publication assertion | 2026-10-21 | 2026-10-21 |
| Canonical publisher publication | 2026-10-24, retained | 2026-10-24, retained |
| Print specifications | 176 pages; 210×297mm (A4); source weight475g | 176 pages; 210×297mm (A4); source weight475g |
| Source barcode labelled ISBN | 9772233427008 | 9772233427039 |
| ISSN / Aladin shop key | 2233-4270 / K702131214 | 2233-4270 / K842131214 |
| Advertised bromides | 차영현 / 박수민 | 차영현 / 지니 |
| Retailer cover | [Exact A listing image](https://image.aladin.co.kr/product/40491/4/cover500/k702131214_1.jpg) | [Exact B listing image](https://image.aladin.co.kr/product/40491/5/cover500/k842131214_1.jpg) |

Aladin's October21 date conflicts with the publisher's explicit October24 date. The canonical day remains October24; the retailer assertion is retained in capture, edition summary and observation evidence. Its 977-prefixed serial barcodes are source assertions rather than book ISBNs, so canonical ISBN fields remain blank. A/B page counts and dimensions are now refined from Aladin; S's unknown fields remain unchanged.

The ordinary KRW9,120 price excludes the conditional KRW7,752 card-benefit amount shown nearby. Shipping is paid below KRW15,000 book subtotal, but the reviewed label did not give the exact fee. Overseas shipments cannot include separately supplied supplements. The two product pages exposed no seller-specific used offer or separately usable additional product-gallery image; unrelated recommendations, ads, series thumbnails and event banners were excluded. No cart, checkout or account action occurred.

The two-record batch was committed before further collection. Exact read-back verified both new offers/observations, shipping and conflict evidence, the 176-page A4 refinements and two retailer-image provenance rows. The public issue response still has three print editions and one cover-model credit. A/B each show separate active publisherKRW9,600 and AladinKRW9,120 offers, with the publisher's eight-image galleries retained. Each Aladin listing has its own one-image cover gallery; S has one publisher cover, no listing, and unknown release/specification fields. The global read-only catalog verifier also passed. Aladin stays disabled/review, and all image URLs remain remote and attributed without a reuse-license assertion.

### MAXIM September 2026 — publisher prices, covers and issue consolidation

[Publisher A](https://www.maximkorea.net/magdb/magdb_view.php?lib=M&number=384) · [publisher B](https://www.maximkorea.net/magdb/magdb_view.php?lib=M&number=383) · [capture](korean-maxim-september-2026-publisher-capture.json) · [scoped import](korean-maxim-september-2026-publisher-import.json) · [identity correction](korean-maxim-september-2026-identity-correction.json) · [before snapshot](korean-maxim-september-2026-publisher-before.json) · [database verification](korean-maxim-september-2026-publisher-db-verification.json)

The live publisher products and public images were checked around 13:01 SGT on 2026-10-25. Both pages identify September 2026, No.280, the 더티토크 theme and publication 2026-08-24. A explicitly credits `미스맥심 뮤아`; B explicitly credits `미스맥심 윤영서`. The public S cover prints `No.280 S type`, subscriber-only limited edition and `COVER MODEL 미스맥심 뮤아`. The final comparison panel maps A, B and S to the same issue. This replaces the earlier inferred A mapping and press-only B credit with primary publisher evidence, without face matching.

| Edition | Verified cover model | Publication | Publisher price / status | Images |
| --- | --- | --- | --- | --- |
| A print | Existing 미스맥심 뮤아 person | 2026-08-24 | KRW9,600; active quantity/cart controls | [Cover](https://www.maximkorea.net/magdb/file/384/384_img_1787299828_1215.jpg) + seven public panels |
| B print | Existing 윤영서 person; no duplicate prefixed identity | 2026-08-24 | KRW9,600; active quantity/cart controls | [Cover](https://www.maximkorea.net/magdb/file/383/383_img_1787214115_1215.jpg) + seven public panels |
| Subscriber S print | 미스맥심 뮤아, printed credit | Unknown | No ordinary single-copy price/offer verified | [Exact S cover](https://www.maximkorea.net/magdb/file/384/384_img3_1787299829_1215.jpg) only |
| Existing PDF, preserved | 미스맥심 뮤아, prior contents credit | 2026-09-01 | Prior KRW5,500 observation, availability unknown; not refreshed in this batch | Existing image state preserved |

The publisher's August24 day takes precedence over the earlier YES24 August25 assertion. The old retailer observations retain their original prices, status evidence and timestamps. A/B retain independently captured YES24 176-page specifications; A retains its source-attributed 210×297×15mm dimensions, while B dimensions remain unverified. No print date or specification is copied into the 183-page PDF or subscriber S. Bromide/lineup names are not additional cover credits, and shipping charges were not stated on the publisher pages.

The existing B edition was incorrectly owned by a separate September B work. The publisher comparison establishes it as a cover variant of the existing September issue, so the import explicitly reassigns that same edition ID to `korea-maxim-2026-09-mua-digital`. Its listing and observation IDs stay unchanged. The old B work and credits remain as superseded history, with no records deleted. A saved pre-import snapshot retains both original work records, all three original editions/listings and their observations. The ledger's old B identity is corrected to the shared work, while its original record is retained in the identity-correction file.

The importer accepts this explicit correction only for a publisher-reviewed Korean magazine product with the same issue month and the source work's sole existing print edition; ordinary cross-work conflicts remain rejected. The work correction and publisher records commit in the same transaction. This batch adds two publisher offers/observations, one S metadata edition and 19 explicit media rows across 17 image URLs. September19 Mua fan-meeting banners, logos, archive thumbnails, duplicate S artwork and paid B-cut content were excluded. Public references remain remote and attributed; no pixels were mirrored or reuse license asserted.

Exact before/after read-back passed: all three original listings and observations are unchanged, PDF metadata is unchanged, two existing canonical people supply the issue's cover credits, and the public issue returns four editions with A/B/S galleries of eight/eight/one images. A/B each show the active publisherKRW9,600 offer alongside the preserved unknown-availability YES24KRW9,120 observation. S has no listing, original release day or inferred specifications. The global catalog verifier and cumulative 233-record manifest validation passed before another source list was collected. Publisher source remains disabled/review.

## DJ SODA — Candid: print bibliography, publisher images and current retail

Three sequential scoped batches were committed and read back before the next source was collected:

| Batch | Accepted data | Saved evidence |
| --- | --- | --- |
| [Hanmoto publisher-supplied bibliography](https://www.hanmoto.com/bd/isbn/9784087901566) | South Korean model DJ SODA; Shueisha Japanese print edition; publication 2024-04-05; ISBN 9784087901566; 128 pages; A4 297×210×11mm, height×width×thickness | [capture](korean-photobook-dj-soda-candid-hanmoto-capture.json), [scoped import](korean-photobook-dj-soda-candid-hanmoto-import.json), [database verification](korean-photobook-dj-soda-candid-hanmoto-db-verification.json) |
| [Shueisha / Weekly Playboy announcement](https://wpb.shueisha.co.jp/gravure/info/20240216-122279/) | Confirms release, photographer ND CHOW and print specifications; one visually checked cover plus two public promotional previews, retained as remote attributed references | [capture](korean-photobook-dj-soda-candid-publisher-capture.json), [scoped import](korean-photobook-dj-soda-candid-publisher-import.json), [database verification](korean-photobook-dj-soda-candid-publisher-db-verification.json) |
| [Maruzen Junkudo public product page](https://www.maruzenjunkudo.co.jp/products/9784087901566) | Current tax-inclusive selling price JPY 3,630; active net-store offer with partner-warehouse stock and enabled cart control; publication/ISBN corroborated | [capture](korean-photobook-dj-soda-candid-maruzen-capture.json), [scoped import](korean-photobook-dj-soda-candid-maruzen-import.json), [database verification](korean-photobook-dj-soda-candid-maruzen-db-verification.json) |

The work is `korea-dj-soda-candid-2024`; its sole currently verified edition is `korea-dj-soda-candid-2024-jp-print`. Korean model origin remains separate from Japanese publication market. DJ SODA is the featured model; ND CHOW is the photographer. No magazine issue fields or unverified digital edition are added. The Hanmoto registration date 2024-01-22 is not publication. Its JPY 3,300 before-tax / JPY 3,630 including-tax reference price, and the publisher's February 2024 planned JPY 3,630, are not treated as current offers. Only the independently checked Maruzen listing establishes the current selling price.

Maruzen's `在庫△ 提携倉庫在庫あり` means partner-warehouse stock; local branch stock, delivery date and shipping fee are not inferred. No cart, checkout or account action was performed. Kinokuniya's exact ISBN route returned HTTP 403; no bypass or offer assertion was made. Source `maruzen-junkudo-manual` remains disabled/review and uses manual rendered-page capture only. No retailer image was added; the publisher cover and previews remain unchanged. Each batch's exact database/public-book audit passed. The final global read-only verifier passed, and the cumulative 236-record manifest validated without being reapplied. The publisher public gallery returns three distinct images and the Maruzen listing is classified as `physical_retail`, separate from used asking prices and completed sales.

Hanmoto provides a conditional image/bibliography route: its [reuse policy](https://www.hanmoto.com/use_bibliographic_information) allows the stated book-introduction/sales-promotion uses for exact assets marked `利用可`, subject to its conditions, including preserving the whole image when resizing. This is asset-specific, not blanket automation approval. The exact Candid page says `書影利用可否不明`; it therefore supplies no recorded reuse approval. The Shueisha footer also prohibits unauthorized reproduction. The saved publisher URLs do not establish a license; no image pixels were mirrored and no permission request was sent.

## DJ SODA — Candid: separate Apple Books digital edition

The [Apple Books Japan product](https://books.apple.com/jp/book/dj-soda%E5%86%99%E7%9C%9F%E9%9B%86-candid/id6480587148) was checked directly through its rendered public preview on 2026-10-25. It identifies release 2024-04-05, Japanese language, publisher 集英社, seller Shueisha Inc., **132 digital pages**, a **106.3 MB** file and displayed price **JPY 3,400**. These Apple-specific electronic figures are stored on `korea-dj-soda-candid-2024-jp-digital`, under the existing Korean-model work. Digital ISBN and file format remain unverified. The print edition keeps its 128 pages, A4 dimensions, ISBN and independently observed Maruzen JPY 3,630 warehouse offer.

Apple's public preview establishes the displayed price, while account/storefront purchase eligibility remains unknown. The listing is therefore `unknown` availability and `digital_retail`, with no completed-sale or active-stock assertion. The exact displayed cover URL was obtained from the visible product picture's source set, rather than the transparent placeholder or an invented image-size route. One remote listing-image reference retains Apple provenance. No paid reader, download, login, purchase or API was used; no pixels were mirrored and reuse permission remains unconfirmed. Source `apple-books-jp-manual` stays disabled/review.

The one-record [scoped import](korean-photobook-dj-soda-candid-apple-import.json) was committed before another source list was collected. The [capture](korean-photobook-dj-soda-candid-apple-capture.json) records exact source details. The [database/public-book audit](korean-photobook-dj-soda-candid-apple-db-verification.json) verifies digital fields, price observation, cover provenance, the single canonical DJ SODA model and preservation of the print edition/offer. The public work returns two editions, with three print gallery images and one digital cover. The full read-only catalog verifier passed after the commit. The cumulative 237-record ledger validated without reapplying earlier imports.

## MAXIM August 2026 — public publisher archive, detail gate respected

The [public publisher archive](https://www.maximkorea.net/magdb/magdb.php?lib=M) was checked through the rendered browser on 2026-10-25. Its A and B cards explicitly identify **No.279**, **August 2026**, the issue title **치어리더 서여진**, and displayed prices of **KRW 9,600 each**. The rendered navigation targets are [A product 382](https://www.maximkorea.net/magdb/magdb_view.php?lib=M&number=382) and [B product 381](https://www.maximkorea.net/magdb/magdb_view.php?lib=M&number=381). Normal navigation to A redirects to the publisher's login/identity-based age-verification page. Both cards carry adult-content overlays. No verification, login, gate bypass, obscured-cover extraction or gated product/gallery collection was attempted.

These are public archive price observations, with **unknown purchase availability**. No enabled product cart or stock state was established. The existing A edition keeps its independently captured YES24 2026-07-23 release, 176 pages and 210×297×15mm dimensions; the archive does not corroborate those specifications. The new `korea-maxim-2026-08-print-b` edition is under the same issue work, with no inferred release date, page count, dimensions, ISBN or cover. The archive title corroborates the existing issue-level 서여진 credit; it does not establish individual A/B cover identities. The original YES24 PDF record remains untouched. No image references were added in this batch.

The [two-record scoped import](korean-maxim-august-2026-publisher-archive-import.json) was committed before the next source list. The [capture](korean-maxim-august-2026-publisher-archive-capture.json) records the public evidence and gate. An authoritative [before snapshot](korean-maxim-august-2026-publisher-archive-before.json) and [database/public-issue audit](korean-maxim-august-2026-publisher-archive-db-verification.json) verify the new B edition, two separate archive listings/observations, issue number279, existing single model identity, and exact preservation of earlier listings/observations and PDF data. A date/specifications are preserved. Publisher source remains disabled/review. The full read-only catalog verifier passed after commit. The cumulative 239-record ledger validated without reapplying previous imports.

## MAXIM August 2026 — Aladin print specifications and public covers

After the archive batch was committed and verified, Aladin's [August series](https://www.aladin.co.kr/shop/common/wseriesitem.aspx?srid=1366196) and exact [A product398885034](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=398885034) / [B product398885187](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=398885187) were checked through the rendered browser on 2026-10-25. Both products identify 176 pages, A4 210×297mm, 475g, publication 2026-07-22, list KRW9,600 and displayed sale KRW9,120. Both explicitly say sold out and publisher distribution stopped, so these are last-displayed prices with unknown purchase availability. B also shows historical sold-out confirmation2026-08-04; that is neither publication nor current stock evidence.

A's earlier YES24 2026-07-23 date and 210×297×15mm dimensions remain canonical, with the Aladin July22 conflict recorded. B now independently receives July22 and A4 dimensions from its own page. The publisher detail gate prevents authoritative resolution of the A release-day conflict. Aladin shop keys A K952130723 / B K932130723 are retained as source assertions, despite being labelled ISBN; canonical book-ISBN fields remain blank. ISSN is2233-4270. The special bromide credits 서여진/은지 are supplement credits, without adding 은지 as a cover model. Shipping is paid below KRW15,000, exact fee unknown, and separate supplements are excluded from overseas delivery.

The public retailer covers were visually checked and their exact image URLs saved remotely with source attribution. They were obtained from independently accessible Aladin product pages; no MAXIM overlay or gate was bypassed. No image pixels were mirrored and reuse permission is unconfirmed. The blocked YES24 B route reports `전시제한된 상품입니다.`; no data was taken from that restricted page.

The [two-record scoped import](korean-maxim-august-2026-aladin-print-import.json) and [capture](korean-maxim-august-2026-aladin-print-capture.json) retain the details. PostgreSQL commit and [exact database/public-issue audit](korean-maxim-august-2026-aladin-print-db-verification.json) passed: the same issue and three editions remain, original PDF and all prior price observations are unchanged, each print gallery has one public cover, and two new Aladin retail observations are separate from the publisher archive prices. Source `aladin-kr-manual` stays disabled/review. The full read-only catalog verifier passed after commit. The cumulative 241-record ledger validated without reapplying older imports.


After that commit and verification, the exact A/B used-inventory pages were checked. Each shows total used(0), Aladin used(0), store used(0), seller used(0), no registered products and zero pages. The [empty-inventory capture](korean-maxim-august-2026-aladin-used-empty-capture.json) records both source URLs and observation time. No used seller row or zero-price offer was invented. These zero counts apply only to the observed Aladin inventories.

## MAXIM February–July 2026 — 12 public publisher archive cards

The rendered [public MAXIM archive](https://www.maximkorea.net/magdb/magdb.php?lib=M) was checked on 2026-10-25 after the August Aladin batch and its catalog verification completed. Twelve A/B cards supply publisher issue numbers, exact navigation targets, themes, displayed prices and stock/condition labels. No gated detail image or hidden cover URL was collected. The [capture](korean-maxim-feb-jul-2026-publisher-archive-capture.json) retains each card and its observation time.

| Issue | Public theme | A / B product numbers | A / B displayed price | Visible special labels |
| --- | --- | --- | --- | --- |
| February2026 No.273 | 검스 | 370 / 369 | KRW9,600 / KRW9,600 | Both 완전품절 |
| March2026 No.274 | 치어리더 김도아 | 372 / 371 | KRW9,600 / KRW9,600 | Both 완전품절,19금 |
| April2026 No.275 | 치어리더 김나연 | 374 / 373 | KRW9,600 / KRW9,600 | A 품절임박; B 완전품절 |
| May2026 No.276 | 살스 | 376 / 375 | KRW9,600 / KRW9,600 | Both19금; B 품절임박 |
| June2026 No.277 | 김우현 | 378 / 377 | KRW9,600 / KRW9,600 | Both19금; B 완전품절 |
| July2026 No.278 | 브라운더스트2 콜라보 | 380 / 379 | **KRW8,600 damaged A copy** / KRW9,600 | A SALE,19금,파본할인, regular referenceKRW9,600; B19금 |

Every listing remains `unknown` purchase availability because no detail-page stock/cart was established. Sold-out labels do not represent completed transactions; near-sold-out labels do not establish a currently purchasable offer. JulyA's KRW8,600 is explicitly a damaged-copy discount and retains that condition separately from the existing ordinary YES24 observation. This amount must not be presented as the ordinary undamaged-copy price. Issue themes do not create model identities or map people to specific A/B artwork.

Eleven previously catalogued print editions retain their original release dates, dimensions, page counts, ISBN fields and bibliography-source URLs. The new `korea-maxim-2026-07-print-b` edition is an independently identified cover variant of the July magazine work, with release day/specifications/cover still unknown. All six existing digital PDFs remain byte-for-byte unchanged in the database audit, as do prior listings and price observations. Existing issue-level model credits are preserved. February's three pre-existing featured roles duplicate its three cover-model roles; the before snapshot and public response record this as an outstanding credit-role review at that checkpoint, without changing those roles during a price-only capture. The later guarded correction below resolves those generated duplicates.

The [12-record scoped import](korean-maxim-feb-jul-2026-publisher-archive-import.json) committed before any next source list. The authoritative [before snapshot](korean-maxim-feb-jul-2026-publisher-archive-before.json) and [exact database/public-catalog verification](korean-maxim-feb-jul-2026-publisher-archive-db-verification.json) verify six issue works, one new edition, 12 additional listings/observations and all preserved history/credits/specifications. Public responses contain one magazine work with A/B/PDF editions for each month. No images were added, and publisher source remains disabled/review. The full read-only catalog verifier passed after commit. The cumulative 253-record manifest validated without reapplying older imports.

## Pyo Eunji Rondo — exact-title permission check and Maruzen retail

Hanmoto's [exact print ISBN9784048976268 page](https://www.hanmoto.com/bd/isbn/9784048976268) was checked on2026-10-25. It corroborates KADOKAWA, release2023-08-10,128pages,A4 and reference tax-inclusiveJPY3,300. The exact image-use label is **書影利用可否不明**. The [permission capture](korean-photobook-pyo-eunji-rondo-hanmoto-permission-capture.json) records this; no Hanmoto cover/detail image is treated as approved or added. This does not satisfy the site's separate 利用可 asset-level permission route. No rights inquiry was sent.

The linked [Maruzen Junkudo product](https://www.maruzenjunkudo.co.jp/products/9784048976268) displays **JPY3,300 including tax**, matching ISBN and release, but explicitly says **在庫なし お取り扱いできません**: no net-store stock and cannot supply. A cart label does not override that stock message. The price is saved as an unavailable displayed retail amount with `unknown` purchase availability, separate from the official artist store's MYR97 members-only observation. Shipping fee/date and branch stock are unverified. No membership, cart, checkout or API was used.

The [one-record scoped import](korean-photobook-pyo-eunji-rondo-maruzen-import.json) was committed before any next source list. The [capture](korean-photobook-pyo-eunji-rondo-maruzen-capture.json), [authoritative before snapshot](korean-photobook-pyo-eunji-rondo-maruzen-before.json) and [exact database/public-book verification](korean-photobook-pyo-eunji-rondo-maruzen-db-verification.json) confirm one additional retail listing/observation and no duplicate work/edition. Existing print128pages/ISBN/A4 dimensions, canonical model, artist-storeMYR97 observation, Apple digital136pages/JPY3,400 and earlier price history remain intact. The public print edition has its existing cover; the artist listing retains its four attributed product images. No additional image URLs were accepted. Source `maruzen-junkudo-manual` remains disabled/review. The full read-only catalog verifier passed after commit. The cumulative254-record manifest validated without reapplying older imports.

## February2026 MAXIM — guarded legacy credit-role correction

The archive audit exposed three `legacy_credit` featured roles on `korea-maxim-2026-02`, generated from `works.featured_names` by the existing synchronization trigger. Each person already had an independently verified `cover_model` credit: 리리, 첼설아 and 섹밍. The stored source evidence identifies them as issue-cover subjects; it does not establish separate featured roles. The authoritative [before snapshot](korean-maxim-february-2026-credit-correction-before.json) preserves all six original credit rows and people/source identities, plus all edition, listing, observation and image rows. The [original ledger records](korean-maxim-february-2026-credit-correction-original-records.json) retain the old text values.

A metadata-only [scoped correction](korean-maxim-february-2026-credit-correction-import.json) explicitly selects `useCoverCreditsOnly`. The importer locks the existing published Korean magazine work and requires every legacy name/person to be accounted for by an existing verified cover credit. It rejects independent verified featured credits, unmatched names, unexpected legacy roles, new cover identities and price-observation batches. Only then may it clear the redundant legacy text; the existing trigger removes its generated featured rows, while the three people and their verified cover credits remain. No migration or blanket credit deletion was added.

The correction was committed and then reapplied once to verify the finalized guard and idempotence. [Exact read-back and public GetBook verification](korean-maxim-february-2026-credit-correction-db-verification.json) passed: three verified cover models, zero generated featured roles, same three editions, unchanged people identities/sources, edition metadata, listings, observations and images. February ledger entries now keep the redundant featured-name text blank so cumulative imports do not regenerate those roles. Earlier scoped files remain historical evidence and should not be reapplied. The full read-only catalog verifier passed. The cumulative255-record ledger validates without being reapplied. No new source price or image was collected in this correction.

## MAXIM April2026 — public publisher A/B and subscriber S refinement

The exact public publisher [A product374](https://www.maximkorea.net/magdb/magdb_view.php?lib=M&number=374) and [B product373](https://www.maximkorea.net/magdb/magdb_view.php?lib=M&number=373) were checked in the rendered browser on2026-10-25. Both explicitly identify **275호 표지모델 치어리더 김나연** and **publication2026-03-24**. This primary-publisher date takes precedence over the earlier Aladin2026-03-23 assertion; the prior retailer observations, original import records and before snapshot retain that conflict. A/B176pages and210×297mm remain retailer-derived; these specifications are not transferred to the PDF or S edition.

| Variant | Publisher price and availability | Cover/model evidence |
| --- | --- | --- |
| A | KRW9,600; active at observation, quantity controls and enabled cart, labelled 품절임박 | Exact A description credits 김나연; yellow-cover artwork |
| B | Displayed KRW9,600; complete-sold-out label and sold-out control, availability `unknown` | Exact B description credits 김나연; pink-cover artwork |
| Subscriber S | No ordinary single-copy price, original release day or specifications established; no listing created | Public artwork prints No275 Stype, subscriber-only limited edition and 치어리더 김나연 |

The same canonical 김나연 person is reused; no prefixed duplicate identity is created. Lineup and special-bromide names 전지은,퓨리,조이온 do not become extra cover credits. Shipping fees are unstated. Publisher product references retain exact remote URLs and attribution: A cover plus eight public product panels, B cover plus eight panels, and one S cover. A/B panels include a variant-identification notice, so they are not described as eight interior samples. Two linked contest/merchandise banners per page, recent-view thumbnails, duplicate S artwork and paid B-cut content were excluded. No pixels were mirrored and no reuse license is asserted.

The [three-record scoped import](korean-maxim-april-2026-publisher-import.json) and [capture](korean-maxim-april-2026-publisher-capture.json) were committed before another source list. The [authoritative before snapshot](korean-maxim-april-2026-publisher-before.json) and [database/public-issue audit](korean-maxim-april-2026-publisher-db-verification.json) verify the publisher dates, exact model identity, stock states, same publisher listing IDs, two additional observations, one S metadata edition and21 explicit media rows using19 distinct URLs. All earlier retailer/used listings and observations are unchanged; the PDF is unchanged. Public edition galleries deduplicate automatic covers to9 A images,9 B images and1 S image. S has no listing or inferred date/specifications. Source remains disabled/review. The full read-only catalog verifier passed after commit. The cumulative258-record ledger validated without reapplying earlier imports.

## MAXIM February2026 — primary publisher A/B/S confirmation

The public publisher [A product370](https://www.maximkorea.net/magdb/magdb_view.php?lib=M&number=370) and [B product369](https://www.maximkorea.net/magdb/magdb_view.php?lib=M&number=369) were checked on2026-10-25. They explicitly identify No273 A cover model 미스맥심 리리 and B cover model 미스맥심 첼설아, with **publication2026-01-24**. This primary-source date takes precedence over the preserved Aladin2026-01-21 assertion. Existing retailer specifications remain independently sourced; the digital PDF is unchanged.

Both A/B product pages display KRW9,600, complete-sold-out labels and a sold-out control instead of a cart. Their ordinary price displays remain `unknown` availability, not completed-sale records. The public subscriber S cover prints No273 Stype, subscriber-only limited edition and **COVER MODEL 미스맥심 섹밍**. The name was read through the page's ordinary public full-size-image control; no identity was inferred from a face. S is added as `korea-maxim-2026-02-print-s-subscription` under the same magazine work, with original release day, pages, dimensions, ISBN and ordinary single-copy price unknown.

A/B each retain one cover and seven public product panels; S has one cover. Variant-notice panels are not interior photo samples. Two Naver promotional banners per page, a recent-view thumbnail, duplicate S artwork, logos, paid B-cut and the age-restricted embedded YouTube video were excluded. No video gate was bypassed. Exact public image references stay remote and attributed; no pixels were mirrored and reuse permission remains unconfirmed.

The [three-record scoped import](korean-maxim-february-2026-publisher-import.json) committed before another source list. The [capture](korean-maxim-february-2026-publisher-capture.json), [before snapshot](korean-maxim-february-2026-publisher-before.json) and [database/public-issue audit](korean-maxim-february-2026-publisher-db-verification.json) verify existing A/B listing identities, two additional observations, one new S edition,19 explicit media rows using17 URLs and public galleries of8/8/1 distinct images. All earlier observations, retailer listings, PDF metadata and print specifications remain unchanged. The three existing canonical cover identities are preserved, with no regenerated featured roles after the preceding guarded correction. Source remains disabled/review. The full read-only catalog verifier passed after commit. The cumulative261-record manifest validated without reapplying earlier imports.

## Password — 18 source-backed subject profiles and live print offer

The [YES24 print page](https://www.yes24.com/product/goods/126289609) was checked directly in the rendered browser on2026-10-25. Its subtitle identifies a senior-model photobook, the publisher-supplied introduction describes the senior-model context, and the contents print18 individual Korean names with English spellings plus a separate event-photo section. The [capture](korean-photobook-password-models-yes24-capture.json) retains every exact name/spelling. 이미진 is both the listed author and a named subject, with a bio explicitly identifying model work. The event-photo heading is not a person; no cover-model role is assigned to this anthology.

The live page confirms release2024-04-19,226pages,210×297×20mm,ISBN9791129052346,listKRW45,000,sellingKRW42,750,판매중,quantity/cart/immediate-purchase controls and free domestic shipping with domestic delivery only. One active physical-retail observation is saved at the capture time. The earlier stale KRW42,750/unknown observation remains unchanged. No login,cart,checkout or retailer API was used. The separate linked ebook is a discovery lead only; no digital specifications were copied into the print edition.

The [18-record scoped import](korean-photobook-password-models-yes24-import.json) refines18 existing people against this one source; it does not add18 books or duplicate editions. Each profile retains its exact existing personID and canonical Korean name, receives the source-printed English spelling and verification URL, and uses `publisher_supplied_model_contents` confidence. The18 existing anthology links are promoted from legacy to verified featured-model credits. This verifies the named subject in this book context; it does not infer birth dates,private identities,agencies or merge homonyms. No additional image URLs were accepted and cover reuse remains unconfirmed.

The batch was committed before another source list. The [before snapshot](korean-photobook-password-models-yes24-before.json) and [database/public-book audit](korean-photobook-password-models-yes24-db-verification.json) verify all18 retained identities,18 source-backed profiles/featured roles,one additional price observation,same work/edition/listing,unchanged print specifications,prior price history and images. The public book returns18 subjects and one physical edition with an activeKRW42,750 retail offer. Source remains disabled/review. The full read-only catalog verifier passed after commit. The cumulative279-record ledger validated without reapplying earlier records. A refreshed cohort audit reports zero integrity failures and reduces missing person-source URLs from58 to40.

## Password — independently verified digital DRM PDF

The print page linked [YES24 ebook126988114](https://www.yes24.com/product/goods/126988114), checked through its rendered public page on2026-10-25 after the18-profile print batch was committed and verified. It is explicitly the same senior-model anthology, with a separate **2024-05-31** release, **digitalISBN9791129055156**, **PDF(DRM)** and **101.04MB** file. Digital page count is not stated and stays unknown. Print226pages,A4 dimensions,April19 release andISBN9791129052346 are not copied into the electronic edition.

The ordinary list/selling price is **KRW45,000**, with 판매중 and cart/immediate-purchase controls. The conditional coupon priceKRW40,500 is retained only as context. The linked rentalKRW31,500 and CremaClub subscription are separate access offers and are not represented as this purchase price. The page states TTS unavailable and printing disabled. No paid reader,preview,download,login,purchase orAPI was accessed. No image URL was accepted pending reuse permission.

The [one-record scoped import](korean-photobook-password-digital-yes24-import.json) committed before another source list. The [capture](korean-photobook-password-digital-yes24-capture.json), [before snapshot](korean-photobook-password-digital-yes24-before.json) and [database/public-book audit](korean-photobook-password-digital-yes24-db-verification.json) verify one new digital edition/listing/observation under the same work. The original print edition,activeKRW42,750 offer,earlier history and all18 verified model profiles/credits are unchanged. The public book returns separate print/PDF editions and prices. Manual source remains disabled/review. The full read-only catalog verifier passed after commit. The cumulative280-record ledger validates without reapplying older imports; the cohort audit reports zero integrity failures across196 editions and349 item references.

## The Briller — corrected18-subject anthology and13 source-profile gaps

The [YES24 public print page](https://www.yes24.com/product/goods/119131898) was checked directly on2026-10-25. Its publisher-supplied introduction identifies a senior-model fashion anthology. The live contents name **18 model subjects**, including **이지유**, omitted from the earlier17-subject capture. `187 / 임민경(사진작가)` explicitly identifies the photographer separately. The event/fashion-show heading is not a person. `이 진` is the printed spacing for the existing canonical이진; no English romanization is invented. 이미진 and신성훈 each have their own named subject section as well as author credits.

The page confirms hardcover2023-05-24,248pages,210×297×20mm,ISBN9791192584027,publisher북엠,listKRW55,000,sellingKRW49,500,판매중 andquantity/cart/immediate-purchase controls. Free domestic shipping and domestic-delivery-only notices are captured. One active ordinary retail observation is added; the earlier staleKRW49,500/unknown observation remains. No checkout,login,API orimage reuse was attempted, and no new image URLs were accepted.

The [18-record scoped import](korean-photobook-briller-models-yes24-import.json) reuses all18 existing people. Thirteen formerly unsourced profiles receive the Briller verification URL and publisher-supplied-model-contents confidence. The five profiles already verified throughPassword retain their exact source URLs and English names. The missing이지유 work link is added using her existing personID. All18 model links are verified featured roles, while the work photographer field is임민경; that photographer is not added as a model subject of this book. No birth dates,private identities,agencies orhomonym merges are inferred.

The import committed, but the temporary audit helper failed to compile before saving a pre-import database snapshot. **No such snapshot exists**, and none is fabricated. The [verification report](korean-photobook-briller-models-yes24-db-verification.json) records this limitation and compares exact post-import PostgreSQL/public-book state with the [preserved prior cohort audit](korean-photobook-briller-models-yes24-prior-cohort-audit.json), [original ledger record](korean-photobook-briller-models-yes24-prior-ledger-record.json) and earlier Password profile verification. These prove all18 personIDs existed before this batch, five verified profiles remain unchanged, print specifications match prior evidence and the original price-observation payload is intact. The public book returns18 subjects,photographer임민경 andactiveKRW49,500 retail.

The [capture](korean-photobook-briller-models-yes24-capture.json) retains the source facts. The complete cohort audit reports zero integrity failures and reduces missing profile-source URLs from40 to27. Source remains disabled/review. The full read-only catalog verifier passed. The cumulative298-record ledger validates without reapplying earlier batches. This source batch was saved and verified before another source list.

## Password 4 — 15 model-source gaps resolved and live print price

The [YES24 print page](https://www.yes24.com/product/goods/143622988) was checked directly on 2026-10-25. Its publisher-supplied introduction and contents identify 21 senior-model subjects, each with a printed English name. Group-photo and event-photo headings are excluded from the person list. Fifteen profiles lacked verification-source URLs; those receive this exact source and its printed spellings. Six already verified profiles retain their existing URLs and English names, even where this page uses different spelling or capitalization. The [capture](korean-photobook-password4-models-yes24-capture.json) preserves every printed spelling separately.

The live page confirms release 2025-02-19, 244 pages, dimensions 210×297×20mm, ISBN 9791129057945 and publisher 진한엠앤비. It shows list price KRW 77,000, ordinary selling price KRW 73,150, 판매중, quantity/cart/purchase controls, free domestic shipping and domestic delivery only. One active retail observation is added at the capture time; the earlier stale KRW 73,150/unknown observation remains. The linked ebook is a discovery lead only, with no digital specifications copied. No login, cart modification, purchase, API or image reuse was attempted.

The [21-record scoped import](korean-photobook-password4-models-yes24-import.json) refines one existing anthology and its existing people; it does not add 21 books. All 21 work links become verified featured-model credits. No cover-model role or magazine issue is assigned. 임민경 is a named subject in this book; the separate photographer role in The Briller is not transferred here. No private identity, birth date, agency or homonym merge is inferred. No new image URLs were accepted.

The audit helper compiled and saved the [exact database before snapshot](korean-photobook-password4-models-yes24-before.json) before import was allowed. The batch committed before another source list. [Database/public-book verification](korean-photobook-password4-models-yes24-db-verification.json) confirms 15 newly sourced profiles, six preserved profiles, the same 21 person IDs, unchanged print specifications/images/old price history and one additional active KRW 73,150 observation. The public book returns 21 subjects and one physical edition. Source remains disabled/review. The full read-only catalog verifier passed. The cumulative 319-record ledger validates without reapplying earlier imports; the refreshed cohort audit reports zero integrity failures and only 12 remaining person-source gaps.

## Password 5 — 11 model-source gaps resolved and live print offer

The [YES24 print page](https://www.yes24.com/product/goods/188880176) was checked directly on 2026-10-25. Its publisher-supplied introduction and contents identify 14 individual model subjects. Event photographs, the walking-performance group, documentary PASSWORD2 and the creative-fashion-week heading are excluded from person records. Eleven profiles lacked verification-source URLs and now use this exact book-context evidence. The three already verified profiles retain their existing source URLs and English names. No English romanizations are printed for the newly sourced names, so none are invented.

The page confirms release 2026-05-04, 186 pages, dimensions 210×297×20mm, ISBN 9791129064202 and publisher 진한엠앤비. List price is KRW 75,000 and ordinary selling price KRW 71,250, with 판매중, quantity/cart/purchase controls, free domestic shipping and domestic delivery only. One active retail observation is added at the capture time. The earlier stale KRW 71,250/unknown observation remains unchanged. A linked ebook is recorded only as a discovery lead. No login, cart modification, purchase, API, reader access or image reuse was attempted; no new image URLs were accepted.

The [14-record scoped import](korean-photobook-password5-models-yes24-import.json) refines one existing anthology and its existing people. The [capture](korean-photobook-password5-models-yes24-capture.json) preserves all source facts. The audit helper compiled and saved the [exact database before snapshot](korean-photobook-password5-models-yes24-before.json) before import. The batch committed before another source list. [Database/public-book verification](korean-photobook-password5-models-yes24-db-verification.json) confirms 11 newly sourced profiles, three preserved profiles, the same 14 person IDs and verified featured roles, unchanged print metadata/images/old history and one additional active KRW 71,250 observation. The public book has 14 subjects and one physical edition, with no magazine or cover-model role. Source remains disabled/review.

The global read-only catalog verifier passed: 338 physical works, 5,024 digital works and 8,378 database-wide listing observations. The cumulative 333-record ledger validates without reapplying earlier imports. The refreshed cohort audit reports zero integrity failures across all 110 works and reduces missing person-source URLs from 12 to one: 지수 (JISOO). This measures profile-source coverage, not image reuse permission or current-stock freshness across all records.

## JISOO [ME] — live price refresh and duplicate subject correction

The [public YES24 product page](https://www.yes24.com/product/goods/121961075) was checked on 2026-10-25. It identifies one subject, 지수 (JISOO), in the title, artist section and publisher-supplied introduction. The introduction describes her participation in production/design and unreleased album-jacket/music-video images. The release remains 2023-09-18, with a 176-page photobook, 20-piece postcard book and the separately listed package inclusions. Package dimensions remain 252×162×28mm. The item table and specification text disagree on weight (2,000g versus 1kg), so no weight is inferred.

The displayed selling and discounted prices are both KRW 39,000. The page explicitly states 품절 / 한정판매 and that new copies cannot currently be purchased. A new unavailable retail-price observation is stored as unknown, preserving the earlier observation; it is neither an active offer nor a completed sale. No used offer or new image URL was accepted, and no API, login, cart operation, purchase or restricted reader was used. Reuse permission remains unconfirmed; the source stays disabled/review.

The read-only database snapshot exposed two featured links for the same subject: canonical person16986 지수 and generated legacy person16985 지수 (JISOO). The [one-record scoped import](korean-photobook-jisoo-yes24-import.json) registers the latter spelling in the existing person_aliases table and uses an explicitly guarded work-credit correction. It requires an existing verified canonical subject, permits removal only of the named unverified legacy link, rejects other subjects/roles/alias conflicts, and preserves both person rows. The normal work-credit trigger removes the duplicate link. The canonical profile now cites the primary product page for photobook-subject provenance and retains the printed English name JISOO. This source supports the subject credit; it does not establish a separate professional fashion-model credential or cover-model role.

The [capture](korean-photobook-jisoo-yes24-capture.json), [original ledger record](korean-photobook-jisoo-yes24-original-record.json), [before snapshot](korean-photobook-jisoo-yes24-before.json), [separate pre-apply alias snapshot](korean-photobook-jisoo-yes24-preapply-alias-snapshot.json), [read-back](korean-photobook-jisoo-yes24-readback.json) and [exact verification](korean-photobook-jisoo-yes24-db-verification.json) preserve the audit trail. The original before snapshot was retained unchanged; the supplemental snapshot matches all its captured work, credit, price-history, listing, image and public-response fields. Automatic approval review rejected an attempted overwrite of the original snapshot; no overwrite occurred. The import ran only after validation and both snapshots were saved. Public-book read-back now shows one subject, one physical edition and no cover-model role. All old observations, print specifications, edition/listing identities and media are preserved.

The cumulative ledger now has334 records. Its earlier JISOO record uses the canonical featured-name spelling so future imports cannot regenerate the duplicate; the original record is separately retained above. Validation, exact read-back, the global public-catalog verifier and the full cohort audit passed. All110 works,196 editions,353 listing-item references and134 media references match; zero linked people lack provenance URLs. This resolves the linked-person provenance gap, not the remaining date/page/cover/availability/permission gaps. No subsequent source list was opened before verification.

## Password 4 — separately verified digital PDF edition

The [linked YES24 ebook page](https://www.yes24.com/product/goods/145598316) was checked directly on 2026-10-25. Its title is Password original korea 4, subtitle 시니어모델 화보집, author 이미진 and publisher 진한엠앤비. Its visible paper-book link points to the previously verified print143622988, establishing the same anthology with separate editions. The digital release is **2025-04-07**, digital ISBN **9791129059451**, file format **PDF(DRM)** and size **82.11MB**. Digital page count is unstated. The print edition's 2025-02-19 release, ISBN9791129057945,244 pages and dimensions are not copied across formats.

List and ordinary purchase prices are **KRW77,000**, with 판매중 and cart/immediate-purchase controls. The conditional coupon price KRW69,300 is excluded from the ordinary offer. A [separate rental link](https://www.yes24.com/product/goods/194752956) advertises KRW53,900; it is a discovery lead only and is not imported as a purchase price. TTS is unavailable and printing is disabled for copyright protection. No preview, paid reader, ebook download, login, cart operation, purchase or API was accessed. No new cover or image URL was accepted; exact image reuse remains unconfirmed and manual source yes24-kr remains disabled/review.

The [one-record scoped import](korean-photobook-password4-digital-yes24-import.json) committed under existing work korea-password-4-senior-models-2025 before any next source list. The [capture](korean-photobook-password4-digital-yes24-capture.json), [genuine before snapshot](korean-photobook-password4-digital-yes24-before.json), [read-back](korean-photobook-password4-digital-yes24-readback.json) and [exact verification](korean-photobook-password4-digital-yes24-db-verification.json) confirm one additional digital edition, listing and active purchase-price observation. The complete existing print edition, print listings/history, media and all21 person profiles/credits are unchanged. The public book has one physical and one digital edition and a separate active digital_retail KRW77,000 offer; no magazine issue or cover-model role is introduced.

The cumulative335-record ledger validates without reapplying old imports. The full cohort audit and global read-only public-catalog verifier passed after commit:110 works,197 editions,354 listing-item references and134 media references match, with zero integrity failures. Digital works increased to5,025; editions to6,814; listings to8,331; observations to8,380. Remaining missing canonical covers169 and page counts86 include the newly sourced ebook whose exact values and reuse rights are unconfirmed.

## Password 5 — separately verified digital PDF edition

The [linked YES24 ebook page](https://www.yes24.com/product/goods/193432650) was checked directly on 2026-10-25. It names Password original korea (5), author 이미진 and publisher 진한엠앤비. Its visible paper-book link points to print188880176, establishing the same anthology with separate editions. The digital release is **2026-07-31**, digital ISBN **9791129064585**, file format **PDF(DRM)** and size **86.74MB**. Digital page count is unstated. The print edition's 2026-05-04 release, ISBN9791129064202,186 pages and dimensions are not copied across formats.

List and ordinary purchase prices are **KRW75,000**, with 판매중 and cart/immediate-purchase controls. The conditional coupon price KRW67,500 is excluded from the ordinary offer. A [separate rental link](https://www.yes24.com/product/goods/194757196) advertises KRW52,500; it is a discovery lead only, not a purchase offer. TTS is unavailable and printing is disabled for copyright protection. No preview, paid reader, ebook download, login, cart operation, purchase or API was accessed. No new cover or image URL was accepted; exact image reuse remains unconfirmed and manual source yes24-kr remains disabled/review.

The [one-record scoped import](korean-photobook-password5-digital-yes24-import.json) committed under existing work korea-password-5-senior-models-2026 before another source list. The [capture](korean-photobook-password5-digital-yes24-capture.json), [genuine before snapshot](korean-photobook-password5-digital-yes24-before.json), [read-back](korean-photobook-password5-digital-yes24-readback.json) and [exact verification](korean-photobook-password5-digital-yes24-db-verification.json) confirm one additional digital edition, listing and active purchase-price observation. The complete existing print edition, print listings/history, media and all14 person profiles/credits are unchanged. The public book has one physical and one digital edition and a separate active digital_retail KRW75,000 offer; no magazine issue or cover-model role is introduced.

The cumulative336-record ledger validates without reapplying old imports. The full cohort audit and global read-only public-catalog verifier passed after commit:110 works,198 editions,355 listing-item references and134 media references match, with zero integrity failures. Digital works increased to5,026; editions to6,815; listings to8,332; observations to8,381. Missing canonical covers170 and page counts87 include the new ebook's unstated values; exact image reuse remains unresolved.

## MAXIM July 2026 B — exact retailer date, pages and public cover reference

The exact [Aladin July B product](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=396576004) was checked directly on 2026-10-25. It identifies 맥심 Maxim B형 2026.7 in the July issue series and supplies **2026-06-24**, **176 pages**, **210×297mm (A4)** and **475g**. These fill the existing B edition's missing release date/page count/dimensions. The retailer's ISBN label contains shop keyK202130193, which is not a valid book ISBN; canonical ISBN stays blank. ISSN2233-4270 is retained as serial context. The historical sold-out confirmation2026-07-27 is not the publication date.

List price is **KRW9,600**, displayed selling price **KRW9,120**, with explicit 품절 and a publisher/distributor supply-stopped notice. The observation is stored as unknown/unavailable retail display, not an active offer or a completed sale. Shipping is paid belowKRW15,000, but an exact fee is unstated; separate supplements are excluded from overseas delivery. No used inventory is included in this source batch.

The public product cover was inspected visually and its actual CoverMainImage URL recorded as an [attributed remote reference](https://image.aladin.co.kr/product/39657/60/cover500/k202130193_1.jpg). One explicit listing media reference and the corresponding canonical edition-cover row are persisted; the public edition gallery deduplicates their identical URL. No pixels were mirrored and no reuse permission is asserted. The public retailer page required no login or age verification; the restricted publisher detail was not opened. The inside-book 코스어 윤설화/김연지 special-bromide supplement does not independently establish B cover-model identities, so no extra people or cover credits are added. The pre-existing issue-level 바비앙 credit from digital contents is retained without claiming it maps to this B cover.

The [one-record scoped import](korean-maxim-july-2026-b-aladin-import.json) committed before another source list. The [capture](korean-maxim-july-2026-b-aladin-capture.json), [genuine before snapshot](korean-maxim-july-2026-b-aladin-before.json), [read-back](korean-maxim-july-2026-b-aladin-readback.json) and [exact verification](korean-maxim-july-2026-b-aladin-db-verification.json) confirm the same July magazine work and all three existing edition IDs. A/PDF metadata, existing person details, credit content, listings, observations and old media remain unchanged; the repeated cover-credit upsert refreshes only its update timestamp. The existing publisher B KRW9,600 history stays separate from the new Aladin observation. The A print release remains its independently sourced2026-06-29 and is not overwritten with the B date. Manual source remains disabled/review; no API, login, purchase, paid reader or restriction bypass was used.

The cumulative337-record ledger validates without reapplying old imports. Exact batch read-back, the full cohort audit and global read-only public-catalog verifier passed after commit:110 works,198 editions,356 listing-item references and135 media references match, with zero integrity failures. Unknown release dates fell to8, page counts to86 and canonical covers to169. Global listings are8,333 and observations8,382. No next source list was opened before verification.

## MAXIM July 2026 A — retailer price, cover and unresolved date conflict

The exact [Aladin July A product](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=396575889) was checked directly on 2026-10-25. It lists **2026-06-24**,176 pages,A4 210×297mm,475g and ISSN2233-4270. This conflicts with the existing [YES24 A source](https://www.yes24.com/product/goods/192563526), which supplied2026-06-29 and210×297×15mm. The canonical A release and dimensions remain unchanged; the new Aladin assertion is retained in capture, edition summary and price evidence. The publisher detail is restricted, so this batch does not resolve the date conflict. Retailer keyK142130193 is not a valid book ISBN; canonical ISBN stays blank.

List price is **KRW9,600**, displayed selling price **KRW9,120**, with explicit 품절 and distributor supply stopped. This is stored as unknown/unavailable retail display, not active stock or a completed sale. Historical sold-out confirmation2026-07-27 is not a publication date. Existing publisher damaged-copy KRW8,600 and older price history remain separate. The inside-book 미스맥심 바비앙/채솔 special-bromide supplement does not independently establish an additional cover-model credit.

The actual public CoverMainImage [remote cover URL](https://image.aladin.co.kr/product/39657/58/cover500/k142130193_1.jpg) was inspected visually and attributed to the exact product page. One explicit listing media reference and the corresponding edition-cover row persist; the public edition gallery deduplicates their identical URL. No pixels were mirrored and no reuse license is asserted. Source remains disabled/review. No API, login, age verification, restricted publisher detail, paid reader or purchase was used; used inventory was not collected.

The [one-record scoped import](korean-maxim-july-2026-a-aladin-import.json) committed before another source list. Its [capture](korean-maxim-july-2026-a-aladin-capture.json), [genuine before snapshot](korean-maxim-july-2026-a-aladin-before.json), [read-back](korean-maxim-july-2026-a-aladin-readback.json) and [exact verification](korean-maxim-july-2026-a-aladin-db-verification.json) confirm the same magazine work, all three edition IDs, preserved A canonical bibliography, unchanged B/PDF metadata, people, credit content and all previous listings/observations/media. Repeated upserts refresh the existing source and cover-credit update timestamps; their content remains unchanged. The public A edition returns its sourced cover and separate unknown KRW9,120 physical_retail offer. The issue-level Babian credit is preserved without inferring any additional subject from appearance or supplement text.

The cumulative338-record ledger validates without reapplying old imports. Exact batch read-back, the full cohort audit and global read-only public-catalog verifier passed after commit:110 works,198 editions,357 listing-item references and136 media references match, with zero integrity failures. Unknown dates remain8 and page counts86; blank canonical covers fell to168. Global listings are8,334 and observations8,383. No next source list was opened before verification.

## July A used inventory — verified empty

The [exact Aladin July A used inventory](https://www.aladin.co.kr/shop/UsedShop/wuseditemall.aspx?ItemId=396575889&start=newproduct) was checked on2026-10-25. All-used,Aladin-used,store-used and seller-used counts are zero, and the page explicitly says no used products are registered. The [empty-list capture](korean-maxim-july-2026-a-aladin-used-empty-capture.json) records zero accepted seller offers and zero database rows required. No zero-price offer, invented seller, sold transaction or replacement new-copy price was inserted. This is a point-in-time check of this exact source, not a claim about every retailer. The zero-row list was finished before the next product source was collected.

## SANTORINI — exact-ISBN Aladin bibliography and unavailable retail price

The [exact Aladin product](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=445208) was checked on2026-10-25. It identifies Santorini - 고소영 화보집,photographer 조세현,publisherDreamax,ISBN9788995439500 and the same stored release2003-11-29. It supplies previously missing **174 pages** and **228×300mm** dimensions. Its470g weight differs from the prior YES24 1,030g field; no canonical weight is inferred. Five photo/poster sheets and a compilationCD describe the original package, not seller-specific used completeness.

List price is **KRW27,000**, displayed selling price **KRW24,300**, with explicit 절판 and no further production/distribution plan. The observation is unknown/unavailable retail display, not an active offer or completed sale. Historical out-of-print confirmation2013-07-30 is not the publication date. The earlier YES24 unavailableKRW25,650 observation remains separate. Used inventory and new image URLs are excluded from this batch.

The [one-record scoped import](korean-photobook-santorini-aladin-import.json) committed before another source list. Its [capture](korean-photobook-santorini-aladin-capture.json), [genuine before snapshot](korean-photobook-santorini-aladin-before.json), [read-back](korean-photobook-santorini-aladin-readback.json) and [exact verification](korean-photobook-santorini-aladin-db-verification.json) confirm the same standalone work and edition, added bibliography and one additional retailer listing/observation. The stored model and photographer credits,ISBN,release date,old listings/history and all image URLs/provenance remain intact. The canonical metadataSourceURL stays YES24 to preserve its existing cover provenance; the Aladin bibliography URL is explicitly recorded in the edition summary and capture. The repeated cover upsert may refresh its update timestamp without changing content. No magazine fields,extra people,mirror pixels or reuse permission are introduced. Manual source remains disabled/review; no API,login,reader or purchase was used.

A Kyobo exact-ISBN search result is a discovery lead with apparently different metadata. Its direct product page has not been opened or accepted in this batch; search snippets alone do not establish a verified conflict. Verify the exact page before importing another assertion or changing canonical data.

The cumulative339-record ledger validates without reapplying old imports. Exact SANTORINI read-back, the full cohort audit and global read-only public-catalog verifier passed after commit:110 works,198 editions,358 listing-item references and136 media references match, with zero integrity failures. Unknown page counts fell to85; unknown dates remain8 and blank canonical covers168. Global listings are8,335 and observations8,384. The prior empty used list accepted no rows and required no database insert. No subsequent source list was opened before verification.

## SANTORINI Kyobo — direct source conflict and unavailable price

The [exact Kyobo product](https://product.kyobobook.co.kr/detail/S000001572227) was opened directly on2026-10-25. It identifies 고소영화보집 CD포함,publisherDREAMAX and the same **ISBN9788995439500**, but lists **2003-09-03**, **170 pages** and **297×420mm**. This is a verified direct-source disagreement with the existing YES24/Aladin release2003-11-29 and Aladin174 pages/228×300mm. Search-snippet ambiguity is now resolved into an explicit source conflict. The canonical values are retained pending stronger publisher or physical-copy evidence; the shared ISBN/title/CD context does not justify fabricating a second edition. Kyobo labels 조세현 as author; the already sourced photographer credit remains unchanged.

Kyobo displays **KRW27,000** and explicit 품절 with a restock-notification control. The price is stored as unknown/unavailable retail display, not an active offer or completed transaction. Overseas delivery is described, but an exact shipping fee is unstated. Earlier YES24KRW25,650 and AladinKRW24,300 history remains intact. No images,used inventory,API,login,reader or purchase were collected.

The [one-record scoped import](korean-photobook-santorini-kyobo-import.json) committed before another source list. Its [capture](korean-photobook-santorini-kyobo-capture.json), [genuine before snapshot](korean-photobook-santorini-kyobo-before.json), [read-back](korean-photobook-santorini-kyobo-readback.json) and [exact verification](korean-photobook-santorini-kyobo-db-verification.json) confirm one additional listing/observation on the same physical edition. Canonical date/pages/dimensions/ISBN,model and photographer credits,old listings/history and all media provenance remain unchanged. Both conflicting bibliographies are explicit in stored edition summary and Kyobo observation evidence. New source kyobo-kr-print-manual is confirmed disabled/review with manual_browser access; registering it does not approve automated collection or image reuse. No new edition or image row is added.

The cumulative340-record ledger validates without reapplying old imports. Exact Kyobo conflict read-back, the full cohort audit and global read-only public-catalog verifier passed after commit:110 works,198 editions,359 listing-item references and136 media references match, with zero integrity failures. Unknown date/page/cover counts are unchanged; the source conflict remains unresolved. Global listings are8,336,sources32 and observations8,385. No subsequent source list was opened before verification.

## Uhyun Eye — seller-marked-sold advertised price history

The [public Joongna listing124752547](https://web.joongna.com/product/124752547) was checked on2026-10-25. Its title 우현-아이 김우현 화보집 판매합니다 and description identify the existing standalone photobook. Seller 닥터꽥꽥 advertises **KRW70,000**; the page shows **판매완료** and a sold-item popup. The displayed listing date is2023-08-01. This is seller-marked-sold advertised price history, not an independently verified final payment amount or actual sale date. The seller claims an unopened purchase followed by opening only, but condition was not inspected. Shipping costs extra; the exact fee would require inquiry, and no contact was made.

The page supplies no ISBN,page count or dimensions. Those fields remain unknown, and the prior2021-12-09 publication date and unavailable YES24KRW180,000 retail history are preserved. The restricted YES24 detail was not accessed. Seller images and book pages were not collected; no paid-content,login,age verification,API,purchase or message was attempted. A related newerKRW50,000 card is recorded only as a [discovery lead](https://web.joongna.com/product/233418359), not an accepted current offer before direct-page review.

The [one-record scoped import](korean-photobook-uhyun-joongna-sold-import.json) committed before another source list. Its [capture](korean-photobook-uhyun-joongna-sold-capture.json), [genuine before snapshot](korean-photobook-uhyun-joongna-sold-before.json) and [exact verification](korean-photobook-uhyun-joongna-sold-db-verification.json) confirm one new seller listing/observation under the same physical edition, with unchanged bibliography,model profile,credit content,old retail listing/history and media. The first import transaction failed the existing80-character condition limit and rolled back; the display condition was shortened while the full claim stayed in evidence. The successful retry persisted exactly one listing and observation.

The [initial read-back](korean-photobook-uhyun-joongna-sold-readback.json) caught that native status sold was not classified into public sold history because the response helper recognized only completed. The helper now accepts both statuses without rewriting stored evidence. The [corrected public read-back](korean-photobook-uhyun-joongna-sold-public-readback.json) confirms one marketplace_sold entry and a separate unavailable retail offer. This classification is a listing state, not proof of an independently verified transaction. Source joongna-kr-manual remains disabled/review and no new image is accepted.

The cumulative341-record ledger validates without reapplying old imports. Exact seller-history read-back, the full cohort audit and global read-only public-catalog verifier passed after commit and the public classification correction:110 works,198 editions,360 listing-item references and136 media references match, with zero integrity failures. Missing date/page/cover counts remain8/85/168. Global listings are8,337 and observations8,386. No subsequent source list was opened before verification.

## Uhyun Eye — verified current seller asking offer

The newer [Joongna listing233418359](https://web.joongna.com/product/233418359) was opened directly on2026-10-25. Its title 김우현 화보 아이 팝니다 and description identify the existing photobook. Seller mongoose08 asks **KRW50,000**, with **KRW3,000** ordinary-parcel shipping, and the page exposes chat/purchase controls with no sold overlay. The item plus displayed shipping isKRW53,000; the listing price remainsKRW50,000 with shipping separate. Condition is 중고, 구성품 없음 (used, no included extras), a seller claim that was not inspected. The listing age is only3일 전, so no exact listing date is inferred.

The [one-record scoped import](korean-photobook-uhyun-joongna-active-import.json) committed before another source list. Its [capture](korean-photobook-uhyun-joongna-active-capture.json), [genuine before snapshot](korean-photobook-uhyun-joongna-active-before.json), [read-back](korean-photobook-uhyun-joongna-active-readback.json) and [exact verification](korean-photobook-uhyun-joongna-active-db-verification.json) confirm one new active seller listing/observation under the same physical edition. The public book separates this marketplace_asking entry from seller-marked-sold advertisedKRW70,000 history and unavailable new-copy retailKRW180,000. Neither asking price nor seller-marked-sold display establishes a verified transaction payment.

Publication date,model profile,credit content,old observations/listings and media are preserved. Page count,ISBN,dimensions and images remain unknown because the seller supplies none. No new edition,paid book pages,seller images,API,login,age verification,contact or purchase was involved. Source remains disabled/review and image reuse permission remains unresolved.

The cumulative342-record ledger validates without reapplying old imports. Exact active-offer read-back, the full cohort audit and global read-only public-catalog verifier passed after commit:110 works,198 editions,361 listing-item references and136 media references match, with zero integrity failures. Editions without a stored active listing fell from141 to140; missing date/page/cover counts remain8/85/168. Global listings are8,338 and observations8,387. No subsequent source list was opened before verification.

## MAXIM June 2026 — public Kyobo-specific PDF metadata

The [public Kyobo ebook page](https://ebook-product.kyobobook.co.kr/dig/epd/ebook/E000013081612) was checked on2026-10-25. It identifies the June2026 issue,publisher와이미디어,release **2026-06-01**, **PDF70.26MB**, **183 pages** and digitalISSN25083597. The public contents tab explicitly states 표지모델 김우현. The digitalISSN is not a book ISBN. The separately displayed domestic-print date2026-05-26 is context only and is not copied onto existing A/B print editions.

The ordinary ownership price is **KRW5,500**, corroborated by the sticky purchase total and enabled eBook-purchase button. KRW4,950 is labelled coupon price and is excluded from the ordinary offer. sam subscription is separate. TTS is listed available; DRM and print/save/edit restrictions apply, and physical supplements are excluded. No preview,reader,download,login,age verification,purchase,API or image collection was performed. This is ordinary public product/contents metadata, not paid ebook content.

The [one-record scoped import](korean-maxim-june-2026-kyobo-digital-import.json) adds a Kyobo-specific digital edition under the existing No.277 magazine issue. The source independently identifies this file's page count/size; these are not transferred to the existing YES24 PDF, whose exact file was not verified, or to either print variant. Its [capture](korean-maxim-june-2026-kyobo-digital-capture.json), [genuine before snapshot](korean-maxim-june-2026-kyobo-digital-before.json), [read-back](korean-maxim-june-2026-kyobo-digital-readback.json) and [exact verification](korean-maxim-june-2026-kyobo-digital-db-verification.json) confirm one new edition/listing/active purchase-price observation. All three previous edition payloads,old listings/history/media,person profile and credit content are preserved; no new model identity or standalone photobook work is created. The public edition returns183pages and active digital_retail KRW5,500.

New source kyobo-kr-digital-manual is confirmed disabled/review with manual_browser access. Registration does not grant automated collection or image reuse permission; no new media is accepted. The batch committed before any subsequent source list.

The cumulative343-record ledger validates without reapplying old imports. Exact June Kyobo read-back, the full cohort audit and global read-only public-catalog verifier passed after commit:110 works,199 editions,362 listing-item references and136 media references match, with zero integrity failures. Existing YES24PDF page count remains unverified;183pages belongs to the new Kyobo-specific edition. Missing date/page/cover counts are8/85/169. Global editions are6,816,listings8,339,sources33 and observations8,388. No subsequent source list was opened before verification.

## MAXIM July 2026 — public Kyobo-specific PDF metadata

The [public Kyobo ebook page](https://ebook-product.kyobobook.co.kr/dig/epd/ebook/E000013195770) was checked on2026-10-25. It identifies July2026,publisher와이미디어,release **2026-07-01**, **PDF69.52MB**, **181 pages** and digitalISSN25083597. The public contents tab explicitly states 표지모델 미스맥심 바비앙. No book ISBN is supplied. This file's181pages differ from June Kyobo's183pages; neither value is inferred from print or another issue.

The ordinary ownership price is **KRW5,500**, supported by the sticky purchase total and enabled eBook-purchase button. KRW4,950 is labelled coupon price and excluded from the ordinary offer. sam subscription is separate; TTS is listed unavailable. No preview,reader,download,login,age verification,purchase,API or image collection was performed.

The [one-record scoped import](korean-maxim-july-2026-kyobo-digital-import.json) adds a Kyobo-specific digital edition under the existing No.278 magazine issue. Its [capture](korean-maxim-july-2026-kyobo-digital-capture.json), [genuine before snapshot](korean-maxim-july-2026-kyobo-digital-before.json), [read-back](korean-maxim-july-2026-kyobo-digital-readback.json) and [exact verification](korean-maxim-july-2026-kyobo-digital-db-verification.json) confirm one new edition/listing/active purchase-price observation. All three previous July edition payloads,prices/history/media,person profile and credit content are preserved. The existing YES24 PDF page count remains unverified and the A print date conflict remains unresolved. No new work or model identity is created. The public Kyobo edition returns181pages and active digital_retail KRW5,500.

The manual Kyobo digital source remains disabled/review; image reuse permission remains unconfirmed and no new image is accepted. The batch committed before another source list.

The cumulative344-record ledger validates without reapplying old imports. Exact July Kyobo read-back,the full cohort audit and global read-only public-catalog verifier passed after commit:110 works,200 editions,363 listing-item references and136 media references match,with zero integrity failures. The new181-page metadata belongs only to the Kyobo-specific PDF. Missing date/page/cover counts are8/85/170. Global editions are6,817,listings8,340 and observations8,389. No subsequent source list was opened before verification.

## MAXIM August 2026 — public Kyobo-specific PDF metadata

The [public Kyobo ebook page](https://ebook-product.kyobobook.co.kr/dig/epd/ebook/E000013351170) was checked on2026-10-25. It identifies August2026,publisher와이미디어,release **2026-08-01**, **PDF62.55MB**, **181 pages** and digitalISSN25083597. The public contents tab explicitly states 표지모델 치어리더 서여진. No book ISBN is supplied. The file size differs from July's69.52MB despite the same page count; neither is inferred from another issue or print.

The ordinary ownership price is **KRW5,500**,supported by sticky purchase total and an enabled eBook-purchase button. KRW4,950 is labelled coupon price and excluded from the ordinary offer. sam subscription remains separate; TTS is unavailable. No preview,reader,download,login,age verification,purchase,API or image collection was performed.

The [one-record scoped import](korean-maxim-august-2026-kyobo-digital-import.json) adds a Kyobo-specific digital edition under the existing No.279 issue. Its [capture](korean-maxim-august-2026-kyobo-digital-capture.json), [genuine before snapshot](korean-maxim-august-2026-kyobo-digital-before.json), [read-back](korean-maxim-august-2026-kyobo-digital-readback.json) and [exact verification](korean-maxim-august-2026-kyobo-digital-db-verification.json) confirm one new edition/listing/active purchase-price observation. All previous edition payloads,prices/history,person profile,credit content and media URLs/provenance are preserved; repeated work-cover upsert may refresh its update timestamp. Existing YES24 PDF page count remains unverified and the A print date conflict remains unresolved. No new work,model or image is introduced. The public Kyobo edition returns181pages and active digital_retail KRW5,500.

The manual Kyobo digital source remains disabled/review; image reuse permission remains unresolved. The batch committed before any subsequent source list.

The cumulative345-record ledger validates without reapplying old imports. Exact August Kyobo read-back,the full cohort audit and global read-only public-catalog verifier passed after commit:110 works,201 editions,364 listing-item references and136 media references match,with zero integrity failures. New181-page metadata belongs only to Kyobo's August PDF. Missing date/page/cover counts are8/85/171. Global editions are6,818,listings8,341 and observations8,390. No subsequent source list was opened before verification.

## MAXIM September 2026 — public Kyobo-specific PDF metadata

The [public Kyobo ebook page](https://ebook-product.kyobobook.co.kr/dig/epd/ebook/E000013514799) was checked on2026-10-25. It identifies September2026,publisher와이미디어,release **2026-09-01**, **PDF83.91MB**, **183 pages** and digitalISSN25083597. Public contents explicitly state 표지모델 미스맥심 뮤아. No book ISBN is supplied. The separately displayed print date2026-08-25 remains context and does not overwrite publisher print dates or subscriber unknowns.

The ordinary ownership price is **KRW5,500**,with sticky purchase total and enabled eBook-purchase control. KRW4,950 is coupon-only and excluded from the ordinary offer. sam subscription remains separate; TTS is unavailable. No preview,reader,download,login,age verification,purchase,API or image collection occurred. Initial browser navigation timed out; the already created tab was recovered from inventory,with no duplicate navigation or restriction bypass.

The [one-record scoped import](korean-maxim-september-2026-kyobo-digital-import.json) adds a Kyobo-specific digital edition under the existing No.280 issue. Its [capture](korean-maxim-september-2026-kyobo-digital-capture.json), [genuine before snapshot](korean-maxim-september-2026-kyobo-digital-before.json), [read-back](korean-maxim-september-2026-kyobo-digital-readback.json) and [exact verification](korean-maxim-september-2026-kyobo-digital-db-verification.json) confirm one new edition/listing/active purchase-price observation. Every earlier edition payload,old prices/history,person profile,credit content and media URL/provenance remains unchanged; repeated work-cover upsert may refresh its update timestamp. Existing B-specific 윤영서 credit and all A/B/S metadata are preserved. No new work,model or image is introduced. The public Kyobo edition returns183pages and active digital_retail KRW5,500.

The manual Kyobo digital source remains disabled/review and image reuse permission remains unresolved. The batch committed before any subsequent source list.

The cumulative346-record ledger validates without reapplying old imports. Exact September Kyobo read-back,the full cohort audit and global read-only public-catalog verifier passed after commit:110 works,202 editions,365 listing-item references and136 media references match,with zero integrity failures. New183-page metadata belongs only to Kyobo's September PDF. Missing date/page/cover counts are8/85/172. Global editions are6,819,listings8,342 and observations8,391. No subsequent source list was opened before verification.

## MAXIM October 2026 — Kyobo purchase PDF distinct from sam

The known [Kyobo sam page](https://ebook-product.kyobobook.co.kr/dig/epd/sam/E000013637393) was opened on2026-10-25,then its visible eBook link followed to the [ordinary purchase page](https://ebook-product.kyobobook.co.kr/dig/epd/ebook/E000013637393). The purchase page independently confirms **2026-10-01**, **PDF64.05MB**, **182 pages**,publisher와이미디어 and digitalISSN25083597. Public contents explicitly state 표지모델 미스맥심 쥬. No book ISBN is supplied.

The ordinary purchase price is **KRW5,500**,with enabled eBook-purchase control. KRW4,950 is labelled coupon price and excluded; sam subscription availability is not a purchase-price observation. TTS is unavailable. No preview,reader,download,login,age verification,purchase,API or image collection occurred.

The [one-record scoped import](korean-maxim-october-2026-kyobo-digital-import.json) adds a Kyobo-specific purchase edition under existing No.281. Its [capture](korean-maxim-october-2026-kyobo-digital-capture.json), [genuine before snapshot](korean-maxim-october-2026-kyobo-digital-before.json), [read-back](korean-maxim-october-2026-kyobo-digital-readback.json) and [exact verification](korean-maxim-october-2026-kyobo-digital-db-verification.json) confirm one new edition/listing/active purchase-price observation. All earlier edition payloads,old prices/history,person profiles,credit content and media URLs/provenance are preserved; repeated work-cover upsert may refresh its update timestamp. Existing A 쥬,B 조아 and subscriberS 유디 credits remain intact; only the Kyobo PDF is credited from its own public contents. No new work,model or image is introduced. Public Kyobo metadata returns182pages and active digital_retail KRW5,500.

Manual source remains disabled/review,image reuse remains unresolved,and the batch committed before another source list.

The cumulative347-record ledger validates without reapplying old imports. Exact October Kyobo read-back,the full cohort audit and global read-only public-catalog verifier passed after commit:110 works,203 editions,366 listing-item references and136 media references match,with zero integrity failures. New182-page metadata belongs only to Kyobo's purchase PDF;sam is separate. Missing date/page/cover counts are8/85/173. Global editions are6,820,listings8,343 and observations8,392. No subsequent source list was opened before verification.

## November Kyobo discovery — no exact indexed match

A focused exact-title/site query on2026-10-25 returned no matching November2026 Kyobo product; the broader fallback result was an unrelated2024 issue. The [discovery capture](korean-maxim-november-2026-kyobo-discovery-no-match.json) records zero accepted items and zero database rows required. This is not proof of nonexistence or future release/availability. No digital date,price or edition was inferred from November print or nearby months. The zero-row discovery list was finished before May metadata collection.

## MAXIM May 2026 — public Kyobo-specific PDF metadata

The [public Kyobo ebook page](https://ebook-product.kyobobook.co.kr/dig/epd/ebook/E000012932768) was checked on2026-10-25. It identifies May2026,publisher와이미디어,release **2026-05-01**, **PDF57.50MB**, **180 pages** and digitalISSN25083597. Public contents explicitly state 표지모델 미스맥심 채솔; the existing canonical 채솔 identity is reused. No book ISBN is supplied.

The ordinary ownership price is **KRW5,500**,with sticky purchase total and enabled eBook-purchase control. KRW4,950 is coupon-only and excluded from the ordinary offer; sam subscription is separate. TTS is unavailable. No preview,reader,download,login,age verification,purchase,API or image collection occurred.

The [one-record scoped import](korean-maxim-may-2026-kyobo-digital-import.json) adds a Kyobo-specific edition under existing No.276. Its [capture](korean-maxim-may-2026-kyobo-digital-capture.json), [genuine before snapshot](korean-maxim-may-2026-kyobo-digital-before.json), [read-back](korean-maxim-may-2026-kyobo-digital-readback.json) and [exact verification](korean-maxim-may-2026-kyobo-digital-db-verification.json) confirm one new edition/listing/active purchase-price observation. All earlier edition payloads,prices/history,person profile,credit content and media remain preserved. File metadata is not copied into YES24PDF or A/B print. No new work,model or image is introduced. Public Kyobo metadata returns180pages and active digital_retail KRW5,500. Manual source stays disabled/review; image reuse remains unresolved. The batch committed before another source list.

The cumulative348-record ledger validates without reapplying old imports. Exact May Kyobo read-back,the full cohort audit and global read-only public-catalog verifier passed after commit:110 works,204 editions,367 listing-item references and136 media references match,with zero integrity failures. November discovery accepted zero rows and no record was fabricated. New180-page metadata belongs only to Kyobo's May PDF. Missing date/page/cover counts are8/85/174. Global editions are6,821,listings8,344 and observations8,393. No subsequent source list was opened before verification.

## MAXIM April 2026 — public Kyobo-specific PDF metadata

The [public Kyobo ebook page](https://ebook-product.kyobobook.co.kr/dig/epd/ebook/E000012761487) was checked on2026-10-25. It identifies April2026,publisher와이미디어,release **2026-04-01**, **PDF78.20MB**, **182 pages** and digitalISSN25083597. Public contents explicitly state 표지모델 치어리더 김나연; the existing canonical 김나연 identity is reused. No book ISBN is supplied. TTS is listed available on this item,not copied from neighbouring issues.

The ordinary ownership price is **KRW5,500**,with sticky purchase total and enabled purchase control. KRW4,950 is coupon-only and excluded from the ordinary offer; sam subscription is separate. No preview,reader,download,login,age verification,purchase,API or image collection occurred.

The [one-record scoped import](korean-maxim-april-2026-kyobo-digital-import.json) adds a Kyobo-specific edition under existing No.275. Its [capture](korean-maxim-april-2026-kyobo-digital-capture.json), [genuine before snapshot](korean-maxim-april-2026-kyobo-digital-before.json), [read-back](korean-maxim-april-2026-kyobo-digital-readback.json) and [exact verification](korean-maxim-april-2026-kyobo-digital-db-verification.json) confirm one new edition/listing/active purchase-price observation. All earlier edition payloads,prices/history,person profile,credit content and media URLs/provenance remain preserved; repeated work-cover upsert may refresh its update timestamp. Existing publisher/retailer print-date assertions and subscriber unknowns remain untouched. File metadata is not copied into YES24PDF or A/B/S print. No new work,model or image is introduced. Public Kyobo metadata returns182pages and active digital_retail KRW5,500. Manual source stays disabled/review,image reuse remains unresolved,and the batch committed before another source list.

The cumulative349-record ledger validates without reapplying old imports. Exact April Kyobo read-back,the full cohort audit and global read-only public-catalog verifier passed after commit:110 works,205 editions,368 listing-item references and136 media references match,with zero integrity failures. New182-page metadata and TTS availability belong only to Kyobo's April PDF. Missing date/page/cover counts are8/85/175. Global editions are6,822,listings8,345 and observations8,394. No subsequent source list was opened before verification.

## MAXIM March 2026 — public Kyobo PDF and source-specific ISSN

The [public Kyobo ebook page](https://ebook-product.kyobobook.co.kr/dig/epd/ebook/E000012645261) was checked on2026-10-25. It identifies March2026,publisher와이미디어,release **2026-03-01**, **PDF93.12MB** and **181 pages**. This page displays **ISSN22334270**,not the25083597 shown on later issues; its exact assertion is preserved without treating it as ISBN or relabelling it as an independently verified electronicISSN. Public contents explicitly state 표지모델 치어리더 김도아; the existing canonical 김도아 identity is reused. TTS is listed available. The separately displayed print date2026-02-27 is context only and does not overwrite existing print metadata.

The ordinary ownership price is **KRW5,500**,with sticky purchase total and enabled purchase control. KRW4,950 is coupon-only and excluded; sam subscription is separate. No preview,reader,download,login,age verification,purchase,API or image collection occurred.

The [one-record scoped import](korean-maxim-march-2026-kyobo-digital-import.json) adds a Kyobo-specific edition under existing No.274. Its [capture](korean-maxim-march-2026-kyobo-digital-capture.json), [genuine before snapshot](korean-maxim-march-2026-kyobo-digital-before.json), [read-back](korean-maxim-march-2026-kyobo-digital-readback.json) and [exact verification](korean-maxim-march-2026-kyobo-digital-db-verification.json) confirm one new edition/listing/active purchase-price observation. All earlier edition payloads,prices/history,person profile,credit content and media remain preserved. File metadata is not copied into YES24PDF or print. No new work,model or image is introduced. Public Kyobo metadata returns181pages and active digital_retail KRW5,500. Manual source stays disabled/review,image reuse remains unresolved,and the batch committed before another source list.

The cumulative350-record ledger validates without reapplying old imports. Exact March Kyobo read-back,the full cohort audit and global read-only public-catalog verifier passed after commit:110 works,206 editions,369 listing-item references and136 media references match,with zero integrity failures. New181-page metadata and displayedISSN22334270 are scoped to Kyobo's March PDF. Missing date/page/cover counts are8/85/176. Global editions are6,823,listings8,346 and observations8,395. No subsequent source list was opened before verification.

## MAXIM February 2026 — Kyobo purchase PDF and placeholder ISSN

The [public Kyobo purchase page](https://ebook-product.kyobobook.co.kr/dig/epd/ebook/E000012542859), reached through its visible sam-to-eBook link, identifies publication **2026-02-02**, **183 pages**, PDF **100.38MB**, and TTS available. Ordinary purchase is **KRW5,500** with an enabled purchase control; conditional coupon KRW4,950 and sam subscription are excluded. Displayed ISSN `00000000` is a placeholder retained in source evidence; no verified identifier or ISBN is inferred. Linked print January23 is context only and does not replace the existing publisher January24 assertion.

Public contents mention 리리,첼설아 and 섹밍 without an explicit digital-cover assignment. The importer requires an issue-level verified cover credit; its initial validation rejected the credit-free record before any write. The corrected scoped record retains the already sourced print issue credit solely for validation, without identifying the digital cover. Existing A/B/S credits, profiles, editions, prices and images remain preserved. No images were accepted, and reuse permission remains unconfirmed.

Evidence: [capture](korean-maxim-february-2026-kyobo-digital-capture.json), [scoped import](korean-maxim-february-2026-kyobo-digital-import.json), [before](korean-maxim-february-2026-kyobo-digital-before.json), [committed read-back](korean-maxim-february-2026-kyobo-digital-committed-readback.json), [verification](korean-maxim-february-2026-kyobo-digital-db-verification.json). The earlier file named readback records the unchanged database after rejected validation; the committed file is authoritative. Exactly one edition, listing and observation were added, with zero media added. Exact read-back, the 351-record cumulative validation, cohort audit and global public catalog verification passed. The cohort now covers110 works/207 editions/370 item references/136 media references with zero integrity failures. No next source list was opened before verification.

## MAXIM January 2026 — Kyobo purchase PDF

The [public Kyobo purchase page](https://ebook-product.kyobobook.co.kr/dig/epd/ebook/E000012407155), reached through its visible sam-to-eBook link, identifies **2026-01-02**, **165 pages**, PDF **123.61MB**, and TTS available. Ordinary purchase is **KRW5,500** with an enabled purchase control; conditional coupon KRW4,950 and sam subscription are excluded. Displayed ISSN `00000000` is retained as a placeholder anomaly, with no verified ISSN or book ISBN inferred. Public contents name the 치어리더 조예린 theme, consistent with the existing sourced issue credit; lineup names are not additional cover credits. Linked print2025-12-26 is context only.

Exactly one retailer-specific digital edition, listing and price observation were committed. Existing print/YES24PDF metadata, people, credits, media and historical observations were preserved by exact read-back (update timestamps excluded from content comparison). No image was accepted, no reader/preview was opened, and no API, login, purchase or rights-holder message was used. Kyobo remains disabled/review; image reuse permission is unconfirmed.

Evidence: [capture](korean-maxim-january-2026-kyobo-digital-capture.json), [scoped import](korean-maxim-january-2026-kyobo-digital-import.json), [before](korean-maxim-january-2026-kyobo-digital-before.json), [read-back](korean-maxim-january-2026-kyobo-digital-readback.json), [verification](korean-maxim-january-2026-kyobo-digital-db-verification.json). Exact read-back,352-record cumulative validation,cohort audit and global public catalog verification all passed. No next source list was opened before verification.

## MAXIM April 2025 S — exact eBay variation asking offer

A public subscriber-date search led to [eBay item335870483825](https://www.ebay.com.my/itm/335870483825), which offers A/B/S choices. Selecting **S type** visibly changed the URL to [variation545414919616](https://www.ebay.com.my/itm/335870483825?var=545414919616) and changed the asking price from base US$15 to **US$25**. The selected page retained an enabled quantity field,5-available display and Buy It Now control. Seller bargainkorea claims Brand New condition and explicitly maps S to Myua; this corroborates the existing 뮤아 credit without creating another person. Shipping **US$15.50** is the quote shown for destination63000, not a worldwide shipping price. Seller import-fee exclusions remain explicit.

The page identifies April2025/issue263 but supplies no original S publication day. August13,2026 is a listing revision timestamp. The aggregate17-sold count is neither S-specific sales history nor a verified final paid price. A conflicting generic contributor field and barcode-like9772233427008 labelled ISSN were not promoted into canonical metadata. No date, pages, original retail price or ISBN was inferred from A/B/PDF. No seller contact, purchase, login or image collection occurred. Source ebay-public-manual stays disabled/review; public access does not establish permission for automation or image reuse.

One new listing and observation were committed under the existing S edition, with no new work/edition/media. Exact read-back preserved all prior editions, profiles, credits, media, listings and observations (update timestamps excluded from content comparison). [Capture](korean-maxim-april-2025-s-ebay-capture.json), [scoped import](korean-maxim-april-2025-s-ebay-import.json), [before](korean-maxim-april-2025-s-ebay-before.json), [read-back](korean-maxim-april-2025-s-ebay-readback.json), [verification](korean-maxim-april-2025-s-ebay-db-verification.json). Exact read-back,353-record cumulative validation,cohort audit and global public catalog verification passed before further source collection. The date search did not resolve the original publication day; the gap remains.

## eBay collection route — explicit restriction verified

The [eBay Malaysia User Agreement](https://www.ebay.com.my/help/policies/member-behaviour-policies/user-agreement?id=4259) was read in the public rendered browser on2026-10-25 after the S-variant batch. Section3 explicitly prohibits automated access, including scrapers, and requires express rightsholder permission for reproduction/display of protected content. Section9 describes catalog-content use for eBay listings; it does not approve reuse in MuseBooks. The page displays June16,2021 as its effective date for existing users; this is not a newly issued2026 policy.

**Decision: exclude eBay from further automated product collection, including browser automation, pending explicit platform permission.** A manual_page_capture label does not establish an exemption for an agent-operated browser. The source ebay-public-manual was already disabled/review; that operational disable remains appropriate. The previously captured S offer remains a historical source assertion, not evidence of collection or image reuse permission. No images were collected, no permission message was sent, and no API alternative was introduced. This corrects the route assessment without deleting historical price evidence or asserting permission retroactively.

[Policy capture and route decision](korean-ebay-collection-policy-capture.json). This policy review accepted zero product records and requires zero product database rows. It must not generate a fake listing or zero-price observation. Continue bibliographic work through other sources after checking their applicable terms; do not treat publicly accessible pages as automatically permission-approved. The full catalog goal remains incomplete because exact-asset reuse grants and other source permissions are still unverified.

## Exact-asset clearance register and runtime limitation

The [image clearance register](korean-image-clearance-register.json) inventories the current353-record ledger without making network requests or database writes. It groups **255 URL-reference occurrences into121 distinct exact asset URLs**, including136 explicit media references plus work/edition/listing cover references. **Zero assets have verified MuseBooks reuse permission**; all121 are marked unconfirmed. Repeated references are not additional images or additional grants. Every entry retains its associated work/edition and source URLs for subsequent rights review. This is an evidence register, not a license declaration.

Code inspection found that CatalogMedia stores URL provenance and source attribution without a permission field. publicGallery checks HTTPS/source URLs and duplicate image URLs, but does not establish or enforce exact-asset permission. Consequently, prior successful gallery/catalog verification proves record/provenance integrity only. It must not be cited as image clearance. This review changed no runtime image delivery, deleted no stored provenance and promoted no image to approved status.

Remaining work is concrete: obtain an applicable grant or exact approved-use label for each desired asset; record the allowed site/use, restrictions and permission evidence; then enforce that permission state before treating an image as cleared for delivery. Hanmoto's generic conditional policy cannot clear exact assets labelled unknown, and retailer/public source access cannot substitute for a reuse grant. No outbound request is sent without user authorization. Other bibliographic gaps remain open in the coverage audit. This inventory accepts zero new product records and requires zero product database rows; the existing353-record imported ledger is unchanged.

## Pyo Eunji — KADOKAWA cover-use route review and requested stop

The [original KADOKAWA corporate/media guidance](https://www.kadokawa.co.jp/support/b/media/) was checked in the rendered browser on2026-10-25. It provides conditional cover use for qualifying book introductions, subject to official product-page saveability, special conditions, unaltered/band-free cover and prescribed title/author/ＫＡＤＯＫＡＷＡ-imprint attribution. Advertising, merchandise/sales and other non-introduction uses are outside that route; interiors require separate inquiry. This is not a general scraping grant or a blanket commercial image license.

For Pyo Eunji's 輪舞曲 (ISBN9784048976268), the existing exact Hanmoto result marks cover reuse unknown. The linked [special-conditions PDF](https://media-cdn.kadokawa.co.jp/ijwyneak/hgdliokbjr/shoei.pdf) opened but exposed no readable text through this browser, so this review cannot establish title-specific eligibility or absence from exceptions. The policy alone does not clear the exact cover, companion digital cover or interior images for MuseBooks. All Pyo Eunji assets remain unconfirmed; no image was downloaded/approved, no rights-holder request was sent and no product/database row was added.

[Policy review evidence](korean-photobook-pyo-eunji-kadokawa-cover-policy-review.json). The current review is recorded with those limits. At the user's request to finish this model and stop, collection stops here and the broad goal is paused, not completed. Resume only on user request; the353-record ledger and prior committed evidence remain intact.

## Cohort-wide coverage and import audit — 2026-10-25

The [read-only cohort audit](korean-catalog-coverage-audit-2026-10-25.json) checked the current353-record ledger against a repeatable-read PostgreSQL snapshot: **110 works,208 editions,372 listing-item references and136 explicit media references**. It found **zero integrity failures**. Every referenced work/edition has the expected Korean classification and ownership; every source/external-item link exists; every historical observation key resolves to the expected listing, amount,currency,status and evidence; every explicit image reference retains its expected URL and source provenance. Repeated observation keys were also checked for cross-listing collisions. This proves the reviewed imports are present; it does not prove complete source coverage, current stock or image rights.

| Requirement | Current authoritative evidence | Remaining work |
| --- | --- | --- |
| Photobooks separate from magazines |72 photobook works/79 editions;38 magazine works/127 editions; no classification/ownership failures | Continue applying the same identity rules to newly verified titles/variants |
| Publication dates |198 editions have a date;59 dated editions use less than day precision |8 edition dates remain unknown; do not transfer A/PDF dates to subscriber or commemorative covers. Stored dates/pages can still have unresolved source conflicts, including SANTORINI and July2026 A |
| Prices and availability |All372 ledger item references match persisted observations;208 editions are audited |5 subscriber editions have no listing;140 editions have no stored active listing. This includes legitimate unavailable/unknown cases and is not a current-stock recheck |
| Model provenance |Existing credits and people are linked to the reviewed works |Zero linked people lack person-level provenance URLs after source verification and the JISOO duplicate-credit correction; verify each new subject against exact source evidence |
| Cover and other images |136 explicit attributed references persist; public source-specific galleries verified in batch reports |178 editions have blank canonical covers. URL attribution is not permission; no exact captured image is marked reuse-approved in this guide |
| Permission-approved routes |Hanmoto documents conditional reuse for exact assets marked利用可 |Both checked Korean-model titles,Candid andRondo,are marked permission unknown. Written/exact-asset permission remains unresolved; no automated source is approved by this audit |

The8 unknown dates belong to six MAXIM subscriber S covers and two Pyo Eunji commemorative/annual editions. July2026 B now has its own exact retailer date. The full JSON lists each edition's source URL, variant and gaps. The anthology-source batches verified missing model sources, and the JISOO correction consolidated its duplicate work credit under the sourced canonical subject. No linked person now lacks a provenance URL. Unknown fields are retained explicitly instead of fabricated. No new source list was collected or database rows changed during this audit.

The reusable command is [backend/cmd/korean-catalog-audit/main.go](../backend/cmd/korean-catalog-audit/main.go). From `backend`, run `go run .\cmd\korean-catalog-audit -manifest ..\docs\korean-maxim-issue-review.json -output ..\docs\korean-catalog-coverage-audit-2026-10-25.json`. It uses a PostgreSQL transaction declaredREAD ONLY and writes only the local JSON report. It does not call retailer APIs, refresh source availability, infer licenses or mark this goal complete.

## Catalog and permission state

The cumulative review ledger now contains **353 imported records**. Records can refine an existing edition or add another source offer; they are not a count of distinct books.

| Reviewed scope | Records | Distinct works | Distinct editions | Listing items | Editions with listing items |
| --- | ---: | ---: | ---: | ---: | ---: |
| Standalone photobooks, including model-specific digital pictorials | 164 | 72 | 79 | 102 | 79 |
| MAXIM magazine issues and B-SIDE issues | 189 | 38 | 129 | 270 | 124 |

All79 reviewed photobook editions have a listing observation, including unavailable displayed prices; this does not establish current purchasability. Five MAXIM subscriber editions are metadata-only. The latest source batch adds an exact April2025 S eBay variation asking offer,following January–October Kyobo and earlier retailer/model-source batches; November discovery accepted no item. The preceding batch confirms February2026 publisher A/B/S details. The cohort-wide audit above checks every imported reference and identifies the remaining gaps. Earlier sections and their capture/import/verification files preserve source-specific history, date conflicts, seller details and unresolved fields.

The latest exact batch audit and global read-only catalog verifier passed. One formerly split B-cover work is now superseded under its September issue, explaining the one-work decrease in the physical count without losing an edition or observation. There are 110 published Korean works represented by the ledger. Public catalog totals are **338 physical works** and **5,026 digital works**. Database-wide totals, including material outside this Korean capture, are **6,064 works, 6,825 editions, 8,349 listings, 34 sources and 8,398 listing observations**. There are 1,509 unlinked verified listings and 179 editions with pending covers across the full database.

Follow the requested import cadence for future collection: finish one source-list batch, save its scoped import file and cumulative ledger entry, validate it, commit the scoped batch to PostgreSQL, and verify the database before starting another source list. Earlier committed records need not be reapplied. The required accounts migration was applied with explicit user approval; subsequent imports and read-back verification succeeded.

This continuation used public rendered retailer pages and contemporaneous reporting. No retailer API or API key was used. YES24 remains `review` with automated collection disabled; this work records manual page captures only. Earlier MAXIM/retailer image fields remain blank at their original checkpoints. The artist-store batches record nine remote image references with source attribution: Rondo cover plus three additional product images, annual fanclub cover plus three additional images, and one first-edition promotional graphic. The October 2026 MAXIM refresh adds one YES24 digital cover, and the Aladin list adds distinct A/B print covers, followed by 19 explicit publisher-batch media references (17 edition and two listing rows), then three S seller photos, followed by two commemorative-cover/promotion URLs, then two KADOKAWA digital covers, then four BE JOYFUL edition/listing media rows using two image URLs, then four 김설화 26 edition/listing rows using two image URLs, then two SANTORINI edition/listing cover rows using one URL, then 19 November 2026 publisher edition/listing media rows using 17 URLs, then two November Aladin listing-cover references, then 19 September publisher edition/listing references using 17 URLs, then three DJ SODA publisher cover/preview references, then one Candid Apple digital cover reference, then two August2026 Aladin print cover references, then21 April2026 publisher edition/listing references using19 URLs, then19 February2026 publisher edition/listing references using17 URLs, then one July2026 B Aladin listing-cover reference, then one July2026 A Aladin listing-cover reference, bringing this manifest to136 explicit media references across121 distinct URLs; automatic cover rows are additional; no pixels are mirrored and no reuse license is asserted. No MAXIM/YES24 permission request has been sent. The new B-cut records describe digital PDFs, with month precision where no exact day was exposed; page counts and gallery images still need product-page access. Print editions, cover variants, print-only supplements, and used listings need their own exact listings before they can be represented as physical editions.


The read-only [work snapshot command](../backend/cmd/catalog-work-snapshot/main.go) saves a repeatable-read view of the public book, work, credits, alias mappings, retained person rows, listings, observations and media. It requires an explicit work ID and output path and refuses to overwrite an existing evidence file. From backend: `go run .\cmd\catalog-work-snapshot -work WORK_ID -output ..\docs\NEW_EVIDENCE_FILE.json`. This tool performs no database writes or source collection.

Password4 and Password5 digital editions are now imported and verified independently of their print specifications. July2026 B date/pages are now verified. July A retailer price/cover are now verified and its date conflict recorded. The Kyobo SANTORINI conflict is now directly verified and stored; publisher or physical-copy evidence is needed to resolve it. The newer Uhyun asking offer is now directly verified and imported. January through October Kyobo purchase PDFs are now verified. November discovery accepted no product. Continue with non-eBay subscriber-date sources and exact-asset reuse permission. eBay automation is excluded by the policy review above. Do not infer missing dates or bypass gates. Continue addressing unknown MAXIM subscriber dates, page counts, canonical covers and exact-asset reuse permission. Each accepted source batch must commit and pass read-back before the next list.

## Korean MAXQ Secret B additions — Choi Sohyeon and Yang Yuna

Two more creator-led photobooks are now in the catalog. Choi Sohyeon's physical *Secret B* No. 2 is a 116-page, 220 × 285 mm edition with a 2022-12-23 publication date; Spomax's product page identifies the exact book, and its Gmarket-attributed specification page provides the pagination and dimensions. A 2020 Twig24 profile identifies Choi as an Instagram influencer. ([Spomax product](https://spomax.kr/product/%ED%8A%B9%EA%B8%89%ED%98%9C%ED%83%9D%EC%9D%B4%EB%B2%A4%ED%8A%B8-2%ED%98%B8-%EB%A8%B8%EC%8A%AC%ED%80%B8-%EC%B5%9C%EC%86%8C%ED%98%84-%ED%99%94%EB%B3%B4%EC%A7%91/5115/), [Gmarket/Spomax specifications](https://item.gmarket.co.kr/Item?goodsCode=2833706378), [Sports Seoul release report](https://www.sportsseoul.com/news/read/1184574), [Twig24 profile](https://www.twig24.com/news/entertainments/2020/09/20/20200920500023))

Yang Yuna's digital *Secret B* Vol. 15 is an e-book/PDF. MAXQ's 2024-05-28 article calls her a fitness model, trainer, and influencer, names her as the solo model, and announces release through e-book sites/apps for May 31. Aladin's e-book series record lists the exact Vol. 15 title and PDF from 2024-06; this date difference is recorded in its manifest, while the publisher-announced date is stored. ([MAXQ publisher article](https://maxq.kr/articles/chimyeongjeokine-seksi-beigeulnyeo-yangyuna-sikeuritbi-hwabojip-seongonggae), [Aladin Secret B series record](https://www.aladin.co.kr/m/mseriesitem.aspx?srid=927494), [Digital Times/Daum profile](https://v.daum.net/v/X0woHRj4Ce))

Both imports passed their scoped read-only audits with zero integrity findings. Neither has a listing or media row; no price was recorded. Their covers remain unconfirmed for R2 reuse. Manifests, snapshots, and audits: [Choi Sohyeon No. 2](korean-secret-b-2-choi-sohyeon-import.json), [Yang Yuna Vol. 15](korean-secret-b-15-yang-yuna-import.json).

## Korean MAXQ Secret B additions — Jeong Hanna and Yoon Na-gyeom

Added two verified digital photobook works. Aladin lists Secret B Vol. 11 featuring Jeong Hanna (정한나) as a PDF from 2022-08; Sports Seoul confirms the No. 11 shoot, and Maeil Business identifies her as a fitness influencer. RIDI lists the separately titled Secret B + MAXQ Compilation Vol. 02 featuring Yoon Na-gyeom (윤나겸) as a 65-page PDF dated 2022-06-02, combining selected and unreleased Secret B/MAXQ images. Yoon's influencer status is supported by Electronic Times' model-influencer coverage. A live read-only title/person check found no Vol. 11 work for Jeong Hanna and only the already cataloged Vol. 9 work for Yoon; no Vol. 02 match was present.

Both metadata-only records were committed, read back, and audited: each has one work and one digital edition, zero listing/media references, and zero integrity findings. Jeong Hanna's page count and exact release day remain unknown. Vol. 02's possible image overlap with Vol. 9 has not been checked; the distinct compilation title is retained as its own work. No cover or paid PDF was copied to R2 because exact-image reuse permission is unconfirmed.

Sources: [Aladin Secret B series](https://www.aladin.co.kr/m/mseriesitem.aspx?srid=927494), [Sports Seoul on Jeong Hanna's Vol. 11 shoot](https://www.sportsseoul.com/news/read/1132455), [Maeil Business influencer profile](https://www.mk.co.kr/news/entertain/10007223), [RIDI Yoon Na-gyeom Vol. 02](https://ridibooks.com/books/3563000137), [Electronic Times Yoon Na-gyeom profile](https://www.etnews.com/20220916000275). Manifests, readbacks, and scoped audits: [Jeong Hanna](korean-secret-b-11-jeong-hanna-import.json), [Yoon Na-gyeom](korean-secret-b-maxq-vol02-yoon-na-gyeom-import.json).

## Korean MAXQ Secret B and Special Edition additions — 2026-10-30

Five exact products have been added as separate photobook records: digital Secret B Vol. 6 (Baek Seonghye), Vol. 13 (Kim Dahye), and Vol. 14 (Choi Sohyeon); physical Secret B No. 3 (Baek Seonghye); and digital MAXQ Special Edition Vol. 1 (Gong Minseo, Son Sohee, Choi Seolhwa). RIDI/Aladin and Spomax identify the exact numbered products and available edition metadata. Baek's influencer status is explicit in Korean press. Choi Seolhwa's contemporary profile documents her YouTube fitness channel and social content; Kim Dahye's matching Instagram/fitness-creator evidence is credible but the reviewed sources do not consistently call her an influencer. All five products are distinct titles/retail products; image-level overlap for same-subject titles is not verified and no photographic uniqueness is claimed.

The five manifest records validated and committed. Each scoped database audit found one work, one edition, no listings or media, and zero integrity findings. Secret B No. 3 is stored with August 2023 month precision and unknown pagination because retailers report both 116 and 166 pages and disagree on exact dates. Vol. 6 retains November 2020 month precision with no verified page count. Vol. 13 and Vol. 14 have 42 and 41 pages respectively; Special Edition Vol. 1 has 50 pages. No cover or PDF was copied to R2; reuse permission is unconfirmed and exact-photo overlap remains open for the relevant works.

Sources: [Aladin Secret B catalogue](https://www.aladin.co.kr/m/mseriesitem.aspx?srid=927494), [RIDI Vol. 13](https://ridibooks.com/books/3563000173), [RIDI Vol. 14](https://ridibooks.com/books/3563000182), [RIDI Special Edition Vol. 1](https://ridibooks.com/books/3563000054), [Spomax No. 3](https://spomax.kr/product/%EC%8B%9C%ED%81%AC%EB%A6%BF-b-3%ED%98%B8-%EB%A8%B8%EC%8A%AC%ED%80%B8-%EB%B0%B1%EC%84%B1%ED%98%9C-%ED%99%94%EB%B3%B4%EC%A7%91/5130/), [FNEWSTV No. 3 release article](https://www.fnewstv.com/news/newsview.php?ncode=1065554021938672), [Aju Economy on Baek Seonghye](https://www.ajunews.com/view/20220604233643912?photoIdx=0&term=0), [MAXQ/Daum Kim Dahye profile](https://v.daum.net/v/VWH0AnkUCo), [Xports News on Choi Sohyeon](https://www.xportsnews.com/article/1457242), [Big Data News on Choi Seolhwa](https://www.thebigdata.co.kr/view.php?ud=202007161721581840992c130dbe_23). Manifests, snapshots, and audits are in matching `korean-secret-b-*` and `korean-maxq-special-edition-vol01-*` files in `docs/`.


## Pyo Eunji creator photobooks — 2026-10-30

Fifteen further records for Korean model/YouTuber Pyo Eunji have been added from publisher, retailer, and official fan-club pages: nine Japanese digital photobooks and six Comiket booklets. The digital products include *Tokyo Life* (76 pages), *Bold Amaryllis* (80 pages), *Omotenashi* (73 pages), *Icha Icha Joshi Kai*, *Juicy*, *Kisekae Oneesan*, two DIGVII other-cut books, and *Time yo, Tomare*. The physical products are DokiDoki, PuniPuni, and AnotherMe from C105, plus Operation: Cute Today Too, Under Construction, and Nekomimi Gamer from C107. The official store specifies B5 dimensions and pagination for each booklet; C105/C107 dates are stored at month precision based on the event month. Pyo's official profile describes her as a Korean gravure model and YouTuber, and publisher/retailer sources further identify her as an influencer.

All 15 metadata records were validated and committed. Their scoped audit found 15 works, 15 editions, zero listing/media references, zero integrity findings, and zero people missing provenance. Page counts were left unknown where the source omitted them. No cover or paid file was copied to R2; the reviewed pages provide no exact-asset reuse permission.

Sources: [Pyo Eunji official profile](https://pyoeunji.com/ko/pages/profile), [C105 booklet set](https://pyoeunji.com/ko/products/c105set2), [C107 booklet set](https://pyoeunji.com/products/%E3%82%B3%E3%83%9F%E3%82%B1c107-%E6%96%B0%E5%88%8A%E3%82%BB%E3%83%83%E3%83%88), [Tokyo Life on Rakuten Kobo](https://www.kobo.com/us/en/ebook/1xpXER34kjaxPRcqg2CQCA), [Bold Amaryllis on Rakuten](https://books.rakuten.co.jp/rk/1203f5b17e723e96a497f1f2ed16084b/), [Omotenashi on Shueisha Grajapa](https://www.grajapa.shueisha.co.jp/item/detail/gravure/f5c94ac05eccfae8d0e6dca4147d1737), [Icha Icha Joshi Kai on Weekly Playboy](https://wpb.shueisha.co.jp/gravure/20230423-119184/), [Juicy on Kodansha](https://www.kodansha.co.jp/book/products/0000402926), [Kisekae Oneesan on Rakuten](https://books.rakuten.co.jp/rk/b0e746abeae13d33811185fbde413049/), [DIGVII co-featured photobook on Rakuten](https://books.rakuten.co.jp/rk/7ce4ae2a33e93e71a0602dbb7bba2a36/), and [Time yo, Tomare on Weekly Playboy](https://wpb.shueisha.co.jp/gravure/movie/20260808-132428/). The [import manifest](korean-pyo-eunji-creator-photobooks-import.json) and [database audit](korean-pyo-eunji-creator-photobooks-db-verification.json) preserve the complete list and field-level provenance.


## MAXQ Special Edition Vol. 10 - Park Eunhye

RIDI lists *MAXQ Special Edition 10ho* as a 33-page PDF e-book published on 2024-06-27 by MAXQ International. Its description calls the Special Edition a selection of high-quality MAXQ pictorials not previously released online. Sports Seoul identifies Park Eunhye as a YouTuber and reports that she operated the JamongTube channel. A live repeatable-read catalog check found Park's three existing MAXQ/Secret B works but no Vol. 10 title or RIDI product URL. The separate product was imported with image overlap left unresolved; the record does not claim unique photographs.

The scoped database audit reports one work, one digital edition, no listing/media rows, zero integrity findings, and zero people missing provenance. The public catalog verifier reported 355 physical and 5,081 digital works. No cover or paid PDF was copied to R2 because exact-asset reuse permission remains unverified. Sources: [RIDI product](https://ridibooks.com/books/3563000201), [Sports Seoul profile](https://www.sportsseoul.com/news/read/948176). Evidence: [manifest](korean-maxq-special-edition-vol10-park-eunhye-import.json), [read-back](korean-maxq-special-edition-vol10-park-eunhye-db-readback.json), [audit](korean-maxq-special-edition-vol10-park-eunhye-db-verification.json).

## MAXQ Special Edition Vol. 5 — Jeong Hanna

RIDI identifies the exact digital product as *MAXQ Special Edition 5호*: a 29-page PDF e-book released 2021-04-30. MAXQ's publisher article identifies Jeong Hanna as its solo Vol. 5 muse and cover model and calls the issue an online photobook. The live catalog had no match for RIDI product 3563000091; Hanna already had a separate Secret B Vol. 11 work. The new Vol. 5 work is cataloged with a publisher-sourced featured credit. Photo overlap with her other MAXQ editions remains unchecked. No cover or paid file was copied to R2; exact-image reuse permission is unconfirmed. Sources: [RIDI product](https://ridibooks.com/books/3563000091), [MAXQ publisher article](https://maxq.kr/articles/wanpannyeo-jeonghanna-maekseukyu-onrain-migonggae-hwabojip-seupesyeol-edisyeoneuro-choegang-seksimi-balsan), [Sports Seoul](https://www.sportsseoul.com/news/read/1040486). Database records: [import manifest](korean-maxq-special-edition-vol05-jeong-hanna-2021-import.json), [read-only snapshot](korean-maxq-special-edition-vol05-jeong-hanna-2021-db-readback.json), [scoped audit](korean-maxq-special-edition-vol05-jeong-hanna-2021-db-verification.json).

## MAXQ Special Edition Vol. 9 — Kim Minjeong

RIDI identifies the exact digital product as *MAXQ Special Edition 9호*, a 32-page PDF e-book released 2024-02-05. Finance Today (using a MAXQ photo credit) reports Kim Minjeong as Vol. 9 cover model; MAXQ's own content documents her @min.joy___ Instagram, fitness teaching, and exercise videos. The exact product URL/title and Korean featured name were absent from the live catalog, so the work and its featured creator were added as a separate digital photobook. The June 2024 press article names the issue and model but does not state a separate ebook release date. Image overlap with other MAXQ material has not been checked. No image or paid file was copied to R2 because exact-asset reuse permission is unconfirmed. Sources: [RIDI product](https://ridibooks.com/books/3563000187), [Finance Today / MAXQ](https://www.fntoday.co.kr/news/articleView.html?idxno=321826), [MAXQ profile story](https://v.daum.net/v/kO4iSlRryD?f=p). Records: [manifest](korean-maxq-special-edition-vol09-kim-minjeong-2024-import.json), [snapshot](korean-maxq-special-edition-vol09-kim-minjeong-2024-db-readback.json), [audit](korean-maxq-special-edition-vol09-kim-minjeong-2024-db-verification.json).

## Korean influencer photobooks — Rustic Studio 24SS and Kim Woo-hyun Nxde

Wadiz's Rustic Studio campaign identifies 러스틱 사진집 24SS as a three-version men's body photobook and names the model-specific versions for 간현배 (KAN HYEON BAE), 김동윤 (KIM DONG YOON), and 심민섭 (SHIM MIN SUP). The same campaign describes Kan as a national-team gymnast and influencer, Kim as a fitness model and influencer, and Shim as a climbing influencer. The exact campaign ran 2023-12-06 to 2023-12-20; those are campaign dates, not a bibliographic publication date. It omits page count, ISBN, formal publisher imprint, and actual release date. The three physical editions are represented separately under one work, without asserting that their interiors are unique.

Fanding identifies Kim Woo-hyun's successful 2023 campaign as WOO HYEON'S Nxde PhotoBook. The campaign offers two separately selectable physical rewards, EP 1: Mandarin and EP 2: Cyber Punk; its delivery-enabled rewards and the creator's community post titled “우현의 종이 화보집 후기” support the paper-book classification. Its scheduled reward date (2023-08-16) is not treated as an actual release or shipment date. No page count, ISBN, publisher imprint, or actual release date is available. The creator already has a separate 2021 우현-아이 화보집 record; the Nxde title and project are distinct.

Exact work/product/person checks found no Rustic 24SS catalog match and no Nxde campaign match. The metadata-only import added two works, five physical editions, and four featured creator links. Repeatable-read read-back passed; the scoped audit found zero integrity findings and zero people missing provenance. The public catalog verifier returned 358 physical and 5,087 digital works at this checkpoint. All five new editions have unknown date, pages, and cover; the campaigns do not grant permission to mirror any exact image, and no campaign image or paid file was uploaded to R2.

Sources: [Wadiz Rustic 24SS campaign](https://www.wadiz.io/web/campaign/detail/250208), [Fanding Nxde campaign](https://fanding.kr/@woohye0n/funding/140/), [creator paper-photobook community post](https://fanding.kr/ja/@woohye0n/community/42256/). Import evidence: [manifest](korean-influencer-photobooks-batch-138-import.json), [database read-back](korean-influencer-photobooks-batch-138-db-readback.json), [scoped audit](korean-influencer-photobooks-batch-138-db-verification.json). The held Yeo Si-yeon Vol. 7 and Anessa/Hurricane Kimchi leads are documented under research_notes/Korean influencer photobook additions 4/.

## MAXQ Special Edition Vol. 8 — Jo Aera

RIDI identifies *MAXQ Special Edition 8호* (Vol. 8 featuring 조애라) as a 33-page PDF e-book released 2023-04-25 by MAXQ International. Its description calls the series an online photobook of selected MAXQ pictorials previously unreleased online. A Wellness Insight interview dated 2023-04-13 identifies Jo Aera as owner of the Pilates studio Aera Infit and gives her Instagram account @aerassam_; a later Vanaro profile links the same Instagram and describes her ongoing studio, teaching, and education work. The live database had no exact RIDI product ID, title/featured-name, or person-row match. The separate digital work is now recorded with one edition and one publisher-sourced featured credit. Photo overlap with her other MAXQ or Secret B shoots is not checked. No cover or paid file was copied to R2 because exact-image reuse permission is unconfirmed. Sources: [RIDI product](https://ridibooks.com/books/3563000166), [Wellness Insight interview](https://contents.premium.naver.com/wellness/wellnessinsight/contents/230413143753301gh), [Vanaro profile](https://www.vanaro.co.kr/home/?bmode=view&idx=169725418&q=YToyOntzOjEyOiJrZXl3b3JkX3R5cGUiO3M6MzoiYWxsIjtzOjQ6InBhZ2UiO2k6Mjt9&t=board). Database evidence: [import manifest](korean-maxq-special-edition-vol08-jo-aera-2023-import.json), [read-only snapshot](korean-maxq-special-edition-vol08-jo-aera-2023-db-readback.json), [scoped audit](korean-maxq-special-edition-vol08-jo-aera-2023-db-verification.json).


## MAXQ Special Edition Vol. 3 — four models

RIDI identifies *MAXQ Special Edition 3호* as a 41-page PDF e-book released 2020-12-24 and describes the series as an online photobook. Newstown's contemporary MAXQ-sourced report names Jeong Hanna (정한나), Lee Ha-rin (이하린), Kang Ju-yeon (강주연), and Lee Seon-i (이선이) as the four models in the Vol. 3 project. Maeil Business separately identifies Jeong Hanna as a fitness influencer. The other three subjects are listed as models because separate creator activity was not established in this pass. A repeatable-read query found no exact product URL or matching title, and the metadata-only record is now in the database. The scoped audit has zero integrity failures and zero missing person provenance. No listing or media was added; exact-cover reuse permission and photo overlap with other MAXQ works remain unverified. Sources: [RIDI product](https://ridibooks.com/books/3563000074), [Newstown report](https://www.newstown.co.kr/news/articleView.html?idxno=473998), [Maeil Business on Jeong Hanna](https://www.mk.co.kr/news/entertain/10007223). Database evidence: [manifest](korean-maxq-special-edition-vol03-four-models-2020-import.json), [snapshot](korean-maxq-special-edition-vol03-four-models-2020-db-readback.json), [scoped audit](korean-maxq-special-edition-vol03-four-models-2020-db-verification.json).

## Anessa and Hurricane Kimchi 10th-anniversary photobook

The successful Tumblbug campaign establishes a physical photobook-and-poster project featuring the drag performers Anessa and Hurricane Kimchi. Heezy Yang's official bio connects Hurricane Kimchi to a Seoul-born Korean artist and documents original music and music videos. The product is cataloged as a creator-led campaign item; the reviewed sources do not call either person a social-media influencer, and actual shipment is unverified. No image was copied to R2 because exact-asset reuse permission remains undocumented. Sources: [campaign](https://tumblbug.com/drag10), [official artist bio](https://heezyyang.wixsite.com/heezyyang), [official music/social page](https://heezyyang.wixsite.com/heezyyang/music). Records: [manifest]({slug}-import.json), [readback]({slug}-db-readback.json), [audit]({slug}-db-verification.json).
