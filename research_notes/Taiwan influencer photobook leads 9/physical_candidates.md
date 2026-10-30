# Physical Taiwan creator photobook candidates

## Potential new record: 阿古《Self：A-KU寫真》

### Takeaway
This is a strong, previously uncataloged physical creator photobook candidate. **Go for DB/R2 import**: the CityBook product's direct JPEG was retrieved and visually confirmed as the 《Self：A-KU寫真》 book cover. Omit pageCount because the retailer and NCL disagree and no source explains the difference.

### Cited Findings
- TAAZE identifies the exact standalone paperback as 《Self：A-KU寫真》 by 阿古、黑雨舍, published by 尖端 on 2021-05-31, ISBN 9786263023475, 160 pages, with the product image displayed on the listing; it marks the new-book listing out of print. [TAAZE product page](https://www.taaze.tw/products/11100936032.html)
- CityBook (城邦讀書花園) independently confirms the same title, author, publisher, date, ISBN, paperback binding and 18 × 25.6 cm format, and describes it as 阿古's first individual physical photobook. [CityBook product page](https://www.cite.com.tw/book?id=88379)
- The National Central Library bibliography records the physical ISBN and title, but gives 150 pages rather than the retailers' 160. [NCL bibliography](https://isbn.ncl.edu.tw/FCKEDITOR_UploadFiles/1618364931.pdf)
- CityBook's author bio says 阿古 graduated from National Chiao Tung University's finance graduate program and began self-media work in 2019; the product copy explicitly calls him an internet influencer. Neither source explicitly states nationality, so the Taiwan link here is creator activity/education and Taiwan publication, not a verified nationality claim. [CityBook product page](https://www.cite.com.tw/book?id=88379)
- Exact live MuseBooks queries for 阿古, A-KU, the title, and ISBN 9786263023475 each returned zero results; the local catalog also has no 阿古/A-KU entry. [MuseBooks 阿古 query](https://musebooks.my/v1/books?q=%E9%98%BF%E5%8F%A4); [MuseBooks ISBN query](https://musebooks.my/v1/books?q=9786263023475)
- CityBook's product page declares `og:image` as `https://d4dpzjhk0g50s.cloudfront.net/images/s/SPB7G000090.jpg`. The JPEG is 439 × 600 pixels and 25,039 bytes; SHA-256 `09f2b22aad78b779e14913907fad7725f76fe0f54a21d7493d1c536aa20310be`. [Direct cover image](https://d4dpzjhk0g50s.cloudfront.net/images/s/SPB7G000090.jpg); [CityBook product page](https://www.cite.com.tw/book?id=88379)
- The downloaded image visibly shows a physical book mockup with the front title “Self”, the spine title “Self / Expose your true self”, and “A-KU” on the cover, matching the product ISBN/title page. It returned `image/jpeg` HTTP 200 when requested with the CityBook page as Referer; the same CDN blocks hotlink-free requests with HTTP 403. Local inspection copy: `.tmp/self_aku_cover.jpg`.

### Inferences
- Product and creator evidence plus the retrieved cover are sufficient to identify the historical Taiwan-market standalone physical edition for DB/R2 import.
- Use ISBN as the strongest edition identity and omit pageCount: TAAZE and CityBook say 160, while NCL says 150; none explains the discrepancy.

### Gaps
- Page count conflicts: TAAZE/CityBook say 160; NCL says 150. The discrepancy is unexplained, so do not write pageCount.
- No evidence of current new-copy availability; TAAZE labels its listing out of print.

## Recent physical search hits already represented or outside the target scope

### Takeaway
The recent high-signal individual releases checked in this pass do not add a new record: the catalog already contains the queried editions for 邊荷律, 禾羽 and 劉芷伊. 博文's newly released photo-art package is physical and well-described, but the available evidence identifies him as a bassist/musician rather than a Taiwan influencer or online creator, so it is held as scope-adjacent.

### Cited Findings
- 《荷止微甜：邊荷律影像紀實》 is already a two-edition physical work in MuseBooks (`work-tw-702b1a106e9e740afbb6dce7`); Newtalk describes its Taiwan retail launch and uses the influencer tag. [MuseBooks record](https://musebooks.my/books/work-tw-702b1a106e9e740afbb6dce7); [Newtalk report](https://newtalk.tw/news/view/2026-05-21/1036447)
- 禾羽's second physical photo book 《2026〈禾你相羽 in Okinawa〉寫真書》 already appears as a physical MuseBooks edition (`work-tw-d83d47417493a7a1f42f626e`); Kaboom is the direct product page. [MuseBooks record](https://musebooks.my/books/work-tw-d83d47417493a7a1f42f626e); [Kaboom product page](https://www.kaboom.tw/products/2026-kimi-in-okinawa-photo-book)
- 《芷想靠近你：劉芷伊醫師寫真》 is already present in the live catalog with physical and digital editions (`work-tw-0fe3296d84c633e5ab200c65`). [MuseBooks title query](https://musebooks.my/v1/books?q=%E8%8A%B7%E6%83%B3%E9%9D%A0%E8%BF%91%E4%BD%A0)
- 佳佳唱片 lists 《Play Bass Boy 聲景寫真輯》 by 博文/TTENG as released 2026-01-23, with a 92-page 170 × 260 mm photo book bundled with an NFC mini-album and random photo card; the sales page calls him a bassist and says it is a limited physical package. The item has barcode 5026854399287, not a stated book ISBN. [CCR product page](https://www.ccr.com.tw/goods/456171)
- MTV's release coverage calls 《Play Bass Boy》 博文's first photo-art book and describes him as a TRASH bassist. [MTV report](https://www.mtv.com.tw/news/newsdetail/13024)
- Live exact-name searches for 博文 and Play Bass Boy returned zero MuseBooks records. [MuseBooks 博文 query](https://musebooks.my/v1/books?q=%E5%8D%9A%E6%96%87); [MuseBooks title query](https://musebooks.my/v1/books?q=Play%20Bass%20Boy)

### Inferences
- The MuseBooks entries for 邊荷律, 禾羽 and 劉芷伊 make further imports duplicates, even where their newest book appeared after older catalog snapshots.
- 博文's work is a standalone personal photo book inside a multimedia package, but the musician/artist evidence alone does not establish influencer or online-creator fit. Do not import unless the scope is broadened to musicians/entertainers; if later included, record the photo book itself as the physical edition, not the NFC bundle as another book.

### Gaps
- For 博文, no primary bibliographic ISBN or separately documented final cover was found in the reviewed product listing; the page's product imagery is described as illustrative and the offer is currently out of stock.
- No new importer action was taken in this research note.

## Overall recommendation

### Takeaway
One well-supported older physical book, 阿古's 《Self：A-KU寫真》, appears absent from both the current catalog file and the live API. It is the best next addition if its displayed final cover can be retrieved and checked; the other recent candidates are duplicates or outside the requested creator scope.

### Cited Findings
- The duplicate checks above queried both creator and exact title/ISBN endpoints in the live catalog and checked the local Taiwan photobook catalog.
- Round 7 and 8 already document continuing holds such as 《韓你菲》 and 《FOUR》; this physical search pass did not resolve those trails. [Round 7 report](../../reports/Taiwan%20influencer%20photobook%20leads%207.md); [Round 8 report](../../reports/Taiwan%20influencer%20photobook%20leads%208.md)

### Inferences
- Given the out-of-print retailer status, any catalog addition would be archival; record current price/stock only if an active listing is separately found.

### Gaps
- Cover-file retrieval and resolution of page-count conflict remain the gating checks for 阿古.
