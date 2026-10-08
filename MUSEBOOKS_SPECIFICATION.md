# MuseBooks — Product and Technical Specification

Date: 8 October 2026
Reference project: MuseCards, in `../gravure-model/`
Status: target specification; this document does not imply that every feature is implemented.

Implementation update: the frontend now builds with React/Vite and includes models, publishers, active listings, and sold listings. New directory and ledger APIs use the layered backend structure. Directories read persisted people/work_people and companies/editions relationships, backfilled from existing catalog credits. Curated profiles and alias management, account synchronization, and administration remain later work. Obsolete Next.js files and TypeScript application sources were removed. The summary below distinguishes delivered catalog features from remaining delivery items.

8 October implementation: canonical model and publisher profile read APIs and shareable pages now link to paginated photobook catalogs. Publisher/model catalogs support title, format, language, release-year, and featured-model filters; book responses include canonical model and publisher links. Photobook pages group exact-edition offers by platform, preserve separate offers and native currencies, and distinguish retail, active marketplace, confirmed sold, and previous offers. Static profile pages and sitemap entries are generated during website builds. Profile curation, arbitrary alias management, account collection synchronization, and protected catalog administration remain later delivery items.

## 1. Product direction

MuseBooks is a discovery, comparison, and collection platform for **digital and physical photobooks featuring models, influencers, idols, and celebrities**. This includes official publisher releases and verified independent releases by the featured person or their authorized representatives.

Use the same technology family, application boundaries, and backend structure as MuseCards/gravure-model, adapting the catalog domain from trading cards to photobooks.

Users should be able to discover a person’s photobooks, understand the available editions, compare relevant retailer and marketplace offers, and maintain a wishlist or personal collection.

The primary browsing structure is **Models → Photobooks** and **Publishers → Photobooks → Prices from different platforms**. Models and publishers are first-class catalog entities. Each publisher page lists its photobooks; each photobook page links its featured models and publishers and contains an edition-aware platform price comparison. The same photobook reached through either directory uses one canonical record.

Initial coverage includes Japan, Taiwan, China, and Malaysia, with additional markets supported by the same data model. Preserve original titles, names, scripts, and aliases.

## 2. Scope

### Included

- Physical photobooks: standard, hardcover, paperback, limited, publisher-issued signed, and other documented editions.
- Authorized digital photobooks, including releases sold as ebooks, PDF, EPUB, or storefront-only digital publications.
- Photobooks featuring one person, a group, or several credited people within the target categories.
- Verified self-published and agency/publisher releases.
- Edition metadata, permitted covers/previews, purchase links, availability, price observations, and source evidence.
- Collector wishlists and physical/digital ownership records.

“Ebook” is a delivery category. A verified model or celebrity photobook remains in scope when a retailer categorizes its digital edition as an ebook.

### Excluded from the initial product

- Generic scenic photography books, unrelated illustrated books, empty albums, and custom photo-printing services.
- Standalone trading cards, posters, magazines, or merchandise without an eligible photobook. Bundles containing a photobook must identify their contents.
- Unauthorized digital copies or unofficial digital-file resale offers.
- Hosting complete purchased books, a digital reader, checkout, fulfillment, or a user-to-user resale marketplace. The initial product links to external sources.

## 3. Technology alignment with MuseCards

The following baseline is based on the local gravure-model repository, rather than a claim about the latest upstream dependency versions.

| Layer | Shared target technology | MuseBooks responsibility |
| --- | --- | --- |
| Website | React + Vite, using JavaScript/JSX | Public photobook catalog, people pages, edition comparison, accounts, collections |
| Mobile | Capacitor for Android and iOS; Ionic React for native app UI where appropriate | Locally bundled app consuming the same Go API |
| Backend | Go + Echo | HTTP API, validation, domain rules, account and admin operations |
| Persistence | GORM + PostgreSQL | Canonical catalog, source records, listings, observations, collections |
| Media | Cloudflare R2 through an S3-compatible backend integration | Permitted covers and previews, stable storage references, backend URL resolution |
| Collection workers | Separate browser-worker processes submitting normalized results | Source discovery and listing observations through authenticated ingestion |
| Deployment | Independently deployed frontend, API, and workers | Dedicated MuseBooks configuration, database, media namespace, and domains |

Use the reference project’s applicable patterns and compatible dependency versions during implementation. Advertising, subscriptions, and payment SDKs are optional later features, rather than requirements merely because MuseCards includes them.

### Existing implementation and alignment work

