# Taiwan physical photobook retail sweep

## Is there a verified new Taiwan-origin creator photobook to import?

### Takeaway
No GO this round: the strongest recently surfaced retail candidate, 彭彭’s 《彭然心動》, is already represented in MuseBooks, as are the other current physical-title leads checked. I found no uncatalogued title that cleared the required origin, product, and cover-evidence checks; therefore there is no new cover to prepare for R2 and no catalog/DB/R2 action was taken.

### Cited Findings
- 城邦讀書花園’s direct product page identifies 彭彭 and 黃天仁 as authors, 時報出版 as publisher, release date 2026-09-11, ISBN 9786264448420, paperback, and 144 pages; its indexed product state said the new book had not yet arrived in stock, so current fulfillment is unresolved. [Retailer product page](https://www.cite.com.tw/book?id=108961)
- Taiwan’s FTV reports 彭彭 joined Rakuten Girls after basketball cheerleading, supporting the Taiwan creator/cheerleader association for this candidate. [FTV profile](https://www.ftvnews.com.tw/news/detail/2025A03W0279)
- The live title/person query `q=彭然心動` returned one matching work, `work-tw-48cee531f79d279264813cd3`; `q=彭彭` returned the same one work. [MuseBooks title query](https://musebooks.my/v1/books?q=%E5%BD%AD%E7%84%B6%E5%BF%83%E5%8B%95&pageSize=50), [person query](https://musebooks.my/v1/books?q=%E5%BD%AD%E5%BD%AD&pageSize=50)

### Inferences
- The title/product/origin checks do not justify importing this already-cataloged title.

### Gaps
- I did not find a separate source establishing 彭彭’s birthplace or nationality; the evidence establishes association with a Taiwan cheerleading team. This origin gap does not affect the duplicate decision.
- Retailer stock/shipping status is not conclusive: the book is listed, but the indexed 城邦 page says it had not yet arrived in stock.

## Do the other recent physical leads already exist in MuseBooks?

### Takeaway
Live title/person queries returned matching work records for the recent seller and publisher leads checked. Search-by-ISBN through `/v1/books?q=` returned zero even for known records, so that endpoint’s q parameter cannot be used as an ISBN absence check.

### Cited Findings
- The MuseBooks ISBN query `q=9786264448420` returned zero, but the endpoint only searches title/name fields; this zero is not a duplicate or absence signal. [MuseBooks ISBN query](https://musebooks.my/v1/books?q=9786264448420&pageSize=50)
- 《禾你相羽 in Okinawa》 is sold through the direct Kaboom shop and already has a live MuseBooks work `work-tw-d83d47417493a7a1f42f626e`; `q=禾羽` also returns its existing entry. [Kaboom product page](https://www.kaboom.tw/products/2026-kimi-in-okinawa-photo-book), [MuseBooks title query](https://musebooks.my/v1/books?q=%E7%A6%BE%E4%BD%A0%E7%9B%B8%E7%BE%BD%20in%20Okinawa&pageSize=50), [person query](https://musebooks.my/v1/books?q=%E7%A6%BE%E7%BE%BD&pageSize=50)
- 《心動蕾達：夏蕾寫真》 is listed by the publisher and ebook seller; live title query returns two records, including `work-tw-44b0143f8e9afb4d9fff0e09`. This is a duplicate/multiple-record signal to leave for separate catalog QA, not a new import. [時報出版 product page](https://www.readingtimes.com.tw/product/?pid=1VY0480), [Readmoo ebook product page](https://reading.udn.com/ebook/store/store_product.do?pid=173955), [MuseBooks title query](https://musebooks.my/v1/books?q=%E5%BF%83%E5%8B%95%E8%95%BE%E9%81%94&pageSize=50)
- 《芷想靠近你：劉芷伊醫師寫真》 exists as `work-tw-0fe3296d84c633e5ab200c65`; 《芷想被你收藏Candy芷媗首本個人實體寫真》 exists as `work-tw-bd736260748f93769128a0f1`. [Books.com.tw category listing](https://www.books.com.tw/web/books_bmidm_2204/?loc=P_0001_2_174), [MuseBooks title query for 芷伊](https://musebooks.my/v1/books?q=%E8%8A%B7%E6%83%B3%E9%9D%A0%E8%BF%91%E4%BD%A0&pageSize=50), [MuseBooks title query for 芷媗](https://musebooks.my/v1/books?q=%E8%8A%B7%E6%83%B3%E8%A2%AB%E4%BD%A0%E6%94%B6%E8%97%8F&pageSize=50)
- Other title/person queries also matched existing works: 周感恩 (`work-tw-aa6e6382632cf200d0a3d05c`), 安生 (`work-tw-53f4134579704b7535fb87aa`), 陳葳 (`work-tw-97188d1ee436dbdbe4c1923e`), 郭郭 (`work-tw-f9cfb820c42b901a88a196de`), 黃氏兄弟’s 《有你的旅程》 (`work-tw-a682a99d8303d3a9328b15ff`) and 《有你的夏天》 (`work-tw-6255401cda979711c736496a`), 《敏綺Miki同名寫真》 (`work-tw-7c5236d4baf87679d49a533b`), and 《雪之下．岑之名》 (`work-tw-b509bca8b9edd4b2078b1a20`). [ShaShin publisher retail list](https://www.books.com.tw/web/sys_puballb/books/?pubid=shashin), [黃氏兄弟 creator-agency announcement](https://www.capsuleinc.cc/creators-news-inner/621), [NCL catalog record for 雪之下．岑之名](https://isbn.ncl.edu.tw/FCKEDITOR_UploadFiles/1765854517.pdf), [MuseBooks query: 周感恩](https://musebooks.my/v1/books?q=%E5%91%A8%E6%84%9F%E6%81%A9&pageSize=50), [安生](https://musebooks.my/v1/books?q=%E5%AE%89%E7%94%9F%20Anshi&pageSize=50), [陳葳](https://musebooks.my/v1/books?q=%E9%99%B3%E8%91%B3%20VV%20Chen&pageSize=50), [郭郭](https://musebooks.my/v1/books?q=%E9%83%AD%E9%83%AD%20RAINY%20SUMMER&pageSize=50), [黃氏兄弟](https://musebooks.my/v1/books?q=%E9%BB%83%E6%B0%8F%E5%85%84%E5%BC%9F&pageSize=50), [敏綺](https://musebooks.my/v1/books?q=%E6%95%8F%E7%B6%BA&pageSize=50), [雪岑](https://musebooks.my/v1/books?q=%E9%9B%AA%E5%B2%91&pageSize=50)

### Inferences
- These are excluded from new additions because their direct title/person queries find existing MuseBooks work records. Query-by-ISBN is not a reliable duplicate check here: repository implementation limits `q` matching to original title, English title, and featured names. [catalog filter implementation](../../backend/repository/catalog_filters.go)

### Gaps
- ISBN-specific live verification would require an API route or database lookup that searches editions by ISBN; the public `/v1/books?q=` implementation does not search ISBN. I did not treat its zero-result ISBN queries as evidence of absence.
- I did not fetch/hash covers for other cataloged duplicate leads; 彭彭’s candidate is documented in the cover-evidence section below.

## Does the strongest candidate have verifiable title-specific cover evidence?

### Takeaway
Yes, the Kingstone page’s image clearly corresponds to 《彭然心動》 and was fetched and hashed. It is seller product artwork, not a verified final print proof, and belongs to an existing catalog record.

### Cited Findings
- Kingstone’s direct page identifies the title and ISBN and publishes the title-specific listing image. The page returned HTTP 200; its `og:image` URL was `https://assets.kingstone.com.tw/prodassets/6eb88_b08d773ad01db902b95c7fd34a6f5fb.jpg`. Download returned HTTP 200, `image/jpeg`, 67,623 bytes, SHA-256 `d8030f23819f33c335ede15864f5157d14f2884c7a52a89128730c67be1c74a6`. Visual inspection shows a promotional montage with a 3-D book mockup, two sample photos, and poster callout. [Kingstone product page](https://www.kingstone.com.tw/basic/2019900107007/)

### Inferences
- The seller image is sufficient to identify the existing title asset but cannot establish final printed appearance.

### Gaps
- No publisher proof or photograph of the final printed cover was found during this sweep.
