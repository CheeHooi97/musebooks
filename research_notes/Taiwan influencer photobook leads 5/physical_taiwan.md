# Physical Taiwan creator photobooks

## Are any new import-grade physical editions absent from both records?

### Takeaway

No import-grade new physical edition was confirmed absent from both the local catalog and live MuseBooks API. The strongest newly announced physical candidate is Rina 謝艾娜’s 《盛夏・謝艾娜》, but the available campaign and reseller records do not establish core bibliographic fields or a direct cover asset, so it remains unverified.

### Cited Findings

- A 2026-08-17 campaign announcement, credited to 杰斯汀整合行銷, identifies Rina’s first personal **physical photobook** as 《盛夏・謝艾娜》 and says preorder was scheduled for 2026-08-19 through 2026-08-31; it says sales-platform information would follow, but gives no publisher, ISBN, page count, or publication date. [Campaign announcement](https://www.estarlight.idv.tw/2026/08/rina.html)
- A current third-party Ruten item names 《盛夏・謝艾娜》寫真書 and advertises a book with a hard case, standee, and postcards, but the result does not supply ISBN, pagination, publisher, or publication date. The page could not be fetched during this pass, so its image could not be verified as a final cover. [Ruten reseller listing](https://www.ruten.com.tw/item/22640770348621/)
- Rina is a Taiwan-market cheerleader: reporting on the release describes her as joining the Taoyuan Cloud Leopard Flyers’ 桃氣女孩 team and identifies her as Rina 謝艾娜. [CTi News](https://ctinews.com/news/items/4bnbjEjDnP)
- Exact-title search returned no 《盛夏・謝艾娜》 entry in the checked local catalog. The live API exact-title query returned no item; searching 謝艾娜 returns the distinct 2024 digital title 《娜就愛吧 謝艾娜Rina數位寫真》, not this physical book. [Local catalog](../../scraper/taiwan-photobook-catalog.md); [API title query](https://musebooks.my/v1/books?q=%E7%9B%9B%E5%A4%8F%E3%83%BB%E8%AC%9D%E8%89%BE%E5%A8%9C); [API creator query](https://musebooks.my/v1/books?q=%E8%AC%9D%E8%89%BE%E5%A8%9C); [尖端 listing for the distinct digital work](https://www.espp.com.tw/ctn.aspx?bc=EAFB0092-001)

### Inferences

- Treat 《盛夏・謝艾娜》 as an **unverified lead**, not an import candidate: the format, title, creator, and preorder window are supported, but the retailer/publisher evidence needed to identify and describe a stable edition is incomplete. [Campaign announcement](https://www.estarlight.idv.tw/2026/08/rina.html); [Ruten reseller listing](https://www.ruten.com.tw/item/22640770348621/)

### Gaps

- Missing: an accessible publisher or primary retailer product record; confirmed publisher/imprint; ISBN; final publication/issue date; page count; and a direct, identified cover-image asset. The campaign article says its sales platforms were to be announced later, and the Ruten page was not fetchable in this pass. [Campaign announcement](https://www.estarlight.idv.tw/2026/08/rina.html); [Ruten reseller listing](https://www.ruten.com.tw/item/22640770348621/)

## What recently announced or upcoming Taiwan-linked books were already recorded?

### Takeaway

Several strong 2026 candidates are already in the local catalog, the public API, or both, so they are not new edition leads. One upcoming cheerleader photobook, 禹洙漢同名寫真, is complete on a retailer record and present in the API, but its stated 2026-11-03 publication date falls after the 2026-10-30 scope.

### Cited Findings

- 《芷想靠近你：劉芷伊醫師寫真》 is in the local catalog and live API as a physical edition (ISBN **9786264444811**, **144 pages**, 時報文化, 2026-10-13). Kingstone identifies the print format, date, ISBN, and pages and describes 劉芷伊 as a Taiwan dentist; the API also records a separate digital edition. [Kingstone listing](https://www.kingstone.com.tw/basic/2019900107137/); [API query](https://musebooks.my/v1/books?q=%E8%8A%B7%E4%BC%8A%E9%86%AB%E5%B8%AB); [local catalog](../../scraper/taiwan-photobook-catalog.md)
- 《芷想被你收藏Candy芷媗首本個人實體寫真》 is in both records. Its producer’s product page gives **144 pages**, paperback binding, 2025-10-23 release date, company, and ISBN **9786269273300**; the National Central Library’s monthly new-book list independently identifies the print bibliographic record. [iWIN product page](https://www.iwinimc.com/products/candy1023-photobook); [NCL new-book list](https://isbn.ncl.edu.tw/FCKEDITOR_UploadFiles/1763434068.pdf); [API work record](https://musebooks.my/books/work-tw-bd736260748f93769128a0f1); [local catalog](../../scraper/taiwan-photobook-catalog.md)
- 《心動蕾達：夏蕾寫真》 and 《2026 禾你相羽 in Okinawa》 already have physical editions in both records. The latter remains bibliographically incomplete in the current record: its official shop says pages and ISBN are unpublished and 2026-09-15 was an estimated shipping date, but that does not make it a new unrecorded work. [時報 official product page](https://www.readingtimes.com.tw/product/?pid=1VY0480); [KABOOM product page](https://www.kaboom.tw/products/2026-kimi-in-okinawa-photo-book); [API query for 夏蕾](https://musebooks.my/v1/books?q=%E5%BF%83%E5%8B%95%E8%95%BE%E9%81%94); [API query for 禾羽](https://musebooks.my/v1/books?q=%E7%A6%BE%E4%BD%A0%E7%9B%B8%E7%BE%BD); [local catalog](../../scraper/taiwan-photobook-catalog.md)
- 《綾の邊界 きわ》阿厚綾 and 《向你走來：向理來寫真》 also appear in the local catalog and API as physical titles. [Kingstone 阿厚綾 listing](https://www.kingstone.com.tw/basic/2075020023320/); [Sanmin 向理來 listing](https://www.sanmin.com.tw/product/index/015549423); [API query for 阿厚綾](https://musebooks.my/v1/books?q=%E9%98%BF%E5%8E%9A%E7%B6%BE); [API query for 向理來](https://musebooks.my/v1/books?q=%E5%90%91%E4%BD%A0%E8%B5%B0%E4%BE%86); [local catalog](../../scraper/taiwan-photobook-catalog.md)
- 博客來 lists 禹洙漢同名寫真 = SUHAN WOO PHOTOGRAPHY as a **paperback**, ISBN **9786267742365**, **144 pages**, 水靈文創, scheduled for **2026-11-03**; its author description says she came from Korea and joined Rakuten Girls in Taiwan. The live API already contains its physical edition, although the local catalog search found no title match. This is both API-duplicate and post-cutoff, not a new in-scope edition. [Books.com.tw product record](https://www.books.com.tw/products/0011066810?loc=P_0103_005); [API query](https://musebooks.my/v1/books?q=%E7%A6%B9%E6%B4%99%E6%BC%A2); [local catalog](../../scraper/taiwan-photobook-catalog.md)
- The local catalog also already lists TAKA’s physical 《TAKA：深夜名堂男子寫真》 and Rina’s earlier digital 《娜就愛吧》; neither is a new physical edition for this pass. [Kingstone TAKA listing](https://www.kingstone.com.tw/basic/2019910061054/); [尖端 Rina digital listing](https://www.espp.com.tw/ctn.aspx?bc=EAFB0092-001); [local catalog](../../scraper/taiwan-photobook-catalog.md)

### Inferences

- The verified creator/cheerleader releases already indexed in 2026—including the October 劉芷伊 paperback—should be treated as reconciliation checks, not additions. The only in-window new physical lead found that was absent from both systems is Rina’s incomplete 《盛夏・謝艾娜》 announcement. [Kingstone 劉芷伊 record](https://www.kingstone.com.tw/basic/2019900107137/); [Rina campaign announcement](https://www.estarlight.idv.tw/2026/08/rina.html)

### Gaps

- I did not establish whether additional small-press or creator-only physical photobooks were announced outside retailer indexing. Retailer/new-book discovery and exact title/creator searches are not exhaustive of social-only preorder campaigns. [Sanmin photobook search](https://www.sanmin.com.tw/search?k=%E5%AF%AB%E7%9C%9F%E6%9B%B8&ls=ed&pt=t); [Books.com.tw physical-photo category](https://www.books.com.tw/web/books_bmidm_2204/?loc=P_0001_2_174)

## What is import-ready, and what evidence remains outstanding?

### Takeaway

There are **zero import-grade new editions** from this pass. Rina’s 《盛夏・謝艾娜》 is the only newly identified in-scope physical lead absent from both local and API records, and must remain unverified until its bibliographic and cover evidence is found.

### Cited Findings

- The campaign source confirms a physical photobook and preorder period but explicitly says selling-platform information would be released later; the current reseller record does not supply the missing bibliographic fields, while the local catalog and API title query have no matching physical edition. [Campaign announcement](https://www.estarlight.idv.tw/2026/08/rina.html); [Ruten listing](https://www.ruten.com.tw/item/22640770348621/); [local catalog](../../scraper/taiwan-photobook-catalog.md); [API title query](https://musebooks.my/v1/books?q=%E7%9B%9B%E5%A4%8F%E3%83%BB%E8%AC%9D%E8%89%BE%E5%A8%9C)

### Inferences

- Do not create an edition record for 《盛夏・謝艾娜》 yet. The verified announcement establishes a genuine physical project, but the exact book edition and cover are not sufficiently documented for import. [Campaign announcement](https://www.estarlight.idv.tw/2026/08/rina.html)

### Gaps

- Required follow-up evidence is a primary product page (or library/publisher record) that confirms ISBN, publisher, publication date and pagination, plus its direct cover image. [Campaign announcement](https://www.estarlight.idv.tw/2026/08/rina.html); [Ruten reseller listing](https://www.ruten.com.tw/item/22640770348621/)
