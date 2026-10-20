"""Decide whether a store product title names a model.

Store searches for a short name (もも, 葵, 七海, こころ...) return books by other
people whose names contain it (藤田もも, 萌木七海). Only a title that names the
model should credit the model; everything else stays an unlinked offer for
review. Mirrors classifyTitle in backend/cmd/people-merge/audit.go.

Classes:
  named  - a name of three or more characters (or a full Latin name) stands alone
  weak   - only a short name or single-word alias stands alone
  other  - the short name only appears inside a longer name, which is returned
  absent - no name of the model appears
"""
import unicodedata

PARTICLES = set('のとがはをにもやで')


def _is_han(ch):
    return 'CJK UNIFIED IDEOGRAPH' in unicodedata.name(ch, '') or ch in '々〆'


def _is_hiragana(ch):
    return 'ぁ' <= ch <= 'ゖ'


def _is_kana(ch):
    return ('ぁ' <= ch <= 'ゖ' or 'ァ' <= ch <= 'ヺ') and ch != 'ー'


def _is_surname_char(ch):
    return _is_han(ch) or ch in 'ノヶケ'


def _is_ascii_word(ch):
    return ch.isascii() and ch.isalnum()


def normalize(value):
    return unicodedata.normalize('NFKC', value or '').lower()


def is_short_name(name):
    """A given name or single word: Han up to two characters, kana-only names,
    and single-word Latin names."""
    text = normalize(name).strip()
    if any(ch.isascii() and ch.isalpha() for ch in text):
        return ' ' not in text
    han = sum(1 for ch in text if _is_han(ch))
    kana = sum(1 for ch in text if _is_kana(ch) or ch == 'ー')
    return (han > 0 and kana == 0 and len(text) <= 2) or (han == 0 and kana > 0 and len(text) <= 4)


def classify_title(title, names):
    """Return (class, proposed_name) for how a title relates to a model's names."""
    original = unicodedata.normalize('NFKC', title or '')
    text = original.lower()
    if len(text) != len(original):
        original = text
    best, proposed = 'absent', ''
    for name in names:
        needle = normalize(name).strip()
        if not needle:
            continue
        short = is_short_name(name)
        start = text.find(needle)
        while start >= 0:
            end = start + len(needle)
            before = text[start - 1] if start > 0 else ''
            after = text[end] if end < len(text) else ''
            inside_word = (_is_ascii_word(needle[0]) and before and _is_ascii_word(before)) or \
                (_is_ascii_word(needle[-1]) and after and _is_ascii_word(after))
            if not inside_word:
                if not short:
                    return 'named', ''
                if before and _is_surname_char(before):
                    if best == 'other':
                        start = text.find(needle, start + 1)
                        continue
                    first = start
                    while first > 0 and start - first < 4 and _is_surname_char(text[first - 1]):
                        first -= 1
                    best, proposed = 'other', original[first:end]
                elif _is_han(needle[-1]) and after and _is_hiragana(after) and after not in PARTICLES:
                    last = end
                    while last < len(text) and last - end < 4 and _is_hiragana(text[last]):
                        last += 1
                    if last - end >= 2 and best != 'other':
                        best, proposed = 'other', original[start:last]
                elif best == 'absent':
                    best = 'weak'
            start = text.find(needle, start + 1)
    return best, proposed


def model_names(model):
    return [name for name in dict.fromkeys([model.get('canonical_public_name'), model.get('original_name'),
            model.get('english_name'), *model.get('aliases', [])]) if name]


def credits_model(title, model):
    """True only when the title names the model itself."""
    return classify_title(title, model_names(model))[0] == 'named'
