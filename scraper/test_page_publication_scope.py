import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from publish_japan_import_pages import publish


class PagePublicationScopeTests(unittest.TestCase):
    def fixture(self, output, **changes):
        result = dict(expected=2, present=2, priceMismatches=0, formatMismatches=0,
            missingMedia=0, missingPublisherMedia=0, workMismatches=0, exclusionMismatches=0)
        result.update(changes)
        for name, value in {
            'import-verification.json': {'checkedAt': 'verified', 'result': result},
            'verification-manifest.json': [{'work': {'slug': 'a'}}, {'work': {'slug': 'b'}}],
            'pending-import.json': [{'work': {'slug': 'a'}}, {'work': {'slug': 'unverified'}}],
            'page-publication-pending.json': {'refreshSlugs': ['b', 'superseded']},
            'page-publication-verification.json': {'mode': 'applied_verified_catalog_pages',
                'requestedBooks': 2, 'changedPages': 2, 'newPages': 1,
                'checkedAt': 'published', 'outputDir': '/managed/release'},
        }.items():
            (output / name).write_text(json.dumps(value), encoding='utf-8')

    def test_incomplete_database_snapshot_prevents_network_or_publication(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            self.fixture(output, present=1)
            with patch('publish_japan_import_pages.OUT', output), patch('publish_japan_import_pages.subprocess.run') as run:
                with self.assertRaises(RuntimeError):
                    publish('server', 'key', apply=True)
            run.assert_not_called()

    def test_database_mismatch_prevents_network_or_publication(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            self.fixture(output, workMismatches=1)
            with patch('publish_japan_import_pages.OUT', output), patch('publish_japan_import_pages.subprocess.run') as run:
                with self.assertRaises(RuntimeError):
                    publish('server', 'key', apply=True)
            run.assert_not_called()

    def test_retry_scope_preserves_pending_routes_and_excludes_unverified_work(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            self.fixture(output)
            with patch('publish_japan_import_pages.OUT', output), patch('publish_japan_import_pages.subprocess.run'):
                publish('server', 'key', apply=True)
            payload = json.loads((output / 'page-publication-manifest.json').read_text(encoding='utf-8'))
            self.assertEqual(payload['bookSlugs'], ['a', 'b'])
            self.assertEqual(payload['refreshSlugs'], ['a', 'b'])
            pending = json.loads((output / 'page-publication-pending.json').read_text(encoding='utf-8'))
            self.assertEqual(pending['refreshSlugs'], [])


if __name__ == '__main__':
    unittest.main()
