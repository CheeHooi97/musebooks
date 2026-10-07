"""Public Taiwan digital storefront URL rules and selected book metadata.

No network clients live here. Callers supply rendered pages and JSON-LD.
Mixed retailers require product-local ebook evidence before accepting prices.
"""
import json
import re
from urllib.parse import parse_qsl, urlencode, urlparse

EXTRA_DIGITAL_SOURCES = frozenset({
    'hami-tw', 'google-play-books-tw', 'apple-books-tw', 'hyread-tw',
    'momo-books-tw', 'pchome-books-tw', 'yahoo-shopping-books-tw',
    'kingstone-books-tw', 'taaze-books-tw', 'sanmin-books-tw', 'apple-books-us',
    'rakuten-kobo-tw', 'fan520-tw',
})
MIXED_DIGITAL_SOURCES = frozenset({'momo-books-tw', 'pchome-books-tw', 'yahoo-shopping-books-tw', 'books-com-tw', 'kingstone-books-tw', 'taaze-books-tw', 'sanmin-books-tw'})

def result_id(source_id, url):
    parsed = urlparse(url)
    host = parsed.hostname
    path = parsed.path
    query = dict(parse_qsl(parsed.query))
    patterns = {
        'hami-tw': ('www.hamibook.com.tw', r'/book/(\d+)/?'),
        'apple-books-tw': ('books.apple.com', r'/tw/book/(?:[^/]+/)?id(\d+)/?'),
        'apple-books-us': ('books.apple.com', r'/us/book/(?:[^/]+/)?id(\d+)/?'),
        'pchome-books-tw': ('24h.pchome.com.tw', r'/(?:books/)?prod/([A-Z0-9-]+)/?'),
        'yahoo-shopping-books-tw': ('tw.buy.yahoo.com', r'/gdsale/(?:[^/]+-)?(\d+)\.html'),
        'kingstone-books-tw': ('www.kingstone.com.tw', r'/basic/(\d+)/?'),
        'sanmin-books-tw': ('www.sanmin.com.tw', r'/product/index/(\d+)/?'),
        'rakuten-kobo-tw': ('www.rakuten.com.tw', r'/shop/kobo/product/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/?'),
        'fan520-tw': ('www.fan520.net', r'/products/([A-Za-z0-9-]+)/?'),
    }
    if source_id in patterns:
        expected, pattern = patterns[source_id]
        match = re.fullmatch(pattern, path)
        return match.group(1) if host == expected and match else ''
    if source_id == 'google-play-books-tw' and host == 'play.google.com' and re.fullmatch(r'/store/books/details(?:/[^/]+)?', path) and query.get('gl', 'TW').upper() == 'TW':
        return query.get('id', '') if re.fullmatch(r'[A-Za-z0-9_-]+', query.get('id', '')) else ''
    if source_id == 'hyread-tw' and host == 'ebook.hyread.com.tw' and path == '/bookDetail.jsp':
        return query.get('id', '') if query.get('id', '').isdigit() else ''
    if source_id == 'momo-books-tw' and host in {'www.momoshop.com.tw', 'm.momoshop.com.tw'}:
        match = re.fullmatch(r'/product/(\d+)/?', path)
        if match:
            return match.group(1)
        if path in {'/goods/GoodsDetail.jsp', '/goods.momo'} and query.get('i_code', '').isdigit():
            return query['i_code']
    if source_id == 'taaze-books-tw' and host == 'm.taaze.tw' and path == '/do/mobile/single.aspx':
        return query.get('pid', '') if query.get('pid', '').isdigit() else ''
    if source_id == 'taaze-books-tw' and host == 'www.taaze.tw':
        match = re.fullmatch(r'/products/(\d+)\.html', path)
        return match.group(1) if match else ''
    return ''

