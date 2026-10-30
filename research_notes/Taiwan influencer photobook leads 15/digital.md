# Taiwan-origin creator digital photobook leads, round 15 (checked 2026-10-30)

## Is ADAM 林冠宇’s 《FOUR》 a new, import-ready digital photobook?

### Takeaway

《FOUR》 is a verified Taiwan creator digital-photobook preorder and has no exact MuseBooks work, but it is not ready for import: the active campaign promises a future encrypted PDF, and I found no final ebook-cover asset or edition identifier.

### Cited Findings

- The official Zeczec project identifies 《FOUR》 as ADAM 林冠宇’s fourth book and first digital photobook, describes the content as photographs only, and gives the campaign window as 2026-10-12 through 2026-11-12. [Zeczec campaign](https://www.zeczec.com/projects/ADAM2026)
- The project bio calls Adam a Taiwan emerging actor, names his three earlier physical books, and links his Facebook and Instagram accounts. [Zeczec campaign](https://www.zeczec.com/projects/ADAM2026)
- A pure-digital reward contains only the ebook, costs NT$780, and is estimated for December 2026. The FAQ says the deliverable is a password-encrypted PDF and that download details will be announced after fundraising ends and production is complete. [Zeczec campaign](https://www.zeczec.com/projects/ADAM2026); [Zeczec FAQ](https://www.zeczec.com/projects/ADAM2026/faqs)
- The campaign labels the displayed reward imagery and physical collector items illustrative rather than final; the page does not identify a final PDF cover. [Zeczec campaign](https://www.zeczec.com/projects/ADAM2026)
- Live MuseBooks API queries on 2026-10-30 returned no exact work for ADAM or 林冠宇. The query FOUR returns one unrelated Korean MAXQ compilation, not this project. [ADAM query](https://musebooks.my/v1/books?q=ADAM); [林冠宇 query](https://musebooks.my/v1/books?q=%E6%9E%97%E5%86%A0%E5%AE%87); [FOUR query](https://musebooks.my/v1/books?q=FOUR). The current Taiwan catalog file also has no match for FOUR, ADAM2026, or 林冠宇. [Current Taiwan catalog](../../scraper/taiwan-photobook-catalog.md)

### Inferences

- Keep 《FOUR》 as a verified preorder lead, not a completed digital edition. Recheck after campaign fulfillment for the delivered file, a final cover, and any edition-level identifier or page count. [Zeczec FAQ](https://www.zeczec.com/projects/ADAM2026/faqs)

### Gaps

- The project page and FAQ do not provide an ISBN/EISBN, page count, delivered file, or final cover image; the December 2026 realization date is an estimate. [Zeczec campaign](https://www.zeczec.com/projects/ADAM2026); [Zeczec FAQ](https://www.zeczec.com/projects/ADAM2026/faqs)

## What current Taiwan ebook-store results are new versus already in MuseBooks?

### Takeaway

The recent 彭彭 and 夏蕾 ebooks are valid digital photo books, but both already have digital editions and covers in the live database. 彭彭’s digital ISBN metadata conflicts across retailers, so this is an enrichment/metadata-review issue rather than a new import.

### Cited Findings

- Books.com lists 《彭然心動：彭彭寫真〖電子書祕藏版〗》 as a fixed-layout EPUB, EISBN 9786264448314, publisher 時報出版, publication date 2026-09-11, Taiwan edition, and 139.1 MB; it says the ebook adds 40 exclusive photos and cross-references print ISBN 9786264448420. [Books.com ebook](https://www.books.com.tw/products/E050359832)
- BOOK☆WALKER’s product page also identifies the digital edition as EISBN 9786264448314, while the HyRead demo-library listing instead gives EISBN 9786264448321 and 191 pages for an EPUB; HyRead lists the same print ISBN 9786264448420 and 2026 publication year. The available pages do not establish whether this is a separate ebook package or a metadata error. [BOOK☆WALKER product 311413](https://www.bookwalker.com.tw/product/311413); [HyRead demo ebook](https://demo.ebook.hyread.com.tw/bookDetail.jsp?id=518699)
- The official Lioneers Muse Girls roster identifies 彭彭 among its Taiwan-side new members and says she has nearly 300,000 social followers, supporting Taiwan creator/influencer context. [Lioneers Muse Girls roster](https://www.lioneers.tw/pages/musegirls-1)
- The Books.com ebook page exposes a product-cover image at [E050359832.jpg](https://www.books.com.tw/img/E05/035/98/E050359832.jpg). The live MuseBooks search for 彭然心動 returns the existing Taiwan work `work-tw-48cee531f79d279264813cd3`, with both print ISBN 9786264448420 and a digital edition, EISBN 9786264448314, which already has its own stored cover. [MuseBooks 彭然心動 query](https://musebooks.my/v1/books?q=%E5%BD%AD%E7%84%B6%E5%BF%83%E5%8B%95)
- The current local Taiwan catalog lists 彭彭’s physical edition only; its missing ebook row is a catalog/documentation gap because the live API already has the digital edition. [Current catalog entry](../../scraper/taiwan-photobook-catalog.md#L827)
- Books.com identifies 《心動蕾達：夏蕾寫真》 as a Taiwan ebook product dated 2026-09-18; Sanmin lists EISBN 9786264446433. [Books.com ebook](https://www.books.com.tw/products/E050357688); [Sanmin ebook](https://www.sanmin.com.tw/product/index/015899348)
- The current Passion Sisters roster includes 夏蕾, and the product is described as her first personal photobook; this supports a Taiwan-based creator connection. [Passion Sisters roster](https://www.lala-peace.tw/Team/9); [Books.com ebook](https://www.books.com.tw/products/E050357688)
- Live MuseBooks search for 夏蕾 returns the existing digital edition 9786264446433 with Readmoo, Pubu, and Sanmin listings and a stored edition cover, alongside a physical edition and a separate boxed physical work. [MuseBooks 夏蕾 query](https://musebooks.my/v1/books?q=%E5%A4%8F%E8%95%BE)
- Readmoo’s current photo-ebook category page lists 彭彭 and 夏蕾 among the available titles. Other displayed titles such as 瑟七, 向理來, 李雅英, 寶兒, TAKA, and SHOYA already have entries in the local Taiwan catalog or earlier round notes, so they were not counted as fresh additions in this pass. [Readmoo photo ebook category](https://reading.udn.com/ebook/store/store_cate.do?cid=114); [Current Taiwan catalog](../../scraper/taiwan-photobook-catalog.md)

### Inferences

- Keep 9786264448314 as 彭彭’s known digital edition identifier because Books.com and BOOK☆WALKER agree and it is the identifier stored in the live record. Flag HyRead’s 9786264448321 and 191-page figure for publisher/platform clarification; do not create another edition from that discrepancy alone. [Books.com ebook](https://www.books.com.tw/products/E050359832); [BOOK☆WALKER product 311413](https://www.bookwalker.com.tw/product/311413); [HyRead demo ebook](https://demo.ebook.hyread.com.tw/bookDetail.jsp?id=518699); [MuseBooks 彭然心動 query](https://musebooks.my/v1/books?q=%E5%BD%AD%E7%84%B6%E5%BF%83%E5%8B%95)

### Gaps

- Books.com and BOOK☆WALKER identify 彭彭’s EISBN as 9786264448314, but HyRead identifies 9786264448321; Books.com gives no ebook page count, while HyRead reports 191. The publisher’s authoritative digital-asset metadata was not located. [Books.com ebook](https://www.books.com.tw/products/E050359832); [BOOK☆WALKER product 311413](https://www.bookwalker.com.tw/product/311413); [HyRead demo ebook](https://demo.ebook.hyread.com.tw/bookDetail.jsp?id=518699)

## What should be added or rechecked after this research pass?

### Takeaway

No new completed digital edition is import-ready from this pass. Keep 《FOUR》 on hold pending delivery and cover verification; do not duplicate 彭彭 or 夏蕾, and consider a later metadata-only reconciliation for 彭彭.

### Cited Findings

- 《FOUR》 remains an active preorder with estimated December fulfillment, and the promised PDF is supplied only after campaign close and production; no final cover or ISBN/EISBN is published on the cited campaign materials. [Zeczec campaign](https://www.zeczec.com/projects/ADAM2026); [Zeczec FAQ](https://www.zeczec.com/projects/ADAM2026/faqs)
- MuseBooks already stores the 彭彭 and 夏蕾 digital editions and their covers, even though the current Markdown catalog lacks 彭彭’s digital row. [MuseBooks 彭彭 query](https://musebooks.my/v1/books?q=%E5%BD%AD%E7%84%B6%E5%BF%83%E5%8B%95); [MuseBooks 夏蕾 query](https://musebooks.my/v1/books?q=%E5%A4%8F%E8%95%BE); [Current Taiwan catalog](../../scraper/taiwan-photobook-catalog.md#L827)
- This pass checked the live Zeczec project, Readmoo’s photo-ebook category, direct Books.com/HyRead/Sanmin pages, and live MuseBooks title queries; it does not establish that every Taiwan digital store or creator storefront has been exhaustively searched. [Zeczec campaign](https://www.zeczec.com/projects/ADAM2026); [Readmoo photo ebook category](https://reading.udn.com/ebook/store/store_cate.do?cid=114)

### Inferences

- The only current round-15 follow-up is to revisit 《FOUR》 after fulfillment and resolve 彭彭’s conflicting eISBN metadata if the publisher or retailers clarify it; this assignment made no catalog, database, or R2 changes. [Zeczec FAQ](https://www.zeczec.com/projects/ADAM2026/faqs); [Books.com ebook](https://www.books.com.tw/products/E050359832); [HyRead demo ebook](https://demo.ebook.hyread.com.tw/bookDetail.jsp?id=518699)

### Gaps

- No final digital file or cover for 《FOUR》 is available yet from the cited campaign information, and no authoritative source resolved the Peng ebook metadata discrepancy. [Zeczec FAQ](https://www.zeczec.com/projects/ADAM2026/faqs); [HyRead demo ebook](https://demo.ebook.hyread.com.tw/bookDetail.jsp?id=518699)
