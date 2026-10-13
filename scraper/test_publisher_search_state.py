import unittest
from publisher_search_state import initialize_searches


class PublisherResumeTests(unittest.TestCase):
    def test_partial_legacy_query_restarts_discovery_instead_of_skipping_page_one(self):
        state = dict(status='source_failed', pages=['https://www.wani.co.jp/category.php?tag=Model'])
        query = initialize_searches(state, ['Model'], 'www.wani.co.jp')['Model']
        self.assertEqual(query['status'], 'running')
        self.assertEqual(query['pending'], state['pages'])

    def test_completed_legacy_query_stays_complete_but_new_alias_is_pending(self):
        state = dict(status='public_search_exhausted', pages=['https://www.wani.co.jp/category.php?tag=Model'])
        queries = initialize_searches(state, ['Model', 'Alias'], 'www.wani.co.jp')
        self.assertEqual(queries['Model']['status'], 'public_search_exhausted')
        self.assertEqual(queries['Alias']['status'], 'running')

    def test_interrupted_pagination_preserves_the_pending_page(self):
        query = dict(status='running', pending=['page-2'], seen=['page-1'])
        state = dict(status='source_failed', pages=['page-1'], searches={'Model': query})
        self.assertIs(initialize_searches(state, ['Model'], 'www.wani.co.jp')['Model'], query)
        self.assertEqual(query['pending'], ['page-2'])


if __name__ == '__main__':
    unittest.main()
