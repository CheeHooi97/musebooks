# Goal: MuseCards model → MuseBooks photobooks

## Active goal: all Japan models (11 October 2026)

Read MuseCards without modifying its records. Export all model identities associated with Japan-origin releases, including native/English names, verified career aliases, and the relationship evidence. The preserved 11 October export contains 366 people; the refreshed 13 October export contains 370 people and 195 career-name records. This is Japan-market association; the person table does not establish nationality.

Use `scraper/japan-models/musecards-models.json` as the preserved input and `scraper/japan-models/queue.json` as the resumable queue. Store per-person captures under the MuseCards person ID. Reuse Fumina's completed capture and imported listings rather than recapturing or deleting them. Generalize physical and authorized digital collection to accept these model inputs, exhaust public pagination, and report source-specific completion, failures, and no-result searches.

Capture selling prices/currency/price basis, observed availability and time, publication and store-release dates with precision and provenance, covers, and additional public product/publisher images. Unknown values remain unknown. Preserve physical/digital identity, bundles, and different sellers. Exclude previews and unrelated or unofficial products. Import verified offers idempotently into MuseBooks, retaining source attribution and all media evidence. Verify homepage model-credit search, physical/digital filters, offer counts, dates and platform prices, then publish necessary fixes using reversible releases. Complete with per-model/source coverage and imported totals; do not equate completed accessible-source searches with a worldwide complete bibliography.

This goal authorizes the end-to-end collection, verified import, and homepage integration requested by the user. Earlier pilot statements about local-only capture describe the original pilot phase.

### Resuming name coverage

The publisher pass `scraper/run_japan_model_queue.py --source wani` gathers print bibliography separately from offers. Publisher ISBNs and publication dates support conservative physical associations; conflicting ISBNs and multi-book bundles remain unmatched. Publisher list prices do not replace recorded asking prices or auction bids. Public publisher image URLs are retained with their product-page provenance, and visual verification remains a separate requirement.

Generated manifests also retain `publisherMedia` separately from seller `media`. The importer stores publisher assets against the reviewed edition and rejects assets whose source page differs from the edition metadata source. Physical/digital offer observations and seller gallery attribution remain separate.

Digital product release dates are recorded as `storeReleaseDate`; they do not establish the original publication date. The homepage and book detail page label these dates as “Store release,” while physical edition dates use “Published.” Reports count unknown original publication and store-release dates separately. Keep this distinction when reviewing future source adapters and imports.

Physical marketplace pages sometimes return unrelated recommendation cards after a model query has no matching result. The collector retains those pages and stops that query after five consecutive pages without a title naming the selected model, using `query_relevance_exhausted`. Reports distinguish these relevance-limited searches from `public_search_exhausted`; they do not claim the remaining unrelated pagination was checked.

The deployed book API returns attributed edition and listing galleries. Book detail pages show these public images with links back to the publisher or listing source. `scraper/japan-models/gallery-verification.json` records the rendered live check; it verifies the selected page, not every captured image.

`frontend/scripts/verify-japan-homepage.mjs` checks every Japan-associated model against the frontend grouping/search function and both format filters. Run `npm run verify:japan-homepage` for saved imported manifests, or `npm run verify:japan-homepage-live` to fetch every public marketplace API page and confirm those imported offers remain searchable on the live site. The live run saves the page and offer totals in its verification file; these totals change with new imports and do not establish that source discovery found every photobook.

Digital queues compare the captured search names with the current database names before treating a terminal capture as complete. Earlier native-only captures remain incomplete until English names and verified career aliases have been searched. The collectors preserve existing offers, detail evidence and observation timestamps during backfills.

Run `scraper/run_japan_model_queue.py --source grajapa --pending-names-only` or the same command with `--source kobo` after the corresponding active queue finishes. Use `--wait-pid` with a freshly confirmed source-runner PID to serialize a backfill behind a live queue. Backfills for both running digital queues have been queued this way; they must not be launched concurrently with another collector for the same source.

The generated `scraper/japan-models/REPORT.md` and `coverage.json` show per-model source state, unsearched names, offer counts and unknown metadata. A completed name search does not resolve detail failures or establish a complete bibliography. Imports are checkpointed in `import-checkpoint.json`; `import-verification.json` records the cumulative database checks. The goal remains active while collection, metadata verification and identity review are unfinished.

## Expanded Fumina Suzuki scope

This section preserves the original Fumina pilot scope and capture layout. Its generalization to the Japan-model queue and import workflow is now part of the active goal above.

