# Model name-search bucket audit — 2026-10-20

The Japan model importer attached store search results for a model's name to that model. For short names (もも, 葵, 七海, こころ, しおり, しずく…) the results include many other people whose names contain the search term, so their books were credited to the wrong model.

Method (read-only, `go run ./cmd/people-merge -audit <file>`): every featured credit is compared with the credited model's recorded names (main name, original/English name, person_aliases).

- **named** — a name of the model of three or more characters stands alone in the title.
- **weak** — only a short name or single-word alias stands alone (`もも from 63ANGEL`, `Nanami「Departure」`).
- **other** — the model's short name appears only inside a longer name: a surname before it (藤田**もも**, 美ノ嶋**めぐり**) or a hiragana given name after it (**七海**ひより). That longer name is proposed as the credit.
- **absent** — no recorded name appears in the title.

Proposals are limited to Japanese titles (containing kana). Eight Taiwanese hits were false positives where a Chinese phrase precedes the name (戀上冰熙, 神系甜心夏晴) and are excluded; proposals whose prefix before the name is longer than three characters are dropped for the same reason. Names continued by a kanji were extended (日向葵 → 日向葵衣, 沢尻もも → 沢尻もも美); 写真集 suffixes were not.

Draft corrections: [model-bucket-corrections-draft.json](model-bucket-corrections-draft.json) — **413 works** across 11 models. Each entry matches one work by exact title and exact current credit list, removes the bucket model's names from that list and inserts the person named in the title (or keeps the existing credit if that person is already listed, e.g. 乙陽葵). Nothing has been applied.

## Models with books naming someone else

| Model | named | weak | absent | corrections | People named in the titles |
|---|---:|---:|---:|---:|---|
| 葵 | 0 | 25 | 17 | 107 | 日向葵衣 ×25, 乙陽葵 ×21, 溝端葵 ×17, 川口葵 ×8, 葵りんご ×6, 中村葵 ×4, 葵ゆりか ×4, 中城葵 ×3, 古賀葵 ×2, 葵うたの ×2, 葵さくら ×2, 坂田葵 ×2, 夏葵 ×2, 木村葵 ×2, 瀬名葵 ×2, 葵りん ×2, 中瀬葵 ×1, 須賀葵 ×1, 翔野葵 ×1 |
| 浅野こころ | 0 | 1 | 22 | 89 | 篠崎こころ ×55, 晴こころ ×14, 須羽こころ ×7, 綾瀬こころ ×5, 結月こころ ×4, 雫こころ ×3, 河合こころ ×1 |
| もも | 0 | 48 | 12 | 66 | 月野もも ×11, 椎名もも ×11, 赤羽もも ×9, 鈴もも ×5, 藤田もも ×5, 入來もも ×3, 大河もも ×2, 桜井もも ×2, 小鳥遊もも ×2, 井上もも ×2, 水瀬もも ×2, 竹本もも ×1, 坂田もも ×1, 沢尻もも美 ×1, 塩見もも ×1, 天使もも ×1, 田中もも ×1, 福田もも ×1, 宮花もも ×1, 泉もも ×1, 神崎もも ×1, 高橋もも ×1, 麻倉もも ×1 |
| 兒玉七海 | 1 | 16 | 2 | 51 | 萌木七海 ×15, 戸咲七海 ×9, 七海りお ×5, 七海ひより ×4, 七海れん ×2, 小山七海 ×2, 吉沢七海 ×2, 山下七海 ×2, 大空七海 ×2, 七海まり ×2, 佐藤七海 ×1, 七海さき ×1, 佐々木七海 ×1, 咲良七海 ×1, 七海かのん ×1, 浅井七海 ×1 |
| 神木麗 | 1 | 2 | 10 | 46 | 池本しおり ×27, 真木しおり ×13, 柚木しおり ×2, 本多しおり ×1, 根岸しおり ×1, 徳永しおり ×1, 葉月しおり ×1 |
| 初美沙希 | 3 | 0 | 1 | 19 | 太田しずく ×11, 花井しずく ×4, 朝日しずく ×3, 真野しずく ×1 |
| めぐり | 6 | 6 | 0 | 18 | 美ノ嶋めぐり ×17, 南国めぐり ×1 |
| 寧々 | 0 | 0 | 2 | 6 | 伊藤寧々 ×4, 古園井寧々 ×1, 吉高寧々 ×1 |
| つぼみ | 0 | 4 | 0 | 5 | 望月つぼみ ×5 |
| 金子みひろ | 0 | 5 | 0 | 4 | 金谷みひろ ×4 |
| ティア | 0 | 0 | 0 | 2 | 綾瀬ティア ×2 |

