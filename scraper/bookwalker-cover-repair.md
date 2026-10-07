# BOOK☆WALKER cover repair — 2026-10-07

Seven imported digital editions used BOOK☆WALKER social-preview `_mask.jpg` images with an embedded age warning. The selected product page's `#app[data-page]` payload publishes the actual cover in `props.productData.product_image`.

Replaced the covers for 惑之庭, 羽の魅, 溺愛羽庭, 雨停 羽庭, Girl Friend女友寫真-子婷, 鄭家純(雞排妹) 愛是神馬寫真, and Dragon Beauties 小映. Each source cover was visually inspected, uploaded using its content hash, and verified with HTTP 200 and a matching SHA-256 from the public image host. Database updates were atomic and limited to edition cover fields and matching work/listing cover references. All seven edition replacements passed database readback.

The scraper now prefers the selected product's published cover over the social preview and search thumbnail. Selection requires the exact product ID and official image host. The importer rejects known warning images before consulting its cache; the downloader also rejects them on each redirect. It does not infer cover URLs by removing `_mask`.

The source URLs, edition/work identities, old and replacement image URLs, storage keys, byte counts, and hashes are recorded in [bookwalker-cover-repair.json](bookwalker-cover-repair.json). Historical research records describe the original imports; this report supersedes their masked-cover decisions.
