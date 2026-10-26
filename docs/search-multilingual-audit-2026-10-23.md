# MuseBooks search and multilingual implementation review

Search Console follow-up: [verified ownership, successful sitemap processing and four live indexability tests](search-console-setup-2026-10-23.md). This supersedes the earlier Search Console access limitation recorded below.

Inspected 23 October 2026, Asia/Singapore. The website was deployed and verified live at approximately 21:25 SGT that day. Source changes remain in the local working tree; this was a direct website-only deployment.

## Live deployment verification

Release: `05eee9dc319a9bafb9a29dc78ad788e626bd8499-languages-1792761063`, under `/var/www/musebooks/releases/`. The API and database were unchanged. The previous release and Nginx configuration are retained for rollback in `/var/www/musebooks/deployment-backups/05eee9dc319a9bafb9a29dc78ad788e626bd8499-languages-1792761063`.

The real-data build includes 5,687 publications, 802 model profiles and 156 publishers. Its sitemap has 33,250 indexable URLs. The uploaded archive contained 66,822 files and matched local/server SHA-256 `7e783e4c526b92261c33cf53a5494b610db4da2ebed3a9461ae50c52fc394268`. Nginx configuration validation and origin smoke checks passed before completion.

Public HTTPS verification passed for 28 HTML pages: each language's home, books/models/publishers directory, and representative book/model/publisher detail page. Checks confirmed HTTP 200, document language, self-canonical, reciprocal hreflang, indexing permission, sitemap inclusion, and language-specific WebPage metadata. Additional checks passed for every language's slash redirect, direct Markdown, negotiated Markdown, and missing-page HTTP 404. `npm run check:geo -- https://musebooks.my` passed.

Browser verification confirmed visible translated headings, working Japanese/Traditional Chinese/Simplified Chinese/Korean language switching, loaded stylesheets, and no horizontal overflow at the tested desktop viewport. The English app's language links worked after reloading its pre-deployment cached page. Magazine language documents preserve separate cover-model credits, and model bibliographies include cover-only publications. All 34 regression tests passed.

