"""Join a model-scoped capture to explicitly reviewed publisher metadata."""
import argparse
import csv
import json
import re
import unicodedata
from pathlib import Path


def normalized(value):
    return re.sub(r'\s+', '', unicodedata.normalize('NFKC', value)).casefold()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--capture', required=True)
    parser.add_argument('--books', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    output = (root / args.output).resolve()
    if not output.is_relative_to(root):
        parser.error('Output must stay inside the repository')
    capture = json.loads((root / args.capture).read_text(encoding='utf-8'))
    verified = json.loads((root / args.books).read_text(encoding='utf-8'))
    if capture['model']['id'] != verified['musecardsPersonId']:
        parser.error('Capture and bibliography model identities differ')
    offers = []
    for original in capture['items']:
        item = dict(original)
        title = normalized(item['title'])
        matches = []
        if normalized(verified['nativeName']) in title and not re.search(r'セット|まとめ|\d+冊', title):
            for book in verified['books']:
                alias = unicodedata.normalize('NFKC', book['titleAlias']).casefold()
                if re.search(r'(?<![a-z])' + re.escape(alias) + r'(?![a-z])', unicodedata.normalize('NFKC', item['title']).casefold()):
                    matches.append(book)
        item['listingImageUrl'] = item.pop('coverImageUrl', '')
        item['listingImages'] = [dict(role='listing_photo', url=url, sourceUrl=item['url']) for url in item.pop('imageUrls', [])]
        item['editionId'] = None
        item['matchMethod'] = 'unlinked'
        if len(matches) == 1:
            book = matches[0]
            item.update(editionId=book['id'], publicationDate=book['publicationDate'],
                        publicationDateSourceUrl=book['metadataSourceUrl'],
                        canonicalCoverImageUrl=book['coverImageUrl'],
                        matchMethod='reviewed_model_title_physical',
                        matchEvidence='Database native model name and distinct title match publisher physical-book metadata; listing ISBN not independently verified.')
        offers.append(item)
    assets_path = output.parent / 'publisher-images/assets.json'
    assets = json.loads(assets_path.read_text(encoding='utf-8')) if assets_path.exists() else []
    for asset in assets:
        if asset['bookId'] == 'jp-isbn-9784046053039' and asset['role'] == 'publisher_product_image':
            asset['role'] = 'cover'
    if assets_path.exists():
        assets_path.write_text(json.dumps(assets, ensure_ascii=False, indent=2), encoding='utf-8')
    result = dict(model=capture['model'], modelDatabase='gravure_model', retrievedAt=capture['retrievedAt'],
                  books=verified['books'], offers=offers, publisherAssets=assets, runs=capture['runs'],
                  scope='Bounded pilot: 1 search page and up to 8 details per platform; no database import or media upload.')
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    fields = ['platform', 'title', 'priceJPY', 'currency', 'priceType', 'publicationDate', 'publicationDateSourceUrl', 'editionId', 'url', 'listingImageUrl', 'canonicalCoverImageUrl', 'observedAt']
    with output.with_suffix('.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(offers)
    print(json.dumps(dict(offers=len(offers), verifiedBooks=len(verified['books']), datedOffers=sum(bool(x['publicationDate']) for x in offers), listingImageUrls=sum(len(x['listingImages']) for x in offers), downloadedPublisherAssets=sum(x['status']=='downloaded' for x in assets))))


if __name__ == '__main__':
    main()
