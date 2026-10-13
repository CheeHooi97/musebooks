import subprocess
import unittest
from argparse import Namespace
from unittest.mock import patch
from unittest.mock import MagicMock

from import_japan_model_captures import import_captures
from watch_japan_model_imports import start_database_tunnel


class AutomaticImportValidationTests(unittest.TestCase):
    def test_failed_quality_audit_prevents_database_mutations(self):
        commands = []

        def run(command, **kwargs):
            commands.append(command)
            if any(str(value).endswith('audit_japan_model_captures.py') for value in command):
                raise subprocess.CalledProcessError(1, command)
            return subprocess.CompletedProcess(command, 0)

        args = Namespace(apply=True, repairer='.tmp/repairer.exe',
                         importer='.tmp/importer.exe', verifier='.tmp/verifier.exe')
        with patch('import_japan_model_captures.subprocess.run', side_effect=run):
            with self.assertRaises(subprocess.CalledProcessError):
                import_captures(args)
        self.assertTrue(any('-bindings-output' in command for command in commands))
        self.assertFalse(any('-apply' in command for command in commands))
        self.assertFalse(any(str(value).endswith('importer.exe') for command in commands for value in command))

    def test_database_forwarding_is_local_and_checks_known_host_key(self):
        process = MagicMock()
        process.poll.return_value = None
        with patch('watch_japan_model_imports.subprocess.Popen', return_value=process) as launch, \
                patch('watch_japan_model_imports.socket.create_connection') as connect:
            self.assertIs(start_database_tunnel('root@server', 'existing-key', 4187), process)
        command = launch.call_args.args[0]
        self.assertIn('StrictHostKeyChecking=yes', command)
        self.assertIn('ExitOnForwardFailure=yes', command)
        self.assertIn('127.0.0.1:4187:127.0.0.1:5432', command)
        connect.assert_called_once_with(('127.0.0.1', 4187), timeout=0.2)

    def test_failed_ssh_connection_cleans_up_and_never_returns_ready(self):
        process = MagicMock()
        process.poll.return_value = 255
        with patch('watch_japan_model_imports.subprocess.Popen', return_value=process), \
                patch('watch_japan_model_imports.socket.create_connection') as connect:
            with self.assertRaises(RuntimeError):
                start_database_tunnel('root@server', 'existing-key', 4187)
        connect.assert_not_called()
        process.terminate.assert_called_once()
        process.wait.assert_called_once_with(timeout=10)


if __name__ == '__main__':
    unittest.main()
