# Japan scraper resume and grouping repair — 13 October 2026

The read-only `gravure_model` export now contains 370 Japan-market-associated
people, four more than the preserved 11 October snapshot. Queue preparation
retains capture state, updates verified names and career aliases, and preserves
Fumina's original captures.

The runner checks individual physical queries and digital name/detail coverage
before skipping a model. Failed queries remain resumable; physical searches
with unresolved failures report `incomplete`. Source file locks prevent two
queues from overwriting the same checkpoints. Repeated source failures stop
the queue with evidence retained. Successful/rejected detail pages clear stale
timeout errors, and recovered source errors are retained as history.

Exact model/title/publisher groups retain stable publication IDs, all source
editions, offers, prices, observations and attributed images. Before an import,
the workflow reads actual database ownership so partly imported groups retain
an existing work. Collaborative publications share their reviewed identity
across every featured model, including models with only one store capture.
The database repair preserves model credits and validates all editions in its
reviewed scope. Ambiguous titles, title qualifiers and volumes remain distinct.

This run committed batches of 264, 102 and 1,116 new or changed model-offer
records. The latest cumulative read-only check passed all 4,014 checkpointed
records with zero
price, format, gallery, publisher-media, work-link or exclusion mismatches.
These are model-offer associations; shared offers can occur under several
models. Fumina's previously imported capture is retained separately.

Live verification passed model search and both format filters for all 370
models against 5,146 distinct Japan offers across 103 API pages, with zero
catalog work identity issues. Verified career-name expansion also finds
unmatched offers under earlier names, such as 山岸逢花 when searching for
山岸あや花, without assigning an unverified publication identity.

The complete website build rendered 2,611 book pages and 3,357 sitemap URLs.
Release `japan-model-search-20261013T024924Z` is active; previous releases are
retained for rollback. The deployed `index-DubXaEc6.js` SHA-256 matches the
tested local build:
`b2f30e36e0acbc65ef91b3bc76d145c6aa073b3071756a6aff07dc577e2f2eb3`.

Collection is still running for physical marketplaces, Grajapa and Kobo.
The Wani queue completed the 369 non-Fumina model searches, including a
successful retry for the final new model; Fumina remains a preserved reuse
case. Source completion does not establish a complete worldwide bibliography.
`scraper/japan-models/REPORT.md` and `coverage.json` distinguish captured,
imported, pending, relevance-limited and failed work.

Evidence: `japan-model-pipeline-20261013.txt`,
`japan-model-pipeline-20261013-collaboration.txt`,
`../scraper/japan-models/import-verification.json`, and
`../scraper/japan-models/homepage-models-verification.json`.

The user explicitly authorized automatic imports on 13 October. The background
watcher is running as PID 59960, checking every five minutes while the attached
confirmed source and serialized retry queues run. Each batch reconciles exact
publication identities, imports changed captures, and verifies database readback.
The watcher performs a final import after the queues exit and stops after three
consecutive import failures, retaining captures and logs for recovery.
The initial batch passed its local audit (5,613 associations, zero conflicts)
but lost database access when this computer's public IP changed. Its import
transaction failed and its checkpoint did not advance. The watcher was paused
for diagnosis and resumed using strict SSH host-key verification and localhost
port 4187 forwarding to the server's existing PostgreSQL listener. Only child
import processes receive the temporary host/port override; TLS mode, credentials,
server configuration and access rules remain unchanged. The watcher owns the
tunnel and closes it on normal exit. Current logs are
`../scraper/japan-models/automatic-imports-ssh-20261013.log` and its `-errors.log`.
Six focused audit, SSH failure-path and atomic checkpoint tests passed, as did
the importer and HTTP handler Go tests.

### Automatic publication of new detail routes

The production route check found that API-imported books without generated HTML
returned HTTP 404. The new publication step runs only after cumulative database
verification, stages all changed pages before writing, and keeps rollback backups
outside the public release. It reuses the existing SEO/body renderer and deployed
assets, updates the sitemap, and creates missing linked model/publisher profiles.
Unknown book URLs still return HTTP 404; no Nginx or service configuration changed.

