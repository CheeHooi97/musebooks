# SOOP 2024 Streamer Awards Photobook Follow-up

## Is the work fully identified and can its metadata be reused?

### Takeaway
The existence of a physical group photobook is confirmed, but the exact edition is not bibliographically resolved. No public license or permission was found that clearly authorizes MuseBooks to reuse the product metadata from SOOPTORE; under the project source policy, this remains a research lead and is not ready to import.

### Cited Findings
- SOOP’s ESG page lists “Sale of 2024 Streamer Awards Photo Books” and says the commemorative books were sold as merchandise with all sales proceeds donated ([SOOP ESG 2024](https://corp.sooplive.com/esg/2024/index.php?page=sharing)).
- SOOP’s 2024 event information says the event merchandise package was available through SOOPTORE and directs readers to a product-detail page for details ([official 2024 SOOP event information](https://2024award.sooplive.co.kr/?page=information)). The current visible store link did not resolve to an identifiable book listing in the rendered page review; its linked route was a generic `/products/123999999` route, and the route could not be fetched.
- Kuki News refers to the item as “2024 SOOP 스트리머 대상 포토북” and reports that it was a limited SOOPTORE release offered from January 2025, involving 65 streamers including Gamst, Isegye Idol, Woowakgood, and UjeongIng. It describes a hardcover album of about 100 pages with participant portraits, behind-the-scenes images, event scenes, and performances; buyers could choose a participating streamer’s photograph for the cover ([Kuki News, 12 March 2025](https://m.kukinews.com/article/view/kuk202503120038)).
- SOOP’s event program independently lists UjeongIng among the event’s fan-signing streamers and Isegye Idol as an opening act ([official 2024 SOOP event program](https://2024award.sooplive.co.kr/?page=program)). This supports their event participation, not a complete book credit list.
- SOOPTORE’s terms §22(2) state that information obtained through the mall in which intellectual-property rights belong to the mall may not be reproduced, transmitted, published, distributed, broadcast, or otherwise used commercially or provided to third parties without the mall’s prior approval ([SOOPTORE terms of use](https://sooptore.sooplive.com/terms/use)). The terms do not provide a positive license for MuseBooks’ metadata reuse. Their wording concerns information with mall-owned intellectual-property rights; it is not a legal determination about independent reuse of bare facts from other sources.
- The project source register says public product/press pages are discovery and corroboration sources unless reuse conditions are established, and documents that no source has blanket automated extraction permission ([project source register](../../docs/korean-model-photobook-sources.md)).
- Live read-only catalog checks against the `catalog-preview` service (`database.Open(true, false)`) queried exact Korean title `2024 SOOP 스트리머 대상 포토북` and English title `2024 SOOP Streamer Awards Photobook`, each with `publicationType=photobook`; both returned `total=0`. These exact searches do not prove absence under other aliases.

### Inferences
- The evidence supports classifying this as a physical creator-group photobook lead, not as 65 individually verified Korean models. The articles and official page identify streamers/event participants, but the complete contents and identities are not available.
- Because the exact bibliographic record and an affirmative metadata-use grant are missing, I did not stage or import the item. This is a project-policy hold; I am not making a legal conclusion about whether isolated facts can be reused absent a license.

### Gaps
- No verified ISBN, exact SOOPTORE item identifier, publisher/imprint, exact release date, exact page count, or complete title-page/participant credit list was found. “About 100 pages” is a press description, not an exact pagination statement.
- No express permission or compatible open license was found for commercial reuse of SOOPTORE metadata. A grant covering the specific product page and metadata fields would be needed to clear the project’s current source gate.

## Do the named subjects meet the Korean influencer scope?

### Takeaway
The book is clearly tied to SOOP’s Korean streamer community and includes named online creators, but the reviewed evidence does not establish the nationality or full identity of every participant. Treat it as a Korean creator-group lead rather than as a verified collection of 65 Korean influencer/model records.

### Cited Findings
- Kuki News calls the 65 participants streamers and names Gamst, Isegye Idol, Woowakgood, and UjeongIng as examples ([Kuki News](https://m.kukinews.com/article/view/kuk202503120038)).
- SOOP’s official program identifies UjeongIng, Jipiti, Park Ppippi, and Wanana for its fan-signing lineup, and Isegye Idol for the opening performance ([2024 SOOP event program](https://2024award.sooplive.co.kr/?page=program)).

### Inferences
- The “streamer” designation is adequate to describe the product’s creator theme. It does not establish that all 65 participants are Korean nationals, individual models, or separately credited in the book.

### Gaps
- A complete participant list and authoritative identity/nationality evidence for each named subject were not found. Avoid creating individual person credits from the partial press list alone.

## Is any exact cover image cleared for R2 storage and public delivery?

### Takeaway
No. The reviewed sources do not identify a specific cover asset or grant permission for its storage in R2 and public delivery from MuseBooks.

### Cited Findings
- Kuki News says purchasers could choose a participating streamer’s photograph as the cover, indicating multiple possible cover variants rather than one universal image ([Kuki News](https://m.kukinews.com/article/view/kuk202503120038)).
- SOOP’s official ESG and event pages confirm the fundraiser and merchandise context but do not state an image license for any exact book cover ([SOOP ESG 2024](https://corp.sooplive.com/esg/2024/index.php?page=sharing); [official event information](https://2024award.sooplive.co.kr/?page=information)).
- SOOPTORE’s terms describe mall-owned intellectual property and prohibit certain reuse without prior consent, but do not grant image rights for this photobook ([SOOPTORE terms of use](https://sooptore.sooplive.com/terms/use)).

### Inferences
- Any future upload would need permission tied to the exact selectable cover and confirmation that it covers both R2 storage and public delivery. Product availability or public display on a retailer/press page is not itself that permission.

### Gaps
- No exact cover file/asset URL, selected cover variant, image-rightsholder identification, or written grant for storage and public delivery was found.
- No image was downloaded, copied, or uploaded; no database write or external contact occurred during this follow-up.
