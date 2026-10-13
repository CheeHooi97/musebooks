"""Collect publisher-backed print bibliography; publisher list prices are not offers."""
import argparse
import json
import re
import time
import unicodedata
from pathlib import Path
from urllib.parse import parse_qs, quote, urlparse

from cloakbrowser import launch
from photobook_worker import ensure_rendered_page, iso_utc, photobook_title_exclusion
from publisher_search_state import initialize_searches
from capture_checkpoint import save_json as save

HOST = 'www.wani.co.jp'
ROOT = Path(__file__).resolve().parent.parent


def normalize(value):
    return re.sub(r'\s+', '', unicodedata.normalize('NFKC', value)).casefold()


def parse_book(body, title, images, url, names):
    """Require a publisher print ISBN/date, a photobook title and a model credit."""
    if '写真集' not in title or not any(normalize(name) in normalize(title) for name in names):
        return None
    if photobook_title_exclusion(title):
        return None
    isbn = re.search(r'\[ISBN\]\s*([0-9-]{13,17})', body)
    date = re.search(r'\[発売日\]\s*(\d{4}-\d{2}-\d{2})', body)
    if not isbn or not date:
        return None
    digits = isbn.group(1).replace('-', '')
    if len(digits) != 13 or sum(int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(digits)) % 10:
        return None
    alias = re.search(r'[『「](.+?)[』」]', title)
    book = dict(id='jp-isbn-' + digits, title=title, titleAlias=alias.group(1).strip() if alias else title,
        format='physical', isbn=digits, publisher='ワニブックス', publicationDate=date.group(1),
        publicationPrecision='day', metadataSourceUrl=url, observedAt=iso_utc())
    price = re.search(r'￥\s*([\d,]+)', body)
    if price:
        book['publisherListPriceJPY'] = int(price.group(1).replace(',', ''))
    public_images = list(dict.fromkeys(image for image in images if urlparse(image).hostname == HOST and '/images/Article/' in urlparse(image).path))
    if public_images:
        book['coverImageUrl'] = public_images[0]
        book['images'] = [dict(role='publisher_product_image', url=image, sourceUrl=url) for image in public_images]
        book['imageNote'] = 'Images observed on the publisher product page; visual verification recorded separately.'
    return book


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model-file', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    output = (ROOT / args.output).resolve()
    if not output.is_relative_to(ROOT):
        parser.error('Output must stay inside workspace')
    output.mkdir(parents=True, exist_ok=True)
    person = json.loads((ROOT / args.model_file).read_text(encoding='utf-8'))['models'][0]
    names = list(dict.fromkeys(name for name in [person.get('original_name'), person['canonical_public_name'],
        person.get('english_name'), *person.get('aliases', [])] if name))
    checkpoint = output / 'publisher-wani-state.json'
    state = json.loads(checkpoint.read_text(encoding='utf-8')) if checkpoint.exists() else dict(items={}, pages=[], candidates={}, rejected={}, errors={})
    searches = initialize_searches(state, names, HOST)
    state['status'] = 'running'
    if state.get('error'):
        state.setdefault('previousSourceErrors', []).append(state.pop('error'))
    browser = launch(headless=True)
    last = 0

    def navigate(page, url):
        nonlocal last
        if urlparse(url).hostname != HOST:
            raise ValueError('Off-host publisher navigation')
        time.sleep(max(0, 10 - (time.monotonic() - last)))
        last = time.monotonic()
        page.goto(url, wait_until='domcontentloaded', timeout=60000)
        page.wait_for_timeout(750)
        body = page.locator('body').inner_text()
        ensure_rendered_page(body, 'wani-publisher')
        if urlparse(page.url).hostname != HOST:
            raise ValueError('Publisher redirected off host')
        return body

    try:
        search, detail = browser.new_page(locale='ja-JP'), browser.new_page(locale='ja-JP')
        for name in names:
            query = searches[name]
            if query['status'] == 'public_search_exhausted':
                continue
            pending = query['pending']
            seen = set(query['seen'])
            save(checkpoint, state)
            while pending:
                # Retain this URL until its navigation and parsing succeed.
                url = pending[0]
                if url in seen:
                    pending.pop(0)
                    continue
                print('Publisher search:', url, flush=True)
                body = navigate(search, url)
                links = search.locator('a[href]').evaluate_all('els=>els.map(a=>({url:a.href,text:a.innerText.trim()||a.querySelector("img")?.alt||""}))')
                for link in links:
                    parsed = urlparse(link['url'])
                    if parsed.hostname != HOST:
                        continue
                    if parsed.path == '/event.php' and '写真集' in link['text']:
                        state['candidates'].setdefault(link['url'], link['text'])
                    elif parsed.path == '/category.php' and parse_qs(parsed.query).get('tag', [''])[0] == name and link['text'].isdigit():
                        if link['url'] != url and link['url'] not in seen and link['url'] not in pending:
                            pending.append(link['url'])
                pending.pop(0)
                seen.add(url)
                query['seen'].append(url)
                if url not in state['pages']:
                    state['pages'].append(url)
                query['status'] = 'running' if pending else 'public_search_exhausted'
                save(output / ('wani-search-' + str(len(state['pages'])) + '.json'),
                    dict(url=url, body=body, links=links, pending=pending.copy(), observedAt=iso_utc()))
                save(checkpoint, state)
            query['status'] = 'public_search_exhausted'
            save(checkpoint, state)
        for url in state['candidates']:
            if url in state['items'] or url in state['rejected']:
                continue
            try:
                print('Publisher detail:', url, flush=True)
                body = navigate(detail, url)
                title = detail.locator('h1').inner_text().strip()
                images = detail.locator('img[src]').evaluate_all('els=>els.map(e=>e.src)')
                book = parse_book(body, title, images, url, names)
                save(output / ('wani-detail-' + parse_qs(urlparse(url).query)['id'][0] + '.json'),
                    dict(url=url, body=body, title=title, images=images, observedAt=iso_utc()))
                if book:
                    state['items'][url] = book
                else:
                    state['rejected'][url] = 'Not a verified print photobook with this model and publisher ISBN/date'
                state['errors'].pop(url, None)
            except Exception as exc:
                state['errors'][url] = f'{type(exc).__name__}: {exc}'
            finally:
                save(checkpoint, state)
        state['errors'] = {url: error for url, error in state['errors'].items()
            if url not in state['items'] and url not in state['rejected']}
        state['status'] = 'detail_failures' if state['errors'] else 'public_search_exhausted'
    except Exception as exc:
        state.update(status='source_failed', error=f'{type(exc).__name__}: {exc}')
    finally:
        browser.close()
        save(checkpoint, state)
        bibliography = output / 'physical-books.json'
        previous = json.loads(bibliography.read_text(encoding='utf-8')) if bibliography.exists() else dict(musecardsPersonId=person['id'], books=[])
        books = {book['id']: book for book in previous['books']}
        for book in state['items'].values():
            books.setdefault(book['id'], book)
        previous['books'] = list(books.values())
        save(bibliography, previous)
        print('Publisher print editions:', len(state['items']), state['status'], flush=True)


if __name__ == '__main__':
    main()