MuseBooks began with a Next.js App Router + React + TypeScript website. Its active frontend is now React/Vite, with Capacitor projects inside `frontend/` and a Go/Echo/GORM/PostgreSQL backend. Browser workers currently live in `scraper/`.

The React/Vite migration is complete. Continue organizing pages, shared components, API clients, and mobile UI using the MuseCards pattern. Preserve catalog behavior, existing records, URLs or redirects, source attribution, and collection data in further changes. Verify routing, metadata, and API configuration against the active Vite implementation.

This specification describes the target product; editing it does not change the running application. `README.md` and deployed code describe current operation. Older statements in `plan.md`, including deferred mobile and generic photography coverage, should be reconciled with this specification during implementation.

## 4. Repository and backend structure

```text
musebooks/
  frontend/
    src/
      assets/
      components/
      lib/
      pages/
      mobile/
      main.jsx
    android/
    ios/
    scripts/
    capacitor.config.ts
    package.json
  backend/
    cmd/
    config/
    database/
    errcode/
    handler/
    middleware/
    model/
    repository/
    router/
    service/
    storage/
    transformer/
    utils/
    main.go
    go.mod
  deploy/
  docs/
  MUSEBOOKS_SPECIFICATION.md
```

Scraping remains a separate execution boundary. Existing `scraper/` and `scraper_worker/` code can remain during transition; workers must submit results through the API rather than modify canonical tables directly. Match MuseCards’ external-worker deployment pattern when extracting them into a dedicated worker project.

Follow the reference request flow:

```text
router -> handler -> service -> repository -> database
```

- **Router:** route declarations only; no database access.
- **Handler:** HTTP binding, validation, business rules, orchestration, and responses, matching the reference project’s convention.
- **Service:** thin boundary between handlers and repositories.
- **Repository:** queries and persistence operations.
- **Model:** persisted photobook domain structures.
- **Database:** connection setup, migrations, and bootstrap infrastructure.
- **Middleware:** authentication, authorization, and request controls.
- **Storage:** media storage integration and trusted media URL resolution.

Use a dedicated MuseBooks database and storage namespace. Share patterns and reusable code where appropriate without coupling MuseBooks records to the MuseCards database.

## 5. Photobook catalog model

### Models, publishers, photobooks, and platforms

Use MuseCards' persisted `Person`, `Company`, release/person associations, and marketplace/listing patterns as the reference. In MuseBooks, the public label **Model** maps to `Person`, **Publisher** maps to a `Company` acting as publisher, and **Photobook** maps to `Work` plus its `Edition` records. MuseCards' trading-card sets, designs, and variants are domain references rather than tables to copy into the photobook catalog.

Required relationships:

- A model can feature in many photobooks, and a photobook can feature many models through `WorkPerson` credits. Preserve credited names and roles; photographers and other contributors do not automatically become featured models.
- A publisher has many published editions. Each edition links to its canonical publisher through `publisherCompanyId`; the existing publisher text remains a display/provenance fallback during migration.
- A publisher's photobook list is the distinct set of works with an edition published by that company. Show its relevant editions under each book. A work with editions from different publishers may appear under each publisher without duplicating the work.
- An edition has many listings across platforms. Each listing identifies its platform/source and, where applicable, its seller. Each listing has timestamped price observations.
- A platform is a retailer or marketplace, not the publisher or publication country. A publisher's own store can also act as a platform, with those roles recorded separately. Preserve existing `Source` ingestion identities and reconcile them with `Marketplace` records rather than creating disconnected platform identities.

```text
Model (Person) <-> WorkPerson <-> Photobook (Work)
Publisher (Company) -> Edition -> Photobook (Work)
Photobook (Work) -> Edition -> Listing -> Price observation
Platform (Source / Marketplace) -> Listing
```

Unknown publishers remain explicitly unknown until evidence supports a match. Do not create a publisher from a seller name or assign a model exclusively to one publisher. Product lines are optional grouping metadata, not a prerequisite for publishing a photobook.

### Works, editions, and listings

Keep **work**, **edition**, and **listing** separate.

For example, a person’s photobook is one work. Its Japanese paperback and authorized digital release are separate editions. Two shops selling the paperback create separate listings for that edition.

