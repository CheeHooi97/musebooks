"""Create an idempotent catalog-import manifest from preserved model captures."""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit
from functools import lru_cache
from model_title_match import classify_title, model_names


@lru_cache(maxsize=4)
def read_identities(path, modified):
    return json.loads(path.read_text(encoding='utf-8'))['identities']


def identities_at(path):
    return read_identities(path, path.stat().st_mtime_ns)


@lru_cache(maxsize=4)
def edition_work_index(path, modified):
    plan = json.loads(path.read_text(encoding='utf-8'))
    index = {}
    for group in plan.get('groups', []):
        for member in group['members']:
            shared = dict(id=group['workId'], title=group['title'])
            previous = index.get(member['editionId'])
            if previous and previous['id'] != shared['id']:
                raise ValueError('A source edition has conflicting reviewed work identities')
            index[member['editionId']] = shared
    return index


def publication_for_edition(edition_id):
    root = Path(__file__).parent
    for name in ('fumina-suzuki-work-identities.json', 'japan-work-identities.json'):
        path = root / name
        if path.exists():
            shared = edition_work_index(path, path.stat().st_mtime_ns).get(edition_id)
            if shared:
                return shared
    return None


def identity(prefix, value):
    return prefix + hashlib.sha256(value.encode()).hexdigest()[:24]