The verified production origin is 157.245.200.202: its certificate identifies
`musebooks.my`, and its deployed JavaScript SHA-256 matches the local tested build.
Automatic review initially rejected the helper upload as an unverified destination;
these read-only identity checks satisfied review, and the helper was installed in
the private `/opt/musebooks/japan-import-pages` directory. Its package contains no
credentials, private keys or database exports. Twelve Node tests and six Python
publication/validation tests passed, including staging failure, rollback, metadata
escaping, repeatability, unsafe paths and rejecting unverified publication scope.

The first page update generated 4,717 pages, creating 1,600 missing book/profile
routes. Backups are retained at
`/var/www/musebooks/releases/.book-page-backups/ec171d4c-861f-4d0b-8075-cd50bcc2cf67`.
The previously missing live book
`/books/work-jp-1ab64ffcddf09ff6b76afcbe` now returns HTTP 200; a real Chromium check
verified its title, imported edition and exact 990 JPY source price, with no page
errors. The public JavaScript bundle is unchanged. Evidence:
`../scraper/japan-models/new-import-book-route-verification.json`.

Watcher PID 12920 runs with `--publish-pages`; current logs are
`../scraper/japan-models/automatic-imports-pages-20261013.log` and `-errors.log`.
Its first automatic cycle verified 6,009/6,009 database records and published
60 changed pages, including 52 new routes. Publication failures retain their
refresh scope for the next cycle, even if database import was already committed.
The later 40-record database failure was caused by an external PostgreSQL restart
at 09:26 UTC; its transaction rolled back, and the recurring importer subsequently
recovered without advancing a failed checkpoint. Source queues continued running
through the watcher upgrade.

The physical child for model 72 (本庄鈴) later exited with Windows code
4294967295 while its checkpoint was still running. Its accepted offer and one
failed detail were retained. After confirming that the producer was terminal
and the active physical child had moved to model 78, the inactive checkpoint
was backed up and marked interrupted. The serialized physical retry will select
it. Queue outcomes now retain the capture phase and hash, report interrupted
children accurately, and count nonzero exits toward the consecutive failure
limit even when partial captures exist. Resumed physical collectors record a
fresh start timestamp, preventing stale failure records from describing a new
attempt. Sixteen focused outcome, retry and queue tests passed. The running
parent's already-loaded code remains unchanged; updated outcome handling applies
to newly launched queues.

The resumed Grajapa main pass reached the final model and exited normally, with
365/369 non-Fumina captures complete and four browser-interrupted/detail-failure
captures remaining. After confirming no Grajapa producer was active, a bounded
four-model retry ran as PID 9920 and recovered models 2345, 2347, 2349 and 2350.
Each finished `public_search_exhausted` with exit code zero. The importer watcher
was refreshed between transactions as PID 59960 to attach the retry and current
live source queues; current logs are `automatic-imports-final-retry-20261013.log`
and its errors file. Physical and Kobo work remain ongoing; the source-completion
snapshot does not establish a worldwide complete bibliography.
The disconnected first import left PostgreSQL session 845110 idle with an open
transaction, blocking the resumed batch. A bounded helper verified that session's
database, user, exact start minute and blocking relationship before terminating
only that abandoned session; PostgreSQL rolled its uncommitted work back. The
local importer now sets a transaction-local 120-second idle timeout to release
locks automatically after a future lost connection. No server-wide setting changes.
The updated importer is `.tmp/japan-catalog-import-v2.exe`; subsequent watcher
batches use it by default. The active batch keeps its original executable.

The first SSH-backed automatic batch committed 1,688 new or changed records on
13 October at 08:53 UTC. Its durable checkpoint contains 5,702 non-Fumina
associations; including the 150 preserved Fumina offers, 5,852 associations are
imported. Read-only database verification passed all 5,702 records, with zero
price, format, listing-gallery, publisher-media, work-link or exclusion mismatches.
The post-commit live check at 08:55 UTC passed all 370 model searches and both
format filters across 6,819 distinct Japan offers and 137 API pages, with no
duplicate API rows, identity errors or split-publication cards. All six reviewed
physical/digital publication pairs passed. Collection remains ongoing; this
verification establishes the imported snapshot, not completion of every model's
source searches.

Subsequent automatic batches committed another 139 and 26 records; cumulative
database readback passed 5,867/5,867 records with zero mismatches. The recurring
workflow is using the updated importer with its transaction-local idle timeout.

