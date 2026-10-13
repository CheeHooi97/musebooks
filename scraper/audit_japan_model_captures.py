"""Read-only quality and identity audit of the current local import snapshot."""
import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from prepare_japan_work_repair import build

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'scraper/japan-models'


def audit():
    exclusions = json.loads((OUT / 'excluded-listings.json').read_text(encoding='utf-8'))
    excluded = {(item['sourceId'], item['externalId']) for item in exclusions}
    records = [record for path in OUT.glob('*/home-import.json')
        for record in json.loads(path.read_text(encoding='utf-8'))]
    offers = defaultdict(list)
    issues = []
    for record in records:
        item = record['batch']['items'][0]
        key = (record['source']['id'], item['externalId'])
        offers[key].append(record)
        def issue(reason):
            issues.append(dict(sourceId=key[0], externalId=key[1], issue=reason))
        if record['batch']['sourceId'] != key[0]:
            issue('batch_source_mismatch')
        if key not in excluded and (type(item.get('priceMinor')) is not int or item['priceMinor'] <= 0):
            issue('missing_or_nonpositive_paid_price')
        if item.get('currency') != 'JPY':
            issue('unexpected_japan_currency')
        if not item.get('imageUrl'):
            issue('missing_cover')
        if item.get('format') == 'digital' and item.get('digitalAccess') != 'authorized_store':
            issue('unverified_digital_store')
        edition, work = record['edition'], record['work']
        if edition and (edition['workId'] != work['id'] or item.get('editionId') != edition['id'] or edition['format'] != item['format']):
            issue('catalog_identity_mismatch')
        if any(media['sourceUrl'] != item['url'] for media in record.get('media', [])):
            issue('listing_media_source_mismatch')
        if any(media['sourceUrl'] != edition['metadataSourceUrl'] for media in record.get('publisherMedia', [])):
            issue('publisher_media_source_mismatch')
    for key, shared in offers.items():
        observations = {(r['batch']['items'][0]['format'], r['batch']['items'][0].get('priceMinor'),
            r['batch']['items'][0].get('currency'), r['batch']['items'][0].get('priceType')) for r in shared}
        if len(observations) > 1:
            issues.append(dict(sourceId=key[0], externalId=key[1], issue='shared_offer_values_differ'))
    plan = build()
    mapping = defaultdict(set)
    for group in plan['groups']:
        for member in group['members']:
            mapping[member['editionId']].add(group['workId'])
    conflicts = {key: sorted(value) for key, value in mapping.items() if len(value) > 1}
    return dict(checkedAt=datetime.now(timezone.utc).isoformat(),
        mode='local_snapshot_no_database_changes', modelOfferRecords=len(records),
        uniqueOffers=len(offers), excludedOffers=sum(key in excluded for key in offers),
        proposedGroups=len(plan['groups']), issues=issues, editionIdentityConflicts=conflicts)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='scraper/japan-models/local-quality-audit-20261013.json')
    args = parser.parse_args()
    output = (ROOT / args.output).resolve()
    if not output.is_relative_to(ROOT):
        parser.error('Audit output must stay inside the workspace')
    report = audit()
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Audited {report['modelOfferRecords']} records / {report['uniqueOffers']} offers; "
        f"{report['proposedGroups']} proposed publication groups; issues={len(report['issues'])}; "
        f"identity conflicts={len(report['editionIdentityConflicts'])}; reviewed exclusions={report['excludedOffers']}")
    if report['issues'] or report['editionIdentityConflicts']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
