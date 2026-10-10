# Japan later-page collection and scope review — 2026-10-10

The latest auction and Flea Market batches added 58 unique listings before
manual review. Eleven listings were then removed from public inventory:
seven non-book products/magazines and four requiring publication-age review.
Their original database observations remain preserved. Reviewed manifests and
`japan-reviewed-exclusions.json` record the decisions. The worker now rejects
these title patterns before image upload and import.

| Source | Listings | Active | Completed | Observations | Attributed images |
|---|---:|---:|---:|---:|---:|
| Rakuma | 32 | 31 | 1 | 32 | 32 |
| Yahoo Auctions | 120 | 89 | 31 | 121 | 120 |
| Yahoo Flea Market | 109 | 108 | 1 | 109 | 109 |
| Total | 261 | 228 | 33 | 262 | 261 |

This adds 47 qualifying unique listings to the previous 214-listing snapshot.
Every qualifying listing has matching R2 image attribution in the database.
Neither completed batch had unresolved image-upload failures.

All three source-local runners remain active: auctions resume page 4 offset 20,
Flea Market page 3 offset 40, and Rakuma page 7 offset 0. Rakuma's preceding
60-detail batch returned no qualifying products and advanced its cursor.
The previous production release fca99ff completed successfully. Broader query
coverage, further edition matching and collection remain unfinished.
