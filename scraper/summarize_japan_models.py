"""Export per-model captures and aggregate coverage without rewriting raw evidence."""
import json
import csv
import hashlib
import re
import unicodedata
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from prepare_model_home_import import prepare
from physical_book_match import match_physical_book
from run_japan_model_queue import pending_names, capture_hash
from model_offer_dates import normalized_offer_dates
from digital_photobook_titles import pending_title_reviews
from listing_images import listing_image_urls

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'scraper/japan-models'
sources = json.loads((ROOT / 'scraper/japan-marketplace-import-20261010.json').read_text(encoding='utf-8-sig'))
queue = json.loads((OUT / 'queue.json').read_text(encoding='utf-8'))
checkpoint_path = OUT / 'import-checkpoint.json'
imported_records = json.loads(checkpoint_path.read_text(encoding='utf-8')).get('records', {}) if checkpoint_path.exists() else {}
exclusions_path = OUT / 'excluded-listings.json'
excluded_listings = json.loads(exclusions_path.read_text(encoding='utf-8')) if exclusions_path.exists() else []
homepage_verification_path = OUT / 'homepage-models-verification.json'
homepage_verification = json.loads(homepage_verification_path.read_text(encoding='utf-8')) if homepage_verification_path.exists() else None
database_verification_path = OUT / 'import-verification.json'
database_verification = json.loads(database_verification_path.read_text(encoding='utf-8')) if database_verification_path.exists() else None
summary = []
pending_import_associations = 0
process_progress = {}
for source in ('physical', 'grajapa', 'kobo', 'wani'):
    progress_path = OUT / (source + '-progress.json')
    process_progress[source] = json.loads(progress_path.read_text(encoding='utf-8')) if progress_path.exists() else {}
