# Round 19 physical retail sweep — Taiwan creator photobooks

Checked 2026-10-30 (Asia/Singapore). No DB, R2, or scraper-catalog writes.

## Strongest recent physical candidate: 《三倍心跳》

### Takeaway
The publisher confirms a current physical photobook set, but the live catalog already contains it. No new import qualifies.

### Cited Findings
- 小蜂光 Bee3Shine lists 《三倍心跳》梓梓×林莎×元元 限量三人寫真套組 at NT$2,999 with stock available and a first-wave signed-board edition. Its page omits ISBN, page count, dimensions, and publication/dispatch date. [Official seller page](https://bee3shine.com/product/%E3%80%8A%E4%B8%89%E5%80%8D%E5%BF%83%E8%B7%B3%E3%80%8B%E6%A2%93%E6%A2%93x%E6%9E%97%E8%8E%8Ex%E5%85%83%E5%85%83-%E9%99%90%E9%87%8F%E4%B8%89%E4%BA%BA%E5%AF%AB%E7%9C%9F%E5%A5%97%E7%B5%84/)
- Subject identities connect to Taiwan’s creator/entertainment scene: Lin Sha is profiled as a Taiwanese model and YouTuber; 梓梓’s profile documents her work in Taiwanese performance and cheerleading; 元元 is identified as a Taiwanese entertainer. [Lin Sha](https://zh.wikipedia.org/wiki/%E6%9E%97%E8%8E%8E), [梓梓](https://cheeronair.com/zh-Hant/people/p-%E6%A2%93%E6%A2%93), [元元](https://www.ttshow.tw/celebrity/%E5%85%83%E5%85%83)
- The title-specific image `https://bee3shine.com/wp-content/uploads/2026/06/%E5%AF%AB%E7%9C%9F%E6%9B%B8-1080x1350-1.png` fetched successfully (HTTP 200, 535,787 bytes; SHA-256 `3119a0c6b1b86ada4e9168715964b8bbacb9bcb976339bd01252c8b710c5a6a0`). It is labeled as a book product image, but the seller does not identify it as final cover art. [Publisher image](https://bee3shine.com/wp-content/uploads/2026/06/%E5%AF%AB%E7%9C%9F%E6%9B%B8-1080x1350-1.png)
- The live API query returns one matching work, `work-tw-96926b38696ba73e299897d0`, with physical edition `edition-2aacde30ca082f374c8041ab`; the API record already has a stored cover URL. [Live API query](https://musebooks.my/v1/books?q=%E4%B8%89%E5%80%8D%E5%BF%83%E8%B7%B3), [existing record](https://musebooks.my/books/work-tw-96926b38696ba73e299897d0)

### Inferences
- This is a Taiwanese creator group photobook set, but available evidence does not say whether it contains one book or multiple volumes. Keep the seller’s “set” description.

### Gaps
- Final cover status and the missing bibliographic fields are unresolved; because the work and cover are already in MuseBooks, no second import or R2 upload is warranted.

## Cross-check: *Babe Fantasy‧寶兒寫真書*

### Takeaway
This is a fully specified physical book with a retrievable cover, but it is also already cataloged.

### Cited Findings
- 城邦’s storefront lists Bao (吳昀廷), publication 2025-12-09, ISBN 9786267683798, paperback, 160 pages, 18.5 × 26 cm, and NT$650. Its author bio connects Bao to Taiwanese girl group Popu Lady and Fubon Angels. [Publisher storefront](https://www.cite.com.tw/book?id=105737)
- The National Central Library bibliography independently records the print ISBN, 160 pages, 26 cm, and NT$650. [NCL bibliography](https://isbn.ncl.edu.tw/FCKEDITOR_UploadFiles/1760932966.pdf)
- Cover image `https://d4dpzjhk0g50s.cloudfront.net/images/2/2AB325.jpg` fetched with the storefront Referer (HTTP 200, 49,707 bytes; SHA-256 `9b3bd2cbfea26052ec6272862cf847a8101d1c4134533fc0e73ec55940f6f2ed`). [Cover image](https://d4dpzjhk0g50s.cloudfront.net/images/2/2AB325.jpg)
- Live API title query returned one work, `work-tw-6bfdeef40b49b66040c85d2e`, with physical edition `edition-b2a9959454f98bae93952c9f` (ISBN 9786267683798) and digital edition `edition-e641bc1592a1c564d82b937b` (ISBN 9786267683781). [Live API query](https://musebooks.my/v1/books?q=%E5%AF%B6%E5%85%92)

### Inferences
- The verified physical cover is evidence for the existing book only; do not create a duplicate edition or upload a second image.

### Gaps
- No additional in-scope uncatalogued physical title cleared direct-product, creator-origin, duplicate, and cover checks in this sweep.

## Decision

### Takeaway
HOLD for new imports: both strongest candidates are duplicates. Leave MuseBooks DB and R2 unchanged.

### Cited Findings
- Exact live API queries returned the existing work and edition IDs for both titles. [《三倍心跳》](https://musebooks.my/v1/books?q=%E4%B8%89%E5%80%8D%E5%BF%83%E8%B7%B3), [*Babe Fantasy*](https://musebooks.my/v1/books?q=%E5%AF%B6%E5%85%92)

### Inferences
- Revisit only if a distinct new edition is published or the seller supplies final book specifications for a genuinely missing catalog record.

### Gaps
- This sweep was limited to physical retail; digital products and campaign-only offers were outside scope.
