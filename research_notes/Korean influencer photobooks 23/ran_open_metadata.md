# Ran’s NDL Metadata Source Check (Round 23)

## Does a public bibliographic record exist, and what facts does it provide?

### Takeaway

Yes. A manually rendered National Diet Library Search record exists for Ran’s 2023 physical photobook, with NDL Bibliographic ID 032712353 and the expected ISBN. The record’s bibliographic fields say 109 pages while KADOKAWA’s publisher listing says 112; keep this source conflict visible rather than silently choosing one count.

### Cited Findings

- The NDL Search record is titled `蘭 : らんファースト写真集`, record URL `https://ndlsearch.ndl.go.jp/books/R100000002-I032712353`, call number `Y94-M30789`, NDL Bibliographic ID `032712353`, book / paper format, photographer `[山内洋枝] [撮影]`, publisher KADOKAWA, publication month 2023.3, ISBN `978-4-04-737435-5`, quantity `109p`, and size `26cm`. Its subject is `らん ラン`. [NDL Search record](https://ndlsearch.ndl.go.jp/books/R100000002-I032712353)
- On that same record, the descriptive summary is explicitly attributed as `提供元: 出版情報登録センター（JPRO）` (provided by the Japan Publication Registry Office). [NDL Search record](https://ndlsearch.ndl.go.jp/books/R100000002-I032712353)
- KADOKAWA’s publisher record lists the same ISBN, release date 2023-03-29, B5 format and 112 pages, a different page-count value from the NDL catalog record. [KADOKAWA product record](https://www.kadokawa.co.jp/product/322301000031)
- A fresh MuseBooks duplicate check ran in PostgreSQL using a repeatable-read transaction with `READ ONLY`, matching ISBN `9784047374355`, Japanese title variants, English title `Ran First Photobook`, and slug `ran-first-photobook`. Exact stdout was `Read-only exact-title/ISBN candidate rows:` followed by `null`; the query returned no rows (the temporary Go check serialized its nil result slice as JSON `null`). No database write was made.

### Inferences

- The public record clears bibliographic discovery and corroborates the physical edition, but it does not make every value agree with the publisher listing. Preserve the NDL value of 109 pages only when explicitly sourced to NDL; do not present it as a settled count.
- The person-and-format match is independently documented in the round 22 research; this round was limited to source reuse clearance and the exact record.

### Gaps

- The rendered record does not provide a field-by-field provenance/license assignment for the core title and edition fields. The summary’s JPRO attribution is explicit, but it is not stated as the source of every other field.

## Do the record’s terms clearly allow commercial use of the factual metadata?

### Takeaway

Not conclusively for the full record. NDL’s website terms place eligible NDL-created content under Japan’s PDL 1.0, which permits commercial use with attribution, but those same terms carve out third-party-created bibliographic metadata. Since the displayed entry mixes NDL catalog data with a JPRO-attributed description and does not show per-field provenance, this check cannot verify that every metadata field intended for MuseBooks is in the licensed portion.

### Cited Findings

- NDL’s terms say website information, including bibliographic data, is generally available under PDL 1.0 except where other rules apply. They specifically identify third-party-created book bibliographic metadata, including metadata in NDL Search, as third-party content outside that general grant. [NDL Terms of Use](https://www.ndl.go.jp/en/sitepolicy/terms)
- Japan’s PDL 1.0 allows covered content to be copied, transmitted, modified, and used commercially when the source is cited; it also places responsibility on users for third-party rights and excluded content. [Digital Agency, PDL 1.0](https://www.digital.go.jp/en/resources/open_data/public_data_license_v1.0)
- JPO’s public Books catalog terms state that use is limited to non-commercial purposes and prohibit reproducing, repurposing, or selling its provided information or images without the right holder’s permission. These terms do not themselves govern the NDL page, but they do not offer an alternative commercial reuse route for JPRO/Books content. [Books catalog terms](https://www.books.or.jp/books-terms)
- The project source-use register says public accessibility alone does not approve reuse and calls for checking each source’s applicable terms; it separately treats image permission as asset-specific. [Project source-use register](../../docs/korean-model-photobook-sources.md)

### Inferences

- Do not treat the NDL page as a blanket commercial metadata grant. A future import can use this route only after the metadata fields to be reused are shown to be NDL-created and covered by PDL 1.0, or another applicable permission is documented. This round did not make that attribution determination.
- The record is useful as a public factual cross-check, but it does not establish that the JPRO-provided summary is available for commercial reuse.

### Gaps

- No record-level source breakdown or separate JPRO commercial reuse permission for the summary was identified. No request was sent.

## Does the NDL cover image have rights for R2 storage and public delivery?

### Takeaway

No permission for the exact image was established. The NDL page displays a cover image and warns that covers may differ by holding institution; the NDL terms also identify JPRO-provided book images as third-party content outside PDL 1.0.

### Cited Findings

- The NDL record labels the image `書影` and says `表紙は所蔵館によって異なることがあります` (the cover may differ by holding library). [NDL Search record](https://ndlsearch.ndl.go.jp/books/R100000002-I032712353)
- NDL’s terms list book images provided by JPRO as an example of third-party content and require users to check the provider’s rules and obtain consent if necessary. [NDL Terms of Use](https://www.ndl.go.jp/en/sitepolicy/terms)
- The project source-use register requires permission evidence for the exact asset and intended public R2 delivery; an image’s presence or URL is provenance, not a reuse license. [Project source-use register](../../docs/korean-model-photobook-sources.md)

### Inferences

- Do not copy or upload this NDL cover to R2. No exact-asset license, storage permission, or public-delivery permission was found.

### Gaps

- The exact cover asset’s rights holder and any permission covering storage, resizing, and public delivery remain undocumented. No image was downloaded, staged, or uploaded; no external party was contacted.
