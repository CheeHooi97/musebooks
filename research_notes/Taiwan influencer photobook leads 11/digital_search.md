# Taiwan creator digital photobook discovery, round 11

## Is there a newly verified Taiwan creator ebook suitable for import?

### Takeaway
One import-ready digital candidate surfaced: 小丁《白色原味 小丁日常原創數位寫真》. The direct ebook product page, National Central Library deposit record, creator coverage, product-image URL, and live MuseBooks checks collectively support recording it as a new digital work/edition; no DB or R2 changes were made in this research pass.

### Cited Findings
- Readmoo’s direct product page sells **《白色原味 小丁日常原創數位寫真》** as an **EPUB fixed-layout ebook** by 小丁, published by **尖端出版**, with publication and online date **2021-05-28** and product ISBN **9786263085206**. [Readmoo product page](https://reading.udn.com/ebook/store/store_product.do?pid=29667)
- The NCL deposit record identifies the matching title/author and assigns **9786263085206 to EPUB** and **9786263085084 to PDF**, both under 尖端; this verifies the format-specific ebook identifiers. [NCL deposit list, 2021](https://isbn.ncl.edu.tw/FCKEDITOR_UploadFiles/1634009009.pdf); [NCL EPS new-title list](https://nclfile.ncl.edu.tw/files/202210/f53f976e-e791-41c2-bbdb-f0e9faf5db5e.pdf)
- Readmoo’s product page embeds the product image as its cover image, with the page’s book-cover `<img>` alt text matching this title. [Readmoo cover image](https://pgw.udn.com.tw/gw/photo.php?u=https://dc.udn.com/hsuanhao/TEK2209DP007/images/R18.jpg)
- Google Play lists the same digital title by 小丁、傑路, from 尖端出版, dated **2021-05**, and reports **210 pages**. Readmoo does not expose a page count, so 210 is the Google Play listing’s pagination, not a verified count for every platform package. [Google Play ebook](https://play.google.com/store/books/details/%E7%99%BD%E8%89%B2%E5%8E%9F%E5%91%B3_%E5%B0%8F%E4%B8%81%E6%97%A5%E5%B8%B8%E5%8E%9F%E5%89%B5%E6%95%B8%E4%BD%8D%E5%AF%AB%E7%9C%9F?hl=zh_TW&id=xfIvEAAAQBAJ)
- Mirror Media calls 小丁 an Instagram influencer with **120,000 followers** at the time and identifies this exact book as her first photobook; JUKSY describes her as a Taiwan cosplayer and names the same digital photobook. [Mirror Media](https://www.mirrormedia.mg/story/20210607ent005); [JUKSY](https://kol.juksy.com/article/110064)
- Live MuseBooks API queries for the creator, title and EPUB ISBN returned zero works on **2026-10-30**; the current local Taiwan photobook catalog also has no match for 小丁, Komachi, 白色原味 or either ebook ISBN. [MuseBooks creator query](https://musebooks.my/v1/books?q=%E5%B0%8F%E4%B8%81); [title query](https://musebooks.my/v1/books?q=%E7%99%BD%E8%89%B2%E5%8E%9F%E5%91%B3); [EISBN query](https://musebooks.my/v1/books?q=9786263085206); [Taiwan catalog](../../scraper/taiwan-photobook-catalog.md)

### Inferences
- Treat **9786263085206** as the EPUB edition identifier and **9786263085084** as its PDF-format counterpart; do not combine them into one identifier. The title is a digital product, not merely an ebook offer for a print listing, because Readmoo labels the product EPUB fixed-layout and NCL registers separate electronic formats.
- A new record appears warranted based on the available title and identifier checks. If imported later, preserve the Readmoo product link and use its product image as the candidate cover asset; do not infer page count from the EPUB itself because only Google Play reports 210 pages.

### Gaps
- No independent product-specific publication date was located for the PDF sibling; NCL lists the deposit month as 2021-05, while Readmoo gives the exact date for the EPUB product.
- The API and catalog checks are point-in-time checks; this assignment did not authorize creating the catalog record or uploading the cover to R2.

## Which recently surfaced digital-storefront titles are already covered?

### Takeaway
Fresh retailer/category results also surfaced several existing Taiwanese creator ebooks. They are duplicate leads, not imports.

### Cited Findings
- **《Babe Fantasy‧寶兒寫真書》** already has an EPUB edition, EISBN **9786267683781**, in the current catalog and live MuseBooks record; its print ISBN is **9786267683798**. [Readmoo listing](https://reading.udn.com/ebook/store/store_product.do?pid=150278); [Kobo ebook](https://www.kobo.com/tw/zh/ebook/babe-fantasy); [live MuseBooks record](https://musebooks.my/books/work-tw-6bfdeef40b49b66040c85d2e); [local catalog entry](../../scraper/taiwan-photobook-catalog.md#L632)
- **《與你襄遇 林襄數位寫真（含影音）》** is present in the catalog and current MuseBooks records, with digital EISBN **9786263061255**. [Pubu combo/product](https://m.pubu.com.tw/combo/231895); [Sanmin ebook listing](https://www.sanmin.com.tw/product/index/013426283); [local catalog entry](../../scraper/taiwan-photobook-catalog.md#L1136)
- **《微澀．微瑟》瑟七數位寫真** is also an existing digital edition, EISBN **9786264555029**; Books.com identifies it as a fixed-layout EPUB dated **2026-08-30**. [Books.com ebook](https://www.books.com.tw/products/E050354223); [Pubu product](https://www.pubu.com.tw/ebook/690306); [MuseBooks 瑟七 query](https://musebooks.my/v1/books?q=%E7%91%9F%E4%B8%83)

### Inferences
- Current product discovery pages can return already-cataloged titles, so the exact title/EISBN API check should remain part of the import screen.

### Gaps
- The storefront scan does not establish that all older or creator-run ebook stores have been exhausted; it only records titles checked in this pass.

## What is the disposition for this pass?

### Takeaway
Advance 小丁’s EPUB as the one new import-ready candidate. Keep the three covered titles above out of the import batch. No DB/R2 mutation was performed.

### Cited Findings
- The candidate has a direct Readmoo EPUB product page, an EPUB-specific NCL deposit identifier, a cover image embedded on the product page, and independent Taiwan-cosplayer/influencer coverage. [Readmoo](https://reading.udn.com/ebook/store/store_product.do?pid=29667); [NCL](https://isbn.ncl.edu.tw/FCKEDITOR_UploadFiles/1634009009.pdf); [JUKSY](https://kol.juksy.com/article/110064); [Mirror Media](https://www.mirrormedia.mg/story/20210607ent005)
- Live MuseBooks creator/title/EISBN searches returned no records, and the local Taiwan catalog has no title or creator match. [Creator query](https://musebooks.my/v1/books?q=%E5%B0%8F%E4%B8%81); [title query](https://musebooks.my/v1/books?q=%E7%99%BD%E8%89%B2%E5%8E%9F%E5%91%B3); [EISBN query](https://musebooks.my/v1/books?q=9786263085206); [catalog](../../scraper/taiwan-photobook-catalog.md)

### Inferences
- The candidate is suitable for the Taiwan digital-photobook queue with the EPUB ISBN as its edition identifier; page count should remain source-qualified.

### Gaps
- The final catalog/R2 import and a post-import readback remain unperformed because this round was assigned research only.
