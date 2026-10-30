# Taiwan creator digital photobook candidate — Round 18 (checked 2026-10-30)

## Which current digital lead is closest to import-ready, and does a new one clear all gates?

### Takeaway
No new digital title clears import this round. The strongest live campaign lead is ADAM 林冠宇’s 《FOUR》: the creator’s campaign explicitly describes a Taiwan actor’s first pure digital photobook and offers a PDF reward, but the campaign is still open and will deliver the file after production; the page does not establish a final title-matched ebook cover. Keep it **HOLD**. A separate fresh Pubu discovery, 劉淇’s 《SOAKING WET》, has verifiable product and cover evidence but is already in MuseBooks as one work with two digital editions, so it is a **DUPLICATE**.

### Cited Findings
- ADAM’s direct Zeczec campaign identifies the creator as 林冠宇, calls 《FOUR》 his first electronic photo book and fourth book, and describes its contents as photographs only. The same page describes him as a “Taiwan emerging actor” and links his Facebook and Instagram accounts. [Zeczec project](https://www.zeczec.com/projects/ADAM2026)
- The Zeczec campaign is active through 2026-11-12. Its “看見《FOUR》” reward is pure digital and lists one electronic photobook, NT$780, with expected realization in December 2026. [Zeczec project](https://www.zeczec.com/projects/ADAM2026)
- The official FAQ says the product is a PDF, and that access information will be provided only after fundraising ends and production is complete; it also says the PDF will be encrypted. Thus, on the check date the final digital file was not available for inspection. [Zeczec FAQ](https://www.zeczec.com/projects/ADAM2026/faqs)
- The campaign page displays promotional photos, but the project warns that displayed imagery/design for the reward photos and physical collectibles is illustrative and may differ from the final production. I found no product-specific statement identifying a final ebook jacket or cover image. [Zeczec project](https://www.zeczec.com/projects/ADAM2026)
- Live MuseBooks API query `q=林冠宇` returned 0 items. Query `q=FOUR` returned one unrelated Korean work, *MAXQ Special Edition 3호*, so the campaign title is not an exact duplicate in the live catalog. [MuseBooks 林冠宇 query](https://musebooks.my/v1/books?q=%E6%9E%97%E5%86%A0%E5%AE%87); [MuseBooks FOUR query](https://musebooks.my/v1/books?q=FOUR)
- Decision for 《FOUR》: **HOLD**, pending campaign fulfillment and a verifiable final cover/product image. The direct campaign and creator-origin context are strong, but current delivery and final-cover evidence do not meet the import bar. [Zeczec project](https://www.zeczec.com/projects/ADAM2026); [Zeczec FAQ](https://www.zeczec.com/projects/ADAM2026/faqs)

### Inferences
- Treat 《FOUR》 as a forthcoming digital photobook preorder, not a currently available ebook edition, until the campaign provides the promised PDF after production. [Zeczec FAQ](https://www.zeczec.com/projects/ADAM2026/faqs)

### Gaps
- No final ebook file, page count, ISBN/EISBN, or final title-matched cover could be verified from the campaign materials on 2026-10-30. [Zeczec project](https://www.zeczec.com/projects/ADAM2026); [Zeczec FAQ](https://www.zeczec.com/projects/ADAM2026/faqs)

## What did the newly surfaced Pubu digital title show on duplicate and cover checks?

### Takeaway
Pubu’s 《濕樂園：劉淇《SOAKING WET》寫真書》 has two live digital formats and a working title cover, but MuseBooks already contains the same work and both editions. Do not create another record or upload another cover (**DUPLICATE**).

### Cited Findings
- Pubu product 686437 identifies the Traditional Chinese PDF ebook, dated 2026-08-06, 106 pages, 31 MB, NT$499, and its subject/title. [Pubu product 686437](https://www.pubu.com.tw/magazine/686437)
- Pubu’s product image `2SyinL_xl.jpg` returned HTTP 200 as `image/jpeg`, 921,957 bytes, SHA-256 `c07c95551f7e282086e03cd8ca0e6f79cb33ef3a3bb9e75a6432e8a497e1a090` on 2026-10-30. [Pubu product cover](https://res1.pubu.tw/docs/586276/67808/2SyinL_xl.jpg)
- The creator-origin evidence found is an editorial profile in men’s uno Taiwan: it describes 劉淇’s entry in the Taiwan Mr. selection and his wish to compete internationally representing Taiwan. A profile mirror of his Instagram account shows the handle `@chi_liu`, a self-description as a cook/performer, and 37.7K followers, but that mirror is secondary and does not establish birthplace. [men’s uno Taiwan profile](https://www.mensuno.tw/%E5%BE%9E%E5%BB%9A%E6%88%BF%E7%81%B6%E5%89%8D%E5%88%B0%E9%81%B8%E7%BE%8E%E8%88%9E%E5%8F%B0%EF%BC%9A%E5%8A%89%E6%B7%87%E7%9A%84%E6%96%9C%E6%A7%93%E4%BA%BA%E7%94%9F%EF%BC%8C%E7%94%A8%E4%B8%8D%E8%AA%8D/); [Instagram profile mirror](https://imginn.com/chi_liu/)
- Live API searches `q=劉淇` and `q=濕樂園` return the existing work `work-tw-eb156b0615005365d78916bb`, 《濕樂園：劉淇《SOAKING WET》寫真書》, with digital editions `edition-e7229205490000ea2ec259d9` (Pubu product 686433, PDF影音版) and `edition-ecd90d51e7d23b543494ca73` (Pubu product 686437, PDF電子版), both dated 2026-08-06 and 106 pages. [MuseBooks 劉淇 query](https://musebooks.my/v1/books?q=%E5%8A%89%E6%B7%87); [MuseBooks 濕樂園 query](https://musebooks.my/v1/books?q=%E6%BF%95%E6%A8%82%E5%9C%92); [Pubu product 686433](https://www.pubu.com.tw/magazine/686433); [Pubu product 686437](https://www.pubu.com.tw/magazine/686437)
- Decision for this Pubu title: **DUPLICATE**. The existing live database already contains both formats; no database or R2 changes were made in this research pass. [MuseBooks 劉淇 query](https://musebooks.my/v1/books?q=%E5%8A%89%E6%B7%87)

### Inferences
- Pubu treats the audio/video-inclusive and standard PDF versions as separate digital products; MuseBooks has already modeled them as separate editions of one photobook work. [Pubu product 686433](https://www.pubu.com.tw/magazine/686433); [Pubu product 686437](https://www.pubu.com.tw/magazine/686437); [MuseBooks 劉淇 query](https://musebooks.my/v1/books?q=%E5%8A%89%E6%B7%87)

### Gaps
- I found no primary biographical source establishing 劉淇’s birthplace or an official creator profile during this narrow pass; the Taiwan connection is supported by his Taiwan Mr. participation and his own quoted Taiwan-representation goal, while the follower count is from a third-party mirror. [men’s uno Taiwan profile](https://www.mensuno.tw/%E5%BE%9E%E5%BB%9A%E6%88%BF%E7%81%B6%E5%89%8D%E5%88%B0%E9%81%B8%E7%BE%8E%E8%88%9E%E5%8F%B0%EF%BC%9A%E5%8A%89%E6%B7%87%E7%9A%84%E6%96%9C%E6%A7%93%E4%BA%BA%E7%94%9F%EF%BC%8C%E7%94%A8%E4%B8%8D%E8%AA%8D/); [Instagram profile mirror](https://imginn.com/chi_liu/)
