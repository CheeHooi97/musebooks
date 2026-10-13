"""Capture public Rakuten Kobo author listings, with evidence and checkpoints."""
import argparse
import json
import re
import time
from pathlib import Path
from urllib.parse import parse_qs, urlparse, quote
from cloakbrowser import launch
from photobook_worker import ensure_rendered_page, iso_utc, japan_publication_date, photobook_title_exclusion
from kobo_cover_match import selected_cover_images
from kobo_search_scope import PHOTOBOOK_GENRE_ID, author_search_url, filter_candidates, search_scope
from digital_photobook_titles import digital_title_exclusion, reopen_title_reviews
from capture_checkpoint import save_json as save

HOST = 'books.rakuten.co.jp'
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'scraper/fumina-suzuki-expanded'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='scraper/fumina-suzuki-expanded')
    parser.add_argument('--model-file', default='scraper/fumina-suzuki-model.json')
    parser.add_argument('--offline', action='store_true', help='Reassess saved product evidence without browser navigation')
    args = parser.parse_args()
    OUT = (ROOT / args.output).resolve()
    if not OUT.is_relative_to(ROOT):
        parser.error('Output must stay inside workspace')
    OUT.mkdir(parents=True, exist_ok=True)
    selected_model = json.loads((ROOT / args.model_file).read_text(encoding='utf-8'))['models'][0]
    native_name = selected_model.get('original_name') or selected_model['canonical_public_name']
    names = list(dict.fromkeys(name for name in [native_name, selected_model['canonical_public_name'], selected_model.get('english_name'), *selected_model.get('aliases', [])] if name))
    # The unfiltered author index can include over a thousand unrelated titles
    # for short names. Retain Kobo's dedicated e-book photobook genre query.
    start = author_search_url(native_name)
    path = OUT / 'kobo-state.json'
    state = json.loads(path.read_text(encoding='utf-8')) if path.exists() else dict(items={}, candidates={}, pages=[], rejected={}, errors={}, nextUrl=start, status='running')
    state.setdefault('pendingSearches', [])
    state.setdefault('photobookCategoryCandidates', {})
    state.setdefault('preFilteredCandidates', {})
    reopen_title_reviews(state)
    searched_scopes = {search_scope(url) for url in state['pages']}
    current_scope = search_scope(state['nextUrl']) if state['nextUrl'] else None
    for name in names:
        seed = author_search_url(name)
        if (name, PHOTOBOOK_GENRE_ID) not in searched_scopes and (name, PHOTOBOOK_GENRE_ID) != current_scope and seed not in state['pendingSearches']:
            state['pendingSearches'].append(seed)
    if not (args.offline and state.get('status') == 'pagination_stalled'):
        state['status'] = 'running'
    if state.get('error'):
        state.setdefault('previousSourceErrors', []).append(state.pop('error'))
    b = None if args.offline else launch(headless=True)
    cache_root = ROOT / 'scraper/japan-models/shared-details/kobo'
    cache_root.mkdir(parents=True, exist_ok=True)
    last = 0
    def navigate(page, url):
        nonlocal last
        if urlparse(url).hostname != HOST:
            raise ValueError('Off-host navigation')
        time.sleep(max(0, 10 - (time.monotonic() - last)))
        last = time.monotonic()
        page.goto(url, wait_until='domcontentloaded', timeout=60000)
        page.wait_for_timeout(1000)
        body = page.locator('body').inner_text()
        ensure_rendered_page(body, 'rakuten-kobo-jp')
        if urlparse(page.url).hostname != HOST:
            raise ValueError('Redirected off-host')
        return body
    try:
        search, detail = (None, None) if args.offline else (b.new_page(locale='ja-JP'), b.new_page(locale='ja-JP'))
        while not args.offline and (state['nextUrl'] or state['pendingSearches']):
            if not state['nextUrl']:
                state['nextUrl'] = state['pendingSearches'].pop(0)
            url = state['nextUrl']
            if url in state['pages']:
                state['status'] = 'pagination_stalled'
                break
            print('Kobo search:', url, flush=True)
            body = navigate(search, url)
            links = search.locator('a').evaluate_all('els=>els.map(a=>({url:a.href,text:a.innerText,title:a.title}))')
            category_query = search_scope(url)[1] == PHOTOBOOK_GENRE_ID
            for a in links:
                parsed = urlparse(a['url'])
                if parsed.hostname == HOST and re.fullmatch('/rk/[0-9a-f]{32}/', parsed.path):
                    product_url = 'https://' + HOST + parsed.path
                    label = (a['text'] or a['title'] or '').strip()
                    # Search cards link to the same product once for its cover
                    # and again for its title. Keep the title instead of the
                    # first, empty image-link label.
                    if label or product_url not in state['candidates']:
                        state['candidates'][product_url] = label
                    if category_query:
                        state['photobookCategoryCandidates'][product_url] = label
            following = ''
            for a in links:
                parsed = urlparse(a['url'])
                if parsed.hostname == HOST and parsed.path == '/search' and search_scope(a['url']) == search_scope(url) and re.search(r'次|Next', a['text'], re.I):
                    following = a['url']
                    break
            state['pages'].append(url)
            state['nextUrl'] = following
            save(OUT / f'kobo-search-{len(state["pages"])}.json', dict(url=url, body=body, links=links, nextUrl=following))
            save(path, state)
        candidate_rows, prefiltered = filter_candidates(
            state['candidates'], state.get('photobookCategoryCandidates', {}),
            category_searched=any(search_scope(url)[1] == PHOTOBOOK_GENRE_ID for url in state['pages']))
        state['preFilteredCandidates'].update(prefiltered)
        if state.get('photobookCategoryCandidates'):
            for url in state['photobookCategoryCandidates']:
                if url in state['rejected'] and url not in state['items']:
                    state.setdefault('previouslyRejected', {})[url] = state['rejected'].pop(url)
        save(path, state)
        for url, label in candidate_rows.items():
            if url in state['items'] or url in state['rejected']:
                continue
            print('Kobo detail:', url, flush=True)
            try:
                cache_path = cache_root / (urlparse(url).path.split('/')[2] + '.json')
                cached = json.loads(cache_path.read_text(encoding='utf-8')) if cache_path.exists() else None
                if args.offline and not cached:
                    state['errors'][url] = 'Product evidence has not been captured; online detail inspection remains pending'
                    continue
                body = cached['body'] if cached else navigate(detail, url)
                if not cached:
                    cached = dict(body=body, images=detail.locator('img').evaluate_all('els=>els.map(i=>({url:i.currentSrc||i.src,alt:i.alt}))'), observedAt=iso_utc())
                    save(cache_path, cached)
                selected = body.split('シリーズ商品：', 1)[0].split('この商品を買った人', 1)[0]
                heading = re.search(r'([^\n]+)\s*\[電子書籍版\]', selected)
                title = heading.group(1).strip() if heading else ''
                reason = digital_title_exclusion(title)
                price = re.search(r'([0-9,]+)円\s*[（(]税込[）)]', selected)
                author = re.search(r'著者\s*[:：]\s*([\s\S]*?)(?:シリーズ名|レーベル|発売日|出版社)', selected)
                if not title or reason or not author or not any(re.sub(r'\s+', '', name) in re.sub(r'\s+', '', author.group(1)) for name in names) or '電子書籍' not in selected or '写真集' not in selected or not price:
                    state['rejected'][url] = reason or 'selected_photobook_model_or_price_unverified'
                    continue
                images = cached['images'] if cached else detail.locator('img').evaluate_all('els=>els.map(i=>({url:i.currentSrc||i.src,alt:i.alt}))')
                if not cached:
                    save(cache_path, dict(body=body, images=images, observedAt=iso_utc()))
                # Match selected product title, excluding unrelated recommendations.
                images = selected_cover_images(images, title)
                date = japan_publication_date({}, selected)
                publisher = re.search(r'出版社\s*[:：]\s*([^\n]+)', selected)
                eid = urlparse(url).path.split('/')[2]
                state['items'][url] = dict(sourceId='rakuten-kobo-jp', platform='楽天Kobo', externalId=eid, musecardsPersonId=selected_model['id'], format='digital', digitalAccess='authorized_store', title=title, url=url, priceMinor=int(price.group(1).replace(',', '')), currency='JPY', priceType='digital', taxIncluded=True, status='unknown', releaseDate=date, publicationDateSourceUrl=url if date else '', publisher=publisher.group(1).strip() if publisher else '', imageUrl=images[0] if images else '', imageUrls=images, observedAt=cached['observedAt'] if cached else iso_utc(), modelEvidence=author.group(0))
                save(OUT / f'kobo-detail-{eid}.json', dict(url=url, body=body, selected=selected, images=images))
                state['errors'].pop(url, None)
            except Exception as exc:
                state['errors'][url] = f'{type(exc).__name__}: {exc}'
                print('Kobo failure:', str(exc), flush=True)
            finally:
                save(path, state)
        if state['status'] != 'pagination_stalled':
            state['errors'] = {url: error for url, error in state['errors'].items()
                if url not in state['items'] and url not in state['rejected']}
            state['status'] = ('pending_searches' if state['nextUrl'] or state['pendingSearches'] else
                'public_search_exhausted' if not state['errors'] else 'detail_failures')
    except Exception as exc:
        state.update(status='source_failed', error=f'{type(exc).__name__}: {exc}')
    finally:
        if b:
            b.close()
        save(path, state)
        save(OUT / 'kobo-listings.json', dict(items=list(state['items'].values()), coverage={k:v for k,v in state.items() if k not in ['items','candidates']}))
        print('Kobo collected:', len(state['items']), state['status'], flush=True)


if __name__ == '__main__':
    main()
