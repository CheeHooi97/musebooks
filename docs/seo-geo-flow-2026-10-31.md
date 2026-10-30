# MuseBooks SEO and GEO flow, 31 October 2026

Same order as the MuseCards run of 30 October: `seo-geo`, `seo-agentic`, crawl, then its ten-step SEO workflow, fixing after each step. Changes are in the working tree, not committed or deployed. Live measurements are from the current production site. "After" figures come from the real build run locally on a 31 October API snapshot.

## Status by step

| Step | How it ran | Result |
| --- | --- | --- |
| `seo-geo` | Skill, live checks | Fixed: see below. Citation rates not measured (no paid tool) |
| `seo-agentic` | Skill, all scripts; Lighthouse 13.6.0 locally, mobile only, because the PSI quota was exhausted | Agentic Browsing 3/3, Agent-UX 100/100, no P0 failure. Added WebMCP search markup |
| Crawl | Custom scan of all 6,450 English record pages from the build. `seo-firecrawl` was not used; `seo-crawl` is not installed here | No missing title, description or canonical; every page has one H1 |
| `keyword-research` | Skill; Search Console and Autocomplete | No volume or difficulty data, so nothing is scored |
| Competitor check | Free web search, 3 queries | Directional only |
| `keyword-clustering` | Manual map; skill not loaded (needs OpenSEO) | Below |
| `claude-seo-content-brief` | Manual brief; skill not loaded | Below; page not built |
| `on-page-seo-checker` | Manual, by the same scan; skill not loaded | Below |
| `30x-seo-content-audit` | Manual review; skill not loaded; no score given | Below |
| `30x-seo-internal-links` | Manual link data from the catalog; skill not loaded | Fixed one gap |
| `seo-audit` | Manual, from Search Console; skill not loaded (needs OpenSEO) | Below |
| `rank-tracker` | Manual baseline; skill not loaded | First snapshot, no changes to report |
| `seo-report` | This Markdown file; skill not loaded | No HTML report |

## Measured baseline

