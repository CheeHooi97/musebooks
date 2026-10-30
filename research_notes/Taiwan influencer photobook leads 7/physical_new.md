# Physical Taiwan creator photobook leads

## New physical editions verified

### Takeaway
The direct iWIN product record and Taiwan National Central Library bibliography support one qualifying self-published solo physical photobook, 《芷想被你收藏Candy芷媗首本個人實體寫真》. It appeared in the live MuseBooks catalog while this research was in progress, so it is already covered and should not be imported again.

### Cited Findings
- iWIN's direct product page identifies the item as Candy 芷媗's first personal physical photobook, specifies paperback binding, 144 pages, dimensions 18×25.6×1.2 cm, initial printing, NT$1,499, release date 2025-10-23, and iWIN 曖維多媒體廣告行銷股份有限公司 as the producing company; the shop currently marks it sold out. [iWIN product page](https://www.iwinimc.com/products/candy1023-photobook)
- The National Central Library's 11410 new-books bibliography lists the same title and author, ISBN 9786269273300, 144 pages, paperback, 2025-10 publication, Taipei, and publisher 曖維多媒體廣告行銷. This resolves the ISBN omitted from the seller page. [NCL monthly bibliography PDF](https://isbn.ncl.edu.tw/FCKEDITOR_UploadFiles/1763434068.pdf)
- A secondary mirror of the creator's Instagram profile identifies the account as 芷媗｜Candy (@candy_muwanna_0903), describes her as a Tainan girl and actor/model, and advertises the same first physical photobook. The mirror displayed about 127,000 followers at retrieval; follower counts are dynamic and the mirror is not Instagram itself. [Profile mirror](https://imginn.com/candy_muwanna_0903/)
- The iWIN page describes 芷媗 as a model and AV actress, and says she personally financed the photobook; this is individual creator material rather than an ensemble or drama tie-in. [iWIN product page](https://www.iwinimc.com/products/candy1023-photobook)
- The live MuseBooks record is [work-tw-bd736260748f93769128a0f1](https://musebooks.my/books/work-tw-bd736260748f93769128a0f1). Its edition records ISBN 9786269273300, physical format, 144 pages, 2025-10-23, TW market, and the iWIN publisher. A read of the live API succeeded; its stored cover media URL was HTTP 200, image/jpeg, 3,417,403 bytes, SHA-256 `c993f877b73a6a7a0b5fbf4021d24e4e7c6afebd65df8a7d533aa5954af4a4a6`. [Live edition API](https://musebooks.my/v1/books/work-tw-bd736260748f93769128a0f1)
- Stored cover URL: https://media.musebooks.my/musebooks/covers/c993f877b73a6a7a0b5fbf4021d24e4e7c6afebd65df8a7d533aa5954af4a4a6.jpg . The image object currently resolves from MuseBooks media; this pass did not independently compare its pixels to the seller gallery because the seller storefront blocked direct image retrieval.

### Inferences
- The self-description as a Tainan girl, model/actor and the individual book offer support treating 芷媗 as a Taiwan-based creator; they do not independently establish nationality or residence.
- This is import-grade bibliographic evidence, but it is already in the live catalog and its seller listing is sold out. No new import is recommended from this lane.

### Gaps
- iWIN does not show the ISBN in the direct product page; ISBN is supported by the NCL listing.
- The seller gallery's original cover-image URL could not be retrieved in this pass. The live catalog contains a working R2/MuseBooks media object, but the image-to-product visual match was not independently checked here.

## Duplicate and scope checks

### Takeaway
Recent physical titles surfaced during the scan were already represented in the catalog, or were team/group products rather than new individual influencer editions.

### Cited Findings
- The live catalog already contains separate physical and digital versions of 瑟七's 《微澀・微瑟》; the physical edition's publisher, ISBN, date, 144-page count and solo-author attribution are documented by 城邦讀書花園. [Cite product page](https://www.cite.com.tw/book?id=108115)
- Current API searches returned existing physical records for MILA林采婕's 《A SLOWER SUMMER》, 郭郭's 《RAINY SUMMER SECRETS》, 舒舒's 《舒舒19歲寫真》, 夏蕾's 《心動蕾達：夏蕾寫真》, and 彭彭's 《彭然心動：彭彭寫真》; these were not treated as new additions in this assignment.
- 《FIRST JUMP：TOKKI CUTIE 臺北伊斯特啦啦隊寫真故事 2025-2026》 is a 16-member team photo story, not an individual creator's personal photobook; the publisher/retailer record confirms the ensemble authorship and 16-member content. [Sanmin product page](https://www.sanmin.com.tw/product/index/015309196)

### Inferences
- Exact-title and creator API checks are necessary because same-season new releases are being added to the shared catalog concurrently; a web-search hit alone does not make an edition new.

### Gaps
- This scan did not establish a further importer-ready, not-yet-cataloged solo physical photobook beyond 《芷想被你收藏》.
