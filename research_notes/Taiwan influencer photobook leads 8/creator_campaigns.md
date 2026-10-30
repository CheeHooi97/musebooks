# Taiwan creator campaigns and crowdfunded photobooks

## New editions with direct creator or crowdfunding evidence

### Takeaway

The strongest new Taiwan creator lead is Adam Lin's digital-only photo book *FOUR*. The creator's active crowdfunding campaign offers paid access to the PDF and establishes his Taiwan background, but the book has not yet been delivered and the campaign images do not confirm a final ebook cover, so this is a research lead rather than an R2/DB-ready import.

### Cited Findings
- Adam Lin's Zeczec campaign describes *FOUR* as his first pure digital photo book, says it contains only photographs, and identifies him as a Taiwan actor with three prior physical books. The campaign is scheduled for 2026-10-12 through 2026-11-12. [Zeczec campaign](https://www.zeczec.com/projects/ADAM2026)
- The campaign offers the digital book as a purchasable reward (NT$780) with supporter activity shown on the page; the reward is a pure digital product, with estimated realization in December 2026. [Zeczec campaign](https://www.zeczec.com/projects/ADAM2026)
- The campaign FAQ specifies delivery as an encrypted PDF after the crowdfunding period and production; it says the file will be made available through a later project announcement. No page count, ISBN/EISBN, or final delivery date is given in the FAQ. [Zeczec FAQ](https://www.zeczec.com/projects/ADAM2026/faqs)
- Zeczec explicitly says the displayed images and physical collector inserts are illustrative rather than final. I did not identify a distinct final ebook-cover image or ebook-specific cover URL on the campaign page; its current mockup/sample imagery should not be treated as the final cover. [Zeczec campaign](https://www.zeczec.com/projects/ADAM2026)
- Live MuseBooks API title search for `FOUR` returned `total=0`; creator searches for `林冠宇` and `ADAM` also returned `total=0`. The local [Taiwan photobook catalog](../../scraper/taiwan-photobook-catalog.md) had no exact matches for `FOUR`, `ADAM2026`, or `林冠宇` at the time of this check. [MuseBooks FOUR search](https://musebooks.my/v1/books?q=FOUR)

### Inferences
- *FOUR* appears to be a genuinely new digital edition, not a duplicate of Adam's prior print works: the campaign presents it as his fourth book and first digital photo book, and exact-title/creator API searches were empty. [Zeczec campaign](https://www.zeczec.com/projects/ADAM2026); [MuseBooks FOUR search](https://musebooks.my/v1/books?q=FOUR)
- It is not import-ready yet under the cover provenance requirement: wait for a final ebook-specific cover asset and the promised PDF release/fulfillment update, then capture the delivered format and any final bibliographic metadata. [Zeczec campaign](https://www.zeczec.com/projects/ADAM2026); [Zeczec FAQ](https://www.zeczec.com/projects/ADAM2026/faqs)

### Gaps
- No ISBN/EISBN, page count, finalized ebook cover, or completed digital delivery is published on the campaign page/FAQ. [Zeczec campaign](https://www.zeczec.com/projects/ADAM2026); [Zeczec FAQ](https://www.zeczec.com/projects/ADAM2026/faqs)
- Exact-name API searches are useful duplicate checks but do not establish that every prior edition under alternate name spellings is absent; the local catalog had no exact-name hit either. [MuseBooks FOUR search](https://musebooks.my/v1/books?q=FOUR); [local catalog](../../scraper/taiwan-photobook-catalog.md)

## Crowdfunding and seller trails that did not produce another import-ready edition

### Takeaway

Other surfaced crowdfunding and retailer titles were duplicates or did not meet the Taiwan-creator/edition criteria. I found no completed new physical edition with an independently confirmed final cover during this pass.

### Cited Findings
- The new 《顏》 campaign is a completed physical photo book by the Taiwan photography brand 晏人物 featuring 顏尼克; Zeczec says the 128-page, 18 × 25.6 cm book began shipping on 2026-04-20. The campaign page establishes the physical product and fulfillment, but this pass did not establish 顏尼克's Taiwan creator identity or locate a final cover image, so I did not qualify it as a Taiwan influencer import. [Zeczec 《顏》 campaign and shipping update](https://www.zeczec.com/projects/NickYenHBD)
- 《Fairy Land 秘密嗑》 by Adam Lin was shipped in 2024 and includes a standalone photo-book-sized section within a 248-page hybrid travel/essay book; it is not a new work and is not a dedicated photobook edition. [Zeczec 《秘密嗑》 campaign and shipping update](https://www.zeczec.com/projects/secret_adam)
- Aikyo 鄭若青's 2022 physical photobook is already in the local catalog with ISBN 9789860635072; the live product result likewise identifies the author, Taiwan publication, date, pages, and ISBN. [Kingstone listing](https://www.kingstone.com.tw/basic/2029960399717/); [local catalog](../../scraper/taiwan-photobook-catalog.md)

### Inferences
- The crowdfunding trail does reveal an additional promising item—*FOUR*—but excluding it from the current import set preserves the catalog's cover and fulfillment evidence requirements. [Zeczec campaign](https://www.zeczec.com/projects/ADAM2026); [Zeczec FAQ](https://www.zeczec.com/projects/ADAM2026/faqs)

### Gaps
- No newer product or cover evidence was established for 《韓你菲》 or 鄭羽凡's digital edition in this pass; their round-7 holds therefore remain unresolved. [Round 7 report](../../reports/Taiwan%20influencer%20photobook%20leads%207.md)
