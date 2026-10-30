# Taiwan creator preorder and campaign checks — round 15

Checked 2026-10-30. This note covers the assigned campaign lane; it is not an exhaustive census.

## Which active product pages have changed or need a later fulfillment check?

### Takeaway

No campaign lead is import-ready today. 《FOUR》 and the new 2027 蘋蘋澎澎 book are explicit future preorders; 四月桐’s product page still documents a photobook but its expected shipping window is stale or underspecified, and its linked art is promotional rather than a verified cover.

### Cited Findings

- The [official Zeczec campaign for ADAM 林冠宇《FOUR》](https://www.zeczec.com/projects/ADAM2026) is open from 2026-10-12 through 2026-11-12. It calls the work his first digital photobook, offers the ebook as a PDF, and estimates fulfillment in December 2026. It explicitly says campaign images and reward mockups are illustrative and not the final items. The [campaign FAQ](https://www.zeczec.com/projects/ADAM2026/faqs) says the PDF will be encrypted and its collection details will be announced after the campaign closes and production is complete.
- 四月桐’s [direct 7-Eleven MyShip listing](https://myship.7-11.com.tw/general/detail/GM2512029367180) sells a 2026 photo series including a photobook with 12 outfit sets. The seller first estimates shipping from December to mid-January, then amends this for printing delay to late January–early February; it does not state the year for that window and asks buyers to follow her social accounts for a shipping notice. The listing’s [linked product image](https://myship.7-11.com.tw/i/cgdm/GM2512029367180/GM2512029367180_1833102.jpg) is a wide promotional collage/banner, not a clearly isolated or confirmed final book cover.
- 蘋蘋澎澎’s [official creator site](https://pinpinponpon.tw/) identifies her as a creator from Taiwan and links the newly promoted title 《澎然心動的蘋率30赫茲》. The [official 2027 VIP product listing](https://pinpinponpon627.waca.tw/product/detail/2706145) describes a 128-page physical photobook, a 2027 calendar, and high-resolution photobook/calendar files on USB in the VIP bundle. It says preorder runs through November 11, with dispatch expected in December 2026 (the FAQ says mid-December). The storefront also lists a separate single-book product. The product page fetch returned 403 in this check, so I could not inspect its displayed artwork and cannot confirm a final cover.
- Live MuseBooks API searches on 2026-10-30 returned zero for [林冠宇](https://musebooks.my/v1/books?q=%E6%9E%97%E5%86%A0%E5%AE%87), [四月桐](https://musebooks.my/v1/books?q=%E5%9B%9B%E6%9C%88%E6%A1%90), and the new title phrase [澎然心動](https://musebooks.my/v1/books?q=%E6%BE%8E%E7%84%B6%E5%BF%83%E5%8B%95).

### Inferences

- **HOLD 《FOUR》.** The campaign establishes a real digital product, but it is still a preorder; there is no delivered file, final cover, or edition identifier yet. Recheck after December fulfillment.
- **HOLD 四月桐.** The direct seller establishes a photobook product, but the expected shipping window is already past if it refers to 2026, the page supplies no year, and no shipment-complete post was located. The linked collage should not be treated as the final cover.
- **HOLD 《澎然心動の蘋率》.** This is a distinct, direct product lead, but both physical and bundled digital files are future fulfillment; the accessible product evidence does not verify the final cover. The VIP USB files are part of a bundle, not evidence of a separately sold digital edition.

### Gaps

- For 《FOUR》, final PDF, release/delivery confirmation, ISBN/EISBN or other edition identifier, and a final-cover asset are unavailable in the campaign materials. [Campaign](https://www.zeczec.com/projects/ADAM2026); [FAQ](https://www.zeczec.com/projects/ADAM2026/faqs)
- For 四月桐, the listing does not date its corrected January–February shipping window, and no creator shipping-completion notice was found. No ISBN, page count, or verified final cover is provided. [MyShip listing](https://myship.7-11.com.tw/general/detail/GM2512029367180)
- For 《澎然心動の蘋率》, the official product page confirms a future preorder and formats but was blocked from direct inspection; a final cover, publication identifier, and delivered copy/files remain unverified. [Official product listing](https://pinpinponpon627.waca.tw/product/detail/2706145)

## Did 《韓你菲》 gain a direct product and final-cover trail?

### Takeaway

No. The announced sale date has passed, but the sources found still stop at a press announcement: there is no direct item-level seller page, confirmed final cover, edition identifier, or delivery evidence. The work is distinct from 李恩菲’s older cataloged books.

### Cited Findings

- The [FTV announcement](https://www.ftvnews.com.tw/news/detail/2026831W0260) and [UDN report](https://stars.udn.com/star/story/10089/9724294), both dated 2026-08-31, say 李恩菲’s first solo physical photobook 《韓你菲》 was scheduled to go on sale at 8 p.m. on September 2 and direct readers to her official social channels for the sales details. The article images are not identified as the book’s final cover.
- The live MuseBooks API returned zero for the exact [《韓你菲》 title query](https://musebooks.my/v1/books?q=%E9%9F%93%E4%BD%A0%E8%8F%B2). A [李恩菲 query](https://musebooks.my/v1/books?q=%E6%9D%8E%E6%81%A9%E8%8F%B2) returned four existing works, including 《菲你莫屬-菲菲數位寫真書-中文版》, 《菲進你心 菲菲個人數位寫真（含影音）》, and the earlier collaboration 《bestie閨蜜：孟潔×菲菲寫真》.

### Inferences

- **HOLD 《韓你菲》.** The press coverage confirms an announced title and sale date, not the product identity or fulfillment. Keep it separate from the already-cataloged solo digital books and the 2022 collaboration; do not add a record from the article announcement alone.

### Gaps

- The September 2 announcement did not identify a direct shop, ISBN, page count, exact edition details, final-cover asset, or shipment status. Those item-level facts were not established in the official or retailer results located for this pass. [FTV](https://www.ftvnews.com.tw/news/detail/2026831W0260); [UDN](https://stars.udn.com/star/story/10089/9724294)

## Which catalog matches should be treated as duplicates, and what should be revisited?

### Takeaway

蘋蘋澎澎’s 2026 《純·欲姊姊特休中》 is already a physical MuseBooks work with an R2 cover, so it is a duplicate. The 2027 title is new but held; the other campaign leads remain held pending fulfillment and/or cover evidence. No database or R2 changes were made in this campaign research pass.

### Cited Findings

- The creator’s [official page](https://pinpinponpon.tw/) links the older 2026 title and the new title separately. The [older direct product page](https://pinpinponpon627.waca.tw/product/detail/2589988) describes 《純·欲姊姊特休中》 as a 128-page physical photobook featuring 蘋蘋澎澎 and 湘綾 and estimates shipment from mid-June 2026. The page remains marked preorder/sold out and retains stale countdown text, so that estimate alone is not proof of fulfillment.
- The live [MuseBooks record for 《純·欲姊姊特休中》](https://musebooks.my/books/work-tw-8ce4dd25e173839b10d88706) is `work-tw-8ce4dd25e173839b10d88706`, with physical edition `edition-51b040d29f2ce074f6e91c36`, 128 pages, and a stored R2 cover URL. This exact record is why the older title is a **DUPLICATE**, not a new import.
- Live API checks returned zero for the new product phrase [澎然心動](https://musebooks.my/v1/books?q=%E6%BE%8E%E7%84%B6%E5%BF%83%E5%8B%95), and for [《韓你菲》](https://musebooks.my/v1/books?q=%E9%9F%93%E4%BD%A0%E8%8F%B2); the [creator-name query for 李恩菲](https://musebooks.my/v1/books?q=%E6%9D%8E%E6%81%A9%E8%8F%B2) matches only her prior works.

### Inferences

- Decision summary: **DUPLICATE** old 2026 蘋蘋澎澎 title; **HOLD** new 2027 蘋蘋澎澎 title, 《FOUR》, 四月桐’s 2026 series, and 《韓你菲》. No campaign-side item meets both the fulfillment/final-cover evidence threshold and a resolved edition record for import in this pass.
- Recheck 《FOUR》 and PinPin’s 2027 title after their expected December 2026 fulfillment; recheck April when the creator confirms shipment and supplies a title-matched final cover; recheck 《韓你菲》 when an official seller or product post is identified.

### Gaps

- Campaign discovery was limited to the named creator/product trails, their linked official channels, relevant product pages, and live MuseBooks queries; it does not prove that no other Taiwan creator photobooks exist. [FOUR campaign](https://www.zeczec.com/projects/ADAM2026); [April listing](https://myship.7-11.com.tw/general/detail/GM2512029367180); [PinPin product](https://pinpinponpon627.waca.tw/product/detail/2706145); [韓你菲 announcement](https://www.ftvnews.com.tw/news/detail/2026831W0260)
