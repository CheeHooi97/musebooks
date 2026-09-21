import unittest

import catalog_worker


class FakePage:
    def __init__(self, text):
        self.text = text

    def evaluate(self, _script):
        return self.text

    def eval_on_selector_all(self, _selector, _script):
        return []


class MediaWorkerTests(unittest.TestCase):
    def test_build_terms_includes_model_and_volume(self):
        terms = catalog_worker.media_build_terms({
            "title": "WooHoo Girls Vol. 24",
            "subtitle": "斎藤恭代 ～CHURA～",
            "volume": 24,
        })
        self.assertIn("斎藤恭代", terms)
        self.assertIn("vol.24", terms)

    def test_woohoo_category_page_matches_model_and_volume(self):
        terms = catalog_worker.media_build_terms({
            "title": "\u5cb8\u660e\u65e5\u9999 2026\u5e7410\u670824\u65e5\u767a\u58f2 WooHoo Girls Vol. 25",
            "volume": 25,
        })
        self.assertIn("\u5cb8\u660e\u65e5\u9999", terms)
        page = FakePage("\u5546\u54c1\u60c5\u5831 \u5cb8\u660e\u65e5\u9999 WooHoo Girls Series \u7b2c25\u5f3e")
        source = "https://gain-p.jp/products/list?category_id=900"
        self.assertTrue(catalog_worker.media_resolve_release_page(page, source, terms))

    def test_woohoo_category_page_rejects_wrong_release(self):
        terms = catalog_worker.media_build_terms({
            "title": "\u5cb8\u660e\u65e5\u9999 WooHoo Girls Vol. 25",
            "volume": 25,
        })
        page = FakePage("\u5546\u54c1\u60c5\u5831 \u5c0f\u6c60\u91cc\u5948 WooHoo Girls Vol.19")
        source = "https://gain-p.jp/products/list?category_id=817"
        self.assertFalse(catalog_worker.media_resolve_release_page(page, source, terms))

    def test_numbered_term_does_not_match_later_volume(self):
        self.assertTrue(catalog_worker.media_term_matches("vol.1", "woohoo girls vol.1"))
        self.assertFalse(catalog_worker.media_term_matches("vol.1", "woohoo girls vol.19"))
        self.assertFalse(catalog_worker.media_term_matches("vol1", "woohoo girls vol10"))

    def test_release_signal_requires_volume_or_non_latin_model(self):
        self.assertTrue(catalog_worker.media_is_release_signal("vol.1"))
        self.assertTrue(catalog_worker.media_is_release_signal("斎藤恭代"))
        self.assertFalse(catalog_worker.media_is_release_signal("woohoo company"))

    def test_normalize_images_rejects_icons_and_small_images(self):
        images = catalog_worker.normalize_images([
            {"url": "https://example.com/logo.png", "width": 900, "height": 400},
            {"url": "https://example.com/tiny.jpg", "width": 80, "height": 80},
            {"url": "https://example.com/product-box.jpg", "alt": "Trading card box", "width": 900, "height": 700},
        ], "https://example.com/release", 5)
        self.assertEqual(len(images), 1)
        self.assertEqual(images[0]["mediaType"], "box")

    def test_juicy_honey_cover_beats_card_preview_and_ignores_host_directory(self):
        images = catalog_worker.normalize_images([
            {
                "url": "https://livedoor.blogimg.jp/juicy_honey_card/imgs/5/a/5a1c7ad8.jpg",
                "alt": "JH17 Fly (1)-page-001",
                "width": 600,
                "height": 800,
            },
            {
                "url": "https://livedoor.blogimg.jp/juicy_honey_card/imgs/b/6/IMG_7755.jpg",
                "alt": "rare card preview",
                "width": 1400,
                "height": 1000,
            },
        ], "https://juicy-honey.blog.jp/archives/1080177233.html", 1)
        self.assertEqual(len(images), 1)
        self.assertEqual(images[0]["mediaType"], "series_cover")
        self.assertIn("5a1c7ad8.jpg", images[0]["originalUrl"])

    def test_meta_image_can_have_unknown_dimensions(self):
        images = catalog_worker.normalize_images([
            {"url": "/release-card.webp", "source": "meta", "scoreBoost": 80},
        ], "https://example.com/product/1", 5)
        self.assertEqual(images[0]["originalUrl"], "https://example.com/release-card.webp")
        self.assertEqual(images[0]["mimeType"], "image/webp")

    def test_linked_full_size_image_can_have_unknown_dimensions(self):
        images = catalog_worker.normalize_images([
            {
                "url": "https://resize.blogsys.jp/release/juicy-honey-plus-29.jpg",
                "source": "linked",
                "scoreBoost": 55,
                "alt": "JUICY HONEY PLUS #29 trading cards",
            },
            {
                "url": "https://example.com/placeholder.gif",
                "source": "img",
                "width": 1,
                "height": 1,
            },
        ], "https://juicy-honey.blog.jp/archives/1083269737.html", 5)
        self.assertEqual(len(images), 1)
        self.assertIn("juicy-honey-plus-29.jpg", images[0]["originalUrl"])

    def test_linked_product_page_is_not_saved_as_an_image(self):
        images = catalog_worker.normalize_images([
            {
                "url": "https://gain-p.jp/products/detail/2012",
                "source": "linked",
                "width": 1000,
                "height": 1000,
            },
        ], "https://gain-p.jp/products/list?category_id=817", 5)
        self.assertEqual(images, [])

    def test_rejects_svg_and_placeholder_images(self):
        images = catalog_worker.normalize_images([
            {"url": "https://example.com/hero-placeholder.png", "source": "meta"},
            {"url": "https://example.com/card-logo.svg", "source": "meta"},
        ], "https://example.com/release", 5)
        self.assertEqual(images, [])

    def test_deduplicates_wordpress_thumbnail_derivatives(self):
        images = catalog_worker.normalize_images([
            {"url": "https://example.com/card-300x270.jpg", "width": 300, "height": 270},
            {"url": "https://example.com/card.jpg", "width": 1000, "height": 900},
        ], "https://example.com/release", 5)
        self.assertEqual(len(images), 1)
        self.assertEqual(images[0]["originalUrl"], "https://example.com/card.jpg")

    def test_release_image_beats_duplicate_box_mirrors_within_limit(self):
        images = catalog_worker.normalize_images([
            {
                "url": "https://jyu-toku.sakura.ne.jp/jyu-toku/wp-content/uploads/2017/08/sakura_momo_box-0822.jpg",
                "alt": "product box",
                "width": 716,
                "height": 1024,
            },
            {
                "url": "https://synergy.tokyo/wp_jyutoku/wp-content/uploads/2017/08/sakura_momo_box-0822-716x1024.jpg",
                "alt": "product box",
                "width": 716,
                "height": 1024,
            },
            {
                "url": "http://synergy.tokyo/wp_jyutoku/wp-content/uploads/2017/08/sakura_momo_box-0822-716x1024.jpg",
                "alt": "product box",
                "width": 716,
                "height": 1024,
            },
            {
                "url": "https://jyu-toku.sakura.ne.jp/jyu-toku/wp-content/uploads/2017/08/sakura_momo.jpg",
                "width": 800,
                "height": 732,
            },
        ], "https://jyu-toku.sakura.ne.jp/jyu-toku/sakura33/", 3)
        self.assertEqual(len(images), 2)
        self.assertEqual(images[0]["mediaType"], "release_image")
        self.assertIn("sakura_momo.jpg", images[0]["originalUrl"])

    def test_https_page_drops_mixed_content_image(self):
        images = catalog_worker.normalize_images([
            {"url": "http://example.com/release.jpg", "width": 800, "height": 600},
        ], "https://example.com/release", 5)
        self.assertEqual(images, [])


if __name__ == "__main__":
    unittest.main()
