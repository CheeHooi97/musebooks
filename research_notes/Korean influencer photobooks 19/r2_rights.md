# Korean influencer photobook cover reuse rights

## Does the current catalog show an exact cover licensed for R2 storage and public delivery?

### Takeaway

No current Korean influencer photobook cover has documented permission for both R2 storage and public delivery. A live read-only PostgreSQL review found 153 published Korean photobook editions; 10 editions have a cover URL, but none has an R2 object key, an R2-hosted URL, or a stored URL distinct from its original source. The cover URLs remain remote references. The catalog's `catalog_media` provenance fields identify the source and URL, not a reuse license. This is a database snapshot, not a legal conclusion about fair use or other statutory exceptions.

### Cited Findings

- The read-only query used `database.Open(true, false)`, whose PostgreSQL connection sets `default_transaction_read_only=on`; it selected published `KR` photobooks and checked each edition's `cover_url`, `original_cover_url`, `cover_object_key`, edition-level `catalog_media`, and work-level cover/media references. Result: 142 works, 153 editions, 10 editions with a cover URL, 20 edition-media rows, eight works with work-level cover/media records, zero cover object keys and zero R2/distinct-storage assets. The edition and work media rows preserve the same external URL as the original source; representative DB records are linked below. [DJ SODA physical DB verification](../../docs/korean-photobook-dj-soda-candid-publisher-db-verification.json); [DJ SODA digital DB verification](../../docs/korean-photobook-dj-soda-candid-apple-db-verification.json); [Kim Seolhwa DB verification](../../docs/korean-photobook-kim-seolhwa-26-yes24-db-verification.json); [Pyo Eunji Rondo DB verification](../../docs/korean-photobook-pyo-eunji-rondo-db-verification.json)
- Shueisha says its publications and website images are protected and rights belong to each rightsholder; its FAQ says it does not grant individuals permission to use book covers, jackets, or packaging photographs, and does not answer or review individual inquiries. This is not a public license for R2 storage or delivery. [Shueisha cover-reuse FAQ](https://faq.shueisha.co.jp/faq/show/28?back=front%2Fcategory%3Ashow&category_id=2&faq_id=17&site_domain=default)
- KADOKAWA's general rights page rejects unauthorized use of publisher-issued publications and images. Its cover-use rules give a limited, conditional route for book introductions: certain library/media uses, unmodified covers from KADOKAWA product pages that allow image saving, required bibliographic credits, and title-specific conditions. The rules direct broadcast/video/internet distribution to an inquiry route; they do not establish permission for MuseBooks' public R2 delivery without that review. The previous exact-title review of Pyo Eunji's *Rondo* found the exception list unverified and marked the exact asset unapproved. [KADOKAWA works-use policy](https://www.kadokawa.co.jp/copyrightpolicy/); [KADOKAWA cover-use rules](https://www.kadokawa.co.jp/support/b/library/); [prior exact Pyo Eunji policy review](../../docs/korean-photobook-pyo-eunji-kadokawa-cover-policy-review.json)
- Pyo Eunji's official fanclub terms prohibit unauthorized copying, transfer, reposting, and public transmission of site/fanclub images and other content, and prohibit copying or commercial use of service information on another site without prior written consent. They do not grant a reuse license for product-image assets. [Pyo Eunji official terms, clauses 11 and 13](https://pyoeunji.com/pages/terms)
- Apple states that delivery of Apple Services or content does not transfer commercial or promotional use rights. That means an Apple Books image URL is not permission to mirror the artwork into a public catalog. [Apple Media Services terms](https://www.apple.com/legal/internet-services/itunes/us/terms.html)
- YES24's product record for *김설화 26* identifies it as the first solo photobook of influencer/model 김설화, credits publisher 아이다호 and author 로글, and notes two randomly supplied cover designs. MuseBooks' current exact image reference is YES24's `https://image.yes24.com/goods/116981923/XL`; the product record does not supply a rightsholder license for copying that exact image to R2. No official Idaho image-use policy or public rights contact route was found in the scoped checks. [YES24 exact product page](https://www.yes24.com/product/goods/116981923)
- Shueisha's business inquiry site is publicly identified for business/rights-use questions; its existence is a contact route, not approval. [Shueisha corporate/business inquiry](https://faq.shueisha.co.jp/?site_domain=business)
- KADOKAWA provides public publication-use and media inquiry routes for title-specific cover-use requests. [KADOKAWA publication/media contact](https://www.kadokawa.co.jp/support/b/); [KADOKAWA media inquiry](https://wwws.kadokawa.co.jp/support/b/media/)
- Pyo Eunji's official site publishes a contact page for its official fanclub/site operator. [Pyo Eunji official contact](https://pyoeunji.com/en/pages/contact)

### Inferences

- A source-attributed public URL or ordinary display on a publisher/retailer page establishes provenance, not a license to copy the image, store a separate copy in R2, or serve it from MuseBooks. None of the checked policies grants the required combined storage-and-public-delivery scope for the exact candidate assets.
- KADOKAWA's limited cover rules may support some forms of book-introduction use, but the relevant Internet-delivery request is routed to inquiry and the title-specific conditions were not confirmed. Treating it as permission for R2 would exceed the evidence.
- No attribution text can cure the missing grant. If rights are pursued, the request should identify the exact image URL, work/edition, R2 storage, public delivery through MuseBooks, any resizing/format conversion, term/territory, and requested credit.

### Gaps

- No written permission record for any exact candidate image was found in the catalog metadata or reviewed project documents. No rights-holder was contacted.
- No public license or rights-holder contact route was identified for the *김설화 26* cover beyond the retailer page; the publisher/author would need to be reached through a verified public business contact if one is later found.
- The KADOKAWA special-condition list and the image-save eligibility of each Pyo title were not fully established. Even if those conditions were satisfied, the public policy directs Internet distribution to an inquiry and no approval is documented.

## Which exact influencer cover assets are in the database, and what permission applies to each?

### Takeaway

The database contains exact remote cover references for DJ SODA's *Candid*, Kim Seolhwa's *26*, and Pyo Eunji's titles. These eight editions are the influencer-focused subset of the 10 Korean photobook editions with cover URLs; the other two covers belong to *SANTORINI* and *BE JOYFUL*, which were excluded from this influencer-specific review. No exact cover below is stored in R2.

### Cited Findings

| Work / edition in current database | Exact cover asset (`edition.cover_url`) | Rights result |
|---|---|---|
| *DJ SODA写真集『Candid』*, `korea-dj-soda-candid-2024-jp-print` | `https://wpb.shueisha.co.jp/gravure/info/images/410449f9028d78d0cac98f3b9e1633f8113310f6.jpg` | Shueisha's official publication page identifies the book, Korean-born DJ SODA, and a 20-million-plus combined social audience; its official FAQ grants no cover-use permission to individuals. No R2 license. [Publisher page](https://wpb.shueisha.co.jp/gravure/info/20240216-122279/); [rights FAQ](https://faq.shueisha.co.jp/faq/show/28?back=front%2Fcategory%3Ashow&category_id=2&faq_id=17&site_domain=default) |
| *DJ SODA写真集『Candid』*, `korea-dj-soda-candid-2024-jp-digital` | `https://is1-ssl.mzstatic.com/image/thumb/Publication221/v4/2e/bf/12/2ebf1261-0203-2b67-ba58-c65c710e960e/08790156051224000000.jpg/626x0w.webp` | Apple Books CDN asset. Apple content access does not grant commercial/promotional rights; Shueisha's cover policy supplies no public reuse grant. No R2 license. [Apple Books title page](https://books.apple.com/jp/book/dj-soda%E5%86%99%E7%9C%9F%E9%9B%86-candid/id6480587148); [Apple terms](https://www.apple.com/legal/internet-services/itunes/us/terms.html) |
| *김설화 26*, `korea-kim-seolhwa-26-print-yes24` | `https://image.yes24.com/goods/116981923/XL` | YES24-hosted image for the exact 2022 photobook; publisher listed as 아이다호. No official image-reuse license or public rights contact route identified. No R2 license. [Exact product page](https://www.yes24.com/product/goods/116981923) |
| Pyo Eunji *Rondo* print, `korea-pyo-eunji-rondo-2023-jp-print` | `https://pyoeunji.com/cdn/shop/files/71gw11c9DjL._SL1500_grande.jpg?v=1707811313` | Official artist-store image for the KADOKAWA book. The asset is not the KADOKAWA-hosted product-page cover to which its limited cover-use rule refers; no R2 license. [KADOKAWA product](https://www.kadokawa.co.jp/product/322303002115/); [Pyo official terms](https://pyoeunji.com/pages/terms) |
| Pyo Eunji *Rondo* digital edition, `korea-pyo-eunji-rondo-2023-jp-digital` | `https://cdn.kdkw.jp/cover_1000/322303/322303002121.webp` | KADOKAWA-hosted exact digital cover. Limited cover-use rules do not confirm R2/public Internet delivery; Internet distribution is directed to inquiry, and no approval/exception-list clearance is recorded. [KADOKAWA product](https://www.kadokawa.co.jp/product/322303002121/); [cover-use rules](https://www.kadokawa.co.jp/support/b/library/) |
| Pyo Eunji digital *円舞曲* all-other edition, `korea-pyo-eunji-enbukyoku-2023-jp-digital` | `https://cdn.kdkw.jp/cover_1000/322310/322310001500.webp` | Same conditional KADOKAWA position; no exact R2 approval. [KADOKAWA product](https://www.kadokawa.co.jp/product/322310001500/); [cover-use rules](https://www.kadokawa.co.jp/support/b/library/) |
| Pyo Eunji official fanclub first book / Japan visit cover, `korea-pyo-eunji-fanclub-first-2022-jp-visit-cover` | `https://pyoeunji.com/cdn/shop/products/A___No1_grande.png?v=1724745338` | Official-store product image. Site/fanclub terms do not authorize third-party reproduction/public transmission; no R2 license. [Pyo official terms](https://pyoeunji.com/pages/terms) |
| Pyo Eunji *PHOTO BOOK 2022*, `korea-pyo-eunji-fanclub-photo-book-2022-jp-print` | `https://pyoeunji.com/cdn/shop/products/FjXeDhfUoAA429M_55dbc58f-3f8c-4f15-b7b5-c0b89b102539_grande.jpg?v=1672028251` | Official-store product image. Site/fanclub terms do not authorize third-party reproduction/public transmission; no R2 license. [Pyo official terms](https://pyoeunji.com/pages/terms) |

### Inferences

- For Shueisha and KADOKAWA, the official contact routes are appropriate places to request exact, written rights; they are not evidence that approval will be granted. For Pyo Eunji store images, the site provides its official contact page. No outbound contact was made.
- YES24 is the recorded host for Kim Seolhwa's asset, not an identified grantor of R2 rights. A rightsholder permission would need to identify the exact cover variant, since the product listing states the book was supplied with one of two randomly selected covers.

### Gaps

- There is no license text, allowed attribution, term, territory, or storage/delivery scope for any exact candidate image above. All remain ineligible for an R2 upload based on the evidence currently on file.
- No permission contact was sent, and no rightsholder response exists. If permission is later obtained, attach it to the exact work, edition, and image URL before copying the asset to R2.
