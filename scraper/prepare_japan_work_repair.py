"""Build exact cross-store work groups, preserving source editions."""
import json
import unicodedata
from collections import defaultdict
from pathlib import Path
from prepare_model_home_import import identity
ROOT = Path(__file__).parent

def normalized(value):
    return ''.join(unicodedata.normalize('NFKC', value).split()).casefold()


def add_reviewed_cross_formats(groups, identities):
    path = ROOT / 'japan-cross-format-identities.json'
    if not path.exists():
        return
    edition_groups = {member['editionId']: group['workId'] for group in groups for member in group['members']}
    for pair in json.loads(path.read_text(encoding='utf-8'))['pairs']:
        model_id = str(pair['musecardsPersonId'])
        capture = ROOT / 'japan-models' / model_id / 'home-import.json'
        by_edition = {record['edition']['id']: record for record in json.loads(capture.read_text(encoding='utf-8')) if record.get('edition')}
        physical, digital = (by_edition[key] for key in (pair['physicalEditionId'], pair['digitalEditionId']))
        for record, fmt, source in ((physical, 'physical', pair['publisherUrl']), (digital, 'digital', pair['storeUrl'])):
            edition = record['edition']
            if (edition['format'] != fmt or edition['metadataSourceUrl'] != source or
                    normalized(edition['editionLabel']) != normalized(pair['title']) or
                    normalized(edition['publisher']) != normalized(pair['publisher'])):
                raise ValueError('Reviewed physical/digital evidence changed; review before merging')
        if physical['edition']['isbn'] != pair['isbn']:
            raise ValueError('Reviewed print ISBN changed; review before merging')
        canonical = pair['physicalWorkId']
        members = []
        for record, work_id in ((physical, pair['physicalWorkId']), (digital, pair['digitalWorkId'])):
            edition = record['edition']
            if edition_groups.get(edition['id'], canonical) != canonical:
                raise ValueError('Physical/digital pairing conflicts with a reviewed publication identity')
            edition_groups[edition['id']] = canonical
            members.append(dict(workId=work_id, editionId=edition['id'], title=edition['editionLabel'],
                publisher=edition['publisher'], format=edition['format']))
            identities.setdefault(model_id, {})[edition['editionLabel'] + '\0' + edition['publisher']] = dict(id=canonical, title=pair['title'])
        groups.append(dict(workId=canonical, title=pair['title'], personSlug=physical['featuredPerson']['slug'],
            members=members, matchEvidence=dict(basis='reviewed_publisher_and_store_format_pair',
                isbn=pair['isbn'], publisherUrl=pair['publisherUrl'], storeUrl=pair['storeUrl'], evidence=pair.get('evidence', []))))

def build():
    groups, identities = [], {}
    saved_path = ROOT / 'japan-work-identities.json'
    saved = json.loads(saved_path.read_text(encoding='utf-8')) if saved_path.exists() else {}
    checkpoint_path = ROOT / 'japan-models/import-checkpoint.json'
    imported = json.loads(checkpoint_path.read_text(encoding='utf-8')).get('records', {}) if checkpoint_path.exists() else {}
    bindings_path = ROOT / 'japan-models/catalog-work-bindings.json'
    bindings = json.loads(bindings_path.read_text(encoding='utf-8')) if bindings_path.exists() else None
    for path in sorted((ROOT / 'japan-models').glob('*/home-import.json')):
        person = json.loads(path.with_name('listings.json').read_text(encoding='utf-8'))['model']
        if person['id'] == 6:
            continue
        candidates = defaultdict(dict)
        existing_works = {}
        for record in json.loads(path.read_text(encoding='utf-8')):
            work, edition = record['work'], record['edition']
            if not work or edition['format'] != 'digital' or not edition.get('publisher'):
                continue
            title = edition['editionLabel']
            item = record['batch']['items'][0]
            if f"{person['id']}:{record['source']['id']}:{item['externalId']}" in imported:
                existing_works[edition['id']] = work
            record['work'] = dict(work, id=identity('work-jp-', record['source']['id'] + ':' + item['externalId']), originalTitle=title)
            if 'オールアザー' in title:
                continue
            candidates[(normalized(title), normalized(edition['publisher']))][edition['id']] = record
        mapped = dict(saved.get('identities', {}).get(str(person['id']), {}))
        for records in candidates.values():
            records = sorted(records.values(), key=lambda r: r['work']['id'])
            if len({r['source']['id'] for r in records}) < 2 or len({r['work']['id'] for r in records}) < 2:
                continue
            previous = [mapped.get(r['edition']['editionLabel'] + '\0' + r['edition']['publisher']) for r in records]
            previous = [p for p in previous if p]
            if len({p['id'] for p in previous}) > 1:
                raise ValueError('Conflicting saved work identities; review before merging')
            existing = [existing_works[r['edition']['id']] for r in records if r['edition']['id'] in existing_works]
            canonical = dict(id=previous[0]['id'], originalTitle=previous[0]['title']) if previous else (existing[0] if existing else records[0]['work'])
            if bindings and (canonical['id'] not in bindings['works'] or
                    bindings['works'][canonical['id']]['status'] == 'superseded'):
                actual_ids = list(dict.fromkeys(bindings['editions'][r['edition']['id']]
                    for r in records if r['edition']['id'] in bindings['editions']))
                if actual_ids:
                    actual = bindings['works'][actual_ids[0]]
                    canonical = dict(id=actual_ids[0], originalTitle=actual['title'])
            members = []
            for record in records:
                work, edition = record['work'], record['edition']
                members.append(dict(workId=work['id'], editionId=edition['id'], title=work['originalTitle'], publisher=edition['publisher'], format=edition['format']))
                mapped[edition['editionLabel'] + '\0' + edition['publisher']] = dict(id=canonical['id'], title=canonical['originalTitle'])
            groups.append(dict(workId=canonical['id'], title=canonical['originalTitle'],
                personSlug=records[0].get('featuredPerson', {}).get('slug', ''), members=members))
        identities[str(person['id'])] = mapped
    add_reviewed_cross_formats(groups, identities)
    return dict(model='Japan models', groups=groups, identities=identities)

if __name__ == '__main__':
    plan = build()
    temporary = ROOT / 'japan-work-identities.new.json'
    temporary.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding='utf-8')
    temporary.replace(ROOT / 'japan-work-identities.json')
    print(f"Prepared {len(plan['groups'])} cross-store work groups")
