# Taiwan digital creator photobook leads — round 7

## Did this pass find a new, import-ready Taiwan creator ebook?

### Takeaway

No new digital title cleared both the Taiwan-creator qualification and duplicate checks. The direct retailer searches found a recently issued title for model 木子, but the live MuseBooks API already contains that title and five related digital works; the sources reviewed did not independently establish 木子 as a Taiwan influencer. Mier’s newly surfaced titles are likewise already present in the live catalog, and independent coverage identifies Mier as Malaysian.

### Cited Findings

- TAAZE lists **《回眸-木子性感寫真集》** as a Chinese ebook by 拾捌寫真製作所, dated **2026-09-09**, fixed-layout, 0.11 MB; its page names photographer 拾捌 and model 木子 (`@muzi_0t.3o`). It does not give a page count or ISBN. [TAAZE direct product page](https://www.taaze.tw/products/14100142314.html)
- Kobo’s Taiwan-market Rakuten store separately lists **《回眸-木子性感寫真集》** as ebook ISBN **7020081020018**, EPUB3 fixed-format; the listing names 拾捌寫真製作所 and 木子. Kobo’s identifier and format are kept as that retailer reports them; it was not treated as a conventional 978/979 ISBN. [Rakuten Kobo Taiwan product page](https://www.rakuten.com.tw/shop/kobo/product/b16a4678-5714-3488-b1c5-033a5cbfa8e5/)
- Google Play has a same-titled **《回眸-木子性感寫真集》** ebook by 拾捌, dated September 2026, published by 滾石移動, and lists **69 pages**. Its description credits 拾捌 as photographer and 木子 (`@muzi_0t.3o`) as model. TAAZE and Google Play differ on publisher naming and TAAZE does not provide pagination, so those fields should be attributed to their respective records rather than silently reconciled. [Google Play product](https://play.google.com/store/books/details/%E6%8B%BE%E6%8D%8C_%E5%9B%9E%E7%9C%B8_%E6%9C%A8%E5%AD%90%E6%80%A7%E6%84%9F%E5%AF%AB%E7%9C%9F%E9%9B%86?id=ZNgUEgAAQBAJ)
- The public MuseBooks API already returns **《回眸-木子性感寫真集》** as work `work-tw-75dbabfcd1f13f56402524c5`, with a digital edition and TAAZE metadata source. Its `木子` query currently returns six digital works: **《微光側影》**, **《鏡中迷情》**, **《晨光私語》**, **《午後的慵懶》**, **《回眸》**, and **《夢境夏娃》**. This live readback rules these titles out as missing additions at this check. [MuseBooks live creator query](https://musebooks.my/v1/books?q=%E6%9C%A8%E5%AD%90); [MuseBooks live exact-title query](https://musebooks.my/v1/books?q=%E5%9B%9E%E7%9C%B8-%E6%9C%A8%E5%AD%90)
- The Books.com publisher page for 拾捌 surfaced **《無聲凝視-Mier性感寫真集》**; the direct Taiwan Kobo/Rakuten listing for **《PUBLIC PRIVATE-Mier性感寫真集》** names model Mier (`@medea0212`), photographer 拾捌, publisher 拾捌寫真製作所, date **2026-07-29**, product ISBN **7020081020013**, and EPUB3 fixed-format. [Books.com publisher results](https://www.books.com.tw/web/sys_puballb/books/?pubid=18photostudio); [Rakuten Kobo Taiwan product page](https://www.rakuten.com.tw/shop/kobo/product/c8f22bf6-5516-372f-898b-1cc41b6d2214/)
- A live MuseBooks creator query already returns eight digital Mier titles, including **《PUBLIC PRIVATE-Mier性感寫真集》** and **《無聲凝視-Mier性感寫真集》**. Taiwan reporting identifies Mier/米兒 as a Malaysian model and internet personality, so the Taiwan storefront and publisher do not establish that she is a Taiwan influencer. [MuseBooks live Mier query](https://musebooks.my/v1/books?q=Mier); [EBC News profile](https://news.ebc.net.tw/news/world/175502); [Yahoo Taiwan report](https://tw.news.yahoo.com/%E5%A4%A7%E9%A6%AC%E7%B6%B2%E7%B4%85%E6%9B%AC%E8%BE%A3%E7%85%A7%E4%BD%9C%E9%A2%A8%E6%8E%80%E8%AD%B0-ig%E7%8B%82%E8%A2%AB%E9%97%9C%E4%BA%8C%E7%99%BE%E8%90%AC%E4%BA%BA%E6%B0%A3%E6%9A%B4%E8%B7%8C-112513040.html)
- Google Play and TAAZE have direct pages for 木子’s additional September 2026 ebooks **《晨光私語-木子性感寫真集》**, **《午後的慵懶-木子性感寫真集》**, **《微光側影-木子性感寫真集》**, and **《夢境夏娃-木子性感寫真集》**; each Google Play listing names 木子 as model and 拾捌 as photographer, with Google Play pagination of 79, 66, 62, and an unspecified count respectively. They are among the six works returned by the live MuseBooks 木子 query. [晨光私語 — Google Play](https://play.google.com/store/books/details/%E6%8B%BE%E6%8D%8C_%E6%99%A8%E5%85%89%E7%A7%81%E8%AA%9E_%E6%9C%A8%E5%AD%90%E6%80%A7%E6%84%9F%E5%AF%AB%E7%9C%9F%E9%9B%86?id=jNgUEgAAQBAJ); [午後的慵懶 — Google Play](https://play.google.com/store/books/details/%E6%8B%BE%E6%8D%8C_%E5%8D%88%E5%BE%8C%E7%9A%84%E6%85%B5%E6%87%B6_%E6%9C%A8%E5%AD%90%E6%80%A7%E6%84%9F%E5%AF%AB%E7%9C%9F%E9%9B%86?id=gNgUEgAAQBAJ); [微光側影 — Google Play](https://play.google.com/store/books/details/%E6%8B%BE%E6%8D%8C_%E5%BE%AE%E5%85%89%E5%81%B4%E5%BD%B1_%E6%9C%A8%E5%AD%90%E6%80%A7%E6%84%9F%E5%AF%AB%E7%9C%9F%E9%9B%86?id=fNgUEgAAQBAJ); [夢境夏娃 — TAAZE](https://www.taaze.tw/products/14100142342.html)

### Inferences

- A retailer result, Taiwan ebook platform, Taiwan publisher, or a Taiwan-origin value already stored in MuseBooks does not independently prove the featured model is a Taiwan influencer. For 木子, the reviewed product pages identify only the model handle; a reliable creator-origin/profile source was not located. Keep this as a qualification gap instead of assuming nationality.
- These are creator-specific ebooks, but live API records show the relevant works are already cataloged. Do not create duplicate work or edition records from the retailer hits.

### Gaps

- No independent source reviewed in this pass establishes 木子’s identity, Taiwan connection, or influencer status beyond a retailer-supplied social handle.
- Google Play exposes page counts for several 木子 ebook titles, while the TAAZE product pages use the retailer’s proprietary Image reader and generally do not list an ISBN or pagination. No source reviewed reconciles the different publisher labels between these platforms.

## What Taiwan-market lead was excluded on creator origin?

### Takeaway

Mier was excluded from the Taiwan-influencer additions: the creator’s photobooks are sold through Taiwan storefronts, but Taiwan reporting identifies her as Malaysian. The new products are already represented in MuseBooks as well.

### Cited Findings

- Rakuten’s Taiwan Kobo shop lists **《PUBLIC PRIVATE-Mier性感寫真集》** as a digital EPUB3 fixed-format product from 拾捌寫真製作所, dated **2026-07-29**, with product number **7020081020013**; it credits Mier (`@medea0212`) as model. [Kobo/Rakuten Taiwan listing](https://www.rakuten.com.tw/shop/kobo/product/c8f22bf6-5516-372f-898b-1cc41b6d2214/)
- EBC’s profile identifies Mier/米兒 as a Malaysian model; Yahoo Taiwan likewise describes her as a Malaysian internet personality. [EBC News](https://news.ebc.net.tw/news/world/175502); [Yahoo Taiwan](https://tw.news.yahoo.com/%E5%A4%A7%E9%A6%AC%E7%B6%B2%E7%B4%85%E6%9B%AC%E8%BE%A3%E7%85%A7%E4%BD%9C%E9%A2%A8%E6%8E%80%E8%AD%B0-ig%E7%8B%82%E8%A2%AB%E9%97%9C%E4%BA%8C%E7%99%BE%E8%90%AC%E4%BA%BA%E6%B0%A3%E6%9A%B4%E8%B7%8C-112513040.html)
- The public MuseBooks `Mier` query returns **《PUBLIC PRIVATE-Mier性感寫真集》** and **《無聲凝視-Mier性感寫真集》** among eight digital-title records. [MuseBooks live query](https://musebooks.my/v1/books?q=Mier)

### Inferences

- Local sale and publication are not sufficient to classify an overseas creator as a Taiwan influencer. If the catalog’s future scope explicitly includes overseas influencers published in Taiwan, Mier’s records can be considered under that broader scope; under the current Taiwan-creator request, exclude.

### Gaps

- The user’s stated scope has not been broadened to overseas creators merely marketed by Taiwanese publishers.

## Other recent digital hits screened in this pass

### Takeaway

Search results also surfaced a TAKA ebook and several recently indexed titles already cataloged or not sufficiently connected to a Taiwan creator. None was proposed as a new addition.

### Cited Findings

- Google Play describes **《TAKA：深夜名堂男子寫真（數位特別版）》** as a September 2026 ebook by 台灣角川 with **146 pages** and says the featured TAKA is a Japanese internet personality; the MuseBooks result checked in this pass contains TAKA’s physical edition. [Google Play TAKA ebook](https://play.google.com/store/books/details/%E6%B7%B1%E5%A4%9C%E5%90%8D%E5%A0%82_TAKA_%E6%B7%B1%E5%A4%9C%E5%90%8D%E5%A0%82%E7%94%B7%E5%AD%90%E5%AF%AB%E7%9C%9F_%E6%95%B8%E4%BD%8D%E7%89%B9%E5%88%A5%E7%89%88?id=Cf4OEgAAQBAJ); [MuseBooks TAKA work](https://musebooks.my/books/work-tw-32d4b8a05027619bf9fb19ff)
- The **彭彭** ebook **《彭然心動：彭彭寫真〖電子書祕藏版〗》** is a known round-2 addition with EISBN **9786264448314** and should not be re-added. [Books.com product](https://www.books.com.tw/products/E050359832); [round-2 report](../../reports/Taiwan%20influencer%20photobook%20leads%202.md)
- **《心動蕾達：夏蕾寫真》** is already represented as a digital edition alongside its physical edition in local catalog/API checks documented in round 5; it is not a new ebook candidate. [round-5 digital research](../Taiwan%20influencer%20photobook%20leads%205/digital_taiwan.md); [Google Play product](https://play.google.com/store/books/details/%E5%A4%8F%E8%95%BE_%E5%BF%83%E5%8B%95%E8%95%BE%E9%81%94_%E5%A4%8F%E8%95%BE%E5%AF%AB%E7%9C%9F?id=nS8PEgAAQBAJ)

### Inferences

- Round-2 and round-5 notes plus current live API checks avoid repeating already completed additions. TAKA’s ebook is a distinct digital edition but the product itself calls the model Japanese, so it does not meet the current Taiwan-creator filter.

### Gaps

- This was a targeted indexed-retailer search, not a complete crawl of every Taiwan ebook platform or creator storefront. No new qualifying missing edition is claimed from this pass.
