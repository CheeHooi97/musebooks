"""Capture Japan photobook prices locally, without media uploads or ingestion."""
import argparse
import csv
import json
from pathlib import Path

import photobook_worker
from photobook_worker import collect, iso_utc


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    parser.add_argument('--details', type=int, default=10)
    parser.add_argument('--source', action='append', choices=['yahoo-auctions-jp', 'yahoo-furima-jp', 'rakuma'])
    parser.add_argument('--query', default='グラビア 写真集')
    parser.add_argument('--model-snapshot', help='read-only MuseCards model export containing exactly one model')
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    output = (root / args.output).resolve()
    if not output.is_relative_to(root):
        parser.error('Output must stay inside the repository')
    output.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((root / 'scraper/japan-marketplace-import-20261010.json').read_text(encoding='utf-8-sig'))
    sources = {record['source']['id']: record['source'] for record in manifest}
    rows, runs = [], []
    model = None
    if args.model_snapshot:
        models = json.loads((root / args.model_snapshot).read_text(encoding='utf-8'))['models']
        if len(models) != 1:
            parser.error('Select exactly one MuseCards model')
        model = models[0]
    assets = {}
    snapshot = photobook_worker.detail_snapshot
    def progress_snapshot(*values, **options):
        print('Inspecting:', values[1], flush=True)
        detail = snapshot(*values, **options)
        image_value = detail.get('structured', {}).get('image', [])
        image_value = image_value if isinstance(image_value, list) else [image_value]
        urls = []
        for value in image_value:
            value = value.get('url') or value.get('contentUrl') if isinstance(value, dict) else value
            if isinstance(value, str) and value.startswith(('https://', 'http://')) and value not in urls:
                urls.append(value)
        assets[values[1]] = urls
        return detail
    photobook_worker.detail_snapshot = progress_snapshot
    for source_id in args.source or ['yahoo-auctions-jp', 'yahoo-furima-jp', 'rakuma']:
        source = dict(sources[source_id])
        source['allowedHosts'] = source['allowedHosts'].split(',')
        source['allowedFormats'] = ['physical']
        request = dict(sourceId=source_id, source=source, query=args.query,
                       operation='active_discovery', format='physical',
                       maxDetailPages=args.details, maxPages=1, maxCandidates=100)
        if model:
            names = list(dict.fromkeys(value for key in ['canonical_public_name', 'original_name', 'english_name'] if (value := model.get(key))))
            request.update(humanModelKeywords=names, personKeywords=names)
        print('Starting:', source_id, flush=True)
        try:
            batch = collect(request)
            (output / f'{source_id}.capture.json').write_text(json.dumps(batch, ensure_ascii=False, indent=2), encoding='utf-8')
            for item in batch['items']:
                if item['priceMinor'] <= 0:
                    continue
                rows.append(dict(platform=source['name'], sourceId=source_id,
                                 externalId=item['externalId'], title=item['title'],
                                 url=item['url'], priceJPY=item['priceMinor'],
                                 currency=item['currency'], priceType=item['priceType'],
                                 publicationDate=item.get('releaseDate', ''),
                                 musecardsPersonId=model['id'] if model else None,
                                 coverImageUrl=item.get('imageUrl', ''),
                                 imageUrls=list(dict.fromkeys(([item['imageUrl']] if item.get('imageUrl') else []) + assets.get(item['url'], []))),
                                 observedAt=item['observedAt']))
            runs.append(dict(sourceId=source_id, diagnostics=batch['diagnostics']))
            print('Collected:', source_id, len(batch['items']), batch['diagnostics'], flush=True)
        except Exception as exc:
            runs.append(dict(sourceId=source_id, error=f'{type(exc).__name__}: {exc}'))
            print('Failed:', source_id, type(exc).__name__, str(exc), flush=True)
        result = dict(retrievedAt=iso_utc(), model=model, query=args.query, items=rows, runs=runs)
        (output / 'photobooks.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    columns = ['platform', 'sourceId', 'externalId', 'title', 'url', 'priceJPY', 'currency', 'priceType', 'publicationDate', 'musecardsPersonId', 'coverImageUrl', 'imageUrls', 'observedAt']
    with (output / 'photobooks.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    print('Saved:', len(rows), 'priced listings;', sum(bool(row['publicationDate']) for row in rows), 'publication dates', flush=True)


if __name__ == '__main__':
    main()
