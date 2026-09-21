import json
import unittest
from datetime import datetime, timedelta, timezone
from io import StringIO
from unittest.mock import patch

import worker


class _EmptyLocator:
    @property
    def first(self):
        return self

    def count(self):
        return 0


class _PageWithoutTime:
    def locator(self, _selector):
        return _EmptyLocator()


class _TextLocator:
    def __init__(self, value):
        self.value = value

    @property
    def first(self):
        return self

    def count(self):
        return 1

    def inner_text(self, timeout=None):
        return self.value


class _ScriptListLocator:
    def __init__(self, values, index=None):
        self.values = values
        self.index = index

    def count(self):
        return len(self.values)

    def nth(self, index):
        return _ScriptListLocator(self.values, index)

    def inner_text(self):
        return self.values[self.index]


class _StructuredPage:
    def __init__(self, payloads):
        self.payloads = payloads

    def locator(self, _selector):
        return _ScriptListLocator(self.payloads)


class _PageWithBody:
    def __init__(self, body):
        self.body = body

    def locator(self, _selector):
        return _TextLocator(self.body)


class _ActiveCheckPage:
    def __init__(self, body, title="Auction listing"):
        self.body = body
        self.title = title

    def goto(self, *_args, **_kwargs):
        return None

    def locator(self, selector):
        if selector == "body":
            return _TextLocator(self.body)
        if selector == "h1":
            return _TextLocator(self.title)
        if selector == "script[type='application/ld+json']":
            return _ScriptListLocator([])
        return _EmptyLocator()


class _FlakySearchPage:
    def __init__(self):
        self.goto_calls = 0
        self.goto_options = []

    def goto(self, *_args, **kwargs):
        self.goto_calls += 1
        self.goto_options.append(kwargs)
        if self.goto_calls == 1:
            raise TimeoutError("transient navigation failure")

    def wait_for_timeout(self, _milliseconds):
        return None

    def wait_for_selector(self, _selector, **_options):
        return None

    def locator(self, _selector):
        return _TextLocator("売り切れ 3,500円 2026/01/02 該当する商品がありません")


class _HydratingDoorzoPage:
    def __init__(self):
        self.evaluate_calls = 0

    def evaluate(self, _script):
        self.evaluate_calls += 1
        return "" if self.evaluate_calls < 3 else "Doorzo search results"

    def wait_for_selector(self, _selector, **_options):
        return None

    def locator(self, _selector):
        return _TextLocator("")

    def wait_for_timeout(self, _milliseconds):
        return None


class _YahooPage:
    def __init__(self, cards):
        self.cards = cards

    def eval_on_selector_all(self, _selector, _script):
        return self.cards


class _GenericPage:
    def __init__(self, cards, body=""):
        self.cards = cards
        self.body = body

    def eval_on_selector_all(self, _selector, script):
        if "map(a => a.href)" in script:
            return [card["url"] for card in self.cards]
        return self.cards

    def locator(self, _selector):
        return _TextLocator(self.body)


class _YahooFurimaDetailPage(_GenericPage):
    def __init__(self, cards, body, detail_title=""):
        super().__init__(cards, body)
        self.detail_title = detail_title
        self.goto_calls = []

    def goto(self, url, **_options):
        self.goto_calls.append(url)

    def locator(self, selector):
        if selector == "body":
            return _TextLocator(self.body)
        if selector == "h1":
            return _TextLocator(self.detail_title) if self.detail_title else _EmptyLocator()
        return _EmptyLocator()


class _StreamPage:
    def __init__(self, pages):
        self.pages = pages
        self.current_page = 1

    def eval_on_selector_all(self, _selector, script):
        cards = self.pages.get(self.current_page, [])
        if "map(a => a.href)" in script:
            return [card["url"] for card in cards]
        return cards


class _StreamBrowser:
    def __init__(self, page):
        self.page = page
        self.closed = False

    def new_page(self):
        return self.page

    def close(self):
        self.closed = True


