# Alternate bibliographic sources: Korean creator/model photobooks

## Kim Young Ju — imported from the NLK LOD record

### Source and exact bibliographic result
- Queried the public National Library of Korea LOD SPARQL endpoint (`https://lod.nl.go.kr/sparql`) without a private key. ISBN query: `SELECT ?s ?p ?o WHERE { ?s <http://purl.org/ontology/bibo/isbn> "9791197931567" . ?s ?p ?o . } LIMIT 25`.
- Exact result: `https://lod.nl.go.kr/resource/KMO202332009`. The returned record identifies creator `김영주`, publisher `Nadaum(나다움북스)`, year `2022`, ISBN `9791197931567`, extent `133 p`, physical size `30 cm`, and remainder of title `photography booklet`.
- A focused title query returned `dcterms:title = "Kim Young Ju"` and `lod:remainderOfTitle = "photography booklet"`. Accordingly, the import preserves `originalTitle: "Kim Young Ju"` and the complete title/subtitle in `englishTitle: "Kim Young Ju: photography booklet"`.
- NLK's LOD dataset downloads are documented as KOGL Type 1 and CC0 1.0, providing an authorized public source for factual catalog metadata: [NLK LOD dataset/download and license](https://lod.nl.go.kr/home/dataset/datadownload.do). The NLK record itself is the metadata source URL.
- A separate press source identifies Kim Young Ju as a Korean fitness model and cultural planner; it supports cataloging her as a model, without claiming social-media influencer reach: [Sports Seoul, 28 February 2023](https://www.sportsseoul.com/news/read/1202040).
- KPA's May 2023 title list also corroborates the ISBN and Korean title, but its commercial reuse terms were not established; it was not used to fill or override imported fields: [KPA, May 2023 new-title list](https://member.kpa21.or.kr/wp-content/uploads/sites/2/2023/06/2023%EB%85%84-5%EC%9B%94%EC%9D%98-%EC%8B%A0%EA%B0%84.pdf).

### Database result
- Live read-only exact/alias/source scan before import: **0 matching rows** for ISBN `9791197931567`, record ID `KMO202332009`, title variants, creator name, and aliases.
- `go run ./cmd/catalog-import --manifest ../docs/korean-kim-young-ju-photography-booklet-2022-import.json` → `Validated 1 import records`.
- The same manifest with `--apply` → `Catalog records and price observations committed; listing image provenance records: 0`.
- Read-only snapshot: [DB read-back](../../docs/korean-kim-young-ju-photography-booklet-2022-db-readback.json). It confirms work `korea-kim-young-ju-photography-booklet-2022`, person `김영주`, physical edition, ISBN `9791197931567`, 133 pages, `30 cm`, NLK record URL, one credit, and **0 media assets**.
- No R2 upload: the open metadata license does not grant image rights, and no asset-specific cover license for storage/public delivery was found.

## 캔디 화보집 NO.1 꾸뿌 — unresolved

- Retailer records show the exact issue candidate and a serial-style number `9773059141000`, but its magazine-vs-standalone-photobook classification and commercial metadata authorization were not resolved. Retailer fields were not imported.
- One direct NLK LOD SPARQL query checked exact identifiers `9773059141000`, `30591414`, and `3059-1414`. It timed out after 20 seconds with no response body; no exact NLK record was confirmed. This result is inconclusive, not evidence that no catalog record exists.
- Leave Candy out of the catalog until an exact record and reusable source are available. Do not upload the cover without image-specific hosting/public-delivery rights.
## Verification addendum — 2026-10-30

- Exact NLK title-field query: `SELECT ?p ?o WHERE { <http://lod.nl.go.kr/resource/KMO202332009> ?p ?o . FILTER(?p IN (<http://purl.org/dc/terms/title>, <http://lod.nl.go.kr/ontology/remainderOfTitle>)) }`. It returned `dcterms:title = Kim Young Ju` and `remainderOfTitle = photography booklet`.
- Exact NLK work lookup: `SELECT ?s ?p ?o WHERE { ?s <http://purl.org/ontology/bibo/isbn> "9791197931567" . ?s ?p ?o . } LIMIT 25`; exact record `KMO202332009`.
- Import validation output: `Validated 1 import records`.
- Apply output: `Validated 1 import records` followed by `Catalog records and price observations committed; listing image provenance records: 0`.
- The stored read-back confirms release year `2022` at `year` precision, physical edition ID `korea-kim-young-ju-photography-booklet-2022-physical`, ISBN `9791197931567`, 133 pages, `30 cm`, one credit, and zero media assets.
- Candy query checked `9773059141000`, `30591414`, and `3059-1414` via the same public endpoint. `curl.exe -L -sS --max-time 20` returned `curl: (28) Operation timed out after 20008 milliseconds with 0 bytes received`; no result was obtained and nothing was imported for Candy.