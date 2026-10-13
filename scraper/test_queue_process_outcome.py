import unittest
import tempfile
import json
import io
from contextlib import redirect_stdout
from pathlib import Path
from argparse import Namespace
from unittest.mock import patch
from subprocess import CompletedProcess
from run_japan_model_queue import process_outcome, capture_hash, run_queue


class QueueProcessOutcomeTests(unittest.TestCase):
    def test_partial_checkpoint_does_not_make_failed_process_successful(self):
        state = {'status': 'running', 'items': {'offer': {'priceMinor': 1000}}}
        result = process_outcome(state, 4294967295)
        self.assertEqual(result['status'], 'interrupted')
        self.assertEqual(result['captureStatus'], 'running')
        self.assertEqual(result['items'], 1)
        self.assertEqual(state['status'], 'running')
        self.assertEqual(result['checkpointHash'], capture_hash(state))

    def test_successful_capture_keeps_its_coverage_status(self):
        self.assertEqual(process_outcome({'status': 'incomplete'}, 0)['status'], 'incomplete')

    def test_stale_process_record_cannot_describe_a_changed_checkpoint(self):
        state = {'status': 'running', 'items': {}}
        result = process_outcome(state, 1)
        state['items']['new'] = {'priceMinor': 1200}
        self.assertNotEqual(result['checkpointHash'], capture_hash(state))

    def test_repeated_failures_stop_even_when_partial_captures_exist(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            queue_root = root / 'scraper/japan-models'
            queue_root.mkdir(parents=True)
            rows = []
            for person_id in (1, 2, 3):
                relative = f'scraper/japan-models/{person_id}'
                output = root / relative
                output.mkdir()
                (output / 'model.json').write_text(json.dumps({'models': [dict(id=person_id,
                    canonical_public_name='Model', original_name='Model')]}), encoding='utf-8')
                (output / 'physical-state.json').write_text(json.dumps(dict(status='running',
                    items={'existing': {}}, runs={})), encoding='utf-8')
                rows.append(dict(musecardsPersonId=person_id, directory=relative, status='queued', name='Model'))
            (queue_root / 'queue.json').write_text(json.dumps(rows), encoding='utf-8')
            args = Namespace(source='physical', start_id=0, pending_names_only=False,
                dry_run=False, limit=0, max_source_failures=2)
            with patch('run_japan_model_queue.ROOT', root), \
                    patch('run_japan_model_queue.subprocess.run', return_value=CompletedProcess([], 1)) as run, \
                    redirect_stdout(io.StringIO()):
                run_queue(args, queue_root)
            self.assertEqual(run.call_count, 2)
            progress = json.loads((queue_root / 'physical-progress.json').read_text(encoding='utf-8'))
            self.assertEqual(set(progress), {'1', '2'})
            self.assertEqual(progress['1']['status'], 'interrupted')


if __name__ == '__main__':
    unittest.main()
