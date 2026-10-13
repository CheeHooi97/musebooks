import unittest
from urllib.parse import parse_qs, urlparse

from kobo_search_scope import author_search_url, filter_candidates, search_scope


class KoboSearchScopeTests(unittest.TestCase):
    def test_author_query_uses_kobo_photobook_genre(self):
        url = author_search_url('RaMu')
        self.assertEqual(parse_qs(urlparse(url).query), {'g': ['101915'], 'pname': ['RaMu']})

    def test_paginated_photo_search_keeps_its_scope(self):
        self.assertEqual(search_scope('https://books.rakuten.co.jp/search?pname=RaMu&g=101915&o=30'),
                         ('RaMu', '101915'))
        self.assertEqual(search_scope('https://books.rakuten.co.jp/search?g=101&pname=RaMu'),
                         ('RaMu', '101'))

    def test_category_filter_preserves_reasons_for_broad_results(self):
        candidates = {'photo': 'RaMu写真集', 'other': 'RaMu小説'}
        kept, skipped = filter_candidates(candidates, {'photo': 'RaMu写真集'})
        self.assertEqual(kept, {'photo': 'RaMu写真集'})
        self.assertEqual(skipped, {'other': 'outside_kobo_photobook_category'})

    def test_no_category_results_does_not_filter_candidates(self):
        candidates = {'other': 'candidate title'}
        self.assertEqual(filter_candidates(candidates, ({}) ), (candidates, {}))

    def test_empty_completed_category_does_not_retry_unrelated_broad_candidates(self):
        candidates = {'novel': 'RaMu 小説'}
        kept, skipped = filter_candidates(candidates, {}, category_searched=True)
        self.assertEqual(kept, {})
        self.assertEqual(skipped, {'novel': 'outside_kobo_photobook_category'})


if __name__ == '__main__':
    unittest.main()
