import unittest
from unittest.mock import patch
from run_japan_model_queue import collection_complete


class ResumeTests(unittest.TestCase):
    model = {'models': [{'canonical_public_name': 'Model'}]}

    def test_failed_digital_search_is_pending_even_when_name_was_searched(self):
        state = dict(status='source_failed', pages=['https://example/search?keyword=Model'], errors={})
        self.assertFalse(collection_complete('grajapa', self.model, state))

    def test_detail_errors_are_retried(self):
        state = dict(status='detail_failures', pages=['https://example/search?keyword=Model'], errors={'book': 'timeout'})
        self.assertFalse(collection_complete('grajapa', self.model, state))

    def test_completed_digital_capture_with_new_alias_is_pending(self):
        model = {'models': [dict(self.model['models'][0], aliases=['Alias'])]}
        state = dict(status='public_search_exhausted', pages=['https://example/search?keyword=Model'], errors={})
        self.assertFalse(collection_complete('grajapa', model, state))
        state['pages'].append('https://example/search?keyword=Alias')
        self.assertTrue(collection_complete('grajapa', model, state))

    def test_finished_physical_capture_with_failed_query_is_pending(self):
        runs = {s + ':' + q: {'status': 'public_search_exhausted'}
            for s in ('yahoo-auctions-jp', 'yahoo-furima-jp', 'rakuma')
            for q in ('Model 写真集', 'Model')}
        state = dict(status='finished', runs=runs)
        self.assertTrue(collection_complete('physical', self.model, state))
        runs['rakuma:Model']['status'] = 'source_failed'
        self.assertFalse(collection_complete('physical', self.model, state))

    def test_blocked_physical_source_is_accounted_for_only_during_cooldown(self):
        runs = {s + ':' + q: {'status': 'public_search_exhausted'}
            for s in ('yahoo-auctions-jp', 'yahoo-furima-jp', 'rakuma')
            for q in ('Model 写真集', 'Model')}
        runs['yahoo-furima-jp:Model']['status'] = 'source_blocked'
        state = dict(status='finished_with_source_blocks', runs=runs)
        with patch('run_japan_model_queue.source_is_blocked',
                side_effect=lambda source_id: source_id == 'yahoo-furima-jp'):
            self.assertTrue(collection_complete('physical', self.model, state))
        with patch('run_japan_model_queue.source_is_blocked', return_value=False):
            self.assertFalse(collection_complete('physical', self.model, state))

    def test_broad_kobo_author_search_does_not_complete_photobook_search(self):
        state = dict(status='public_search_exhausted', pages=['https://books.rakuten.co.jp/search?pname=Model'], errors={})
        self.assertFalse(collection_complete('kobo', self.model, state))
        state['pages'].append('https://books.rakuten.co.jp/search?g=101915&pname=Model')
        self.assertTrue(collection_complete('kobo', self.model, state))

    def test_publisher_first_page_does_not_complete_an_interrupted_query(self):
        state = dict(status='public_search_exhausted', pages=['https://www.wani.co.jp/category.php?tag=Model'],
            searches={'Model': dict(status='running', pending=['https://www.wani.co.jp/category.php?tag=Model&page=2'])})
        self.assertFalse(collection_complete('wani', self.model, state))
        state['searches']['Model'].update(status='public_search_exhausted', pending=[])
        self.assertTrue(collection_complete('wani', self.model, state))

    def test_obsolete_magazine_rejection_requires_a_reassessment_pass(self):
        state = dict(status='public_search_exhausted', pages=['https://books.rakuten.co.jp/search?g=101915&pname=Model'],
            errors={}, rejected={'photo': 'magazine_only'}, candidates={'photo': 'EX大衆デジタル写真集 Model'})
        self.assertFalse(collection_complete('kobo', self.model, state))


if __name__ == '__main__':
    unittest.main()
