# Korean Influencer Digital Photobooks

## Verified candidate not previously cataloged

### Takeaway
RIDI’s *Secret B 9* is a well-supported digital photobook candidate featuring Korean model and influencer Yoon Na-gyeom (윤나겸). It has a direct retailer page with the PDF format, page count, release date, and current purchase price.

### Cited Findings
- RIDI lists **Secret B 9호-윤나겸**, published by MAXQ International, as an e-book released **2021-09-28**. Its file is a **42-page, 7.8 MB PDF**; the listed purchase price is **₩6,900** (rental ₩3,900). RIDI describes Secret B as MAXQ’s digital-only photobook series. — [RIDI product page](https://ridibooks.com/books/3563000107)
- Electronic Times’ article on the Fitthy project describes the four participants as models who are “모델이자 인플루언서, 배우 등을 하고 있는” and names **윤나겸** among them. — [ETNews article](https://www.etnews.com/20220916000275)
- Current-workspace duplicate screening on **2026-10-30**: the read-only Korean catalog query matching 윤나겸 in titles, featured names, or person credits returned **0 works**; an exact-term scan of `docs` and `scraper` also found no Yoon Na-gyeom / RIDI ID match.

### Inferences
- The exact title, person, PDF format, and digital-photobook series description make this a distinct eligible digital photobook, not a K-pop album photobook.
- Metadata can be considered for import. A retailer’s paid PDF access does not grant a license to copy its contents or cover into R2; no image reuse permission was found.

### Gaps
- No explicit cover-image or PDF-rehosting permission was located. Keep R2 media omitted unless the publisher or creator confirms reuse rights.

## Related same-creator edition and duplicate controls

### Takeaway
A second Yoon Na-gyeom title is listed as a digital compilation, but it may reuse Secret B imagery. Treat it as a separate lead requiring content-overlap review; do not import it yet. Secret B Vol.16 by Baek Seonghye surfaced during this research but has since been imported by the parent task and is excluded from new recommendations.

### Cited Findings
- RIDI lists **<시크릿 B+맥스큐> 합본호 Vol.02: 윤나겸** as a **65-page, 28.6 MB PDF**, e-book release **2022-06-02**, sale price **₩8,900** (rental ₩5,900). Its description calls it an online photobook combining selected and previously unreleased cuts from Secret B and MAXQ. — [RIDI product page](https://ridibooks.com/books/3563000137)
- The related title has its own RIDI product record and edition details, distinct in title and release from Vol.9. — [RIDI Secret B+MAXQ Vol.02](https://ridibooks.com/books/3563000137); [RIDI Secret B Vol.9](https://ridibooks.com/books/3563000107)
- The workspace now contains a Vol.16 import and DB readback, so it is already cataloged and should not be recommended again: [import manifest](../../docs/korean-secret-b-16-baek-seonghye-import.json), [DB readback](../../docs/korean-secret-b-16-baek-seonghye-db-readback.json).

### Inferences
- Since Vol.02 is a compilation featuring the same person and drawing from the Secret B/MAXQ photo sets, it could contain imagery also present in Vol.9. This overlap is not confirmed by the product listing; check before treating them as wholly distinct photographic content.
- Vol.16’s local readback appeared after my initial database query, illustrating why current manifest/DB state should be checked again immediately before import.

### Gaps
- RIDI’s Vol.02 page does not say whether it reuses any exact images from Vol.9. No edition-level overlap check or rights grant was found.
- The Vol.16 product is confirmed in the current repository; its earlier zero-match database result is stale and must not be used for deduplication.

## Verified and imported digital title

### Takeaway
*Secret B* Vol. 15 is a verified digital photobook featuring fitness model, trainer, and influencer Yang Yuna. MAXQ's official article announces the product, creator, and e-book release; Aladin's series record lists the exact Vol. 15 PDF and publisher.

### Cited Findings
- MAXQ's 2024-05-28 publisher article names Yang Yuna as the Secret B Vol. 15 solo model, describes her as a fitness model, trainer, and influencer, and announces the e-book/app release for 2024-05-31. — [MAXQ publisher article](https://maxq.kr/articles/chimyeongjeokine-seksi-beigeulnyeo-yangyuna-sikeuritbi-hwabojip-seongonggae)
- Aladin's Secret B series record lists **맥스큐 디지털화보집 Secret B Vol.15 양유나** as a MAXQ International PDF dated **2024-06**; this differs from the publisher's announced release date. It also shows a 6.36 MB file. — [Aladin Secret B series record](https://www.aladin.co.kr/m/mseriesitem.aspx?srid=927494)
- A Digital Times report mirrored on Daum identifies Yang as an Instagram influencer with 140,000 followers. — [Daum report](https://v.daum.net/v/X0woHRj4Ce)

### Database and rights status
- A live read-only duplicate check on 2026-10-30 found no matching work or person before import. The bibliographic record is now published as `korea-secret-b-15-yang-yuna-2024`, using the publisher-announced 2024-05-31 date and preserving the retailer's June 2024 date in the notes. Page count and ISBN remain unknown.
- Readback and audit: [manifest](../../docs/korean-secret-b-15-yang-yuna-import.json), [readback](../../docs/korean-secret-b-15-yang-yuna-db-readback.json), [verification](../../docs/korean-secret-b-15-yang-yuna-db-verification.json). The audit found one work, one digital edition, no listing/media references, and zero integrity findings.
- No cover or paid PDF was copied to R2; exact-image reuse permission was not found.
