# Open Bibliographic Search for Korean Creator Photobooks (Round 21)

## Did a new candidate clear creator, product, and open-metadata gates?

### Takeaway
No new candidate cleared all three gates in this pass. The strongest subject-fit lead is MAXQ’s physical *Secret B* No. 4 featuring Magarin, but it is already in MuseBooks and I did not verify an exact National Library of Korea (NLK) open-catalog record for it. Its detailed bibliographic fields still come from a bookseller record without an identified commercial metadata-reuse grant.

### Cited Findings
- MAXQ’s official Spomax store names the exact product `시크릿 B 4호 '머슬퀸' 마가린 화보집`, lists it under books/posters/calendars, and gives physical shipping information. The page also displays a “SOLD OUT” marker, so it does not establish current availability. [Spomax product page](https://spomax.kr/product/%EC%8B%9C%ED%81%AC%EB%A6%BF-b-4%ED%98%B8-%EB%A8%B8%EC%8A%AC%ED%80%B8-%EB%A7%88%EA%B0%80%EB%A6%B0-%ED%99%94%EB%B3%B4%EC%A7%91/5221/)
- A 2025 Sports Seoul profile republished by Nate describes Magarin as a model, reports about 140,000 followers and influencer-award recognition, and says she was selected as the sole model for *Secret B* No. 4 in December 2024. The article supports creator/influencer relevance; it does not expressly state her citizenship. [Sports Seoul article via Nate](https://news.nate.com/view/20251208n02046)
- A previously captured Youngpoong listing gives the bibliographic title `시크릿 B (2025.4호) 머슬퀸 마가린 화보집`, publisher MAXQ International, date 2024-12-27, 114 pages, and code `9772799363000`. That code is serial-style, not a verified ISBN; the listing classifies the product as a magazine. The current web fetch returned a cache miss, so these fields are cited as the earlier captured listing, not as a fresh page observation. [Youngpoong listing](https://www.ypbooks.co.kr/books/202412304692212430); [round-20 research report](../../reports/Korean%20influencer%20photobooks%2020.md)
- NLK documents the LOD download dataset under KOGL Type 1 and CC0 1.0, which can authorize factual metadata actually drawn from that dataset; this license does not cover cover artwork. No exact LOD record for the Magarin title or serial was confirmed in this pass. [NLK LOD dataset and license](https://lod.nl.go.kr/home/dataset/datadownload.do)
- The project source register says NLK collection for this workflow should use the public catalogue page and that no API is part of that route. It separately states that public catalog access does not license cover-image reuse. [Project source register](../../docs/korean-model-photobook-sources.md)

### Inferences
- Magarin’s product and influencer evidence make this the best title-fit lead reviewed here, but the identity of an applicable open-licensed bibliographic record remains unverified. Spomax and Youngpoong establish product facts, not a commercial factual-metadata license.
- The NLK dataset’s CC0/KOGL terms cannot be applied to a record that was not identified in that dataset. Absence from indexed search results or an unavailable page is not evidence that NLK has no record.
- The record has no verified ISBN in the existing manifest; the serial-style barcode should not be promoted into the ISBN field. [Existing Magarin import manifest](../../docs/korean-photobook-magarin-secret-b-4-import.json)

### Gaps
- Public web searches for the exact serial and title on NLK catalogue domains returned no indexed result. The NLK catalogue guidance page failed to load through the web reader, and the Youngpoong product page returned a cache miss. These failures leave the manual catalogue search unresolved; they do not prove the record is absent. [NLK catalogue search guidance](https://books.nl.go.kr/NL/contents/N11400000000.do); [NLK catalogue](https://www.nl.go.kr/)
- Before noticing the project register’s no-API restriction, I made one low-volume read-only SPARQL request to NLK: the broad query returned generic, unrelated matches; a narrower title-term query timed out after 25 seconds. I did not use those results to assert candidate metadata or absence. No further endpoint requests were made. [NLK LOD service](https://lod.nl.go.kr/sparql); [project source register](../../docs/korean-model-photobook-sources.md)

## Is the strongest lead new to the MuseBooks catalog, and what remains unresolved?

### Takeaway
No: the prior repeatable-read, read-only MuseBooks audit already contains Magarin’s work and physical edition. This pass therefore proposes no import. The exact cover remains absent from the stored media, and no R2 write was attempted.

### Cited Findings
- I reran the exact candidate audit on 2026-10-30 13:27:51 UTC using a repeatable-read PostgreSQL transaction with `READ ONLY`. It reported `Audited 1 works/1 editions/1 item references/0 media references: 0 integrity findings`, one linked listing, and the existing physical edition `korea-magarin-secret-b-4-2024-print-spomax`; the title, date 2024-12-27, and 114-page extent match the manifest. The temporary audit output was removed after reading, and no database write occurred. The persisted prior audit remains linked for its complete snapshot. [Read-only Magarin DB verification](../../docs/korean-photobook-magarin-secret-b-4-db-verification.json); [existing import manifest](../../docs/korean-photobook-magarin-secret-b-4-import.json)
- The audit has no cover URL and identifies `cover_unknown`; the project register states that source URLs/provenance are not permission to store and publicly deliver an image from R2. [Read-only Magarin DB verification](../../docs/korean-photobook-magarin-secret-b-4-db-verification.json); [project source register](../../docs/korean-model-photobook-sources.md)
- Kim Young Ju’s 2022 *photography booklet* already has an NLK LOD record and was imported in round 19. The existing report classifies her as a model and says the reviewed evidence does not establish influencer reach, so it is neither a new catalog record nor a verified influencer-qualified addition. [NLK record](https://lod.nl.go.kr/resource/KMO202332009); [round-19 report](../../reports/Korean%20influencer%20photobooks%2019.md)

### Inferences
- The fresh repeatable-read audit confirms the exact candidate work and edition already exist; no new import or database change is warranted.
- R2 rights are a separate gate from factual metadata licensing. The metadata source gap and the exact-image reuse gap remain distinct.

### Gaps
- A manual NLK catalogue search or an exact NLK record with a documented open license is still needed before treating Magarin’s factual fields as source-cleared for a new import; the live duplicate already makes a second work record unnecessary.
- No exact-cover authorization for R2 storage and public delivery was found. No image or paid file was downloaded, copied, or uploaded, and no database write or creator/publisher contact occurred in this pass.
