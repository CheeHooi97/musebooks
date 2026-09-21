"""Unified CloakBrowser worker for catalog discovery, checklists, and media.

The Go adapters select an operation (``discovery``, ``checklist``, or ``media``)
and retain their original flat JSON response contracts. Requests without an
operation use the combined pipeline and return enriched releases.
"""

from __future__ import annotations

import io
import os
import json
import hashlib
import re
import sys
import unicodedata
from contextlib import contextmanager, redirect_stdout
from datetime import date, datetime
from html.parser import HTMLParser
from typing import Any
from urllib.parse import unquote, urlencode, urljoin, urlparse
from urllib.request import Request, urlopen

from cloakbrowser import launch


DEFAULT_BROWSER_LAUNCH_TIMEOUT_MS = 90_000


def browser_launch_timeout_ms() -> int:
    """Return a bounded Playwright startup timeout for the catalog browser."""
    raw_value = os.environ.get("CLOAKBROWSER_LAUNCH_TIMEOUT_MS", "").strip()
    try:
        value = int(raw_value) if raw_value else DEFAULT_BROWSER_LAUNCH_TIMEOUT_MS
    except ValueError:
        value = DEFAULT_BROWSER_LAUNCH_TIMEOUT_MS
    return max(1_000, min(value, 300_000))


@contextmanager
def browser_launch_lock():
    """Serialize Chromium startup across workers sharing this service host."""
    if os.name != "posix":
        yield
        return

    import fcntl

    lock_path = (
        os.environ.get("CLOAKBROWSER_LAUNCH_LOCK_PATH", "").strip()
        or "/tmp/musecards-cloakbrowser-launch.lock"
    )
    lock_directory = os.path.dirname(lock_path)
    if lock_directory:
        os.makedirs(lock_directory, exist_ok=True)
    with open(lock_path, "a+", encoding="utf-8") as lock_file:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


PROGRESS_LOG_PATH = os.environ.get(
    "CATALOG_WORKER_PROGRESS_LOG",
    "/opt/gravure-model/logs/catalog-worker-progress.log",
)


def progress(message: str) -> None:
    """Write progress without touching stdout/stderr JSON contracts."""
    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    line = f"{timestamp} {message}\n"
    try:
        directory = os.path.dirname(PROGRESS_LOG_PATH)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(PROGRESS_LOG_PATH, "a", encoding="utf-8") as handle:
            handle.write(line)
            handle.flush()
    except Exception:
        pass

DATE_PATTERN = re.compile(r"(20\d{2})\s*(?:年|[-/.])\s*(\d{1,2})(?:\s*(?:月|[-/.])\s*(\d{1,2})\s*(?:日)?)?")


ANSI_ESCAPE_PATTERN = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")

CLOAKBROWSER_INFO_PATTERNS = (
    re.compile(
        r"^Update available:\s*cloakbrowser\s+\S+\s*[→>-]+\s*\S+\.?"
        r"(?:\s+Run:\s*pip\s+install\s+--upgrade\s+cloakbrowser\s*)?$",
        re.I,
    ),
    re.compile(r"^Run:\s*pip\s+install\s+--upgrade\s+cloakbrowser\s*$", re.I),
)


class FilteredStderr(io.TextIOBase):
    """Forward worker diagnostics while dropping CloakBrowser update notices.

    The Go adapter treats any stderr output as a failed worker invocation.
    CloakBrowser prints version-update notices to stdout, which this worker
    redirects to stderr to protect the JSON stdout contract.  Buffer complete
    lines so only those known informational notices are suppressed.
    """

    def __init__(self, target):
        self.target = target
        self._buffer = ""

    @property
    def encoding(self):
        return getattr(self.target, "encoding", "utf-8")

    def writable(self):
        return True

    def write(self, value):
        text = str(value or "")
        self._buffer += text
        while "\n" in self._buffer:
            line, self._buffer = self._buffer.split("\n", 1)
            self._emit(line, newline=True)
        return len(text)

    def flush(self):
        if self._buffer:
            self._emit(self._buffer, newline=False)
            self._buffer = ""
        self.target.flush()

    def _emit(self, line: str, newline: bool):
        stripped = ANSI_ESCAPE_PATTERN.sub("", line).strip()
        lowered = stripped.lower()
        if (
            stripped
            and (
                any(pattern.match(stripped) for pattern in CLOAKBROWSER_INFO_PATTERNS)
                or ("update available:" in lowered and "cloakbrowser" in lowered)
                or ("pip install --upgrade" in lowered and "cloakbrowser" in lowered)
            )
        ):
            return
        self.target.write(line + ("\n" if newline else ""))




JUICY_RELEASE_REQUIRED_MARKERS = (
    "発売", "発売決定", "発売予定", "予約開始", "予約受付", "新発売",
    "販売開始", "先着販売", "抽選販売", "release", "on sale",
)

JUICY_ANCILLARY_MARKERS = (
    "直筆メッセージ", "直筆サイン", "サインカード", "レアカード",
    "カード画像", "全カード", "表面", "裏面", "特典カード",
    "ボックス特典", "イベント", "キャンペーン", "プレゼント",
    "開封", "チェックリスト", "フライヤー", "撮影", "オフショット",
    "追加情報", "訂正", "お知らせ", "通販", "通信販売", "シングルカード",
    "誤表記",
)


# Some historical releases only remain discoverable through official restock
# notices that name several products in one headline.  A shared article cannot
# safely attribute its cast or date to any one release, so retain the small set
# of independently verified facts needed to hydrate those exact identities.
# The source URL is additional evidence; the discovered official article stays
# the primary source URL so existing database rows reconcile by their slug.
JUICY_VERIFIED_RELEASE_METADATA = {
    # The legacy numbered releases are frequently mentioned only in later
    # stock notices.  Keep their original release facts here so a mixed notice
    # cannot make every release inherit the notice's date (or leave the cast
    # empty when the original post is no longer linked by the archive).
    "volume:26": {
        "releaseDate": "2014-04-26",
        "modelNames": ["由愛可奈", "希崎ジェシカ", "紗倉まな"],
        "sourceUrl": "https://fs.xcity.jp/aja/archives/free/juicyhoney/backnumber.html",
    },
    "volume:24": {
        "releaseDate": "2013-11-23",
        "modelNames": ["さとう遥希", "つぼみ", "上原亜衣"],
        "sourceUrl": "https://fs.xcity.jp/aja/archives/free/juicyhoney/backnumber.html",
    },
    "volume:22": {
        "releaseDate": "2013-05-24",
        "modelNames": ["さとう遥希", "希崎ジェシカ", "瑠川リナ"],
        "sourceUrl": "https://fs.xcity.jp/aja/archives/free/juicyhoney/backnumber.html",
    },
    "volume:21": {
        "releaseDate": "2013-03-23",
        "modelNames": ["成瀬心美", "紗倉まな", "ティア"],
        "sourceUrl": "https://fs.xcity.jp/aja/archives/free/juicyhoney/backnumber.html",
    },
    "volume:19": {
        "releaseDate": "2012-04-28",
        "modelNames": ["成瀬心美", "横山美雪", "星美りか"],
        "sourceUrl": "https://fs.xcity.jp/aja/archives/free/juicyhoney/backnumber.html",
    },
    "volume:14": {
        "releaseDate": "2010-09-25",
        "modelNames": ["つぼみ", "希志あいの", "明日花キララ"],
        "sourceUrl": "https://fs.xcity.jp/aja/archives/free/juicyhoney/backnumber.html",
    },
    "volume:13": {
        "releaseDate": "2010-07-10",
        "modelNames": ["並木優", "周防ゆきこ", "横山美雪"],
        "sourceUrl": "https://fs.xcity.jp/aja/archives/free/juicyhoney/backnumber.html",
    },
    "volume:12": {
        "releaseDate": "2010-02-13",
        "modelNames": ["天海つばさ", "大橋未久", "佳山三花"],
        "sourceUrl": "https://fs.xcity.jp/aja/archives/free/juicyhoney/backnumber.html",
    },
    "volume:9": {
        "releaseDate": "2008-08-09",
        "modelNames": ["みひろ", "小澤マリア", "七海なな", "黒木アリサ"],
        "sourceUrl": "https://fs.xcity.jp/aja/archives/free/juicyhoney/backnumber.html",
    },
    "volume:6": {
        "releaseDate": "2007-06-16",
        "modelNames": ["紅音ほたる", "麻美ゆま", "範田紗々", "涼果りん"],
        "sourceUrl": "https://fs.xcity.jp/aja/archives/free/juicyhoney/backnumber.html",
    },
    "volume:5": {
        "releaseDate": "2007-02-24",
        "modelNames": ["結城凛", "松嶋れいな", "安達真実", "北原多香子"],
        "sourceUrl": "https://fs.xcity.jp/aja/archives/free/juicyhoney/backnumber.html",
    },
    "volume:4": {
        "releaseDate": "2006-10-07",
        "modelNames": ["青木りん", "乙女奈々", "寧々", "工藤はつみ"],
        "sourceUrl": "https://fs.xcity.jp/aja/archives/free/juicyhoney/backnumber.html",
    },
    # The old catalogue labels this 2008 special edition as Premium Edition;
    # some blog imports expose it under the recurring Luxury Edition key.
    "luxury:2008:": {
        "releaseDate": "2008-12-20",
        "modelNames": ["麻美ゆま", "希志あいの", "ほしのみゆ"],
        "sourceUrl": "https://fs.xcity.jp/aja/archives/free/juicyhoney/backnumber.html",
    },
    # Some old notices call this THE DELUXE, while the generated row can carry
    # the shorter LUXURY label.  Hydrate both identities with the same facts.
    "luxury:2017:": {
        "releaseDate": "2017-07-01",
        "modelNames": ["桐谷まつり", "JULIA", "高橋しょう子", "佐倉絆"],
        "sourceUrl": "https://juicy-honey.blog.jp/archives/1066107472.html",
    },
    "plus:1": {
        "releaseDate": "2018-12-22",
        "modelNames": ["天使もえ", "希崎ジェシカ", "白石茉莉奈", "益坂美亜"],
        "sourceUrl": "https://juicy-honey.jp/?ca=112",
    },
    "plus:2": {
        "releaseDate": "2019-04-27",
        "modelNames": ["AIKA", "JULIA", "本庄鈴", "桃乃木かな"],
        "sourceUrl": "https://juicy-honey.jp/?ca=114",
    },
    "plus:3": {
        "releaseDate": "2019-06-29",
        "modelNames": ["篠田ゆう", "唯井まひろ", "橋本ありな", "波多野結衣"],
        "sourceUrl": "https://juicy-honey.jp/?ca=118",
    },
    "luxury:2019:": {
        "releaseDate": "2019-02-24",
        "modelNames": ["戸田真琴", "三上悠亜", "明日花キララ", "成宮りか"],
        "sourceUrl": "https://juicy-honey.blog.jp/archives/1073518535.html",
    },
    # Early official posts sometimes omitted "THE" from this product name.
    "deluxe:2019:": {
        "releaseDate": "2019-08-25",
        "modelNames": ["阿部乃みく", "紗倉まな", "高橋しょう子", "浜崎真緒"],
        "sourceUrl": "https://juicy-honey.blog.jp/archives/1074978912.html",
    },
    "the-deluxe:2019:": {
        "releaseDate": "2019-08-25",
        "modelNames": ["阿部乃みく", "紗倉まな", "高橋しょう子", "浜崎真緒"],
        "sourceUrl": "https://juicy-honey.blog.jp/archives/1074978912.html",
    },
}

JUICY_BROAD_ARTICLE_MARKERS = (
    "ジューシーハニー", "juicy honey", "jh plus", "jh vol",
    "luxury edition", "the luxury", "ラグジュアリー", "高級版",
    "the deluxe", "deluxe", "デラックス", "exquisite",
    "エクスクイジット", "anniversary", "annversary", "アニバーサリー",
)

JUICY_SERIES_PATTERNS = (
    (
        "plus",
        re.compile(
            r"(?:juicy\s*honey|ジューシーハニー|jh)?\s*"
            r"(?:collection\s*cards?\s*)?(?:plus|ＰＬＵＳ)"
            r"\s*(?:#|＃|vol(?:ume)?[.]?)?\s*(\d{1,3})",
            re.I,
        ),
    ),
    (
        "volume",
        re.compile(
            r"(?:juicy\s*honey|ジューシーハニー|jh)?\s*"
            r"(?:collection\s*cards?\s*)?"
            r"(?:vol(?:ume)?[.]?|ＶＯＬ[．.]?)\s*(\d{1,3})",
            re.I,
        ),
    ),
)


def compact_series_digits(value: str) -> str:
    """Join digits split by layout whitespace, e.g. ``VOL. 2 8`` -> ``VOL. 28``."""
    value = unicodedata.normalize("NFKC", clean_text(value))
    previous = None
    while previous != value:
        previous = value
        value = re.sub(r"(?<=\d)\s+(?=\d)", "", value)
    return value


def juicy_series_identity(text: str) -> tuple[str, int | None, str]:
    """Return canonical identity, numeric volume and display title.

    Special editions are checked before numbered editions. This is important
    because a Luxury/Deluxe article body can mention older PLUS/VOL products,
    which must not change the identity of the current article.
    """
    normalized = compact_series_digits(text)
    lowered = normalized.lower()

    special_series = (
        (
            ("the luxury", "the\u3000luxury", "the luxury edition"),
            "the-luxury",
            "JUICY HONEY THE LUXURY EDITION",
        ),
        (
            ("luxury edition", "luxury", "ラグジュアリーエディション", "ラグジュアリー"),
            "luxury",
            "JUICY HONEY LUXURY EDITION",
        ),
        (("the deluxe", "the\u3000deluxe"), "the-deluxe", "JUICY HONEY THE DELUXE"),
        (("deluxe", "デラックス"), "deluxe", "JUICY HONEY DELUXE"),
        (("exquisite", "エクスクイジット"), "exquisite", "JUICY HONEY EXQUISITE"),
        (("anniversary", "annversary", "アニバーサリー", "周年"), "anniversary", "JUICY HONEY ANNIVERSARY"),
    )

    for aliases, key, title in special_series:
        if not any(alias in lowered for alias in aliases):
            continue

        # The year is part of the identity because these editions recur.
        edition_year_match = re.search(r"\b(20\d{2})\b", normalized)
        edition_year = edition_year_match.group(1) if edition_year_match else "unknown"

        # Preserve a genuine named edition such as Duo Divas, but never use a
        # cast list, price, release wording, or product specification as it.
        descriptor = ""
        descriptor_patterns = (
            r"(?:the\s+luxury|luxury|ラグジュアリー)(?:\s+edition|\s*エディション)?\s*20\d{2}\s+([^|｜!！\n]{2,60})",
            r"(?:the\s+deluxe|deluxe|デラックス)\s*20\d{2}\s+([^|｜!！\n]{2,60})",
            r"(?:exquisite|エクスクイジット)\s*20\d{2}\s+([^|｜!！\n]{2,60})",
        )
        for pattern in descriptor_patterns:
            match = re.search(pattern, normalized, re.I)
            if not match:
                continue
            candidate = clean_text(match.group(1)).strip(" -~〜～'\"")
            if re.search(
                r"(?:発売|販売|予約|先着|抽選|box|pack|カード|card|女優|出演|"
                r"税込|税別|円|[＆&、,/]|\d+枚)",
                candidate,
                re.I,
            ):
                continue
            if 2 <= len(candidate) <= 40:
                descriptor = candidate
                break

        if key == "anniversary":
            ordinal_match = re.search(
                r"(?<!\d)(\d{1,2})(?:st|nd|rd|th)?\s*ann(?:i)?versary\b"
                r"|(?<!\d)(\d{1,2})\s*周年",
                normalized,
                re.I,
            )
            if ordinal_match:
                ordinal = int(ordinal_match.group(1) or ordinal_match.group(2))
                suffix = "TH"
                if ordinal % 100 not in {11, 12, 13}:
                    suffix = {1: "ST", 2: "ND", 3: "RD"}.get(ordinal % 10, "TH")
                identity = f"anniversary:{ordinal}:{edition_year}"
                return identity, None, f"JUICY HONEY {ordinal}{suffix} ANNIVERSARY"

        identity = f"{key}:{edition_year}:{normalize_text(descriptor)}"
        display = f"{title} {edition_year}" if edition_year != "unknown" else title
        if descriptor:
            display += f" {descriptor}"
        return identity, None, display

    for kind, pattern in JUICY_SERIES_PATTERNS:
        match = pattern.search(normalized)
        if not match:
            continue
        volume = int(match.group(1))
        if kind == "plus":
            return f"plus:{volume}", volume, f"JUICY HONEY PLUS #{volume}"
        return f"volume:{volume}", volume, f"JUICY HONEY VOL.{volume}"

    # Some early posts describe the standard line as 第○弾 without VOL.
    if re.search(r"(?:juicy\s*honey|ジューシーハニー)", normalized, re.I):
        generation = re.search(r"第\s*(\d{1,3})\s*弾", normalized)
        if generation:
            volume = int(generation.group(1))
            return f"volume:{volume}", volume, f"JUICY HONEY VOL.{volume}"

    return "", None, ""


def juicy_series_routing_key(identity: str) -> str:
    """Collapse historical display-name aliases used for image routing only."""
    parts = str(identity or "").split(":")
    if not parts:
        return ""
    kind = parts[0]
    if kind in {"luxury", "the-luxury"}:
        kind = "luxury"
    elif kind in {"deluxe", "the-deluxe"}:
        kind = "deluxe"
    return ":".join([kind, *parts[1:2]]) if len(parts) > 1 else kind


def juicy_series_identities(text: str) -> list[tuple[str, int | None, str]]:
    """Return every explicit Juicy Honey release named by a headline or image.

    Official stock notices sometimes use compact headlines such as
    ``[JH PLUS #9][#14][LX2018][DX2021]``. The older single-identity parser must
    remain conservative for ordinary article bodies, while this parser expands
    only explicit series tokens and OCR-tolerant card marks.
    """
    normalized = compact_series_digits(text)
    candidates: list[tuple[int, int, str, int | None, str]] = []

    def add(match: re.Match, identity: str, volume: int | None, title: str) -> None:
        candidates.append((match.start(), match.end(), identity, volume, title))

    for match in re.finditer(
        r"\b(?:JUICY\s+HONEY\s+)?(?:COLLECTION\s+CARDS?\s+)?(?:JH\s+)?"
        r"PLUS\s*(?:[#H*]\s*)?0*(\d{1,3})\b",
        normalized,
        re.I,
    ):
        volume = int(match.group(1))
        add(match, f"plus:{volume}", volume, f"JUICY HONEY PLUS #{volume}")

    for match in re.finditer(
        r"\b(?:JUICY\s+HONEY\s+)?(?:COLLECTION\s+CARDS?\s+)?(?:JH\s+)?"
        r"VOL(?:UME)?[.]?\s*0*(\d{1,3})\b",
        normalized,
        re.I,
    ):
        volume = int(match.group(1))
        add(match, f"volume:{volume}", volume, f"JUICY HONEY VOL.{volume}")

    special_patterns = (
        (r"\bLX\s*(20\d{2})\b", "luxury", "JUICY HONEY LUXURY EDITION"),
        (r"\bDX\s*(20\d{2})\b", "the-deluxe", "JUICY HONEY THE DELUXE"),
        (r"\bTHE\s+LUXURY(?:\s+EDITION)?\s*(20\d{2})\b", "the-luxury", "JUICY HONEY THE LUXURY EDITION"),
        (r"(?<!THE\s)\bLUXURY\s+EDITION\s*(20\d{2})\b", "luxury", "JUICY HONEY LUXURY EDITION"),
        (r"\bTHE\s+DELUXE\s*(20\d{2})\b", "the-deluxe", "JUICY HONEY THE DELUXE"),
        (r"(?<!THE\s)\bDELUXE\s*(20\d{2})\b", "deluxe", "JUICY HONEY DELUXE"),
        (r"\bEXQUISITE\s*(20\d{2})\b", "exquisite", "JUICY HONEY EXQUISITE"),
    )
    for pattern, kind, title in special_patterns:
        for match in re.finditer(pattern, normalized, re.I):
            year = match.group(1)
            add(match, f"{kind}:{year}:", None, f"{title} {year}")

    for match in re.finditer(
        r"(?<!\d)(\d{1,2})(?:ST|ND|RD|TH)?\s*ANN(?:I)?VERSARY\b",
        normalized,
        re.I,
    ):
        ordinal = int(match.group(1))
        suffix = "TH"
        if ordinal % 100 not in {11, 12, 13}:
            suffix = {1: "ST", 2: "ND", 3: "RD"}.get(ordinal % 10, "TH")
        nearby = normalized[match.start():match.end() + 16]
        year_match = re.search(r"\b(20\d{2})\b", nearby)
        year = year_match.group(1) if year_match else "unknown"
        add(match, f"anniversary:{ordinal}:{year}", None, f"JUICY HONEY {ordinal}{suffix} ANNIVERSARY")

    # A bracketed bare number inherits the nearest explicit PLUS/VOL marker.
    # Restricting this to brackets prevents card numbers and dates from becoming
    # accidental release identities.
    occupied = [(start, end) for start, end, *_ in candidates]
    for match in re.finditer(r"(?:\[|【)\s*#\s*0*(\d{1,3})\s*(?:\]|】)", normalized):
        if any(match.start() < end and match.end() > start for start, end in occupied):
            continue
        previous = [item for item in candidates if item[0] < match.start() and item[2].split(":", 1)[0] in {"plus", "volume"}]
        if not previous:
            continue
        kind = max(previous, key=lambda item: item[0])[2].split(":", 1)[0]
        volume = int(match.group(1))
        title = f"JUICY HONEY PLUS #{volume}" if kind == "plus" else f"JUICY HONEY VOL.{volume}"
        add(match, f"{kind}:{volume}", volume, title)

    candidates.sort(key=lambda item: item[0])
    result: list[tuple[str, int | None, str]] = []
    seen: set[str] = set()
    for _, _, identity, volume, title in candidates:
        if identity in seen:
            continue
        seen.add(identity)
        result.append((identity, volume, title))

    if len(result) == 1:
        single = juicy_series_identity(normalized)
        if single[0] and juicy_series_routing_key(single[0]) == juicy_series_routing_key(result[0][0]):
            return [single]
    if result:
        return result
    single = juicy_series_identity(normalized)
    return [single] if single[0] else []

def juicy_release_score(text: str) -> int:
    """Rank complete product pages above sales notices and preview posts."""
    normalized = compact_series_digits(text)
    lowered = normalized.lower()
    identity, _, _ = juicy_series_identity(normalized)
    if not identity:
        return -10000

    score = 100
    if any(marker.lower() in lowered for marker in JUICY_RELEASE_REQUIRED_MARKERS):
        score += 80
    if extract_juicy_release_date(normalized):
        score += 40
    # A dated product announcement is stronger evidence than a later
    # single-card sales/update article that merely repeats the volume number.
    if re.search(r"\d{1,2}\s*月\s*\d{1,2}\s*日\s*発売", normalized):
        score += 60
    if re.search(r"(?:商品構成|collect\s+all|upc|jan|発売元|販売元)", normalized, re.I):
        score += 80
    if re.search(r"(?:収録女優|profile|出演|featuring)", normalized, re.I):
        score += 30
    score -= 25 * sum(1 for marker in JUICY_ANCILLARY_MARKERS if marker.lower() in lowered)
    return score


def looks_like_juicy_article(text: str) -> bool:
    normalized = compact_series_digits(text).lower()
    return any(marker in normalized for marker in JUICY_BROAD_ARTICLE_MARKERS)


def looks_like_juicy_release_announcement(text: str) -> bool:
    normalized = compact_series_digits(text)
    identity, _, _ = juicy_series_identity(normalized)
    if not identity:
        return False
    lowered = normalized.lower()
    has_release_marker = any(marker.lower() in lowered for marker in JUICY_RELEASE_REQUIRED_MARKERS)
    ancillary_hits = sum(1 for marker in JUICY_ANCILLARY_MARKERS if marker.lower() in lowered)
    return ancillary_hits == 0 or has_release_marker


def normalize_juicy_title(text: str) -> str:
    _, _, canonical = juicy_series_identity(text)
    return canonical or clean_text(text)


JUICY_NON_MODEL_PATTERN = re.compile(
    r"(?:juicy|honey|ジューシー|ハニー|card|カード|トレカ|vol|plus|発売|予定|価格|"
    r"box|pack|edition|limited|profile|誕生日|星座|出身地|body|size|camera|カメラマン|"
    r"税込|税別|売価|希望小売|円|枚入り|パック|ボックス|カートン|jan|upc|code|"
    r"販売元|発売元|株式会社|限定生産|adult|only|収録|女優|新定番|第\d+弾|"
    r"twitter|instagram|wikipedia|facebook|website|image|date of birth|sign|height|"
    r"regular|insert|special|premium|autograph|photo|bra|lingerie|bikini|costume|"
    r"relationship|pending|official|information|detail|sample|preview|duo|trio|quartet|https?|"
    r"ご紹介|紹介いたします|お知らせ|ご案内|ください|受付|終了|通販ページ|"
    r"お客様|ご不便|一部店舗|公開|掲載|こちら|もちろん|こんにちは)",
    re.I,
)


def normalize_juicy_person_name(value: str) -> str:
    """Return one display name without phonetic/English profile suffixes."""
    name = unicodedata.normalize("NFKC", clean_text(value)).strip()
    name = re.sub(r"\s*[\[［][^\]］]+[\]］]\s*$", "", name)
    name = name.strip("!！?？~〜～()（）[]［］{}:：*-・")

    # Profile headings commonly use ``星乃莉子 RIKO HOSHINO [ホシノリコ]``.
    # The Japanese prefix is the canonical public name; the romanized suffix
    # belongs in englishName and must never become part of the person identity.
    japanese_prefix = re.match(
        r"^([ぁ-んァ-ヶ一-龯々〆ヵヶー]+(?:[\s　・･]+[ぁ-んァ-ヶ一-龯々〆ヵヶー]+)*)",
        name,
    )
    if japanese_prefix:
        return re.sub(r"[\s　]+", "", japanese_prefix.group(1))
    return name


def is_probable_juicy_model_name(value: str) -> bool:
    name = normalize_juicy_person_name(value)
    if not name or len(name) < 2 or len(name) > 35:
        return False
    lowered = name.lower()
    # These are common leftovers from profile/social markup, not performer
    # names. Keep these checks in Unicode form because the source blog mixes
    # Japanese punctuation and English labels.
    if re.search(r"[\u3002\uFF01\uFF1F!?]", name):
        return False
    if lowered in {
        "http", "https", "www", "duo", "trio", "quartet",
        "hello", "こんにちは", "model relationship pending",
    }:
        return False
    if re.search(r"(?:https?://|www[.]|(?:^|@)x[.]com|[.](?:com|net|org|jp)(?:$|/))", lowered):
        return False
    if JUICY_NON_MODEL_PATTERN.search(name):
        return False
    if re.search(r"\d", name):
        return False
    if re.search(r"[。！？!?]|(?:です|ます|ました|ません|ので|ため|へ)$", name):
        return False
    if name in {"金", "銀", "赤", "青", "白", "黒", "税別", "税込", "以上", "以下"}:
        return False
    if re.fullmatch(r"[ぁ-んァ-ヶ一-龯々〆ヵヶー・･]{2,20}", name):
        return True
    # Roman-only stage names must be known mononyms. Accepting arbitrary
    # alphabetic tokens turns English ordering text into fake people.
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{1,19}", name):
        return False
    return lowered in {
        "aika", "anri", "julia", "maria", "minamo", "miru",
        "rara", "rio", "rion", "yua",
    }


def _split_juicy_names(value: str) -> list[str]:
    value = unicodedata.normalize("NFKC", clean_text(value))
    value = re.sub(r"^(?:出演|featuring|収録女優|models?|cast)\s*[:：]?\s*", "", value, flags=re.I)
    value = re.sub(
        r"(?:プレミアム\s*)?(?:アダルトトレカ|セクシー女優トレカ|トレーディングカード).*$",
        "",
        value,
        flags=re.I,
    )
    value = re.sub(r"\s+[A-Z][A-Z .'-]{3,}(?:\s*\[[^\]]+\])?", " ", value)
    value = re.sub(r"\s*[\[［][^\]］]+[\]］]", " ", value)
    # Older sales articles describe the cast in prose, for example
    # ``通販ページは新着順ではなく、鈴村あいりさん→あやみ旬果さん→
    # 明日花キララさんの順に掲載``. Keep only the ordered names.
    value = re.sub(r"^.*?(?:通販ページ|通信販売ページ)[^、,，]*[、,，]\s*", "", value)
    value = re.sub(r"(?:の)?\s*\d+\s*名\s*(?:収録|出演|登場).*$", "", value)
    value = re.sub(r"(?:の)?\s*順(?:に|で|へ).*$", "", value)
    value = re.sub(
        r"(?:ちゃん|さん)(?=\s*(?:と|、|,|，|＆|&|／|/|・|→|$))",
        "",
        value,
    )

    parts = re.split(r"\s*(?:と|＆|&|、|,|，|／|/|・|→|\band\b)\s*|\s{2,}", value, flags=re.I)
    if len(parts) == 1:
        tokens = [token for token in value.split() if token]
        if 2 <= len(tokens) <= 10:
            parts = tokens

    names: list[str] = []
    for part in parts:
        name = normalize_juicy_person_name(part)
        if not is_probable_juicy_model_name(name):
            continue
        if name not in names:
            names.append(name)
    return names


def juicy_model_names(*values: Any) -> list[str]:
    """Return distinct performers, never product text or specification rows."""
    names: list[str] = []
    for value in values:
        candidates = value if isinstance(value, (list, tuple, set)) else [value]
        for candidate in candidates:
            for name in _split_juicy_names(str(candidate or "")):
                if name not in names:
                    names.append(name)
    return names


def merge_model_names(*values: Any) -> str:
    """Legacy display value; database importers should use modelNames."""
    return " / ".join(juicy_model_names(*values))


def extract_juicy_model_names(text: str) -> list[str]:
    """Extract the complete Juicy Honey performer list from official text.

    The official blog repeats the cast in several reliable structures:
      * the line immediately after the AVC/JUICY HONEY product name;
      * the article headline after the canonical series title;
      * the ``収録女優Profile`` section, where each performer name appears
        immediately before a birthday/profile block.

    Marketing prose, prices, card names, lottery notices and product
    specifications are deliberately ignored.
    """
    normalized = unicodedata.normalize("NFKC", str(text or ""))
    lines = [clean_text(line) for line in normalized.splitlines() if clean_text(line)]
    names: list[str] = []

    def add_many(value: str, require_multiple: bool = False) -> None:
        extracted = _split_juicy_names(value)
        if require_multiple and len(extracted) < 2:
            return
        for name in extracted:
            if name not in names:
                names.append(name)

    # 1. Most reliable source: official product block. Example:
    # AVC ジューシーハニーコレクションカード PLUS #30
    # 浜辺やよい miru 神木麗 天神羽衣 アダルトトレカ
    product_marker = re.compile(
        r"(?:AVC\s*)?(?:ジューシーハニー(?:コレクションカード)?|"
        r"JUICY\s+HONEY(?:\s+COLLECTION\s+CARDS)?)\s*"
        r"(?:THE\s+)?(?:PLUS\s*#?\s*\d+|VOL[.]?\s*\d+|"
        r"LUXURY(?:\s+EDITION)?|DELUXE(?:\s+EDITION)?|"
        r"EXQUISITE(?:\s+EDITION)?|ANNIVERSARY|20TH\s+ANNIVERSARY)",
        re.I,
    )
    hard_stop = re.compile(
        r"^(?:売価|価格|発売|発売予定|発売日|release\s*date|upc|jan|"
        r"発売元|販売元|商品構成|限定生産|limited\s+production|"
        r"1\s*パック|1\s*box|1\s*ボックス|srp|adults?\s+only)",
        re.I,
    )
    for index, line in enumerate(lines):
        if not product_marker.search(line):
            continue
        for candidate in lines[index + 1:index + 8]:
            if product_marker.search(candidate):
                continue
            if hard_stop.search(candidate):
                break
            candidate = re.sub(
                r"\s*(?:プレミアム\s*)?(?:アダルトトレカ|セクシー女優トレカ|トレーディングカード)\s*$",
                "",
                candidate,
                flags=re.I,
            )
            extracted = _split_juicy_names(candidate)
            # Juicy Honey sets normally have 3-4 performers. Requiring at
            # least two here prevents a slogan or card name becoming a model.
            if len(extracted) >= 2:
                add_many(candidate, require_multiple=True)
                break

    # 2. Explicit cast labels when present.
    for match in re.finditer(
        r"(?:featuring|出演(?:女優)?|収録女優|cast|models?)\s*[:：]\s*([^\n]{3,200})",
        normalized,
        re.I,
    ):
        add_many(match.group(1), require_multiple=True)

    # Several older release announcements put the cast in a sentence instead
    # of a labelled line, e.g. ``カードはAさんとBさん、Cさんの3名収録``.
    for match in re.finditer(
        r"(?:カード|トレーディングカード)[^。\n]{0,100}?は\s*([^。\n]{3,140}?)(?:の)?\s*\d+\s*名\s*収録",
        normalized,
        re.I,
    ):
        add_many(match.group(1), require_multiple=True)

    # Sales/stock pages sometimes preserve the cast only as an ordering note.
    for match in re.finditer(
        r"(?:通販ページ|通信販売ページ)[^。\n]{0,100}?[、,，]\s*([^。\n]{3,140}?)(?:の)?\s*順",
        normalized,
        re.I,
    ):
        add_many(match.group(1), require_multiple=True)

    # 3. Article headlines often end with all performer names. Remove the
    # date, announcement wording and canonical series portion before parsing.
    for line in lines[:40]:
        if not re.search(r"(?:ジューシーハニー|JUICY\s+HONEY)", line, re.I):
            continue
        if not re.search(
            r"(?:PLUS\s*#?\s*\d+|VOL[.]?\s*\d+|LUXURY|DELUXE|EXQUISITE|ANNIVERSARY)",
            line,
            re.I,
        ):
            continue

        # Older release headlines put the complete cast in Japanese
        # parentheses after ``アダルトトレカ``. Parse that bounded group before
        # stripping the headline prefix; otherwise the first name remains
        # attached to product wording and is rejected while the other names
        # are accepted, producing a plausible-looking but incomplete cast.
        for parenthesized in re.findall(r"[（(]([^()（）]{3,180})[）)]", line):
            if re.search(r"(?:＆|&|、|,|/|\band\b)", parenthesized, re.I):
                add_many(parenthesized, require_multiple=True)

        tail = re.sub(r"^.*?(?:ジューシーハニー|JUICY\s+HONEY)", "", line, flags=re.I)
        tail = re.sub(
            r"^(?:\s*(?:COLLECTION\s+CARDS?)?\s*(?:THE\s+)?"
            r"(?:PLUS\s*#?\s*\d+|VOL[.]?\s*\d+|LUXURY(?:\s+EDITION)?(?:\s*20\d{2})?|"
            r"DELUXE(?:\s+EDITION)?(?:\s*20\d{2})?|EXQUISITE(?:\s+EDITION)?(?:\s*20\d{2})?|"
            r"20TH\s+ANNIVERSARY|ANNIVERSARY)(?:\s*[-~〜～][^-~〜～]+[-~〜～])?)",
            "",
            tail,
            flags=re.I,
        )
        tail = re.sub(
            r"^(?:\s*(?:レアカード一挙掲載|発売決定|発売予定|予約開始|"
            r"抽選販売のお知らせ|アダルトトレカ|セクシー女優トレカ)[!！:：\s]*)+",
            "",
            tail,
            flags=re.I,
        )
        tail = re.sub(r"\b\d{1,2}\s*月\s*\d{1,2}\s*日\s*発売\b", " ", tail)
        add_many(tail, require_multiple=True)

    # 4. Parse only inside the real profile section. The previous parser
    # searched backwards from every birthday on the page and could select a
    # nearby slogan. Here the section boundary and line shape are strict.
    profile_start = next(
        (i for i, line in enumerate(lines) if re.search(r"収録女優\s*Profile", line, re.I)),
        -1,
    )
    if profile_start >= 0:
        profile_end = len(lines)
        for i in range(profile_start + 1, len(lines)):
            if re.search(
                r"^(?:カメラマン|Photography\s+by|AVC\s+ジューシーハニー|"
                r"AVC\s+JUICY\s+HONEY|商品構成|\[REGULAR\s+CARDS\])",
                lines[i],
                re.I,
            ):
                profile_end = i
                break
        profile_lines = lines[profile_start + 1:profile_end]
        for i, line in enumerate(profile_lines):
            if not re.search(r"^(?:誕生日|生年月日)\b", line, re.I):
                continue
            if i == 0:
                continue
            candidate = profile_lines[i - 1]
            # Official format: 浜辺やよい [ハマベヤヨイ]
            candidate = normalize_juicy_person_name(candidate)
            if is_probable_juicy_model_name(candidate):
                add_many(candidate)

    # Final defensive cleanup. Real Juicy Honey cast lists are generally 3-4
    # names; do not fill missing positions with prose or metadata.
    return juicy_model_names(names)


