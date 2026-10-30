# Taiwan digital photobook leads through 2026-10-30 — round 6

## What new creator/title combination emerged?

### Takeaway

The strongest new combination is 蕭芷渲 — **《芷為你而閃亮-蕭芷渲數位寫真書》**. 蕭芷渲 already has a different digital photobook in the local catalog, so this is a new title/creator pair rather than a newly discovered creator. This exact title and Google Play ID do not appear in the digital leads reviewed in rounds 2–5. ([round 2](../Taiwan%20influencer%20photobook%20leads%202/digital_taiwan.md), [round 3](../Taiwan%20influencer%20photobook%20leads%203/digital_taiwan.md), [round 4](../Taiwan%20influencer%20photobook%20leads%204/digital_taiwan.md), [round 5](../Taiwan%20influencer%20photobook%20leads%205/digital_taiwan.md))

### Cited Findings

- The direct Taiwan storefront product is [Google Play book GPGZEQAAQBAJ](https://play.google.com/store/books/details?id=GPGZEQAAQBAJ&hl=zh_TW&gl=TW). It names 蕭芷渲 as author, identifies the item as an e-book, and displays publication as 2022年8月 by 滾石移動. The title is **《芷為你而閃亮-蕭芷渲數位寫真書》**.
- The matching [Google Books bibliographic record](https://books.google.com.tw/books?id=GPGZEQAAQBAJ&hl=zh-TW) identifies 蕭芷渲 as author and 滾石移動 as publisher, gives the date as **2022-08-05**, and lists **242 pages**. Its description is written in the author’s first person and says readers helped choose the book’s title; it also thanks them for supporting her first solo photobook. This connects the product listing to the author’s creator/audience relationship.
- A Taiwan-market creator signal appears in MediaDrive’s [2022/08 travel-and-lodging influencer ranking PDF](https://www.mediadrive.com.tw/manage/files/44220220928180430.pdf): it lists **蕭芷渲Iris** at rank 8 with **627,235 followers**. The name aligns with the book’s author, 蕭芷渲. This supports treating her as a Taiwan-facing online creator; it does not establish citizenship or residence.
- Google Play exposes the direct [cover image asset](https://play.google.com/books/publisher/content/images/frontcover/GPGZEQAAQBAJ?fife). The JPEG returned successfully and was visually checked: it is a pale-blue cover with a portrait of a smiling woman in a white top and the title text **「芷為你而閃亮」**.

### Inferences

- The combined direct product and bibliographic records support a **digital e-book edition** from 滾石移動, dated 2022-08-05, with 242 digital pages. Google Play’s product page specifies “e-book” but does not identify a file subtype; record the format as digital/e-book and do not assert EPUB or PDF.
- The Taiwan context is supported by a locally targeted Google Play listing, a Taiwan-market influencer ranking, and a Taiwan digital-publishing context. No source checked here establishes the creator’s nationality or residence, so neither is claimed.

## Does the source chain support recording this edition?

### Takeaway

**Provisional candidate; no EISBN is displayed.** The direct retailer, Google Books metadata, author context, and identifiable cover are aligned. The source chain supports recording a digital edition with EISBN left blank; the Google Books platform ID is not an EISBN. The exact file container remains unspecified.

### Cited Findings

- The Google Play item is the direct product page for an e-book, and Google Books ties the same title and author to the 2022-08-05 release, 滾石移動, and 242 pages. Neither page displays an EISBN. Treat `GPGZEQAAQBAJ` as Google’s volume/product ID, not as an ISBN.
- The direct cover asset above matches the product title visually. No replacement cover or MuseBooks cover file was created.
- Live MuseBooks exact-title query [`芷為你而閃亮`](https://musebooks.my/v1/books?q=%E8%8A%B7%E7%82%BA%E4%BD%A0%E8%80%8C%E9%96%83%E4%BA%AE) returned `total: 0`.
- Live MuseBooks creator query [`蕭芷渲`](https://musebooks.my/v1/books?q=%E8%95%AD%E8%8A%B7%E6%B8%B2) returned one different title: **《芷為你而燦爛-蕭芷渲數位寫真書》**, work `work-tw-7a111147a978c621209750fd`, with digital edition `edition-0a375843809b4446a5735c6f` (莉奈文創; 2023-05-20; 186 pages; Readmoo listing [210282307000101](https://readmoo.com/book/210282307000101)). The new Google Play title is absent from this result.
- The local [Taiwan photobook catalog, 蕭芷渲 section](../../scraper/taiwan-photobook-catalog.md#L1720) has that same 2023 Readmoo title and no row for **《芷為你而閃亮-蕭芷渲數位寫真書》**. Exact searches of the existing round 2–5 research notes also found no occurrence of 蕭芷渲, the new title, or Google Play ID `GPGZEQAAQBAJ`.

### Inferences

- This is a distinct title from the catalogued 2023 book: the wording, Google product ID, publisher, date, and page count differ. If added, do not merge it into the existing 2023 work solely because the author name is the same.
- I would **not hold solely for the missing EISBN**: Google Play directly identifies the product as an e-book, and the same product’s Google Books record supplies publisher, date, author, and page count while the cover asset is identifiable. Leave EISBN blank and do not substitute the Google Books ID.

### Gaps

- Neither Google page states a concrete file container (EPUB/PDF); keep the format at digital/e-book unless a publisher source supplies more detail. If a future import field requires a file subtype, hold until that subtype is verified.
- No source checked here establishes 蕭芷渲’s nationality or residence. This note supports Taiwan creator-market relevance, not a citizenship claim.

No database, R2 object, or catalog file was changed for this research note.
