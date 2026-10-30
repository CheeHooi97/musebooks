# Taiwan digital creator photobooks — Round 19 (checked 2026-10-30)

## Verified digital edition — DUPLICATE

### Takeaway

Rakuten Girls × Yanmaga Taiwan Kobo edition is import-grade but already present in MuseBooks; no DB or R2 change is needed.

### Cited Findings

- PChome lists a nonphysical fixed-layout EPUB3 ebook, item `DJBQ2E-D900KE504`, ISBN 8982431001000, 講談社, release 2026-08-31, NT$650, featuring 穎樂、高橋佳帆、笑笑、溫妮. [PChome product](https://24h.pchome.com.tw/books/prod/DJBQ2E-D900KE504)
- The official Yanmaga Taiwan page confirms the four subjects and says the Taiwan edition adds 20 black-swimsuit pages. [Yanmaga Taiwan page](https://ymclub.kodansha.co.jp/pages/yanmaga-cup-tw)
- PChome’s title-matched cover returned HTTP 200 (`image/jpeg`, 149,522 bytes), SHA-256 `106fed6c775fd6bdd70e76e58e1fec1cac9897a5530747241b166d861bfbb6ba`. [Cover image](https://img.pchome.com.tw/cs/items/DJBQ2ED900KE504/000001_1788469203.jpg)
- Live MuseBooks query returned one exact match: `work-tw-76b3b9559d5cbb77566e2795`, edition `edition-99a8b5430bbd6b8fc29e61c4`, same ISBN/date, Taiwan Kobo label, and active NT$650 PChome offer. [API title query](https://musebooks.my/v1/books?q=%E6%A8%82%E5%A4%A9%E5%A5%B3%E5%AD%A9%20Yanmaga%20%E6%95%B8%E4%BD%8D%E5%AF%AB%E7%9C%9F%E9%9B%86); [MuseBooks work](https://musebooks.my/books/work-tw-76b3b9559d5cbb77566e2795)

### Inferences

- **DUPLICATE**; its matching edition, source offer, cover, price, and release date are already recorded. [MuseBooks work](https://musebooks.my/books/work-tw-76b3b9559d5cbb77566e2795)

### Gaps

- Total page count is not stated; the 20 pages are only the Taiwan-specific addition. [PChome product](https://24h.pchome.com.tw/books/prod/DJBQ2E-D900KE504); [Yanmaga Taiwan page](https://ymclub.kodansha.co.jp/pages/yanmaga-cup-tw)

## Possible individual mini photobook — 笑笑 / シャオシャオ (HOLD)

### Takeaway

A separate 2026 digital mini title appears to be absent from the database, but its direct retailer page and cover remain unverified. Do not import yet.

### Cited Findings

- Kodansha’s official Yanmaga Cup listing names a separate “Rakuten Girls mini photo book — シャオシャオ — Yanmaga digital photo book.” [Kodansha listing](https://www.kodansha.co.jp/book/products/0000429233)
- FindBook lists the localized title, identifier 8982002000020, 講談社, date 2026-04-24, Japanese language, and a $150 Kobo ebook offer; it does not label the currency and is an aggregator. [FindBook item](https://findbook.com.tw/8982002000020)
- The official campaign identifies 笑笑 among the four Rakuten Girls selected for the project; the Yanmaga notice calls シャオシャオ a Taiwan cheerleader. [Yanmaga Taiwan page](https://ymclub.kodansha.co.jp/pages/yanmaga-cup-tw); [Yanmaga profile/product notice](https://ymclub.kodansha.co.jp/products/%E6%A5%BD%E5%A4%A9%E3%82%AC%E3%83%BC%E3%83%AB%E3%82%BA-%E3%82%B7%E3%83%A3%E3%82%AA%E3%82%B7%E3%83%A3%E3%82%AA-%E5%8F%B0%E6%B9%BE%E3%83%81%E3%82%A2%E3%81%AE%E8%B2%B4%E9%87%8D%E3%81%99%E3%81%8E%E3%82%8B%E6%B0%B4%E7%9D%80%E3%82%B0%E3%83%A9%E3%83%93%E3%82%A2%E3%82%92%E8%A6%8B%E9%80%83%E3%81%99%E3%81%AA?variant=52118563127617)
- MuseBooks queries for identifier `8982002000020` and the mini title returned zero. Query `笑笑` returned only the existing four-member group edition above. [API identifier query](https://musebooks.my/v1/books?q=8982002000020); [API title query](https://musebooks.my/v1/books?q=Rakuten%20Girls%20%E8%BF%B7%E4%BD%A0%E5%AF%AB%E7%9C%9F%E9%9B%86%20%E7%AC%91%E7%AC%91); [API subject query](https://musebooks.my/v1/books?q=%E7%AC%91%E7%AC%91)

### Inferences

- **HOLD** pending an item-specific Kobo/source page, exact format and current price/currency, total pages, and title-matched cover. [Kodansha listing](https://www.kodansha.co.jp/book/products/0000429233); [FindBook item](https://findbook.com.tw/8982002000020)

### Gaps

- No direct Taiwan store URL, page count, verified cover, or direct price/currency evidence was found. [FindBook item](https://findbook.com.tw/8982002000020)

## Other likely digital discoveries — DUPLICATES

### Takeaway

Other recent Taiwan ebook searches surfaced existing MuseBooks works, not new import candidates.

### Cited Findings

- “一棋一會” is already one work with digital ISBN 9786264343435 and physical ISBN 9786264343466. [MuseBooks API query](https://musebooks.my/v1/books?q=%E4%B8%80%E6%A3%8B%E4%B8%80%E6%9C%83); [Books.com ebook](https://www.books.com.tw/products/E050302727)
- “曼曼喜歡你” is already digital ISBN 9786264036115. [MuseBooks work](https://musebooks.my/books/work-tw-03c5ae12b61ad3d1e9c5b3b5); [Sanmin listing](https://www.sanmin.com.tw/product/index/013978283)
- Searches also matched existing digital works “元來有你,” “Heartbeat 芳婷,” “洛入你心,” and “彭然心動.” [API queries: 元來有你](https://musebooks.my/v1/books?q=%E5%85%83%E4%BE%86%E6%9C%89%E4%BD%A0), [芳婷](https://musebooks.my/v1/books?q=Heartbeat%20%E8%8A%B3%E5%A9%B7), [洛入你心](https://musebooks.my/v1/books?q=%E6%B4%9B%E5%85%A5%E4%BD%A0%E5%BF%83), [彭然心動](https://musebooks.my/v1/books?q=%E5%BD%AD%E7%84%B6%E5%BF%83%E5%8B%95)

### Inferences

- No import-ready new digital title cleared the direct-product, Taiwan creator, duplicate, and usable-cover checks in this pass.

### Gaps

- Follow up on the 笑笑 mini-title only if its direct seller page or an official purchase link becomes available. [Kodansha listing](https://www.kodansha.co.jp/book/products/0000429233)

## Focused follow-up — 笑笑 / シャオシャオ (HOLD)

- **Creator fit:** Taiwanese outlet Mirror Media identifies 笑笑 as 劉姿妤 and reports her selection for the Taiwan Beer Leopards’ cheer squad; NOWnews also identifies her as a Rakuten Girls and Leopard Girls cheerleader. This supports a Taiwan-based creator connection, but the sources do not establish her birthplace or nationality. [Mirror Media](https://www.mirrormedia.mg/story/20240314ent026?from=referral_bottom); [NOWnews](https://www.nownews.com/news/6877528)
- **Product evidence:** Kodansha’s listing and FindBook support a separate Japanese-language digital mini-book, with FindBook ID `8982002000020`, date `2026-04-24`, and an ebook offer shown as `$150` (currency unspecified). Targeted searches did not locate the direct Kobo item page; the Kobo request was inaccessible (403). No directly verifiable page count, retailer format metadata, or price/currency was available. [Kodansha](https://www.kodansha.co.jp/book/products/0000429233); [FindBook](https://findbook.com.tw/8982002000020)
- **Cover:** No title-matched downloadable ebook cover was verified, so there is no cover hash. The official Yanmaga campaign/episode thumbnail is not established as the ebook cover. [Yanmaga campaign](https://ymclub.kodansha.co.jp/pages/yanmaga-cup-tw); [episode thumbnail page](https://yanmaga.jp/gravures/books/Rakuten_Girls%E3%83%A4%E3%83%B3%E3%82%B0%E3%83%9E%E3%82%AC%E3%82%B8%E3%83%B3_%E3%83%A4%E3%83%B3%E3%83%9E%E3%82%AC%E6%9D%AF_%E7%AC%91%E7%AC%91%E3%82%B7%E3%83%A3%E3%82%AA%E3%82%B7%E3%83%A3%E3%82%AA/2cc08728279df2cf707b6d0803b64e4f)
- **MuseBooks:** Live queries for `8982002000020` and the mini-book title returned zero matches; the subject query returned only the existing Rakuten Girls group edition. [ID query](https://musebooks.my/v1/books?q=8982002000020); [title query](https://musebooks.my/v1/books?q=Rakuten%20Girls%20%E8%BF%B7%E4%BD%A0%E5%AF%AB%E7%9C%9F%E9%9B%86%20%E7%AC%91%E7%AC%91%20Yanmaga%20Cup); [subject query](https://musebooks.my/v1/books?q=%E7%AC%91%E7%AC%91)

**Decision: HOLD.** Taiwan team affiliation and a likely digital mini-book are supported, but no direct seller page, complete seller metadata, title-matched cover, or definitive Taiwan-origin evidence clears the import bar. No catalog, database, or R2 changes were made.

