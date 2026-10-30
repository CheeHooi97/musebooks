# Open-Licensed Bibliographic Discovery: Korean Model and Influencer Photobooks (Round 20)

## Newly confirmed candidates from NLK or another explicitly open-licensed metadata source

### Takeaway
I found no new candidate that I could verify simultaneously from an openly reusable bibliographic record and independent Korean model/influencer identity evidence. The best apparent new lead, Magarin’s *Secret B* No. 4, was already in MuseBooks and I could not confirm an NLK LOD record for it; therefore I am not proposing an import.

### Cited Findings
- The existing MuseBooks source manifest identifies `시크릿 B 4호 '머슬퀸' 마가린 화보집`, work `korea-magarin-secret-b-4-2024`, and physical edition `korea-magarin-secret-b-4-2024-print-spomax`; the read-only catalog verification records one photobook edition, one linked listing, and no media reference. [Existing import manifest](../../docs/korean-photobook-magarin-secret-b-4-import.json); [read-only DB verification](../../docs/korean-photobook-magarin-secret-b-4-db-verification.json)
- MAXQ’s official store offers the exact *Secret B* No. 4 item as a photobook in its “books/posters/calendars” section. [Spomax / MAXQ official product page](https://spomax.kr/product/%EC%8B%9C%ED%81%AC%EB%A6%BF-b-4%ED%98%B8-%EB%A8%B8%EC%8A%AC%ED%80%B8-%EB%A7%88%EA%B0%80%EB%A6%B0-%ED%99%94%EB%B3%B4%EC%A7%91/5221/)
- Youngpoong’s bibliographic listing gives the display title `시크릿 B (2025.4호) 머슬퀸 마가린 화보집`, publisher 맥스큐인터내셔널, date 2024-12-27, 114 pages, and serial/barcode `9772799363000`; the listing classifies the product as a magazine. [Youngpoong book record](https://www.ypbooks.co.kr/books/202412304692212430)
- A 2024 influencer-awards video describes Magarin as active across fashion, racing, and fitness modeling and says she won an influencer award in the racing-model category; it also names her as the solo model for *Secret B* No. 4. [The Influencer Awards: Magarin](https://www.youtube.com/watch?v=1DQ6pAz5sx4)
- The 2025 profile article also identifies Magarin as a racing model, records her 2024 influencer-award, and says she was selected for *Secret B* No. 4 in December 2024. [Sports Seoul profile](https://news.nate.com/view/20251208n02046)
- Web search for the exact barcode/title and NLK LOD did not return an NLK record. An attempted direct request to the public LOD SPARQL endpoint did not return usable content. This is an unconfirmed record, not proof that NLK lacks a record. [NLK LOD service](https://lod.nl.go.kr/sparql); [NLK dataset and reuse terms](https://lod.nl.go.kr/home/dataset/datadownload.do)

### Inferences
- Magarin’s title is a strong subject-fit lead, but it is not new to the live catalog; the existing DB verification settles duplicate status for this title.
- The Youngpoong serial-style barcode is not treated here as an ISBN, consistent with the existing record’s blank ISBN field.
- NLK documents its LOD dataset under KOGL Type 1 and CC0 1.0, but that open license can only authorize metadata actually obtained from that dataset. The store and bookseller pages establish bibliographic facts but their terms do not establish an open metadata reuse license. No new record therefore clears the assigned open-metadata requirement.
- Metadata permission, even if later confirmed, would not grant rights to any cover image. The existing Magarin edition has no catalog media reference, and this round made no image copy or R2 upload.

### Gaps
- Whether NLK has an exact LOD record for Magarin’s `9772799363000`/title remains unresolved because the public endpoint request could not be completed in this run.
- I did not find a different, unrecorded Korean creator/model photobook with an exact NLK record and an explicit open metadata license during this bounded round.

## Known titles excluded from new-candidate count

### Takeaway
The checked obvious MAXIM matches were already present in the catalog or earlier research, so they do not count as newly discovered records in this round.

### Cited Findings
- MuseBooks already publishes the MAXIM B-SIDE No. 5 issue featuring Kim So-hee; publisher and press records describe it as her first solo photobook, released 2019-06-10. [MuseBooks catalog page](https://musebooks.my/books/korea-maxim-bside-2019-5-kim-sohee); [Sports Donga report](https://sports.donga.com/ent/article/all/20190605/95862530/1)
- Kim Young Ju’s NLK LOD record and prior import are documented in the preceding round’s report; this is not a new candidate. [Round 19 report](../../reports/Korean%20influencer%20photobooks%2019.md)

### Inferences
- Public catalog presence and the preceding batch record were used only to exclude duplicates; no repeat import or second database write was made.

### Gaps
- No live SQL duplicate scan was necessary for Magarin because the existing project’s live read-only verification file confirms its exact work and edition IDs. The Kim So-hee public catalog page is cited only as an exclusion, not as a source-cleared import proposal.

## Source, access, and catalog-check limits

### Takeaway
This round produced one already-cataloged lead and no new metadata record safe to propose for import. Search coverage is limited by the unavailable direct NLK query response.

### Cited Findings
- The NLK open dataset page documents terms for its LOD dataset and is the applicable license route for an NLK metadata record. [NLK LOD dataset page](https://lod.nl.go.kr/home/dataset/datadownload.do)
- The project’s current read-only verification for Magarin was captured on 2026-10-30 and records `ledgerIntegrityPassed: true`, `goalComplete: false`, and the exact existing work and edition identities. [Magarin DB verification](../../docs/korean-photobook-magarin-secret-b-4-db-verification.json)

### Inferences
- A missing search-engine result or failed endpoint request cannot establish that a bibliographic record does not exist; the result is reported as a research gap.
- No database import, DB mutation, image download, R2 upload, or contact with a creator/publisher was performed for this assignment.

### Gaps
- A later search could retry the NLK public LOD SPARQL service or use NLK’s catalog interface manually, then compare exact work/edition/title/person matches against the live database before any import.
