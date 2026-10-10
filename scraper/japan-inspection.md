> Current policy: retail bookstores and digital stores are excluded from all scraping operations. Retail live results below describe earlier inspection only. Marketplace active and sold scraping remains supported.
>
> Current collection access policy (2026-10-10): Mercari remains disabled pending
> access/terms approval, as specified in `scraper.md`. The historical successful
> browser checks below do not authorize or enable its collection. Current Japan
> imports use Yahoo Auctions, Yahoo Flea Market, and Rakuma.

# Japan book scraper verification — 2026-10-05

Scope: `photobook_worker.py` and the `japan_photobook_worker.py` JSON
stdin/stdout entrypoint used by the books pipeline. Legacy `scraper_worker/`
trading-card workers were not changed. Public browser checks exercised discovery,
details and normalized observations; no records were imported into the database.

## Live results

| Source | Active book listing | Completed listing | Configuration |
| --- | --- | --- | --- |
| Yahoo! JAPAN Auctions | `p1246942418`, Enako W:WONDERLAND, JPY 3,500, `auction_current` | `q1243985894` and `p1244003190`, Enako エピローグ, JPY 1,760 each; `s1245263409`, JPY 1,500; `auction_hammer` | Enabled; active and native closed-search sold discovery |
| Mercari Japan | `m66055261560`, Enako mini photobook, JPY 330 | `m93190924618`, 林襄 photobook, JPY 6,699; keyword sold search also returned `m52768264219`, Enako エピローグ, JPY 2,800; selected Product `SoldOut` | Enabled; active/sold routes verified; rendered-page pagination only |
| Rakuma | `ec915c42e01a209065445dd76a41d8e2`, Enako BUNNY GIRL'S, JPY 3,000 | `5b53076cb0ccb56fe2620973d9d33d32`, Enako エピローグ, JPY 1,600, visible `SOLDOUT` | Enabled; sold jobs require an exact public item URL or verified search URL |
| Yahoo! Flea Market | `z698017440`, Enako enalive, JPY 1,800 | `z675632342`, C103 Enako photobook **bundle**, JPY 18,000; public sold receipt and purchase timestamp | Enabled; sold jobs require an exact public item URL or verified search URL |
| Rakuten Books | Search returned `18280957`, Enako エピローグ, JPY 3,300, and `16838189`, OFF COSTUME, JPY 2,420 | Ordinary retail catalog; no public completed-transaction feed configured | Enabled for catalog/active/detail; physical active verified, Kobo digital active remains unverified |
| BOOK☆WALKER Japan | Digital `de60a06148-1391-4af6-827c-dea4e264d1c5` and `dea610c149-40f1-4b75-a03f-30022830341f`, JPY 1,320 each | Digital retailer; no public completed-transaction feed configured | Enabled for catalog/active/detail |
| Suruga-ya | Security verification page; skipped | Not verified | Disabled/blocked |
| Mandarake | Configured order-store search and home routes redirect to a generic `www.mandarake.co.jp` page with no product grid | Not verified for this configured ordinary store source | Remains disabled/review |

The actual regional worker returned successful batches for all eight active/sold
marketplace cases above, plus the two retail search cases. Yahoo's keyword
closed-search job returned all three completed books listed in the table.
The fixed-price sold observations preserve prices displayed on completed item
pages; no private payment or negotiated settlement records were accessed.
Mercari's keyword `status=sold_out` job returned one completed book and rejected
two non-book candidates. The Yahoo Flea result is a bundle price and must not be treated as a single-book
edition price during downstream matching.

## Repairs

- Wait for selected product fields, not just an initial footer/navigation shell.
  Mercari needs extra hydration time before its Product schema appears.
- Recognize Japanese purchase/bidding controls, completed auctions with bids,
  sold receipts, and `SOLDOUT`. Zero-bid, future-ending and cancelled auctions
  are not sold observations.
- Use selected-item evidence: Yahoo recommendations above the auction panel,
  seller prose, and related products cannot determine its status or price.
- Preserve Mercari's original JPY price even when its international display
  shows MYR. Its selected `SoldOut` Product schema confirms completion.
- Rakuma's visible sold badge overrides its stale `InStock` schema.
- Yahoo completed auction prices use the selected ended auction's `現在`/
  `落札価格` field; classify active bids as `auction_current` and completed
  auction prices as `auction_hammer`.
- Restrict Rakuten product links to `/rb/{id}/` and `/rk/{id}/`; canonicalize
  tracking URLs to avoid spending detail slots on duplicate offers. Product
  metadata supplies the title when earlier H1s are empty logo headings.
- Restrict BOOK☆WALKER details to `/de{UUID}/`. Verified keyword search is
  `/search/?word={query}&qcat=8`; navigation/login/series links are excluded.
- Magazine clippings and laminated excerpts are excluded from book listings.
- Retail sold jobs fail explicitly. Unverified Rakuma/Yahoo Flea keyword sold
  jobs are rejected before enqueueing rather than repeatedly retrying the active
  search route. Exact sold URLs continue through existing host validation.
- Mercari no longer invents later-page tokens. Without an observed next URL,
  a discovery run stops at the rendered page; this is not exhaustive inventory.
- Japan verification-required details are skipped, while public records are
  retained. An entirely verification-blocked batch reports a blocked source.

All 50 Python worker/adapter regression tests pass. The offline URL/identity dry
run passes, backend catalog/database checks pass, and `git diff --check` passes.
Seed changes take effect when the backend next executes its seed routine. The
running database was not modified and the backend was not restarted.

## Reproduction

Run `japan_photobook_worker.py` with UTF-8 JSON on stdin. Source host lists must
match the source being tested.

Yahoo active or sold discovery:

```json
{"sourceId":"yahoo-auctions-jp","source":{"id":"yahoo-auctions-jp","kind":"marketplace","region":"JP","locale":"ja-JP","allowedFormats":["physical"],"allowedHosts":["auctions.yahoo.co.jp"],"ratePerMinute":6},"operation":"sold_discovery","query":"えなこ エピローグ","format":"physical","humanModelKeywords":["えなこ"],"maxCandidates":3,"maxDetailPages":3,"maxPages":1}
```

For an active auction use `operation: "active_discovery"`. For an exact item
add `url`, such as `https://auctions.yahoo.co.jp/jp/auction/p1246942418`.

Rakuma exact sold item:

```json
{"sourceId":"rakuma","source":{"id":"rakuma","kind":"marketplace","region":"JP","allowedFormats":["physical"],"allowedHosts":["fril.jp","item.fril.jp"],"ratePerMinute":6},"operation":"sold_discovery","url":"https://item.fril.jp/5b53076cb0ccb56fe2620973d9d33d32","format":"physical","humanModelKeywords":["えなこ"],"maxCandidates":1,"maxDetailPages":1}
```

BOOK☆WALKER digital active:

```json
{"sourceId":"bookwalker-jp","source":{"id":"bookwalker-jp","kind":"digital_store","region":"JP","allowedFormats":["digital"],"allowedHosts":["bookwalker.jp","www.bookwalker.jp"],"ratePerMinute":6},"operation":"active_discovery","query":"えなこ","format":"digital","humanModelKeywords":["えなこ"],"maxCandidates":3,"maxDetailPages":3}
```
