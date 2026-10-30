# Taiwan influencer photobook campaign status sweep — round 17

Checked 2026-10-30. This note rechecks the Round 16 holds and one newly surfaced 2027 creator-store preorder. Live MuseBooks API queries were run for each name/title. No DB, R2, or catalog changes were made.

## What changed for the Round 16 campaign and store holds?

### Takeaway

None of the three Round 16 holds is now a verified delivered, import-ready book. 《FOUR》 remains an open digital-book preorder, Office State Of Mind remains a future-delivery group campaign with unresolved model origins and no confirmed final cover, and Q尼’s in-stock item still lacks a title-matched cover and basic edition metadata.

### Cited Findings

- The [official Zeczec《FOUR》campaign](https://www.zeczec.com/projects/ADAM2026) identifies Adam 林冠宇 as a Taiwanese actor and describes 《FOUR》 as his first electronic photobook. Fundraising runs from 2026-10-12 to 2026-11-12, so the campaign remains open as of this check. The [official FAQ](https://www.zeczec.com/projects/ADAM2026/faqs) specifies a PDF file and says access instructions will follow campaign close and production; it does not provide a delivery date. The book has not yet been fulfilled. Images for its physical extras are explicitly illustrative, and I found no confirmed final ebook-cover asset. A linked project image, [asset_1206710](https://assets.zeczec.com/asset_1206710_image_big.jpg?1790266361=), returned HTTP 403 with a 4,569-byte HTML response, not an image; no image hash was computed.
- The [official Office State Of Mind campaign](https://www.zeczec.com/projects/OfficeStatOfMind) offers the physical 128-page, 18 × 25.6 cm “Office Stat Of Mind：晏人物攝影集” as a reward/add-on, with estimated fulfillment in December 2026. December has not passed, so delivery is unverified. The campaign says its illustrations are mockups that may differ from shipped goods. Its [October 14 project update](https://www.zeczec.com/projects/OfficeStatOfMind/updates/66729) announces an extension, but it could not be fetched in this check; the campaign’s date field and search-indexed copies disagree about the revised deadline. The linked [photobook image asset](https://assets.zeczec.com/asset_1197844_image_big.jpg?1788597270=) returned HTTP 403 with a 4,569-byte HTML response, so final-cover inspection and hashing were not possible. The project identifies 晏人物 as a Taiwan photography studio, but does not map Taiwan origin to each of the seven models; it identifies Kevin as Australian. [Project](https://www.zeczec.com/projects/OfficeStatOfMind) and [indexed creator-update excerpt](https://www.pixnoy.com/profile/timothy_figure/)
- The [direct MyShip listing for Q尼](https://myship.7-11.com.tw/general/detail/GM2508203612183) still describes a limited in-stock physical booklet and says in-stock orders ship within 10 business days. It gives an approximate 21 × 19 cm size and one outfit, but no ISBN, page count, or stable title. A [ZEEK profile](https://zeekmagazine.com/archives/12399) identifies Q尼/Queenie as 郭珉妏 and says she is from Kaohsiung. The listing’s [current product image](https://myship.7-11.com.tw/i/cgdm/GM2508203612183/GM2508203612183_3014237.jpg) fetched successfully (HTTP 200, JPEG, 109,496 bytes; SHA-256 \`589550f379c429e7a665d61541abb59ee8ebec416f1b252e96d55eb57079cca5\`). It is a three-panel promotional collage, not a demonstrated printed cover.
- Live MuseBooks API queries returned no exact match for [林冠宇](https://musebooks.my/v1/books?q=%E6%9E%97%E5%86%A0%E5%AE%87), [Office State Of Mind](https://musebooks.my/v1/books?q=Office%20State%20Of%20Mind), [晏人物](https://musebooks.my/v1/books?q=%E6%99%8F%E4%BA%BA%E7%89%A9), [Q尼](https://musebooks.my/v1/books?q=Q%E5%B0%BC), or [qni510510](https://musebooks.my/v1/books?q=qni510510). The broad [FOUR query](https://musebooks.my/v1/books?q=FOUR) returned an unrelated Korean title, not Adam’s book.

### Inferences

- **HOLD — FOUR:** Taiwan creator and PDF format are verified, but the download is future and there is no confirmed final cover.
- **HOLD — Office State Of Mind:** a photobook reward and Taiwan studio are verified, but delivery is future, art is illustrative, the campaign deadline is inconsistent across accessible copies, and the models’ Taiwan origins are not established.
- **HOLD — Q尼 booklet:** seller stock and creator Taiwan connection are supported, but there is no stable title/ISBN/page count or final book-cover evidence.

### Gaps

- The exact extended Office State Of Mind close time and any post-campaign shipment update could not be confirmed from the inaccessible project update. No delivered copy or final-cover photo was verified for these three leads.

## Does the new 2027 蘋蘋澎澎 preorder have import-ready cover evidence?

### Takeaway

Yes, as a preorder metadata candidate: 蘋蘋澎澎’s official storefront identifies a new 128-page physical book, and the creator website posts a title-specific Vol. 8 cover asset. It is not fulfilled yet, and the store does not list an ISBN or explicitly say that the displayed artwork is immutable.

### Cited Findings

- 蘋蘋澎澎’s [official website](https://pinpinponpon.tw/) identifies the twins as Taiwan creators and lists the new title as Vol. 8, “澎然心動的蘋率：30赫茲.” The [official creator-store product page](https://pinpinponpon627.waca.tw/product/detail/2706145) sells a 2027 “澎然心動の蘋率” VIP package that includes one physical single book (128 pages). It also includes a USB with high-resolution digital files for the book and calendar; this supports bundled digital files, not a separate standalone ebook edition.
- The store marks the item as preorder, says the preorder price runs through November 11, and estimates shipments starting in mid-December 2026. These dates are future as of 2026-10-30; no delivery has occurred.
- The official site’s image tag identifies the cover as “澎然心動的蘋率：30赫茲 — 蘋蘋澎澎寫真集 Vol.8.” The [cover asset](https://pinpinponpon.tw/images/vol8.jpg) fetched successfully (HTTP 200, JPEG, 88,054 bytes; SHA-256 \`5768BAE3B7583F70644A3AB1347F25DCE4602562356D3D44BEB70D718C4F9210\`). This is official, title-specific cover artwork; no in-hand copy or explicit statement that the printed cover is final was found.
- The live API’s [exact-title query](https://musebooks.my/v1/books?q=%E6%BE%8E%E7%84%B6%E5%BF%83%E5%8B%95) returned zero. Its [蘋蘋澎澎 query](https://musebooks.my/v1/books?q=%E8%98%8B%E8%98%8B%E6%BE%8E%E6%BE%8E) returned earlier books, including the 2026 “純·欲姊姊特休中” work, but not Vol. 8.

### Inferences

- **GO — 蘋蘋澎澎《澎然心動の蘋率》 physical preorder record:** item source, title, creator origin, 128-page format, future fulfillment estimate, official cover asset, and live-API non-duplication are documented. Keep the status marked preorder, not delivered; note the missing ISBN and that this is official cover artwork rather than an inspected printed copy.

### Gaps

- The store does not list an ISBN or separate standalone digital edition in the retrieved product page. The physical copy and shipment remain unverified.

## What are the round’s decisions and remaining limits?

### Takeaway

One new candidate is GO for a preorder metadata record; the three earlier holds remain on hold. This is a focused status sweep, not a complete census.

### Cited Findings

- The new preorder’s direct sources are the [official creator-store listing](https://pinpinponpon627.waca.tw/product/detail/2706145) and [official Vol. 8 cover asset](https://pinpinponpon.tw/images/vol8.jpg).
- Decisions: **GO — 蘋蘋澎澎《澎然心動の蘋率》 physical preorder**; **HOLD — ADAM 林冠宇《FOUR》 digital PDF preorder**; **HOLD — 晏人物 Office State Of Mind group photobook campaign**; **HOLD — Q尼 physical booklet**. The source links and live API checks above support these calls.

### Inferences

- No catalog or media mutation was authorized for this round, so GO means an import candidate only; no DB or R2 write was made.

### Gaps

- The search covered the named campaigns, creator store, and directly surfaced sources; it cannot establish every Taiwan creator photobook or verify deliveries outside the checked pages.