Search Console, last 7 days to 28 October (the report's displayed period): 193 clicks, 2.73K impressions, 7.1% CTR, average position 13.7. By clicks: Taiwan 80, Japan 53, South Korea 17, Hong Kong 14, Malaysia 10, China 9. Mobile 124, desktop 60, tablet 9.

Indexing report, last updated 23 October: 12.4K indexed, 914 not indexed (754 crawled but not indexed, 114 noindex, 24 server error, 12 Google chose another canonical, 5 redirect, 3 soft 404, 2 not found).

- All 5 server-error URLs rechecked now return 200, so those look transient.
- The noindex examples are filter URLs and merged-name redirect pages. Both are intended.
- The 2 soft 404 URLs rechecked are live thin model pages with almost no text. Google's reason is not stated, so thinness is the likely cause rather than a proven one.

Lighthouse, home page, local mobile run: performance 38, FCP 9.7 s, LCP 12.7 s, TBT 720 ms, CLS 0.06, 154 requests, 7.6 MB. 108 of those requests fetched the whole catalog. One cover image was 3.5 MB.

## What changed

| Problem | Fix | After |
| --- | --- | --- |
| Home downloads the entire catalog for 8 cards and 3 totals | Build writes `/home.json`; the full catalog loads only for visitors with saved books. Apps and dev fall back to the full load | 0 `/v1/books` requests in a local browser check; file is 76 KB against 2.6 MB. Lighthouse not re-run |
| No definition of the site | "What is MuseBooks?" on the home page in HTML, Markdown and the app (ja, zh-Hans, zh-Hant strings), with live counts in the HTML | Present |
| Home and `/books` carried the same 5,300 links | Home lists the newest 100 and links to `/books` | Home HTML 480 KB to 15 KB |
| Model and publisher pages had no text and "X publications" titles | Lead sentence from recorded facts, dated bibliography, title "X photobooks", Person/Organization markup | Same text in HTML, Markdown and app |
| Translated pages shared one description per language | Record-specific lead and description in ja, zh-Hant, zh-Hans, ko | Japanese books: 5,384 unique of 5,386 |
| `/jp` title repeated itself | Titles rebuilt, with a language word such as 寫真集 or 写真集 | "写真集・雑誌カタログ — MuseBooks" |
| Book descriptions were "Explore X..." | Uses the fact summary, ended on a whole sentence | Publisher, date and edition count |
| Book summary sat below the editions in HTML | Moved directly under the title | Present |
| Related links needed JavaScript | "More with X" in prerendered pages, up to 6 | 4,999 of 5,386 books share a person with another book |
| Copy claimed Japan, Taiwan, China, Malaysia | Live origins are Japan, Taiwan, South Korea. Copy and translations updated | Please confirm: China and Malaysia may be planned coverage |
| Sitemap had no dates | API returns `updatedAt` (latest of work and editions); sitemap writes `lastmod` | Takes effect on the build after the API is deployed |
| Agent search | WebMCP attributes and a real GET form, `SearchAction` on the home page | Lighthouse may still count WebMCP as N/A in its browser |

Book pages also link to featured people through `about`, not `author`, because a featured model is not necessarily the author.

Tests: 37 SEO tests pass, including 2 new ones; `backend/model` passes. Whole-page audit after the change: 51 titles over 70 characters (long original titles, left alone, because identity outweighs a length rule) and 4 descriptions over 160 by escaped HTML length.

Not tested: nginx with the new `home.json` rule, the production deploy, the React language-switch view of the new home text, and a repeat Lighthouse run.

## Follow-up fixes, same day

- **Coverage copy.** Search of 31 October: Malaysia 10 web records (6 people), and the catalog already holds 11 publications featuring 5 Malaysian models (藍星蕾 5, 周甄娜 2, 張安琪 2, 李藹蔚 1, 鄔唯 1). Mainland China 19 web records (12 people, mostly actors and singers), none in the catalog. Copy names Malaysian models and says mainland China is being added, because no Chinese-origin record exists yet.
- **`/books`.** Search, filters, sort and paging run on the API (`sort` added to `/v1/books`; `q` also matches photographer and publisher). Saved books load one by one.
- **Oversized covers.** The media Worker serves R2 covers above 300 KB as 720 px WebP. Covers hosted by publishers (for example maximkorea.net) are outside it.
- **Guide.** `/guides/digital-vs-physical-photobooks` in en, ja, zh-Hant, zh-Hans and ko.
- **Damaged records.** Hidden from the index and the sitemap; the importer now rejects titles containing `??`. The data itself still needs [the repair script](data-repair-2026-10-31.sql).
- **Same-title books.** Titles add the credited person when different people share a title.

## Still open

1. **Apply `data-repair-2026-10-31.sql`.** It needs production database access, which this session was refused. It repairs both damaged books and retires the true duplicate.
2. **Possible duplicates needing a person's check.** `明日も明後日も` (高崎かなみ, 集英社, 2023-01-23) has two records with different grajapa item IDs and covers. The 【オールアザー版】 pairs have different dates. Left as they are.
3. **Identity.** No named editor or official accounts are recorded, so no `sameAs`. Off-site mentions need work outside the codebase.
4. **Opaque URLs.** Not changed: 12.4K indexed pages would need redirects, and the risk outweighs the gain.

## Keyword clusters

Volume and difficulty: Unknown. Priority: NOT_SCORED. Evidence is Search Console and Google Autocomplete (unofficial endpoint), 31 October.

| Cluster | Measured examples | Target |
| --- | --- | --- |
| Name + 寫真 (largest pattern) | 高橋佳帆寫真 (17 impressions, position 8.6), 小映寫真 (17, 9.1), 林莎 寫真, 周宜霈寫真 | `/tw/models/*` |
| Name + 写真集 / グラビア | 井上もも 写真集 (4, 13.0), 乙アリスグラビア, 後藤まつり 写真集 | `/jp/models/*` |
| Exact title | 橋本梨菜 黒蜜, 未梨一花 回帰線, 仲根なのか ファースト写真集 おはなの | `/books/*` and editions |
| Korean magazines | 박민정 맥심 2024 pdf (9, 18.1), maxim bcut, 맥심b컷, 맥심 2026 | `/kr/books/*` |
| Newest and rankings | グラビア 写真集 最新, 写真集ランキング, 寫真集推薦 | Home editions for "newest". No ranking page: no data supports one |
| Definitions | デジタル写真集とは, 寫真集是什麼, gravure photobook meaning | Proposed guide, below |

**Never target:** "junior idol" terms and age-number queries that Autocomplete returned (possible sexualized content involving minors). These are excluded regardless of demand.

**Do not target:** "無料", "scans", "pdf" and "download" queries. Some bring clicks today (余家儀 寫真pdf), but the catalog links to legal sources and doesn't host files.

Competitor check: name queries return Amazon, publisher catalogs (Kodansha, Kobunsha), Rakuten and YouTube. Genre queries return shops, eBay, HMV and Goodreads. No dedicated cross-publisher database appeared in these samples, which is the position MuseBooks can hold. These are a few uncontrolled samples, not rankings.

## Content brief (built as the guide above)

- **Page:** `/guides/digital-vs-physical-photobooks`, with ja and zh-Hant editions first, since those markets show the demand.
- **Queries:** デジタル写真集とは, デジタル写真集 買い方, 寫真集電子書.
- **Answer first:** what a digital photobook is, then how it differs from print, using real edition pairs from the catalog. くりえみ金メダル くりえみ2 has two recorded digital editions, a usable example of why editions are recorded separately.
- **Sections:** where each format is sold; why one title can have several editions; what a recorded price means.
- **Rules:** no promises of availability; no invented page or content differences; no "free" angle. No word-count target.

## Content audit (qualitative)

Strong: About separates retail, asking, bid and completed-sale prices; missing facts are stated as unknown; corrections have a contact. Weak: no reviewed-on date; model and publisher pages stay short (median 45 and 54 words in the English HTML) because the catalog records little per person. More real data is the fix. Do not pad with template text.

## Rank baseline

First snapshot: no earlier point exists, so no changes are claimed. Search Console, 7 days to 28 October. Under 10 impressions a move means little.

| Query | Impressions | Clicks | Position |
| --- | ---: | ---: | ---: |
| 高橋佳帆寫真 | 17 | 1 | 8.6 |
| 小映寫真 | 17 | 1 | 9.1 |
| 박민정 맥심 2024 pdf | 9 | 2 | 18.1 |
| 林莎 honey | 6 | 2 | 7.5 |
| 純白彩永 寫真 | 5 | 1 | 9.8 |
| 井上もも 写真集 | 4 | 1 | 13.0 |
| 千葉奈々希 | 4 | 1 | 13.2 |
| 林莎 寫真 | 4 | 2 | 14.2 |

Compare after deployment, once Google has recrawled the model pages, over the same window length.

## After deploying

1. Deploy, then run `npm run check:geo -- https://musebooks.my` from `frontend`.
2. Deploy again (or dispatch `catalog-updated`) so the sitemap picks up `updatedAt` from the new API.
3. Confirm `https://musebooks.my/home.json` returns 200 and the home page makes no `/v1/books` requests.
4. Re-run Lighthouse on the home page and compare with the baseline above.
5. `npm run indexnow -- --submit` from `frontend`.
