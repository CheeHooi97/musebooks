# MuseBooks visibility in search and AI answers

MuseBooks follows the same SEO, GEO (generative engine optimization) and
answer-engine setup as MuseCards. MuseCards renders documents in a Go server;
MuseBooks prerenders them at build time (`frontend/scripts/seo-build.mjs`) and
nginx serves the files, so the same behavior comes from static files plus
nginx rules.

## What a crawler or agent receives

| Need | MuseBooks |
| --- | --- |
| Content without JavaScript | Every book, profile and list page is prerendered with its facts, editions, prices and links |
| Direct answers | Book pages lead with a citable summary and question headings ("When was X published?", "How much does X cost?", "What has X sold for?") from `src/lib/book-answers.js`, shared by React, the HTML and markdown |
| Structured data | `Book`/`PublicationIssue` with each edition, breadcrumbs, profile `ItemList`s, site `Organization` (`src/lib/seo.js`) |
| Markdown | `{page}.md` beside every indexable page (`/index.md` for home); `Accept: text/markdown` returns it at the page URL; page heads and `Link` headers point to it |
| Summary for AI systems | `/llms.txt` and `/llms-full.txt` (adds the methodology) |
| New publications | `/feed.xml` (Atom, 50 newest by publication date) |
| API | `/openapi.json` (OpenAPI 3.1) and `/.well-known/api-catalog` (RFC 9727) |
| Crawler policy | `robots.txt` with `Content-Signal: search=yes, ai-input=yes, ai-train=yes`, the same policy as MuseCards |
| Discovery headers | HTML documents send `Link` (markdown, api-catalog, llms.txt, sitemap) and `Vary: Accept` |

Signed image URLs are never baked into prerendered pages: covers point at
`/v1/catalog/media/redirect`, which robots.txt allows.

## Content rules

Keep the distinctions in the About page. Retail prices, marketplace asking
prices, auction bids and confirmed completed sales are different
observations; an ended listing is not a sale. Answers only use recorded facts
and say "not recorded" otherwise. Do not add keywords or claims the catalog
cannot support.

The policy permits AI training (`ai-train=yes`). To opt out of training while
staying citable, change the content signal to `ai-train=no` in
`frontend/scripts/agent-files.mjs`, and add per-agent groups (for example
`GPTBot`, `Google-Extended`, `CCBot`) if a hard block is wanted.

## Checks

After a deploy:

```powershell
npm run check:geo -- https://musebooks.my
```

It verifies initial HTML answers for browser and AI user agents, the markdown
twin and negotiation, `Link`/`Vary` headers, robots.txt access for search and
AI crawlers, llms.txt, the feed, OpenAPI and the API catalog. A passing check
does not verify bot IP access through Cloudflare or predict AI citations.

Cloudflare: keep AI crawlers allowed for musebooks.my (AI Crawl Control /
bot settings), and do not enable Cloudflare's managed robots.txt, which would
replace the file above.

For a monthly baseline, record the date, AI service, exact question, whether
web search was enabled, whether MuseBooks was cited, the URL and factual
accuracy, for questions the catalog can answer: a model's photobooks, a
photobook's publication date or ISBN, and its current or sold price.