A physical detail-coverage audit found one qualifying but uncaptured Yahoo Flea
Market detail in model 20 (原つむぎ), whose capture had been marked finished.
The collector now persists `pendingDetails`, retries them through the normal
public listing-detail operation, and keeps their search runs in `detail_failures`
until resolved. Successful or verified rejected details restore the original
pagination status; failed searches remain failed. Legacy recovery uses retained
matching candidate evidence, not generic error counts or unrelated cards.
The inactive model-20 checkpoint was backed up and migrated to incomplete with
one pending detail, preserving all 13 offers and all cached details. Its pending
run also remains visible to the already-running serialized retry queue. Fifteen
regression tests passed, including the collector's real checkpoint/retry flow
with network calls mocked. Reports expose pending product details separately.

The continuation audit found 13 early Kobo captures that had searched author
names outside the photobook genre. Category-aware completion now reports their
26 outstanding native/English name searches. A serialized backfill waits on
the confirmed running Kobo queue, rather than starting a second collector for
the same source.

Publisher pagination now persists unvisited URLs per name. A failed later
page cannot be mistaken for a completed query after a restart. The final new
model's publisher search was replayed with the new checkpoint format and
finished successfully.

Yahoo's observed empty-result message,
`条件に一致する商品は見つかりませんでした`, was missing from the parser.
The same public query changed from a render failure to one loaded page with
zero candidates and no further pages. Model 27's single failed query was
retried through the normal collector and its physical capture is now finished.
Loading shells and missing-page errors remain failures; access gates are
rejected before empty-result classification. Future render failures retain
their public page evidence. Physical collection retains each platform's
navigation clock across page-sized jobs.

The preserved Fumina capture had copied 82 digital store dates into the
original-publication field. Derived reports now keep them as store release
dates and mark the original dates unknown. The original capture hash and its
database import projection remain unchanged. Independently sourced publisher
dates remain separate, and digital edition release dates use the store date.

Read-only retry passes are queued behind the confirmed Grajapa and physical
queue handles to recover remaining failed searches/details after the current
passes finish. These collectors do not import database records.

The local quality audit checks paid prices, JPY currency, digital authorization,
covers, catalog/media ownership and shared-offer consistency. The latest
fixed import snapshot has 4,014 model-offer records, 3,936 distinct offers and 529 proposed
cross-store groups, with no validation or identity conflicts. The reviewed
free-preview exclusion is counted separately. This snapshot remains local.

The rejection audit found magazine-branded standalone digital photo books
rejected as whole magazines: the collectors checked `magazine_or_supplement`
while many titles returned `magazine_only`. The corrected helper removes only
recognized brands from explicit standalone photo book titles and rechecks all
other exclusions. Whole magazines, supplements, junior gravure, illustrated
books, synthetic subjects and artist monographs remain excluded.

Saved Kobo product evidence recovered 27 model-offer associations without
browser requests or database writes. Original observation times, prices, store
dates and image attribution remain intact. `--offline` reuses saved evidence
without launching a browser; missing queries or uncaptured details stay
pending. A Kobo reassessment pass waits behind its confirmed category backfill.

The next import was frozen at `scraper/japan-models/review-batch-20261013T044000Z`:
1,116 pending model-offer records (1,115 new and one changed), representing
1,112 distinct offers. It includes 634 Kobo, 467 Grajapa, five Yahoo Auctions
and ten Yahoo Flea Market associations. The snapshot contains exact inputs,
record hashes, the preceding checkpoint, exclusions and a cumulative
verification manifest. All 4,014 local records passed the quality audit.

Read-only database validation accepted 396 existing publication groups and
deferred 153 groups until their offers arrive. The frozen importer dry run
accepted all 1,116 pending records. Automatic approval review accepted this
finite, hash-checked, one-time database update, which committed successfully.
Readback verified all 4,014 cumulative records with zero price, format, gallery,
publisher-media, work-ownership or exclusion mismatches. A second read-only
check confirmed all 529 publication groups, with zero deferred groups.
The recurring watcher was awaiting authorization at this snapshot; it is now
enabled following the user's explicit approval (see the current status above).

