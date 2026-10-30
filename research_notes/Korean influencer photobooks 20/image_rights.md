# Exact-image rights check for Korean influencer photobooks (Round 20)

## Does any exact cover or preview already in the catalog have permission for R2 storage and public delivery?

### Takeaway

No exact cover or preview image in the current Korean photobook catalog is documented as licensed for both a separate R2 copy and public display from MuseBooks. I reran a read-only query on 2026-10-30 using `database.Open(true, false)`; it returned 10 published Korean photobook editions with cover references, and every row had an empty `cover_object_key` and the same external URL in `cover_url`, `original_cover_url`, `catalog_media.original_url`, and `catalog_media.storage_url`. The earlier round-19 audit records the wider 153-edition review and the eight influencer-focused covers; those are remote source references, not R2 copies. [Round-19 exact-cover audit](../Korean%20influencer%20photobooks%2019/r2_rights.md); [project source-policy register](../../docs/korean-model-photobook-sources.md)

### Cited Findings

- The influencer-focused rows are DJ SODA’s print and Apple digital *Candid*, Kim Seolhwa’s *26*, and five Pyo Eunji editions (two *Rondo* editions, *Enbukyoku*, the fanclub first book, and *PHOTO BOOK 2022*). Their exact cover URLs and edition IDs are itemized in the prior read-only audit. The other two cover-bearing editions in the 10-row current query are *BE JOYFUL* and *SANTORINI*, excluded from that influencer subset. [Round-19 audit table and DB verification links](../Korean%20influencer%20photobooks%2019/r2_rights.md)
- Shueisha’s official FAQ says it does not grant individuals permission to use book covers, jackets, or packaging photographs. Its *Candid* publisher page identifies the exact title and publisher image, but no title-specific R2/public-display license appears there. [Shueisha cover-reuse FAQ](https://faq.shueisha.co.jp/faq/show/28?back=front%2Fcategory%3Ashow&category_id=2&faq_id=17&site_domain=default); [Shueisha *Candid* page](https://wpb.shueisha.co.jp/gravure/info/20240216-122279/)
- Apple’s Media Services terms state that delivery of Apple content does not transfer commercial or promotional use rights; the Apple-hosted *Candid* cover URL therefore does not itself authorize mirroring to R2. [Apple Media Services terms](https://www.apple.com/legal/internet-services/itunes/us/terms.html); [Apple Books *Candid* listing](https://books.apple.com/jp/book/dj-soda%E5%86%99%E7%9C%9F%E9%9B%86-candid/id6480587148)
- KADOKAWA’s cover-use rules describe limited, conditional uses for book introductions, including exact-source and credit conditions, and route Internet distribution to inquiry. No approval for MuseBooks’ public R2 delivery is recorded for the KADOKAWA-hosted digital covers of Pyo Eunji’s *Rondo* or *Enbukyoku*. [KADOKAWA cover-use rules](https://www.kadokawa.co.jp/support/b/library/); [*Rondo* digital product](https://www.kadokawa.co.jp/product/322303002121/); [*Enbukyoku* digital product](https://www.kadokawa.co.jp/product/322310001500/)
- Pyo Eunji’s official site terms prohibit unauthorized copying, reposting, and public transmission of site/fanclub material. The official-store URLs used for her print covers are not a grant of third-party image reuse. [Pyo Eunji site terms](https://pyoeunji.com/pages/terms); [official contact page](https://pyoeunji.com/en/pages/contact)
- YES24’s exact *김설화 26* product listing identifies the photobook and two randomly selected cover designs, but supplies no license for copying either exact design into R2. No public reuse grant for this cover was found in the scoped source review. [YES24 *김설화 26* listing](https://www.yes24.com/product/goods/116981923); [round-19 exact-asset rights review](../Korean%20influencer%20photobooks%2019/r2_rights.md)
- The Korea Copyright Commission’s FAQ explains that a photograph can be protected as a photographic work owned by its photographer, and celebrity/model use can raise a separate likeness/publicity permission issue. This supports requiring the exact image’s actual rights grant, not relying on the retailer host or subject’s public profile. [Korea Copyright Commission FAQ](https://www.copyright.or.kr/customer-center/faq/list.do?categorycode1=02)

### Inferences

- Public availability, a publisher/retailer image URL, and recorded provenance do not establish permission to make an R2 copy or serve the image publicly. The round-19 audit shows no exact cover in this set with the required grant, and the live read-only query confirms no intervening R2 key/storage copy was added.
- KADOKAWA’s limited cover policy and Shueisha’s inquiry/business routes may support future title-specific rights requests, but no approval has been received. Attribution alone would not expand those narrow routes into an R2 license.

### Gaps

- For every current cover, MuseBooks still lacks a license or written approval identifying the exact asset URL, R2 storage, public delivery from MuseBooks, any resizing/format conversion, allowed term/territory, and required attribution.
- No contact was sent and no image was downloaded, copied, uploaded, or changed in the database during this check.

## Did the open-license search find a new influencer photobook and exact image suitable for the same permission route?

### Takeaway

No. The only new rights-marked image lead found was an official Korea Racing Authority KOGL Type 2 image set introducing the horse-racing character/influencer “Kkaeali”; its page does not identify a physical or digital photobook, and Type 2 bars commercial use. It is not a photobook-cover or preview candidate for this catalog. [Official KOGL Kkaeali asset record](https://www.kogl.or.kr/recommend/recommendDivView.do?division=img&recommendIdx=50613)

### Cited Findings

- KOGL’s record identifies seven images as “경마캐릭터_나는 ‘깨알이’입니다”, says the Korean Racing Authority holds the work, describes Kkaeali as its horse-racing influencer, and marks the assets Korea Open Government License Type 2 (attribution + noncommercial use). [Kkaeali KOGL asset record](https://www.kogl.or.kr/recommend/recommendDivView.do?division=img&recommendIdx=50613)
- The project’s source-policy register says a KOGL item can provide a supplementary image only when the exact asset bears a compatible license and all conditions are followed; it does not license commercial photobook covers or MAXIM images by default. [KOGL source-policy entry](../../docs/korean-model-photobook-sources.md)
- Search queries for KOGL influencer photo assets and Korean influencer photobook CC/KOGL licenses returned this Kkaeali result, unrelated photobook uses, and no rights-holder-issued license for a cover/preview tied to a new influencer photobook. [KOGL search result](https://www.kogl.or.kr/recommend/recommendDivView.do?division=img&recommendIdx=50613); [Creative Commons reuse search guide](https://ccl.cckorea.org/reuse/find/)

### Inferences

- Kkaeali establishes that a Korean public institution has published an influencer-related image set under an item-specific open license, but that license is limited to those seven named assets and does not extend to another publisher’s cover or a hypothetical photobook. Its Type 2 noncommercial restriction also needs a use-specific assessment before a commercial catalog could rely on it.
- The National Library of Korea’s open LOD record for Kim Young Ju supports bibliographic metadata reuse only; the round-20 DB readback for her photography booklet has no media rows, and no image license is attached to that metadata record. [NLK record](https://lod.nl.go.kr/resource/KMO202332009); [NLK dataset/reuse terms](https://lod.nl.go.kr/home/dataset/datadownload.do); [Kim Young Ju readback](../../docs/korean-kim-young-ju-photography-booklet-2022-db-readback.json)

### Gaps

- No new influencer photobook was found whose exact cover or preview image is explicitly licensed for R2 storage and public MuseBooks delivery. More generally licensed portrait images do not qualify unless the source ties that exact image to a documented photobook and grants compatible rights.
- The KOGL Type 2 image set is not attached to a photobook product, and commerciality of MuseBooks use has not been established for evaluating that noncommercial asset. No catalog import or image operation was performed for it.
