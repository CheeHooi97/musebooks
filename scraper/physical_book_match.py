"""Conservative associations between resale offers and a reviewed print bibliography."""
import re
import unicodedata


def normalized(value):
    return re.sub(r'\s+', '', unicodedata.normalize('NFKC', value or '')).casefold()


def match_physical_book(item, bibliography):
    if item.get('format') != 'physical' or re.search(r'セット|まとめ|\d+冊', item.get('title', '')):
        return None, None
    isbn = re.sub(r'[^0-9X]', '', str(item.get('isbn') or ''), flags=re.I)
    if isbn:
        matches = [book for book in bibliography if isbn == re.sub(r'[^0-9X]', '', book.get('isbn', ''), flags=re.I)]
        return (matches[0], 'reviewed_publisher_isbn_physical') if len(matches) == 1 else (None, None)
    title = unicodedata.normalize('NFKC', item.get('title', '')).casefold()
    matches = []
    for book in bibliography:
        alias = unicodedata.normalize('NFKC', book['titleAlias']).strip().casefold()
        if re.fullmatch(r'[a-z]{1,5}', alias):
            # A short title such as "Asuka" also appears in the model's English
            # name and other book titles. Require explicit book-title context.
            token = re.escape(alias)
            quoted = re.search(r'[『「"\']\s*' + token + r'\s*[』」"\']', title)
            labelled = re.search(r'写真集\s*[『「"\']?\s*' + token + r'\s*(?:[』」"\']|$)|^' + token + r'\s*写真集', title)
            if quoted or labelled:
                matches.append(book)
        elif normalized(alias) in normalized(title):
            matches.append(book)
    return (matches[0], 'reviewed_model_title_physical') if len(matches) == 1 else (None, None)
