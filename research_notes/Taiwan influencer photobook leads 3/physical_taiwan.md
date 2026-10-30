# Uncatalogued Taiwan creator physical photobooks

## Does a new creator meet the Taiwan influencer scope?

### Takeaway
瑀熙（Yuci）is a strong in-scope, previously uncatalogued creator: retailer metadata identifies her Twitch game-streaming and YouTube work, while Taiwanese news coverage describes her as a popular influencer and YouTuber. Her first-person introduction says she started streaming on Twitch in 2015 and began a YouTube lifestyle channel in 2019. ([Kingstone listing](https://www.kingstone.com.tw/basic/2019910049946/); [TVBS profile](https://news.tvbs.com.tw/entertainment/2434263))

### Cited Findings
- The Kingstone author biography says 瑀熙（Yuci）started streaming games on Twitch in 2015 and began a YouTube lifestyle channel in 2019. ([Kingstone listing](https://www.kingstone.com.tw/basic/2019910049946/))
- TVBS describes her as a game-streamer-turned influencer/YouTuber and reports that her Instagram had about one million followers at the time of its March 2024 article. ([TVBS profile](https://news.tvbs.com.tw/entertainment/2434263))
- The National Central Library deposit record lists 瑀熙 as the author of 《只想瑀你初體驗 = miss you photobook》 under 水靈文創, with planned publication month 2023-02 and paperback binding. ([NCL deposit list](https://nclfile.ncl.edu.tw/files/202307/27cfb872-5f11-473e-8173-f00dfe5d7ca7.pdf))
- I checked the creator headings and ISBN/title strings in the current Taiwan catalog and the previous research report; 瑀熙 and ISBN 9786269709908 do not appear there. The book is therefore a new candidate for the existing catalog rather than a duplicate of an already recorded creator/title.

### Inferences
- Her long-running Taiwan-facing streaming and YouTube activity, combined with her Taiwan-published book, makes this a sound match for the requested Taiwan influencer scope. This classification is an inference from her creator work and Taiwan publication context, not a nationality claim.

### Gaps
- I found no authoritative biography explicitly stating 瑀熙’s nationality; the evidence confirms her creator platforms, Taiwan-based publisher and Taiwan book release, which is sufficient for Taiwan-market inclusion but not to assert nationality.

## What physical edition and cover can be verified?

### Takeaway
《只想瑀你．初體驗 miss you photobook》 is a verified physical paperback by 瑀熙, published by 水靈文創, ISBN 9786269709908, with 160 pages. Kingstone’s item gallery exposes a primary product image asset that appears to be the cover. Retailers disagree on the exact day of release, so leave the date unresolved pending the catalog owner’s date policy. ([Kingstone listing](https://www.kingstone.com.tw/basic/2019910049946/); [Sanmin listing](https://www.sanmin.com.tw/product/index/011520713); [Kingstone cover asset](https://cdn.kingstone.com.tw/book/images/product/20199/2019910049946/2019910049946b.jpg))

### Cited Findings
- Kingstone lists the physical item as 《只想瑀你．初體驗 miss you photobook》, by 瑀熙 and published by 水靈文創; it identifies paperback format, ISBN 9786269709908, 160 pages, and Taiwan as place of publication. ([Kingstone listing](https://www.kingstone.com.tw/basic/2019910049946/))
- Sanmin independently lists the same title, author, publisher, ISBN 9786269709908, paperback binding, 160 pages, and dimensions 26 × 18.5 × 1 cm. ([Sanmin listing](https://www.sanmin.com.tw/product/index/011520713))
- Release dates conflict: Kingstone records 2023-02-24, while Sanmin records 2023-03-06. The NCL deposit record gives only the planned month, 2023-02, so it does not resolve the day-level difference. ([Kingstone listing](https://www.kingstone.com.tw/basic/2019910049946/); [Sanmin listing](https://www.sanmin.com.tw/product/index/011520713); [NCL deposit list](https://nclfile.ncl.edu.tw/files/202307/27cfb872-5f11-473e-8173-f00dfe5d7ca7.pdf))
- The first product-gallery image linked from Kingstone’s listing resolves to `https://cdn.kingstone.com.tw/book/images/product/20199/2019910049946/2019910049946b.jpg`; this is the direct retailer asset to use for the cover. The web fetch interface exposed the URL but returned a cache-miss when opening the image, so I did not hash or independently inspect the downloaded bytes. ([Kingstone listing](https://www.kingstone.com.tw/basic/2019910049946/); [Kingstone cover asset](https://cdn.kingstone.com.tw/book/images/product/20199/2019910049946/2019910049946b.jpg))
- An additional article image promotes the book and visibly carries its title and 瑀熙’s name, but it is a press/promo image rather than stronger evidence of the final printed cover. ([SiCAR article image](https://api.sicar.com.tw/public/uploads/ori/article/2023/02/20230215170054104846605.jpeg))

### Inferences
- The common ISBN, author, publisher, page count, and binding make this a single physical edition despite the date discrepancy. For import, preserve the ISBN and page count; keep the release date null or explicitly adjudicate the two retailer dates rather than silently choosing one.
- The linked Kingstone gallery asset is the best available direct cover source because it is attached to the item’s official retailer gallery; byte-level image verification remains outstanding.

### Gaps
- Exact publication day remains unresolved (2023-02-24 at Kingstone versus 2023-03-06 at Sanmin).
- No standalone publisher product page was recovered. The bibliographic record is cross-supported by the National Central Library deposit list and multiple bookseller pages.
- The cover image URL is identified from Kingstone’s product gallery, but the current web retrieval path could not render it because of a cache miss; download and verify the actual image before any R2 upload.