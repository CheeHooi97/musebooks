"""Capture resumable Japan marketplace batches and prepare R2-backed imports."""
import argparse
import json
from pathlib import Path
import photobook_worker
from photobook_worker import collect
from r2_covers import R2Covers, load_env

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', required=True)
    parser.add_argument('--query', default='グラビア 写真集')
    parser.add_argument('--operation', default='active_discovery')
    parser.add_argument('--cursor', default='')
    parser.add_argument('--output', required=True)
    parser.add_argument('--details', type=int, default=60)
    parser.add_argument('--capture', help='reuse a saved capture without revisiting marketplaces')
    args = parser.parse_args()
    records = json.loads(Path('scraper/japan-marketplace-import-20261010.json').read_text(encoding='utf-8-sig'))
    source = next(record['source'] for record in records if record['source']['id'] == args.source)
    browser_source = dict(source)
    browser_source['allowedHosts'] = source['allowedHosts'].split(',')
    browser_source['allowedFormats'] = ['physical']
    request = dict(sourceId=args.source, source=browser_source, operation=args.operation,
                   query=args.query, format='physical', maxCandidates=200,
                   maxDetailPages=args.details, maxPages=4, pageCursor=args.cursor)
    if args.capture:
        batch = json.loads(Path(args.capture).read_text(encoding='utf-8'))
        if batch.get('sourceId') != args.source:
            raise ValueError('Capture source does not match requested source')
    else:
        snapshot = photobook_worker.detail_snapshot
        def progress_snapshot(*values, **options):
            print('Inspect:', values[1], flush=True)
            return snapshot(*values, **options)
        photobook_worker.detail_snapshot = progress_snapshot
        batch = collect(request)
    output = Path(args.output)
    output.with_suffix('.capture.json').write_text(json.dumps(batch, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Capture:', len(batch.get('items', [])), 'items;', batch.get('diagnostics'), flush=True)
    load_env('backend/.env')
    store = R2Covers()
    media = []
    accepted = []
    failures = []
    cached = {}
    for item in batch.get('items', []):
        excluded = photobook_worker.photobook_title_exclusion(item['title'])
        if excluded:
            failures.append({'externalId': item['externalId'], 'phase': 'scope', 'error': excluded})
            continue
        original = item.get('imageUrl', '')
        if not original:
            failures.append({'externalId': item['externalId'], 'phase': 'image', 'error': 'No source image'})
            continue
        try:
            if original not in cached:
                cached[original] = store.upload(original)
            item['imageUrl'] = cached[original]['url']
            accepted.append(item)
            media.append(dict(externalId=item['externalId'], mediaType='listing_image',
                              originalUrl=original, storageUrl=item['imageUrl'],
                              sourceUrl=item['url'], isPrimary=True))
            print('R2:', item['externalId'], flush=True)
        except Exception as exc:
            failures.append({'externalId': item['externalId'], 'phase': 'image', 'error': str(exc)})
    batch['items'] = accepted
    output.write_text(json.dumps([dict(collection=dict(query=args.query, operation=args.operation, inputCursor=args.cursor), origin=dict(code='JP', name='Japan', nativeName='日本'),
                     work={}, edition={}, source=source, batch=batch, media=media)],
                     ensure_ascii=False, indent=2), encoding='utf-8')
    output.with_suffix('.failures.json').write_text(json.dumps(failures, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Prepared', len(accepted), 'observations; image failures:',
          sum(entry['phase'] == 'image' for entry in failures),
          '; scope exclusions:', sum(entry['phase'] == 'scope' for entry in failures), flush=True)

if __name__ == '__main__':
    main()
