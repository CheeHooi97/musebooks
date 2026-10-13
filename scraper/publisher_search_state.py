"""Persist each publisher name query until all observed pagination is visited."""
from urllib.parse import parse_qs, quote, urlparse


def initialize_searches(state, names, host):
    legacy_complete = (state.get('status') == 'public_search_exhausted'
        and not state.get('errors') and not state.get('error'))
    legacy_names = {parse_qs(urlparse(url).query).get('tag', [''])[0]
                    for url in state.get('pages', [])}
    searches = state.setdefault('searches', {})
    for name in names:
        if name in searches:
            continue
        complete = legacy_complete and name in legacy_names
        searches[name] = dict(status='public_search_exhausted' if complete else 'running',
            pending=[] if complete else ['https://' + host + '/category.php?tag=' + quote(name)],
            seen=[])
    return searches
