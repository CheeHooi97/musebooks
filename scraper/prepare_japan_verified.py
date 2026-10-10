"""Mirror reviewed publisher covers before importing canonical Japan editions."""
import json
from pathlib import Path
from r2_covers import R2Covers, load_env

load_env('backend/.env')
store = R2Covers()
records = json.loads(Path('scraper/japan-publisher-verified.json').read_text(encoding='utf-8'))
for record in records:
    image = store.upload(record['edition']['originalCoverUrl'])
    record['work']['coverUrl'] = image['url']
    record['edition']['coverUrl'] = image['url']
    record['edition']['coverObjectKey'] = image['key']
Path('scraper/japan-verified-import.json').write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')
print('Prepared verified Japan editions:', len(records))
