# Taiwan creator photobook campaign discovery — round 16

Checked 2026-10-30. This round reviewed newly surfaced direct campaign/store leads, then queried the live MuseBooks API. No DB, R2, or catalog changes were made.

## Which newly surfaced campaigns contain a physical photobook?

### Takeaway

晏人物’s current 《Office State Of Mind》 campaign sells a new 128-page group photo collection, but it remains a preorder and the project does not map Taiwan origin to each model or verify final cover art. Keep it on hold.

### Cited Findings

- The [official Zeczec project](https://www.zeczec.com/projects/OfficeStatOfMind) identifies 晏人物 as a Taiwan photography brand/studio and introduces a 2027 project featuring seven models described as influencers, dancers, a dentist, fitness coaches, and others. The project names the models as 炫晨, Kevin, 鈞丞, Cooper, Ray, 泓達, and Jerry; it specifically calls Kevin an Australian physiotherapist but gives no national-origin mapping for the other six.
- The same project offers a physical photobook labelled **“Office Stat Of Mind：晏人物攝影集”** (the campaign title uses “State”). It specifies 128 pages, 18 × 25.6 cm, and lay-flat binding; the book is included in the large bundle/add-on rather than listed as a solo reward. The current campaign window ends 2026-10-30 23:59 UTC+8 and the bundle estimates fulfillment in December 2026. [Project and reward details](https://www.zeczec.com/projects/OfficeStatOfMind)
- The campaign says project images are finished-product mockups that may differ from the shipped product. The linked [photobook image asset](https://assets.zeczec.com/asset_1197844_image_big.jpg?1788597270=) returned a CDN cache-miss / invalid image response during this check, so its final-cover design could not be inspected or hashed.
- Live MuseBooks queries on 2026-10-30 returned zero for [“Office State Of Mind”](https://musebooks.my/v1/books?q=Office%20State%20Of%20Mind), [“Office Stat Of Mind”](https://musebooks.my/v1/books?q=Office%20Stat%20Of%20Mind), and [晏人物](https://musebooks.my/v1/books?q=%E6%99%8F%E4%BA%BA%E7%89%A9).

### Inferences

- **HOLD — Office Stat Of Mind：晏人物攝影集.** This is a credible new physical-photo-book lead, but the fulfillment date is still future, the pictured art is explicitly illustrative, and the project does not establish which contributors are Taiwan-origin creators. Recheck after shipment and after the models’ identities/origins and final cover are documented.

### Gaps

- No final printed-cover image, ISBN, confirmed release/delivery, or national-origin confirmation for six of the seven models was available from the campaign page. The photo asset could not be retrieved successfully. [Official campaign](https://www.zeczec.com/projects/OfficeStatOfMind)

## Does Q尼/Queenie have a new creator-sold booklet suitable for import?

### Takeaway

The direct store confirms an in-stock physical photo booklet associated with Taiwan model Q尼/Queenie, but its title and final cover are not established. The retrieved image is a promotional collage, so keep the item on hold.

### Cited Findings

- The [direct 7-Eleven MyShip listing](https://myship.7-11.com.tw/general/detail/GM2508203612183) calls the product “Q尼實體寫真/周邊,” describes a physical booklet about 21 × 19 cm with one outfit set, and says each booklet includes a photo-shoot video at the back. It labels the item limited in-stock; its shipping terms say in-stock orders ship within 10 business days and stockouts may take 14–28 business days. The listing does not give an ISBN, page count, or stable book title; “夏日的天台” appears as the photo theme in the retrieved image, not a confirmed cover title.
- A [ZEEK profile interview](https://zeekmagazine.com/archives/12399) identifies Q尼 as model 郭珉妏/Queenie and says she was from Kaohsiung and studied fashion design at Tainan University of Technology. Her linked [Instagram profile](https://www.instagram.com/qni510510/) uses the Q尼/Queenie identity.
- The listing’s [product image asset](https://myship.7-11.com.tw/i/cgdm/GM2508203612183/GM2508203612183_3014237.jpg) was downloaded and visually inspected: 109,496 bytes, SHA-256 `589550f379c429e7a665d61541abb59ee8ebec416f1b252e96d55eb57079cca5`. It is a three-panel photo collage with “夏日的天台” text, not a clearly shown printed-book cover.
- Live MuseBooks searches returned zero for [Q尼](https://musebooks.my/v1/books?q=Q%E5%B0%BC), [qni510510](https://musebooks.my/v1/books?q=qni510510), and [怦然心動](https://musebooks.my/v1/books?q=%E6%80%A6%E7%84%B6%E5%BF%83%E5%8B%95).

### Inferences

- **HOLD — Q尼 photo booklet.** The Taiwan model connection and physical seller listing are credible, but the product title/edition metadata and final cover are missing. Do not create a work from the collage alone; revisit if the creator or seller posts a title-matched cover or a photograph of the finished booklet.

### Gaps

- The MyShip page exposes multiple bundles and mentions two “怦然心動” booklets in one merchandise option, but it does not identify those books as this single 21 × 19 cm booklet or give their individual title, page count, or cover. The seller’s relationship to Q尼 is not stated on the page. [MyShip listing](https://myship.7-11.com.tw/general/detail/GM2508203612183)

## What should be treated as already cataloged, and what is the round decision?

### Takeaway

Candy 芷媗’s 《芷想被你收藏》 is already in MuseBooks with a physical edition and stored R2 cover, so it is a duplicate. The two newly surfaced products above remain held; no item from this campaign pass is a GO import.

### Cited Findings

- The [official iWIN product listing](https://www.iwinimc.com/products/candy1023-photobook) describes Candy 芷媗’s physical book as 144 pages, 18 × 25.6 cm, and formally released 2025-10-23; the listing currently says sold out. The [National Central Library monthly deposit list](https://isbn.ncl.edu.tw/FCKEDITOR_UploadFiles/1763434068.pdf) gives the matching title, author, publisher, 144 pages, and ISBN **9786269273300**.
- The live [MuseBooks title query](https://musebooks.my/v1/books?q=%E8%8A%B7%E6%83%B3%E8%A2%AB%E4%BD%A0%E6%94%B6%E8%97%8F) returns `work-tw-bd736260748f93769128a0f1` and physical edition `edition-65e97ae96f67c57043dfa960`, with ISBN 9786269273300, release date 2025-10-23, 144 pages, and a stored R2 cover. [MuseBooks work record](https://musebooks.my/books/work-tw-bd736260748f93769128a0f1)
- Campaign and creator-store checks found no other item with stronger new import evidence than the group project and Q尼 booklet documented above; the recent Zeczec search also returned older/previously recorded campaigns such as 顏尼克《顏》, which were not counted as new candidates. [Zeczec photography category](https://www.zeczec.com/categories?category=9&type=0); [prior creator-campaign note](../Taiwan%20influencer%20photobook%20leads%208/creator_campaigns.md)

### Inferences

- Decision register: **HOLD** Office Stat Of Mind group photo collection; **HOLD** Q尼 physical booklet; **DUPLICATE** Candy’s 《芷想被你收藏》. No DB/R2/catalog edits were made.

### Gaps

- This is a bounded search of current Zeczec photography projects, MyShip creator-store listings, and direct source-linked records, not an exhaustive census of Taiwan influencer photobooks. The held items need final-cover and/or creator-origin evidence before any import decision changes. [Zeczec project](https://www.zeczec.com/projects/OfficeStatOfMind); [Q尼 store](https://myship.7-11.com.tw/general/detail/GM2508203612183)
