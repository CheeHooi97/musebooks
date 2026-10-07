# Taiwan catalog import — 2026-10-07

The live `musebooks` database contains 441 work rows and 535 edition rows. The refreshed source-linked export contains 439 published works and 528 active edition rows across 334 model/artist credit labels; two superseded works and seven superseded editions remain as history. Waves 104–112 add twenty-one works and thirty-seven format-specific editions.

The complete source-linked list by model is in [taiwan-photobook-catalog.md](taiwan-photobook-catalog.md). The matching JSON export contains edition identifiers, original published titles, credited models, metadata URLs, R2 references, digital and physical retail offers, and separate active/sold physical marketplace listings. Shared books appear under each participant in the bibliography but have one catalog work identity.

## Current verified results

- The source-linked bibliography lists 289 physical editions and 239 digital editions.
- Public catalog handlers return 258 physical works and 231 digital works. Related formats can share a work, while titles without verified equivalence remain separate.
- 283 listings and 289 observations across 16 sources.
- Four calendar/illustration listings remain excluded and retained for history.
- 35 valid marketplace listings remain unlinked because their specific edition cannot be identified confidently.
- All four Wave 104, four Wave 105, three Wave 106, five Wave 107, six Wave 108, four Wave 109, one Wave 110, and four Wave 111 and one Wave 112 R2 objects passed HEAD and public GET SHA-256 checks. One Kobo edition still has no cover because its source image is behind an 18+ confirmation prompt; the HamiBook image for the same work is explicitly a generic 18+ preview.
- One current edition has a pending cover. Unavailable images were not replaced with guessed edition covers.

The original six models were supplemented with 巫苡萱、林孟潔、李恩菲、林真亦、許玲玲、林艾融、斐棋、畇二、倪暄、陳伊、董梓甯、泥泥、鄭家純、王芯羽、沐妍、郭鬼鬼、短今、李優、羚安、金渡兒 and 阿厚綾. 楊曉帆 is also credited through the verified 伊梓帆 group books.

## Latest import: Wave 107

Three newly verified models were added as separate works: 吳岳擎《擎書》、黃信赫《偽裝Camouflage》 and 林嘉威《愛戀❤嘉威》. Each has distinct print and fixed-layout EPUB editions with format-specific R2 covers. The live records include five current store offers: two physical Sanmin retailer prices and three BOOK☆WALKER digital prices. Physical bookstore offers are classified separately from secondhand marketplace asking/sold prices. The 擎書 physical edition remains cataloged but has no active offer because the publisher currently marks it sold out. Prices are asking prices, not completed-sale prices.

The batch also fixed bookstore format inference so `bookstore` sources follow their configured default/allowed format; physical Sanmin listings had been rejected when the backend assumed every bookstore was digital. Catalog package tests passed, the batch committed, and public catalog readback confirmed the new format-separated works.

## Latest import: Wave 108

Three newly verified works were added: 邱宇辰 and 黃宏軒《遠在謙邊：關於未知的我們 CP寫真書》, 謝佳見《臨界之地Land Boundary》, and 陳彥名《#Y1闖入》. Each work has separately cataloged physical and digital editions. Physical and digital covers use different R2 assets where the source artwork differs.

The six editions have five current store offers: one Sanmin physical retailer backorder at NT$612 and four digital asking prices—BOOK☆WALKER NT$450 for《遠在謙邊》; BOOK☆WALKER and Sanmin Bookroll each NT$408 for《臨界之地》; and BOOK☆WALKER NT$399 for《#Y1闖入》. These are current offers, not completed-sale prices. The《遠在謙邊》print edition and《#Y1闖入》print edition remain in the bibliography without active offers because the publisher/retailer pages show sold out. 博客來's product code 4718008486882 is retained as a note rather than mislabeled as an ISBN.

All six Wave 108 covers passed R2 HEAD and public GET SHA-256 readback. Import validation, database commit and public format-filter readback succeeded. The two members of《遠在謙邊》are stored as separate model credits; additional title discovery remains in progress.

## Latest import: Wave 109

Two additional works were added with print and ebook editions: 陳柏文與姜典《柏愛典藏》and 陳肇天《Sky》. Each of the four editions has its own source-specific cover asset; the print mockups and ebook covers are visually different.

The batch records three live store asking prices: Sanmin print retailer price NT$612 with one copy in stock and add-to-cart enabled for《柏愛典藏》; BOOK☆WALKER ebook NT$510 for《柏愛典藏》; and BOOK☆WALKER ebook NT$450 for《Sky》. Kadokawa marks the《Sky》print edition sold out, so it is cataloged without an active offer. Prices are asking prices, not completed-sale prices.

All four Wave 109 R2 objects passed HEAD and public GET SHA-256 verification. The database import and source-linked catalog export succeeded; 陳柏文 and 姜典 have separate model credits. Physical bookstore prices are now classified as retailer offers in the API/UI and bibliography export, rather than appearing in the physical marketplace asking-price section.

## Latest import: Wave 110

Added 羚安《羚家女孩 羚安數位寫真》 as one digital-only fixed-layout EPUB edition (EISBN 9786263771208; BOOK☆WALKER release date 2023-09-20). The book description credits photographer 陳賢瀛 and describes playful, calm, indoor portrait and relaxed outdoor looks. BOOK☆WALKER lists 280 pages while Readmoo lists 282 for the same EISBN; the catalog records the primary listing value and preserves the discrepancy in its notes. No physical edition was inferred or created.

BOOK☆WALKER and Readmoo both showed active NT$259 digital-store offers with purchase controls during live review. The one digital cover was copied to R2 and passed HEAD, public GET and SHA-256 readback. The bibliography export and public API verify one new digital work, no new physical work, and no marketplace listing for this title. These are current retailer asking prices, not completed-sale prices.

