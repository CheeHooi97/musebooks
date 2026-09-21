import io
import json
import sys
import unittest
from unittest.mock import patch

import catalog_worker


class CatalogWorkerDispatchTests(unittest.TestCase):
    def test_browser_shutdown_errors_do_not_replace_a_scrape_result(self):
        class Resource:
            def close(self):
                raise RuntimeError("context canceled")

        catalog_worker.close_quietly(Resource())

    def test_navigation_retries_once_after_a_transient_failure(self):
        class Page:
            def __init__(self):
                self.attempts = 0

            def goto(self, *_args, **_kwargs):
                self.attempts += 1
                if self.attempts == 1:
                    raise RuntimeError("temporary navigation failure")

            def wait_for_timeout(self, _milliseconds):
                pass

        page = Page()
        catalog_worker.goto(page, "https://example.com", 0)
        self.assertEqual(2, page.attempts)

    def test_navigation_can_use_commit_and_a_ready_selector(self):
        class Page:
            def __init__(self):
                self.goto_options = None
                self.selector_options = None

            def goto(self, _url, **options):
                self.goto_options = options

            def wait_for_selector(self, selector, **options):
                self.selector_options = (selector, options)

            def wait_for_timeout(self, _milliseconds):
                pass

        page = Page()
        catalog_worker.goto(
            page,
            "https://example.com",
            wait_ms=0,
            wait_until="commit",
            ready_selector="a[href]",
        )

        self.assertEqual("commit", page.goto_options["wait_until"])
        self.assertEqual(
            ("a[href]", {"state": "attached", "timeout": 15000}),
            page.selector_options,
        )

    def test_colored_cloakbrowser_update_notice_is_filtered(self):
        target = io.StringIO()
        filtered = catalog_worker.FilteredStderr(target)
        filtered.write(
            "\x1b[33mUpdate available: cloakbrowser 0.5.3 → 0.5.6. "
            "Run: pip install --upgrade cloakbrowser\x1b[0m\n"
        )
        filtered.write("navigation failed\n")
        filtered.flush()

        self.assertEqual("navigation failed\n", target.getvalue())

    def test_page_link_parser_reads_nested_image_and_relative_url(self):
        parser = catalog_worker.PageLinkParser("https://gain-p.jp/user_data/title_list")
        parser.feed(
            '<a href="/products/list?category_id=844" title="Series">'
            '<img src="cover.jpg" alt="Vol.25"> 岸明日香</a>'
        )

        self.assertEqual(
            [{
                "href": "https://gain-p.jp/products/list?category_id=844",
                "text": "岸明日香",
                "title": "Series",
                "alt": "Vol.25",
            }],
            parser.items,
        )

    def test_cj_discovery_uses_wordpress_batches_without_browser_navigation(self):
        posts = [
            {
                "link": "https://jyu-toku.sakura.ne.jp/jyu-toku/hatano140/",
                "title": {
                    "rendered": "\u6ce2\u591a\u91ce\u7d50\u8863 CJ SEXY CARD SERIES VOL.140"
                },
                "content": {
                    "rendered": (
                        "<p>\u30bf\u30a4\u30c8\u30eb\uff1a \uff5eOnly Yui\uff5e<br>"
                        "\u767a\u58f2\u65e5\uff1a2026\u5e7410\u670831\u65e5</p>"
                        "<h4>\u6ce2\u591a\u91ce\u7d50\u8863 \u30d7\u30ed\u30d5\u30a3\u30fc\u30eb</h4>"
                        "<p>\u751f\u5e74\u6708\u65e5\uff1a1988\u5e745\u670824\u65e5</p>"
                    )
                },
            },
            {
                "link": "https://jyu-toku.sakura.ne.jp/jyu-toku/other-product/",
                "title": {"rendered": "JYUTOKU other product"},
                "content": {"rendered": "<p>2026\u5e741\u67081\u65e5</p>"},
            },
        ]
        responses = [
            ([{"id": 4, "count": 2}], {}),
            (posts, {"X-WP-TotalPages": "1"}),
        ]

        with patch.object(
            catalog_worker, "fetch_json_document", side_effect=responses
        ) as fetch_json, patch.object(
            catalog_worker,
            "discover_cj_browser",
            side_effect=AssertionError("browser fallback must not run"),
        ) as browser_fallback:
            releases = catalog_worker.discover_cj(object(), max_pages=1)

        self.assertEqual(1, len(releases))
        self.assertEqual(140, releases[0]["volume"])
        self.assertEqual("2026-10-31", releases[0]["releaseDate"])
        self.assertEqual("\u6ce2\u591a\u91ce\u7d50\u8863", releases[0]["modelName"])
        self.assertEqual("1988-05-24", releases[0]["models"][0]["birthDate"])
        self.assertIn("per_page=6", fetch_json.call_args_list[1].args[0])
        browser_fallback.assert_not_called()

    def test_cj_discovery_falls_back_to_browser_when_wordpress_is_unavailable(self):
        expected = [{"publisherKey": "cj-sexy", "volume": 140}]
        browser = object()
        with patch.object(
            catalog_worker,
            "discover_cj_wordpress",
            side_effect=RuntimeError("API unavailable"),
        ), patch.object(
            catalog_worker, "discover_cj_browser", return_value=expected
        ) as fallback:
            releases = catalog_worker.discover_cj(browser, max_pages=20)

        self.assertEqual(expected, releases)
        fallback.assert_called_once_with(browser, 20, False)

    def test_media_operation_keeps_flat_adapter_contract(self):
        expected = {
            "sourceUrl": "https://example.com/release",
            "pageUrl": "https://example.com/release/1",
            "items": [],
            "warnings": [],
        }
        with patch.object(catalog_worker, "media_for_release", return_value=expected):
            result = catalog_worker.execute_request(
                object(),
                {
                    "operation": "media",
                    "sourceUrl": "https://example.com/release",
                    "maxImages": 5,
                },
            )

        self.assertEqual(expected, result)
        self.assertNotIn("releases", result)

    def test_execute_request_ignores_ocr_cache_for_all_publishers(self):
        catalog_worker.configure_juicy_ocr_cache([
            {
                "imageUrl": "https://example.com/card.jpg",
                "ocrText": "HONEY LINGERIE TYPE A",
                "ocrConfidence": 0.98,
                "status": "completed",
            }
        ])
        expected = {"items": [], "warnings": []}
        try:
            with patch.object(catalog_worker, "media_for_release", return_value=expected):
                result = catalog_worker.execute_request(
                    object(),
                    {
                        "operation": "media",
                        "sourceUrl": "https://example.com/release",
                        "imageOcrCache": [
                            {
                                "imageUrl": "https://example.com/card.jpg",
                                "ocrText": "HONEY LINGERIE TYPE A",
                                "status": "completed",
                            }
                        ],
                    },
                )

            self.assertEqual(expected, result)
            self.assertEqual([], catalog_worker.juicy_ocr_results())
        finally:
            catalog_worker.configure_juicy_ocr_cache([])

    def test_checklist_operation_keeps_flat_adapter_contract(self):
        expected = {
            "sourceUrl": "https://example.com/release",
            "pageUrl": "https://example.com/release/1",
            "items": [],
            "checklistImages": [],
            "announcedTotal": 0,
            "warnings": [],
        }
        with patch.object(catalog_worker, "checklist_for_release", return_value=expected):
            result = catalog_worker.execute_request(
                object(),
                {
                    "operation": "checklist",
                    "sourceUrl": "https://example.com/release",
                },
            )

        self.assertEqual(expected, result)
        self.assertNotIn("releases", result)

    def test_suruga_card_row_parses_numeric_and_insert_card_codes(self):
        release = {"volume": 23}
        regular = catalog_worker.parse_suruga_card_row(
            {
                "href": "https://www.suruga-ya.jp/product/detail/GL511757",
                "text": "23[レギュラーカード]：波多野結衣/CJ SEXY CARD SERIES VOL.23",
                "imageUrl": "https://cdn.suruga-ya.jp/database/pics_webp/game/GL511757.jpg.webp",
                "altText": "23 レギュラーカード",
            },
            release,
        )
        insert = catalog_worker.parse_suruga_card_row(
            {
                "href": "https://www.suruga-ya.jp/product/detail/GU713120",
                "text": "BCO-2[ビッグコスチュームカード]：CJ SEXY CARD SERIES VOL.23",
                "imageUrl": "https://cdn.suruga-ya.jp/database/pics_webp/game/GU713120.jpg.webp",
            },
            release,
        )

        self.assertEqual("23", regular["cardCode"])
        self.assertEqual("BCO-2", insert["cardCode"])
        self.assertEqual("trusted_retailer", regular["sourceConfidence"])
        self.assertTrue(regular["imageUrl"].startswith("https://cdn.suruga-ya.jp/"))

    def test_suruga_card_row_accepts_current_subtitle_naming(self):
        item = catalog_worker.parse_suruga_card_row(
            {
                "href": "https://www.suruga-ya.jp/product/detail/G3918815",
                "text": "04[レギュラーカード]：桜空もも/レギュラーカード/桜空もも オフィシャルカードコレクション ももいろキャンバス",
                "imageUrl": "https://cdn.suruga-ya.jp/database/pics_webp/game/G3918815.jpg.webp",
            },
            {"volume": 45, "subtitle": "ももいろキャンバス"},
        )

        self.assertIsNotNone(item)
        self.assertEqual("04", item["cardCode"])
        self.assertEqual("trusted_retailer", item["sourceConfidence"])

    def test_suruga_product_image_url_lowercases_case_sensitive_management_code(self):
        self.assertEqual(
            "https://cdn.suruga-ya.jp/database/pics_webp/game/g3918815.jpg.webp",
            catalog_worker.suruga_product_image_url(
                "https://www.suruga-ya.jp/product/detail/G3918815"
            ),
        )

    def test_suruga_card_row_normalizes_uppercase_cdn_image_path(self):
        item = catalog_worker.parse_suruga_card_row(
            {
                "href": "https://www.suruga-ya.jp/product/detail/G3918815",
                "text": "04[レギュラーカード]：桜空もも/CJ SEXY CARD SERIES VOL.45",
                "imageUrl": "https://cdn.suruga-ya.jp/database/pics_webp/game/G3918815.jpg.webp",
            },
            {"volume": 45},
        )

        self.assertEqual(
            "https://cdn.suruga-ya.jp/database/pics_webp/game/g3918815.jpg.webp",
            item["imageUrl"],
        )

    def test_suruga_card_row_replaces_lazy_data_uri_placeholder(self):
        item = catalog_worker.parse_suruga_card_row(
            {
                "href": "https://www.suruga-ya.jp/product/detail/G3918815",
                "text": "04[CJ SEXY CARD]：桜空もも/CJ SEXY CARD SERIES VOL.45",
                "imageUrl": "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP",
            },
            {"volume": 45},
        )

        self.assertEqual(
            "https://cdn.suruga-ya.jp/database/pics_webp/game/g3918815.jpg.webp",
            item["imageUrl"],
        )

    def test_suruga_queries_include_release_subtitle(self):
        queries = catalog_worker.suruga_card_queries(
            {"volume": 45, "subtitle": "ももいろキャンバス"}
        )

        self.assertEqual("CJ SEXY CARD SERIES VOL.45", queries[0])
        self.assertIn("ももいろキャンバス", queries)
        self.assertNotIn("CJ ももいろキャンバス", queries)

    def test_suruga_queries_derive_model_from_official_release_url(self):
        release = {
            "volume": 45,
            "sourceUrl": "https://jyu-toku.sakura.ne.jp/jyu-toku/%e6%a1%9c%e7%a9%ba%e3%82%82%e3%82%82%e3%80%80cj-sexy-card-series-vol-45/",
        }

        queries = catalog_worker.suruga_card_queries(release)

        self.assertIn("桜空もも オフィシャルカードコレクション", queries)
        self.assertIn("桜空もも", queries)
        row = {
            "href": "https://www.suruga-ya.jp/product/other/G3918815",
            "text": "04[レギュラーカード]：桜空もも/レギュラーカード/桜空もも オフィシャルカードコレクション ももいろキャンバス",
        }
        self.assertIsNotNone(catalog_worker.parse_suruga_card_row(row, release))

    def test_suruga_queries_combine_model_and_collection_subtitle(self):
        release = {
            "volume": 45,
            "subtitle": "ももいろキャンバス",
            "sourceUrl": "https://jyu-toku.sakura.ne.jp/jyu-toku/%e6%a1%9c%e7%a9%ba%e3%82%82%e3%82%82%e3%80%80cj-sexy-card-series-vol-45/",
        }

        queries = catalog_worker.suruga_card_queries(release)

        self.assertIn("桜空もも ももいろキャンバス", queries)
        self.assertLess(
            queries.index("桜空もも ももいろキャンバス"),
            queries.index("桜空もも"),
        )

    def test_suruga_index_fallback_urls_keep_suruga_as_the_card_source(self):
        search_url = catalog_worker.suruga_index_search_url(
            "桜空もも ももいろキャンバス", 2
        )
        image_url = catalog_worker.suruga_product_image_url(
            "https://www.suruga-ya.jp/product/detail/G3918815"
        )

        self.assertIn("search.yahoo.co.jp/search?", search_url)
        self.assertIn("site%3Asuruga-ya.jp%2Fproduct", search_url)
        self.assertIn("b=11", search_url)
        self.assertEqual(
            "https://cdn.suruga-ya.jp/database/pics_webp/game/g3918815.jpg.webp",
            image_url,
        )

    def test_suruga_row_derives_image_from_product_management_code(self):
        item = catalog_worker.parse_suruga_card_row(
            {
                "href": "https://www.suruga-ya.jp/product/detail/G3918815",
                "text": "04[レギュラーカード]：桜空もも/桜空もも オフィシャルカードコレクション ももいろキャンバス",
            },
            {"volume": 45, "subtitle": "ももいろキャンバス"},
        )

        self.assertEqual(
            "https://cdn.suruga-ya.jp/database/pics_webp/game/g3918815.jpg.webp",
            item["imageUrl"],
        )

    def test_suruga_cloudflare_page_uses_public_index_fallback(self):
        class Body:
            def inner_text(self, timeout=None):
                return "Performing security verification by Cloudflare"

        class Page:
            url = ""

            def title(self):
                return "Just a moment..."

            def locator(self, selector):
                return Body()

            def eval_on_selector_all(self, selector, script):
                if "search.yahoo.co.jp" not in self.url:
                    return []
                return [{
                    "href": "https://www.suruga-ya.jp/product/detail/G3918815",
                    "text": "04[レギュラーカード]：桜空もも オフィシャルカードコレクション ももいろキャンバス",
                    "altText": "04 レギュラーカード",
                }]

        page = Page()

        def fake_goto(target, url, **kwargs):
            target.url = url

        with (
            patch.object(catalog_worker, "new_page", return_value=page),
            patch.object(catalog_worker, "goto", side_effect=fake_goto),
            patch.object(catalog_worker, "close_quietly"),
        ):
            items, warnings = catalog_worker.scrape_suruga_cj_cards(
                object(),
                {
                    "volume": 45,
                    "subtitle": "ももいろキャンバス",
                    "sourceUrl": "https://jyu-toku.sakura.ne.jp/jyu-toku/%e6%a1%9c%e7%a9%ba%e3%82%82%e3%82%82%e3%80%80cj-sexy-card-series-vol-45/",
                },
                10,
            )

        self.assertEqual(["04"], [item["cardCode"] for item in items])
        self.assertTrue(any("blocked by Cloudflare" in item for item in warnings))

    def test_cj_card_media_uses_suruga_without_opening_official_page(self):
        expected = [{
            "cardCode": "04",
            "entryKind": "card",
            "imageUrl": "https://www.suruga-ya.jp/product/detail/G3918815",
        }]

        class Browser:
            def new_page(self):
                raise AssertionError("CJ cardMedia should not open the official page")

        with patch.object(
            catalog_worker,
            "scrape_suruga_cj_cards",
            return_value=(expected, ["Suruga-ya individual card listings found: 1"]),
        ) as scrape:
            result = catalog_worker.checklist_for_release(
                Browser(),
                {
                    "publisherKey": "cj-sexy",
                    "cardMedia": True,
                    "sourceUrl": "https://jyu-toku.sakura.ne.jp/jyu-toku/example-vol-45/",
                    "title": "CJ SEXY CARD SERIES Vol. 45",
                    "subtitle": "ももいろキャンバス",
                    "volume": 45,
                },
                100,
            )

        scrape.assert_called_once()
        self.assertEqual(expected, result["items"])
        self.assertEqual([], result["checklistImages"])

    def test_cj_composition_media_uses_official_page(self):
        class Locator:
            def inner_text(self):
                return "CJ SEXY CARD SERIES VOL.45"

        class Page:
            url = "https://jyu-toku.sakura.ne.jp/jyu-toku/example-vol-45/"

            def __init__(self):
                self.goto_options = []
                self.selector_options = []

            def goto(self, *args, **kwargs):
                self.goto_options.append(kwargs)

            def wait_for_selector(self, *args, **kwargs):
                self.selector_options.append((args, kwargs))

            def wait_for_timeout(self, *args, **kwargs):
                return None

            def locator(self, *args, **kwargs):
                return Locator()

        class Browser:
            def __init__(self):
                self.page = Page()

            def new_page(self):
                return self.page

        official_sheet = [{
            "originalUrl": "https://jyu-toku.sakura.ne.jp/wp-content/uploads/vol45.jpg",
            "altText": "CJ SEXY Vol.45 composition",
            "width": 1200,
            "height": 800,
        }]
        browser = Browser()
        with patch.object(catalog_worker, "resolve_release_page", return_value=True), \
                patch.object(catalog_worker, "extract_composition", return_value=[]), \
                patch.object(catalog_worker, "extract_jyutoku_composition_images", return_value=official_sheet), \
                patch.object(catalog_worker, "scrape_suruga_cj_cards") as scrape:
            result = catalog_worker.checklist_for_release(
                browser,
                {
                    "publisherKey": "cj-sexy",
                    "sourceUrl": "https://jyu-toku.sakura.ne.jp/jyu-toku/example-vol-45/",
                    "title": "CJ SEXY CARD SERIES Vol. 45",
                    "subtitle": "ももいろキャンバス",
                    "volume": 45,
                },
                100,
            )

        scrape.assert_not_called()
        self.assertEqual(official_sheet, result["checklistImages"])
        self.assertEqual("commit", browser.page.goto_options[0]["wait_until"])
        self.assertEqual("body", browser.page.selector_options[0][0][0])

    def test_suruga_card_row_rejects_a_different_volume(self):
        item = catalog_worker.parse_suruga_card_row(
            {
                "href": "https://www.suruga-ya.jp/product/detail/GL960405",
                "text": "23[レギュラーカード]：JULIA/CJ SEXY CARD SERIES VOL.100",
                "imageUrl": "https://cdn.suruga-ya.jp/database/pics_webp/game/GL960405.jpg.webp",
            },
            {"volume": 23},
        )

        self.assertIsNone(item)

    def test_discovery_operation_keeps_discovery_contract(self):
        release = {"publisherKey": "woohoo", "title": "WooHoo Girls Vol. 1"}
        with patch.object(
            catalog_worker,
            "discover_releases",
            return_value=("woohoo", [release], []),
        ):
            result = catalog_worker.execute_request(
                object(),
                {"operation": "discovery", "publisher": "woohoo"},
            )

        self.assertEqual("woohoo", result["publisherKey"])
        self.assertEqual([release], result["releases"])

    def test_formosa_candidate_requires_a_card_product_and_normalizes_identity(self):
        release = catalog_worker.formosa_release_candidate(
            "https://www.formosadreamers.com/products/formosa-sexy-vol4",
            "Formosa Sexy 年度女孩卡 Vol.4",
            "Formosa Sexy 年度女孩卡 Vol.4 NT$1,280",
        )

        self.assertIsNotNone(release)
        self.assertEqual("formosa-sexy", release["publisherKey"])
        self.assertEqual("formosa-sexy-vol-4", release["seriesKey"] + "-vol-" + str(release["volume"]))
        self.assertEqual("Formosa Sexy 年度女孩卡 Vol. 4", release["title"])
        self.assertEqual("suggestive_age_gated", release["contentRating"])
        self.assertIsNone(
            catalog_worker.formosa_release_candidate(
                "https://www.formosadreamers.com/products/formosa-sexy-vol4",
                "S9 FORMOSA SEXY 女孩相機背帶",
                "S9 FORMOSA SEXY 女孩相機背帶 NT$400",
            )
        )

    def test_formosa_marketplace_candidate_uses_known_volume_and_source_confidence(self):
        release = catalog_worker.formosa_release_candidate(
            "https://shopee.tw/formosa-sexy-2022",
            "2022 Formosa Sexy 女孩卡",
            "Formosa Sexy 女孩卡 2022",
            known_volume=1,
            source_type="marketplace_listing",
        )

        self.assertIsNotNone(release)
        self.assertEqual("Formosa Sexy 年度女孩卡 Vol. 1", release["title"])
        self.assertEqual("shopee-taiwan", release["sourcePlatformKey"])
        self.assertEqual("inferred", release["sourceConfidence"])

    def test_rakuten_candidate_requires_explicit_card_markers(self):
        release = catalog_worker.rakuten_release_candidate(
            catalog_worker.RAKUTEN_GIRLS_RELEASES[0],
            "2020 Rakuten Girls Cards 女孩卡上市。1包五張售價70元。",
        )

        self.assertEqual("rakuten-girls", release["publisherKey"])
        self.assertEqual("year:2020", release["editionKey"])
        self.assertEqual("Rakuten Girls Trading Cards 2020", release["title"])
        self.assertIsNone(
            catalog_worker.rakuten_release_candidate(
                catalog_worker.RAKUTEN_GIRLS_RELEASES[0],
                "Rakuten Girls 活動贈送限量卡片",
            )
        )
        retail_metadata = next(
            item for item in catalog_worker.RAKUTEN_GIRLS_RELEASES if item["year"] == 2025
        )
        retail_release = catalog_worker.rakuten_release_candidate(
            retail_metadata,
            "2025 Rakuten Girls 年度女孩卡-精裝盒 女孩卡",
        )
        self.assertEqual("", retail_release["releaseDate"])

        metadata_2024 = next(
            item for item in catalog_worker.RAKUTEN_GIRLS_RELEASES if item["year"] == 2024
        )
        release_2024 = catalog_worker.rakuten_release_candidate(
            metadata_2024,
            "2024 Rakuten Girls Collection Cards Packs",
        )
        self.assertEqual("1collectibles", release_2024["sourcePlatformKey"])
        self.assertEqual("trusted_retailer", release_2024["sourceConfidence"])

        metadata_2021 = next(
            item for item in catalog_worker.RAKUTEN_GIRLS_RELEASES if item["year"] == 2021
        )
        release_2021 = catalog_worker.rakuten_release_candidate(
            metadata_2021,
            "2021 Rakuten Girls 樂天女孩卡 全套178張",
        )
        self.assertEqual("ruten-taiwan", release_2021["sourcePlatformKey"])
        self.assertEqual("inferred", release_2021["sourceConfidence"])

    def test_taiwan_release_registry_includes_marketplace_backfill_sources(self):
        formosa_urls = {item["sourceUrl"] for item in catalog_worker.FORMOSA_SEXY_KNOWN_PRODUCTS}
        self.assertTrue(any("1collectibles.com/products/2023-24-formosa-sexy" in url for url in formosa_urls))
        self.assertTrue(any("jjcs.com.tw/products/tpbl-2025-formosa" in url for url in formosa_urls))
        self.assertEqual(
            {1, 2, 3, 4},
            {item["volume"] for item in catalog_worker.FORMOSA_SEXY_KNOWN_PRODUCTS},
        )
        self.assertEqual(
            {2020, 2021, 2022, 2023, 2024, 2025},
            {item["year"] for item in catalog_worker.RAKUTEN_GIRLS_RELEASES},
        )

    def test_all_publisher_discovery_includes_taiwan_publishers(self):
        formosa = {"publisherKey": "formosa-sexy", "title": "Formosa Sexy 年度女孩卡 Vol. 4"}
        rakuten = {"publisherKey": "rakuten-girls", "title": "Rakuten Girls Trading Cards 2020"}
        with patch.object(catalog_worker, "discover_woohoo", return_value=[]), \
                patch.object(catalog_worker, "discover_hits", return_value=[]), \
                patch.object(catalog_worker, "discover_tic", return_value=[]), \
                patch.object(catalog_worker, "discover_cj", return_value=[]), \
                patch.object(catalog_worker, "discover_juicy", return_value=[]), \
                patch.object(catalog_worker, "discover_mint", return_value=[]), \
                patch.object(catalog_worker, "discover_formosa", return_value=[formosa]) as formosa_scrape, \
                patch.object(catalog_worker, "discover_rakuten_girls", return_value=[rakuten]) as rakuten_scrape:
            publisher, releases, warnings = catalog_worker.discover_releases(
                object(), {"allPublishers": True, "maxPages": 1}
            )

        self.assertEqual("all", publisher)
        self.assertEqual([formosa, rakuten], releases)
        self.assertEqual([], warnings)
        formosa_scrape.assert_called_once_with(unittest.mock.ANY, 1, source_url="")
        rakuten_scrape.assert_called_once_with(unittest.mock.ANY, 1, source_url="")

    def test_single_publisher_discovery_returns_scrape_error(self):
        with patch.object(
            catalog_worker,
            "discover_woohoo",
            side_effect=RuntimeError("navigation failed"),
        ):
            with self.assertRaisesRegex(
                RuntimeError,
                "woohoo discovery failed: navigation failed",
            ):
                catalog_worker.discover_releases(
                    object(),
                    {"publisher": "woohoo"},
                )

    def test_browser_launch_failure_is_returned_as_an_error(self):
        stdin = io.StringIO(json.dumps({"operation": "discovery", "publisher": "woohoo"}))
        stdout = io.StringIO()
        with patch.object(
            catalog_worker,
            "launch",
            side_effect=RuntimeError("browser unavailable"),
        ), patch.object(sys, "stdin", stdin), patch.object(sys, "stdout", stdout):
            with self.assertRaisesRegex(
                RuntimeError,
                "CloakBrowser launch failed: browser unavailable",
            ):
                catalog_worker.main()

        self.assertEqual("", stdout.getvalue())

    def test_targeted_juicy_discovery_uses_db_source_url_without_archive_scan(self):
        release = {
            "publisherKey": "juicy-honey",
            "title": "JUICY HONEY PLUS #27",
            "sourceUrl": "https://juicy-honey.blog.jp/archives/1082756245.html",
        }
        with patch.object(
            catalog_worker,
            "discover_juicy_target",
            return_value=[release],
        ) as targeted, patch.object(
            catalog_worker,
            "discover_juicy",
            side_effect=AssertionError("targeted discovery must not scan archives"),
        ) as full_scan:
            publisher, releases, warnings = catalog_worker.discover_releases(
                object(),
                {
                    "publisher": "juicy-honey",
                    "releaseSlug": "juicy-honey-juicy-honey-plus-27",
                    "sourceUrl": "https://juicy-honey.blog.jp/archives/1082756245.html",
                },
            )

        self.assertEqual("juicy-honey", publisher)
        self.assertEqual([release], releases)
        self.assertEqual([], warnings)
        targeted.assert_called_once_with(
            unittest.mock.ANY,
            "https://juicy-honey.blog.jp/archives/1082756245.html",
        )
        full_scan.assert_not_called()

    def test_targeted_juicy_discovery_without_db_source_falls_back_to_archive_scan(self):
        release = {
            "publisherKey": "juicy-honey",
            "title": "JUICY HONEY PLUS #29",
            "sourceUrl": "https://juicy-honey.blog.jp/archives/plus-29.html",
        }
        with patch.object(
            catalog_worker,
            "discover_juicy",
            return_value=[release],
        ) as full_scan, patch.object(
            catalog_worker,
            "discover_juicy_target",
            side_effect=AssertionError("a missing catalog row has no target article"),
        ) as targeted:
            publisher, releases, warnings = catalog_worker.discover_releases(
                object(),
                {
                    "publisher": "juicy-honey",
                    "releaseSlug": "juicy-honey-juicy-honey-plus-29",
                },
            )

        self.assertEqual("juicy-honey", publisher)
        self.assertEqual([release], releases)
        self.assertEqual([], warnings)
        full_scan.assert_called_once_with(unittest.mock.ANY, 240, 0, 20, source_url="")
        targeted.assert_not_called()

    def test_targeted_juicy_discovery_uses_direct_article_url_without_release_slug(self):
        source_url = "https://juicy-honey.blog.jp/archives/1077602459.html"
        release = {
            "publisherKey": "juicy-honey",
            "seriesKey": "anniversary",
            "editionKey": "anniversary:15:2020",
            "title": "JUICY HONEY 15TH ANNIVERSARY",
            "sourceUrl": source_url,
        }
        with patch.object(
            catalog_worker,
            "discover_juicy_target",
            return_value=[release],
        ) as targeted, patch.object(
            catalog_worker,
            "discover_juicy",
            side_effect=AssertionError("a direct article URL must not scan monthly archives"),
        ) as full_scan:
            publisher, releases, warnings = catalog_worker.discover_releases(
                object(),
                {
                    "publisher": "juicy-honey",
                    "sourceUrl": source_url,
                    "maxMonths": 1,
                },
            )

        self.assertEqual("juicy-honey", publisher)
        self.assertEqual([release], releases)
        self.assertEqual([], warnings)
        targeted.assert_called_once_with(unittest.mock.ANY, source_url)
        full_scan.assert_not_called()

    def test_juicy_archive_discovery_follows_month_pagination(self):
        archive = "https://juicy-honey.blog.jp/archives/2014-07.html"

        class Page:
            current = ""

        page = Page()
        pages = {
            archive: [
                {"href": archive + "?p=2", "text": "2"},
                {
                    "href": "https://juicy-honey.blog.jp/archives/1000000001.html",
                    "text": "7月12日発売 ジューシーハニー VOL.27",
                },
            ],
            archive + "?p=2": [
                {
                    "href": "https://juicy-honey.blog.jp/archives/1000000002.html",
                    "text": "10月12日発売 ジューシーハニー VOL.28",
                },
            ],
        }

        def navigate(_page, url, **_kwargs):
            _page.current = url

        with patch.object(catalog_worker, "goto", side_effect=navigate), patch.object(
            catalog_worker,
            "links",
            side_effect=lambda current_page: pages[current_page.current],
        ):
            candidates, pages_scanned = catalog_worker.juicy_archive_article_candidates(
                page,
                archive,
                10,
                set(),
            )

        self.assertEqual(2, pages_scanned)
        self.assertEqual(
            [
                "https://juicy-honey.blog.jp/archives/1000000001.html",
                "https://juicy-honey.blog.jp/archives/1000000002.html",
            ],
            [item[0] for item in candidates],
        )

    def test_juicy_archive_discovery_accepts_real_unicode_japanese_titles(self):
        archive = "https://juicy-honey.blog.jp/archives/2025-09.html"

        class Page:
            current = ""

        page = Page()
        pages = {
            archive: [{
                "href": "https://juicy-honey.blog.jp/archives/1082756245.html",
                "text": (
                    "\u30ec\u30a2\u30ab\u30fc\u30c9\u4e00\u6319\u63b2\u8f09 "
                    "8\u670830\u65e5\u767a\u58f2 "
                    "\u30b8\u30e5\u30fc\u30b7\u30fc\u30cf\u30cb\u30fcPLUS#27"
                ),
            }],
        }

        def navigate(_page, url, **_kwargs):
            _page.current = url

        with patch.object(catalog_worker, "goto", side_effect=navigate), patch.object(
            catalog_worker,
            "links",
            side_effect=lambda current_page: pages[current_page.current],
        ):
            candidates, pages_scanned = catalog_worker.juicy_archive_article_candidates(
                page,
                archive,
                10,
                set(),
            )

        self.assertEqual(1, pages_scanned)
        self.assertEqual(
            ["https://juicy-honey.blog.jp/archives/1082756245.html"],
            [item[0] for item in candidates],
        )

    def test_juicy_archive_pagination_rejects_other_months(self):
        archive = "https://juicy-honey.blog.jp/archives/2014-07.html"
        self.assertEqual(
            archive + "?p=2",
            catalog_worker.juicy_archive_pagination_url(archive + "?p=2", archive),
        )
        self.assertEqual(
            "",
            catalog_worker.juicy_archive_pagination_url(
                "https://juicy-honey.blog.jp/archives/2014-08.html?p=2",
                archive,
            ),
        )

    def test_woohoo_candidate_separates_series_name_and_strips_model_date(self):
        release = catalog_worker.candidate(
            "woohoo",
            "商品情報 斎藤恭代 2026年10月10日発売 WooHoo Girls Vol. 24 ～CHURA～",
            "https://gain-p.jp/product/woohoo-24",
            24,
            "2026-10-10",
            "official_release",
            "https://gain-p.jp/user_data/check_list",
        )

        self.assertEqual("～CHURA～", release["title"])
        self.assertEqual("WooHoo Girls Vol. 24", release["subtitle"])
        self.assertEqual("斎藤恭代", release["modelName"])

    def test_woohoo_discovery_hydrates_series_name_from_product_page(self):
        class Body:
            def inner_text(self, **_kwargs):
                return "岸明日香～15th Anniversary～トレーディングカード"

        class Page:
            def __init__(self, title=""):
                self._title = title

            def title(self):
                return self._title

            def locator(self, selector):
                self.assert_body_selector = selector
                return Body()

            def close(self):
                pass

        index_page = Page()
        detail_page = Page("Smile Gain / 岸明日香～15th Anniversary～")
        link = {
            "href": "https://gain-p.jp/products/list?category_id=844",
            "text": "Vol.25 岸明日香 2026年10月24日発売",
            "title": "",
            "alt": "",
        }
        with patch.object(catalog_worker, "new_page", side_effect=[index_page, detail_page]), patch.object(
            catalog_worker,
            "goto",
        ), patch.object(catalog_worker, "links", return_value=[link]):
            releases = catalog_worker.discover_woohoo(object())

        self.assertEqual(1, len(releases))
        self.assertEqual("～15th Anniversary～", releases[0]["title"])
        self.assertEqual("WooHoo Girls Vol. 25", releases[0]["subtitle"])

    def test_woohoo_discovery_uses_http_index_fallback(self):
        class Page:
            def title(self):
                return "Smile Gain / 岸明日香～15th Anniversary～"

            def locator(self, _selector):
                raise RuntimeError("body not needed when title contains the name")

            def close(self):
                pass

        index_page = Page()
        detail_page = Page()
        link = {
            "href": "https://gain-p.jp/products/list?category_id=844",
            "text": "Vol.25 岸明日香 2026年10月24日発売",
            "title": "",
            "alt": "",
        }
        with patch.object(catalog_worker, "new_page", side_effect=[index_page, detail_page]), patch.object(
            catalog_worker,
            "goto",
            side_effect=[RuntimeError("browser index timeout"), None],
        ), patch.object(catalog_worker, "fetch_page_links", return_value=[link]):
            releases = catalog_worker.discover_woohoo(object())

        self.assertEqual(1, len(releases))
        self.assertEqual("～15th Anniversary～", releases[0]["title"])


    def test_woohoo_title_index_volume_is_not_part_of_model_name(self):
        release = catalog_worker.candidate(
            "woohoo",
            "Vol.25 岸明日香 2026年10月24日発売",
            "https://gain-p.jp/products/list?category_id=844",
            25,
            "2026-10-24",
            "official_release",
            "https://gain-p.jp/user_data/check_list",
        )

        self.assertEqual("岸明日香", release["modelName"])

    def test_woohoo_product_page_composition_sheet_is_detected(self):
        class Page:
            def eval_on_selector_all(self, _selector, script):
                if "forEach" in script:
                    return None
                return [{
                    "originalUrl": "https://gain-p.jp/html/template/default/assets/img/top/amano/amano900.jpg",
                    "altText": "",
                    "width": 1200,
                    "height": 800,
                }]

            def wait_for_timeout(self, _milliseconds):
                pass

        images = catalog_worker.extract_woohoo_product_checklist_images(Page())

        self.assertEqual(1, len(images))
        self.assertEqual(
            "https://gain-p.jp/html/template/default/assets/img/top/amano/amano900.jpg",
            images[0]["originalUrl"],
        )

    def test_woohoo_checklist_uses_product_sheet_when_index_has_no_release(self):
        class Locator:
            def inner_text(self):
                return "WooHoo Girls Vol. 23"

        class Page:
            url = "https://gain-p.jp/products/list?category_id=834"

            def goto(self, *_args, **_kwargs):
                pass

            def wait_for_selector(self, *_args, **_kwargs):
                pass

            def wait_for_timeout(self, _milliseconds):
                pass

            def locator(self, _selector):
                return Locator()

        class Browser:
            def new_page(self):
                return Page()

        sheet = [{
            "originalUrl": "https://gain-p.jp/html/template/default/assets/img/top/amano/amano900.jpg",
            "altText": "",
            "width": 1200,
            "height": 800,
        }]
        with patch.object(catalog_worker, "resolve_release_page", return_value=True), \
                patch.object(catalog_worker, "extract_composition", return_value=[]), \
                patch.object(catalog_worker, "resolve_gain_checklist_page", return_value=False), \
                patch.object(catalog_worker, "extract_woohoo_product_checklist_images", return_value=sheet):
            result = catalog_worker.checklist_for_release(
                Browser(),
                {
                    "publisherKey": "woohoo",
                    "sourceUrl": "https://gain-p.jp/products/list?category_id=834",
                    "title": "~FURI FURI~",
                    "subtitle": "WooHoo Girls Vol. 23",
                    "volume": 23,
                },
                100,
            )

        self.assertEqual(sheet, result["checklistImages"])
        self.assertTrue(any("product composition sheet" in warning for warning in result["warnings"]))

    def test_woohoo_historical_checklist_uses_verified_direct_volume_path(self):
        class Page:
            url = "https://gain-p.jp/user_data/check_list"

            def __init__(self):
                self.urls = []

            def goto(self, url, **_kwargs):
                self.urls.append(url)
                self.url = url

            def wait_for_timeout(self, _milliseconds):
                pass

            def eval_on_selector_all(self, _selector, _script):
                return []

        expected_urls = {
            3: "https://gain-p.jp/user_data/fubuki_checklist",
            9: "https://gain-p.jp/user_data/sanada_checklist",
            12: "https://gain-p.jp/user_data/hanai_checklist",
            18: "https://gain-p.jp/user_data/noumi_checklist",
        }
        for volume, expected_url in expected_urls.items():
            with self.subTest(volume=volume):
                page = Page()
                self.assertTrue(
                    catalog_worker.resolve_gain_checklist_page(
                        page,
                        [f"woohoo-girls-vol-{volume}"],
                    )
                )
                self.assertEqual(expected_url, page.urls[-1])

    def test_woohoo_checklist_falls_back_when_release_page_does_not_match(self):
        class Locator:
            def inner_text(self):
                return ""

        class Page:
            url = "https://gain-p.jp/product/old-woohoo-page"

            def goto(self, *_args, **_kwargs):
                pass

            def wait_for_selector(self, *_args, **_kwargs):
                pass

            def wait_for_timeout(self, _milliseconds):
                pass

            def locator(self, _selector):
                return Locator()

        class Browser:
            def new_page(self):
                return Page()

        checklist_images = [{
            "originalUrl": "https://gain-p.jp/html/template/default/assets/img/top/noumi/NM18_CheckList_01.jpg",
            "altText": "",
            "width": 1200,
            "height": 1800,
        }]
        with (
            patch.object(catalog_worker, "resolve_release_page", return_value=False),
            patch.object(catalog_worker, "resolve_gain_checklist_page", return_value=True),
            patch.object(catalog_worker, "extract_checklist_images", return_value=checklist_images),
        ):
            result = catalog_worker.checklist_for_release(
                Browser(),
                {
                    "publisherKey": "woohoo",
                    "sourceUrl": "https://gain-p.jp/product/old-woohoo-page",
                    "title": "WooHoo Girls Vol. 18",
                    "volume": 18,
                },
                100,
            )

        self.assertEqual(checklist_images, result["checklistImages"])
        self.assertEqual([], result["items"])

    def test_juicy_identity_preserves_named_luxury_edition(self):
        identity, volume, title = catalog_worker.juicy_series_identity(
            "JUICY HONEY The Luxury Edition 2025 -Duo Divas-"
        )

        self.assertEqual("the-luxury:2025:duo divas", identity)
        self.assertIsNone(volume)
        self.assertEqual("JUICY HONEY THE LUXURY EDITION 2025 Duo Divas", title)

    def test_juicy_identity_accepts_official_annversary_headline_typo(self):
        identity, volume, title = catalog_worker.juicy_series_identity(
            "8月22日発売【ジューシーハニー 15th ANNVERSARY】通販予約受付"
        )

        self.assertEqual("anniversary:15:unknown", identity)
        self.assertIsNone(volume)
        self.assertEqual("JUICY HONEY 15TH ANNIVERSARY", title)

    def test_juicy_identity_expands_mixed_stock_article_headline(self):
        identities = catalog_worker.juicy_series_identities(
            "【JH PLUS #9】【#14】【LX2018】【DX2021】のレアシングルカード"
        )

        self.assertEqual(
            ["plus:9", "plus:14", "luxury:2018:", "the-deluxe:2021:"],
            [item[0] for item in identities],
        )
        self.assertEqual(
            [
                "JUICY HONEY PLUS #9",
                "JUICY HONEY PLUS #14",
                "JUICY HONEY LUXURY EDITION 2018",
                "JUICY HONEY THE DELUXE 2021",
            ],
            [item[2] for item in identities],
        )

    def test_juicy_mixed_article_hydrates_one_release_per_headline_identity(self):
        source_url = "https://juicy-honey.blog.jp/archives/1079808227.html"

        class Page:
            url = source_url

        payload = {
            "title": "【JH PLUS #9】【#14】【LX2018】【DX2021】のレアシングルカード",
            "heading": "ジューシーハニー トレーディングカード Blog",
            "body": "Official rare singles",
            "published": "2022-07-20",
            "castCandidates": [],
            "profileNames": [],
            "modelProfiles": [],
            "articleImages": [],
        }
        with patch.object(catalog_worker, "goto"), patch.object(
            catalog_worker,
            "juicy_article_payload",
            return_value=payload,
        ):
            hydrated = catalog_worker.hydrate_juicy_article(
                Page(), source_url, payload["title"], 2022
            )

        releases = hydrated["releases"]
        self.assertEqual(4, len(releases))
        self.assertTrue(all(item["release"]["sourceReleaseCount"] == 4 for item in releases))
        self.assertEqual(
            ["plus:9", "plus:14", "luxury:2018:", "the-deluxe:2021:"],
            [item["identity"] for item in releases],
        )
        self.assertTrue(all(not item["release"]["releaseDate"] for item in releases))

    def test_juicy_mixed_article_recovers_cast_scoped_to_each_volume(self):
        source_url = "https://juicy-honey.blog.jp/archives/legacy-restock.html"

        class Page:
            url = source_url

        payload = {
            "title": "[VOL.7][VOL.8] restock",
            "heading": "JUICY HONEY Trading Card Blog",
            "body": (
                "青木りんさん、工藤はつみさんを収録した【VOL.7】と、"
                "紅音ほたるさん、麻美ゆまさんを収録した【VOL.8】！"
            ),
            "published": "2022-07-21",
            "castCandidates": [],
            "profileNames": [],
            "modelProfiles": [],
            "articleImages": [],
        }
        with patch.object(catalog_worker, "goto"), patch.object(
            catalog_worker,
            "juicy_article_payload",
            return_value=payload,
        ):
            hydrated = catalog_worker.hydrate_juicy_article(
                Page(), source_url, payload["title"], 2022
            )

        releases = {
            item["identity"]: item["release"] for item in hydrated["releases"]
        }
        self.assertEqual(
            ["青木りん", "工藤はつみ"], releases["volume:7"]["modelNames"]
        )
        self.assertEqual(
            ["紅音ほたる", "麻美ゆま"], releases["volume:8"]["modelNames"]
        )
        self.assertTrue(releases["volume:7"]["castComplete"])
        self.assertEqual("mixed_article_scoped", releases["volume:8"]["castSource"])
        self.assertEqual("", releases["volume:7"]["releaseDate"])

    def test_juicy_mixed_article_hydrates_verified_historical_releases(self):
        source_url = "https://juicy-honey.blog.jp/archives/1079805229.html"

        class Page:
            url = source_url

        payload = {
            "title": "[JH VOL.9][VOL.42][VOL.43][PLUS #1][#2][#3][#5] rare singles",
            "heading": "JUICY HONEY Trading Card Blog",
            "body": "Official rare singles restock",
            "published": "2022-07-21",
            "castCandidates": [],
            "profileNames": [],
            "modelProfiles": [],
            "articleImages": [],
        }
        with patch.object(catalog_worker, "goto"), patch.object(
            catalog_worker,
            "juicy_article_payload",
            return_value=payload,
        ):
            hydrated = catalog_worker.hydrate_juicy_article(
                Page(), source_url, payload["title"], 2022
            )

        releases = {
            item["identity"]: item["release"] for item in hydrated["releases"]
        }
        expected = {
            "plus:1": ("2018-12-22", ["天使もえ", "希崎ジェシカ", "白石茉莉奈", "益坂美亜"]),
            "plus:2": ("2019-04-27", ["AIKA", "JULIA", "本庄鈴", "桃乃木かな"]),
            "plus:3": ("2019-06-29", ["篠田ゆう", "唯井まひろ", "橋本ありな", "波多野結衣"]),
        }
        for identity, (release_date, names) in expected.items():
            self.assertEqual(release_date, releases[identity]["releaseDate"])
            self.assertEqual(names, releases[identity]["modelNames"])
            self.assertTrue(releases[identity]["castComplete"])
            self.assertEqual(
                "verified_release_registry", releases[identity]["castSource"]
            )
        self.assertFalse(releases["plus:5"]["castComplete"])
        self.assertEqual("", releases["plus:5"]["releaseDate"])

    def test_verified_juicy_registry_covers_2019_special_editions(self):
        expected = {
            "luxury:2019:": (
                "2019-02-24",
                ["戸田真琴", "三上悠亜", "明日花キララ", "成宮りか"],
            ),
            "deluxe:2019:": (
                "2019-08-25",
                ["阿部乃みく", "紗倉まな", "高橋しょう子", "浜崎真緒"],
            ),
        }
        for identity, (release_date, names) in expected.items():
            release = catalog_worker.apply_verified_juicy_release_metadata(
                identity,
                {"sourceUrl": "https://juicy-honey.blog.jp/archives/restock.html"},
            )
            self.assertEqual(release_date, release["releaseDate"])
            self.assertEqual(names, release["modelNames"])
            self.assertTrue(release["castComplete"])

    def test_verified_juicy_registry_covers_legacy_rows(self):
        expected = {
            "volume:26": ("2014-04-26", ["由愛可奈", "希崎ジェシカ", "紗倉まな"]),
            "volume:24": ("2013-11-23", ["さとう遥希", "つぼみ", "上原亜衣"]),
            "volume:22": ("2013-05-24", ["さとう遥希", "希崎ジェシカ", "瑠川リナ"]),
            "volume:21": ("2013-03-23", ["成瀬心美", "紗倉まな", "ティア"]),
            "volume:19": ("2012-04-28", ["成瀬心美", "横山美雪", "星美りか"]),
            "volume:14": ("2010-09-25", ["つぼみ", "希志あいの", "明日花キララ"]),
            "volume:13": ("2010-07-10", ["並木優", "周防ゆきこ", "横山美雪"]),
            "volume:12": ("2010-02-13", ["天海つばさ", "大橋未久", "佳山三花"]),
            "volume:9": ("2008-08-09", ["みひろ", "小澤マリア", "七海なな", "黒木アリサ"]),
            "volume:6": ("2007-06-16", ["紅音ほたる", "麻美ゆま", "範田紗々", "涼果りん"]),
            "volume:5": ("2007-02-24", ["結城凛", "松嶋れいな", "安達真実", "北原多香子"]),
            "volume:4": ("2006-10-07", ["青木りん", "乙女奈々", "寧々", "工藤はつみ"]),
            "luxury:2008:": ("2008-12-20", ["麻美ゆま", "希志あいの", "ほしのみゆ"]),
            "luxury:2017:": ("2017-07-01", ["桐谷まつり", "JULIA", "高橋しょう子", "佐倉絆"]),
        }
        for identity, (release_date, names) in expected.items():
            release = catalog_worker.apply_verified_juicy_release_metadata(
                identity,
                {"sourceUrl": "https://juicy-honey.blog.jp/archives/restock.html"},
            )
            self.assertEqual(release_date, release["releaseDate"])
            self.assertEqual(names, release["modelNames"])
            self.assertTrue(release["castComplete"])

    def test_juicy_annversary_article_uses_release_year_and_not_body_luxury_mention(self):
        source_url = "https://juicy-honey.blog.jp/archives/1077602459.html"

        class Page:
            url = source_url

        payload = {
            "title": "ジューシーハニー 15th ANNVERSARY",
            "heading": "8月22日発売【ジューシーハニー 15th ANNVERSARY】",
            "body": "Release Date: August 22nd, 2020\nThe LUXURY series is also available.",
            "published": "2020-07-20",
            "castCandidates": [],
            "profileNames": [],
            "modelProfiles": [],
            "articleImages": [],
        }
        with patch.object(catalog_worker, "goto"), patch.object(
            catalog_worker,
            "juicy_article_payload",
            return_value=payload,
        ):
            hydrated = catalog_worker.hydrate_juicy_article(
                Page(),
                source_url,
                source_url,
                2026,
            )

        self.assertEqual("anniversary:15:2020", hydrated["identity"])
        self.assertEqual("JUICY HONEY 15TH ANNIVERSARY", hydrated["release"]["title"])
        self.assertEqual("anniversary:15:2020", hydrated["release"]["editionKey"])
        self.assertEqual("2020-08-22", hydrated["release"]["releaseDate"])

    def test_juicy_model_validator_rejects_punctuation_and_social_leftovers(self):
        for value in ("https", "Duo", "こんにちは。", "hello!"):
            self.assertFalse(
                catalog_worker.is_probable_juicy_model_name(value),
                msg=value,
            )

    def test_juicy_release_date_does_not_use_archive_year_for_yearless_labels(self):
        self.assertEqual(
            "2020-06-27",
            catalog_worker.extract_juicy_release_date(
                "発売予定 : 2020年6月27日", 2021
            ),
        )
        self.assertEqual(
            "",
            catalog_worker.extract_juicy_release_date("10月24日発売", 2021),
        )

    def test_juicy_release_date_uses_final_revised_date(self):
        self.assertEqual(
            "2022-05-14",
            catalog_worker.extract_juicy_release_date(
                "Release Date: April 30, 2022 -> May 14th, 2022"
            ),
        )

    def test_source_platform_does_not_replace_actual_publisher(self):
        publisher = catalog_worker.resolve_actual_publisher("HIT'S LIMITED gravure card", "produce-216")
        release = catalog_worker.candidate(
            publisher,
            "HIT'S LIMITED Example Trading Card",
            "https://tic.jp/products/list?category_id=123",
            None,
            "2026-08-08",
            "official_store",
            "",
        )

        self.assertEqual("hits", release["publisherKey"])
        self.assertEqual("tic-store", release["sourcePlatformKey"])

    def test_article_image_merge_retains_unknown_images_and_dom_order(self):
        images = catalog_worker.merge_article_images(
            [
                {"originalUrl": "https://example.com/full-a.jpg", "altText": "card preview"},
                {"originalUrl": "https://example.com/unknown-b.jpg", "altText": ""},
            ],
            [
                {"originalUrl": "https://example.com/full-a.jpg", "altText": "duplicate"},
                {"originalUrl": "https://example.com/full-c.jpg", "altText": "flyer"},
            ],
        )

        self.assertEqual(3, len(images))
        self.assertEqual([1, 2, 3], [item["articleImageSequence"] for item in images])
        self.assertEqual("unknown", images[1]["mediaType"])

    def test_juicy_cover_image_keeps_full_anchor_asset_not_thumbnail(self):
        images = catalog_worker.normalize_first_juicy_cover_image(
            [{
                "imageUrl": "https://livedoor.blogimg.jp/juicy_honey_card/imgs/9/8/98b68147.jpg",
                "altText": "Fly_jh_plus31",
                "width": 600,
                "height": 837,
            }],
            "https://juicy-honey.blog.jp/archives/1080000000.html",
        )

        self.assertEqual(
            "https://livedoor.blogimg.jp/juicy_honey_card/imgs/9/8/98b68147.jpg",
            images[0]["originalUrl"],
        )
        self.assertNotIn("-s.jpg", images[0]["originalUrl"])
        self.assertEqual("series_cover", images[0]["mediaType"])

    def test_juicy_cover_prefers_named_flyer_after_card_images(self):
        images = catalog_worker.normalize_first_juicy_cover_image(
            [
                {
                    "imageUrl": "https://livedoor.blogimg.jp/juicy_honey_card/imgs/4/a/4acf7bb6.jpg",
                    "altText": "img20180825_15041603",
                    "titleText": "img20180825_15041603",
                    "width": 441,
                    "height": 640,
                },
                {
                    "imageUrl": "https://livedoor.blogimg.jp/juicy_honey_card/imgs/3/f/3fba858f.jpg",
                    "altText": "Fly_dx",
                    "titleText": "Fly_dx",
                    "width": 600,
                    "height": 845,
                },
            ],
            "https://juicy-honey.blog.jp/archives/1072389175.html",
        )

        self.assertEqual(1, len(images))
        self.assertEqual(
            "https://livedoor.blogimg.jp/juicy_honey_card/imgs/3/f/3fba858f.jpg",
            images[0]["originalUrl"],
        )
        self.assertEqual(
            200,
            catalog_worker.juicy_named_cover_score([{
                "originalUrl": images[0]["originalUrl"],
                "altText": "Fly_dx",
            }]),
        )

    def test_juicy_deluxe_2018_headline_keeps_complete_parenthesized_cast(self):
        names = catalog_worker.extract_juicy_model_names(
            "レアカード！8月26日発売！ジューシーハニーTHE DELUXE 2018"
            "高級版アダルトトレカ（桜もこ＆松田美子＆三上悠亜＆桃乃木かな）"
        )

        self.assertEqual(["桜もこ", "松田美子", "三上悠亜", "桃乃木かな"], names)

    def test_combined_response_separates_composition_and_cards(self):
        release = catalog_worker.normalize_combined_release(
            {
                "publisherKey": "woohoo",
                "sourceUrl": "https://gain-p.jp/release",
                "sourcePlatformKey": "smile-gain",
                "modelNames": ["Example Model"],
                "checklist": {
                    "announcedTotal": 10,
                    "items": [
                        {"entryKind": "composition", "cardCode": "COMP-001", "title": "Regular", "announcedCount": 9},
                        {"entryKind": "card", "cardCode": "R-01", "title": "Regular 1"},
                    ],
                    "checklistImages": [],
                },
            },
            True,
        )

        self.assertEqual(1, len(release["composition"]))
        self.assertEqual(["R-01"], [item["cardCode"] for item in release["cards"]])
        self.assertEqual("partially_parsed", release["cardDataStatus"])

    def test_reference_gallery_does_not_count_as_identified_cards(self):
        release = catalog_worker.normalize_combined_release(
            {
                "publisherKey": "juicy-honey",
                "sourceUrl": "https://juicy-honey.blog.jp/archives/example.html",
                "sourcePlatformKey": "juicy-honey-blog",
                "checklist": {
                    "announcedTotal": 12,
                    "items": [
                        {"entryKind": "preview", "cardCode": "ARCHIVE-001", "title": "Official preview"},
                    ],
                    "checklistImages": [],
                },
            },
            True,
        )

        self.assertEqual(1, len(release["cards"]))
        self.assertEqual(0, release["parsedCardTotal"])
        self.assertEqual("reference_gallery_only", release["cardDataStatus"])

    def test_mint_inventory_cannot_mark_release_complete(self):
        release = catalog_worker.normalize_combined_release(
            {
                "publisherKey": "hits",
                "sourceUrl": "https://www.mint-mall.net/products/detail.php?product_id=1",
                "sourcePlatformKey": "mint-mall",
                "sourceConfidence": "trusted_retailer",
                "modelNames": ["Example Model"],
                "checklist": {
                    "announcedTotal": 1,
                    "items": [{"entryKind": "card", "cardCode": "A-01", "title": "Example"}],
                    "checklistImages": [],
                },
            },
            True,
        )

        self.assertEqual("partially_parsed", release["cardDataStatus"])

    def test_cj_profile_parser_tolerates_missing_cup(self):
        profiles = catalog_worker.extract_cj_model_profiles(
            """
小日向みゆう（コヒナタミユ）プロフィール
生年月日：1998年3月9日
身長 158cm B 86cm W 58cm H 88cm

MINAMO（ミナモ）プロフィール
生年月日：2000年8月10日
身長：160cm バスト：85cm ウエスト：58cm ヒップ：86cm カップ：E
""",
            "https://jyu-toku.sakura.ne.jp/jyu-toku/example/",
        )

        self.assertEqual(2, len(profiles))
        self.assertEqual((158, 86, 58, 88, ""), (
            profiles[0]["heightCm"], profiles[0]["bustCm"],
            profiles[0]["waistCm"], profiles[0]["hipCm"], profiles[0]["cup"],
        ))
        self.assertEqual("E", profiles[1]["cup"])

    def test_juicy_cast_parser_keeps_all_models_from_official_product_block(self):
        names = catalog_worker.extract_juicy_model_names(
            """
ジューシーハニー Exquisite Edition 2026 -Harmony of Elegance-
星乃莉子 ＆ 田野憂 ＆ 明里つむぎ ＆ 恋渕ももな プレミアム セクシー女優トレカ
売価 : ボックス＠16,000円
【収録女優Profile】
星乃莉子 RIKO HOSHINO [ホシノリコ]
誕生日：1999年4月20日
田野憂 Yu Tano [タノユウ]
誕生日：2003年12月24日
明里つむぎ TSUMUGI AKARI [アカリツムギ]
誕生日：1998年3月31日
恋渕ももな MOMONA KOIBUCHI [コイブチモモナ]
誕生日：1999年3月3日
カメラマン 篠原潔
"""
        )

        self.assertEqual(["星乃莉子", "田野憂", "明里つむぎ", "恋渕ももな"], names)

    def test_juicy_cast_selection_ignores_social_and_marketing_labels(self):
        names, source, complete = catalog_worker.select_juicy_cast(
            [
                "X.com",
                "Duo",
                "星乃莉子 ＆ 田野憂 ＆ 明里つむぎ ＆ 恋渕ももな プレミアム セクシー女優トレカ",
            ],
            ["X.com", "星乃莉子", "田野憂", "明里つむぎ", "恋渕ももな"],
            [],
            "",
        )

        self.assertTrue(complete)
        self.assertEqual("profile_section", source)
        self.assertEqual(["星乃莉子", "田野憂", "明里つむぎ", "恋渕ももな"], names)

    def test_juicy_person_name_normalizes_spaced_japanese_profile_heading(self):
        self.assertEqual(
            "瀬戸環奈",
            catalog_worker.normalize_juicy_person_name("瀬戸 環奈 KANNA SETO [セトカンナ]"),
        )

    def test_juicy_anniversary_accepts_complete_twenty_model_profile_section(self):
        anniversary_names = [
            "石川澪", "山岸あや花", "伊藤舞雪", "天使もえ", "小島みなみ", "miru",
            "三上悠亜", "波多野結衣", "あやみ旬果", "希志あいの", "希崎ジェシカ", "希島あいり",
            "紗倉まな", "白石茉莉奈", "河北彩伽", "大槻ひびき", "桃乃木かな", "戸田真琴",
            "高橋しょう子", "JULIA",
        ]

        names, source, complete = catalog_worker.select_juicy_cast(
            [],
            anniversary_names,
            [{"name": name} for name in anniversary_names],
            "JUICY HONEY 20th Anniversary",
            allow_large_cast=True,
        )

        self.assertTrue(complete)
        self.assertEqual("profile_section", source)
        self.assertEqual(anniversary_names, names)

        identity, _, _ = catalog_worker.juicy_series_identity(
            "JUICY HONEY 20th Anniversary 2025"
        )
        self.assertEqual("anniversary", identity.split(":", 1)[0])

    def test_ordinary_release_does_not_inherit_large_anniversary_sidebar_cast(self):
        sidebar_names = [
            "北岡果林", "明里つむぎ", "水卜さくら", "新川空", "浜辺やよい", "神木麗",
            "天神羽衣", "本庄鈴", "伊藤舞雪", "瀬戸環奈", "楓ふうあ", "紫堂るい",
            "石川澪", "白上咲花", "純白彩永", "美乃すずめ",
        ]

        names, source, complete = catalog_worker.select_juicy_cast(
            [],
            sidebar_names,
            [{"name": name} for name in sidebar_names],
            "JUICY HONEY PLUS #19 sidebar: JUICY HONEY 20th Anniversary",
        )

        self.assertFalse(complete)
        self.assertEqual("incomplete", source)
        self.assertEqual(sidebar_names, names)

    def test_juicy_product_cast_outweighs_truncated_english_profiles(self):
        names, source, complete = catalog_worker.select_juicy_cast(
            ["大槻ひびき＆三上悠亜＆古川いおり"],
            ["YUA MIKAMI", "KOGAWA", "大槻ひびき"],
            [],
            "JUICY HONEY VOL.36",
        )

        self.assertTrue(complete)
        self.assertEqual("product_cast_line", source)
        self.assertEqual(["大槻ひびき", "三上悠亜", "古川いおり"], names)

    def test_juicy_model_validator_rejects_parser_noise(self):
        for value in (
            "X.com",
            "https",
            "Duo",
            "一部をご紹介いたしますヾ",
            "お客様にはご不便をおかけいたしますが",
            "通販ページにUP済みですので",
            "Model relationship pending",
            "We",
            "have",
            "sales",
            "restriction",
            "sidebar",
            "KOGAWA",
        ):
            self.assertFalse(
                catalog_worker.is_probable_juicy_model_name(value),
                msg=value,
            )

    def test_juicy_model_extractor_reads_older_cast_sentences(self):
        text = (
            "７月１２日発売ジューシーハニーVOL.27アダルトトレーディングカードは\n"
            "鈴村あいりちゃんとあやみ旬果ちゃん、明日花キララちゃんの３名収録で、発売記念イベントも予定！"
        )
        self.assertEqual(
            ["鈴村あいり", "あやみ旬果", "明日花キララ"],
            catalog_worker.extract_juicy_model_names(text),
        )

    def test_juicy_model_extractor_reads_sales_page_ordering_note(self):
        text = "※通販ページは新着順ではなく、鈴村あいりさん→あやみ旬果さん→明日花キララさんの順に掲載されております"
        self.assertEqual(
            ["鈴村あいり", "あやみ旬果", "明日花キララ"],
            catalog_worker.extract_juicy_model_names(text),
        )

    def test_juicy_headline_date_uses_article_year_only_for_explicit_release_label(self):
        self.assertEqual(
            "2014-07-12",
            catalog_worker.extract_juicy_headline_release_date(
                "着用済みランジェリーカード！７月１２日発売ジューシーハニーVOL.27",
                2014,
            ),
        )

    def test_juicy_release_merge_does_not_union_incomplete_noise(self):
        names, profiles, source, complete = catalog_worker.reconcile_juicy_release_cast(
            {
                "modelName": "X.com",
                "modelNames": ["X.com"],
                "castSource": "incomplete",
                "castComplete": False,
            },
            {
                "modelName": "北岡果林",
                "modelNames": ["北岡果林", "明里つむぎ", "水卜さくら", "新川空"],
                "models": [{"name": "北岡果林"}],
                "castSource": "product_cast_line",
                "castComplete": True,
            },
        )

        self.assertTrue(complete)
        self.assertEqual("product_cast_line", source)
        self.assertEqual(["北岡果林", "明里つむぎ", "水卜さくら", "新川空"], names)
        self.assertEqual(names, [profile["name"] for profile in profiles])


if __name__ == "__main__":
    unittest.main()