def prepare(capture, source_manifest):
    model = capture.get('model', {'id': 6, 'canonical_public_name': '鈴木ふみ奈', 'english_name': 'Fumina Suzuki'})
    reviewed = identities_at(Path(__file__).parent / 'fumina-suzuki-work-identities.json') if model['id'] == 6 else capture.get('reviewedIdentities', {})
    sources = {r['source']['id']: r['source'] for r in source_manifest}
    japan_identities = Path(__file__).parent / 'japan-work-identities.json'
    if model['id'] != 6 and japan_identities.exists():
        reviewed = {**identities_at(japan_identities).get(str(model['id']), {}), **reviewed}
    books = {b['id']: b for b in capture.get('physicalBooks', [])}
    records = []
    for item in capture['items']:
        if item.get('importStatus') == 'already_imported':
            continue
        sid = item['sourceId']
        fmt = item['format']
        source = sources.get(sid)
        if source is None:
            host = urlsplit(item['url']).hostname
            source = dict(id=sid, name=item['platform'], region='JP', locale='ja-JP',
                          timezone='Asia/Tokyo', kind='digital_store', adapter=sid.replace('-', '_'),
                          accessMethod='browser', defaultFormat='digital', allowedFormats='digital',
                          baseUrl='https://' + host, allowedHosts=host, capabilities='listing_detail',
                          accessStatus='browser_review', ratePerMinute=6, enabled=True)
        observation = {key: item[key] for key in ('externalId', 'url', 'title', 'status', 'priceMinor',
            'currency', 'priceType', 'format', 'digitalAccess', 'publisher', 'imageUrl', 'observedAt',
            'statusEvidence', 'condition', 'shippingText') if key in item}
        record = dict(origin=dict(code='JP', name='Japan', nativeName='日本'), work={}, edition={},
                      source=source, batch=dict(sourceId=sid, parserVersion='model-home-import-v1',
                      retrievedAt=item['observedAt'], items=[observation]))
        image_urls = list(dict.fromkeys(url for url in [item.get('imageUrl'), *item.get('imageUrls', [])] if url and urlsplit(url).scheme == 'https'))
        record['media'] = [dict(externalId=item['externalId'], mediaType='listing_image' if index == 0 else f'listing_image_{index:03d}',
            originalUrl=url, storageUrl=url, sourceUrl=item['url'], isPrimary=index == 0) for index, url in enumerate(image_urls)]
        book = books.get(item.get('editionId')) if fmt == 'physical' else item
        if book:
            key = book.get('id') or sid + ':' + item['externalId']
            wid = identity('work-jp-', key)
            eid = identity('edition-jp-', key + ':' + fmt)
            title = book['title']
            # A store product identifies an edition/offer, not a new publication work.
            shared = reviewed.get(title + '\0' + book.get('publisher', ''))
            # Reviewed physical/digital pairs and collaborative publications
            # retain one work while their source editions stay distinct.
            shared = publication_for_edition(eid) or shared
            work_title = shared['title'] if shared else title
            if shared:
                wid = shared['id']
            # A store search for a short name also returns other people's books
            # (藤田もも for もも). Unless a reviewed identity or a reviewed item says
            # otherwise, only credit the model when the title names the model; the
            # offer stays unlinked and is flagged for review.
            match, proposed = classify_title(title, model_names(model))
            if not shared and not item.get('creditReviewed') and match != 'named':
                record['creditReview'] = dict(model=model.get('canonical_public_name', ''), title=title,
                                              match=match, proposedName=proposed)
                records.append(record)
                continue
            cover = book.get('coverImageUrl') or item['imageUrl']
            record['work'] = dict(id=wid, slug=wid, originalTitle=work_title, originCode='JP',
                                 featuredNames=','.join(dict.fromkeys(name for name in [model.get('canonical_public_name'), model.get('original_name'), model.get('english_name'), *model.get('aliases', [])] if name)), coverUrl=cover)
            native_name = model['canonical_public_name']
            record['featuredPerson'] = dict(slug='model-' + hashlib.sha256(native_name.strip().lower().encode()).hexdigest(),
                canonicalPublicName=native_name, originalName=model.get('original_name', ''), englishName=model.get('english_name', ''),
                personType=model.get('person_type', 'gravure_model'), verificationSourceUrl=model.get('verification_source_url', ''),
                profileSourceConfidence='musecards_database')
            record['edition'] = dict(id=eid, workId=wid, format=fmt, language='ja', editionMarket='JP',
                publisher=book.get('publisher', ''), isbn=book.get('isbn', ''), editionLabel=title,
                metadataSourceUrl=book.get('metadataSourceUrl') or item['url'], coverUrl=cover,
                originalCoverUrl=cover)
            if fmt == 'physical':
                publisher_images = list(dict.fromkeys(image['url'] for image in book.get('images', [])
                    if image.get('sourceUrl') == record['edition']['metadataSourceUrl'] and
                    urlsplit(image.get('url', '')).scheme == 'https'))
                record['publisherMedia'] = [dict(mediaType='publisher_cover' if url == cover else f'publisher_sample_{index:03d}',
                    originalUrl=url, storageUrl=url, sourceUrl=record['edition']['metadataSourceUrl'],
                    isPrimary=url == cover) for index, url in enumerate(publisher_images)]
            date = (book.get('storeReleaseDate') or item.get('releaseDate')) if fmt == 'digital' else book.get('publicationDate')
            if date:
                precision = 'day' if len(date) == 10 else 'month' if len(date) == 7 else 'year'
                stored_date = date if precision == 'day' else date + '-01' if precision == 'month' else date + '-01-01'
                record['edition'].update(releaseDate=stored_date + 'T00:00:00Z', releasePrecision=precision)
            observation['editionId'] = eid
        records.append(record)
    return records


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--capture', default='scraper/fumina-suzuki-expanded/listings.json')
    parser.add_argument('--sources', default='scraper/japan-marketplace-import-20261010.json')
    parser.add_argument('--output', default='scraper/fumina-suzuki-expanded/home-import.json')
    args = parser.parse_args()
    records = prepare(json.loads(Path(args.capture).read_text(encoding='utf-8')),
                      json.loads(Path(args.sources).read_text(encoding='utf-8')))
    Path(args.output).write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')
    held = [r for r in records if r.get('creditReview')]
    print(f'Prepared {len(records)} offers; {len(held)} kept unlinked because the title does not name the model; original captures unchanged')
    for r in held[:20]:
        review = r['creditReview']
        print(f"  {review['match']:6} {review['proposedName'] or '-':10} {review['title']}")
