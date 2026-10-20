"""Build a deduplicated listing gallery from normalized and detail evidence."""
from urllib.parse import urlsplit


def _image_urls(value):
    if isinstance(value, str):
        url = value.strip()
        return [url] if url else []
    if isinstance(value, (list, tuple)):
        return [url for entry in value for url in _image_urls(entry)]
    if isinstance(value, dict):
        urls = []
        for key in ('url', 'contentUrl', '@id'):
            urls.extend(_image_urls(value.get(key)))
        return urls
    return []


def _image_key(url):
    parts = urlsplit(url)
    host = (parts.hostname or '').lower()
    path = parts.path
    if host == 'auc-pctr.c.yimg.jp' and path.startswith('/i/'):
        original = path[len('/i/'):]
        _original_host, separator, original_path = original.partition('/')
        if separator:
            return ('yahoo-image', '/' + original_path)
    if host.endswith('.yimg.jp'):
        return ('yahoo-image', path)
    return (host, path, parts.query)


def _image_quality(url):
    """Prefer a source image over a resized Yahoo thumbnail for one photo."""
    parts = urlsplit(url)
    return 0 if (parts.hostname or '').lower() == 'auc-pctr.c.yimg.jp' else 1


def listing_image_urls(item, detail=None):
    """Return secure gallery URLs with the listing cover first."""
    item = item if isinstance(item, dict) else {}
    detail = detail if isinstance(detail, dict) else {}
    metadata = detail.get('metadata') if isinstance(detail.get('metadata'), dict) else {}
    structured = detail.get('structured') if isinstance(detail.get('structured'), dict) else {}
    values = [item.get('imageUrl'), item.get('imageUrls'), detail.get('imageUrl'),
        metadata.get('image'), structured.get('image')]
    result = []
    positions = {}
    qualities = []
    for value in values:
        for url in _image_urls(value):
            if urlsplit(url).scheme.lower() != 'https':
                continue
            key = _image_key(url)
            quality = _image_quality(url)
            if key in positions:
                index = positions[key]
                if quality > qualities[index]:
                    result[index] = url
                    qualities[index] = quality
                continue
            positions[key] = len(result)
            result.append(url)
            qualities.append(quality)
    return result
