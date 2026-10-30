# Korean influencer-led digital photobooks — round 20

## Key question 1: Did this pass find a new title that clears creator identity, digital-book, and metadata-source gates?

### Takeaway
No new candidate cleared all three gates. MAXQ’s *Secret B* No. 1 has official publisher evidence that the series began digitally and later received a print edition, but the same named work and print edition are already in the catalog snapshot; MAXQ’s pages do not grant commercial factual-metadata reuse. A newly surfaced RZCOS/STOVE cosplay photo book is an exact downloadable product, but the evidence does not establish its credited cosplayer as a Korean influencer.

### Cited Findings
- MAXQ’s publisher announcement says *Secret B* No. 1 first appeared digitally, then received a print edition, and identifies the paired subjects as Ryu Se-bi (류세비) and Park Eunhye (박은혜). The MAXQ article’s footer says unauthorized reproduction is prohibited; no positive license for commercial catalog reuse is stated. [MAXQ publisher announcement](https://maxq.kr/articles/sikeurit-b-ryusebibakeunhye-hwabojip-yeyakpanmae-opeun)
- MAXQ’s contest profile identifies Park Eunhye as a Chinese-language instructor and YouTuber, names her Instagram account `@grace823_`, and says she operates the YouTube channel 자몽튜브. [MAXQ creator profile](https://maxq.kr/articles/pyojimodeleun-naya-na-maekseukyu-pyojimodel-konteseuteu-bonseon-jinchulja-gonggae)
- A 2021 Sports Seoul report calls Park a YouTuber, names her channel 자몽튜브, and reports about 140,000 subscribers at the time. This supports influencer activity but does not add a new identity/product combination. [Sports Seoul profile](https://www.sportsworldi.com/newsView/20210821503607)
- STOVE’s official store lists *동아리 김가을 코스프레 포토북* (Circles Kim Ga-eul Cosplay Photo Book), credits TOPCO and RZCOS as creator/publisher, gives a 2025-06-26 release date, and describes the item as a downloadable cosplay photobook featuring the character Kim Ga-eul; the description credits “Coser. 시루 [김가을].” The listing does not establish that this person is a Korean influencer or authorize third-party commercial metadata reuse. [STOVE product page](https://store.onstove.com/ko/games/100488)

### Inferences
- The MAXQ announcement establishes a digital-first release history, but not a distinct digital edition with its own product identifier, ISBN, or edition-specific metadata. The publisher’s notice against unauthorized reproduction is not an affirmative license to reproduce page text or reuse the source for a commercial catalog.
- STOVE’s listing is a digital photo-book product lead, not a verified human influencer title: its focus is a cosplay portrayal of a webtoon character, and the credited cosplayer’s identity/origin is not resolved by the product page.

### Gaps
- No new digital title was found with both independently verified Korean influencer identity and a metadata source whose terms clearly authorize commercial factual reuse.
- No title-specific R2 cover/preview-image permission was found. No image or paid file was downloaded or uploaded.

## Key question 2: What did the catalog check establish, and which leads remain held?

### Takeaway
The existing read-only database audit already contains the MAXQ *Secret B* No. 1 physical record and a separate digital MAXQ compilation for Park Eunhye. Neither provides a reason to add the No. 1 listing as a new work; the sources reviewed did not establish a separate No. 1 digital edition to attach. The STOVE cosplay book remains a discovery lead only, so no live duplicate query or import was run for it.

### Cited Findings
- The existing repeatable-read, read-only database verification snapshot lists work `korea-secret-b-no1-ryusebi-jamong-2021` with physical edition `korea-secret-b-no1-print-2021`, and Park Eunhye’s distinct Vol. 03 digital compilation. It records no separate No. 1 digital edition in that audited cohort. [Catalog verification snapshot](../../docs/korean-secret-b-photobooks-db-verification.json)
- The local manifest and prior report record the same physical No. 1 work and digital Vol. 03; this round did not alter them. [Existing import manifest](../../docs/korean-secret-b-photobooks-import.json); [prior report](../../reports/Korean%20influencer%20photobook%20additions%203.md)

### Inferences
- Because the MAXQ work is already cataloged and the publisher provides no clear commercial metadata license, adding another record from the same announcement would risk duplicating the work and would not resolve the source-use gate.
- The STOVE listing did not meet the assignment’s identity/source threshold, so it was not treated as a strong candidate for a live database query.

### Gaps
- A separate, edition-level official record for the MAXQ No. 1 digital release (including stable identifier and format) and an authorized commercial metadata source would be needed to consider a digital edition link.
- The cosplayer “Siru” needs a reliable identity source linking the real person to South Korea and an influencer/creator profile; the STOVE listing alone does not do this.