def extract_juicy_scoped_model_names(text: str, identity: str) -> list[str]:
    """Extract cast text explicitly attached to one identity in a mixed post.

    Older restock posts use prose such as ``Aさん、Bさんを収録した【VOL.4】``
    and then continue with a different cast before ``【VOL.6】``.  The normal
    article extractor intentionally sees the whole post, so using its result
    for every identity would create false memberships.  Only accept a cast
    when the same sentence contains the requested product marker.
    """
    normalized = unicodedata.normalize("NFKC", str(text or ""))
    pattern = re.compile(
        r"(?P<names>[^。\n]{3,180}?)(?:を|が)\s*"
        r"収録(?:した|されている|されています)?\s*"
        r"(?P<marker>【[^】\n]{1,80}】|\[[^\]\n]{1,80}\])",
        re.I,
    )
    for match in pattern.finditer(normalized):
        marker_identities = {
            row[0] for row in juicy_series_identities(match.group("marker"))
        }
        if identity not in marker_identities:
            continue
        names = juicy_model_names(match.group("names"))
        if len(names) >= 2:
            return names
    return []


def extract_juicy_models(text: str) -> str:
    """Backward-compatible combined display value."""
    return " / ".join(extract_juicy_model_names(text))

def extract_juicy_release_date(text: str, fallback_year: int | None = None) -> str:
    """Extract an explicitly labelled product release date.

    The archive year is the publication year of a blog listing, not
    necessarily the product release year. In particular, a yearless label
    such as ``10月24日発売`` must not be converted with ``fallback_year``;
    doing so caused unrelated article/archive dates to become false release
    dates. The optional argument remains for adapter compatibility but is
    intentionally ignored.
    """
    value = unicodedata.normalize("NFKC", str(text or ""))
    candidates: list[tuple[int, str]] = []

    japanese_labelled_patterns = (
        r"(?:発売予定|発売日|発売|release\s*date)\s*[:：]?\s*"
        r"(20\d{2})\s*(?:年|[-/.])\s*(\d{1,2})\s*(?:月|[-/.])\s*(\d{1,2})",
        r"(20\d{2})\s*(?:年|[-/.])\s*(\d{1,2})\s*(?:月|[-/.])\s*(\d{1,2})\s*日?\s*"
        r"(?:発売予定|発売日|発売)",
    )
    for pattern in japanese_labelled_patterns:
        for match in re.finditer(pattern, value, re.I):
            year, month, day = map(int, match.groups())
            try:
                parsed = date(year, month, day)
            except ValueError:
                continue

            # Official Juicy Honey pages sometimes show a postponed date as
            # ``2022年4月30日 -> 5月14日``. Keep the final date in the label.
            revision = re.match(
                r"\s*(?:~{1,2}\s*)?(?:→|->)\s*"
                r"(?:(20\d{2})\s*年\s*)?(\d{1,2})\s*月\s*(\d{1,2})\s*日?",
                value[match.end() : match.end() + 80],
                re.I,
            )
            if revision:
                revised_year = int(revision.group(1) or year)
                try:
                    parsed = date(
                        revised_year, int(revision.group(2)), int(revision.group(3))
                    )
                except ValueError:
                    pass
            candidates.append((match.start(), parsed.isoformat()))

    english_pattern = (
        r"release\s*date\s*[:：]?\s*([A-Za-z]+)\s+"
        r"(\d{1,2})(?:st|nd|rd|th)?[,]?\s+(20\d{2})"
    )
    for match in re.finditer(english_pattern, value, re.I):
        try:
            parsed = datetime.strptime(" ".join(match.groups()), "%B %d %Y")
        except ValueError:
            try:
                parsed = datetime.strptime(" ".join(match.groups()), "%b %d %Y")
            except ValueError:
                continue

        revision = re.match(
            r"\s*~{0,2}\s*(?:→|->)\s*([A-Za-z]+)\s+"
            r"(\d{1,2})(?:st|nd|rd|th)?[,]?\s+(20\d{2})",
            value[match.end() : match.end() + 100],
            re.I,
        )
        if revision:
            try:
                parsed = datetime.strptime(" ".join(revision.groups()), "%B %d %Y")
            except ValueError:
                try:
                    parsed = datetime.strptime(" ".join(revision.groups()), "%b %d %Y")
                except ValueError:
                    pass
        candidates.append((match.start(), parsed.date().isoformat()))

    # If an official page contains both an original and a revised labelled
    # date, the last explicit candidate is the final one. Unlabelled dates
    # (including article publication dates) never enter this list.
    return max(candidates, key=lambda item: item[0])[1] if candidates else ""


def extract_juicy_headline_release_date(text: str, year: int | None) -> str:
    """Resolve an explicit month/day release date from a dated article title."""
    if not year or year < 2000:
        return ""
    normalized = unicodedata.normalize("NFKC", str(text or ""))
    candidates: list[tuple[int, str]] = []
    for match in re.finditer(
        r"(?<!\d)(\d{1,2})\s*月\s*(\d{1,2})\s*日\s*発売(?:予定)?",
        normalized,
        re.I,
    ):
        try:
            parsed = date(year, int(match.group(1)), int(match.group(2)))
        except ValueError:
            continue
        candidates.append((match.start(), parsed.isoformat()))
    return max(candidates, key=lambda item: item[0])[1] if candidates else ""


def juicy_article_payload(page) -> dict:
    """Return article metadata and structured performer profiles from the DOM.

    The official Juicy Honey article contains a canonical magenta cast line and
    a ``収録女優Profile`` section.  Each profile usually includes Japanese and
    English names, date of birth, zodiac sign, body measurements, social links,
    and a portrait image.  Extract those elements directly instead of inferring
    them from the full marketing text.
    """
    return page.evaluate(
        r"""() => {
            const root = document.querySelector('.article-body-inner')
                || document.querySelector('.article-body.entry-content')
                || document.querySelector('article, .entry-content')
                || document.body;

            const clean = value => (value || '')
                .replace(/\u00a0/g, ' ')
                .replace(/\s+/g, ' ')
                .trim();

            const productPattern = /(?:AVC\s*)?(?:ジューシーハニー(?:コレクションカード)?|JUICY\s+HONEY(?:\s+COLLECTION\s+CARDS)?)\s*(?:THE\s+)?(?:PLUS\s*#?\s*\d+|VOL\.?\s*\d+|LUXURY(?:\s+EDITION)?|DELUXE(?:\s+EDITION)?|EXQUISITE(?:\s+EDITION)?|(?:\d{1,2}(?:ST|ND|RD|TH)?\s*)?ANN(?:I)?VERSARY)/i;
            const hardStop = /^(?:売価|価格|発売|発売予定|発売日|Release\s*Date|UPC|JAN|発売元|販売元|商品構成|限定生産|1\s*パック|1\s*BOX|1\s*ボックス|SRP|Adults?\s+Only)/i;
            const castSuffix = /\s*(?:プレミアム\s*)?(?:アダルトトレカ|セクシー女優トレカ|トレーディングカード)\s*$/i;

            const blocks = Array.from(root.querySelectorAll('div, p, li'));
            const castCandidates = [];
            const addCast = value => {
                const text = clean(value).replace(castSuffix, '').trim();
                if (!text || text.length > 180 || productPattern.test(text) || hardStop.test(text)) return;
                if (!castCandidates.includes(text)) castCandidates.push(text);
            };

            // Primary cast source: the short magenta line immediately after
            // the official AVC product heading.
            for (const block of blocks) {
                const ownText = clean(block.innerText || block.textContent);
                if (!productPattern.test(ownText) || ownText.length > 260) continue;
                let sibling = block.nextElementSibling;
                for (let i = 0; sibling && i < 6; i++, sibling = sibling.nextElementSibling) {
                    const candidate = clean(sibling.innerText || sibling.textContent);
                    if (!candidate) continue;
                    if (productPattern.test(candidate)) continue;
                    if (hardStop.test(candidate)) break;
                    addCast(candidate);
                    if (castCandidates.length) break;
                }
            }
            for (const block of blocks) {
                const text = clean(block.innerText || block.textContent);
                if (text.length <= 180 && castSuffix.test(text) && !productPattern.test(text)) {
                    addCast(text);
                }
            }

            const all = Array.from(root.querySelectorAll('*'));
            const profileStartIndex = all.findIndex(element => {
                const text = clean(element.innerText || element.textContent);
                return text.length < 80 && /収録女優\s*Profile/i.test(text);
            });
            let profileEndIndex = all.length;
            if (profileStartIndex >= 0) {
                for (let i = profileStartIndex + 1; i < all.length; i++) {
                    const text = clean(all[i].innerText || all[i].textContent);
                    if (text.length < 100 && /^(?:カメラマン|Photography\s+by)/i.test(text)) {
                        profileEndIndex = i;
                        break;
                    }
                }
            }
            const birthdayIndexes = [];
            for (let i = Math.max(0, profileStartIndex + 1); i < profileEndIndex; i++) {
                const text = clean(all[i].innerText || all[i].textContent);
                if (/^(?:誕生日|生年月日)\s*/i.test(text) && text.length < 80) {
                    birthdayIndexes.push(i);
                }
            }

            const profileNames = [];
            const modelProfiles = [];
            const absolute = value => {
                if (!value) return '';
                try { return new URL(value, document.baseURI).href; } catch (_) { return value; }
            };
            const parseBirthday = text => {
                const m = clean(text).match(/(20\d{2}|19\d{2})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日/);
                if (!m) return '';
                return `${m[1]}-${String(Number(m[2])).padStart(2, '0')}-${String(Number(m[3])).padStart(2, '0')}`;
            };
            const parseMeasurements = text => {
                const normalized = clean(text).replace(/（/g, '(').replace(/）/g, ')');
                const number = pattern => {
                    const m = normalized.match(pattern);
                    return m ? Number(m[1]) : 0;
                };
                const cupMatch = normalized.match(/B\s*\d+(?:\.\d+)?\s*cm?\s*\(([A-Z])\s*-?\s*cup\)/i)
                    || normalized.match(/\(([A-Z])\s*-?\s*cup\)/i);
                return {
                    heightCm: number(/(?:Ht|Height)\s*([0-9]{2,3}(?:\.[0-9]+)?)\s*cm/i),
                    bustCm: number(/B\s*([0-9]{2,3}(?:\.[0-9]+)?)\s*cm?/i),
                    waistCm: number(/W\s*([0-9]{2,3}(?:\.[0-9]+)?)\s*cm?/i),
                    hipCm: number(/H\s*([0-9]{2,3}(?:\.[0-9]+)?)\s*cm?/i),
                    cup: cupMatch ? cupMatch[1].toUpperCase() : ''
                };
            };

            for (let position = 0; position < birthdayIndexes.length; position++) {
                const birthdayIndex = birthdayIndexes[position];
                const endIndex = position + 1 < birthdayIndexes.length
                    ? birthdayIndexes[position + 1]
                    : Math.min(profileEndIndex, birthdayIndex + 180);

                let rawName = '';
                for (let i = birthdayIndex - 1; i >= Math.max(0, birthdayIndex - 35); i--) {
                    const element = all[i];
                    const text = clean(element.innerText || element.textContent);
                    if (!text || text.length > 80) continue;
                    const style = clean(element.getAttribute?.('style') || '').toLowerCase();
                    const parentStyle = clean(element.parentElement?.getAttribute?.('style') || '').toLowerCase();
                    const isMagenta = /255\s*,\s*0\s*,\s*255|#ff00ff|magenta/.test(`${style} ${parentStyle}`);
                    if (!isMagenta && !/[\[［][^\]］]+[\]］]/.test(text)) continue;
                    if (/^(?:誕生日|星座|ボディサイズ|Date of Birth|Sign|Ht\d)/i.test(text)) continue;
                    rawName = text;
                    break;
                }
                if (!rawName) continue;

                const nameMatch = rawName.match(/^(.+?)\s*[\[［]([^\]］]+)[\]］]\s*$/);
                const beforePhonetic = clean(nameMatch ? nameMatch[1] : rawName);
                const japanesePrefix = beforePhonetic.match(/^([ぁ-んァ-ヶ一-龯々〆ヵヶー]+(?:[\s　・･]+[ぁ-んァ-ヶ一-龯々〆ヵヶー]+)*)/);
                const japaneseHeading = japanesePrefix ? japanesePrefix[1] : '';
                const name = clean(japanesePrefix ? japaneseHeading.replace(/[\s　]+/g, '') : beforePhonetic);
                const phoneticName = clean(nameMatch ? nameMatch[2] : '');
                const headingEnglishName = japanesePrefix
                    ? clean(beforePhonetic.slice(japaneseHeading.length))
                    : '';
                if (!name || name.length > 40) continue;

                let birthday = '';
                let zodiac = '';
                let englishName = /^[A-Za-z][A-Za-z .'-]{1,45}$/.test(headingEnglishName)
                    ? headingEnglishName
                    : '';
                let measurementText = '';
                let imageUrl = '';
                let xUrl = '';
                let instagramUrl = '';
                let wikipediaUrl = '';

                for (let i = birthdayIndex; i < endIndex; i++) {
                    const element = all[i];
                    const text = clean(element.innerText || element.textContent);
                    if (!birthday && /^(?:誕生日|生年月日)/i.test(text)) birthday = parseBirthday(text);
                    if (!zodiac && /^星座/i.test(text)) zodiac = clean(text.replace(/^星座\s*[:：]?\s*/i, ''));
                    if (!measurementText && /(?:ボディサイズ|Ht\s*\d+).*B\s*\d+/i.test(text)) measurementText = text;

                    if (!englishName && /^[A-Za-z][A-Za-z .'-]{1,45}$/.test(text)
                        && !/^(?:Date of Birth|Sign|Instagram|Wikipedia|Photography|Adults Only)$/i.test(text)) {
                        englishName = text;
                    }

                    if (!imageUrl && element.tagName === 'IMG') {
                        const link = element.closest('a[href]');
                        imageUrl = absolute(link?.href || element.currentSrc || element.src || element.dataset?.src || '');
                    }
                    if (element.tagName === 'A' && element.href) {
                        const href = absolute(element.href);
                        const label = clean(element.innerText || element.textContent).toLowerCase();
                        if (!xUrl && (/(?:x\.com|twitter\.com)/i.test(href) || label === 'x' || label === 'twitter')) xUrl = href;
                        if (!instagramUrl && /instagram\.com/i.test(href)) instagramUrl = href;
                        if (!wikipediaUrl && /wikipedia\.org/i.test(href)) wikipediaUrl = href;
                    }
                }

                const measurements = parseMeasurements(measurementText);
                const profile = {
                    name,
                    originalName: name,
                    phoneticName,
                    englishName,
                    birthDate: birthday,
                    zodiac,
                    heightCm: measurements.heightCm,
                    bustCm: measurements.bustCm,
                    waistCm: measurements.waistCm,
                    hipCm: measurements.hipCm,
                    cup: measurements.cup,
                    imageUrl,
                    xUrl,
                    instagramUrl,
                    wikipediaUrl
                };
                if (!profileNames.includes(name)) profileNames.push(name);
                if (!modelProfiles.some(item => item.name === name)) modelProfiles.push(profile);
            }

            // Capture the complete authoritative article-body inventory before
            // classification. A presentation maxImages value must never trim
            // this evidence collection.
            const articleImages = [];
            const seenImages = new Set();
            const imageHref = value => /\.(?:avif|gif|jpe?g|png|webp)(?:$|[?#])/i.test(value || '');
            const srcsetURL = value => {
                const entries = clean(value).split(',').map(entry => entry.trim()).filter(Boolean);
                if (!entries.length) return '';
                return entries[entries.length - 1].split(/\s+/)[0] || '';
            };
            const precedingContext = image => {
                let node = image;
                for (let depth = 0; node && depth < 5; depth++, node = node.parentElement) {
                    let previous = node.previousElementSibling;
                    for (let offset = 0; previous && offset < 4; offset++, previous = previous.previousElementSibling) {
                        const text = clean(previous.innerText || previous.textContent);
                        if (text) return text.slice(-500);
                    }
                }
                return '';
            };
            for (const image of Array.from(root.querySelectorAll('img'))) {
                const linked = image.closest('a[href]')?.getAttribute('href') || '';
                const discovered = image.getAttribute('data-original')
                    || image.getAttribute('data-src')
                    || image.getAttribute('data-lazy-src')
                    || image.currentSrc
                    || srcsetURL(image.getAttribute('srcset') || '')
                    || image.getAttribute('src')
                    || '';
                const selected = imageHref(linked) ? linked : discovered;
                const originalURL = absolute(selected);
                if (!originalURL || seenImages.has(originalURL)) continue;
                seenImages.add(originalURL);
                articleImages.push({
                    originalUrl: originalURL,
                    discoveredUrl: absolute(discovered),
                    sourceUrl: document.location.href,
                    articleImageSequence: articleImages.length + 1,
                    altText: clean(image.getAttribute('alt') || ''),
                    titleText: clean(image.getAttribute('title') || ''),
                    context: precedingContext(image),
                    width: Number(image.naturalWidth || image.width || 0),
                    height: Number(image.naturalHeight || image.height || 0),
                    mediaType: 'unknown',
                    sourcePlatformKey: 'juicy-honey-blog',
                    sourceConfidence: 'official_image'
                });
            }

            return {
                title: document.title || '',
                heading: document.querySelector('.article-title, h2.entry-title, .entry-title, h1, h2')?.innerText || '',
                body: root?.innerText || root?.textContent || '',
                html: root?.innerHTML || '',
                castCandidates,
                profileNames,
                modelProfiles,
                articleImages,
                published: document.querySelector('meta[property="article:published_time"]')?.content
                    || document.querySelector('time[datetime]')?.getAttribute('datetime')
                    || document.querySelector('abbr.updated[title], .article-date[title]')?.getAttribute('title')
                    || ''
            };
        }"""
    )


def classify_juicy_article_image(item: dict) -> str:
    """Classify only after preserving the full article image inventory."""
    evidence = clean_text(" ".join([
        str(item.get("originalUrl") or ""),
        str(item.get("altText") or ""),
        str(item.get("titleText") or ""),
        str(item.get("context") or ""),
    ])).lower()
    if juicy_cover_hint(evidence):
        return "flyer"
    rules = (
        (("checklist", "check-list", "check_list"), "checklist"),
        (("flyer", "chirashi"), "flyer"),
        (("box",), "box"),
        (("pack",), "pack"),
        (("autograph", "sign", "signed"), "autograph_card"),
        (("relic", "bra", "panty", "costume"), "relic_card"),
        (("promo", "bonus", "privilege"), "promo_card"),
        (("profile", "portrait"), "model_portrait"),
        (("card", "preview"), "card_preview"),
    )
    for markers, media_type in rules:
        if any(marker in evidence for marker in markers):
            return media_type
    return "unknown"


def juicy_cover_hint(value: str) -> bool:
    """Return whether image evidence explicitly identifies release artwork."""
    normalized = unicodedata.normalize("NFKC", clean_text(value)).lower()
    return bool(re.search(
        r"(?:^|[^a-z0-9])(?:fly(?:er)?|cover|front)(?:[^a-z0-9]|$)|"
        r"(?:フライヤー|チラシ|表紙)",
        normalized,
        re.I,
    ))


def juicy_named_cover_score(images: Any) -> int:
    """Prefer a release source that explicitly contains its flyer/cover.

    Cast and release-date fields are reconciled independently when duplicate
    articles merge, so choosing the media-rich sales post does not weaken the
    authoritative metadata collected from the full release announcement.
    """
    entries = images if isinstance(images, list) else []
    for item in entries:
        if not isinstance(item, dict):
            continue
        evidence = " ".join([
            str(item.get("originalUrl") or ""),
            str(item.get("altText") or ""),
            str(item.get("titleText") or ""),
        ])
        if juicy_cover_hint(evidence):
            return 200
    return 0


def normalize_juicy_article_images(value: Any) -> list[dict]:
    result: list[dict] = []
    seen: set[str] = set()
    entries = value if isinstance(value, list) else []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        original_url = clean_text(entry.get("originalUrl") or "")
        if not original_url or original_url in seen:
            continue
        seen.add(original_url)
        normalized = dict(entry)
        normalized["originalUrl"] = original_url
        normalized["mediaType"] = classify_juicy_article_image(normalized)
        normalized["classificationConfidence"] = (
            "inferred" if normalized["mediaType"] != "unknown" else "unknown"
        )
        normalized["sourcePlatformKey"] = "juicy-honey-blog"
        normalized["sourceConfidence"] = "official_image"
        result.append(normalized)
    return result


def merge_article_images(*values: Any) -> list[dict]:
    merged: list[dict] = []
    seen: set[str] = set()
    for value in values:
        for item in normalize_juicy_article_images(value):
            key = item["originalUrl"]
            if key in seen:
                continue
            seen.add(key)
            merged.append(item)
    for sequence, item in enumerate(merged, start=1):
        item["articleImageSequence"] = sequence
    return merged


def normalize_juicy_model_profile(value: Any) -> dict:
    """Normalize one structured model profile returned by the browser."""
    source = value if isinstance(value, dict) else {}
    name = normalize_juicy_person_name(source.get("name") or source.get("originalName") or "")
    if not is_probable_juicy_model_name(name):
        return {}

    def integer(key: str) -> int:
        try:
            return max(0, int(float(source.get(key) or 0)))
        except (TypeError, ValueError):
            return 0

    return {
        "name": name,
        "originalName": clean_text(source.get("originalName") or name),
        "phoneticName": clean_text(source.get("phoneticName") or ""),
        "englishName": clean_text(source.get("englishName") or ""),
        "birthDate": clean_text(source.get("birthDate") or ""),
        "zodiac": clean_text(source.get("zodiac") or ""),
        "heightCm": integer("heightCm"),
        "bustCm": integer("bustCm"),
        "waistCm": integer("waistCm"),
        "hipCm": integer("hipCm"),
        "cup": clean_text(source.get("cup") or "").upper(),
        "imageUrl": clean_text(source.get("imageUrl") or ""),
        "xUrl": clean_text(source.get("xUrl") or ""),
        "instagramUrl": clean_text(source.get("instagramUrl") or ""),
        "wikipediaUrl": clean_text(source.get("wikipediaUrl") or ""),
        "sourceUrl": clean_text(source.get("sourceUrl") or ""),
        "sourceConfidence": clean_text(source.get("sourceConfidence") or ""),
    }


def merge_juicy_model_profiles(*values: Any) -> list[dict]:
    """Merge duplicate profile data, preferring non-empty fields."""
    merged: dict[str, dict] = {}
    order: list[str] = []
    for value in values:
        entries = value if isinstance(value, (list, tuple)) else [value]
        for entry in entries:
            profile = normalize_juicy_model_profile(entry)
            if not profile:
                continue
            key = normalize_text(profile["name"])
            if key not in merged:
                merged[key] = profile
                order.append(key)
                continue
            current = merged[key]
            for field, incoming in profile.items():
                if field in {"name", "originalName"}:
                    continue
                if (not current.get(field)) and incoming:
                    current[field] = incoming
    return [merged[key] for key in order]


def select_juicy_cast(
    cast_candidates: Any,
    profile_names: Any,
    model_profiles: Any,
    fallback_text: str,
    allow_large_cast: bool = False,
) -> tuple[list[str], str, bool]:
    """Choose one authoritative cast set instead of unioning nearby prose.

    A complete profile section or a single official product cast line outranks
    title fragments and flattened article text. This prevents related lottery,
    social-link, and card-preview posts from contributing fake performers.
    """
    max_cast_size = 30 if allow_large_cast else 6
    profile_group = juicy_model_names(
        profile_names or [],
        [item.get("name", "") for item in merge_juicy_model_profiles(model_profiles)],
    )

    groups: list[list[str]] = []
    candidates = cast_candidates if isinstance(cast_candidates, (list, tuple)) else [cast_candidates]
    for candidate in candidates:
        group = juicy_model_names(candidate)
        if 2 <= len(group) <= max_cast_size and group not in groups:
            groups.append(group)

    # Prefer structured profiles when they are at least as complete as the
    # product cast. Older pages sometimes label profiles only in English,
    # yielding fragments such as YUA/KOGAWA; an exact Japanese product line
    # with more people is stronger evidence in that case.
    if 2 <= len(profile_group) <= max_cast_size:
        best_product = max(groups, key=len) if groups else []
        if len(best_product) <= len(profile_group):
            return profile_group, "profile_section", True
    if groups:
        best = max(groups, key=len)
        return best, "product_cast_line", True

    text_group = extract_juicy_model_names(fallback_text)
    text_has_cast_marker = bool(re.search(
        r"(?:収録女優\s*Profile|収録女優|出演(?:者)?|models?\s*[:：]|cast\s*[:：]|セクシー女優トレカ|\d+\s*名\s*収録|通販ページ.*順)",
        fallback_text,
        re.I,
    ))
    if text_has_cast_marker and (
        2 <= len(text_group) <= 6
        or (allow_large_cast and 10 <= len(text_group) <= max_cast_size)
    ):
        return text_group, "article_text", True

    incomplete_groups = [
        group for group in (profile_group, *(juicy_model_names(item) for item in candidates), text_group)
        if group
    ]
    if not incomplete_groups:
        return [], "", False
    return max(incomplete_groups, key=len), "incomplete", False


def reconcile_juicy_release_cast(current: dict, incoming: dict) -> tuple[list[str], list[dict], str, bool]:
    """Keep the strongest complete cast while merging profile attributes."""
    choices: list[tuple[tuple[int, int, int], dict, list[str]]] = []
    source_rank = {
        "verified_release_registry": 5,
        "profile_section": 4,
        "product_cast_line": 3,
        "article_text": 2,
        "incomplete": 1,
    }
    for release in (current, incoming):
        names = juicy_model_names(release.get("modelNames", []), release.get("modelName", ""))
        complete = bool(release.get("castComplete")) and 2 <= len(names) <= 30
        source = str(release.get("castSource") or "")
        choices.append(((1 if complete else 0, source_rank.get(source, 0), len(names)), release, names))

    _, selected_release, selected_names = max(choices, key=lambda item: item[0])
    complete = bool(selected_release.get("castComplete")) and 2 <= len(selected_names) <= 30
    source = str(selected_release.get("castSource") or ("incomplete" if selected_names else ""))
    all_profiles = merge_juicy_model_profiles(
        current.get("modelProfiles", current.get("models", [])),
        incoming.get("modelProfiles", incoming.get("models", [])),
    )
    profiles_by_name = {normalize_text(item.get("name", "")): item for item in all_profiles}
    profiles = [
        profiles_by_name.get(normalize_text(name), {"name": name, "originalName": name})
        for name in selected_names
    ]
    return selected_names, profiles, source, complete


def apply_verified_juicy_release_metadata(identity: str, release: dict) -> dict:
    """Fill exact historical facts that a mixed official article cannot own."""
    metadata = JUICY_VERIFIED_RELEASE_METADATA.get(identity)
    if not metadata:
        return release

    names = list(metadata["modelNames"])
    evidence_url = str(metadata["sourceUrl"])
    existing_profiles = merge_juicy_model_profiles(
        release.get("modelProfiles", release.get("models", []))
    )
    profiles_by_name = {
        normalize_text(item.get("name", "")): item for item in existing_profiles
    }
    profiles = []
    for name in names:
        profile = dict(
            profiles_by_name.get(
                normalize_text(name),
                {"name": name, "originalName": name},
            )
        )
        profile["sourceUrl"] = evidence_url
        profile["sourceConfidence"] = "official_structured"
        profiles.append(profile)

    release["releaseDate"] = metadata["releaseDate"]
    release["modelName"] = names[0]
    release["modelNames"] = names
    release["models"] = profiles
    release["modelProfiles"] = profiles
    release["castComplete"] = True
    release["castSource"] = "verified_release_registry"
    release["sourceUrls"] = list(dict.fromkeys([
        *release.get("sourceUrls", []),
        release.get("sourceUrl", ""),
        evidence_url,
    ]))
    return release