Preserve `scraper/fumina-suzuki-pilot/` unchanged. Save expanded results under
`scraper/fumina-suzuki-expanded/`, and verify the preserved file hashes.
Discover both physical and digital photobooks, including separate digital
editions of physical titles. Follow each accessible source's public photobook
pagination to its end, deduplicate offers by source and external ID, and retain
all distinct sellers and prices. Search results that cannot be verified remain
in the candidate evidence, rather than becoming confirmed photobook listings.
Collect authorized digital store offers alongside enabled physical marketplaces.
Report source-specific completion and access failures; completing one store
does not establish a complete worldwide bibliography. Keep original publication
dates separate from a store's later digital release date. The expanded Fumina
capture and its original pilot files remain preserved after the authorized
database import.

Current expanded capture entry points:

- `scraper/collect_model_physical.py --output scraper/fumina-suzuki-expanded`
  resumes enabled physical marketplaces from saved checkpoints.
- `scraper/collect_model_digital.py --output scraper/fumina-suzuki-expanded`
  follows Grajapa's observed photobook pagination controls.
- `scraper/collect_model_kobo.py` follows the observed Kobo author search and
  verifies all public product candidates, preserving rejected free previews.
- `scraper/summarize_model_expansion.py` verifies pilot hashes and rebuilds the
  separate JSON, CSV, and Markdown review from the capture checkpoints.

These Fumina-specific commands were the pilot entry points. The reusable model
collectors now accept a model file, and `run_japan_model_queue.py` drives the
Japan-wide queue; `import_japan_model_captures.py` applies reviewed manifests
with durable checkpoints.
The shared production worker's Japanese retail-source policy is unchanged.

Start with a read-only query of the MuseCards `gravure_model` database. Select a
public model from `people`, retain its person ID and verified names, and use
those names to discover related photobooks. Complete the pilot for **Fumina
Suzuki**, MuseCards person ID **6**, native name **鈴木ふみ奈**, before expanding
to other models.

For each verified photobook, collect its title, format, ISBN when available,
publisher, publication date and date precision, canonical cover image, and
other public product/gallery images. Attach every date and image to its source
URL. Use publisher metadata to distinguish physical and digital editions.
For each selling listing, collect platform, external listing ID, URL, observed
selling price, currency, price basis, availability, observation time, and the
listing's own images. Preserve asking prices, current auction bids, and sold
prices as distinct kinds. Do not estimate per-book bundle prices.

Keep `musecardsPersonId` as the cross-application identity; do not reuse it as a
MuseBooks primary key. Search the database's native and English names and
verified career aliases separately. Reject other people, trading cards, DVDs,
clippings, and unrelated photography books. Match offers to editions using
ISBN or corroborated model/title/format evidence; ambiguous matches remain
unlinked. Unknown dates and images stay null/empty with a reason.

Read public rendered marketplace pages through the existing browser worker.
Honor configured source enablement, navigation rate limits, and access gates.
Use public publisher bibliographic pages to verify books. Collect public
product assets only, preserving source attribution; no full-book downloads.
The pilot should save reviewable local JSON/CSV and an evidence report before
any database import or media upload.

## Acceptance criteria

- MuseCards model identity is read from the database, with provenance.
- At least one related book has a verified publication date and cover URL.
- Live selling offers retain platform, amount/currency, price basis, and time.
- Additional public product images are recorded when exposed by the selected
  product; unavailable galleries are reported instead of invented.
- Every offer-to-edition association includes match evidence and every asset
  includes its source page and role (cover, publisher sample, listing photo).
- Pilot output reports counts, missing fields, source failures, and the bounded
  scope of discovery; it makes no exhaustive-inventory claim.
- The later implementation can accept a MuseCards person ID to repeat the same
  workflow without hardcoding Fumina Suzuki.

## Pilot identity

Database: `gravure_model`; table: `people`; person ID: `6`.
Database snapshot: `scraper/fumina-suzuki-model.json`.
Native/canonical name: `鈴木ふみ奈`; English name: `Fumina Suzuki`.
The pilot does not modify the MuseCards profile or database.

## Completed pilot artifacts

- `scraper/fumina-suzuki-pilot/reviewed.json`: eight live selling offers,
  three reviewed publisher editions, publication-date provenance, listing
  images, and publisher asset results.
- `scraper/fumina-suzuki-pilot/reviewed.csv`: flat offer export.
- `scraper/fumina-suzuki-pilot/publisher-images/assets.json`: six downloaded
  publisher images with checksums and three unavailable assets.
- `scraper/fumina-suzuki-pilot/REPORT.md`: results, limits, and repeat workflow.

Later implementation should make the read-only database export reusable by
person ID, expand discovery through resumable source cursors and aliases,
verify the remaining book metadata, and integrate reviewed records with the
existing MuseBooks importer and media provenance tables. Keep canonical
publisher assets separate from seller listing photos.
