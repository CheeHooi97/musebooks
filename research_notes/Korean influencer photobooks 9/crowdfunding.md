# Korean creator photobook crowdfunding

## What campaign and product are verified?

### Takeaway
One fresh campaign candidate surfaced: the 2024 Tumblbug project for `<차원을 넘어 이세계아이돌> 단행본&굿즈`, which included a separately named `특별 화보집` reward. The product appears to be an illustrated book about the virtual creators’ webtoon characters, not a conventional photographic portrait book, so catalog-scope fit is uncertain.

### Cited Findings
- Tumblbug names the project `<차원을 넘어 이세계아이돌> 단행본&굿즈`, identifies Kakao Entertainment as the creator, and lists the project as successful, with 35,651 backers, ₩8,822,342,758 raised, and a campaign period of 2024-10-23 through 2024-11-22. Its progress indicator is at `발송완료` (shipping complete). [Tumblbug project page](https://tumblbug.com/beyondthedimension_isedol)
- Contemporary coverage says the campaign included a standalone special photobook among the printed webtoon volumes and other merchandise. [News1](https://www.news1.kr/amp/it-science/general-it/5612728); [Yonhap News](https://www.yna.co.kr/view/AKR20241127157700005)
- A product-focused report describes the special photobook as a collection of illustrations, distinguishing it from a photographed creator/model pictorial. [I Love Character](https://www.ilovecharacter.com/news/newsview.php?ncode=1065597047851664)
- A public resale listing titled `차세돌 화보집` describes the item as new and unused. This is seller-provided condition information, not an independent inspection, but it is additional evidence that a physical item with this title circulated after the campaign. [Bunjang listing](https://m.bunjang.co.kr/products/387923398)
- News1 identifies ISEGYE IDOL as a six-member virtual idol group produced with YouTuber Woowakgood; it reports that the campaign was based on the group and included the special photobook. [News1](https://www.news1.kr/amp/it-science/general-it/5612728)

### Inferences
- The campaign, creator connection, and post-campaign project-completion evidence are strong. Taken together with a separate listing for an unused copy, they support that the photobook was produced physically; the direct project page marks overall campaign rewards shipped, but does not show a photobook-specific dispatch record in its readable public text.
- Since the contents are illustrations of a virtual-idol/webtoon property, cataloging it as an influencer photobook would depend on MuseBooks treating illustrated avatar books as photobooks. Under a strict photographic-book definition, it should stay out of the influencer photobook set.

### Gaps
- No standalone bibliographic title beyond `특별 화보집` / `차세돌 화보집`, ISBN, page count, dimensions, or separate publisher imprint was verified. [Tumblbug project page](https://tumblbug.com/beyondthedimension_isedol); [News1](https://www.news1.kr/amp/it-science/general-it/5612728)
- The sources do not establish that the photobook itself, rather than other reward items, is what a particular backer received; Tumblbug’s status is campaign-level. The resale condition claim is unverified. [Tumblbug project page](https://tumblbug.com/beyondthedimension_isedol); [Bunjang listing](https://m.bunjang.co.kr/products/387923398)
- No asset-specific license or reuse permission for campaign/book images was found. No image was downloaded or proposed for R2.

## Does this count as a fresh campaign lead?

### Takeaway
It is absent from the repository’s Korean photobook reports, research notes, docs, and cumulative catalog log checked in this pass, but live database uniqueness was not checked. The older named leads and the already documented Kim Woo-hyun `Extreme` thread were excluded from candidate consideration.

### Cited Findings
- The repository-wide exact-name scan across `reports`, `research_notes`, `docs`, and `scraper/catalog-import-report.md` returned no matches for `차원을 넘어 이세계아이돌`, `차세돌`, or `ISEGYE IDOL` at the time of this pass.
- The creator/project is distinct from the known exclusions (Anessa/Hurricane Kimchi, Rustic 24SS, Kim Hong-hee/XMosaiX, Woomori, and 냥슬). Kim Woo-hyun’s separate `Extreme` project is already discussed in earlier repository notes and was not counted as fresh. [Prior research note](../Korean%20influencer%20photobook%20additions%204/woohyun.md)

### Inferences
- The candidate is fresh relative to the checked workspace files; that does not establish it is absent from the live MuseBooks database.

### Gaps
- A live catalog/DB duplicate lookup is outside this research assignment and remains necessary before any import.

## Import recommendation

### Takeaway
Hold for a catalog-scope decision. The campaign and physical production signal are much better supported than many campaign-only leads, but its content is described as illustration-based rather than photographs of the creators.

### Cited Findings
- The Tumblbug page confirms successful funding and project-wide shipment completion; the reported project package included the special photobook. [Tumblbug project page](https://tumblbug.com/beyondthedimension_isedol); [News1](https://www.news1.kr/amp/it-science/general-it/5612728)
- The available product description specifically characterizes the book as a collection of illustrations. [I Love Character](https://www.ilovecharacter.com/news/newsview.php?ncode=1065597047851664)

### Inferences
- If MuseBooks includes illustrated works depicting virtual creator personas in its photobook category, this is a reasonable physical-edition candidate after live DB deduplication and a better bibliographic record. If the collection is limited to photographic photobooks, do not import it as an influencer portrait book.

### Gaps
- A decision on whether avatar illustrations fit the catalog’s influencer-photobook scope, plus a live duplicate check, is needed before proposing a manifest or DB write.
