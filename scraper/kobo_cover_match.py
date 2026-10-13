"""Match a Kobo cover label to its verified selected product title."""
import re
import unicodedata
from urllib.parse import urlparse

TRAILING_GROUP = re.compile(r'\s*(?:\([^()]*\)|（[^（）]*）|\[[^\[\]]*\]|［[^［］]*］|【[^【】]*】)\s*$')


def key(value):
    return ''.join(char for char in unicodedata.normalize('NFKC', value or '').casefold() if char.isalnum())


def without_trailing_groups(value):
    value = value.strip()
    while match := TRAILING_GROUP.search(value):
        value = value[:match.start()].rstrip()
    return value


def selected_cover_images(images, title):
    title_key = key(without_trailing_groups(title))
    title_keys = [title_key]
    # Rakuten image metadata can replace the leading circled "secret" mark
    # (㊙) with a question mark, which key() removes. Try the title without
    # that single decorative marker as well.
    if title_key.startswith('秘') and len(title_key) > 6:
        title_keys.append(title_key[1:])
    if len(title_key) < 6:
        # Short titles are too ambiguous for partial matching. Accept only an
        # exact product-image label from Kobo's own cover host and directory.
        # The first page-ordered exact image is the product hero; later exact
        # labels can belong to recommended books by the same person.
        exact_matches = list(dict.fromkeys(
            image.get('url', '') for image in images
            if urlparse(image.get('url', '')).hostname in {'shop.r10s.jp', 'tshop.r10s.jp', 'thumbnail.image.rakuten.co.jp'}
            and '/rakutenkobo-ebooks/cabinet/' in urlparse(image.get('url', '')).path
            and key(without_trailing_groups(image.get('alt', ''))) == title_key
        ))
        return exact_matches[:1]
    matches = []
    for image in images:
        url, alt = image.get('url', ''), image.get('alt', '')
        parsed = urlparse(url)
        # Kobo image alts often append the same publisher/format suffix that
        # appears in the selected listing title. Strip it before matching.
        label_key = key(without_trailing_groups(alt))
        if parsed.hostname not in {'shop.r10s.jp', 'tshop.r10s.jp', 'thumbnail.image.rakuten.co.jp'}:
            continue
        if '/rakutenkobo-ebooks/cabinet/' not in parsed.path or not label_key:
            continue
        # Kobo adds publisher, imprint and format after the product's short
        # cover title. Allow that suffix, while requiring most of the selected
        # title to be present so a related recommendation cannot be selected.
        if any(
            (candidate.startswith(label_key) and len(label_key) / len(candidate) >= 0.55)
            or (label_key.startswith(candidate) and len(candidate) / len(label_key) >= 0.55)
            for candidate in title_keys
        ):
            matches.append(url)
    return list(dict.fromkeys(matches))