| Entity | Purpose and principal fields |
| --- | --- |
| Person / Model | Stable identity, original and canonical public names, aliases, slug, verified roles: model, influencer, idol, celebrity; associated photobooks through work credits |
| Work | Original title, aliases, slug, description, publication origin, classification, verification status |
| Work credit | Work/person association and role, distinguishing featured people from photographers and other contributors |
| Edition | Work, physical/digital format, language, publisher, edition market, release date and precision, ISBN when present, page count, edition label |
| Digital edition details | Delivery format, platform, access requirements, known regional restrictions; unknown fields stay unknown |
| Company / Publisher | Stable identity, name, aliases, slug, official source links; published editions and a deduplicated photobook catalog |
| Source / Platform | Retailer/marketplace identity, region, permitted hosts, collection settings, source health; canonical marketplace association where available |
| Listing | Source and external ID, canonical URL, edition match, seller, condition, bonuses, bundle contents, availability, last observed time |
| Price observation | Listing, amount, currency, price type, timestamp, shipping/tax information when known, evidence |
| Source record | Retrieved URL, normalized input, content hash, parser version, provenance, matching outcome |
| Media | Cover/preview role, original URL, storage reference, source attribution, permitted usage |
| Collection entry | User, edition, wishlist/owned state, acquisition information and private notes |
| Scrape job/run | Source, operation, lease, heartbeat, attempts, progress, results, errors |
| Review/audit record | Ambiguous matches, metadata corrections, approvals, merges, actor history |

An individually signed used copy is normally a listing attribute. A documented publisher-issued signed edition can be a distinct edition. Alternate covers and bonuses become separate editions only when evidence identifies a distinct release.

Publication origin, language, person nationality, seller location, and marketplace region are separate facts. Digital editions may have no ISBN. Do not fabricate one or infer a physical counterpart.

## 6. Website and mobile experience

| Screen | Required behavior |
| --- | --- |
| Home | Recent releases, featured people, search, clear physical and digital entry points |
| Models directory | Search featured people by canonical names and aliases; open each model's photobooks and publisher links |
| Publishers directory | Search publishers; show distinct photobook counts and link to each publisher's catalog |
| Publisher detail | Canonical name, aliases, official links, and paginated photobooks published by this company; filter by featured model, format, language, and release year |
| Catalog | Search and filters for person, origin, format, language, release year, publisher, availability; shareable filter state and pagination |
| Work / Photobook detail | Original title, linked featured models and publishers, credits, cover, description, edition selector, source evidence, and prices from different platforms for the selected edition |
| Edition detail | Exact format and release details, digital platform information or physical specifications, relevant offers |
| Person detail | Names, aliases, verified roles, associated photobooks across both formats |
| Platform price comparison | Group offers by platform for the selected edition; show native prices/currencies, price type, seller, condition, bonuses, availability, source link, and last checked time |
| Price history | Dated observations with asking, auction, and confirmed sold prices distinguished |
| Collection/wishlist | Save editions, track owned format, remove records; private user data |
| Account | Registration, sign-in, sign-out, account/session management |
| Administration | Review candidates, verify people and formats, match listings, merge duplicates, inspect jobs and sources |

Use a cover-led catalog with legible titles, original-language metadata, visible format labels, keyboard access, and responsive layouts. Provide explicit loading, empty, error, and retry states. API failures must never substitute fabricated books or prices.

On a photobook page, changing the selected edition refreshes the platform comparison. Multiple sellers on one marketplace remain separate offers inside that platform group. Keep retail prices, active resale asking prices/auction bids, and confirmed sold history in clearly labeled sections. A missing price displays as unavailable, never zero. If no platform offers are recorded, retain the photobook metadata and show an explicit empty state. Any lowest-price summary must identify the comparable edition, currency, condition, and included costs; do not rank raw amounts across currencies.

The mobile build bundles its own application assets and calls the configured HTTPS API. Use platform-appropriate navigation, external purchase links, sharing, and deep links. Keep catalog meaning and edition identity consistent across website and mobile.

Local collection persistence can support guests. Account-backed collection synchronization is a separate feature that must be implemented before claiming cross-device sync.

## 7. API and ingestion contract

Keep public catalog endpoints and protected account/admin/worker operations under a versioned `/v1` API. The exact route names should follow existing contracts or be introduced with a migration plan.

Required API capabilities:

- Browse/search models, publishers, and photobooks; retrieve model/publisher profiles and their paginated photobook catalogs.
- Retrieve photobook, edition, listing, and price-observation details, including publisher/model identities and platform identifiers needed for linked navigation and price grouping.
- Resolve known catalog media references through the backend.
- Register/authenticate users and manage their private collection entries.
- Review, correct, approve, and merge catalog records with administrator authorization.
- Lease scrape jobs, accept heartbeats, ingest idempotent observation batches, and complete runs using worker authentication.

