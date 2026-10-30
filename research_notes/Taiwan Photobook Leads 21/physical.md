# Physical retailer sweep — Round 21

## Did any newly surfaced retailer title qualify as an uncatalogued Taiwan creator photobook?

### Takeaway
No new import-ready title emerged. The strongest apparently fresh direct-retailer lead, 安于晴 (Charlene)’s 《不安于室》, is already in MuseBooks with a matching physical edition and R2 cover; other promising creator searches also resolved to existing catalog entries.

### Cited Findings
- RedBoy’s direct product page identifies 《不安于室》 as Charlene’s physical photobook and supplies its release date (2025-01-05), 144 pages, 182 × 257 mm trim, publisher (子席國際股份有限公司), price (NT$799), and “sold out” status. The page also names the featured subject as 安于晴 and gives the creator’s first-person description. It does not list an ISBN. [RedBoy product page](https://redboy.com.tw/product/Charlene00A)
- The official product page’s cover asset is `https://redboy.com.tw/images/product/banner/Charlene00A_cover.jpg`. Its fetched 250,777-byte image has SHA-256 `7716fc885a60fe64fedc7dce61461f77761d79c9c7c477bec9b4d20088d9f781`, matching the existing MuseBooks cover-object key. The cover was fetched from the live API record’s signed cover URL as a read-only check; the API returned the same hash. [Official cover source](https://redboy.com.tw/images/product/banner/Charlene00A_cover.jpg); [MuseBooks work record](https://musebooks.my/books/work-tw-fa9869b2c733f4c7c40f2cd5)
- A profile/interview identifies 安于晴 as a Taiwanese model/actor, and a Taiwan entertainment report covers the book’s release. [GQ Taiwan interview](https://www.gq.com.tw/women/content-33156); [TVBS report](https://news.tvbs.com.tw/entertainment/2691887)
- A live MuseBooks API query by creator name, `q=安于晴&pageSize=50`, returned exactly one work: `work-tw-fa9869b2c733f4c7c40f2cd5`, title 《不安于室》-Charlene實體寫真書, with physical edition `edition-7ab42fa03b227f477bbe1a64`, release date 2025-01-05, 144 pages, and the same RedBoy metadata source. [MuseBooks API query](https://musebooks.my/v1/books?q=%E5%AE%89%E4%BA%8E%E6%99%B4&pageSize=50)
- The existing local Taiwan catalog also lists this same work and cover key. [Local catalog](../../scraper/taiwan-photobook-catalog.md)

### Inferences
- **DUPLICATE.** Product, subject, date, pagination, publisher, and exact cover hash align with the existing catalog/API record, so no DB or R2 write is warranted.
- The omission of ISBN by the seller does not block this duplicate finding because the direct title/subject and edition details match the existing record.

### Gaps
- No ISBN is displayed by the seller or stored for this existing edition. This is a metadata gap, not evidence of a second edition.

## Which other physical-retailer leads were duplicates or remain on hold?

### Takeaway
The sampled bookstore/publisher leads were duplicates. One ambiguous RedBoy listing, “七七師傅回來了,” remains a hold because the page does not establish that it is a photobook or identify its subject as a Taiwan creator.

### Cited Findings
- The Taiwan corner-stone retailer identifies 《魅：郭鬼鬼Angela寫真書(Ⅱ)》 as a 144-page Taiwan Kadokawa paperback, ISBN 9786263523463; the live MuseBooks creator query returned the existing work `work-tw-b741dd5f6e26bdc818bcc689` and both its physical and digital editions. [Retailer product page](https://www.tcsb.com.tw/product/9786263523463); [MuseBooks API query](https://musebooks.my/v1/books?q=%E9%83%AD%E9%AC%BC%E9%AC%BC&pageSize=50)
- Sanmin lists 解婕翎’s same-name physical photobook as ISBN 9789869224390; the live MuseBooks query by her name returned the existing physical work. [Sanmin product page](https://www.sanmin.com.tw/product/index/005481050); [MuseBooks API query](https://musebooks.my/v1/books?q=%E8%A7%A3%E5%A9%95%E7%BF%8E&pageSize=50)
- Cite lists 郭郭’s 《RAINY SUMMER SECRETS》 as a 120-page physical book, ISBN 9786267742167, dated 2025-09-29; MuseBooks already returns the matching work. [Cite product page](https://www.cite.com.tw/book?id=105020); [MuseBooks API query](https://musebooks.my/v1/books?q=%E9%83%AD%E9%83%AD&pageSize=50)
- Other live creator-name checks also returned catalog records for Candy 芷媗, 波波蓁, 陳可頡, 夏蕾, and 禾羽, so these were treated as duplicates rather than re-import candidates. The relevant first-party/retailer pages are [Candy](https://www.iwinimc.com/products/candy1023-photobook), [波波蓁](https://redboy.com.tw/product/redboy0049), [陳可頡](https://redboy.com.tw/product/redboy0041), [夏蕾 ebook](https://reading.udn.com/ebook/store/store_product.do?pid=173955), and [禾羽 ebook](https://24h.pchome.com.tw/books/prod/DJBQ2E-D900JY2UU); the live MuseBooks checks are [芷媗](https://musebooks.my/v1/books?q=%E8%8A%B7%E5%AA%97&pageSize=50), [波波蓁](https://musebooks.my/v1/books?q=%E6%B3%A2%E6%B3%A2%E8%93%81&pageSize=50), [陳可頡](https://musebooks.my/v1/books?q=%E9%99%B3%E5%8F%AF%E9%A0%A1&pageSize=50), [夏蕾](https://musebooks.my/v1/books?q=%E5%A4%8F%E8%95%BE&pageSize=50), and [禾羽](https://musebooks.my/v1/books?q=%E7%A6%BE%E7%BE%BD&pageSize=50).
- RedBoy’s direct listing for “七七師傅回來了” has no useful bibliographic description: its page description and specification field say `n`, and there is no ISBN, pagination, dimensions, or explicit photobook format. A MuseBooks query for the exact title returned zero works. [RedBoy listing](https://redboy.com.tw/product/redboy0029); [MuseBooks API query](https://musebooks.my/v1/books?q=%E4%B8%83%E4%B8%83%E5%B8%AB%E5%82%85%E5%9B%9E%E4%BE%86%E4%BA%86&pageSize=50)

### Inferences
- **DUPLICATE:** 郭鬼鬼, 解婕翎, 郭郭, Candy 芷媗, 波波蓁, 陳可頡, 夏蕾, and 禾羽 based on matching live catalog searches; do not import again.
- **HOLD:** “七七師傅回來了.” A zero-result catalog query alone is not enough: the retailer page does not establish a qualifying photobook, a specific model, or a Taiwan-origin creator. Do not infer this title is related to the separate Taiwan influencer nicknamed 七七.

### Gaps
- For “七七師傅回來了,” a fuller direct product description, an unambiguous creator identity/origin, and book-specific bibliographic data are missing. Its title-matched cover was not treated as verified product-cover evidence.
