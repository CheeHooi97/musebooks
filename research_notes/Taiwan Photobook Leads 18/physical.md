# Taiwan creator physical photobook — strongest verified candidate

Checked 2026-10-30. This focused pass stopped at the first source-complete candidate. No database, R2, or scraper-catalog writes were made.

## Is the creator and physical edition directly verifiable?

### Takeaway

**DUPLICATE — 《心動蕾達：夏蕾寫真》** is a Taiwan creator photobook with a direct retailer listing and an official, title-specific book image. The exact work and both its digital and physical editions are already in MuseBooks. The retailer still labels the physical listing “preorder” despite a September 18 publication date, so fulfillment is not independently confirmed in this check.

### Cited Findings

- Sanmin’s direct [product page](https://www.sanmin.com.tw/product/index/015783272) lists author 夏蕾, publisher 時報文化, ISBN 9786264446549, paperback, 144 pages, dimensions 18 × 25.6 × 1.1 cm, publication date 2026-09-18, and displays a live “預購中” (preorder) status. Its author bio calls her a Taiwan new-generation cheerleader and a member of the CTBC Brothers’ Passion Sisters. (Checked 2026-10-30.)
- The direct [Readmoo ebook product page](https://reading.udn.com/ebook/store/store_product.do?pid=173955&source=%E5%AF%AB%E7%9C%9F%E9%9B%86) describes 夏蕾 as a Taiwan new-generation cheerleader and identifies the work as her first personal photobook. Search-indexed product details list the EPUB format, EISBN 9786264446433, and September 2026 publication. The page reader returned a cache miss during this check, so the retailer metadata could not be re-opened.
- 時報文化’s official [limited boxed-edition page](https://www.readingtimes.com.tw/product/?pid=1VY0480) names the book and author, and lists a planned shipment date of 2026-09-15 and publication date of 2026-09-15. It is a distinct box-set product from Sanmin’s standard paperback listing; the current page text is sparse and does not prove that orders shipped.
- The official product image linked from the publisher page is [this title-specific cover/product image](https://img.readingtimes.com.tw/images/7b1bb5a2-3f18-480f-a165-e012bb03a1c4/conversions/9a317edc8b05380dd6a34246d3dfa684-500x500.jpg). Downloaded as JPEG (18,170 bytes), SHA-256 `9677489199F22A147DA33D867924C8A6843272B3F06311F868FE4649FB620990`; visual inspection shows the book itself with the title 《心動蕾達》 and 夏蕾’s name on the cover. This is publisher product photography, not an in-hand copy report.
- The live MuseBooks API query for [心動蕾達](https://musebooks.my/v1/books?q=%E5%BF%83%E5%8B%95%E8%95%BE%E9%81%94) returned **2** works. `work-tw-44b0143f8e9afb4d9fff0e09` already has physical edition `edition-21a1147c8c1f52e77866c7ed` (ISBN 9786264446549, 144 pages, Sanmin metadata URL) and digital edition `edition-cf999a4774a1d09f39dbfd70` (EISBN 9786264446433). A second result, `work-tw-1fd7b32e6cb78d5e5382d7f0`, is the official limited-box product. The query was run directly against the live API on 2026-10-30.

### Inferences

- The edition, creator’s Taiwan connection, and title-specific cover evidence are sufficient to identify the work, but the current Sanmin “preorder” label conflicts with the elapsed publication date and the sources do not verify dispatch or delivery. ([Sanmin](https://www.sanmin.com.tw/product/index/015783272); [official publisher page](https://www.readingtimes.com.tw/product/?pid=1VY0480))
- **DUPLICATE — do not import or upload again.** The live API already contains the standard physical edition, corresponding digital edition, and a separate box-set work. ([MuseBooks API title query](https://musebooks.my/v1/books?q=%E5%BF%83%E5%8B%95%E8%95%BE%E9%81%94))

### Gaps

- No dispatch notice, buyer receipt, or physical in-hand report was found; Sanmin’s current preorder label remains unexplained. The image verifies title-specific official product artwork but not the exact printed finish or whether the photographed copy was final production.

## Was a separate R2 or database import appropriate?

### Takeaway

No. This title is already represented in the live catalog with matching physical ISBN, page count, product URL, and a separate digital edition. I made no external or catalog changes.

### Cited Findings

- The API’s exact-title response contains the existing physical edition record `edition-21a1147c8c1f52e77866c7ed` and the separate digital edition record `edition-cf999a4774a1d09f39dbfd70`. ([MuseBooks API title query](https://musebooks.my/v1/books?q=%E5%BF%83%E5%8B%95%E8%95%BE%E9%81%94))
- The cover image was downloaded only to the workspace temporary directory for visual inspection and hashing; no R2 request or database mutation was run.

### Inferences

- **Decision: DUPLICATE.** Keep the existing edition records; revisit only if the catalog’s fulfillment status needs a later update after a direct shipping confirmation.

### Gaps

- This pass did not confirm whether the existing R2 cover object is byte-identical to the official publisher image. No replacement or second upload was attempted.
