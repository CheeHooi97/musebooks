# Taiwan creator physical photobooks — Round 17

Checked 2026-10-30. No database, R2, or catalog changes were made.

## Did the Round 16 preorder leads become import-ready?

### Takeaway

No. 四月桐 and 蘋蘋澎澎 remain preorders without a verified final jacket or dispatch confirmation; 洪蓉’s estimated dispatch date is still in the future and its cover asset could not be fetched. All three remain **HOLD**.

### Cited Findings

- The official [四月桐 2026 MyShip listing](https://myship.7-11.com.tw/general/detail/GM2512029367180) still describes a physical photobook with 12 outfit sets. Its corrected estimate says copies will be sent “late January to early February” but gives no year and asks buyers to wait for a later social-media shipping notice. Taiwan media identify 四月桐 as a Taiwan cosplayer/internet creator, and her [official LinkGoods profile](https://linkgoods.com/apr913) links her social channels. [Taiwan creator profile](https://www.ttshow.tw/article/54062)
- The listing’s [current image asset](https://myship.7-11.com.tw/i/cgdm/GM2512029367180/GM2512029367180_1833102.jpg) fetched successfully as JPEG, 122,772 bytes, SHA-256 `16C8EC6E90D569E4AA10F9DB72200885D0E32609AC626A081A0E2F0EA6A11F95`. Visual inspection shows a multi-photo banner labelled “四月桐2026寫真書、桌曆,” not a final book jacket. No ISBN or page count is provided. The live [MuseBooks 四月桐 query](https://musebooks.my/v1/books?q=%E5%9B%9B%E6%9C%88%E6%A1%90) returned total 0.
- 洪蓉’s [official Vol.02 product page](https://www.yenq888.com/e950vr) currently identifies a 2026 glue-bound, full-color 24-page photo magazine, 21 × 29.7 cm, NT$899, with estimated dispatch “around 11/10.” As of 2026-10-30 that estimate is still future. [HK01’s profile](https://www.hk01.com/%E5%8D%B3%E6%99%82%E5%A8%9B%E6%A8%82/60269413/%E5%8F%B0%E7%81%A3%E7%B6%B2%E7%B4%85%E7%82%BA-%E8%AA%87%E5%BC%B5%E8%BA%AB%E6%9D%90%E7%A8%B1%E8%99%9F-%E8%A8%BB%E5%86%8A%E5%95%86%E6%A8%99-%E5%87%BA%E9%81%9314%E5%B9%B4%E6%8B%8D%E5%BB%A3%E5%91%8A%E8%B5%B0%E7%B4%85) identifies her as a Taiwan internet personality. The product HTML exposes an image named `IMG_8058` at `https://img.1shop.tw/B5OrwMWXgNozxLqRVl7m4dYa/v5zx6meKY4vVr22gl0DVkLyo/`; direct retrieval returned `NoSuchKey`, so there are no image bytes or hash and the final cover cannot be confirmed. The live MuseBooks queries for [洪蓉](https://musebooks.my/v1/books?q=%E6%B4%AA%E8%93%89), [馬友蓉](https://musebooks.my/v1/books?q=%E9%A6%AC%E5%8F%8B%E8%93%89), and [i級豔后](https://musebooks.my/v1/books?q=i%E7%B4%9A%E8%B1%94%E5%90%8E) each returned total 0.
- The official [蘋蘋澎澎 site](https://pinpinponpon.tw/) describes them as Taiwan twins creators. Its current [2027 VIP product page](https://pinpinponpon627.waca.tw/product/detail/2706145) lists one 128-page physical photobook, with expected dispatch in mid-December 2026 and preorder through November 11; high-resolution book and calendar files are part of a USB bundle. This does not establish a separately sold digital edition. The product page returned HTTP 202 with an empty body in this check and HTTP 403 through the page reader, so no final-cover URL, image bytes, or hash could be verified. The exact-title live [MuseBooks query](https://musebooks.my/v1/books?q=%E6%BE%8E%E7%84%B6%E5%BF%83%E5%8B%95%E3%81%AE%E8%98%8B%E7%8E%87) returned total 0.

### Inferences

- **HOLD 四月桐** until a dated shipping-complete notice and individual final cover are available; the fetched image is a promotional collage. ([MyShip listing](https://myship.7-11.com.tw/general/detail/GM2512029367180); [image asset](https://myship.7-11.com.tw/i/cgdm/GM2512029367180/GM2512029367180_1833102.jpg))
- **HOLD 洪蓉 Vol.02** until the seller exposes a verifiable final cover and confirms shipment; also confirm whether a single photo-magazine issue fits the catalog’s photobook definition. ([Vol.02 page](https://www.yenq888.com/e950vr))
- **HOLD 蘋蘋澎澎 2027** until after its stated December fulfillment and until the finished book cover can be inspected. Do not create a second digital edition from USB files bundled with the physical preorder alone. ([VIP product page](https://pinpinponpon627.waca.tw/product/detail/2706145))

### Gaps

- 四月桐’s revised shipping estimate has no year, and no completed-shipment post or final jacket was found. The only retrieved image is the hashed banner described above. ([MyShip listing](https://myship.7-11.com.tw/general/detail/GM2512029367180))
- 洪蓉’s official product page exposes a broken image reference; no ISBN, public cover bytes, or delivered-copy evidence was available. ([Vol.02 page](https://www.yenq888.com/e950vr))
- 蘋蘋澎澎’s product page is not readable through this fetch path, and the image URL and final cover hash remain unknown. ([VIP product page](https://pinpinponpon627.waca.tw/product/detail/2706145))

## Did the retailer and publisher scan find another uncatalogued Taiwan creator book?

### Takeaway

No new **GO** candidate emerged. The direct 2026 retailer listing for 《向你走來：向理來寫真》 is a title-query match already returned by MuseBooks, and its subject is a Japanese performer rather than a Taiwan-origin influencer. Other recent search results were either cataloged, team/photography projects, or outside the Taiwan-origin scope.

### Cited Findings

- 三民’s direct [《向你走來：向理來寫真》 listing](https://www.sanmin.com.tw/product/index/015549423) gives ISBN **9786264446723**, paperback, 168 pages, publisher 時報文化, and publication date 2026-06-12. Retail descriptions identify 向理來 as a Japanese performer and Taiwan’s Tiny as the project coordinator. ([CityBook listing](https://www.cite.com.tw/book?id=108020); [Kingstone listing](https://www.kingstone.com.tw/basic/2019910059433/))
- The live MuseBooks title query [向你走來](https://musebooks.my/v1/books?q=%E5%90%91%E4%BD%A0%E8%B5%B0%E4%BE%86) returned total 2 and the existing [MuseBooks work record](https://musebooks.my/books/work-tw-0a1c9019e4adafb97e326467) confirms a cataloged work. The ISBN search for **9786264446723** returned total 0 despite the title match, so title matching is the reliable duplicate check in this case. The already-cataloged book’s cover was not downloaded or re-hashed in this scan.
- A newer physical item located during retailer search, 《慾見SHOYA：筋肉教練寫真》, is explicitly described by the [publisher Kadokawa](https://www.kadokawa.com.tw/products/9786264359313) as a Japanese coach’s 2026 book (ISBN **9786264359313**, issued 2026-01-22); it is not a Taiwan-origin creator title. A 2026 listing for 《TRUE：人態好攝影集2》 credits photography brand 人態好 NICE PEOPLE PHOTOGRAPHY rather than an identified Taiwan influencer, so it was not treated as an eligible individual creator photobook. ([Momo product listing](https://www.momoshop.com.tw/product/10418060))

### Inferences

- **DUPLICATE / OUT OF SCOPE — 《向你走來》**: the exact title is already returned by MuseBooks, and the subject is Japanese; no new Taiwan influencer record or cover upload is warranted. ([MuseBooks title query](https://musebooks.my/v1/books?q=%E5%90%91%E4%BD%A0%E8%B5%B0%E4%BE%86); [Sanmin listing](https://www.sanmin.com.tw/product/index/015549423))
- The current scan yielded no new physical title with the required combination of Taiwan-origin creator evidence, direct product evidence, an uncatalogued live-title result, and a verifiable final cover. Search remains bounded, not exhaustive. ([Sanmin photo-book search](https://www.sanmin.com.tw/search?k=%E5%AF%AB%E7%9C%9F%E6%9B%B8&ls=ed&pt=t); [Books.com photo-book category](https://www.books.com.tw/web/books_bmidm_2204/); [MuseBooks title query](https://musebooks.my/v1/books?q=%E5%90%91%E4%BD%A0%E8%B5%B0%E4%BE%86))

### Gaps

- No source established a new, uncatalogued Taiwan-origin individual print photobook with an inspectable final cover during this pass. The 2026 search results need to be revisited as future release and delivery pages become available. ([Sanmin photo-book search](https://www.sanmin.com.tw/search?k=%E5%AF%AB%E7%9C%9F%E6%9B%B8&ls=ed&pt=t); [Books.com photo-book category](https://www.books.com.tw/web/books_bmidm_2204/))
