import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from capture_checkpoint import save_json


class CheckpointTests(unittest.TestCase):
    def test_locked_target_retains_old_capture_until_atomic_replacement(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'state.json'
            save_json(target, {'items': ['old']})
            original_replace = os.replace
            calls = []

            def briefly_locked(source, destination):
                calls.append(source)
                self.assertEqual(json.loads(Path(source).read_text(encoding='utf-8')), {'items': ['新しい']})
                if len(calls) < 3:
                    self.assertEqual(json.loads(target.read_text(encoding='utf-8')), {'items': ['old']})
                    raise PermissionError('Windows sharing violation')
                return original_replace(source, destination)

            with patch('capture_checkpoint.os.replace', side_effect=briefly_locked), patch('capture_checkpoint.time.sleep'):
                save_json(target, {'items': ['新しい']})
            self.assertEqual(json.loads(target.read_text(encoding='utf-8')), {'items': ['新しい']})
            self.assertEqual(len(calls), 3)
            self.assertEqual(list(Path(directory).iterdir()), [target])

    def test_permanent_lock_raises_and_preserves_last_valid_capture(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'state.json'
            save_json(target, {'status': 'completed'})
            with patch('capture_checkpoint.os.replace', side_effect=PermissionError('locked')) as replace, patch('capture_checkpoint.time.sleep'):
                with self.assertRaises(PermissionError):
                    save_json(target, {'status': 'running'})
            self.assertEqual(replace.call_count, 5)
            self.assertEqual(json.loads(target.read_text(encoding='utf-8')), {'status': 'completed'})
            self.assertEqual(list(Path(directory).iterdir()), [target])

    def test_other_filesystem_errors_are_not_retried(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'state.json'
            save_json(target, {'items': []})
            with patch('capture_checkpoint.os.replace', side_effect=OSError('filesystem unavailable')) as replace, patch('capture_checkpoint.time.sleep') as sleep:
                with self.assertRaises(OSError):
                    save_json(target, {'items': ['pending']})
            self.assertEqual(replace.call_count, 1)
            sleep.assert_not_called()
            self.assertEqual(json.loads(target.read_text(encoding='utf-8')), {'items': []})
            self.assertEqual(list(Path(directory).iterdir()), [target])


if __name__ == '__main__':
    unittest.main()
