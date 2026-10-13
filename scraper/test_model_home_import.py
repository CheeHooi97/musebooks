import json
import unittest
from pathlib import Path
from prepare_model_home_import import prepare, identity, publication_for_edition


class ModelHomeIdentityTests(unittest.TestCase):
    def test_collaborative_store_product_reuses_work_for_another_featured_model(self):
        external_id = '70671df428a83cd7974917adb51b3459'
        edition_id = identity('edition-jp-', 'rakuten-kobo-jp:' + external_id + ':digital')
        shared = publication_for_edition(edition_id)
        self.assertIsNotNone(shared)
        item = dict(sourceId='rakuten-kobo-jp', platform='Kobo', externalId=external_id,
            url='https://books.rakuten.co.jp/rk/' + external_id + '/', format='digital',
            title='バスト100cmグラドル　爆乳連峰', publisher='小学館', imageUrl='',
            observedAt='2026-10-13T00:00:00Z')
        capture = dict(model=dict(id=999999, canonical_public_name='Other featured model'), items=[item])
        record = prepare(capture, [])[0]
        self.assertEqual(record['work']['id'], shared['id'])
        self.assertEqual(record['edition']['id'], edition_id)

    def test_digital_store_release_date_does_not_require_a_print_publication_date(self):
        item = dict(sourceId='store-test', platform='Test', externalId='ebook',
            url='https://store.example/book', format='digital', title='Example photo book',
            publisher='Example', imageUrl='https://store.example/cover.jpg',
            releaseDate='2025-03-04', storeReleaseDate='2025-03-04', publicationDate=None,
            observedAt='2026-10-11T00:00:00Z')
        record = prepare(dict(physicalBooks=[], items=[item]), [])[0]
        self.assertEqual(record['edition']['releaseDate'], '2025-03-04T00:00:00Z')
        self.assertNotIn('publicationDate', record['batch']['items'][0])

    def test_digital_edition_stores_store_date_when_original_publication_is_known(self):
        item = dict(sourceId='store-test', platform='Test', externalId='ebook-dates',
            url='https://store.example/book', format='digital', title='Example photo book',
            publisher='Example', imageUrl='', releaseDate='2025-03-04',
            storeReleaseDate='2025-03-04', publicationDate='2020-06-01',
            observedAt='2026-10-13T00:00:00Z')
        record = prepare(dict(physicalBooks=[], items=[item]), [])[0]
        self.assertEqual(record['edition']['releaseDate'], '2025-03-04T00:00:00Z')

    def test_japan_groups_reuse_work_and_keep_source_editions(self):
        root = Path(__file__).parent
        plan = json.loads((root / 'japan-work-identities.json').read_text(encoding='utf-8'))
        checked = 0
        for path in (root / 'japan-models').glob('*/listings.json'):
            capture = json.loads(path.read_text(encoding='utf-8'))
            if capture['model']['id'] == 6:
                continue
            for record in prepare(capture, []):
                edition = record['edition']
                if not edition:
                    continue
                shared = plan['identities'].get(str(capture['model']['id']), {}).get(edition['editionLabel'] + '\0' + edition['publisher'])
                if shared:
                    self.assertEqual(record['work']['id'], shared['id'])
                    self.assertEqual(edition['workId'], shared['id'])
                    item = record['batch']['items'][0]
                    key = record['source']['id'] + ':' + item['externalId'] if edition['format'] == 'digital' else 'jp-isbn-' + edition['isbn']
                    self.assertEqual(edition['id'], identity('edition-jp-', key + ':' + edition['format']))
                    checked += 1
        self.assertGreaterEqual(checked, 400)

    def test_reviewed_store_products_share_work_but_retain_editions(self):
        reviewed = json.loads((Path(__file__).parent / 'fumina-suzuki-work-identities.json').read_text(encoding='utf-8'))
        for group in reviewed['groups']:
            for member in group['members']:
                if member['format'] != 'digital':
                    continue
                item = dict(sourceId='store-test', platform='Test', externalId=member['editionId'],
                            url='https://example.com/book', format='digital', title=member['title'],
                            publisher=member['publisher'], imageUrl='https://example.com/cover.jpg',
                            observedAt='2026-10-11T00:00:00Z')
                result = prepare(dict(physicalBooks=[], items=[item]), [])[0]
                self.assertEqual(result['work']['id'], group['workId'])
                self.assertEqual(result['work']['originalTitle'], group['title'])
                self.assertEqual(result['edition']['workId'], group['workId'])
                self.assertEqual(result['edition']['editionLabel'], member['title'])
                self.assertEqual(result['edition']['id'], identity('edition-jp-', 'store-test:' + member['editionId'] + ':digital'))
                self.assertEqual(result['batch']['items'][0]['editionId'], result['edition']['id'])

    def test_unreviewed_volumes_and_ambiguous_titles_remain_separate(self):
        for titles in [('鈴木ふみ奈 vol.1', '鈴木ふみ奈 vol.2'),
                       ('【オールアザー版】鈴木ふみ奈写真集', '【オールアザー版】鈴木ふみ奈写真集')]:
            items = [dict(sourceId='store-test', platform='Test', externalId=str(i),
                          url='https://example.com/' + str(i), title=title, publisher='KADOKAWA',
                          format='digital', imageUrl='', observedAt='2026-10-11T00:00:00Z')
                     for i, title in enumerate(titles)]
            records = prepare(dict(physicalBooks=[], items=items), [])
            self.assertNotEqual(records[0]['work']['id'], records[1]['work']['id'])
            self.assertNotEqual(records[0]['edition']['id'], records[1]['edition']['id'])

if __name__ == '__main__':
    unittest.main()
