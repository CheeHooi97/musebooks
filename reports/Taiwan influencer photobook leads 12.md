# Round twelve corrects an ebook identifier; no new work cleared import

Round 12 did not surface a new Taiwan influencer photobook that met the import bar. It did resolve a format-specific identifier error on an existing title: 《心存感恩：心恩做最好的自己真愛寫真》 now records its EPUB ISBN **9786263741713**, distinct from the physical ISBN **9786263741645**. The existing work and R2 cover remain in place. A separate PDF sibling has ISBN **9786263741706** in the National Central Library records, but this pass did not find a seller item that confirms that exact PDF package.

## 廖心恩’s digital edition now has the EPUB identifier

Kobo’s direct product page describes the title as an **EPUB3 fixed-layout** ebook by 廖心恩 and gives ISBN **9786263741713**. The National Central Library independently records **9786263741713 as EPUB** and **9786263741706 as PDF**; the physical edition’s ISBN is **9786263741645**. ([Kobo ebook listing](https://www.rakuten.com.tw/shop/kobo/product/59ff1e8e-b5d9-3fb3-b447-10a43f125dcc/); [NCL format records](https://isbn.ncl.edu.tw/FCKEDITOR_UploadFiles/1692349219.pdf); [print edition identifier](https://item.rakuten.co.jp/asia-music/bk-9786263741645/))

Before the correction, the live work `work-tw-8b1823cc55eec939d9a91699` had one physical and one digital edition, and both incorrectly carried the physical ISBN. The guarded importer updated the existing digital edition `edition-b2e728c72efb55b4fa567905` with the EPUB ISBN, an EPUB3 fixed-layout label, and the Kobo metadata source. It did not create another work. The existing Pubu offer remains attached; no format-specific PDF offer was added. ([Pubu photobook category](https://www.pubu.com.tw/bookbuffet/category/photo-books-399?fl_chid=1))

The live MuseBooks API now returns the corrected digital ISBN and the existing physical edition under the same work. Its cover still resolves through the public Media Worker: **349,524 bytes**, SHA-256 `17a55f75126f0795812998979defbfd3791333c36b0267b5b9344e7ae34f3de5`. The catalog importer reported `Validated 1 import records` and `Catalog records and price observations committed; listing image provenance records: 0`. A full catalog verification retry completed successfully with **360 physical** and **5,092 digital** works; its first pass encountered a repeated work across pages while catalog totals were changing.

## Physical search returned duplicates, not a new Taiwan solo title

Recent search results included 夏蕾’s physical and EPUB editions, but both were already recorded under `work-tw-44b0143f8e9afb4d9fff0e09`. The 16-member FIRST JUMP: TOKKI CUTIE team book is also already recorded under its group work. No additional R2 cover was needed for either result. ([Pubu 夏蕾 ebook listing](https://www.pubu.com.tw/ebook/696714); [Sanmin physical listing](https://www.sanmin.com.tw/product/index/015783272); [MuseBooks 夏蕾 record](https://musebooks.my/books/work-tw-44b0143f8e9afb4d9fff0e09); [Sanmin FIRST JUMP listing](https://www.sanmin.com.tw/product/index/015309196); [MuseBooks group record](https://musebooks.my/books/work-tw-27180567259fb6d43aed9de4))

## 《韓你菲》 has a preorder clue, but no import-grade listing

FTV’s announcement says 李恩菲’s first solo physical photobook 《韓你菲》 was scheduled to go on sale on 2026-09-02, with sales details on her social channels. A Kolr snapshot updated 2026-10-17 still labels a preorder link in her Instagram bio. A Shopee search snippet names a preorder seller offer and an end-of-October shipping estimate, but the destination is only a generic search page; it does not prove that copies shipped or identify a final cover. Keep the title on hold until a direct product page and confirmed cover are available. ([FTV announcement](https://finance.ftvnews.com.tw/news/detail/2026831W0260); [Kolr profile snapshot](https://www.kolr.ai/influencer/a7c5f083-7e76-46ad-8b53-e6ca47e18ea9); [Shopee search](https://shopee.tw/search?keyword=%E6%9D%8E%E6%81%A9%E8%8F%B2))

## Search remains open

The new evidence corrected one existing digital edition but added no new work this round. The creator-storefront and older self-published catalog is still a selective search, and 《韓你菲》 and the previously held products need better item-level or fulfillment evidence before import.
