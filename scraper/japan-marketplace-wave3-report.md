# Japan expansion and reviewed edition matches — 2026-10-10

## Imported later-page batches

Wave 3 imports contain 26 reviewed auction observations, 20 Yahoo Flea Market
observations, and two Rakuma observations. Existing listing identities and
unchanged price observations are deduplicated by the database importer.

| Source | Unique qualifying listings | Active | Completed | Observations | Attributed images |
|---|---:|---:|---:|---:|---:|
| Yahoo Auctions | 69 | 66 | 3 | 70 | 69 |
| Yahoo Flea Market | 64 | 63 | 1 | 64 | 64 |
| Rakuma | 29 | 28 | 1 | 29 | 29 |
| Total | 162 | 157 | 5 | 163 | 162 |

Counts exclude out-of-scope products. Two Rakuma products subsequently identified
as a DVD and a magazine were marked excluded; their original observations remain
in the database. The reviewed manifests and `japan-reviewed-exclusions.json`
record those decisions. The classifier now also rejects disc-only and magazine
products before import.

## Reviewed edition links

- Rakuma `5b53076cb0ccb56fe2620973d9d33d32`: photographed barcode reads
  ISBN 9784087902075, matching the publisher's physical Enako Epilogue edition.
- Yahoo Flea `z701362702`: selected title and photographed cover match the same
  physical book. Its promotional-photo bonus remains described in the listing.
- Yahoo Auctions `o1237209176`: photographed cover, title, publisher, and
  photographer match Shiroma Miru LOVE RUSH, ISBN 9784087808674.

The production Epilogue API now exposes its active JPY 2,000 offer separately
from the completed JPY 1,600 listing. `catalog-match` requires exact current
listing titles, matching formats, and the edition's verified publisher URL. It
refuses to replace a different existing edition link. Price observations are
preserved.

## Continued coverage

The Yahoo Auctions completed-search batch is running. Yahoo Flea Market and
Rakuma continue through their exact saved cursors in source-local checkpointed
runners. Configured queries cover general photobooks, gravure, idols, actors,
actresses, and models. Exhausting those searches does not prove that every
photobook or every marketplace in Japan is covered.

`crawl_japan_marketplace.py` checkpoints after each import, verifies the database,
records unresolved image failures, and stops on nonadvancing cursors or errors.
Rerunning an existing state reuses the saved capture for the pending batch rather
than restarting completed search pages. Only one runner may collect each source
at a time, preserving the source's navigation rate limit.

```powershell
python scraper/crawl_japan_marketplace.py --source rakuma --state scraper/.tmp/japan-rakuma-crawl-state.json --resume-from scraper/japan-marketplace-wave3-rakuma.json --resume-query "グラビア 写真集"
go run -C backend ./cmd/japan-audit
```

For an older manifest without collection metadata, `--resume-query` is required.
New manifests retain their query, operation, and input cursor explicitly.