Notable: 浅野こころ has no title naming 浅野こころ or 歌野こころ; most of her credited books are 篠崎こころ (55) and 晴こころ (14). 葵 is not one model at all: 日向葵衣, 乙陽葵, 溝端葵, 川口葵 and others.

## Left for manual review

These works stay credited as they are. A title with only a short alias or no name at all cannot show which person it features; check the store page before changing them.

### 葵 (59)

*no model name in title* (17):

- 100万ドルの笑顔の先に―
- 2026年も、バズ確定！～prologue～
- Run and Run
- Straight Story
- sabra net girls マシェバラ スペシャル4 [sabra net e-Book]
- 【デジタル限定】南早紀フォトブック「ダレニモミセナイ。〜僕の南（ヒカリ）〜」
- あおいままで。
- あおいろ
- この街で
- その顔、好きになれって言ってる？～prologue～
- ねぇ、ドウキしちゃう？
- もうひとつの、あおいままで。
- ガチでブレイクする5秒前
- グラドル名鑑2021　（グラドル名鑑）
- ソルエト目線
- 夏はすぐそこ！うたのとオレンジジュース。
- 彼女には何かがある。

*non-Japanese title (phrase before name)* (17):

- A Beautiful Mallow 権藤葵1 [sabra net e-Book]
- A Beautiful Mallow 権藤葵2 [sabra net e-Book]
- A Beautiful Mallow 権藤葵DX [sabra net e-Book]
- PROTO STAR 佐藤葵 complete1　（PROTO STAR）
- PROTO STAR 佐藤葵 complete2　（PROTO STAR）
- PROTO STAR 佐藤葵 vol.1　（PROTO STAR）
- PROTO STAR 佐藤葵 vol.2　（PROTO STAR）
- PROTO STAR 佐藤葵 vol.3　（PROTO STAR）
- PROTO STAR 佐藤葵 vol.4　（PROTO STAR）
- 宮瀬葵菜 Lucu Masterpiece#018
- 宮瀬葵菜「Cute」　（Bamboo e-Book）
- 宮瀬葵菜「Lucu」　（Idol Line）
- 宮瀬葵菜「Pretty」　（Bamboo e-Book）
- 宮瀬葵菜「Pure」　（Bamboo e-Book）
- 日向葵衣 idolpost ORANGEJUICE Extra edition 168Photos
- 日向葵衣SpecialEdition　（萌得）
- 駒木根葵汰 1st写真集 Key

*only a short alias in title* (25):

- FLASHデジタル写真集　ミスFLASH2025　葵成美　（FLASHデジタル写真集）
- FLASHデジタル写真集　葵成美　和らぎのなかで　（FLASHデジタル写真集）
- Girl’s Room 家で撮っていいですか？　No.007葵井えりか Special Edition　（Girl's Labo）
- LOVEPOP デラックス　葵井みずほ　001　（ラビリンス）
- LOVEPOP デラックス　葵井みずほ　002　（ラビリンス）
- LOVEPOP デラックス　葵井みずほ　003　（ラビリンス）
- LOVEPOP デラックス　葵井みずほ　005　（ラビリンス）
- 【デジタル限定】ポラリス　葵音琴
- 【デジタル限定】葵成美写真集「Run and Run」
- 【電子版限定特典画像付き】伊原　葵１ｓｔ写真集　Ｎｏｏｎ
- グラビアポーズ360° 特別編 No.021 葵井えりか part1　（ガールズ☆ラボ!）
- グラビアポーズ360° 特別編 No.048 葵井えりか part2　（ガールズ☆ラボ!）
- セーラー服の天使達Angelic Sailor-Girls　葵野まりん
- ビキニ☆ガールズ！ 葵井えりか1　（絶対ビキニ宣言）
- ビキニ☆ガールズ！ 葵井えりか2　（絶対ビキニ宣言）
- ポラリス 葵音琴
- 熟女TV Gravure　葵百合香 Vol.01　（ラビリンス）
- 熟女TV Gravure　葵百合香 Vol.02　（ラビリンス）
- 熟女TV Gravure　葵百合香 Vol.03　（ラビリンス）
- 熟女TV Gravure　葵百合香 Vol.04　（ラビリンス）
- 葵 成美 ふっくら谷間にピットイン
- 葵成美 くびれエンジェル 40PhotosDX[sabra net e-Book]
- 葵成美　天使に恋して　ＦＲＩＤＡＹデジタル写真集　（ＦＲＩＤＡＹデジタル写真集）
- 葵成美「日本一ＳＥＸＹなレースクイーン」　ＦＲＩＤＡＹデジタル写真集　（ＦＲＩＤＡＹデジタル写真集）
- 週刊GIRLS-PEDIA135 葵成美