Live pages: [Japanese](https://musebooks.my/jp), [Traditional Chinese](https://musebooks.my/tw), [Simplified Chinese](https://musebooks.my/cn), [Korean](https://musebooks.my/kr). [Detailed HTTP verification](language-live-verification-2026-10-23.json).

The earlier environment limitations below describe the initial inspection; live HTTPS access, browser rendering and Nginx validation were subsequently verified during deployment. Search Console property access and actual Google indexing of the new pages remain unverified.

## Findings and implementation

Compared MuseBooks with `D:/Workspace/Go/gravure-model` (MuseCards), particularly its public-web localization, language alternates, guide editions, sitemap generation, crawler policy, and Search Console audit scripts.

| Area | Inspection | Result in MuseBooks |
| --- | --- | --- |
| SEO: search engine optimization | Both projects expose catalog content as initial HTML, canonical URLs, crawlable links, sitemaps and publication metadata. | Retained existing rendering and source citations. Corrected magazine schema: unknown periodicals no longer become MAXIM, and profile lists identify magazine issues as PublicationIssue. |
| Multilingual search | MuseCards publishes separate `/jp`, `/tw`, `/cn`, `/kr` editions. MuseBooks only stored a language preference locally. | Added Japanese, Traditional Chinese, Simplified Chinese and Korean documents for the homepage, books/models/publishers directories, and each publication/model/publisher detail page. English stays at existing URLs. |
| Language discovery | A local preference does not expose distinct translated URLs to crawlers. | Added self-canonicals, reciprocal hreflang including en and x-default, correct HTML language, visible language links, localized internal links and sitemap entries. Browser metadata updates preserve language alternates during English SPA navigation. |
| AEO: answer engine optimization | MuseBooks already renders fact summaries, questions, edition facts, dated prices and source links in HTML and Markdown. | Preserved the English answers; translated editions expose bibliographic facts with translated labels and source links. They link to English price comparisons. |
| GEO: generative engine optimization | Both projects emphasize entities, source-backed claims and retrievable text. | Added translated WebPage language metadata while preserving each publication edition's recorded language; kept unknown facts unknown and removed unsupported periodical defaults. |
| AAO | Interpreted here as AI/agent access optimization; this abbreviation has no single agreed scope. MuseBooks already has Markdown twins, llms files, read-only OpenAPI, API catalog and Atom feed. | Added language discovery in llms files and localized Markdown twins; maintained original publication titles, dates, ISBNs and metadata sources. |
| Freshness | Full builds alone would leave newly imported publications without language siblings. | Incremental imports stage and publish English and translated HTML/Markdown together, update the sitemap, and roll back changed files on failure. |
| Serving | Existing Nginx already resolves generated documents and negotiates Markdown. | Extended slash normalization to language routes. Unknown routes still use existing 404 behavior. |

Language editions are complete static catalog documents. They deliberately do not load the English SPA, which would replace their text and metadata. Interactive filters, collection features, detailed market comparisons, About and privacy pages remain in the existing app. This is catalog language coverage, not a claim that every app feature or editorial text has been translated. Original titles, names and recorded facts are retained rather than machine-invented. Translation review by fluent speakers remains advisable.

Google recommends separate language URLs and reciprocal language annotations: [multilingual sites](https://developers.google.com/search/docs/specialty/international/managing-multi-regional-sites), [localized versions](https://developers.google.com/search/docs/specialty/international/localized-versions). Google says its AI search features use ordinary search eligibility and do not require special AI files or schema: [AI features](https://developers.google.com/search/docs/appearance/ai-features). Machine-readable companions help access, but are not a demonstrated ranking or citation boost. Schema must reflect visible facts: [structured-data guidelines](https://developers.google.com/search/docs/appearance/structured-data/sd-policies).

## Google Search Console observations

Read directly from the signed-in Search Console UI. These are first-party observations, not search-volume estimates or live ranking checks. No property settings, submissions or validation workflows were changed.

| Property | Web search performance | Page indexing | Interpretation |
| --- | --- | --- | --- |
| musecards.my | 127 clicks; 1.54K impressions; 8.2% CTR; average position 8.6. Selected range: 3 months; chart coverage shown: 3 September–21 October 2026. | Report last updated 16 October: 1,493 indexed, 3,325 not indexed. | Search Console explicitly reports a move to musecards.app. Do not transfer this domain's traffic or exclusions to MuseBooks. |
| musecards.app | 17 clicks; 161 impressions; 10.6% CTR; average position 11.2. Selected range: 3 months; chart coverage shown: 15–21 October 2026. | Report last updated 16 October: 5 indexed, 140 not indexed. | Migration and reporting lag prevent a conclusion that the current implementation caused these counts. |
| musebooks.my | Unavailable. | Domain-property request returned “you don't have access to this property”; MuseBooks was absent from the signed-in account's property list. | Need verified property access or an owner-provided export before evaluating MuseBooks clicks, queries, countries and indexing. No traffic numbers inferred. |

MuseCards old-domain exclusions: 1,498 noindex; 978 not found; 463 crawled, currently not indexed; 303 discovered, currently not indexed; 52 alternate canonical; 16 Google-selected different canonical; 10 server errors; 4 redirects; 1 unauthorized. The presence of these categories does not prove each is an error; intentional exclusions and migration redirects can be expected.

MuseCards new-domain exclusions: 61 noindex; 77 crawled, currently not indexed; 2 redirects. Its sitemap index was submitted and last read **22 October 2026**, reported **Success**, and discovered **6,215 pages**. That is newer than the indexing report, so 5 indexed versus 6,215 discovered must not be read as a current rejection rate.

Example queries observed: old property `juicy honey 31` (2 clicks/12 impressions) and `浜辺やよい` (1/2); new property `塩地美澄 トレカ` (0/5) and `壯壯卡` (0/1). These small samples establish that non-Latin queries occur for MuseCards, not demand estimates for MuseBooks photobooks. Average position is an aggregate Search Console metric, not an exact present-day organic rank. Query rows do not sum to property totals.

Reports: [old-domain performance](https://search.google.com/search-console/performance/search-analytics?resource_id=sc-domain%3Amusecards.my), [new-domain performance](https://search.google.com/search-console/performance/search-analytics?resource_id=sc-domain%3Amusecards.app), [new-domain indexing](https://search.google.com/search-console/index?resource_id=sc-domain%3Amusecards.app), [new-domain sitemaps](https://search.google.com/search-console/sitemaps?resource_id=sc-domain%3Amusecards.app).

## Validation and limits

- SEO tests cover reciprocal language annotations, canonical URLs, sitemap inclusion, native HTML language, translated Markdown, preserved bibliographic precision, recorded publication language versus document language, escaped hostile text, repeatable imports, rollback across language siblings and magazine schema.
- Production-mode Vite build and its actual SEO plugin completed using an in-memory synthetic catalog. This output is test-only in `frontend/dist-seo-review`; do not deploy it.
- Run tests on Windows with TEMP and TMP pointing to the repository's `.tmp` directory if the sandbox's package temp directory rejects atomic rename. No production atomic-write behavior was weakened.
- Live homepage/robots/sitemap requests failed with ENOTFOUND in this shell. Local browser preview timed out. These environment failures do not establish a public DNS outage; live rendering and visual layout remain unverified.
- Nginx is not available for `nginx -t` here. Deploy and check real localized URL responses, redirects, HTML and Markdown negotiation before judging production activation.

After deployment, run `npm run check:geo -- https://musebooks.my` from frontend. It now checks translated homepage and book documents as well as existing agent access. Obtain MuseBooks Search Console property access, submit its real sitemap if necessary, then inspect representative English and language URLs. Compare query, page and country data only after recording a baseline and respecting reporting delays. No ranking, rich-result or AI-citation gain is promised.