def hydrate_juicy_article(page, url: str, link_text: str, archive_year: int) -> dict | None:
    """Open a blog article and derive canonical release metadata from its body."""
    try:
        goto(page, url, wait_ms=350, timeout_ms=30000, attempts=2)
        payload = juicy_article_payload(page)
    except Exception as exc:
        progress(f"[juicy-honey] detail failed url={url} error={exc}")
        return None

    title = clean_text(payload.get("title") or "")
    heading = clean_text(payload.get("heading") or "")
    body = str(payload.get("body") or "")
    identity_source = "\n".join(part for part in (heading, link_text, title) if part)
    combined = "\n".join(part for part in (heading, title, link_text, body) if part)
    identities = juicy_series_identities(identity_source)
    if not identities:
        fallback = juicy_series_identity(combined)
        identities = [fallback] if fallback[0] else []
    if not identities:
        return None
    identity, volume, canonical_title = identities[0]

    published = str(payload.get("published") or "")
    article_date = extract_date(published) or extract_date(combined)
    release_date = extract_juicy_release_date(combined)
    if not release_date:
        article_year = int(article_date[:4]) if re.match(r"^20\d{2}", article_date) else archive_year
        release_date = extract_juicy_headline_release_date(
            identity_source,
            article_year,
        )
    # Headlines for recurring special editions often omit the calendar year.
    # Keep the headline's strong series identity, then qualify its unknown year
    # from the official release date (or, as a fallback, the article date).
    def qualify_identity_year(
        row: tuple[str, int | None, str],
    ) -> tuple[str, int | None, str]:
        row_identity, row_volume, row_title = row
        identity_parts = row_identity.split(":")
        identity_year_index = 2 if identity_parts[0] == "anniversary" else 1
        if (
            len(identity_parts) > identity_year_index
            and identity_parts[identity_year_index] == "unknown"
        ):
            dated_year = next(
                (
                    value[:4]
                    for value in (release_date, article_date)
                    if re.match(r"^20\d{2}", str(value or ""))
                ),
                "",
            )
            if dated_year:
                identity_parts[identity_year_index] = dated_year
                row_identity = ":".join(identity_parts)
                if identity_parts[0] != "anniversary" and dated_year not in row_title:
                    row_title = f"{row_title} {dated_year}"
        return row_identity, row_volume, row_title

    identities = [qualify_identity_year(row) for row in identities]
    identity, volume, canonical_title = identities[0]
    # Prefer cast strings extracted from the official DOM structure. The
    # flattened article text remains a final fallback for older layouts.
    model_profiles = merge_juicy_model_profiles(payload.get("modelProfiles") or [])
    models, cast_source, cast_complete = select_juicy_cast(
        payload.get("castCandidates") or [],
        payload.get("profileNames") or [],
        model_profiles,
        combined,
        allow_large_cast=any(row[0].split(":", 1)[0] == "anniversary" for row in identities),
    )

    # Ensure every cast member has at least a minimal structured record.
    profiles_by_name = {normalize_text(item.get("name", "")): item for item in model_profiles}
    model_profiles = [
        profiles_by_name.get(
            normalize_text(name),
            {"name": name, "originalName": name},
        )
        for name in models
    ]

    if len(models) < 2:
        progress(
            f"[juicy-honey] cast incomplete url={page.url} "
            f"candidates={payload.get('castCandidates') or []} "
            f"profiles={payload.get('profileNames') or []} models={models}"
        )
    jan_code = extract_jan(combined)
    score = juicy_release_score(identity_source + "\n" + combined)
    article_images = normalize_juicy_article_images(payload.get("articleImages") or [])
    score += juicy_named_cover_score(article_images)
    for profile in model_profiles:
        profile["sourceUrl"] = page.url
        profile["sourceConfidence"] = "official_structured"

    hydrated_releases = []
    mixed_article = len(identities) > 1
    for release_identity, release_volume, release_title in identities:
        series_key = release_identity.split(":", 1)[0]
        edition_key = "" if series_key in {"plus", "volume"} else release_identity
        release_models = models
        release_profiles = model_profiles
        release_cast_complete = cast_complete
        release_cast_source = cast_source
        if mixed_article:
            # A mixed restock article is unsafe by default, but some legacy
            # posts scope a cast to a product marker in the same sentence.
            # Recover only that bounded cast; never reuse the article-wide
            # candidate list for every release.
            release_models = extract_juicy_scoped_model_names(
                combined,
                release_identity,
            )
            release_profiles = [
                profiles_by_name.get(
                    normalize_text(name),
                    {"name": name, "originalName": name},
                )
                for name in release_models
            ]
            release_cast_complete = len(release_models) >= 2
            release_cast_source = (
                "mixed_article_scoped" if release_cast_complete else "mixed_article"
            )
        for profile in release_profiles:
            profile.setdefault("sourceUrl", page.url)
            profile.setdefault("sourceConfidence", "official_structured")
        release = {
            "publisherKey": "juicy-honey",
            "sourcePlatformKey": "juicy-honey-blog",
            "seriesKey": series_key,
            "editionKey": edition_key,
            "title": release_title,
            "subtitle": "",
            # Keep modelName scalar for the existing flat Go contract, but do
            # not put several performers into one database model name.
            "modelName": release_models[0] if release_models else "",
            # Importers should iterate modelNames and upsert every name
            # independently (ON CONFLICT DO NOTHING / equivalent).
            "modelNames": release_models,
            # Structured alias for importers that prefer objects. Each entry
            # represents one model and must be upserted independently.
            "models": release_profiles,
            "modelProfiles": release_profiles,
            "castComplete": release_cast_complete,
            "castSource": release_cast_source,
            "volume": release_volume,
            # A date parsed from a mixed restock headline belongs to the article,
            # not to every release it lists. Exact registry data may fill it.
            "releaseDate": "" if mixed_article else release_date,
            "articleDate": article_date,
            "janCode": jan_code,
            "sourceUrl": page.url,
            "sourceType": "official_release",
            "sourceConfidence": "official_structured",
            "checklistUrl": "",
            "contentRating": "restricted_18_plus",
            "articleImages": article_images,
            "sourceUrls": [page.url],
            "sourceReleaseCount": len(identities),
            "sourceSeriesIdentities": [row[0] for row in identities],
        }
        release = apply_verified_juicy_release_metadata(release_identity, release)
        hydrated_releases.append({
            "identity": release_identity,
            "score": score,
            "release": release,
        })

    primary = hydrated_releases[0]
    primary["releases"] = hydrated_releases
    return primary


def merge_juicy_discovery_candidate(best_by_identity: dict[str, dict], hydrated: dict) -> None:
    identity = hydrated["identity"]
    incoming = hydrated["release"]
    incoming_score = int(hydrated["score"])
    previous = best_by_identity.get(identity)

    if previous is None:
        best_by_identity[identity] = {"score": incoming_score, "release": incoming}
        return

    current = previous["release"]
    merged_models, merged_profiles, cast_source, cast_complete = reconcile_juicy_release_cast(
        current,
        incoming,
    )
    current["modelNames"] = merged_models
    current["modelName"] = merged_models[0] if merged_models else ""
    current["modelProfiles"] = merged_profiles
    current["models"] = merged_profiles
    current["castSource"] = cast_source
    current["castComplete"] = cast_complete
    current["articleImages"] = merge_article_images(
        current.get("articleImages", []),
        incoming.get("articleImages", []),
    )
    current["sourceUrls"] = list(dict.fromkeys([
        *current.get("sourceUrls", []),
        *incoming.get("sourceUrls", []),
        current.get("sourceUrl", ""),
        incoming.get("sourceUrl", ""),
    ]))
    if not current.get("releaseDate") and incoming.get("releaseDate"):
        current["releaseDate"] = incoming["releaseDate"]
    if not current.get("articleDate") and incoming.get("articleDate"):
        current["articleDate"] = incoming["articleDate"]
    if not current.get("janCode") and incoming.get("janCode"):
        current["janCode"] = incoming["janCode"]

    if incoming_score <= int(previous["score"]):
        return

    preserved_models = juicy_model_names(
        current.get("modelNames", []), current.get("modelName", "")
    )
    preserved_cast_source = current.get("castSource", "")
    preserved_cast_complete = bool(current.get("castComplete"))
    preserved_date = current.get("releaseDate", "")
    preserved_article_date = current.get("articleDate", "")
    preserved_jan = current.get("janCode", "")
    preserved_profiles = merge_juicy_model_profiles(
        current.get("modelProfiles", current.get("models", []))
    )
    preserved_images = merge_article_images(
        current.get("articleImages", []),
        incoming.get("articleImages", []),
    )
    preserved_source_urls = list(dict.fromkeys([
        *current.get("sourceUrls", []),
        *incoming.get("sourceUrls", []),
        current.get("sourceUrl", ""),
        incoming.get("sourceUrl", ""),
    ]))
    previous["release"] = incoming
    previous["score"] = incoming_score
    replacement_models = list(preserved_models)
    previous["release"]["modelNames"] = replacement_models
    previous["release"]["modelName"] = replacement_models[0] if replacement_models else ""
    replacement_profiles = list(preserved_profiles)
    previous["release"]["modelProfiles"] = replacement_profiles
    previous["release"]["models"] = replacement_profiles
    previous["release"]["castSource"] = preserved_cast_source
    previous["release"]["castComplete"] = preserved_cast_complete
    previous["release"]["articleImages"] = preserved_images
    previous["release"]["sourceUrls"] = preserved_source_urls
    previous["release"]["releaseDate"] = incoming.get("releaseDate") or preserved_date
    previous["release"]["articleDate"] = incoming.get("articleDate") or preserved_article_date
    previous["release"]["janCode"] = incoming.get("janCode") or preserved_jan


VOLUME_PATTERNS = (
    re.compile(r"(?:vol(?:ume)?\.?\s*|ＶＯＬ(?:．|\.)?\s*)(\d{1,4})", re.I),
    re.compile(r"(?:plus|ＰＬＵＳ)\s*#?\s*(\d{1,4})", re.I),
)


def new_page(browser):
    return browser.new_page()


def close_quietly(resource) -> None:
    """Do not turn a completed scrape into a failed worker on shutdown."""
    try:
        resource.close()
    except Exception:
        # CloakBrowser can report a late context-cancelled error while the
        # process is already shutting down. The scrape result is still valid.
        pass


def goto(
    page,
    url: str,
    wait_ms: int = 500,
    timeout_ms: int = 30000,
    attempts: int = 2,
    wait_until: str = "domcontentloaded",
    ready_selector: str = "",
) -> None:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            page.goto(url, wait_until=wait_until, timeout=timeout_ms)
            if ready_selector:
                page.wait_for_selector(
                    ready_selector,
                    state="attached",
                    timeout=min(timeout_ms, 15000),
                )
            if wait_ms:
                page.wait_for_timeout(wait_ms)
            return
        except Exception as exc:
            last_error = exc
            if attempt < attempts:
                try:
                    page.wait_for_timeout(300)
                except Exception:
                    pass
    raise RuntimeError(
        f"navigation failed after {attempts} attempt(s): {url}: {last_error}"
    ) from last_error


def goto_rendered_page(page, url: str, wait_ms: int = 1200, timeout_ms: int = 60000) -> None:
    """Navigate after response commit and wait only for a usable document body."""
    goto(
        page,
        url,
        wait_ms=wait_ms,
        timeout_ms=timeout_ms,
        attempts=2,
        wait_until="commit",
        ready_selector="body",
    )


def links(page) -> list[dict]:
    return page.eval_on_selector_all(
        "a[href]",
        """els => els.map(a => ({
            href: a.href,
            text: (a.innerText || a.textContent || '').replace(/\\s+/g, ' ').trim(),
            title: (a.title || '').trim(),
            alt: (a.querySelector('img')?.alt || '').trim()
        })).filter(x => x.href)""",
    )


class PageLinkParser(HTMLParser):
    def __init__(self, base_url: str):
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.items = []
        self.current = None

    def handle_starttag(self, tag: str, attrs) -> None:
        values = dict(attrs)
        if tag.lower() == "a" and values.get("href") and self.current is None:
            self.current = {
                "href": urljoin(self.base_url, values["href"]),
                "textParts": [],
                "title": values.get("title", ""),
                "alt": "",
            }
        elif tag.lower() == "img" and self.current is not None:
            self.current["alt"] = values.get("alt", "")

    def handle_data(self, data: str) -> None:
        if self.current is not None:
            self.current["textParts"].append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() != "a" or self.current is None:
            return
        self.items.append({
            "href": self.current["href"],
            "text": re.sub(r"\s+", " ", " ".join(self.current["textParts"])).strip(),
            "title": self.current["title"].strip(),
            "alt": self.current["alt"].strip(),
        })
        self.current = None


class PageTextParser(HTMLParser):
    BLOCK_TAGS = {
        "article", "blockquote", "br", "div", "figcaption", "footer",
        "h1", "h2", "h3", "h4", "h5", "h6", "header", "li", "main",
        "p", "section", "table", "td", "th", "tr",
    }
    SKIPPED_TAGS = {"script", "style", "noscript", "template"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.skipped_depth = 0

    def handle_starttag(self, tag: str, _attrs) -> None:
        normalized = tag.lower()
        if normalized in self.SKIPPED_TAGS:
            self.skipped_depth += 1
            return
        if self.skipped_depth == 0 and normalized in self.BLOCK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        normalized = tag.lower()
        if normalized in self.SKIPPED_TAGS:
            self.skipped_depth = max(0, self.skipped_depth - 1)
            return
        if self.skipped_depth == 0 and normalized in self.BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self.skipped_depth == 0:
            self.parts.append(data)

    def text(self) -> str:
        lines = []
        for line in "".join(self.parts).splitlines():
            cleaned = re.sub(r"\s+", " ", line).strip()
            if cleaned:
                lines.append(cleaned)
        return "\n".join(lines)


def html_to_text(value: str) -> str:
    parser = PageTextParser()
    parser.feed(str(value or ""))
    parser.close()
    return parser.text()


def fetch_page_links(url: str, timeout_seconds: int = 20) -> list[dict]:
    request = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/146 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "ja,en-US;q=0.8,en;q=0.6",
        },
    )
    with urlopen(request, timeout=timeout_seconds) as response:
        content_type = response.headers.get_content_charset() or "utf-8"
        body = response.read(4 << 20).decode(content_type, errors="replace")
    parser = PageLinkParser(url)
    parser.feed(body)
    return parser.items


def fetch_json_document(
    url: str, timeout_seconds: int = 30, maximum_bytes: int = 16 << 20
) -> tuple[Any, dict[str, str]]:
    request = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/146 Safari/537.36",
            "Accept": "application/json",
            "Accept-Language": "ja,en-US;q=0.8,en;q=0.6",
        },
    )
    with urlopen(request, timeout=timeout_seconds) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        raw = response.read(maximum_bytes + 1)
        if len(raw) > maximum_bytes:
            raise RuntimeError(f"JSON response exceeded {maximum_bytes} bytes")
        headers = {key: value for key, value in response.headers.items()}
    return json.loads(raw.decode(charset, errors="replace")), headers


def same_host(raw: str, host: str) -> bool:
    return urlparse(raw).netloc.lower().endswith(host)


def woohoo_release_links(items: list[dict]) -> list[dict]:
    result = []
    for item in items:
        href = item.get("href", "")
        text = clean_text(" ".join([item.get("text", ""), item.get("title", ""), item.get("alt", "")]))
        if same_host(href, "gain-p.jp") and re.search(r"\bvol\.?\s*\d+", text, re.I):
            result.append(item)
    return result


def discover_woohoo(browser) -> list[dict]:
    index_url = "https://gain-p.jp/user_data/title_list"
    page = new_page(browser)
    detail_page = None
    try:
        # gain-p.jp can keep third-party resources open long enough that
        # Playwright never observes DOMContentLoaded. The release links are
        # server-rendered, so response commit + the first category link is the
        # reliable readiness boundary for discovery.
        browser_error = None
        release_links = []
        try:
            goto(page, index_url, 1500, attempts=1, wait_until="commit")
            release_links = woohoo_release_links(links(page))
        except Exception as exc:
            browser_error = exc
            progress(f"[woohoo] browser title index unavailable: {exc}")
        if not release_links:
            try:
                release_links = woohoo_release_links(fetch_page_links(index_url))
                if release_links:
                    progress(f"[woohoo] HTTP title index fallback found={len(release_links)}")
            except Exception as exc:
                detail = f"; browser error: {browser_error}" if browser_error else ""
                raise RuntimeError(f"WooHoo title index unavailable: {exc}{detail}") from exc
        if not release_links:
            detail = f": {browser_error}" if browser_error else ""
            raise RuntimeError(f"WooHoo title index contained no release links{detail}")
        result = []
        seen = set()
        detail_page = new_page(browser)
        for link in release_links:
            href = link.get("href", "")
            text = clean_text(" ".join([link.get("text", ""), link.get("title", ""), link.get("alt", "")]))
            if not same_host(href, "gain-p.jp") or not re.search(r"\bvol\.?\s*\d+", text, re.I):
                continue
            if href in seen:
                continue
            volume = extract_volume(text)
            if not volume:
                continue
            seen.add(href)
            release = candidate("woohoo", text, href, volume, extract_date(text), "official_release", "https://gain-p.jp/user_data/check_list")
            try:
                goto(
                    detail_page,
                    href,
                    350,
                    wait_until="commit",
                    ready_selector="body",
                )
                series_name = woohoo_product_series_name(detail_page)
                if series_name:
                    release["title"] = series_name
                    release["subtitle"] = f"WooHoo Girls Vol. {volume}"
            except Exception as exc:
                progress(f"[woohoo] product detail failed url={href}: {exc}")
            result.append(release)
        return result
    finally:
        if detail_page is not None:
            close_quietly(detail_page)
        close_quietly(page)


def discover_tic(browser, max_pages: int) -> list[dict]:
    page = new_page(browser)
    try:
        result = []
        seen = set()
        for category_id in (8, 9):
            for page_number in range(1, max_pages + 1):
                url = f"https://tic.jp/products/list?category_id={category_id}&pageno={page_number}"
                goto(page, url, 350)
                found_category = False
                for link in links(page):
                    href = link.get("href", "")
                    text = clean_text(" ".join([link.get("text", ""), link.get("title", ""), link.get("alt", "")]))
                    if not same_host(href, "tic.jp") or "category_id=" not in href:
                        continue
                    category = re.search(r"category_id=(\d+)", href)
                    if not category or category.group(1) in {"8", "9"}:
                        continue
                    if not looks_like_tic_release(text):
                        continue
                    found_category = True
                    canonical = href.split("&", 1)[0]
                    if canonical in seen:
                        continue
                    seen.add(canonical)
                    publisher_key = resolve_actual_publisher(text, "produce-216")
                    result.append(candidate(publisher_key, text, canonical, extract_volume(text), extract_date(text), "official_store", ""))
                if page_number > 1 and not found_category:
                    break
        return result
    finally:
        close_quietly(page)


def discover_hits(browser, max_pages: int) -> list[dict]:
    """Discover HIT'S / Produce 216 releases from the manufacturer site."""
    page = new_page(browser)
    try:
        result = []
        seen = set()
        index_urls = ["https://toreca.biz/girls/", "https://toreca.biz/"]
        for index_url in index_urls[:max_pages]:
            goto(page, index_url, 500)
            for link in links(page):
                href = str(link.get("href") or "").split("#", 1)[0]
                text = clean_text(" ".join([
                    str(link.get("text") or ""),
                    str(link.get("title") or ""),
                    str(link.get("alt") or ""),
                ]))
                if not same_host(href, "toreca.biz") or href.rstrip("/") in {
                    "https://toreca.biz", "https://toreca.biz/girls"
                }:
                    continue
                if href in seen or not looks_like_tic_release(text):
                    continue
                seen.add(href)
                publisher_key = resolve_actual_publisher(text, "hits")
                result.append(candidate(
                    publisher_key, text, href, extract_volume(text),
                    extract_date(text), "official_release", "https://toreca.biz/check-list/"
                ))
        return result
    finally:
        close_quietly(page)


def discover_mint(browser, max_pages: int) -> list[dict]:
    """Use linked MINT product pages as trusted secondary evidence only."""
    page = new_page(browser)
    detail_page = new_page(browser)
    try:
        result = []
        seen = set()
        for page_number in range(1, max_pages + 1):
            list_url = "https://www.mint-mall.net/products/list.php?category_id=8690"
            if page_number > 1:
                list_url += f"&page={page_number}"
            goto(page, list_url, 400)
            detail_links = []
            for link in links(page):
                href = str(link.get("href") or "")
                if not same_host(href, "mint-mall.net") or "products/detail.php" not in href:
                    continue
                if "product_id=" not in href or href in seen:
                    continue
                seen.add(href)
                detail_links.append((href, clean_text(link.get("text") or link.get("alt") or "")))
            if page_number > 1 and not detail_links:
                break
            for href, link_text in detail_links:
                try:
                    goto(detail_page, href, 300)
                    body = clean_text(detail_page.locator("body").inner_text())
                except Exception as exc:
                    progress(f"[mint-mall] detail failed url={href} error={exc}")
                    continue
                combined = clean_text(f"{link_text} {body}")
                publisher_key = resolve_actual_publisher(combined, "")
                if not publisher_key:
                    progress(f"[mint-mall] publisher unresolved url={href}")
                    continue
                release = candidate(
                    publisher_key, link_text or combined[:180], href,
                    extract_volume(combined), extract_date(combined), "trusted_retailer", ""
                )
                release["manufacturer"] = extract_manufacturer(combined)
                release["janCode"] = extract_jan(combined)
                sku = re.search(r"\b(?:NTC|TC|MINT)[A-Z0-9-]{5,}\b", combined, re.I)
                release["retailerSku"] = sku.group(0) if sku else ""
                release["sourceConfidence"] = "trusted_retailer"
                result.append(release)
        return result
    finally:
        close_quietly(detail_page)
        close_quietly(page)


FORMOSA_SEXY_INDEX_URLS = (
    "https://www.formosadreamers.com/categories/formosa-sexy",
    "https://www.formosadreamers.com/products",
)
FORMOSA_SEXY_KNOWN_PRODUCTS = (
    {
        "sourceUrl": (
            "https://www.formosadreamers.com/products/formosa-sexy-%E5%B9%B4%E5%BA%A6%E5%A5%B3%E5%AD%A9%E5%8D%A1-"
            "vol4-%E5%85%B8%E8%97%8F%E7%9B%92"
        ),
        "label": "Formosa Sexy 年度女孩卡 Vol. 4",
        "volume": 4,
        "sourceType": "official_store",
    },
    {
        "sourceUrl": (
            "https://shopee.tw/%E7%A6%8F%E7%88%BE%E6%91%A9%E6%B2%99-%E5%A4%A2%E6%83%B3%E5%AE%B6-%E5%95%A6%E5%95%A6%E9%9A%8A-"
            "Formosa-Sexy-%E5%A5%B3%E5%AD%A9%E5%8D%A1-%E6%A2%93%E6%A2%93-%E8%8E%8E%E8%8E%8E-%E5%B0%91%E9%B9%BD-%E8%8A%8A%E8%8A%8A-"
            "Ariel-%E5%A4%A2%E6%83%B3%E5%AE%B6-2022-i.89522650.27967384607"
        ),
        "label": "2022 Formosa Sexy 女孩卡",
        "volume": 1,
        "sourceType": "marketplace_listing",
    },
    {
        "sourceUrl": "https://www.1collectibles.com/products/2023-24-formosa-sexy-vol-2-collection-cards-packs",
        "label": "2023-24 Formosa Sexy Vol. 2 Collection Cards Packs",
        "volume": 2,
        "sourceType": "trusted_retailer",
    },
    {
        "sourceUrl": "https://www.jjcs.com.tw/products/tpbl-2025-formosa-dreamers-sexy-cheerleaders-03-box",
        "label": "2025 Formosa Sexy 年度女孩卡 Vol. 3",
        "volume": 3,
        "releaseDate": "2025-05-10",
        "sourceType": "trusted_retailer",
    },
)
# Backward-compatible alias for callers that used the original single-source constant.
FORMOSA_SEXY_KNOWN_PRODUCT_URL = FORMOSA_SEXY_KNOWN_PRODUCTS[0]["sourceUrl"]
FORMOSA_SEXY_RELEASE_MARKERS = (
    "年度女孩卡",
    "女孩卡",
    "girls card",
    "girls cards",
    "collection card",
    "collection cards",
    "trading card",
)
RAKUTEN_GIRLS_RELEASES = (
    {
        "year": 2020,
        "sourceUrl": "https://monkeys.rakuten.com.tw/news_detail/210",
        "releaseDate": "2020-09-26",
    },
    {
        "year": 2022,
        "sourceUrl": "https://monkeys.rakuten.com.tw/news_detail/535",
        "releaseDate": "2022-09-27",
        "sourceType": "official_release",
    },
    {
        "year": 2023,
        "sourceUrl": "https://sports.ltn.com.tw/news/breakingnews/4440357",
        "releaseDate": "2023-09-27",
        "sourceType": "press_report",
    },
    {
        "year": 2021,
        "sourceUrl": "https://www.ruten.com.tw/search/rakuten+girls%E7%B1%83%E7%B1%83/",
        "releaseDate": "",
        "sourceType": "marketplace_listing",
    },
    {
        "year": 2024,
        "sourceUrl": "https://www.1collectibles.com/products/2024-rakuten-girls-collection-cards-box",
        "releaseDate": "",
        "sourceType": "trusted_retailer",
    },
    {
        "year": 2025,
        "sourceUrl": "https://www.rakuten.com.tw/shop/monkeyshop/product/fzi8sf4bz/",
        "releaseDate": "",
        "sourceType": "official_release",
    },
)


def page_body_text(page) -> str:
    values = []
    try:
        values.append(str(page.title() or ""))
    except Exception:
        pass
    try:
        values.append(str(page.locator("body").inner_text(timeout=15000) or ""))
    except Exception:
        pass
    return clean_text("\n".join(values))


def formosa_release_volume(text: str) -> int | None:
    match = re.search(r"(?:vol(?:ume)?\.?\s*|第\s*)(\d{1,3})", text, re.I)
    return int(match.group(1)) if match else None


def dedupe_taiwan_releases(items: list[dict]) -> list[dict]:
    result = []
    seen = set()
    for item in items:
        key = "|".join([
            str(item.get("publisherKey") or ""),
            str(item.get("seriesKey") or ""),
            str(item.get("editionKey") or ""),
            str(item.get("volume") or ""),
            str(item.get("title") or ""),
        ])
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result


def formosa_release_candidate(
    source_url: str,
    link_text: str,
    body: str,
    page_title: str = "",
    known_volume: int | None = None,
    source_type: str = "official_store",
    release_date: str = "",
) -> dict | None:
    identity = clean_text(" ".join((link_text, page_title, source_url)))
    identity_lowered = identity.lower()
    if not any(marker.lower() in identity_lowered for marker in FORMOSA_SEXY_RELEASE_MARKERS):
        return None
    combined = clean_text(" ".join((identity, body)))
    volume = formosa_release_volume(combined) or known_volume
    if not volume:
        return None
    title = f"Formosa Sexy 年度女孩卡 Vol. {volume}"
    parsed_release_date = release_date or extract_date(combined)
    if re.fullmatch(r"20\d{2}-\d{2}", parsed_release_date or ""):
        parsed_release_date = ""
    release = candidate(
        "formosa-sexy", title, source_url, volume,
        parsed_release_date, source_type, "",
    )
    release.update({
        "seriesKey": "formosa-sexy",
        "editionKey": f"volume:{volume}",
        "title": title,
        "originalTitle": title,
        "subtitle": "Formosa Sexy",
        "modelName": "",
        "modelNames": [],
        "models": [],
        "contentRating": "suggestive_age_gated",
    })
    return release


def discover_formosa(browser, max_pages: int, source_url: str = "") -> list[dict]:
    """Discover Formosa Sexy card products from the official Dreamers store."""
    page = new_page(browser)
    detail_page = new_page(browser)
    try:
        known_by_url = {
            str(item["sourceUrl"]): item for item in FORMOSA_SEXY_KNOWN_PRODUCTS
        }
        targets = [source_url] if source_url else list(FORMOSA_SEXY_INDEX_URLS)
        product_links: list[dict] = []
        seen = set()
        if not source_url:
            for item in FORMOSA_SEXY_KNOWN_PRODUCTS:
                product_links.append(dict(item))
                seen.add(str(item["sourceUrl"]))
        elif source_url in known_by_url:
            product_links.append(dict(known_by_url[source_url]))
            seen.add(source_url)
        for index_url in targets[:max(1, max_pages)]:
            try:
                goto_rendered_page(page, index_url, wait_ms=500, timeout_ms=45000)
            except Exception as exc:
                progress(f"[formosa-sexy] index failed url={index_url} error={exc}")
                if source_url:
                    raise
                continue
            for link in links(page):
                href = str(link.get("href") or "").split("#", 1)[0].rstrip("/")
                if not same_host(href, "formosadreamers.com") or "/products/" not in href:
                    continue
                text = clean_text(" ".join([
                    str(link.get("text") or ""),
                    str(link.get("title") or ""),
                    str(link.get("alt") or ""),
                    href,
                ]))
                if not any(marker.lower() in text.lower() for marker in FORMOSA_SEXY_RELEASE_MARKERS):
                    continue
                if href in seen:
                    continue
                seen.add(href)
                product_links.append({
                    "sourceUrl": href,
                    "label": text,
                    "sourceType": "official_store",
                })

        result = []
        for product in product_links:
            href = str(product.get("sourceUrl") or "")
            link_text = str(product.get("label") or "")
            try:
                goto_rendered_page(detail_page, href, wait_ms=500, timeout_ms=45000)
                body = page_body_text(detail_page)
                try:
                    page_title = str(detail_page.title() or "")
                except Exception:
                    page_title = ""
            except Exception as exc:
                progress(f"[formosa-sexy] product failed url={href} error={exc}")
                continue
            release = formosa_release_candidate(
                href,
                link_text,
                body,
                page_title,
                known_volume=product.get("volume"),
                source_type=str(product.get("sourceType") or "official_store"),
                release_date=str(product.get("releaseDate") or ""),
            )
            if release:
                result.append(release)
        progress(f"[formosa-sexy] discovery completed products={len(product_links)} releases={len(result)}")
        return dedupe_taiwan_releases(result)
    finally:
        close_quietly(detail_page)
        close_quietly(page)


def rakuten_release_candidate(metadata: dict, body: str) -> dict | None:
    combined = clean_text(body)
    if not re.search(
        r"(?:樂天女孩卡|女孩卡|rakuten\s+girls\s+(?:collection\s+)?cards?|collection\s+cards?)",
        combined,
        re.I,
    ):
        return None
    if not re.search(r"(?:女孩卡|卡包|盒|上市|發售|售價|cards?)", combined, re.I):
        return None
    year = int(metadata["year"])
    title = f"Rakuten Girls Trading Cards {year}"
    source_url = str(metadata["sourceUrl"])
    source_type = str(metadata.get("sourceType") or "")
    if not source_type:
        source_type = "official_release" if "rakuten.com.tw" in source_url else "press_report"
    release_date = str(metadata.get("releaseDate") or "")
    if "releaseDate" not in metadata:
        release_date = extract_date(combined)
    release = candidate(
        "rakuten-girls", title, source_url, None,
        release_date,
        source_type, "",
    )
    release.update({
        "seriesKey": "rakuten-girls",
        "editionKey": f"year:{year}",
        "title": title,
        "originalTitle": title,
        "subtitle": "Rakuten Girls",
        "modelName": "",
        "modelNames": [],
        "models": [],
        "contentRating": "general",
    })
    return release


def discover_rakuten_girls(browser, max_pages: int, source_url: str = "") -> list[dict]:
    """Hydrate the verified Rakuten Girls card releases from source pages."""
    page = new_page(browser)
    try:
        metadata_by_url = {
            str(item["sourceUrl"]): item for item in RAKUTEN_GIRLS_RELEASES
        }
        targets = []
        if source_url:
            target = metadata_by_url.get(source_url)
            if target is None:
                target = {"year": date.today().year, "sourceUrl": source_url, "releaseDate": ""}
            targets.append(target)
        else:
            targets.extend(RAKUTEN_GIRLS_RELEASES)

            # The official home page sometimes exposes a newer card article
            # before the checked-in registry is updated. Treat it only as a
            # locator; the same card markers are still required during hydration.
            try:
                goto_rendered_page(page, "https://monkeys.rakuten.com.tw/", wait_ms=500, timeout_ms=45000)
                seen = {str(item["sourceUrl"]) for item in targets}
                for link in links(page):
                    href = str(link.get("href") or "").split("#", 1)[0]
                    if not re.search(r"https?://monkeys\.rakuten\.com\.tw/news_detail/\d+", href, re.I):
                        continue
                    if href in seen:
                        continue
                    link_text = clean_text(" ".join([
                        str(link.get("text") or ""),
                        str(link.get("title") or ""),
                        str(link.get("alt") or ""),
                    ]))
                    if not re.search(r"(?:女孩卡|girls?\s*cards?)", link_text, re.I):
                        continue
                    year_match = re.search(r"\b(20\d{2})\b", link_text)
                    if not year_match:
                        continue
                    seen.add(href)
                    targets.append({"year": int(year_match.group(1)), "sourceUrl": href, "releaseDate": ""})
                    if len(targets) >= max(1, max_pages):
                        break
            except Exception as exc:
                progress(f"[rakuten-girls] archive locator unavailable error={exc}")

        result = []
        seen_releases = set()
        for metadata in targets:
            href = str(metadata["sourceUrl"])
            if href in seen_releases:
                continue
            seen_releases.add(href)
            try:
                render_wait_ms = 5000 if source_platform_for_url(href) == "ruten-taiwan" else 500
                goto_rendered_page(page, href, wait_ms=render_wait_ms, timeout_ms=45000)
                body = page_body_text(page)
            except Exception as exc:
                progress(f"[rakuten-girls] source failed url={href} error={exc}")
                continue
            release = rakuten_release_candidate(metadata, body)
            if release:
                result.append(release)
        progress(f"[rakuten-girls] discovery completed sources={len(targets)} releases={len(result)}")
        return dedupe_taiwan_releases(result)
    finally:
        close_quietly(page)


def extract_cj_model_profiles(text: str, source_url: str = "") -> list[dict]:
    """Parse only explicitly labeled JYUTOKU/CJ profile blocks."""
    value = unicodedata.normalize("NFKC", str(text or "")).replace("\r\n", "\n")
    headings = list(re.finditer(r"(?m)^\s*([^\n]{1,70}?)\s*(?:プロフィール|PROFILE)\s*$", value, re.I))
    result = []
    seen = set()
    for index, heading in enumerate(headings):
        raw_name = clean_text(heading.group(1)).strip("◆◇●○■□*-:： ")
        if not raw_name or re.search(r"(?:商品|カード|構成|特典)", raw_name):
            continue
        end = headings[index + 1].start() if index + 1 < len(headings) else min(len(value), heading.end() + 1400)
        block = value[heading.end():end]
        name_match = re.match(r"^(.+?)\s*[（(]([^）)]+)[）)]$", raw_name)
        name = clean_text(name_match.group(1) if name_match else raw_name)
        phonetic = clean_text(name_match.group(2) if name_match else "")
        key = normalize_text(name)
        if not name or key in seen:
            continue
        seen.add(key)

        birth_date = ""
        birthday = re.search(
            r"(?:生年月日|誕生日)\s*[:：]?\s*(?:(19\d{2}|20\d{2})\s*[年./-])?\s*(\d{1,2})\s*[月./-]\s*(\d{1,2})\s*日?",
            block,
        )
        if birthday and birthday.group(1):
            try:
                birth_date = date(int(birthday.group(1)), int(birthday.group(2)), int(birthday.group(3))).isoformat()
            except ValueError:
                birth_date = ""

        def measurement(label: str) -> int:
            match = re.search(rf"(?:{label})\s*[:：]?\s*(\d{{2,3}}(?:\.\d+)?)\s*cm?", block, re.I)
            return int(float(match.group(1))) if match else 0

        cup_match = re.search(r"(?:カップ|cup)\s*[:：]?\s*([A-Z])", block, re.I)
        result.append({
            "name": name,
            "originalName": name,
            "phoneticName": phonetic,
            "birthDate": birth_date,
            "heightCm": measurement("身長|height|ht"),
            "bustCm": measurement("バスト|bust|b"),
            "waistCm": measurement("ウエスト|waist|w"),
            "hipCm": measurement("ヒップ|hip|h"),
            "cup": cup_match.group(1).upper() if cup_match else "",
            "sourceUrl": source_url,
            "sourceConfidence": "official_structured",
        })
    return result


