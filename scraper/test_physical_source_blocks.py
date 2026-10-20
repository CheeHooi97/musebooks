import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from physical_source_blocks import block_is_active, load_source_blocks, record_source_block


class PhysicalSourceBlockTests(unittest.TestCase):
    def test_recorded_block_has_a_cooldown_and_persists_evidence_pointer(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'source-blocks.json'
            now = datetime(2026, 10, 16, 0, 0, tzinfo=timezone.utc)
            block = record_source_block('yahoo-furima-jp', 'temporary access restriction',
                details={'evidenceFile': 'physical-failure.json'}, path=path, now=now)
            saved = load_source_blocks(path)['yahoo-furima-jp']
            self.assertTrue(block_is_active(saved, now + timedelta(hours=23)))
            self.assertFalse(block_is_active(block, now + timedelta(hours=24)))
            self.assertEqual(saved['evidenceFile'], 'physical-failure.json')

    def test_missing_or_invalid_cooldown_stays_blocked_conservatively(self):
        self.assertTrue(block_is_active({'status': 'source_blocked'}))
        self.assertTrue(block_is_active({'status': 'source_blocked', 'retryAfter': 'not-a-date'}))
        self.assertFalse(block_is_active({'status': 'public_search_exhausted'}))


if __name__ == '__main__':
    unittest.main()