### もも (60)

*no model name in title* (12):

- 12th Birthday Party!
- QUEEN OF BURLESQUE
- pop'n sexy pure girl
- 『こういうのがいい』コラボグラビア
- いつもかわいい　〜旬なインフルエンサーたちの日常グラビア写真集〜　（ENTAMEデジタル写真集）
- その距離は
- ひとりでできるもんっ！
- むにむにむ
- スペシャルな彼女
- バスト100cmグラドルサミットＢ７　爆乳山脈
- ヒミツの居場所
- 素顔のキミに癒やされたい

*only a short alias in title* (48):

- 1st Digital Photo Book とももともも　（Platinum Digital）
- [ハレム]もも from 63ANGEL（旧バーレスク東京）「無邪気な猫のように」【美麗版32P】
- [ハレム]もも from 63ANGEL（旧バーレスク東京）「無邪気な猫のように」【美麗版32P】　（ハレム）
- 【デジタル限定 YJ PHOTO BOOK】さくらもも(Toi Toi Toi)写真集「Be Naked, Be Alright!」
- 【デジタル限定 YJ PHOTO BOOK】たゆらもも写真集「ずっと待ってた、はじめまして。」
- 【デジタル限定 YJ PHOTO BOOK】ももいろクローバーZ写真集「12th Birthday Party!」
- 【デジタル限定 YJ PHOTO BOOK】もも（バーレスク東京）「はじめての、ももいろ」
- 【デジタル限定 YJ PHOTO BOOK】もも（バーレスク東京）写真集「pop'n sexy pure girl」
- 【デジタル限定 YJ PHOTO BOOK】もも（バーレスク東京）写真集「『こういうのがいい』コラボグラビア」
- 【デジタル限定】さくらもも写真集「夢で終わらせない」
- 【デジタル限定】もものすけ写真集
- 【デジタル限定】もものすけ写真集　（Ｇテレデジタル！）
- 【デジタル限定】もものすけ写真集「むにむにむ」
- 【デジタル限定】もも写真集「もしもショーガールの超絶人気美女とこっそりお泊まりデートできたら究極の優越感にひたれる件。　もも編」
- 【デジタル限定】もも＆神山みれい写真集（バーレスク東京）
- 【デジタル限定】もも＆神山みれい写真集（バーレスク東京）　（Ｇテレデジタル！）
- 【デジタル限定】もも（バーレスク東京）写真集
- 【デジタル限定】もも（バーレスク東京）写真集　（Ｇテレデジタル！）
- 【デジタル限定】もも（バーレスク東京）写真集「QUEEN OF BURLESQUE」
- 【デジタル限定】もも（バーレスク東京）写真集「ひとりでできるもんっ！」
- 【デジタル限定】もも（バーレスク東京）写真集「スペシャルな彼女」
- 【デジタル限定】もも（バーレスク東京）写真集「ヒミツの居場所」
- さんぽガール　みついももかさん　千鳥ヶ淵編　（さんぽガール）
- さんぽガール　みついももかさん　新宿御苑編　（さんぽガール）
- しとうももデジタル写真集　ももびより
- とももとももが水着でコスプレ　ヤンマガデジタル写真集　（ヤンマガデジタル写真集）
- とももとももが水着でロードバイク　ヤンマガデジタル写真集　（ヤンマガデジタル写真集）
- とれたてももちゃん！
- はじめての、ももいろ
- もしもショーガールの超絶人気美女とこっそりお泊まりデートできたら究極の優越感にひたれる件。 もも編
- もも　Peach Time
- もも「24 hours」【ヤングチャンピオンデジグラ】
- もも「24 hours」【ヤングチャンピオンデジグラ】　（ヤングチャンピオンデジグラ）
- もも「もも、夜に攻める！」【ヤングチャンピオンデジグラ】
- もも「もも、夜に攻める！」【ヤングチャンピオンデジグラ】　（ヤングチャンピオンデジグラ）
- ももいろクローバーZ 公式 パンフレット「ももいろクリスマス2014　さいたまスーパーアリーナ大会〜Shining Snow Story〜」
- ももせもも「巨乳転生」　（アイドルニッポン）
- もものすけ「Iカップのぬくもり」ＳＰＡ！デジタル写真集　（ＳＰＡ！ＢＯＯＫＳ）
- もも写真集 One and Only
- もも写真集 One and Only　（GUIDEWORKS DIGITAL PHOTO BOOK）
- … 8 more

