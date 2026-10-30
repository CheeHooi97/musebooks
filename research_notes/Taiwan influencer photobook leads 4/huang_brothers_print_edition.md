# Huang Brothers print edition

## Does the physical edition have sufficient product evidence?

### Takeaway
Yes. 《有你的夏天：黃氏兄弟寫真書II》 is a separately identified, import-grade paperback edition. Taiwan retailer records and the National Central Library agree on ISBN 9789865249793 and 144 pages; the retailers give the same 2021-10-25 publication date and provide identifiable product-cover images.

### Cited Findings
- The publisher’s [Kadokawa Taiwan product page](https://www.kadokawa.com.tw/en/products/9789865249793) lists the print title. Its product page was discoverable through search but returned HTTP 403 on direct fetch in this check; it was not the sole source for the physical edition details.
- Sanmin identifies the exact title as a 台灣角川 paperback, ISBN **9789865249793**, publication date **2021/10/25**, and **144 pages**; the product page’s Open Graph image points to its cover asset at [cdnec.sanmin.com.tw/product_images/986/986524979.jpg](https://cdnec.sanmin.com.tw/product_images/986/986524979.jpg). ([Sanmin product page](https://www.sanmin.com.tw/product/index/009797406))
- Kingstone independently identifies the title, author 黃氏兄弟, 台灣角川, date **2021/10/25**, print ISBN **9789865249793**, and paperbound format. Its product page identifies the cover and provides this direct image asset: [assets.kingstone.com.tw/book/images/product/20199/2019900098381/2019900098381b.jpg](https://assets.kingstone.com.tw/book/images/product/20199/2019900098381/2019900098381b.jpg). ([Kingstone listing](https://www.kingstone.com.tw/basic/2019900098381/))
- The National Central Library’s deposit list records the physical edition as a first edition from 臺灣角川, dated 2021-10, 144 pages, 26 cm, and 平裝 under ISBN **9789865249793**. ([NCL deposit list](https://isbn.ncl.edu.tw/FCKEDITOR_UploadFiles/1634009009.pdf))
- I downloaded and visually checked the Sanmin and Kingstone product-image assets. Both show the front cover of the same book, including its title and 黃氏兄弟寫真書II marking; the retailer images use different crops/mockup framing, so the image files are not byte-identical.

### Inferences
- The print edition should be represented as a distinct physical edition under the existing work `work-tw-6255401cda979711c736496a`, with ISBN 9789865249793, separate from the digital EISBN 9789865249809.
- The sources agree on the edition’s core metadata, so there is no material date, page-count, title, or format conflict to resolve before adding it.

### Gaps
- The publisher page itself could not be fetched directly because it returned HTTP 403. The edition details are independently corroborated by Sanmin, Kingstone, and the National Central Library.
- The Sanmin and Kingstone product images show the same cover design with different rendering/cropping. I did not retrieve a standalone cover file from Kadokawa’s own product page.

## Is the physical edition already in the live MuseBooks record?

### Takeaway
The work is now present in the live API, but its record currently contains only the digital edition. I found no physical edition in that work’s edition list.

### Cited Findings
- A direct read of the live [MuseBooks work record](https://musebooks.my/v1/books/work-tw-6255401cda979711c736496a) returns work `work-tw-6255401cda979711c736496a`, with one edition only: digital edition `edition-a4c8c2595ebda0ac9b7f42e3`, EISBN **9789865249809**, date 2021-10-29, 144 pages, and source BOOK☆WALKER product 126031.
- That API response contains no physical edition. The separate physical ISBN and metadata are independently supported by the [Sanmin listing](https://www.sanmin.com.tw/product/index/009797406), [Kingstone listing](https://www.kingstone.com.tw/basic/2019900098381/), and [NCL print deposit record](https://isbn.ncl.edu.tw/FCKEDITOR_UploadFiles/1634009009.pdf).
- A public API title search returned zero results during this check, but fetching the supplied work ID directly returned the full digital-only record. I rely on the ID lookup for the current edition count because it addresses the work directly.

### Inferences
- The product-level evidence supports adding a physical edition to the existing work, not creating another work for the same title. The physical edition should use ISBN 9789865249793, date 2021-10-25, 144 pages, paperback format, and a physical-product image source from one of the verified Taiwan retailer pages.

### Gaps
- The public API response is a point-in-time read; a separate physical edition could be added after this check.
- This check verified listing-level cover provenance and visual agreement between two retailer assets, but did not compare the source images against any private publisher master file.
