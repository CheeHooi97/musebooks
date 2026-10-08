# Model and publisher photobook discovery

Implemented 8 October 2026 against MuseCards' persisted person/company patterns, preserving the existing MuseBooks work/edition/listing schema.

- `/models/:id` and `/publishers/:id` are shareable profile pages using existing directory slugs. They show paginated photobooks and links to active and sold ledgers.
- `GET /v1/models/:id` and `GET /v1/publishers/:id` return public profile metadata and distinct work/edition counts. They expose selected public fields only, rather than serializing company configuration.
- Existing `/:id/books` endpoints accept `q`, `format`, `language`, `year`, and `model`, plus pagination. The model filter accepts a canonical slug or a public-name substring. All edition filters apply to the same edition; publisher results retain only that publisher's matching editions. An existing profile with no filtered matches returns HTTP 200 and an empty page; an unknown profile returns 404.
- Book responses add `models` with public IDs/names and editions add `publisherProfile`. Existing fields and identities remain compatible. Credits are linked only for the featured role.
- Book details compare prices by source/platform for the selected edition. Retail, active marketplace, completed physical sales, and previous offers are separated. Offers retain individual listing IDs, conditions, recorded dates, shipping information, native amounts/currencies, and purchase URLs. Missing prices are explicit; raw amounts across currencies are not ranked. Edition selections are retained in the `edition` query parameter.
- Website builds generate static profile entries and metadata from the paginated model/publisher directory APIs, along with existing book pages and the sitemap. Deployment must update both API and frontend; no database migration is required for these read capabilities.

The UI extends the existing warm paper palette, Gloock headings, and Hanken Grotesk body typography, using cover-led catalogs and tabular price numerals. New labels support English, Japanese, Simplified Chinese, and Traditional Chinese. Mobile web uses responsive layouts; Capacitor bundles the same screens.

Validation covers Go tests, isolated PostgreSQL relationship/filter tests, frontend price-policy tests, and desktop/mobile browser flows with explicit QA fixtures. No QA catalog records are imported. Live read-only API checks verify profile links and empty filtered results against existing records.

Account synchronization, catalog profile/alias editing, protected administration, full price-observation history views, and native device verification remain later specification work. Existing guest collection behavior is preserved.
