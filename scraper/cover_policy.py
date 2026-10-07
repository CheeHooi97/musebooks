"""Recognize source warning assets and select product-specific cover metadata."""
import json
import re
from urllib.parse import urlsplit


def validate_cover_url(url):
    parsed = urlsplit(url)
    if parsed.hostname == 'cdn.kingstone.com.tw' and parsed.path.casefold() == '/images/restricted.jpg':
        raise ValueError('Generic restricted-content placeholder is not an edition cover')
    if parsed.hostname == 'taiwan-image.bookwalker.com.tw' and re.search(r'_mask\.[a-z]+$', parsed.path, re.I):
        raise ValueError('BOOKWALKER age-warning mask is not an edition cover')


def bookwalker_product_cover(data_page, product_url):
    """Use the selected product's published image, never guess an unmasked URL."""
    try:
        product_id = re.fullmatch(r'/product/(\d+)/?', urlsplit(product_url).path).group(1)
        data = json.loads(data_page)['props']['productData']
        image = data['product_image']
        parsed = urlsplit(image)
        if (parsed.scheme != 'https' or parsed.hostname != 'taiwan-image.bookwalker.com.tw'
                or not parsed.path.startswith('/product/' + product_id + '/')
                or parsed.username or parsed.password):
            return ''
        validate_cover_url(image)
        return image
    except (ValueError, TypeError, KeyError, AttributeError):
        return ''
