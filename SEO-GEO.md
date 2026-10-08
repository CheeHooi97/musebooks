# MuseBooks SEO and GEO inspection

Inspection date: 8 October 2026 (Asia/Singapore).

SEO means search engine optimization. GEO means generative engine optimization: making MuseBooks' records easy for AI search systems to retrieve, understand, and cite accurately.

## Implementation status

The repository now implements the technical and catalog-provenance fixes below. Production activation and account-based measurement still require deployment and access to the live services.

| Area | Implemented behavior | Remaining work |
| --- | --- | --- |
| HTML retrieval | Build emits book facts, all recorded editions, source-backed price observations, directory links, profile bibliographies, and listing text in the initial response | Verify deployed HTML and crawler access |
| Book loading | Generated book pages include safely serialized initial data; the browser refreshes only the requested book | Measure performance with the real catalog |
| Indexing | Loading preserves generated metadata; confirmed missing records get noindex; tracking and edition parameters remain indexable | Check live URL Inspection and HTTP responses |
| Missing URLs | Nginx serves generated routes and a real 404 response for unknown paths, with a noindex error page | Run nginx -t and production smoke tests; rebuild after removals |
| API crawling | Public catalog read paths are allowed; other /v1 paths stay disallowed | Verify deployed robots.txt and CDN rules |
| Canonical URLs | Build and browser normalize the configured site origin; Nginx removes trailing slashes; encoded URLs use decoded filesystem names | Verify redirects with real non-Latin slugs |
| Provenance | Book detail shows ISBN, date precision, dimensions, edition summary, and metadata source when recorded | Review underlying sources and identity aliases |
| Structured data | Work/edition relationships, verified edition fields, site organization, profile breadcrumbs and visible item lists | Validate deployed markup against real records |
| Methodology | /about explains scope, record types, source limits, price definitions, and corrections | Maintain editorial ownership information as available |
| Freshness and checks | Deployment runs SEO tests and accepts a catalog-updated repository dispatch | Trigger a rebuild after imports or removals; connect reporting accounts |

Validation: 10 Node tests passed. The complete production Vite build and its SEO plugin passed with an in-memory synthetic catalog. Playwright verified delayed book loading, tracking/edition indexing, record-specific requests, transient API failures, missing books/profiles, About, unknown routes, and desktop/mobile layouts. No browser page errors or horizontal overflow were found. The Browser plugin was not available, so the installed Playwright runtime was used. Nginx execution, production catalog builds, CDN access, Search Console, and AI citation measurements remain unverified.

The fixture catalog is test-only and must never be deployed. Production builds continue to require real API data and fail when requests fail. Static snapshots refresh on rebuild; a record removed from the API may retain its old generated HTTP 200 page until the next release, although the browser marks a confirmed missing record noindex.

## Original next actions

1. Publish useful book and directory content in the initial HTML, and resolve the API crawler-access conflict.
2. Make indexing directives stable during loading and return real HTTP errors for missing pages.
3. Expose edition metadata provenance and strengthen record identity before expanding into new search landing pages.

MuseBooks already has a useful foundation: separate works, editions, and listings; source links; original currencies; dated observations; and explicit distinctions between retail offers, asking prices, and confirmed completed sales. Preserve these distinctions throughout SEO and GEO work.

## Scope and limits

This is a repository inspection of the current working tree, including uncommitted changes. It covers React pages, metadata generation, static build behavior, Go response models, Nginx routing, and deployment configuration. It is not a production crawl or a measured ranking audit.

Live requests to the homepage, robots.txt, sitemap.xml, and a two-record catalog API sample failed with `No such host is known` from this environment. The web reader also could not access the homepage. These failures do not establish a global DNS outage. Check DNS and access from an independent network before treating availability as a production defect. The historical MuseCards routing warning in DEPLOYMENT.md is not evidence of current production behavior.

No Search Console, analytics reports, backlink data, keyword volumes, competitor rankings, or AI citation baseline were available. There are no traffic forecasts or ranking claims in this document. The requested Markdown deliverable takes precedence over the SEO skill's connected-provider and HTML reporting workflow.

