# Digital Taiwan creator photobook sweep — Round 21

## Can the Round 20 關關 / G-JAN lead be tied to an identifiable Taiwan creator?

### Takeaway

**HOLD.** The direct Pubu listing and title-matched cover remain verifiable, but no primary source located in this pass links the model alias 關關 / G-JAN to a full identity or Taiwan origin. Do not import or upload this item on the current evidence.

### Cited Findings

- Pubu lists *關關寫真集2-Vol.02* as a Traditional Chinese PDF, 73 pages, product ID `604421`, released 2025-09-11, with NT$699 DRM and NT$1,399 DRM-free options; the description calls the subject an influencer/coach 關關 and says it is a second photobook made with photographer 劉京, but supplies no full model name or origin. [Pubu product](https://www.pubu.com.tw/ebook/604421)
- The product’s cover URL is [Pubu cover](https://res1.pubu.tw/docs/512992/13071/QXSQbl_l.jpg); the Round 20 download measured 158,463 bytes with SHA-256 `1fb65cb6ac2dabadf9a5640ca4f6b886136670a76dc2c1c525b277abe8e74f5a`. Its visible “G-JAN 關關 II / Fitness Prince” wording matches the product alias but does not identify a Taiwan-origin model. [Pubu product](https://www.pubu.com.tw/ebook/604421)
- The current live MuseBooks API returned 0 results for `604421`, the exact title, and `關關`; this absence does not close the missing identity/origin evidence. [ID query](https://musebooks.my/v1/books?q=604421), [title query](https://musebooks.my/v1/books?q=%E9%97%9C%E9%97%9C%E5%AF%AB%E7%9C%9F%E9%9B%862-Vol.02), [subject query](https://musebooks.my/v1/books?q=%E9%97%9C%E9%97%9C)
- Searches surfaced other people using 關關, including Taiwanese media creator 關韶文 and a separate Guangdong-born social-media creator, but no source connects either person to the Pubu model or the G-JAN cover. [A Day Magazine interview](https://www.adaymag.com/2021/03/07/a-day-paper-self-employed-interview-with-ethan-kuan-kuan.html), [EBC report](https://news.ebc.net.tw/news/politics/533288)

### Inferences

- **HOLD**, not duplicate: catalog searches are negative, but neither the named subject nor Taiwan-origin criterion is established. [Pubu product](https://www.pubu.com.tw/ebook/604421)

### Gaps

- A primary creator profile or reliable Taiwan press source identifying the model behind 關關 / G-JAN is still missing. The seller page’s use of a generic alias is insufficient to select among namesakes. [Pubu product](https://www.pubu.com.tw/ebook/604421)

## Did the fresh digital sweep find an uncatalogued Taiwan creator photobook?

### Takeaway

No **GO** emerged. Fresh direct listings for 夏蕾, 瑟七, 林真亦, and the Rakuten Girls group all resolve to existing MuseBooks works and digital editions. The first three have downloadable cover images whose hashes were checked during this pass.

### Cited Findings

- Pubu’s direct page lists 夏蕾’s *心動蕾達：夏蕾寫真* as an EPUB released 2026-09-18, product ID `696714`, ISBN `9786264446433`, 147 pages; the product description identifies her as a Taiwan-based new-generation cheerleader and Passion Sisters member. Its downloaded cover ([Pubu cover](https://res4.pubu.tw/docs/595327/40141/wHEwKs_l.jpg)) returned HTTP 200, 300,944 bytes, SHA-256 `165153e02e7796419e645dd4810829d4b0c20eee3c927d214a15a1fdada25fd2`. The live API title/subject query returns the existing work `work-tw-44b0143f8e9afb4d9fff0e09`, already containing digital edition `edition-cf999a4774a1d09f39dbfd70` (the same ISBN, 147 pages) and the physical edition. **DUPLICATE.** [Pubu product](https://www.pubu.com.tw/ebook/696714), [team profile](https://www.cpblgirls.tw/front/4/passionsistersm/member.php?ID=Y3BibGdpcmxzJnBhc3Npb25zaXN0ZXJzbQ%3D%3D&PID=116), [MuseBooks title query](https://musebooks.my/v1/books?q=%E5%BF%83%E5%8B%95%E8%95%BE%E9%81%94&pageSize=50), [MuseBooks subject query](https://musebooks.my/v1/books?q=%E5%A4%8F%E8%95%BE&pageSize=50)
- Pubu lists 瑟七’s *《微澀．微瑟》瑟七 Seul7 數位寫真（含影音）* as a 294-page fixed-layout EPUB released 2026-08-30, product ID `690306`, ISBN `9786264555029`. The product identifies her as 林沂玟, a Tainan-born Uni-Girls / CPBL cheerleader. The downloaded [Pubu cover](https://res4.pubu.tw/docs/589787/8033/qAzbR8_l.jpg) returned HTTP 200, 292,845 bytes, SHA-256 `086f70fcd70389a0501086b5bb54642964fdcb096975000e9382d2dfce681cf8`. The live MuseBooks `瑟七` query finds existing Taiwan work `work-tw-df1e291d2b2f39f368a77cc1`, including digital edition `edition-0b730768da4b9e6b0bef9b82` with that ISBN and active Pubu, Readmoo, and BookWalker listings, alongside the physical edition. **DUPLICATE.** [Pubu product](https://www.pubu.com.tw/ebook/690306), [Uni-Girls member profile](https://www.cpblgirls.tw/front/4/Unigirlsintro/member.php?ID=Y3BibGdpcmxzJlVuaWdpcmxzaW50cm8%3D&PID=49), [MuseBooks subject query](https://musebooks.my/v1/books?q=%E7%91%9F%E4%B8%83&pageSize=50)
- Readmoo’s direct seller page lists *亦如初見：YUNA林真亦寫真〖數位典藏豪華增量版〗* as fixed-layout EPUB, dated online 2025-10-27, EISBN `9786264197281`; the creator’s own channel promoted the title and its Taiwan retailer preorder. Its downloaded [Readmoo cover](https://pgw.udn.com.tw/gw/photo.php?u=/readmoocom/cover/jd/nkbfrpj.jpg) returned HTTP 200, 185,939 bytes, SHA-256 `3236ff20dd266ac51e411d0b365ccd19b917bdad432b5a0c21b497b455074477`. MuseBooks title query finds `work-tw-4950e1fde40ebfa591030990` with the corresponding digital edition and physical ISBN `9786264197328`. **DUPLICATE.** [Readmoo product](https://reading.udn.com/ebook/store/store_product.do?pid=73371), [creator’s channel announcement](https://www.youtube.com/watch?v=ny3BJo_XoSI), [MuseBooks title query](https://musebooks.my/v1/books?q=%E4%BA%A6%E5%A6%82%E5%88%9D%E8%A6%8B&pageSize=50)
- Kobo Taiwan’s direct listing for the four-member *Rakuten Girls Yanmaga* edition gives publication date 2026-08-31, product ID `8982431001000`, EPUB 3 with Adobe DRM, 179 MB, and the four featured members; it does not state page count or a separate ISBN on the product page. The linked Kobo cover ([cover image](https://cdn.kobo.com/book-images/8874ded3-cf05-4486-a3fd-1035c4ab0103/353/569/90/False/kobo-rakuten-girls-2.jpg)) returned HTTP 200, 140,072 bytes, SHA-256 `ba5e95a270b17203e9dd452c0178d5d67c18f1efdc879214f18726f60ae9bf74`. The official Yanmaga Taiwan campaign confirms the Taiwan-edition contents and group members; the MuseBooks title/subject API query finds existing work `work-tw-76b3b9559d5cbb77566e2795`, digital edition `edition-99a8b5430bbd6b8fc29e61c4`, and the same Kobo identifier. **DUPLICATE.** [Kobo product](https://www.kobo.com/tw/zh/ebook/kobo-rakuten-girls-2), [official Yanmaga Taiwan campaign](https://ymclub.kodansha.co.jp/pages/yanmaga-cup-tw), [MuseBooks group-title query](https://musebooks.my/v1/books?q=%E6%A8%82%E5%A4%A9%E5%A5%B3%E5%AD%A9%20Yanmaga&pageSize=50), [MuseBooks subject query](https://musebooks.my/v1/books?q=%E7%AC%91%E7%AC%91&pageSize=50)
- Other shelf/search hits were excluded before import review where the seller or campaign did not name a Taiwan-origin individual model. For example, Pubu’s *MESOfotoBOOK-08* is a 176-page PDF photo/video title by MESOfoto, but its description does not identify a featured person. [Pubu product](https://www.pubu.com.tw/magazine/687967)

### Inferences

- **DUPLICATE** 夏蕾, 瑟七, 林真亦, and the Rakuten Girls team edition; none requires a new DB or R2 record based on this sweep. Existing edition records are stronger duplicate evidence than zero results from identifier-only queries because the catalog search indexes title and featured-name fields. [MuseBooks 夏蕾 query](https://musebooks.my/v1/books?q=%E5%BF%83%E5%8B%95%E8%95%BE%E9%81%94&pageSize=50), [MuseBooks 瑟七 query](https://musebooks.my/v1/books?q=%E7%91%9F%E4%B8%83&pageSize=50), [MuseBooks YUNA query](https://musebooks.my/v1/books?q=%E4%BA%A6%E5%A6%82%E5%88%9D%E8%A6%8B&pageSize=50), [MuseBooks Rakuten Girls query](https://musebooks.my/v1/books?q=%E6%A8%82%E5%A4%A9%E5%A5%B3%E5%AD%A9%20Yanmaga&pageSize=50)
- **No new GO** from the digital pass. The currently verified digital publications are either already cataloged or do not identify a Taiwan-origin influencer. [Pubu Summer Lei product](https://www.pubu.com.tw/ebook/696714), [Pubu Seul7 product](https://www.pubu.com.tw/ebook/690306), [Kobo Rakuten Girls product](https://www.kobo.com/tw/zh/ebook/kobo-rakuten-girls-2), [Pubu MESOfoto product](https://www.pubu.com.tw/magazine/687967)

### Gaps

- The current Pubu page for 夏蕾 supplies product ID, EPUB format, date, ISBN, page count, Taiwan cheerleader description, and a downloadable cover; all are already represented in the MuseBooks record. [Pubu product](https://www.pubu.com.tw/ebook/696714), [MuseBooks result](https://musebooks.my/v1/books?q=%E5%BF%83%E5%8B%95%E8%95%BE%E9%81%94&pageSize=50)
- The current Kobo group page does not provide page count and does not label its product ID as an ISBN; the duplicate relationship is established by the exact existing title and edition record instead. [Kobo product](https://www.kobo.com/tw/zh/ebook/kobo-rakuten-girls-2), [MuseBooks result](https://musebooks.my/v1/books?q=%E6%A8%82%E5%A4%A9%E5%A5%B3%E5%AD%A9%20Yanmaga&pageSize=50)

## Does 笑笑’s standalone Yanmaga mini now have a direct retailer record or matching cover?

### Takeaway

**HOLD.** This pass still found no direct Kobo page for the individual mini and no cover that can be matched to it. The newly found direct Kobo page is for the separate four-member August group edition, which is already cataloged.

### Cited Findings

- FindBook lists the standalone *Rakuten Girls 迷你寫真集 笑笑 Yanmaga Cup Yanmaga 數位寫真集*, ID `8982002000020`, dated 2026-04-24, with a Kobo ebook offer but no stated currency; it remains an aggregator entry rather than the direct retailer product page. [FindBook item](https://findbook.com.tw/8982002000020)
- Kodansha’s official campaign/product material names 笑笑 among the Yanmaga Cup members, but the product image previously inspected for the general mini collection visibly names 高橋佳帆, not 笑笑. The official page does not map FindBook’s item ID to an individual mini cover. [Kodansha product page](https://www.kodansha.co.jp/book/products/0000429233), [official cover image](https://dvs-cover.kodansha.co.jp/0000429233/3Imo3PF8TywvuwAePzoHfNqRAX4sBjo7iilxvymT.jpg), [official Yanmaga Taiwan campaign](https://ymclub.kodansha.co.jp/pages/yanmaga-cup-tw)
- Targeted search queries for the title, Kobo item ID, and Japanese member name surfaced FindBook and the group campaign but no individual Kobo retail page. The group Kobo listing opened in this round is a different product: the four-person Taiwan edition released 2026-08-31. [FindBook item](https://findbook.com.tw/8982002000020), [direct group Kobo page](https://www.kobo.com/tw/zh/ebook/kobo-rakuten-girls-2)
- MuseBooks’ live `笑笑` query returns the already cataloged four-member group work, not the April standalone mini; the group record remains a distinct product. [MuseBooks `笑笑` query](https://musebooks.my/v1/books?q=%E7%AC%91%E7%AC%91&pageSize=50), [group Kobo page](https://www.kobo.com/tw/zh/ebook/kobo-rakuten-girls-2)

### Inferences

- **HOLD**, not duplicate and not GO: the group item must not be substituted for the missing standalone retailer record or cover. [FindBook item](https://findbook.com.tw/8982002000020), [Kodansha image](https://dvs-cover.kodansha.co.jp/0000429233/3Imo3PF8TywvuwAePzoHfNqRAX4sBjo7iilxvymT.jpg)

### Gaps

- Still missing the individual Kobo URL, product metadata needed to match the ISBN/product identifier, its own downloadable cover, and page-count data if the retailer exposes one. Until then there is no import-ready standalone record. [FindBook item](https://findbook.com.tw/8982002000020), [Kodansha product page](https://www.kodansha.co.jp/book/products/0000429233)
