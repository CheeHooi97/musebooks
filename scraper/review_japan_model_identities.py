"""Identify corroboration candidates while preserving distinct source editions."""
import json
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent / 'japan-models'
groups = defaultdict(list)
for path in ROOT.glob('*/listings.json'):
    capture = json.loads(path.read_text(encoding='utf-8'))
    for item in capture['items']:
        if item['format'] != 'digital':
            continue
        title = ''.join(unicodedata.normalize('NFKC', item['title']).split()).casefold()
        publisher = ''.join(unicodedata.normalize('NFKC', item.get('publisher', '')).split()).casefold()
        if not publisher:
            continue
        groups[(item['musecardsPersonId'], title, publisher, item['format'])].append(item)
review = []
for key, items in groups.items():
    unique = {(item['sourceId'], item['externalId']): item for item in items}
    if len({item['sourceId'] for item in unique.values()}) < 2:
        continue
    review.append(dict(musecardsPersonId=key[0], title=items[0]['title'], publisher=items[0]['publisher'],
        format=key[3], status='awaiting_corroboration',
        reason='Exact normalized title and publisher across stores; confirm product identity, content and edition evidence before merging.',
        members=[dict(sourceId=item['sourceId'], externalId=item['externalId'], url=item['url'],
            title=item['title'], releaseDate=item.get('releaseDate'), pageCount=item.get('pageCount'),
            isbn=item.get('isbn'), imageUrl=item.get('imageUrl')) for item in unique.values()]))
(ROOT / 'identity-review.json').write_text(json.dumps(review, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'{len(review)} potential shared-edition groups; no works or offers merged')
