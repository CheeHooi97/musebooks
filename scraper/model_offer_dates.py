"""Normalize derived offer dates without rewriting original source captures."""
from urllib.parse import urlparse


def normalized_offer_dates(offer):
    item = dict(offer)
    if item.get('format') != 'digital':
        return item
    item['storeReleaseDate'] = item.get('storeReleaseDate') or item.get('releaseDate') or None
    item['storeReleaseDateSourceUrl'] = item.get('storeReleaseDateSourceUrl') or (
        item.get('url', '') if item['storeReleaseDate'] else '')
    original_source = item.get('publicationDateSourceUrl') or ''
    original_url = urlparse(original_source)
    store_host = urlparse(item.get('url') or '').hostname
    original_host = original_url.hostname
    retail_hosts = {'books.rakuten.co.jp', 'www.grajapa.shueisha.co.jp'}
    if original_url.scheme not in ('http', 'https') or not original_host or original_host == store_host or original_host in retail_hosts:
        item['publicationDate'] = None
        item['publicationDateSourceUrl'] = ''
        item['dateNote'] = 'Digital store release date; original publication date is unknown unless verified separately.'
    return item