class WorkerTests(unittest.TestCase):
    def test_requested_page_runs_only_that_page(self):
        page_size, max_pages, page_numbers = worker.resolve_pagination(
            {"pageSize": 25, "pageNumber": 37, "untilEnd": True}
        )
        self.assertEqual(page_size, 25)
        self.assertEqual(max_pages, 1)
        self.assertEqual(page_numbers, [37])

    def test_search_page_retries_when_body_is_temporarily_unavailable(self):
        page = _FlakySearchPage()
        worker.load_search_page(page, "https://jp.mercari.com/search", "mercari-jp")
        self.assertEqual(page.goto_calls, 2)
        self.assertEqual(page.goto_options[0]["wait_until"], "commit")
        self.assertEqual(page.goto_options[0]["timeout"], 45000)

    def test_doorzo_waits_for_hydrated_body_after_domcontentloaded(self):
        page = _HydratingDoorzoPage()
        worker.ensure_search_page_usable(page, "doorzo-mercari")
        self.assertEqual(page.evaluate_calls, 3)

    def test_until_end_has_a_finite_emergency_ceiling(self):
        page_size, max_pages, page_numbers = worker.resolve_pagination(
            {"pageSize": 25, "untilEnd": True}
        )
        self.assertEqual(page_size, 25)
        self.assertEqual(max_pages, 1000)
        self.assertEqual(page_numbers.start, 1)
        self.assertEqual(page_numbers.stop, 1001)

    def test_until_end_honors_configured_max_pages(self):
        _, max_pages, page_numbers = worker.resolve_pagination(
            {"pageSize": 25, "untilEnd": True, "maxPages": 7}
        )
        self.assertEqual(max_pages, 7)
        self.assertEqual(page_numbers.stop, 8)

    def test_stream_continues_after_rendered_page_has_zero_accepted_items(self):
        page = _StreamPage({
            1: [{
                "url": "https://jp.mercari.com/item/figure-1",
                "title": "Popular figure",
                "text": "販売中 1,000円 フィギュア",
                "image": "",
            }],
            2: [{
                "url": "https://jp.mercari.com/item/card-1",
                "title": "WooHoo トレカ",
                "text": "販売中 1,000円 WooHoo トレカ",
                "image": "",
            }],
            3: [],
        })
        browser = _StreamBrowser(page)

        def fake_load(_page, url, _platform, mode="sold"):
            del mode
            page.current_page = 3 if "v1%3A2" in url else (2 if "v1%3A1" in url else 1)

        output = StringIO()
        with patch.object(worker, "launch", return_value=browser), patch.object(
            worker, "load_search_page", side_effect=fake_load
        ), patch("sys.stdout", output):
            worker.stream_active_pages(
                {"query": "woohoo", "untilEnd": True, "maxPages": 3, "pageSize": 25},
                "mercari-jp",
            )

        events = [json.loads(line) for line in output.getvalue().splitlines()]
        pages = [event for event in events if event["type"] == "page"]
        self.assertEqual([event["pageNumber"] for event in pages], [1, 2, 3])
        self.assertFalse(pages[0]["batch"]["pageEmpty"])
        self.assertEqual(pages[0]["batch"]["items"], [])
        self.assertEqual(len(pages[1]["batch"]["items"]), 1)
        self.assertTrue(pages[2]["batch"]["pageEmpty"])

    def test_stream_stops_on_repeated_page_fingerprint(self):
        card = {
            "url": "https://jp.mercari.com/item/card-1",
            "title": "WooHoo トレカ",
            "text": "販売中 1,000円 WooHoo トレカ",
            "image": "",
        }
        page = _StreamPage({1: [card], 2: [card]})
        browser = _StreamBrowser(page)

        def fake_load(_page, url, _platform, mode="sold"):
            del mode
            page.current_page = 2 if "v1%3A1" in url else 1

        output = StringIO()
        with patch.object(worker, "launch", return_value=browser), patch.object(
            worker, "load_search_page", side_effect=fake_load
        ), patch("sys.stdout", output):
            worker.stream_active_pages(
                {"query": "woohoo", "untilEnd": True, "maxPages": 5, "pageSize": 25},
                "mercari-jp",
            )

        events = [json.loads(line) for line in output.getvalue().splitlines()]
        self.assertEqual([event["type"] for event in events], ["page", "stop"])
        self.assertEqual(events[-1]["stopReason"], "repeated_page_fingerprint")

    def test_stream_skips_failed_query_and_continues_with_next_query(self):
        browser = _StreamBrowser(_StreamPage({1: []}))
        query_specs = [
            {"query": "woohoo"},
            {"query": "juicy honey"},
        ]
        output = StringIO()
        with patch.object(worker, "launch", return_value=browser), patch.object(
            worker,
            "stream_active_query_pages",
            side_effect=[RuntimeError("navigation timeout"), None],
        ), patch("sys.stdout", output):
            worker.stream_active_pages(
                {"queries": query_specs, "mode": "active", "pageSize": 25},
                "yahoo-auctions-jp",
            )

        events = [json.loads(line) for line in output.getvalue().splitlines()]
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["query"]["query"], "woohoo")
        self.assertEqual(events[0]["stopReason"], "query_error")

    def test_mixed_stream_emits_active_and_sold_rows_from_one_page(self):
        page = _StreamPage({1: [{
            "url": "https://jp.mercari.com/item/active-1",
            "title": "WooHoo active card",
            "text": "販売中 1,000円 WooHoo トレカ",
            "image": "",
        }, {
            "url": "https://jp.mercari.com/item/sold-1",
            "title": "WooHoo sold card",
            "text": "売り切れ 1,500円 WooHoo トレカ",
            "accessibleText": "売り切れ 1,500円",
            "image": "",
        }]})
        browser = _StreamBrowser(page)
        output = StringIO()
        with patch.object(worker, "launch", return_value=browser), patch.object(
            worker, "load_search_page", return_value=None
        ), patch("sys.stdout", output):
            worker.stream_active_pages(
                {"mode": "mixed", "query": "woohoo", "pageSize": 25},
                "mercari-jp",
            )

        event = json.loads(output.getvalue().strip())
        self.assertEqual(event["type"], "page")
        self.assertEqual(
            {item["saleType"] for item in event["batch"]["items"]},
            {"active", "completed"},
        )
        self.assertEqual(event["batch"]["diagnostics"]["renderedCandidates"], 2)
        self.assertEqual(event["batch"]["diagnostics"]["activeCandidates"], 1)
        self.assertEqual(event["batch"]["diagnostics"]["soldCandidates"], 1)

    def test_mixed_stream_keeps_active_rows_when_sold_surface_times_out(self):
        active_item = {"externalListingId": "active-1", "saleType": "active"}
        sold_item = {"externalListingId": "sold-1", "saleType": "completed"}
        diagnostics = {}
        with patch.object(
            worker,
            "load_search_page",
            side_effect=[None, RuntimeError("sold navigation timeout")],
        ), patch.object(
            worker,
            "collect_marketplace_active_items",
            return_value=[active_item],
        ), patch.object(
            worker,
            "collect_marketplace_completed_items",
            return_value=[sold_item],
        ), patch.object(worker, "collect_result_urls", return_value=["active-url"]):
            items, urls = worker.collect_marketplace_mixed_items(
                _StreamPage({1: []}),
                "mercari-jp",
                25,
                query="woohoo",
                diagnostics=diagnostics,
                active_page_url="https://jp.mercari.com/search?status=on_sale",
                sold_page_url="https://jp.mercari.com/search?status=sold_out",
            )

        self.assertEqual(items, [active_item])
        self.assertEqual(urls, ["active-url"])
        self.assertEqual(diagnostics["soldSurfaceErrors"], 1)

    def test_jdirect_uses_completed_results(self):
        url = worker.build_search_url(
            "jdirectmarket", "CJ SEXY trading card", 25
        )
        self.assertIn("auctions.yahoo.co.jp/closedsearch/closedsearch/", url)
        self.assertNotIn("doorzo.com", url)

    def test_yahoo_is_the_canonical_japan_platform(self):
        url = worker.build_search_url(
            "yahoo-auctions-jp", "JUICY HONEY ジューシーハニー", 25
        )
        self.assertIn("auctions.yahoo.co.jp/closedsearch/closedsearch/", url)
        self.assertIn("ebay.com/sch/i.html", worker.build_search_url("ebay", "trading card", 25))

    def test_doorzo_search_url_selects_one_source_and_disables_stock_only_mode(self):
        url = worker.build_search_url(
            "doorzo-mercari", '"JUICY HONEY" 29', 25
        )
        self.assertIn("www.doorzo.com/en/search", url)
        self.assertNotIn("isStock", url)
        self.assertIn("website=mercari", url)
        self.assertIn("keywords=JUICY%20HONEY%20trading%20cards", url)

    def test_doorzo_discovery_query_matches_reference_model_rule(self):
        query = '"WooHoo トレーディングカード" "～NATURAL BODY～" "佐々木優佳里"'
        self.assertEqual(
            worker.doorzo_discovery_query(query),
            "佐々木優佳里 trading cards",
        )
        self.assertEqual(
            worker.doorzo_discovery_query('"JUICY HONEY" "LUXURY" "2026"'),
            "JUICY HONEY trading cards",
        )
        self.assertEqual(
            worker.doorzo_discovery_query('"WooHoo Girls" "～NATURAL BODY～"'),
            "WooHoo trading cards",
        )
        self.assertIn(
            "keywords=woohoo%20%EF%BD%9Enatural%20body%EF%BD%9E%20%E4%BD%90%E3%80%85%E6%9C%A8%E5%84%AA%E4%BD%B3%E9%87%8C",
            worker.build_search_url("doorzo-surugaya", query, 25),
        )

    def test_doorzo_retail_query_keeps_release_terms(self):
        query = '"WooHoo Girls Series" "～NATURAL BODY～" "佐々木優佳里" "トレカ"'
        self.assertEqual(
            worker.doorzo_catalog_query(query),
            "woohoo girls series ～natural body～ 佐々木優佳里",
        )
        url = worker.build_search_url("doorzo-surugaya", query, 25)
        self.assertIn(
            "keywords=woohoo%20girls%20series%20%EF%BD%9Enatural%20body%EF%BD%9E%20%E4%BD%90%E3%80%85%E6%9C%A8%E5%84%AA%E4%BD%B3%E9%87%8C",
            url,
        )

    def test_doorzo_pagination_uses_infinite_grid_windows(self):
        url = worker.build_search_url("doorzo-rakuma", "JUICY HONEY", 25)
        page_two = worker.with_marketplace_page("doorzo-rakuma", url, 2, 25)
        self.assertEqual(page_two, url)
        self.assertEqual(worker.doorzo_page_slice(list(range(60)), 2, 25), list(range(25, 50)))

    def test_doorzo_source_mapping_and_completed_date_fallback(self):
        self.assertEqual(worker.doorzo_source_platform("paypay"), "yahoo-furima-jp")
        self.assertTrue(
            worker.doorzo_source_url_matches(
                "https://www.mercari.com/jp/items/m123", "mercari-jp"
            )
        )
        self.assertFalse(
            worker.doorzo_source_url_matches(
                "https://page.auctions.yahoo.co.jp/jp/auction/x123", "mercari-jp"
            )
        )
        self.assertEqual(
            worker.extract_doorzo_sold_date(
                None, "Sold\nEnd Time\nAug. 18, 2026 20:54:33"
            ),
            "2026-08-18T20:54:33Z",
        )
        self.assertEqual(
            worker.extract_doorzo_sold_date(
                None, "End Time: 2026/08/18 20:54:33", "Asia/Tokyo"
            ),
            "2026-08-18T11:54:33Z",
        )

    def test_active_auction_end_date_parses_short_yahoo_timestamp(self):
        end = worker.extract_auction_end_date("現在価格 1,200円 8/18 21:30終了", "Asia/Tokyo")
        self.assertIsNotNone(end)
        parsed = datetime.fromisoformat(end.replace("Z", "+00:00"))
        self.assertEqual((parsed.month, parsed.day, parsed.hour, parsed.minute), (8, 18, 12, 30))

        japanese_end = worker.extract_auction_end_date("終了日時 8月18日 21:30", "Asia/Tokyo")
        self.assertIsNotNone(japanese_end)
        japanese_parsed = datetime.fromisoformat(japanese_end.replace("Z", "+00:00"))
        self.assertEqual((japanese_parsed.month, japanese_parsed.day, japanese_parsed.hour, japanese_parsed.minute), (8, 18, 12, 30))

        yahoo_detail_end = worker.extract_auction_end_date(
            "終了日時：2026年 8月 20日（木） 21時 30分", "Asia/Tokyo"
        )
        self.assertEqual(yahoo_detail_end, "2026-08-20T12:30:00Z")

        yahoo_detail_suffix_end = worker.extract_auction_end_date(
            "9月5日（土）19時29分 終了予定", "Asia/Tokyo"
        )
        self.assertIsNotNone(yahoo_detail_suffix_end)
        suffix_parsed = datetime.fromisoformat(
            yahoo_detail_suffix_end.replace("Z", "+00:00")
        )
        self.assertEqual(
            (suffix_parsed.month, suffix_parsed.day,
             suffix_parsed.hour, suffix_parsed.minute),
            (9, 5, 10, 29),
        )

    def test_auction_end_date_reads_labeled_embedded_page_data(self):
        page = _StructuredPage([
            '{"auctionEndTime":"2026-08-20T21:30:00+09:00"}'
        ])
        self.assertEqual(
            worker.extract_auction_end_date_from_page(page, "", "Asia/Tokyo"),
            "2026-08-20T12:30:00Z",
        )

    def test_active_auction_end_date_parses_unlabeled_yahoo_countdown(self):
        before = datetime.now(timezone.utc)
        end = worker.extract_auction_end_date(
            "現在 12,988円 即決 15,900円 送料は商品ページ参照 0 3日",
            "Asia/Tokyo",
        )
        after = datetime.now(timezone.utc)
        self.assertIsNotNone(end)
        parsed = datetime.fromisoformat(end.replace("Z", "+00:00"))
        self.assertGreaterEqual(parsed, before + timedelta(days=2, hours=23))
        self.assertLessEqual(parsed, after + timedelta(days=3, minutes=1))

        short_end = worker.extract_auction_end_date(
            "現在 299円 0 9分15秒", "Asia/Tokyo"
        )
        self.assertIsNotNone(short_end)
        short_parsed = datetime.fromisoformat(short_end.replace("Z", "+00:00"))
        self.assertGreaterEqual(short_parsed, before + timedelta(minutes=8))
        self.assertLessEqual(short_parsed, after + timedelta(minutes=11))

    def test_active_listing_check_returns_auction_deadline_for_reconciliation(self):
        page = _ActiveCheckPage(
            "現在価格 1,200円 終了日時 2026年 12月 18日（木） 21時 30分 入札"
        )
        items = worker.collect_active_listing_check(
            page,
            "yahoo-auctions-jp",
            "https://page.auctions.yahoo.co.jp/jp/auction/x123",
        )
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["listingType"], "auction")
        parsed = datetime.fromisoformat(items[0]["auctionEndsAt"].replace("Z", "+00:00"))
        self.assertEqual((parsed.month, parsed.day, parsed.hour, parsed.minute), (12, 18, 12, 30))
        self.assertEqual(items[0]["originalPriceAmount"], 1200.0)

    def test_expired_yahoo_auction_with_winner_returns_final_sold_price(self):
        page = _ActiveCheckPage(
            "落札価格 3,500円 終了日時 2026年 8月 20日（木） 21時 30分"
        )
        items = worker.collect_active_listing_check(
            page,
            "yahoo-auctions-jp",
            "https://page.auctions.yahoo.co.jp/jp/auction/x-sold",
        )
        self.assertEqual(items[0]["saleType"], "inactive")
        self.assertEqual(items[0]["statusEvidence"], "ended_with_winner")
        self.assertEqual(items[0]["priceType"], "auction_hammer")
        self.assertEqual(items[0]["originalPriceAmount"], 3500.0)
        self.assertEqual(items[0]["soldAt"], "2026-08-20T12:30:00Z")

    def test_expired_yahoo_auction_without_winner_is_not_a_sold_result(self):
        page = _ActiveCheckPage("落札者なし 終了")
        items = worker.collect_active_listing_check(
            page,
            "yahoo-auctions-jp",
            "https://page.auctions.yahoo.co.jp/jp/auction/x-unsold",
        )
        self.assertEqual(items[0]["saleType"], "inactive")
        self.assertEqual(items[0]["statusEvidence"], "auction_ended_without_winner")
        self.assertIsNone(items[0]["originalPriceAmount"])
        self.assertIsNone(items[0]["soldAt"])

    def test_expired_yahoo_auction_with_old_bid_labels_is_not_active(self):
        page = _ActiveCheckPage(
            "現在価格 1,200円 終了日時 2026年 8月 20日（木） 21時 30分 入札 0"
        )
        items = worker.collect_active_listing_check(
            page,
            "yahoo-auctions-jp",
            "https://page.auctions.yahoo.co.jp/jp/auction/x-expired",
        )
        self.assertEqual(items[0]["saleType"], "inactive")
        self.assertEqual(items[0]["statusEvidence"], "auction_ended")
        self.assertIsNone(items[0]["originalPriceAmount"])

    def test_active_collection_filters_timestamped_cards_outside_requested_day(self):
        page = _GenericPage(
            [
                {
                    "url": "https://jp.mercari.com/item/old",
                    "title": "WooHoo old trading card",
                    "text": "販売中 1,200円 WooHoo trading card",
                    "activeAt": "2026-08-19T23:59:59Z",
                    "image": "",
                },
                {
                    "url": "https://jp.mercari.com/item/today",
                    "title": "WooHoo today trading card",
                    "text": "販売中 1,500円 WooHoo trading card",
                    "activeAt": "2026-08-20T03:00:00Z",
                    "image": "",
                },
            ]
        )
        diagnostics = {}
        items = worker.collect_marketplace_active_items(
            page,
            "mercari-jp",
            25,
            query="woohoo",
            from_bound=datetime(2026, 8, 20, tzinfo=timezone.utc),
            to_bound=datetime(2026, 8, 20, 23, 59, 59, tzinfo=timezone.utc),
            diagnostics=diagnostics,
        )
        self.assertEqual([item["externalListingId"] for item in items], ["today"])
        self.assertEqual(diagnostics["outsideActiveDateRange"], 1)

    def test_yahoo_completed_search_fallback_rewrites_exact_listing(self):
        candidate = {
            "externalListingId": "x-sold",
            "endedAt": "2026-08-20T12:30:00Z",
            "statusEvidence": "ended_with_winner",
            "rawPayload": json.dumps({"source": "closed-search"}),
        }
        with patch.object(worker, "load_search_page") as load, patch.object(
            worker, "collect_yahoo_completed_items", return_value=[candidate]
        ):
            result = worker.find_yahoo_completed_search_item(
                object(),
                "https://auctions.yahoo.co.jp/jp/auction/x-sold",
                "WooHoo card",
            )
        load.assert_called_once()
        self.assertEqual(result["originalUrl"], "https://auctions.yahoo.co.jp/jp/auction/x-sold")
        self.assertEqual(result["listingType"], "auction")
        self.assertEqual(result["auctionEndsAt"], "2026-08-20T12:30:00Z")
        self.assertEqual(
            json.loads(result["rawPayload"])["reconciliationEvidence"],
            "exact_external_id_closed_search_match",
        )

    def test_aucfan_active_collection_reads_detail_only_auction_deadline(self):
        page = _YahooFurimaDetailPage(
            [{
                "url": "https://aucfan.com/item/x123",
                "title": "WooHoo 風吹ケイ トレカ",
                "text": "現在価格 1,200円 入札 0 WooHoo トレカ",
                "image": "",
            }],
            body=(
                "WooHoo 風吹ケイ トレカ 現在価格 1,200円 入札 "
                "終了日時：2026年 8月 20日（木） 21時 30分"
            ),
            detail_title="WooHoo 風吹ケイ トレカ - Yahoo!オークション",
        )
        diagnostics = {}
        items = worker.collect_marketplace_active_items(
            page, "aucfan", 25, query="woohoo", diagnostics=diagnostics
        )
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["listingType"], "auction")
        self.assertEqual(items[0]["auctionEndsAt"], "2026-08-20T12:30:00Z")
        self.assertEqual(json.loads(items[0]["rawPayload"])["auctionEndEvidence"], "detail_page")
        self.assertEqual(diagnostics["auctionEndDates"], 1)
        self.assertEqual(diagnostics.get("missingAuctionEndDate", 0), 0)

    def test_yahoo_active_collection_reads_exact_end_epoch_from_search_metadata(self):
        page = _YahooFurimaDetailPage(
            [{
                "url": "https://auctions.yahoo.co.jp/jp/auction/x123",
                "title": "WooHoo 風吹ケイ トレカ 260724-800",
                "text": "現在 1,200円 入札 0 8時間 WooHoo トレカ",
                "auctionEndsAt": "1787236764",
                "image": "",
            }],
            body="",
        )
        diagnostics = {}
        items = worker.collect_marketplace_active_items(
            page, "yahoo-auctions-jp", 25, query="woohoo", diagnostics=diagnostics
        )
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["auctionEndsAt"], "2026-08-20T14:39:24Z")
        self.assertEqual(
            json.loads(items[0]["rawPayload"])["auctionEndEvidence"],
            "search_metadata",
        )
        self.assertEqual(diagnostics["auctionEndDates"], 1)
        self.assertEqual(diagnostics.get("detailNavigations", 0), 0)
        self.assertEqual(page.goto_calls, [])

    def test_active_listing_check_uses_exact_yahoo_search_match_for_reconciliation(self):
        search_item = {
            "externalListingId": "x123",
            "saleType": "active",
            "listingType": "auction",
            "auctionEndsAt": "2026-08-20T12:26:04Z",
        }
        page = _ActiveCheckPage(
            "Yahoo! JAPAN ご覧になろうとしているページは現在表示できません。"
        )
        with patch.object(
            worker, "find_yahoo_active_search_item", return_value=search_item
        ) as search:
            items = worker.collect_active_listing_check(
                page,
                "yahoo-auctions-jp",
                "https://auctions.yahoo.co.jp/jp/auction/x123",
                "WooHoo 風吹ケイ トレカ",
            )
        self.assertEqual(items, [search_item])
        search.assert_called_once()

    def test_active_listing_check_prefers_live_yahoo_detail_price_over_search_card(self):
        page = _ActiveCheckPage(
            "現在 88 円 6件 入札 残り 3日 終了日時 2026年 9月 13日（日） 22時 35分"
        )
        stale_search_item = {
            "externalListingId": "x1243496983",
            "saleType": "active",
            "listingType": "auction",
            "originalPriceAmount": 1.0,
        }
        with patch.object(
            worker, "find_yahoo_active_search_item", return_value=stale_search_item
        ) as search:
            items = worker.collect_active_listing_check(
                page,
                "yahoo-auctions-jp",
                "https://auctions.yahoo.co.jp/jp/auction/x1243496983",
                "澄田綾乃 生キス入り特典カードB",
            )
        self.assertEqual(items[0]["originalPriceAmount"], 88.0)
        self.assertEqual(items[0]["listingType"], "auction")
        search.assert_not_called()

    def test_active_listing_check_does_not_assign_deadline_to_fixed_price(self):
        page = _ActiveCheckPage("販売中 購入手続き 1,200円")
        items = worker.collect_active_listing_check(
            page,
            "mercari-jp",
            "https://jp.mercari.com/item/m123",
        )
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["listingType"], "fixed_price")
        self.assertIsNone(items[0]["auctionEndsAt"])

    def test_active_listing_check_preserves_fixed_price_sold_observation(self):
        page = _ActiveCheckPage("売り切れ 1,800円")
        items = worker.collect_active_listing_check(
            page,
            "mercari-jp",
            "https://jp.mercari.com/item/m-sold",
        )
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["saleType"], "inactive")
        self.assertEqual(items[0]["statusEvidence"], "sold_out_badge")
        self.assertEqual(items[0]["priceType"], "fixed_price_sold")
        self.assertEqual(items[0]["originalPriceAmount"], 1800.0)

    def test_mercari_sold_page_ignores_unrelated_auction_words(self):
        page = _ActiveCheckPage("売り切れ 1,500円 残り 1点")
        items = worker.collect_active_listing_check(
            page,
            "mercari-jp",
            "https://jp.mercari.com/item/m-sold-with-recommendation-copy",
        )
        self.assertEqual(items[0]["saleType"], "inactive")
        self.assertEqual(items[0]["listingType"], "")
        self.assertEqual(items[0]["priceType"], "fixed_price_sold")
        self.assertEqual(items[0]["originalPriceAmount"], 1500.0)

    def test_active_listing_check_recognizes_mercari_shipping_confirmation(self):
        page = _ActiveCheckPage("¥5,600 この商品は ゆうパケットプラス で配送されました")
        items = worker.collect_active_listing_check(
            page,
            "mercari-jp",
            "https://jp.mercari.com/item/m-shipped",
        )
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["saleType"], "inactive")
        self.assertEqual(items[0]["statusEvidence"], "sold_out_badge")
        self.assertEqual(items[0]["priceType"], "fixed_price_sold")
        self.assertEqual(items[0]["originalPriceAmount"], 5600.0)

    def test_doorzo_missing_source_date_uses_marked_observation_time(self):
        sold_at, evidence = worker.resolve_doorzo_sold_at(
            None, "Price\nSold Out", "Asia/Tokyo"
        )
        self.assertEqual(evidence, "first_observed_sold")
        self.assertIsNotNone(worker.normalize_date(sold_at))
        bounded_at, bounded_evidence = worker.resolve_doorzo_sold_at(
            None,
            "Price\nSold Out",
            "Asia/Tokyo",
            from_bound=datetime(2026, 8, 1, tzinfo=timezone.utc),
        )
        self.assertIsNone(bounded_at)
        self.assertEqual(bounded_evidence, "")

    def test_doorzo_schema_graph_supplies_exact_price_and_description(self):
        payload = json.dumps({
            "@context": "https://schema.org",
            "@graph": [{
                "@type": "Product",
                "name": "JUICY HONEY card",
                "description": "JUICY HONEY PLUS #02 AIKA",
                "sku": "m79994065264",
                "image": ["https://img.example/card.jpg"],
                "offers": {
                    "availability": "https://schema.org/OutOfStock",
                    "price": 3600,
                    "priceCurrency": "JPY",
                },
            }],
        })
        product = worker.extract_structured_product(_StructuredPage([payload]))
        self.assertEqual(product["price"], 3600)
        self.assertEqual(product["currency"], "JPY")
        self.assertEqual(product["description"], "JUICY HONEY PLUS #02 AIKA")

    def test_doorzo_active_yahoo_evidence_is_not_sold(self):
        self.assertEqual(
            worker.sold_evidence("Buyout 5,000 JPY Time Left 2 days", "yahoo-auctions-jp"),
            "",
        )
        self.assertEqual(
            worker.sold_evidence("売り切れ 3,000円", "yahoo-furima-jp"),
            "platform_sold",
        )
        self.assertEqual(
            worker.marketplace_price_type(
                "yahoo-furima-jp", "platform_sold", "売り切れ 3,000円"
            ),
            "fixed_price_sold",
        )

    def test_all_marketplace_search_urls_are_supported(self):
        expected_hosts = {
            "aucfan": "aucfan.com",
            "mercari-jp": "jp.mercari.com",
            "rakuma": "fril.jp",
            "yahoo-furima-jp": "paypayfleamarket.yahoo.co.jp",
            "surugaya": "suruga-ya.jp",
            "mandarake": "mandarake.co.jp",
            "ebay": "ebay.com",
            "tcgplayer": "tcgplayer.com",
        }
        for platform, host in expected_hosts.items():
            self.assertIn(host, worker.build_search_url(platform, "JUICY HONEY", 25))
        self.assertIn("/s-ya/", worker.build_search_url("aucfan", "JUICY HONEY", 25))

    def test_direct_result_url_filters_accept_current_yahoo_and_rakuma_links(self):
        self.assertTrue(
            worker.is_marketplace_result_url(
                "https://auctions.yahoo.co.jp/jp/auction/n123456789", "yahoo-auctions-jp"
            )
        )
        self.assertFalse(
            worker.is_marketplace_result_url(
                "https://paypayfleamarket.yahoo.co.jp/item/z123", "yahoo-auctions-jp"
            )
        )
        self.assertTrue(
            worker.is_marketplace_result_url(
                "https://item.fril.jp/abc123", "rakuma"
            )
        )
        self.assertTrue(
            worker.is_marketplace_result_url(
                "https://paypayfleamarket.yahoo.co.jp/item/z123", "yahoo-furima-jp"
            )
        )

    def test_regional_result_url_filters_accept_current_product_paths(self):
        self.assertTrue(
            worker.is_marketplace_result_url(
                "https://shopee.tw/2025-rakuten-girls-i.11737622.26283865836",
                "shopee-tw",
            )
        )
        self.assertTrue(
            worker.is_marketplace_result_url(
                "https://www.daangn.com/kr/buy-sell/seventeen-trading-card-1jzqm8pb5ieb/",
                "karrot-kr",
            )
        )
        self.assertTrue(
            worker.is_marketplace_result_url(
                "https://smartstore.naver.com/store/products/123456789",
                "naver-shopping-kr",
            )
        )

    def test_korean_marketplace_restriction_page_fails_fast(self):
        with self.assertRaisesRegex(RuntimeError, "access challenge"):
            worker.ensure_search_page_usable(
                _PageWithBody(
                    "쇼핑 서비스 접속이 일시적으로 제한되었습니다. "
                    "비정상적인 접근이 감지되었습니다."
                ),
                "naver-shopping-kr",
            )

    def test_regional_inactive_markers_do_not_treat_aggregate_sales_as_sold_out(self):
        self.assertEqual(
            worker.inactive_listing_evidence("판매완료 39,000원", "bunjang-kr"),
            "inactive_status",
        )
        self.assertEqual(
            worker.inactive_listing_evidence("已售完 NT$500", "shopee-tw"),
            "inactive_status",
        )
        self.assertEqual(
            worker.inactive_listing_evidence("已售出 3 NT$500", "shopee-tw"),
            "",
        )

    def test_regional_active_collector_keeps_localized_card_rows(self):
        page = _GenericPage(
            [{
                "url": "https://shopee.tw/2025-rakuten-girls-i.11737622.26283865836",
                "title": "2025 樂天女孩卡 琳妲",
                "text": "現貨 NT$150 2025 樂天女孩卡 收藏卡",
                "image": "",
            }]
        )
        items = worker.collect_marketplace_active_items(
            page, "shopee-tw", 25, query="2025 樂天女孩卡"
        )
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["originalCurrencyCode"], "TWD")
        self.assertEqual(items[0]["marketplaceRegion"], "TW")

    def test_korean_active_collector_keeps_localized_card_rows(self):
        page = _GenericPage(
            [{
                "url": "https://smartstore.naver.com/store/products/123456789",
                "title": "세븐틴 공식 트레이딩 카드",
                "text": "판매중 ₩11,430 세븐틴 공식 트레이딩 카드",
                "image": "",
            }]
        )
        items = worker.collect_marketplace_active_items(
            page,
            "naver-shopping-kr",
            25,
            query="세븐틴 공식 트레이딩 카드",
            model_aliases=["SEVENTEEN", "세븐틴", "트레이딩 카드"],
        )
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["originalCurrencyCode"], "KRW")
        self.assertEqual(items[0]["marketplaceRegion"], "KR")

    def test_ebay_sold_collector_accepts_registered_localized_alias(self):
        page = _GenericPage(
            [{
                "url": "https://www.ebay.com/itm/26283865836",
                "title": "2025 樂天女孩卡 琳妲 收藏卡",
                "text": "Sold US$25.00",
                "soldAt": "2026-08-20T12:00:00Z",
                "image": "",
            }]
        )
        items = worker.collect_marketplace_completed_items(
            page,
            "ebay",
            25,
            query="2025 Rakuten Girls trading cards",
            model_aliases=["2025 樂天女孩卡"],
        )
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["originalCurrencyCode"], "USD")

    def test_yahoo_furima_uses_detail_purchase_timestamp(self):
        page = _YahooFurimaDetailPage(
            [{
                "url": "https://paypayfleamarket.yahoo.co.jp/item/z123",
                "title": "CJ SEXY CARD SERIES 小日向みゆう",
                "text": "売り切れ 3,100円",
                "image": "https://img.example/z123.jpg",
            }],
            "売り切れ\n3,100円\n購入日時：2026年8月10日 15:19",
        )
        items = worker.collect_yahoo_furima_completed_items(page, 25, query="cj sexy")
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["originalPriceAmount"], 3100.0)
        self.assertEqual(items[0]["soldAt"], "2026-08-10T06:19:00Z")
        self.assertEqual(items[0]["originalUrl"], "https://paypayfleamarket.yahoo.co.jp/item/z123")
        self.assertEqual(items[0]["statusEvidence"], "platform_sold")
        self.assertEqual(page.goto_calls, ["https://paypayfleamarket.yahoo.co.jp/item/z123"])

    def test_yahoo_furima_completed_rejects_result_card_chrome_as_series_match(self):
        page = _YahooFurimaDetailPage(
            [{
                "url": "https://paypayfleamarket.yahoo.co.jp/item/z1240",
                "title": "DX Nintendo Switch ニンテンドースイッチ",
                "text": "CJ SEXY CARD SERIES\n売り切れ\n3,000円",
                "image": "https://img.example/z1240.jpg",
            }],
            "売り切れ\n3,000円\n購入日時：2026年8月10日 15:19",
        )
        items = worker.collect_yahoo_furima_completed_items(page, 25, query="cj sexy")
        self.assertEqual(items, [])
        self.assertEqual(page.goto_calls, [])

    def test_yahoo_furima_purchase_timestamp_alone_confirms_sold(self):
        self.assertEqual(
            worker.sold_evidence(
                "22,900円 購入日時：2026年5月31日 14:45",
                "yahoo-furima-jp",
            ),
            "platform_sold",
        )

    def test_yahoo_furima_active_refreshes_price_badge_title_from_detail(self):
        page = _YahooFurimaDetailPage(
            [{
                "url": "https://paypayfleamarket.yahoo.co.jp/item/z124",
                "title": "2,580円 いいね!",
                "text": "2,580円 いいね! WooHoo トレカ",
                "image": "https://img.example/z124.jpg",
            }],
            "販売中\n2,580円\nWooHoo トレカ",
            detail_title="風吹ケイ WooHoo ～EVOLUTION～ トレカ | PayPayフリマ",
        )
        items = worker.collect_marketplace_active_items(
            page, "yahoo-furima-jp", 25, query="woohoo"
        )
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["title"], "風吹ケイ WooHoo ～EVOLUTION～ トレカ")
        self.assertEqual(page.goto_calls, ["https://paypayfleamarket.yahoo.co.jp/item/z124"])

    def test_yahoo_furima_rejects_price_likes_promotion_as_title(self):
        self.assertTrue(
            worker.invalid_marketplace_listing_title("5,000円 いいね！ 最大10%対象")
        )
        self.assertFalse(
            worker.invalid_marketplace_listing_title(
                "Honey' Cheon GSAM / JUICY HONEY Collection Cards"
            )
        )

    def test_yahoo_furima_active_recovers_title_after_promotion_anchor(self):
        correct_title = "紫藤るい ジューシーハニー PLUS #29 直筆サインカード 2枚セット"
        page = _YahooFurimaDetailPage(
            [{
                "url": "https://paypayfleamarket.yahoo.co.jp/item/z666375558",
                "title": "5,000円 いいね！ 最大10%対象",
                "text": "5,000円\nいいね！\n最大10%対象\n" + correct_title,
                "image": "https://img.example/z666375558.jpg",
            }],
            body="ご覧になろうとしているページは現在表示できません。",
            detail_title="Yahoo! JAPAN - ご覧になろうとしているページは現在表示できません。",
        )
        items = worker.collect_marketplace_active_items(
            page, "yahoo-furima-jp", 25, query="juicy honey"
        )
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["title"], correct_title)
        self.assertEqual(page.goto_calls, [])

    def test_yahoo_furima_active_recovers_title_from_search_card_without_detail(self):
        correct_title = (
            "鈴木ふみ奈5 ～COLORS～ コスチュームカード01A "
            "#46/90 (ホワイトシャツ) /WooHoo トレカ"
        )
        page = _YahooFurimaDetailPage(
            [{
                "url": "https://paypayfleamarket.yahoo.co.jp/item/f1236897268",
                "title": "1,580円\n\nいいね！",
                "text": "1,580円\n\nいいね！\n" + correct_title,
                "accessibleText": "",
                "image": "https://img.example/f1236897268.jpg",
            }],
            body="ご覧になろうとしているページは現在表示できません。",
            detail_title="Yahoo! JAPAN - ご覧になろうとしているページは現在表示できません。",
        )
        items = worker.collect_marketplace_active_items(
            page, "yahoo-furima-jp", 25, query="woohoo"
        )
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["title"], correct_title)
        self.assertEqual(page.goto_calls, [])

    def test_yahoo_furima_rejects_rate_limit_page_as_detail_title(self):
        self.assertEqual(
            worker.clean_marketplace_detail_title(
                "Yahoo! JAPAN - ご覧になろうとしているページは現在表示できません。",
                "yahoo-furima-jp",
            ),
            "",
        )

    def test_active_relevance_rejects_apparel_but_keeps_collectible_cheki(self):
        self.assertFalse(
            worker.active_listing_is_relevant(
                "初音ミク コスプレ 大人 セクシー 水着 衣装 VOCALOID M",
                "販売中 3,000円",
                query="CJ SEXY",
            )
        )
        self.assertTrue(
            worker.active_listing_is_relevant(
                "鈴木ふみ奈5 ～COLORS～ 1of1 水着オフショットチェキ /WooHoo",
                "販売中 3,000円",
                query="woohoo",
            )
        )

    def test_active_relevance_keeps_card_bundle_with_poster_bonus(self):
        self.assertTrue(
            worker.active_listing_is_relevant(
                "CJ SEXY CARD SERIES VOL.137 OFFICIAL CARD 限定ポスター付き",
                "販売中 3,000円",
                query="CJ SEXY",
            )
        )

    def test_active_relevance_ignores_result_card_chrome(self):
        result_card_chrome = (
            "CJ SEXY CARD SERIES\nACTIVE SAMPLE\n販売中 3,000円"
        )
        for title in (
            "DX Nintendo Switch ニンテンドースイッチ",
            "バンダナ柄逆十字 スナップバックキャップ 黒 666486",
            "20th Anniversary LIVE! LIVE会場限定グッズ ホログラム缶バッジ キュアフォーチュン",
            "AGF Blendy ブレンディ 詰替200g",
            "Dr.ゼノ",
            "MOBILITY JOINT GUNDAM 8 ゲルググメテオース 一般機＆EXパーツ 2種セット",
        ):
            self.assertFalse(
                worker.active_listing_is_relevant(
                    title, result_card_chrome, query="cj sexy"
                ),
                title,
            )

    def test_mercari_search_removes_literal_quotes_and_generic_hint(self):
        url = worker.build_search_url(
            "mercari-jp",
            '"WooHoo Girls Series" "～INFINITY～" "虹咲カリナ" "トレカ"',
            25,
        )
        self.assertNotIn("%22", url)
        self.assertNotIn("%E3%83%88%E3%83%AC%E3%82%AB", url)
        self.assertIn("keyword=woohoo", url)
        self.assertIn("status=sold_out", url)

    def test_mercari_default_series_urls_match_public_search_filters(self):
        woohoo = worker.build_search_url("mercari-jp", "woohoo", 25)
        cj_sexy = worker.build_search_url("mercari-jp", "CJ SEXY", 25)
        juicy = worker.build_search_url("mercari-jp", "JUICY HONEY", 25)
        hits = worker.build_search_url("mercari-jp", "HIT'S", 25)
        hits_japanese = worker.build_search_url("mercari-jp", "ヒッツ", 25)
        self.assertIn("keyword=woohoo&status=sold_out", woohoo)
        self.assertIn("keyword=cj%20sexy&status=sold_out", cj_sexy)
        self.assertIn(
            "keyword=juicy%20honey&status=sold_out&category_id=7325",
            juicy,
        )
        self.assertIn("keyword=HIT%27S&status=sold_out", hits)
        self.assertIn("keyword=%E3%83%92%E3%83%83%E3%83%84&status=sold_out", hits_japanese)
        self.assertFalse(
            worker.mercari_title_matches_series("Publicity, Publicity, Woohoooow!", "woohoo")
        )
        self.assertTrue(
            worker.mercari_title_matches_series("斎藤恭代 WooHoo LUMINOUS", "woohoo")
        )
        self.assertTrue(
            worker.mercari_title_matches_series("ＲａＭｕ ＨＩＴ'Ｓ ヒッツ トレカ", "HITS")
        )
        self.assertTrue(
            worker.active_listing_is_relevant(
                "ＲａＭｕ ＨＩＴ'Ｓ ヒッツ トレカ",
                "販売中 4,200円",
                query="HITS",
            )
        )
        for title in (
            "平嶋夏海 HITS 生キスカード A #29/95",
            "HITS 直筆サイン入り特典カード A",
        ):
            self.assertTrue(
                worker.active_listing_is_relevant(title, "販売中 4,200円", query="HITS"),
                title,
            )
        for title in (
            "HITS LIMITED RaMu photo book",
            "HITS baseball card collection",
            "NEW LISTING HITS Card 2026",
            "NEW LISTING HITS Card 2025",
            "HITS RaMu CD",
            "HITS トレーディングカード バインダー",
            "HITS RaMu",
            "三代目 J SOUL BROTHERS from EXILE TRIBE / 山下健二郎 / LDH LIVE-EXPO 2024-EXILE TRIBE BEST HITSノ フォトカード",
            "ビリー・ジョエル 「ビリー・ザ・ベスト(Greatest Hits Volume I & Volume II)」 品番:CSCS-5071/2 歌詞カード傷み",
        ):
            self.assertFalse(
                worker.active_listing_is_relevant(title, "販売中 4,200円", query="HITS"),
                title,
            )

    def test_mercari_mixed_mode_requests_active_and_sold_filters(self):
        url = worker.build_search_url("mercari-jp", "woohoo", 25, mode="mixed")
        self.assertIn("keyword=woohoo&status=sold_out%7Con_sale", url)
        active_url = worker.build_search_url("mercari-jp", "woohoo", 25, mode="active")
        self.assertIn("keyword=woohoo&status=on_sale", active_url)

    def test_mercari_active_stream_never_uses_sold_only_filter(self):
        active_url = worker.build_search_url("mercari-jp", "woohoo", 25, mode="active")
        mixed_url = worker.build_search_url("mercari-jp", "woohoo", 25, mode="mixed")
        self.assertIn("status=on_sale", active_url)
        self.assertNotIn("status=sold_out", active_url)
        self.assertIn("status=sold_out%7Con_sale", mixed_url)

    def test_yahoo_keeps_phrase_quotes_supported_by_closed_search(self):
        url = worker.build_search_url(
            "yahoo-auctions-jp", '"JUICY HONEY" 29 "石川澪"', 25
        )
        self.assertIn("%22JUICY%20HONEY%22", url)

    def test_marketplace_pagination_uses_current_page_parameters(self):
        mercari_url = worker.build_search_url("mercari-jp", "JUICY HONEY", 25)
        self.assertEqual(
            worker.with_marketplace_page("mercari-jp", mercari_url, 1, 25),
            mercari_url,
        )
        self.assertIn(
            "page_token=v1%3A1",
            worker.with_marketplace_page("mercari-jp", mercari_url, 2, 25),
        )

        aucfan_url = worker.build_search_url("aucfan", "JUICY HONEY", 25)
        self.assertTrue(
            worker.with_marketplace_page("aucfan", aucfan_url, 2, 25).endswith("?p=2")
        )

        ruten_url = worker.build_search_url("ruten-tw", "trading card", 25)
        self.assertTrue(
            worker.with_marketplace_page("ruten-tw", ruten_url, 2, 25).endswith("&p=2")
        )

        naver_url = worker.build_search_url("naver-shopping-kr", "trading card", 25)
        naver_page = worker.with_marketplace_page(
            "naver-shopping-kr", naver_url, 2, 25
        )
        self.assertIn("pagingIndex=2", naver_page)
        self.assertIn("pagingSize=25", naver_page)

        shopee_url = worker.build_search_url("shopee-tw", "trading card", 25)
        self.assertTrue(
            worker.with_marketplace_page("shopee-tw", shopee_url, 1, 25).endswith("&page=0")
        )

    def test_rakuten_girls_taiwan_queries_use_chinese_marketplace_terms(self):
        query = "2025 Rakuten Girls collectible cards"
        self.assertEqual(
            worker.taiwan_marketplace_search_query(query),
            "2025 樂天女孩卡",
        )
        self.assertIn(
            "q=2025%20%E6%A8%82%E5%A4%A9%E5%A5%B3%E5%AD%A9%E5%8D%A1",
            worker.build_search_url("ruten-tw", query, 25, mode="active"),
        )
        self.assertIn(
            "keyword=2025%20%E6%A8%82%E5%A4%A9%E5%A5%B3%E5%AD%A9%E5%8D%A1",
            worker.build_search_url("shopee-tw", query, 25, mode="active"),
        )
        self.assertIn(
            "_nkw=2025%20Rakuten%20Girls%20collectible%20cards",
            worker.build_search_url("ebay", query, 25, mode="active"),
        )
        self.assertTrue(
            worker.active_listing_is_relevant(
                "2025 樂天女孩卡 精裝盒",
                "現貨 NT$3,150",
                query="2025 樂天女孩卡",
                aliases=["2025 Rakuten Girls", "2025 樂天女孩卡"],
            )
        )
        self.assertFalse(
            worker.active_listing_is_relevant(
                "2022 樂天女孩卡 平裝盒",
                "現貨 NT$20,000",
                query="2025 樂天女孩卡",
                aliases=["2025 Rakuten Girls", "2025 樂天女孩卡"],
            )
        )

    def test_collectors_do_not_drop_rendered_rows_above_requested_page_size(self):
        active_cards = [
            {
                "url": f"https://jp.mercari.com/item/active-{index}",
                "title": f"WooHoo trading card {index}",
                "text": "販売中 ¥1,000 トレカ",
                "image": "",
            }
            for index in range(2)
        ]
        active_items = worker.collect_marketplace_active_items(
            _GenericPage(active_cards), "mercari-jp", 1, query="woohoo"
        )
        self.assertEqual(len(active_items), 2)

        sold_cards = [
            {
                "url": f"https://jp.mercari.com/item/sold-{index}",
                "title": f"JUICY HONEY trading card {index}",
                "text": "売り切れ ¥1,000 トレカ",
                "updateTime": "2026-08-18T12:00:00+09:00",
                "image": "",
            }
            for index in range(2)
        ]
        sold_items = worker.collect_marketplace_completed_items(
            _GenericPage(sold_cards), "mercari-jp", 1, query="juicy honey"
        )
        self.assertEqual(len(sold_items), 2)

    def test_generic_marketplace_requires_sold_state_date_and_price(self):
        page = _GenericPage([{
            "url": "https://jp.mercari.com/item/m123",
            "title": "JUICY HONEY PLUS #29 card",
            "text": "売り切れ ¥3,500 2026年1月2日",
            "soldAt": "",
            "image": "https://img.example/m123.jpg",
        }])
        items = worker.collect_marketplace_completed_items(
            page, "mercari-jp", 25, query='"JUICY HONEY"'
        )
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["externalListingId"], "m123")
        self.assertEqual(items[0]["originalCurrencyCode"], "JPY")
        self.assertEqual(items[0]["statusEvidence"], "sold_out_badge_observed_at")
        self.assertEqual(items[0]["soldAtEvidence"], "first_observed_sold")
        self.assertEqual(items[0]["saleType"], "completed")

    def test_mercari_reads_status_title_and_jpy_price_from_accessible_label(self):
        page = _GenericPage([{
            "url": "https://jp.mercari.com/item/m76722888865",
            "title": "RM\n40.29\n虹咲カリナ ～INFINITY～ 生写真カード06",
            "text": "RM\n40.29\n虹咲カリナ ～INFINITY～ 生写真カード06",
            "accessibleText": (
                "虹咲カリナ ～INFINITY～ 生写真カード06の画像 "
                "売り切れ 1,480円 RM40.29"
            ),
            "updateTime": "2026-08-14T12:00:00+09:00",
            "image": "https://img.example/m767.jpg",
        }])
        diagnostics = {}
        items = worker.collect_marketplace_completed_items(
            page,
            "mercari-jp",
            25,
            query='"WooHoo Girls Series" "～INFINITY～" "虹咲カリナ"',
            diagnostics=diagnostics,
        )
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["title"], "虹咲カリナ ～INFINITY～ 生写真カード06")
        self.assertEqual(items[0]["originalPriceAmount"], 1480.0)
        self.assertEqual(items[0]["originalCurrencyCode"], "JPY")
        self.assertEqual(items[0]["soldAtEvidence"], "update_time")
        self.assertEqual(items[0]["soldAt"], "2026-08-14T03:00:00Z")
        self.assertEqual(json.loads(items[0]["rawPayload"])["updateTime"], "2026-08-14T12:00:00+09:00")
        self.assertEqual(diagnostics["renderedCandidates"], 1)
        self.assertEqual(diagnostics["soldCandidates"], 1)

    def test_mercari_update_time_accepts_embedded_unix_milliseconds(self):
        self.assertEqual(
            worker.extract_mercari_update_time(
                None, '{"updateTime": 1786665600000}'
            ),
            "2026-08-14T00:00:00Z",
        )

    def test_mercari_simple_series_query_keeps_sold_card_without_literal_series_title(self):
        page = _GenericPage([{
            "url": "https://jp.mercari.com/item/m96254653281",
            "title": "RM\n108.97\nCJ137 小日向みゆう オフィシャルカードコレクション",
            "text": "RM\n108.97\nCJ137 小日向みゆう オフィシャルカードコレクション",
            "accessibleText": (
                "CJ137 小日向みゆう オフィシャルカードコレクションの画像 "
                "売り切れ 3,999円 RM108.97"
            ),
            "soldAt": "",
            "image": "https://img.example/m962.jpg",
        }])
        diagnostics = {}
        items = worker.collect_marketplace_completed_items(
            page, "mercari-jp", 25, query="cj sexy", diagnostics=diagnostics
        )
        self.assertEqual(len(items), 1)
        self.assertEqual(diagnostics.get("queryMismatch", 0), 0)

    def test_hits_sold_query_rejects_non_card_results_with_hits_keyword(self):
        page = _GenericPage([
            {
                "url": "https://jp.mercari.com/item/hits-card",
                "title": "RaMu HITS LIMITED トレカ",
                "text": "売り切れ ¥4,200",
                "updateTime": "2026-08-18T12:00:00+09:00",
                "image": "",
            },
            {
                "url": "https://jp.mercari.com/item/hits-baseball",
                "title": "HITS baseball card collection",
                "text": "売り切れ ¥4,200",
                "updateTime": "2026-08-18T12:00:00+09:00",
                "image": "",
            },
            {
                "url": "https://jp.mercari.com/item/hits-athlete",
                "title": "HITS 公式アスリートカード2023 直筆サインカード",
                "text": "売り切れ ¥4,200",
                "updateTime": "2026-08-18T12:00:00+09:00",
                "image": "",
            },
        ])
        diagnostics = {}
        items = worker.collect_marketplace_completed_items(
            page, "mercari-jp", 25, query="HITS", diagnostics=diagnostics
        )
        self.assertEqual([item["externalListingId"] for item in items], ["hits-card"])
        self.assertEqual(diagnostics.get("queryMismatch"), 2)

    def test_broad_series_sold_queries_reject_generic_cards_and_media(self):
        page = _GenericPage([
            {
                "url": "https://jp.mercari.com/item/cj-good",
                "title": "CJ SEXY CARD SERIES VOL.137 小日向みゆう トレカ",
                "text": "売り切れ ¥3,999",
                "updateTime": "2026-08-18T12:00:00+09:00",
                "image": "",
            },
            {
                "url": "https://jp.mercari.com/item/cj-generic",
                "title": "紗倉まな あなたに夢中なの オフィシャルカードコレクション",
                "text": "売り切れ ¥2,999",
                "updateTime": "2026-08-18T12:00:00+09:00",
                "image": "",
            },
            {
                "url": "https://jp.mercari.com/item/cj-media",
                "title": "CJ SEXY 音楽CD",
                "text": "売り切れ ¥1,999",
                "updateTime": "2026-08-18T12:00:00+09:00",
                "image": "",
            },
        ])
        diagnostics = {}
        items = worker.collect_marketplace_completed_items(
            page, "mercari-jp", 25, query="cj sexy", diagnostics=diagnostics
        )
        self.assertEqual([item["externalListingId"] for item in items], ["cj-good"])
        self.assertEqual(diagnostics.get("queryMismatch"), 1)
        self.assertEqual(diagnostics.get("irrelevantSoldCandidates"), 1)

    def test_broad_juicy_query_keeps_packaging_and_rejects_model_only_card(self):
        page = _GenericPage([
            {
                "url": "https://jp.mercari.com/item/juicy-good",
                "title": "JUICY HONEY 4パックセット",
                "text": "売り切れ ¥4,500",
                "updateTime": "2026-08-18T12:00:00+09:00",
                "image": "",
            },
            {
                "url": "https://jp.mercari.com/item/juicy-generic",
                "title": "瀬戸環奈 カード",
                "text": "売り切れ ¥1,500",
                "updateTime": "2026-08-18T12:00:00+09:00",
                "image": "",
            },
        ])
        items = worker.collect_marketplace_completed_items(
            page, "mercari-jp", 25, query="juicy honey"
        )
        self.assertEqual([item["externalListingId"] for item in items], ["juicy-good"])

    def test_mercari_sold_badge_without_exact_date_uses_first_observed_time(self):
        page = _GenericPage([{
            "url": "https://jp.mercari.com/item/m76722888865",
            "title": "虹咲カリナ ～INFINITY～ 生写真カード06",
            "text": "RM 40.29 虹咲カリナ ～INFINITY～ 生写真カード06",
            "accessibleText": "虹咲カリナ ～INFINITY～ 生写真カード06の画像 売り切れ 1,480円",
            "soldAt": "",
            "image": "",
        }])
        diagnostics = {}
        items = worker.collect_marketplace_completed_items(
            page, "mercari-jp", 25, diagnostics=diagnostics
        )
        self.assertEqual(len(items), 1)
        self.assertEqual(diagnostics["soldCandidates"], 1)
        self.assertEqual(diagnostics["observedSoldDate"], 1)
        self.assertEqual(items[0]["statusEvidence"], "sold_out_badge_observed_at")
        self.assertEqual(items[0]["soldAtEvidence"], "first_observed_sold")

    def test_mercari_sold_price_falls_back_to_search_card_after_detail_visit(self):
        page = _YahooFurimaDetailPage([{
            "url": "https://jp.mercari.com/item/m-price-fallback",
            "title": "WooHoo sold card",
            "text": "WooHoo sold card",
            "accessibleText": "売り切れ 3,500円",
            "soldAt": "",
            "image": "",
        }], body="売り切れ 更新日時の表示なし")
        diagnostics = {}
        items = worker.collect_marketplace_completed_items(
            page, "mercari-jp", 25, query="woohoo", diagnostics=diagnostics
        )
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["originalPriceAmount"], 3500.0)
        self.assertEqual(items[0]["originalCurrencyCode"], "JPY")
        self.assertEqual(diagnostics.get("missingFinalPrice", 0), 0)

    def test_mercari_sold_badge_without_exact_date_is_rejected_for_bounded_scan(self):
        page = _GenericPage([{
            "url": "https://jp.mercari.com/item/m76722888865",
            "title": "虹咲カリナ ～INFINITY～ 生写真カード06",
            "text": "RM 40.29 虹咲カリナ ～INFINITY～ 生写真カード06",
            "accessibleText": "虹咲カリナ ～INFINITY～ 生写真カード06の画像 売り切れ 1,480円",
            "soldAt": "",
            "image": "",
        }])
        diagnostics = {}
        items = worker.collect_marketplace_completed_items(
            page,
            "mercari-jp",
            25,
            from_bound=datetime(2026, 8, 1, tzinfo=timezone.utc),
            diagnostics=diagnostics,
        )
        self.assertEqual(items, [])
        self.assertEqual(diagnostics["missingSoldDate"], 1)

    def test_aucfan_sold_card_with_yen_suffix_is_importable(self):
        page = _GenericPage([{
            "url": "https://aucfan.com/item/auc123",
            "title": "JUICY HONEY PLUS #29 card",
            "text": "落札 3,500円 落札日 2026/01/02",
            "soldAt": "",
            "image": "https://img.example/auc123.jpg",
        }])
        items = worker.collect_marketplace_completed_items(
            page, "aucfan", 25, query='"JUICY HONEY" 29 "trading card"'
        )
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["externalListingId"], "auc123")
        self.assertEqual(items[0]["originalPriceAmount"], 3500.0)
        self.assertEqual(items[0]["originalCurrencyCode"], "JPY")

    def test_aucfan_history_heading_supplies_status_context_for_result_rows(self):
        page = _GenericPage([{
            "url": "https://aucview.aucfan.com/yahoo/x123/",
            "title": "楓ふうあ ジューシーハニー PLUS #16",
            "text": "4,465円 55件 2022年10月27日",
            "soldAt": "",
            "image": "",
        }], body="2022年10月の落札済み商品 落札日 入札数 落札価格")
        items = worker.collect_marketplace_completed_items(
            page, "aucfan", 25, query='"JUICY HONEY" "Vol. 16" "楓ふうあ"'
        )
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["externalListingId"], "x123")
        self.assertEqual(items[0]["originalPriceAmount"], 4465.0)

    def test_generic_search_hints_do_not_require_hint_in_listing_title(self):
        self.assertTrue(
            worker.title_matches_query(
                "CJ SEXY CARD SERIES VOL. 137 Model A",
                '"CJ SEXY CARD SERIES" "Vol. 137" "Model A" "trading card"',
            )
        )

    def test_active_listing_relevance_rejects_figures_and_cosmetics(self):
        self.assertFalse(
            worker.active_listing_is_relevant(
                "[CJ-892] 1/64 セクシーガール フィギュア ミニチュア ジオラマ",
                "現在価格 1,860円",
                query="cj sexy",
            )
        )
        self.assertFalse(
            worker.active_listing_is_relevant(
                "新品 rom&nd ジューシーハニースティングティント 29 36 38",
                "コスメ 美容 ティント",
                query="juicy honey",
            )
        )

    def test_active_listing_relevance_accepts_trading_card_title(self):
        self.assertTrue(
            worker.active_listing_is_relevant(
                "CJ SEXY CARD SERIES VOL. 137 小日向みゆう トレカ",
                "販売中 3,999円",
                query="cj sexy",
            )
        )

    def test_active_listing_keeps_result_image_for_telegram_payload(self):
        page = _GenericPage([{
            "url": "https://fril.jp/item/rakuma-card-1",
            "title": "JUICY HONEY PLUS #29 トレカ",
            "text": "販売中 2,000円 JUICY HONEY PLUS #29 トレカ",
            "image": "https://img.example/rakuma-card-1.jpg",
        }])
        items = worker.collect_marketplace_active_items(
            page, "rakuma", 25, query="juicy honey"
        )
        self.assertEqual(len(items), 1)
        self.assertEqual(
            json.loads(items[0]["imageReferences"]),
            ["https://img.example/rakuma-card-1.jpg"],
        )

    def test_image_reference_prefers_lazy_photo_over_rakuma_placeholder(self):
        self.assertEqual(
            worker.first_usable_image_reference(
                "https://asset.fril.jp/assets/new_web/item_square_dummy-example.png",
                "https://img.fril.jp/img/123/m/456.jpg?789",
            ),
            "https://img.fril.jp/img/123/m/456.jpg?789",
        )
        self.assertEqual(
            worker.first_usable_image_reference(
                "https://asset.fril.jp/assets/new_web/item_square_dummy-example.png",
            ),
            "",
        )

    def test_series_search_phrase_can_be_omitted_when_release_and_person_match(self):
        self.assertTrue(
            worker.title_matches_query(
                "虹咲カリナ ～INFINITY～ 生写真カード06",
                '"WooHoo Girls Series" "～INFINITY～" "虹咲カリナ"',
            )
        )

    def test_quoted_volume_matches_hash_volume_in_title(self):
        self.assertTrue(
            worker.title_matches_query(
                "石川澪 JUICY HONEY PLUS #29 card",
                '"JUICY HONEY" "Vol. 29" "石川澪"',
            )
        )

    def test_juicy_honey_edition_qualifier_prevents_volume_collision(self):
        query = '"JUICY HONEY" "PLUS" 29'
        self.assertTrue(
            worker.title_matches_query("石川澪 JUICY HONEY PLUS #29 card", query)
        )
        self.assertFalse(
            worker.title_matches_query("小島みなみ JUICY HONEY VOL.29 card", query)
        )

    def test_juicy_honey_named_edition_requires_name_and_year(self):
        query = '"JUICY HONEY" "LUXURY" "2026"'
        self.assertTrue(
            worker.title_matches_query("JUICY HONEY THE LUXURY EDITION 2026 box", query)
        )
        self.assertFalse(
            worker.title_matches_query("JUICY HONEY THE DELUXE 2026 box", query)
        )

    def test_japanese_series_alias_is_a_discovery_hint(self):
        self.assertTrue(
            worker.title_matches_query(
                "ジューシーハニー LUXURY EDITION 2026 box",
                '"ジューシーハニー" "LUXURY" "2026"',
            )
        )
        self.assertTrue(
            worker.title_matches_query(
                "CJ SEXY CARD SERIES VOL. 137 小日向みゆう",
                '"CJ トレカ" 137 "小日向みゆう"',
            )
        )
        self.assertTrue(
            worker.title_matches_query(
                "ＲａＭｕ ＨＩＴ'Ｓ ヒッツ トレカ",
                '"HIT\'S" "RaMu"',
            )
        )

    def test_japanese_yen_suffix_is_parsed_for_japan_marketplaces(self):
        price, currency = worker.extract_price(
            None, "売り切れ 3,500円", "mercari-jp"
        )
        self.assertEqual(price, 3500.0)
        self.assertEqual(currency, "JPY")

    def test_marketplace_external_ids_use_stable_item_segments(self):
        self.assertEqual(
            worker.extract_marketplace_external_id(
                "https://www.ebay.com/itm/123456789/card", "ebay"
            ),
            "123456789",
        )

    def test_retail_and_aggregate_platforms_do_not_fake_sold_listings(self):
        self.assertEqual(worker.sold_evidence("品切れ中 ¥3,500", "surugaya"), "")
        self.assertEqual(worker.sold_evidence("Market Price $3.50", "tcgplayer"), "")

    def test_marketplace_sold_markers_are_not_interchangeable(self):
        self.assertEqual(
            worker.sold_evidence("落札額 3,500円 落札日 2026/01/02", "aucfan"),
            "aucfan_winning_bid",
        )
        self.assertEqual(
            worker.sold_evidence("落札 3,500円 2026/01/02", "aucfan"),
            "aucfan_winning_bid",
        )
        self.assertEqual(
            worker.sold_evidence("最低落札価格 3,500円", "aucfan"),
            "",
        )
        self.assertEqual(
            worker.sold_evidence("落札価格 3,500円", "mandarake"),
            "mandarake_winning_bid",
        )
        self.assertEqual(
            worker.sold_evidence("Ended Jan 2, 2026 $35.00", "mandarake"),
            "",
        )
        self.assertEqual(
            worker.sold_evidence("Sold for US $35.00 Aug 1, 2026", "ebay"),
            "ebay_sold_label",
        )
        self.assertEqual(
            worker.sold_evidence("Ended Aug 1, 2026 US $35.00", "ebay"),
            "",
        )

    def test_title_sold_words_do_not_count_as_a_badge(self):
        self.assertEqual(
            worker.sold_evidence(
                "JUICY HONEY SOLD OUT EDITION ¥3,500 2026/01/02",
                "mercari-jp",
                title="JUICY HONEY SOLD OUT EDITION",
            ),
            "",
        )
        self.assertEqual(
            worker.sold_evidence(
                "JUICY HONEY SOLD OUT EDITION 売り切れ ¥3,500 2026/01/02",
                "mercari-jp",
                title="JUICY HONEY SOLD OUT EDITION",
            ),
            "sold_out_badge",
        )

    def test_mercari_english_sold_sticker_counts_as_sold_evidence(self):
        self.assertEqual(
            worker.sold_evidence(
                "SOLD ¥3,500",
                "mercari-jp",
                title="CJ SEXY CARD SERIES VOL.126",
            ),
            "sold_out_badge",
        )

    def test_marketplace_price_type_matches_sale_mechanism(self):
        self.assertEqual(
            worker.marketplace_price_type("ebay", "ebay_sold_label", "Sold for US $35"),
            "fixed_price_sold",
        )
        self.assertEqual(
            worker.marketplace_price_type("ebay", "ebay_sold_label", "Sold auction bid US $35"),
            "auction_hammer",
        )
        self.assertEqual(
            worker.marketplace_price_type(
                "ebay",
                "ebay_sold_label",
                "Auction Edition Sold for US $35",
                title="Auction Edition",
            ),
            "fixed_price_sold",
        )
        self.assertEqual(
            worker.marketplace_price_type("mandarake", "mandarake_winning_bid", "落札価格 3500円"),
            "auction_hammer",
        )

    def test_yahoo_active_price_uses_current_bid_and_separates_buy_now(self):
        current, buy_now = worker.extract_yahoo_active_prices(
            "開始価格 500円 現在価格 1,200円 即決価格 2,000円"
        )
        self.assertEqual(current, 1200.0)
        self.assertEqual(buy_now, 2000.0)

    def test_yahoo_active_price_does_not_use_unlabeled_starting_bid(self):
        current, buy_now = worker.extract_yahoo_active_prices("開始価格 500円 入札 0")
        self.assertIsNone(current)
        self.assertIsNone(buy_now)

    def test_yahoo_sold_evidence_rejects_reserve_and_no_winner_labels(self):
        self.assertEqual(
            worker.sold_evidence("最低落札価格 5,000円 終了", "yahoo-auctions-jp"),
            "",
        )
        self.assertEqual(
            worker.sold_evidence("落札者なし 終了", "yahoo-auctions-jp"),
            "",
        )
        self.assertEqual(
            worker.sold_evidence("未落札 終了", "yahoo-auctions-jp"),
            "",
        )

    def test_yahoo_active_detail_copy_does_not_count_as_sold(self):
        self.assertEqual(
            worker.sold_evidence(
                "現在 11,000円 即決 11,800円 2日 今すぐ落札 ご落札後48時間以内のご入金 落札時に佐川急便を選択",
                "yahoo-auctions-jp",
            ),
            "",
        )

    def test_yahoo_completed_card_requires_end_and_final_price(self):
        end = int(datetime(2026, 1, 2, 3, 4, tzinfo=timezone.utc).timestamp() * 1000)
        page = _YahooPage([
            {
                "url": "https://page.auctions.yahoo.co.jp/jp/auction/x123",
                "title": "JUICY HONEY Collection Cards Vol. 30 小島みなみ",
                "text": "落札 3,500円",
                "tracking": f"end:{end};p=3500",
                "image": "https://img.example/x123.jpg",
            },
            {
                "url": "https://page.auctions.yahoo.co.jp/jp/auction/no-price",
                "title": "No final price",
                "text": "終了",
                "tracking": f"end:{end}",
                "image": "",
            },
            {
                "url": "https://page.auctions.yahoo.co.jp/jp/auction/ended-unsold",
                "title": "Ended without winner",
                "text": "終了 3,500円",
                "tracking": f"end:{end};p=3500",
                "image": "",
            },
        ])
        items = worker.collect_yahoo_completed_items(
            page, 25, query='"JUICY HONEY Collection Cards Vol. 30" "小島みなみ"'
        )
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["externalListingId"], "x123")
        self.assertEqual(items[0]["dataProviderCode"], "yahoo-auctions-jp")
        self.assertEqual(items[0]["statusEvidence"], "ended_with_winner")
        self.assertEqual(items[0]["priceType"], "auction_hammer")
        self.assertEqual(json.loads(items[0]["rawPayload"])["marketplaceCode"], "yahoo-auctions-jp")

    def test_yahoo_unquoted_volume_token_rejects_neighboring_volume(self):
        self.assertTrue(
            worker.title_matches_query(
                "JUICY HONEY PLUS #9 card",
                '"JUICY HONEY" 9',
            )
        )
        self.assertFalse(
            worker.title_matches_query(
                "JUICY HONEY PLUS #29 card",
                '"JUICY HONEY" 9',
            )
        )
        self.assertFalse(
            worker.title_matches_query(
                "JUICY HONEY autograph photo",
                '"JUICY HONEY" 9',
            )
        )

    def test_yahoo_accepts_japanese_completed_heading_and_price_text(self):
        worker.ensure_search_page_usable(
            _PageWithBody("落札された商品を表示しています"), "yahoo-auctions-jp"
        )
        end = int(datetime(2026, 1, 2, tzinfo=timezone.utc).timestamp())
        page = _YahooPage([{
            "url": "https://page.auctions.yahoo.co.jp/jp/auction/text-price",
            "title": "JUICY HONEY test card",
            "text": "落札 4,800円",
            "tracking": f"end:{end}",
            "image": "",
        }])
        items = worker.collect_yahoo_completed_items(page, 25)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["originalPriceAmount"], 4800.0)

    def test_yahoo_current_tracking_format_uses_visible_final_price_fallback(self):
        end = int(datetime(2026, 8, 14, 12, 31, tzinfo=timezone.utc).timestamp())
        page = _YahooPage([{
            "url": "https://auctions.yahoo.co.jp/jp/auction/x-live",
            "title": "石川澪 JUICY HONEY PLUS #29 34 トレカ",
            "text": "落札\n89円\n1\n8/14 21:31終了",
            # ``p`` is the displayed current/start price in Yahoo's tracking
            # payload; the rendered 落札 amount is the winning price.
            "tracking": f"_cl_vmodule:aal;etc:p=100,b=1;end:{end};label:1",
            "image": "",
        }])
        items = worker.collect_yahoo_completed_items(
            page, 25, query='"JUICY HONEY" 29 "石川澪"'
        )
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["originalPriceAmount"], 89.0)
        self.assertEqual(items[0]["soldAt"], "2026-08-14T12:31:00Z")

    def test_yahoo_rejects_search_result_that_omits_release_phrase(self):
        end = int(datetime(2026, 1, 2, tzinfo=timezone.utc).timestamp())
        page = _YahooPage([
            {
                "url": "https://page.auctions.yahoo.co.jp/jp/auction/x123",
                "title": "岸明日香 切り抜き",
                "text": "落札 100円",
                "tracking": f"end:{end};p=100",
                "image": "",
            },
        ])
        items = worker.collect_yahoo_completed_items(
            page, 25, query='"WooHoo Girls Vol. 1" "岸明日香"'
        )
        self.assertEqual(items, [])

    def test_yahoo_completed_card_honors_request_date_bounds(self):
        end = int(datetime(2026, 1, 2, tzinfo=timezone.utc).timestamp())
        page = _YahooPage([
            {
                "url": "https://page.auctions.yahoo.co.jp/jp/auction/x123",
                "title": "card",
                "text": "落札 100円",
                "tracking": f"end:{end};p=100",
                "image": "",
            },
        ])
        items = worker.collect_yahoo_completed_items(
            page,
            25,
            from_bound=worker.parse_request_bound("2026-01-03T00:00:00Z", "from"),
        )
        self.assertEqual(items, [])

    def test_unwraps_doorzo_hex_detail_url(self):
        source = "https://www.mercari.com/jp/items/m30875536920/"
        wrapped = (
            "https://www.doorzo.com/en/mall/mercari/detail/"
            + source.encode("utf-8").hex()
            + "/"
        )
        self.assertEqual(worker.unwrap_doorzo_url(wrapped), source)
        self.assertEqual(worker.extract_external_id(wrapped), "m30875536920")

    def test_parses_english_completed_date(self):
        sold_at = worker.extract_sold_date(
            _PageWithoutTime(), "This item Sold Aug 1, 2026 at 9:45 PM"
        )
        self.assertEqual(sold_at, "2026-08-01T21:45:00Z")


if __name__ == "__main__":
    unittest.main()
