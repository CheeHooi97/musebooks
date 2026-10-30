# Taiwan influencer physical photobooks — round 11

## Search for new Taiwan-origin creator photobooks

### Takeaway

No new import-grade physical title emerged in this bounded pass. Recent direct retail hits were already present in MuseBooks/catalog, were a team book, or featured a Korean creator rather than a Taiwan-origin influencer. No database or R2 changes were made.

### Cited Findings

- Kingstone and Sanmin list **《芯裡都是你》小珍奶王芯羽寫真書** as a Taiwan paperback, ISBN **9786264034050**, publisher 尖端, 176 pages; the seller page gives 2025-03-11. Kingstone describes 王芯羽 as a cheerleader with substantial social followership. A live MuseBooks exact-title query returns existing physical work **work-tw-e1053f2e1c9480b4a9235a75**, with the same ISBN. The existing work is also present in the catalog file. ([Kingstone product page](https://www.kingstone.com.tw/basic/2019590014883/); [Sanmin product page](https://www.sanmin.com.tw/product/index/014063456); [MuseBooks record](https://musebooks.my/books/work-tw-e1053f2e1c9480b4a9235a75); [catalog entry](../../scraper/taiwan-photobook-catalog.md#王芯羽))
- **《彭然心動：彭彭寫真》** has an item-specific physical listing from CityBook: ISBN **9786264448420**, paperback, 144 pages, publisher 時報文化. CityBook and TAAZE differ on the release day (2026-09-11 vs. 2026-09-15). A live MuseBooks exact-title query returns existing work **work-tw-48cee531f79d279264813cd3**, which already contains physical and digital editions. ([CityBook product page](https://www.cite.com.tw/book?id=108961); [TAAZE product page](https://ebook.taaze.tw/do/mobile/single.aspx?org_flg=1&pid=11101097844&prod_cat_id=11); [MuseBooks record](https://musebooks.my/books/work-tw-48cee531f79d279264813cd3))
- **《心動蕾達：夏蕾寫真》** has a physical paperback edition (ISBN **9786264446549**, 144 pages, 2026-09-18) and an EPUB edition (EISBN **9786264446433**). The publisher/retailer describes 夏蕾 as a Taiwan cheerleader. Live MuseBooks search returns existing work **work-tw-44b0143f8e9afb4d9fff0e09** with both formats, plus a separate limited-box work; neither is a new title. ([Sanmin physical listing](https://www.sanmin.com.tw/product/index/015783272); [Readmoo digital listing](https://reading.udn.com/ebook/store/store_product.do?pid=173955&source=%E5%AF%AB%E7%9C%9F%E9%9B%86); [MuseBooks work](https://musebooks.my/books/work-tw-44b0143f8e9afb4d9fff0e09); [publisher boxed edition](https://www.readingtimes.com.tw/product/?pid=1VY0480))
- **《想與你一起渡過：金渡兒影像紀實》** is a current physical 144-page paperback, ISBN **9786264553773**, published by 尖端 on 2026-09-09. Sanmin identifies 金渡兒 as Korean-born Kim Do-A from Incheon; Taiwan coverage also calls her a Korean cheerleader. A live MuseBooks exact-title/person query returns existing work **work-tw-ced53516a440d27c1c1f6e1d**. It is both out of the Taiwan-origin scope and already cataloged. ([Sanmin product page](https://www.sanmin.com.tw/product/index/015782086); [Taiwan Yahoo Sports profile/interview](https://tw.sports.yahoo.com/news/%E5%B0%88%E8%A8%AA-ps%E5%A5%B3%E5%AD%A9-%E6%80%A7%E6%84%9F%E6%93%94%E7%95%B6-%E5%85%A8%E7%9C%8B%E5%A5%B9-%E9%87%91%E6%B8%A1%E5%85%92%E6%9B%9D%E8%8F%AF%E9%BA%97%E8%BD%89%E8%BA%AB%E5%A4%A2%E6%83%B3-063654969.html); [MuseBooks record](https://musebooks.my/books/work-tw-ced53516a440d27c1c1f6e1d))
- The recent **FIRST JUMP：TOKKI CUTIE** result is a 16-member cheer-team photo story rather than an individual creator book, and the physical work is already recorded as **work-tw-27180567259fb6d43aed9de4**. ([CityBook product page](https://www.cite.com.tw/book?id=107503); [MuseBooks record](https://musebooks.my/books/work-tw-27180567259fb6d43aed9de4))

### Inferences

- These sources establish that the products are genuine physical books and that the surfaced Taiwan-origin solo titles already have records. I found no basis to create a new work or physical edition in this pass.
- Direct API checks using each exact title/person return the existing work and edition ISBN. Direct ISBN-only queries returned zero because the MuseBooks search endpoint did not index ISBN as a query term; the ISBN match is verified in the returned edition metadata and retailer record.

### Gaps

- This is a focused scan of recent accessible retailer listings, not a complete census of small-run/self-published books or creator-store-only releases. A future pass may find new titles through social storefronts or older print catalogs, but those need item-level publication evidence before import.
- The linked seller pages expose product image previews, but I did not retrieve, visually inspect, or hash the individual image assets: every plausible Taiwan-origin title found here already has a MuseBooks record, so no cover asset was needed for a new import decision.

## Round 11 decision and duplicate checks

### Takeaway

No new candidate cleared the import bar. Keep the search open; this round only records screened duplicates and scope exclusions.

### Cited Findings

- Reproducible live MuseBooks queries: [王芯羽](https://musebooks.my/v1/books?q=%E7%8E%8B%E8%8A%AF%E7%BE%BD), [芯裡都是你](https://musebooks.my/v1/books?q=%E8%8A%AF%E8%A3%A1%E9%83%BD%E6%98%AF%E4%BD%A0), [彭然心動](https://musebooks.my/v1/books?q=%E5%BD%AD%E7%84%B6%E5%BF%83%E5%8B%95), [夏蕾](https://musebooks.my/v1/books?q=%E5%A4%8F%E8%95%BE), [金渡兒](https://musebooks.my/v1/books?q=%E9%87%91%E6%B8%A1%E5%85%92), and [FIRST JUMP](https://musebooks.my/v1/books?q=FIRST%20JUMP).
- The catalog already lists 王芯羽’s physical title and her earlier digital books; Round 10 records 夏蕾’s standard physical and digital editions, and prior catalog/research records cover 彭彭 and the team title. ([王芯羽 catalog entry](../../scraper/taiwan-photobook-catalog.md#王芯羽); [Round 10 physical search](../Taiwan%20influencer%20photobook%20leads%2010/physical_search.md); [Round 10 creator updates](../Taiwan%20influencer%20photobook%20leads%2010/creator_updates.md))

### Inferences

- Do not re-import any of these products. Do not include the Korean creator’s book when selecting Taiwan-origin influencer works. Do not turn the group book into an individual creator record.

### Gaps

- The remaining work is discovery of genuinely new Taiwan-origin creator books with direct seller/publisher metadata and confirmed cover assets; this pass did not locate one.
