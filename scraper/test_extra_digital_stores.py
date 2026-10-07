import json
import unittest
from unittest.mock import patch

from digital_storefronts import EXTRA_DIGITAL_SOURCES, selected_book_schema
from marketplace_adapters import resolve_adapter
from photobook_worker import (bookwalker_photo_category, collect, make_observation,
                              read_attribute, detail_snapshot, taaze_product_category,
                              NavigationRateLimiter)


class ExtraDigitalStoreTests(unittest.TestCase):
    def test_regional_identity_and_tracking(self):
        cases = [
            ('hami-tw', 'https://www.hamibook.com.tw/book/0100345610?_cookie_check=1', '0100345610'),
            ('google-play-books-tw', 'https://play.google.com/store/books/details/title?id=NoArEAAAQBAJ', 'NoArEAAAQBAJ'),
            ('apple-books-tw', 'https://books.apple.com/tw/book/title/id6760949828', '6760949828'),
            ('apple-books-us', 'https://books.apple.com/us/book/title/id6760949828', '6760949828'),
            ('hyread-tw', 'https://ebook.hyread.com.tw/bookDetail.jsp?id=324597', '324597'),
            ('momo-books-tw', 'https://m.momoshop.com.tw/goods.momo?i_code=12583611&campaign=x', '12583611'),
            ('pchome-books-tw', 'https://24h.pchome.com.tw/books/prod/DJBR5E-D900IO5U9', 'DJBR5E-D900IO5U9'),
            ('yahoo-shopping-books-tw', 'https://tw.buy.yahoo.com/gdsale/title-11285372.html?utm_source=x', '11285372'),
            ('kingstone-books-tw', 'https://www.kingstone.com.tw/basic/2800000212957/?lid=search', '2800000212957'),
            ('taaze-books-tw', 'https://www.taaze.tw/products/14100093289.html', '14100093289'),
            ('sanmin-books-tw', 'https://www.sanmin.com.tw/product/index/013978283', '013978283'),
            ('rakuten-kobo-tw', 'https://www.rakuten.com.tw/shop/kobo/product/154b4821-edfb-3eb7-8c42-0f7b6685e63d/', '154b4821-edfb-3eb7-8c42-0f7b6685e63d'),
            ('fan520-tw', 'https://www.fan520.net/products/abao-070701?utm_source=search', 'abao-070701'),
        ]
        for sid, url, identity in cases:
            adapter = resolve_adapter(sid)
            self.assertTrue(adapter.is_result_url(url), sid)
            self.assertEqual(adapter.extract_external_id(url), identity)
            canonical = adapter.canonical_result_url(url)
            self.assertEqual(adapter.extract_external_id(canonical), identity)
            self.assertNotIn('campaign', canonical)
            self.assertFalse(adapter.is_result_url(url.replace('https://', 'https://evil.')))
        google = resolve_adapter('google-play-books-tw')
        self.assertIn('gl=TW', google.canonical_result_url(cases[1][1]))
        self.assertFalse(google.is_result_url('https://play.google.com/store/books/details?id=abc&gl=US'))
        self.assertFalse(google.is_result_url('https://play.google.com/store/apps/details?id=abc'))
        self.assertFalse(resolve_adapter('apple-books-tw').is_result_url('https://books.apple.com/us/book/id123'))
        self.assertFalse(resolve_adapter('hyread-tw').is_result_url('https://library.ebook.hyread.com.tw/bookDetail.jsp?id=123'))

    def test_google_nested_offer_has_correct_currency_and_isbn(self):
        payload = {'@type': 'Book', 'name': '與你襄遇 林襄數位寫真（含影音）',
                   'author': [{'name': '林襄、莉奈'}],
                   'workExample': {'bookFormat': 'https://schema.org/EBook', 'isbn': '9786263061255',
                                   'potentialAction': {'expectsAcceptanceOf': [{'price': '203', 'priceCurrency': 'TWD', 'availability': 'https://schema.org/InStock'}]}}}
        result = selected_book_schema([json.dumps(payload)])
        self.assertEqual((result['price'], result['currency'], result['isbn']), ('203', 'TWD', '9786263061255'))
        self.assertEqual(result['author'], '林襄、莉奈')

    def test_momo_parent_metadata_and_variant_offer(self):
        payload = {'@graph': [{'@type': 'ProductGroup', 'name': '【momoBOOK】林襄寫真(電子書)',
                              'additionalProperty': [{'name': 'ISBN', 'value': '9786263061255'}, {'name': '出版社', 'value': '尖端出版'}, {'name': '類型', 'value': '電子書'}],
                              'hasVariant': [{'@type': 'Product', 'name': '單一規格', 'offers': {'price': '263', 'priceCurrency': 'TWD'}}]}]}
        result = selected_book_schema([json.dumps(payload)])
        self.assertIn('林襄', result['name'])
        self.assertEqual(result['price'], '263')
        self.assertEqual(result['publisher'], '尖端出版')
        self.assertEqual(result['bookFormat'], '電子書')

    def test_mixed_retail_rejects_paper_despite_ebook_navigation(self):
        for sid, url in [('momo-books-tw', 'https://www.momoshop.com.tw/product/123'), ('pchome-books-tw', 'https://24h.pchome.com.tw/books/prod/ABC-123'), ('yahoo-shopping-books-tw', 'https://tw.buy.yahoo.com/gdsale/title-123.html'), ('sanmin-books-tw', 'https://www.sanmin.com.tw/product/index/123'), ('taaze-books-tw', 'https://www.taaze.tw/products/14100093289.html')]:
            source = {'id': sid, 'kind': 'digital_store', 'region': 'TW', 'allowedHosts': [url.split('/')[2]], 'allowedFormats': ['digital']}
            candidate = {'url': url, 'title': '林襄 寫真書 紙本平裝'}
            detail = {'body': '電子書 類別 推薦書籍 購買 $263', 'structured': {'price': 263, 'currency': 'TWD', 'availability': 'https://schema.org/InStock'}}
            item, reason = make_observation({'sourceId': sid, 'format': 'digital', 'humanModelKeywords': ['林襄']}, source, candidate, detail, 'active_discovery')
            self.assertIsNone(item)
            self.assertEqual(reason, 'digital_product_unverified')

    def test_taaze_selected_ebook_heading_is_accepted_without_matching_site_navigation(self):
        url = 'https://www.taaze.tw/products/14100142342.html'
        title = '夢境夏娃-木子性感寫真集'
        source = {'id': 'taaze-books-tw', 'kind': 'digital_store', 'region': 'TW',
                  'allowedHosts': ['www.taaze.tw'], 'allowedFormats': ['digital']}
        candidate = {'url': url, 'title': '', 'text': '', 'imageUrl': ''}
        body = ('首頁 > 中文電子書 > 生活風格 > 影視寫真 > ' + title +
                '（電子書） 作者：拾捌 特價：67折，NT$299 放入購物車 ' +
                '模特／ 木子（@muzi_0t.3o）')
        structured = {'name': title, 'description': '模特／ 木子（@muzi_0t.3o）',
                      'price': '299', 'currency': 'TWD',
                      'availability': 'https://schema.org/InStock',
                      'publisher': '拾捌寫真製作所'}
        item, reason = make_observation(
            {'sourceId': source['id'], 'format': 'digital', 'humanModelKeywords': ['木子']},
            source, candidate, {'body': body, 'structured': structured}, 'active_discovery')
        self.assertEqual(reason, 'accepted')
        self.assertEqual((item['format'], item['status'], item['priceMinor'], item['currency']),
                         ('digital', 'active', 29900, 'TWD'))

    def test_fan520_digital_photobook_offer_is_accepted(self):
        source = {'id': 'fan520-tw', 'kind': 'digital_store', 'region': 'TW',
                  'allowedHosts': ['www.fan520.net'], 'allowedFormats': ['digital']}
        title = '許小葆 數位寫真 - 女僕小葆貝(D) "送影片"'
        url = 'https://www.fan520.net/products/abao-070701'
        schema = {'@type': 'Product', 'name': title, 'description': '女僕主題數位寫真，購買附影片。',
                  'image': 'https://img.shoplineapp.com/media/image_clips/sample/original.jpg',
                  'offers': {'@type': 'Offer', 'price': 490, 'priceCurrency': 'TWD',
                             'availability': 'https://schema.org/InStock'}}
        structured = selected_book_schema([json.dumps(schema, ensure_ascii=False)])
        self.assertEqual((structured['price'], structured['currency'], structured['availability']),
                         (490, 'TWD', 'https://schema.org/InStock'))
        item, reason = make_observation(
            {'sourceId': 'fan520-tw', 'operation': 'active_discovery', 'format': 'digital',
             'humanModelKeywords': ['許小葆', '小葆']},
            source, {'url': url, 'title': title, 'text': '', 'imageUrl': schema['image']},
            {'body': title + ' 數位寫真 附影片 加入購物車 NT$490', 'structured': structured},
            'active_discovery')
        self.assertEqual(reason, 'accepted')
        self.assertEqual((item['format'], item['priceType'], item['priceMinor'], item['currency'], item['status']),
                         ('digital', 'digital', 49000, 'TWD', 'active'))
        self.assertEqual(item['digitalAccess'], 'authorized_store')
        self.assertEqual(item['editionVariant'], 'with_video')

    def test_taaze_photo_category_identifies_generic_title(self):
        url = 'https://www.taaze.tw/products/14100142341.html'
        title = '柔和日光-Mier'
        body = ('首頁 > 中文電子書 > 生活風格 > 影視寫真 > ' + title +
                '（電子書） 作者：拾捌 特價：67折，NT$299 放入購物車 ' +
                '模特／ Mier（@medea0212）')
        category = taaze_product_category(body, title)
        self.assertEqual(category, '影視寫真')
        source = {'id': 'taaze-books-tw', 'kind': 'digital_store', 'region': 'TW',
                  'allowedHosts': ['www.taaze.tw'], 'allowedFormats': ['digital']}
        structured = {'name': title, 'description': '模特／ Mier（@medea0212）',
                      'category': category, 'price': '299', 'currency': 'TWD',
                      'availability': 'https://schema.org/InStock'}
        item, reason = make_observation(
            {'sourceId': source['id'], 'format': 'digital', 'humanModelKeywords': ['Mier']},
            source, {'url': url, 'title': '', 'text': '', 'imageUrl': ''},
            {'body': body, 'structured': structured}, 'active_discovery')
        self.assertEqual(reason, 'accepted')
        self.assertEqual((item['format'], item['status'], item['priceMinor'], item['currency']),
                         ('digital', 'active', 29900, 'TWD'))

    def test_rakuten_kobo_taiwan_offer_is_a_digital_edition(self):
        source = {'id': 'rakuten-kobo-tw', 'kind': 'digital_store', 'region': 'TW',
                  'allowedHosts': ['www.rakuten.com.tw'], 'allowedFormats': ['digital']}
        url = 'https://www.rakuten.com.tw/shop/kobo/product/154b4821-edfb-3eb7-8c42-0f7b6685e63d/'
        title = '鏡中迷情-木子性感寫真集'
        item, reason = make_observation(
            {'sourceId': source['id'], 'format': 'digital', 'humanModelKeywords': ['木子']},
            source, {'url': url, 'title': title, 'text': '', 'imageUrl': ''},
            {'body': '鏡中迷情-木子性感寫真集（電子書） EPUB3固式格式 NT$299 加入購物車',
             'structured': {'name': title, 'author': '拾捌', 'publisher': '拾捌寫真製作所',
                            'price': '299', 'currency': 'TWD',
                            'availability': 'https://schema.org/InStock'}},
            'active_discovery')
        self.assertEqual(reason, 'accepted')
        self.assertEqual((item['format'], item['status'], item['priceMinor'], item['currency']),
                         ('digital', 'active', 29900, 'TWD'))

    def test_bookwalker_photo_genre_makes_generic_series_title_discoverable(self):
        body = ('Journey Girl Vol.23 Sunny 作者 一加 、 Sunny 類型標籤 人物寫真 '
                '出版社 滾石移動 系列 Journey Girl EPUB格式 固定版面 價格 $179 '
                '立即結帳 加入購物車')
        category = bookwalker_photo_category(body)
        self.assertEqual(category, '人物寫真')
        source = {'id': 'bookwalker-tw', 'kind': 'digital_store', 'region': 'TW',
                  'allowedHosts': ['www.bookwalker.com.tw'], 'allowedFormats': ['digital']}
        candidate = {'url': 'https://www.bookwalker.com.tw/product/308235', 'title': '', 'text': '', 'imageUrl': ''}
        structured = {'name': 'Journey Girl Vol.23 Sunny', 'category': category,
                      'author': '一加 、 Sunny', 'publisher': '滾石移動',
                      'price': '179', 'currency': 'TWD',
                      'availability': 'https://schema.org/InStock'}
        item, reason = make_observation(
            {'sourceId': source['id'], 'format': 'digital', 'humanModelKeywords': ['Sunny']},
            source, candidate, {'body': body, 'structured': structured}, 'active_discovery')
        self.assertEqual(reason, 'accepted')
        self.assertEqual((item['format'], item['status'], item['priceMinor'], item['currency']),
                         ('digital', 'active', 17900, 'TWD'))

    def test_sanmin_ebook_offer_is_digital_and_vendor_sku_is_not_an_isbn(self):
        payload = {'@context': 'https://schema.org', '@type': 'Book',
                   'isbn': '2222222869403', 'name': 'Girl Friend女友寫真 No.4(電子書)',
                   'description': '書名：Girl Friend女友寫真 No.4(電子書)，模特兒：草草、金瑀恩、Liya莉亞、佳佳兒',
                   'BookFormat': 'GraphicNovel',
                   'offers': {'@type': 'Offer', 'priceCurrency': 'TWD', 'price': '399',
                              'availability': 'https://schema.org/InStock'}}
        schema = selected_book_schema([json.dumps(payload, ensure_ascii=False)])
        self.assertEqual((schema['price'], schema['currency'], schema['availability']),
                         ('399', 'TWD', 'https://schema.org/InStock'))
        self.assertEqual(schema['isbn'], '')

        source = {'id': 'sanmin-books-tw', 'kind': 'digital_store', 'region': 'TW',
                  'allowedHosts': ['www.sanmin.com.tw'], 'allowedFormats': ['digital']}
        candidate = {'url': 'https://www.sanmin.com.tw/product/index/015876854',
                     'title': schema['name'], 'text': schema['description']}
        item, reason = make_observation(
            {'sourceId': source['id'], 'operation': 'active_discovery', 'format': 'digital'},
            source, candidate, {'body': schema['description'], 'structured': schema}, 'active_discovery')
        self.assertEqual(reason, 'accepted')
        self.assertEqual((item['format'], item['priceType'], item['priceMinor'], item['currency'], item['status']),
                         ('digital', 'digital', 39900, 'TWD', 'active'))
        self.assertEqual(item['isbn'], '')

    def test_group_ebook_models_are_matched_from_selected_book_description(self):
        source = {'id': 'google-play-books-tw', 'kind': 'digital_store', 'region': 'TW',
                  'allowedHosts': ['play.google.com'], 'allowedFormats': ['digital']}
        candidate = {'url': 'https://play.google.com/store/books/details?id=m4cgEQAAQBAJ&hl=zh_TW&gl=TW',
                     'title': 'MotoH車漾女神誌 - 女神降臨寫真集'}
        detail = {'body': '電子書 NT$279.00', 'structured': {
            'name': 'MotoH車漾女神誌 - 女神降臨寫真集',
            'description': '作者：子席國際股份有限公司。',
            'publisher': '子席國際股份有限公司', 'price': '279', 'currency': 'TWD',
            'availability': 'https://schema.org/InStock', 'bookFormat': 'https://schema.org/EBook'}}
        detail['body'] = ('MotoH車漾女神誌 - 女神降臨寫真集 '
                          '四位模特兒：陳白白（阿白）、葉蛋蛋、波奇、Liya莉亞。'
                          '相關推薦：陳白白另一寫真')
        item, reason = make_observation(
            {'sourceId': source['id'], 'operation': 'active_discovery', 'format': 'digital',
             'humanModelKeywords': ['陳白白']},
            source, candidate, detail, 'active_discovery')
        self.assertEqual(reason, 'accepted')
        self.assertEqual((item['title'], item['format'], item['priceType'], item['priceMinor'], item['currency']),
                         ('MotoH車漾女神誌 - 女神降臨寫真集', 'digital', 'digital', 27900, 'TWD'))

        detail['body'] = ('MotoH車漾女神誌 - 女神降臨寫真集 電子書內容說明。'
                          '相關推薦：陳白白另一本寫真')
        item, reason = make_observation(
            {'sourceId': source['id'], 'operation': 'active_discovery', 'format': 'digital',
             'humanModelKeywords': ['陳白白']},
            source, candidate, detail, 'active_discovery')
        self.assertIsNone(item)
        self.assertEqual(reason, 'not_in_people_scope')

    def test_foreign_price_is_never_relabelled_as_twd(self):
        source = {'id': 'google-play-books-tw', 'kind': 'digital_store', 'region': 'TW', 'allowedHosts': ['play.google.com']}
        candidate = {'url': 'https://play.google.com/store/books/details?id=abc&gl=TW', 'title': '林襄 數位寫真書 電子書'}
        detail = {'body': 'Buy $9.99', 'structured': {'price': '9.99', 'currency': 'USD', 'availability': 'https://schema.org/InStock'}}
        item, reason = make_observation({'sourceId': source['id'], 'format': 'digital', 'humanModelKeywords': ['林襄']}, source, candidate, detail, 'active_discovery')
        self.assertIsNone(item)
        self.assertEqual(reason, 'digital_retail_price_unverified')

    def test_extra_stores_reject_sold_and_physical_jobs(self):
        for sid in EXTRA_DIGITAL_SOURCES:
            for op, fmt in [('sold_discovery', 'digital'), ('active_discovery', 'physical')]:
                with patch('photobook_worker.launch') as browser, self.assertRaises(ValueError):
                    collect({'sourceId': sid, 'source': {'id': sid, 'kind': 'digital_store'}, 'operation': op, 'format': fmt})
                browser.assert_not_called()

    def test_empty_image_locator_does_not_wait_for_attribute(self):
        from unittest.mock import MagicMock
        locator = MagicMock()
        locator.count.return_value = 0
        self.assertEqual(read_attribute(locator, 'alt'), '')
        locator.get_attribute.assert_not_called()

    def test_books_nested_offer_beats_recommendation_price(self):
        payload = {'@type': 'Book', 'name': '林襄數位寫真（電子書）', 'workExample': {'workExample': {'bookFormat': 'http://schema.org/EBook', 'potentialAction': {'expectsAcceptanceOf': {'price': 299, 'priceCurrency': 'TWD', 'availability': 'http://schema.org/InStock'}}}}}
        result = selected_book_schema([json.dumps(payload)])
        self.assertEqual(result['price'], 299)
        self.assertEqual(result['bookFormat'], 'http://schema.org/EBook')

    def test_taaze_catalog_price_does_not_claim_active(self):
        from unittest.mock import MagicMock
        body = '書名：張雅涵寫真書（中文電子書） 作者：張雅涵 出版社：莉奈文創 出版日期：2023-03-18 定價：590元 特價：67折 395元 閱讀軟體：TAAZE eBook'
        page = MagicMock(); page.locator.return_value.count.return_value = 0
        page.url = 'https://m.taaze.tw/do/mobile/single.aspx?pid=14100093289'
        with patch('photobook_worker.navigate_page', return_value=body), patch('photobook_worker.page_body', return_value=body), patch('photobook_worker.structured_product', return_value={}), patch('photobook_worker.page_metadata', return_value={}), patch('photobook_worker.read_text', return_value='張雅涵寫真書（中文電子書）'):
            detail = detail_snapshot(page, 'https://m.taaze.tw/do/mobile/single.aspx?pid=14100093289', {'m.taaze.tw'}, 'taaze-books-tw', NavigationRateLimiter({}, {}))
        self.assertEqual(detail['structured']['price'], '395')
        self.assertEqual(detail['structured']['publisher'], '莉奈文創')
        self.assertNotIn('availability', detail['structured'])

    def test_apple_us_preserves_usd_and_unknown_availability(self):
        source = {'id': 'apple-books-us', 'kind': 'digital_store', 'region': 'US', 'allowedHosts': ['books.apple.com']}
        candidate = {'url': 'https://books.apple.com/us/book/id6760949828', 'title': '張雅涵 個人寫真書'}
        detail = {'body': '$26.99 Publisher Description', 'structured': {'price': 26.99, 'currency': 'USD', 'bookFormat': 'EBook'}}
        item, reason = make_observation({'sourceId': source['id'], 'format': 'digital', 'humanModelKeywords': ['張雅涵']}, source, candidate, detail, 'catalog_discovery')
        self.assertEqual(reason, 'accepted')
        self.assertEqual((item['priceMinor'], item['currency'], item['status']), (2699, 'USD', 'unknown'))
        item, reason = make_observation({'sourceId': source['id'], 'format': 'digital', 'humanModelKeywords': ['張雅涵']}, source, candidate, detail, 'active_discovery')
        self.assertIsNone(item)
        self.assertEqual(reason, 'active_status_unverified')