Initial inspection verification covered three existing metadata tests. Subsequent implementation verification is recorded above; live production validation remains outstanding.

## Original findings and priorities

Priority describes implementation order, not proven traffic loss. Confidence is high for the source-code behavior described below; production impact remains unverified.

| Priority | Finding | Evidence | Recommended change |
| --- | --- | --- | --- |
| P1 | Generated pages contain metadata but no rendered catalog body | `frontend/index.html` has an empty root; `renderSeo()` changes the head only | Render book facts, editions, prices, and internal links at build time or on the server |
| P1 | Required catalog API is disallowed to compliant crawlers | `seo-build.mjs` emits `Disallow: /v1/`; `Home.jsx` fetches `/v1/books` and `/v1/origins` to display content | Remove crawler dependence on the API; meanwhile allow only public read paths needed for rendering |
| P1 | Valid book routes receive temporary `noindex` during loading | `pageSeo()` treats an unknown book route as missing; `SeoHead` runs before catalog loading finishes | Distinguish loading, confirmed missing, and temporary API failure |
| P1 | Missing URLs can return the homepage shell with HTTP 200 | Nginx uses `try_files $uri $uri/ /index.html` | Serve real 404 responses for unknown public routes; retain valid direct-link support |
| P2 | Profile errors do not update metadata or indexing state | `DirectoryProfile.jsx` mounts `SeoHead` only after a successful profile response | Handle confirmed profile 404s and temporary failures explicitly |
| P2 | Book structured data carries only basic work identity | `seo.js` includes name, alternateName, URL, optional description/image, and breadcrumbs | Add verified edition identity and relationships consistent with visible facts |
| P2 | Metadata source information is available but not shown in book detail | `EditionResponse` includes `metadataSourceUrl` and `contentSummary`; `BookDetail.jsx` does not render them | Show cited edition facts and relevant edition summaries |
| P2 | A detail page loads the entire catalog before resolving its book | `Home.jsx` loads every `/v1/books` page and searches the result by slug | Bootstrap the current record or fetch it directly; load unrelated catalog data separately |
| P2 | Build and browser origins can diverge under environment overrides | `SITE_URL` reads `import.meta.env`; the Node build script imports that module directly | Pass the canonical origin explicitly to the build and validate parity |
| P3 | Language preferences do not create separately addressable translations | `preferences.jsx` changes interface text and document language through browser storage | Add language URLs only when substantive translated pages can be maintained |

### 1. Make catalog content retrievable without JavaScript

`buildSeo()` creates files for books, models, publishers, and core pages. However, these are metadata-enriched application shells, not fully prerendered pages. A bot reading only the HTTP response sees no book facts or catalog links in the body.

Google can render JavaScript, but rendering is a separate step and some bots do not execute it. Its documentation recommends server rendering or prerendering where appropriate. [Google JavaScript SEO guidance](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics)

The generated robots.txt also blocks `/v1/`, which includes the requests needed to populate those shells. This is a concrete configuration conflict and a plausible rendering obstacle, not verified evidence that Google has excluded the site.

Implementation:

- Extend the static build to emit actual page content, or adopt server rendering for public catalog routes.
- Include the title, credited people, publisher, edition facts, source citations, observation dates, and links in the initial body.
- Keep interactive filters, collection saving, and live price refresh as progressive enhancements.
- If the shell remains temporarily, allow the public catalog GET paths required to render it. Keep scraper/control endpoints excluded and authenticated; robots.txt is not access control.
- Ensure CDN rules do not challenge legitimate search crawlers. Verify access using logs and provider guidance.

Acceptance: a request without JavaScript returns a book's facts and internal links; a directory returns real record links; URL Inspection shows complete content rather than an empty or error state.

### 2. Stabilize indexing and missing-page behavior

On a valid book URL, `selectedBook` initially has no value. `pageSeo('/books/...')` consequently returns a not-found title and `noindex: true`, and `SeoHead` writes them into the head. A later successful fetch reverses this. Rendering that ends during loading or API failure can encounter the wrong state.

