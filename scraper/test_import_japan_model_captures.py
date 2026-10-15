import unittest

from import_japan_model_captures import missing_current_records


class ImportCheckpointTests(unittest.TestCase):
    def test_retired_records_do_not_block_current_manifest_verification(self):
        expected = {'current-model:source:item-1': 'current-digest'}
        checkpoint = {
            'current-model:source:item-1': 'current-digest',
            'retired-model:source:item-2': 'historical-digest',
        }

        self.assertEqual(missing_current_records(expected, checkpoint), [])

    def test_current_manifest_digest_must_match_checkpoint(self):
        expected = {'model:source:item-1': 'expected-digest'}
        checkpoint = {'model:source:item-1': 'old-digest'}

        self.assertEqual(
            missing_current_records(expected, checkpoint),
            ['model:source:item-1'],
        )


if __name__ == '__main__':
    unittest.main()
