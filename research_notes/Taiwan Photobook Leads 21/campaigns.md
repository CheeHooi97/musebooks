# Taiwan Creator-Owned Stores and Crowdfunding

## Which fresh campaign candidate has the strongest import evidence?

### Takeaway

**GO candidate: 宋偉恩《貳柒.禮：The Present of Wayne's 27th》**, as a published Taiwan creator photobook. The creator-run Zeczec project, Taiwan-origin evidence, National Central Library deposit metadata, and a retailer record with a photograph of the finished physical book jointly establish the product and fulfillment. The retailer's product photo is a composite set image rather than an isolated flat cover scan, so use it only if MuseBooks accepts that cover source/crop policy.

### Cited Findings

- Song's official Zeczec campaign names the work 《貳柒.禮》 / *The Present of Wayne's 27th*, describes it as his first personal photo book, says he is a photographer and actor, records NT$1,910,640 from 726 backers, and gives a full-color 128–144-page, 28 × 21 cm specification and planned December 2021 publication. [Official Zeczec campaign](https://www.zeczec.com/projects/The-Present-of-Waynes-27th)
- The National Central Library's December 2021 publication record identifies 宋偉恩 as author, 怡佳娛樂經紀 as Taipei publisher, 144 pages, December 2021, paperback, and ISBN 978-626-95451-0-0. [NCL deposit record (PDF)](https://nclfile.ncl.edu.tw/files/202204/58dc014c-a17e-4259-ac08-e039a107fc62.pdf)
- The official Japanese distributor VAP's artist introduction identifies Wayne Song / 宋偉恩 as born in Taichung, Taiwan. This is the strongest direct Taiwan-origin evidence located. [VAP artist profile](https://www.vap.co.jp/life/special/article2.html)
- Suruga-ya's direct product record, item JB7083, identifies the crowdfunding set as the photobook plus a 2022 calendar and five postcards. Its page says online stock is sold out and nearby store stock may already have sold. [Suruga-ya product page](https://www.suruga-ya.jp/product/detail/JB7083)
- The retailer's title-specific product image shows the physical book with the title printed on the front cover alongside the calendar and postcards. The image returned HTTP 200 with 22,654 bytes; SHA-256 `41b51785b1853852e5a22667e17f2f7f21642c7592b8843b79ee4734d9a0814f`. It shows an actual finished copy rather than a mockup, but the source image is a composite set photo, not a clean cover scan. [Retailer product image](https://cdn.suruga-ya.jp/database/pics_webp/game/jb7083.jpg.webp)

### Inferences

- The NCL deposited record plus the actual finished copy shown in the retailer listing is sufficient evidence that the planned publication was fulfilled; the edition can be cataloged as a historical photobook even though the online reseller listing is currently sold out. [NCL deposit record](https://nclfile.ncl.edu.tw/files/202204/58dc014c-a17e-4259-ac08-e039a107fc62.pdf); [Suruga-ya product page](https://www.suruga-ya.jp/product/detail/JB7083)
- This is a Taiwan actor and creator's personal photobook; the sources found do not describe Song as a social-media influencer specifically. If the catalog uses a strict influencer-only scope, exclude or hold on that scope distinction; if it covers Taiwan creators who independently made photobooks, import is supported. [Official Zeczec campaign](https://www.zeczec.com/projects/The-Present-of-Waynes-27th); [VAP artist profile](https://www.vap.co.jp/life/special/article2.html)
- Read-only MuseBooks API title/name searches returned `total: 0` for `貳柒.禮`, `宋偉恩`, and `The Present of Wayne`; no matching work was found. [Title query](https://musebooks.my/v1/books?q=%E8%B2%B3%E6%9F%92.%E7%A6%AE); [creator query](https://musebooks.my/v1/books?q=%E5%AE%8B%E5%81%89%E6%81%A9); [English-title query](https://musebooks.my/v1/books?q=The%20Present%20of%20Wayne)

### Gaps

- The currently accessible seller image is a composite set photograph, not a separate front-cover scan, and its image page does not state image reuse terms. Prefer the official creator's full-resolution cover if available; otherwise retain retailer attribution and provenance if using this asset. [Retailer product image](https://cdn.suruga-ya.jp/database/pics_webp/game/jb7083.jpg.webp); [official campaign](https://www.zeczec.com/projects/The-Present-of-Waynes-27th)
- Online mail-order inventory is exhausted; only the seller's page-level notice about possible physical-store stock remains, so present availability for purchase is unconfirmed. [Suruga-ya product page](https://www.suruga-ya.jp/product/detail/JB7083)

### Focused follow-up: Taiwan creator scope and final-cover check

- **Creator/origin check passes for Taiwan creator scope; influencer status is not established.** The official project is labelled Taiwan, and Song describes his photography and the book as his own creative work; the page also links his Facebook and Instagram. A CBOOK profile likewise frames 《貳柒.禮》 as his photography-led creation, while VAP identifies him as born in Taichung. These sources support cataloging him as a Taiwanese actor-photographer/creator, but do not establish that he is a social-media influencer. [Official Zeczec campaign](https://www.zeczec.com/projects/The-Present-of-Waynes-27th); [CBOOK profile](https://cbook.tw/archives/17341/amp); [VAP artist profile](https://www.vap.co.jp/life/special/article2.html)
- **Cover check remains unresolved for import.** The official campaign image was fetched directly with HTTP 200 (132,866 bytes; SHA-256 `3B6256326E5F52BE27FC4C7F86195ACD40F658B27C26712A074114A8195190B8`) and visually inspected. It shows a title-specific 《貳柒.禮》 / *The Present of Wayne's 27th* book mockup, but the same image says the cover preview is for reference only. Its white-background portrait/layout differs from the finished copy visible in Suruga-ya's composite set photo (HTTP 200; 22,654 bytes; SHA-256 `41B51785B1853852E5A22667E17F2F7F21642C7592B8843B79EE4734D9A0814F`), so it cannot verify the final cover design. [Official campaign cover preview](https://assets.zeczec.com/asset_345409_image_big.jpg?1626858983=); [Suruga-ya product photo](https://cdn.suruga-ya.jp/database/pics_webp/game/jb7083.jpg.webp)
- **Decision: HOLD for MuseBooks import until a clean, final standalone cover is available or the composite-cover policy is explicitly accepted.** Product identity, Taiwan creator origin, publication/fulfillment, and the prior live-API no-duplicate check are supported by the sources above and the NCL/retailer records already cited; this follow-up made no DB, R2, or catalog writes. [NCL deposit record](https://nclfile.ncl.edu.tw/files/202204/58dc014c-a17e-4259-ac08-e039a107fc62.pdf); [Suruga-ya product page](https://www.suruga-ya.jp/product/detail/JB7083)

## Did any other newly surfaced creator-store leads clear the evidence bar?

### Takeaway

No other lead found in this sweep is GO-ready. A Shopee listing for 尹書潾 / 湧湧's first photobook is a reseller listing with incomplete creator-origin and current-fulfillment evidence; the newly listed 《101 STYLE》 project is a portrait-session service, not a named creator's published photobook.

### Cited Findings

- A Shopee product listing titled “尺度大突破！湧湧第一本同名寫真〖尹書潾〗” offers a photobook and reports Taiwan dispatch, but the seller shown is a merchandise reseller, not the creator. [Shopee listing](https://shopee.tw/%E5%B0%BA%E5%BA%A6%E5%A4%A7%E7%AA%81%E7%A0%B4%EF%BC%81%E6%B9%A7%E6%B9%A7%E7%AC%AC%E4%B8%80%E6%9C%AC%E5%90%8C%E5%90%8D%E5%AF%AB%E7%9C%9F%E3%80%90%E5%B0%B9%E6%9B%B8%E6%BD%BE%E3%80%91%E9%A0%90%E8%B3%BC%E9%96%8B%E8%B7%91-%E5%85%B6%E4%BB%96%E5%AF%AB%E7%9C%9F%E6%9B%B8%E7%8F%BE%E8%B2%A8%E4%BE%9B%E6%87%89-i.59782454.42812486814)
- 尹書潾's Patreon identifies the creator as “中韓混血” but does not establish Taiwan origin. [Creator Patreon](https://www.patreon.com/cw/yyseorin)
- The live MuseBooks API search for 尹書潾 returned `total: 0`; that absence does not resolve the missing origin or seller/cover evidence. [MuseBooks query](https://musebooks.my/v1/books?q=%E5%B0%B9%E6%9B%B8%E6%BD%BE)
- The Zeczec 《101 STYLE》 campaign offers commissioned portrait sessions with file delivery and an optional online showcase; it does not identify a specific Taiwan influencer's photobook edition. [Official campaign](https://www.zeczec.com/projects/xiangpai)

### Inferences

- **HOLD — 湧湧 / 尹書潾:** the product claim exists on a third-party reseller page, but origin is unresolved and the page's delivery estimate is stale relative to this check; no stable title-specific final cover/fulfillment evidence was confirmed. [Shopee listing](https://shopee.tw/%E5%B0%BA%E5%BA%A6%E5%A4%A7%E7%AA%81%E7%A0%B4%EF%BC%81%E6%B9%A7%E6%B9%A7%E7%AC%AC%E4%B8%80%E6%9C%AC%E5%90%8C%E5%90%8D%E5%AF%AB%E7%9C%9F%E3%80%90%E5%B0%B9%E6%9B%B8%E6%BD%BE%E3%80%91%E9%A0%90%E8%B3%BC%E9%96%8B%E8%B7%91-%E5%85%B6%E4%BB%96%E5%AF%AB%E7%9C%9F%E6%9B%B8%E7%8F%BE%E8%B2%A8%E4%BE%9B%E6%87%89-i.59782454.42812486814); [creator Patreon](https://www.patreon.com/cw/yyseorin)
- **EXCLUDE — 《101 STYLE》:** it sells portrait photography sessions rather than a creator-authored/featured photobook product. [Official campaign](https://www.zeczec.com/projects/xiangpai)

### Gaps

- For 尹書潾, I found no first-party product page, clear Taiwan-origin evidence, or final cover asset in this sweep. The Shopee product page remains the only direct product detail located. [Shopee listing](https://shopee.tw/%E5%B0%BA%E5%BA%A6%E5%A4%A7%E7%AA%81%E7%A0%B4%EF%BC%81%E6%B9%A7%E6%B9%A7%E7%AC%AC%E4%B8%80%E6%9C%AC%E5%90%8C%E5%90%8D%E5%AF%AB%E7%9C%9F%E3%80%90%E5%B0%B9%E6%9B%B8%E6%BD%BE%E3%80%91%E9%A0%90%E8%B3%BC%E9%96%8B%E8%B7%91-%E5%85%B6%E4%BB%96%E5%AF%AB%E7%9C%9F%E6%9B%B8%E7%8F%BE%E8%B2%A8%E4%BE%9B%E6%87%89-i.59782454.42812486814)

## What changed among the previously held campaign leads?

### Takeaway

The previously held Adam Lin 《FOUR》 project has no clearing change in this pass: it remains a preorder for a PDF slated for December 2026, with no delivered file/final cover evidence. No prior hold was promoted. The fresh 《貳柒.禮》 lead above is the sole GO candidate from this creator-store/crowdfunding sweep.

### Cited Findings

- The official ADAM2026 campaign says 《FOUR》 is a pure PDF photo book, delivery information will follow production after funding closes, and estimated realization is December 2026; its image disclaimer calls the visible material mockup/sample art. [Official campaign](https://www.zeczec.com/projects/ADAM2026)
- The official FAQ confirms the PDF form and that delivery details depend on project completion. [Campaign FAQ](https://www.zeczec.com/projects/ADAM2026/faqs)
- A 2027 晏人物 calendar campaign is currently listed on Zeczec, but it is a photo calendar and not a separate photobook edition. [Zeczec photography category](https://www.zeczec.com/categories?category=9&page=1)

### Inferences

- **HOLD — ADAM 《FOUR》:** the book's format and Taiwan-creator fit are clear, but until delivery occurs the public page still supports only a future preorder; do not import the campaign mockup as a final cover. [Official campaign](https://www.zeczec.com/projects/ADAM2026); [campaign FAQ](https://www.zeczec.com/projects/ADAM2026/faqs)
- **EXCLUDE — Office State Of Mind 2027:** the surfaced current campaign is a calendar product, outside the standalone photobook scope. [Zeczec photography category](https://www.zeczec.com/categories?category=9&page=1)

### Gaps

- Recheck 《FOUR》 after the planned December 2026 delivery only if its campaign publishes a shipped-file notice or a final cover/edition update. [Official campaign](https://www.zeczec.com/projects/ADAM2026)
