# Fumina Suzuki duplicate repair — 2026-10-11

The work identity in `scraper/prepare_model_home_import.py` used each digital store's external product ID. Kobo and Grajapa therefore created different publication works for the same title. Store titles also vary in whitespace, punctuation, model-name prefixes, and series suffixes.

Applied 24 explicitly reviewed work groups in one database transaction using `backend/cmd/fumina-work-repair`. Editions retain their IDs, source URLs, labels, dates, ISBNs, covers, and store offers. Duplicate work records are retained with `superseded` status. No listings or price observations were removed. Copies of source editions remain separate to preserve store bonuses, release differences, and provenance.

The importer now uses `scraper/fumina-suzuki-work-identities.json` to reuse the reviewed canonical work for these captured products. Other titles retain their existing identity behavior. Different volumes, side A/B, compilations, and ambiguous `【オールアザー版】鈴木ふみ奈写真集` products were not inferred to be identical. Broader catalog matching is outside this repair.

Database verification: 89 original Fumina work records became 65 published works; all 89 editions and 142 linked offers retained exactly the same metadata and offers. Before/after JSON snapshots are saved beside this report. The screenshot pairs 足の先からずっと, 鼓動, and GLAMOROUS BODY each resolve to a single work with two source editions.

Validation:

- Python regression tests cover every mapped digital record, stable edition IDs, and separation of unreviewed volumes and ambiguous titles; passed.
- `go test ./cmd/fumina-work-repair ./cmd/catalog-import`; passed.
- `go run ./cmd/catalog-import -verify`; public catalog pagination and format checks passed.
- A second repair dry run passed after application.

The database was corrected directly; the application server did not need restarting. The importer source fix is in the MuseBooks project. Old pre-repair manifests can fail the existing edition/work conflict check; regenerate them with the updated importer before reimporting.
