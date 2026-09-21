"""Offline contract tests for every seeded resale-marketplace adapter."""

import unittest
from urllib.parse import parse_qs, urlparse

try:
    from marketplace_adapters import resolve_adapter
except ModuleNotFoundError:  # Run from the repository root as a unittest module.
    from scraper.marketplace_adapters import resolve_adapter


MARKETPLACES = {
    "ebay": ("Fan Model photobook", "www.ebay.com"),
    "yahoo-auctions-jp": ("モデル 写真集", "auctions.yahoo.co.jp"),
    "mercari-jp": ("モデル 写真集", "jp.mercari.com"),
    "rakuma": ("モデル 写真集", "fril.jp"),
    "yahoo-furima-jp": ("モデル 写真集", "paypayfleamarket.yahoo.co.jp"),
    "ruten-tw": ("模特 寫真集", "www.ruten.com.tw"),
    "shopee-tw": ("模特 寫真集", "shopee.tw"),
    "yahoo-tw": ("模特 寫真集", "tw.bid.yahoo.com"),
    "taobao-cn": ("模特 写真集", "s.taobao.com"),
    "xianyu-cn": ("模特 写真集", "www.goofish.com"),
    "carousell-my": ("model photobook", "www.carousell.com.my"),
    "shopee-my": ("model photobook", "shopee.com.my"),
    "lazada-my": ("model photobook", "www.lazada.com.my"),
    "mudah-my": ("photobook", "www.mudah.my"),
}


class MarketplaceAdapterTests(unittest.TestCase):
    def test_seeded_marketplaces_have_a_consumer_route_or_explicit_configuration_error(self) -> None:
        for source_id, (query, expected_host) in MARKETPLACES.items():
            with self.subTest(source_id=source_id):
                adapter = resolve_adapter(source_id)
                try:
                    url = adapter.build_search_url(query, "active_discovery", "physical")
                except ValueError as exc:
                    self.assertIn("exact rendered searchUrl", str(exc))
                    continue
                self.assertEqual(urlparse(url).hostname, expected_host)
                self.assertTrue(urlparse(url).scheme in {"http", "https"})

    def test_status_specific_routes_keep_marketplace_filters(self) -> None:
        ebay = resolve_adapter("ebay").build_search_url(
            "model photobook", "sold_discovery", "physical"
        )
        self.assertEqual(parse_qs(urlparse(ebay).query)["LH_Sold"], ["1"])
        self.assertEqual(parse_qs(urlparse(ebay).query)["LH_Complete"], ["1"])

        yahoo = resolve_adapter("yahoo-auctions-jp").build_search_url(
            "モデル 写真集", "sold_discovery", "physical"
        )
        self.assertIn("/closedsearch/closedsearch/", yahoo)

        mercari = resolve_adapter("mercari-jp").build_search_url(
            "モデル 写真集", "sold_discovery", "physical"
        )
        self.assertEqual(parse_qs(urlparse(mercari).query)["status"], ["sold_out"])

        with self.assertRaisesRegex(ValueError, "exact rendered closed-listing searchUrl"):
            resolve_adapter("yahoo-tw").build_search_url(
                "模特 寫真集", "sold_discovery", "physical"
            )

        with self.assertRaisesRegex(ValueError, "does not expose a verified public sold-history route"):
            resolve_adapter("mudah-my").build_search_url(
                "photobook", "sold_discovery", "physical"
            )

    def test_new_candidate_detail_urls_have_stable_ids(self) -> None:
        cases = {
            "yahoo-tw": (
                "https://tw.bid.yahoo.com/item/101752226580",
                "101752226580",
            ),
            "mudah-my": (
                "https://www.mudah.my/yes-i-am-chaeyoung-1st-photobook-115829041.htm",
                "115829041",
            ),
        }
        for source_id, (url, external_id) in cases.items():
            with self.subTest(source_id=source_id):
                adapter = resolve_adapter(source_id)
                self.assertTrue(adapter.is_result_url(url))
                self.assertEqual(adapter.extract_external_id(url), external_id)

    def test_jdirectitems_alias_uses_canonical_yahoo_identity(self) -> None:
        alias = resolve_adapter("jdirectmarket")
        canonical = resolve_adapter("yahoo-auctions-jp")
        self.assertEqual(alias.key, canonical.key)


if __name__ == "__main__":
    unittest.main()
