"""Recognize source warning assets and select product-specific cover metadata."""
import json
import hashlib
import re
from urllib.parse import urlsplit

# SHA-256 of Kingstone's generic lock/18+ warning asset. Its R2 mirror
# must be rejected as well as the original retailer URL.
WARNING_IMAGE_HASHES = {'3c1ce976516c44566b414484ce00a85bd0da127555d7d9ff3e115c34816583c5'}


def validate_cover_url(url):
    parsed = urlsplit(url)
    if parsed.path.rsplit('/', 1)[-1].split('.')[0] in WARNING_IMAGE_HASHES:
        raise ValueError('Mirrored warning image is not an edition cover')
    if parsed.hostname == 'cdn.kingstone.com.tw' and parsed.path.casefold() == '/images/restricted.jpg':
        raise ValueError('Generic restricted-content placeholder is not an edition cover')
    if parsed.hostname == 'taiwan-image.bookwalker.com.tw' and re.search(r'_mask\.[a-z]+$', parsed.path, re.I):
        raise ValueError('BOOKWALKER age-warning mask is not an edition cover')


def validate_cover_bytes(data):
    if hashlib.sha256(data).hexdigest() in WARNING_IMAGE_HASHES:
        raise ValueError('Generic warning-image content is not an edition cover')


def select_cover_url(*candidates):
    """Prefer available product metadata, skipping known warning assets."""
    for candidate in candidates:
        if not candidate:
            continue
        try:
            validate_cover_url(candidate)
            return candidate
        except ValueError:
            continue
    return ''


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
