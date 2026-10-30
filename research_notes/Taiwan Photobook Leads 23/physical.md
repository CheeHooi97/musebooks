# Physical Taiwan Creator Photobook Search

## Which fresh physical-book leads had a live MuseBooks match?

### Takeaway

No new title cleared the import gate. The clearest title newly surfaced in this round was Huang Brothers’ 《有你的旅程：黃氏兄弟寫真紀實》; a live API search returns its existing work and a second existing Huang Brothers title, 《有你的夏天：黃氏兄弟寫真書II》. Other recent retail discoveries—周感恩, 安生 Anshi, 寶兒, and 妮可 Nicole—also match existing MuseBooks works. These are duplicate checks, not candidates for another database or R2 write.

### Cited Findings
- CAPSULE Taiwan identifies Huang Brothers as its managed YouTube creators and reports that 《有你的旅程》 was formally released in physical standard and special editions, followed by signings in Taipei, Taichung, Tainan, and Kaohsiung. [CAPSULE release and book-tour report](https://www.capsuleinc.cc/creators-news-inner/621?language=ZH)
- CAPSULE Taiwan’s official statement links the brothers’ Facebook, YouTube, Instagram, and TikTok accounts; its company name is explicitly CAPSULE Taiwan. [CAPSULE Taiwan identity statement](https://www.capsuleinc.cc/creators-news-inner/569)
- The direct TCSB ISBN listing identifies 《有你的旅程》 as ISBN 9789577434555. A separate retailer record describes the released product as a 144-page Traditional Chinese photobook by Taiwan Kadokawa, but marks it discontinued. [TCSB product listing](https://www.tcsb.com.tw/9789577434555); [YesAsia bibliographic listing](https://www.yesasia.com/global/%E6%9C%89%E4%BD%A0%E7%9A%84%E6%97%85%E7%A8%8B-%E9%BB%84%E6%B0%8F%E5%85%84%E5%BC%9F%E5%86%99%E7%9C%9F%E7%BA%AA%E5%AE%9E/1078986591-0-0-0-zh_CN/info.html)
- Sanmin’s direct listing and the Taiwan Kadokawa product page identify 《有你的夏天：黃氏兄弟寫真書II》 as a book; Sanmin lists ISBN 9789865249793. [Sanmin product](https://www.sanmin.com.tw/product/index/009797406); [Taiwan Kadokawa product page](https://www.kadokawa.com.tw/products/9789865249793)
- A live MuseBooks API search for 黃氏兄弟 returned two works: 《有你的旅程：黃氏兄弟寫真紀實》 (work-tw-a682a99d8303d3a9328b15ff) and 《有你的夏天：黃氏兄弟寫真書II》 (work-tw-6255401cda979711c736496a). [MuseBooks API results](https://musebooks.my/v1/books?q=%E9%BB%83%E6%B0%8F%E5%85%84%E5%BC%9F&pageSize=50); [first work](https://musebooks.my/books/work-tw-a682a99d8303d3a9328b15ff); [second work](https://musebooks.my/books/work-tw-6255401cda979711c736496a)
- Kingstone’s direct product page gives 安生 Anshi’s physical title, ISBN 9786269687794, 112 pages, publisher, and Taiwan as publication place. An official-looking creator Linktree links to the same book campaign. The API returns existing work work-tw-53f4134579704b7535fb87aa. [Kingstone product](https://www.kingstone.com.tw/basic/2019960402098/); [Anshi creator links](https://linktr.ee/anshi81314); [MuseBooks API results](https://musebooks.my/v1/books?q=%E5%AE%89%E7%94%9F&pageSize=50)
- TAAZE’s direct listing describes 寶兒’s 《Babe Fantasy‧寶兒寫真書》 as a 2025 physical book and gives ISBN 9786267683798. The live API returns the existing work work-tw-6bfdeef40b49b66040c85d2e with two editions. [TAAZE physical product](https://ebook.taaze.tw/do/mobile/single.aspx?pid=11101079087); [MuseBooks API results](https://musebooks.my/v1/books?q=Babe%20Fantasy&pageSize=50)
- Sanmin lists 妮可 Nicole’s 《想見妮》 physical edition, ISBN 9786267683088; the live API returns existing work work-tw-e23888df7c68a3c7d3bc18ea, with physical and digital editions. The sources reviewed here do not establish Nicole’s Taiwan origin. [Sanmin physical product](https://www.sanmin.com.tw/product/index/014272084); [MuseBooks API results](https://musebooks.my/v1/books?q=%E6%83%B3%E8%A6%8B%E5%A6%AE&pageSize=50)

### Inferences
- **DUPLICATE — Huang Brothers, 周感恩, 安生, 寶兒, Nicole.** Exact-title/creator API results already contain these works, so creating another work or re-uploading a cover would duplicate existing records. [Huang Brothers API results](https://musebooks.my/v1/books?q=%E9%BB%83%E6%B0%8F%E5%85%84%E5%BC%9F&pageSize=50); [安生 API results](https://musebooks.my/v1/books?q=%E5%AE%89%E7%94%9F&pageSize=50); [寶兒 API results](https://musebooks.my/v1/books?q=Babe%20Fantasy&pageSize=50); [Nicole API results](https://musebooks.my/v1/books?q=%E6%83%B3%E8%A6%8B%E5%A6%AE&pageSize=50)
- **HOLD — 《有你的旅程》 current stock and cover recheck.** Historical fulfillment is supported by the release announcement and signing tour, but the separate retailer now says discontinued, and I did not find an independently retrievable final cover image to hash against the existing MuseBooks cover. [CAPSULE report](https://www.capsuleinc.cc/creators-news-inner/621?language=ZH); [YesAsia listing](https://www.yesasia.com/global/%E6%9C%89%E4%BD%A0%E7%9A%84%E6%97%85%E7%A8%8B-%E9%BB%84%E6%B0%8F%E5%85%84%E5%BC%9F%E5%86%99%E7%9C%9F%E7%BA%AA%E5%AE%9E/1078986591-0-0-0-zh_CN/info.html)
- **HOLD — Nicole’s Taiwan-origin scope.** The physical and digital book exists and is already catalogued, but the reviewed first-party product/event trail did not establish that the featured creator is Taiwan-origin. [Sanmin product](https://www.sanmin.com.tw/product/index/014272084); [Nicole book-event listing](https://www.accupass.com/event/2505220702594263259590)

### Gaps
- The exact source cover for Huang Brothers’ first book was not independently retrieved and compared against the existing MuseBooks/R2 image; current physical stock was not confirmed. This does not affect the duplicate decision because the live API already has the work. [MuseBooks work](https://musebooks.my/books/work-tw-a682a99d8303d3a9328b15ff); [YesAsia listing](https://www.yesasia.com/global/%E6%9C%89%E4%BD%A0%E7%9A%84%E6%97%85%E7%A8%8B-%E9%BB%84%E6%B0%8F%E5%85%84%E5%BC%9F%E5%86%99%E7%9C%9F%E7%BA%AA%E5%AE%9E/1078986591-0-0-0-zh_CN/info.html)
- Nicole needs a reliable first-party Taiwan-origin source before she can be counted as an in-scope Taiwan creator; a Taiwan seller or publisher alone is not origin evidence. [Sanmin product](https://www.sanmin.com.tw/product/index/014272084)

## Did any candidate meet the Taiwan-creator, finished-edition, cover, and catalog checks?

### Takeaway

No. Huang Brothers have strong creator and Taiwan-source evidence, and the products were released, but one is already in MuseBooks and current stock plus independent final-cover comparison remain unverified. The other candidate listings either resolve to already catalogued works or still have an origin/scope gap.

### Cited Findings
- CAPSULE Taiwan describes Huang Brothers as YouTube creators, identifies them as its managed creators, and documents release of the first photobook and its Taiwan signing tour. [Book release report](https://www.capsuleinc.cc/creators-news-inner/621?language=ZH); [official company statement](https://www.capsuleinc.cc/creators-news-inner/569); [CAPSULE Taiwan creator profile](https://www.capsuleinc.cc/creators-news-inner/702)
- TAAZE lists 周感恩’s physical photobook with ISBN and an observed stock count, while MuseBooks returns existing work work-tw-aa6e6382632cf200d0a3d05c; the accessible seller observation is not treated as a new import. [TAAZE product](https://m.taaze.tw/do/mobile/single.aspx?org_flg=1&pid=11101064760&prod_cat_id=11); [MuseBooks API results](https://musebooks.my/v1/books?q=%E5%91%A8%E6%84%9F%E6%81%A9&pageSize=50)
- Kingstone has an identifiable Anshi physical edition and the creator’s link hub points to its campaign, but the live catalog already returns its ISBN-matched work. [Kingstone product](https://www.kingstone.com.tw/basic/2019960402098/); [Anshi creator links](https://linktr.ee/anshi81314); [MuseBooks API results](https://musebooks.my/v1/books?q=%E5%AE%89%E7%94%9F&pageSize=50)
- The candidate “Babe Fantasy” is in the local Taiwan catalog and the live API as a physical-and-digital work; the direct retailer confirms the physical product, so this is a duplicate rather than a missing edition. [Local catalog](../../scraper/taiwan-photobook-catalog.md); [TAAZE product](https://ebook.taaze.tw/do/mobile/single.aspx?pid=11101079087); [MuseBooks API results](https://musebooks.my/v1/books?q=Babe%20Fantasy&pageSize=50)
- Live API searches for 周感恩, 安生, 寶兒, 黃氏兄弟, and Nicole all return matching existing works; no unrecorded title was identified among these leads. [周感恩](https://musebooks.my/v1/books?q=%E5%91%A8%E6%84%9F%E6%81%A9&pageSize=50); [安生](https://musebooks.my/v1/books?q=%E5%AE%89%E7%94%9F&pageSize=50); [寶兒](https://musebooks.my/v1/books?q=Babe%20Fantasy&pageSize=50); [黃氏兄弟](https://musebooks.my/v1/books?q=%E9%BB%83%E6%B0%8F%E5%85%84%E5%BC%9F&pageSize=50); [Nicole](https://musebooks.my/v1/books?q=%E6%83%B3%E8%A6%8B%E5%A6%AE&pageSize=50)

### Inferences
- The round’s decision is **no import**. A live API duplicate is enough to stop a second DB/R2 write even when a retailer page is newly found.
- Keep Huang Brothers’ first title on a source-cover/current-stock recheck list only if the existing image itself needs review; it is not an uncatalogued title.

### Gaps
- No uncatalogued physical Taiwan influencer photobook with an independently verified final cover was found in this focused retailer/publisher sweep.
- No catalog, database, or R2 write was made in this research task.

## What import decision and changes resulted?

### Takeaway

No work from this physical sweep was imported. The API already returns matches for each candidate identified here, so no catalog, R2, or database mutation was warranted.

### Cited Findings
- The live creator-name query returns the two Huang Brothers works with existing work IDs, while exact creator/title queries return one existing record each for 周感恩, 安生, and Nicole, and Babe Fantasy returns one work with two editions. [Huang Brothers API](https://musebooks.my/v1/books?q=%E9%BB%83%E6%B0%8F%E5%85%84%E5%BC%9F&pageSize=50); [周感恩 API](https://musebooks.my/v1/books?q=%E5%91%A8%E6%84%9F%E6%81%A9&pageSize=50); [安生 API](https://musebooks.my/v1/books?q=%E5%AE%89%E7%94%9F&pageSize=50); [寶兒 API](https://musebooks.my/v1/books?q=Babe%20Fantasy&pageSize=50); [Nicole API](https://musebooks.my/v1/books?q=%E6%83%B3%E8%A6%8B%E5%A6%AE&pageSize=50)

### Inferences
- Existing API results make all confirmed titles duplicates for this task. The round produced no candidate for import and no database or R2 writes.

### Gaps
- If the existing Huang Brothers cover record is ever reviewed, retrieve an independently accessible final-cover source and compare it to the live cover asset; this is a data-quality follow-up, not a missing-title import. [Huang Brothers MuseBooks work](https://musebooks.my/books/work-tw-a682a99d8303d3a9328b15ff); [CAPSULE release report](https://www.capsuleinc.cc/creators-news-inner/621?language=ZH)
