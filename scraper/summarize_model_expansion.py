"""Build reviewable snapshots without changing the pilot or importing records."""
import csv
import hashlib
import html
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path
from photobook_worker import japan_publication_date


def main():
    root = Path(__file__).resolve().parent.parent
    folder = root / 'scraper/fumina-suzuki-expanded'
    read = lambda path: json.loads(path.read_text(encoding='utf-8'))
    preserved = read(folder / 'preserved-pilot.json')
    for entry in preserved:
        assert hashlib.sha256((root / entry['path']).read_bytes()).hexdigest() == entry['sha256'], entry['path']
    pilot = read(root / 'scraper/fumina-suzuki-pilot/reviewed.json')
    books = [*pilot['books'], *read(folder / 'additional-physical-books.json')['books']]
    physical = read(folder / 'physical-state.json')
    digital = read(folder / 'digital-state.json')
    kobo = read(folder / 'kobo-state.json') if (folder / 'kobo-state.json').exists() else dict(items={}, status='not_started', pages=[])
    database_check = (folder / 'database-import-check.json').exists()
    imported = read(folder / ('database-import-check.json' if database_check else 'import-check.json'))
    if not database_check:
        assert imported['totalPages'] <= 1, 'Import comparison needs additional API pages'
    imported_ids = {(i['sourceId'] if database_check else i['source']['id'], i['externalId']) for i in imported['items']}
    imported_urls = {i['url'].split('?', 1)[0].split('#', 1)[0] for i in imported['items']}
    normalize = lambda value: re.sub(r'\s+', '', unicodedata.normalize('NFKC', value).casefold())
    offers = {}
    for original in [*pilot['offers'], *physical['items'].values(), *digital['items'].values(), *kobo['items'].values()]:
        item = dict(original)
        item['title'] = html.unescape(item['title'])
        item.setdefault('format', 'physical')
        item.setdefault('musecardsPersonId', 6)
        item.setdefault('priceMinor', item.get('priceJPY'))
        item.setdefault('imageUrls', [a['url'] for a in item.get('listingImages', [])])
        item.setdefault('imageUrl', item.get('coverImageUrl') or item.get('listingImageUrl', ''))
        if item['format'] == 'physical':
            detail = physical['details'].get(item['url'], {})
            pictures = detail.get('structured', {}).get('image', [])
            pictures = pictures if isinstance(pictures, list) else [pictures]
            pictures = [p.get('url') or p.get('contentUrl') if isinstance(p, dict) else p for p in pictures]
            item['imageUrls'] = list(dict.fromkeys([*item['imageUrls'], *([item['imageUrl']] if item['imageUrl'] else []), *(p for p in pictures if isinstance(p, str) and p.startswith(('https://', 'http://')))]))
        item['importStatus'] = 'already_imported' if (item['sourceId'], item['externalId']) in imported_ids or item['url'] in imported_urls else ('not_imported_at_database_check' if database_check else 'not_imported_by_this_capture')
        # Store release dates can differ from a publisher's original edition date.
        item['storeReleaseDate'] = item.get('releaseDate') if item['format'] == 'digital' else None
        item.setdefault('publicationDate', item.get('releaseDate'))
        if item['format'] == 'physical' and not item['publicationDate']:
            selected_description = physical['details'].get(item['url'], {}).get('structured', {}).get('description', '')
            item['publicationDate'] = japan_publication_date({}, selected_description)
            if item['publicationDate']:
                item['publicationDateSourceUrl'] = item['url']
        item.setdefault('publicationPrecision', 'day' if item['publicationDate'] else 'unknown')
        if item['format'] == 'physical' and not re.search(r'セット|まとめ|\d+冊', item['title']):
            matches = [b for b in books if re.search(r'(?<![a-z])' + re.escape(normalize(b['titleAlias'])) + r'(?![a-z])', normalize(item['title']))]
            if len(matches) == 1:
                book = matches[0]
                item.update(publicationDate=book['publicationDate'], publicationPrecision=book['publicationPrecision'], publicationDateSourceUrl=book['metadataSourceUrl'], canonicalCoverImageUrl=book['coverImageUrl'], editionId=book['id'], matchMethod='model_title_physical')
        assert item['priceMinor'] > 0 and item['currency'] == 'JPY'
        item['images'] = [dict(url=url, sourceUrl=item['url'], role='listing_photo' if item['format'] == 'physical' else 'store_product_image') for url in item['imageUrls']]
        if item['format'] == 'digital':
            item['storeCoverImageUrl'] = item['imageUrl']
        offers[(item['sourceId'], item['externalId'], item['format'])] = item
    items = sorted(offers.values(), key=lambda i: (i['format'], i['platform'], i['title'], i['externalId']))
    if database_check:
        assert imported['inputListingCount'] == len(items), 'Refresh the database comparison for the latest capture'
    coverage = dict(physicalStatus=physical['status'], physicalRuns=list(physical['runs'].values()), digitalStatus=digital['status'], digitalPages=digital['pages'], digitalRejected=digital['rejected'], digitalErrors=digital['errors'])
    coverage['kobo'] = {k:v for k,v in kobo.items() if k not in ['items', 'candidates']}
    payload = dict(model=pilot['model'], physicalBooks=books, items=items, coverage=coverage, preservedPilotFiles=len(preserved), importCheck=imported)
    (folder / 'listings.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    unimported = [i for i in items if i['importStatus'] != 'already_imported']
    (folder / 'unimported-listings.json').write_text(json.dumps(dict(payload, items=unimported), ensure_ascii=False, indent=2), encoding='utf-8')
    fields = ['format', 'platform', 'title', 'priceMinor', 'currency', 'priceType', 'publicationDate', 'publicationPrecision', 'storeReleaseDate', 'publicationDateSourceUrl', 'url', 'imageUrl', 'canonicalCoverImageUrl', 'imageUrls', 'importStatus']
    for filename, rows in [('listings.csv', items), ('unimported-listings.csv', unimported)]:
        with (folder / filename).open('w', encoding='utf-8-sig', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=fields, extrasaction='ignore')
            writer.writeheader()
            for item in rows:
                writer.writerow(dict(item, imageUrls=' | '.join(item['imageUrls'])))
    counts = Counter(i['format'] for i in items)
    lines = ['# Fumina Suzuki expanded listings', '', f'Original pilot preserved: {len(preserved)} file hashes verified. No database import or upload performed.', '', f"Snapshot: {counts['physical']} physical offers; {counts['digital']} digital offers.", '', f"Physical capture: {physical['status']}. Digital Grajapa capture: {digital['status']} ({len(digital['pages'])} public result pages).", '', 'Coverage is source-specific, not a worldwide completeness claim. Mercari remains disabled by source configuration. BOOK☆WALKER returned no visible author results; Kodansha exposed a seven-title bibliography but its complete selling offers have not been verified. Rejected shared anthologies require individual model confirmation.', '', 'Digital dates below are the store’s release dates; they may be later than the original publisher edition. Physical dates use independently verified publisher metadata when matched, otherwise the listing’s explicit publication date. Missing dates remain unknown. Image URLs and gallery evidence are in listings.json and listings.csv. Auction prices are current bids, not fixed asking prices.', '', '| Format | Platform | Listing | Price (JPY) | Publication/store release |', '|---|---|---|---:|---|']
    for item in unimported:
        title = item['title'].replace('|', '\\|').replace('\n', ' ')
        basis = {'auction_current':'current bid', 'fixed':'asking', 'digital':'store price'}.get(item['priceType'], item['priceType'])
        lines.append(f"| {item['format']} | {item['platform']} | [{title}]({item['url']}) | {item['priceMinor']:,} ({basis}) | {item.get('publicationDate') or 'unknown'} |")
    lines.extend(['', '## Physical search coverage', ''])
    lines.append(f"- Table shows {len(unimported)} offers absent from the saved {'read-only database' if database_check else 'public API'} check; {len(items)-len(unimported)} already imported offers are retained in listings.json but omitted from the table.")
    lines.append(f"- Rakuten Kobo digital: {kobo['status']}; {len(kobo['pages'])} saved search pages.")
    for run in physical['runs'].values():
        lines.append(f"- {run['sourceId']} / {run['query']}: {run['status']}; {len(run['batches'])} saved batches; cursor {run['cursor'] or 'first page'}.")
    lines.extend(['', '## Solo physical bibliography', '', 'The agency’s [official profile](https://www.office-pocket.com/profile.html) identifies seven solo physical books. Their prices above belong to individual seller offers. A month-only date does not imply a known day.', '', '| Title | Publication | Publisher | Evidence |', '|---|---|---|---|'])
    for book in sorted(books, key=lambda b: b['publicationDate']):
        lines.append(f"| {book['title']} | {book['publicationDate']} ({book['publicationPrecision']}) | {book['publisher']} | [metadata]({book['metadataSourceUrl']}) |")
    (folder / 'REPORT.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(json.dumps(dict(counts=counts, preservedPilotFiles=len(preserved), physicalStatus=physical['status'], digitalStatus=digital['status'])))


if __name__ == '__main__':
    main()
