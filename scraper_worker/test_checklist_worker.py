import unittest
from unittest.mock import patch

import catalog_worker

from catalog_worker import (
    build_terms,
    configure_juicy_ocr_cache,
    extract_announced_total,
    extract_composition,
    extract_jyutoku_composition_images,
    extract_juicy_preview_cards,
    juicy_card_classification,
    juicy_ocr_results,
    juicy_ocr_text_for_image,
    record_juicy_ocr_observation,
    juicy_lingerie_parallel_from_color,
    juicy_archive_urls,
    juicy_article_matches,
    juicy_related_index_urls,
)


class FakeLocator:
    def __init__(self, text):
        self.text = text

    def inner_text(self):
        return self.text


class FakeJuicyPage:
    def __init__(self, text, images):
        self.text = text
        self.images = images

    def locator(self, _selector):
        return FakeLocator(self.text)

    def eval_on_selector_all(self, _selector, _script):
        return self.images


class FakeJyuTokuPage:
    url = "https://jyu-toku.sakura.ne.jp/jyu-toku/hatano23/"

    def __init__(self, images):
        self.images = images

    def eval_on_selector_all(self, _selector, _script):
        return self.images

    def wait_for_timeout(self, _milliseconds):
        return None


class ChecklistWorkerTest(unittest.TestCase):
    def test_cj_composition_keeps_counts_and_sections(self):
        text = """
        商品構成 全178類（予定）
        ◆Regular Card 72種
        ◆Rare Card 38種★
        ・Autograph Card（A）＜3種＞
        ・Sexy Lingerie Bra in Card ＜5種＞
        長浜みつりプロフィール
        """
        items = extract_composition(text, "jyu-toku.sakura.ne.jp")

        self.assertEqual(178, extract_announced_total(text))
        self.assertEqual([72, 38, 3, 5], [item["announcedCount"] for item in items])
        self.assertEqual("Rare Card", items[2]["rarityLabel"])
        self.assertTrue(all(item["entryKind"] == "composition" for item in items))

    def test_jyutoku_composition_image_prefers_full_size_article_asset(self):
        page = FakeJyuTokuPage([
            {
                "originalUrl": "https://jyu-toku.sakura.ne.jp/jyu-toku/wp-content/uploads/2017/06/hatano23-01.jpg",
                "altText": "",
                "linked": True,
                "width": 707,
                "height": 1000,
            },
            {
                "originalUrl": "https://jyu-toku.sakura.ne.jp/jyu-toku/wp-content/uploads/2017/06/hatano23-01-212x300.jpg",
                "altText": "",
                "linked": False,
                "width": 212,
                "height": 300,
            },
            {
                "originalUrl": "https://jyu-toku.sakura.ne.jp/jyu-toku/wp-content/uploads/2017/06/logo1.png",
                "altText": "JYUTOKU logo",
                "linked": False,
                "width": 200,
                "height": 70,
            },
        ])

        images = extract_jyutoku_composition_images(page)

        self.assertEqual(1, len(images))
        self.assertEqual(
            "https://jyu-toku.sakura.ne.jp/jyu-toku/wp-content/uploads/2017/06/hatano23-01.jpg",
            images[0]["originalUrl"],
        )
        self.assertEqual(707, images[0]["width"])
        self.assertEqual(1000, images[0]["height"])

    def test_hits_composition_does_not_parse_navigation_years(self):
        text = """
        NBA 2018/2019 カード
        全127種類（予定）
        ?Regular Card（レギュラーカード）：81種類
        ?Super Rare Card
        ・Autograph Card（直筆サインカード）：3種類
        ※種類数、商品仕様は変更になる場合があります。
        MLB 2026カード
        """
        items = extract_composition(text, "www.target.co.jp")

        self.assertEqual(127, extract_announced_total(text))
        self.assertEqual(2, len(items))
        self.assertEqual("Regular Card（レギュラーカード）", items[0]["title"])
        self.assertEqual(3, items[1]["announcedCount"])

    def test_cj_one_of_one_group_uses_design_count_after_label(self):
        text = """
        商品構成 全155種類（予定）
        ◆1of1 Card 13種★
        ・Brassiere Hook in Card＜8種＞
        プロフィール
        """

        items = extract_composition(text, "www.target.co.jp")

        self.assertEqual("1of1 Card", items[0]["title"])
        self.assertEqual(13, items[0]["announcedCount"])

    def test_juicy_print_run_is_not_mistaken_for_design_count(self):
        text = """
        <Collect All 332 Cards>
        [SPECIAL INSERT CARDS]
        ● Base Autograph Set: 8 cards
        Type A [Limited to 250] 4種類 [各250枚限定]
        Type B [Limited to 200] 4種類 [各200枚限定]
        ※パックには332種類のカードがランダムに入っています。
        """
        items = extract_composition(text, "juicy-honey.blog.jp")

        self.assertEqual(332, extract_announced_total(text))
        self.assertEqual([8, 4, 4], [item["announcedCount"] for item in items])
        self.assertEqual("Base Autograph Set", items[1]["rarityLabel"])

    def test_build_terms_adds_model_name_from_subtitle(self):
        terms = build_terms({"subtitle": "岸明日香 ～OTONA KAWAII～", "volume": 1})
        self.assertIn("岸明日香", terms)
        self.assertIn("vol.1", terms)

    def test_juicy_volume_matching_accepts_full_width_text(self):
        terms = build_terms({"title": "JUICY HONEY Collection Cards Vol. 28", "volume": 28})

        self.assertTrue(juicy_article_matches("ＪＵＩＣＹ ＨＯＮＥＹ ＶＯＬ．２８ レアカード", terms))
        self.assertFalse(juicy_article_matches("JUICY HONEY Vol. 280 rare cards", terms))
        self.assertFalse(juicy_article_matches("JUICY HONEY Vol. 29 rare cards", terms))

    def test_juicy_archive_search_spans_release_month(self):
        urls = juicy_archive_urls("2014-10-12")

        self.assertEqual(7, len(urls))
        self.assertIn("https://juicy-honey.blog.jp/archives/2014-10.html", urls)
        self.assertEqual("https://juicy-honey.blog.jp/archives/2014-07.html", urls[0])
        self.assertEqual("https://juicy-honey.blog.jp/archives/2015-01.html", urls[-1])

    def test_juicy_volume_search_uses_official_tag_before_archives(self):
        terms = build_terms({"title": "JUICY HONEY Collection Cards Vol. 28", "volume": 28})
        urls = juicy_related_index_urls(terms, "2014-10-12")

        self.assertEqual("https://juicy-honey.blog.jp/tag/jh28", urls[0])

    def test_juicy_preview_filter_keeps_cards_and_rejects_product_art(self):
        images = [
            {
                "imageUrl": "https://livedoor.blogimg.jp/juicy_honey_card/imgs/b/6/card.jpg",
                "altText": "hybs1",
                "context": "ブラストラップカードを公開！全て1of1です。",
                "localContext": "ブラストラップカードを公開！全て1of1です。",
                "width": 300,
                "height": 400,
            },
            {
                "imageUrl": "https://livedoor.blogimg.jp/juicy_honey_card/imgs/f/2/flyer.jpg",
                "altText": "JH28flyer A4",
                "context": "ブラストラップカードを公開！フライヤー画像です。",
                "width": 600,
                "height": 800,
            },
            {
                "imageUrl": "https://livedoor.blogimg.jp/juicy_honey_card/imgs/e/1/event.jpg",
                "altText": "写真 (14)",
                "context": "秋葉原で発売記念イベントを開催しました。",
                "width": 600,
                "height": 800,
            },
        ]

        items = extract_juicy_preview_cards(FakeJuicyPage("Vol.28 preview", images))

        self.assertEqual(1, len(items))
        self.assertEqual("Bra strap", items[0]["rarityLabel"])
        self.assertEqual("Bra strap official preview 1", items[0]["title"])

    def test_juicy_image_ocr_classifies_plus_27_card_labels(self):
        cases = (
            ("AUTO GRAPH TYPE B", "Base Autograph", "autograph", "Type B", True, False),
            ("JUICY BUNNY GIRL", "Honey Costume", "costume_relic", "Type A", False, True),
            ("HONEY LINGERIE TYPE A", "Honey Lingerie", "lingerie_relic", "Type A", False, True),
            ("HONEY LINGERIE TYPE B", "Honey Lingerie", "lingerie_relic", "Type B", False, True),
            ("HONEY STOCKINGS AUTO PARALLEL", "Honey Stockings Autograph", "stockings", "", True, True),
            ("The Juicy Honey model signature RUT TYPER", "Base Autograph", "autograph", "Type B", True, False),
            ("Juicy H el sigratur RUT TYPER", "Base Autograph", "autograph", "Type B", True, False),
            ("The Juicy Honey model sigratur TYPE E", "Base Autograph", "autograph", "Type B", True, False),
            ("AIRI KIJIMA JUIC UNNY BUNNY GIRL", "Honey Costume", "costume_relic", "Type A", False, True),
            ("SUZU HONJO HONEY NEGLI GEE", "Honey Costume", "costume_relic", "Type B", False, True),
            ("SUZUME MINO BRASSIERE ONEY INGERIE", "Honey Lingerie", "lingerie_relic", "", False, True),
        )

        for raw_text, rarity, card_type, parallel, autograph, relic in cases:
            with self.subTest(raw_text=raw_text):
                result = juicy_card_classification(raw_text)
                self.assertEqual(rarity, result["rarityLabel"])
                self.assertEqual(card_type, result["cardType"])
                self.assertEqual(parallel, result["parallelType"])
                self.assertEqual(autograph, result["isAutograph"])
                self.assertEqual(relic, result["isRelic"])

    def test_juicy_classifier_covers_deluxe_luxury_and_anniversary_types(self):
        cases = (
            ("CANDY HONEY AUTOGRAPH #20", "candy_honey_autograph", "#20"),
            ("CLEAR VIEW AUTOGRAPH GOLD", "clear_view_autograph", "Gold"),
            ("AUTOGRAPHED BIG LINGERIE", "autographed_big_lingerie", ""),
            ("CHIN SPOT 1 OF 1", "chin_spot", "1 of 1"),
            ("NIPPLE SEAL", "nipple_seal", ""),
            ("HONEY MONO KINI", "monokini_relic", ""),
            ("PREMIUM 10 SUNSET", "premium_10_sunset", ""),
            ("SLEEPING BEUTY AUTOGRAPH", "sleeping_beauty_autograph", ""),
            ("MOMENT AUTOGRAPH PINK", "moment_autograph", "Pink"),
            ("JUICY EYES AUTOGRAPH GREEN", "honey_eyes_autograph", "Green"),
            ("SIREN SERENADE", "siren_serenade", ""),
            ("CHOUCHOU CARD", "chouchou", ""),
            ("STAR ART OF HONEY FOIL AUTOGRAPH", "juicy_star_art_of_honey_foil_autograph", ""),
            ("HONEY FEET AUTOGRAPH GOLD", "honey_feet_autograph", "Gold"),
            ("GILDED GRACE AUTOGRAPH BLACK 1 OF 1", "gilded_grace_autograph", "Black"),
            ("BOOKLET 20TH VINGT ETOILES", "vingt_etoiles_booklet", ""),
            ("AUTOGRAPHED BASKETBALL BIG PATCH", "autographed_basketball_big_patch", ""),
        )

        for raw_text, type_key, parallel in cases:
            with self.subTest(raw_text=raw_text):
                result = juicy_card_classification(raw_text)
                self.assertEqual(type_key, result["cardTypeKey"])
                self.assertEqual(parallel, result["parallelType"])

    def test_juicy_persisted_ocr_cache_is_reused_and_reclassified(self):
        image_url = "https://livedoor.blogimg.jp/juicy_honey_card/imgs/a/b/card.jpg"
        configure_juicy_ocr_cache([
            {
                "imageUrl": image_url,
                "ocrText": "HONEY FEET AUTOGRAPH PINK",
                "ocrConfidence": 0.93,
                "status": "completed",
            }
        ])

        ocr_text, confidence = juicy_ocr_text_for_image(image_url)
        classification = juicy_card_classification(ocr_text)
        record_juicy_ocr_observation(image_url, ocr_text, confidence, classification)
        results = juicy_ocr_results()

        self.assertEqual(1, len(results))
        self.assertTrue(results[0]["cacheHit"])
        self.assertEqual("honey_feet_autograph", results[0]["cardTypeKey"])
        self.assertEqual("Pink", results[0]["parallelType"])
        configure_juicy_ocr_cache([])

    def test_juicy_lingerie_color_fallback_is_conservative(self):
        import cv2
        import numpy as np

        def card_with_label_color(bgr):
            image = np.full((100, 200, 3), 210, dtype=np.uint8)
            image[18:68, 100:192] = bgr
            return image

        self.assertEqual(
            "Type A",
            juicy_lingerie_parallel_from_color(card_with_label_color((0, 120, 240))),
        )
        self.assertEqual(
            "Type B",
            juicy_lingerie_parallel_from_color(card_with_label_color((40, 180, 40))),
        )
        self.assertEqual(
            "",
            juicy_lingerie_parallel_from_color(card_with_label_color((160, 160, 160))),
        )

        ambiguous = card_with_label_color((0, 120, 240))
        ambiguous[18:68, 146:192] = (40, 180, 40)
        self.assertEqual("", juicy_lingerie_parallel_from_color(ambiguous))

    def test_juicy_preview_uses_each_image_ocr_and_excludes_flyer(self):
        base_url = "https://livedoor.blogimg.jp/juicy_honey_card/imgs/a/b/"
        images = [
            {
                "imageUrl": base_url + "flyer.jpg",
                "altText": "Fly_27_plus_page-0001",
                "context": "Autograph cards available",
                "localContext": "",
                "ocrText": "JUICY HONEY PLUS 27 6 CARDS PER PACK",
                "ocrConfidence": 0.98,
                "width": 600,
                "height": 800,
            },
            {
                "imageUrl": base_url + "auto.jpg",
                "altText": "IMG_5008",
                "context": "Autograph cards available",
                "localContext": "",
                "ocrText": "AUTO GRAPH TYPE B",
                "ocrConfidence": 0.94,
                "width": 600,
                "height": 800,
            },
            {
                "imageUrl": base_url + "bunny.jpg",
                "altText": "IMG_5007",
                "context": "Autograph cards available",
                "localContext": "",
                "ocrText": "JUICY BUNNY GIRL",
                "ocrConfidence": 0.91,
                "width": 600,
                "height": 800,
            },
            {
                "imageUrl": base_url + "lingerie-a.jpg",
                "altText": "IMG_5006",
                "context": "Autograph cards available",
                "localContext": "",
                "ocrText": "HONEY LINGERIE TYPE A",
                "ocrConfidence": 0.96,
                "width": 800,
                "height": 600,
            },
            {
                "imageUrl": base_url + "lingerie-b.jpg",
                "altText": "IMG_5005",
                "context": "Autograph cards available",
                "localContext": "",
                "ocrText": "HONEY LINGERIE TYPE B",
                "ocrConfidence": 0.95,
                "width": 800,
                "height": 600,
            },
        ]

        items = extract_juicy_preview_cards(
            FakeJuicyPage("all card fronts and backs", images)
        )

        self.assertEqual(4, len(items))
        self.assertEqual(
            ["Base Autograph", "Honey Costume", "Honey Lingerie", "Honey Lingerie"],
            [item["rarityLabel"] for item in items],
        )
        self.assertEqual(["Type B", "Type A", "Type A", "Type B"], [item["parallelType"] for item in items])
        self.assertEqual([True, False, False, False], [item["isAutograph"] for item in items])
        self.assertTrue(all("image OCR" in item["description"] for item in items))

    def test_juicy_preview_runs_ocr_even_when_caption_can_classify_image(self):
        image_url = "https://livedoor.blogimg.jp/juicy_honey_card/imgs/a/b/captioned.jpg"
        images = [
            {
                "imageUrl": image_url,
                "altText": "IMG_5008",
                "context": "Autograph cards available",
                "localContext": "",
                "width": 600,
                "height": 800,
            }
        ]
        calls = []

        def fake_ocr(url):
            calls.append(url)
            return "HONEY LINGERIE TYPE A", 0.94

        with patch.object(catalog_worker, "juicy_ocr_text_for_image", side_effect=fake_ocr):
            items = extract_juicy_preview_cards(FakeJuicyPage("Vol. 28 preview", images))

        self.assertEqual([image_url], calls)
        self.assertEqual(1, len(items))
        self.assertEqual("Honey Lingerie", items[0]["rarityLabel"])
        self.assertIn("image OCR", items[0]["description"])

    def test_juicy_mixed_article_routes_each_image_to_only_its_ocr_series(self):
        article_title = "【JH PLUS #9】【#14】【LX2018】【DX2021】 rare cards"
        base_url = "https://livedoor.blogimg.jp/juicy_honey_card/imgs/a/b/"
        ocr_texts = (
            "BIG2 HONEY LINGERIE JUICY HONEY PLUS #09",
            "ART OF HONEY JUICY HONEY COLLECTION CARDS PLUS H09",
            "ART OF HONEY JUICY HONEY COLLECTION CARDS PLUS *14",
            "THE LUXURY EDITION 2018 HONEY LINGERIE TYPE A",
            "THE LUXURY EDITION 2018 HONEY LINGERIE TYPE B",
            "JUICY HONEY THE DELUXE 2021 ANDY HONEY",
            "JUICY HONEY THE DELUXE 2021 CANDY HONEY",
        )
        images = [
            {
                "imageUrl": f"{base_url}card-{index}.jpg",
                "altText": f"IMG_{index}",
                "context": "Official rare cards",
                "localContext": "",
                "ocrText": ocr_text,
                "ocrConfidence": 0.95,
                "width": 600,
                "height": 800,
            }
            for index, ocr_text in enumerate(ocr_texts, start=1)
        ]
        expected_counts = {
            "plus:9": 2,
            "plus:14": 1,
            "luxury:2018:": 2,
            "the-deluxe:2021:": 2,
        }

        all_urls = set()
        for identity, expected_count in expected_counts.items():
            stats = {}
            items = extract_juicy_preview_cards(
                FakeJuicyPage(article_title, images),
                expected_series_identity=identity,
                routing_stats=stats,
            )
            self.assertEqual(expected_count, len(items), msg=identity)
            self.assertEqual(expected_count, stats["matched"], msg=identity)
            urls = {item["imageUrl"] for item in items}
            self.assertTrue(all_urls.isdisjoint(urls), msg=identity)
            all_urls.update(urls)

        self.assertEqual(7, len(all_urls))

    def test_juicy_single_series_article_appends_unlabelled_card_images(self):
        image_url = "https://livedoor.blogimg.jp/juicy_honey_card/imgs/a/b/art-card.jpg"
        images = [{
            "imageUrl": image_url,
            "altText": "IMG_1234",
            "context": "Official card preview",
            "localContext": "",
            "ocrText": "ART OF HONEY JUICY HONEY PLUS #31",
            "ocrConfidence": 0.94,
            "width": 600,
            "height": 800,
        }]

        first = extract_juicy_preview_cards(
            FakeJuicyPage("JUICY HONEY PLUS #31 official cards", images),
            expected_series_identity="plus:31",
        )
        second = extract_juicy_preview_cards(
            FakeJuicyPage("JUICY HONEY PLUS #31 official cards", images),
            expected_series_identity="plus:31",
        )

        self.assertEqual(1, len(first))
        self.assertEqual(first[0]["cardCode"], second[0]["cardCode"])
        self.assertTrue(first[0]["cardCode"].startswith("ARCHIVE-"))

    def test_juicy_complete_gallery_keeps_cards_after_ocr_budget(self):
        base_url = "https://livedoor.blogimg.jp/juicy_honey_card/imgs/a/b/"
        images = [
            {
                "imageUrl": f"{base_url}card-{index}.jpg",
                "altText": f"IMG_{index}",
                "context": "",
                "localContext": "",
                "width": 600,
                "height": 800,
            }
            for index in range(1, 5)
        ]
        calls = []

        def fake_ocr(image_url):
            calls.append(image_url)
            return "", 0.0

        with patch.object(catalog_worker, "JUICY_OCR_MAX_IMAGES", 2), patch.object(
            catalog_worker, "juicy_ocr_text_for_image", side_effect=fake_ocr
        ):
            items = extract_juicy_preview_cards(
                FakeJuicyPage("all card fronts and backs", images)
            )

        self.assertEqual(4, len(items))
        self.assertEqual(2, len(calls))

    def test_juicy_persisted_ocr_does_not_consume_budget_or_run_again(self):
        base_url = "https://livedoor.blogimg.jp/juicy_honey_card/imgs/a/b/"
        cached_url = base_url + "cached.jpg"
        fresh_url = base_url + "fresh.jpg"
        configure_juicy_ocr_cache([
            {
                "imageUrl": cached_url,
                "ocrText": "HONEY LINGERIE TYPE A",
                "ocrConfidence": 0.93,
                "status": "completed",
            }
        ])
        images = [
            {
                "imageUrl": cached_url,
                "altText": "IMG_1",
                "context": "",
                "localContext": "",
                "width": 600,
                "height": 800,
            },
            {
                "imageUrl": fresh_url,
                "altText": "IMG_2",
                "context": "",
                "localContext": "",
                "width": 600,
                "height": 800,
            },
        ]
        calls = []

        def fake_ocr(image_url):
            calls.append(image_url)
            return "AUTO GRAPH TYPE B", 0.91

        with patch.object(catalog_worker, "JUICY_OCR_MAX_IMAGES", 1), patch.object(
            catalog_worker, "juicy_ocr_text_for_image", side_effect=fake_ocr
        ):
            stats = {}
            items = extract_juicy_preview_cards(
                FakeJuicyPage("all card fronts and backs", images),
                routing_stats=stats,
            )

        self.assertEqual([fresh_url], calls)
        self.assertEqual(2, len(items))
        self.assertEqual(1, stats["ocrProcessed"])
        self.assertEqual(1, stats["ocrCacheHits"])
        configure_juicy_ocr_cache([])


if __name__ == "__main__":
    unittest.main()
