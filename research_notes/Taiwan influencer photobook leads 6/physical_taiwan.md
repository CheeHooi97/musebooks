# Physical Taiwan creator photobook leads

## Does a fresh physical edition pass the exclusion and duplicate checks?

### Takeaway

No new physical edition passed every requested check by 2026-10-30. The strongest two ISBN-backed leads were checked against Taiwan reports 2–5, the local Taiwan catalog, and the live MuseBooks API; one is outside the creator-photobook scope and the other lacks proof of a Taiwan creator connection and several edition details.

### Cited Findings

- Prior physical research notes for batches 2–5 document earlier evaluations and are linked here: [batch 2](../Taiwan%20influencer%20photobook%20leads%202/physical_taiwan.md), [batch 3](../Taiwan%20influencer%20photobook%20leads%203/physical_taiwan.md), [batch 4](../Taiwan%20influencer%20photobook%20leads%204/physical_taiwan.md), and [batch 5](../Taiwan%20influencer%20photobook%20leads%205/physical_taiwan.md).
- Exact-title/ISBN searches found no matching row for either K-DOL愛心增加學院 寫真書 ([title query](https://musebooks.my/v1/books?q=K-DOL%20%E6%84%9B%E5%BF%83%E5%A2%9E%E5%8A%A0%E5%AD%B8%E9%99%A2%E5%AF%AB%E7%9C%9F%E6%9B%B8&pageSize=50&page=1); [ISBN query](https://musebooks.my/v1/books?q=9786264006330&pageSize=50&page=1)) or Minamo 1st 寫真集 ([title query](https://musebooks.my/v1/books?q=Minamo%201st%20%E5%AF%AB%E7%9C%9F%E9%9B%86&pageSize=50&page=1); [ISBN query](https://musebooks.my/v1/books?q=9786264374781&pageSize=50&page=1)).
- Neither title nor ISBN appears in the checked local [Taiwan photobook catalog](../../scraper/taiwan-photobook-catalog.md); the catalog contains previously indexed examples such as TOKKI CUTIE's *FIRST JUMP* (ISBN 9786267776919) and 寶兒's *Babe Fantasy* physical edition (ISBN 9786267683798). [Catalog](../../scraper/taiwan-photobook-catalog.md)

### Inferences

- Neither lead is a duplicate of an existing live MuseBooks item based on the exact-title and ISBN queries. That does not by itself establish eligibility: the K-DOL product falls outside the requested creator-photobook type, while Minamo's Taiwan creator connection is unverified. [K-DOL title query](https://musebooks.my/v1/books?q=K-DOL%20%E6%84%9B%E5%BF%83%E5%A2%9E%E5%8A%A0%E5%AD%B8%E9%99%A2%E5%AF%AB%E7%9C%9F%E6%9B%B8&pageSize=50&page=1); [Minamo title query](https://musebooks.my/v1/books?q=Minamo%201st%20%E5%AF%AB%E7%9C%9F%E9%9B%86&pageSize=50&page=1)

### Gaps

- Catalog and API checks cover exact title and ISBN variants found in this pass; transliteration or alternate-name records could require a separate manual reconciliation if a candidate later qualifies. [Local Taiwan catalog](../../scraper/taiwan-photobook-catalog.md); [MuseBooks API](https://musebooks.my/v1/books)

## What are the strongest physical near-misses, and what do their records establish?

### Takeaway

K-DOL愛心增加學院 寫真書 has strong publisher and library bibliographic evidence but is a 2024 fictional-drama ensemble tie-in. Minamo 1st 寫真集 has a Taiwan National Central Library print record for May 2026, but the available evidence does not establish that Minamo is a Taiwan influencer or creator.

### Cited Findings

- **K-DOL愛心增加學院 寫真書** — Taiwan Kadokawa's official product page identifies the exact title, the credited author/project K-DOL愛心增加學院, ISBN **9786264006330**, and listing date **2024-09-26**. Its description presents the book as photographs, cast profiles, and drama material for a fictional school story, rather than an individual creator's photobook. [Taiwan Kadokawa product page](https://www.kadokawa.com.tw/products/9786264006330)
- The National Central Library bibliography identifies the K-DOL print edition as paperback, **144 pages**, published by Taiwan Kadokawa in **September 2024**. It also lists a separate ebook EISBN; that ebook is not the physical edition being evaluated here. [NCL bibliography](https://isbn.ncl.edu.tw/FCKEDITOR_UploadFiles/1726802166.pdf)
- **Minamo 1st 寫真集** — The NCL monthly new-book list records Minamo as creator/author, 鈴木ゴータ as photographer, Taiwan ToHan as publisher, the registered publication month **2026-05**, print ISBN **9786264374781**, and paperback format. The same record separately lists EISBN **9786264374729**, which is not the print ISBN. [NCL monthly new-book list](https://isbn.ncl.edu.tw/FCKEDITOR_UploadFiles/1776397570.pdf)
- The NCL records do not provide an independently recovered cover-image asset for either title. The Kadokawa page is the direct product page, but an asset URL for its cover was not identified in the accessible page text; no Minamo publisher or direct-seller product page was found in this pass. [Taiwan Kadokawa product page](https://www.kadokawa.com.tw/products/9786264006330); [NCL Minamo record](https://isbn.ncl.edu.tw/FCKEDITOR_UploadFiles/1776397570.pdf)

### Inferences

- K-DOL does not meet the target category: the publisher describes a drama tie-in featuring an ensemble cast, and the listing date is in 2024, before the current search window's 2026 releases. Treat it as an ISBN-verified out-of-scope lead, not a new creator photobook. [Taiwan Kadokawa product page](https://www.kadokawa.com.tw/products/9786264006330); [NCL bibliography](https://isbn.ncl.edu.tw/FCKEDITOR_UploadFiles/1726802166.pdf)
- Minamo is a possible physical-photo-book lead but not a verified Taiwan influencer/creator work. A Taiwan publisher and an NCL print record do not establish the creator's Taiwan connection. [NCL monthly new-book list](https://isbn.ncl.edu.tw/FCKEDITOR_UploadFiles/1776397570.pdf)

### Gaps

- K-DOL: exact retail/release day beyond the publisher listing date, an independently identified cover-image asset, and evidence that this is a creator's own photobook are missing. The available publisher description instead identifies a fictional drama ensemble product. [Taiwan Kadokawa product page](https://www.kadokawa.com.tw/products/9786264006330)
- Minamo: no page count, exact release day, primary publisher/direct-seller page, identified cover asset, or source verifying a Taiwan creator connection was found. The NCL list supplies a publication month, not an exact day, and lists a separate ebook ISBN. [NCL monthly new-book list](https://isbn.ncl.edu.tw/FCKEDITOR_UploadFiles/1776397570.pdf)

## What should be reported as the result of this pass?

### Takeaway

There are **zero verified new physical Taiwan influencer/online-creator/streamer/cheerleader photobooks** from this pass that meet the requested evidence standard. Keep both titles above as near-misses only; neither is an import-ready addition.

### Cited Findings

- K-DOL has a publisher-backed physical ISBN and a library page count, but its publisher page describes drama cast photography and its 2024 listing date is outside the current release year. [Taiwan Kadokawa product page](https://www.kadokawa.com.tw/products/9786264006330); [NCL bibliography](https://isbn.ncl.edu.tw/FCKEDITOR_UploadFiles/1726802166.pdf)
- Minamo has an NCL print ISBN and May 2026 publication month, but the searched live database has no exact-title or ISBN match and the source does not establish a Taiwan creator connection, pagination, exact day, or cover asset. [NCL monthly new-book list](https://isbn.ncl.edu.tw/FCKEDITOR_UploadFiles/1776397570.pdf); [MuseBooks title query](https://musebooks.my/v1/books?q=Minamo%201st%20%E5%AF%AB%E7%9C%9F%E9%9B%86&pageSize=50&page=1); [MuseBooks ISBN query](https://musebooks.my/v1/books?q=9786264374781&pageSize=50&page=1)

### Inferences

- Do not promote either near-miss as a qualifying new Taiwanese creator edition without the missing scope and cover evidence. The live duplicate checks are clear, but absence from the database is not sufficient to pass the other requested fields. [Taiwan Kadokawa product page](https://www.kadokawa.com.tw/products/9786264006330); [NCL monthly new-book list](https://isbn.ncl.edu.tw/FCKEDITOR_UploadFiles/1776397570.pdf)

### Gaps

- This pass did not establish whether additional social-only preorder announcements exist outside indexed publisher, library, and retailer records. No third lead with stronger direct product evidence was verified by the cutoff date. [NCL monthly new-book list](https://isbn.ncl.edu.tw/FCKEDITOR_UploadFiles/1776397570.pdf); [local Taiwan catalog](../../scraper/taiwan-photobook-catalog.md)
