"""Keep reviewed imports current while confirmed local source queues are running."""
import argparse
import ctypes
import os
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path
from run_japan_model_queue import source_lock

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'scraper/japan-models'


def start_database_tunnel(host, key, port):
    command = [shutil.which('ssh') or 'ssh', '-N', '-i', str(key),
        '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes',
        '-o', 'ExitOnForwardFailure=yes', '-o', 'ConnectTimeout=10',
        '-o', 'ServerAliveInterval=30', '-o', 'ServerAliveCountMax=3',
        '-L', f'127.0.0.1:{port}:127.0.0.1:5432', host]
    tunnel = subprocess.Popen(command, creationflags=subprocess.CREATE_NO_WINDOW)
    try:
        for _ in range(100):
            if tunnel.poll() is not None:
                raise RuntimeError('Database SSH connection exited before forwarding was ready')
            try:
                with socket.create_connection(('127.0.0.1', port), timeout=0.2):
                    return tunnel
            except OSError:
                time.sleep(0.1)
        raise RuntimeError('Database SSH forwarding did not become ready')
    except BaseException:
        tunnel.terminate()
        tunnel.wait(timeout=10)
        raise


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--collector-pid', type=int, action='append', required=True,
        help='Freshly confirmed Windows source-queue PID; repeat for each queue')
    parser.add_argument('--interval', type=int, default=300)
    parser.add_argument('--database-ssh-host')
    parser.add_argument('--database-ssh-key', type=Path)
    parser.add_argument('--database-tunnel-port', type=int, default=4187)
    parser.add_argument('--publish-pages', action='store_true')
    args = parser.parse_args()
    if sys.platform != 'win32' or args.interval < 60:
        parser.error('This local watcher requires Windows and an interval of at least 60 seconds')
    if bool(args.database_ssh_host) != bool(args.database_ssh_key):
        parser.error('Database SSH host and key must be supplied together')
    if not 1024 <= args.database_tunnel_port <= 65535:
        parser.error('Database tunnel port must be between 1024 and 65535')
    if args.publish_pages and not args.database_ssh_host:
        parser.error('Page publication requires the configured production SSH host and key')
    import_environment = os.environ.copy()
    if args.database_ssh_host:
        import_environment.update(POSTGRES_HOST='127.0.0.1', POSTGRES_PORT=str(args.database_tunnel_port))
    api = ctypes.WinDLL('kernel32', use_last_error=True)
    api.OpenProcess.restype = ctypes.c_void_p
    api.OpenProcess.argtypes = [ctypes.c_uint32, ctypes.c_int, ctypes.c_uint32]
    api.WaitForSingleObject.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
    api.CloseHandle.argtypes = [ctypes.c_void_p]
    handles = []
    tunnel = None
    with source_lock(OUT / 'import-watch.lock'):
        try:
            for pid in args.collector_pid:
                handle = api.OpenProcess(0x00100000, False, pid)
                if not handle:
                    raise RuntimeError(f'Collector PID {pid} is unavailable; revalidate the active queues')
                handles.append(handle)
            failures = 0
            while True:
                states = [api.WaitForSingleObject(handle, 0) for handle in handles]
                if any(status not in (0, 258) for status in states):
                    raise RuntimeError('Collector status check failed')
                if args.database_ssh_host and (tunnel is None or tunnel.poll() is not None):
                    tunnel = start_database_tunnel(args.database_ssh_host,
                        args.database_ssh_key, args.database_tunnel_port)
                    print('Database SSH forwarding ready on localhost; access rules unchanged', flush=True)
                print('Reconciling captures; active queues:', states.count(258), flush=True)
                import_command = [sys.executable, '-X', 'utf8',
                    str(ROOT / 'scraper/import_japan_model_captures.py'), '--apply']
                if args.publish_pages:
                    import_command.extend(['--page-ssh-host', args.database_ssh_host,
                        '--page-ssh-key', str(args.database_ssh_key)])
                result = subprocess.run(import_command, cwd=ROOT,
                    env=import_environment)
                failures = failures + 1 if result.returncode else 0
                if failures >= 3:
                    raise RuntimeError('Repeated import failures; captures retained for review')
                if result.returncode == 0:
                    subprocess.run([sys.executable, '-X', 'utf8',
                        str(ROOT / 'scraper/summarize_japan_models.py')], cwd=ROOT, check=True)
                if not states.count(258):
                    if result.returncode:
                        raise RuntimeError('Final import failed; review the watcher log')
                    print('Source queues exited; final snapshot imported and verified. Check coverage for source failures.', flush=True)
                    break
                time.sleep(args.interval)
        finally:
            if tunnel is not None and tunnel.poll() is None:
                tunnel.terminate()
                tunnel.wait(timeout=10)
            for handle in handles:
                api.CloseHandle(handle)


if __name__ == '__main__':
    main()
