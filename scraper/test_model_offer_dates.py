import unittest
from model_offer_dates import normalized_offer_dates


class ModelOfferDateTests(unittest.TestCase):
    def test_legacy_store_date_is_not_reported_as_original_publication(self):
        original = dict(format='digital', url='https://books.rakuten.co.jp/rk/book/',
            releaseDate='2025-12-16', publicationDate='2025-12-16',
            publicationDateSourceUrl='https://books.rakuten.co.jp/rk/book/')
        derived = normalized_offer_dates(original)
        self.assertIsNone(derived['publicationDate'])
        self.assertEqual(derived['storeReleaseDate'], '2025-12-16')
        self.assertEqual(original['publicationDate'], '2025-12-16')

    def test_separate_publisher_evidence_is_retained(self):
        item = dict(format='digital', url='https://books.rakuten.co.jp/rk/book/',
            storeReleaseDate='2025-12-16', publicationDate='2020-06-01',
            publicationDateSourceUrl='https://www.wani.co.jp/event.php?id=book')
        self.assertEqual(normalized_offer_dates(item)['publicationDate'], '2020-06-01')

    def test_another_store_is_not_original_publication_evidence(self):
        item = dict(format='digital', url='https://books.rakuten.co.jp/rk/book/',
            releaseDate='2025-12-16', publicationDate='2025-12-01',
            publicationDateSourceUrl='https://www.grajapa.shueisha.co.jp/item/detail/gravure/book')
        self.assertIsNone(normalized_offer_dates(item)['publicationDate'])

    def test_physical_publisher_dates_are_preserved(self):
        item = dict(format='physical', publicationDate='2020-06-01')
        self.assertEqual(normalized_offer_dates(item), item)

    def test_missing_source_url_does_not_establish_original_publication(self):
        item = dict(format='digital', url='https://books.rakuten.co.jp/rk/book/',
            releaseDate='2025-12-16', publicationDate='2020-06-01',
            publicationDateSourceUrl='unknown')
        self.assertIsNone(normalized_offer_dates(item)['publicationDate'])


if __name__ == '__main__':
    unittest.main()
