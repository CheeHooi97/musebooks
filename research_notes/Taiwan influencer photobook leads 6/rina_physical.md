# Rina 謝艾娜《盛夏・謝艾娜》 physical edition

## Does an in-scope Taiwan creator have a directly listed physical book that is actually on sale?

### Takeaway

Yes. A Taiwan marketplace seller now has a direct, active “現貨” product listing dated 2026-09-29, after the August preorder period; the listing shows one remaining unit as of the 2026-10-30 check. This establishes an actual retail offer, though not a completed sale or shipment. [Ruten seller listing](https://www.ruten.com.tw/item/22640770348621/); [CTi News report](https://ctinews.com/news/items/4bnbjEjDnP)

### Cited Findings

- CTi News identifies Rina 謝艾娜 as having just joined the Taoyuan Cloud Leopard Flyers’ 桃氣女孩 in Taiwan’s professional volleyball league, and identifies 《盛夏・謝艾娜》 as her first personal physical photobook. Its 2026-08-17 report says preorders were scheduled for 2026-08-19 through 2026-08-31. [CTi News report](https://ctinews.com/news/items/4bnbjEjDnP)
- The direct Ruten item is titled “「星空小舖」（現貨）《盛夏 •謝艾娜》寫真書 精裝書盒 人形立牌 精選明信片（酷卡）”; its item data gives seller 星空小舖, listing time 2026-09-29 01:14:46, last price update 2026-10-03 19:08:26, one remaining unit, and zero sold. The listing was still active and marked 現貨 when checked on 2026-10-30. [Ruten seller listing](https://www.ruten.com.tw/item/22640770348621/)
- The seller listing describes physical options including a hardcover book and boxed set; the listing date and stock state are post-preorder on-sale evidence. [Ruten seller listing](https://www.ruten.com.tw/item/22640770348621/)

### Inferences

- This is the first located evidence that the physical book reached an active retail offer after the campaign’s preorder window. The listing is from a marketplace seller, not a publisher or confirmed official shop, so it does not establish the publisher or primary sales channel. [Ruten seller listing](https://www.ruten.com.tw/item/22640770348621/); [CTi News report](https://ctinews.com/news/items/4bnbjEjDnP)

### Gaps

- The seller listing shows an available unit and `soldNum: 0`; I found no completed customer transaction, receipt, or shipment confirmation. This is a remaining shipment gap, not a gap in evidence that the book was put on sale. [Ruten seller listing](https://www.ruten.com.tw/item/22640770348621/)

## What bibliographic fields and catalog/API records are available?

### Takeaway

The direct seller record confirms the physical title and product, but leaves publisher/imprint, ISBN/EAN, and page count unreported. The local catalog and live MuseBooks API still have only Rina’s older digital book, not this physical edition. [Ruten seller listing](https://www.ruten.com.tw/item/22640770348621/); [local Taiwan photobook catalog](../../scraper/taiwan-photobook-catalog.md); [MuseBooks exact-title query](https://musebooks.my/v1/books?q=%E7%9B%9B%E5%A4%8F%E3%83%BB%E8%AC%9D%E8%89%BE%E5%A8%9C)

### Cited Findings

- The Ruten page’s item data has an empty ISBN field and does not state a publisher or page count. I found no EAN either. [Ruten seller listing](https://www.ruten.com.tw/item/22640770348621/)
- The checked local catalog section for 謝艾娜 contains only 《娜就愛吧 謝艾娜Rina數位寫真》 (digital ISBN 9786263777200); it has no physical 《盛夏・謝艾娜》 entry. [Local Taiwan photobook catalog](../../scraper/taiwan-photobook-catalog.md)
- Live API queries for the exact title, the same title without the middle dot, and the creator name returned respectively 0, 0, and 1 result. The creator result is the older 2024 digital title, not the physical book. [MuseBooks exact-title query](https://musebooks.my/v1/books?q=%E7%9B%9B%E5%A4%8F%E3%83%BB%E8%AC%9D%E8%89%BE%E5%A8%9C); [MuseBooks no-dot title query](https://musebooks.my/v1/books?q=%E7%9B%9B%E5%A4%8F%E8%AC%9D%E8%89%BE%E5%A8%9C); [MuseBooks creator query](https://musebooks.my/v1/books?q=%E8%AC%9D%E8%89%BE%E5%A8%9C)
- The publisher’s page for the distinct older digital book identifies its format as an electronic publication and its listing date as 2024-02-14, further distinguishing it from the 2026 physical release. [Sharp Point digital-book page](https://www.espp.com.tw/ctn.aspx?bc=EAFB0092-001)

### Inferences

- An edition record can identify the supported medium as physical and use the campaign title; publisher, ISBN/EAN, and pagination should remain unknown unless the catalog permits blank fields. No evidence supports copying identifiers or pagination from the separate digital edition. [CTi News report](https://ctinews.com/news/items/4bnbjEjDnP); [Sharp Point digital-book page](https://www.espp.com.tw/ctn.aspx?bc=EAFB0092-001)

### Gaps

- Still missing: a publisher/imprint, ISBN or EAN, and page count from a publisher, official seller, library record, or explicit seller description. Public searches for the physical title surfaced the older digital publication and the Ruten listing, but no primary bibliographic record. [Ruten seller listing](https://www.ruten.com.tw/item/22640770348621/); [Sharp Point digital-book page](https://www.espp.com.tw/ctn.aspx?bc=EAFB0092-001)

## Does a seller-identified final cover image exist, and is there shipment proof?

### Takeaway

The Ruten seller’s own product gallery now supplies final-cover identification: its actual-product photo marks the book’s front and back as 正面 and 反面, and a separate product render shows the titled hardcover. These are seller-hosted product images, not campaign portraits; however, the front cover is shown in a product photo/render rather than as a clean, isolated cover scan. [Ruten front/back product photo](https://gcs.rimg.com.tw/g1/a/96/4d/22640770348621_306.jpg); [Ruten hardcover render](https://gcs.rimg.com.tw/g1/a/96/4d/22640770348621_366.jpg)

### Cited Findings

- The seller’s image `22640770348621_306.jpg` shows the physical book, with the cover side labeled 正面 and the reverse labeled 反面; the front bears the title 《盛夏・謝艾娜》. This is the clearest final-cover identification in the listing. [Ruten front/back product photo](https://gcs.rimg.com.tw/g1/a/96/4d/22640770348621_306.jpg)
- The seller’s image `22640770348621_366.jpg` shows the titled hardcover and box as a product render, while `22640770348621_328.jpg` shows the actual hardcover product with its front and reverse visible. [Ruten hardcover render](https://gcs.rimg.com.tw/g1/a/96/4d/22640770348621_366.jpg); [Ruten second product photo](https://gcs.rimg.com.tw/g1/a/96/4d/22640770348621_328.jpg)
- The direct item page still reports one remaining unit and zero units sold; that is compatible with an active offer but supplies no shipment or completed-purchase proof. [Ruten seller listing](https://www.ruten.com.tw/item/22640770348621/)

### Inferences

- The physical copy photo and cover render are enough to identify the final cover design for review, without substituting campaign portrait photography. They are not a standalone cover-file scan suitable for direct catalog cover use without cropping or further verification. [Ruten front/back product photo](https://gcs.rimg.com.tw/g1/a/96/4d/22640770348621_306.jpg); [Ruten hardcover render](https://gcs.rimg.com.tw/g1/a/96/4d/22640770348621_366.jpg)

### Gaps

- A standalone flat front-cover asset and shipment proof remain unavailable. The seller’s gallery contains sufficient visual evidence to identify the cover, but there is no separate image labeled as a clean cover-only file. [Ruten seller listing](https://www.ruten.com.tw/item/22640770348621/)
