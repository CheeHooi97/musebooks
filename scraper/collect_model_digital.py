"""Collect the public, authorized Grajapa ebook catalogue for one model."""
import argparse
import json
import re
import time
from pathlib import Path
from urllib.parse import parse_qs, urljoin, urlparse, quote

from cloakbrowser import launch
from photobook_worker import ensure_rendered_page, iso_utc, japan_publication_date, photobook_title_exclusion, structured_product
from digital_photobook_titles import digital_title_exclusion, reopen_title_reviews
from capture_checkpoint import save_json as save

HOST = 'www.grajapa.shueisha.co.jp'
START = 'https://www.grajapa.shueisha.co.jp/search?keyword=%E9%88%B4%E6%9C%A8%E3%81%B5%E3%81%BF%E5%A5%88'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    parser.add_argument('--model-file', default='scraper/fumina-suzuki-model.json')
    parser.add_argument('--offline', action='store_true', help='Reassess saved product evidence without browser navigation')
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    output = (root / args.output).resolve()
    if not output.is_relative_to(root):
        parser.error('Output must stay inside workspace')
    output.mkdir(parents=True, exist_ok=True)
    selected_model = json.loads((root / args.model_file).read_text(encoding='utf-8'))['models'][0]
    native_name = selected_model.get('original_name') or selected_model['canonical_public_name']
    names = list(dict.fromkeys(name for name in [native_name, selected_model['canonical_public_name'], selected_model.get('english_name'), *selected_model.get('aliases', [])] if name))
    start = 'https://' + HOST + '/search?keyword=' + quote(native_name)
    path = output / 'digital-state.json'
    state = json.loads(path.read_text(encoding='utf-8')) if path.exists() else dict(items={}, candidates={}, pages=[], rejected={}, errors={}, nextUrl=start, status='running')
    state.setdefault('pendingSearches', [])
    reopen_title_reviews(state)
    searched_names = {parse_qs(urlparse(url).query).get('keyword', [''])[0] for url in state['pages']}
    current_name = parse_qs(urlparse(state['nextUrl']).query).get('keyword', [''])[0]
    for name in names:
        seed = 'https://' + HOST + '/search?keyword=' + quote(name)
        if name not in searched_names and name != current_name and seed not in state['pendingSearches']:
            state['pendingSearches'].append(seed)
    if not (args.offline and state.get('status') == 'pagination_stalled'):
        state['status'] = 'running'
    if state.get('error'):
        state.setdefault('previousSourceErrors', []).append(state.pop('error'))
    browser = None if args.offline else launch(headless=True)
    cache_root = root / 'scraper/japan-models/shared-details/grajapa'
    cache_root.mkdir(parents=True, exist_ok=True)
    last_navigation = 0
    def navigate(page, url):
        nonlocal last_navigation
        if urlparse(url).hostname != HOST:
            raise ValueError('Page left the authorized store host')
        time.sleep(max(0, 10 - (time.monotonic() - last_navigation)))
        last_navigation = time.monotonic()
        page.goto(url, wait_until='domcontentloaded', timeout=60000)
        page.wait_for_timeout(750)
        body = page.locator('body').inner_text()
        ensure_rendered_page(body, 'grajapa-jp')
        if urlparse(page.url).hostname != HOST or '/login' in page.url:
            raise ValueError('Store redirected to an access gate')
        return body
    try:
        search, detail = (None, None) if args.offline else (browser.new_page(locale='ja-JP'), browser.new_page(locale='ja-JP'))
        while not args.offline and (state['nextUrl'] or state['pendingSearches']):
            if not state['nextUrl']:
                state['nextUrl'] = state['pendingSearches'].pop(0)
            url = state['nextUrl']
            if url in state['pages']:
                state['status'] = 'pagination_stalled'
                break
            print('Digital search:', url, flush=True)
            body = navigate(search, url)
            cards = search.locator('a[href*="/item/detail/gravure/"]').evaluate_all("els=>els.map(a=>({url:a.href,title:a.innerText.trim()||a.querySelector('img')?.alt||'',imageUrl:a.querySelector('img')?.src||''}))")
            for card in cards:
                if re.fullmatch(r'/item/detail/gravure/[0-9a-f]{32}', urlparse(card['url']).path) and urlparse(card['url']).hostname == HOST:
                    state['candidates'].setdefault(card['url'], card)
            # This store uses observed span[data-url] controls, separately for
            # photobooks, magazines, and news. Follow only the photobook pager.
            current_page = int(parse_qs(urlparse(url).query).get('gravure_page', ['1'])[0])
            following = ''
            for control in search.locator('span.js-pagination-link[data-url]').evaluate_all("els=>els.map(e=>e.getAttribute('data-url'))"):
                parsed = urlparse(control)
                params = parse_qs(parsed.query)
                if parsed.hostname == HOST and parsed.path == '/search' and parsed.fragment == 'cat1' and params.get('keyword') == parse_qs(urlparse(url).query).get('keyword') and params.get('gravure_page') == [str(current_page + 1)]:
                    following = control
                    break
            state['pages'].append(url)
            state['nextUrl'] = following
            save(output / f'grajapa-search-{len(state["pages"])}.json', dict(url=url, body=body, cards=cards, nextUrl=following))
            save(path, state)
        for url, card in state['candidates'].items():
            if url in state['items'] or url in state['rejected']:
                continue
            print('Digital detail:', url, flush=True)
            try:
                cache_path = cache_root / (urlparse(url).path.rsplit('/', 1)[-1] + '.json')
                cached = json.loads(cache_path.read_text(encoding='utf-8')) if cache_path.exists() else None
                if args.offline and not cached:
                    state['errors'][url] = 'Product evidence has not been captured; online detail inspection remains pending'
                    continue
                body = cached['body'] if cached else navigate(detail, url)
                if not cached:
                    cached = dict(body=body, structured=structured_product(detail),
                        imageUrls=detail.locator('img').evaluate_all("els=>els.map(i=>i.currentSrc||i.src)"), observedAt=iso_utc())
                    save(cache_path, cached)
                selected = body.split('続きを読む', 1)[0]
                model = re.search(r'モデル\s*[:：]\s*([^\n]+)', selected)
                if not model or not any(re.sub(r'\s+', '', name) in re.sub(r'\s+', '', model.group(1)) for name in names):
                    state['rejected'][url] = 'selected_model_mismatch'
                    continue
                structured = cached['structured'] if cached else structured_product(detail)
                title = structured.get('name') or card['title']
                reason = digital_title_exclusion(title)
                if reason:
                    state['rejected'][url] = reason
                    continue
                # Native tax-inclusive price precedes membership discounts;
                # this store's JSON-LD price is sometimes the pre-tax amount.
                price = re.search(r'[￥¥]\s*([0-9,]+)\s*(?:\(税込\)|（税込）)', selected)
                if not price:
                    state['rejected'][url] = 'tax_inclusive_price_unverified'
                    continue
                date = japan_publication_date({}, selected)
                external_id = urlparse(url).path.rsplit('/', 1)[-1]
                image_value = structured.get('image')
                images = image_value if isinstance(image_value, list) else [image_value]
                images += cached['imageUrls'] if cached else detail.locator('img').evaluate_all("els=>els.map(i=>i.currentSrc||i.src)")
                images = list(dict.fromkeys(urljoin(url, value) for value in images if isinstance(value, str) and external_id in value))
                publisher = re.search(r'出版社\s*[:：]\s*([^\n]+)', selected)
                pages = re.search(r'ページ数\s*[:：]\s*(\d+)', selected)
                state['items'][url] = dict(sourceId='grajapa-jp', platform='週プレ グラジャパ！', externalId=external_id,
                    musecardsPersonId=selected_model['id'], format='digital', digitalAccess='authorized_store', title=title, url=url,
                    priceMinor=int(price.group(1).replace(',', '')), currency='JPY', priceType='digital',
                    taxIncluded=True, status='active' if '買い物かごに追加' in selected else 'unknown',
                    releaseDate=date, publicationDateSourceUrl=url if date else '', publisher=publisher.group(1) if publisher else '',
                    pageCount=int(pages.group(1)) if pages else None, imageUrl=images[0] if images else '', imageUrls=images,
                    observedAt=cached['observedAt'] if cached else iso_utc(), modelEvidence=model.group(0))
                save(output / f'grajapa-detail-{external_id}.json', dict(url=url, body=body, structured=structured))
                state['errors'].pop(url, None)
            except Exception as exc:
                state['errors'][url] = f'{type(exc).__name__}: {exc}'
                print('Digital failure:', url, str(exc), flush=True)
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
        if browser:
            browser.close()
        save(path, state)
        save(output / 'digital-listings.json', dict(retrievedAt=iso_utc(), items=list(state['items'].values()), coverage=dict(status=state['status'], pages=state['pages'], candidates=len(state['candidates']), rejected=state['rejected'], errors=state['errors'], error=state.get('error'))))
        print('Digital collected:', len(state['items']), state['status'], flush=True)


if __name__ == '__main__':
    main()
