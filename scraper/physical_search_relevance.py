"""Bound broad marketplace fallback pagination with explicit relevance state."""
import json
import re
from pathlib import Path


IRRELEVANT_PAGE_LIMIT = 5
PHOTOBOOK_TITLE_RE = re.compile(
    r"写真集|フォトブック|photobook|photo\s*book|leap|fly\s*high|grace|fish|maganda|love.{0,8}peace|奇跡の|grafan|肉食女子部|グラドル.{0,4}ベスト",
    re.I,
)


def has_photobook_title_signal(title):
    return bool(PHOTOBOOK_TITLE_RE.search(title or ""))


def matching_candidate_count(candidates, names, subject_matches, title_exclusion):
    """Count cards that meet the collector's model and photobook title rules."""
    request = {"humanModelKeywords": names}
    count = 0
    for candidate in candidates:
        title = candidate.get("title") or candidate.get("text") or ""
        if has_photobook_title_signal(title) and not title_exclusion(title) and subject_matches(request, title):
            count += 1
    return count


def trailing_irrelevant_page_count(run, output_dir, count_matches):
    """Recover the current no-match streak from retained page evidence."""
    streak = 0
    for batch in reversed(run.get("batches", [])):
        filename = batch.get("file")
        if not filename:
            break
        path = Path(output_dir) / filename
        if not path.is_file():
            break
        try:
            evidence = json.loads(path.read_text(encoding="utf-8")).get("candidateEvidence")
        except (OSError, json.JSONDecodeError):
            break
        if evidence is None:
            break
        if count_matches(evidence):
            break
        streak += 1
    return streak


def next_irrelevant_page_count(previous, matching_candidates):
    return 0 if matching_candidates else previous + 1
