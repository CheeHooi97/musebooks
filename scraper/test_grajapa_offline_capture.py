import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import collect_model_digital as collector
import collect_model_kobo as kobo


class OfflineCaptureTests(unittest.TestCase):
    def run_capture(self, root, *, cached=True, alias=None, stalled=False):
        person = dict(id=997, canonical_public_name='Model', original_name='Model', aliases=[alias] if alias else [])
        (root / 'model.json').write_text(json.dumps({'models': [person]}), encoding='utf-8')
        output = root / 'output'
        output.mkdir()
        eid = 'a' * 32
        url = 'https://www.grajapa.shueisha.co.jp/item/detail/gravure/' + eid
        state = dict(items={}, candidates={url: dict(url=url, title='Model デジタル写真集')},
            pages=['https://www.grajapa.shueisha.co.jp/search?keyword=Model'], rejected={},
            errors={url: 'previous timeout'}, nextUrl='', pendingSearches=[], status='detail_failures')
        if stalled:
            state['status'] = 'pagination_stalled'
        (output / 'digital-state.json').write_text(json.dumps(state), encoding='utf-8')
        observed = '2026-10-01T00:00:00Z'
        if cached:
            cache_root = root / 'scraper/japan-models/shared-details/grajapa'
            cache_root.mkdir(parents=True)
            evidence = dict(body='モデル：Model\n出版社：集英社\n発売日：2026-10-01\n￥1,100（税込）\n買い物かごに追加',
                structured=dict(name='Model デジタル写真集', image='https://example.com/' + eid + '.jpg'),
                imageUrls=[], observedAt=observed)
            (cache_root / (eid + '.json')).write_text(json.dumps(evidence), encoding='utf-8')
        with patch.object(collector, '__file__', str(root / 'scraper/collect_model_digital.py')), \
                patch('sys.argv', ['collector', '--offline', '--model-file', 'model.json', '--output', 'output']), \
                patch.object(collector, 'launch', side_effect=AssertionError('Offline mode launched a browser')) as launch, \
                redirect_stdout(io.StringIO()):
            collector.main()
        launch.assert_not_called()
        return json.loads((output / 'digital-state.json').read_text(encoding='utf-8')), url, observed

    def test_saved_evidence_recovers_timeout_without_browser_or_new_observation(self):
        with tempfile.TemporaryDirectory() as directory:
            state, url, observed = self.run_capture(Path(directory))
            self.assertEqual(state['status'], 'public_search_exhausted')
            self.assertEqual(state['errors'], {})
            self.assertEqual(state['items'][url]['priceMinor'], 1100)
            self.assertEqual(state['items'][url]['observedAt'], observed)

    def test_missing_product_evidence_remains_pending(self):
        with tempfile.TemporaryDirectory() as directory:
            state, url, _ = self.run_capture(Path(directory), cached=False)
            self.assertEqual(state['status'], 'detail_failures')
            self.assertIn(url, state['errors'])
            self.assertEqual(state['items'], {})

    def test_unsearched_alias_stays_pending_even_with_recovered_product(self):
        with tempfile.TemporaryDirectory() as directory:
            state, url, _ = self.run_capture(Path(directory), alias='Alias')
            self.assertEqual(state['status'], 'pending_searches')
            self.assertTrue(state['pendingSearches'])
            self.assertIn(url, state['items'])
            self.assertEqual(len(state['pages']), 1)

    def test_offline_recovery_cannot_resolve_a_pagination_stall(self):
        with tempfile.TemporaryDirectory() as directory:
            state, url, _ = self.run_capture(Path(directory), stalled=True)
            self.assertEqual(state['status'], 'pagination_stalled')
            self.assertIn(url, state['items'])

    def test_kobo_offline_recovery_also_retains_a_pagination_stall(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'model.json').write_text(json.dumps({'models': [dict(id=997, canonical_public_name='Model')]}), encoding='utf-8')
            output = root / 'output'
            output.mkdir()
            state = dict(items={}, candidates={}, rejected={}, errors={}, nextUrl='',
                pendingSearches=[], status='pagination_stalled',
                pages=['https://books.rakuten.co.jp/search?g=101915&pname=Model'])
            (output / 'kobo-state.json').write_text(json.dumps(state), encoding='utf-8')
            with patch.object(kobo, 'ROOT', root), \
                    patch('sys.argv', ['collector', '--offline', '--model-file', 'model.json', '--output', 'output']), \
                    patch.object(kobo, 'launch', side_effect=AssertionError('Offline mode launched a browser')) as launch, \
                    redirect_stdout(io.StringIO()):
                kobo.main()
            launch.assert_not_called()
            after = json.loads((output / 'kobo-state.json').read_text(encoding='utf-8'))
            self.assertEqual(after['status'], 'pagination_stalled')
            self.assertEqual(after['pages'], state['pages'])


if __name__ == '__main__':
    unittest.main()
