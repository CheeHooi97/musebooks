# Digital Taiwan creator photobook sweep — Round 22

## Did this round find a new import-ready Taiwan influencer ebook?

### Takeaway

No **GO** emerged. Three fresh direct ebook listings have a product and live catalog checks, but the new subjects do not yet have enough reliable identity/origin evidence to qualify as Taiwan influencers. I made no catalog, database, or R2 changes.

### Cited Findings

- Readmoo lists *FEVER：人態好攝影集5（數位特別版）* as a fixed-layout EPUB released 2026-10-30, with ISBN 9786264683760 and EISBN 9786264685108, available for NT$490. The listing identifies two featured male models only as Chris and Ice; it gives Chris’s Instagram handle as chris.qingyu, and describes the series publisher/photography account as a male-portrait social-media outlet. It does not state either model’s Taiwan origin. [Readmoo direct product](https://reading.udn.com/ebook/store/store_product.do?pid=176271&source=%E5%AF%AB%E7%9C%9F%E9%9B%86)
- Live MuseBooks API searches returned total 0 for FEVER, 人態好攝影集5, EISBN 9786264685108, chris.qingyu, 曾擎宇, and Ice 人態好; there is no matching catalog work under those queries at the time checked. [FEVER query](https://musebooks.my/v1/books?q=FEVER), [title query](https://musebooks.my/v1/books?q=%E4%BA%BA%E6%85%8B%E5%A5%BD%E6%94%9D%E5%BD%B1%E9%9B%865), [EISBN query](https://musebooks.my/v1/books?q=9786264685108), [Chris query](https://musebooks.my/v1/books?q=chris.qingyu), [Chinese-name query](https://musebooks.my/v1/books?q=%E6%9B%BE%E6%93%8E%E5%AE%87)
- Pubu directly offers *RAW第一集* as a 120-page Traditional Chinese PDF, product ID 704517, released 2026-10-23. Its description calls the featured subject Vivian and credits photographer JONIMAGE, but does not give Vivian’s full identity or Taiwan origin. [Pubu direct product](https://www.pubu.com.tw/magazine/704517)
- Live MuseBooks API searches returned total 0 for RAW第一集, Vivian JONIMAGE, and JONIMAGE. [Title query](https://musebooks.my/v1/books?q=RAW%E7%AC%AC%E4%B8%80%E9%9B%86), [subject/photographer query](https://musebooks.my/v1/books?q=Vivian%20JONIMAGE), [photographer query](https://musebooks.my/v1/books?q=JONIMAGE)
- Pubu directly offers *李昊禹個人寫真書昇肌勃勃* as a 126-page PDF, product ID 686431, released 2026-08-06 for NT$499. Its description calls him a fitness coach and former runway/ad model, but does not establish his Taiwan origin or connect him to a named social profile. The product page gives no ISBN. [Pubu direct product](https://www.pubu.com.tw/magazine/686431)
- MuseBooks API returned total 0 for 李昊禹. A Linktree search hit describes a Taichung fitness coach using the similar handle liho0420, but no source links that account to the Pubu model, so it cannot establish this book subject’s origin. [MuseBooks query](https://musebooks.my/v1/books?q=%E6%9D%8E%E6%98%8A%E7%A6%B9), [possible but unlinked creator profile](https://linktr.ee/liho0420)

### Inferences

- **HOLD — FEVER:** the ebook is genuinely published and directly available, but the listing does not establish the featured models’ Taiwan origin; its author credit is the photography collective, not a named Taiwan influencer. A zero-result catalog search alone is not enough to import it. [Readmoo product](https://reading.udn.com/ebook/store/store_product.do?pid=176271&source=%E5%AF%AB%E7%9C%9F%E9%9B%86), [MuseBooks title query](https://musebooks.my/v1/books?q=FEVER)
- **HOLD — RAW第一集:** Pubu verifies a released digital photo product, but the alias Vivian and photographer credit do not identify a Taiwan-origin influencer. [Pubu product](https://www.pubu.com.tw/magazine/704517)
- **HOLD — 李昊禹:** a released digital photobook is verified, but the origin/identity match remains unresolved; the similar Taichung profile cannot safely be attributed to this subject. [Pubu product](https://www.pubu.com.tw/magazine/686431), [possible profile](https://linktr.ee/liho0420)

### Gaps

- For *FEVER*, a reliable primary profile linking either Chris or Ice to Taiwan, and clearer subject identity, are missing. The seller page gives only a first name for Ice and a social handle for Chris. [Readmoo product](https://reading.udn.com/ebook/store/store_product.do?pid=176271&source=%E5%AF%AB%E7%9C%9F%E9%9B%86)
- For *RAW第一集*, Vivian’s full name and Taiwan-origin evidence are missing; the product page alone does not connect the alias to a creator profile. [Pubu product](https://www.pubu.com.tw/magazine/704517)
- For 李昊禹, a primary source tying the exact model in the book to a Taiwan-origin public creator profile is missing. The similar handle is not enough to resolve identity. [Pubu product](https://www.pubu.com.tw/magazine/686431), [Linktree profile](https://linktr.ee/liho0420)

## Which recent direct ebook listings were already in MuseBooks?

### Takeaway

Several newly surfaced direct product pages are duplicates, including current digital editions for 彭彭, 劉芷伊, and the TOKKI CUTIE team. Do not add another work or digital edition for these products.

### Cited Findings

- Books.com.tw lists 彭彭’s *彭然心動：彭彭寫真〖電子書祕藏版〗* as an ebook dated 2026-09-11. MuseBooks already has Taiwan-origin work `work-tw-48cee531f79d279264813cd3`, physical edition `edition-c2d2d74dc924b86b6baecd61`, and digital edition `edition-df94fe03d2280d96d59dc422` with EISBN 9786264448314. **DUPLICATE.** [Books.com.tw ebook](https://www.books.com.tw/products/E050359832), [MuseBooks API title query](https://musebooks.my/v1/books?q=%E5%BD%AD%E7%84%B6%E5%BF%83%E5%8B%95&pageSize=50), [MuseBooks creator query](https://musebooks.my/v1/books?q=%E5%BD%AD%E5%BD%AD&pageSize=50)
- Kingstone lists the ebook *FIRST JUMP* for the TOKKI CUTIE Taipei East Power cheer team; the official club profile describes it as the team’s photo story book and names the team roster. MuseBooks already returns the digital edition as work `work-tw-ed159843adbd6278211767e4`, edition `edition-8849001daa8ba7233f189920`, ISBN 9786260160128, released 2026-04-30. It also returns a similarly titled physical work `work-tw-27180567259fb6d43aed9de4` with edition `edition-b4dd69f8f6bd38f895ec4a56`; avoid adding a second digital copy. **DUPLICATE.** [Kingstone ebook](https://www.kingstone.com.tw/basic/2800000241943/), [official TAIPEI EAST POWER profile](https://eastpower.tw/en/6177), [MuseBooks live query](https://musebooks.my/v1/books?q=FIRST%20JUMP&pageSize=50)
- Books.com.tw lists the ebook *芷想靠近你：劉芷伊醫師寫真* with a 2026-10-09 digital release. MuseBooks already returns Taiwan work `work-tw-0fe3296d84c633e5ab200c65`, digital edition `edition-58e8bdd2d57ed353039d3a87` (ISBN 9786264444965), and physical edition `edition-423fb16ca0efa625e72af8f5` (ISBN 9786264444811). **DUPLICATE.** [Books.com.tw ebook](https://www.books.com.tw/products/E050360504), [MuseBooks API title query](https://musebooks.my/v1/books?q=%E8%8A%B7%E6%83%B3%E9%9D%A0%E8%BF%91%E4%BD%A0), [MuseBooks creator query](https://musebooks.my/v1/books?q=%E5%8A%89%E8%8A%B7%E4%BC%8A)
- Round 21 had already verified 夏蕾’s *心動蕾達*, 瑟七’s *微澀．微瑟*, 林真亦’s *亦如初見*, and the four-member Rakuten Girls Yanmaga ebook as existing catalog editions. They remain excluded from this fresh-candidate pass. [Round 21 digital notes](../Taiwan%20Photobook%20Leads%2021/digital.md)

### Inferences

- The exact seller EISBNs and live work/edition IDs show that the 彭彭 and 劉芷伊 digital listings are already represented; no R2 cover or DB write is warranted. [彭彭 API result](https://musebooks.my/v1/books?q=%E5%BD%AD%E7%84%B6%E5%BF%83%E5%8B%95&pageSize=50), [劉芷伊 API result](https://musebooks.my/v1/books?q=%E8%8A%B7%E6%83%B3%E9%9D%A0%E8%BF%91%E4%BD%A0)
- The TOKKI CUTIE team already has a digital record and a separate similarly titled physical record in the API. The current catalog structure should be reviewed separately if the team’s digital and physical formats need to share one work; this is not a missing ebook import. [MuseBooks live query](https://musebooks.my/v1/books?q=FIRST%20JUMP&pageSize=50)

### Gaps

- The API’s separate TOKKI CUTIE physical and digital work IDs appear to split one title by format. This sweep did not change that catalog structure. [MuseBooks live query](https://musebooks.my/v1/books?q=FIRST%20JUMP&pageSize=50)

## Which discovered titles remain outside the Taiwan influencer scope?

### Takeaway

The Readmoo result for *TAKA：深夜名堂男子寫真（數位特別版）* is a current direct ebook, but its product copy describes TAKA as a Japanese internet personality and says the book was photographed in Taiwan. Location of a shoot does not establish Taiwan origin, so it is excluded from this Taiwan-creator pass.

### Cited Findings

- Readmoo lists TAKA’s fixed-layout EPUB with a 2026-09-24 online release, ISBN 9786264681902 and EISBN 9786264683340. The copy calls TAKA a Japanese popular online male personality and says the book was photographed in Taiwan. [Readmoo direct product](https://reading.udn.com/ebook/store/store_product.do?pid=173781&source=%E5%AF%AB%E7%9C%9F%E9%9B%86)

### Inferences

- **EXCLUDE from Taiwan-origin scope:** the seller’s description supports a Taiwan photo location, not a Taiwan-origin featured creator. [Readmoo direct product](https://reading.udn.com/ebook/store/store_product.do?pid=173781&source=%E5%AF%AB%E7%9C%9F%E9%9B%86)

### Gaps

- No evidence located in this pass identifies TAKA as a Taiwan-origin creator; the seller instead calls him Japanese. [Readmoo direct product](https://reading.udn.com/ebook/store/store_product.do?pid=173781&source=%E5%AF%AB%E7%9C%9F%E9%9B%86)
