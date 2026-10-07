import unittest
from unittest.mock import MagicMock, patch
from urllib.parse import parse_qs, urlparse

from marketplace_adapters import resolve_adapter
from photobook_worker import collect, make_observation, status_for, SourceBlockedError, ensure_rendered_page, detail_snapshot, NavigationRateLimiter


class JapanTests(unittest.TestCase):
    def observation(self, source_id, body, operation, availability='', price=1760, category=''):
        source = {'id':source_id,'region':'JP','kind':'marketplace','allowedFormats':['physical']}
        urls = {'yahoo-auctions-jp':'https://auctions.yahoo.co.jp/jp/auction/q1243985894',
                'mercari-jp':'https://jp.mercari.com/item/m93190924618',
                'rakuma':'https://item.fril.jp/5b53076cb0ccb56fe2620973d9d33d32',
                'yahoo-furima-jp':'https://paypayfleamarket.yahoo.co.jp/item/z675632342'}
        detail = {'body':body,'structured':{'name':'えなこ 写真集','price':price,'currency':'JPY','availability':availability,'category':category}}
        return make_observation({'sourceId':source_id,'humanModelKeywords':['えなこ']},source,
                                {'url':urls[source_id],'title':'えなこ 写真集','text':'SOLD recommendation'},detail,operation)

    def test_japanese_active_controls(self):
        for source, label in [('yahoo-auctions-jp','入札する'),('rakuma','購入に進む'),('yahoo-furima-jp','購入手続きへ')]:
            self.assertEqual(status_for(label,'active_discovery',source)[0], 'active')

    def test_ended_yahoo_with_bids_has_hammer_price(self):
        item, reason = self.observation('yahoo-auctions-jp','現在 1,760円 送料 230円 2件 9月23日22時53分 終了','sold_discovery',price=1)
        self.assertEqual(reason,'accepted')
        self.assertEqual((item['status'],item['priceMinor'],item['currency'],item['priceType']),('completed',1760,'JPY','auction_hammer'))

    def test_yahoo_zero_bid_ended_auction_is_not_a_sale(self):
        for body in ['現在 100円 0件 終了','現在 100円 2件 終了予定 入札する','現在 100円 2件 終了 落札者なし','現在 100円 2件 終了 オークションが取り消されました']:
            self.assertEqual(self.observation('yahoo-auctions-jp',body,'sold_discovery')[1], 'sold_status_unverified')

    def test_active_yahoo_has_current_price(self):
        item, reason = self.observation('yahoo-auctions-jp','現在 3500円 入札する','active_discovery',price=3500)
        self.assertEqual((reason,item['status'],item['priceMinor'],item['priceType']),('accepted','active',3500,'auction_current'))

    def test_rakuma_sold_badge_overrides_stale_instock(self):
        body = '¥1,600 SOLDOUT 商品説明 未使用'
        item, reason = self.observation('rakuma',body,'sold_discovery','http://schema.org/InStock',1600)
        self.assertEqual((reason,item['status'],item['priceMinor']),('accepted','completed',1600))
        self.assertEqual(self.observation('rakuma',body,'active_discovery','http://schema.org/InStock')[1], 'active_status_unverified')

    def test_mercari_soldout_schema_and_original_yen_price(self):
        item, reason = self.observation('mercari-jp','RM184.09 (¥6,699) 送料 ¥210','sold_discovery','https://schema.org/SoldOut',6699)
        self.assertEqual((reason,item['status'],item['priceMinor'],item['currency']),('accepted','completed',6699,'JPY'))
        self.assertEqual(self.observation('mercari-jp','¥6699','sold_discovery','https://schema.org/OutOfStock')[1], 'sold_status_unverified')

    def test_seller_description_cannot_mark_japan_item_sold(self):
        for source in ['rakuma','yahoo-furima-jp','mercari-jp']:
            self.assertEqual(status_for('購入手続きへ 商品説明 SOLD OUT となる場合があります','sold_discovery',source)[0], 'unknown')

    def test_furima_sold_receipt(self):
        item, reason = self.observation('yahoo-furima-jp','この商品は19分で売れました 18,000円送料無料','sold_discovery',price=18000)
        self.assertEqual((reason,item['status'],item['priceMinor']),('accepted','completed',18000))

    def test_bookwalker_and_rakuten_do_not_scrape_navigation_as_products(self):
        cases = [('bookwalker-jp','https://bookwalker.jp/de60a06148-1391-4af6-827c-dea4e264d1c5/',['https://bookwalker.jp/beginner/','https://member.bookwalker.jp/app/03/webstore/cooperation']),
                 ('rakuten-books-jp','https://books.rakuten.co.jp/rb/18333587/',['https://books.rakuten.co.jp/book/','https://books.rakuten.co.jp/event/book/'])]
        for source,url,invalid in cases:
            adapter=resolve_adapter(source)
            self.assertTrue(adapter.is_result_url(url))
            self.assertTrue(adapter.extract_external_id(url))
            for other in invalid:self.assertFalse(adapter.is_result_url(other))

    def test_verified_bookwalker_search(self):
        url=resolve_adapter('bookwalker-jp').build_search_url('えなこ','active_discovery','digital')
        self.assertEqual(parse_qs(urlparse(url).query), {'word':['えなこ'],'qcat':['8']})

    def test_unverified_sold_search_fails_before_browser(self):
        for source in ['rakuma','yahoo-furima-jp']:
            with self.assertRaisesRegex(ValueError,'exact public sold-listing'):
                resolve_adapter(source).build_search_url('写真集','sold_discovery','physical')

    def test_japan_retailers_have_no_completed_transaction_feed(self):
        for source in ['bookwalker-jp','rakuten-books-jp','surugaya','mandarake']:
            with self.assertRaisesRegex(ValueError,'retail sources are excluded'):
                collect({'sourceId':source,'operation':'sold_discovery'})

    def test_japan_retail_active_is_excluded(self):
        with patch('photobook_worker.launch',side_effect=RuntimeError('browser reached')):
            with self.assertRaisesRegex(ValueError,'retail sources are excluded'):
                collect({'sourceId':'rakuten-books-jp','source':{'region':'JP','kind':'bookstore','allowedHosts':['books.rakuten.co.jp']},'query':'えなこ','operation':'active_discovery'})

    def test_security_verification_is_blocked(self):
        with self.assertRaises(SourceBlockedError):
            ensure_rendered_page('Performing security verification This page verifies you are not a bot','surugaya')

    def test_rakuten_product_metadata_survives_empty_logo_headings(self):
        page=MagicMock()
        with patch('photobook_worker.navigate_page',return_value='えなこ 写真集 3,300円 在庫あり 買い物かごに入れる'), patch('photobook_worker.structured_product',return_value={}), patch('photobook_worker.page_metadata',return_value={'name':'えなこ 写真集'}):
            detail=detail_snapshot(page,'https://books.rakuten.co.jp/rb/18280957/',{'books.rakuten.co.jp'},'rakuten-books-jp',NavigationRateLimiter({},{}))
        self.assertEqual(detail['structured']['name'],'えなこ 写真集')
        self.assertEqual(resolve_adapter('rakuten-books-jp').canonical_result_url('https://books.rakuten.co.jp/rb/18280957/?l-id=search-c-item-review'),'https://books.rakuten.co.jp/rb/18280957/')

    def test_mercari_details_wait_for_product_schema(self):
        page=MagicMock()
        schema={'name':'林襄 写真集','price':6699,'availability':'https://schema.org/SoldOut'}
        with patch('photobook_worker.navigate_page',return_value='メルカリについて プライバシー'), patch('photobook_worker.structured_product',side_effect=[{}, {}, schema]), patch('photobook_worker.page_metadata',return_value={}), patch('photobook_worker.page_body',return_value='林襄 写真集 ¥6699'):
            detail=detail_snapshot(page,'https://jp.mercari.com/item/m93190924618',{'jp.mercari.com'},'mercari-jp',NavigationRateLimiter({},{}))
        self.assertEqual(detail['structured']['price'],6699)
        self.assertEqual(page.wait_for_timeout.call_count,2)

    def test_mercari_pagination_never_invents_tokens(self):
        adapter=resolve_adapter('mercari-jp')
        with self.assertRaisesRegex(ValueError,'observed page token'):
            adapter.page_url('https://jp.mercari.com/search?keyword=test',2,60)
        self.assertEqual(parse_qs(urlparse(adapter.page_url('https://jp.mercari.com/search?keyword=test',2,60,cursor='real-token')).query)['page_token'],['real-token'])

    def test_magazine_clippings_are_not_book_listings(self):
        source={'id':'yahoo-auctions-jp','region':'JP','kind':'marketplace'}
        title='えなこ 写真集 切り抜き ラミネート加工'
        item,reason=make_observation({'sourceId':'yahoo-auctions-jp','humanModelKeywords':['えなこ']},source,{'url':'https://auctions.yahoo.co.jp/jp/auction/h1246825334','title':title},{'body':'現在190円 2件 終了','structured':{'name':title}},'sold_discovery')
        self.assertEqual(reason,'not_a_photobook')


if __name__ == '__main__':
    unittest.main()
