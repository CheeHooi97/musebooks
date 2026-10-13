"""Use Rakuten Kobo's electronic photobook genre for author searches."""
from urllib.parse import parse_qs, quote, urlparse

HOST = 'books.rakuten.co.jp'
PHOTOBOOK_GENRE_ID = '101915'


def author_search_url(name):
    return f'https://{HOST}/search?g={PHOTOBOOK_GENRE_ID}&pname={quote(name)}'


def search_scope(url):
    query = parse_qs(urlparse(url).query)
    return query.get('pname', [''])[0], query.get('g', [''])[0]


def filter_candidates(candidates, photobook_candidates, *, category_searched=False):
    """Keep photo-genre results and retain reasons for broad-query skips."""
    if not photobook_candidates and not category_searched:
        return dict(candidates), {}
    kept = {url: label for url, label in candidates.items() if url in photobook_candidates}
    skipped = {url: 'outside_kobo_photobook_category' for url in candidates if url not in photobook_candidates}
    return kept, skipped
