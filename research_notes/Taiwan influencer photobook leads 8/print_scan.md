# Taiwan influencer physical photobook scan

## Newly surfaced editions and import decision

### Takeaway
I found no newly published Taiwan influencer photobook with both a non-duplicate catalog record and a usable cover asset for a safe import. Two leads are worth tracking: ADAM 林冠宇’s actively funded upcoming digital book 《FOUR》, and the newly released 《FEVER》 by photographer self-media account 人態好, whose creator/subject fit and cover need more evidence.

### Cited Findings
- Zeczec describes 《FOUR》 as ADAM 林冠宇’s first digital photobook, says his earlier three books were physical, shows an active campaign dated 2026-10-12 to 2026-11-12, and estimates fulfilment in December 2026. Its public description identifies ADAM as a Taiwan actor and lists his Instagram handle. It does not provide ISBN, page count, a final downloadable edition, or a final cover; treat as a preorder lead and defer importing until release/cover confirmation. [Zeczec project](https://www.zeczec.com/projects/ADAM2026)
- Kingstone lists 《FEVER：人態好攝影集5》 by 人態好 NICE PEOPLE PHOTOGRAPHY, Taiwan Kadokawa, published 2026-10-22, ISBN 9786264683760. Its blurb identifies models Chris (Instagram @chris.qingyu; commercial/ad model and engineer) and Ice (advertising model and former paratrooper), but does not establish that the subjects are Taiwan influencers. Kingstone’s page exposes only its age-restricted placeholder as the social image; I did not retrieve or inspect the explicit book cover, so no R2-ready cover source was confirmed. [Kingstone product](https://www.kingstone.com.tw/basic/2019500066780/)
- 人態好 describes itself as a male-portrait photography social-media outlet established in 2019; that supports a Taiwan creator/publisher connection, but not that this new title is an influencer photobook under the catalog’s intended scope. [Kingstone product](https://www.kingstone.com.tw/basic/2019500066780/)
- The live MuseBooks API title query for “FEVER” returned `total=0`; the query for “FOUR ADAM” returned `total=0`. These confirm neither lead is currently present by those query terms. Direct API endpoint: [FEVER query](https://musebooks.my/v1/books?q=FEVER), [FOUR ADAM query](https://musebooks.my/v1/books?q=FOUR%20ADAM).

### Inferences
- 《FOUR》 may qualify once the digital book is delivered, but a crowdfunding pledge page is not evidence of a final file or R2 cover.
- 《FEVER》 is a new print photobook but is borderline for this goal: its named subjects are described as models rather than influencers, and a suitable cover image was not verified. Leave it out of this import pass pending scope/cover evidence.

### Gaps
- 《FOUR》 final release date/file, ISBN or equivalent identifier, page count, and final cover remain unavailable before the stated December fulfilment.
- 《FEVER》 page count and accessible non-placeholder cover asset were not verified; no independent evidence was found that its two subjects are Taiwan internet influencers.

## Recently surfaced titles that are already represented

### Takeaway
Retail discovery returned several current Taiwan creator titles, but each is already represented in the local public-catalog source or live MuseBooks, so these are duplicate checks only.

### Cited Findings
- Sanmin lists 彭彭’s physical book 《彭然心動：彭彭寫真》 (ISBN 9786264448420, 時報文化, 2026-09-11, paperback, 144 pages, in stock). The local catalog already has its physical edition, and MuseBooks search shows the work under [work-tw-48cee531f79d279264813cd3](https://musebooks.my/books/work-tw-48cee531f79d279264813cd3); the digital edition is also already recorded in the prior-round ledger. [Sanmin product](https://www.sanmin.com.tw/product/index/015778708)
- 城邦 lists 瑟七’s 《微澀・微瑟》 physical book (ISBN 9786264552080, 尖端, 2026-07-07, 144 pages) and states it is her first physical photobook after digital title 《青瑟47》. The local catalog already contains this physical book and related digital editions. [Cite product](https://www.cite.com.tw/book?id=108115)
- TAAZE lists 夏蕾’s 《心動蕾達：夏蕾寫真》 physical paperback (ISBN 9786264446549, 時報文化, 144 pages) and marks it forthcoming/available in late September 2026; the catalog already contains its physical and digital records. [TAAZE product](https://www.taaze.tw/products/11101098397.html)
- Eslite markets an exclusive “真心收藏版” for the existing group photobook FIRST JUMP, adding a signed collector board; it does not provide a distinct ISBN, and the standard physical/digital work already exists in MuseBooks. Treat this as a retailer bundle unless a separate book edition is evidenced. [Eslite product](https://www.eslite.com/product/10012102292683127157000); [live MuseBooks work](https://musebooks.my/books/work-tw-27180567259fb6d43aed9de4)
- The official 小蜂光 Bee3Shine product page lists 《三倍心跳》 as a physical three-person photobook, and MuseBooks already has the work plus a signed-board set edition. [Publisher product](https://bee3shine.com/product/%E3%80%8A%E4%B8%89%E5%80%8D%E5%BF%83%E8%B7%B3%E3%80%8B%E6%A2%93%E6%A2%93x%E6%9E%97%E8%8E%8Ex%E5%85%83%E5%85%83-%E9%99%90%E9%87%8F%E4%B8%89%E4%BA%BA%E5%AF%AB%E7%9C%9F%E5%A5%97%E7%B5%84/); [live MuseBooks work](https://musebooks.my/books/work-tw-96926b38696ba73e299897d0)

### Inferences
- No additional edition or cover should be uploaded for these duplicate title checks without evidence of a distinct book edition, rather than merely a retailer gift bundle.

### Gaps
- The exclusive FIRST JUMP bundle’s product barcode is visible as an EAN on Eslite, but no distinct book ISBN or changed book contents were identified; a separate edition-level import is not justified by this page alone.

## Search boundary

### Takeaway
This pass focused on recently published or newly surfaced titles at Taiwanese print retailers, publisher pages, and creator campaigns. It did not establish exhaustive coverage of informal, expired, or social-only preorder listings.

### Cited Findings
- Retail search surfaced 《FOUR》 as a current preorder but not yet fulfilled, and 《FEVER》 as a recently released Taiwan Kadokawa physical title; their source-level limits are recorded above. [Zeczec](https://www.zeczec.com/projects/ADAM2026); [Kingstone](https://www.kingstone.com.tw/basic/2019500066780/)

### Inferences
- Repeating the same retailer search now is unlikely to produce a catalog-safe addition; a later pass can revisit campaign projects after fulfilment and cover release.

### Gaps
- Crowdfunding, social-store, and expired preorder pages can be difficult to distinguish from issued editions until a final product page or delivered book becomes available.
