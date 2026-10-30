# Taiwan Creator Campaign and Storefront Leads — Round 24

## Did a fresh campaign photobook meet the import gate?

### Takeaway

**HOLD — 《吳玳慈．再jian》寫真書.** The creator-led Zeczec campaign names it as 阿布吳玳慈’s first personal fashion photobook, explicitly describes physical and digital versions, and says signed books would begin shipping after May 20, 2023. The campaign itself succeeded, but this check did not find a standalone final cover, a receipt/fulfillment confirmation, or enough primary-source evidence of her Taiwan origin to recommend an R2/DB import. The live MuseBooks API returned zero for the title/creator query.

### Cited Findings

- Zeczec identifies the project proposer as 吳玳慈 and reports that the campaign succeeded on April 30, 2023. Its book reward is titled 《吳玳慈．再jian》寫真書, describes it as her first personal fashion photobook in physical and digital forms, and specifies a planned May 20 onward dispatch for signed copies. The one-book reward was backed 58 times. [Official campaign and reward details](https://www.zeczec.com/projects/aboo-tzaijianfashionshow)
- The campaign says the photo project was shot in Pingtung with 阿布 modeling the redesigned outfits; it describes the book as conveying sustainable fashion and says 10% of sales would be donated. The listing does not give page count, ISBN, dimensions, or a separate digital-file format/delivery specification. [Official campaign](https://www.zeczec.com/projects/aboo-tzaijianfashionshow)
- A Chinese Culture University media profile reports that 吳玳慈 moved from modeling toward acting and drew attention after publishing TikTok/runway clips that went viral on PTT. An Instagram-profile aggregator lists the creator handle `@dianna__914` at 93.6K followers when crawled. These support a plausible social-creator fit, though coverage principally describes her as an actor/model. [University profile](https://joumedia.pccu.edu.tw/article.php?id=298); [profile snapshot](https://imginn.com/dianna__914/)
- The visible campaign reward image is a 600×200 banner labeled as one early-bird photobook reward; it is a promo banner with a portrait, not a standalone image of the printed book cover. [Zeczec reward banner](https://assets.zeczec.com/projects/14534/options/99881_banner.jpg?1679421950=)
- Live MuseBooks API searches for `吳玳慈 再jian` and `再jian` returned zero works. [Creator/title API query](https://musebooks.my/v1/books?q=%E5%90%B3%E7%8E%B3%E6%85%88%20%E5%86%8Djian&pageSize=50); [title API query](https://musebooks.my/v1/books?q=%E5%86%8Djian&pageSize=50)

### Inferences

- Keep **HOLD**, not GO. The campaign strongly establishes that a title-specific photobook reward was offered and had a planned dispatch date, but a shipping promise is not independent evidence that recipients received the finished item. The only image retrieved is a reward banner, not final cover artwork. [Campaign](https://www.zeczec.com/projects/aboo-tzaijianfashionshow); [reward banner](https://assets.zeczec.com/projects/14534/options/99881_banner.jpg?1679421950=)
- The reviewed evidence supports a Taiwan-based public creator profile, but does not establish the creator’s birthplace or nationality through a first-party or authoritative biography. A Taiwan project venue and local university enrollment do not establish Taiwan origin by themselves. [Campaign](https://www.zeczec.com/projects/aboo-tzaijianfashionshow); [university profile](https://joumedia.pccu.edu.tw/article.php?id=298)

### Gaps

- Find a title-matched, standalone final cover or official photo showing the finished 《再jian》 book, and an official fulfillment or creator post confirming delivery.
- Confirm whether a downloadable edition was actually distributed and capture its format/metadata; the campaign labels physical and digital versions but does not specify a file edition in the inspected reward details.
- Verify Taiwan origin from a reliable biography before assigning Taiwan-origin status. [Campaign](https://www.zeczec.com/projects/aboo-tzaijianfashionshow)

## Which other apparent storefront discoveries were duplicates or not separate photobooks?

### Takeaway

蘋蘋澎澎’s 2026 《純·欲姊姊特休中》 and 阿古’s 《Self：A-KU寫真》 are live-catalog duplicates. Adam 林冠宇’s 《Fairy Land 秘密嗑》 campaign describes a travel/memoir book with a photobook-sized section, rather than a clearly separate photobook product, so it remains outside this pass’s import queue.

### Cited Findings

- 蘋蘋澎澎’s official site calls the twins creators from Taiwan, documents their creator platforms, and lists their photobook series. The official store describes 《2026「純·欲姊姊特休中」寫真單書》 as a 128-page book and says shipping was expected to start in mid-June 2026. The live API already returns `work-tw-8ce4dd25e173839b10d88706` for the title. **DUPLICATE.** [Official creator site](https://pinpinponpon.tw/); [official store listing](https://pinpinponpon627.waca.tw/product/detail/2589988); [MuseBooks exact-title query](https://musebooks.my/v1/books?q=%E7%B4%94%C2%B7%E6%AC%B2%E5%A7%8A%E5%A7%8A%E7%89%B9%E4%BC%91%E4%B8%AD&pageSize=50)
- 城邦’s direct listing identifies 阿古’s *Self：A-KU寫真* as a 160-page, full-color, 2021 physical book from 尖端, ISBN 9786263023475. The seller describes him as an internet celebrity and says he began self-media activity in 2019. The live MuseBooks API returns existing work `work-tw-77b41737167ce4ef7be012ea`. **DUPLICATE.** [Direct publisher-retailer listing](https://www.cite.com.tw/book?id=88379); [MuseBooks exact-title query](https://musebooks.my/v1/books?q=Self%EF%BC%9AA-KU%E5%AF%AB%E7%9C%9F&pageSize=50)
- The successful 《Fairy Land 秘密嗑》 campaign describes a 248-page travel/essay book that contains a “photobook-sized” photo section and says the project began shipping in July 2024. The exact-title live API query returned zero, but the evidence reviewed does not show a separately titled/marketed photobook edition. **HOLD / not a distinct photobook import on this evidence.** [Official campaign and shipping update](https://www.zeczec.com/projects/secret_adam); [MuseBooks title query](https://musebooks.my/v1/books?q=Fairy%20Land%20%E7%A7%98%E5%AF%86%E5%97%91&pageSize=50)

### Inferences

- No duplicate should create another work or trigger another cover upload. The official creator site and API independently establish that the 2026 蘋蘋澎澎 book is already cataloged; the publisher page and API do the same for 阿古’s title. [蘋蘋澎澎 API](https://musebooks.my/v1/books?q=%E7%B4%94%C2%B7%E6%AC%B2%E5%A7%8A%E5%A7%8A%E7%89%B9%E4%BC%91%E4%B8%AD&pageSize=50); [阿古 API](https://musebooks.my/v1/books?q=Self%EF%BC%9AA-KU%E5%AF%AB%E7%9C%9F&pageSize=50)
- The Adam campaign has Taiwan creator context and a released physical publication, but its description makes the photographs a section of a broader travel/memoir book. Reconsider only if catalog policy accepts mixed-format books as photobooks or a separate photobook edition is found. [Official campaign](https://www.zeczec.com/projects/secret_adam)

### Gaps

- For 《再jian》, final-cover and delivery evidence remain missing; for 《Fairy Land 秘密嗑》, a distinct photo-book edition remains unverified. [《再jian》 campaign](https://www.zeczec.com/projects/aboo-tzaijianfashionshow); [Adam campaign](https://www.zeczec.com/projects/secret_adam)

## What changed in the catalog, database, or R2 this pass?

### Takeaway

No catalog, database, or R2 changes were made. The fresh campaign lead remains HOLD; the other complete direct-product matches are duplicates or a hybrid book without a separate photobook edition.

### Cited Findings

- The live API returned zero for 《再jian》, an existing work for 蘋蘋澎澎’s 2026 title, an existing work for *Self：A-KU寫真*, and zero for the mixed Adam title. These were read-only API searches; no import manifest or R2 write was created. [《再jian》 API](https://musebooks.my/v1/books?q=%E5%86%8Djian&pageSize=50); [蘋蘋澎澎 API](https://musebooks.my/v1/books?q=%E7%B4%94%C2%B7%E6%AC%B2%E5%A7%8A%E5%A7%8A%E7%89%B9%E4%BC%91%E4%B8%AD&pageSize=50); [阿古 API](https://musebooks.my/v1/books?q=Self%EF%BC%9AA-KU%E5%AF%AB%E7%9C%9F&pageSize=50); [Adam API](https://musebooks.my/v1/books?q=Fairy%20Land%20%E7%A7%98%E5%AF%86%E5%97%91&pageSize=50)

### Inferences

- The useful next action is a targeted final-cover and delivery search for 《再jian》, while avoiding repeat work on the verified duplicates.

### Gaps

- This campaign sweep produced no new import-grade work and no R2/DB verification receipt because no writes were made.

## Focused follow-up — 《吳玳慈．再jian》 (2026-10-30)

**HOLD.** Rechecked the title against the live MuseBooks API: the exact-title query returned `total: 0` (`items: []`). The Zeczec campaign is a real sale signal: it closed successfully at NT$202,200 with 122 backers, and the one-book reward shows 58 backings. It also explicitly calls the book physical and digital. However, the campaign page still only promises shipping after May 20, 2023; no delivery/receipt confirmation or digital-file specification surfaced. The only book-associated image previously inspected is a 600×200 reward banner, not a title-matched final cover; focused exact-title/social searches did not find a standalone final cover.

For origin, Shih Hsin University’s official profile identifies 吳玳慈 as its film/TV program student, actor and Taipei event curator; its program page also records her Taiwan contest win. TVBS independently reports her as a child performer at a Kaohsiung event at age seven. This supports a well-established Taiwan creator career, but the sources do not explicitly state birthplace or nationality, so do not encode either as fact. [Shih Hsin University profile](https://www.shu.edu.tw/Spotlight.aspx?from=06&sID=30178); [Shih Hsin program notice](https://vci.wp.shu.edu.tw/?page_id=280); [TVBS childhood profile](https://news.tvbs.com.tw/life/85405).

**Gate result:** title/creator fit and crowdfunding sale are supported; fulfillment is unconfirmed, Taiwan career is supported (formal birthplace/nationality is not), and final cover is missing. Keep **HOLD** until a standalone final cover is found; the missing cover alone prevents GO. No catalog, DB, or R2 changes were made. [Official Zeczec campaign/reward status](https://www.zeczec.com/projects/aboo-tzaijianfashionshow); [live exact-title MuseBooks API query](https://musebooks.my/v1/books?q=%E5%90%B3%E7%8E%B3%E6%85%88%EF%BC%8E%E5%86%8Djian&pageSize=50)