CJ_RELEASE_PATTERN = re.compile(r"CJ\s*SEXY|CJ\s*\u30ab\u30fc\u30c9", re.I)
CJ_RELEASES_PER_ARCHIVE_PAGE = 6
JYUTOKU_API_ROOT = "https://jyu-toku.sakura.ne.jp/jyu-toku/wp-json/wp/v2"


def wordpress_rendered_text(post: dict, field: str) -> str:
    value = post.get(field) or ""
    if isinstance(value, dict):
        value = value.get("rendered") or ""
    return html_to_text(str(value))


def discover_cj_wordpress(max_pages: int, include_non_cj: bool = False) -> list[dict]:
    category_query = urlencode({"slug": "release", "_fields": "id,count"})
    categories, _headers = fetch_json_document(
        f"{JYUTOKU_API_ROOT}/categories?{category_query}"
    )
    if not isinstance(categories, list) or not categories:
        raise RuntimeError("release category was not returned by the WordPress API")
    category_id = int(categories[0].get("id") or 0)
    if category_id <= 0:
        raise RuntimeError("release category ID was missing from the WordPress API")

    maximum_posts = max(1, max_pages) * CJ_RELEASES_PER_ARCHIVE_PAGE
    per_page = min(50, maximum_posts)
    posts: list[dict] = []
    page_number = 1
    total_pages = 1
    while page_number <= total_pages and len(posts) < maximum_posts:
        query = urlencode({
            "categories": category_id,
            "per_page": per_page,
            "page": page_number,
            "_fields": "link,title,content,date",
        })
        batch, headers = fetch_json_document(f"{JYUTOKU_API_ROOT}/posts?{query}")
        if not isinstance(batch, list):
            raise RuntimeError("release posts response was not a JSON list")
        posts.extend(item for item in batch if isinstance(item, dict))
        try:
            total_pages = max(1, int(headers.get("X-WP-TotalPages", "1")))
        except (TypeError, ValueError):
            total_pages = 1
        if not batch:
            break
        page_number += 1

    result = []
    for post in posts[:maximum_posts]:
        source_url = str(post.get("link") or "").strip()
        title = wordpress_rendered_text(post, "title")
        content = wordpress_rendered_text(post, "content")
        combined = f"{title}\n{content}"
        publisher_key = "cj-sexy" if CJ_RELEASE_PATTERN.search(combined) else "jutoku"
        if publisher_key == "jutoku" and not include_non_cj:
            continue
        if not source_url.startswith(("http://", "https://")):
            continue

        # The first content lines contain the subtitle and official release
        # date. Keep only that header in the title input; the remainder is used
        # for structured profile extraction without polluting canonical titles.
        content_header = " ".join(content.splitlines()[:4])
        release_text = clean_text(f"{title} {content_header}")
        release = candidate(
            publisher_key,
            release_text,
            source_url,
            extract_volume(combined),
            extract_date(combined),
            "official_release",
            "",
        )
        profiles = extract_cj_model_profiles(content, source_url)
        if profiles:
            release["models"] = profiles
            release["modelProfiles"] = profiles
            release["modelNames"] = [profile["name"] for profile in profiles]
            release["modelName"] = release["modelNames"][0]
            release["sourceConfidence"] = "official_structured"
        result.append(release)

    progress(
        f"[jyutoku] WordPress discovery completed posts={len(posts)} releases={len(result)}"
    )
    return result


def discover_cj_browser(browser, max_pages: int, include_non_cj: bool = False) -> list[dict]:
    page = new_page(browser)
    detail_page = new_page(browser)
    result = []
    seen = set()
    for page_number in range(1, max_pages + 1):
        url = "https://jyu-toku.sakura.ne.jp/jyu-toku/category/release/"
        if page_number > 1:
            url += f"page/{page_number}/"
        goto(page, url, 400)
        found = False
        for link in links(page):
            href = link.get("href", "")
            text = clean_text(" ".join([link.get("text", ""), link.get("title", ""), link.get("alt", "")]))
            if not same_host(href, "jyu-toku.sakura.ne.jp") or "/category/release" in href:
                continue
            if not re.search(r"CJ\s+SEXY|CJ\s*カード|商品情報", text, re.I):
                continue
            found = True
            if href in seen:
                continue
            seen.add(href)
            detail_text = ""
            try:
                goto(detail_page, href, 300)
                detail_text = detail_page.locator("body").inner_text()
            except Exception as exc:
                progress(f"[jyutoku] detail failed url={href} error={exc}")
            combined = f"{text}\n{detail_text}"
            publisher_key = "cj-sexy" if re.search(r"CJ\s*SEXY|CJ\s*カード", combined, re.I) else "jutoku"
            if publisher_key == "jutoku" and not include_non_cj:
                continue
            release = candidate(publisher_key, text, href, extract_volume(combined), extract_date(combined), "official_release", "")
            profiles = extract_cj_model_profiles(detail_text, href)
            if profiles:
                release["models"] = profiles
                release["modelProfiles"] = profiles
                release["modelNames"] = [profile["name"] for profile in profiles]
                release["modelName"] = release["modelNames"][0]
                release["sourceConfidence"] = "official_structured"
            result.append(release)
        if page_number > 1 and not found:
            break
    close_quietly(detail_page)
    close_quietly(page)
    return result


def discover_cj(browser, max_pages: int, include_non_cj: bool = False) -> list[dict]:
    try:
        return discover_cj_wordpress(max_pages, include_non_cj)
    except Exception as exc:
        progress(f"[jyutoku] WordPress discovery unavailable; using browser fallback: {exc}")
        return discover_cj_browser(browser, max_pages, include_non_cj)


def juicy_archive_urls_from_sidebar(
    page, max_months: int, source_url: str = ""
) -> list[str]:
    """Read the exact monthly archive URLs published in the blog sidebar.

    Livedoor does not publish every calendar month. Building URLs by subtracting
    months therefore wastes requests and can make discovery look incomplete.
    The `.plugin-monthly` sidebar is the authoritative archive index, so follow
    only those URLs and preserve the site's newest-first order.
    """
    requested_source = str(source_url or "").strip()
    if requested_source:
        parsed_source = urlparse(requested_source)
        source_match = re.fullmatch(
            r"/archives/(20\d{2})-(\d{2})\.html", parsed_source.path
        )
        if (
            parsed_source.scheme in {"http", "https"}
            and parsed_source.netloc.lower() == "juicy-honey.blog.jp"
            and source_match is not None
            and 1 <= int(source_match.group(2)) <= 12
        ):
            canonical = parsed_source._replace(query="", fragment="").geturl()
            progress(f"[juicy-honey] using requested archive url={canonical}")
            return [canonical]
        progress(f"[juicy-honey] requested source is not a monthly archive url={requested_source}")
        return []

    index_urls = (
        "https://juicy-honey.blog.jp/",
        "https://juicy-honey.blog.jp/archives/2026-08.html",
    )
    archive_urls: list[str] = []
    seen: set[str] = set()

    for index_url in index_urls:
        try:
            goto(page, index_url, wait_ms=500, timeout_ms=30000, attempts=2)
            values = page.eval_on_selector_all(
                ".plugin-monthly a[href*='/archives/'], "
                "#plugin-monthly-921569 a[href*='/archives/']",
                """els => els.map(a => ({
                    href: (a.href || '').trim(),
                    text: (a.innerText || a.textContent || '').replace(/\\s+/g, ' ').trim()
                }))""",
            )
        except Exception as exc:
            progress(
                f"[juicy-honey] archive sidebar read failed url={index_url} error={exc}"
            )
            continue

        for item in values:
            href = str(item.get("href") or "").strip()
            parsed = urlparse(href)
            if parsed.netloc.lower() != "juicy-honey.blog.jp":
                continue
            match = re.fullmatch(r"/archives/(20\d{2})-(\d{2})\.html", parsed.path)
            if not match:
                continue
            month = int(match.group(2))
            if not 1 <= month <= 12:
                continue
            canonical = parsed._replace(query="", fragment="").geturl()
            if canonical in seen:
                continue
            seen.add(canonical)
            archive_urls.append(canonical)

        if archive_urls:
            break

    archive_urls.sort(
        key=lambda value: tuple(
            int(part)
            for part in re.search(r"/(20\d{2})-(\d{2})\.html$", value).groups()
        ),
        reverse=True,
    )

    if max_months > 0:
        archive_urls = archive_urls[:max_months]

    progress(
        f"[juicy-honey] archive sidebar discovered count={len(archive_urls)}"
    )
    return archive_urls


def juicy_archive_pagination_url(value: str, archive_url: str) -> str:
    """Return a canonical monthly-archive page URL or an empty string.

    Livedoor paginates busy months with ``?p=N``. The previous discovery pass
    read only page one, which omitted release announcements whenever preview,
    sales, or event posts pushed them onto a later page.
    """
    candidate = urlparse(str(value or "").strip())
    archive = urlparse(str(archive_url or "").strip())
    if (
        candidate.netloc.lower() != "juicy-honey.blog.jp"
        or candidate.path != archive.path
    ):
        return ""
    match = re.search(r"(?:^|&)p=(\d+)(?:&|$)", candidate.query)
    if not match or int(match.group(1)) < 2:
        return ""
    return candidate._replace(query=f"p={int(match.group(1))}", fragment="").geturl()


def juicy_archive_article_candidates(
    page,
    archive_url: str,
    max_pages: int,
    visited_urls: set[str],
) -> tuple[list[tuple[str, str]], int]:
    pending_pages = [archive_url]
    seen_pages: set[str] = set()
    month_seen_urls: set[str] = set()
    article_candidates: list[tuple[str, str]] = []
    pages_scanned = 0

    while pending_pages and pages_scanned < max(1, max_pages):
        page_url = pending_pages.pop(0)
        if page_url in seen_pages:
            continue
        seen_pages.add(page_url)
        try:
            goto(page, page_url, wait_ms=250, timeout_ms=30000, attempts=2)
            page_links = links(page)
            pages_scanned += 1
        except Exception as exc:
            progress(
                f"[juicy-honey] archive page failed url={page_url} error={exc}"
            )
            continue

        for link in page_links:
            href = str(link.get("href") or "").strip()
            pagination_url = juicy_archive_pagination_url(href, archive_url)
            if pagination_url and pagination_url not in seen_pages:
                pending_pages.append(pagination_url)

            parsed = urlparse(href)
            if parsed.netloc.lower() != "juicy-honey.blog.jp":
                continue
            if not re.fullmatch(r"/archives/\d+\.html", parsed.path):
                continue
            if href.rstrip("/") == archive_url.rstrip("/"):
                continue

            canonical_url = parsed._replace(query="", fragment="").geturl()
            if canonical_url in month_seen_urls or canonical_url in visited_urls:
                continue
            month_seen_urls.add(canonical_url)

            text_value = clean_text(" ".join([
                str(link.get("text") or ""),
                str(link.get("title") or ""),
                str(link.get("alt") or ""),
            ]))
            if not (
                looks_like_juicy_article(text_value)
                or re.search(
                    r"(?:ラグジュアリー|デラックス|エクスクイジット|高級版|"
                    r"発売|発売決定|発売予定|予約開始)",
                    text_value,
                    re.I,
                )
            ):
                continue
            article_candidates.append((canonical_url, text_value))

    return article_candidates, pages_scanned


def discover_juicy(
    browser,
    max_months: int,
    empty_month_limit: int = 0,
    max_pages_per_month: int = 20,
    source_url: str = "",
) -> list[dict]:
    """Discover complete Juicy Honey releases from official blog articles.

    Archive titles are only candidate locators. Every candidate article is
    opened so release date, cast, JAN code, and canonical series identity can
    be read from the complete product block. Duplicate sales/preview posts are
    merged into one release, including model names found in different posts.
    """
    page = new_page(browser)
    best_by_identity: dict[str, dict] = {}
    visited_urls: set[str] = set()
    consecutive_empty_months = 0

    progress(
        "[juicy-honey] discovery started "
        f"maxMonths={max_months} emptyMonthLimit={empty_month_limit} "
        f"maxPagesPerMonth={max_pages_per_month} "
        "archiveSource=sidebar hydrate=true"
    )

    try:
        archive_urls = juicy_archive_urls_from_sidebar(page, max_months, source_url)
        if not archive_urls:
            progress(
                "[juicy-honey] no monthly archive links found in sidebar; "
                "discovery cannot continue"
            )
            return []

        for offset, archive_url in enumerate(archive_urls):
            archive_match = re.search(
                r"/archives/(20\d{2})-(\d{2})\.html$", archive_url
            )
            current_year = int(archive_match.group(1)) if archive_match else date.today().year
            progress(
                f"[juicy-honey] scanning {offset + 1}/{len(archive_urls)} "
                f"url={archive_url}"
            )

            article_candidates, pages_scanned = juicy_archive_article_candidates(
                page,
                archive_url,
                max_pages_per_month,
                visited_urls,
            )
            if pages_scanned == 0:
                consecutive_empty_months += 1
                progress(
                    f"[juicy-honey] archive failed url={archive_url} "
                    f"emptyStreak={consecutive_empty_months}"
                )
                if empty_month_limit > 0 and consecutive_empty_months >= empty_month_limit:
                    break
                continue

            month_found = 0
            for canonical_url, text_value in article_candidates:
                visited_urls.add(canonical_url)
                hydrated = hydrate_juicy_article(
                    page, canonical_url, text_value, current_year
                )
                if not hydrated:
                    continue

                article_releases = hydrated.get("releases") or [hydrated]
                for article_release in article_releases:
                    merge_juicy_discovery_candidate(best_by_identity, article_release)
                    month_found += 1

            consecutive_empty_months = 0 if month_found else consecutive_empty_months + 1
            progress(
                f"[juicy-honey] month complete url={archive_url} "
                f"pages={pages_scanned} articles={len(article_candidates)} matched={month_found} "
                f"unique={len(best_by_identity)} emptyStreak={consecutive_empty_months}"
            )
            if empty_month_limit > 0 and consecutive_empty_months >= empty_month_limit:
                break

        result = [entry["release"] for entry in best_by_identity.values()]
        for release in result:
            names = juicy_model_names(
                release.get("modelNames", []), release.get("modelName", "")
            )
            release["modelNames"] = names
            existing_profiles = merge_juicy_model_profiles(
                release.get("modelProfiles", release.get("models", []))
            )
            by_name = {normalize_text(item.get("name", "")): item for item in existing_profiles}
            profiles = [
                by_name.get(normalize_text(name), {"name": name, "originalName": name})
                for name in names
            ]
            release["models"] = profiles
            release["modelProfiles"] = profiles
            release["modelName"] = names[0] if names else ""
            release["articleImages"] = merge_article_images(
                release.get("articleImages", [])
            )
            if len(names) < 2:
                progress(
                    f"[juicy-honey] cast incomplete title={release.get('title', '')!r} "
                    f"models={names!r} source={release.get('sourceUrl', '')}"
                )

        # Deterministic chronological order. Missing release dates fall back to
        # article date, then series volume. Latest releases are returned first.
        result.sort(
            key=lambda item: (
                str(item.get("releaseDate") or item.get("articleDate") or "0000-00-00"),
                1 if str(item.get("title") or "").startswith("JUICY HONEY PLUS") else 0,
                int(item.get("volume") or 0),
                str(item.get("title") or ""),
            ),
            reverse=True,
        )
        for sequence, item in enumerate(result, start=1):
            item["releaseSequence"] = sequence
            item.pop("articleDate", None)

        progress(f"[juicy-honey] discovery completed releases={len(result)}")
        return result
    finally:
        close_quietly(page)


def discover_juicy_target(browser, source_url: str) -> list[dict]:
    """Hydrate exactly one Juicy Honey article from the catalog source URL."""
    source_url = str(source_url or "").strip()
    parsed = urlparse(source_url)
    if parsed.scheme not in {"http", "https"} or parsed.netloc.lower() != "juicy-honey.blog.jp":
        progress(f"[juicy-honey] targeted discovery rejected sourceUrl={source_url!r}")
        return []

    page = new_page(browser)
    try:
        hydrated = hydrate_juicy_article(page, source_url, source_url, date.today().year)
        if not hydrated:
            return []
        releases = []
        for sequence, item in enumerate(hydrated.get("releases") or [hydrated], start=1):
            release = item["release"]
            release["articleImages"] = merge_article_images(
                release.get("articleImages", [])
            )
            release.pop("articleDate", None)
            release["releaseSequence"] = sequence
            releases.append(release)
        progress(
            f"[juicy-honey] targeted discovery completed sourceUrl={page.url} "
            f"releases={len(releases)} titles={[item.get('title', '') for item in releases]!r}"
        )
        return releases
    finally:
        close_quietly(page)


def source_platform_for_url(raw_url: str) -> str:
    host = urlparse(str(raw_url or "")).netloc.lower()
    if host.endswith("gain-p.jp"):
        return "smile-gain"
    if host.endswith("toreca.biz"):
        return "produce216-site"
    if host.endswith("tic.jp"):
        return "tic-store"
    if host.endswith("jyu-toku.sakura.ne.jp"):
        return "jyutoku-site"
    if host.endswith("juicy-honey.blog.jp"):
        return "juicy-honey-blog"
    if host.endswith("mint-mall.net"):
        return "mint-mall"
    if host.endswith("suruga-ya.jp"):
        return "suruga-ya"
    if host.endswith("formosadreamers.com"):
        return "formosa-dreamers"
    if host.endswith("monkeys.rakuten.com.tw"):
        return "rakuten-monkeys"
    if host.endswith("rakuten.com.tw"):
        return "rakuten-taiwan"
    if host.endswith("ltn.com.tw"):
        return "ltn-press"
    if host.endswith("1collectibles.com"):
        return "1collectibles"
    if host.endswith("jjcs.com.tw"):
        return "jj-cards"
    if host.endswith("shopee.tw"):
        return "shopee-taiwan"
    if host.endswith("ruten.com.tw"):
        return "ruten-taiwan"
    return "unknown"


def resolve_actual_publisher(text: str, fallback: str) -> str:
    value = unicodedata.normalize("NFKC", clean_text(text)).lower()
    rules = (
        (("juicy honey", "ジューシーハニー", "havarossa"), "juicy-honey"),
        (("cj sexy", "cjセクシー"), "cj-sexy"),
        (("woohoo", "woo hoo"), "woohoo"),
        (("hit's", "hits limited", "ヒッツ"), "hits"),
        (("produce 216", "produce216", "プロデュース216"), "produce-216"),
        (("jyutoku", "jyu-toku", "ジュートク"), "jutoku"),
        (("maxim", "マキシム"), "maxim"),
        (("formosa sexy", "年度女孩卡", "福爾摩沙女孩卡"), "formosa-sexy"),
        (("rakuten girls", "樂天女孩卡", "樂天女孩"), "rakuten-girls"),
    )
    for markers, publisher_key in rules:
        if any(marker in value for marker in markers):
            return publisher_key
    return fallback


def extract_manufacturer(text: str) -> str:
    value = clean_text(text)
    match = re.search(
        r"(?:manufacturer|publisher|メーカー|発売元|製造元)\s*[:：]?\s*([^|｜\n]{2,80})",
        value,
        re.I,
    )
    return clean_text(match.group(1)) if match else ""


def candidate(publisher: str, title: str, source_url: str, volume: int | None, release_date: str, source_type: str, checklist_url: str) -> dict:
    title = clean_text(title)
    normalized_title = normalize_title(title, publisher, volume)
    model_name = extract_model(title, publisher)
    subtitle = "" if publisher in {"cj-sexy", "woohoo"} else extract_subtitle(title, publisher)
    if publisher == "woohoo" and volume and normalized_title.startswith(("~", "〜", "～")):
        subtitle = f"WooHoo Girls Vol. {volume}"
    model_names = [model_name] if model_name else []
    source_confidence = {
        "trusted_retailer": "trusted_retailer",
        "marketplace_listing": "inferred",
    }.get(source_type, "official_text")
    return {
        "publisherKey": publisher,
        "sourcePlatformKey": source_platform_for_url(source_url),
        "seriesKey": publisher,
        "editionKey": "",
        "title": normalized_title,
        "originalTitle": title,
        "subtitle": subtitle,
        "modelName": model_name,
        "modelNames": model_names,
        "models": [{"name": model_name, "originalName": model_name}] if model_name else [],
        "volume": volume,
        "releaseDate": release_date,
        "janCode": extract_jan(title),
        "sourceUrl": source_url,
        "sourceType": source_type,
        "sourceConfidence": source_confidence,
        "checklistUrl": checklist_url,
        "contentRating": "restricted_18_plus" if publisher in {"cj-sexy", "juicy-honey", "jutoku"} else "general",
    }


def dedupe_releases(items: list[dict]) -> list[dict]:
    result = []
    seen = set()
    for item in items:
        source_url = item.get("sourceUrl") or ""
        if source_url and int(item.get("sourceReleaseCount") or 0) > 1:
            key = "|".join([
                source_url,
                item.get("seriesKey", ""),
                item.get("editionKey", ""),
                str(item.get("volume") or ""),
                item.get("title", ""),
            ])
        else:
            key = source_url or "|".join([item.get("publisherKey", ""), item.get("title", ""), item.get("releaseDate", "")])
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def normalize_title(title: str, publisher: str, volume: int | None) -> str:
    if publisher == "cj-sexy" and volume:
        model_name = extract_model(title, publisher)
        subtitle = extract_subtitle(title, publisher)
        if model_name:
            subtitle = re.sub(r"^\s*" + re.escape(model_name), "", subtitle, flags=re.I)
        subtitle = subtitle.strip(" ~|\u301c\uff5e")
        value = f"CJ SEXY CARD SERIES VOL.{volume}"
        if subtitle:
            value += f" \uff5e{subtitle}\uff5e"
        if model_name:
            value = f"{model_name} {value}"
        return value
    if publisher == "woohoo" and volume:
        return woohoo_series_name(title) or f"WooHoo Girls Vol. {volume}"
    if publisher == "juicy-honey":
        return normalize_juicy_title(title)
    return clean_text(title)


def extract_volume(text: str) -> int | None:
    for pattern in VOLUME_PATTERNS:
        match = pattern.search(text)
        if match:
            return int(match.group(1))
    match = re.search(r"\b(?:CJ\s+SEXY[^0-9]{0,20}|CJ\s*カード[^0-9]{0,20})(\d{1,4})\b", text, re.I)
    return int(match.group(1)) if match else None


def extract_date(text: str) -> str:
    match = DATE_PATTERN.search(text)
    if not match:
        return ""
    day = match.group(3)
    if not day:
        return f"{int(match.group(1)):04d}-{int(match.group(2)):02d}"
    return f"{int(match.group(1)):04d}-{int(match.group(2)):02d}-{int(day):02d}"


def extract_model(text: str, publisher: str) -> str:
    if publisher == "cj-sexy":
        marker = re.search(r"\bCJ\s+SEXY\b", text, re.I)
        if marker:
            value = clean_text(text[:marker.start()])
            value = re.sub(r"^\u5546\u54c1\u60c5\u5831\s*", "", value, flags=re.I)
            return clean_text(value.split()[-1]) if value else ""
        match = re.search(r"^(.+?)\s+(?:CJ\s+SEXY|CJ\s*カード)", text, re.I)
        if match:
            value = clean_text(match.group(1))
            value = re.sub(r"^(?:\u5546\u54c1\u60c5\u5831|å•†å“æƒ…å ±)\s*", "", value, flags=re.I)
            return clean_text(value)
    if publisher == "woohoo":
        marker = re.search(r"\bwoohoo\s+girls\s+vol\.?\s*\d+\b", text, re.I)
        values = [text[:marker.start()], text[marker.end():]] if marker else [text]
        for value in values:
            model_name = normalize_woohoo_model_name(value)
            if model_name:
                return model_name
        return ""
    if publisher == "juicy-honey":
        return extract_juicy_models(text)
    value = re.split(r"(?:トレーディングカード|trading card|トレカ)", text, flags=re.I)[0]
    value = re.sub(r"^(?:商品情報|new|発売予定)\s*", "", value, flags=re.I)
    return clean_text(value) if len(clean_text(value)) <= 80 else ""


def extract_subtitle(text: str, publisher: str) -> str:
    match = re.search(r"[～~|]\s*(.+?)(?:\s+(?:発売|release)|$)", text, re.I)
    return clean_text(match.group(1)) if match else ""


WOOHOO_SERIES_NAME_PATTERN = re.compile(r"[~〜～]\s*([^~〜～|]+?)\s*[~〜～]")


def woohoo_series_name(value: str) -> str:
    match = WOOHOO_SERIES_NAME_PATTERN.search(str(value or ""))
    if not match:
        return ""
    name = clean_text(match.group(1))
    return f"～{name}～" if name else ""


def woohoo_product_series_name(page) -> str:
    values = []
    try:
        values.append(page.title())
    except Exception:
        pass
    try:
        values.append(page.locator("body").inner_text(timeout=10000))
    except Exception:
        pass
    for value in values:
        if name := woohoo_series_name(value):
            return name
    return ""


def normalize_woohoo_model_name(value: str) -> str:
    value = DATE_PATTERN.sub(" ", str(value or ""))
    value = re.sub(r"\b20\d{2}\s*[-/.]\s*\d{1,2}(?:\s*[-/.]\s*\d{1,2})?\b", " ", value)
    # The official title index puts the volume before the performer, while
    # product pages put it after the performer. Neither belongs in the model
    # identity used for matching or persistence.
    value = re.sub(r"\b(?:vol(?:ume)?\.?|第)\s*\d{1,4}(?:\s*弾)?\b", " ", value, flags=re.I)
    value = re.split(r"[~〜～|]", value, maxsplit=1)[0]
    value = re.sub(r"^(?:商品情報|new)\s*", "", value, flags=re.I)
    value = re.sub(r"(?:発売予定|発売日|発売|release(?:\s+date)?)", " ", value, flags=re.I)
    return clean_text(value).strip(" -—–|:")


def extract_jan(text: str) -> str:
    match = re.search(r"(?:JAN|UPC)[^0-9]{0,10}(\d{8,14})", text, re.I)
    return match.group(1) if match else ""


def looks_like_tic_release(text: str) -> bool:
    lowered = text.lower()
    return any(token in lowered for token in ("トレカ", "trading card", "ファースト", "vol.", "vol", "～"))


def looks_like_juicy_release(text: str) -> bool:
    return looks_like_juicy_release_announcement(text)

CODE_PATTERN = re.compile(r"(?<![A-Za-z0-9])(?:[A-Z]{1,8}[- ]?\d{1,4}|#\s*\d{1,4})(?![A-Za-z0-9])")


NUMBER_PATTERN = re.compile(
    r"(?:#|(?:no\.?|card\s*(?:no\.?|number)?)[\s:.-]*)\s*(\d{1,3})(?![A-Za-z0-9])",
    re.IGNORECASE,
)


IGNORE_WORDS = ("price", "yen", "release", "volume", "vol", "date", "202", "copyright")


COMPOSITION_KIND = "composition"


PREVIEW_KIND = "preview"


def is_reference_entry_kind(value: str) -> bool:
    return str(value or "").strip().lower() in {PREVIEW_KIND, "card_preview", "reference_preview"}


MAJOR_GROUP_WORDS = (
    "regular card", "rare card", "special card", "super rare", "premium rare",
    "double rare", "triple rare", "masterpiece", "insert card", "premium insert",
    "レギュラーカード", "レアカード", "スーパーレア", "プレミアム",
)


def build_terms(request: dict) -> list[str]:
    raw_terms = list(request.get("matchTerms") or [])
    raw_terms.extend([request.get("title", ""), request.get("subtitle", "")])
    volume = request.get("volume")
    if volume:
        raw_terms.extend([f"vol.{volume}", f"vol. {volume}", f"vol{volume}", f"volume {volume}"])
    terms = []
    for value in raw_terms:
        normalized = normalize_text(str(value))
        if not normalized:
            continue
        split_variants = [part.strip() for part in re.split(r"[～~|]", normalized) if len(part.strip()) >= 2]
        for variant in (normalized, normalized.replace("-", " "), *split_variants):
            variant = normalize_text(variant)
            if variant and variant not in terms:
                terms.append(variant)
    return terms


def term_matches(term: str, text: str) -> bool:
    if not term:
        return False
    if term[-1].isdigit():
        return re.search(re.escape(term) + r"(?!\d)", text) is not None
    return term in text


def is_release_signal(term: str) -> bool:
    return any(character.isdigit() or ord(character) > 127 for character in term)


