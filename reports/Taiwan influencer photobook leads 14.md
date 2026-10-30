# Taiwan influencer photobook leads — round 14

This pass checked the remaining Taiwan creator leads against current seller pages and the live MuseBooks catalog. No new title met the evidence threshold for a DB/R2 import, so no catalog or cover objects were changed.

## New lead held for cover evidence

**四月桐／April — 2026 physical photobook preorder.** Her [7-ELEVEN MyShip product page](https://myship.7-11.com.tw/general/detail/GM2512029367180) describes a 12-outfit photobook, lists book and bundle variants at NT$500–590, and gives a delayed Jan–Feb shipping estimate. The page's image is a promotional collage, not a confirmed final jacket; the shipment note is also stale by the date of this check. The live catalog queries for `四月桐` and `四月桐 April` both returned zero. I held it until a creator or seller post confirms fulfillment and shows the finished cover. [Taiwan达人秀 Coser page](https://www.ttshow.tw/tag/Coser?page=3)

## Latest preorder still pending

蘋蘋澎澎's official [2027 preorder page](https://pinpinponpon627.waca.tw/product/detail/2706145) describes a 128-page photobook and a USB bundle of high-resolution files. Her [official archive](https://pinpinponpon.tw/) lists the new title, but I still could not confirm a final jacket image. The current catalog search returned no exact match for `澎然心動` or `30赫茲`; `蘋率` found a different book, 小蘋果's 《心動蘋率》. I did not treat the USB add-on as a standalone digital edition.

## Live catalog duplicate checks

| Candidate | Current catalog result | Decision |
| --- | --- | --- |
| 2026《禾你相羽 in Okinawa》 | `work-tw-d83d47417493a7a1f42f626e`; two physical editions. [Seller page](https://www.kaboom.tw/products/2026-kimi-in-okinawa-photo-book) says preorder ran July 27–Aug 18 and shipping began Sep 15. | Already present; no duplicate import. |
| 《三倍心跳》梓梓×林莎×元元 | `work-tw-96926b38696ba73e299897d0`; one physical edition. [Official Bee3Shine product page](https://bee3shine.com/product/%E3%80%8A%E4%B8%89%E5%80%8D%E5%BF%83%E8%B7%B3%E3%80%8B%E6%A2%93%E6%A2%93x%E6%9E%97%E8%8E%8Ex%E5%85%83%E5%85%83-%E9%99%90%E9%87%8F%E4%B8%89%E4%BA%BA%E5%AF%AB%E7%9C%9F%E5%A5%97%E7%B5%84/) confirms the signed three-person set. | Already present; no duplicate import. |
| 《芯裡都是你》小珍奶王芯羽寫真書 | `work-tw-e1053f2e1c9480b4a9235a75`; physical ISBN 9786264034050. [Sanmin product page](https://www.sanmin.com.tw/product/index/014063456). | Already present; no duplicate import. |
| Babe Fantasy‧寶兒寫真書 | `work-tw-6bfdeef40b49b66040c85d2e`; physical ISBN 9786267683798 and digital ISBN 9786267683781. [Readmoo ebook page](https://reading.udn.com/ebook/store/store_product.do?pid=150278&source=%E5%AF%AB%E7%9C%9F%E6%9C%80%E6%96%B0). | Already present in both formats. |
| FIRST JUMP：TOKKI CUTIE 臺北伊斯特啦啦隊寫真故事 | `work-tw-27180567259fb6d43aed9de4` is physical (ISBN 9786267776919); `work-tw-ed159843adbd6278211767e4` is digital (ISBN 9786260160128). [Team announcement](https://eastpower.tw/6177), [Sanmin listing](https://www.sanmin.com.tw/product/index/015309196). | Both formats are already present; no duplicate import. |

## Other held title

《韓你菲》 is still supported by announcement coverage, but this search did not locate a direct publisher/retailer product page with a final book jacket. [FTV launch report](https://finance.ftvnews.com.tw/news/detail/2026831W0260). Keep it out of R2/DB until those product details are verifiable.

## Checks performed

- Live `GET /v1/books?q=四月桐` and `q=四月桐%20April`: zero records.
- Live `GET /v1/books?q=澎然心動` and `q=30赫茲`: zero records; `q=蘋率` matched a different title.
- Live title searches confirmed existing work IDs and editions for the duplicate rows above.
- No new work or edition imported; no R2 object uploaded in this pass.

This is an incremental screening pass, not a complete census of Taiwan creator photobooks.
