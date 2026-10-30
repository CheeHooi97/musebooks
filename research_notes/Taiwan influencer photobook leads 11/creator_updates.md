# Official Taiwanese creator and campaign updates — round 11

## Prior held leads: did item-level evidence change?

### Takeaway

None of the three earlier holds now has the complete direct product, finalized-cover, and delivery evidence needed to recommend a new import. 《FOUR》 remains a live preorder; 《韓你菲》 has an announced sale date and a creator-profile snapshot that mentions a preorder link, but I could not resolve it to a direct item page; 鄭羽凡’s ebook has a direct Books.com listing, but its file format still conflicts with the National Central Library record.

### Cited Findings

- Zeczec’s live 《FOUR》 campaign identifies the work as Adam 林冠宇’s first ebook, running 2026-10-12 to 2026-11-12. It lists digital and physical-reward bundles with estimated December 2026 fulfillment. The campaign also explicitly labels the shown reward/cover-like images as examples rather than final shipment designs. [Campaign](https://www.zeczec.com/projects/ADAM2026)
- The campaign FAQ says the ebook is a password-encrypted PDF, and that download instructions will follow campaign close and production. [Official FAQ](https://www.zeczec.com/projects/ADAM2026/faqs)
- 民視’s 2026-08-31 story says 李恩菲’s 《韓你菲》 was scheduled to go on sale at 8 p.m. on Sep. 2 and directs readers to her official social channels for sales details. A public profile-index snapshot later included “韓你菲寫真書” and a preorder-link label in her bio, but the indexed page does not expose the link target or product details. [民視 announcement](https://www.ftvnews.com.tw/news/detail/2026831W0260); [public profile-index snapshot](https://www.kolr.ai/influencer/a7c5f083-7e76-46ad-8b53-e6ca47e18ea9); [李恩菲’s Instagram profile](https://www.instagram.com/luvssi_official_/)
- Exact-title and ISBN searches on the live MuseBooks API returned no 《韓你菲》 record. [Title query](https://musebooks.my/v1/books?q=%E9%9F%93%E4%BD%A0%E8%8F%B2); [李恩菲 query](https://musebooks.my/v1/books?q=%E6%9D%8E%E6%81%A9%E8%8F%B2)
- Books.com’s item page currently offers both electronic and paperback versions of 鄭羽凡’s 《其實我有點壞Si;era’s photobook》. It lists publication date 2026-08-18, EISBN 9786267742044, and “EPUB固定版型”; its paperback ISBN is 9786269640614. [Direct Books.com item page](https://www.books.com.tw/products/E050354706)
- The NCL deposit record for EISBN 9786267742044 labels the digital file “PDF,” so the format conflict remains unresolved. The live MuseBooks title search returns the existing physical record, while a direct EISBN query returns zero. [NCL record](https://isbn.ncl.edu.tw/FCKEDITOR_UploadFiles/1755143472.pdf); [MuseBooks 鄭羽凡 query](https://musebooks.my/v1/books?q=%E9%84%AD%E7%BE%BD%E5%87%A1); [MuseBooks EISBN query](https://musebooks.my/v1/books?q=9786267742044); [existing physical work](https://musebooks.my/books/work-tw-9bcbbed2719c0138ff33c410)

### Inferences

- Keep 《FOUR》 on hold: its digital file has not yet been delivered, the campaign remains open, and the campaign’s own terms say the pictured artwork/rewards are not final. [Campaign](https://www.zeczec.com/projects/ADAM2026); [FAQ](https://www.zeczec.com/projects/ADAM2026/faqs)
- Keep 《韓你菲》 on hold: the launch announcement and bio snippet support that a sale was planned, but they do not identify an item-specific seller listing, ISBN, final-cover match, or completed delivery. [民視 announcement](https://www.ftvnews.com.tw/news/detail/2026831W0260); [profile-index snapshot](https://www.kolr.ai/influencer/a7c5f083-7e76-46ad-8b53-e6ca47e18ea9)
- Do not add a second 鄭羽凡 work or edition from the present evidence: a retail ebook exists, but the official deposit metadata conflicts on the file type and the live catalog currently has only the physical edition. [Books.com listing](https://www.books.com.tw/products/E050354706); [NCL record](https://isbn.ncl.edu.tw/FCKEDITOR_UploadFiles/1755143472.pdf); [MuseBooks result](https://musebooks.my/v1/books?q=%E9%84%AD%E7%BE%BD%E5%87%A1)

### Gaps

- 《FOUR》 needs a post-campaign file-delivery notice and the final ebook cover/artwork after production.
- 《韓你菲》 still needs a direct seller or creator product URL, an edition identifier, and a confirmed final cover. The visible bio-index reference is not itself an item page.
- For 鄭羽凡, seek a publisher/retailer clarification for EPUB versus PDF and an ebook-specific cover verification.

## Distinct creator products and live catalog checks

### Takeaway

This search turned up several Taiwan-based creators not named in the round-10 creator notes, but their verified books are already represented in MuseBooks. One record has an ISBN omission and another has an ebook identifier mismatch, so these are metadata-enrichment leads rather than new works; no R2 or database changes were made.

### Cited Findings

- The iWIN publisher/shop listing for 《美家MIGA 2025 PHOTO BOOK》 describes a 152-page paperback, first printing, issued 2025-07-07, and records that shipment began on that date; the related item page is now marked sold out, while iWIN’s current MIGA shop listing marks the title “絕版倒數.” NCL’s deposit list separately gives ISBN 9786269847389 and 152 pages. The live MuseBooks edition records 2025-07-14, a one-week difference from the iWIN ship/release date that should be reviewed before date edits. [iWIN preorder/item page](https://www.iwinimc.com/products/miga0908-photobook-preorderonly); [current iWIN MIGA listings](https://www.iwinimc.com/categories/miga0908); [NCL deposit list](https://nclfile.ncl.edu.tw/files/202601/b3004984-f47b-401e-912e-06a080ffd1b0.pdf); [MuseBooks record](https://musebooks.my/books/work-tw-db4847ca5e3bb47ef8f04363)
- MuseBooks already has MIGA’s work `work-tw-db4847ca5e3bb47ef8f04363` and physical edition `edition-e127cda19a80e7dea8eb5dfc`, with an R2 cover. The live record’s ISBN field is empty, so searching by NCL ISBN 9786269847389 does not return it; do not create a duplicate work. [MuseBooks MIGA record](https://musebooks.my/books/work-tw-db4847ca5e3bb47ef8f04363); [live title query](https://musebooks.my/v1/books?q=%E7%BE%8E%E5%AE%B6Miga); [live ISBN query](https://musebooks.my/v1/books?q=9786269847389)
- 《芯裡都是你》小珍奶王芯羽寫真書 is a 176-page 2025-03-11 paperback, ISBN 9786264034050; the publisher’s Sharp Point page identifies the physical item and describes her as a social-media personality and cheerleader. Sharp Point’s digital division separately lists 《珍芯愛你》 as her digital photobook. [Sharp Point physical item](https://www.spp.com.tw/SalePage/Index/10581490); [retailer bibliographic detail](https://www.cite.com.tw/book?id=102866); [Sharp Point digital item](https://www.espp.com.tw/ctn.aspx?bc=EAFB0091-001)
- The live catalog already has the physical 小珍奶 work `work-tw-e1053f2e1c9480b4a9235a75` and both distinct digital works, including a digital-only 和服 version. [MuseBooks 小珍奶 query and editions](https://musebooks.my/v1/books?q=%E5%B0%8F%E7%8F%8D%E5%A5%B6)
- Kingstone’s item page for 《綾の邊界 きわ》阿厚綾 shows a physical paperback dated 2026-08-18, product artwork, price, and a past estimated shipment date of 2026-10-01; at the time of the page snapshot, it still showed remaining stock. A model-agency profile describes 阿厚綾 as a Taiwan-based KOL. [Kingstone product page](https://www.kingstone.com.tw/basic/2075020023320/?actid=&lid=mag_newprod); [model-agency profile](https://www.showgirl.com.tw/card/S0003684)
- MuseBooks already has 阿厚綾’s physical work `work-tw-3575066e4bd36091324620d0` and edition `edition-e1012f702d528e355fc5384e`, with a cover image. The Kingstone record has no ISBN or page count, so those fields should remain unknown. [MuseBooks 阿厚綾 record](https://musebooks.my/books/work-tw-3575066e4bd36091324620d0); [live API title query](https://musebooks.my/v1/books?q=%E9%98%BF%E5%8E%9A%E7%B6%BE)
- 時報出版’s physical 《心存感恩：心恩做最好的自己真愛寫真》 lists 廖心恩, print ISBN 9786263741645, 2023-09-05 release, and describes her work as DJ and cheerleader. Kobo’s separate ebook listing gives ebook ISBN 9786263741713 and EPUB3 fixed-layout. [TAAZE physical item](https://m.taaze.tw/do/mobile/single.aspx?pid=11101017284); [Kingstone physical item](https://www.kingstone.com.tw/basic/2019910050805/); [Kobo ebook item](https://www.rakuten.com.tw/shop/kobo/product/59ff1e8e-b5d9-3fb3-b447-10a43f125dcc/)
- MuseBooks already has 廖心恩’s work `work-tw-8b1823cc55eec939d9a91699`, with physical and digital editions. However, the live digital edition stores the print ISBN 9786263741645, whereas Kobo identifies the ebook as 9786263741713; exact ISBN API queries return no result. [MuseBooks 廖心恩 query](https://musebooks.my/v1/books?q=%E5%BB%96%E5%BF%83%E6%81%A9); [print ISBN query](https://musebooks.my/v1/books?q=9786263741645); [ebook ISBN query](https://musebooks.my/v1/books?q=9786263741713)

### Inferences

- MIGA’s title is a catalog duplicate, but its catalog edition likely merits a later ISBN metadata patch after review: NCL supplies the identifier while the publisher page omits it and the live edition field is blank. Do not import another work for the same title. [NCL list](https://nclfile.ncl.edu.tw/files/202601/b3004984-f47b-401e-912e-06a080ffd1b0.pdf); [MuseBooks record](https://musebooks.my/books/work-tw-db4847ca5e3bb47ef8f04363)
- The 小珍奶 books and 阿厚綾 book should not be imported again because matching catalog works/editions are already present. [MuseBooks 小珍奶](https://musebooks.my/v1/books?q=%E5%B0%8F%E7%8F%8D%E5%A5%B6); [MuseBooks 阿厚綾](https://musebooks.my/books/work-tw-3575066e4bd36091324620d0)
- 廖心恩’s ebook looks like an existing edition with a likely identifier correction to review, not an extra work: the seller provides a distinct ebook ISBN, while the live record repeats the print ISBN. [Kobo](https://www.rakuten.com.tw/shop/kobo/product/59ff1e8e-b5d9-3fb3-b447-10a43f125dcc/); [MuseBooks record](https://musebooks.my/v1/books?q=%E5%BB%96%E5%BF%83%E6%81%A9)

### Gaps

- MIGA’s product-specific iWIN page does not display its ISBN; the NCL deposit record fills that gap, but the existing live edition would need an explicit metadata correction to match.
- The current creator/publisher search was targeted, not a comprehensive census. It does not establish that all Taiwan influencers with photobooks are cataloged.

## Import decision and remaining checks

### Takeaway

No new record is recommended from this pass: the newly checked creator products are existing works, and the previously held products still lack one or more required item-level checks. This assignment was read-only, so no database or R2 changes were made.

### Cited Findings

- MuseBooks title searches return existing records for MIGA, 小珍奶, 阿厚綾, and 廖心恩. [MIGA](https://musebooks.my/v1/books?q=%E7%BE%8E%E5%AE%B6Miga); [小珍奶](https://musebooks.my/v1/books?q=%E5%B0%8F%E7%8F%8D%E5%A5%B6); [阿厚綾](https://musebooks.my/v1/books?q=%E9%98%BF%E5%8E%9A%E7%B6%BE); [廖心恩](https://musebooks.my/v1/books?q=%E5%BB%96%E5%BF%83%E6%81%A9)
- The 《FOUR》 campaign is still scheduled to deliver in December after its November close, and 《韓你菲》 still has no resolved direct product listing in the search results. [FOUR campaign](https://www.zeczec.com/projects/ADAM2026); [FOUR FAQ](https://www.zeczec.com/projects/ADAM2026/faqs); [韓你菲 announcement](https://www.ftvnews.com.tw/news/detail/2026831W0260)
- 鄭羽凡’s direct ebook listing remains at odds with the NCL record on format. [Books.com](https://www.books.com.tw/products/E050354706); [NCL](https://isbn.ncl.edu.tw/FCKEDITOR_UploadFiles/1755143472.pdf)

### Inferences

- Keep all three held leads open for later evidence; consider MIGA ISBN and 廖心恩 ebook ISBN as metadata-enrichment checks rather than new work imports. No import or R2 upload was made in this round.

### Gaps

- Search coverage remains selective across creator self-publishing, publisher catalogs, digital platforms, and crowdfunding. Further rounds are needed before the larger “all Taiwan influencers” goal can be treated as complete.