The post-import coverage snapshot contains 4,262 captured associations across
158 models: 370 physical and 3,892 digital. Including Fumina's preserved 150
offers, 4,164 associations are checkpointed and 98 newer associations remain
local. All seven main/serialized collector queue processes were confirmed live.
The refreshed website check passed all 370 models with zero paid metadata or
catalog identity issues across 5,146 distinct offers and 103 API pages.

The subsequent checkpoint audit confirmed completed coverage for 26 physical,
226 Grajapa, 209 Kobo and all 369 Wani model searches, excluding the preserved
Fumina reuse. Remaining source failures and name searches stay queued.
Historical Windows replacement failures were present on two digital states;
the existing digital retry logic remains in place through the shared atomic
checkpoint writer, now also used by publisher and queue-progress writes.
Sixteen checkpoint/resume tests passed, including preservation of the last
valid capture under a permanent file lock. Newly started physical model 36
and Grajapa model 1337 were confirmed saving checkpoints after this change.

The latest local report contains 4,304 captured associations and 140 pending
imports. Its 4,154 generated non-Fumina records passed the local quality audit
with zero conflicts; 530 groups are proposed locally, while the previously
imported 529-group batch remains the confirmed database scope.

Grajapa now also supports `--offline`, with the same evidence-only scope as
Kobo. Offline recovery resolved model 29's two stale detail errors, Grajapa
model 38's historical checkpoint-write error and Kobo model 24's historical
checkpoint-write error. Each model was confirmed inactive before recovery;
before-state backups and recovery logs are retained. All eleven existing
offers across these states remained exactly equal as parsed JSON,
and all three states now pass captured source completion. Uncaptured detail
failures on Grajapa model 1302 and Kobo model 1306 remain pending for online
retry. Offline processing preserves pagination stalls, and Grajapa keeps the
stalled page cursor instead of silently dropping it.

Six remaining exact physical/digital duplicates were reviewed against Wani's
ISBN metadata and Kobo's explicit paper/e-book selector. The evidence and
hashes are in `scraper/japan-cross-format-identities.json`. The identity builder
checks each reviewed edition's title, publisher, format, source URL and print
ISBN before including the pairing. Source editions and their release dates
remain separate. The frozen repair at
`scraper/japan-models/cross-format-fix-20261013T050757Z` changed six existing
Kobo records and merged six publication groups. It included no new captures.
All 4,014 cumulative imported records passed database readback; six old work
images were retained in their source-edition galleries.

The homepage previously added a format prefix to each catalog work key,
splitting a shared publication into separate paper and e-book cards. It now
uses the reviewed work identity for one card, with separate format summaries,
dates, prices and comparison panels. Unmatched titles retain format boundaries.
The cover grid now constrains its image track so covers cannot overlap text.
Ten import/identity tests, eight frontend grouping/price tests and sixteen
offline-recovery/completion tests passed.

The complete build rendered 3,628 photobook pages and 4,415 sitemap URLs.
Desktop/mobile rendering checks passed all six reviewed pairs, both format
filters and separate platform prices, with no runtime errors or overflow.
The distinct `ANOTHER EDITION` remained a separate publication. Release
`japan-model-search-20261013T065818Z` is active; the earlier release is retained.
The public website references the tested `index-B5Z7MHCC.js`, whose deployed
SHA-256 matches local:
`2d5488ff7279313197c84d3baf8821a0c46c0325500981190b47e3fc78917ee8`.
Post-deployment verification passed all 370 model searches against 5,146
distinct offers, with zero catalog identity or split-publication issues and
all six physical/digital groups passing. The temporary build-only SSH API
connection was closed after verification; no server/DNS settings changed.

The latest local snapshot has 5,168 captured associations: 5,018 generated
non-Fumina records and 150 preserved Fumina offers. The local quality audit
passed all 4,929 distinct generated offers with no conflicts, and proposes 658
groups. The confirmed database repair scope is 529 earlier digital groups plus
six reviewed physical/digital groups. There are 1,004 newer local associations
awaiting import at that snapshot; the newly authorized recurring database
watcher is now processing subsequent captures.

The original Grajapa queue and its serialized retry both stopped after repeated
navigation timeouts. Their terminal state was verified before a bounded normal
browser retry for model 1361, which completed with twelve offers. The remaining
Grajapa queue then resumed as PID 52584. Physical and Kobo queues remained live.
