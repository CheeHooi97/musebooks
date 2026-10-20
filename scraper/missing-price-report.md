# Missing-price inspection — 8 October 2026

Read-only queries against live PostgreSQL found 528 current editions belonging to published works. A usable price here means a linked listing with price_minor > 0 and a nonempty currency, regardless of availability or public-display eligibility.

| Format | Editions | Missing usable price |
|---|---:|---:|
| Physical | 289 | 273 |
| Digital | 239 | 83 |
| Total | 528 | 356 |

355 editions have no linked listing. One has a completed Ruten listing with price_minor=0: 阿喜(林育品) 私攝概念寫真集 馬尾女孩最無敵, listing-4ad7d5c3cf627e7a608ace5d9a9da01a, https://www.ruten.com.tw/item/22624864044811/. Its final transaction price could not be verified. A retail price must not replace its sold price.

The import history in catalog-import-report.md explicitly documents metadata-only publisher imports and omitted physical retail prices. Prices live in listings, not editions. This explains the dominant pattern: offer collection is incomplete. Format/source/status filtering can also suppress public prices; that is separate from the missing linked-price count.

## Online price research

These ten titles/formats match missing editions in the live audit. Evidence comes from indexed/cached pages, sometimes months old. These are research candidates, not fresh browser observations. No database records were changed. Availability requires a fresh check before importing an active offer.

| Title | Format | Displayed TWD | Source and interpretation |
|---|---|---:|---|
| BIVI華華『最美好的樣子』 | Digital | 666 | [Exact publisher product](https://redboy.com.tw/product/bivi001), sold out; displayed retail price, not a sale transaction. |
| 《 NINIBack XYAB 》 | Digital | 499 | [Exact publisher product](https://redboy.com.tw/product/nini001), cached page shows purchase buttons. |
| Q匠-遇見更好的自己寫真書 | Physical | 980 | [Publisher category](https://www.fan520.net/pages/books), list price 1,280; detail page unavailable. |
| Q匠-零距離接觸寫真集 | Physical | 1,280 | [Publisher category](https://www.fan520.net/pages/books), exact title; availability unverified. |
| 佐藤麻優-求戰版 A4硬殼實體寫真集 | Physical | 1,280 | [Publisher category](https://www.fan520.net/pages/books), physical edition; separate digital product price must not be substituted. |
| 李馨一馨的距璃寫真集 | Physical | 880 | [Exact publisher product](https://www.fan520.net/products/cincinli-photobook), sold out; list price 1,280. |
| TAKA：深夜名堂男子寫真 | Physical | 600 | [Publisher catalog](https://event.kadokawa.com.tw/), title match. Momo's September 540 promotion expired; cached TAAZE 474 has stale upcoming availability. |
| 慾見SHOYA：筋肉教練寫真 | Physical | 620 | [Publisher catalog](https://event.kadokawa.com.tw/), title match. Digital retail is separate. |
| FIRST JUMP：TOKKI CUTIE 臺北伊斯特啦啦隊寫真故事 2025-2026 | Physical | 1,200 | [Official team announcement](https://eastpower.tw/6177), historical list price; launch offer 1,080. Retailer bonus variants need checking. |
| 你的藍色不是我的藍色：Yilian游泳教練首部寫真散文，那些歸屬感、幸福感，以及勇氣和愛 | Physical | 540 | [Publisher group bookstore](https://www.bookrep.com.tw/?at=bookcontent&cl=book&id=14957&md=gwindex), cached exact-title offer. |

The remaining 346 missing-price editions require further research. No marketplace sold prices were recovered in this pass. Raw edition IDs, titles, metadata URLs and listing counts are in missing-price-audit.json. Rerun the audit from backend with `go run ./cmd/price-audit`; it uses a read-only connection and runs no migrations. Command compilation was checked with `go test ./cmd/price-audit`.
