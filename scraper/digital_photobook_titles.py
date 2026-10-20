"""Distinguish standalone branded digital photobooks from whole magazines."""
import re
import unicodedata

from photobook_title_rules import photobook_title_exclusion

MAGAZINE_REASONS = {'magazine_only', 'magazine_or_supplement'}
BRANDS = re.compile(r'週刊現代|週刊プレイボーイ|EX大衆|漫画アクション')


def digital_title_exclusion(title):
    reason = photobook_title_exclusion(title)
    normalized = unicodedata.normalize('NFKC', title)
    explicit = 'デジタル写真集' in normalized or ('グラビアン魂' in normalized and '写真集' in normalized)
    if reason not in MAGAZINE_REASONS or not explicit:
        return reason
    if re.search(r'(?:デジタル|ミニ)写真集(?:付き|付属)|(?:付録|特典).{0,12}(?:デジタル)?写真集|雑誌', normalized):
        return reason
    # Remove only the brand. Recheck every other exclusion so an early
    # magazine match cannot hide junior, illustrated or synthetic content.
    return photobook_title_exclusion(BRANDS.sub('', normalized))


def pending_title_reviews(state):
    pending = []
    for url, reason in state.get('rejected', {}).items():
        if reason not in MAGAZINE_REASONS:
            continue
        candidate = state.get('candidates', {}).get(url, '')
        title = candidate.get('title', '') if isinstance(candidate, dict) else candidate
        if title and not digital_title_exclusion(title):
            pending.append(url)
    return pending


def reopen_title_reviews(state):
    for url in pending_title_reviews(state):
        if url not in state.get('items', {}):
            state.setdefault('previouslyRejected', {})[url] = state['rejected'].pop(url)
