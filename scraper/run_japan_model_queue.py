"""Run a resumable model queue serially per source, preserving capture evidence."""
import argparse
import ctypes
import json
import hashlib
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from kobo_search_scope import search_scope, PHOTOBOOK_GENRE_ID
from digital_photobook_titles import pending_title_reviews
from capture_checkpoint import save_json

ROOT = Path(__file__).resolve().parent.parent


def capture_hash(state):
    return hashlib.sha256(json.dumps(state, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def process_outcome(captured, exit_code):
    status = captured.get('status', 'process_failed')
    if exit_code:
        status = 'interrupted' if status == 'running' else 'process_failed'
    return dict(status=status, captureStatus=captured.get('status'), exitCode=exit_code,
        items=len(captured.get('items', {})), checkpointHash=capture_hash(captured))
SCRIPTS = {'physical': ('collect_model_physical.py', 'physical-state.json'),
           'grajapa': ('collect_model_digital.py', 'digital-state.json'),
           'kobo': ('collect_model_kobo.py', 'kobo-state.json'),
           'wani': ('collect_model_wani.py', 'publisher-wani-state.json')}


def collection_complete(source, model, state):
    if pending_names(source, model, state):
        return False
    if source in ('grajapa', 'kobo') and pending_title_reviews(state):
        return False
    if source == 'physical':
        if state.get('pendingDetails'):
            return False
        person = model['models'][0]
        names = list(dict.fromkeys(n for n in [person.get('original_name'),
            person.get('canonical_public_name'), person.get('english_name'),
            *person.get('aliases', [])] if n))
        queries = list(dict.fromkeys([names[0] + ' 写真集', *names]))
        runs = state.get('runs', {})
        return all(runs.get(s + ':' + q, {}).get('status') in
            ('public_search_exhausted', 'query_relevance_exhausted')
            for s in ('yahoo-auctions-jp', 'yahoo-furima-jp', 'rakuma') for q in queries)
    return (state.get('status') == 'public_search_exhausted'
        and not state.get('errors') and not state.get('error') and not state.get('nextUrl')
        and not state.get('pendingSearches'))


@contextmanager
def source_lock(path):
    """OS-owned lock releases on exit/crash; a second queue cannot overwrite captures."""
    handle = path.open('a+b')
    try:
        handle.seek(0, 2)
        if handle.tell() == 0:
            handle.write(b'0')
            handle.flush()
        handle.seek(0)
        if sys.platform == 'win32':
            import msvcrt
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield
    finally:
        handle.close()


def pending_names(source, model, state):
    """Older terminal captures may have exhausted only the native-name query."""
    if source == 'physical':
        return []
    person = model['models'][0]
    names = list(dict.fromkeys(name for name in [person.get('original_name'),
        person['canonical_public_name'], person.get('english_name'),
        *person.get('aliases', [])] if name))
    parameter = {'grajapa': 'keyword', 'kobo': 'pname', 'wani': 'tag'}[source]
    if source == 'kobo':
        searched = {search_scope(url)[0] for url in state.get('pages', [])
                    if search_scope(url)[1] == PHOTOBOOK_GENRE_ID}
    elif source == 'wani' and 'searches' in state:
        searched = {name for name, query in state['searches'].items()
                    if query.get('status') == 'public_search_exhausted'}
    else:
        searched = {parse_qs(urlparse(url).query).get(parameter, [''])[0]
                    for url in state.get('pages', [])}
    return [name for name in names if name not in searched]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', choices=SCRIPTS, required=True)
    parser.add_argument('--start-id', type=int, default=1)
    parser.add_argument('--limit', type=int, help='Bound the number of collectors launched in this run')
    parser.add_argument('--dry-run', action='store_true', help='Report pending models without launching collectors')
    parser.add_argument('--max-source-failures', type=int, default=3,
        help='Stop after consecutive source failures instead of timing out every remaining model')
    parser.add_argument('--pending-names-only', action='store_true',
        help='Backfill missing digital name queries after the active source queue finishes')
    parser.add_argument('--wait-pid', type=int, help='Wait for a confirmed existing Windows collector before starting this source queue')
    args = parser.parse_args()
    if args.wait_pid:
        api = ctypes.WinDLL('kernel32', use_last_error=True)
        api.OpenProcess.restype = ctypes.c_void_p
        api.OpenProcess.argtypes = [ctypes.c_uint32, ctypes.c_int, ctypes.c_uint32]
        api.WaitForSingleObject.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
        api.CloseHandle.argtypes = [ctypes.c_void_p]
        handle = api.OpenProcess(0x00100000, False, args.wait_pid)
        if not handle:
            raise RuntimeError('Confirmed collector handle unavailable; revalidate before starting queue')
        print(f'Waiting for confirmed {args.source} collector PID {args.wait_pid}', flush=True)
        try:
            while True:
                status = api.WaitForSingleObject(handle, 5000)
                if status == 0:
                    break
                if status != 258:
                    raise RuntimeError('Collector wait failed')
        finally:
            api.CloseHandle(handle)
    queue_root = ROOT / 'scraper/japan-models'
    with source_lock(queue_root / (args.source + '.lock')):
        run_queue(args, queue_root)


def run_queue(args, queue_root):
    queue = json.loads((queue_root / 'queue.json').read_text(encoding='utf-8'))
    progress_path = queue_root / (args.source + '-progress.json')
    progress = json.loads(progress_path.read_text(encoding='utf-8')) if progress_path.exists() else {}
    script, checkpoint = SCRIPTS[args.source]
    launched = 0
    consecutive_failures = 0
    for row in queue:
        pid = row['musecardsPersonId']
        if pid < args.start_id or row['status'] == 'reuse_fumina_capture':
            continue
        directory = ROOT / row['directory']
        state_path = directory / checkpoint
        existing = json.loads(state_path.read_text(encoding='utf-8')) if state_path.exists() else {}
        model = json.loads((directory / 'model.json').read_text(encoding='utf-8'))
        missing_names = pending_names(args.source, model, existing)
        if args.pending_names_only and (not existing or not missing_names):
            continue
        if collection_complete(args.source, model, existing):
            if args.dry_run:
                continue
            progress[str(pid)] = {'status': existing['status'], 'items': len(existing.get('items', {}))}
        else:
            print(f"Collecting {args.source}: {pid} {row['name']}", flush=True)
            if args.dry_run:
                launched += 1
                if args.limit and launched >= args.limit:
                    break
                continue
            with (directory / (args.source + '-collector.log')).open('a', encoding='utf-8') as log:
                result = subprocess.run([sys.executable, '-X', 'utf8', str(ROOT / 'scraper' / script),
                    '--model-file', str((directory / 'model.json').relative_to(ROOT)),
                    '--output', row['directory']], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
            captured = json.loads(state_path.read_text(encoding='utf-8')) if state_path.exists() else {}
            progress[str(pid)] = process_outcome(captured, result.returncode)
            launched += 1
            consecutive_failures = consecutive_failures + 1 if captured.get('status') == 'source_failed' or result.returncode else 0
        save_json(progress_path, progress)
        print(f"Saved {args.source}: {pid} {progress[str(pid)]}", flush=True)
        if args.max_source_failures > 0 and consecutive_failures >= args.max_source_failures:
            print('Source repeatedly unavailable; saved checkpoints for later resume', flush=True)
            break
        if args.limit and launched >= args.limit:
            break


if __name__ == '__main__':
    main()