Separately, `renderSeo()` always writes `index,follow` regardless of `seo.noindex`. The current build generates known routes, so this is an implementation inconsistency rather than proof of generated missing-book pages.

Implementation:

- Preserve correct generated metadata while loading a valid route.
- Apply `noindex` only after a confirmed missing record or an intentional indexing policy decision.
- Handle temporary upstream failures as temporary failures, not missing books. For server-rendered requests, use appropriate 5xx responses.
- Return HTTP 404 for genuinely unknown books, profiles, and paths instead of falling back to a 200 homepage shell.
- Make build-time and client-time robots rules share the same policy.
- Treat ordinary tracking parameters separately from search/filter parameters. `Home.jsx` currently noindexes every URL with any query string, including edition selection and campaign tracking.
- Define pagination policy separately from filters. Profiles rewrite URLs with `page=1` and allow unfiltered later pages, while all pages canonicalize to the base profile. Provide crawlable pagination if later pages contain distinct record links.

A canonical is the declared preferred URL for duplicate content. Use the clean work URL for edition UI selections when editions are not standalone pages. Do not accidentally noindex the canonical book just because a tracking parameter exists.

Acceptance: valid pages remain indexable under delayed API responses; missing pages return 404; error states never inherit a healthy profile's metadata; canonical and robots behavior is tested for clean, tracking, edition, filter, and pagination URLs.

### 3. Make facts and provenance easier to cite

The visible price comparison already includes source links, condition, original amounts, shipping context, status, and observation dates. That is useful evidence for both collectors and AI systems. Edition metadata has less visible provenance despite source fields existing in the API.

Implementation:

- Show `metadataSourceUrl` alongside edition facts, with a descriptive publisher or retailer link label.
- Display verified `contentSummary`, ISBN, full publication date, page count, language, and dimensions when available. Keep unknown values explicit; do not infer an ISBN or edition from a title match.
- Add an About and catalog methodology page covering ownership, regional scope, inclusion rules, edition matching, completed-sale classification, update cadence, and correction contact.
- Show record review dates only when records are actually reviewed. Keep price observation dates separate from bibliographic review dates.
- Support alternate-script names and sourced aliases for people and publishers. Avoid merging identities based only on transliteration.
- Add a short factual overview above each book's edition comparison, derived from verified records rather than promotional template text.

Example format, to populate only with verified facts:

> [Original title] is a [year] photobook featuring [credited person], published by [publisher]. MuseBooks records [verified edition count] editions. Physical and digital records are compared separately. Prices below are source observations, not a current market valuation.

This structure may make extraction and attribution easier. It does not guarantee an AI citation.

## Structured data

Structured data is machine-readable markup describing the visible page. Existing `Book`, `BreadcrumbList`, `WebSite`, `WebPage`, and profile `CollectionPage` markup is a useful starting point.

| Page family | Proposed markup | Constraints |
| --- | --- | --- |
| Book work | Stable `Book` identity, title aliases, verified credits and edition relationships | A featured model is not automatically the author; reflect actual credited roles |
| Edition | Distinct `Book` entity with ISBN, publisher, datePublished, bookFormat, inLanguage, and numberOfPages where verified | Do not put conflicting edition facts on the parent work |
| Directory/profile | `CollectionPage`, breadcrumbs, and `ItemList` for records actually shown | Add `Person` or `Organization` identity only when supported by catalog evidence |
| About/site | `Organization` linked to `WebSite` | Use verified owner and contact details; do not invent social profiles |

Do not turn confirmed sold prices into current `Offer` availability. If offers are added later, keep asking prices, auction bids, completed sales, currency, seller identity, edition, and freshness distinct. MuseBooks is a catalog linking to external sellers; assess applicable search-feature eligibility before adding commerce markup. Generic `Book` markup alone does not promise a rich result.

## Search opportunities to validate

These are intent hypotheses based on the product, not researched search volumes. Prioritize existing book and profile pages before creating broad guides.

