import unittest
from photobook_worker import collect, make_observation

class FormatBoundaryTests(unittest.TestCase):
    def test_photobook_spelling_variants_keep_non_book_guards(self):
        from photobook_worker import looks_like_photobook, photobook_title_exclusion
        for title in ('張雅涵 写真', '張雅涵 寫真', '林襄写真集'):
            self.assertTrue(looks_like_photobook(title), title)
        for title in ('林襄 生写真', '林襄 写真 photo card', '林襄 寫真卡'):
            self.assertFalse(looks_like_photobook(title), title)
        self.assertEqual(photobook_title_exclusion('林襄 写真 calendar'), 'calendar_only')
        self.assertEqual(photobook_title_exclusion('YUNA林真亦2026寫真掛曆'), 'calendar_only')

    def test_marketplaces_reject_digital_jobs_before_browser(self):
        for source_id in ('ruten-tw', 'yahoo-tw', 'yahoo-auctions-jp', 'ebay'):
            with self.subTest(source=source_id), self.assertRaises(ValueError):
                collect({'sourceId': source_id, 'source': {'kind': 'marketplace', 'region': 'TW'}, 'format': 'digital', 'marketplaceOnly': False, 'query': '林襄', 'operation': 'active_discovery'})

    def test_digital_platforms_reject_physical_and_sold_jobs(self):
        for operation, fmt in (('active_discovery', 'physical'), ('sold_discovery', 'digital')):
            with self.subTest(operation=operation), self.assertRaises(ValueError):
                collect({'sourceId': 'readmoo-tw', 'source': {'kind': 'digital_store', 'region': 'TW'}, 'format': fmt, 'query': '林襄', 'operation': operation})

    def test_calendars_illustrations_and_seller_keywords_are_not_model_books(self):
        from photobook_worker import photobook_title_exclusion, marketplace_subject_matches
        self.assertEqual(photobook_title_exclusion('2024 林襄寫真桌曆'),'calendar_only')
        self.assertEqual(photobook_title_exclusion('風の甦醒 張雅涵 美女寫真插畫 畫冊'),'illustrated_book')
        self.assertEqual(photobook_title_exclusion('林襄寫真書 附贈月曆'),'')
        self.assertFalse(marketplace_subject_matches({'humanModelKeywords':['張雅涵'],'catalogModelNames':['林莎','張雅涵']},'Honey 林莎寫真書 林襄 張雅涵'))
        self.assertFalse(marketplace_subject_matches({'humanModelKeywords':['夏蕾'],'catalogModelNames':['夏蕾']},'長澤茉里奈 2026生日限量PHOTOBOOK 寫真書'))
        self.assertTrue(marketplace_subject_matches({'humanModelKeywords':['夏蕾'],'catalogModelNames':['夏蕾']},'夏蕾寫真-心動蕾達 附贈硬書盒'))

    def test_general_ebook_recommendations_do_not_satisfy_model_photobook_scope(self):
        source = {
            'id': 'readmoo-tw',
            'kind': 'digital_store',
            'region': 'TW',
            'allowedFormats': ['digital'],
            'allowedHosts': ['readmoo.com'],
        }
        candidate = {
            'url': 'https://readmoo.com/book/123456',
            'title': '健康飲食入門電子書',
            'text': '健康飲食入門電子書 推薦：林襄寫真集與其他熱銷作品',
        }
        detail = {
            'body': '健康飲食入門電子書 作者 營養師甲 本書介紹日常飲食原則。',
            'structured': {
                'name': '健康飲食入門電子書',
                'author': '營養師甲',
                'bookFormat': 'EBook',
                'description': '一般飲食指南。',
            },
        }
        item, reason = make_observation(
            {'sourceId': 'readmoo-tw', 'format': 'digital', 'humanModelKeywords': ['林襄']},
            source,
            candidate,
            detail,
            'catalog_discovery',
        )
        self.assertIsNone(item)
        self.assertEqual(reason, 'not_a_photobook')

    def test_verified_model_photobook_keeps_ebook_store_format(self):
        source = {
            'id': 'readmoo-tw',
            'kind': 'digital_store',
            'region': 'TW',
            'allowedFormats': ['digital'],
            'allowedHosts': ['readmoo.com'],
        }
        title = '林襄個人寫真集（電子書）'
        candidate = {
            'url': 'https://readmoo.com/book/123456',
            'title': title,
            'text': title,
        }
        detail = {
            'body': title + ' 作者 林襄 出版社 官方出版社 NT$299',
            'structured': {
                'name': title,
                'author': '林襄',
                'bookFormat': 'EBook',
                'price': '299',
                'currency': 'TWD',
                'availability': 'https://schema.org/InStock',
            },
        }
        item, reason = make_observation(
            {'sourceId': 'readmoo-tw', 'format': 'digital', 'humanModelKeywords': ['林襄']},
            source,
            candidate,
            detail,
            'catalog_discovery',
        )
        self.assertEqual(reason, 'accepted')
        self.assertEqual(item['format'], 'digital')
        self.assertEqual(item['digitalAccess'], 'authorized_store')
