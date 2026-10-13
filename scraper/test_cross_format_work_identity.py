import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import prepare_japan_work_repair as repair
from prepare_model_home_import import edition_work_index


class CrossFormatIdentityTests(unittest.TestCase):
    def review(self, root, *, isbn='9784847086731', digital_title='Model 写真集 Book', groups=None):
        pair = dict(musecardsPersonId=42, title='Model写真集Book', publisher='Publisher', isbn='9784847086731',
            physicalEditionId='print-edition', physicalWorkId='print-work', digitalEditionId='ebook-edition',
            digitalWorkId='ebook-work', publisherUrl='https://publisher.example/book', storeUrl='https://store.example/ebook')
        records = [dict(work=dict(id=wid), featuredPerson=dict(slug='model-example'), edition=dict(
            id=eid, workId=wid, format=fmt, editionLabel=title, publisher='Publisher', isbn=book_isbn, metadataSourceUrl=url))
            for eid, wid, fmt, title, book_isbn, url in [
                ('print-edition', 'print-work', 'physical', pair['title'], isbn, pair['publisherUrl']),
                ('ebook-edition', 'ebook-work', 'digital', digital_title, '', pair['storeUrl'])]]
        directory = root / 'japan-models/42'
        directory.mkdir(parents=True)
        (directory / 'home-import.json').write_text(json.dumps(records), encoding='utf-8')
        (root / 'japan-cross-format-identities.json').write_text(json.dumps({'pairs': [pair]}), encoding='utf-8')
        groups = [] if groups is None else groups
        identities = {}
        with patch.object(repair, 'ROOT', root):
            repair.add_reviewed_cross_formats(groups, identities)
        return groups, identities

    def test_reviewed_pair_shares_publication_and_keeps_both_editions(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            groups, identities = self.review(root)
            self.assertEqual(len(groups), 1)
            self.assertEqual(groups[0]['workId'], 'print-work')
            self.assertEqual({member['format'] for member in groups[0]['members']}, {'physical', 'digital'})
            plan = root / 'plan.json'
            plan.write_text(json.dumps({'groups': groups}), encoding='utf-8')
            index = edition_work_index(plan, plan.stat().st_mtime_ns)
            self.assertEqual(index['print-edition'], index['ebook-edition'])
            self.assertEqual(identities['42']['Model 写真集 Book\0Publisher']['id'], 'print-work')

    def test_changed_print_isbn_is_not_merged(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, 'ISBN changed'):
                self.review(Path(directory), isbn='9784847047695')

    def test_different_digital_content_qualifier_is_not_merged(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, 'evidence changed'):
                self.review(Path(directory), digital_title='Model 写真集 Book オールアザー版')

    def test_conflicting_existing_identity_requires_review(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, 'conflicts'):
                self.review(Path(directory), groups=[dict(workId='another-work', members=[dict(editionId='ebook-edition')])])


if __name__ == '__main__':
    unittest.main()
