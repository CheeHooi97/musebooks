# Korean Influencer Photobook Addition 5

## Added to the database

One new verified title is now in the catalog: *MAXQ Special Edition Vol. 8* (MAXQ Special Edition 8호), featuring Pilates and fitness creator Jo Aera (조애라). RIDI lists it as a 33-page PDF e-book published on April 25, 2023 by MAXQ International. The product description calls it an online photobook. A Wellness Insight interview names Jo's Instagram account and identifies her as the owner of Pilates studio Aera Infit; a later professional profile links the same account and documents her instructor and creator work. ([RIDI product](https://ridibooks.com/books/3563000166), [Wellness Insight interview](https://contents.premium.naver.com/wellness/wellnessinsight/contents/230413143753301gh), [Vanaro profile](https://www.vanaro.co.kr/home/?bmode=view&idx=169725418&q=YToyOntzOjEyOiJrZXl3b3JkX3R5cGUiO3M6MzoiYWxsIjtzOjQ6InBhZ2UiO2k6Mjt9&t=board))

The exact RIDI product ID, title/featured name, and creator person row were absent in a repeatable-read pre-import query. The database now contains one work, one digital edition, and one featured credit. It stores the source date and page count; ISBN is blank because RIDI lists none. No listing or price observation was added.

## Verification and R2 status

The read-only snapshot confirms the exact product URL, digital format, April 25, 2023 date, 33 pages, and Jo Aera featured credit. The scoped audit reports **zero integrity findings** and **zero people missing provenance**. Public-catalog verification exited 0 and returned **359 physical works and 5,088 digital works** at the time of the check.

No cover or paid file was copied to R2. RIDI's public product page proves the product identity, but it does not grant permission to reuse its exact cover image. Image overlap with Jo Aera's other MAXQ and Secret B material also remains unchecked.

## Files

- [Import manifest](../docs/korean-maxq-special-edition-vol08-jo-aera-2023-import.json)
- [Database snapshot](../docs/korean-maxq-special-edition-vol08-jo-aera-2023-db-readback.json)
- [Scoped audit](../docs/korean-maxq-special-edition-vol08-jo-aera-2023-db-verification.json)
- [Research notes](../research_notes/Korean%20influencer%20photobook%20additions%205/maxq_vol08_jo_aera.md)