for row in queue:
    directory = ROOT / row['directory']
    person = json.loads((directory / 'model.json').read_text(encoding='utf-8'))['models'][0]
    bibliography_path = directory / 'physical-books.json'
    bibliography = json.loads(bibliography_path.read_text(encoding='utf-8'))['books'] if bibliography_path.exists() else []
    items, coverage = {}, {}
    if row['status'] == 'reuse_fumina_capture':
        saved = json.loads((ROOT / 'scraper/fumina-suzuki-expanded/listings.json').read_text(encoding='utf-8'))
        items = {(x['sourceId'], x['externalId']): normalized_offer_dates(x) for x in saved['items']}
        coverage['fumina'] = 'preserved_existing_capture'
        # The captures stay preserved; refresh the derived projection after
        # work repairs so live verification uses the reviewed publication IDs.
        (ROOT / 'scraper/fumina-suzuki-expanded/home-import.json').write_text(
            json.dumps(prepare(dict(saved, items=list(items.values())), sources), ensure_ascii=False, indent=2), encoding='utf-8')
    else:
        for source, filename in [('physical', 'physical-state.json'), ('grajapa', 'digital-state.json'), ('kobo', 'kobo-state.json'), ('wani', 'publisher-wani-state.json')]:
            path = directory / filename
            if not path.exists():
                coverage[source] = {'status': 'pending'}
                continue
            state = json.loads(path.read_text(encoding='utf-8'))
            coverage[source] = {key: state[key] for key in ['status', 'pages', 'errors', 'rejected', 'runs', 'error'] if key in state}
            outcome = process_progress[source].get(str(person['id']), {})
            if outcome.get('exitCode') and outcome.get('checkpointHash') == capture_hash(state):
                coverage[source]['lastProcessExitCode'] = outcome['exitCode']
                if state.get('status') == 'running':
                    coverage[source]['status'] = 'interrupted'
            if source == 'physical':
                coverage[source]['pendingDetails'] = state.get('pendingDetails', {})
                limited = [dict(sourceId=run.get('sourceId', ''), query=run.get('query', ''),
                    consecutiveIrrelevantPages=run.get('consecutiveIrrelevantPages', 0), stopReason=run.get('stopReason', ''))
                    for run in state.get('runs', {}).values() if run.get('status') == 'query_relevance_exhausted']
                coverage[source]['relevanceLimitedQueries'] = limited
                coverage[source]['failedQueries'] = [dict(sourceId=run.get('sourceId', ''), query=run.get('query', ''),
                    status=run.get('status', ''), error=run.get('error', ''))
                    for run in state.get('runs', {}).values() if run.get('status') in ('source_failed', 'pagination_stalled')]
                coverage[source]['blockedQueries'] = [dict(sourceId=run.get('sourceId', ''), query=run.get('query', ''),
                    retryAfter=run.get('retryAfter', ''), reason=run.get('sourceBlockReason', ''))
                    for run in state.get('runs', {}).values() if run.get('status') == 'source_blocked']
            if source in ('grajapa', 'kobo', 'wani'):
                expected_names = set(name for name in [person.get('original_name'), person['canonical_public_name'], person.get('english_name'), *person.get('aliases', [])] if name)
                parameter = {'grajapa': 'keyword', 'kobo': 'pname', 'wani': 'tag'}[source]
                searched_names = {name for page in state.get('pages', []) for name in parse_qs(urlparse(page).query).get(parameter, [])}
                coverage[source]['searchedNameQueries'] = sorted(searched_names)
                coverage[source]['pendingNameQueries'] = sorted(pending_names(source, {'models': [person]}, state))
                coverage[source]['searchedNameQueries'] = sorted(expected_names - set(coverage[source]['pendingNameQueries']))
                if source in ('grajapa', 'kobo'):
                    coverage[source]['pendingTitleReviews'] = pending_title_reviews(state)
            if source == 'wani':
                coverage[source]['verifiedPrintEditions'] = len(state.get('items', {}))
                continue
            for item in state.get('items', {}).values():
                item = dict(item)
                item['imageUrls'] = listing_image_urls(item, state.get('details', {}).get(item.get('url'), {}))
                if not item.get('imageUrl') and item['imageUrls']:
                    item['imageUrl'] = item['imageUrls'][0]
                book, match_method = match_physical_book(item, bibliography)
                if book:
                    item.update(editionId=book['id'], publicationDate=book['publicationDate'],
                        publicationDateSourceUrl=book['metadataSourceUrl'], matchMethod=match_method)
                item = normalized_offer_dates(item)
                item['images'] = [{'url': url, 'sourceUrl': item['url'], 'role': 'store_product_image' if item['format'] == 'digital' else 'listing_photo'} for url in item.get('imageUrls', [item.get('imageUrl')]) if url]
                items[(item['sourceId'], item['externalId'])] = item
        capture = dict(model=person, physicalBooks=bibliography, items=list(items.values()), coverage=coverage)
        (directory / 'listings.json').write_text(json.dumps(capture, ensure_ascii=False, indent=2), encoding='utf-8')
        manifest = prepare(capture, sources)
        (directory / 'home-import.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
        for record in manifest:
            item = record['batch']['items'][0]
            key = str(person['id']) + ':' + record['source']['id'] + ':' + item['externalId']
            digest = hashlib.sha256(json.dumps(record, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
            if imported_records.get(key) != digest:
                pending_import_associations += 1
    imported_count = 150 if row['status'] == 'reuse_fumina_capture' else sum(key.startswith(str(person['id']) + ':') for key in imported_records)
    summary.append(dict(musecardsPersonId=person['id'], name=person['canonical_public_name'], imported=imported_count,
        physical=sum(x['format'] == 'physical' for x in items.values()), digital=sum(x['format'] == 'digital' for x in items.values()),
        unknownDates=sum(not x.get('publicationDate') for x in items.values()),
        unknownStoreReleaseDates=sum(x['format'] == 'digital' and not x.get('storeReleaseDate') for x in items.values()),
        missingCovers=sum(not x.get('imageUrl') for x in items.values()), coverage=coverage))
    fields = ['musecardsPersonId', 'sourceId', 'externalId', 'format', 'title', 'url', 'priceMinor', 'currency', 'priceType', 'status', 'observedAt', 'publicationDate', 'publicationDateSourceUrl', 'storeReleaseDate', 'storeReleaseDateSourceUrl', 'dateNote', 'imageUrl', 'imageUrls']
    with (directory / 'listings.csv').open('w', encoding='utf-8-sig', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        for item in items.values():
            exported = dict(item)
            exported['imageUrls'] = json.dumps(item.get('imageUrls', []), ensure_ascii=False)
            writer.writerow(exported)
(OUT / 'coverage.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
captured_physical = sum(row['physical'] for row in summary)
captured_digital = sum(row['digital'] for row in summary)
models_with_captures = sum(row['physical'] + row['digital'] > 0 for row in summary)
if homepage_verification:
    homepage_results = homepage_verification.get('results', [])
    homepage_passed = sum(result.get('filtersPassed', False) for result in homepage_results)
    live_api = homepage_verification.get('liveApi') or {}
    live_count = live_api.get('uniqueOffers')
    checked_offers = f'{live_count:,} live marketplace offers' if live_count is not None else f'{homepage_verification.get("importedModelAssociations", 0):,} imported associations'
    live_api_note = (f" Live public API snapshot: {live_api['uniqueOffers']:,} unique offers across {live_api['totalPages']:,} pages."
        if live_api.get('uniqueOffers') is not None and live_api.get('totalPages') is not None else '')
    homepage_line = (f'Homepage model search and physical/digital filters: {homepage_passed}/{len(homepage_results)} model identities passed against {checked_offers}; {pending_import_associations:,} prepared associations await import.' + live_api_note)
else:
    homepage_results, homepage_passed = [], 0
    homepage_line = 'Homepage search verification has not been generated yet.'
lines = ['# Japan-model photobook collection coverage', '',
    f'{len(summary)} MuseCards Japan-market model identities. Collection and verification are ongoing; pending searches are not no-result searches.', '',
    f'Checkpointed imports: {sum(row["imported"] for row in summary):,} records. Fumina Suzuki includes 150 preserved and previously imported offers.', '',
    f'Captured offer associations: {captured_physical + captured_digital:,} ({captured_physical:,} physical, {captured_digital:,} digital) across {models_with_captures} models.',
    f'Unknown original publication dates: {sum(row["unknownDates"] for row in summary):,}; unknown digital store release dates: {sum(row["unknownStoreReleaseDates"] for row in summary):,}; missing covers: {sum(row["missingCovers"] for row in summary):,}.', '',
    homepage_line,
    f'Read-only database verification: {database_verification["result"]["present"]:,}/{database_verification["result"]["expected"]:,} records present; price mismatches {database_verification["result"]["priceMismatches"]}, format mismatches {database_verification["result"]["formatMismatches"]}, missing galleries {database_verification["result"]["missingMedia"]}, missing publisher media {database_verification["result"]["missingPublisherMedia"]}.' if database_verification else 'Database readback verification has not been generated yet.', '',
    f'Paid-offer scope excludes {len(excluded_listings):,} verified free preview(s); their original captures and price observations remain preserved.', '',
    '| Model | Imported | Physical captures | Digital captures | Unknown publication dates | Unknown store release dates | Missing covers | Source state |',
    '| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |']
for row in summary:
    states = ', '.join(source + ': ' + (state.get('status', 'pending') + (f"; {len(state['pendingNameQueries'])} name queries pending" if state.get('pendingNameQueries') else '') + (f"; {len(state['relevanceLimitedQueries'])} broad queries stopped after unrelated results" if state.get('relevanceLimitedQueries') else '') + (f"; {len(state['failedQueries'])} failed or stalled queries" if state.get('failedQueries') else '') + (f"; {len(state['blockedQueries'])} queries paused by marketplace access restriction" if state.get('blockedQueries') else '') + (f"; {len(state['pendingDetails'])} product details pending" if state.get('pendingDetails') else '') if isinstance(state, dict) else state) for source, state in row['coverage'].items())
    name = row['name'].replace('|', '\\|')
    lines.append(f"| {name} | {row['imported']} | {row['physical']} | {row['digital']} | {row['unknownDates']} | {row['unknownStoreReleaseDates']} | {row['missingCovers']} | {states} |")
lines += ['', 'Counts are model-offer associations. Shared works can appear under multiple models; source/external IDs identify offers. A digital store release date is not treated as the original print publication date. Prices and availability reflect the recorded observation, not guaranteed current stock. Raw evidence and the original Fumina pilot remain preserved. Import verification is recorded separately in import-verification.json.']
(OUT / 'REPORT.md').write_text('\n'.join(lines), encoding='utf-8')
print(f'Coverage exported for {len(summary)} models; {sum(x["physical"]+x["digital"] for x in summary)} captured model-offer associations')
