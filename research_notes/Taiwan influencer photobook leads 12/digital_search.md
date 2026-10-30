# Taiwan digital photobook and identifier review — round 12

## Takeaway

No new digital work cleared import review this pass. A verified format-specific identifier corrected an existing Taiwan creator ebook record for 廖心恩; the title and cover were already in MuseBooks.

## Cited findings

- Kobo identifies 《心存感恩：心恩做最好的自己真愛寫真》 by 廖心恩 as an **EPUB3 fixed-layout** ebook, published 2023-09-01, with ebook ISBN **9786263741713**. ([Kobo ebook product](https://www.rakuten.com.tw/shop/kobo/product/59ff1e8e-b5d9-3fb3-b447-10a43f125dcc/))
- The National Central Library deposit list separately assigns **9786263741706 to PDF** and **9786263741713 to EPUB** for the same title. The print ISBN remains **9786263741645**. ([NCL ebook deposit list](https://isbn.ncl.edu.tw/FCKEDITOR_UploadFiles/1692349219.pdf); [publisher / print product record](https://item.rakuten.co.jp/asia-music/bk-9786263741645/))
- Before this correction, the live MuseBooks work `work-tw-8b1823cc55eec939d9a91699` contained a physical edition with print ISBN **9786263741645** and a digital edition incorrectly repeating that print ISBN. The guarded importer updated the existing digital edition `edition-b2e728c72efb55b4fa567905` to ISBN **9786263741713**, label **EPUB3 fixed-layout**, and the Kobo metadata page. It did not create a duplicate work or add a PDF edition.
- Post-import API readback returned the existing work with two editions and the corrected EPUB ISBN. Its existing cover remains on `media.musebooks.my`; public retrieval returned **349,524 bytes**, SHA-256 `17a55f75126f0795812998979defbfd3791333c36b0267b5b9344e7ae34f3de5`.
- The existing Pubu ebook offer remains associated with the work. Its listing page did not provide direct format-specific evidence in this pass, so no PDF edition or additional offer was inferred from the National Central Library deposit alone. ([Pubu title search](https://www.pubu.com.tw/bookbuffet/category/photo-books-399?fl_chid=1))

## Decision and gap

The ebook identifier correction is committed and publicly readable. A separate PDF record needs a format-confirming seller page before it is added.
