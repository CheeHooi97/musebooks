import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import prepare_japan_work_repair as repair


class WorkIdentityTests(unittest.TestCase):
    def test_later_store_discovery_preserves_existing_canonical_identity(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            directory = root / 'japan-models/1'
            directory.mkdir(parents=True)
            (directory / 'listings.json').write_text(json.dumps({'model': {'id': 1}}), encoding='utf-8')
            records = [dict(work=dict(id='work-existing', originalTitle='Book'),
                edition=dict(id='edition-' + source, format='digital', editionLabel='Book', publisher='Publisher'),
                source=dict(id=source), batch=dict(items=[dict(externalId=source)]),
                featuredPerson=dict(slug='model-one')) for source in ('store-a', 'store-b')]
            (directory / 'home-import.json').write_text(json.dumps(records), encoding='utf-8')
            (root / 'japan-work-identities.json').write_text(json.dumps({'identities': {'1': {
                'Book\0Publisher': dict(id='work-existing', title='Book')}}}), encoding='utf-8')
            with patch.object(repair, 'ROOT', root):
                plan = repair.build()
            self.assertEqual(plan['groups'][0]['workId'], 'work-existing')
            self.assertEqual(plan['identities']['1']['Book\0Publisher']['id'], 'work-existing')

            # A plan may have been prepared before one of its stores was imported.
            # Prefer the already imported edition's work over a nonexistent ID.
            (root / 'japan-work-identities.json').write_text(json.dumps({'identities': {'1': {
                'Book\0Publisher': dict(id='work-not-imported', title='Book')}}}), encoding='utf-8')
            (root / 'japan-models/catalog-work-bindings.json').write_text(json.dumps({
                'works': {'work-existing': dict(title='Book', status='published')},
                'editions': {'edition-store-a': 'work-existing'}}), encoding='utf-8')
            with patch.object(repair, 'ROOT', root):
                plan = repair.build()
            self.assertEqual(plan['groups'][0]['workId'], 'work-existing')

    def test_normalization_keeps_volumes_and_punctuation_distinct(self):
        self.assertEqual(repair.normalized('Ｂｏｏｋ  Title'), repair.normalized('booktitle'))
        self.assertNotEqual(repair.normalized('Book vol.1'), repair.normalized('Book vol.2'))
        self.assertNotEqual(repair.normalized('Book!'), repair.normalized('Book'))


if __name__ == '__main__':
    unittest.main()
