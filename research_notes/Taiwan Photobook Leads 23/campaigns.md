# Taiwan Creator-Owned Stores and Crowdfunding

## Did any new campaign book clear the import gate?

### Takeaway

**GO — 《Loop：晏人物攝影集》**, a physical, photographer-led group photobook that features Taiwanese Instagram creator 黃景. The official campaign specifies the book, and its shipping update both confirms dispatch and shows the finished, title-bearing physical cover. Live MuseBooks title searches returned no matching record. The cover evidence is an official product photograph of the book rather than a standalone flat scan; it still shows the final physical cover clearly enough to identify the edition.

### Cited Findings

- The official Zeczec campaign was successful on 2024-10-20 and sold a limited add-on edition named 《Loop：晏人物攝影集》, separate from its 2025 calendar. The book is specified as a 128-page, lay-flat physical photo book measuring 18 × 25.6 cm and containing all seven models' photos. [Official campaign, product details](https://www.zeczec.com/projects/loop-2005)
- The campaign names 黃景 among the seven models featured in the project and states that the photobook collects the seven models' photographs. [Official campaign, model list and photobook description](https://www.zeczec.com/projects/loop-2005)
- The campaign's 2024-12-13 update says the 《Loop》 calendar/book package had begun shipping. It explains that the physical book's original cover was reprinted due to color and finishing problems, and shows the finished item with 《Loop》 visible on the book cover. In this research check, the official update image downloaded successfully at 572,658 bytes; SHA-256 `5DF4918901C08C2AA33EC11FC5FFE75626927366FD0C7C39C3B79B11347ED11D`. [Official shipping update](https://www.zeczec.com/projects/loop-2005/updates/48979); [official final-product photo](https://assets.zeczec.com/asset_913856_image_big.jpg?1733981411=)
- A Taiwanese news report calls 黃景 an Instagram star, reports nearly 100,000 Instagram followers at the time, and identifies him as from Kaohsiung. This links Taiwan origin and influencer status to a model explicitly named in the book campaign. [臺灣人民報 profile of 黃景](https://www.peponews.tw/2020/01/07/66692/)
- The live MuseBooks API returned `total: 0` for the exact title query `Loop：晏人物攝影集` and a second query for `Loop：晏人物`. The local Taiwan photobook catalog also has no `Loop` entry. [MuseBooks exact-title query](https://musebooks.my/v1/books?q=Loop%EF%BC%9A%E6%99%8F%E4%BA%BA%E7%89%A9%E6%94%9D%E5%BD%B1%E9%9B%86&pageSize=50); [MuseBooks creator/title query](https://musebooks.my/v1/books?q=Loop%EF%BC%9A%E6%99%8F%E4%BA%BA%E7%89%A9&pageSize=50); [local catalog](../../scraper/taiwan-photobook-catalog.md)

### Inferences

- **GO for a shared photobook record featuring 黃景.** This is not 黃景's personal book; it is a seven-model anthology made by the photographer brand 晏人物. The catalog already contains shared/group photobooks, and the official seller page links 黃景 to this exact physical title. Record only the featured creators whose identities and Taiwan connection are verified; this pass verified 黃景, not the Taiwan origin of every other model. [Official campaign](https://www.zeczec.com/projects/loop-2005); [Taiwan-origin/influencer evidence](https://www.peponews.tw/2020/01/07/66692/)
- The seller's final-book photograph is a product photo rather than an isolated cover scan. The image visibly documents the final printed cover after the campaign's stated reprint; retain its source URL and provenance if using it as the cover image. [Final-product photo and update](https://www.zeczec.com/projects/loop-2005/updates/48979)

### Gaps

- The publisher does not provide a standalone flat image file for the final 《Loop》 cover in the cited update. The final cover is visible on the actual book in the official shipment photograph. [Official final-product photo](https://assets.zeczec.com/asset_913856_image_big.jpg?1733981411=)
- The campaign does not establish Taiwan origin for all seven models. 黃景 is the subject for whom this pass found explicit Taiwan-origin and influencer evidence; do not infer the same status for the full roster. [Official model list](https://www.zeczec.com/projects/loop-2005); [黃景 source](https://www.peponews.tw/2020/01/07/66692/)

## Which other fresh campaign lead remains below the import threshold?

### Takeaway

**HOLD — 娜娜美食寫真集.** The creator campaign verifies a real physical photobook project and shows substantial audience reach, but its own progress log records a shooting/shipping delay, and this pass found no current delivery confirmation, final cover, or reliable source for the model's Taiwan origin. The live MuseBooks title query returned no match.

### Cited Findings

- The official Zeczec project names “Nana 娜娜,” describes a physical A4 photo book with an estimated 80–100 pages, and says she had 600,000 Facebook followers at the campaign time. It funded successfully in July 2021. The page's delivery estimate was September 2021 and lists a later update titled “疫情因素寫真延期拍攝延期發送.” [Official Nana campaign and progress log](https://www.zeczec.com/projects/nana-xie-zhen)
- The same project describes the book as including food, photos, and personal writing, and lists the model as 娜娜. The available campaign material does not establish a final printed cover or confirm that delivery subsequently occurred. [Official campaign](https://www.zeczec.com/projects/nana-xie-zhen)
- The live MuseBooks API returned `total: 0` for `娜娜美食寫真集`. [MuseBooks title query](https://musebooks.my/v1/books?q=%E5%A8%9C%E5%A8%9C%E7%BE%8E%E9%A3%9F%E5%AF%AB%E7%9C%9F%E9%9B%86&pageSize=50)

### Inferences

- The campaign supports that a physical photobook was planned and crowdfunded, but the visible page does not close the edition's fulfillment and final-cover gaps. A successful fundraiser and a stale estimated delivery date do not prove a shipped book. [Official campaign and delay update listing](https://www.zeczec.com/projects/nana-xie-zhen)
- The campaign is Taiwan-facing and discusses life in Taiwan, but that does not establish that Nana herself is Taiwan-origin. Hold pending an authoritative creator-origin source and final product evidence. [Official campaign](https://www.zeczec.com/projects/nana-xie-zhen)

### Gaps

- No independently verifiable fulfillment notice or image of the finished 《娜娜美食寫真集》 was found in this pass. The official campaign page's listed 2021 delay is the last accessible fulfillment signal. [Official campaign](https://www.zeczec.com/projects/nana-xie-zhen)
- The project does not provide a final, title-specific book cover, ISBN, or confirmed finished pagination beyond its provisional 80–100-page specification. [Official campaign](https://www.zeczec.com/projects/nana-xie-zhen)
- No reliable source found in this pass identifies Nana's Taiwan birthplace or nationality; high follower count and Taiwan-based content alone are insufficient to establish Taiwan origin. [Official campaign](https://www.zeczec.com/projects/nana-xie-zhen)

## Which apparent discoveries resolve to existing catalog items?

### Takeaway

The checked names 《甄情萬種》, 《天使芯》, and 《SECRET：游泳教練寫真書》 are existing MuseBooks/catalog records, not new imports. No R2, database, or catalog writes were made by this research subtask.

### Cited Findings

- The live MuseBooks API returned one matching work each for `甄情萬種` and `天使芯`; the local master catalog also lists both titles. [MuseBooks query: 甄情萬種](https://musebooks.my/v1/books?q=%E7%94%84%E6%83%85%E8%90%AC%E7%A8%AE&pageSize=50); [MuseBooks query: 天使芯](https://musebooks.my/v1/books?q=%E5%A4%A9%E4%BD%BF%E8%8A%AF&pageSize=50); [local catalog](../../scraper/taiwan-photobook-catalog.md)
- MuseBooks has a live work page for Yilianboy's 《SECRET：游泳教練寫真書》, explicitly listing physical and digital editions. The local catalog also already contains Yilian's 《你的藍色不是我的藍色》. [MuseBooks SECRET work](https://musebooks.my/books/work-tw-197cc6785d521e1a26f13ee5); [local catalog](../../scraper/taiwan-photobook-catalog.md)

### Inferences

- These duplicate checks were read-only. They do not create a second work or edition. The only GO item from this campaign sweep is the separate 《Loop：晏人物攝影集》 group photobook described above.

### Gaps

- None for duplicate classification; live API and local catalog evidence agree that these titles are already present.

## Focused follow-up: final cover and fulfillment evidence for Loop

**Import recommendation: GO, using the official shipping-update photograph as a clearly labeled cropped cover image with its original source URL retained.** I found no standalone, high-resolution flat image of the final cover on the official campaign or its update. The campaign's pre-shipment product visuals are explicitly described as illustrative and may differ from the physical item. The 2024-12-13 official update instead shows the finished book in a product-set photograph. In the 1131 × 960 source image, the front of the top-center copy is fully visible: its large “Loop” title and cover portrait are unambiguous. A crop around that copy is technically usable as a catalog cover thumbnail, though the book is photographed at an angle and the crop is not a flat cover scan; keep the original image as provenance and do not represent it as standalone artwork.

The item photographed is the actual 128-page, 18 × 25.6 cm limited photobook add-on described in the campaign. The official update says the calendar campaign had begun shipping, specifically explains that people who bought the photo book would receive its original jacket plus a separately printed replacement jacket, and shows the physical book during that shipment update. This verifies production and dispatch of this edition at campaign level, though comments also show some individual supporters were still waiting for their parcels. Sources: [official campaign product details and reward tiers](https://www.zeczec.com/projects/loop-2005), [official shipping and jacket update](https://www.zeczec.com/projects/loop-2005/updates/48979), and [official product-set photograph](https://assets.zeczec.com/asset_913856_image_big.jpg?1733981411=).
