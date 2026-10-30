# Taiwan digital photobook candidate check

## Does the new digital edition have import-grade product evidence?

### Takeaway
《芷想靠近你：劉芷伊醫師寫真》 has a clearly identified digital edition with a distinct EISBN, fixed-layout EPUB format, release date, 143-page count, publisher, and retailer cover assets. It is **not a new DB import**: the live MuseBooks work already contains both physical and digital editions, each with a stored R2 cover.

### Cited Findings
- Pubu identifies the digital product as 《芷想靠近你：劉芷伊醫師寫真》 by 劉芷伊, 時報出版, released 2026-10-09; it specifies fixed-layout EPUB (77 MB), 143 pages, and ID 701209. [Pubu product page](https://www.pubu.com.tw/ebook/701209)
- Books.com separately identifies print ISBN **9786264444811** and EISBN **9786264444965**, and specifies fixed-layout EPUB (84.0 MB). The page lists the same publisher and 2026-10-09 date. [Books.com ebook page](https://www.books.com.tw/products/E050360504)
- The publisher and date also appear on the retailer product pages; Books.com calls the work an ebook and Pubu explicitly labels it an ebook. [Pubu](https://www.pubu.com.tw/ebook/701209); [Books.com](https://www.books.com.tw/products/E050360504)
- Cover URLs exposed by the retailer pages: Pubu `https://res3.pubu.tw/docs/599522/49541/2lfZsK_l.jpg`; Books.com `https://im1.book.com.tw/image/getImage?i=https://www.books.com.tw/img/E05/036/05/E050360504.jpg&v=6acedc38k&w=1146&h=600`. [Pubu](https://www.pubu.com.tw/ebook/701209); [Books.com](https://www.books.com.tw/products/E050360504)
- TAAZE’s ebook listing instead labels the print ISBN 9786264444811 as ISBN/ISSN, so use Books.com’s explicit EISBN field or Pubu’s digital-product ISBN 9786264444965 to distinguish the ebook from print. [TAAZE ebook listing](https://www.taaze.tw/products/14100142767.html); [Books.com](https://www.books.com.tw/products/E050360504); [Pubu](https://www.pubu.com.tw/ebook/701209)

### Inferences
- The ebook is bibliographically distinct from the paper edition: its EISBN is 9786264444965, while the paper ISBN is 9786264444811.
- Retailer page-size fields conflict at 77 MB (Pubu) and 84.0 MB (Books.com); file size is not needed for the catalog record. Both pages agree on fixed-layout EPUB and the EISBN.

### Gaps
- Pubu supplies the ebook page count (143); Books.com does not report digital pagination. The print edition is 144 pages, which should not be substituted for ebook pagination.
- The retailer cover URLs were located in their product pages; this pass did not compare their image bytes pixel-for-pixel with the already stored R2 cover.

## Does the creator meet the Taiwan influencer scope?

### Takeaway
Yes. Retailer and media evidence identify 劉芷伊 as a Taiwan dentist and content creator with an established social-media audience; this supports including her work in the requested Taiwan creator scope.

### Cited Findings
- Pubu’s author bio describes 劉芷伊 as a well-known Taiwanese dentist and calls this her first personal photobook as a dentist. [Pubu product page](https://www.pubu.com.tw/ebook/701209)
- Mirror Media describes her as a dentist and content creator and reports her Taiwan medical-professional profile. [Mirror Media profile](https://www.mirrormedia.mg/story/20260709-190ent-171025)
- KOLR’s profile for Dr. Chavelle / 劉芷伊 links her Instagram account and gives roughly 305,820 Instagram followers and 800,000+ followers across social platforms at its 2026-10-13 update; it also reproduces her own post promoting the photobook. [KOLR creator profile](https://www.kolr.ai/influencer/fbd6dcbe-f71b-422c-92cf-57580745e210)

### Inferences
- The Taiwanese publisher and product bio alone would establish a Taiwan-market work, while the cited profile and media coverage provide the creator-specific Taiwan and influencer evidence.

### Gaps
- KOLR is a third-party influencer analytics directory; its follower totals are a dated snapshot, not a direct platform verification. The creator’s product announcement reproduced on that profile independently supports the link between her social presence and this edition.

## Is this absent from the catalog, and what should happen?

### Takeaway
It is already in MuseBooks and has an R2 cover, so do not re-import or upload another cover. This was a false-new lead caused by the local Markdown catalog showing only its physical edition.

### Cited Findings
- The local catalog file currently shows only the physical edition (ISBN 9786264444811) under 劉芷伊. [Taiwan photobook catalog](../../scraper/taiwan-photobook-catalog.md#L310)
- The exact live MuseBooks query returns work **work-tw-0fe3296d84c633e5ab200c65**, with physical edition **edition-423fb16ca0efa625e72af8f5** (ISBN 9786264444811) and digital edition **edition-58e8bdd2d57ed353039d3a87** (EISBN 9786264444965). [Live MuseBooks title query](https://musebooks.my/v1/books?q=%E8%8A%B7%E6%83%B3%E9%9D%A0%E8%BF%91%E4%BD%A0)
- The live digital edition is dated 2026-10-09, lists fixed-layout EPUB, and has an R2 cover stored at `musebooks/covers/fa5e0a19ec756ce870a8905949c3bede645c71a1cb776c34fe3d7eb4bc766c5e.jpg`; its stored pageCount is blank. [Live MuseBooks work record](https://musebooks.my/books/work-tw-0fe3296d84c633e5ab200c65)
- A live MuseBooks search by the EISBN alone returned total 0, although the exact title query exposes the existing digital edition. [MuseBooks EISBN query](https://musebooks.my/v1/books?q=9786264444965); [MuseBooks title query](https://musebooks.my/v1/books?q=%E8%8A%B7%E6%83%B3%E9%9D%A0%E8%BF%91%E4%BD%A0)

### Inferences
- The API record is the deciding duplicate check; the ISBN-only search appears not to index this EISBN consistently.
- No new record or R2 object should be created for this title. If the local catalog snapshot is refreshed later, it should represent both existing formats and retain the EISBN/print ISBN distinction.

### Gaps
- I did not run a separate live HTTP/hash check on the existing signed R2 media URL; this research assignment did not authorize an import or any R2 write.
