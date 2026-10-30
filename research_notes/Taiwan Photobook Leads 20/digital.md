# Digital Taiwan creator photobook sweep — Round 20

## Is the 笑笑 / シャオシャオ mini-book ready to import?

### Takeaway

**HOLD.** Kodansha confirms a digital-only Rakuten Girls mini-photo-book project and lists a シャオシャオ title among its member minis, but the evidence does not connect FindBook’s item ID `8982002000020` to a direct Taiwan retailer page or to a matching cover. No DB or R2 mutation is justified.

### Cited Findings

- Kodansha’s official product page is for the broader title *Rakuten Girls Mini Photo Book: Yanmaga Cup*. It marks the work as digital-only, gives release date 2026-04-27 and JDCN `06A0000000001019636K`, and lists ten member-specific mini-photo-book titles, including シャオシャオ. [Kodansha product record](https://www.kodansha.co.jp/book/products/0000429233)
- FindBook lists *Rakuten Girls 迷你寫真集 笑笑 Yanmaga Cup Yanmaga 數位寫真集*, ID `8982002000020`, date 2026-04-24, and an ebook offer from Kobo displayed as `$150`; it does not state the currency and is an aggregator rather than the seller page. [FindBook item](https://findbook.com.tw/8982002000020)
- The official Kodansha page’s `og:image` asset downloaded successfully over HTTP 200 as JPEG, 69,920 bytes, SHA-256 `bdb7e2fd1ff644812b05d27db44b1eae84511aaed09051fe3d7208cbb8e4d158`. The downloaded image visibly names 高橋佳帆, so it is not verified as a cover for the 笑笑 mini-book. [Kodansha image](https://dvs-cover.kodansha.co.jp/0000429233/3Imo3PF8TywvuwAePzoHfNqRAX4sBjo7iilxvymT.jpg)
- The Yanmaga Taiwan campaign and official member/product notice connect 笑笑 / シャオシャオ to the Rakuten Girls Taiwan cheerleader project. This supports a Taiwan-related creator connection, while the campaign affiliation alone does not establish birthplace or nationality. [Yanmaga Taiwan campaign](https://ymclub.kodansha.co.jp/pages/yanmaga-cup-tw); [Yanmaga member notice](https://ymclub.kodansha.co.jp/products/%E6%A5%BD%E5%A4%A9%E3%82%AC%E3%83%BC%E3%83%AB%E3%82%BA-%E3%82%B7%E3%83%A3%E3%82%AA%E3%82%B7%E3%83%A3%E3%82%AA-%E5%8F%B0%E6%B9%BE%E3%83%81%E3%82%A2%E3%81%AE%E8%B2%B4%E9%87%8D%E3%81%99%E3%81%8E%E3%82%8B%E6%B0%B4%E7%9D%80%E3%82%B0%E3%83%A9%E3%83%93%E3%82%A2%E3%82%92%E8%A6%8B%E9%80%83%E3%81%99%E3%81%AA?variant=52118563127617)
- Live MuseBooks API checks returned zero for identifier `8982002000020`, the localized mini title, and `シャオシャオ`. The subject search `笑笑` returns one different work, the existing four-member *樂天女孩 Yanmaga 數位寫真集* (work `work-tw-76b3b9559d5cbb77566e2795`, edition `edition-99a8b5430bbd6b8fc29e61c4`, ISBN `8982431001000`) with direct Kobo source `https://www.kobo.com/tw/zh/ebook/kobo-rakuten-girls-2`. [API identifier query](https://musebooks.my/v1/books?q=8982002000020); [API title query](https://musebooks.my/v1/books?q=Rakuten%20Girls%20%E3%83%9F%E3%83%8B%E5%86%99%E7%9C%9F%E9%9B%86%20%E7%AC%91%E7%AC%91%20Yanmaga%20Cup); [API subject query](https://musebooks.my/v1/books?q=%E7%AC%91%E7%AC%91); [existing group Kobo page](https://www.kobo.com/tw/zh/ebook/kobo-rakuten-girls-2)

### Inferences

- **HOLD**, not a duplicate: the existing four-person Kobo edition is a separate group title; the standalone mini-book still lacks direct seller confirmation and a title-matched cover. [Kodansha product record](https://www.kodansha.co.jp/book/products/0000429233); [existing group Kobo page](https://www.kobo.com/tw/zh/ebook/kobo-rakuten-girls-2)

### Gaps

- No direct Taiwan Kobo item page was located for the 笑笑 mini. Exact seller price/currency, pages, retailer identifier-to-JDCN/ISBN mapping, and the mini’s own cover remain unverified. [FindBook item](https://findbook.com.tw/8982002000020); [Kodansha product record](https://www.kodansha.co.jp/book/products/0000429233)

## Did the fresh direct-retailer sweep produce another Taiwan-origin ebook?

### Takeaway

No fresh candidate cleared the Taiwan-origin, exact-product, duplicate, and cover checks. The best unresolved Pubu lead was `關關寫真集2-Vol.02`, but its subject’s identity and Taiwan origin are unclear, so it stays on hold.

### Cited Findings

- Pubu’s direct page for `關關寫真集2-Vol.02` identifies an ebook PDF (73 pages), product ID `604421`, release date 2025-09-11, with prices NT$699 (DRM) and NT$1,399 (DRM-free). Its description calls the subject “網紅教練關關” but provides no full name or origin evidence. [Pubu product](https://www.pubu.com.tw/ebook/604421)
- Pubu’s product-page `og:image` is a title-matched cover: HTTP 200, JPEG, 158,463 bytes, SHA-256 `1fb65cb6ac2dabadf9a5640ca4f6b886136670a76dc2c1c525b277abe8e74f5a`. The cover reads “G-JAN 關關 II / Fitness Prince,” but does not establish the subject’s legal identity or origin. [Pubu cover](https://res1.pubu.tw/docs/512992/13071/QXSQbl_l.jpg); [Pubu product](https://www.pubu.com.tw/ebook/604421)
- Live MuseBooks checks for `604421`, the exact title, and `關關` each returned zero. The lead remains not import-ready because the direct listing and cover do not securely identify a Taiwan-origin creator. [API item-ID query](https://musebooks.my/v1/books?q=604421); [API title query](https://musebooks.my/v1/books?q=%E9%97%9C%E9%97%9C%E5%AF%AB%E7%9C%9F%E9%9B%862-Vol.02); [API subject query](https://musebooks.my/v1/books?q=%E9%97%9C%E9%97%9C)
- The existing digital title *答應你：林岱縈寫真* already has two digital editions in MuseBooks, including Pubu ISBN `9786263746688`; it is a duplicate rather than a new import. [Pubu item](https://m.pubu.com.tw/ebook/401983); [MuseBooks API creator query](https://musebooks.my/v1/books?q=%E6%9E%97%E5%B2%B1%E7%B8%88)
- The direct Pubu catalog page lists the 2026 team ebook *FIRST JUMP：TOKKI CUTIE 臺北伊斯特啦啦隊寫真故事 2025-2026* (ID `668172`, EPUB, 156 pages, 2026-04-30). MuseBooks already has a matching digital work and an associated physical work, so this is not a new title. [Pubu product](https://www.pubu.com.tw/bookbuffet/ebook/668172); [MuseBooks API title query](https://musebooks.my/v1/books?q=FIRST%20JUMP)
- The *彭然心動* ebook and *Babe Fantasy* ebook are already digital editions in their corresponding MuseBooks works; their direct listings surfaced again during the search but do not represent new editions to import. [Books.com彭彭 ebook](https://www.books.com.tw/products/E050359832); [MuseBooks API 彭彭 query](https://musebooks.my/v1/books?q=%E5%BD%AD%E5%BD%AD); [MuseBooks API Babe Fantasy query](https://musebooks.my/v1/books?q=Babe%20Fantasy)

### Inferences

- **HOLD** `關關寫真集2-Vol.02`; **DUPLICATE** `答應你`, `FIRST JUMP`, `彭然心動`, and `Babe Fantasy`. No candidate from this sweep warranted an R2 upload or catalog write. [Pubu product](https://www.pubu.com.tw/ebook/604421); [MuseBooks API](https://musebooks.my/v1/books?q=%E6%9E%97%E5%B2%B1%E7%B8%88)

### Gaps

- The `關關` page does not identify a full creator name, establish Taiwan origin, state an ISBN, or expose enough verified cover provenance to clear import review. [Pubu product](https://www.pubu.com.tw/ebook/604421)

## Are any apparent Taiwan-market false positives actually in scope?

### Takeaway

The Taiwan-store search also returned catalog duplicates and non-Taiwan creators; retailer availability in Taiwan was not treated as proof of creator origin.

### Cited Findings

- Pubu’s current photo-book shelves surfaced *劉淇首本個人寫真書 濕樂園 越濕越愛*. MuseBooks already records both its with-video and ebook-only Pubu digital editions under one work, so it is a duplicate. [Pubu product](https://www.pubu.com.tw/magazine/686437); [MuseBooks API creator query](https://musebooks.my/v1/books?q=%E5%8A%89%E6%B7%87)
- Taiwan retailer listings label *TAKA：深夜名堂男子寫真* as a Japanese-popular TAKA title and list a Taiwan-market ebook special edition; this is a market match, not evidence of a Taiwan-origin influencer. MuseBooks already exposes the underlying photobook work. [Kingstone listing](https://www.kingstone.com.tw/basic/2019910061054); [Taiwan Kadokawa ebook catalog](https://reading.udn.com/ebook/store/store_cate.do?cid=114); [MuseBooks work](https://musebooks.my/books/work-tw-32d4b8a05027619bf9fb19ff)

### Inferences

- **DUPLICATE** *濕樂園*; **EXCLUDE** TAKA from the Taiwan-origin queue. These findings do not produce an import candidate. [MuseBooks API creator query](https://musebooks.my/v1/books?q=%E5%8A%89%E6%B7%87); [TAKA listing](https://www.kingstone.com.tw/basic/2019910061054)

### Gaps

- No direct Taiwan-origin ebook with a verified item-level seller record and title-matched cover emerged from this pass; revisit when a seller or publisher exposes stronger evidence for the held items. [Pubu catalog](https://m.pubu.com.tw/magazine-category/photo-books-444); [Books.com publisher catalog](https://www.books.com.tw/web/sys_puballb/books/?pubid=18photostudio)

### Focused follow-up — 關關 / G-JAN identity and origin

- Rechecked Pubu product `604421`: the seller responds HTTP 200 and lists *關關寫真集2-Vol.02*, PDF, 73 pages, released 2025-09-11, NT$699 DRM / NT$1,399 DRM-free. [Pubu product](https://www.pubu.com.tw/ebook/604421)
- Its linked cover also returns HTTP 200 (`image/jpeg`, 158,463 bytes; SHA-256 `1fb65cb6ac2dabadf9a5640ca4f6b886136670a76dc2c1c525b277abe8e74f5a`) and visibly reads “G-JAN 關關 II / Fitness Prince,” consistent with the Pubu product title. [Pubu cover](https://res1.pubu.tw/docs/512992/13071/QXSQbl_l.jpg)
- Targeted searches for “G-JAN 關關,” “Fitness Prince,” and “網紅教練關關” did not surface a reliable creator or primary profile tying this subject to Taiwan. The product page uses only the alias 關關 and photographer/seller adonisjing, so the item evidence does not establish the required creator origin. [Pubu product](https://www.pubu.com.tw/ebook/604421)
- Live MuseBooks exact queries for `604421`, `關關寫真集2-Vol.02`, and `關關` each returned zero matches. [API item-ID query](https://musebooks.my/v1/books?q=604421); [API title query](https://musebooks.my/v1/books?q=%E9%97%9C%E9%97%9C%E5%AF%AB%E7%9C%9F%E9%9B%862-Vol.02); [API subject query](https://musebooks.my/v1/books?q=%E9%97%9C%E9%97%9C)

**Decision: HOLD.** Product and cover are verified, but creator identity and Taiwan origin are unresolved; do not add to R2 or DB on the current evidence. [Pubu product](https://www.pubu.com.tw/ebook/604421)
