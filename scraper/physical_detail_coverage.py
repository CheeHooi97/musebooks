"""Retain qualifying failed details independently of search pagination."""
import json
from physical_search_relevance import has_photobook_title_signal


def recover_pending_details(state, output, names, worker):
    pending = state.setdefault('pendingDetails', {})
    if state.get('detailCoverageVersion') == 1:
        return
    for key, run in state.get('runs', {}).items():
        for reference in run.get('batches', []):
            if not reference.get('diagnostics', {}).get('detailErrors'):
                continue
            path = output / reference['file']
            if not path.exists():
                continue
            batch = json.loads(path.read_text(encoding='utf-8'))
            for candidate in batch.get('candidateEvidence', []):
                title, url = candidate.get('title', ''), candidate.get('url', '')
                if (not url or url in state.get('details', {}) or
                    not has_photobook_title_signal(title) or worker.photobook_title_exclusion(title) or
                    not worker.marketplace_subject_matches({'humanModelKeywords': names}, title)):
                    continue
                record = pending.setdefault(url, dict(sourceId=run['sourceId'], title=title,
                    runKeys=[], error='Qualifying product detail was not captured; public inspection remains pending'))
                if key not in record['runKeys']:
                    record['runKeys'].append(key)
    state['detailCoverageVersion'] = 1
    update_detail_coverage(state)


def update_detail_coverage(state):
    owners = {key for value in state.get('pendingDetails', {}).values() for key in value.get('runKeys', [])}
    if owners and state.get('status') == 'finished':
        state['status'] = 'incomplete'
    for key, run in state.get('runs', {}).items():
        if key in owners and run.get('status') in ('public_search_exhausted', 'query_relevance_exhausted'):
            run['paginationStatus'] = run['status']
            run['status'] = 'detail_failures'
        elif key not in owners and run.get('status') == 'detail_failures':
            run['status'] = run.pop('paginationStatus', 'running')
