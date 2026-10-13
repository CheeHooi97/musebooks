"""Apply reviewed generated records with durable content-hash checkpoints."""
import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from run_japan_model_queue import source_lock
from capture_checkpoint import save_json

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'scraper/japan-models'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--importer', default='.tmp/japan-catalog-import-v2.exe')
    parser.add_argument('--repairer', default='.tmp/japan-work-repair.exe')
    parser.add_argument('--verifier', default='.tmp/verify-japan-import.exe')
    parser.add_argument('--page-ssh-host')
    parser.add_argument('--page-ssh-key', type=Path)
    args = parser.parse_args()
    if bool(args.page_ssh_host) != bool(args.page_ssh_key):
        parser.error('Page-publication SSH host and key must be supplied together')
    with source_lock(OUT / 'import.lock'):
        import_captures(args)


def import_captures(args):
    if args.apply:
        subprocess.run([str(ROOT / args.repairer), '-manifest', str(ROOT / 'scraper/japan-work-identities.json'),
            '-bindings-output', str(OUT / 'catalog-work-bindings.json')], cwd=ROOT / 'backend', check=True)
    subprocess.run([sys.executable, '-X', 'utf8', str(ROOT / 'scraper/summarize_japan_models.py')], cwd=ROOT, check=True)
    # Extend exact model/title/publisher identities before importing new offers.
    # Preserve prior canonical IDs so later store discoveries cannot split works.
    subprocess.run([sys.executable, '-X', 'utf8', str(ROOT / 'scraper/prepare_japan_work_repair.py')], cwd=ROOT, check=True)
    subprocess.run([sys.executable, '-X', 'utf8', str(ROOT / 'scraper/summarize_japan_models.py')], cwd=ROOT, check=True)
    checkpoint_path = OUT / 'import-checkpoint.json'
    subprocess.run([sys.executable, '-X', 'utf8', str(ROOT / 'scraper/audit_japan_model_captures.py'),
        '--output', 'scraper/japan-models/automatic-import-quality-audit.json'], cwd=ROOT, check=True)
    checkpoint = json.loads(checkpoint_path.read_text(encoding='utf-8')) if checkpoint_path.exists() else {'records': {}}
    pending, keys = [], []
    for path in sorted(OUT.glob('*/home-import.json')):
        for record in json.loads(path.read_text(encoding='utf-8')):
            item = record['batch']['items'][0]
            key = path.parent.name + ':' + record['source']['id'] + ':' + item['externalId']
            digest = hashlib.sha256(json.dumps(record, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
            if checkpoint['records'].get(key) != digest:
                pending.append(record)
                keys.append((key, digest))
    manifest = OUT / 'pending-import.json'
    manifest.write_text(json.dumps(pending, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Prepared {len(pending)} new or changed model-offer records', flush=True)
    if not args.apply:
        return
    repair_plan = ROOT / 'scraper/japan-work-identities.json'
    if json.loads(repair_plan.read_text(encoding='utf-8'))['groups']:
        repair = [str(ROOT / args.repairer), '-manifest', str(repair_plan)]
        subprocess.run(repair, cwd=ROOT / 'backend', check=True)
        subprocess.run([*repair, '-apply'], cwd=ROOT / 'backend', check=True)
    if pending:
        subprocess.run([str(ROOT / args.importer), '-manifest', str(manifest), '-apply'], cwd=ROOT / 'backend', check=True)
        checkpoint['records'].update(keys)
        checkpoint['appliedAt'] = datetime.now(timezone.utc).isoformat()
        save_json(checkpoint_path, checkpoint)
        print(f'Committed checkpoint for {len(pending)} records', flush=True)
    exclusions = OUT / 'excluded-listings.json'
    if exclusions.exists() and json.loads(exclusions.read_text(encoding='utf-8')):
        subprocess.run([str(ROOT / args.importer), '-exclude-listings', str(exclusions)], cwd=ROOT / 'backend', check=True)
        print('Reapplied reviewed listing exclusions; source captures and observations are retained', flush=True)
    verified_records = []
    for path in sorted(OUT.glob('*/home-import.json')):
        for record in json.loads(path.read_text(encoding='utf-8')):
            item = record['batch']['items'][0]
            key = path.parent.name + ':' + record['source']['id'] + ':' + item['externalId']
            digest = hashlib.sha256(json.dumps(record, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
            if checkpoint['records'].get(key) == digest:
                verified_records.append(record)
    if len(verified_records) != len(checkpoint['records']):
        raise RuntimeError('Applied record snapshot incomplete; inspect checkpoint before cumulative verification')
    (OUT / 'verification-manifest.json').write_text(json.dumps(verified_records, ensure_ascii=False, indent=2), encoding='utf-8')
    if verified_records:
        subprocess.run([str(ROOT / args.verifier)], cwd=ROOT / 'backend', check=True)
        if getattr(args, 'page_ssh_host', None):
            from publish_japan_import_pages import publish
            publish(args.page_ssh_host, args.page_ssh_key, apply=True)


if __name__ == '__main__':
    main()