def resolve_release_page(page, source_url: str, terms: list[str]) -> bool:
    parsed = urlparse(source_url)
    path = parsed.path.lower()
    if parsed.netloc.lower().endswith("gain-p.jp") and re.search(r"/user_data/[^/]*(?:checklist|check_list)[^/]*$", path, re.IGNORECASE):
        return True
    if "/archives/" in path or "/view/item/" in path:
        return True
    if "/jyu-toku/" in path and "/category/release" not in path:
        return True
    if parsed.netloc.lower().endswith("tic.jp") and "/products/list" in path:
        return True

    def find_matching_link() -> tuple[str, int]:
        links = page.eval_on_selector_all(
            "a[href]",
            """els => els.map(a => ({
                href: a.href,
                text: (a.innerText || a.textContent || '').trim(),
                alt: (a.querySelector('img')?.alt || '').trim()
            }))""",
        )
        source_host = parsed.netloc.lower()
        best_url = ""
        best_score = 0
        for link in links:
            href = link.get("href", "")
            if not href.startswith(("http://", "https://")):
                continue
            if urlparse(href).netloc.lower() != source_host:
                continue
            haystack = normalize_text(f"{link.get('text', '')} {link.get('alt', '')} {href}")
            matched_terms = [term for term in terms if len(term) >= 2 and term_matches(term, haystack)]
            if not any(is_release_signal(term) for term in matched_terms):
                continue
            score = len(matched_terms) * 3
            if "vol." in haystack or "trading" in haystack or "card" in haystack:
                score += 1
            if score > best_score:
                best_score = score
                best_url = href
        return best_url, best_score

    best_url, best_score = find_matching_link()
    if best_url and best_score >= 3 and best_url.rstrip("/") != source_url.rstrip("/"):
        page.goto(best_url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(1200)
        return True

    if parsed.netloc.lower() == "jyu-toku.sakura.ne.jp" and "/category/release" in path:
        archive_root = source_url.rstrip("/")
        for page_number in range(2, 35):
            page.goto(f"{archive_root}/page/{page_number}/", wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(600)
            best_url, best_score = find_matching_link()
            if best_url and best_score >= 3:
                page.goto(best_url, wait_until="domcontentloaded", timeout=60000)
                page.wait_for_timeout(1200)
                return True
    return False


def extract_candidate_rows(page) -> list[dict]:
    return page.eval_on_selector_all(
        "main table tr, main li, main article, main p, main div, article table tr, article li, article p",
        """els => els.map((el, index) => ({
            index,
            text: (el.innerText || el.textContent || '').replace(/\\s+/g, ' ').trim(),
            imageUrl: (el.querySelector('img')?.currentSrc || el.querySelector('img')?.src || el.querySelector('img')?.dataset?.src || el.querySelector('img')?.dataset?.original || '').trim(),
            altText: (el.querySelector('img')?.alt || '').trim()
        })).filter(item => item.text.length > 0 && item.text.length < 500)""",
    )


def resolve_gain_checklist_page(page, terms: list[str]) -> bool:
    parsed = urlparse(page.url)
    if parsed.netloc.lower().endswith("gain-p.jp") and re.search(r"/user_data/[^/]*checklist[^/]*$", parsed.path, re.IGNORECASE):
        return True
    page.goto("https://gain-p.jp/user_data/check_list", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(800)
    links = page.eval_on_selector_all(
        "a.cg_titlelist_link[href], a[href*='_checklist']",
        """els => els.map(a => ({
            href: a.href,
            text: (a.querySelector('.cg_titlelist_name')?.innerText || a.innerText || a.textContent || '').replace(/\\s+/g, ' ').trim()
        }))""",
    )
    checklist_links = [
        link for link in links
        if "gain-p.jp/user_data/" in str(link.get("href") or "")
        and re.search(r"(?:checklist|check_list)", str(link.get("href") or ""), re.IGNORECASE)
    ]
    volume = requested_volume(terms)
    if volume:
        # Prefer an explicit volume marker when the publisher includes one in
        # the link text or URL (Vol-2, Vol.2, and Vol. 2 are all accepted).
        for link in checklist_links:
            if requested_volume([str(link.get("text") or ""), str(link.get("href") or "")]) == volume:
                page.goto(link["href"], wait_until="domcontentloaded", timeout=60000)
                page.wait_for_timeout(800)
                return True
        # A few historical WooHoo checklist links have intermittently been
        # omitted from the index DOM returned by the browser. Keep their
        # verified direct paths as a fallback instead of relying on position.
        direct_slug = {
            3: "fubuki_checklist",
            9: "sanada_checklist",
            12: "hanai_checklist",
            18: "noumi_checklist",
        }.get(volume)
        if direct_slug:
            page.goto(
                f"https://gain-p.jp/user_data/{direct_slug}",
                wait_until="domcontentloaded",
                timeout=60000,
            )
            page.wait_for_timeout(800)
            return True
        if volume <= len(checklist_links):
            # The current official index is displayed newest-first: Vol. 12, ..., Vol. 1.
            page.goto(checklist_links[len(checklist_links) - volume]["href"], wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(800)
            return True
    best_url = ""
    best_score = 0
    for link in links:
        href = str(link.get("href") or "")
        if "gain-p.jp/user_data/" not in href or not re.search(r"(?:checklist|check_list)", href, re.IGNORECASE):
            continue
        haystack = normalize_text(f"{link.get('text', '')} {href}")
        compact_haystack = re.sub(r"\s+", "", haystack)
        score = 0
        for term in terms:
            normalized = normalize_text(term)
            if len(normalized) < 2:
                continue
            compact_term = re.sub(r"\s+", "", normalized)
            exact_match = term_matches(normalized, haystack)
            compact_match = not normalized[-1].isdigit() and compact_term in compact_haystack
            if exact_match or compact_match:
                score += 3 if is_release_signal(normalized) else 1
        if score > best_score:
            best_score = score
            best_url = href
    if not best_url or best_score < 3:
        return False
    page.goto(best_url, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(800)
    return True


def requested_volume(terms: list[str]) -> int:
    for term in terms:
        normalized = normalize_text(term)
        match = re.search(r"\bvol(?:ume)?\s*[-.]?\s*(\d{1,3})\b", normalized, re.IGNORECASE)
        if not match:
            match = re.search(r"woohoo[- ]girls[- ]vol(?:ume)?[-.]?\s*(\d{1,3})\b", normalized, re.IGNORECASE)
        if match:
            return int(match.group(1))
    return 0


def extract_checklist_images(page) -> list[dict]:
    selector = ".ec-role img, main img, .ec-layoutRole__main img"
    page.eval_on_selector_all(
        selector,
        """els => els.forEach(img => {
            img.loading = 'eager';
            if (img.dataset?.original && !img.getAttribute('src')) img.src = img.dataset.original;
            if (img.dataset?.src && !img.getAttribute('src')) img.src = img.dataset.src;
            img.scrollIntoView({block: 'center'});
        })""",
    )
    page.wait_for_timeout(1200)
    images = page.eval_on_selector_all(
        selector,
        """els => els.map(img => {
            const link = img.closest('a[href]');
            const candidates = [
                link?.href,
                img.dataset?.original,
                img.dataset?.src,
                img.dataset?.lazySrc,
                img.currentSrc,
                img.src
            ].filter(Boolean);
            const originalUrl = candidates.find(value => /(?:check|sheet|list)/i.test(value) && /\\.(?:jpe?g|png|webp|gif)(?:[?#].*)?$/i.test(value))
                || candidates.find(value => /\\.(?:jpe?g|png|webp|gif)(?:[?#].*)?$/i.test(value))
                || candidates[0]
                || '';
            return {
                originalUrl: originalUrl.trim(),
                altText: (img.alt || '').trim(),
                width: img.naturalWidth || Number(img.getAttribute('width')) || 0,
                height: img.naturalHeight || Number(img.getAttribute('height')) || 0
            };
        }).filter(item => item.originalUrl)""",
    )
    seen = set()
    result = []
    blocked_asset_words = (
        "box", "logo", "banner", "bnr", "button", "icon", "header", "footer", "thumb",
    )
    for item in images:
        url = str(item.get("originalUrl") or "").strip()
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            continue
        normalized_path = parsed.path.lower()
        if not re.search(r"\.(?:jpe?g|png|webp|gif)$", normalized_path, re.IGNORECASE):
            continue
        if any(word in normalized_path for word in blocked_asset_words):
            continue
        canonical_url = parsed._replace(query="", fragment="").geturl()
        if canonical_url in seen:
            continue
        seen.add(canonical_url)
        item["originalUrl"] = canonical_url
        result.append(item)
    return result


def extract_woohoo_product_checklist_images(page) -> list[dict]:
    """Extract the composition sheet published on a WooHoo product page.

    Gain-P sometimes publishes a product page before adding the release to its
    separate checklist index. Those product pages still contain the full
    composition sheet, conventionally named ``*900.jpg`` (for example
    ``amano900.jpg``). Keep this fallback narrowly scoped so product covers,
    banners, and individual card thumbnails are not mistaken for a checklist.
    """
    selector = ".ec-role img, main img, .ec-layoutRole__main img"
    page.eval_on_selector_all(
        selector,
        """els => els.forEach(img => {
            img.loading = 'eager';
            if (img.dataset?.original && !img.getAttribute('src')) img.src = img.dataset.original;
            if (img.dataset?.src && !img.getAttribute('src')) img.src = img.dataset.src;
            img.scrollIntoView({block: 'center'});
        })""",
    )
    page.wait_for_timeout(600)
    images = page.eval_on_selector_all(
        selector,
        """els => els.map(img => {
            const link = img.closest('a[href]');
            const candidates = [
                link?.href,
                img.dataset?.original,
                img.dataset?.src,
                img.dataset?.lazySrc,
                img.currentSrc,
                img.src
            ].filter(Boolean);
            const imageUrl = candidates.find(value => {
                try {
                    const path = new URL(value, document.baseURI).pathname;
                    const filename = path.split('/').pop() || '';
                    return /(?:check(?:list)?|list|900)(?:[_-]?\\d+)?\\.(?:jpe?g|png|webp|gif)$/i.test(filename);
                } catch (_) {
                    return false;
                }
            }) || '';
            return {
                originalUrl: imageUrl.trim(),
                altText: (img.alt || img.title || '').trim(),
                width: img.naturalWidth || Number(img.getAttribute('width')) || 0,
                height: img.naturalHeight || Number(img.getAttribute('height')) || 0
            };
        }).filter(item => item.originalUrl)""",
    )
    seen = set()
    result = []
    for item in images:
        url = str(item.get("originalUrl") or "").strip()
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"}:
            continue
        if not parsed.netloc.lower().endswith("gain-p.jp"):
            continue
        if not re.search(r"\.(?:jpe?g|png|webp|gif)$", parsed.path, re.IGNORECASE):
            continue
        canonical_url = parsed._replace(query="", fragment="").geturl()
        if canonical_url in seen:
            continue
        seen.add(canonical_url)
        item["originalUrl"] = canonical_url
        result.append(item)
    return result


def extract_jyutoku_composition_images(page) -> list[dict]:
    """Extract composition sheets embedded in a JYUTOKU release article.

    JYUTOKU's older release pages usually publish the composition as an image
    in ``.entry-content`` rather than as selectable HTML text.  The image is
    commonly wrapped in an anchor whose href is the full-size asset, so prefer
    that URL over the rendered thumbnail.  Restricting the selector to article
    content keeps the page hero, related releases, and site chrome out of the
    checklist evidence.
    """
    selector = ".entry-content img, .article .entry-content img, .article-body img"
    page.eval_on_selector_all(
        selector,
        """els => els.forEach(img => {
            img.loading = 'eager';
            if (img.dataset?.original && !img.getAttribute('src')) img.src = img.dataset.original;
            if (img.dataset?.src && !img.getAttribute('src')) img.src = img.dataset.src;
            img.scrollIntoView({block: 'center'});
        })""",
    )
    page.wait_for_timeout(600)
    images = page.eval_on_selector_all(
        selector,
        """els => els.map(img => {
            const link = img.closest('a[href]');
            const candidates = [
                link?.href,
                img.dataset?.original,
                img.dataset?.src,
                img.dataset?.lazySrc,
                img.currentSrc,
                img.src
            ].filter(Boolean);
            const originalUrl = candidates.find(value => {
                try {
                    return /\\.(?:jpe?g|png|webp|gif)(?:[?#].*)?$/i.test(new URL(value, document.baseURI).pathname);
                } catch (_) {
                    return false;
                }
            }) || candidates[0] || '';
            return {
                originalUrl: originalUrl.trim(),
                altText: (img.alt || img.title || '').trim(),
                linked: Boolean(link?.href && originalUrl === link.href),
                width: img.naturalWidth || Number(img.getAttribute('width')) || 0,
                height: img.naturalHeight || Number(img.getAttribute('height')) || 0
            };
        }).filter(item => item.originalUrl)""",
    )
    page_host = urlparse(page.url).netloc.lower()
    seen = set()
    result = []
    blocked_asset_words = (
        "logo", "banner", "bnr", "button", "icon", "header", "footer",
        "avatar", "profile", "related", "navigation", "placeholder",
    )
    for item in images:
        raw_url = str(item.get("originalUrl") or "").strip()
        parsed = urlparse(urljoin(page.url, raw_url))
        if parsed.scheme not in {"http", "https"}:
            continue
        if page_host and parsed.netloc.lower() != page_host:
            continue
        if not re.search(r"\.(?:jpe?g|png|webp|gif)$", parsed.path, re.IGNORECASE):
            continue
        if any(word in parsed.path.lower() for word in blocked_asset_words):
            continue
        width = int(item.get("width") or 0)
        height = int(item.get("height") or 0)
        # A linked full-size asset may be rendered through a small thumbnail;
        # only reject undersized files when the source itself is not linked.
        if not item.get("linked") and ((width and width < 240) or (height and height < 180)):
            continue
        canonical_url = parsed._replace(query="", fragment="").geturl()
        if canonical_url in seen:
            continue
        seen.add(canonical_url)
        result.append({
            "originalUrl": canonical_url,
            "altText": str(item.get("altText") or "").strip(),
            "width": width,
            "height": height,
        })
    return result


SURUGA_CARD_CODE_PATTERN = re.compile(
    r"(?<![A-Za-z0-9])([A-Za-z]{1,6}(?:\s*[-‐‑‒–—]\s*\d{1,4}|\s*\d{1,4})|\d{1,4})\s*[\[［]",
    re.I,
)


def suruga_card_query(release: dict) -> str:
    """Build a narrow Suruga-ya query for one CJ SEXY volume."""
    volume = release.get("volume")
    try:
        volume = int(volume) if volume else 0
    except (TypeError, ValueError):
        volume = 0
    if volume > 0:
        return f"CJ SEXY CARD SERIES VOL.{volume}"
    title = clean_text(release.get("title") or release.get("originalTitle") or "")
    return title or "CJ SEXY CARD SERIES"


def suruga_card_queries(release: dict) -> list[str]:
    """Return volume-first and release-identity Suruga-ya queries.

    Suruga-ya uses two naming schemes for CJ SEXY sets. Older rows include
    ``CJ SEXY CARD SERIES VOL.N`` while newer/renamed rows use the model and
    release subtitle only. Try both without ever widening to an unscoped CJ
    search.
    """
    values = [suruga_card_query(release)]
    model_values = [release.get("modelName")]
    if isinstance(release.get("modelNames"), list):
        model_values.extend(release.get("modelNames") or [])
    model_values.extend(suruga_release_identity_terms(release))

    models: list[str] = []
    for raw in model_values:
        value = clean_text(raw)
        if value and value not in models:
            models.append(value)

    def append_query(raw: str) -> None:
        query = clean_text(raw)
        if query and query not in values:
            values.append(query)

    # Suruga's newer titles use "<model> オフィシャルカードコレクション
    # <subtitle>" and omit both CJ and the volume. A CJ prefix therefore
    # makes its AND-style search return no rows.
    subtitle = clean_text(release.get("subtitle") or "")
    if subtitle:
        for model in models:
            append_query(f"{model} {subtitle}")
        append_query(subtitle)
    for model in models:
        append_query(f"{model} オフィシャルカードコレクション")
    for model in models:
        append_query(model)
    return values


def suruga_release_identity_terms(release: dict) -> list[str]:
    """Extract retailer-searchable model names from a release identity.

    Older CJ SEXY Suruga-ya rows omit ``VOL.N`` and use the model's name
    instead. Some seeded CJ releases have an empty subtitle, but their
    official JYUTOKU URL contains the model name before the ``cj-sexy`` slug.
    Decode that URL segment so a volume-only command can still find the
    retailer rows without importing official card media.
    """
    values: list[str] = []
    for key in ("sourceUrl", "checklistUrl"):
        raw_url = str(release.get(key) or "").strip()
        if not raw_url:
            continue
        segment = unquote(urlparse(raw_url).path.rstrip("/").rsplit("/", 1)[-1])
        marker = re.search(r"cj[\s_-]*sexy", segment, re.I)
        if not marker:
            continue
        prefix = clean_text(segment[:marker.start()]).strip(" -_/")
        if prefix and len(prefix) <= 80:
            values.append(prefix)
    return values


def suruga_row_matches_release(raw_text: str, release: dict) -> bool:
    """Check a Suruga-ya row against the requested CJ SEXY release."""
    normalized = normalize_text(raw_text)
    volume = release.get("volume")
    try:
        volume = int(volume) if volume else 0
    except (TypeError, ValueError):
        volume = 0
    if volume <= 0:
        return True

    # The legacy naming scheme embeds the volume in every product title.
    volume_match = re.search(r"cj\s*(?:sexy\s*card\s*series)?\s*vol(?:ume)?\.?\s*0*(\d+)", normalized, re.I)
    if volume_match:
        return int(volume_match.group(1)) == volume

    # Current Suruga-ya rows omit VOL.N. Prefer the release subtitle because
    # the same model can have several CJ volumes on Suruga-ya.
    subtitle = normalize_text(release.get("subtitle"))
    if subtitle and len(subtitle) >= 3:
        return subtitle in normalized

    identity_values = [release.get("modelName")]
    identity_values.extend(suruga_release_identity_terms(release))
    for raw in identity_values:
        token = normalize_text(raw)
        if token and len(token) >= 3 and token in normalized:
            return True
    model_names = release.get("modelNames")
    if isinstance(model_names, list):
        for raw in model_names:
            token = normalize_text(raw)
            if token and len(token) >= 3 and token in normalized:
                return True
    return False


def suruga_search_url(query: str, page_number: int, buy_search: bool = False) -> str:
    params = {
        "category": "50108032503" if buy_search else "",
        "search_word": query,
        "adult_s": "3",
        "adult_t": "On",
    }
    if page_number > 1:
        params["page"] = page_number
    path = "/kaitori/search_buy" if buy_search else "/search"
    return "https://www.suruga-ya.jp" + path + "?" + urlencode(params)


def suruga_index_search_url(query: str, page_number: int) -> str:
    """Build the Yahoo Japan fallback URL for Suruga-indexed product rows."""
    params = {
        "p": f"site:suruga-ya.jp/product {query}",
        "n": 100,
        "ei": "UTF-8",
    }
    if page_number > 1:
        params["b"] = 1 + ((page_number - 1) * 10)
    return "https://search.yahoo.co.jp/search?" + urlencode(params)


def suruga_product_image_url(source_url: str) -> str:
    """Derive Suruga's public product image URL from its management code."""
    parsed = urlparse(str(source_url or "").strip())
    product_code = parsed.path.rstrip("/").rsplit("/", 1)[-1]
    if not re.fullmatch(r"[A-Za-z0-9_-]{4,40}", product_code):
        return ""
    # Suruga's CDN paths are case-sensitive even though product detail URLs
    # expose management codes in uppercase (for example ``G3918815``).  The
    # uppercase path is redirected/blocked, while the lowercase CDN path
    # serves the image directly.
    product_code = product_code.lower()
    return f"https://cdn.suruga-ya.jp/database/pics_webp/game/{product_code}.jpg.webp"


def normalize_suruga_image_url(image_url: str) -> str:
    """Canonicalize a Suruga image URL so its case-sensitive CDN path works.

    Search result markup can contain an uppercase management code even when
    the CDN only serves the lowercase path. Keep the source host when it is
    not a Suruga image, but normalize both the CDN and origin Suruga hosts.
    """
    value = str(image_url or "").strip()
    if not value or not value.startswith(("http://", "https://")):
        return ""
    parsed = urlparse(value)
    host = parsed.netloc.lower()
    if not host.endswith("suruga-ya.jp"):
        return value
    match = re.fullmatch(
        r"(/database/pics_webp/game/)([A-Za-z0-9_-]{4,40})(\.jpg(?:\.webp)?)",
        parsed.path,
        re.I,
    )
    if not match:
        return value
    normalized_path = f"{match.group(1)}{match.group(2).lower()}{match.group(3).lower()}"
    # Prefer the CDN host. The www origin redirects the same request through
    # the protected storefront, while the CDN serves the public image object.
    return parsed._replace(netloc="cdn.suruga-ya.jp", path=normalized_path).geturl()


def suruga_search_is_blocked(page) -> bool:
    """Detect the Cloudflare verification page returned to server browsers."""
    try:
        title = normalize_text(page.title())
        body = normalize_text(page.locator("body").inner_text(timeout=3000))
    except Exception:
        return False
    return (
        "just a moment" in title
        or "performing security verification" in body
        or ("cloudflare" in body and "verify" in body)
    )


def parse_suruga_card_row(row: dict, release: dict) -> dict | None:
    """Normalize one Suruga-ya result into the existing card-design contract."""
    raw_text = clean_text(row.get("text") or row.get("title") or "")
    if not raw_text or not re.search(
        r"(?:\bCJ\b|オフィシャルカード|official\s+card|カード)",
        raw_text,
        re.I,
    ):
        return None
    volume = release.get("volume")
    try:
        volume = int(volume) if volume else 0
    except (TypeError, ValueError):
        volume = 0
    if volume > 0:
        if not suruga_row_matches_release(raw_text, release):
            return None
    match = SURUGA_CARD_CODE_PATTERN.search(raw_text)
    if not match:
        return None
    code = re.sub(r"\s+", "", match.group(1)).upper()
    if code in {"2020", "2021", "2022", "2023", "2024", "2025", "2026"}:
        return None
    bracket = re.search(r"[\[［]([^\]］]{1,120})[\]］]", raw_text[match.start():])
    rarity = clean_text(bracket.group(1)) if bracket else ""
    image_url = str(row.get("imageUrl") or "").strip()
    source_url = str(row.get("href") or row.get("sourceUrl") or "").strip()
    if image_url:
        image_url = urljoin(source_url or "https://www.suruga-ya.jp/", image_url)
        image_url = normalize_suruga_image_url(image_url)
    # Suruga lazy-loads thumbnails with a data-URI placeholder before the
    # browser has loaded the real image. Fall back to the management-code URL
    # whenever the captured value is not a usable HTTP image URL.
    if not image_url:
        image_url = suruga_product_image_url(source_url)
    if source_url and not source_url.startswith(("http://", "https://")):
        source_url = urljoin("https://www.suruga-ya.jp/", source_url)
    title = clean_text(raw_text[match.start():])
    return {
        "cardCode": code,
        "entryKind": "card",
        "title": title,
        "description": raw_text[:480],
        "rarityLabel": rarity,
        "checklistSequence": 0,
        "imageUrl": image_url,
        "altText": clean_text(row.get("altText") or title),
        "sourceUrl": source_url,
        "sourceConfidence": "trusted_retailer",
    }


def scrape_suruga_cj_cards_from_index(
    page,
    release: dict,
    max_cards: int,
    queries: list[str],
) -> tuple[list[dict], list[str]]:
    """Read Suruga product rows from Yahoo Japan when Suruga blocks search.

    Yahoo's result links still point to Suruga and expose Suruga's product
    title and management code. This is a discovery fallback only; every saved
    source and image URL remains on a Suruga domain.
    """
    parsed_items: list[dict] = []
    seen_codes: set[str] = set()
    seen_urls: set[str] = set()
    warnings: list[str] = []
    max_pages = max(1, min(20, (max_cards + 9) // 10 + 2))
    subtitle = clean_text(release.get("subtitle") or "")
    index_queries: list[str] = []

    def append_index_query(raw: str) -> None:
        query = clean_text(raw)
        if query and query not in index_queries:
            index_queries.append(query)

    if subtitle:
        subtitle_queries = [
            query for query in queries
            if normalize_text(subtitle) in normalize_text(query)
        ]
        for query in subtitle_queries:
            append_index_query(query)
        base_query = subtitle_queries[0] if subtitle_queries else subtitle
        # Yahoo exposes different Suruga products for rarity-specific searches.
        # These labels cover CJ's published composition families without
        # inventing card rows or accepting results from another collection.
        for label in (
            "レギュラーカード",
            "箔押しサインカード",
            "直筆サインカード",
            "ランジェリーカード",
            "コスチュームカード",
            "フォトカード",
            "キスカード",
            "メッセージカード",
            "ビキニカード",
            "ストッキングカード",
            "ガーターベルトカード",
            "1of1カード",
            "チェキ",
            "特典カード",
        ):
            append_index_query(f"{base_query} {label}")
    else:
        for query in queries:
            append_index_query(query)

    for query_index, query in enumerate(index_queries):
        page_limit = max_pages if query_index < 2 else min(3, max_pages)
        for page_number in range(1, page_limit + 1):
            search_url = suruga_index_search_url(query, page_number)
            try:
                goto(page, search_url, wait_ms=900, timeout_ms=60000, attempts=2)
                rows = page.eval_on_selector_all(
                    "a[href*='suruga-ya.jp/product/'], a[href*='suruga-ya.jp/kaitori/']",
                    """els => els.map(a => {
                        const root = a.closest('section, article, li') || a;
                        return {
                            href: a.href,
                            text: (root.innerText || root.textContent || a.innerText || '').replace(/\\s+/g, ' ').trim(),
                            altText: (a.innerText || a.textContent || '').replace(/\\s+/g, ' ').trim()
                        };
                    }).filter(item => item.href && item.text)""",
                )
            except Exception as exc:
                warnings.append(
                    f"Suruga-ya index fallback failed ({query}, page {page_number}): {exc}"
                )
                break
            if not rows:
                break

            new_urls = 0
            for row in rows:
                source_url = str(row.get("href") or "").strip()
                if source_url in seen_urls:
                    continue
                seen_urls.add(source_url)
                new_urls += 1
                if subtitle:
                    row["text"] = clean_text(f"{row.get('text') or ''} {subtitle}")
                item = parse_suruga_card_row(row, release)
                if not item or item["cardCode"] in seen_codes:
                    continue
                seen_codes.add(item["cardCode"])
                item["checklistSequence"] = len(parsed_items) + 1
                parsed_items.append(item)
                if len(parsed_items) >= max_cards:
                    break
            if len(parsed_items) >= max_cards or new_urls == 0:
                break
        if len(parsed_items) >= max_cards:
            break

    if parsed_items:
        warnings.append(
            "Suruga-ya search was blocked by Cloudflare; "
            f"used Yahoo Japan's Suruga index and found {len(parsed_items)} card listings"
        )
    else:
        warnings.append(
            "Suruga-ya search was blocked by Cloudflare and its public index returned no card rows"
        )
    return parsed_items[:max_cards], warnings


def scrape_suruga_cj_cards(browser, release: dict, max_cards: int) -> tuple[list[dict], list[str]]:
    """Search Suruga-ya for individual CJ SEXY card listings.

    The normal product search is preferred. The buy-search index is a useful
    fallback for sold-out adult listings, which are often omitted by the
    normal search safe-search defaults.
    """
    queries = suruga_card_queries(release)
    page = new_page(browser)
    try:
        warnings: list[str] = []
        parsed_items: list[dict] = []
        seen_codes: set[str] = set()
        search_blocked = False
        max_pages = max(1, min(100, (max_cards + 23) // 24 + 2))
        for query in queries:
            for buy_search in (False, True):
                if parsed_items:
                    break
                for page_number in range(1, max_pages + 1):
                    search_url = suruga_search_url(query, page_number, buy_search)
                    try:
                        goto(page, search_url, wait_ms=900, timeout_ms=60000, attempts=2)
                        if suruga_search_is_blocked(page):
                            search_blocked = True
                            break
                        rows = page.eval_on_selector_all(
                            "a[href*='/product/detail/'], a[href*='/product/other/'], a[href*='/kaitori/kaitori_detail/']",
                            """els => els.map(a => {
                                const root = a.closest("li, article, tr, .item, [class*='product'], [class*='item']") || a;
                                const img = root.querySelector('img') || a.querySelector('img');
                                return {
                                    href: a.href,
                                    text: (root.innerText || root.textContent || a.innerText || '').replace(/\\s+/g, ' ').trim(),
                                    imageUrl: (img?.currentSrc || img?.src || img?.dataset?.original || img?.dataset?.src || '').trim(),
                                    altText: (img?.alt || '').trim()
                                };
                            }).filter(item => item.href && item.text)""",
                        )
                    except Exception as exc:
                        warnings.append(f"Suruga-ya search failed ({query}, {'buy' if buy_search else 'product'} page {page_number}): {exc}")
                        break
                    if not rows:
                        break
                    added = 0
                    for row in rows:
                        item = parse_suruga_card_row(row, release)
                        if not item or item["cardCode"] in seen_codes:
                            continue
                        seen_codes.add(item["cardCode"])
                        item["checklistSequence"] = len(parsed_items) + 1
                        parsed_items.append(item)
                        added += 1
                        if len(parsed_items) >= max_cards:
                            break
                    if len(parsed_items) >= max_cards or added == 0:
                        break
                if search_blocked:
                    break
                if parsed_items:
                    break
            if search_blocked:
                break
            if parsed_items:
                break
        if search_blocked and not parsed_items:
            indexed_items, indexed_warnings = scrape_suruga_cj_cards_from_index(
                page, release, max_cards, queries
            )
            parsed_items.extend(indexed_items)
            warnings.extend(indexed_warnings)
        if not parsed_items:
            warnings.append(f"Suruga-ya returned no individual CJ SEXY cards for {' / '.join(queries)}")
        else:
            warnings.append(f"Suruga-ya individual card listings found: {len(parsed_items)}")
        return parsed_items[:max_cards], warnings
    finally:
        close_quietly(page)


def resolve_juicy_preview_article(
    page,
    terms: list[str],
    release_date: str,
    expected_series_identity: str = "",
    enable_ocr: bool = False,
) -> tuple[str, list[dict], list[str]]:
    """Find the best official image article belonging to this Juicy Honey release.

    Older releases commonly split composition, flyer, bonus-photo and rare-card
    previews across separate blog posts.  A related article is accepted only when
    its title/body identifies the same release.
    """
    original_url = page.url
    original_text = page.locator("body").inner_text()
    original_identities = [item[0] for item in juicy_page_series_identities(page)]
    original_items = extract_juicy_preview_cards(
        page,
        enable_ocr=False,
        expected_series_identity=expected_series_identity,
        article_series_identities=original_identities,
    )
    best_url = original_url
    best_items = original_items
    best_text = original_text
    best_identities = original_identities
    best_score = juicy_gallery_score(original_text, original_items)

    candidates = []
    if len({juicy_series_routing_key(item) for item in original_identities}) <= 1 and not juicy_has_complete_gallery_marker(original_text):
        candidates = collect_matching_juicy_links(page, terms, release_date)
        for archive_url in juicy_related_index_urls(terms, release_date):
            try:
                page.goto(archive_url, wait_until="domcontentloaded", timeout=60000)
                page.wait_for_timeout(500)
                candidates.extend(collect_matching_juicy_links(page, terms, release_date))
            except Exception:
                continue

    seen_urls = {original_url.rstrip("/")}
    for candidate in candidates[:30]:
        candidate_url = str(candidate.get("href") or "").rstrip("/")
        if not candidate_url or candidate_url in seen_urls:
            continue
        seen_urls.add(candidate_url)
        try:
            page.goto(candidate_url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(700)
            body_text = page.locator("body").inner_text()
        except Exception:
            continue
        identity_text = f"{candidate.get('text', '')} {body_text[:5000]}"
        if not juicy_article_matches(identity_text, terms, release_date):
            continue
        candidate_identities = [item[0] for item in juicy_page_series_identities(page)]
        items = extract_juicy_preview_cards(
            page,
            enable_ocr=False,
            expected_series_identity=expected_series_identity,
            article_series_identities=candidate_identities,
        )
        score = juicy_gallery_score(body_text, items)
        if score > best_score:
            best_url = page.url
            best_items = items
            best_text = body_text
            best_identities = candidate_identities
            best_score = score

    # Rebuild the selected gallery once after ranking. OCR is opt-in; normal
    # catalog scraping creates image-backed card rows for manual classification.
    routing_stats: dict[str, int] = {}
    if best_items or best_identities:
        try:
            if page.url.rstrip("/") != best_url.rstrip("/"):
                page.goto(best_url, wait_until="domcontentloaded", timeout=60000)
                page.wait_for_timeout(500)
            best_items = extract_juicy_preview_cards(
                page,
                enable_ocr=enable_ocr,
                expected_series_identity=expected_series_identity,
                article_series_identities=best_identities,
                routing_stats=routing_stats,
            )
        except Exception as exc:
            progress(f"[catalog-gallery] final gallery failed url:{best_url} error:{exc}")

    warnings = []
    if len({juicy_series_routing_key(item) for item in best_identities}) > 1:
        routing_method = (
            "per-image OCR and caption evidence"
            if enable_ocr
            else "per-image caption evidence (OCR disabled)"
        )
        warnings.append(
            f"mixed official article routed by {routing_method}: "
            f"{routing_stats.get('matched', 0)} matched this release, "
            f"{routing_stats.get('otherSeries', 0)} belonged to another release, "
            f"{routing_stats.get('ambiguous', 0)} ambiguous images were skipped"
        )
    if best_items:
        if juicy_has_complete_gallery_marker(best_text):
            warnings.append(
                f"official all-card gallery article selected: {len(best_items)} published image files; "
                "an image file can contain multiple card fronts/backs, and 1of1 variations may still be partial"
            )
        else:
            warnings.append(
                f"official partial card-preview article selected: {len(best_items)} image files; "
                "the publisher did not expose a complete individually numbered image checklist"
            )
        if best_url.rstrip("/") != original_url.rstrip("/"):
            warnings.append(f"card previews were found in related official article: {best_url}")
        if routing_stats.get("ocrBudgetReached", 0) > 0:
            warnings.append(
                "OCR image budget reached; remaining gallery images were saved as "
                "caption-based or generic previews"
            )
    else:
        warnings.append(
            "no official card-preview gallery was found for this release; only composition groups can be imported"
        )
    return best_url, best_items, warnings


def collect_matching_juicy_links(page, terms: list[str], release_date: str) -> list[dict]:
    links = page.eval_on_selector_all(
        "a[href]",
        """els => els.map(a => ({
            href: (a.href || '').trim(),
            text: ((a.innerText || a.textContent || '') + ' ' + (a.querySelector('img')?.alt || '')).replace(/\\s+/g, ' ').trim()
        }))""",
    )
    result = []
    seen = set()
    for link in links:
        href = str(link.get("href") or "").strip()
        parsed = urlparse(href)
        if parsed.netloc.lower() != "juicy-honey.blog.jp" or not re.search(r"/archives/\d+\.html$", parsed.path):
            continue
        haystack = f"{link.get('text', '')} {href}"
        if not juicy_article_matches(haystack, terms, release_date):
            continue
        canonical = href.rstrip("/")
        if canonical in seen:
            continue
        seen.add(canonical)
        result.append({"href": href, "text": str(link.get("text") or "")})
    return result


def juicy_archive_urls(release_date: str) -> list[str]:
    try:
        released = datetime.strptime(release_date[:10], "%Y-%m-%d")
    except (TypeError, ValueError):
        return []
    urls = []
    month_index = released.year * 12 + released.month - 1
    for offset in range(-3, 4):
        candidate = month_index + offset
        year, zero_month = divmod(candidate, 12)
        urls.append(f"https://juicy-honey.blog.jp/archives/{year:04d}-{zero_month + 1:02d}.html")
    return urls


def juicy_related_index_urls(terms: list[str], release_date: str) -> list[str]:
    urls = []
    for term in terms:
        match = re.search(r"\bvol(?:ume)?\.?\s*(\d{1,3})(?!\d)", normalize_text(term))
        if match:
            urls.append(f"https://juicy-honey.blog.jp/tag/jh{int(match.group(1))}")
            break
    urls.extend(juicy_archive_urls(release_date))
    return urls


def juicy_article_matches(value: str, terms: list[str], release_date: str = "") -> bool:
    haystack = normalize_text(value)
    volume_numbers = []
    for term in terms:
        match = re.search(r"\bvol(?:ume)?\.?\s*(\d{1,3})(?!\d)", normalize_text(term))
        if match:
            volume_numbers.append(int(match.group(1)))
    if volume_numbers:
        volume = volume_numbers[0]
        if re.search(rf"\bvol(?:ume)?\.?\s*{volume}(?!\d)", haystack) is None:
            return False
        # A tag/archive page can contain several articles for the same
        # volume. When the release carries model terms, require one of those
        # identities as well so a lottery or social post cannot supply the
        # gallery for the wrong article.
        identity_terms = [
            normalize_text(term)
            for term in terms
            if len(normalize_text(term)) >= 2
            and is_release_signal(normalize_text(term))
            and not re.search(r"\b(?:juicy|honey|collection|cards?|plus|vol(?:ume)?\.?\s*\d+)\b", normalize_text(term), re.I)
            and not normalize_text(term).isdigit()
        ]
        return not identity_terms or any(term_matches(term, haystack) for term in identity_terms)

    release_year = release_date[:4] if re.fullmatch(r"\d{4}", release_date[:4]) else ""
    aliases = {
        "luxury": ("luxury", "ラグジュアリー"),
        "deluxe": ("deluxe", "デラックス"),
        "exquisite": ("exquisite", "エクスクイジット"),
        "anniversary": ("anniversary", "アニバーサリー"),
    }
    normalized_terms = " ".join(normalize_text(term) for term in terms)
    for marker, marker_aliases in aliases.items():
        if marker in normalized_terms or any(alias in normalized_terms for alias in marker_aliases):
            marker_match = any(alias in haystack for alias in marker_aliases)
            year_match = not release_year or release_year in haystack
            return marker_match and year_match

    significant = [
        normalize_text(term) for term in terms
        if len(normalize_text(term)) >= 4 and is_release_signal(normalize_text(term))
    ]
    return any(term_matches(term, haystack) for term in significant)


def juicy_has_complete_gallery_marker(text: str) -> bool:
    normalized = normalize_text(text)
    return (
        ("全カード" in normalized and "表面" in normalized and "裏面" in normalized)
        or "全てのカード画像" in normalized
        or "レアカード一挙掲載" in normalized
        or "all card fronts and backs" in normalized
        or "all cards front and back" in normalized
        or "all rare card images" in normalized
    )


def juicy_gallery_score(text: str, items: list[dict]) -> int:
    if not items:
        return 0
    normalized = normalize_text(text)
    score = len(items)
    if juicy_has_complete_gallery_marker(text):
        score += 10000
    elif any(marker in normalized for marker in ("レアカード", "rare card", "直筆サイン", "autograph")):
        score += 1000
    return score


def clean_juicy_context(value: str) -> str:
    value = re.sub(r"\s+", " ", str(value or "")).strip()
    return value[:240]


# OCR is intentionally disabled for every publisher. Keep the classifier
# implementation available for historical tests and a future explicit opt-in,
# but do not let deployment environment variables turn it on accidentally.
JUICY_OCR_ENABLED = False
JUICY_OCR_MIN_CONFIDENCE = float(os.environ.get("CATALOG_IMAGE_OCR_MIN_CONFIDENCE", "0.45"))
try:
    JUICY_OCR_MAX_IMAGES = max(
        0, int(os.environ.get("CATALOG_IMAGE_OCR_MAX_IMAGES", "2"))
    )
except (TypeError, ValueError):
    JUICY_OCR_MAX_IMAGES = 2
try:
    JUICY_OCR_MAX_SIDE_LEN = min(
        2000, max(640, int(os.environ.get("CATALOG_IMAGE_OCR_MAX_SIDE_LEN", "1280")))
    )
except (TypeError, ValueError):
    JUICY_OCR_MAX_SIDE_LEN = 1280
try:
    JUICY_OCR_THREADS = min(
        4, max(1, int(os.environ.get("CATALOG_IMAGE_OCR_THREADS", "1")))
    )
except (TypeError, ValueError):
    JUICY_OCR_THREADS = 1
_JUICY_OCR_ENGINE: Any = None
_JUICY_OCR_UNAVAILABLE = False
_JUICY_OCR_CACHE: dict[str, tuple[str, float]] = {}
_JUICY_OCR_META: dict[str, dict[str, Any]] = {}
_JUICY_OCR_OBSERVATIONS: dict[str, dict[str, Any]] = {}
JUICY_OCR_CLASSIFIER_VERSION = 2


def configure_juicy_ocr_cache(entries: Any) -> None:
    """Load release-scoped PostgreSQL OCR rows supplied by the Go process."""
    _JUICY_OCR_CACHE.clear()
    _JUICY_OCR_META.clear()
    _JUICY_OCR_OBSERVATIONS.clear()
    for raw in entries if isinstance(entries, list) else []:
        if not isinstance(raw, dict):
            continue
        image_url = str(raw.get("imageUrl") or "").strip()
        status = str(raw.get("status") or "").strip().lower()
        if not image_url or status not in {"completed", "no_text"}:
            continue
        _JUICY_OCR_CACHE[image_url] = (
            clean_juicy_context(raw.get("ocrText") or ""),
            float(raw.get("ocrConfidence") or 0.0),
        )
        _JUICY_OCR_META[image_url] = {
            "status": status,
            "lastError": "",
            "cacheHit": True,
        }


def juicy_ocr_engine_version() -> str:
    try:
        from importlib.metadata import version

        return version("rapidocr")
    except Exception:
        return ""


def record_juicy_ocr_observation(
    image_url: str,
    ocr_text: str,
    ocr_confidence: float,
    classification: dict[str, Any],
) -> None:
    meta = _JUICY_OCR_META.get(image_url)
    if meta is None:
        return
    _JUICY_OCR_OBSERVATIONS[image_url] = {
        "imageUrl": image_url,
        "ocrText": ocr_text,
        "ocrConfidence": ocr_confidence,
        "engineKey": "rapidocr",
        "engineVersion": juicy_ocr_engine_version(),
        "classifierVersion": JUICY_OCR_CLASSIFIER_VERSION,
        "rarityLabel": str(classification.get("rarityLabel") or ""),
        "cardType": str(classification.get("cardType") or ""),
        "cardTypeKey": str(classification.get("cardTypeKey") or ""),
        "parallelType": str(classification.get("parallelType") or ""),
        "isAutograph": bool(classification.get("isAutograph")),
        "isRelic": bool(classification.get("isRelic")),
        "isOneOfOne": bool(classification.get("isOneOfOne")),
        "status": str(meta.get("status") or "completed"),
        "lastError": str(meta.get("lastError") or ""),
        "cacheHit": bool(meta.get("cacheHit")),
    }


def juicy_ocr_results() -> list[dict]:
    return list(_JUICY_OCR_OBSERVATIONS.values())


def juicy_lingerie_parallel_from_color(source_image: Any) -> str:
    """Infer PLUS-style lingerie subtype from a strongly dominant label color.

    The official horizontal card design prints the subtype panel on the right:
    Type A uses a warm orange/red treatment and Type B uses green.  Keep this
    deliberately conservative so skin tones, neutral art, and mixed colors do
    not manufacture a subtype when the tiny dot-matrix text defeats OCR.
    """
    if source_image is None or not hasattr(source_image, "shape") or len(source_image.shape) < 2:
        return ""
    try:
        import cv2

        height, width = source_image.shape[:2]
        if height < 20 or width < 20:
            return ""
        region = source_image[
            int(height * 0.18) : max(int(height * 0.18) + 1, int(height * 0.68)),
            int(width * 0.50) : max(int(width * 0.50) + 1, int(width * 0.96)),
        ]
        if not region.size:
            return ""
        hsv = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)
        hue, saturation, value = cv2.split(hsv)
        vivid = (saturation > 90) & (value > 45) & (value < 245)
        counts = {
            "Type A": int((vivid & ((hue < 30) | (hue >= 170))).sum()),
            "Type B": int((vivid & (hue >= 30) & (hue < 90)).sum()),
        }
        ranked = sorted(counts.items(), key=lambda item: item[1], reverse=True)
        dominant_label, dominant_count = ranked[0]
        runner_up_count = ranked[1][1]
        pixel_count = int(region.shape[0] * region.shape[1])
        if (
            dominant_count >= max(100, int(pixel_count * 0.015))
            and dominant_count >= max(1, runner_up_count) * 5
        ):
            return dominant_label
    except Exception:
        return ""
    return ""


def juicy_ocr_engine():
    """Return one lazily initialized local OCR engine for the worker process.

    OCR is optional at import time so discovery and unit tests continue to work
    when only CloakBrowser is installed. Production checklist workers install
    RapidOCR and ONNX Runtime from ``requirements.txt``.
    """
    global _JUICY_OCR_ENGINE, _JUICY_OCR_UNAVAILABLE
    if not JUICY_OCR_ENABLED or _JUICY_OCR_UNAVAILABLE:
        return None
    if _JUICY_OCR_ENGINE is not None:
        return _JUICY_OCR_ENGINE
    try:
        from rapidocr import RapidOCR

        # The API worker also keeps a Chromium process alive while this worker
        # runs. Bound ONNX Runtime's thread pools and image preprocessing so a
        # small production host cannot be taken down by an unbounded OCR pass.
        _JUICY_OCR_ENGINE = RapidOCR(params={
            "Global.max_side_len": JUICY_OCR_MAX_SIDE_LEN,
            "EngineConfig.onnxruntime.intra_op_num_threads": JUICY_OCR_THREADS,
            "EngineConfig.onnxruntime.inter_op_num_threads": 1,
        })
    except Exception as exc:
        _JUICY_OCR_UNAVAILABLE = True
        progress(f"[catalog-ocr] unavailable error:{exc}")
        return None
    return _JUICY_OCR_ENGINE


def juicy_ocr_text_for_image(image_url: str) -> tuple[str, float]:
    """Read text printed on one official card image using local CPU OCR."""
    image_url = str(image_url or "").strip()
    if not image_url:
        return "", 0.0
    cached = _JUICY_OCR_CACHE.get(image_url)
    if cached is not None:
        return cached
    engine = juicy_ocr_engine()
    if engine is None:
        result = ("", 0.0)
        _JUICY_OCR_CACHE[image_url] = result
        _JUICY_OCR_META[image_url] = {
            "status": "failed",
            "lastError": "RapidOCR engine is unavailable",
            "cacheHit": False,
        }
        return result
    try:
        accepted = []
        accepted_scores = []

        def append_output(output) -> None:
            texts = tuple(getattr(output, "txts", ()) or ())
            scores = tuple(getattr(output, "scores", ()) or ())
            for index, text in enumerate(texts):
                score = float(scores[index]) if index < len(scores) else 0.0
                cleaned = clean_juicy_context(text)
                if cleaned and score >= JUICY_OCR_MIN_CONFIDENCE:
                    accepted.append(cleaned)
                    accepted_scores.append(score)

        def current_classification() -> dict[str, Any]:
            return juicy_card_classification(" ".join(accepted))

        def needs_label_detail(classification: dict[str, Any]) -> bool:
            if not classification:
                return True
            return (
                classification.get("cardType") in {"autograph", "lingerie_relic"}
                and not classification.get("parallelType")
            )

        output = engine(image_url, use_det=True, use_cls=False, use_rec=True)
        append_output(output)
        source_image = getattr(output, "img", None)
        # Measure the untouched decoded image before OCR enhancement passes;
        # some OCR backends may reuse or mutate NumPy view buffers.
        color_parallel = juicy_lingerie_parallel_from_color(source_image)
        if source_image is not None and needs_label_detail(current_classification()):
            height, width = source_image.shape[:2]
            top_crop = source_image[: max(1, int(height * 0.72)), :]
            append_output(engine(top_crop, use_det=True, use_cls=False, use_rec=True))

            if needs_label_detail(current_classification()):
                import cv2

                title_crop = source_image[
                    : max(1, int(height * 0.78)),
                    : max(1, int(width * 0.72)),
                ]
                gray = cv2.cvtColor(title_crop, cv2.COLOR_BGR2GRAY)
                enlarged = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(enlarged)
                append_output(engine(clahe, use_det=True, use_cls=False, use_rec=True))
                if needs_label_detail(current_classification()):
                    _, otsu = cv2.threshold(
                        clahe, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
                    )
                    append_output(engine(otsu, use_det=True, use_cls=False, use_rec=True))
            classification = current_classification()
            if (
                classification.get("cardType") == "lingerie_relic"
                and not classification.get("parallelType")
            ):
                if color_parallel:
                    accepted.append(color_parallel.upper())
                    accepted_scores.append(0.75)
        confidence = sum(accepted_scores) / len(accepted_scores) if accepted_scores else 0.0
        result = (" ".join(accepted), confidence)
        _JUICY_OCR_META[image_url] = {
            "status": "completed" if result[0] else "no_text",
            "lastError": "",
            "cacheHit": False,
        }
    except Exception as exc:
        progress(f"[catalog-ocr] image failed url:{image_url} error:{exc}")
        result = ("", 0.0)
        _JUICY_OCR_META[image_url] = {
            "status": "failed",
            "lastError": str(exc),
            "cacheHit": False,
        }
    _JUICY_OCR_CACHE[image_url] = result
    return result


def normalize_juicy_card_text(value: str) -> str:
    value = unicodedata.normalize("NFKC", str(value or "")).upper()
    value = re.sub(r"[^A-Z0-9#]+", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    value = re.sub(r"\bAUT[0O]\s*GRAPH\b", "AUTOGRAPH", value)
    value = re.sub(r"\bH[0O]NEY\b", "HONEY", value)
    value = re.sub(r"\bTYPER\b|\bTYPE\s*[R8]\b", "TYPE B", value)
    value = re.sub(r"\bNEGLI\s+GEE\b", "NEGLIGEE", value)
    value = re.sub(r"\b(?:H)?ONEY\s+(?:L)?INGERIE\b", "HONEY LINGERIE", value)
    value = re.sub(r"\bCLEARVIEW\b", "CLEAR VIEW", value)
    value = re.sub(r"\bPARR?ALEL\b|\bPARALEL\b", "PARALLEL", value)
    value = re.sub(r"\bSLEEPING\s+BEUTY\b", "SLEEPING BEAUTY", value)
    value = re.sub(r"\bKAISYO\b", "KAISHO", value)
    value = re.sub(r"\bMASSEGE\b", "MESSAGE", value)
    value = re.sub(r"\bMONO\s+KINI\b", "MONOKINI", value)
    if re.search(r"\bSIGRAT\w*\b", value):
        value += " MODEL SIGNATURE"
    return value


def juicy_preview_asset_kind(image_url: str, alt_text: str, ocr_text: str = "") -> str:
    """Identify release artwork which must not become a card-design row."""
    parsed = urlparse(str(image_url or ""))
    basename = unquote(parsed.path.rsplit("/", 1)[-1]).lower()
    metadata = f"{basename} {str(alt_text or '').lower()}"
    if re.search(r"(?:^|[^a-z])fly(?:er)?[_\s-]*\d*|fly_.+_page|フライヤー", metadata, re.I):
        return "flyer"
    if re.search(r"(?:^|[^a-z])(box|pack|package|sales[_\s-]*sheet)(?:[^a-z]|$)", metadata, re.I):
        return "package"
    if re.search(r"(?:^|[^a-z])(event|profile|off[_\s-]*shot|behind[_\s-]*scenes?)(?:[^a-z]|$)", metadata, re.I):
        return "editorial"
    normalized_ocr = normalize_juicy_card_text(ocr_text)
    if "CARDS PER PACK" in normalized_ocr or "PACKS PER BOX" in normalized_ocr:
        return "flyer"
    return ""


def juicy_card_classification(value: str) -> dict[str, Any]:
    """Map per-image OCR/caption text to normalized card-design metadata.

    Specific product names intentionally precede generic words such as
    ``AUTOGRAPH``. A card reading ``HONEY STOCKINGS AUTO`` should retain its
    stockings identity while also setting the autograph flag.
    """
    text = normalize_juicy_card_text(value)
    if not text:
        return {}

    type_match = re.search(r"\bTYPE\s*([A-Z12])\b", text)
    type_value = type_match.group(1) if type_match else ""
    if type_value == "E" and "MODEL SIGNATURE" in text:
        type_value = "B"
    parallel_type = f"Type {type_value}" if type_value in {"A", "B", "C", "D", "E", "1", "2"} else ""
    if "FOIL PARALLEL" in text:
        parallel_type = "Foil Parallel"
    else:
        for color in ("GOLD", "GREEN", "PINK", "BLACK", "RED", "BLUE", "PURPLE", "SILVER", "CLEAR"):
            if re.search(rf"\b{color}\b", text):
                parallel_type = color.title()
                break
    if not parallel_type:
        limited_match = re.search(r"#\s*(\d+)\b|\b(\d+)\s+LIMITED\b", text)
        if limited_match:
            parallel_type = f"#{limited_match.group(1) or limited_match.group(2)}"

    is_autograph = bool(re.search(r"\b(?:AUTOGRAPH|AUTOGRAPHED|AUTO)\b", text))
    is_one_of_one = bool(re.search(r"\b1\s*OF\s*1\b|#\s*1\s*/\s*1\b", text))
    if is_one_of_one and not parallel_type:
        parallel_type = "1 of 1"
    rules = (
        (r"\bSTAR\s+ACTRESS\s+DNA\s+TRIPLE\b", "Juicy STAR Actress DNA Triple", "juicy_star_actress_dna_triple", "dna_relic", False, True),
        (r"\bSTAR\s+ACTRESS\s+DNA\b", "Juicy STAR Actress DNA", "juicy_star_actress_dna", "dna_relic", False, True),
        (r"\bSTAR\s+ART\s+OF\s+HONEY\s+FOIL\b", "Juicy STAR Art of Honey Foil Autograph", "juicy_star_art_of_honey_foil_autograph", "autograph", True, False),
        (r"\bSTAR\s+OPUS\s+NOIR\b", "Juicy STAR Opus Noir Autograph", "juicy_star_opus_noir_autograph", "autograph", True, False),
        (r"\b(?:JUICY\s+)?STAR\s+KAISHO\b", "Juicy STAR Kaisho Autograph", "juicy_star_kaisho_autograph", "autograph", True, False),
        (r"\b(?:JUICY\s+)?STAR\s+MESSAGE\b", "Juicy STAR Message Autograph", "juicy_star_message_autograph", "autograph", True, False),
        (r"\b(?:JUICY\s+)?STAR\s+AUTOGRAPH\b", "Juicy STAR Autograph", "juicy_star_autograph", "autograph", True, False),
        (r"\bGILDED\s+GRACE\b", "Gilded Grace Autograph", "gilded_grace_autograph", "autograph", True, False),
        (r"\bHONEY\s+FEET\b", "Honey Feet Autograph", "honey_feet_autograph", "autograph", True, False),
        (r"\bART\s+OF\s+HONEY\s+FOIL\b", "Art of Honey Foil Autograph", "art_of_honey_foil_autograph", "autograph", True, False),
        (r"\bART\s+OF\s+HONEY\b", "Art of Honey Autograph", "art_of_honey_autograph", "autograph", True, False),
        (r"\bJUICY\s+HIP\b", "Juicy Hip Autograph", "juicy_hip_autograph", "autograph", True, False),
        (r"\bCANDY\s+HONEY\b", "Candy Honey Autograph", "candy_honey_autograph", "autograph", True, False),
        (r"\bCLEAR\s+VIEW\b", "Clear View Autograph", "clear_view_autograph", "autograph", True, False),
        (r"\bSLEEPING\s+BEAUTY\b", "Sleeping Beauty Autograph", "sleeping_beauty_autograph", "autograph", True, False),
        (r"\bSHORE\s+AUTOGRAPH\b", "Shore Autograph", "shore_autograph", "autograph", True, False),
        (r"\bARABESQUE\b", "Arabesque Autograph", "arabesque_autograph", "autograph", True, False),
        (r"\bMOMENT\s+AUTOGRAPH\b", "Moment Autograph", "moment_autograph", "autograph", True, False),
        (r"\b(?:HONEY|JUICY)\s+EYES\b", "Honey Eyes Autograph", "honey_eyes_autograph", "autograph", True, False),
        (r"\bHANA\s+AUTOGRAPH\b", "Hana Autograph", "hana_autograph", "autograph", True, False),
        (r"\bHOKUSAI\b", "Hokusai Autograph", "hokusai_autograph", "autograph", True, False),
        (r"\bMANGA\s+AUTOGRAPH\b", "Manga Autograph", "manga_autograph", "autograph", True, False),
        (r"\bART\s+BURST\b", "Art Burst Autograph", "art_burst_autograph", "autograph", True, False),
        (r"\bBELLEZA\b", "Belleza Autograph", "belleza_autograph", "autograph", True, False),
        (r"\bOPUS\s+NOIR\b", "Opus Noir Autograph", "opus_noir_autograph", "autograph", True, False),
        (r"\bSUCCUBUS\b", "Succubus Autograph", "succubus_autograph", "autograph", True, False),
        (r"\bLEGACY\s+INK\b", "Legacy Ink Autograph", "legacy_ink_autograph", "autograph", True, False),
        (r"\bKAISHO\s+AUTOGRAPH\b", "Kaisho Autograph", "kaisho_autograph", "autograph", True, False),
        (r"\bFIRST\s+JUICY\b", "First Juicy Autograph", "first_juicy_autograph", "autograph", True, False),
        (r"\bPREMIUM\s*10\s+SUNSET\b", "Premium 10 Sunset", "premium_10_sunset", "autograph", True, False),
        (r"\bPREMIUM\s*30\s+DIE\s*CUT\b", "Premium 30 Die Cut", "premium_30_die_cut", "autograph", True, False),
        (r"\bPREMIUM\s*20\s+DIE\s*CUT\b", "Premium 20 Die Cut", "premium_20_die_cut", "autograph", True, False),
        (r"\bPREMIUM\s*(?:1\s*OF\s*1|1OF1)\b", "1 of 1 Autograph", "one_of_one_autograph", "autograph", True, False),
        (r"\bPREMIUM\s*30\b", "Premium 30", "premium_30", "autograph", True, False),
        (r"\bPREMIUM\s*10\b", "Premium 10", "premium_10", "autograph", True, False),
        (r"\bPREMIUM\s+AUTOGRAPH\b", "Premium Autograph", "premium_autograph", "autograph", True, False),
        (r"\bNEW\s+AUTOGRAPH\s+(?:99|50)\b", "New Autograph", "new_autograph", "autograph", True, False),
        (r"\b(?:NEW\s+)?GOLD\s+AUTOGRAPH\b", "Gold Autograph", "gold_autograph", "autograph", True, False),
        (r"\b1\s*OF\s*1\s+AUTOGRAPH\b|\bAUTOGRAPH\s+1\s*OF\s*1\b", "1 of 1 Autograph", "one_of_one_autograph", "autograph", True, False),
        (r"\bDIE\s*CUT\s+AUTOGRAPH\b", "Die Cut Autograph", "die_cut_autograph", "autograph", True, False),
        (r"\bQUIN\s+DECTET\s+AUTOGRAPH\b", "Quin-dectet Autograph", "quin_dectet_autograph", "autograph", True, False),
        (r"\bAUTOGRAPH\s+QUARTET\s+KAISHO\b", "Quartet Kaisho Autograph", "quartet_kaisho_autograph", "autograph", True, False),
        (r"\b(?:AUTOGRAPH\s+QUARTET|QUARTET\s+AUTOGRAPH)\b", "Quartet Autograph", "quartet_autograph", "autograph", True, False),
        (r"\b(?:AUTOGRAPH\s+TRIPLE|TRIPLE\s+AUTOGRAPH)\b", "Triple Autograph", "triple_autograph", "autograph", True, False),
        (r"\b(?:AUTOGRAPH\s+COMBO|COMBO\s+AUTOGRAPH)\b", "Combo Autograph", "combo_autograph", "autograph", True, False),
        (r"\b(?:AUTOGRAPHED\s+MESSAGE|MESSAGE\s+AUTOGRAPH)\b", "Message Autograph", "message_autograph", "autograph", True, False),
        (r"\bAUTOGRAPH(?:ED)?\s+PANTIES\b", "Autograph Panties", "autograph_panties", "panties_relic", True, True),
        (r"\bBOOKLET\s+THEN\s+AND\s+NOW\b", "Then and Now Autograph Booklet", "then_and_now_booklet", "booklet", True, False),
        (r"\bBOOKLET\s+(?:20TH\s+)?VINGT\s+ETOILES\b", "20th Vingt Etoiles Booklet", "vingt_etoiles_booklet", "booklet", False, False),
        (r"\bBOOKLET\s+LINGERIE\s+(?:AND|&)\s+AUTOGRAPH\b", "Autograph and Lingerie Booklet", "autograph_lingerie_booklet", "booklet", True, True),
        (r"\bBOOKLET\s+LINGERIE\s+KAISHO\b", "Lingerie Kaisho Booklet", "lingerie_kaisho_booklet", "booklet", True, True),
        (r"\bBOOKLET\s+AUTOGRAPH(?:ED)?\s+COMBO\b", "Autographed Combo Booklet", "autographed_combo_booklet", "booklet", True, False),
        (r"\bBOOKLET\s+DRESS\s+QUARTET\b", "Dress Quartet Booklet", "dress_quartet_booklet", "booklet", False, True),
        (r"\bBOOKLET\s+AUTOGRAPH\s+QUARTET\b", "Autograph Quartet Booklet", "autograph_quartet_booklet", "booklet", True, False),
        (r"\bBOOKLET\s+NIPPLE\s+STAMPS?\b|\bNIPPLE\s+STAMPS\b", "Nipple Stamp Booklet", "nipple_stamp_booklet", "booklet", False, False),
        (r"\bAUTOGRAPH\s+(?:AND\s+)?LINGERIE\b", "Autograph and Lingerie Booklet", "autograph_lingerie_booklet", "booklet", True, True),
        (r"\bAUTOGRAPH\s+(?:AND\s+)?KISS\b", "Autograph and Kiss Booklet", "autograph_kiss_booklet", "booklet", True, False),
        (r"\bPINKY\s+SPOT\s+BOOKLET\b", "Pinky Spot Booklet", "pinky_spot_booklet", "booklet", False, True),
        (r"\bHONEY\s+STOCKINGS?\s+(?:AUTO|AUTOGRAPH)", "Honey Stockings Autograph", "stockings_autograph", "stockings", True, True),
        (r"\bAUTOGRAPHED\s+BASEBALL\s+BIG\s+PATCH\b", "Autographed Baseball Big Patch", "autographed_baseball_big_patch", "patch_relic", True, True),
        (r"\bAUTOGRAPHED\s+BASKETBALL\s+BIG\s+PATCH\b", "Autographed Basketball Big Patch", "autographed_basketball_big_patch", "patch_relic", True, True),
        (r"\bBASEBALL\s+BIG\s+PATCH\b", "Baseball Big Patch", "baseball_big_patch", "patch_relic", False, True),
        (r"\bBASKETBALL\s+BIG\s+PATCH\b", "Basketball Big Patch", "basketball_big_patch", "patch_relic", False, True),
        (r"\bSOCCER\s+BIG\s+PATCH\b", "Soccer Big Patch", "soccer_big_patch", "patch_relic", False, True),
        (r"\bAUTOGRAPHED\s+BASEBALL\b", "Autographed Baseball", "autographed_baseball", "autograph", True, False),
        (r"\b(?:AUTOGRAPHED\s+)?ACTRESS\s+DNA\s+(?:TRIPLE|QUARTET)\b|\bDNA\s+(?:TRIPLE|QUARTET)\b", "Actress DNA Group", "dna_triple" if "TRIPLE" in text else "dna_quartet", "dna_relic", is_autograph, True),
        (r"\bDNA\s+(?:AND\s+)?LINGERIE\b", "DNA and Lingerie", "dna_lingerie", "dna_relic", is_autograph, True),
        (r"\bAUTOGRAPHED\s+(?:ACTRESS\s+)?DNA\b", "Autographed Actress DNA", "autographed_dna", "dna_relic", True, True),
        (r"\bACTRESS\s+DNA\b|\bDNA\s+(?:CARD|SET)\b", "Actress DNA", "dna", "dna_relic", is_autograph, True),
        (r"\bAUTOGRAPHED\s+JUICY\s+KISS\b|\bJUICY\s+KISS\s+AUTOGRAPH\b|\bAUTOGRAPHED\s+KISS\b", "Autographed Juicy Kiss", "autographed_kiss", "kiss", True, False),
        (r"\bKISS\s+(?:AND\s+)?PHOTO\b", "Kiss and Photo", "kiss_photo", "kiss", False, False),
        (r"\bKISS\s+(?:AND\s+)?MESSAGE\b", "Kiss and Message", "kiss_message", "kiss", False, False),
        (r"\bJUICY\s+KISS\b|\bKISS\s+(?:CARD|SET)\b", "Juicy Kiss", "kiss", "kiss", is_autograph, False),
        (r"\bAUTOGRAPHED\s+INSTANT\s+PHOTO", "Autographed Instant Photo", "autographed_instant_photo", "instant_photo", True, False),
        (r"\bAUTOGRAPHED\s+PHOTO", "Autographed Photo", "autographed_photo", "photo", True, False),
        (r"\bJUICY\s+PHOTO\b", "Juicy Photo", "juicy_photo", "photo", False, False),
        (r"\bPHOTO\s+(?:CARD|SET)", "Photo Card", "photo", "photo", False, False),
        (r"\bAUTOGRAPHED\s+(?:SUPER\s+)?BIG\s+LINGERIE\b|\bAUTOGRAPHED\s+HONEY\s+BIG\s+LINGERIE\b", "Autographed Big Lingerie", "autographed_big_lingerie", "lingerie_relic", True, True),
        (r"\bAUTOGRAPHED\s+BIG\s+SHIRTS?\b", "Autographed Big Shirts", "autographed_big_shirts", "apparel_relic", True, True),
        (r"\b20TH\s+ANNIVERSARY\s+BIG\s+T\s*SHIRTS?\b", "20th Anniversary Big T-Shirts", "big_tshirts", "apparel_relic", False, True),
        (r"\bBIG\s+JERSEY\b", "Big Jersey", "big_jersey", "apparel_relic", False, True),
        (r"\bMICRO\s+BIKINI\s+LARGE\b", "Micro Bikini Large", "micro_bikini_large", "bikini_relic", False, True),
        (r"\b(?:HONEY\s+)?BIKINI\s+QUARTET\b", "Bikini Quartet", "bikini_quartet", "bikini_relic", False, True),
        (r"\bCOMBO\s+BIKINI\b", "Combo Bikini", "combo_bikini", "bikini_relic", False, True),
        (r"\bPINKY\s+SPOT\s+BIKINI\b", "Pinky Spot Bikini", "pinky_spot_bikini", "bikini_relic", False, True),
        (r"\bLINGERIE\s+QUARTET\b|\bQUARTET\s+LINGERIE\b", "Quartet Lingerie", "quartet_lingerie", "lingerie_relic", False, True),
        (r"\bLINGERIE\s+COMBO\b", "Lingerie Combo", "lingerie_combo", "lingerie_relic", False, True),
        (r"\bDOUBLE\s+LINGERIE\b", "Double Lingerie", "double_lingerie", "lingerie_relic", False, True),
        (r"\bTRIPLE\s+LINGERIE\b", "Triple Lingerie", "triple_lingerie", "lingerie_relic", False, True),
        (r"\bLINGERIE\s+LARGE\b", "Lingerie Large", "lingerie_large", "lingerie_relic", False, True),
        (r"\bPINKY\s+SPOT\s+LINGERIE\b|\bHONEY\s+LINGERIE\s+PINKY\s+SPOT\b", "Pinky Spot Lingerie", "pinky_spot_lingerie", "lingerie_relic", False, True),
        (r"\bPINKY\s+SPOT\b", "Pinky Spot", "pinky_spot", "memorabilia_relic", False, True),
        (r"\b(?:FIVE|5)\s+COLORS?\s+LINGERIE\b", "Five Colors Lingerie", "five_color_lingerie", "lingerie_relic", False, True),
        (r"\bRANDOM\s+COLORS?\s+LINGERIE\b", "Random Colors Lingerie", "random_color_lingerie", "lingerie_relic", False, True),
        (r"\bAUTOGRAPHED\s+LINGERIE\b", "Autographed Lingerie", "autographed_lingerie", "lingerie_relic", True, True),
        (r"\bHONEY\s+BIG\s+LINGERIE\b|\bBIG\s+LINGERIE\b", "Big Lingerie", "big_lingerie", "lingerie_relic", is_autograph, True),
        (r"\bHONEY\s+BIG\s+PANTIES\b|\bHONEY\s+PANTIES\b|\bPANTIES\s+(?:CARD|SET)\b", "Panties", "panties_relic", "panties_relic", is_autograph, True),
        (r"\bHONEY\s+LINGERIE\b|\bBRASSIERE\b", "Honey Lingerie", "lingerie_relic", "lingerie_relic", is_autograph, True),
        (r"\bHONEY\s+MONOKINI\b", "Honey Monokini", "monokini_relic", "bikini_relic", False, True),
        (r"\bBATHING\s+SUIT\b", "Bathing Suit", "bathing_suit_relic", "bikini_relic", False, True),
        (r"\bHONEY\s+BIKINI\b|\bBIKINI\s+(?:CARD|SET)\b", "Honey Bikini", "bikini_relic", "bikini_relic", is_autograph, True),
        (r"\bHONEY\s+STOCKINGS?\b", "Honey Stockings", "stockings_relic", "stockings_relic", is_autograph, True),
        (r"\bHONEY\s+DRESS\b", "Honey Dress", "dress_relic", "costume_relic", False, True),
        (r"\bHONEY\s+SLIP\b|\bSLIP\s+(?:CARD|SET)\b", "Honey Slip", "slip_relic", "costume_relic", False, True),
        (r"\bHONEY\s+DENIM\b|\bTANK\s+TOP\s+(?:AND\s+)?DENIM\b", "Honey Denim", "denim_relic", "costume_relic", False, True),
        (r"\bJUIC\w*\s+(?:B)?UNNY(?:\s+GIRL)?\b", "Honey Costume", "costume_relic", "costume_relic", is_autograph, True),
        (r"\bHONEY\s+NEGLIGEE\b", "Honey Costume", "negligee_relic", "costume_relic", is_autograph, True),
        (r"\bSANTA\s+CLAUS\s+COSTUME\b", "Santa Claus Costume", "santa_costume_relic", "costume_relic", False, True),
        (r"\bALOHA\s+SHIRT\s+COSTUME\b", "Aloha Shirt Costume", "aloha_shirt_relic", "costume_relic", False, True),
        (r"\bHONEY\s+HAT\b", "Honey Hat", "honey_hat", "apparel_relic", False, True),
        (r"\bJUICY\s+JEWEL\b", "Juicy Jewel", "juicy_jewel", "jewelry_relic", is_autograph, True),
        (r"\bSIREN\s+SERENADE\b", "Siren Serenade", "siren_serenade", "lenticular", False, False),
        (r"\bCHOUCHOU\b", "Chouchou", "chouchou", "insert", False, False),
        (r"\bPRIVATE\s+GOODS\b|\bPERSONAL\s+ITEMS?\b", "Private Goods", "private_goods", "memorabilia_relic", False, True),
        (r"\bILLUSTRATION\b", "Illustration", "illustration_autograph" if is_autograph else "illustration", "art", is_autograph, False),
        (r"\bCHIN\s*SPOT\b", "Chin Spot", "chin_spot", "body_impression", False, False),
        (r"\bBRA\s*HOOK\b", "Bra Hook", "bra_hook", "bra_hook_relic", is_autograph, True),
        (r"\bBRA\s*STRAP\b", "Bra Strap", "bra_strap", "bra_strap_relic", is_autograph, True),
        (r"\bMASQUERADE\b", "Masquerade", "masquerade", "mask_relic", is_autograph, True),
        (r"\bNIPPLE\s+SEAL\b", "Nipple Seal", "nipple_seal", "memorabilia_relic", False, True),
        (r"\b3D\s+NIPPLE\b", "3D Nipple", "three_d_nipple", "body_impression", False, False),
        (r"\bNIPPLE\s+STAMP\b", "Nipple Stamp", "nipple_stamp", "stamp", is_autograph, False),
        (r"\bDIE\s*CUT\b", "Die Cut Autograph", "die_cut_autograph", "autograph", True, False),
        (r"\bKAISHO\b", "Kaisho Autograph", "kaisho_autograph", "autograph", True, False),
        (r"\bQUARTET\b", "Quartet Autograph", "quartet_autograph", "autograph", True, False),
        (r"\bTRIPLE\b", "Triple Autograph", "triple_autograph", "autograph", True, False),
        (r"\bCOMBO\b", "Combo Autograph", "combo_autograph", "autograph", True, False),
        (r"\bMESSAGE(?:\s+(?:CARD|SET))?\b", "Message", "message", "message", False, False),
        (r"\bREGULAR\s+PARALLEL\b", "Regular Parallel", "regular_parallel", "base", False, False),
        (r"\bJUICY\s+(?:SPECIAL|SP)\b", "Juicy Special", "juicy_special", "insert", False, False),
        (r"\b(?:BASE\s+)?AUTOGRAPH\b|\bAUTO\s*GRAPH\b|\bMODEL\s+SIGNATURE\b", "Base Autograph", "base_autograph", "autograph", True, False),
        (r"\bREGULAR\s+(?:CARD|CARDS)\b|\bBASE\s+(?:CARD|SET)\b|\bBASIC\s+SET\b", "Regular Card", "base", "base", False, False),
    )
    for pattern, rarity_label, card_type_key, card_type, autograph, relic in rules:
        if re.search(pattern, text):
            if not parallel_type and re.search(r"\bJUIC\w*\s+(?:B)?UNNY|\bBUNNY\s+GIRL\b", text):
                parallel_type = "Type A"
            elif not parallel_type and "HONEY NEGLIGEE" in text:
                parallel_type = "Type B"
            display_label = rarity_label + (f" {parallel_type}" if parallel_type else "")
            return {
                "rarityLabel": rarity_label,
                "cardType": card_type,
                "cardTypeKey": card_type_key,
                "parallelType": parallel_type,
                "isAutograph": bool(autograph),
                "isRelic": bool(relic),
                "isOneOfOne": is_one_of_one,
                "displayLabel": display_label,
            }
    return {}


def juicy_rarity_from_context(value: str) -> str:
    normalized = normalize_text(value)
    labels = (
        (("ブラホック", "bra hook"), "Bra hook"),
        (("ブラストラップ", "bra strap"), "Bra strap"),
        (("ニップルスタンプ", "乳拓", "nipple stamp"), "Nipple stamp"),
        (("メッセージ", "message card"), "Message card"),
        (("dnaカード", "dna card", "トリプルdna"), "DNA card"),
        (("直筆サイン", "autograph", "signed"), "Autograph"),
        (("生キス", "キスカード", "kiss card"), "Kiss"),
        (("レアカード", "rare card"), "Rare card"),
        (("レギュラーカード", "regular card", "base card"), "Regular card"),
        (("インサート", "insert card"), "Insert card"),
        (("ランジェリー", "lingerie"), "Lingerie"),
        (("ビキニ", "bikini"), "Bikini"),
        (("コスチューム", "costume"), "Costume"),
        (("チェキ", "cheki"), "Cheki"),
        (("プロモ", "promo"), "Promo"),
    )
    for markers, label in labels:
        if any(marker in normalized for marker in markers):
            return label
    return "Published preview"


def juicy_context_classification(value: str) -> dict[str, Any]:
    """Classify a caption adjacent to one image when OCR has no match."""
    classification = juicy_card_classification(value)
    if classification:
        return classification
    rarity_label = juicy_rarity_from_context(value)
    if rarity_label == "Published preview":
        return {}
    card_type, card_type_key, is_autograph, is_relic = {
        "Bra hook": ("bra_hook_relic", "bra_hook", False, True),
        "Bra strap": ("bra_strap_relic", "bra_strap", False, True),
        "Nipple stamp": ("stamp", "nipple_stamp", False, False),
        "Message card": ("message", "message", False, False),
        "DNA card": ("dna_relic", "dna", False, True),
        "Autograph": ("autograph", "base_autograph", True, False),
        "Kiss": ("kiss", "kiss", False, False),
        "Rare card": ("rare", "", False, False),
        "Regular card": ("base", "base", False, False),
        "Insert card": ("insert", "juicy_special", False, False),
        "Lingerie": ("lingerie_relic", "lingerie_relic", False, True),
        "Bikini": ("bikini_relic", "bikini_relic", False, True),
        "Costume": ("costume_relic", "costume_relic", False, True),
        "Cheki": ("instant_photo", "autographed_instant_photo", False, False),
        "Promo": ("promo", "", False, False),
    }.get(rarity_label, ("preview", "", False, False))
    return {
        "rarityLabel": rarity_label,
        "cardType": card_type,
        "cardTypeKey": card_type_key,
        "parallelType": "",
        "isAutograph": is_autograph,
        "isRelic": is_relic,
        "isOneOfOne": bool(re.search(r"(?:1\s*of\s*1|one[- ]of[- ]one)", value, re.I)),
        "displayLabel": rarity_label,
    }


def juicy_page_series_identities(page) -> list[tuple[str, int | None, str]]:
    """Read release identities from the article title, never from the sidebar."""
    try:
        title_text = page.locator("title").inner_text()
    except Exception:
        title_text = ""
    return juicy_series_identities(title_text)


def extract_juicy_preview_cards(
    page,
    enable_ocr: bool = True,
    expected_series_identity: str = "",
    article_series_identities: list[str] | None = None,
    routing_stats: dict[str, int] | None = None,
) -> list[dict]:
    page_is_complete_gallery = juicy_has_complete_gallery_marker(page.locator("body").inner_text())
    if article_series_identities is None:
        article_series_identities = [item[0] for item in juicy_page_series_identities(page)]
    article_routing_keys = {
        juicy_series_routing_key(identity) for identity in article_series_identities if identity
    }
    expected_routing_key = juicy_series_routing_key(expected_series_identity)
    mixed_article = len(article_routing_keys) > 1
    single_series_verified = (
        len(article_routing_keys) == 1
        and expected_routing_key
        and expected_routing_key in article_routing_keys
    )
    stats = routing_stats if routing_stats is not None else {}
    stats.setdefault("eligible", 0)
    stats.setdefault("matched", 0)
    stats.setdefault("otherSeries", 0)
    stats.setdefault("ambiguous", 0)
    stats.setdefault("ocrProcessed", 0)
    stats.setdefault("ocrBudgetReached", 0)
    images = page.eval_on_selector_all(
        "article img, .article-body img, .entry-content img, .article img, img.pict",
        """els => els.map(img => {
            const link = img.closest('a[href]');
            const candidates = [
                link?.href,
                img.dataset?.original,
                img.dataset?.src,
                img.dataset?.lazySrc,
                img.currentSrc,
                img.src
            ].filter(Boolean);
            const imageUrl = candidates.find(value => /\\.(?:jpe?g|png|webp|gif)(?:[?#].*)?$/i.test(value)) || candidates[0] || '';
            const article = img.closest('.article-body-inner, .article-body, .entry-content, article');
            let precedingText = '';
            let localContext = '';
            if (article) {
                try {
                    const range = document.createRange();
                    range.setStart(article, 0);
                    range.setEndBefore(link || img);
                    precedingText = range.toString().replace(/\\s+/g, ' ').trim().slice(-360);
                } catch (_) {}
                try {
                    const articleImages = Array.from(article.querySelectorAll('img'));
                    const imageIndex = articleImages.indexOf(img);
                    const previousImage = imageIndex > 0 ? articleImages[imageIndex - 1] : null;
                    if (previousImage) {
                        const localRange = document.createRange();
                        localRange.setStartAfter(previousImage.closest('a[href]') || previousImage);
                        localRange.setEndBefore(link || img);
                        localContext = localRange.toString().replace(/\\s+/g, ' ').trim().slice(-240);
                    }
                } catch (_) {}
            }
            const container = img.closest('p, figure, li');
            return {
                imageUrl: imageUrl.trim(),
                altText: (img.alt || img.title || '').trim(),
                context: `${precedingText} ${container?.innerText || ''}`.replace(/\\s+/g, ' ').trim().slice(-500),
                localContext: `${localContext} ${container?.innerText || ''}`.replace(/\\s+/g, ' ').trim().slice(-300),
                width: img.naturalWidth || Number(img.getAttribute('width')) || 0,
                height: img.naturalHeight || Number(img.getAttribute('height')) || 0
            };
        })""",
    )
    items = []
    seen = set()
    blocked_words = (
        "logo", "banner", "profile", "avatar", "twitter", "instagram", "youtube",
        "icon", "favicon", "header", "footer", "button", "emoji",
    )
    blocked_asset_words = (
        "flyer", "フライヤー", "box", "ボックス", "package", "パッケージ",
        "profile", "プロフィール", "event", "イベント", "twitter", "wikipedia",
    )
    for image in images:
        image_url = str(image.get("imageUrl") or "").strip()
        parsed = urlparse(image_url)
        normalized_url = image_url.lower()
        if parsed.scheme not in {"http", "https"}:
            continue
        if parsed.netloc.lower() not in {"juicy-honey.blog.jp", "livedoor.blogimg.jp"}:
            continue
        if not re.search(r"\.(?:jpe?g|png|webp|gif)$", parsed.path, re.IGNORECASE):
            continue
        if any(word in normalized_url for word in blocked_words):
            continue
        if parsed.netloc.lower() == "livedoor.blogimg.jp" and "/juicy_honey_card/imgs/" not in parsed.path.lower():
            continue
        width = int(image.get("width") or 0)
        height = int(image.get("height") or 0)
        if (width and width < 120) or (height and height < 120):
            continue
        canonical_url = parsed._replace(query="", fragment="").geturl()
        if canonical_url in seen:
            continue
        seen.add(canonical_url)
        sequence = len(items) + 1
        alt_text = clean_juicy_context(image.get("altText") or "")
        context = clean_juicy_context(image.get("context") or "")
        local_context = clean_juicy_context(image.get("localContext") or "")
        normalized_alt = normalize_text(alt_text)
        if any(word in normalized_alt for word in blocked_asset_words):
            continue
        if juicy_preview_asset_kind(canonical_url, alt_text):
            continue
        stats["eligible"] += 1

        caption_classification = juicy_context_classification(f"{alt_text} {local_context}")
        supplied_ocr_text = clean_juicy_context(image.get("ocrText") or "")
        supplied_ocr_confidence = float(image.get("ocrConfidence") or 0.0)
        persisted_ocr = _JUICY_OCR_CACHE.get(canonical_url)
        if supplied_ocr_text:
            ocr_text, ocr_confidence = supplied_ocr_text, supplied_ocr_confidence
        elif not enable_ocr:
            ocr_text, ocr_confidence = "", 0.0
        elif persisted_ocr is not None:
            # A completed/no-text row from PostgreSQL is already authoritative
            # for inference. Reuse it directly and keep it out of the OCR
            # budget; the classifier may still be reapplied below.
            ocr_text, ocr_confidence = persisted_ocr
            stats.setdefault("ocrCacheHits", 0)
            stats["ocrCacheHits"] += 1
        elif (
            JUICY_OCR_MAX_IMAGES > 0
            and stats["ocrProcessed"] >= JUICY_OCR_MAX_IMAGES
        ):
            # An explicitly configured OCR budget still preserves a card row
            # for every eligible image in a single-series gallery. Mixed
            # articles cannot safely route an image without OCR, so those
            # images remain ambiguous and are skipped after the budget.
            ocr_text, ocr_confidence = "", 0.0
            stats["ocrBudgetReached"] += 1
        else:
            ocr_text, ocr_confidence = juicy_ocr_text_for_image(canonical_url)
            stats["ocrProcessed"] += 1
        if juicy_preview_asset_kind(canonical_url, alt_text, ocr_text):
            continue

        classification = juicy_card_classification(ocr_text)
        classification_method = "image OCR" if classification else "adjacent official caption"
        if not classification:
            classification = caption_classification
        record_juicy_ocr_observation(
            canonical_url, ocr_text, ocr_confidence, classification
        )
        series_routed = False
        if mixed_article:
            detected = juicy_series_identities(f"{alt_text} {local_context} {ocr_text}")
            detected_keys = {
                juicy_series_routing_key(item[0])
                for item in detected
                if juicy_series_routing_key(item[0]) in article_routing_keys
            }
            if len(detected_keys) != 1:
                stats["ambiguous"] += 1
                continue
            detected_key = next(iter(detected_keys))
            if not expected_routing_key or detected_key != expected_routing_key:
                stats["otherSeries"] += 1
                continue
            stats["matched"] += 1
            series_routed = True
        elif single_series_verified:
            stats["matched"] += 1
            series_routed = True
        rarity_label = str(classification.get("rarityLabel") or "Published preview")
        display_label = str(classification.get("displayLabel") or rarity_label)
        if not page_is_complete_gallery and not classification and not series_routed:
            continue
        meaningful_alt = alt_text
        if re.fullmatch(
            r"(?:IMG|DSC)[_-]?\d+|写真\s*[（(]?\d+[）)]?|[0-9a-f]{24,}|[a-z]{1,8}\d+[a-z0-9_-]*",
            alt_text,
            re.IGNORECASE,
        ):
            meaningful_alt = ""
        title = meaningful_alt or f"{display_label} official preview {sequence}"
        classification_note = ""
        if classification:
            classification_note = f" Card type detected from {classification_method}."
            if classification_method == "image OCR" and ocr_confidence > 0:
                classification_note += f" OCR confidence: {ocr_confidence:.2f}."
        items.append({
            # URL identity keeps retries idempotent and appends images from a
            # different official article instead of overwriting PREVIEW-001.
            "cardCode": "ARCHIVE-" + hashlib.sha256(canonical_url.encode("utf-8")).hexdigest()[:10].upper(),
            "entryKind": PREVIEW_KIND,
            "title": title,
            "description": (
                "Official Juicy Honey card-preview image. The published image file may contain more than one "
                "card front/back, and no individual printed checklist code is exposed in the article HTML."
                + classification_note
                + (f" Context: {context}" if context else "")
            ),
            "rarityLabel": rarity_label,
            "cardType": str(classification.get("cardType") or ""),
            "cardTypeKey": str(classification.get("cardTypeKey") or ""),
            "parallelType": str(classification.get("parallelType") or ""),
            "isAutograph": bool(classification.get("isAutograph")),
            "isRelic": bool(classification.get("isRelic")),
            "isOneOfOne": bool(classification.get("isOneOfOne")),
            "checklistSequence": sequence,
            "imageUrl": canonical_url,
            "altText": meaningful_alt or title,
        })
    return items


def extract_juicy_archive_images(page, page_url: str, max_images: int) -> list[dict]:
    """Return the ordered article gallery, including every published image.

    This is intentionally less selective than card-preview extraction. The
    Telegram assignment flow needs a stable 1-based list so an operator can
    map image positions to existing series manually.
    """
    images = page.eval_on_selector_all(
        "article img, .article-body img, .entry-content img, .article img, img.pict",
        """els => els.map(img => {
            const looksLikeImageUrl = value => {
                try {
                    const path = new URL(value, document.baseURI).pathname.toLowerCase();
                    return /\\.(?:jpe?g|png|webp|gif)(?:[?#].*)?$/.test(path);
                } catch (_) {
                    return false;
                }
            };
            const link = img.closest('a[href]');
            const linked = link?.href || '';
            const linkedImage = looksLikeImageUrl(linked) ? linked : '';
            const discovered = [
                img.dataset?.original,
                img.dataset?.src,
                img.dataset?.lazySrc,
                img.currentSrc,
                img.src
            ].find(looksLikeImageUrl) || '';
            const article = img.closest('.article-body-inner, .article-body, .entry-content, article');
            let context = '';
            if (article) {
                try {
                    context = article.innerText || '';
                } catch (_) {}
            }
            return {
                imageUrl: linkedImage || discovered,
                altText: (img.alt || img.title || '').trim(),
                context: context.replace(/\\s+/g, ' ').trim().slice(0, 500),
                width: img.naturalWidth || Number(img.getAttribute('width')) || 0,
                height: img.naturalHeight || Number(img.getAttribute('height')) || 0
            };
        }).filter(item => item.imageUrl)""",
    )
    items = []
    seen = set()
    blocked_words = (
        "logo", "banner", "profile", "avatar", "twitter", "instagram", "youtube",
        "icon", "favicon", "header", "footer", "button", "emoji",
    )
    for image in images:
        raw_url = str(image.get("imageUrl") or "").strip()
        parsed = urlparse(urljoin(page_url, raw_url))
        if parsed.scheme not in {"http", "https"}:
            continue
        if parsed.netloc.lower() not in {"juicy-honey.blog.jp", "livedoor.blogimg.jp"}:
            continue
        if not re.search(r"\.(?:jpe?g|png|webp|gif)$", parsed.path, re.IGNORECASE):
            continue
        normalized_url = parsed.geturl().lower()
        if any(word in normalized_url for word in blocked_words):
            continue
        if parsed.netloc.lower() == "livedoor.blogimg.jp" and "/juicy_honey_card/imgs/" not in parsed.path.lower():
            continue
        width = int(image.get("width") or 0)
        height = int(image.get("height") or 0)
        if (width and width < 120) or (height and height < 120):
            continue
        canonical_url = parsed._replace(query="", fragment="").geturl()
        if canonical_url in seen:
            continue
        seen.add(canonical_url)
        sequence = len(items) + 1
        items.append({
            "originalUrl": canonical_url,
            "sourceUrl": page_url,
            "altText": clean_juicy_context(image.get("altText") or ""),
            "context": clean_juicy_context(image.get("context") or ""),
            "mediaType": "release_image",
            "mimeType": infer_mime_type(canonical_url),
            "width": width,
            "height": height,
            "articleImageSequence": sequence,
        })
        if len(items) >= max_images:
            break
    return items


def extract_juicy_archive_gallery(page, archive_url: str, max_images: int) -> list[dict]:
    """Collect the ordered images across all pagination pages for a month."""
    pending_pages = [archive_url]
    seen_pages = set()
    items = []
    seen_images = set()
    while pending_pages and len(items) < max_images and len(seen_pages) < 20:
        page_url = pending_pages.pop(0)
        if page_url in seen_pages:
            continue
        seen_pages.add(page_url)
        try:
            page.goto(page_url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(1200)
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(1000)
        except Exception as exc:
            progress(f"[juicy-honey] archive image page failed url={page_url} error={exc}")
            continue

        for item in extract_juicy_archive_images(page, page.url, max_images - len(items)):
            original_url = str(item.get("originalUrl") or "").strip()
            if not original_url or original_url in seen_images:
                continue
            seen_images.add(original_url)
            item["articleImageSequence"] = len(items) + 1
            items.append(item)
            if len(items) >= max_images:
                break

        if len(items) >= max_images:
            break
        pagination_urls = page.eval_on_selector_all(
            "a[href]",
            """els => els.map(link => link.href || '').filter(Boolean)""",
        )
        for href in pagination_urls:
            pagination_url = juicy_archive_pagination_url(href, archive_url)
            if pagination_url and pagination_url not in seen_pages and pagination_url not in pending_pages:
                pending_pages.append(pagination_url)
    return items


def extract_announced_total(text: str) -> int:
    patterns = (
        r"<\s*Collect\s+All\s+(\d{1,4})\s+Cards\s*>",
        r"(?:商品構成\s*)?全\s*(\d{1,4})\s*(?:類|種類)",
        r"全\s*(\d{1,4})\s*種類\s*[（(]?予定",
        r"(\d{1,4})\s*種類\s*予定",
    )
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = int(match.group(1))
            if 1 <= value <= 5000:
                return value
    return 0


def composition_region(text: str, host: str) -> list[str]:
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    start_markers = ["商品構成", "全127種類", "<Collect All", "[REGULAR CARDS]"]
    if host.endswith("juicy-honey.blog.jp"):
        start_markers = ["<Collect All", "[REGULAR CARDS]"]
    start = 0
    for index, line in enumerate(lines):
        if any(marker.lower() in line.lower() for marker in start_markers):
            start = index
            break
    end_markers = ("プロフィール", "トレーディングカードは、1ボックス", "※種類数", "※パックには", "<JH PLUS", "システム商品コード")
    end = len(lines)
    for index in range(start + 1, len(lines)):
        if any(marker.lower() in lines[index].lower() for marker in end_markers):
            end = index
            break
    return lines[start:end]


def clean_composition_title(value: str) -> str:
    value = re.sub(r"^[◆●■★☆?・\-\s]+", "", value).strip()
    value = re.sub(r"\[(?:Limited\s+to|#'?d\s+to)[^\]]+\]", "", value, flags=re.IGNORECASE)
    value = re.sub(r"[|:：\s]+$", "", value).strip()
    return re.sub(r"\s+", " ", value)


def is_major_group(title: str, raw_line: str) -> bool:
    normalized = normalize_text(title)
    return raw_line.startswith(("◆", "★", "[")) or any(word in normalized for word in MAJOR_GROUP_WORDS)


def composition_count(line: str) -> tuple[int, int, int] | None:
    patterns = (
        r"[<＜]\s*(\d{1,4})\s*種\s*[>＞]",
        r"(\d{1,4})\s*種類",
        # Prefer the Japanese design count before looking for an English
        # "Card" count. Otherwise "1of1 Card 13種" is misread as one design.
        r"(\d{1,4})\s*種(?!類)",
        r"(\d{1,4})\s*cards?\b",
    )
    for pattern in patterns:
        match = re.search(pattern, line, re.IGNORECASE)
        if match:
            return int(match.group(1)), match.start(), match.end()
    if "card" in line.lower() or "カード" in line:
        match = re.search(r"(?:[:：|]\s*|\s)(\d{1,4})\s*$", line)
        if match:
            return int(match.group(1)), match.start(), match.end()
    return None


def extract_composition(text: str, host: str) -> list[dict]:
    lines = composition_region(text, host)
    items = []
    current_section = "Published composition"
    seen = set()
    for raw_line in lines:
        if not raw_line or re.search(r"(?:商品構成|Collect All|全\s*\d+\s*(?:類|種類))", raw_line, re.IGNORECASE):
            continue
        bracket_heading = re.match(r"^\[([^\]]+CARDS?)\]", raw_line, re.IGNORECASE)
        if bracket_heading and composition_count(raw_line) is None:
            current_section = clean_composition_title(bracket_heading.group(1).title())
            continue
        parsed = composition_count(raw_line)
        if parsed is None:
            continue
        count, count_start, _ = parsed
        if count <= 0 or count > 5000:
            continue
        title = clean_composition_title(raw_line[:count_start])
        title = re.sub(r"[<＜\[(]+$", "", title).strip()
        if not title or title.lower() in {"type", "card"}:
            continue
        key = (normalize_text(title), count, normalize_text(current_section))
        if key in seen:
            continue
        seen.add(key)
        sequence = len(items) + 1
        rarity = title if is_major_group(title, raw_line) else current_section
        announced_count = count
        items.append({
            "cardCode": f"COMP-{sequence:03d}",
            "entryKind": COMPOSITION_KIND,
            "title": title,
            "description": raw_line,
            "rarityLabel": rarity,
            "announcedCount": announced_count,
            "checklistSequence": sequence,
            "imageUrl": "",
            "altText": "",
        })
        if raw_line.startswith("●") or is_major_group(title, raw_line):
            current_section = title
    return items


def extract_cards(rows: list[dict], max_cards: int) -> list[dict]:
    items = []
    seen = set()
    for row in rows:
        raw_text = row.get("text", "")
        text = normalize(raw_text)
        if not text or any(word in text for word in IGNORE_WORDS) and "card" not in text:
            continue
        codes = CODE_PATTERN.findall(raw_text)
        if not codes:
            codes = NUMBER_PATTERN.findall(raw_text)
        for raw_code in codes:
            code = normalize_code(raw_code)
            if not code or code in seen or code in {"2024", "2025", "2026"} or is_metadata_code(code):
                continue
            seen.add(code)
            rarity = ""
            for label in ("signed", "autograph", "rare", "special", "parallel", "regular", "base"):
                if label in text:
                    rarity = label
                    break
            items.append({
                "cardCode": code,
                "entryKind": "card",
                "title": row.get("altText") or raw_text[:240],
                "description": raw_text[:480],
                "rarityLabel": rarity,
                "checklistSequence": len(items) + 1,
                "imageUrl": row.get("imageUrl", ""),
                "altText": row.get("altText", ""),
            })
            if len(items) >= max_cards:
                return items
    return items


def normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFKC", str(value or ""))
    return re.sub(r"\s+", " ", value).strip().lower()


def normalize(value: str) -> str:
    return normalize_text(value)


def normalize_code(value: str) -> str:
    value = re.sub(r"\s+", "", value.strip().upper())
    return value.lstrip("#") if value.startswith("#") else value


def is_metadata_code(value: str) -> bool:
    return value.startswith(("VOL", "VOLUME", "PAGE", "ITEM", "NO", "CARD"))

EXCLUDED_IMAGE_MARKERS = (
    "favicon",
    "logo",
    "loading",
    "spacer",
    "tracking",
    "pixel",
    "avatar",
    "header-icon",
    "footer-icon",
    "sns-icon",
    "transparent",
    "placeholder",
    "noimage",
    "no-image",
    "1x1",
)


def media_build_terms(request: dict) -> list[str]:
    raw_terms = list(request.get("matchTerms") or [])
    raw_terms.extend([request.get("title", ""), request.get("subtitle", "")])
    volume = request.get("volume")
    if volume:
        raw_terms.extend([f"vol.{volume}", f"vol. {volume}", f"vol{volume}"])
    terms = []
    for value in raw_terms:
        normalized = media_normalize_text(str(value))
        if normalized and normalized not in terms:
            terms.append(normalized)
        # Subtitles often begin with the model name followed by a title.
        first = media_normalize_text(re.split(r"[～~|]", str(value), maxsplit=1)[0])
        if len(first) >= 2 and first not in terms:
            terms.append(first)
    for value in raw_terms:
        normalized = media_normalize_text(str(value))
        series_marker = re.search(
            r"\b(?:woohoo\s+girls|cj\s+sexy(?:\s+card\s+series)?)\b",
            normalized,
            re.I,
        )
        if not series_marker:
            continue
        # Release-index titles can contain a release date between the model
        # name and the series name. Keep the model as a standalone term so a
        # category page can still be matched when its wording differs.
        model = normalized[: series_marker.start()]
        model = re.sub(r"^\s*(?:商品情報\s*)", "", model)
        model = re.sub(r"\s*20\d{2}.*?(?:発売|release)\s*$", "", model, flags=re.I)
        if len(model) >= 2 and model not in terms:
            terms.append(model)
    return terms


def media_normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().lower()


def image_label_text(image_url: str, alt_text: str = "") -> str:
    """Return image filename/alt labels without host-directory noise."""
    path = unquote(urlparse(str(image_url or "")).path)
    filename = path.rsplit("/", 1)[-1]
    return media_normalize_text(f"{filename} {alt_text}")


def is_series_cover_label(value: str) -> bool:
    return bool(re.search(r"(?<![a-z])(fly(?:er)?|cover|chirashi)(?![a-z])", value, re.I))


def media_term_matches(term: str, text: str) -> bool:
    """Match release numbers without treating vol.1 as vol.19 or vol.10."""
    if not term:
        return False
    if term[-1].isdigit():
        return re.search(re.escape(term) + r"(?!\d)", text) is not None
    return term in text


def media_is_release_signal(term: str) -> bool:
    return any(character.isdigit() or ord(character) > 127 for character in term)


def is_woohoo_category_url(parsed) -> bool:
    return (
        parsed.netloc.lower().endswith("gain-p.jp")
        and parsed.path.lower().rstrip("/") == "/products/list"
        and bool(parsed.query)
    )


def volume_numbers(terms: list[str]) -> set[str]:
    numbers = set()
    for term in terms:
        for match in re.finditer(r"\b(?:vol(?:ume)?\.?\s*|vol)\s*(\d+)\b", term, re.I):
            numbers.add(match.group(1))
    return numbers


def release_number_matches(text: str, number: str) -> bool:
    return bool(
        re.search(
            rf"\b(?:vol(?:ume)?\.?\s*|vol)\s*{re.escape(number)}\b",
            text,
            re.I,
        )
        or re.search(rf"第\s*{re.escape(number)}\s*弾", text)
    )


def is_probable_image_url(image_url: str, source: str) -> bool:
    if source != "linked":
        return True
    path = urlparse(image_url).path.lower()
    return bool(
        re.search(r"\.(?:jpe?g|png|webp|gif|avif)$", path)
        or re.search(r"/(?:image|images|img|upload|uploads)/", path)
    )


def page_matches_release(page, terms: list[str]) -> bool:
    page_text = page.evaluate(
        "() => `${document.title || ''} ${document.body?.innerText || document.body?.textContent || ''}`"
    )
    haystack = media_normalize_text(str(page_text or ""))
    if not haystack:
        return False

    # A category page is valid only when its own text contains the requested
    # volume. This prevents a generic title index from being treated as the
    # release page.
    matched_volume = any(
        release_number_matches(haystack, number)
        for number in volume_numbers(terms)
    )
    if not matched_volume:
        return False

    # If a model-specific term is available, require it too. Generic terms
    # such as “WooHoo Girls” and “company” are intentionally ignored here.
    identity_terms = [
        term
        for term in terms
        if len(term) >= 2
        and not re.search(r"\b(?:woohoo|girls|cj|sexy|card|series|company|vol|volume)\b", term, re.I)
        and not term.isdigit()
    ]
    return not identity_terms or any(media_term_matches(term, haystack) for term in identity_terms)


def media_resolve_release_page(page, source_url: str, terms: list[str]) -> bool:
    parsed = urlparse(source_url)
    path = parsed.path.lower()
    # These sources are already release/product detail pages.
    if "/archives/" in path or "/view/item/" in path:
        return True
    if "/jyu-toku/" in path and "/category/release" not in path:
        return True
    if is_woohoo_category_url(parsed) and page_matches_release(page, terms):
        return True

    links = page.eval_on_selector_all(
        "a[href]",
        """els => els.map(a => ({
            href: a.href,
            text: (a.innerText || a.textContent || '').trim(),
            alt: (a.querySelector('img')?.alt || '').trim()
        }))""",
    )
    source_host = parsed.netloc.lower()
    best_url = ""
    best_score = 0
    for link in links:
        href = link.get("href", "")
        if not href.startswith(("http://", "https://")):
            continue
        if urlparse(href).netloc.lower() != source_host:
            continue
        haystack = media_normalize_text(f"{link.get('text', '')} {link.get('alt', '')} {href}")
        matched_terms = [term for term in terms if len(term) >= 2 and media_term_matches(term, haystack)]
        if not any(media_is_release_signal(term) for term in matched_terms):
            continue
        score = len(matched_terms) * 3
        if "vol." in haystack or "trading" in haystack or "トレカ" in haystack:
            score += 1
        if score > best_score:
            best_score = score
            best_url = href
    if best_url and best_score >= 3 and best_url.rstrip("/") != source_url.rstrip("/"):
        page.goto(best_url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(1200)
        return True

    # Older CJ releases are spread over JYUTOKU's paginated archive. The seed
    # can point at the canonical archive root, so search each archive page
    # before rejecting the release and dropping its generic listing images.
    if source_host == "jyu-toku.sakura.ne.jp" and "/category/release" in path:
        archive_root = source_url.rstrip("/")
        for page_number in range(2, 35):
            archive_url = f"{archive_root}/page/{page_number}/"
            page.goto(archive_url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(600)
            page_links = page.eval_on_selector_all(
                "a[href]",
                """els => els.map(a => ({
                    href: a.href,
                    text: (a.innerText || a.textContent || '').trim(),
                    alt: (a.querySelector('img')?.alt || '').trim()
                }))""",
            )
            for link in page_links:
                href = link.get("href", "")
                if not href.startswith(("http://", "https://")):
                    continue
                if urlparse(href).netloc.lower() != source_host:
                    continue
                haystack = media_normalize_text(f"{link.get('text', '')} {link.get('alt', '')} {href}")
                matched_terms = [term for term in terms if len(term) >= 2 and media_term_matches(term, haystack)]
                if not any(media_is_release_signal(term) for term in matched_terms):
                    continue
                if len(matched_terms) * 3 >= 3:
                    page.goto(href, wait_until="domcontentloaded", timeout=60000)
                    page.wait_for_timeout(1200)
                    return True
    return False


def collect_images(page, terms: list[str]) -> list[dict]:
    candidates = page.eval_on_selector_all(
        "img",
        """els => els.flatMap(img => {
            const parseSrcset = value => (value || '')
                .split(',')
                .map(part => part.trim().split(/\\s+/)[0])
                .filter(Boolean);
            const pictureSources = Array.from(
                img.closest('picture')?.querySelectorAll('source') || []
            ).flatMap(source => parseSrcset(
                source.srcset || source.dataset.srcset || source.dataset.lazySrcset
            ));
            const linked = img.closest('a[href]')?.href || '';
            const looksLikeImageUrl = value => {
                try {
                    const path = new URL(value, document.baseURI).pathname.toLowerCase();
                    return /\\.(?:jpe?g|png|webp|gif|avif)$/.test(path)
                        || /\\/(?:image|images|img|upload|uploads)\\//.test(path);
                } catch (_) {
                    return false;
                }
            };
            const linkedImage = looksLikeImageUrl(linked) ? linked : '';
            const values = [
                img.currentSrc,
                img.dataset.original,
                img.dataset.src,
                img.dataset.lazySrc,
                img.dataset.originalSrc,
                ...parseSrcset(img.dataset.srcset || img.dataset.lazySrcset),
                ...parseSrcset(img.srcset),
                ...pictureSources,
                img.src,
                linkedImage,
            ].filter(Boolean);
            const unique = [...new Set(values)];
            const inArticle = Boolean(img.closest(
                'article, main, .entry-content, .article-body, .post-content, .article'
            ));
            return unique.map(url => ({
                url,
                alt: (img.alt || img.title || '').trim(),
                width: img.naturalWidth || Number(img.getAttribute('width')) || 0,
                height: img.naturalHeight || Number(img.getAttribute('height')) || 0,
                source: url === linkedImage ? 'linked' : 'img',
                scoreBoost: (inArticle ? 35 : 0) + (url === linkedImage ? 20 : 0)
            }));
        })""",
    )
    og_images = page.eval_on_selector_all(
        'meta[property="og:image"], meta[name="twitter:image"], meta[property="twitter:image"]',
        """els => els.map(meta => ({
            url: meta.content || '', alt: '', width: 0, height: 0, source: 'meta'
        }))""",
    )
    for candidate in og_images:
        candidate["scoreBoost"] = 80
    candidates.extend(og_images)

    for candidate in candidates:
        text = media_normalize_text(f"{candidate.get('url', '')} {candidate.get('alt', '')}")
        candidate["termMatches"] = sum(1 for term in terms if len(term) >= 2 and media_term_matches(term, text))
    return candidates


def normalize_images(candidates: list[dict], page_url: str, max_images: int) -> list[dict]:
    ranked = []
    seen = set()
    for candidate in candidates:
        raw_url = candidate.get("url", "").strip()
        if not raw_url:
            continue
        image_url = urljoin(page_url, raw_url)
        if not image_url.startswith(("http://", "https://")) or image_url in seen:
            continue
        if page_url.startswith("https://") and image_url.startswith("http://"):
            continue
        lowered = image_url.lower()
        if any(marker in lowered for marker in EXCLUDED_IMAGE_MARKERS):
            continue
        path = urlparse(image_url).path.lower()
        if path.endswith((".svg", ".ico")):
            continue
        if not is_probable_image_url(image_url, candidate.get("source", "")):
            continue
        canonical_path = re.sub(r"-\d+x\d+(?=\.[a-z0-9]+$)", "", path)
        width = int(candidate.get("width") or 0)
        height = int(candidate.get("height") or 0)
        source = candidate.get("source")
        has_unknown_dimensions = source in {"meta", "linked"}
        if not has_unknown_dimensions and width and height and (width < 240 or height < 180):
            continue
        score = int(candidate.get("scoreBoost") or 0)
        score += min((width * height) // 50000, 50)
        score += int(candidate.get("termMatches") or 0) * 25
        media_type = classify_media(image_url, candidate.get("alt", ""))
        score += {
            "release_image": 35,
            "card_preview": 25,
            "box": 5,
            "pack": 5,
        }.get(media_type, 0)
        descriptor = image_label_text(image_url, candidate.get("alt", ""))
        if any(word in descriptor for word in ("product", "item", "card", "box", "pack", "トレカ", "商品")):
            score += 20
        if width >= 600 and height >= 400:
            score += 15
        filename_key = canonical_path.rsplit("/", 1)[-1] or canonical_path
        canonical_key = (media_type, filename_key)
        ranked.append((score, image_url, candidate, width, height, canonical_key, media_type))
        seen.add(image_url)

    ranked.sort(key=lambda item: item[0], reverse=True)
    ranked = [
        *[item for item in ranked if item[6] == "series_cover"],
        *[item for item in ranked if item[6] != "series_cover"],
    ]
    items = []
    selected_canonical = set()
    for _, image_url, candidate, width, height, canonical_key, media_type in ranked:
        if canonical_key in selected_canonical:
            continue
        selected_canonical.add(canonical_key)
        items.append({
            "originalUrl": image_url,
            "sourceUrl": page_url,
            "altText": candidate.get("alt", ""),
            "mediaType": media_type,
            "mimeType": infer_mime_type(image_url),
            "width": width,
            "height": height,
        })
        if len(items) >= max_images:
            break
    return items


def classify_media(image_url: str, alt_text: str) -> str:
    value = image_label_text(image_url, alt_text)
    if is_series_cover_label(value):
        return "series_cover"
    if "checklist" in value or "チェックリスト" in value:
        return "checklist"
    if "pack" in value or "パック" in value:
        return "pack"
    if "box" in value or "ボックス" in value:
        return "box"
    if "card" in value or "トレカ" in value:
        return "card_preview"
    return "release_image"


def infer_mime_type(image_url: str) -> str:
    path = urlparse(image_url).path.lower()
    for extension, mime_type in (
        (".webp", "image/webp"),
        (".png", "image/png"),
        (".gif", "image/gif"),
        (".jpeg", "image/jpeg"),
        (".jpg", "image/jpeg"),
    ):
        if path.endswith(extension):
            return mime_type
    return ""

def as_bool(value: Any, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def bounded_int(value: Any, default: int, minimum: int, maximum: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = default
    return max(minimum, min(parsed, maximum))


def normalize_publisher(value: Any) -> str:
    publisher = str(value or "").strip().lower()
    return {
        "woohoo-girls": "woohoo",
        "woohoo-company": "woohoo",
        "tic": "produce-216",
        "hits-limited": "hits",
        "jyutoku": "cj-sexy",
        "jyu-toku": "cj-sexy",
        "cj": "cj-sexy",
        "havarossa": "juicy-honey",
        "juicy": "juicy-honey",
        "formosa": "formosa-sexy",
        "formosa-dreamers": "formosa-sexy",
        "rakuten": "rakuten-girls",
        "rakuten-monkeys": "rakuten-girls",
    }.get(publisher, publisher)


def is_cj_release(release: dict) -> bool:
    """Identify CJ SEXY releases before opening the official source page."""
    if normalize_publisher(release.get("publisherKey")) == "cj-sexy":
        return True
    values = [
        release.get("title"), release.get("subtitle"),
        release.get("sourceUrl"), release.get("checklistUrl"),
    ]
    if isinstance(release.get("matchTerms"), list):
        values.extend(release.get("matchTerms") or [])
    return any(
        re.search(r"cj[\s_-]*sexy", normalize_text(value), re.I)
        for value in values
        if value
    )


def release_terms(release: dict) -> list[str]:
    values = list(release.get("matchTerms") or [])
    for key in ("title", "subtitle", "modelName"):
        value = str(release.get(key) or "").strip()
        if value:
            values.append(value)
    return values


def discover_releases(browser, request: dict) -> tuple[str, list[dict], list[str]]:
    publisher = normalize_publisher(request.get("publisher"))
    all_publishers = as_bool(request.get("allPublishers"), False) or publisher in {"", "all"}
    max_pages = bounded_int(request.get("maxPages"), 20, 1, 100)
    max_months = bounded_int(
        request.get("maxMonths", request.get("maxArchiveMonths")),
        240, 1, 500,
    )
    # Zero means scan the full requested history. Set a positive value only
    # when the caller intentionally wants an early-stop optimization.
    empty_month_limit = bounded_int(request.get("emptyMonthLimit"), 0, 0, 120)
    publishers = [
        "woohoo", "hits", "produce-216", "cj-sexy", "juicy-honey", "mint",
        "formosa-sexy", "rakuten-girls",
    ] if all_publishers else [publisher]

    releases: list[dict] = []
    warnings: list[str] = []
    for key in publishers:
        progress(f"[catalog] discovery started publisher={key}")
        try:
            if key == "woohoo":
                found = discover_woohoo(browser)
            elif key == "produce-216":
                found = discover_tic(browser, max_pages)
            elif key == "hits":
                found = discover_hits(browser, max_pages)
            elif key == "cj-sexy":
                found = discover_cj(browser, max_pages, include_non_cj=all_publishers)
            elif key == "jutoku":
                found = [item for item in discover_cj(browser, max_pages, include_non_cj=True) if item.get("publisherKey") == "jutoku"]
            elif key == "juicy-honey":
                target_url = str(request.get("sourceUrl") or "").strip()
                target_path = urlparse(target_url).path
                target_is_article = bool(
                    re.fullmatch(r"/archives/\d+\.html", target_path)
                )
                if request.get("releaseSlug") or target_is_article:
                    if not target_url:
                        # A newly announced series has no catalog row yet, so
                        # there is no canonical article URL to pass to the
                        # fast targeted path. Fall back to the normal archive
                        # scan; the Go handler filters the hydrated results to
                        # the requested release slug before importing it.
                        progress(
                            "[juicy-honey] targeted discovery has no sourceUrl; "
                            "falling back to archive scan"
                        )
                        found = discover_juicy(
                            browser,
                            max_months,
                            empty_month_limit,
                            max_pages,
                            source_url=target_url,
                        )
                    else:
                        found = discover_juicy_target(browser, target_url)
                else:
                    found = discover_juicy(
                        browser,
                        max_months,
                        empty_month_limit,
                        max_pages,
                        source_url=target_url,
                    )
            elif key == "mint":
                found = discover_mint(browser, max_pages)
            elif key == "formosa-sexy":
                found = discover_formosa(
                    browser, max_pages, source_url=str(request.get("sourceUrl") or "").strip()
                )
            elif key == "rakuten-girls":
                found = discover_rakuten_girls(
                    browser, max_pages, source_url=str(request.get("sourceUrl") or "").strip()
                )
            else:
                found = []
                warnings.append(f"unsupported publisher: {key}")
            releases.extend(found)
            progress(f"[catalog] discovery completed publisher={key} found={len(found)}")
        except Exception as exc:
            warning = f"{key} discovery failed: {exc}"
            progress(f"[catalog] {warning}")
            if not all_publishers:
                raise RuntimeError(warning) from exc
            warnings.append(warning)

    releases = dedupe_releases(releases)
    if not releases:
        warnings.append("no release candidates found")
    return ("all" if all_publishers else publisher), releases, warnings


def checklist_for_release(browser, release: dict, max_cards: int) -> dict:
    source_url = str(release.get("checklistUrl") or release.get("sourceUrl") or "").strip()
    if not source_url.startswith(("http://", "https://")):
        return {
            "sourceUrl": source_url,
            "pageUrl": "",
            "items": [],
            "checklistImages": [],
            "announcedTotal": 0,
            "warnings": ["checklist skipped: release has no valid source URL"],
        }

    request = {
        **release,
        "sourceUrl": source_url,
        "matchTerms": release_terms(release),
    }
    # Card media is the retailer-backed stage for CJ SEXY. Composition media
    # deliberately continues through the official JYUTOKU release page so the
    # composition sheet remains available as series evidence.
    if is_cj_release(request) and as_bool(request.get("cardMedia"), False):
        items, warnings = scrape_suruga_cj_cards(browser, request, max_cards)
        if not items:
            warnings.append("Suruga-ya returned no CJ SEXY card rows")
        return {
            "sourceUrl": source_url,
            "pageUrl": source_url,
            "items": items,
            "checklistImages": [],
            "imageOcrResults": [],
            "announcedTotal": 0,
            "warnings": warnings,
        }
    terms = build_terms(request)
    page = browser.new_page()
    try:
        # JYUTOKU pages can keep third-party resources open after the usable
        # document has been committed. Waiting for DOMContentLoaded makes a
        # valid release page look like a scraper failure.
        goto_rendered_page(page, source_url)
        result_page_url = page.url
        release_page_found = resolve_release_page(page, source_url, terms)
        checklist_fallback_used = False
        if not release_page_found:
            source_host = urlparse(source_url).netloc.lower()
            publisher_key = str(release.get("publisherKey") or "").strip().lower()
            if source_host.endswith("gain-p.jp") and publisher_key == "woohoo":
                # Historical WooHoo product pages can fail release matching
                # even though the official checklist page is available. Try
                # the verified checklist resolver before giving up.
                checklist_fallback_used = resolve_gain_checklist_page(page, terms)
                if checklist_fallback_used:
                    result_page_url = page.url
            if not checklist_fallback_used:
                return {
                    "sourceUrl": source_url,
                    "pageUrl": result_page_url,
                    "items": [],
                    "checklistImages": [],
                    "announcedTotal": 0,
                    "warnings": ["no matching official release page found; checklist was not imported"],
                }

        host = urlparse(page.url).netloc.lower()
        body_text = page.locator("body").inner_text()
        announced_total = extract_announced_total(body_text)
        composition = extract_composition(body_text, host)
        checklist_images: list[dict] = []
        warnings: list[str] = []

        if host.endswith("gain-p.jp"):
            # Recent WooHoo releases can appear in the product catalog before
            # Gain-P publishes their dedicated checklist page. Preserve the
            # product page sheet before resolve_gain_checklist_page navigates
            # to the checklist index.
            product_checklist_images = []
            if str(release.get("publisherKey") or "").lower() == "woohoo" and not checklist_fallback_used:
                product_checklist_images = extract_woohoo_product_checklist_images(page)
            dedicated_checklist_found = checklist_fallback_used or resolve_gain_checklist_page(page, terms)
            if dedicated_checklist_found:
                result_page_url = page.url
                checklist_images = extract_checklist_images(page)
            if not checklist_images and product_checklist_images:
                checklist_images = product_checklist_images
                result_page_url = source_url
                warnings.append(
                    "dedicated checklist page is not published yet; using the official product composition sheet"
                )
            elif not dedicated_checklist_found:
                warnings.append(
                    "official checklist page was not found on Gain-P; only product-page composition text is available"
                )
            items = composition[:max_cards]
        elif host.endswith("juicy-honey.blog.jp"):
            expected_series_identity = str(release.get("editionKey") or "").strip()
            if not expected_series_identity:
                expected_series_identity = juicy_series_identity(
                    " ".join([
                        str(release.get("title") or ""),
                        str(release.get("subtitle") or ""),
                    ])
                )[0]
            result_page_url, previews, preview_warnings = resolve_juicy_preview_article(
                page,
                terms,
                str(release.get("releaseDate") or "").strip(),
                expected_series_identity,
                # OCR is intentionally disabled for every publisher. Ignore
                # any legacy request flag so production jobs cannot opt in.
                enable_ocr=False,
            )
            items = (previews + composition)[:max_cards]
            warnings.extend(preview_warnings)
        elif host.endswith("jyu-toku.sakura.ne.jp"):
            # JYUTOKU's historical pages often publish the complete
            # composition as a linked image in the article body, with no
            # corresponding text for extract_composition to parse. Keep the
            # official composition sheet as checklist evidence for compositionMedia;
            # cardMedia has already returned through the Suruga-ya branch above.
            checklist_images = extract_jyutoku_composition_images(page)
            items = composition[:max_cards]
        elif host.endswith(("tic.jp", "toreca.biz", "target.co.jp")):
            items = composition[:max_cards]
        elif host.endswith("mint-mall.net"):
            rows = extract_candidate_rows(page)
            items = extract_cards(rows, max_cards)
            warnings.append("MINT is secondary evidence and cannot establish official checklist completeness")
        else:
            rows = extract_candidate_rows(page)
            items = extract_cards(rows, max_cards)

        if composition and not any(item.get("entryKind") == PREVIEW_KIND for item in items):
            warnings.append("publisher exposes card composition counts, not individual numbered card records")
        if checklist_images:
            warnings.append(f"official checklist sheets found: {len(checklist_images)}")
        if not items and not checklist_images:
            warnings.append("no card checklist entries found on the official release page")

        return {
            "sourceUrl": source_url,
            "pageUrl": result_page_url,
            "items": items,
            "checklistImages": checklist_images,
            "imageOcrResults": juicy_ocr_results(),
            "announcedTotal": announced_total,
            "warnings": warnings,
        }
    finally:
        close_quietly(page)


def media_for_release(browser, release: dict, max_images: int) -> dict:
    source_url = str(release.get("sourceUrl") or "").strip()
    if not source_url.startswith(("http://", "https://")):
        return {
            "sourceUrl": source_url,
            "pageUrl": "",
            "items": [],
            "warnings": ["media skipped: release has no valid source URL"],
        }

    request = {
        **release,
        "sourceUrl": source_url,
        "matchTerms": release_terms(release),
    }
    terms = media_build_terms(request)
    page = browser.new_page()
    try:
        goto_rendered_page(page, source_url)
        if as_bool(release.get("archiveGallery"), False):
            items = extract_juicy_archive_gallery(page, source_url, max_images)
            return {
                "sourceUrl": source_url,
                "pageUrl": page.url,
                "items": items,
                "warnings": [] if items else ["no suitable archive gallery images found"],
            }
        if not media_resolve_release_page(page, source_url, terms):
            return {
                "sourceUrl": source_url,
                "pageUrl": page.url,
                "items": [],
                "warnings": ["no matching release page found; generic listing images were not saved"],
            }

        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(1000)
        if urlparse(page.url).netloc.lower().endswith("juicy-honey.blog.jp"):
            # Juicy Honey's first article image is the cover/flyer. The image
            # is commonly rendered as a -s thumbnail inside an anchor whose
            # href points at the full-size livedoor.blogimg.jp asset. Do not
            # rank the thumbnail against card previews; keep this one cover.
            items = extract_first_juicy_cover_image(page, page.url)
        else:
            candidates = collect_images(page, terms)
            items = normalize_images(candidates, page.url, max_images)
        return {
            "sourceUrl": source_url,
            "pageUrl": page.url,
            "items": items,
            "warnings": [] if items else ["no suitable release product images found"],
        }
    finally:
        close_quietly(page)


def normalize_first_juicy_cover_image(items: Any, page_url: str) -> list[dict]:
    """Keep the strongest full-size cover image from a Juicy article body.

    Most release posts lead with the flyer, but sales posts can lead with many
    individual card images and place a ``Fly_*`` cover at the end. Explicit
    cover/flyer evidence therefore wins; DOM order remains the fallback.
    """
    valid: list[tuple[int, int, dict, str]] = []
    for sequence, raw in enumerate(items if isinstance(items, list) else []):
        if not isinstance(raw, dict):
            continue
        image_url = str(raw.get("imageUrl") or "").strip()
        parsed = urlparse(urljoin(page_url, image_url))
        if parsed.scheme not in {"http", "https"}:
            continue
        if parsed.netloc.lower() not in {"juicy-honey.blog.jp", "livedoor.blogimg.jp"}:
            continue
        if "/juicy_honey_card/imgs/" not in parsed.path.lower() and parsed.netloc.lower() == "livedoor.blogimg.jp":
            continue
        if not re.search(r"\.(?:jpe?g|png|webp|gif)$", parsed.path, re.I):
            continue
        canonical_url = parsed._replace(query="", fragment="").geturl()
        evidence = " ".join([
            canonical_url,
            str(raw.get("altText") or ""),
            str(raw.get("titleText") or ""),
        ])
        valid.append((0 if juicy_cover_hint(evidence) else 1, sequence, raw, canonical_url))

    if valid:
        _, _, raw, canonical_url = min(valid, key=lambda item: (item[0], item[1]))
        return [{
            "originalUrl": canonical_url,
            "sourceUrl": page_url,
            "altText": clean_juicy_context(raw.get("altText") or raw.get("titleText") or ""),
            "mimeType": infer_mime_type(canonical_url),
            "mediaType": "series_cover",
            "width": int(raw.get("width") or 0),
            "height": int(raw.get("height") or 0),
        }]
    return []


def extract_first_juicy_cover_image(page, page_url: str) -> list[dict]:
    images = page.eval_on_selector_all(
        "article img, .article-body img, .entry-content img, .article img, img.pict",
        """els => els.map(img => {
            const looksLikeImageUrl = value => {
                try {
                    const path = new URL(value, document.baseURI).pathname.toLowerCase();
                    return /\\.(?:jpe?g|png|webp|gif)$/.test(path);
                } catch (_) {
                    return false;
                }
            };
            const link = img.closest('a[href]');
            const linked = link?.href || '';
            const linkedImage = looksLikeImageUrl(linked) ? linked : '';
            const discovered = [
                img.dataset?.original,
                img.dataset?.src,
                img.dataset?.lazySrc,
                img.currentSrc,
                img.src
            ].find(looksLikeImageUrl) || '';
            return {
                // Prefer the anchor href, which is the full-size image in
                // livedoor's -s thumbnail markup.
                imageUrl: linkedImage || discovered,
                altText: (img.alt || '').trim(),
                titleText: (img.title || '').trim(),
                width: img.naturalWidth || Number(img.getAttribute('width')) || 0,
                height: img.naturalHeight || Number(img.getAttribute('height')) || 0
            };
        }).filter(item => item.imageUrl)""",
    )
    return normalize_first_juicy_cover_image(images, page_url)


def direct_release_from_request(request: dict) -> dict:
    release = {
        **request,
        "publisherKey": normalize_publisher(request.get("publisher")),
        "title": str(request.get("title") or "").strip(),
        "subtitle": str(request.get("subtitle") or "").strip(),
        "modelName": str(request.get("modelName") or "").strip(),
        "modelNames": juicy_model_names(
            request.get("modelNames") or [], request.get("modelName") or ""
        ),
        "models": merge_juicy_model_profiles(
            request.get("modelProfiles") or request.get("models") or []
        ),
        "modelProfiles": merge_juicy_model_profiles(
            request.get("modelProfiles") or request.get("models") or []
        ),
        "volume": request.get("volume"),
        "releaseDate": str(request.get("releaseDate") or "").strip(),
        "sourceUrl": str(request.get("sourceUrl") or "").strip(),
        "sourcePlatformKey": str(request.get("sourcePlatformKey") or source_platform_for_url(request.get("sourceUrl"))).strip(),
        "sourceConfidence": str(request.get("sourceConfidence") or "official_text").strip(),
        "checklistUrl": str(request.get("checklistUrl") or "").strip(),
        "matchTerms": list(request.get("matchTerms") or []),
    }
    release.pop("operation", None)
    return release


def normalized_composition_items(items: list[dict], release: dict) -> list[dict]:
    result = []
    parent_key = ""
    for sequence, raw in enumerate(items, start=1):
        if not isinstance(raw, dict) or raw.get("entryKind") != COMPOSITION_KIND:
            continue
        title = clean_text(raw.get("title") or raw.get("rarityLabel") or raw.get("description") or "")
        code = clean_text(raw.get("compositionKey") or raw.get("cardCode") or "")
        if not code:
            code = f"composition-{sequence}-{normalize_code(title)}"
        key = normalize_code(code) or f"composition-{sequence}"
        item = {
            "compositionKey": key,
            "parentKey": clean_text(raw.get("parentKey") or parent_key),
            "categoryKey": normalize_code(raw.get("categoryKey") or raw.get("rarityLabel") or title),
            "title": title,
            "rawText": clean_text(raw.get("rawText") or raw.get("description") or title),
            "announcedCount": raw.get("announcedCount"),
            "printRun": raw.get("printRun"),
            "isOneOfOne": bool(raw.get("isOneOfOne") or re.search(r"(?:1\s*of\s*1|one[- ]of[- ]one)", title, re.I)),
            "sequence": sequence,
            "sourceUrl": clean_text(raw.get("sourceUrl") or release.get("sourceUrl") or ""),
            "sourceConfidence": clean_text(raw.get("sourceConfidence") or release.get("sourceConfidence") or "official_text"),
        }
        result.append(item)
        if is_major_group(title, item["rawText"]):
            parent_key = key
            item["parentKey"] = ""
    return result


def normalized_individual_cards(items: list[dict], release: dict) -> list[dict]:
    result = []
    seen = set()
    for raw in items:
        if not isinstance(raw, dict) or raw.get("entryKind") == COMPOSITION_KIND:
            continue
        code = clean_text(raw.get("cardCode") or "")
        normalized = normalize_code(code)
        if not code or not normalized or normalized in seen:
            continue
        seen.add(normalized)
        item = dict(raw)
        item["entryKind"] = clean_text(item.get("entryKind") or "card")
        item["normalizedCardCode"] = normalized
        item["sourceUrl"] = clean_text(item.get("sourceUrl") or release.get("sourceUrl") or "")
        item["sourceConfidence"] = clean_text(item.get("sourceConfidence") or release.get("sourceConfidence") or "official_image")
        item.setdefault("modelNames", [])
        item.setdefault("images", [])
        result.append(item)
    return result


def normalized_evidence_images(items: Any, release: dict, default_type: str) -> list[dict]:
    result = []
    seen = set()
    for sequence, raw in enumerate(items if isinstance(items, list) else [], start=1):
        if not isinstance(raw, dict):
            continue
        original_url = clean_text(raw.get("originalUrl") or raw.get("imageUrl") or "")
        if not original_url or original_url in seen:
            continue
        seen.add(original_url)
        item = dict(raw)
        item["originalUrl"] = original_url
        item["sourceUrl"] = clean_text(item.get("sourceUrl") or release.get("sourceUrl") or "")
        item["sourcePlatformKey"] = clean_text(item.get("sourcePlatformKey") or release.get("sourcePlatformKey") or source_platform_for_url(item["sourceUrl"]))
        item["sourceConfidence"] = clean_text(item.get("sourceConfidence") or release.get("sourceConfidence") or "official_image")
        item["mediaType"] = clean_text(item.get("mediaType") or default_type)
        item["articleImageSequence"] = int(item.get("articleImageSequence") or sequence)
        result.append(item)
    return result


def normalize_combined_release(enriched: dict, do_review: bool) -> dict:
    checklist = enriched.get("checklist") if isinstance(enriched.get("checklist"), dict) else {}
    media = enriched.get("media") if isinstance(enriched.get("media"), dict) else {}
    checklist_items = checklist.get("items") if isinstance(checklist.get("items"), list) else []
    composition = normalized_composition_items(checklist_items, enriched)
    cards = normalized_individual_cards(checklist_items, enriched)
    checklist_images = normalized_evidence_images(
        checklist.get("checklistImages"), enriched, "checklist_sheet"
    )
    release_media = normalized_evidence_images(media.get("items"), enriched, "release_image")
    article_images = normalized_evidence_images(
        enriched.get("articleImages"), enriched, "unknown"
    )
    announced = int(checklist.get("announcedTotal") or enriched.get("announcedCardTotal") or 0)
    parsed = sum(
        1 for item in cards
        if not is_reference_entry_kind(item.get("entryKind"))
    )
    if parsed:
        status = "complete" if announced > 0 and parsed >= announced else "partially_parsed"
    elif checklist_images:
        status = "checklist_images_only"
    elif composition:
        status = "composition_only"
    elif cards:
        status = "reference_gallery_only"
    else:
        status = "not_started"
    if enriched.get("sourcePlatformKey") == "mint-mall" and status == "complete":
        status = "partially_parsed"

    warnings = list(enriched.get("warnings") or [])
    warnings.extend(checklist.get("warnings") or [])
    warnings.extend(media.get("warnings") or [])
    review_items = list(enriched.get("reviewItems") or [])
    if do_review:
        if not enriched.get("modelNames"):
            review_items.append({
                "reviewType": "cast_parse",
                "sourceUrl": enriched.get("sourceUrl", ""),
                "message": "No verified cast row or profile name was parsed.",
            })
        if checklist_images and parsed == 0:
            review_items.append({
                "reviewType": "checklist_image_parse",
                "sourceUrl": checklist.get("pageUrl") or enriched.get("sourceUrl", ""),
                "sourceImageUrl": checklist_images[0].get("originalUrl", ""),
                "message": "Official checklist images require manual parsing.",
            })
        if announced > 0 and parsed > 0 and parsed != announced:
            review_items.append({
                "reviewType": "card_count_mismatch",
                "sourceUrl": checklist.get("pageUrl") or enriched.get("sourceUrl", ""),
                "message": f"Parsed {parsed} of {announced} announced cards.",
                "payload": {"parsedCardTotal": parsed, "announcedCardTotal": announced},
            })

    enriched["sourcePlatformKey"] = clean_text(
        enriched.get("sourcePlatformKey") or source_platform_for_url(enriched.get("sourceUrl"))
    )
    enriched["sourceConfidence"] = clean_text(
        enriched.get("sourceConfidence") or (
            "trusted_retailer" if enriched["sourcePlatformKey"] == "mint-mall" else "official_text"
        )
    )
    enriched["composition"] = composition
    enriched["cards"] = cards
    enriched["articleImages"] = article_images
    enriched["checklistImages"] = checklist_images
    enriched["releaseMedia"] = release_media
    enriched["announcedCardTotal"] = announced
    enriched["parsedCardTotal"] = parsed
    enriched["cardDataStatus"] = status
    enriched["completenessConfidence"] = enriched["sourceConfidence"]
    enriched["warnings"] = list(dict.fromkeys(warnings))
    enriched["reviewItems"] = review_items
    enriched.setdefault("modelNames", juicy_model_names(enriched.get("modelName", "")))
    enriched.setdefault("models", [])
    return enriched

def execute_request(browser, request: dict) -> dict:
    # OCR is disabled at the worker boundary for every publisher. Do not load
    # a caller-supplied cache or honor legacy enableOcr flags.
    configure_juicy_ocr_cache([])
    operation = str(request.get("operation") or "").strip().lower()

    if operation == "discovery":
        publisher_key, releases, warnings = discover_releases(browser, request)
        return {
            "publisherKey": publisher_key,
            "releases": releases,
            "warnings": warnings,
        }

    release = direct_release_from_request(request)
    if operation == "checklist":
        max_cards = bounded_int(request.get("maxCards", request.get("maxCardsPerRelease")), 1000, 1, 2000)
        return checklist_for_release(browser, release, max_cards)
    if operation == "media":
        archive_gallery = as_bool(request.get("archiveGallery"), False)
        max_images = bounded_int(
            request.get("maxImages", request.get("maxImagesPerRelease")),
            100 if archive_gallery else 5,
            1,
            5000 if archive_gallery else 12,
        )
        return media_for_release(browser, release, max_images)
    if operation:
        raise ValueError(f"unsupported catalog worker operation: {operation}")

    # With no caller-supplied release/source, combined mode discovers the
    # current publisher roster from the official websites. The constant seed
    # is not consulted by this worker.
    has_supplied_release = bool(request.get("sourceUrl") or request.get("releases"))
    do_discovery = as_bool(
        request.get("discovery", request.get("discover")),
        not has_supplied_release,
    )
    composition_requested = request.get("compositionMedia")
    if composition_requested is None:
        composition_requested = request.get("checklist", True)
    card_media_requested = as_bool(request.get("cardMedia"), False)
    do_checklist = as_bool(composition_requested, True) or card_media_requested
    do_cards = as_bool(request.get("cards"), True)
    do_profiles = as_bool(request.get("profiles"), True)
    do_review = as_bool(request.get("review"), True)
    do_media = as_bool(
        request.get("media", request.get("releaseMedia")),
        True,
    )
    max_cards = bounded_int(
        request.get("maxCards", request.get("maxCardsPerRelease")),
        1000, 1, 5000,
    )
    max_images = bounded_int(
        request.get("maxImages", request.get("maxImagesPerRelease")),
        5, 1, 100,
    )
    max_releases = bounded_int(request.get("maxReleases"), 10000, 1, 10000)

    result = {
        "publisherKey": "",
        "options": {
            "discovery": do_discovery,
            "checklist": do_checklist,
            "compositionMedia": as_bool(composition_requested, True),
            "cardMedia": card_media_requested,
            "media": do_media,
            "profiles": do_profiles,
            "cards": do_cards,
            "review": do_review,
            "maxCards": max_cards,
            "maxImages": max_images,
            "maxReleases": max_releases,
        },
        "releases": [],
        "warnings": [],
    }

    if do_discovery:
        publisher_key, releases, warnings = discover_releases(browser, request)
        result["publisherKey"] = publisher_key
        result["warnings"].extend(warnings)
    elif isinstance(request.get("releases"), list):
        releases = [item for item in request["releases"] if isinstance(item, dict)]
        result["publisherKey"] = normalize_publisher(request.get("publisher")) or "provided"
    else:
        releases = [release]
        result["publisherKey"] = release.get("publisherKey") or "provided"

    total_releases = min(len(releases), max_releases)
    for index, item in enumerate(releases[:max_releases], start=1):
        enriched = dict(item)
        enriched["workerSequence"] = index
        progress(
            f"[catalog] release {index}/{total_releases} "
            f"publisher={enriched.get('publisherKey', '')} "
            f"title={enriched.get('title', '')!r}"
        )

        if do_checklist or do_cards:
            try:
                enriched["cardMedia"] = card_media_requested
                enriched["checklist"] = checklist_for_release(browser, enriched, max_cards)
            except Exception as exc:
                enriched["checklist"] = {
                    "items": [],
                    "checklistImages": [],
                    "announcedTotal": 0,
                    "warnings": [f"checklist extraction failed: {exc}"],
                }

        if do_media:
            try:
                enriched["media"] = media_for_release(browser, enriched, max_images)
            except Exception as exc:
                enriched["media"] = {
                    "items": [],
                    "warnings": [f"media extraction failed: {exc}"],
                }

        result["releases"].append(normalize_combined_release(enriched, do_review))

    return result


def main() -> None:
    request = json.load(sys.stdin)
    filtered_stderr = FilteredStderr(sys.stderr)
    with redirect_stdout(filtered_stderr):
        try:
            with browser_launch_lock():
                browser = launch(headless=True, timeout=browser_launch_timeout_ms())
        except Exception as exc:
            raise RuntimeError(f"CloakBrowser launch failed: {exc}") from exc

        try:
            result = execute_request(browser, request)
        finally:
            close_quietly(browser)

    filtered_stderr.flush()
    json.dump(result, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
