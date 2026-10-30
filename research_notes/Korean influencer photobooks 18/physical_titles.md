# Korean Influencer Photobooks 18: Physical Titles

## Commercially usable bibliographic source route

### Takeaway
The National Library of Korea’s ISBN metadata API is the best cleared route found for commercial catalog facts: its government data portal labels the permission scope “unrestricted,” and the library documents queries by ISBN plus output fields for title, author, publisher, pages, format, date, and a cover URL. The API requires a `cert_key`, which is not configured in this workspace, so I could not verify either exact title against the API and did not import a record.

### Cited Findings
- The Ministry of Culture / National Library of Korea dataset description says the ISBN API provides publisher-submitted metadata such as title, author, publisher, pages, size, and planned publication date, and lists its permitted-use scope as unrestricted. [Public Data Portal: National Library ISBN Bibliography API](https://www.data.go.kr/data/3078982/openapi.do)
- The National Library’s API guide documents an ISBN query parameter and output fields including title, author, ISBN, publisher, pages, book size, format, publication date, and cover-image URL; the request requires an API `cert_key`. [National Library of Korea ISBN Bibliography API Guide](https://www.nl.go.kr/NL/contents/N31101030500.do)
- Aladin’s terms, Article 20(2), prohibit using information obtained through its mall for profit without prior consent. [Aladin Terms of Use](https://www.aladin.co.kr/m/join/mJoin_rules.aspx?rule=5)
- The KPA PDF itself did not display a reuse license in its indexed record; a direct fetch returned HTTP 403, and searches for KPA terms did not surface a permission covering commercial reuse of this particular list. No specific prohibition clause was found for the PDF, so its license status remains unclear rather than affirmatively restrictive. [KPA, New Books of May 2023](https://member.kpa21.or.kr/wp-content/uploads/sites/2/2023/06/2023%EB%85%84-5%EC%9B%94%EC%9D%98-%EC%8B%A0%EA%B0%84.pdf)

### Inferences
- For these candidates, the National Library API is a suitable onward route once an authorized API key is available; a public retailer page alone is not cleared as the metadata source for a commercial catalog.
- No key name matching ISBN/National Library/data.go was present in `backend/.env` or the current process environment (only variable names were checked; no secret values were displayed).

### Gaps
- The exact National Library API record for ISBN `9791197931567` could not be fetched without `cert_key`; no exact ISSN or publisher catalog record for Candy NO.1 was located.
- The Korean Publishers Association’s monthly new-title PDF supplies useful facts for Kim Young Ju but its page did not state a reuse license; retain it as corroboration rather than the cleared commercial source. [KPA, New Books of May 2023](https://member.kpa21.or.kr/wp-content/uploads/sites/2/2023/06/2023%EB%85%84-5%EC%9B%94%EC%9D%98-%EC%8B%A0%EA%B0%84.pdf)
- Searches for `나다움북스` and the exact Kim Young Ju title did not reveal an official publisher or author page independently confirming that title; the author-page and press sources confirm model work, not publication metadata.

## KIM YOUNG JU 김영주 화보집

### Takeaway
This is an exact physical, print-on-demand model photobook candidate with an ISBN and Korean publisher. Kim Young Ju’s author bio and a contemporaneous sports press profile converge on a distinctive identity (a woman in her 40s, a cultural planner, and a fitness/model figure), but retailer terms block commercial use of its page-derived facts without prior consent, while the alternative KPA record has no explicit reuse license and differs on page count. Hold metadata import until the exact National Library API record or publisher permission/source is available.

### Cited Findings
- The KPA May 2023 new-title list records `KIMYOUNGJU 김영주 화보집`, author 김영주, 133 pages, ₩19,500, publisher 나다움북스, and ISBN `9791197931567`. [KPA, New Books of May 2023](https://member.kpa21.or.kr/wp-content/uploads/sites/2/2023/06/2023%EB%85%84-5%EC%9B%94%EC%9D%98-%EC%8B%A0%EA%B0%84.pdf)
- The book-linked author profile says Kim Young Ju works as a housewife and fitness model, is a working mother and cultural planner, and that the book collects her model photographs from 2019–2022 made with 25 photographers. [Aladin author profile](https://www.aladin.co.kr/author/wauthor_overview.aspx?AuthorSearch=%409123536)
- Sports Seoul described a 40s cultural planner and fitness model Kim Young Ju who won the 2022 Musclemania Figure Grand Prix, and reported her MAXQ special-edition photo-shoot. [Sports Seoul, 28 February 2023](https://www.sportsseoul.com/news/read/1202040)
- Aladin describes the item as POD and explains that a paper copy is produced from a digital file when ordered; it lists ISBN `9791197931567`, 134 pages, A4 dimensions, and publication date 2022-12-05. The 134-page count conflicts with KPA’s 133-page entry. [Aladin product record](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=307017330)
- The live-catalog read-only duplicate lookup returned **0 matching work/edition rows** for `김영주`, `YOUNG JU`, or ISBN `9791197931567`.

### Inferences
- The author-profile subject and the Sports Seoul model are likely the same person: both are characterized as a 40s cultural planner and fitness model, and the product-linked biography identifies its subject’s modeled photo sessions. This is a strong identity match, not an explicit cross-reference between the article and ISBN record.
- The Korean title, domestic publisher, KPA bibliographic entry, and Korean-language profile support classifying the publication as Korea-origin. The opened sources establish modeling activity, but do not establish a large social following; categorize as a model rather than claiming influencer reach.

### Gaps
- Need the exact National Library API record or a publisher-side catalog entry with terms permitting commercial bibliographic reuse; current API lookup is blocked by the missing key.
- KPA reports 133 pages while Aladin reports 134; omit page count pending authoritative resolution.
- No cover asset permission was found for storage in R2 or public delivery. Do not collect or upload a cover.

## 캔디 화보집 NO.1 꾸뿌

### Takeaway
The exact physical issue and its named model are clear from retailer listings and MAXIM/press identity sources, but the available bibliographic route is not reuse-cleared, and retailer classification treats it as a men’s magazine rather than an unambiguous standalone photobook. Hold import pending a publisher or authorized open bibliographic record that establishes product type and terms.

### Cited Findings
- Aladin and YES24 list `캔디 화보집 NO.1 꾸뿌` / `캔디 NO.1 꾸뿌`, credited to 김선광 and 라이트미디어, dated 2025-03-14, with 128 pages and 210×275 mm dimensions. Both retailer records place it in the men’s-magazine category and display `9773059141000` (YES24 also shows `30591414` as its ISBN-10 field). [Aladin product record](https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=360355817), [YES24 product record](https://www.yes24.com/product/goods/143544132)
- MAXIM Korea’s BCUT creator profile labels 꾸뿌 as a model and identifies her creator-page work; Sports Seoul identifies the public stage name 꾸뿌 with a MAXIM model/influencer profile. [MAXIM Korea BCUT profile](https://bcut.maximkorea.net/creator/28), [Sports Seoul profile](https://www.sportsseoul.com/news/read/792965)
- Aladin’s Article 20(2) terms block commercial use of information obtained through the mall absent prior consent. [Aladin Terms of Use](https://www.aladin.co.kr/m/join/mJoin_rules.aspx?rule=5)
- The live-catalog read-only duplicate lookup returned **0 matching work/edition rows** for `캔디`, `꾸뿌`, `CANDY NO.1`, or the retailer-displayed number `9773059141000`.

### Inferences
- The title and model name probably describe a photobook-style issue, but the retailer’s men’s-magazine classification plus serial-style numbering leaves the work-type boundary unresolved; do not force it into the standalone-photobook category.
- The 977-prefixed number should not be stored as an ISBN without validation against an official serial/bibliographic source. The retailer’s ISBN label is insufficient by itself.

### Gaps
- No direct publisher listing, exact National Library/ISSN record, or clear commercial-reuse license for the bibliographic facts was found.
- The product’s classification as a photobook versus a magazine issue needs publisher or authoritative library confirmation.
- No permission for the specific cover image to be stored in R2 and publicly delivered was found; do not collect or upload a cover.
