# Korean Physical Creator Photobooks in Retail Catalogs

## Which new physical creator photobook has an exact retail edition record?

### Takeaway

One new candidate meets the product evidence threshold: **임팩트 정다연 화보집** (Impact Photobook: Jung Da-yeon), a physical portrait photobook featuring Korean fitness model and Pilates instructor Jung Da-yeon. Youngpoong Bookstore lists an exact standalone edition with a publisher, date, product identifier, and pagination; its August 2019 date conflicts with a contemporaneous report that online presales began in March 2019, so retain that discrepancy rather than silently normalizing the date.

### Cited Findings

- Youngpoong Bookstore lists **임팩트 정다연 화보집**, credits the editorial department, names **임팩트크루** (Impact Crew) as publisher, gives the date **2019-08-08**, identifier **9772635471005** (the retailer labels this ISBN-13), **204 pages**, and product composition as a standalone book. The page does not supply a usable physical size. [Youngpoong product record](https://www.ypbooks.co.kr/books/202308233114560575)
- A contemporaneous report says Impact Crew began online presales of “임팩트화보집 정다연” on March 30, 2019 and identifies it as a personal photobook featuring Jung Da-yeon. This indicates a date conflict with the later August 8 retailer metadata; it may reflect preorder versus listing/release date, but the source does not resolve that. [Sidae report](https://www.sidae.com/article/2019040414378040003)
- Sports Seoul identifies Jung Da-yeon as a fitness model and Pilates-center CEO, says she used a personal social account to share fitness and daily-life content with fans, and reported about 40,000 followers in April 2019. [Sports Seoul profile](https://www.sportsseoul.com/news/read/749739)
- Wikitree identifies the Instagram account embedded in its profile as **정다연 (@jblanc_pila)** and explicitly connects that account to the named fitness model and her “임팩트화보집 정다연.” [Wikitree profile with embedded Instagram posts](https://www.wikitree.co.kr/articles/453827); [creator account](https://www.instagram.com/jblanc_pila/)
- The current `docs/korean-*-import.json` scan and targeted search for `임팩트`, `정다연`, `jungdayeon`, and `Impact` found no existing imported manifest for this title. It also does not appear among the held candidates summarized in reports 8 and 9.

### Inferences

- Catalog it as a single physical photobook work/edition featuring Jung Da-yeon; the retailer's standalone title, publisher, identifier, and pagination support that interpretation.
- The identifier is reported exactly as the bookseller labels it. Because it begins with `977`, treat it as a retailer-supplied product identifier/ISBN-13 field and avoid reformatting or inferring a separate ISBN until another bibliographic source confirms it.
- The reported creator trail supports a featured-person credit and the requested creator/model scope; it does not establish that Jung Da-yeon authored or photographed the book.

### Gaps

- The release-date conflict is unresolved: Youngpoong gives August 8, 2019, while the March 2019 report describes online presales beginning March 30. No second retailer or publisher page for this exact edition was found in this pass.
- No physical dimensions were found.
- No publisher/creator terms granting reuse of the cover or interior were found. Retail listing visibility is not a reuse license; do not copy any image to R2 without asset-specific permission.

## Do nearby Impact Crew records provide additional new creator titles?

### Takeaway

Impact Crew appears to have issued several additional model-specific photobooks, but this scan did not verify exact edition metadata for those titles beyond the Jung Da-yeon candidate. Keep them as research leads rather than importing them from search-result snippets.

### Cited Findings

- Kyobo's Impact Crew search page lists separate model-specific records including **임팩트(Impact): 이소영 화보집**, **김민지 화보집**, **민한나 화보집**, **걸크러쉬**, **정유나**, **정혜율**, **유니드(UNEED)**, and **임팩트(Impact). 1: 정다연**; it shows publisher/date snippets, but this pass did not open and verify each individual edition's exact identifier and pagination. [Kyobo Impact Crew catalog search](https://search.kyobobook.co.kr/search?chrc=%EC%9E%84%ED%8C%A9%ED%8A%B8%ED%81%AC%EB%A3%A8&keyword=%EC%9E%84%ED%8C%A9%ED%8A%B8%ED%81%AC%EB%A3%A8)
- The Youngpoong catalog page directly verifies the Jung Da-yeon standalone record described above. [Youngpoong product record](https://www.ypbooks.co.kr/books/202308233114560575)

### Inferences

- These model-specific listings are plausible candidates for later retail verification, but a search-result title alone is insufficient to create a new work or edition record.

### Gaps

- The other Impact Crew listings need exact edition pages, identifiers, page counts/dimensions, and individual creator evidence before inclusion.
- No asset-specific image permissions were established for any Impact Crew item.

## Does the retail evidence authorize R2 image hosting?

### Takeaway

No. This turn found no image-reuse license for the Jung Da-yeon book; keep the candidate metadata-only unless permission covering the exact asset and R2 hosting is obtained.

### Cited Findings

- Youngpoong's page provides a commercial product listing and catalog metadata but no stated license to reproduce the cover or interior images. [Youngpoong product record](https://www.ypbooks.co.kr/books/202308233114560575)
- The contemporary announcement identifies the producer and presale but does not state image-hosting or redistribution rights. [Sidae report](https://www.sidae.com/article/2019040414378040003)

### Inferences

- A retailer's display of a cover for product discovery does not by itself grant MuseBooks permission to copy that image into its own R2 bucket.

### Gaps

- Written permission or a clearly applicable license for a specific cover/interior asset was not located. No image was copied, downloaded for catalog use, or uploaded to R2.

## Focused verification addendum

### Takeaway

Treat **9772635471005 as a barcode/retailer identifier, not an ISBN**. A second exact Kyobo listing corroborates an August 2019 Impact Crew catalog record for Jung Da-yeon, but it does not expose page count or ISBN in the accessible catalog response. The earlier March source is expressly about a preorder window, so it does not by itself disprove an August catalogue/release date; however, the actual release/fulfillment date remains unresolved. Recommendation: the work is importable as a physical photobook with **ISBN blank** and the reported barcode retained only as a source-supplied product identifier if the schema supports it; leave release date blank until the March preorder versus August retail-date ambiguity is resolved.

### Cited Findings

- The International ISBN Agency says the ISBN prefix element currently can only be **978 or 979**. As `9772635471005` starts with 977, it is **not an ISBN-13**, despite Youngpoong's field label. [International ISBN Agency: What is an ISBN?](https://www.isbn-international.org/index.php/content/what-isbn/10)
- The ISSN International Centre says **977** is the EAN-13 prefix assigned to serial publications; the next seven digits encode the ISSN without its check digit, the next two are variable, and the thirteenth is the EAN check digit. The listed string can be segmented as `977 | 2635471 | 00 | 5`, matching that barcode structure. This structural resemblance does not prove an ISSN was allocated or identify its serial title. [ISSN International Centre: EAN-13 barcode structure](https://www.issn.org/understanding-the-issn/issn-uses/identification-with-the-ean-13-barcode/)
- Youngpoong remains the only exact edition page found that supplies the Jung Da-yeon title, Impact Crew, 204 pages, and the 977-prefixed code; it labels that code ISBN-13 and gives 2019-08-08. It does not give dimensions. [Youngpoong exact product record](https://www.ypbooks.co.kr/books/202308233114560575)
- Kyobo's exact Impact Crew catalog search shows a separate record titled **임팩트(Impact). 1: 정다연**, by Impact Crew, dated **2019-08-12**. Its linked product is [Kyobo item S000000330301](https://product.kyobobook.co.kr/detail/S000000330301); the available product response did not expose further bibliographic fields. [Kyobo Impact Crew catalog results](https://search.kyobobook.co.kr/search?chrc=%EC%9E%84%ED%8C%A9%ED%8A%B8%ED%81%AC%EB%A3%A8&keyword=%EC%9E%84%ED%8C%A9%ED%8A%B8%ED%81%AC%EB%A3%A8)
- The March 2019 report describes **2019-03-30 to 2019-04-14 as an online preorder period**, not a confirmed publication or fulfillment date, and says the product would include an unreleased video bonus and a later showcase/fan meeting. [Newstown preorder report](https://www.newstown.co.kr/news/articleView.html?idxno=405209)
- An April 24, 2019 Seoul News report says the book had been published the previous month but also says it sold out during preorder before its release. That wording is internally ambiguous; it does not settle when physical copies shipped. [Seoul News report](https://m.go.seoul.co.kr/news/twig/entertainments/2019/04/24/20190424500112?cp=go)
- Kyobo lists other Impact Crew model-specific books by Lee So-young, Kim Min-ji, Min Hanna, Girl Crush, Jeong Yuna, Jung Hyeyul, and UNEED, with catalog dates and titles. The accessible listing/product data in this pass did not establish exact pagination and edition identifiers for these works, so no additional candidate meets the requested edition-ready threshold. [Kyobo Impact Crew catalog results](https://search.kyobobook.co.kr/search?chrc=%EC%9E%84%ED%8C%A9%ED%8A%B8%ED%81%AC%EB%A3%A8&keyword=%EC%9E%84%ED%8C%A9%ED%8A%B8%ED%81%AC%EB%A3%A8)

### Inferences

- The March preorder report and August catalog dates may represent planned presales followed by a later retail listing/release, but the reporting's ambiguous April wording prevents firm reconciliation. Store neither March nor August as a normalized release date without a stronger publisher or library record.
- The exact title, creator, publisher, and physical format are supported by retailer and contemporary reporting; page count is supported only by Youngpoong. This is enough for a metadata-only candidate if the catalog permits missing ISBN/date and can preserve a non-ISBN source identifier separately.
- No other Impact Crew listing was imported or recommended as ready in this pass; search-result listing titles and dates alone do not establish complete editions or first-party creator identity.

### Gaps

- No second exact source located in this pass confirms the 204-page count or a true ISBN. No matching National Library/ISSN registry record for the alleged code was located.
- Actual shipment/release timing remains unknown; the March press material calls its date a preorder interval, while the April account is ambiguous and the August bookseller dates are catalog metadata.
- Exact page counts, edition identifiers, and creator-profile evidence remain to be verified for the other Impact Crew catalog entries.
