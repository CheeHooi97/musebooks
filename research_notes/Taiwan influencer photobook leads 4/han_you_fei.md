# 《韓你菲》 by 菲菲／李恩菲

## Did this exact book go on sale or ship, and where was it sold?

### Takeaway
The book is a credible physical-photobook release, and a preorder call to action was still present in a third-party snapshot of 菲菲’s Instagram bio on 2026-10-17. I could not recover the linked order destination or verify that orders were fulfilled or copies shipped.

### Cited Findings
- UDN reported on 2026-08-31 that 菲菲／李恩菲’s first solo physical photobook was titled 《韓你菲》 and was scheduled to go on sale on 2026-09-02 at 8 p.m.; the report directed readers to her official social channels for selling details. [UDN report](https://stars.udn.com/star/story/10089/9724294)
- FTV’s 2026-08-31 report independently gives the same planned launch time and says sale details would be announced through 菲菲’s official social channels. This confirms the planned release, not completed transactions or shipment. [FTV report](https://www.ftvnews.com.tw/news/detail/2026831W0260)
- A third-party Instagram profile snapshot, marked updated 2026-10-17, displays the bio text “韓你菲寫真書💖🛒預購連結🔗⬇️” and links to the creator’s `@aviva_1028` Instagram profile. The snapshot does not expose the preorder URL itself. [Kolr profile snapshot](https://www.kolr.ai/influencer/a7c5f083-7e76-46ad-8b53-e6ca47e18ea9); [Instagram profile](https://www.instagram.com/aviva_1028/)
- The Shopee search result for 李恩菲 showed a third-party listing snippet: “全新預購。10月底前出貨》 《韓你菲》在釜山等日落。李恩菲Aviva第一本個人實體寫真《韓你菲》終於來了！” at NT$1,380, with a seller location shown as Taipei’s Da’an District. The page is a search-results URL, not the seller’s item page, so seller identity, exact item URL, stock, and fulfillment are unverified. [Shopee search results for 李恩菲](https://shopee.tw/search?keyword=%E6%9D%8E%E6%81%A9%E8%8F%B2)

### Inferences
- The scheduled 2026-09-02 opening and the later Instagram-bio preorder prompt plus matching Shopee preorder snippet make an actual preorder campaign likely; they do not prove that the creator’s linked store accepted paid orders or shipped copies.

### Gaps
- No primary creator post or recoverable official profile link target was found for the order page.
- No direct seller item page was recovered. The third-party snippet’s “10月底前出貨” is a promised shipping window, not evidence that shipment occurred by 2026-10-30.

## What edition metadata and cover can be verified?

### Takeaway
The available sources establish a first solo physical photobook and its title, but do not supply publisher, ISBN/EAN, page count, or a direct product page. I found promotional photos of 李恩菲, but no image explicitly identified as the finished cover.

### Cited Findings
- UDN identifies 《韓你菲》 as her first solo physical photobook and says the photoshoot took place in Busan; its image caption credits 杰斯汀整合行銷 and calls the image a photo of 李恩菲’s personal photobook, without labeling it as a book cover. [UDN report](https://stars.udn.com/star/story/10089/9724294)
- FTV likewise identifies the announced item as a physical photobook and describes the Busan shoot, but gives no publisher, ISBN, barcode, page count, final cover, or seller URL. [FTV report](https://www.ftvnews.com.tw/news/detail/2026831W0260)
- The Shopee search snippet calls it 李恩菲／Aviva’s first personal physical photobook and uses “《韓你菲》在釜山等日落” in its title copy, but the search page does not establish whether that phrase is a subtitle or a seller-added description. [Shopee search results for 李恩菲](https://shopee.tw/search?keyword=%E6%9D%8E%E6%81%A9%E8%8F%B2)

### Inferences
- The press-photo caption and reportage image are promotional material; without a direct listing or a photo visibly and explicitly presented as the book’s front cover, they should not be imported as cover art.
- “在釜山等日落” may be sales copy or a subtitle, but the source available is only a Shopee search snippet; preserve 《韓你菲》 as the only verified title form.

### Gaps
- Publisher/imprint, ISBN/EAN, publication date, page count, physical specifications, price from an official seller, cover asset URL, and direct sales listing remain unknown.

## Does the local catalog or live MuseBooks API already contain it?

### Takeaway
The local Taiwan catalog has several earlier 李恩菲 editions, but no 《韓你菲》 row. The live title query returns zero matches, while the live creator-name query returns four existing works; do not confuse those older editions with this 2026 release.

### Cited Findings
- The local catalog section `## 李恩菲` lists the Japanese-language digital photobook, 《菲你莫屬》, 《菲進你心》, and 《bestie閨蜜》 editions, with no 《韓你菲》 row. [Taiwan photobook catalog](../../scraper/taiwan-photobook-catalog.md)
- The public API query `q=韓你菲` returned `total: 0`. [MuseBooks title query](https://musebooks.my/v1/books?q=%E9%9F%93%E4%BD%A0%E8%8F%B2)
- The public API query `q=李恩菲` returned four existing works: `work-tw-251bb59b48293b06776ca8fe` (台湾グラドルYuYu 1stデジタル写真集「君だけのYuYu」), `work-tw-bb29c83f5cf348d07ac7150b` (菲你莫屬-菲菲數位寫真書-中文版), `work-tw-b308cbd8292f131b7cf48caf` (bestie閨蜜：孟潔×菲菲寫真, with physical and digital editions), and `work-tw-6e753ec264a9dee85a990bb1` (菲進你心 菲菲個人數位寫真（含影音）). None is titled 《韓你菲》. [MuseBooks creator-name query](https://musebooks.my/v1/books?q=%E6%9D%8E%E6%81%A9%E8%8F%B2)

### Inferences
- The new release would be a separate physical work if a seller or publisher page later confirms its edition details and cover; it should not be merged into the existing digital works solely because the featured person is the same.

### Gaps
- The API title query is text search and does not prove no alternate-title record exists under another spelling or creator alias. The local catalog and creator-name results show no apparent duplicate, but source-level matching should be repeated if a direct listing is recovered.
