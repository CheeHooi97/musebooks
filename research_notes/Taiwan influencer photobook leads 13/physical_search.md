# Taiwan physical photobook scan — round 13

## Takeaway

Seven 蘋蘋澎澎 photobook works were added to MuseBooks with R2-backed covers: her debut, Vol.2–Vol.6, and the extra title. The creator's own website provides the historical photobook archive and cover art. For Vol.2–Vol.6 and the extra volume, the database leaves ISBN, publication date, and pagination empty because the archive does not state those details.

## Creator and title evidence

- 蘋蘋澎澎's [official site](https://pinpinponpon.tw/) calls her a “Twins Creator from Taiwan,” describes the creator's content, and reports 120 萬+ total followers. Its `Photobooks` section calls the collection eight main books plus one extra and lists Vol.1–Vol.6 with title-specific cover images. Its FAQ says the series has been published and that some early books are sold out.
- The official site identifies the extra title `家有雙生女友` and its cover. The six numbered covers were downloaded from `https://pinpinponpon.tw/images/vol2.jpg` through `vol6.jpg`; the extra cover is `https://pinpinponpon.tw/images/sp.jpg`. Each image was visually inspected against its title before upload.
- The [official Vol.1 video](https://www.youtube.com/watch?v=BekoJfovM6g), published 2022-07-10, calls `蘋什麼這麼可愛` her first personal photobook and states 180 pages. The linked [Shopee item](https://shopee.tw/Twitch%E5%9C%96%E5%A5%87%E7%9B%B4%E6%92%AD%E4%B8%BB%E2%80%9C%E8%98%8B%E8%98%8B%E6%BE%8E%E6%BE%8E%E2%80%9C%E5%B9%B3%E7%94%9F%E7%AC%AC%E4%B8%80%E6%9C%AC%E5%AF%AB%E7%9C%9F%E9%9B%86%E3%80%8E%E8%98%8B%E4%BB%80%E9%BA%BC%E9%80%99%E9%BA%BC%E5%8F%AF%E6%84%9B%E3%80%8F-i.4548848.19756951264) names the same book, labels the edition general, and shows publication year 2022; it is a resale listing and is sold out.
- `一蘋的海岸線` also appeared in the creator's [2023 calendar preorder questionnaire](https://www.surveycake.com/s/g8pkL), which says she planned to publish a first physical calendar under that title. The official photobook archive now labels it as Vol.2. It is recorded under the creator's current official photobook-series classification; the separate calendar bundle is not entered as an additional work.

## Database and R2 result

The first import batch validated and committed one work/edition. A second batch validated and committed six works/editions. Seven exact-title API readbacks returned the intended work and a physical edition. Each signed media URL returned HTTP 200; the downloaded bytes matched the R2 object's SHA-256:

| Title | Work ID | R2 SHA-256 |
| --- | --- | --- |
| 蘋什麼這麼可愛 | `work-tw-2d56003a1afc4b209934df4a` | `c928983c8fc24385ec5e0bd40409dddbe50363028f66076a3d5dbaac1369b389` |
| 一蘋的海岸線 | `work-tw-82a1cfe69cb047da988a3ab3` | `5652eace9fa488d29b864139933fcd90fa178dd58a33863c0f6b64e59e0ac2ab` |
| 雪妹的交換日記 | `work-tw-24137561d93d4d3ab4b028da` | `9a7c8a8e6cbf6832e4011c2412f41b5440fbe9dffa83e4aaed704a7fadafec88` |
| 轉生到蘋行世界 | `work-tw-58275e7fb6d64d2e96d2eee0` | `66c568825fe2d0da8e9fc600c237ab51fe79dcf19da6e55ebf915974ba082a1c` |
| 讓世界和蘋的純欲姊姊 | `work-tw-c2b41a72b0c44e47bb76a510` | `2705ad315b40498efd5212ea1651fffa7879e17b9510ca0ca384de4cc3a2b9ff` |
| 純・欲双子 | `work-tw-e037cf16ad8441c0be28d3e2` | `f1af5889d5d4bdd1027545c815b1910899c33f9372a7fa582f3326f2fc0e12d4` |
| 家有雙生女友 | `work-tw-a15b0d82bac4439dab64233a` | `e801013d95d11fe50b6d8170a881bff9d913f5e58526c6a7b0789ba4c83204cc` |

## Holds and gaps

- The creator's 2026 `純·欲姊姊特休中` store product already exists in MuseBooks. Do not duplicate it.
- The official shop has a newer preorder, `澎然心動的蘋率：30赫茲`, at [product detail 2706145](https://pinpinponpon627.waca.tw/product/detail/2706145). It states 128 pages and mentions digital files as a preorder add-on, but this pass did not confirm the final cover. Do not create a separate digital edition from bundled files without a distinct product record.
- `《韓你菲》` remains unimported pending a direct seller/product URL and a final-cover match. The available [FTV announcement](https://finance.ftvnews.com.tw/news/detail/2026831W0260) establishes the announced book, but not a verified product/cover pair.

This is a targeted creator-series update, not a complete census of Taiwan photobooks.