| Search intent | Existing or proposed destination | What would make it useful |
| --- | --- | --- |
| Exact title plus ISBN, publisher, or edition | `/books/{slug}` | Original-script and English titles, verified edition facts, sources |
| Person name plus photobook bibliography | `/models/{id}` | Sourced aliases, publication chronology, linked edition records |
| Publisher plus photobook catalog | `/publishers/{id}` | Verified publisher identity, catalog coverage, linked books |
| Title plus available price | Book page and active listings | Current observation dates, condition, currency, external purchase source |
| Title plus sold price | Book page and sold listings | Confirmed completed physical sales with dates and comparability limits |
| How physical and digital editions differ | Proposed collector guide | Sourced examples of format, access, content, and rights differences |
| Japanese or Taiwanese photobook discovery | Proposed curated regional pages | Useful editorial context and linked catalog records, beyond a filter clone |

Validate demand and current visibility using Search Console and regional SERP research before commissioning new page families. The strongest runner-up is regional discovery content, but rendering and indexing consistency come first because they affect the existing catalog. Broad keywords may also refer to personalized photo-printing services; qualify the site's focus on published model, idol, and celebrity photobooks.

## GEO and crawler policy

For Google's AI search features, ordinary search eligibility remains the foundation; Google specifies no special AI schema or AI text-file requirement. Start with retrievable text, clear entities, source citations, and accurate dates. [Google AI features guidance](https://developers.google.com/search/docs/appearance/ai-features)

