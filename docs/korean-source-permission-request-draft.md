# Korean catalog source-permission request draft

Prepared 2026-11-01 from the current official route documentation. This is an internal draft only: no application, partnership request, API-key request, or rights inquiry has been submitted. Do not mark any `source_permissions` or `catalog_media` record approved based on this draft.

## YES24 developer application: live retail display

**Requested service:** MuseBooks, a commercial catalog for Korean-model standalone photobooks and MAXIM magazine issues. The display will keep photobooks and magazine issues as distinct publication types.

**Intended API use:** For a specific product already matched to a MuseBooks record, request its YES24 Goods API details by exact product ID or ISBN and display only its YES24 list price, sale price, publication date, sale status, and matching YES24 product link. Show YES24 attribution and a direct link on the same detail view. Fetch on demand and use only short-lived cache if needed for performance; refresh price/status at the cadence specified by YES24. We will not crawl the whole API catalog, build a separate YES24-derived database, redistribute API data, share the key with another service operator, or store price history under this API scope.

**Images:** The initial application excludes cover, side-cover, and back-cover URLs from MuseBooks image storage, transformation, and display. Please confirm whether direct remote display of these specific URLs within the attributed YES24-linked product view is covered by the API terms, given that underlying image rights may belong to third parties. Unless confirmed, MuseBooks will not use those image URLs.

**Key ownership:** Issue the key to the MuseBooks applicant/account owner. Keep it server-side and do not place it in source code, client code, or a shared integration. Add a runtime route only after the account owner has accepted the current terms and the service identity is confirmed.

**Official material:** [YES24 developer portal](https://developers.yes24.com/), [Goods search schema](https://developers.yes24.com/api-doc/goods-item-list), [current API terms](https://developers.yes24.com/support/terms).

## Bunjang Global Partner Center: used asking offers

**Requested service:** MuseBooks, a commercial reference catalog for Korean-model standalone photobooks and MAXIM magazine issues, with separate photobook and magazine-issue records. MuseBooks is not requesting order creation, payment, purchasing, or resale features.

**Requested catalog scope:** Search/query only for matched Korean photobooks and MAXIM print issues, returning item ID, title, price, quantity, condition, shipping fee, active-sale state, seller ID, item URL, and creation/update or observation time. We request permission to display each listing as a source-linked used asking offer and to retain a current observation plus limited history for the agreed period and refresh cadence. We will not download the entire catalog unless separately authorized.

**Images and seller data:** No seller image will be stored, transformed, or displayed unless the agreement expressly licenses that exact use. Please specify whether seller IDs may be retained/displayed, any privacy restrictions, permitted territories, attribution/link wording, rate limits, retention/deletion rules, and how promptly sold/deleted offers must be removed. The MuseBooks image gate will remain closed until exact image permission is recorded separately.

**Requested confirmation:** Does the partner agreement permit an independent source-linked reference catalog and historical price observations, or is it limited to merchant inventory synchronization and overseas sale fulfillment? Please identify any additional approval needed for catalog comparison or display.

**Official material:** [Bunjang Global Partner Center](https://sell-global.bunjang.co.kr/en), [Bunjang API overview](https://api.bgzt.guide/), [catalog field schema](https://api.bgzt.guide/api-10619068).

## MAXIM Korea: metadata and image-use inquiry

**Requested permission:** A MuseBooks commercial catalog route for selected MAXIM issue facts: issue identity/month, publisher-confirmed issue or edition publication dates, explicitly attributed cover-model names and roles, retailer/publisher price and availability fields if the publisher authorizes them, and any collection method or update frequency the publisher approves. Keep MAXIM issues as `magazine_issue` records, separate from standalone photobooks.

**Image request (separate):** For each permitted exact asset, request either direct remote display or storage/display/thumbnail rights, specifying the cover or product image URL, image rightsholder, commercial use, territories, duration, attribution, linking, and whether crops/resizes are allowed. Ask MAXIM to identify the actual rights holder where a photographer or another provider owns the image. No image should be copied before written approval and exact-asset registration.

**Official inquiry channels:** MAXIM's image-use FAQ directs case-by-case inquiries to customer service or site Q&A; its FAQ lists customer service at 1800-5650. This draft has not been submitted. [Image-use FAQ](https://www.maximkorea.net/board/board_view.php?board_cate1=&code=bbs_faq&key=&keyfield=&number=87&page=1&sort=), [customer Q&A](https://www.maximkorea.net/board/board_list.php?code=bbs_qna).

## Approval and import checklist

1. Keep written response, contract/application scope, current terms version, effective period, attribution, retention, rate, link, and permitted fields together as evidence.
2. Create approved source grants only for fields/uses the rightsholder or API terms expressly allow. Use temporary retention for YES24 display; do not convert it to permanent import authority.
3. For Bunjang, record seller-offer terms separately from book/issue bibliography. Treat the listing's asking price and active state as a dated offer observation; never call it a completed sale.
4. Keep exact image grants separate from source metadata grants and record the exact asset identity before any display or copying.
5. Before importing, run identity/duplicate matching and verify `publicationType`: standalone pictorials as `photobook`, monthly MAXIM/B-SIDE products as `magazine_issue` with their issue month. Capture date precision, source URLs, list/sale/used basis, currency, availability evidence, and observation time only where each approved route permits.
6. Verify database read-back and run the Korean cohort audit. The latest permission-aware audit found 0 Korean source grants and 0 permitted media in the cohort, so no route is currently active for this workflow.
