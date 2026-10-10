# Japan expansion — 2026-10-10

The second collection wave used the existing browser worker, six navigations per
minute per source, reviewed physical photobook scope, content-addressed R2 image
uploads, and the transactional catalog importer.

## Database readback after wave 2

| Source | Unique listings | Active | Completed | Stored observations | Attributed listing images |
|---|---:|---:|---:|---:|---:|
| Yahoo Auctions | 49 | 46 | 3 | 50 | 49 |
| Yahoo Flea Market | 44 | 43 | 1 | 44 | 44 |
| Rakuma | 27 | 26 | 1 | 27 | 27 |
| Total | 120 | 115 | 5 | 121 | 120 |

There are 90 additional unique listings compared with the initial 30. Reviewed
wave 2 manifests contain 34 auction, 35 flea-market, and 26 Rakuma observations;
overlapping listings and unchanged observations are not counted as new records.
All accepted listing images have matching original image and listing URLs in
`catalog_media`. R2 uploads verified both object existence and public image bytes.

Magazine-only products, supplements, synthetic subjects, download resales,
junior gravure, and a photographer monograph were excluded during review.
Bundles retain their whole-listing price. Active bids and fixed asking prices
remain distinct from completed-sale prices; shipping is not added to the price.

## Verified canonical editions

Three physical editions were independently verified using publisher pages,
uploaded to R2, imported, and exposed by the public catalog API:

- [Enako: Epilogue](https://www.shueisha.co.jp/books/items/contents.html?isbn=978-4-08-790207-5), ISBN 9784087902075.
- [Shiroma Miru: LOVE RUSH](https://www.shueisha.co.jp/books/items/contents.html?isbn=978-4-08-780867-4), ISBN 9784087808674.
- [Enako: cosplayer](https://books.shueisha.co.jp/items/contents.html?isbn=978-4-08-780861-2), ISBN 9784087808612.

Marketplace listings remain pending edition matching. Publisher verification
does not establish that a resale bundle or bonus variant equals a single edition.

## Remaining collection

This is not an exhaustive Japan catalog. More active results remain, and the
completed-auction search still needs expansion. Wave 3 continues auction page 2
and the stored flea-market and Rakuma cursors. Captures preserve `nextCursor`
and `hasMore`; collection must resume those cursors rather than infer completion.
Mercari remains excluded under the configured access policy.

The worker's full-page check now uses requested page size instead of the overall
candidate limit, preventing a large candidate budget from stopping numbered
pagination after the first page.

## Commands

Run from the repository root with Python 3.12 and configured `backend/.env`:

```powershell
python scraper/expand_japan_marketplace.py --source yahoo-auctions-jp --cursor 2 --output scraper/japan-marketplace-wave3-auctions.json
python scraper/review_japan_import.py scraper/japan-marketplace-wave3-auctions.json
go run -C backend ./cmd/catalog-import -manifest ../scraper/japan-marketplace-wave3-auctions.json -apply
go run -C backend ./cmd/japan-audit
```

`--capture` reuses a saved `.capture.json` for R2 upload retries without revisiting
marketplace pages. `--cursor` accepts the exact returned cursor, including JSON
cursors that contain a page URL and candidate offset.
