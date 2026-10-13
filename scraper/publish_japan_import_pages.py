"""Publish routes only from the cumulatively verified Japan import snapshot."""
import argparse
import json
import subprocess
from pathlib import Path
from capture_checkpoint import save_json
from run_japan_model_queue import source_lock

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'scraper/japan-models'


def publish(host, key, *, apply=False, refresh_all=False):
    verification = json.loads((OUT / 'import-verification.json').read_text(encoding='utf-8'))
    result = verification['result']
    records = json.loads((OUT / 'verification-manifest.json').read_text(encoding='utf-8'))
    if result['expected'] != result['present'] or result['expected'] != len(records):
        raise RuntimeError('Publication requires a complete verified import snapshot')
    for field in ('priceMismatches', 'formatMismatches', 'missingMedia',
                  'missingPublisherMedia', 'workMismatches', 'exclusionMismatches'):
        if result[field] != 0:
            raise RuntimeError('Publication requires zero database verification mismatches')
    slugs = sorted({record['work']['slug'] for record in records if record.get('work')})
    pending_path = OUT / 'page-publication-pending.json'
    pending = json.loads(pending_path.read_text(encoding='utf-8')) if pending_path.exists() else {}
    changed = json.loads((OUT / 'pending-import.json').read_text(encoding='utf-8'))
    refresh = {record['work']['slug'] for record in changed if record.get('work')}
    refresh.update(pending.get('refreshSlugs', []))
    # Removed/superseded work identities are not publication targets.
    refresh.intersection_update(slugs)
    payload = dict(schemaVersion=1, databaseCheckedAt=verification['checkedAt'],
        bookSlugs=slugs, refreshSlugs=sorted(refresh),
        refreshAll=refresh_all or pending.get('refreshAll', False))
    manifest = OUT / 'page-publication-manifest.json'
    save_json(manifest, payload)
    if apply:
        save_json(pending_path, payload)
    subprocess.run(['scp', '-i', str(key), '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes',
        str(manifest), host + ':/var/www/musebooks/import-pages-input.json'], check=True)
    command = ('flock -n /var/www/musebooks/.japan-page-publish.lock '
        'node /opt/musebooks/japan-import-pages/frontend/scripts/publish-import-pages.mjs '
        '--output-dir /var/www/musebooks/current '
        '--manifest /var/www/musebooks/import-pages-input.json '
        '--report /var/www/musebooks/import-pages-report.json')
    if apply:
        command += ' --apply'
    subprocess.run(['ssh', '-i', str(key), '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes',
        host, command], check=True)
    report = OUT / 'page-publication-verification.json'
    subprocess.run(['scp', '-i', str(key), '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes',
        host + ':/var/www/musebooks/import-pages-report.json', str(report)], check=True)
    published = json.loads(report.read_text(encoding='utf-8'))
    if apply:
        if published['mode'] != 'applied_verified_catalog_pages' or published['requestedBooks'] != len(slugs):
            raise RuntimeError('Unexpected publication readback; retain pending routes for retry')
        save_json(pending_path, dict(refreshSlugs=[], refreshAll=False,
            publishedAt=published['checkedAt'], release=published['outputDir']))
    print('Book-route publication:', published['mode'], published['changedPages'],
        'changed pages;', published['newPages'], 'new routes', flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ssh-host', required=True)
    parser.add_argument('--ssh-key', required=True, type=Path)
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--refresh-all', action='store_true')
    args = parser.parse_args()
    with source_lock(OUT / 'import.lock'):
        publish(args.ssh_host, args.ssh_key, apply=args.apply, refresh_all=args.refresh_all)


if __name__ == '__main__':
    main()
