# Taiwan digital influencer photobook leads through 2026-10-30

## Import-grade result

### Takeaway

No fully import-grade, previously unrecorded digital edition survived the required checks in this pass. A likely new ebook edition of 鄭羽凡’s existing photobook has an EISBN and direct Books.com listing, but the retailer does not report ebook page count, and the National Central Library record conflicts with the retailer on format and publication timing; its standalone cover asset also could not be verified.

### Cited Findings

- Books.com lists **其實我有點壞Si;era’s photobook鄭羽凡寫真書 (電子書)** by 鄭羽凡, from 水靈文創, dated **2026-08-18**, as a fixed-layout EPUB with EISBN **9786267742044**. The listing shows the separate print ISBN **9786269640614**, but does not state an ebook page count. [Books.com ebook product page](https://www.books.com.tw/products/E050354706)
- The National Central Library’s 2025 deposit list records the same title and creator under 水靈文創 with identifier **978-626-7742-04-4**, format **PDF**, and expected publication month **11408 (2025-08)**. This differs from Books.com’s EPUB format and 2026-08-18 date; the NCL field is an expected month, not evidence of the actual release date. [NCL deposit list](https://isbn.ncl.edu.tw/FCKEDITOR_UploadFiles/1755143472.pdf)
- Print sources identify the related physical edition as **9786269640614** and **128 pages**, including Kingstone’s product page and Eslite’s specifications. Those figures belong to the print edition and should not be copied onto the digital edition without a digital-page source. [Kingstone print listing](https://www.kingstone.com.tw/basic/2019910048444/); [Eslite print listing](https://www.eslite.com/product/1001261682682253441007)
- The Books.com author biography says 鄭羽凡 formerly belonged to the online group 「在不瘋狂就等死」, was active in self-media, and moved into YouTube; it also describes her Taiwanese connection. Mirror Media independently describes the group as a popular YouTube influencer group in Taiwan and identifies her as former member 亞亞, later renamed 鄭羽凡. [Books.com ebook product page](https://www.books.com.tw/products/E050354706); [Mirror Media profile](https://www.mirrormedia.mg/story/amp/20220113web009)
- Books.com’s product page presents the title-specific cover image, but I could not retrieve or verify its standalone image asset: the likely retailer image route returned HTTP 403. The existing MuseBooks catalog has a cover asset for the **print** edition; it is not evidence that the ebook used the same cover file. [Books.com ebook product page](https://www.books.com.tw/products/E050354706); [local catalog print entry](../../scraper/taiwan-photobook-catalog.md#L1961)

### Inferences

- The EISBN query returned no live catalog work, while exact title and creator queries resolve to an existing 鄭羽凡 work with only the 2022 physical edition. If eventually cleared, the digital item should be added as a second edition to that work, not as a duplicate work. [MuseBooks exact-title API query](https://musebooks.my/v1/books?q=%E5%85%B6%E5%AF%A6%E6%88%91%E6%9C%89%E9%BB%9ESi); [MuseBooks creator API query](https://musebooks.my/v1/books?q=%E9%84%AD%E7%BE%BD%E5%87%A1); [MuseBooks EISBN API query](https://musebooks.my/v1/books?q=9786267742044)
- Because the digital page count is absent and NCL/Books.com disagree on format and expected/reported timing, this is a **hold**, not a complete import candidate under the requested metadata bar. The print’s 128 pages and ISBN cannot fill the missing digital metadata.

### Gaps

- No direct retailer or publisher page found in this pass states the ebook’s page count.
- No publisher clarification found for why NCL records this EISBN as PDF for 2025-08 while Books.com lists it as fixed-layout EPUB dated 2026-08-18.
- A standalone, title-identifiable digital cover-image URL could not be verified; the Books.com product page itself displays the cover image, but its likely image endpoint returned 403 during direct retrieval.

## Duplicate checks and screened titles

### Takeaway

The exact title/person API check confirms that 鄭羽凡’s physical work already exists but its digital EISBN does not. The other recent retailer hits checked here are already represented as digital editions, so none should be proposed as new imports.

### Cited Findings

- Local exact-text searches found no 鄭羽凡/《其實我有點壞》 entry in the prior leads 2–4 reports, but the local catalog does include her print edition under creator 鄭羽凡 with ISBN **9786269640614**. [Local Taiwan photobook catalog, 鄭羽凡](../../scraper/taiwan-photobook-catalog.md#L1961)
- Read-only `GET https://musebooks.my/v1/books?q=其實我有點壞Si` and `q=鄭羽凡` both returned `work-tw-9bcbbed2719c0138ff33c410`, featured name 鄭羽凡, and a single **physical** edition with ISBN **9786269640614**. Query `q=9786267742044` returned `total: 0`. Thus the exact work is known, but the Books.com EISBN was absent at check time. [Title API query](https://musebooks.my/v1/books?q=%E5%85%B6%E5%AF%A6%E6%88%91%E6%9C%89%E9%BB%9ESi); [creator API query](https://musebooks.my/v1/books?q=%E9%84%AD%E7%BE%BD%E5%87%A1); [EISBN API query](https://musebooks.my/v1/books?q=9786267742044)
- 瑟七’s **《微澀．微瑟：瑟七寫真書》** is already represented locally as digital EISBN **9786264555029** and physically as ISBN **9786264552080**; the live API returned both editions under work `work-tw-df1e291d2b2f39f368a77cc1`. [Local catalog, 瑟七](../../scraper/taiwan-photobook-catalog.md#L1393); [MuseBooks creator query](https://musebooks.my/v1/books?q=%E7%91%9F%E4%B8%83); [Books.com ebook listing](https://www.books.com.tw/products/E050354223)
- 劉芷伊’s **《芷想靠近你：劉芷伊醫師寫真》** is already in the live API with digital EISBN **9786264444965** and a separate physical edition, under work `work-tw-0fe3296d84c633e5ab200c65`; the local catalog lists the print edition. It is therefore excluded even though Books.com was the search result that surfaced it. [Local catalog, 劉芷伊](../../scraper/taiwan-photobook-catalog.md#L310); [MuseBooks title query](https://musebooks.my/v1/books?q=%E8%8A%B7%E6%83%B3%E9%9D%A0%E8%BF%91%E4%BD%A0); [Books.com ebook listing](https://www.books.com.tw/products/E050360504)
- 夏蕾’s **《心動蕾達：夏蕾寫真》** is already listed in the local catalog as digital EISBN **9786264446433** plus physical ISBN **9786264446549**; the API query returns both editions under work `work-tw-44b0143f8e9afb4d9fff0e09`. [Local catalog, 夏蕾](../../scraper/taiwan-photobook-catalog.md#L477); [MuseBooks creator query](https://musebooks.my/v1/books?q=%E5%A4%8F%E8%95%BE); [Books.com ebook listing](https://www.books.com.tw/products/E050357688)

### Inferences

- Existing physical work identity does not itself rule out a new digital edition; for 鄭羽凡, the API’s physical-only edition list and zero EISBN result show that the digital edition is not currently represented. The missing fields and source conflict, rather than title duplication, are why it does not clear import-grade review.
- The瑟七、劉芷伊, and夏蕾 results are duplicates at the digital-edition level and should not be re-added.

### Gaps

- The API endpoint supports title/person search through `q`; no separate ISBN query route was needed. Exact EISBN search was performed with the same endpoint and returned zero results.
- This check does not establish that every Taiwan creator ebook retailer listing was searched exhaustively.

## Search coverage and limits

### Takeaway

Searches across Books.com, BOOK☆WALKER Taiwan, Kobo Taiwan, Readmoo, Sanmin, and creator-related web results surfaced the four titles above. Three were already covered as digital editions; the only apparent missing digital edition is the 鄭羽凡 EISBN, which remains incomplete because page count, metadata reconciliation, and direct cover-asset verification are unresolved.

### Cited Findings

- Search queries included combinations of `數位寫真`, `寫真`, `電子書`, `EISBN`, `2026`, Taiwanese retailer domains, and `YouTuber`/`網紅`; result pages included current product records for 瑟七, 劉芷伊, 夏蕾, and 鄭羽凡. [瑟七 Books.com product](https://www.books.com.tw/products/E050354223); [劉芷伊 Books.com product](https://www.books.com.tw/products/E050360504); [夏蕾 Books.com product](https://www.books.com.tw/products/E050357688); [鄭羽凡 Books.com product](https://www.books.com.tw/products/E050354706)
- The 2026 Books.com record for 鄭羽凡 reports author, publisher, release date, EISBN, Taiwan publication place, and fixed-layout EPUB format, while the National Central Library deposit record supplies a conflicting PDF format/earlier expected month. Neither establishes a digital page count. [Books.com](https://www.books.com.tw/products/E050354706); [NCL deposit list](https://isbn.ncl.edu.tw/FCKEDITOR_UploadFiles/1755143472.pdf)

### Inferences

- The screened results support continuing discovery, but this pass does not support a complete new digital-edition record ready for import.

### Gaps

- Searches did not produce complete direct records for all Taiwan creator storefronts or all older ebook platforms; no exhaustive-coverage claim is made.
- Next evidence that would clear the 鄭羽凡 hold: publisher or retailer confirmation of the ebook pagination and file format/date, plus a direct identifiable ebook cover asset.
