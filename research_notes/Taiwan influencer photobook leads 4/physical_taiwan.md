# Physical Taiwan influencer photobook research

## Candidate and catalog reconciliation

### Takeaway

A verified physical edition of **《心存感恩：心恩做最好的自己真愛寫真》** is the strongest new physical-format lead. The local Taiwan catalog has no entry for this title, while the live MuseBooks record already has the same work as a single digital edition; the shared ISBN requires careful edition reconciliation before any import. ([local Taiwan catalog](../../scraper/taiwan-photobook-catalog.md); [live MuseBooks title query](https://musebooks.my/v1/books?q=%E5%BF%83%E5%AD%98%E6%84%9F%E6%81%A9&pageSize=5))

### Cited Findings

- MuseBooks currently returns work `work-tw-8b1823cc55eec939d9a91699`, titled **心存感恩：心恩做最好的自己真愛寫真**, credited to 廖心恩, with one **digital** edition sourced to Pubu, ISBN **9786263741645**, publication date **2023-09-01**, and metadata URL `https://www.pubu.com.tw/ebook/384436`. ([MuseBooks API title query](https://musebooks.my/v1/books?q=%E5%BF%83%E5%AD%98%E6%84%9F%E6%81%A9&pageSize=5); [Pubu ebook listing](https://www.pubu.com.tw/ebook/384436))
- Kingstone's current retail page labels the item a paper paperback and gives the exact title, author, 時報文化 publisher, **2023-09-05** publication date, and ISBN **9786263741645**. Its Open Graph cover image is [2019910050805b.jpg](https://assets.kingstone.com.tw/book/images/product/20199/2019910050805/2019910050805b.jpg); I downloaded and visually checked the image against the title. ([Kingstone physical listing](https://www.kingstone.com.tw/basic/2019910050805/))
- The National Central Library's ISBN record independently catalogs the first-edition paperback as **160 pages**, **26 cm**, by 廖心恩, published by 時報文化 in **2023-09**, with ISBN **9786263741645**. ([National Central Library new-book record](https://isbn.ncl.edu.tw/FCKEDITOR_UploadFiles/1692349219.pdf))
- The Kingstone physical listing image is not byte-identical to the live Pubu/R2 digital cover: the former is a three-dimensional paperback mockup (SHA-256 13c9a5bc84ee8e0e7fdf52daf9578a9da5525695144397faec52161d8fef3cbd), while the existing digital object is the matching flat cover artwork (SHA-256 17a55f75126f0795812998979defbfd3791333c36b0267b5b9344e7ae34f3de5). I downloaded and visually compared both; use the Kingstone asset if preserving the physical-format cover image. ([Kingstone cover asset](https://assets.kingstone.com.tw/book/images/product/20199/2019910050805/2019910050805b.jpg); [live MuseBooks title query](https://musebooks.my/v1/books?q=%E5%BF%83%E5%AD%98%E6%84%9F%E6%81%A9&pageSize=5))
- TAAZE has an active Chinese-book listing for the same physical title, author, publisher, date and ISBN; the product description says the author is from Kaohsiung and describes her as a DJ and member of 高雄鋼鐵人啦啦隊「鋼鐵女神雅典娜」. ([TAAZE listing and author bio](https://m.taaze.tw/do/mobile/single.aspx?pid=11101017284))

### Inferences

- This is a **new physical edition under an existing work**, not a new work candidate. The same ISBN is asserted for the existing digital edition by MuseBooks/Pubu and the paper edition by Kingstone/NCL, so the data should be reviewed for ISBN reuse or a format-classification issue before creating another edition record. ([MuseBooks API title query](https://musebooks.my/v1/books?q=%E5%BF%83%E5%AD%98%E6%84%9F%E6%81%A9&pageSize=5); [Kingstone physical listing](https://www.kingstone.com.tw/basic/2019910050805/); [National Central Library new-book record](https://isbn.ncl.edu.tw/FCKEDITOR_UploadFiles/1692349219.pdf))
- The Kingstone cover asset is a usable, identified product image: the retailer page itself names it as the `og:image`, and the downloaded image visibly bears the book title and author. ([Kingstone physical listing](https://www.kingstone.com.tw/basic/2019910050805/); [Kingstone cover asset](https://assets.kingstone.com.tw/book/images/product/20199/2019910050805/2019910050805b.jpg))

### Gaps

- I did not find a separate publisher-hosted page for the physical book; the NCL bibliographic record, Kingstone, and TAAZE independently establish the edition. ([National Central Library record](https://isbn.ncl.edu.tw/FCKEDITOR_UploadFiles/1692349219.pdf); [Kingstone listing](https://www.kingstone.com.tw/basic/2019910050805/); [TAAZE listing](https://m.taaze.tw/do/mobile/single.aspx?pid=11101017284))
- The common ISBN across formats is unresolved. Keep the live digital record and physical bibliographic evidence visible during reconciliation rather than silently changing the existing record. ([MuseBooks API title query](https://musebooks.my/v1/books?q=%E5%BF%83%E5%AD%98%E6%84%9F%E6%81%A9&pageSize=5); [National Central Library record](https://isbn.ncl.edu.tw/FCKEDITOR_UploadFiles/1692349219.pdf))

## Creator background and Taiwan connection

### Takeaway

廖心恩 / DJ Lighley fits a Taiwan creator and cheerleader scope: her own author biography identifies her as from Kaohsiung, and Taiwan sports reporting identifies her as an original member of the Kaohsiung Steelers' Athena Girls and a DJ. An older Yahoo report also records her public Instagram presence and more than 44,000 followers at that time. ([TAAZE author bio](https://m.taaze.tw/do/mobile/single.aspx?pid=11101017284); [Yahoo Taiwan Sports profile](https://tw.sports.yahoo.com/news/%E9%9B%85%E5%85%B8%E5%A8%9Cdj%E5%BF%83%E6%81%A9%E7%81%AB%E8%BE%A3%E9%96%8B%E5%A0%B4-%E9%B3%B3%E5%B1%B1%E4%B8%BB%E5%A0%B4%E8%AE%8A%E5%A4%9C%E5%BA%97-111704308.html); [Yahoo Taiwan profile on her Instagram reach](https://tw.news.yahoo.com/%E6%97%A5%E6%9C%88%E5%85%89%E8%BE%A3%E5%A6%B9%E6%AD%A3%E9%9D%A2%E7%85%A7%E6%9B%9D%E5%85%89-%E7%9C%9F%E5%AF%A6%E8%BA%AB%E5%88%86%E6%98%AF%E8%B6%85%E6%AD%A3dj-034200654.html))

### Cited Findings

- The TAAZE author biography says 廖心恩 is from Kaohsiung and works as a DJ and member of the Steel Girls Athena cheerleading squad. ([TAAZE listing and bio](https://m.taaze.tw/do/mobile/single.aspx?pid=11101017284))
- Yahoo Taiwan Sports reported in February 2023 that 心恩 was a founding member of the Steel Girls Athena, worked as a DJ, and performed regularly at venues and public events in Kaohsiung. ([Yahoo Taiwan Sports](https://tw.sports.yahoo.com/news/%E9%9B%85%E5%85%B8%E5%A8%9Cdj%E5%BF%83%E6%81%A9%E7%81%AB%E8%BE%A3%E9%96%8B%E5%A0%B4-%E9%B3%B3%E5%B1%B1%E4%B8%BB%E5%A0%B4%E8%AE%8A%E5%A4%9C%E5%BA%97-111704308.html))
- A separate Yahoo Taiwan article described 廖心恩 as a DJ/social-media personality and reported that her Instagram then had more than **44,000 followers**; this is a historical audience figure, not a current follower count. ([Yahoo Taiwan article](https://tw.news.yahoo.com/%E6%97%A5%E6%9C%88%E5%85%89%E8%BE%A3%E5%A6%B9%E6%AD%A3%E9%9D%A2%E7%85%A7%E6%9B%9D%E5%85%89-%E7%9C%9F%E5%AF%A6%E8%BA%AB%E5%88%86%E6%98%AF%E8%B6%85%E6%AD%A3dj-034200654.html))

### Inferences

- The source combination supports Taiwan origin/context and a creator/cheerleader/DJ classification; the follower count should not be presented as current. ([TAAZE author bio](https://m.taaze.tw/do/mobile/single.aspx?pid=11101017284); [Yahoo Taiwan Sports](https://tw.sports.yahoo.com/news/%E9%9B%85%E5%85%B8%E5%A8%9Cdj%E5%BF%83%E6%81%A9%E7%81%AB%E8%BE%A3%E9%96%8B%E5%A0%B4-%E9%B3%B3%E5%B1%B1%E4%B8%BB%E5%A0%B4%E8%AE%8A%E5%A4%9C%E5%BA%97-111704308.html))

### Gaps

- I did not verify a current social-platform follower count or a creator-owned post announcing this particular physical edition. ([TAAZE listing](https://m.taaze.tw/do/mobile/single.aspx?pid=11101017284); [Yahoo Taiwan Sports](https://tw.sports.yahoo.com/news/%E9%9B%85%E5%85%B8%E5%A8%9Cdj%E5%BF%83%E6%81%A9%E7%81%AB%E8%BE%A3%E9%96%8B%E5%A0%B4-%E9%B3%B3%E5%B1%B1%E4%B8%BB%E5%A0%B4%E8%AE%8A%E5%A4%9C%E5%BA%97-111704308.html))

## Other leads checked and coverage limits

### Takeaway

Search results for several other recent Taiwanese cheerleader photobooks led to records already present in the current catalog; I found no second new physical title with a complete product and creator evidence trail in this pass. The search was retailer/news-led and should not be treated as exhaustive. ([local Taiwan catalog](../../scraper/taiwan-photobook-catalog.md))

### Cited Findings

- Sanmin lists **FIRST JUMP：TOKKI CUTIE 臺北伊斯特啦啦隊寫真故事 2025-2026** as a 176-page boxed physical item with ISBN **9786267776919**, EZ叢書館 publisher and 2026-04-30 date; this item is already represented in the local Taiwan catalog, and the team's official announcement confirms its release. ([Sanmin listing](https://www.sanmin.com.tw/product/index/015309196); [TOKKI CUTIE official announcement](https://eastpower.tw/6177); [local Taiwan catalog](../../scraper/taiwan-photobook-catalog.md))
- **《微澀・微瑟》瑟七1st寫真書** is already present in the local catalog; Kingstone identifies it as her 2026 physical book. ([Kingstone listing](https://www.kingstone.com.tw/basic/2019590016177/); [local Taiwan catalog](../../scraper/taiwan-photobook-catalog.md))
- Search also surfaced 夏蕾's **《心動蕾達：夏蕾寫真》** and 彭彭's **《彭然心動：彭彭寫真》**; the local catalog already has their physical editions, so they are not additional candidates for this task. ([時報悅讀 official publisher listing for 夏蕾](https://www.readingtimes.com.tw/product/?pid=1VY0480); [城邦 listing for 彭彭](https://www.cite.com.tw/book?id=108961); [local Taiwan catalog](../../scraper/taiwan-photobook-catalog.md))

### Inferences

- The most practical next step is to reconcile the physical bibliographic evidence for 《心存感恩》 with the digital-only live record under the same work, and retain the direct Kingstone cover source for that review. ([Kingstone listing](https://www.kingstone.com.tw/basic/2019910050805/); [MuseBooks API title query](https://musebooks.my/v1/books?q=%E5%BF%83%E5%AD%98%E6%84%9F%E6%81%A9&pageSize=5))

### Gaps

- Retailer catalog search and the current 335-heading local list did not establish complete coverage of every Taiwan influencer, cheerleader, preorder, or small publisher release. ([local Taiwan catalog](../../scraper/taiwan-photobook-catalog.md); [Sanmin photobook search](https://www.sanmin.com.tw/search?k=%E5%AF%AB%E7%9C%9F%E6%9B%B8&ls=ed&pt=t))