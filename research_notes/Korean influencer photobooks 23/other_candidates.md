# Other Korean Photobook Candidates — Round 23

## Does a new Korean influencer/model photobook clear identity and edition verification?

### Takeaway

One digital-book near miss surfaced: *CLOE Magazine Vol. 2: Hye Rin’s First Photobook*. Apple Books’ indexed product listing describes it as an 87-page English e-book released 14 January 2021 by Blurb Inc. The indexed publisher description calls Hye Rin a Korean model, but I could not independently verify her identity or influencer status from another source, and the Apple product page itself was inaccessible to the page viewer during this pass. Treat it as a lead, not a verified catalog candidate.

### Cited Findings

- Apple Books’ public listing result gives the exact title, provider name CLOE Korea, release date, language, 87-page length, publisher Blurb Inc., and a description calling Hye Rin a Korean model: [Apple Books product listing](https://books.apple.com/gb/book/cloe-magazine-vol-2-hye-rins-first-photobook/id1549141595).
- Attempts to open the product page directly in the US, UK, and Korean storefront paths returned an access/cache error in the available page viewer. The facts above therefore come from the rendered search-result listing, not a successful direct-page inspection.
- The product listing does not show an ISBN or another bibliographic identifier in the accessible result.

### Inferences

- Apple’s listing describes a digital photobook-format product. The model attribution and Korean identity are publisher-provided marketing copy, not independent identity verification.
- A bare name “Hye Rin” is insufficient to confidently match a specific public person without an independent profile or linked creator account.

### Gaps

- No independent source found in this pass confirms the subject’s identity, Korean identity, or influencer activity.
- The exact edition could not be manually inspected on Apple Books, and no ISBN or other stable bibliographic ID was found.
- This near miss does not satisfy the independent identity and source-verification gates for import.

## Do the sources authorize commercial metadata reuse or R2 hosting of an exact image?

### Takeaway

No. Apple’s current service terms do not provide the required commercial reuse permission; they expressly limit service/content use to personal, noncommercial purposes, deny transfer of commercial or promotional rights, and restrict copying or scraping. No exact cover-image license for R2 storage and public delivery was found.

### Cited Findings

- Apple’s Media Services terms say users may use the services and content only for personal, noncommercial purposes, that delivery does not transfer commercial/promotional rights, and that users may not use software or manual processes to scrape or copy portions of the services or content: [Apple Media Services Terms, §F](https://www.apple.com/legal/internet-services/itunes/).
- Apple’s author affiliate materials describe marketing links and approved Apple-branded promotional assets; they do not grant a third party general rights to reuse a book’s bibliographic metadata or cover image: [Apple Books affiliate program guidance](https://authors.apple.com/support/3977-apple-affiliate-program-books-audiobooks), [Apple Books identity guidelines](https://marketing.services.apple/apple-books-identity-guidelines).
- The project source register treats Apple Books as a manual/review discovery source and does not assert metadata extraction or image reuse permission: [project source-use register](../../docs/korean-model-photobook-sources.md).

### Inferences

- The Apple storefront is not an authorized source for commercial metadata reuse under the reviewed terms. The product’s presence there does not confer the rights needed to copy its cover into R2 and deliver it publicly.
- The product page or its cover thumbnail, even if accessible, would be provenance rather than a license grant.

### Gaps

- No separate publisher permission or open data license covering commercial reuse of this exact edition’s factual metadata was found.
- No rights-holder grant covering the exact image, R2 storage, and public delivery was found. No image was downloaded or uploaded.

## Is there already a matching work, edition, or person in MuseBooks?

### Takeaway

A repeatable-read read-only database query returned no matching work, edition, or person rows for this exact title and the name “Hye Rin.” This is a narrow duplicate check, not proof of global absence.

### Cited Findings

- The live database check used `database.Open(true, false)` and a PostgreSQL transaction configured with `ReadOnly: true` and `Isolation: repeatable read`. It searched work original/English titles and edition labels for `CLOE Magazine Vol.2` / `Hye Rin`, editions for the title/name and Apple product ID `1549141595`, and person names containing `Hye Rin`.
- Query output: `readOnly: true`, `matchingWorks: []`, `matchingEditions: []`, `matchingPeople: []`.

### Inferences

- No exact title/person match was returned by the specific fields and terms queried, so there is no evidence from this query of an existing record to reuse.

### Gaps

- Romanized name variants, aliases, an uncredited Korean title, or a work row without the queried product ID may exist outside the search terms. No import was made because identity and metadata-reuse authorization remain unresolved.