For other AI search systems, check each provider's crawler guidance. OpenAI distinguishes its search crawler `OAI-SearchBot` from the training crawler `GPTBot`; decide search access and training access separately. Review the actual CDN policy as well as robots.txt. The repository's wildcard allowance is not proof of live access. [OpenAI crawler documentation](https://developers.openai.com/api/docs/bots)

Do not prioritize `llms.txt`, generic FAQ expansion, or bulk generated summaries ahead of HTML retrieval and provenance. An optional AI-oriented index can be evaluated later, but this audit has no evidence that it would improve citations.

Maintain a repeatable citation-check sheet with prompt, language, country, engine, date, cited URL, edition accuracy, and price-date accuracy. Suggested prompts:

- Which editions exist for [verified title]?
- Which photobooks feature [verified person]?
- Where can I find a physical edition of [title]?
- What completed sales are recorded for [title], and when?

Record answers that make no citation as well as answers citing MuseBooks. Repeated checks measure observed behavior; they do not establish stable rankings or prove causation.

## Other checks and decisions

| Area | Observation | Decision |
| --- | --- | --- |
| Sitemap | Build enumerates core, book, model, and publisher URLs; deduplicates entries | Retain; validate deployed URLs and add truthful lastmod only when useful timestamps exist |
| Canonical host | Nginx config redirects HTTP and www to HTTPS apex | Good intended policy; verify live redirects and trailing-slash normalization |
| Build freshness | Static SEO records are generated from API data during deployment | Define rebuild/invalidation after imports; new records otherwise lack generated entries until rebuild |
| Origin configuration | Node-side SEO defaults to musebooks.my; browser build can receive another VITE_SITE_URL | Validate one explicit production canonical origin across both paths |
| Mobile builds | Mobile mode skips web SEO generation and strips analytics | Keep mobile assets separate from website deployment; SEO applies to public web routes |
| Localization | English initial HTML; English/Japanese/Chinese UI preference support | Preserve original-script catalog facts now; do not add hreflang until real translated URLs exist |
| Internal links | Book links to people/publishers; profiles and listings link to books | Preserve and include these links in initial HTML; add crawlable pagination |
| Cover images | Several cover images use empty alt attributes | Review meaningful standalone covers; retain empty alt for truly decorative/redundant images |
| Performance | Detail loading depends on all catalog pages plus origins | Reduce request fan-out; measure LCP, INP, and CLS before claiming performance problems |
| Analytics | Initial HTML includes Google Analytics | Confirm collection and define source-click/save events; tag presence is not traffic evidence |
| Content quality | Detail supports a summary and facts; profiles emphasize record lists | Sample real catalog records before assessing duplication or coverage quality |

## Implementation checklist

### First milestone: reliable access and indexing

- [ ] Independently verify DNS, HTTPS, apex/www redirects, robots.txt, and sitemap.xml.
- [ ] Inspect one live book, one model, one publisher, and one missing URL.
- [x] Render useful catalog text and links in initial HTML.
- [x] Resolve the `/v1/` robots conflict for any remaining rendering dependencies.
- [x] Keep valid book metadata stable while loading and during transient API errors.
- [x] Implement real 404 routing and synchronized build/client indexing policies; deployment validation is pending.
- [ ] Validate canonical origin, trailing slashes, query parameters, and pagination behavior.

### Second milestone: authoritative catalog records

- [x] Expose metadata source links and verified edition facts.
- [x] Add About, methodology, and correction information.
- [x] Expand structured data to reflect verified work/edition identity.
- [x] Replace full-catalog detail loading with record-specific retrieval or bootstrap data.
- [x] Provide a catalog-updated rebuild dispatch; catalog operators must trigger it after changes.

### Third milestone: measure and expand

- [ ] Verify Search Console and submit the sitemap.
- [ ] Establish indexed-page, query, click, and impression baselines by page family and country.
- [ ] Measure useful actions such as source visits and saved books, with applicable privacy controls.
- [ ] Research demand for collector guides and curated regional pages.
- [ ] Establish repeated AI citation and factual-accuracy checks.
- [ ] Consider maintained translated URLs after confirming demand and editorial capacity.

## Verification plan

The next implementation should add focused checks for behavior missing from the current tests:

1. Initial HTML contains real book facts and model/publisher/book anchors without JavaScript.
2. Slow successful loading never changes a valid page to a missing/noindex state.
3. Confirmed missing books and profiles return HTTP 404 with suitable metadata.
4. Temporary API failure is distinguishable from missing data.
5. Robots policy permits resources required for rendering public pages.
6. Static and client metadata agree on canonical origin and indexing rules.
7. Sitemap URLs resolve to intended canonical pages after deployment.
8. Structured data values match the displayed edition and source observations.

Use Search Console URL Inspection for deployed rendering and indexability. Validate structured data with appropriate validators, and measure real page experience rather than inferring it from architecture alone.

## Evidence inventory

Primary repository evidence:

- `frontend/index.html`: HTML shell, language, analytics tag.
- `frontend/vite.config.js`: website/mobile build split and SEO build integration.
- `frontend/scripts/seo-build.mjs`: static metadata entries, sitemap, robots rules, API-backed build.
- `frontend/scripts/seo-build.test.mjs`: existing metadata tests.
- `frontend/src/lib/seo.js`: canonical origin, page metadata, structured data, unknown-route flag.
- `frontend/src/components/SeoHead.jsx`: runtime metadata mutation.
- `frontend/src/pages/Home.jsx`: loading sequence, route metadata, catalog and book navigation.
- `frontend/src/pages/BookDetail.jsx`: visible work/edition facts and source links.
- `frontend/src/pages/DirectoryProfile.jsx`: profile loading, filters, pagination, metadata, internal links.
- `frontend/src/pages/CatalogPages.jsx`: directory and listing views.
- `frontend/src/components/EditionPrices.jsx`: price classification, source links, observation dates.
- `frontend/src/lib/preferences.jsx`: browser-stored language preferences.
- `backend/model/catalog_response.go`: edition metadata and listing observation fields.
- `backend/router/router.go`: public read routes.
- `deploy/musebooks-site.conf`: redirect intent and SPA fallback.
- `.github/workflows/deploy-musebooks.yml`: API-dependent frontend build and deployment.
- `README.md` and `DEPLOYMENT.md`: product scope and deployment context; historical statements require rechecking.

External guidance was read on the inspection date and is linked beside the recommendations it supports. Technical risks above are inferred from repository behavior; no production indexing failure, traffic loss, or citation improvement has been demonstrated.
