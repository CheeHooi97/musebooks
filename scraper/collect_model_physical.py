"""Resume complete model-scoped marketplace searches without importing data."""
import argparse
import hashlib
import json
import time
from pathlib import Path

import photobook_worker as worker
from japan_model_search_names import physical_model_search_names
from source_navigation import SourceNavigationLimiters
from capture_checkpoint import save_json as write
from physical_detail_coverage import recover_pending_details, update_detail_coverage
from physical_source_blocks import (
    block_is_active,
    load_source_blocks,
    record_source_block,
    save_source_blocks,
)
from physical_search_relevance import (
    IRRELEVANT_PAGE_LIMIT,
    has_photobook_title_signal,
    matching_candidate_count,
    next_irrelevant_page_count,
    next_batch_search_status,
    resume_pagination_stalled_run,
    trailing_irrelevant_page_count,
)

TRANSIENT_PAGE_RETRIES = 2
TRANSIENT_RETRY_DELAY_SECONDS = 10


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    parser.add_argument('--model-file', default='scraper/fumina-suzuki-model.json')
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    output = (root / args.output).resolve()
    if not output.is_relative_to(root):
        parser.error('Output must stay inside workspace')
    output.mkdir(parents=True, exist_ok=True)
    model = json.loads((root / args.model_file).read_text(encoding='utf-8'))['models'][0]
    names = physical_model_search_names(model)
    queries = list(dict.fromkeys([names[0] + ' 写真集', *names]))
    sources = {x['source']['id']: x['source'] for x in json.loads((root / 'scraper/japan-marketplace-import-20261010.json').read_text(encoding='utf-8-sig'))}
    state_path = output / 'physical-state.json'
    state = json.loads(state_path.read_text(encoding='utf-8')) if state_path.exists() else dict(items={}, runs={}, details={}, status='running')
    source_blocks = load_source_blocks()
    state['status'] = 'running'
    state['collectorStartedAt'] = worker.iso_utc()
    for run in state.get('runs', {}).values():
        if run.get('query') not in queries and run.get('status') not in (
                'public_search_exhausted', 'query_relevance_exhausted',
                'ambiguous_alias_skipped'):
            run.update(status='ambiguous_alias_skipped',
                stopReason='Skipped because this short alias is not a specific model search name.')
        elif run.get('query') in queries and run.get('status') == 'running':
            # Recount the saved trailing pages against title-only, specific
            # model names so older seller-text matches cannot keep a broad query alive.
            run.pop('consecutiveIrrelevantPages', None)
        elif run.get('query') in queries:
            resume_pagination_stalled_run(run)
    removed_items = []
    request = {'humanModelKeywords': names}
    for item_key, item in list(state.get('items', {}).items()):
        if not worker.marketplace_subject_matches(request, item.get('title', '')):
            removed_items.append(item.get('title', item_key))
            del state['items'][item_key]
    if removed_items:
        state['removedFalseModelAssociations'] = state.get('removedFalseModelAssociations', []) + removed_items
        print('Removed unrelated alias matches:', len(removed_items), flush=True)
    recover_pending_details(state, output, names, worker)
    write(state_path, state)
    original_snapshot = worker.detail_snapshot
    original_candidates = worker.collect_anchor_candidates
    titles = {}
    latest_candidates = []
    def candidates(*values, **options):
        result = original_candidates(*values, **options)
        latest_candidates[:] = result
        titles.update({x['url']: x.get('title', '') for x in result})
        return result
    def snapshot(*values, **options):
        url = values[1]
        if url in state['details']:
            return state['details'][url]
        title = titles.get(url, '')
        if not has_photobook_title_signal(title):
            raise worker.CandidateSkippedBeforeDetail('No photobook evidence in candidate title')
        # Keep the unfiltered card list for correct pagination. Obvious cards,
        # discs, clippings, and other-person offers don't need detail requests.
        if worker.photobook_title_exclusion(title) or not worker.marketplace_subject_matches({'humanModelKeywords': names}, title):
            raise worker.CandidateSkippedBeforeDetail('Candidate excluded before navigation')
        print('Inspecting:', url, flush=True)
        try:
            detail = original_snapshot(*values, **options)
        except worker.DetailSnapshotError as exc:
            pending = state['pendingDetails'].setdefault(url, dict(sourceId=source_id,
                title=title, runKeys=[]))
            if key not in pending['runKeys']:
                pending['runKeys'].append(key)
            pending['error'] = f'{type(exc).__name__}: {exc}'
            write(state_path, state)
            raise
        state['details'][url] = detail
        state['pendingDetails'].pop(url, None)
        write(state_path, state)
        return detail
    worker.collect_anchor_candidates = candidates
    worker.detail_snapshot = snapshot
    # Page-sized jobs must not reset the platform's navigation clock.
    worker.NavigationRateLimiter = SourceNavigationLimiters(worker.NavigationRateLimiter)
    for source_id in ['yahoo-auctions-jp', 'yahoo-furima-jp', 'rakuma']:
        block = source_blocks.get(source_id)
        if block and not block_is_active(block):
            source_blocks.pop(source_id, None)
            save_source_blocks(source_blocks)
        source = dict(sources[source_id])
        source.update(allowedHosts=source['allowedHosts'].split(','), allowedFormats=['physical'])
        for query in queries:
            key = source_id + ':' + query
            run = state['runs'].setdefault(key, dict(sourceId=source_id, query=query, cursor='', batches=[], status='running'))
            block = source_blocks.get(source_id)
            if block_is_active(block):
                if run.get('status') not in ('public_search_exhausted', 'query_relevance_exhausted'):
                    if run.get('status') == 'source_failed':
                        run.setdefault('previousErrors', []).append(run.pop('error', ''))
                    run.update(status='source_blocked', sourceBlockReason=block.get('reason', ''),
                        retryAfter=block.get('retryAfter', ''),
                        stopReason='Paused after the marketplace explicitly restricted access; no further requests will be sent during the cooldown.')
                    write(state_path, state)
                continue
            if run.get('status') == 'source_blocked':
                run['status'] = 'running'
                run.pop('sourceBlockReason', None)
                run.pop('retryAfter', None)
            if run['status'] == 'source_failed':
                run.setdefault('previousErrors', []).append(run.pop('error', ''))
                run['status'] = 'running'
            count_matches = lambda candidates: matching_candidate_count(candidates, names,
                worker.marketplace_subject_matches, worker.photobook_title_exclusion,
                lambda candidate: worker.marketplace_subject_matches(
                    {'humanModelKeywords': names}, candidate.get('title') or candidate.get('text') or ''))
            irrelevant_pages = run.get('consecutiveIrrelevantPages')
            if irrelevant_pages is None:
                irrelevant_pages = trailing_irrelevant_page_count(run, output, count_matches)
            if run['status'] == 'running' and irrelevant_pages >= IRRELEVANT_PAGE_LIMIT:
                run.update(status='query_relevance_exhausted', consecutiveIrrelevantPages=irrelevant_pages,
                    stopReason=f'Stopped after {irrelevant_pages} consecutive pages without a photobook-title card naming this model; unrelated fallback results were not paginated further.')
                print('Stopped low-relevance pagination:', source_id, query, 'unrelated pages:', irrelevant_pages, flush=True)
                write(state_path, state)
            transient_failures = 0
            while run['status'] == 'running':
                cursor = run['cursor']
                print('Search:', source_id, query, 'cursor:', cursor, flush=True)
                try:
                    latest_candidates.clear()
                    batch = worker.collect(dict(sourceId=source_id, source=source, query=query,
                        operation='active_discovery', format='physical', humanModelKeywords=names,
                        personKeywords=names, pageCursor=cursor, maxPages=1, maxDetailPages=200,
                        maxCandidates=200, maxItems=200))
                    transient_failures = 0
                    batch_id = hashlib.sha256((key + ':' + cursor).encode()).hexdigest()[:16]
                    # A detail-budget cursor can resume the same search page at
                    # a later candidate offset; that is progress, not a loop.
                    try:
                        offset = int(json.loads(cursor).get('offset', 0)) if cursor.startswith('{') else 0
                    except (ValueError, TypeError, AttributeError):
                        offset = 0
                    fingerprint = hashlib.sha256(json.dumps(dict(urls=[c['url'] for c in latest_candidates], offset=offset)).encode()).hexdigest()
                    relevant_count = count_matches(latest_candidates)
                    batch['diagnostics']['matchingModelCandidates'] = relevant_count
                    batch['candidateEvidence'] = latest_candidates.copy()
                    write(output / f'physical-{batch_id}.json', batch)
                    for item in batch['items']:
                        if item['priceMinor'] > 0:
                            state['items'][source_id + ':' + item['externalId']] = dict(item, sourceId=source_id, platform=source['name'], musecardsPersonId=model['id'])
                    repeated = any(b.get('candidateFingerprint') == fingerprint for b in run['batches'])
                    run['batches'].append(dict(file=f'physical-{batch_id}.json', diagnostics=batch['diagnostics'], hasMore=batch['hasMore'], nextCursor=batch['nextCursor'], candidateFingerprint=fingerprint))
                    irrelevant_pages = next_irrelevant_page_count(irrelevant_pages, relevant_count)
                    run['consecutiveIrrelevantPages'] = irrelevant_pages
                    cursor_repeats = (not batch['nextCursor'] or batch['nextCursor'] == cursor
                        or any(b['nextCursor'] == batch['nextCursor'] for b in run['batches'][:-1]))
                    run['status'] = next_batch_search_status(
                        has_more=batch['hasMore'], repeated=repeated,
                        cursor_repeats=cursor_repeats, irrelevant_pages=irrelevant_pages)
                    if run['status'] == 'query_relevance_exhausted':
                        run.update(stopReason=f'Stopped after {irrelevant_pages} consecutive pages without a photobook-title card naming this model; unrelated fallback results were not paginated further.')
                    elif run['status'] == 'pagination_stalled':
                        run.update(stopReason='The source repeated or returned a non-advancing page while matching model photobook candidates remained.')
                    elif run['status'] == 'running':
                        run['cursor'] = batch['nextCursor']
                    print('Batch:', source_id, len(batch['items']), 'unique total:', len(state['items']), run['status'], flush=True)
                except Exception as exc:
                    evidence = getattr(exc, 'evidence', None)
                    evidence_file = ''
                    if evidence:
                        files = run.setdefault('errorEvidenceFiles', [])
                        failure_id = hashlib.sha256((key + ':' + cursor).encode()).hexdigest()[:16]
                        filename = f'physical-failure-{failure_id}-{len(files) + 1:03d}.json'
                        write(output / filename, dict(evidence, query=query, cursor=cursor,
                            error=f'{type(exc).__name__}: {exc}'))
                        files.append(filename)
                        evidence_file = filename
                    if isinstance(exc, worker.SourceBlockedError):
                        block = record_source_block(source_id, str(exc), details=dict(
                            musecardsPersonId=model.get('id'), query=query,
                            evidenceFile=evidence_file))
                        source_blocks[source_id] = block
                        run.update(status='source_blocked', sourceBlockReason=block['reason'],
                            retryAfter=block['retryAfter'], stopReason=
                            'Marketplace access was explicitly restricted; paused this source for 24 hours.')
                        for pending in state.get('pendingDetails', {}).values():
                            if pending.get('sourceId') == source_id:
                                pending.update(status='source_blocked', retryAfter=block['retryAfter'],
                                    error='Paused because the marketplace explicitly restricted access.')
                        print('Pausing marketplace source after explicit access restriction:',
                            source_id, 'retry after:', block['retryAfter'], flush=True)
                    else:
                        retryable = isinstance(exc, worker.RenderedPageError) or type(exc).__name__ == 'TimeoutError'
                        if retryable:
                            transient_failures += 1
                            if transient_failures <= TRANSIENT_PAGE_RETRIES:
                                run.setdefault('transientRetryErrors', []).append(f'{type(exc).__name__}: {exc}')
                                print('Retrying rendered marketplace page:', source_id, query,
                                    'attempt:', transient_failures, 'error:', str(exc), flush=True)
                                write(state_path, state)
                                time.sleep(TRANSIENT_RETRY_DELAY_SECONDS * transient_failures)
                                continue
                        run.update(status='source_failed', error=f'{type(exc).__name__}: {exc}')
                        print('Source failed:', source_id, str(exc), flush=True)
                update_detail_coverage(state)
                write(state_path, state)
    for url, pending in list(state['pendingDetails'].items()):
        source_id = pending['sourceId']
        block = source_blocks.get(source_id)
        if block_is_active(block):
            pending.update(status='source_blocked', retryAfter=block.get('retryAfter', ''),
                error='Paused because the marketplace explicitly restricted access.')
            write(state_path, state)
            continue
        pending.pop('status', None)
        pending.pop('retryAfter', None)
        key = pending['runKeys'][0]
        source = dict(sources[source_id])
        source.update(allowedHosts=source['allowedHosts'].split(','), allowedFormats=['physical'])
        titles[url] = pending['title']
        print('Retrying pending physical detail:', url, flush=True)
        try:
            batch = worker.collect(dict(sourceId=source_id, source=source, url=url,
                operation='listing_detail', format='physical', humanModelKeywords=names,
                personKeywords=names, maxPages=1, maxDetailPages=1, maxCandidates=1, maxItems=1))
            filename = 'physical-detail-' + hashlib.sha256(url.encode()).hexdigest()[:16] + '.json'
            write(output / filename, batch)
            for item in batch['items']:
                if item['priceMinor'] > 0:
                    state['items'][source_id + ':' + item['externalId']] = dict(item,
                        sourceId=source_id, platform=source['name'], musecardsPersonId=model['id'])
        except Exception as exc:
            state['pendingDetails'].setdefault(url, pending)['error'] = f'{type(exc).__name__}: {exc}'
            print('Physical detail remains pending:', url, type(exc).__name__, flush=True)
        update_detail_coverage(state)
        write(state_path, state)
    update_detail_coverage(state)
    expected_runs = [state['runs'].get(source_id + ':' + query, {})
        for source_id in ['yahoo-auctions-jp', 'yahoo-furima-jp', 'rakuma']
        for query in queries]
    terminal_statuses = ('public_search_exhausted', 'query_relevance_exhausted', 'source_blocked')
    all_searches_accounted_for = all(r.get('status') in terminal_statuses for r in expected_runs)
    pending_details_accounted_for = all(
        pending.get('status') == 'source_blocked' and block_is_active(source_blocks.get(pending.get('sourceId')))
        for pending in state['pendingDetails'].values())
    if all_searches_accounted_for and (not state['pendingDetails'] or pending_details_accounted_for):
        state['status'] = 'finished_with_source_blocks' if any(
            run.get('status') == 'source_blocked' for run in expected_runs) else 'finished'
    else:
        state['status'] = 'incomplete'
    write(state_path, state)
    write(output / 'physical-listings.json', dict(retrievedAt=worker.iso_utc(), model=model,
        items=list(state['items'].values()), coverage=[r for r in state['runs'].values()
        if r.get('query') in queries]))


if __name__ == '__main__':
    main()
