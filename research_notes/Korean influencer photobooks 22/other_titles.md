# Other Korean Influencer Photobook Lead (Round 22)

## Does a new Korean influencer/model photobook qualify as a discovery lead?

### Takeaway
A strong new physical-book lead is Ran (란/らん), a Korean influencer and model, with KADOKAWA’s *蘭 らんファースト写真集* (2023). The exact publisher record and independent profile support the subject and product, but discovery evidence alone does not clear MuseBooks’ metadata-source gate.

### Cited Findings
- KADOKAWA’s product page identifies *蘭 らんファースト写真集*, release date 2023-03-29, B5 format, 112 pages, and ISBN 9784047374355. [KADOKAWA product record](https://www.kadokawa.co.jp/product/322301000031)
- A 2023 Pop’n’Roll release announcement describes Ran as Korea-born, an influencer and talent, and reports 2.3 million combined social followers at that time. It links the book to KADOKAWA and credits its photographs to Hiroe Yamauchi. [Pop’n’Roll, 29 March 2023](https://popnroll.tv/articles/31921)
- ORICON’s profile describes Ran as a Korean model/TikToker and popular influencer and reports 2.4 million combined social followers in December 2023. This independently supports Korean creator identity and influencer status at that date. [ORICON, 18 December 2023](https://www.oricon.co.jp/news/2306799/full/)
- The book is therefore a Japanese-published physical photobook by a Korean influencer/model, beyond the SOOP, Ayul, and Magarin leads already documented in rounds 19–21. [KADOKAWA product record](https://www.kadokawa.co.jp/product/322301000031); [Pop’n’Roll](https://popnroll.tv/articles/31921)

### Inferences
- This is a strong subject-and-format match for the user’s catalog goal. Ran’s book is published in Japan, but the creator is identified by the cited profile as Korean-born.
- Follower figures are historical values explicitly dated by their sources, not current counts.

### Gaps
- No reliable Korean-language alias beyond the Japanese/Korean forms `らん` / `란` was verified from the reviewed sources; retain the exact publisher title and the cited name forms rather than inventing a Korean legal name.

## Does the candidate have an authorized factual-metadata source and is it new in MuseBooks?

### Takeaway
The exact KADOKAWA bibliographic record is clear, but I found no explicit factual-metadata reuse grant for this commercial catalog. A scoped repeatable-read database query for the exact ISBN and title returned zero rows; this supports novelty only for the fields and variants checked.

### Cited Findings
- KADOKAWA’s public product page supplies the exact title, release date, format, page count, ISBN, and price, but the reviewed product page does not state a license for commercial third-party catalog reuse. [KADOKAWA product record](https://www.kadokawa.co.jp/product/322301000031)
- KADOKAWA’s copyright policy says unauthorized use of its publications and images is not accepted and directs users to separate inquiries for publication use. This does not itself grant MuseBooks commercial reuse rights for the product page’s facts. [KADOKAWA copyright policy](https://www.kadokawa.co.jp/copyrightpolicy/)
- KADOKAWA’s cover guidance provides limited no-application permission for libraries and school libraries using covers to introduce books, subject to conditions; it does not establish a metadata license for a commercial catalog. [KADOKAWA book-cover guidance](https://www.kadokawa.co.jp/support/b/library/)
- Exact-title/ISBN discovery searches on the public web did not surface a National Diet Library Search record for this book. That is an inconclusive search result, not proof that no record exists. The NDL website terms exclude third-party-created bibliographic data from the general NDL content license, so an NDL hit would need its record-level source/terms checked before relying on it. [NDL website terms](https://www.ndl.go.jp/en/sitepolicy/terms)
- A live MuseBooks duplicate check ran in a PostgreSQL repeatable-read transaction with `READ ONLY`. Search fields were edition ISBN `9784047374355`, work title containing `らんファースト写真集` or `蘭 らんファースト写真集`, English title containing `Ran First Photobook`, and slug containing `ran-first-photobook`; output: `Read-only exact-title/ISBN candidate rows: 0` and `[]`. This is a scoped duplicate check, not proof of absence under every possible title alias.

### Inferences
- Do not import the facts from the KADOKAWA storefront into the live catalog under the project’s present source-use rule until an applicable open metadata record or explicit reuse grant is identified.
- The `0` duplicate result clears the exact-identifier/name query only; it is not a rights determination and does not authorize import.

### Gaps
- No exact National Diet Library/Search record with terms that cover this candidate was identified in the scoped public search. Search-result absence is not conclusive.
- No explicit permission for commercial reuse of the title metadata from KADOKAWA was located. No database write was made.

## Is the exact cover licensed for R2 storage and public delivery?

### Takeaway
No. The publisher page shows the book’s cover, but no license for this exact cover image authorizes R2 storage and public delivery from MuseBooks. No cover was downloaded, copied, or uploaded.

### Cited Findings
- KADOKAWA’s cover-use guidance is scoped to libraries and school libraries and to book-introduction use; it directs other use purposes to an inquiry, says only covers downloadable from its product page may be used under that guidance, and prohibits cropping or compositing. It does not grant the commercial catalog/public-delivery use evaluated here. [KADOKAWA book-cover guidance](https://www.kadokawa.co.jp/support/b/library/)
- KADOKAWA’s general copyright policy disallows unauthorized use of its published images and directs publication-use requests to the relevant contact route. No title-specific permission or asset-specific license is shown on the reviewed Ran product page. [KADOKAWA copyright policy](https://www.kadokawa.co.jp/copyrightpolicy/); [KADOKAWA product record](https://www.kadokawa.co.jp/product/322301000031)
- The project’s source register treats an image URL as provenance rather than a reuse license and requires rights for the exact asset and intended public R2 delivery. [Project source-policy register](../../docs/korean-model-photobook-sources.md)

### Inferences
- Do not stage or upload the cover to R2. A future upload needs an explicit grant tied to the exact image and covering storage, public delivery, and any resizing or other transformation required by the catalog.

### Gaps
- No asset-level cover permission or license for public R2 distribution was found. No external party was contacted.
- No exact cover asset was downloaded or placed in a staging directory; image handling remains untouched.