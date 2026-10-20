# Kingstone warning-cover repair — 8 October 2026

The physical paperback **TAKA：深夜名堂男子寫真**, ISBN **9786264681902**, had imported Kingstone's generic `https://cdn.kingstone.com.tw/images/restricted.jpg` social-preview image. Its stored mirror showed a lock and 18+ restriction notice instead of a product cover.

The current database audit found one edition still referencing that warning image. Previously repaired BOOKWALKER masks were absent. The matching [TAAZE physical-book page](https://ebook.taaze.tw/do/mobile/single.aspx?org_flg=1&pid=11101098560&prod_cat_id=11) publishes the same ISBN, publisher, and release date, with its actual product cover in image metadata. That image was visually inspected, uploaded to the existing R2 namespace, and verified through the public image host with HTTP 200 and matching SHA-256. Printed rating labels on the genuine product image are retained.

A reviewed, optimistic, transactional correction updated the edition's cover URL, original image URL, and object key, plus matching work, listing, and catalog-media image references. Work/edition identity, listings, prices, and other metadata were preserved. The public MuseBooks API now returns the replacement for both work and edition. A post-repair audit found no remaining known Kingstone restriction images or BOOKWALKER mask originals in the catalog.

[Repair manifest](kingstone-cover-repair.json) records the exact identities, ISBN, old/new image URLs and storage keys, source page, bytes, and content hash. The canonical Taiwan bibliography/export is updated; historical research records remain provenance rather than replacement instructions.

Prevention now covers worker image selection, importer cache validation, image downloads by content hash, backend import validation, ingestion image sanitization, and public API cover responses. Generic warning assets and the known stored mirror are rejected; genuine photobook covers with printed 18+ text remain valid. An unavailable actual cover retains the book metadata with no cover rather than substituting a warning asset.

Validated with `go test ./...`, 30 Python cover/import/worker tests, exact-edition dry run and apply, live API readback, and public image SHA-256 verification. No frontend deployment is needed for the repaired data. The additional backend/worker prevention code is a local change until deployed.

The live mobile catalog was also checked in a browser and renders the actual replacement cover. That check exposed a separate existing static-route issue: the server redirects book directories to a trailing slash, while the frontend treated that slash as part of the slug. A local route-normalization fix and regression test now preserve book identity with either URL form; the local detail page was verified against the repaired catalog data. This frontend fix also awaits deployment.

Reviewed cover-only repairs can be validated using `go run ./cmd/cover-repair -manifest ../scraper/kingstone-cover-repair.json` from `backend/`; append `-apply` to apply. The command is limited to the MuseBooks database, requires known warning-image old URLs, and verifies edition/work identity and unchanged old or already-repaired URLs.