def canonical_url(source_id, url):
    identity = result_id(source_id, url)
    if not identity:
        return url
    bases = {
        'hami-tw': f'https://www.hamibook.com.tw/book/{identity}',
        'google-play-books-tw': 'https://play.google.com/store/books/details?' + urlencode({'id': identity, 'hl': 'zh_TW', 'gl': 'TW'}),
        'apple-books-tw': f'https://books.apple.com/tw/book/id{identity}',
        'apple-books-us': f'https://books.apple.com/us/book/id{identity}',
        'hyread-tw': f'https://ebook.hyread.com.tw/bookDetail.jsp?id={identity}',
        'momo-books-tw': f'https://www.momoshop.com.tw/product/{identity}',
        'pchome-books-tw': f'https://24h.pchome.com.tw/books/prod/{identity}',
        'kingstone-books-tw': f'https://www.kingstone.com.tw/basic/{identity}/',
        'taaze-books-tw': f'https://m.taaze.tw/do/mobile/single.aspx?pid={identity}',
        'sanmin-books-tw': f'https://www.sanmin.com.tw/product/index/{identity}',
        'rakuten-kobo-tw': f'https://www.rakuten.com.tw/shop/kobo/product/{identity}/',
        'fan520-tw': f'https://www.fan520.net/products/{identity}',
    }
    return bases.get(source_id, 'https://' + urlparse(url).hostname + urlparse(url).path)

def name_text(value):
    if isinstance(value, dict):
        return str(value.get('name') or '')
    if isinstance(value, list):
        return ' '.join(name_text(item) for item in value)
    return str(value or '')

def selected_book_schema(payloads):
    """Read Google's nested book offer and momo's variant offer, never related books."""
    for payload in payloads:
        try:
            value = json.loads(payload)
        except (ValueError, TypeError):
            continue
        roots = value if isinstance(value, list) else [value]
        for root in roots:
            if not isinstance(root, dict):
                continue
            graph = root.get('@graph', [root])
            if not isinstance(graph, list):
                continue
            for book in graph:
                if not isinstance(book, dict):
                    continue
                kind = book.get('@type')
                kinds = kind if isinstance(kind, list) else [kind]
                if not any(kind in ('Book', 'Product', 'ProductGroup') for kind in kinds):
                    continue
                example = book.get('workExample') or {}
                if isinstance(example, list):
                    example = example[0] if example else {}
                if not isinstance(example, dict):
                    example = {}
                # Books.com.tw nests the selected ebook one additional level.
                if isinstance(example, dict) and isinstance(example.get('workExample'), dict):
                    example = example['workExample']
                action = example.get('potentialAction') or {}
                if not isinstance(action, dict):
                    action = {}
                offers = book.get('offers') or action.get('expectsAcceptanceOf') or {}
                variants = book.get('hasVariant') or []
                if not offers and isinstance(variants, list) and variants and isinstance(variants[0], dict):
                    offers = variants[0].get('offers') or {}
                if isinstance(offers, list):
                    offers = offers[0] if offers else {}
                if not isinstance(offers, dict):
                    offers = {}
                properties = book.get('additionalProperty') or []
                if isinstance(properties, dict):
                    properties = [properties]
                if not isinstance(properties, list):
                    properties = []
                props = {item.get('name'): item.get('value') for item in properties if isinstance(item, dict)}
                result = {key: book.get(key) for key in ('name', 'description', 'image', 'isbn', 'category') if book.get(key)}
                isbn = str(book.get('isbn') or example.get('isbn') or props.get('ISBN') or '')
                isbn = re.sub(r'[^0-9Xx]', '', isbn)
                if len(isbn) != 13 or not isbn.startswith(('978', '979')):
                    isbn = ''
                result.update(author=name_text(book.get('author')), publisher=name_text(book.get('publisher') or props.get('出版社')),
                              isbn=isbn,
                              bookFormat=example.get('bookFormat') or book.get('bookFormat') or props.get('類型') or '')
                if offers:
                    result.update(price=offers.get('price'), currency=offers.get('priceCurrency'), availability=offers.get('availability'))
                    result = {key: re.sub(r'\\u([0-9a-fA-F]{4})', lambda match: chr(int(match.group(1), 16)), value) if isinstance(value, str) else value for key, value in result.items()}
                    return result
                # Book node without offers carries authors/ISBN (Hami graph).
                # Continue to its Product node, merging its selected metadata.
                if result:
                    for product in graph:
                        if isinstance(product, dict) and product.get('@type') == 'Product' and isinstance(product.get('offers'), dict):
                            offer = product['offers']
                            result.update(price=offer.get('price'), currency=offer.get('priceCurrency'), availability=offer.get('availability'))
                            return result
    return {}
