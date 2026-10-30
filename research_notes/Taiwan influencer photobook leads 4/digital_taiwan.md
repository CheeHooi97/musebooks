# Digital Taiwan influencer photobooks

## Which newly found digital editions are absent from the catalog and live database?

### Takeaway
I found one import-ready digital photobook that was absent from both the Taiwan catalog and the live MuseBooks search: the fixed-layout EPUB of 《有你的夏天：黃氏兄弟寫真書II》. Its Taiwan creator identity, exact EISBN, ebook format, seller page, release date and cover asset can all be tied to publisher, retailer, or National Central Library records.

### Cited Findings
- BOOK☆WALKER Taiwan sells the exact ebook product as **《有你的夏天：黃氏兄弟寫真書II（數位精華版）》**, product 126031, credits 黃氏兄弟, names 台灣角川 as publisher, labels the format 固定版面, gives **EISBN 9789865249809**, **144 pages**, and a start-of-sale date of **2021-10-29**; its embedded product metadata provides the cover asset at [taiwan-image.bookwalker.com.tw/product/126031/126031_1.jpg](https://taiwan-image.bookwalker.com.tw/product/126031/126031_1.jpg). The live retailer listing is [BOOK☆WALKER product 126031](https://www.bookwalker.com.tw/product/126031).
- Taiwan’s National Central Library deposit list records the EPUB edition under ISBN **9789865249809**, and separately records the print edition under ISBN **9789865249793**. ([NCL deposit list](https://isbn.ncl.edu.tw/FCKEDITOR_UploadFiles/1636420416.pdf))
- The publisher’s listing identifies the Huang Brothers as a Taiwan YouTube channel formed by brothers 黃雍哲 and 黃挺瑋; INSIDE independently describes their channel and YouTube creator work. ([Kadokawa Taiwan title page](https://www.kadokawa.com.tw/en/products/9789865249793); [INSIDE profile](https://www.inside.com.tw/article/21772-zhe-wei-huang))
- Exact-title and creator-name searches of the live public MuseBooks API returned zero works. Neither the current [Taiwan photobook catalog](../../scraper/taiwan-photobook-catalog.md), [research report 2](../../reports/Taiwan%20influencer%20photobook%20leads%202.md), nor [research report 3](../../reports/Taiwan%20influencer%20photobook%20leads%203.md) contains this title or creator. No MuseBooks work or edition ID is assigned yet.

### Inferences
- This is a valid Taiwan creator photobook candidate: the publisher’s page explicitly calls the Huang Brothers a Taiwan YouTube channel, and the official ebook seller provides a distinct EISBN and ebook format. The print ISBN and ebook EISBN should remain separate edition identifiers.
- Because the work is absent as a whole from the public catalog and live API, importing the verified ebook will require creating a work record unless another research lane has already created it. The ISBN deposit and publisher’s print product page also point to the related physical edition, which the physical-releases researcher should handle or coordinate before import.

### Gaps
- The ebook seller’s page has a direct cover-image asset; I did not download and hash it or compare its pixels against a print cover. Use the retailer’s image as the digital product cover source unless import review finds a better publisher asset.
- The public catalog/API searches are title-based; zero results means no matching public record surfaced for these search terms, not proof that an unpublished or differently indexed internal record cannot exist.

## Which apparent digital leads were already represented or outside the new-import set?

### Takeaway
Search results surfaced several relevant Taiwan creator ebooks, but live API checks showed their works and digital editions are already in MuseBooks. I found no reason to create duplicates for them in this pass.

### Cited Findings
- Kobo Taiwan lists 短今’s **《今日旅行中 短今Sammie寫真書》** as an EPUB with ISBN **9789865245702** and release date **2021-05-28**. MuseBooks already has its digital edition `edition-734a03a4bbec314f3330a0f4` under work `work-tw-c1bbf591a5160aff8a48a473`, and the catalog lists the same Pubu digital product alongside the related print edition. ([Kobo listing](https://www.kobo.com/tw/zh/ebook/sammie-3); [catalog](../../scraper/taiwan-photobook-catalog.md))
- Books.com currently lists 瑟七’s **《微澀．微瑟》瑟七 Seul7 數位寫真（含影音）**; MuseBooks already returns digital edition `edition-0b730768da4b9e6b0bef9b82` and a separate physical edition under work `work-tw-df1e291d2b2f39f368a77cc1`. ([Books.com ebook listing](https://www.books.com.tw/products/E050354223); [Readmoo ebook listing](https://readmoo.com/book/210497069000101))
- Readmoo lists 寶兒’s fixed-layout EPUB **《Babe Fantasy‧寶兒寫真書（加贈多張未公開照片）》**, EISBN **9786267683781**, released 2025-12-09; MuseBooks already has a digital edition and a distinct physical edition under work `work-tw-6bfdeef40b49b66040c85d2e`. ([Readmoo listing](https://reading.udn.com/ebook/store/store_product.do?pid=150278); [Sanmin ebook record](https://www.sanmin.com.tw/product/index/015552499))
- Kobo’s product page for **《蔚你著迷 李藹蔚數位寫真》** gives publisher 尖端, EPUB3 fixed format, ISBN **9786263776210**, release date **2024-01-11**, and describes 李藹蔚 as having over 450,000 social followers; MuseBooks already has the matching digital work and edition `edition-bd0f0f5916b6b3382fc8c79b`. The retailer metadata is useful for a later metadata-enrichment review, but it is not a missing work. ([Kobo listing](https://www.rakuten.com.tw/shop/kobo/product/7068dfb7-4a57-33fa-a35a-6786589e4efa/); [Sanmin listing](https://www.sanmin.com.tw/product/index/013650100))
- 《Troy：特洛伊寫真書》 and **《Rainylove 鍾以希數位寫真》** also appeared in retailer discovery but already have live MuseBooks digital editions (`edition-fcc62c065b9cd1a8f5ddb595` and `edition-631debd66f9a32ef6735b23f`, respectively). The latter retailer page describes 鍾以希 as a web influencer and game streamer. ([BOOK☆WALKER Troy listing](https://www.bookwalker.com.tw/product/158173); [Readmoo Rainylove listing](https://reading.udn.com/ebook/store/store_product.do?pid=18665))

### Inferences
- The digital retailer search results are useful for finding additional distribution channels and missing edition metadata, but many are re-listings of works already present in the 439-work Taiwan catalog and live database. Exact-title/API checks should remain part of every candidate review.
- I excluded the generic magazine and series results appearing alongside photobooks in retailer category searches; they are not creator-specific standalone photobook editions.

### Gaps
- I did not verify Taiwan nationality for every non-Taiwan-born performer appearing in local ebook catalogs; a Taiwan retailer listing alone does not make a foreign creator a Taiwan influencer.
- This was a focused digital-retailer pass, not an exhaustive scan of all digital storefronts or all social preorder links. New and differently titled creator editions may still be missing.