### 浅野こころ (23)

*no model name in title* (22):

- 16歳の大冒険
- GIRLS graph. 002　（GIRLS graph.）
- GIRLS graph. 003　（GIRLS graph.）
- GIRLS graph.　（GIRLS graph.）
- PPE ヤングガンガンデジタル限定写真集「Biggest Surprise」　（ヤングガンガン特別編集）
- PPE ヤングガンガンデジタル限定写真集「Never Ending Halloween Night」　（ヤングガンガン特別編集）
- PPEデジタル写真集　虎GIRLSパーティー　（ヤングキング）
- 【アニマルデジタルフォトブック】PPエンタープライズ「Perfect Pretty Engaging Mermaid」　（アニマルデジタルフォトブック）
- 【アニマルデジタルフォトブック】PPエンタープライズ「あつまれ！PPEパーティー」　（アニマルデジタルフォトブック）
- 【デジタル限定 YJ PHOTO BOOK】YJ×ホロライブ写真集「ホロ爛漫」
- 【デジタル限定】PPEデジタル写真集 夏カノコレクション　（ヤングキング）
- 【デジタル限定】PPE写真集「ALL DAY, HALLOWEENTIME.」
- 【大増量60ページ】PPE　PPE Halloween Party！
- あぶない巨乳GAL大集合Vol.03
- ふぁんたじーをあげるよ!!
- マシュマロ
- ミスマガジン２０２５　【増量版　全１００Ｐ】ヤンマガアザーっす！＜ＹＭ２０２５年４０号４１号未公開カット＞　ヤンマガデジタル写真集　（ヤンマガデジタル写真集）
- 可愛さが強い
- 夢のような
- 家出少女
- 晴れもよう
- 溺れる

*only a short alias in title* (1):

- ほんとのところ ほんとのこころ？

### 兒玉七海 (29)

*non-Japanese title (phrase before name)* (11):

- A-collection 萌木七海（１）
- A-collection 萌木七海（３）
- Complete　戸咲七海 2 写真集
- Complete　戸咲七海　写真集
- 『聖女伝説』　夏江美優・戸咲七海　写真集
- 『聖女伝説』　夏江美優・戸咲七海　写真集　Vol.02
- 佐々木七海「Refresh」　（RANKU）
- 女子校生 萌木七海 Complete vol.1
- 萌木七海 NEXTCANVAS
- 萌木七海-Passion Fruits-
- 萌木七海-Water Venus-

*only a short alias in title* (16):

