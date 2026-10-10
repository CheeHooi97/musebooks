"""Continue source-local Japan searches with durable capture/import checkpoints."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
QUERIES = ['グラビア 写真集', '写真集', 'アイドル 写真集', '俳優 写真集', '女優 写真集', 'モデル 写真集']

def save(path, state):
    temporary = path.with_suffix('.new.json')
    temporary.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')
    os.replace(temporary, path)

def run(arguments, cwd=ROOT):
    subprocess.run(arguments, cwd=cwd, check=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', required=True, choices=['yahoo-auctions-jp', 'yahoo-furima-jp', 'rakuma'])
    parser.add_argument('--state', required=True)
    parser.add_argument('--resume-from', help='already imported batch manifest whose cursor should be continued')
    parser.add_argument('--resume-query', choices=QUERIES, help='search query for an older manifest without collection metadata')
    parser.add_argument('--operation', default='active_discovery', choices=['active_discovery', 'sold_discovery'])
    args = parser.parse_args()
    if args.operation == 'sold_discovery' and args.source != 'yahoo-auctions-jp':
        parser.error('Only Yahoo Auctions has a verified keyword sold-search route')
    path = (ROOT / args.state).resolve()
    if not path.is_relative_to(ROOT):
        parser.error('State must stay inside the repository')
    if path.exists():
        state = json.loads(path.read_text(encoding='utf-8'))
        if state['source'] != args.source or state['operation'] != args.operation:
            parser.error('State source/operation mismatch')
    else:
        state = dict(source=args.source, operation=args.operation, queryIndex=0,
                     cursor='', batchIndex=0, history=[], status='running')
        if args.resume_from:
            records = json.loads((ROOT / args.resume_from).read_text(encoding='utf-8'))
            batch = records[0]['batch']
            if batch['sourceId'] != args.source:
                parser.error('Resume manifest source mismatch')
            collection = records[0].get('collection', {})
            resume_query = collection.get('query') or args.resume_query
            if resume_query not in QUERIES:
                parser.error('Resume manifest needs a recognized query or explicit --resume-query')
            if collection.get('operation', args.operation) != args.operation:
                parser.error('Resume manifest operation mismatch')
            state['queryIndex'] = QUERIES.index(resume_query)
            if batch['hasMore']:
                if not batch['nextCursor']:
                    parser.error('Batch reports more results without a cursor')
                state['cursor'] = batch['nextCursor']
            else:
                state['queryIndex'] += 1
        save(path, state)
    while state['queryIndex'] < len(QUERIES):
        query = QUERIES[state['queryIndex']]
        output = ROOT / 'scraper' / f"japan-crawl-{args.source}-{args.operation}-{state['queryIndex']}-{state['batchIndex']}.json"
        state['status'] = 'running'
        state['pending'] = str(output.relative_to(ROOT))
        save(path, state)
        command = [sys.executable, '-X', 'utf8', 'scraper/expand_japan_marketplace.py',
                   '--source', args.source, '--operation', args.operation,
                   '--query', query, '--cursor', state['cursor'], '--output', str(output)]
        capture = output.with_suffix('.capture.json')
        if capture.exists():
            command += ['--capture', str(capture)]
        print('Collect:', args.source, args.operation, query, 'cursor:', state['cursor'], flush=True)
        try:
            run(command)
            run([sys.executable, '-X', 'utf8', 'scraper/review_japan_import.py', str(output)])
            records = json.loads(output.read_text(encoding='utf-8'))
            batch = records[0]['batch']
            failures = json.loads(output.with_suffix('.failures.json').read_text(encoding='utf-8'))
            unresolved = [entry for entry in failures if entry.get('phase') == 'image']
            if batch['items']:
                run(['go', 'run', './cmd/catalog-import', '-manifest', str(output), '-apply'], ROOT / 'backend')
            if batch['hasMore'] and (not batch['nextCursor'] or batch['nextCursor'] == state['cursor']):
                raise RuntimeError('Collector returned a missing or nonadvancing cursor')
            state['history'].append(dict(query=query, inputCursor=state['cursor'],
                                        nextCursor=batch['nextCursor'], hasMore=batch['hasMore'],
                                        manifest=str(output.relative_to(ROOT)), observations=len(batch['items']),
                                        unresolvedImages=unresolved))
            state['batchIndex'] += 1
            state.pop('pending', None)
            if batch['hasMore']:
                state['cursor'] = batch['nextCursor']
            else:
                state['queryIndex'] += 1
                state['cursor'] = ''
            save(path, state)
            run(['go', 'run', './cmd/japan-audit'], ROOT / 'backend')
        except Exception as exc:
            state['status'] = 'needs_attention'
            state['error'] = str(exc)
            save(path, state)
            raise
    state['status'] = 'searches_exhausted_with_image_failures' if any(entry.get('unresolvedImages') for entry in state['history']) else 'searches_exhausted'
    save(path, state)
    print('Configured searches exhausted:', args.source, args.operation, flush=True)

if __name__ == '__main__':
    main()