Workers discover source records; the backend validates, deduplicates, and decides canonical identity. Ambiguous observations remain unmatched or enter a review queue. A title match alone is insufficient to identify an edition.

Preserve the current `/v1/models`, `/v1/models/:id/books`, `/v1/publishers`, and `/v1/publishers/:id/books` contracts. Add profile and comparison capabilities compatibly. Publisher queries must deduplicate works while retaining the publisher's editions; model queries must use featured-person associations. Price responses must retain listing identity, source/platform identity, selected edition, native amount/currency, price type, availability, and observation time. Grouping must not discard individual seller offers or manufacture missing prices.

Use browser-rendered collection for the existing MuseBooks worker approach. Retain source URLs, retrieval timestamps, and parser versions so published facts can be traced to evidence.

## 8. Data quality and pricing rules

- Publish only works with evidence that the featured person and photobook content match the product scope.
- Verify authorized digital releases even when the storefront uses a broad ebook category.
- Separate fixed asking prices, current auction bids, and confirmed sold prices. A vanished listing is not a confirmed sale.
- Store exact decimal amounts or currency-aware minor units; preserve native currency.
- Treat shipping, taxes, regional availability, and access restrictions as unknown when unverified.
- Compare equivalent editions and disclose differences in condition, signature, bonuses, and bundles.
- Show observation timestamps and stale availability. Any currency conversion must disclose its rate timestamp.
- Preserve date precision, original scripts, aliases, provenance, and review status.
- Keep private collection responses out of shared public caches; enforce account and administrator access in the API.
- Store media credentials server-side and resolve only known media records.

## 9. Delivery sequence

1. Preserve the completed React/Vite and layered Go foundations while extending MuseCards-style model and publisher discovery.
2. Complete canonical model/publisher profiles and publisher-to-photobook relationships without losing the current work/edition/listing model or ingestion contracts.
3. Complete model and publisher photobook drill-down and photobook-level platform price comparison for exact physical/digital editions.
4. Complete protected account collections, administration, and source review workflows.
5. Validate separately bundled Android/iOS builds against the shared API.
6. Extend source coverage and price history after verification and matching are reliable.

Before migrations, record the existing data and API contracts, back up affected data, and verify that imported records retain their source links and identities.

## 10. Acceptance criteria

- A visitor finds a model, influencer, idol, or celebrity and sees their verified photobooks.
- A visitor opens a publisher and sees its photobooks, with each work listed once and that publisher's editions identified.
- The same photobook reached through a model or publisher opens the same canonical detail record, with links back to its models and publishers.
- A photobook shows prices from multiple recorded platforms for the selected edition, preserving separate seller offers and clearly labeling empty or unavailable prices.
- Switching between physical and digital editions updates platform offers without mixing incompatible editions or sold history with current asking prices.
- Physical and authorized digital editions are both discoverable and correctly labeled.
- Different formats and releases retain separate identities and relevant purchase links.
- A collector can save an exact edition and distinguish physical from digital ownership.
- Every public offer includes its source, price type, currency, and observation time where available.
- An administrator can review uncertain records without publishing guessed metadata.
- Repeated worker batches do not duplicate works, editions, listings, or observations.
- Website and native builds use the same catalog API and produce clear failure states when it is unavailable.
- Frontend builds and relevant backend/ingestion checks pass after implementation changes; catalog, collection, and mobile journeys receive direct verification.

## Local reference documents

- [MuseCards architecture](../gravure-model/README.md)
- [MuseCards frontend dependencies](../gravure-model/frontend/package.json)
- [MuseCards backend dependencies](../gravure-model/backend/go.mod)
- [MuseCards catalog identities and releases](../gravure-model/backend/model/catalog.go)
- [MuseCards release/person and company associations](../gravure-model/backend/model/catalog_support.go)
- [MuseCards model, publisher, and release pages](../gravure-model/frontend/src/pages/CatalogPages.jsx)
- [MuseBooks current implementation](README.md)
- [MuseBooks product boundaries](PRODUCT.md)
- [MuseBooks earlier implementation plan](plan.md)
- [MuseBooks deployment](DEPLOYMENT.md)


PostgreSQL and application structure follow MuseCards. See [catalog implementation](docs/catalog-implementation.md) for normalized tables, migration commands, shared connection settings, and ownership requirements. Active React/Vite code is under `frontend/src`; obsolete Next.js files and TypeScript application sources have been removed.
