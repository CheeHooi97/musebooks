# MuseBooks Search Console setup and live URL checks

24 October follow-up, 22:14 SGT: the request queue is complete. Google accepted `/cn` and four remaining profile/publication requests. The Japanese, Traditional Chinese and Korean MAXIM August 2024 pages were already indexed with Google-selected canonicals matching their inspected URLs, so they were not resubmitted. The completed request-retry automation is paused; the 22:30 actual-indexing monitor remains active. [Updated per-URL request results](indexing-request-summary-2026-10-24.json).

Follow-up: [MAXIM August 2024 submission-error diagnosis](maxim-indexing-diagnosis-2026-10-23.md). Both affected language URLs passed Google's actual live crawl and indexability tests; no current site-side indexing blocker was found.

Checked 23 October 2026, Asia/Singapore, around 21:30–21:33 SGT.

The `musebooks.my` domain property was already present when this session opened. Settings confirmed **You are a verified owner**, with the property added to the account on 23 October. No duplicate property or DNS change was needed. This supersedes the earlier access limitation in the multilingual audit.

Submitted `https://musebooks.my/sitemap.xml` through Search Console. Google first displayed a transient fetch status, then confirmed **Sitemap processed successfully**, last read 23 October, with **33,250 discovered pages** and zero videos. No repeated submission was needed.

## Google's live inspection results

| URL | Crawl time, SGT | Fetch | Crawl allowed | Indexing allowed | Declared canonical | Result |
| --- | --- | --- | --- | --- | --- | --- |
| https://musebooks.my/jp | 21:30:17 | Successful | Yes | Yes | https://musebooks.my/jp | Page can be indexed |
| https://musebooks.my/tw | 21:30:51 | Successful | Yes | Yes | https://musebooks.my/tw | Page can be indexed |
| https://musebooks.my/cn | 21:31:03 | Successful | Yes | Yes | https://musebooks.my/cn | Page can be indexed |
| https://musebooks.my/kr | 21:31:27 | Successful | Yes | Yes | https://musebooks.my/kr | Page can be indexed |

All four tests used **Google Inspection Tool smartphone** and reported **URL is available to Google**. Their initial Google Index reports said **URL is unknown to Google**. Live eligibility is not confirmation of actual indexing, Google's eventual canonical selection, or search visibility. These checks sampled the four language homepages, not all 33,250 URLs. Reports for the new property were still processing.

The Japanese homepage's manual indexing request was accepted: Google confirmed it was added to a priority crawl queue. The user subsequently explicitly authorized manual requests for `/tw`, `/cn`, and `/kr`. Google accepted `/kr` and `/tw`, confirming both were added to its priority crawl queue. The `/cn` request returned **Quota Exceeded**, with instructions to try submitting again tomorrow. It was not repeatedly submitted or retried through another account. All language URLs remain discoverable through the successfully processed sitemap. Accepted requests do not confirm actual indexing.

Evidence is saved locally under `.tmp/gsc-sitemap-2026-10-23.png`, `.tmp/gsc-{jp,tw,cn,kr}-live-2026-10-23.png`, `.tmp/gsc-jp-indexing-requested-2026-10-23.png`, and `.tmp/gsc-language-checks-2026-10-23.json`.

Follow-up evidence: `.tmp/gsc-{tw,kr}-indexing-requested-2026-10-23.png`, `.tmp/gsc-cn-indexing-quota-2026-10-23.png`, and `.tmp/gsc-indexing-requests-2026-10-23.json`. No automatic retry was scheduled.

## Book and model monitoring sample

Inspected two publication pages and two model profiles in every language edition: 16 additional Google Index reports. Publications: Kasumi Mori's `すのかすみ。` and MAXIM August 2024. Models: AIKA and `치어리더 조연주`. All 16 reports said **URL is unknown to Google**; none was indexed at the baseline check. These were read-only Google Index checks, not new indexing requests or live-test claims.

The existing daily 22:30 Asia/Singapore monitor now covers all 20 fixed targets: these 16 pages plus the four homepages. It will notify on newly indexed pages and meaningful changes, remain quiet for unchanged states, and stop only once all 20 exact URLs are indexed with matching selected canonicals. The separate `/cn` indexing-request retry is unchanged. [Exact monitored URLs](search-console-monitor-targets.json). Raw baseline reports: `.tmp/gsc-sample-inspections-2026-10-23.json`. Persistent monitor state: `.tmp/musebooks-language-indexing-monitor.json`.

## Sample indexing requests and automatic retries

Following explicit user authorization, manual requests were submitted for the sampled pages until Google returned **Quota Exceeded** at approximately 22:14 SGT on 23 October. Nine sample URLs were accepted into Google's priority crawl queue. Seven remain unfinished: two encountered generic submission errors, one hit the quota, and four were not attempted after the quota was reached. Accepted requests were recorded immediately to prevent duplicate submissions. [Per-URL results](indexing-request-summary-2026-10-23.json).

The user additionally authorized automatic retries for generic submission errors. The existing 22:00 daily retry automation now handles the remaining sample requests and the previously queued `/cn` homepage: 17 fixed URLs total, nine accepted and eight unfinished including the homepage. It starts on 24 October, skips accepted or already-indexed URLs, stops each run at the first quota response, and retries unfinished work on following days. Generic errors are deferred rather than repeatedly retried in one run. It notifies on new acceptances and pauses once its entire request queue is accepted or already indexed. The separate 22:30 actual-indexing monitor is unchanged.

Persistent request queue: `.tmp/musebooks-indexing-request-queue.json`. Quota evidence: `.tmp/gsc-sample-quota-2026-10-23.png`. Acceptance screenshots are stored as `.tmp/gsc-sample-accepted-*-2026-10-23.png` and `.tmp/gsc-kr-model-indexing-requested-2026-10-23.png`.

[Sitemap report](https://search.google.com/search-console/sitemaps/info-drilldown?resource_id=sc-domain%3Amusebooks.my&sitemap=https%3A%2F%2Fmusebooks.my%2Fsitemap.xml). [Property settings](https://search.google.com/search-console/settings?resource_id=sc-domain%3Amusebooks.my).
