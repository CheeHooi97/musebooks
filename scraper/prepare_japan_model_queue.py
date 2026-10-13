"""Prepare resumable per-person inputs from a read-only MuseCards export."""
import json
from pathlib import Path

root = Path(__file__).resolve().parent / 'japan-models'
snapshot = json.loads((root / 'musecards-models.json').read_text(encoding='utf-8-sig'))
queue = []
alias_groups = []
queue_path = root / 'queue.json'
previous = {row['musecardsPersonId']: row for row in json.loads(queue_path.read_text(encoding='utf-8'))} if queue_path.exists() else {}
for person in snapshot['models']:
    person = dict(person)
    person['aliases'] = list(dict.fromkeys(a['name'] for a in snapshot['careerNames']
        if a['person_id'] == person['id'] and a.get('name')))
    alias_groups.append(list(dict.fromkeys(name for name in [person.get('canonical_public_name'),
        person.get('original_name'), person.get('english_name'), *person['aliases']] if name)))
    directory = root / str(person['id'])
    directory.mkdir(exist_ok=True)
    (directory / 'model.json').write_text(json.dumps({'models': [person]}, ensure_ascii=False, indent=2), encoding='utf-8')
    row = {**previous.get(person['id'], {}), 'musecardsPersonId': person['id'], 'name': person['canonical_public_name'],
        'englishName': person.get('english_name'), 'japanReleaseCount': person['japan_release_count'],
        'directory': str(directory.relative_to(root.parent.parent)).replace('\\', '/'),
        'status': 'reuse_fumina_capture' if person['id'] == 6 else previous.get(person['id'], {}).get('status', 'pending'),
        'sources': previous.get(person['id'], {}).get('sources', {s: 'pending' for s in ['yahoo-auctions-jp', 'yahoo-furima-jp', 'rakuma', 'grajapa-jp', 'rakuten-kobo-jp']})}
    queue.append(row)
temporary = queue_path.with_suffix('.new.json')
temporary.write_text(json.dumps(queue, ensure_ascii=False, indent=2), encoding='utf-8')
temporary.replace(queue_path)
alias_path = root.parent.parent / 'frontend/src/lib/model-search-aliases.js'
alias_path.write_text('// Generated from the read-only MuseCards model export.\nexport default ' +
    json.dumps(alias_groups, ensure_ascii=False, indent=2) + ';\n', encoding='utf-8')
print(f'Prepared {len(queue)} model inputs; Fumina capture preserved')
