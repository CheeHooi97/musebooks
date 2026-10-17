import json
import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from physical_detail_coverage import recover_pending_details, update_detail_coverage
from run_japan_model_queue import collection_complete
import collect_model_physical as collector


class PhysicalDetailCoverageTests(unittest.TestCase):
    def test_collector_retries_failed_detail_and_preserves_the_offer(self):
        root = Path(__file__).resolve().parent.parent
        url = 'https://auctions.yahoo.co.jp/jp/auction/fixture'
        retries = []
        with tempfile.TemporaryDirectory(dir=root / '.tmp') as directory:
            output = Path(directory)
            model_file = output / 'model.json'
            model_file.write_text(json.dumps({'models': [dict(id=99999,
                original_name='Model', canonical_public_name='Model')]}), encoding='utf-8')

            def collect(request):
                batch = dict(items=[], diagnostics={'detailErrors': 0}, hasMore=False, nextCursor='')
                if request['operation'] == 'listing_detail':
                    retries.append(request['url'])
                    saved = json.loads((output / 'physical-state.json').read_text(encoding='utf-8'))
                    self.assertIn(url, saved['pendingDetails'])
                    collector.worker.detail_snapshot(None, url)
                    batch['items'] = [dict(externalId='fixture', priceMinor=1300, title='Model 写真集', url=url)]
                elif request['sourceId'] == 'yahoo-auctions-jp' and request['query'] == 'Model 写真集':
                    collector.worker.collect_anchor_candidates(None)
                    try:
                        collector.worker.detail_snapshot(None, url)
                    except collector.worker.DetailSnapshotError:
                        batch['diagnostics']['detailErrors'] = 1
                return batch

            with patch('sys.argv', ['collector', '--output', str(output), '--model-file', str(model_file)]), \
                    patch.object(collector, 'load_source_blocks', return_value={}), \
                    patch.object(collector.worker, 'collect', side_effect=collect), \
                    patch.object(collector.worker, 'collect_anchor_candidates', return_value=[dict(url=url, title='Model 写真集')]), \
                    patch.object(collector.worker, 'detail_snapshot', side_effect=[collector.worker.DetailSnapshotError('temporary failure'), {'title': 'Model 写真集'}]), \
                    patch.object(collector.worker, 'NavigationRateLimiter', collector.worker.NavigationRateLimiter), \
                    redirect_stdout(io.StringIO()):
                collector.main()
            state = json.loads((output / 'physical-state.json').read_text(encoding='utf-8'))
        self.assertEqual(retries, [url])
        self.assertEqual(state['status'], 'finished')
        self.assertEqual(state['pendingDetails'], {})
        self.assertEqual(state['items']['yahoo-auctions-jp:fixture']['priceMinor'], 1300)

    def test_only_uncaptured_matching_photobooks_remain_pending(self):
        worker = SimpleNamespace(photobook_title_exclusion=lambda title: 'DVD' in title,
            marketplace_subject_matches=lambda request, title: 'Model' in title)
        candidates = [{'url': url, 'title': title} for url, title in
            [('failed', 'Model 写真集'), ('captured', 'Model 写真集'),
             ('other', 'Other 写真集'), ('excluded', 'Model DVD 写真集'), ('card', 'Model card')]]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            (output / 'batch.json').write_text(json.dumps({'candidateEvidence': candidates}), encoding='utf-8')
            state = dict(status='finished', details={'captured': {}}, runs={'query': dict(
                sourceId='source', status='query_relevance_exhausted',
                batches=[dict(file='batch.json', diagnostics={'detailErrors': 1})])})
            recover_pending_details(state, output, ['Model'], worker)
        self.assertEqual(list(state['pendingDetails']), ['failed'])
        self.assertEqual(state['status'], 'incomplete')
        self.assertEqual(state['runs']['query']['status'], 'detail_failures')
        state['pendingDetails'].clear()
        update_detail_coverage(state)
        self.assertEqual(state['runs']['query']['status'], 'query_relevance_exhausted')

    def test_resolving_one_detail_does_not_clear_another(self):
        state = {'pendingDetails': {'a': {'runKeys': ['query']}, 'b': {'runKeys': ['query']}},
            'runs': {'query': {'status': 'public_search_exhausted'}}}
        update_detail_coverage(state)
        del state['pendingDetails']['a']
        update_detail_coverage(state)
        self.assertEqual(state['runs']['query']['status'], 'detail_failures')

    def test_detail_resolution_does_not_clear_a_failed_search(self):
        state = {'pendingDetails': {}, 'runs': {'query': {'status': 'source_failed'}}}
        update_detail_coverage(state)
        self.assertEqual(state['runs']['query']['status'], 'source_failed')

    def test_queue_does_not_skip_pending_details(self):
        model = {'models': [{'original_name': 'Model', 'canonical_public_name': 'Model'}]}
        state = {'status': 'finished', 'pendingDetails': {'url': {'runKeys': ['query']}},
            'runs': {source + ':' + query: {'status': 'public_search_exhausted'}
                for source in ('yahoo-auctions-jp', 'yahoo-furima-jp', 'rakuma')
                for query in ('Model 写真集', 'Model')}}
        self.assertFalse(collection_complete('physical', model, state))


if __name__ == '__main__':
    unittest.main()
