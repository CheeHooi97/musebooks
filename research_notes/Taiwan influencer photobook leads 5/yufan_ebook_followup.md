# 鄭羽凡《其實我有點壞Si;era’s photobook鄭羽凡寫真書（電子書）》follow-up

## 1. Direct ebook cover asset

### Takeaway

I could not verify a standalone image URL that is identifiable as the ebook cover actually shown for Books.com product E050354706. Keep the cover field on hold; the existing MuseBooks cover belongs to the physical edition and is not a safe substitute.

### Cited Findings

- Books.com has a product page specifically labeled as the ebook edition, EISBN 9786267742044, alongside a separate paperback version. [Books.com ebook product page](https://www.books.com.tw/products/E050354706)
- The current MuseBooks work page lists only one physical edition, ISBN 9786269640614. Its displayed cover is attached to that physical record. [MuseBooks work page](https://musebooks.my/books/work-tw-9bcbbed2719c0138ff33c410)

### Inferences

- The Books.com page confirms an ebook product record, but the accessible sources do not expose an ebook-specific, direct image asset that can be matched to it. Reusing the work’s current cover would therefore assume that the digital edition uses the print cover file.

### Gaps

- A direct Books.com product-page fetch returned HTTP 403 during this follow-up, and the previous attempt to retrieve the likely image endpoint also returned HTTP 403. No title-identifiable standalone ebook image URL was recovered.

## 2. Product format, release date, and page count

### Takeaway

Books.com currently lists the ebook as a fixed-layout EPUB dated 2026-08-18. The National Central Library (NCL) deposit list identifies the same EISBN as PDF for expected publication in 2025-08; neither listing supplies a numeric ebook page count, so the digital metadata is not complete enough to import confidently.

### Cited Findings

- Books.com’s E050354706 page lists publisher 水靈文創, author 鄭羽凡, the date 2026/08/18, and the ebook as a fixed-layout EPUB with EISBN 9786267742044. The listing does not provide ebook pagination. [Books.com ebook product page](https://www.books.com.tw/products/E050354706)
- NCL’s 2025 list uses the field 預計出版年月 and records 鄭羽凡’s title under 水靈文創 at 11408, with ISBN 978-626-7742-04-4 and format PDF. The entry gives “面” rather than a numeric page count. [NCL 2025 deposit list](https://isbn.ncl.edu.tw/FCKEDITOR_UploadFiles/1755143472.pdf)
- The related print edition has a different ISBN, 9786269640614, and 128 pages. These print details are explicitly identified as paper-format metadata and cannot establish the ebook’s page count. [Kingstone print listing](https://www.kingstone.com.tw/basic/2019910048444/)

### Inferences

- Books.com is a retailer source for its live ebook listing, while NCL is the stronger source for what was registered in the deposit/prepublication list. Neither source alone resolves the ebook’s final pagination.

### Gaps

- No publisher statement or reliable retailer record located in this follow-up gives a numeric ebook page count.

## 3. NCL and Books.com discrepancy

### Takeaway

The discrepancy is real, but I found no publisher or library explanation for it. NCL’s date is explicitly an expected month, so the item may have been delayed or its retailer record updated later; that possibility does not explain why the same ISBN is labeled PDF by NCL and fixed-layout EPUB by Books.com.

### Cited Findings

- NCL lists the EISBN as PDF and gives 11408 under 預計出版年月 (expected publication month). [NCL 2025 deposit list](https://isbn.ncl.edu.tw/FCKEDITOR_UploadFiles/1755143472.pdf)
- Books.com lists the same EISBN as fixed-layout EPUB with a full date of 2026/08/18. [Books.com ebook product page](https://www.books.com.tw/products/E050354706)

### Inferences

- A planned 2025 release followed by a 2026 retail date could be consistent with a delay or revised listing. It is only a hypothesis: the available records do not say that the format changed, that the file was converted, or that either entry is erroneous.
- Since the conflict concerns the digital format under the same EISBN, neither source should be silently preferred for a catalog import without a publisher or ISBN-agency correction/confirmation.

### Gaps

- No source located explains whether the ebook was delayed, reissued, converted from PDF to EPUB, or listed incorrectly. No corrected NCL record or publisher notice was found.

## 4. Other retailer or publisher confirmation, and live duplicate check

### Takeaway

Searches did not locate a second independent Taiwanese retailer or publisher page confirming the EISBN. A live API recheck confirms that the existing work remains physical-only and that this EISBN is not currently present in MuseBooks. Given the unresolved format/date conflict, absent ebook page count, and unverified ebook cover asset, recommend **hold**.

### Cited Findings

- Books.com’s publisher-catalog page also includes the ebook record, but it is the same retailer, not independent confirmation from 水靈文創. [Books.com 水靈文創 publisher catalog](https://www.books.com.tw/web/sys_puballb/books/?loc=P_0002_399&pubid=fansapps1)
- Sanmin’s 水靈文創 results show the 2022 鄭羽凡 paperback entry (9786269640614); I found no separate EISBN listing there. This supports only that its surfaced listing is print, not that every Sanmin catalog page has been exhaustively searched. [Sanmin 水靈文創 results](https://www.sanmin.com.tw/search?pu=%E6%B0%B4%E9%9D%88%E6%96%87%E5%89%B5)
- Live read-only MuseBooks API query `q=鄭羽凡` returned work `work-tw-9bcbbed2719c0138ff33c410` with one physical edition, ISBN 9786269640614, dated 2022-09-26, and 128 pages. [MuseBooks creator query](https://musebooks.my/v1/books?q=%E9%84%AD%E7%BE%BD%E5%87%A1)
- Live read-only MuseBooks API query `q=9786267742044` returned `total: 0`, so the EISBN is still not represented as a duplicate edition. [MuseBooks EISBN query](https://musebooks.my/v1/books?q=9786267742044)

### Inferences

- The ebook, if confirmed, belongs as an additional edition under the existing work rather than a new work. The current API result does not establish the ebook’s metadata; it establishes only that the EISBN is absent from the current catalog.
- Do not import or update R2, the database, or catalog from this follow-up. Reconsider only after a publisher/reliable source supplies or resolves the ebook’s format and publication date, provides page count, and exposes or confirms the ebook cover asset.

### Gaps

- No independent Taiwanese retailer or publisher source was found confirming this ebook’s EISBN and product details.
- No reliable source resolves the PDF/EPUB, August 2025/August 2026 discrepancy or provides numeric digital page count.
- No direct, identifiable ebook cover asset was verified.