- Nanami「Departure」　（Idol Line）
- Nanami「触れてもいいですか？」　（Idol Line）
- VIVID GIRL 七海 Chapter1　（VIVID GIRL）
- VIVID GIRL 七海 Chapter2　（VIVID GIRL）
- VIVID GIRL 七海 Chapter3　（VIVID GIRL）
- VIVID GIRL 七海 Chapter4　（VIVID GIRL）
- VIVID GIRL 七海 Omnibus　VIVID GIRL NANAMI Omnibus　（VIVID GIRL）
- VIVID GIRL 七海 前編　（VIVID GIRL）
- VIVID GIRL 七海 後編　（VIVID GIRL）
- 『はじめての…』　七海マキ　デジタル写真集
- 『挑発』　七海マキ　デジタル写真集
- 『転調』　七海マキ　デジタル写真集
- グラビアポーズ360° 特別編 No.026 七海　（ガールズ☆ラボ!）
- ビキニ☆ガールズ！ 七海　（絶対ビキニ宣言）
- 七海「パイレーツ」　（Bamboo e-Book）
- 七海「海の女王」　（Bamboo e-Book）

*no model name in title* (2):

- 会えるAI美少女 未来　（ピュアマーメイド）
- 新潟からきました！

### 神木麗 (12)

*no model name in title* (10):

- F2.8標準ズーム1本勝負 Canon RF28-70mm F2.8 IS STMはここまで撮れる WMC003（Wrist Machine日本語版別冊）
- SUPER☆GiRLS写真集「STARS！！！！」
- Summer of Love
- sabra net girls マシェバラ スペシャル4 [sabra net e-Book]
- 【デジタル限定】プラチナムガール写真集「Summer of Love」
- なつのね
- ふわりふわり
- ミニグラ界の新星　（Platinum Digital）
- 愛はどこにあるの？　（月刊デジタルファクトリー）
- 無防備

*only a short alias in title* (2):

- しおり、まっさら
- ゆきみしおり「#YOYOYO 1st photo book」（AiconiQ digital photo book）　（AiconiQ）

### めぐり (6)

*only a short alias in title* (6):

- お願い抱いて… 寂しさから夫によく似た義弟とイケナイ関係になってしまった爆乳未亡人 めぐり 爆ヤバDIGITAL写真集　（爆ヤバDIGITAL写真集）
- めぐりSpecialEdition　（萌得）
- ㊙蔵出し　The Sexy　めぐりPetitBEST　（ギリ見せ☆）
- 先生・・・集中できません・・・ めぐり
- 爆乳人妻の浮気現場 夫だけでは物足りない欲求不満のめぐりさん めぐり 激ヤバ写真集　（激ヤバ写真集）
- 隣の爆乳お姉さんに逆ナンされて… めぐり 濃厚グラビアPHOTOBOOK　（濃厚グラビアPHOTOBOOK）

### 初美沙希 (1)

*no model name in title* (1):

- ミスマガジン２０２５　【増量版　全１００Ｐ】ヤンマガアザーっす！＜ＹＭ２０２５年４０号４１号未公開カット＞　ヤンマガデジタル写真集　（ヤンマガデジタル写真集）

### 寧々 (4)

*no model name in title* (2):

- COLOR　marvelousII　デジタル写真集
- 坂道を駆け抜けて

*non-Japanese title (phrase before name)* (2):

- NUDE NEXT vol.03 吉高寧々
- 吉高寧々　Love Hotel

### つぼみ (4)

*only a short alias in title* (4):

- 400枚収録　つぼみ　Complete Box　（ラビリンス）
- ULTIMATE BEST つぼみ　（ULTIMATE BEST）
- 濃厚SHOT つぼみ　（濃厚SHOT）
- 花ひらく つぼみ写真集

### 金子みひろ (5)

*only a short alias in title* (5):

- ボクの彼女はみひろ　「とっても気持ちいいデート」
- ボクの彼女はみひろ　「ふたりに良いことあるように」
- ボクの彼女はみひろ　「スカイツリーを見にいこう！」
- ボクの彼女はみひろ　「隅田川をのんびりさんぽ！！」
- 完璧美女な奥様の秘密 みひろ 濃厚グラビアPHOTOBOOK　（濃厚グラビアPHOTOBOOK）

## Importer fix

`scraper/prepare_model_home_import.py` credits every search hit to the searched model. Before crediting, require that the product title contains one of the model's names of three or more characters (or its full name), and reject hits where a short name appears with a surname before it or a hiragana given name after it — the same rules as the audit's `classifyTitle` in `backend/cmd/people-merge/audit.go`. Unmatched hits should go to a review queue instead of the catalog.