Sources: [BOOK☆WALKER 羚家女孩](https://www.bookwalker.com.tw/product/175658), [Readmoo 羚家女孩](https://readmoo.com/book/210291466000101), [Kobo 羚家女孩](https://www.kobo.com/tw/zh/ebook/SiuuctwoCDuY-x-ukjm2iA), [羚安 shooting locations and release coverage](https://www.cool-style.com.tw/wd2/archives/959245-%E5%8F%88%E7%B4%94%E5%8F%88%E6%AC%B2%EF%BC%81%E7%BE%9A%E5%AE%89%E6%95%B8%E4%BD%8D%E5%AF%AB%E7%9C%9F%E3%80%8A%E7%BE%9A%E5%AE%B6%E5%A5%B3%E5%AD%A9%E3%80%8B%E5%B0%BA%E5%BA%A6%E5%A4%A7%E9%96%8B%EF%BC%8C).

## Latest import: Wave 111

Added 金渡兒《想與你一起渡過》as one physical work with four distinct print variants: the standard edition, Books.com’s exclusive cover, Eslite’s exclusive cover and 尖端’s boxed preorder. The standard ISBN edition is 144 pages; Eslite lists 176 pages and EAN 4717702301859, so both source values are preserved without assigning an ISBN to the Eslite variant. Books.com’s product page did not expose its ISBN/page-count fields during review. The boxed set’s product announcement lists a magnetic collector box, exclusive cover, cards, cushion cover and poster; its page count and ISBN were not published in the reviewed listing.

Sanmin showed the standard edition in stock at NT$719, and Eslite showed its cover variant available at NT$631. These are current bookstore asking prices. The special edition’s NT$1,680 amount was a preorder price that ended before this review and is not recorded as current. No digital edition was verified. A Ruten result showed NT$720 with sales count zero, but the item page could not be re-checked and its shipping estimate was stale, so it was not saved as an active marketplace listing. No final sold-price record was verified.

All four edition cover assets passed R2 HEAD and public GET SHA-256 readback. Database readback confirms one 金渡兒 work, four physical editions and two active bookstore observations, with zero digital editions or marketplace listings for this work. Sources: [Sanmin standard edition](https://www.sanmin.com.tw/product/index/015782086), [Books.com exclusive cover](https://www.books.com.tw/products/0011061933), [Eslite exclusive cover](https://www.eslite.com/product/10012116312683215827006), [publisher boxed preorder](https://www.spp.com.tw/SalePage/Index/11962162), [publisher’s announcement of the boxed contents](https://www.cool-style.com.tw/wd2/archives/1322845-%E9%87%91%E6%B8%A1%E5%85%92%E9%A6%96%E6%9C%AC%E5%AF%AB%E7%9C%9F%E6%9B%B8%E3%80%8A%E6%83%B3%E8%88%87%E4%BD%A0%E4%B8%80%E8%B5%B7%E6%B8%A1%E9%81%8E%E3%80%8B7-14-%E6%B5%AA%E6%BC%AB%E9%96%8B%E6%94%BE), [publisher’s report on the retailer cover variants](https://www.cool-style.com.tw/wd2/archives/1341313-%E9%87%91%E6%B8%A1%E5%85%92%E5%AF%AB%E7%9C%9F%E9%96%8B%E8%B3%A3%E5%8D%B3%E5%82%B3%E6%8D%B7%E5%A0%B1%EF%BC%81%E3%80%8A%E6%83%B3%E8%88%87%E4%BD%A0%E4%B8%80%E8%B5%B7%E6%B8%A1%E9%81%8E%E3%80%8B%E7%81%AB/amp).

## Latest import: Wave 112

Added 阿厚綾《綾の邊界 きわ》 as one physical paperback edition. Kingstone lists the 2026-08-18 publication date and 16開 19×26 cm format, but leaves ISBN blank and page count at zero; those fields remain unasserted. The product description identifies hot-spring, kimono, home, Chinese-style and swimwear scenes. An August agency post separately promoted the same title on Books.com, but its current product URL returned HTTP 403 during this check, so that earlier promotion was not treated as a current offer. Exact title searches across Kingstone, BOOK☆WALKER, Readmoo, Rakuten/Kobo and Pubu found no separate digital product; this is “not found,” not proof that no digital edition exists.

Kingstone showed an active NT$890 checkout price (list price NT$980) on 2026-10-07. This is a bookstore asking price, not a used-marketplace listing or completed sale. Exact-title marketplace searches did not surface a separately verifiable active or completed listing; that is not proof none exists, so no marketplace or sold-price observation was imported. The official Kingstone cover was uploaded to R2; PUT, HEAD and public GET returned HTTP 200 with matching SHA-256. Database and public-catalog verification show one 阿厚綾 work with one physical edition and no digital edition. The refreshed bibliography now contains 439 published works, 528 active edition rows and 334 model/artist credit labels. Sources: [Kingstone product](https://www.kingstone.com.tw/basic/2075020023320/), [agency announcement and promotional listing links](https://www.findglocal.com/TW/Taipei/126250264880064/%E6%84%9B%E7%BE%8E%E6%98%9F-iamstar.TV), [photographer-credit post](https://www.kolr.ai/influencer/8bd0c27c-8409-481a-9530-1e2cce684390?lang=zh&platform=ig).

## Expanded research batch

This expansion added 62 individually credited models/artists, 78 works and 90 editions (70 physical and 20 digital). It added 94 unique verified R2 cover objects, including related retail/marketplace images. Metadata and cover references were committed to PostgreSQL and read back successfully.

Additional names include 籃籃、林岱縈、陳紫渝、吳心緹、冼迪琦、寶兒、張景嵐、陳瑀希、蔡黃汝、安心亞、舒子晨、蘇心甯、梁凱莉、許薇安、謝薇安、謝侑芯、許維恩、羽晴、湘綾、波波蓁、佳娜、林倪安、陳子玄、夏蕾 and 彭彭. The complete bibliography lists all 87 credited people and their verified editions. This covers Taiwan-market publications; some credited models are based overseas.

Kingstone's personal-photobook category, Cite publisher lists, Sanmin product pages and RedBoy's public publisher catalog expanded discovery beyond name searches. RedBoy publisher ebooks are catalog metadata in this batch: no recurring RedBoy price worker or offer was configured. Its sold-out BIVI book retains its edition without an active-price claim. 湘綾's ebook page copies physical-book specifications, so those specifications were not attributed to the digital edition.

44 bounded model/source searches were checkpointed. The remaining 22 queries, incomplete result cursors, failed verification queries and further publisher-category candidates are recorded in `taiwan-photobook-research-queue.json`. They are research targets, not assertions of absent or verified books. This batch is not an exhaustive publication history.

## Further publisher expansion

The next public research batch added 44 model/artist credit labels, 67 works and 67 editions: 63 physical and four digital. All 67 additional edition covers were mirrored to R2 and verified. Three pages of the 女神範 book catalog supplied 60 products; primary retailer checks supplied five more, and BOOK☆WALKER supplied two additional digital editions.

New credits include 沐雨柔、蔡瑛紋、莫葵、小蘋果、牛奶兒、李馨、龔映璇、靜川奈、星野優、林育品（阿喜）、卓毓彤（熊熊）、安希、袁艾菲 and 小映. Publisher-scoped 梓梓 and 兔兔 labels remain separate from other publishers until identity equivalence is verified; the credit count is therefore not a confirmed unique-person count. Book images can include the publisher’s promotional border. Unknown ISBNs, dates and page counts remain empty.

卓毓彤’s publisher specifies 162 pages while the ISBN-matched retailer specifies 144; the publisher value is retained with a discrepancy note. 小映’s Japanese digital edition is explicitly marked ja after checking the product page. Physical retail prices were not recorded as marketplace observations. No final sold-price records were added.

## Additional retailer expansion

This batch added six credit labels and 11 editions: three physical and eight digital. 藍星蕾 has five verified books; 妮可 and 護理師依依 each have one ebook; 潔西 has one ebook with five behind-the-scenes videos; 迷路班比 has two distinct ebooks; 李毓芬 has one physical photobook. All 11 covers were uploaded to R2 and verified, and the database import was read back successfully.

Source-specified poster bundles, included videos and overlapping content are retained. The retailer says 藍星蕾《真心愛上蕾》 exceeds 270 pages, so no exact page count is asserted. 妮可’s ebook uses its EISBN rather than the physical ISBN also displayed on the retailer page. This metadata batch adds no marketplace or retail-price observations.

## Series and edition follow-up

Eleven additional author searches supplied eight reviewed retailer products. Five are new editions: 林莎’s physical《揭開．面莎》and 李芷霖’s three separate digital parts without videos plus a Japanese edition. Three ISBN-matched 林莎 products update existing edition metadata. Seven additional distinct R2 objects were verified; one reviewed image reused an existing object. The bibliography now has 222 current works and 260 editions. Duplicate imports were corrected and retained only as superseded history.

A 李芷霖 product whose description credits 楊比 is held for review. Another same-title 林莎 product needs reprint reconciliation. 《三倍心跳》, 《Honey》and 許瑜’s series remain research targets. None is declared fully cataloged from search results alone.

## Official music-artist photobook

吳卓源《ju&u》was verified on the official FIGHT30 merchandise store and imported with its verified R2 cover. The source specifies 56 pages, A3 dimensions and a hardcover. Historic preorder dates and conditional gifts were not presented as a current publication date or fixed bundle. Live lookup of 林莎《Honey》returned HTTP 404, while 鄔唯’s TAAZE detail failed TLS verification; neither was imported from indexed snippets.

## Further digital model discovery

鄔唯《只因唯你》and 李藹蔚《蔚你著迷》were verified through Sanmin product pages, with both covers uploaded and verified in R2. 鄔唯’s source confirms five side-shoot videos. Both editions were committed and read back; no retail or marketplace observations were synthesized from publisher metadata. Twelve author queries were checked; 呼呼’s older series and 周曉涵’s two-book set remain pending stronger accessible primary detail pages.

## Additional physical series

解婕翎’s same-name 112-page photobook and《我就是任性》日系．性感 two-book combined limited edition were verified through Sanmin and CCR retailer pages. 林采婕’s 120-page《A Slower Summer》has one signed bonus card, randomly supplied from three designs; the book itself is not asserted signed. All three covers passed R2 verification and records passed database read-back. The 2016 calendar was excluded. 解婕翎《0324》, 黃沛妍《Sweet Pig》and 周曉涵’s set remain research targets.

## Older two-volume set resolved

周曉涵《BE MINE，be yours（共二冊）》was verified through Sanmin product 006468936, ISBN9789869535724. The retailer specifies 256 pages for the set. Both named books are retained as the composition of one sold edition, with the source-linked cover mirrored to R2 and persistence read back. The search was adjusted to accept the verified title without requiring the model’s name in the title; model credit still requires page evidence.

## Further older physical books

張小筑《Chu一個吧！》and 路雨希《Lucy, Blue Sea！》were verified through Sanmin product detail pages and imported with verified R2 covers. The former has 144 pages and one poster randomly supplied from two designs; the latter also specifies a poster. Database read-back confirms persistence. 林茉晶’s digital full/part editions remain queued for comparison before import.

## Hami and Kingstone verification

林茉晶《晶不起誘惑》was verified on Hami as a digital product without a part suffix. Other platforms’ separately sold parts remain pending content comparison. 艾瑞絲《Aries夏日漫步》was verified on Kingstone, with ISBN9789869596398, 144 pages and a physical format. Both covers were mirrored to R2 and database persistence verified. Hami’s shelf date was not represented as a publication date, and no retail observations were fabricated.

## Further Taiwan-market model books

何念兹《念在你身邊》and 林艾璇《數到3之後》were verified on Kingstone and Sanmin respectively, imported with verified R2 covers, and read back successfully. Both are physical editions. Earlier 林艾璇 releases and 郭書瑤’s text/photo book remain research targets; no full-series completeness claim is made.

## Older actress release

安以軒《我不乖》was verified on Sanmin, imported as a physical edition with a verified R2 cover and read back successfully. 大元《Girl Friend～元氣女友》has retailer and HIM release-history evidence but its live product response did not supply usable detail; alternate edition metadata and cover verification remain pending.

## 郭書瑤 edition discovery

《19歲的微熱》was verified and imported from Sanmin as a simplified-Chinese physical edition, explicitly marked zh-Hans. Its edition cover passed R2 checks and database persistence was verified. NCL identifies《愛．無限大》ISBN9789869355117, which remains pending product-level metadata and cover verification.

## 郭書瑤 follow-up resolved

《愛，無限大∞》was located in the Sanmin author catalog, matched to ISBN9789869355117, and imported as a distinct physical text-and-photo work with its verified R2 cover. Database read-back confirms persistence. The earlier pending product lookup is resolved; full publication history remains under research.

## 簡懿佳 publisher/retailer follow-up

《簡單說懿佳》physical edition was verified through Sanmin after the publisher page failed usable live retrieval. ISBN9789575647797 and its exact cover were verified, imported and read back. Kingstone and Google Play digital products remain queued for edition-level verification.

## 簡懿佳 digital edition

Kingstone’s digital《簡單說懿佳》was verified live and imported with a separate digital edition identity and verified R2 cover, sharing the established work. Its repeated paper ISBN is not claimed as a distinct EISBN; exact digital page count and physical bonus cards remain unasserted. Database read-back confirms the edition.

## Evidence and price boundaries

Name, alias and title searches were followed by product-detail checks. Official publisher catalogs and primary retailers supplemented physical editions and bundle metadata. Where a publisher cover failed, a public retail cover was accepted only after matching the physical product identifier and model identity. Special bundles are not assigned standard-edition images merely because they share a book title.

Physical fixed asking prices, current auction bids and final sold prices remain distinct. Digital offers are platform retail prices and never populate sold listings. No qualifying final-sale observations were found in this batch. A sold counter or current price cannot establish a final transaction price.

Both `写真` and `寫真` are accepted. Individual photo cards, Japanese `生写真`, calendars, illustrated books and unrelated seller keyword mentions remain guarded against. Separately sold digital parts and shared-book cover-order editions retain distinct product identities.

## Schema and persistence

Works group related physical/digital editions when source evidence supports the relationship. Editions retain verified ISBNs, publisher, publication date, page count, variant, content summary, metadata source URL, original cover URL and R2 references when available. Unknown information stays empty.

Imports validate deterministic identities and invoke the existing ingestion validator inside one data transaction. Repeated observations are deduplicated. Reconciliation preserves earlier rows and requires matching source-product identity. Fictional demo records require `MUSEBOOKS_SEED_DEMO=true`.

## Re-run

The reusable model/alias registry is `scraper/taiwan_photobook_models.json`:

```powershell
python scraper/discover_model_catalog.py --model-file scraper/taiwan_photobook_models.json --output .tmp/catalog-discovery.json --sources bookwalker-tw readmoo-tw pubu-tw
```

Discovery has bounded page/detail budgets. Remaining cursors and specific title searches require follow-up collection. Snapshots, verified physical metadata, cover receipts, import manifests and review notes for this run are retained in ignored `.tmp/` files.

```powershell
python .tmp/finalize-more-catalog.py
python scraper/prepare_catalog_import.py --live .tmp/catalog-more-20261006-full-live.json --publisher .tmp/catalog-more-20261006-full-publisher.json --output .tmp/catalog-more-20261006-full-manifest.json --upload
```

From `backend`:

```powershell
go run ./cmd/catalog-import -manifest ../.tmp/catalog-more-20261006-full-manifest.json -apply
go run ./cmd/catalog-import -verify
```

Export the reviewed bibliography from the project root:

```powershell
python scraper/export_model_catalog.py --manifest .tmp/catalog-more-20261006-full-manifest.json --publisher .tmp/catalog-more-20261006-full-publisher.json --output scraper/taiwan-photobook-catalog.md
```

Configuration comes from `backend/.env`; credentials are not copied into manifests or reports.

## Limits and validation

This is a verified public batch, not an exhaustive publication history. Anonymous/adult-content restrictions, verification pages, unavailable publisher servers and closed self-published shops prevented some checks. No restrictions were bypassed. Older titles and missing covers are documented in the bibliography and review notes.

88 Python regression checks and Go tests passed. The database transaction committed and all public catalog pages passed physical/digital consistency and digital sold-price leakage checks. Broad full-name searches that repeatedly returned unrelated books were capped; remaining cursors and exact-title checks are preserved in the research snapshots. Application deployment was not performed.

## Publisher expansion wave 19

Two new physical titles were verified from iWIN publisher product pages: 張語芯 YUXIN CHANG 同名寫真 (ISBN 9789869947640, 144 pages, paperback, 2022-11-07) and 潘映竹 Jennifer 同名寫真書 (ISBN 9789869947626, 136 pages, hardcover, 2021-09-05). Exact publisher covers were uploaded to R2 and verified; ISBN/format collision checks passed before database import. Database readback confirms 199 physical works and 113 digital works through public handlers. Retail prices were not added as marketplace observations. Further primary-product candidates for 瑞比、子喵 and 雪岑 remain in the research queue.

## Publisher expansion wave 20

Verified and imported 瑞比RABY 同名寫真 (ISBN9789869947671, paperback,144pages,2023-05-06) and 〈雪之下．岑之名〉SNOWY雪岑首部同名寫真詩集 (ISBN9786269273317,standard paperback without dust jacket,2025-12-24). Current publisher specifies152pages for Snowy versus144 in NCL registration; discrepancy retained in edition composition. Two exact cover objects uploaded and verified in R2. Both ISBN/format checks passed before import. 子喵 bundle page confirms book composition but is pending standalone-cover verification.

## Publisher expansion wave 21

Imported 夏涵芝CHIH同名寫真 (ISBN9789869947688,144pages) and 〈庭在一瞬間〉瑋庭Angela寫真書 (ISBN9789869947695,144pages,2024-03-14). Both are physical paperbacks with verified publisher covers uploaded to R2. 夏涵芝 publication date remains unknown because publisher2023 conflicts with NCL2024; title/description disagree on dust jacket inclusion, recorded in composition. ISBN collision checks passed before import. Further exclusive covers and new publisher model products remain queued.

## Publisher expansion wave 22

Imported 美家MIGA 2025 PHOTO BOOK (152pages,2025-07-14) and 芷想被你收藏Candy芷媗首本個人實體寫真 (144pages,2025-10-23). Both are published physical paperbacks without dust jackets,180×256×12mm,first print. Publisher pages omit ISBN; those fields remain blank. Model/title/format and edition-ID collision checks passed before import. Two exact publisher cover objects were uploaded and verified in R2. No marketplace price observations were inferred from publisher retail prices.

## Publisher expansion wave 23

Imported three physical books from exact standalone publisher pages: KONEKO子喵同名寫真 (152pages,second printing,ISBN9789869947664), 敏綺Miki同名寫真 (144pages,full edition,2025-07-07) and 凱蒂老師Teacher Keidi同名寫真 (144pages,standard paperback,2024-04-22,ISBN9786269847303). Three exact covers uploaded and verified in R2; collision checks passed before import. 子喵 second-printing date remains unknown; publisher lists original release2022-12-24. 敏綺 publisher omits ISBN and contains an older promotional date conflicting with current specifications; discrepancy retained. Seven model category pages checked and further 林可/陳鈺勳 products preserved in queue.

## Publisher expansion wave 24

Imported 林可《可。已愛》original (2021-12-20) and second printing (2022-10-08), both152pages with ISBN9789869947633 and one shared work. Imported 陳鈺勳《色鈺勳心》and《鈺求不滿》as distinct64page physical books,2025-04-14; their publisher ISBN fields are blank. Four editions,three works added after prior-catalog collision checks. Exact publisher cover images mirrored to R2. No bundle or physical-retail price was treated as a marketplace transaction.

## Publisher expansion wave 25

Imported 雙囍〈囍歡你〉2025同名寫真,ISBN9786269847341,144pages,paperback with standard dust jacket,2025-02-14. Exact cover uploaded and verified in R2; ISBN collision check passed. Eight further publisher categories inspected; standalone/group books and variant candidates are saved in the queue. 托托 product is credited Sutin托托; cross-name identity must be reviewed before import.

## Publisher expansion wave 26

Imported 黎茉 MINI肉包《唯。愛》,140pages,paperback,2022-09-21, and Just A dReam,56pages,hardcover,2022-05-20. Shared book credits are 啾啾JoJo、學長Abby、瑞咪Rami; one work appears under each credit in the bibliography. Exact publisher covers uploaded and verified in R2. Missing ISBNs remain blank. Database readback verifies188physical and90digital public works.

## Publisher expansion wave 27

Imported Sutin托托2025聯名迷你寫真,16pages,A5(150×210mm),saddle stitched,no dust jacket,2025-01-01. Separate standalone physical publication; calendar and NFC cards excluded. Exact cover verified in R2 before database import. Publisher omits ISBN. 胎尼 standard/special products remain pending author-credit review.

## Publisher expansion wave28

Imported 胎尼Tiny《TENY》80page hardcover and96page special glue-bound edition as one work with two editions. Both A4,210×297×6mm,without dust jacket. Special edition adds photos/pages and redesign. Publisher category explicitly identifies Tiny胎尼. ISBN and publication dates remain unconfirmed. Exact covers uploaded and verified in R2 before import; distinct edition and shared-work checks passed.

## Publisher expansion wave29

Imported 張若錡《錡遇Angus》墾丁 and高雄 physical144page volumes,2019-05 month precision. 高雄ISBN9789887738701;墾丁4717095581913 is a retail barcode and was not placed in ISBN. Publisher bonus composition retained. Four merchandise products excluded. Both exact publisher covers verified in R2 before import. Taiwan-market model credit; publisher biography identifies Hong Kong origin. Digital upper/lower-volume candidates preserved for independent composition review.

## Digital expansion wave30

Imported 張若錡《錡遇Angus》墾丁上冊 and下冊 from GooglePlay,each116pages. Explicit電子出版2020-06-21 retained instead of original paper date. Exact per-volume covers uploaded and verified in R2. ISBN unknown; physical full-volume equivalence unconfirmed. No GooglePlay recurring price worker or offer configured in this metadata batch.

## Shared photobook expansion wave31

Imported 貓樣女孩 太平洋の味,168page hardcover,ISBN9789869947619,2020-10-01,featuring 馨馨、李岱倫、雪岑、柯姿、張安娜. Publisher lists five cover variants under the same title and ISBN; one shared work with five editions. All five exact covers uploaded and verified in R2. Preflight passed and importer confirmed database transaction committed. Catalog export confirms263current works and308editions. Post-import database readback was not executed because automatic approval review could not complete after account usage limit was reached; public-handler counts above remain from wave30.

## Import wave36 and restored verification

Approval review became available. Wave31 post-import readback passed, then four physical editions were imported: 希兒Angel standard and special, 舒舒19歲寫真(160pages), 鄭羽凡其實我有點壞(128pages). Exact covers verified in R2; collision checks passed. 希兒 editions share one work. Final database readback passed:268totalworks319totaleditions; current export266works312editions; public196physical92digitalworks. Historical review failure is resolved.

## Wave 37 — digital Angel

希兒《Angel》144-page fixed-layout EPUB, released 2022-04-29 on BOOKWALKER, was saved with its exact verified R2 product cover and linked to the existing physical work. Physical special-edition gifts are excluded from ebook contents. Database readback confirmed 313 current editions, including 99 digital editions.

## Wave 38 — further research

夏蕾《心動蕾達》fixed-layout EPUB (EISBN 9786264446433, publication 2026-09-18; online date 2026-09-22) saved with exact R2 cover. The existing physical gift box remains separate pending content equivalence review. Database readback passed. 禾羽《禾你相羽》ebook is retailer-verified but direct fetch returned 403; no record or cover was guessed. Official 2026 Okinawa product page confirms book-only and gift-set contents; release metadata and individual covers remain under review.

## Wave 39 — physical editions

Imported 夏蕾《心動蕾達》standard paperback (ISBN 9786264446549, 144 pages, 2026-09-18, random one-of-two poster), sharing the verified ebook work via the explicitly identified print ISBN on the ebook source. Imported 禾羽《2026 禾你相羽 in Okinawa》general and collector editions as one work with separate contents. Official cover image is a gift-set collage, so both individual covers remain pending. Unknown ISBN, page count and publication date were omitted; 2026-09-15 is expected shipping only. 四套精裝收藏組 is a four-copy purchase bundle rather than an additional book edition. Database readback confirmed all three editions. 禾羽 is a credit label also associated with 張雅涵, not an additional unique person claim. 周感恩 Thank You was checked and already exists under ISBN 9786269687787; no duplicate added.

## Waves 40–41 — five digital records

Saved 禾羽《禾你相羽》from PChome Kobo product DJBQ2E-D900JY2UU, release 2026-05-20. Kobo public search also verifies fixed-layout EPUB3; direct Kobo fetch returned 403 and was skipped. Retail identifier 7640000000001 was not inserted as ISBN. This is the earlier title, separate from 2026 Okinawa. Saved 芳婷《Heartbeat》200-page ebook (Google Play 2018-05, month precision) and 蔡譯心《打開你的心》147-page ebook (Google Play 2020-04, month precision). TAAZE lists a different date for its digital product; platform-specific dates are recorded explicitly rather than copied from print. Saved 大萌妹子同名數位寫真 (fixed-layout EPUB, 9789571095868, 2020-01-23) and 鍾以希《Rainylove》(fixed-layout EPUB, 9789571095790, 2020-05-11). All five exact covers passed R2 verification and all database readbacks passed. No Google Play/PChome price worker was configured or implied by these metadata imports.

## Wave 42 — three model EPUB editions

Imported 張鳳如《如影隨形》(EPUB EISBN9789571095059, 2018-08-03), 徐韻庭《凝望 Mika》(EPUB EISBN9789571095318, 2018-11-08) and 王寶珶《抽象畫》(EPUB EISBN9789571095325, 2018-12-07). All exact retailer covers passed R2 verification and database readback passed. 王寶珶 follows retailer and publisher spelling; NCL 王寶璋 discrepancy is recorded in the edition summary. 抽象畫 includes artwork and making-of video, explicitly confirmed by retailer. Google Play 如影隨形 has a separately described 195-page video edition, so its page count was not copied to the unverified cross-platform composition.

## Wave 43 — 詩雅 and 寧寧

Saved 詩雅《一起上課吧！》EPUB版式 EISBN9789571095103, release2018-07-20, with exact 三民 product cover. Saved 寧寧《不能錯過寧》Google Play270-page ebook, platform date2020-09 with month precision; ISBN unknown. It incorporates past calendar photographs with new material but is an ebook rather than a calendar product. Both exact covers passed R2 verification; database readback passed. 優菈YOLA51-page ebook identified for next import; 巫艾蓁 remains an NCL-registration lead pending retailer detail.

## Wave 44 — UPlive individual photobooks

Saved 優菈《鄰家女孩型直播主》51 pages, mi（UPlive）《酷艷教主》39 pages and 糖果（UPlive）《甜美萌主》31 pages. Publisher擎天創意科技股份有限公司; all Google Play products explicitly ebooks dated2021-02 with month precision. Exact covers passed R2 verification and database readback passed. ISBN, video and platform-specific file format are unconfirmed. Publisher-scoped credits prevent merging unrelated people with short stage names; TW means Taiwan retail market, not a claim of nationality. Hami catalog additionally lists 小花Flower and 嵐嵐LAN LAN individual photobooks for further product-page review.

## Wave 45 — Flower and LAN LAN

Saved 小花（UPlive）《冷豔御姐型直播主》17-page ebook and 嵐嵐（UPlive）《蜜糖型直播主》21-page ebook from individually verified Google Play products. Both dates2021-02 with month precision; unknown ISBN and video retained as unknown. Publisher擎天創意科技股份有限公司. Exact covers passed R2 verification and database readback passed. Stage-name credits are publisher scoped and do not assert nationality. 心玥《傾城之玥》retailer ebook product identified for next review.

## Wave 46 — 心玥 and 夏晴

Saved 心玥《傾城之玥》147-page Google Play ebook; description separately claims128 pages of photography, retained without assuming another edition. Saved 夏晴《天使と悪魔》146-page ebook, with credited identity張舒晴／夏晴 from product author text. Both platform dates2022-04 with month precision; ISBN and video unknown. Exact covers passed R2 checks and database readback passed. 誠品 confirms separate paperback26×19.5×0.6cm titled2021個人寫真 but direct collection failed identity parsing; physical cover and release details remain pending. Publisher series《女神降臨1/2》has new shared model credits requiring review before import.

## Wave 47 — 女神降臨 shared books

Saved two distinct Google Play162-page digital volumes, each2022-04 with month precision, publisher天禾娛樂事業股份有限公司, 洪逸民攝影. Volume1 credits黃鈺文、潘維亞、哈霓萱、凱蒂兒、安妃、雪兒（女神降臨）. Volume2 credits多麗Doris（女神降臨）、莎莎（女神降臨）、Yvonne（女神降臨）、花苡琍、徐瑜瑜、麗莎（女神降臨）. All credits are directly named in the publisher product descriptions; short names are series scoped, not asserted as canonical legal identities or additional unique people. Both exact covers passed R2 verification and database readback passed. Each volume appears under its six participants in the bibliography but is one catalog work and edition. ISBN, video and individual-model page allocations remain unknown. TAAZE lists fixed-layout volume2 with2022-04-08; Google Play date retained at its published month precision.

## Wave 48 — 夏晴 paperback

Saved 誠品 paperback《天使と悪魔：女神系甜心夏晴2021個人寫真》26×19.5×0.6cm. The exact image linked by the retailer was visually verified and passed R2 checks. Embedded storefront metadata was not available to the simple collector; primary retailer web extraction provided title, binding, dimensions and identity, retained in reviewed publisher input. Printed2021 is in title/cover; no precise release date or page count invented. Store26碼2682029947009 is not ISBN. Cross-format interior equivalence remains unconfirmed, so this physical work is separate from the146-page ebook. Database readback passed.

## Research batch 49

Added 成語蕎《成語蕎同名寫真》: physical paperback, ISBN 9789869316774, released 2016-11-16, 160 pages, 28 × 21 cm. Kingstone verifies a Malaysia island shoot and more than 20 looks. Its exact cover passed R2 verification and the edition was committed to PostgreSQL and read back. 梁凱莉《禮物書》was excluded because the listed contents are a calendar and merchandise, without a standalone photobook. Further leads: 成語蕎《另一個我/a new chapter》寫真＋EP B款 (Kingstone 2019500058167) and 李馨CinCin -ShaShin celeb present寫真書 (Apple Books 1564890878); neither is imported yet.

## Research batch 50

Added 成語蕎《另一個我/a new chapter》寫真＋EP B款首刷限量版: ISBN 9789869667425, 128 pages, 28 × 21 cm, released 2018-08-30, with EP and white-dress standee. Exact retailer cover verified in R2; PostgreSQL import and readback succeeded. Kingstone marks this edition discontinued; no active or sold offer was created. Apple Books abbreviated URL did not resolve the 李馨 identity, so the digital lead remains pending.

## Research batch 51

Added 愛語莎Vanessa - ShaShin celeb present寫真書, a digital edition verified through Kingstone 2800000161189, released there on 2020-12-17, publisher 創笙國際股份有限公司. Winter-garden photography with an Airstream camper and flower-art setting directed by 顔于亭. Placeholder zero pages and paper dimensions were excluded. Exact cover passed R2 verification, with PostgreSQL import and readback successful. 莙莙Queena Kobo retailer returned 403; it remains pending and no verification barrier was bypassed.

## Research batch 52

Added 小林兒Royi -ShaShin celeb present寫真書 through Sanmin 015876978, EPUB fixed-layout digital edition dated 2021-01-06, themed around Indian Motorcycle photography. Exact cover verified in R2 and edition imported to PostgreSQL. Product code 2222222870850 is not ISBN. Other retailers date it 2020-12-17; no print-equivalence claim was made. BOOKWALKER returned 403 and Apple pages did not expose identity metadata. Further accessible lead: 李馨 HyRead PChome DJBR5I-D900IKYFO.

## Research batch 53

Added 莙莙Queena ShaShin digital photobook (Sanmin 015876979, EPUB fixed-layout, 2021-01-06) and 李馨CinCin ShaShin HyRead digital photobook (PChome DJBR5I-D900IKYFO, JPG, platform date 2020-12-01). Composition records Bentley Continental GT W12 / Steve Madden for 莙莙 and Beats / Steve Madden for 李馨. Exact covers passed R2 verification, both records committed and read back in PostgreSQL. Retailer product codes were not treated as ISBN. No physical equivalence or transaction-price claim was created.

## Research batch 54

Added ShaShin celeb present 4 in 1 digital collection (PChome Kobo DJBQ2E-D900DT3DQ, 2020-12-17, EPUB3 fixed-layout) with all four confirmed model credits: 愛語莎Vanessa、李馨、莙莙Queena、小林兒. One shared work, without unverified individual page counts or complete reprint claims. Added 凱琪 K7 X ShaShin Winner Winner 2020個人寫真書 (Sanmin 015876982, 2021-01-08, EPUB fixed-layout). Platform identifiers excluded from ISBN. Both exact covers verified through R2 and both DB imports/readbacks succeeded.

## Research batch 55

Added 林祐青ViVi Lin首本個人寫真書, physical paperback, ISBN 9786269687718, 80 pages, 29.7 × 21 × 0.6 cm, Sanmin release 2023-05-15. Exact cover passed R2 checks; PostgreSQL import/readback succeeded. Promotional mention of calendar/poster did not establish this edition's included extras. 徐薇涵 UDN page did not expose sufficient identity metadata and remains pending. Further publisher leads include Vivi digital, 陳禹霏 FAIRY digital, 唐明翎小精翎愛妮科隆之旅 and 願願願你擁有.

## Research batch 56

Added 願願Yuan 願你擁有 physical hardcover (Sanmin 011299119, ISBN 9786269687701, 112 pages, 2022-12-26) and EPUB fixed-layout digital (015876394, 2024-09-27), plus 林祐青ViVi digital (015876347, 2024-08-30). Three exact R2 covers verified; PostgreSQL imports/readbacks succeeded. Formats remain separate works until contents equivalence is verified. Sanmin 陳禹霏 digital 015876349 was withheld because its description and model Instagram instead credit 周昕; raw conflicting evidence retained. No extra calendar/poster inclusion inferred.

## Research batch 57

Added FAIRY陳禹霏 HyRead fixed-layout EPUB through PChome DJBR1V-D900IQ9SB, platform date 2024-09-01. Consistent author credit and nine-look description resolve the digital lead independently of Sanmin's erroneous 周昕 description. Exact cover passed R2 verification; DB import/readback succeeded. Page count and full print equivalence remain unconfirmed. 唐明翎 博客來 E050121645 now returns 404 and remains pending.

## Research batch 58

Added 海豚 徐薇涵 X Little Journey 首本個人寫真 digital edition through Kingstone 2800000212568, date 2021-06-05. Exact cover verified in R2, DB import/readback succeeded. Page count, file format and included video remain unknown; placeholder zero pages/paper dimensions excluded. UDN lists a separate online-publication date; not copied as this retailer edition date. 唐明翎 alternate source still pending.

## Research batch 59

Added KiKi謝立琪 ShaShin個人寫真書2022 digital edition, Sanmin 015876348, EPUB fixed-layout, platform publication 2024-09-01. Seven looks/themes recorded; title year retained separately from digital release date. Exact R2 cover verified and PostgreSQL import/readback succeeded. Distinct from existing 2019 琪幻夢遊. Printed 2022 book ISBN 9789860635096 is a separate pending retailer-verification lead; not assigned to this ebook. 唐明翎 remains pending despite an Apple Books search result.

## Research batch 60

Added 謝立琪 KiKi 2022個人寫真 ShaShin physical retailer edition through Sanmin 010436145, ISBN 9789860635096, 112 pages, 2022-04-25, 29.7 × 21 × 0.7 cm. Retailers label paperback but NCL deposit labels hardcover; discrepancy preserved without inventing a second variant. Exact R2 cover verified; PostgreSQL import/readback succeeded. Full physical/digital contents equivalence remains unconfirmed.

## Research batch 61

Added 祈錦鈅 MAXINE：首本個人寫真, physical paperback through Sanmin 009186075, ISBN 9789860635003, 128 pages, 2021-05-14, 29.7 × 21 × 0.9 cm. Sport/sunlight photography and brand collaborations recorded; extras unknown. Exact R2 cover verified and PostgreSQL import/readback succeeded. Digital MAXINE and 不祈而遇 remain pending verification.

## Resumed batch 62

Imported 鄭若青’s physical 12 Secrets (128 pages, hardcover, ISBN 9789860635072) and 祈錦鈅’s digital 不祈而遇 (2024-09-10). Two exact covers passed R2 verification. Database readback passed; digital page count and file format remain unconfirmed.

## Research batch 63

Imported 祈錦鈅’s ShaShin-Maxine digital edition from Sanmin: 2022-10-15, fixed-layout EPUB. Its exact cover passed R2 verification and database readback passed. Retailer product code 2222222870928 is not an ISBN. Physical/digital interior equivalence is unconfirmed, so works remain separate. No price observation was created by this metadata import.

## Research batch 64

Imported 吳慈敏（啾啾）啾啾2023寫真書: hardcover, 208 pages, ISBN 9786269687763, 30.3 × 21.6 × 1.2 cm, ten styled photo sets. Kingstone dates publication 2024-07-12 despite the title year. Exact cover passed R2 verification and database readback passed. No transaction or active-price observation was inferred. 吳慈敏 is not merged with the separate 啾啾JoJo credit without identity evidence.

## Research batch 65

Imported three 吳慈敏（啾啾）books: 2021 hardcover (200 pages, dual covers and 2022 desk calendar, ISBN 9789860635089, retailer date 2022-01-25); 2022 hardcover (194 pages, ISBN 9786269687725, retailer date 2023-04-07); and 2020 digital-only fixed-layout EPUB (retailer date 2022-01-27). Title years are preserved separately from retailer publication dates. Three exact covers passed R2 checks; database verification passed. TCSB returned 403, so accessible Sanmin evidence was used for the 2021 book. Digital product code 2222222870911 is not an ISBN.

## Research batch 66

Imported 翁子涵 ZIHAN WENG：「Z」紀念寫真, Taiwan edition, 80 pages, ISBN 9789860635065, 21 × 29.7 cm. Accessible Asia Music Shop primary metadata lists release 2022-01-21 and eyewear collection photography; NCL deposit record supports paperback. Exact retailer cover passed R2 checks. FANCY GREEN has a distinct ISBN 9789860635010 and remains pending because its direct retailer fetch returned 403. No retail or sold-price observation was inferred.

## Research batch 67 — unresolved series evidence

Reviewed 甄馨、安生、陳葳 leads against the existing catalog and avoided duplicate imports. Added five 許瑜 series leads to the research queue. A Ruten seller describes 夏の瑜 as an A4 32-page book with nine outfits in a merchandise bundle; these remain seller-reported, unconfirmed metadata and are not committed as verified catalog data. FANCY GREEN has a date conflict: original-book reporting in 2019 versus ISBN-linked retailer date 2021-06-04. No new DB edition, offer or R2 upload in this research-only batch.

## Research batch 68

Imported 郭郭寫真書：RAINY SUMMER SECRETS（小卡親簽版） from live Sanmin metadata: ISBN 9786267742167, 120 pages, 水靈文創, 2025-09-29. Vietnam Phu Quoc photography; one signed card from three random designs included. Exact cover passed R2 checks and import transaction committed. Companion 林采婕 title already exists, so no duplicate imported. 許瑜 official product evidence remains pending.

## Research batch 69 — announced photobook

Added 劉芷伊 芷想靠近你：劉芷伊醫師寫真, ISBN 9786264444811, 144-page paperback, 時報文化. Live Sanmin page on 2026-10-06 explicitly says preorder with scheduled publication 2026-10-09; summaries retain that status and actual release is unverified. Includes one 30 × 42 cm poster randomly selected from two designs. Exact announced cover passed R2 checks; DB transaction committed. Counts include announced editions, not only released books. Newest search also contains calendars and non-model photography books; these were not imported.

## Research batch 70

Imported TAKA：深夜名堂男子寫真, Japanese model in Taiwan-market publication: 144-page paperback, ISBN 9786264681902, 台灣角川, 2026-09-16, 25.6 × 18 × 1 cm. Tainan/Kenting photography; A3 folded poster, two random designs, first printing only while supplies last. Exact cover passed R2 checks and transaction committed. Sanmin returned an empty response, so live Kingstone metadata was used. A Japanese Yahoo Flea Market sold page z693719218 displays ¥6,100 and purchase time 2026-09-28 13:30 in web retrieval; queued for direct scraper validation, no sold observation imported.

## Research batch 71 — TOKKI CUTIE

Imported physical boxed FIRST JUMP (ISBN 9786267776919, 176 pages) and EPUB (EISBN 9786267776926), retailer dates 2026-04-30. Print box contains three nonduplicate random cards, one mini poster, one charm and one sliding card holder, each from 16 designs. Digital metadata does not inherit physical extras. The team official article https://eastpower.tw/6177 names all 16 participants; each receives a scoped TOKKI CUTIE／name credit to avoid merging ambiguous short names with unrelated models. Exact covers passed R2 checks; DB transaction committed. Full print/digital interior equivalence remains unverified, so source-generated works remain separate pending reconciliation.

## Research batch 72

Imported 向理來 向你走來 physical ISBN 9786264446723 (168 pages, paperback, 23 × 17 × 0.8 cm) and digital EISBN 9786264446600; both retailer dates 2026-06-12. Taiwan photography; print description confirms seven outfits and personal interview. Digital page count and video content unconfirmed. Two exact covers passed R2 checks and database verification passed. Full format equivalence remains unverified; source work identities are retained. SHOYA page failed identity verification and remains pending.

## Research batch 73

Imported 慾見SHOYA：筋肉教練寫真 from publisher primary metadata, ISBN 9786264359313, 2026-01-22. Kingstone confirms 160-page paperback, 25.6 × 18 × 1 cm. Taipei/Danshui photography by XXDanieL; first-print A3 folded poster, two random designs. Kingstone image was generic restricted.jpg and was rejected before import; exact publisher cover passed R2 checks. DB verification passed. Kobo ebook source returns 403; no digital edition imported.

## Research batch 74 — digital metadata and cover guard

Live Kingstone SHOYA ebook page 2800000224255 confirms digital retail availability but repeats physical specifications and returns restricted.jpg as its image. Digital record is held out of DB pending exact cover/ebook identifiers. prepare_catalog_import.py now rejects that known generic Kingstone placeholder before cache lookup or R2 upload; local preparation verified review output and empty cover references. No new DB record or R2 upload in this batch.

## Research batch 74 — SHOYA digital edition

Added SHOYA’s digital edition of 慾見SHOYA：筋肉教練寫真 from the Readmoo primary page. It has EISBN 9786264450362, release date 2026-01-30, EPUB 3 fixed layout, file size 74 MB, and its own exact cover. The physical ISBN 9786264359313 and 2026-01-22 release date remain on the paperback edition; print page count and dimensions were removed from digital metadata. Both editions share the verified work identity. The Readmoo cover passed R2 upload checks and the database importer accepted the linked edition. The Kingstone generic restricted image was rejected and is guarded in prepare_catalog_import.py.


## Research batch 75 — 阿部瑪利亞

Added the physical and EPUB editions of《半分 はんぶん：阿部瑪利亞寫真》to one work. Sanmin confirms physical ISBN 9786264199285, 128 pages, 28 × 21 × 0.95 cm, and a random collector card (two designs); its ebook uses EISBN 9786264199193, EPUB fixed layout, and carries no print-only dimensions or card. Both editions are dated 2025-11-07 and have separate exact covers in R2. Sources: [print](https://www.sanmin.com.tw/product/index/014936599), [ebook](https://www.sanmin.com.tw/product/index/015064155).

## Research batch 76 — YURI／陳洛心

Added the 160-page《洛入你心》心動凝望書封版 (ISBN 9786264196444, with a 30 × 42 cm poster) and EPUB edition (EISBN 9786264196291) to the already catalogued work for the same model. Sanmin’s current-name author bio links 陳洛心/YURI to her earlier 陳怡叡 credit. Readmoo lists 40 bonus photos for the ebook; paper poster details remain on the print edition. Both exact covers are in R2. Sources: [print](https://www.sanmin.com.tw/product/index/014813838), [ebook](https://www.sanmin.com.tw/product/index/014791167), [Readmoo bonus details](https://reading.udn.com/ebook/store/store_product.do?pid=45773), [name-change reporting](https://www.ftvnews.com.tw/news/detail/2025102W0411).

## Research batch 77 — 寶兒

Added the EPUB edition of《Babe Fantasy‧寶兒寫真書》to its existing physical work. Sanmin gives EISBN 9786267683781 and EPUB format; National Central Library deposit data confirms the same EPUB identifier. The print edition remains 160 pages with its random poster; no print page count, poster or box accessories were carried into the ebook. Exact digital cover uploaded to R2. Sources: [Sanmin ebook](https://www.sanmin.com.tw/product/index/015552499), [National Central Library ISBN record](https://isbn.ncl.edu.tw/FCKEDITOR_UploadFiles/1760932966.pdf).


## Research batch 78 — 妮可／Nicole

Added the missing 144-page physical edition of《想見妮‧Nicole妮可寫真書》(ISBN 9786267683088) to the existing ebook work. Sanmin confirms 26 × 18.5 × 1.1 cm, photographer 陳伸維, and one 33 × 49 cm poster randomly selected from four designs. The publisher storefront dates the book 2025-04-29; Sanmin’s retail record shows 2025-05-02, so the catalog keeps the publisher date and records the retailer date as a source discrepancy. The existing digital record has EISBN 9786267683064 and EPUB fixed layout; no physical page count, dimensions or poster are copied to it. Exact print cover is in R2, and both format ISBNs were read back under the same work ID after database import. Sources: [Sanmin print](https://www.sanmin.com.tw/product/index/014272084), [Cite publisher storefront](https://www.cite.com.tw/book?id=103389), [Sanmin ebook](https://www.sanmin.com.tw/product/index/014381528).


## Research batch 79 — 邊荷律、李雅英、李珠珢

Added seven physical/digital editions across three catalog works, each with an exact cover mirrored to R2. 邊荷律 has a 176-page paperback (ISBN 9786264550413) and separate hardcover collector set (SPP code 3F000064, barcode 4717702300906); its collector barcode is not an ISBN, and page count/cm dimensions remain unconfirmed. The paperback includes two random gold cards from eight designs; the collector set adds a 160 × 50 cm pillow cover (no insert), film-roll keychain and four random cards. No digital edition was found; candidate EISBN 9786263399266 collides with an unrelated Kobo book and was excluded. Sources: [Sanmin standard edition](https://www.sanmin.com.tw/product/index/015514569), [SPP collector edition](https://www.spp.com.tw/SalePage/Index/11579526), [collector contents report](https://www.ebc.net.tw/entertainment/entertainment-news/489671).

李雅英 has a 176-page paperback (ISBN 9786264349130), SPP hardcover collector set (code 3F000059, barcode 4717702300647), and EPUB fixed-layout digital edition (EISBN 9786264551892). The EPUB contains 272 new photos absent from print plus backstage video; it has its own cover and no print page/dimension/card metadata. Collector contents include a pillow cover, card sleeve and photo-card series; card quantity per set is not stated. Sources: [Sanmin paperback](https://www.sanmin.com.tw/product/index/015267268), [SPP collector edition](https://www.spp.com.tw/SalePage/Index/11508984), [Sanmin EPUB](https://www.sanmin.com.tw/product/index/015487069).

李珠珢 has the 176-page paperback (ISBN 9786264342247) and hardcover collector edition (ISBN 9786264342254). Both share interior photo content; binding and included items are edition-specific. The collector edition adds the accessory box, 160 × 50 cm pillow cover (no insert), 18 × 6 cm liquid bookmark, and four laser-gold cards. NCL deposit data supports the ISBN/page count/28 cm format; the cover image and bonus details came from publisher-supplied press material because SPP's original time-limited presale page is no longer available. The listed publication date is 2025-09-02; the publisher later announced delayed shipping from 2025-10-28. No digital Taiwan retail edition was verified. Sources: [Sanmin paperback](https://www.sanmin.com.tw/product/index/014740702), [NCL hardcover ISBN deposit](https://isbn.ncl.edu.tw/FCKEDITOR_UploadFiles/1752563403.pdf), [publisher-supplied cover and contents](https://www.popdaily.com.tw/press/1562350?is_app=true), [shipping-delay report](https://news.ebc.net.tw/news/sport/517034).



## Research batch 80 — 冰熙、葉魚魚

Added nine Fan520 editions across nine works: one physical booklet and eight digital PDF photobooks. Each edition has its own exact product cover mirrored to R2; the batch created no active-price or sold-price observations. 冰熙’s official Linktree connects her to the seller profile, which lists a 2001-10-22 birth date. Her physical《616見面會小相本》is a 32-page, 15 × 15 cm hardcover. Two separate digital titles are listed: one says 148 pages or more and includes a 3:47 video; the other includes a 4:41 video, with page count unspecified. Sources: [BingShi Linktree](https://linktr.ee/bingshibabycosplay), [Fan520 profile](https://www.fan520.net/pages/bingbabybaby), [physical booklet](https://www.fan520.net/products/0616c1a), [digital A](https://www.fan520.net/products/bingbabybaby-121801), [digital B](https://www.fan520.net/products/bingbabybaby-0707).

Fan520’s model page, dedicated category and the model’s Linktree corroborate 葉魚魚 / 魚魚 as one identity. Six distinct digital product pages were added. Two state 144 and 130 pages respectively; two alphabetic series items and two standalone releases do not state page counts. Video bonuses are recorded only where the seller/category page states them. No print dimensions, ISBNs or release dates were inferred for these digital editions. Sources: [Fan520 profile](https://www.fan520.net/pages/fishyea), [dedicated category](https://www.fan520.net/categories/yea-fish), [official Linktree](https://linktr.ee/fish0303), [series A](https://www.fan520.net/products/fishyea33-2023062101), [series B](https://www.fan520.net/products/fishyea33-2082401), [series C](https://www.fan520.net/products/fishyea33-2023101401), [series D](https://www.fan520.net/products/fishyea33-2023111301), [standalone release 1](https://www.fan520.net/products/fish0824), [standalone release 2](https://www.fan520.net/products/fish08a).



## Research batch 81 — 楊宇騰YU、鄔又曦、椎名心春、北野未奈、汐世、龍夢柔

Added 13 editions across nine new works for six models. All 13 exact product covers were mirrored to R2; this metadata batch created no active or sold price observations.

楊宇騰YU has three separate Taiwan-market works.《Half》now has a 128-page print edition (ISBN 9789865244750) and an EPUB special edition (EISBN 9789865244767).《光影之間》has the 128-page standard print edition (ISBN 9786263219106), the separately packaged KADOKAWA special set (barcode 4711289612094 is not an ISBN; book page count/specs were not stated for the set), and a BOOK☆WALKER Taiwan digital edition with its own cover. The electronic listing does not disclose an EISBN or digital pagination, and print extras remain edition-specific.《vs YU》is a 200-page Taiwan Tohan anniversary photobook (ISBN 9786264370493) with Taipei photography, archives and interviews. Sources: [KADOKAWA Half print](https://www.kadokawa.com.tw/zh-hant/products/9789865244750), [Airiti Half EPUB](https://www.airitibooks.com/Publication/Details?publicationID=P20220110162), [Sanmin 光影之間](https://www.sanmin.com.tw/product/index/010843105), [KADOKAWA special set](https://www.kadokawa.com.tw/products/4711289612094), [BOOK☆WALKER digital edition](https://www.bookwalker.com.tw/product/154263), [Taiwan Tohan vs YU](https://www.tohan.com.tw/product.php?act=view&id=8279).

鄔又曦／克萊兒 has the 128-page《像我一樣甜：克萊兒甜心日記》(ISBN 9786269640621), a physical sweet-themed photobook documenting different sides of the creator. Dimensions are 26 × 18 × 0.7 cm; no format-specific digital edition was verified. Source: [Eslite](https://www.eslite.com/product/1001261682682283023006).

椎名心春 has two distinct original Taiwan photo books:《海味》(ISBN 9786269973460; sea/outdoor settings) and《山珍》(ISBN 9786269973477; mountain/indoor settings), each 128 pages.《山珍》also has a Google Play digital-limited edition listing 270 ebook pages and 137 additional photos; no EISBN is listed, and no print size or physical bonuses were copied to it. No digital《海味》edition was verified. Sources: [Kingstone 海味](https://www.kingstone.com.tw/basic/2019910058511/), [Kingstone 山珍](https://www.kingstone.com.tw/basic/2019910058481/), [Google Play 山珍 digital](https://play.google.com/store/books/details/%E6%A4%8E%E5%90%8D%E5%BF%83%E6%98%A5_%E6%A4%8E%E5%90%8D%E5%BF%83%E6%98%A5%E5%8F%B0%E7%81%A3%E5%AF%AB%E7%9C%9F%E9%9B%86_%E5%B1%B1%E7%8F%8D_%E6%95%B8%E4%BD%8D%E9%99%90%E5%AE%9A%E7%89%88?id=exkBEgAAQBAJ), [NCL October 2025 deposit list](https://isbn.ncl.edu.tw/FCKEDITOR_UploadFiles/1763434068.pdf). Retailers differ on the public release day for the two print volumes; the record keeps the publisher/TAAZE date and the research source list retains the deposit and retail evidence.

北野未奈 has《Look at Me》(ISBN 9786269294817), a 112-page physical Taiwan edition photographed by 野澤亘伸. A retailer page exposes an eBook option on a shared product record, but the accessible metadata did not expose a file-specific identifier or separate digital cover, so only the verified physical edition was added. Sources: [Kingstone](https://www.kingstone.com.tw/basic/2019000171908/), [Momo exact cover listing](https://www.momoshop.com.tw/product/15076992), [NCL deposit record](https://isbn.ncl.edu.tw/FCKEDITOR_UploadFiles/1771918869.pdf).

汐世 has the 112-page《愛之炎》(ISBN 9786269294800), a physical first photobook photographed by 柳沢康太. Sources: [TAAZE](https://www.taaze.tw/products/11101087042.html), [NCL deposit record](https://isbn.ncl.edu.tw/FCKEDITOR_UploadFiles/1771918869.pdf), [Momo product listing](https://www.momoshop.com.tw/product/15076991).

龍夢柔 has the 128-page《龍夢柔寫真集 1st Photo Book「夢」》(ISBN 9789869944670), photographed by 小暮和音. The book uses Japanese school-life settings including the school commute, classroom, classes, sports and after-school scenes. Source: [Kingstone](https://www.kingstone.com.tw/basic/2019910046280/), [NCL deposit record](https://isbn.ncl.edu.tw/FCKEDITOR_UploadFiles/1615610686.pdf).



## Research batch 82 — digital titles, new physical releases, and cover recovery

Added seven previously unrepresented photo-book works and nine editions, then enriched one existing Candy edition. Five new digital editions and four new physical editions are kept in their own format records. Eight older editions whose source images were already known but had no R2 cover link now have verified public R2 covers; their edition IDs were preserved. The importer verified all 18 edition rows, and the database readback reports zero editions with pending covers. This batch created no price observations, so digital retail prices and physical active/sold marketplace prices still need a separate live collection.

林莎’s《Honey》is recorded as physical-only, with a standalone second-print book and a separate limited merchandise bundle. The artist’s statement and release report say there is no digital edition; the marketplace bundle lists the physical book, two posters, a fan, and four postcards. Sources: [release report](https://www.nownews.com/news/6791189), [official publisher solo edition](https://bee3shine.com/product/2026%E3%80%8Ahoney%E3%80%8B%E6%9E%97%E8%8E%8E%E5%AF%AB%E7%9C%9F%E6%9B%B8-%E5%96%AE%E6%9C%AC/), [Ruten listing](https://www.ruten.com.tw/item/22613373876604/).

劉淇《SOAKING WET》has two Pubu digital PDFs: a 106-page edition and a separately sold 106-page video edition. Sources: [standard PDF](https://www.pubu.com.tw/magazine/686437), [PDF with video](https://www.pubu.com.tw/magazine/686433). 曼容《曼曼喜歡你》is one fixed-layout EPUB, EISBN 9786264036115, with nine behind-the-scenes videos; its three advertised cover designs were not split into invented editions. Sources: [Sanmin ebook metadata](https://www.sanmin.com.tw/product/index/013978283), [Yahoo retail listing](https://tw.buy.yahoo.com/gdsale/gdsale.asp?act=ACT251125012&gdid=11737942&hpp=ACT251125012). 宋羽葤《羽葤的小宇宙》is a fixed-layout EPUB (EISBN 9786263381780); the official creator link says the listed edition includes video, but page and video counts are unavailable. Sources: [Sanmin](https://www.sanmin.com.tw/product/index/013427987), [creator links](https://linktr.ee/songyu.chou). 言嘉佑《Virtual 虛擬情人》is catalogued as a digital edition with EISBN 9786264159883; page count and file format were not published on the retailer page. Source: [Momo](https://www.momoshop.com.tw/product/14197050).

Added the official three-person physical set《三倍心跳》for 董梓甯、林莎、吳元元; page count and full package contents are undisclosed. Source: [Bee3Shine](https://bee3shine.com/product/%E3%80%8A%E4%B8%89%E5%80%8D%E5%BF%83%E8%B7%B3%E3%80%8B%E6%A2%93%E6%A2%93x%E6%9E%97%E8%8E%8Ex%E5%85%83%E5%85%83-%E9%99%90%E9%87%8F%E4%B8%89%E4%BA%BA%E5%AF%AB%E7%9C%9F%E5%A5%97%E7%B5%84/). The creators’《純·欲姊姊特休中》is a 128-page physical book with a random ID card; digital files only appear as part of a mixed VIP bundle, so no digital edition was fabricated. Source: [official creator storefront](https://pinpinponpon627.waca.tw/product/detail/2589988).

The existing Candy physical edition now carries ISBN 9786269273300, 144 pages, dimensions 18 × 25.6 × 1.2 cm, and the verified 2025-10-23 release date. Sources: [IWIN official listing](https://www.iwinimc.com/products/candy1023-photobook), [National Central Library deposit](https://isbn.ncl.edu.tw/FCKEDITOR_UploadFiles/1763434068.pdf). 禾羽’s 2026《禾你相羽 in Okinawa》has separate book-only and collector merchandise editions; both use the publisher gallery image that clearly shows the book face. The official product page lists 17.6 × 25 cm and a planned 2026-09-15 shipment, but no page count, ISBN, or confirmed publication day. Source: [Kaboom](https://www.kaboom.tw/products/2026-kimi-in-okinawa-photo-book).

Restored official publisher covers for 吳元元《元氣東京》special/channel editions,《元氣滿滿》special edition,《元元》celebration edition, 巫苡萱《天天和你在苡起》limited edition, and 黃上晏《仲夏晏之夢》special edition. Cite’s image CDN blocks bare hotlink requests; `r2_covers.py` now sends the publisher-site referrer only for that exact CDN host, and all six R2 uploads passed the public URL hash check. Sources: [元氣東京 special](https://www.cite.com.tw/book?id=82767), [元氣東京 channel](https://www.cite.com.tw/book?id=84369), [元氣滿滿](https://www.cite.com.tw/book?id=76596), [元元](https://www.cite.com.tw/book?id=93763), [巫苡萱](https://www.cite.com.tw/book?id=78441), [黃上晏](https://www.cite.com.tw/book?id=83222).


## Research batch 83 — group photobooks and live digital offers

Added seven new works and eight editions: seven digital editions and 洪仕晟’s separate 160-page physical and fixed-layout EPUB editions. Seven exact cover assets were uploaded to R2 and verified by public URL hash. The research records preserve group credits as shared works, keep print and ebook ISBNs and format-specific metadata apart, and omit Sanmin’s internal product codes and BOOK☆WALKER’s print ISBN from ebook editions. The per-model bibliography now exports all 423 active database editions; superseded edition history stays out of that list.

The newly recorded group ebooks are *MotoH車漾女神誌－女神降臨寫真集* (陳白白、葉蛋蛋、波奇、莉亞; 160 pages); *Girl Friend女友寫真 No.2* (黃艾比、陳安安、貝兒、步步、小桃子); No.3 (夢夢、殷宛琦、尤妝妝、謝立琪、唐琦琦); No.4 (草草、金瑀恩、莉亞、佳佳兒; 144 pages; photographer 許小弘); and *國民女友First Love* (吳昱萱、曼達、鐘挅莉、朱芯辰、親親). No.2, No.3 and First Love do not disclose page counts on the checked product pages. 綵冞／吳綵冞’s *冞冞糊糊愛上你* is an EPUB with EISBN 9786263778207, bathtub and beach scenes, photographer 陳伸維, and eight behind-the-scenes clips. 洪仕晟’s *似曾相識* has a 160-page physical edition (ISBN 9786263211940; 25.8 × 18.2 × 1.2 cm) and a distinct 160-page fixed-layout EPUB with a phone-wallpaper bonus.

The worker confirmed 11 active Taiwan digital retail offers: MotoH NT$279 on Google Play; Girl Friend No.2, No.3 and *國民女友First Love* NT$399 each on Sanmin; Girl Friend No.4 NT$285 on Google Play and NT$399 on Sanmin; 綵冞 NT$350 on Sanmin; 洪仕晟 NT$323 on BOOK☆WALKER; 曼容 NT$350 on Sanmin; and 夏蕾’s digital *心動蕾達* NT$476 each on Pubu and Sanmin. These are digital-store offers. No physical active asking-price or completed-sale observation was verified or imported for this batch.

Sources: [MotoH Google Play](https://play.google.com/store/books/details?id=m4cgEQAAQBAJ&hl=zh_TW&gl=TW), [Girl Friend No.2](https://www.sanmin.com.tw/product/index/015876831), [No.3](https://www.sanmin.com.tw/product/index/015876851), [No.4 Sanmin](https://www.sanmin.com.tw/product/index/015876854), [No.4 Kobo](https://www.kobo.com/tw/zh/ebook/girl-friend-no-4), [First Love](https://www.sanmin.com.tw/product/index/015876853), [綵冞](https://www.sanmin.com.tw/product/index/013627152), [洪仕晟 print](https://www.kadokawa.com.tw/products/9786263211940), [洪仕晟 EPUB](https://www.bookwalker.com.tw/product/133398), [NCL ISBN deposit](https://nclfile.ncl.edu.tw/files/202204/58dc014c-a17e-4259-ac08-e039a107fc62.pdf), [曼容](https://www.sanmin.com.tw/product/index/013978283), [夏蕾 Pubu](https://www.pubu.com.tw/ebook/696714), [夏蕾 Sanmin EPUB](https://www.sanmin.com.tw/product/index/015899348).


## Research batch 84 — five Taiwan creators

Added 12 works and 14 format editions across 毛祁生, 吳俊, Mier, 木子 and Sunny. Two books have separate print and digital editions: 毛祁生《為愛而生》 (print ISBN 9786263784604; EPUB EISBN 9786263785083) and 吳俊《Your Man》 (print ISBN 9789865245689; digital-special EISBN 9789865245801). Print and ebook metadata, covers and accessories remain format-specific. Mier has four digital titles (《殘垣綺夢》、《野性之誘》、《凝視》、《柔和日光》); 木子 has five (《晨光私語》、《鏡中迷情》、《回眸》、《午後的慵懶》、《夢境夏娃》); Sunny has *Journey Girl Vol.23 Sunny*. The photo descriptions and photographer/model credits are recorded per edition in the research JSON. Fifteen distinct cover source URLs were uploaded and verified through public R2 URLs.

The worker confirmed 13 active digital-store offers, observed on 2026-10-07 Taiwan time: 毛祁生《為愛而生》 NT$450 on BOOK☆WALKER; 吳俊《Your Man》 NT$285 on Google Play; Mier’s 《殘垣綺夢》、《凝視》、《柔和日光》 NT$299 each and 《野性之誘》 NT$299 on TAAZE, with a second Google Play offer for 《野性之誘》 at NT$214; 木子’s 《晨光私語》 NT$214 on Google Play, 《鏡中迷情》 NT$299 on Rakuten Kobo Taiwan, and 《回眸》、《午後的慵懶》、《夢境夏娃》 NT$299 each on TAAZE; Sunny’s BOOK☆WALKER offer is NT$179. These are digital retail prices, not resale asking or transaction prices. The two physical editions in this batch have publisher metadata and covers, but no physical active-price or sold-price observation was linked, so publisher prices were not recorded as marketplace prices.

The import completed and the public catalog readback passed: 369 published works and 437 active editions in the generated bibliography, with 263 physical and 174 digital editions across 285 model-credit entries. No active edition has a pending cover. The catalog keeps each ISBN/edition format separate; the BOOK☆WALKER page for 毛祁生 exposes the print ISBN on its ebook offer, so the listing’s ISBN was omitted and the ebook EISBN is stored only on the digital edition.

Sources: [毛祁生 print / KADOKAWA](https://www.kadokawa.com.tw/products/9786263784604), [毛祁生 EPUB / BOOK☆WALKER](https://www.bookwalker.com.tw/product/188914), [毛祁生 EISBN record / Readmoo](https://reading.udn.com/ebook/store/store_product.do?pid=135608), [吳俊 print / KADOKAWA](https://www.kadokawa.com.tw/zh-hant/products/9789865245689), [吳俊 digital / Google Play](https://play.google.com/store/books/details/Your_Man_%E5%90%B3%E4%BF%8Ajunwu185%E5%AF%AB%E7%9C%9F%E6%9B%B8_%E6%95%B8%E4%BD%8D%E7%89%B9%E5%88%A5%E7%89%88?id=LdQ3EAAAQBAJ&hl=zh_TW&gl=TW), [Mier Ruin](https://www.taaze.tw/products/14100142100.html), [Mier Wild](https://www.taaze.tw/products/14100142313.html), [Mier Gaze](https://www.taaze.tw/products/14100142315.html), [Mier Soft Sun](https://www.taaze.tw/products/14100142341.html), [Muzi Dawn](https://play.google.com/store/books/details/%E6%8B%BE%E6%8D%8C_%E6%99%A8%E5%85%89%E7%A7%81%E8%AA%9E_%E6%9C%A8%E5%AD%90%E6%80%A7%E6%84%9F%E5%AF%AB%E7%9C%9F%E9%9B%86?id=jNgUEgAAQBAJ), [Muzi Mirror / Rakuten Kobo](https://www.rakuten.com.tw/shop/kobo/product/154b4821-edfb-3eb7-8c42-0f7b6685e63d/), [Muzi Return](https://www.taaze.tw/products/14100142314.html), [Muzi Afternoon](https://www.taaze.tw/products/14100142316.html), [Muzi Dream Eve](https://www.taaze.tw/products/14100142342.html), [Sunny / BOOK☆WALKER](https://www.bookwalker.com.tw/product/308235).


## Research batch 85 — 艾芸／Arwen、許小葆、明明

Added nine new works across three previously unrepresented creator names: one physical edition for 艾芸／Arwen／陳艾芸 and eight digital PDF photobooks (four each) for 許小葆 and 明明. The physical listing calls 艾芸’s book her first personal photobook, but provides no ISBN, page count, dimensions, photographer or detailed contents; those fields remain unknown. Its NT$1,280 seller price was not imported as a second-hand marketplace price.

Fan520’s current digital listings were captured on 2026-10-07 Taiwan time as active digital retail offers: 許小葆’s A–D titles are NT$590, NT$490, NT$490 and NT$490; 明明’s A–D titles are NT$390 each. Product pages identify the downloads as PDF files. Video is marked only on product titles that advertise a video bonus. Page counts, photographer credits and release dates are not published. Nine exact product covers were uploaded to R2 and verified; the public database readback shows no editions with pending covers. No physical active asking-price or completed-sale observations were added in this batch.

The scraper and API now recognize Fan520 as a Taiwan digital storefront using exact product URLs, with digital-only active-price collection and no sold-price or physical-marketplace jobs. Python storefront/import tests and `go test ./...` passed.

Sources: [艾芸／Arwen profile](https://www.fan520.net/pages/arwen), [艾芸 physical photobook](https://www.fan520.net/products/arwen-2), [許小葆 Fan520 category](https://www.fan520.net/categories/%E5%B0%8F%E8%91%86%E5%AF%AB%E7%9C%9F), [許小葆 A](https://www.fan520.net/products/bao-61501), [許小葆 B](https://www.fan520.net/products/bao-2023082401), [許小葆 C](https://www.fan520.net/products/bao-2023090101), [許小葆 D](https://www.fan520.net/products/abao-070701), [明明 A](https://www.fan520.net/products/ilis61028-052201), [明明 B](https://www.fan520.net/products/ilis61028-070801), [明明 C](https://www.fan520.net/products/ilis61028-072001), [明明 D](https://www.fan520.net/products/ilis61028-083101).


## Research batch 86 — 多莉／Dory

Added two distinct physical photobook works for 多莉Dory, each with an official iWIN product image mirrored to R2 and checked by public URL hash.《San Dory三多莉2025》is the completed first book: 144 pages, 18 × 25.6 × 1.2 cm, paperback, one book plus one dust jacket, ISBN 9786269847396; the publisher currently marks it discontinued. The National Central Library bibliography confirms its author, publication month, pagination and ISBN.

The second work is the separate 2027 collaboration photobook. It is currently in preorder, its title is explicitly tentative, and iWIN lists 64 pages, 18 × 25.6 cm, paperback, one book plus one dust jacket, with planned shipping on 2026-12-01. The publisher identifies the book-cover image as the creekside version and the dust jacket as the rope-binding version. The R2 image is the publisher's sample artwork, so the final cover may change. Mirror Media reports photographer Ryan and 14 styling sets. Exact-title searches found a Ruten multi-variant merchandise listing with a “寫真書+小卡” option and a sold-out Shopee multi-option listing, but neither exposes an edition-specific asking price or confirmed transaction price; no marketplace listing was linked. No dedicated digital edition was verified, and the publisher's NT$1,200 price was not treated as a resale offer.

Sources: [iWIN 2025 book](https://www.iwinimc.com/products/dory0620-sandory2025-preorderonly), [National Central Library bibliography](https://isbn.ncl.edu.tw/FCKEDITOR_UploadFiles/1760932966.pdf), [iWIN 2027 preorder](https://www.iwinimc.com/products/dory0620-dory2027-photobook-preorderonly), [Mirror Media 2027 photo-book report](https://www.mirrormedia.mg/story/20261001-90ent-202231), [Ruten multi-option listing](https://www.ruten.com.tw/item/22601876318464/), [Shopee sold-out listing](https://shopee.tw/%E7%B5%95%E7%89%88%E5%85%A8%E6%96%B0%E6%9C%AA%E6%8B%86-%E8%AA%98%E6%83%91%E8%AA%8C-San-Dory%E4%B8%89%E5%A4%9A%E8%8E%892025-%E5%AF%AB%E7%9C%9F%E9%9B%86-%E5%A4%9A%E8%8E%89Dory-cin-i.130652226.47900330172).

The public bibliography now reads back 380 published works and 448 active editions (266 physical, 182 digital); the two Dory books have separate work and edition IDs, and both R2 cover URLs passed a public hash check.



## Research batch 87 — 馮馮、波多野Bella

Added four separate Fan520 PDF photobook titles for 馮馮 (A–D), plus two separate digital PDF editions sold under 波多野Bella／波多 (A–B). Fan520's dedicated creator categories identify the subjects; each item has its own product URL and exact cover mirrored to R2. 馮馮's pages do not publish pagination or video details, so those fields remain unknown. The two 波多 items each state 106 pages and PDF delivery; the A item includes a 2:13 MP4 and the B item an 8:20 MP4. Their digital works remain separate, with the format-specific video details recorded on each edition.

Current Fan520 digital retail prices observed on 2026-10-07T02:50:53Z: 馮馮 A NT$390 and B–D NT$490; 波多 A NT$100 and B NT$490. These are active digital storefront offers, not completed-sale prices. This bounded Fan520 batch did not search physical marketplaces or establish whether other print editions exist. The source category calls the creator 波多野Bella while the item pages use 波多; the registry retains both verified seller names as aliases.

Sources: [馮馮 category](https://www.fan520.net/categories/feng), [馮馮 A](https://www.fan520.net/products/feng-20230509001), [馮馮 B](https://www.fan520.net/products/feng-20230615001), [馮馮 C](https://www.fan520.net/products/feng-2023080701), [馮馮 D](https://www.fan520.net/products/feng-072001), [波多野Bella category](https://www.fan520.net/categories/bella), [波多 A](https://www.fan520.net/products/bella-pohotbook070401), [波多 B](https://www.fan520.net/products/bella-pohotbook070401-1).


## Market batch 88 — 斐棋《一棋一會》

The database already contained separate print and EPUB editions, so this batch enriched that work rather than creating duplicates. The print edition is the 144-page, 21 × 29.7 cm book (ISBN 9786264343466); publisher metadata credits photographer 黃天仁 and describes 200 images photographed in Japan. The digital edition uses EISBN 9786264343435, is an EPUB with behind-the-scenes video, and Google Play Books reports 264 pages. Its R2 cover links were already present and remain attached to their respective editions.

Live marketplace readback added two active Ruten physical offers: NT$631 at [item 22542187078411](https://www.ruten.com.tw/item/22542187078411/) and NT$703 at [item 22541131917084](https://www.ruten.com.tw/item/22541131917084/). Both pages report in-stock new copies. The database also now records the active Sanmin EPUB offer at NT$350. Existing digital offers remain separate: BOOK☆WALKER NT$277 and Readmoo NT$350. These are asking/retail prices, not sold prices. Ruten's pages show aggregate quantities sold but do not expose an individual completed transaction price, so no sold-price record was inferred. Kobo's page returned HTTP 403 during direct verification and was skipped.

Sources: [Cité physical edition](https://www.cite.com.tw/book?id=104947), [Sanmin EPUB](https://www.sanmin.com.tw/product/index/015061665), [Google Play Books metadata](https://play.google.com/store/books/details?id=pPCZEQAAQBAJ&hl=zh_TW&gl=TW), [BOOK☆WALKER offer](https://www.bookwalker.com.tw/product/265506), [Readmoo offer](https://readmoo.com/book/210430987000101), [Ruten offer 1](https://www.ruten.com.tw/item/22542187078411/), [Ruten offer 2](https://www.ruten.com.tw/item/22541131917084/).


## Market batch 89 — 瑟七《微澀．微瑟》Pubu digital offer

The database already held separate physical and digital editions, so this batch enriched the existing digital edition instead of creating a duplicate. Pubu’s official product page identifies the digital ISBN 9786264555029, a 294-page fixed-layout EPUB (463 MB), release date 2026-08-30, and included video. Its buy/add-to-cart page showed NT$350 when checked. The digital edition now links to the higher-resolution Pubu cover mirrored to R2 and verified by public SHA-256; the physical cover and physical edition were left separate.

The digital edition has active catalog offers from Pubu (NT$350, observed 2026-10-07), BOOK☆WALKER (NT$277, prior observation) and Readmoo (NT$350, prior observation). The physical edition remains ISBN 9786264552080, 144 pages; its two Ruten and one Yahoo active asking-price observations remain linked separately. No sold price was inferred from those current/retail asks or sold counts.

Sources: [Pubu digital edition](https://www.pubu.com.tw/ebook/690306), [Cité physical edition](https://www.cite.com.tw/book?id=108115), [Ruten listing 1](https://www.ruten.com.tw/item/22628062929424/), [Ruten listing 2](https://www.ruten.com.tw/item/22628082675187/), [Yahoo listing](https://tw.bid.yahoo.com/item/101758878879), [BOOK☆WALKER offer](https://www.bookwalker.com.tw/product/305610), [Readmoo offer](https://readmoo.com/book/210497069000101).


## Research batch 90 — 樂天女孩 Yanmaga 數位寫真集

Added one group digital work featuring 穎樂、高橋佳帆、笑笑、溫妮. Kodansha’s campaign page and Kobo edition metadata describe a Taiwan Kobo-exclusive EPUB3 fixed-layout release (Adobe DRM, 179 MB), released 2026-08-31. Kobo’s Taiwan edition adds 20 black-swimsuit pages; no page count is published. The four members share one compilation, so the database stores one digital work with four model credits instead of four invented individual editions. No physical version was found.

PChome’s live product page returned HTTP 200 and showed the Kobo eBook at NT$650 with add-to-cart and buy actions. The verified PChome digital offer and its cover are linked to the digital-only edition. The cover was mirrored to R2 and passed a public hash check. No sold transaction was observed.

Sources: [Kodansha Yanmaga Cup page](https://ymclub.kodansha.co.jp/pages/yanmaga-cup-tw), [Kobo Taiwan edition](https://www.kobo.com/tw/zh/ebook/kobo-rakuten-girls-2), [Rakuten Kobo store page](https://www.rakuten.com.tw/shop/kobo/product/2b86ca34-c543-3708-a100-0cb0bac76b32/), [PChome live offer](https://24h.pchome.com.tw/books/prod/DJBQ2E-D900KE504).


## Research batch 91 — individual Rakuten Girls digital mini photobooks

Added six member-specific digital works for 穎樂、若潼、廉世彬、高橋佳帆、溫妮 and 禹菡. They are separate works from the existing four-member Rakuten Girls group book; all six editions are tagged digital, Japanese-language and 講談社, with publication date 2026-04-24. Kobo’s official Taiwan pages provide ISBN/book IDs and EPUB3 Adobe DRM details for 高橋佳帆 and 廉世彬. PChome metadata provides the ISBN for 溫妮; the other checked PChome product pages have exact member-specific titles but no readable ISBN, so those identifiers remain blank. All six edition covers were mirrored to R2 and passed HEAD and public GET SHA-256 verification. Database readback confirms six new digital works and no pending covers.

PChome’s current product-detail state reports the five checked item codes as unavailable with price zero. Older search-index snapshots show NT$150, but those stale values were not saved as active offers. Kobo’s two Taiwan product pages verify the editions; this browser session required a Taiwan address to purchase, so no current Kobo price was recorded. No completed-sale price was found. Kira、彭彭、Mika and 笑笑 are listed in the ten-title series index, but exact product identities and matching cover images remain to be verified before import.

Sources: [Kodansha Yanmaga Cup page](https://ymclub.kodansha.co.jp/pages/yanmaga-cup-tw), [FindBook series index](https://findbook.com.tw/rakuten%20girls%20%E8%BF%B7%E4%BD%A0%E5%AF%AB%E7%9C%9F%E9%9B%86), [PChome mini-book category index](https://24h.pchome.com.tw/search/?cateId=DJBQ&q=cup), [Kobo 高橋佳帆](https://www.kobo.com/tw/zh/ebook/YLxZIBkZVTuQgCCDkypKtg), [Kobo 廉世彬](https://www.kobo.com/tw/zh/ebook/ucb5JI1zFTa93qIVVPlpHg), [PChome 穎樂](https://24h.pchome.com.tw/books/prod/DJBQ4C-D900JYAIL), [PChome 高橋佳帆](https://24h.pchome.com.tw/books/prod/DJBQ4C-D900JYAHK), [PChome 溫妮](https://24h.pchome.com.tw/books/prod/DJBQ4C-D900JYAHA), [PChome 若潼](https://24h.pchome.com.tw/books/prod/DJBQ4C-D900JYAJU), [PChome 禹菡](https://24h.pchome.com.tw/books/prod/DJBQ4C-D900JYAGZ).

## Research batch 92 — T妹《百變妖精：T妹數位寫真》

Added the digital fixed-layout EPUB edition (ISBN/EISBN 9789571095622, 尖端出版, 2019-09-20) as a digital-only work. Sanmin’s live page showed NT$239 and an add-to-cart control; that active digital ask is the only price observation imported. The exact Sanmin cover was uploaded to R2 and passed public SHA-256 readback. No physical edition or completed-sale price was found. Sanmin’s long description is copied from a different model’s book, so it was excluded from this title’s composition. Readmoo’s indexed record identifies T妹 and photographer 戴群芳, but the old product URL now redirects to a service announcement; BOOK☆WALKER’s indexed NT$189 price was not live-verified and was not imported. Taiwan’s National Central Library PDF lists the same title/creators under ISBN 9789571096544, which conflicts with both retailer EISBN records; the discrepancy is retained in the research JSON rather than inventing a second edition.

Sources: [Sanmin live product](https://www.sanmin.com.tw/product/index/014530039), [Readmoo product record](https://reading.udn.com/ebook/store/store_product.do?pid=11601), [BOOK☆WALKER indexed listing](https://www.bookwalker.com.tw/search?d=7&p=4&series_display=1&v=26), [National Central Library new-books bibliography](https://nclfile.ncl.edu.tw/files/202201/14a17a9b-32cc-4216-8edd-6f776cc373a2.pdf).

## Research batch 93 — 韓智恩《夏日恩典》

Added the digital edition of《夏日恩典》under Nancy韓智恩, keeping her identity separate from the Korean actor with the same name. Sharp Point's publisher campaign and promotional video credit photographer 莉奈 and specify 380 pages with a behind-the-scenes video; the National Central Library bibliography provides ISBN 9789571095646 and credits 韓智恩、莉奈. The exact cover image linked from the publisher campaign was mirrored to R2 and passed public SHA-256 verification. File format and publication date remain unconfirmed. BOOK☆WALKER product 65875 now returns 404; its old campaign price of NT$262 was not imported as a current offer. No physical edition or current digital retail offer was verified.

Sources: [Sharp Point publisher campaign](https://cp.bookwalker.com.tw/event/2020/20200416/index.html), [Sharp Point promotional video](https://www.youtube.com/watch?v=x9LLwCLQDgY), [National Central Library bibliography](https://nclfile.ncl.edu.tw/files/202201/14a17a9b-32cc-4216-8edd-6f776cc373a2.pdf), [BOOK☆WALKER product page](https://www.bookwalker.com.tw/product/65875).

## Research batch 94 — Sharp Point digital photo books

Added five digital-only EPUB editions: 小蘋果《蘋頻靠近你》, 書那娜《混血精靈NANA》, 溫雅云《舞：阿布舞》, 今井彩香《為你加油！》 and 王緒緒《和你在一起》. Sharp Point's 2020 campaign links the matching covers to each product card; Sanmin/Readmoo detail pages supply the live EPUB identifiers and current purchase prices. The five campaign-linked covers were mirrored to R2 and passed public SHA-256 readback. Readmoo page counts were recorded where shown (206–286 pages); 小蘋果's page count remains unknown. The summaries capture source-listed styling and travel themes, not a complete frame-by-frame image inventory. Live digital asking prices at the time of observation are 小蘋果 NT$239 (Sanmin), 書那娜 NT$288 (Sanmin and Readmoo), 溫雅云 NT$236 (Readmoo), 今井彩香 NT$236 (Sanmin and Readmoo) and 王緒緒 NT$249 (Readmoo). The publisher campaign's old discount prices were not treated as current offers. ISBN/EISBN conflicts and separate PDF ISBNs are documented in the research JSON; only each live-sold EPUB EISBN is imported. No physical counterparts were identified for these exact titles, and no sold transactions were inferred.

Sources: [Sharp Point campaign](https://cp.bookwalker.com.tw/event/2020/20200416/index.html), [Sanmin 小蘋果](https://www.sanmin.com.tw/product/index/014538536), [Sanmin 書那娜](https://www.sanmin.com.tw/product/index/014459306), [Readmoo 書那娜](https://readmoo.com/book/210133093000101), [Readmoo 溫雅云](https://readmoo.com/book/210117136000101), [Sanmin 今井彩香](https://www.sanmin.com.tw/product/index/014381525), [Readmoo 今井彩香](https://readmoo.com/book/210111510000101), [Readmoo 王緒緒](https://readmoo.com/book/210100743000101), [NCL bibliography 2020](https://nclfile.ncl.edu.tw/files/202104/f7e692d9-fb48-4ee7-a14e-a70242acf82e.pdf), [NCL bibliography 2021](https://nclfile.ncl.edu.tw/files/202107/54fe4753-37d3-4a44-aaa4-3e0c11fdc280.pdf).

## Research batch 95 — Sharp Point digital photo books

Added six digital-only EPUB editions: 艾璐《我艾你 愛してる》, 雨䕕《Fairy雨䕕同名數位寫真》, Neneko《肉感少女的幻想》, 張香香《Sweet Time》, 芳婷《Heartbeat》, and 茉莉《茉茉在你身邊》. The official Sharp Point campaign links the cover art and photographer credits to each model card; current Sanmin/Readmoo detail pages verify EISBN, EPUB format, date and active price. Six covers were mirrored to R2 and each passed public SHA-256 readback. Reported compositions follow the publisher/retailer descriptions and are not a complete image inventory. The old campaign promo prices were excluded. Live prices at observation: 艾璐 NT$239; 雨䕕 NT$236; Neneko NT$270; 張香香 NT$252; 芳婷 NT$236 at Sanmin and Readmoo; 茉莉 NT$236. No physical edition matching these exact digital EISBNs was verified.

Sources: [Sharp Point campaign](https://cp.bookwalker.com.tw/event/2020/20200416/index.html), [Readmoo 艾璐](https://readmoo.com/book/210133422000101), [Readmoo 雨䕕](https://readmoo.com/book/210114818000101), [Sanmin Neneko](https://www.sanmin.com.tw/product/index/014360185), [Sanmin 張香香](https://www.sanmin.com.tw/product/index/014189632), [Sanmin 芳婷](https://www.sanmin.com.tw/product/index/014360245), [Readmoo 芳婷](https://readmoo.com/book/210089610000101), [Readmoo 茉莉](https://readmoo.com/book/210099764000101).

## Research batch 96 — Readmoo digital photobooks

Recorded eight active Readmoo fixed-layout EPUB offers: four on newly added digital works and four on existing digital catalog entries. The verified titles are 李雅英《沿著海，遇見你》數位版, 江宛庭《宛美情人》, 林岱縈《答應你》電子書加值版, 孫唯真《F巨乳 唯獨是你》, 蕭芷渲《芷為你而燦爛》, 陳熙爰《愛上熙爰前》, 斐棋《一棋一會》 and 瑟七《微澀．微瑟》. Six Readmoo pages display EISBNs; the 孫唯真 and 蕭芷渲 pages do not display an ISBN/EISBN, so their canonical Readmoo product IDs are the saved identifiers. The 李雅英 digital edition explicitly contains 272 images different from the physical edition. The 林岱縈 digital row previously carried the paper ISBN 9786263740402; this import corrected the digital EISBN to 9786263746671 while preserving 9786263740402 on the physical edition. Each Readmoo offer remains format-tagged digital and attached to the matching digital edition. The 瑟七 慶功版 and 蕭芷渲《芷為你而閃亮》 were excluded because their pages identify cover-only or same-content reissues. All eight matching covers were mirrored to R2 and passed public SHA-256 readback.

Active digital asking prices observed on 2026-10-07: 李雅英 NT$499; 江宛庭 NT$350; 林岱縈 NT$455; 孫唯真 NT$299; 蕭芷渲 NT$369; 陳熙爰 NT$350; 斐棋 NT$350; 瑟七 NT$350. These are retailer asking prices, not completed-sale prices.

Sources: [李雅英](https://readmoo.com/book/210468148000101), [江宛庭](https://readmoo.com/book/210326272000101), [林岱縈](https://readmoo.com/book/210305040000101), [孫唯真](https://readmoo.com/book/210106007000101), [蕭芷渲](https://readmoo.com/book/210282307000101), [陳熙爰](https://readmoo.com/book/210343510000101), [斐棋](https://readmoo.com/book/210430987000101), [瑟七](https://readmoo.com/book/210497069000101).

## Research batch 97 — Readmoo digital photobooks and offers

Added four digital editions from live Readmoo product pages: 吳心緹《Holiday》, 陳怡叡《與你．YURI》, 謝凱蒂《浮誇的不是表情，是我的人生》散文＋寫真合輯, and 冼迪琦《刻在心迪》. Holiday and 冼迪琦 each have a new digital edition linked to their existing title work; their paper ISBN remains on the physical edition and Readmoo's EISBN is on the digital edition. The 謝凱蒂 Readmoo page displays two component EISBNs, 9786263535565 and 9786263535596. NCL bibliography identifies them as EPUBs for the life-story volume and the separate photo volume; the Readmoo page sells the combined memoir/photo product for NT$476. The single-ISBN catalog field is left blank for this combined listing and both identifiers are preserved in the research JSON. Added Readmoo offers to four matching existing digital editions: 夏蕾《心動蕾達》, 陳怡叡／陳洛心《洛入你心》, 曼容《曼曼喜歡你》 and 阿部瑪利亞《半分 はんぶん》. Chen Luo Xin's rebranded author name uses the existing print ISBN and EISBN identity rather than creating a duplicate. All eight matching Readmoo covers were uploaded to R2 and passed public SHA-256 readback. Active digital asking prices observed: 吳心緹 NT$455; 夏蕾 NT$476; 陳怡叡 NT$385; 謝凱蒂 NT$476; 陳洛心 NT$476; 曼容 NT$350; 冼迪琦 NT$455; 阿部瑪利亞 NT$476. These are store asking prices, not completed-sale prices.

Sources: [吳心緹](https://readmoo.com/book/210355144000101), [夏蕾](https://readmoo.com/book/210502043000101), [陳怡叡](https://readmoo.com/book/210192450000101), [謝凱蒂](https://readmoo.com/book/210270123000101), [陳洛心](https://readmoo.com/book/210408820000101), [曼容](https://readmoo.com/book/210368780000101), [冼迪琦](https://readmoo.com/book/210381773000101), [阿部瑪利亞](https://readmoo.com/book/210431924000101), [National Central Library bibliography](https://isbn.ncl.edu.tw/FCKEDITOR_UploadFiles/1679039608.pdf).


## Research batch 98 — live digital retailer offers and ISBN corrections

Observed live pages on 2026-10-07 and imported 15 active digital asking-price offers across ten Sanmin ebooks, two 林真亦 stores, two TOKKI stores, and Rakuten Kobo for 向理來. Sanmin prices were refreshed from current product pages, replacing stale promotional values where applicable. The TOKKI momo price is the live October 1–31 88折 offer (NT$792); TAAZE is NT$900. YUNA’s digital edition ISBN is corrected to EISBN 9786264197281 while the physical edition retains ISBN 9786264197328. TOKKI’s digital edition is corrected to EISBN 9786260160128 while the physical edition retains ISBN 9786267776919. The TAAZE page exposes the paperback ISBN, so the digital identifier was taken from the [National Central Library bibliography](https://isbn.ncl.edu.tw/FCKEDITOR_UploadFiles/1776397570.pdf).

All offers are tagged digital and link to already verified R2 cover objects; no new cover uploads were needed. These are authorized-store asking prices, not completed-sale prices.

Sources: [013427981](https://www.sanmin.com.tw/product/index/013427981), [013426304](https://www.sanmin.com.tw/product/index/013426304), [013427546](https://www.sanmin.com.tw/product/index/013427546), [014381528](https://www.sanmin.com.tw/product/index/014381528), [013426301](https://www.sanmin.com.tw/product/index/013426301), [014360181](https://www.sanmin.com.tw/product/index/014360181), [013627195](https://www.sanmin.com.tw/product/index/013627195), [014126685](https://www.sanmin.com.tw/product/index/014126685), [013650100](https://www.sanmin.com.tw/product/index/013650100), [014360306](https://www.sanmin.com.tw/product/index/014360306), [林真亦 Readmoo](https://readmoo.com/book/210424363000101), [林真亦 BOOK☆WALKER](https://www.bookwalker.com.tw/product/262431), [TOKKI TAAZE](https://www.taaze.tw/products/14100139059.html), [TOKKI momo](https://www.momoshop.com.tw/product/15246719), [向理來 Kobo](https://www.rakuten.com.tw/shop/kobo/product/1dd820bd-0e56-3024-aa5e-a5e4cdaae4fa/), [NCL EISBN reference](https://isbn.ncl.edu.tw/FCKEDITOR_UploadFiles/1776397570.pdf).


## Research batch 99 — Journey Girl digital photobook

Added Bella's digital-only edition *Journey Girl Vol.12 Bella 貝拉* from the live BOOK☆WALKER product page. The listing identifies a fixed-layout EPUB, 156 pages, publisher 滾石移動, release date 2025-08-05, and current asking price NT$179. The page credits Bella and photographer 一加 but shows no ISBN/EISBN or detailed shot/scene inventory; the BOOK☆WALKER product ID is retained as the listing identifier. Its cover was copied to R2 and verified by public SHA-256 readback. No physical edition was inferred.

The queued Readmoo searches for 子婷, 許維恩, and 張景嵐 were also checked. 子婷's 方糖兒 ebook is already in the catalog; the other two searches had no qualifying product listing in the returned results.

Source: [BOOK☆WALKER Journey Girl Vol.12 Bella](https://www.bookwalker.com.tw/product/254904).

## Research batch 100 — BOOK☆WALKER digital offers

Rechecked five official BOOK☆WALKER product pages and linked each by EISBN to its existing digital edition. Refreshed Amis《夢遊仙境數位寫真》to NT$249 (the previous BOOK☆WALKER observation was NT$197) and added four missing active offers: 書那娜《混血精靈NANA》NT$288, 孟潔×菲菲《bestie閨蜜》NT$299, 吳綵冞《冞冞糊糊愛上你》NT$350, and 曼容《曼曼喜歡你》NT$350. All five pages show digital-only fixed-layout EPUB purchase controls; no physical editions were created or inferred.

The BW pages supplied matching EISBNs and edition metadata. Updated Amis to the official 300-page, 2019-08-09 listing; filled missing details for the 186-page bestie edition and 306-page 綵冞 edition. BOOK☆WALKER reports 241 pages for 曼容 while the existing same-EISBN Readmoo/Sanmin edition record is 252 pages, so the catalog page count remains 252 pending reconciliation. Existing R2 covers were retained for all five editions; no duplicate cover uploads were needed. Prices are active store asking prices, not completed-sale prices.

Sources: [Amis](https://www.bookwalker.com.tw/product/68340), [書那娜](https://www.bookwalker.com.tw/product/84331), [bestie 孟潔×菲菲](https://www.bookwalker.com.tw/product/94281), [吳綵冞](https://www.bookwalker.com.tw/product/192714), [曼容](https://www.bookwalker.com.tw/product/236735).

## Research batch 101 — 菲菲／YuYu digital photobooks

Added two separate digital works by 李恩菲 (菲菲／YuYu) from official BOOK☆WALKER listings. 《菲你莫屬-菲菲數位寫真書-中文版》 is a 257-page fixed-layout EPUB; 《台湾グラドルYuYu 1stデジタル写真集「君だけのYuYu」》 is 271 pages. Both list photographer 莉奈, publisher 滾石移動, release date 2023-05-03, and an active NT$369 offer. BOOK☆WALKER explicitly says the two books contain entirely different images, so they are cataloged as distinct digital works. Neither page displayed an ISBN/EISBN; product IDs 162224 and 162225 identify the marketplace listings. No physical editions were inferred.

Also linked BOOK☆WALKER product 94282 (EISBN 9789571095714) at NT$299 to the existing alternate-cover/order digital edition of *bestie閨蜜*. The official page says its image content matches the other variant. Both new covers were uploaded to R2; public GETs returned 200 and matched each source file's SHA-256. Database verification found 240 physical and 212 digital works, 414 published works, 492 editions, 252 listings, and zero editions with pending covers. Prices are live digital retail asking prices, not completed-sale prices.

Sources: [菲你莫屬](https://www.bookwalker.com.tw/product/162224), [YuYu](https://www.bookwalker.com.tw/product/162225), [bestie alternate edition](https://www.bookwalker.com.tw/product/94282).

## Research batch 102 — Yilian and 吳翔震 photobooks

Added three works as four format-specific editions: Yilian's physical photo-essay 《你的藍色不是我的藍色》; the physical and digital editions of 《SECRET：游泳教練寫真書》; and 吳翔震's physical photo-poetry book 《抱你寫詩》. The two SECRET editions share one work identity but keep distinct format records, metadata, cover images, and retailer data. The catalog normalizer now maps Yilian/Yilianboy aliases to one model and recognizes the SECRET digital special edition as the same work.

The live Ruten listing for the physical SECRET edition is currently NT$6,500 with listed quantity 1; the seller asks buyers to confirm availability. It is recorded as an active fixed asking price. The page's sales count is not treated as a completed-sale price, and no sold-price observation was created. BOOK☆WALKER currently offers the separate digital EPUB edition at NT$409. Sanmin currently marks both other Yilian physical books unavailable to order, and Eslite marks 《抱你寫詩》 out of print, so no active retailer price was recorded for those editions.

The Sanmin and BOOK☆WALKER metadata describe the different physical/digital contents and formats for SECRET. Eslite's live product page displays 《抱你寫詩》's publication date as 2016-09-08; the imported edition was corrected to that date. Four edition covers were uploaded to R2 and their public readbacks were verified against local SHA-256 hashes. The refreshed public bibliography contains 417 works and 489 edition rows; database verification reports 243 public physical works, 213 public digital works, 419 works, 496 editions, 254 listings, and zero editions with pending covers.

Sources: [Yilian photo-essay — Sanmin](https://www.sanmin.com.tw/product/index/007914280), [SECRET physical edition — Sanmin](https://www.sanmin.com.tw/product/index/007564633), [SECRET digital edition — BOOK☆WALKER](https://www.bookwalker.com.tw/product/81588), [active physical SECRET listing — Ruten](https://www.ruten.com.tw/item/22337668175303/), [抱你寫詩 — Eslite](https://www.eslite.com/product/1001296682534720), [吳翔震 profile — Taiwan Cinema](https://taiwancinema.bamid.gov.tw/Staff/PrintFrameContent?ContentUrl=83263).

## Research batch 103 — Teresa 馮子紜 physical photobook

Added Teresa 馮子紜's physical hardcover 《Teresa馮子紜寫真集》 as one work and one physical edition. Sanmin verifies 馮子紜 and photographer 周明進, 白象文化, publication date 2022-09-01, 112 pages, and 30 × 22 × 1 cm dimensions. Its description says the book contains more than 100 color pages, several styled photo themes, and an A3 poster. The cover was uploaded from Sanmin's product image to R2; its public GET returned 200 and matched the local SHA-256.

The retailer identifier 2428915800900 is displayed as an ISBN13 by sellers but is not stored in the database ISBN field. Sanmin marks the book out of print and unavailable to order; Books.com says sold out and Yahoo Shopping says discontinued. Ruten's listing opens an adult-age confirmation page, which I did not pass. As a result, no active marketplace offer or completed-sale price was imported. A Shopee result was also left unverified.

The refreshed bibliography now contains 418 works, 490 edition rows, and 318 model names. Database verification reports 244 public physical works and 213 public digital works, 420 works, 497 editions, 254 listings, and zero editions with pending covers. Teresa is recorded as one physical work, with no digital edition inferred.

Sources: [Teresa 馮子紜寫真集 — Sanmin](https://www.sanmin.com.tw/product/index/010706483), [Books.com listing](https://www.books.com.tw/products/0010934861), [Yahoo Shopping listing](https://tw.buy.yahoo.com/gdsale/gdsale.asp?gdid=p0082263533936), [Ruten listing (age confirmation required)](https://www.ruten.com.tw/item/22451463357990/).

## Research batch 104 — 阿喜, 嚴正嵐, 海倫清桃, and 羽庭

Added four newly verified works and seven distinct edition rows: 阿喜／林育品《馬尾女孩最無敵》 (standard physical, deluxe physical set, and historical HamiBook digital exclusive); 嚴正嵐《Close to Vera》 (physical); 海倫清桃《坦然做自己》 (physical and fixed-layout EPUB); and 羽庭《VISION MAN 質男幫特刊：雨停》 (physical). Physical and digital editions remain separate. Four retailer covers were copied to R2 and verified by public SHA-256 readback.

Ruten currently shows an active NT$500 asking price for the used signed 《Close to Vera》 copy and an active NT$500 ask for a used signed 《坦然做自己》 copy with three posters. Sanmin currently shows NT$560 for Helen's ebook; this is a digital retail price. Ruten shows 阿喜's 《馬尾女孩最無敵》 sold out with one sold, but its displayed NT$500 is not established as the final transaction amount, so the catalog records sold status without a sale price. TAAZE marks 《雨停》 out of print; no active price was added. The digital HamiBook edition is supported by a 2015 Chungwa Telecom announcement describing 25 exclusive, previously unpublished images, but no current product page or price was found.

《坦然做自己》 uses the same ISBN on the physical product metadata; the EPUB is therefore recorded separately without reusing that ISBN. Eslite's deluxe 阿喜 listing gives EAN 4719760105370, which is retained in the research record as an EAN and not misfiled as an ISBN. No photographer or exact digital release date was assigned where the source did not establish it.

Sources: [阿喜 product details — Five Music](https://www.5music.com.tw/Cdlist-C.asp?cdno=435495678816), [阿喜 ISBN bibliography — NCL](https://nclfile.ncl.edu.tw/files/201511/3714787f-ab04-4c3c-865d-aa9f57d83a3d.pdf), [阿喜 deluxe set — Eslite](https://www.eslite.com/product/1001196942377701), [HamiBook digital exclusive — Chungwa Telecom](https://www.cht.com.tw/zh-tw/home/cht/messages/2015/msg-150212-173544), [阿喜 sold-out listing — Ruten](https://www.ruten.com.tw/item/22624864044811/), [Close to Vera — Kingstone](https://www.kingstone.com.tw/basic/2019500056743/), [Vera Ruten listing](https://www.ruten.com.tw/item/22503672140901/), [坦然做自己 — Sanmin](https://www.sanmin.com.tw/product/index/006316873), [fixed-layout EPUB — Books.com](https://www.books.com.tw/products/E050116880), [Helen Ruten listing](https://www.ruten.com.tw/item/22541162554568/), [雨停 — TAAZE](https://www.taaze.tw/products/21100030956.html).

## Research batch 105 — 羽庭 digital photobooks

BOOK☆WALKER’s official 羽庭 series page lists four volumes. Added all four as digital fixed-layout EPUB editions, each with an active NT$299 offer: 《雨停 羽庭》, 《溺愛羽庭》 (83 pages; 2023-09-24), 《羽の魅》 (71 pages; 2025-01-24), and 《惑之庭》 (78 pages; 2025-01-24). 《雨停》 reuses the physical work identity already in the catalog while preserving a separate digital edition and cover. The other three are separate digital works; no physical editions or EISBNs were inferred.

BOOK☆WALKER identifies these as 18+, fixed-layout EPUBs in the 羽庭 series and currently shows purchase controls. The initial import incorrectly retained the restricted-cover masks. The cover repair on 2026-10-07 replaced all four with the actual product images published in the selected product metadata, verified through R2 public readback with exact SHA-256 matches. These are current digital retail asks, not completed sales.

Sources: [BOOK☆WALKER 羽庭 series](https://www.bookwalker.com.tw/search?series=21942), [雨停 羽庭](https://www.bookwalker.com.tw/product/56313), [溺愛羽庭](https://www.bookwalker.com.tw/product/176363), [羽の魅](https://www.bookwalker.com.tw/product/236737), [惑之庭](https://www.bookwalker.com.tw/product/236738).

## Research batch 106 — additional digital editions

Added three digital works and four digital editions: 羽庭《替身》as a Kobo EPUB3 edition; 羽庭《裸心時刻 羽庭》as separate HamiBook PDF and Kobo fixed-layout EPUB editions; and 林倪安《有倪真好 倪安數位寫真（含影音）》as a BOOK☆WALKER EPUB. The two 《裸心時刻》 editions share one work because the product pages match on title, model, creator, and description. 《有倪真好》 is separate from the previously cataloged 《剛好遇見倪》; BOOK☆WALKER provides its own EISBN, title, and 254-page metadata.

Live product pages show active digital asking prices of NT$199 for 《替身》, NT$399 for Kobo's 《裸心時刻》 EPUB, and NT$350 for 《有倪真好》. HamiBook identifies its 《裸心時刻》 PDF edition but its public page does not expose a verifiable current price, so no offer was added. These are retailer asking prices, not completed-sale prices. No physical edition or marketplace listing was inferred for the digital records. A physical 《替身》 remains a research candidate because this batch found only secondary references and marketplace search results, not primary edition metadata.

The 《替身》 and 《有倪真好》 source images, plus HamiBook's generic 18+ preview image for 《裸心時刻》, were uploaded to R2 and passed exact public SHA-256 readback. HamiBook's image is recorded as its public page preview, not the underlying photobook cover. Kobo's 《裸心時刻》 cover remains pending because the actual image is behind the retailer's 18+ confirmation prompt; no age confirmation was submitted. Read-back verification now reports 430 work rows, 512 edition rows, 265 listings, and one pending cover.

Sources: [羽庭《替身》 — Rakuten Kobo](https://www.rakuten.com.tw/shop/kobo/product/98cf8845-9674-3f9b-b647-4f9155105a2c/), [《裸心時刻》 — HamiBook](https://www.hamibook.com.tw/book/0100406339), [《裸心時刻》 — Rakuten Kobo](https://www.rakuten.com.tw/shop/kobo/product/be364870-e4f7-3490-bb20-9e7810c1a5e4/), [林倪安《有倪真好》 — BOOK☆WALKER](https://www.bookwalker.com.tw/product/182855).
