# Ayul identity, edition matching, and rights follow-up (Round 22)

## Does available evidence establish Ayul’s identity and match the reported 2020 release to Puremedia Vol. 28 or Vol. 51?

### Takeaway
Ayul is documented as a Korean-platform streamer/model with a digital photobook reported in 2020, but the reviewed sources do not establish her nationality or connect that 2020 debut to either current Puremedia SKU. The exact product identity, date, page count, and stable item identifier remain unresolved.

### Cited Findings
- A 2020-08-31 NewsCulture report reproduced by Ppomppu says “BJ 아율” was known from PandaTV and that her debut album was published as a digital photobook; the article calls it her first modeling challenge but provides no ISBN, volume number, page count, or item ID. [NewsCulture report reproduced by Ppomppu](https://m.ppomppu.co.kr/new/bbs_view.php?id=news_broadcast&no=128244)
- The Linktree page `@store_ayul` calls a Puremedia web pictorial “아율 1집 / Ayul 1st Sexy photo album” and links to a Puremedia shop, a Gumroad storefront, and an Ayul PandaTV channel; the Linktree page does not show a platform verification mark or nationality claim. [Ayul Linktree](https://linktr.ee/store_ayul)
- Puremedia’s publicly rendered Ayul category page lists exactly two e-book products: “[Ayul] 아율 스토리 e-book [PURE MEDIA] VOL 51” and the same title with VOL 28, each displayed at KRW 39,900. The rendered listing exposes neither product detail URL/stable item ID nor publication date or pagination. [Puremedia Ayul category](https://puremedia.kr/mall/m_mall_list.php?ps_ctid=01011300)
- The general Puremedia category listing also indexes the Vol. 28 and Vol. 51 products as e-books; it gives no explicit statement that either product is the release described in the 2020 report. [Puremedia e-book category](https://puremedia.co.kr/mall/m_mall_list.php?ps_brand=&ps_company=&ps_ctid=01010000&ps_line=high&ps_max_money=&ps_min_money=&ps_page=1&ps_search=)
- Direct page opens of the Linktree’s Gumroad and PandaTV links returned cache misses; no product page content was available from those opens, so they were not used to infer SKU or release details. [Ayul Linktree](https://linktr.ee/store_ayul)

### Inferences
- Vol. 28 may be a plausible candidate for an earlier “1집” release because it is numerically earlier than Vol. 51 and both products are attributed to Ayul on Puremedia’s site; this is only a hypothesis. Neither the publisher’s listing nor the 2020 report states that Vol. 28 is the 2020 debut, and the listing’s shared “Story e-book” title does not prove the products are separate editions of the same work.
- The evidence supports describing the credited creator as an Ayul associated with a Korean streaming platform and Korean-language creator pages, but not as a Korean national. A separate current person using the same stage name must not be merged without matching identity evidence.

### Gaps
- No reviewed primary source ties the 2020 “Ayul 1st” release to Puremedia Vol. 28 or Vol. 51.
- No stable Puremedia product ID, individual item page, publication date, or page count was visible in the accessible rendered pages.
- No reliable first-party identity source establishes this Ayul’s nationality; the Linktree links to the channel, but its ownership/verification is not established on the page.

## Do Puremedia’s terms authorize commercial metadata reuse or R2 storage/public delivery of an exact cover?

### Takeaway
No commercial metadata-reuse license or exact-image grant for MuseBooks was found. Puremedia’s own terms limit commercial use or third-party provision of information to which the mall holds intellectual-property rights without prior consent; its product images remain uncleared for R2 storage and public delivery.

### Cited Findings
- Puremedia Terms of Use §22(1) says copyright and other intellectual-property rights in works created by the mall belong to the mall; §22(2) says users may not use information obtained through the mall, where the mall holds those rights, commercially or provide it to third parties without prior approval. This does not grant MuseBooks permission for commercial reuse of its product-page information. [Puremedia terms, §22](https://puremedia.kr/mall/m_page.php?ps_pname=page_member2)
- Puremedia’s Ayul listing displays product images but contains no visible grant allowing those exact images to be copied, stored in R2, resized, or publicly served by MuseBooks. [Puremedia Ayul category](https://puremedia.kr/mall/m_mall_list.php?ps_ctid=01011300)
- The project source-use register distinguishes page access/provenance from permission to reuse page data or images and requires compatible authorization before reuse; it records no blanket image permission for publisher/store covers. [Project source-use register](../../docs/korean-model-photobook-sources.md)
- The 2020 press report includes a no-unauthorized-reproduction notice and credits Puremedia for the photo; that is not a license for R2 reuse. [NewsCulture report reproduced by Ppomppu](https://m.ppomppu.co.kr/new/bbs_view.php?id=news_broadcast&no=128244)

### Inferences
- A page’s public accessibility, displayed selling price, and cover preview establish discoverability, not rights to copy the cover into MuseBooks or to republish it from R2.
- Product facts may ultimately be independently recorded from an authorized source or under a written permission route, but the sources reviewed here do not clear that gate for a commercial catalog import.

### Gaps
- No license or written authorization was found covering commercial reuse of the relevant Puremedia product metadata.
- No rights-holder permission identifies either exact Ayul cover/preview asset and authorizes R2 storage plus public catalog delivery (including any transformations).

## What did the read-only duplicate check find, and should anything be imported?

### Takeaway
A fresh repeatable-read transaction opened with the database connection in read-only mode found no matching Ayul person, work, or edition rows. Nothing was imported because both the exact-edition mapping and metadata-use authorization remain unresolved; no image was copied or uploaded.

### Cited Findings
- Read-only database query output: `People matching Ayul/아율: 0`; `Works matching title/featured names: 0`; `Puremedia/Ayul edition URL/label candidates: 0`. The query searched canonical/original/English person names; Korean and English work/featured names; and Puremedia/Ayul edition URL, label, and series fields. Transaction options were PostgreSQL `READ ONLY` and `REPEATABLE READ`.
- The 2020 article supports a digital photobook lead, while Puremedia’s current listing separately shows Vol. 28 and Vol. 51; no reviewed exact-product mapping connects those records. [2020 report](https://m.ppomppu.co.kr/new/bbs_view.php?id=news_broadcast&no=128244); [Puremedia Ayul category](https://puremedia.kr/mall/m_mall_list.php?ps_ctid=01011300)
- The project source-use register does not treat retailer/publisher URLs or image provenance as reuse permission. [Project source-use register](../../docs/korean-model-photobook-sources.md)

### Inferences
- The zero-row result applies only to the exact name/title patterns queried; aliases, transliteration variants, and other identifiers may not be covered.
- No catalog import is warranted until the candidate’s exact Puremedia item and edition metadata are linked to the reported debut and an authorized metadata-use basis is identified. R2 remains independently blocked by the absent exact-image grant.

### Gaps
- An exact-product source is needed to establish whether Vol. 28, Vol. 51, both, or neither matches the August 2020 digital debut.
- A sufficiently reliable nationality/identity source and a compatible commercial metadata license are still missing.
- Exact cover assets and rights-holder permissions for R2 storage/public display remain unavailable.
