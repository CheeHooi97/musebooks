"""Apply current photobook scope checks to captured Japan import manifests."""
import json
import sys
from pathlib import Path
from photobook_worker import photobook_title_exclusion

for filename in sys.argv[1:]:
    path = Path(filename)
    records = json.loads(path.read_text(encoding='utf-8'))
    rejected = []
    count = 0
    for record in records:
        accepted = []
        for item in record['batch']['items']:
            reason = photobook_title_exclusion(item['title'])
            if item.get('format') != 'physical':
                reason = reason or 'nonphysical_marketplace'
            if not item.get('priceMinor') or item.get('currency') != 'JPY':
                reason = reason or 'unverified_jpy_price'
            if reason:
                rejected.append(dict(externalId=item['externalId'], reason=reason))
            else:
                accepted.append(item)
        record['batch']['items'] = accepted
        identities = {item['externalId'] for item in accepted}
        record['media'] = [media for media in record['media'] if media['externalId'] in identities]
        count += len(accepted)
    path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')
    review_path = path.with_suffix('.review.json')
    previous = json.loads(review_path.read_text(encoding='utf-8')) if review_path.exists() else []
    review_path.write_text(json.dumps(previous + rejected, ensure_ascii=False, indent=2), encoding='utf-8')
    print(path.name, 'accepted:', count, 'excluded:', len(rejected))
