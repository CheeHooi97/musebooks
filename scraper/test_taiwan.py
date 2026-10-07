import unittest
from unittest.mock import MagicMock, patch

from marketplace_adapters import resolve_adapter
from photobook_worker import normalize_currency, parse_price, status_for, ensure_rendered_page, SourceBlockedError, collect_anchor_candidates, collect, make_observation, ruten_sold_candidates


class TaiwanTests(unittest.TestCase):
    def test_digital_stores_only_accept_book_details(self):
        for source, host in [('bookwalker-tw', 'www.bookwalker.com.tw'), ('readmoo-tw', 'readmoo.com')]:
            adapter = resolve_adapter(source)
            with self.subTest(source=source):
                url = f'https://{host}/book/123456'
                self.assertTrue(adapter.is_result_url(url))
                self.assertEqual(adapter.extract_external_id(url), '123456')
                if source == 'bookwalker-tw':
                    self.assertTrue(adapter.is_result_url(f'https://{host}/product/308904'))
                for path in ['/login', '/member', '/cart', '/author/123', '/book/', '/']:
                    self.assertFalse(adapter.is_result_url(f'https://{host}{path}'))
                self.assertFalse(adapter.is_result_url(f'https://fake{host.removeprefix("www.")}/book/123456'))

    def test_sold_search_requires_a_verified_surface(self):
        for source in ['shopee-tw', 'yahoo-tw']:
            with self.subTest(source=source), self.assertRaises(ValueError):
                resolve_adapter(source).build_search_url('寫真集', 'sold_discovery', 'physical')

    def test_ruten_default_sold_discovery_and_legacy_links(self):
        adapter = resolve_adapter('ruten-tw')
        self.assertEqual(adapter.build_search_url('寫真集','sold_discovery','physical'),'https://pub.ruten.com.tw/ruten20th/bid.html')
        self.assertEqual(adapter.canonical_result_url('https://www.ruten.com.tw/item/show?62634000007143'),'https://www.ruten.com.tw/item/62634000007143/')

    def test_ruten_sold_index_filters_before_detail_budget(self):
        def card(title, ended=True):
            text = ('競標已結束 0天 00:00:00 ' if ended else '競標中 ') + title + ' $900'
            return {'url':'https://www.ruten.com.tw/item/123456/','title':text,'text':text}
        cards = [card('Figure'),card('Other Model Photobook'),card('Alice Model Photobook',False),card('Alice Model Photobook')]
        result = ruten_sold_candidates(cards,{'query':'Alice photobook'},1)
        self.assertEqual(len(result),1)
        self.assertEqual(result[0]['title'],'Alice Model Photobook')

    def test_ruten_automatic_sold_discovery_verifies_details(self):
        source = {'id':'ruten-tw','region':'TW','kind':'marketplace','allowedHosts':['www.ruten.com.tw']}
        card = {'url':'https://www.ruten.com.tw/item/123456/','title':'競標已結束 0天 00:00:00 Alice Model Photobook $900','text':'競標已結束 Alice Model Photobook $900'}
        detail = {'body':'競標結束 目前出價 $900 得標者 a****9 商品詳情','structured':{'name':'Alice Model Photobook'}}
        with patch('photobook_worker.launch'), patch('photobook_worker.navigate_page') as navigate, patch('photobook_worker.collect_anchor_candidates',return_value=[card]), patch('photobook_worker.next_page_url',return_value=''), patch('photobook_worker.detail_snapshot',return_value=detail):
            batch = collect({'sourceId':'ruten-tw','source':source,'operation':'sold_discovery','query':'Alice photobook','maxCandidates':1,'maxPages':3})
        self.assertEqual(batch['items'][0]['priceMinor'],90000)
        self.assertEqual(batch['diagnostics']['soldDiscoveryMethod'],'public_auction_index')
        self.assertFalse(batch['hasMore'])
        self.assertEqual(navigate.call_count,1)

    def test_books_tracking_links_preserve_product_identity(self):
        adapter = resolve_adapter('books-com-tw')
        url = 'https://search.books.com.tw/redirect/move/key/test/area/mid_name/item/M010241708/page/1/idx/1'
        self.assertTrue(adapter.is_result_url(url))
        self.assertEqual(adapter.extract_external_id(url), 'M010241708')
        self.assertEqual(adapter.canonical_result_url(url), 'https://www.books.com.tw/products/M010241708')

    def test_taiwan_currency_and_invalid_price(self):
        source = {'region': 'TW'}
        self.assertEqual(normalize_currency('元', source), 'TWD')
        self.assertEqual(parse_price('售價 1,200元', {}, source), (120000, 'TWD'))
        self.assertEqual(parse_price('NT$1,200', {'price': 'Infinity'}, source), (120000, 'TWD'))

    def test_unavailable_listing_overrides_purchase_copy(self):
        for marker in ['已售完', '已售出', '售罄', '完售', '無庫存', '缺貨']:
            with self.subTest(marker=marker):
                self.assertEqual(status_for(f'{marker} 立即購買 加入購物車', 'active_discovery')[0], 'ended')
        self.assertEqual(status_for('現貨 銷售 123 已售 10 件', 'sold_discovery')[0], 'unknown')
        self.assertEqual(status_for('現貨 已售出 10 件', 'active_discovery')[0], 'active')

    def test_shopee_login_gate_is_blocked(self):
        with self.assertRaises(SourceBlockedError):
            ensure_rendered_page('看起來您尚未登入。請登入以繼續，或返回首頁。', 'shopee-tw')

    def test_sale_price_wins_over_coupon_and_print_list_price(self):
        self.assertEqual(parse_price('直購價：$680 - $870 滿999現折31元', {}, {'region':'TW'}), (68000, 'TWD'))
        self.assertEqual(parse_price('紙本書定價：NT$350 電子書定價：NT$350 電子書售價：NT$245', {}, {'region':'TW'}), (24500, 'TWD'))

    def test_small_candidate_limit_scans_past_navigation_and_uses_image_alt(self):
        page = MagicMock()
        nav = MagicMock()
        nav.get_attribute.side_effect = lambda name: '/category' if name == 'href' else ''
        anchor = MagicMock()
        anchor.get_attribute.side_effect = lambda name: '/item/123456' if name == 'href' else ''
        anchor.inner_text.return_value = ''
        anchor.locator.return_value.first.get_attribute.side_effect = lambda name: 'Alice Model Photobook' if name == 'alt' else ''
        anchors = page.locator.return_value
        anchors.count.return_value = 101
        anchors.nth.side_effect = lambda index: anchor if index == 100 else nav
        result = collect_anchor_candidates(page, 'https://www.ruten.com.tw/search/test/', {'www.ruten.com.tw'}, resolve_adapter('ruten-tw'), 1)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['title'], 'Alice Model Photobook')

    def test_explicit_false_cannot_enable_retail_scraping(self):
        with patch('photobook_worker.launch', side_effect=RuntimeError('browser reached')):
            with self.assertRaisesRegex(ValueError, 'digital editions only'):
                collect({'sourceId':'books-com-tw', 'source':{'kind':'bookstore','region':'TW','allowedHosts':['search.books.com.tw']},'operation':'active_discovery','marketplaceOnly':False,'format':'physical','query':'寫真集'})

    def test_native_sold_evidence_and_final_price_are_required(self):
        source = {'id':'ruten-tw','region':'TW','kind':'marketplace','allowedFormats':['physical'],'defaultFormat':'physical'}
        candidate = {'url':'https://www.ruten.com.tw/item/123456/','title':'Alice Model Photobook','text':'','imageUrl':''}
        request = {'sourceId':'ruten-tw','format':'physical'}
        for text in ['已結標 $1200','已下架 銷售10 $1200','已成交 $1200']:
            item, reason = make_observation(request, source, candidate, {'body':text,'structured':{'price':1200}}, 'sold_discovery')
            self.assertIsNone(item, text)
        item, reason = make_observation(request, source, candidate, {'body':'已成交 成交價：NT$900','structured':{'price':1200}}, 'sold_discovery')
        self.assertEqual(reason, 'accepted')
        self.assertEqual(item['status'], 'completed')
        self.assertEqual(item['priceMinor'], 90000)
        self.assertEqual(item['currency'], 'TWD')
        self.assertEqual(item['priceType'], 'fixed')

    def test_ruten_candidate_text_cannot_confirm_selected_sale(self):
        source = {'id':'ruten-tw','region':'TW','kind':'marketplace'}
        candidate = {'url':'https://www.ruten.com.tw/item/123456/','title':'Alice Model Photobook','text':'已成交 成交價 NT$900'}
        detail = {'body':'現貨 直購價 NT$1200','structured':{'price':1200}}
        self.assertEqual(make_observation({'sourceId':'ruten-tw'},source,candidate,detail,'sold_discovery')[1], 'sold_status_unverified')

    def test_cancelled_ruten_transaction_is_not_a_sale(self):
        for text in ['交易已取消 已成交 成交價 NT$900', '尚未成交 成交價 NT$900', '訂單取消 已成交 成交價 NT$900']:
            self.assertEqual(status_for(text, 'sold_discovery', 'ruten-tw')[0], 'unknown')

    def test_ruten_unverified_sale_reports_missing_evidence(self):
        source = {'id':'ruten-tw','region':'TW','kind':'marketplace','allowedHosts':['www.ruten.com.tw']}
        candidates = [{'url':'https://www.ruten.com.tw/item/123456/','title':'Alice Model Photobook','text':''}]
        detail = {'body':'商品已下架 銷售1 直購價 NT$100','structured':{'name':'Alice Model Photobook','price':100}}
        with patch('photobook_worker.launch'), patch('photobook_worker.navigate_page'), patch('photobook_worker.collect_anchor_candidates',return_value=candidates), patch('photobook_worker.next_page_url',return_value=''), patch('photobook_worker.detail_snapshot',return_value=detail):
            batch = collect({'sourceId':'ruten-tw','source':source,'operation':'sold_discovery','searchUrl':'https://www.ruten.com.tw/find/?q=photobook','query':'Alice Model Photobook'})
        self.assertEqual(batch['items'], [])
        self.assertEqual(batch['diagnostics']['soldVerification'], 'unverified')
        self.assertTrue(any('final sale price' in warning for warning in batch['warnings']))

    def test_ruten_ended_auction_with_masked_winner_uses_closing_bid(self):
        source = {'id':'ruten-tw','region':'TW','kind':'marketplace'}
        candidate = {'url':'https://www.ruten.com.tw/item/62634000007143/','title':'Alice Model Photobook'}
        body = '競標 競標結束 目前出價 $ 3,660 得標者 m***********6 出價排行紀錄 結標時間 2026/08/26 11:59:59 商品詳情 商品說明'
        item, reason = make_observation({'sourceId':'ruten-tw'}, source, candidate, {'body':body,'structured':{'price':1}}, 'sold_discovery')
        self.assertEqual(reason, 'accepted')
        self.assertEqual(item['priceMinor'], 366000)
        self.assertEqual(item['priceType'], 'auction_hammer')
        for invalid in [body.replace('m***********6','無'), body.replace('競標結束','競標中'), body.replace('目前出價 $ 3,660','起標價 $ 1')]:
            self.assertIsNone(make_observation({'sourceId':'ruten-tw'},source,candidate,{'body':invalid},'sold_discovery')[0])
        self.assertEqual(status_for('競標結束 目前出價 $100 商品詳情 得標者 m****6','sold_discovery','ruten-tw')[0], 'unknown')

    def test_seller_instructions_do_not_mark_selected_listing_sold(self):
        self.assertEqual(status_for('現貨 NT$500 商品說明 交易完成後恕不退貨', 'sold_discovery', 'ruten-tw')[0], 'unknown')

    def test_yahoo_live_completed_book_fields(self):
        source = {'id':'yahoo-tw','region':'TW','kind':'marketplace','allowedFormats':['physical']}
        title = '[小柳懷舊]~絕版寫真 銀幕大特寫2 保證電影電視錄影帶主角 (G1'
        candidate = {'url':'https://tw.bid.yahoo.com/item/101740043019','title':title}
        detail = {
            'body':'競標已結束2026/05/01 21:00:00 結標價格 $1501 次出價 出價增額 20 得標者 Y5316727975(120)',
            'structured':{'name':title,'category':'圖書與雜誌 影視娛樂 寫真集 女藝人','price':150,'availability':'http://schema.org/InStock'},
            'transaction':{'closingPrice':'$150','winner':'Y5316727975(120)'},
        }
        item, reason = make_observation({'sourceId':'yahoo-tw','format':'physical'}, source, candidate, detail, 'sold_discovery')
        self.assertEqual(reason, 'accepted')
        self.assertEqual((item['status'],item['priceMinor'],item['currency'],item['priceType']), ('completed',15000,'TWD','auction_hammer'))
        detail.pop('transaction')
        self.assertEqual(make_observation({'sourceId':'yahoo-tw'}, source, candidate, detail, 'sold_discovery')[1], 'sold_price_unverified')

    def test_yahoo_ended_without_winner_is_not_sold(self):
        for body in ['競標已結束 結標價格 $300 得標者 無', '已成交 成交價 $300 得標者：無']:
            self.assertEqual(status_for(body, 'sold_discovery', 'yahoo-tw')[0], 'unknown')
        self.assertEqual(status_for('競標已結束 結標價格 $150 得標者 Y5316727975(120)', 'sold_discovery', 'yahoo-tw')[0], 'completed')
        self.assertEqual(status_for('競標已結束 結標價格 $150', 'active_discovery', 'yahoo-tw')[0], 'ended')

    def test_final_price_in_seller_instructions_is_not_used(self):
        source = {'id':'ruten-tw','region':'TW','kind':'marketplace'}
        candidate = {'url':'https://www.ruten.com.tw/item/123456/','title':'Alice Model Photobook'}
        detail = {'body':'已成交 商品說明 請以成交價：900支付','structured':{'price':1200}}
        self.assertEqual(make_observation({'sourceId':'ruten-tw'},source,candidate,detail,'sold_discovery')[1], 'sold_price_unverified')

    def test_verified_digital_search_parameters_and_yahoo_pagination(self):
        from urllib.parse import parse_qs, urlparse
        bookwalker = resolve_adapter('bookwalker-tw').build_search_url('林襄', 'active_discovery', 'digital')
        self.assertEqual(parse_qs(urlparse(bookwalker).query), {'w':['林襄']})
        readmoo = resolve_adapter('readmoo-tw').build_search_url('林襄', 'active_discovery', 'digital')
        self.assertEqual(parse_qs(urlparse(readmoo).query)['q'], ['林襄'])
        yahoo = resolve_adapter('yahoo-tw')
        page = yahoo.page_url(yahoo.build_search_url('寫真集','active_discovery','physical'), 2, 60)
        self.assertEqual(parse_qs(urlparse(page).query)['pg'], ['2'])

    def test_restricted_detail_is_skipped_without_losing_public_listing(self):
        source = {'id':'ruten-tw','region':'TW','kind':'marketplace','allowedFormats':['physical'],'defaultFormat':'physical','allowedHosts':['www.ruten.com.tw']}
        candidates = [{'url':f'https://www.ruten.com.tw/item/{item}/','title':'Alice Model Photobook','text':'','imageUrl':''} for item in ['123456','123457']]
        public_detail = {'body':'現貨 直購價 NT$500','structured':{'name':'Alice Model Photobook','price':500,'currency':'TWD'}}
        with patch('photobook_worker.launch'), patch('photobook_worker.navigate_page'), patch('photobook_worker.collect_anchor_candidates', return_value=candidates), patch('photobook_worker.next_page_url',return_value=''), patch('photobook_worker.detail_snapshot', side_effect=[SourceBlockedError('verification required'),public_detail]):
            batch = collect({'sourceId':'ruten-tw','source':source,'operation':'active_discovery','query':'Alice Model Photobook'})
        self.assertEqual(len(batch['items']), 1)
        self.assertEqual(batch['items'][0]['externalId'], '123457')
        self.assertEqual(batch['diagnostics']['blockedDetails'], 1)
        self.assertTrue(any('verification-required' in w for w in batch['warnings']))

    def test_retailer_sold_history_is_not_treated_as_empty_success(self):
        for source_id in ['books-com-tw','bookwalker-tw','readmoo-tw']:
            with self.subTest(source=source_id), self.assertRaisesRegex(ValueError, 'not sold transactions'):
                collect({'sourceId':source_id,'operation':'sold_discovery','url':'https://example.test/book/1','marketplaceOnly':False})

    def test_digital_retail_active_is_enabled(self):
        with patch('photobook_worker.launch', side_effect=RuntimeError('browser reached')), self.assertRaisesRegex(RuntimeError,'browser reached'):
            collect({'sourceId':'readmoo-tw','source':{'region':'TW','kind':'digital_store','allowedHosts':['readmoo.com'],'defaultFormat':'digital'},'operation':'active_discovery','query':'林襄'})


if __name__ == '__main__':
    unittest.main()
