"""CloakBrowser worker for public trading-card marketplace pages.

The worker reads one JSON request from stdin and writes one normalized JSON
batch to stdout. It intentionally does not try to defeat CAPTCHA challenges or
log in to restricted accounts. Only publicly rendered pages are inspected.
"""

from __future__ import annotations

import hashlib
import html
import json
import os
import re
import sys
import time
import unicodedata
from contextlib import contextmanager, redirect_stdout
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, quote, unquote, urlparse

from cloakbrowser import launch


DEFAULT_BROWSER_LAUNCH_TIMEOUT_MS = 90_000


def browser_launch_timeout_ms() -> int:
    """Return a bounded Playwright startup timeout for the worker browser."""
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


# Keep the worker's JSON/progress streams UTF-8 on Windows as well as Linux;
# marketplace titles frequently contain Japanese text and Unicode symbols.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stdin, "reconfigure"):
    # Go sends JSON as UTF-8, but Windows may attach a locale-encoded text
    # wrapper to a redirected stdin. Without an explicit encoding, Japanese
    # model names become mojibake or surrogate characters before the search
    # URL is built.
    sys.stdin.reconfigure(encoding="utf-8", errors="replace")


SUPPORTED_PLATFORM_ALIASES = {
    "yahoo-auctions-jp": "yahoo-auctions-jp",
    "yahoo": "yahoo-auctions-jp",
    "yahoo-japan": "yahoo-auctions-jp",
    "yahoo-auctions": "yahoo-auctions-jp",
    # Kept temporarily so existing clients can migrate without duplicating
    # records. It is never persisted as the marketplace identity.
    "jdirectmarket": "yahoo-auctions-jp",
    "aucfan": "aucfan",
    "mercari-jp": "mercari-jp",
    "mercari": "mercari-jp",
    "mercari-japan": "mercari-jp",
    "rakuma": "rakuma",
    "rakuma-jp": "rakuma",
    "rakuma-japan": "rakuma",
    "yahoo-furima-jp": "yahoo-furima-jp",
    "yahoo-furima": "yahoo-furima-jp",
    "yahoo-flea": "yahoo-furima-jp",
    "jdirectitems-flea": "yahoo-furima-jp",
    "surugaya": "surugaya",
    "mandarake": "mandarake",
    "mandarake-auction": "mandarake",
    "ebay": "ebay",
    "ebay-japan": "ebay",
    "ebay-global": "ebay",
    "tcgplayer": "tcgplayer",
    # Taiwan regional worker surfaces.
    "ruten-tw": "ruten-tw",
    "ruten": "ruten-tw",
    "shopee-tw": "shopee-tw",
    "shopee-taiwan": "shopee-tw",
    # South Korea regional worker surfaces.
    "bunjang-kr": "bunjang-kr",
    "bunjang": "bunjang-kr",
    "naver-shopping-kr": "naver-shopping-kr",
    "naver-shopping": "naver-shopping-kr",
    "karrot-kr": "karrot-kr",
    "karrot": "karrot-kr",
    "daangn": "karrot-kr",
    # Doorzo retrieval surfaces. The persisted marketplace is derived from
    # the source card/detail, never from the Doorzo proxy hostname.
    "doorzo-mercari": "doorzo-mercari",
    "doorzo-rakuma": "doorzo-rakuma",
    "doorzo-yahoo": "doorzo-yahoo",
    "doorzo-jdirectitems": "doorzo-yahoo",
    "doorzo-jdirectitems-auction": "doorzo-yahoo",
    "doorzo-paypay": "doorzo-paypay",
    "doorzo-jdirectitems-flea": "doorzo-paypay",
    "doorzo-surugaya": "doorzo-surugaya",
    "doorzo-rakuten": "doorzo-rakuten",
    "doorzo-amazon": "doorzo-amazon",
    "doorzo-lashinbang": "doorzo-lashinbang",
}

# Active searches are intentionally broad by series, so marketplace results
# must still prove that they are trading-card inventory.  Without this gate a
# Mercari/Rakuma series search also returns figures, cosmetics, toys, and
# other products that merely reuse a series' Japanese wording.
ACTIVE_CARD_SIGNAL_RE = re.compile(
    r"(?:\b(?:trading|collectible|collection|official)\s*cards?\b|\bcard\s*(?:set|series|collection)?\b|\btcgs?\b|"
    r"トレカ|トレーディング\s*カード|コレクションカード|オフィシャルカード|生写真カード|チェキカード|カード|チェキ|"
    r"交易卡|收藏卡|集換式卡牌|卡牌|卡片|球員卡|女孩卡|"
    r"트레이딩\s*카드|컬렉션\s*카드|포토카드|포카|카드)",
    re.I,
)
ACTIVE_NON_CARD_RE = re.compile(
	r"(?:フィギュア|ミニチュア|ジオラマ|ぬいぐるみ|アクリル(?:スタンド|キーホルダー)|ドール|模型|プラモデル|"
	r"\b(?:figure|figurine|doll|statue|toy|plush|diorama|model\s*kit)\b|"
	r"化粧品|コスメ|美容|スキンケア|ローション|クリーム|リップ|ティント|ファンデーション|香水|"
	r"\b(?:cosmetics?|beauty|skincare|lip(?:stick|\s*tint)?|foundation|perfume)\b|"
	r"(?<![a-z])(?:cd|dvd|blu-ray)(?![a-z])|ＣＤ|ＤＶＤ|ブルーレイ|"
	r"カード(?:ファイル|ケース|スリーブ|バインダー|収納)|"
	r"コスプレ|cosplay|ボーカロイド|vocaloid|初音ミク|写真集|ポスター|カレンダー|"
	r"抱き枕|タペストリー|"
	r"公仔|玩偶|娃娃|海報|寫真集|日曆|應援棒|周邊|服飾|衣服|抱枕|立牌|壓克力(?:立牌|吊飾)?|"
	r"포토북|앨범|응원봉|아크릴(?:스탠드|키링)?|인형|피규어|굿즈|잡지|달력|포스터|의류|후드티|티셔츠|"
	r"\b(?:swimwear|lingerie|underwear|leotard)\b)",
    re.I,
)
ACTIVE_APPAREL_RE = re.compile(
    r"水着|スクール水着|swimsuit|レオタード|下着|ランジェリー|ブラジャー|ブラトップ|"
    r"ショーツ|パンツ|ハイレグ|キャミソール|セーラー服|制服|ドレス|衣装|\bdress\b",
    re.I,
)
ACTIVE_COLLECTIBLE_RE = re.compile(
	r"トレカ|トレーディング\s*カード|\b(?:official|collection|trading)\s+cards?\b|\bcard\b|カード|"
	r"交易卡|收藏卡|集換式卡牌|卡牌|卡片|球員卡|女孩卡|"
	r"트레이딩\s*카드|컬렉션\s*카드|포토카드|포카|카드|チェキ|色紙|台紙|\b1of1\b|直筆サイン",
	re.I,
)
HITS_SERIES_RE = re.compile(r"\bhit['’]?s(?:\s*limited)?\b|ヒッツ", re.I)
# Bare ``HITS`` is also a common keyword in unrelated marketplace titles.
# Require either the seller's explicit HITS spelling or a card phrase that
# carries enough product provenance to disambiguate it from ``HITS Card 2026``
# style false positives returned by broad eBay/Yahoo searches.
HITS_EXPLICIT_BRAND_RE = re.compile(r"(?:\bhit['’]s(?:\s*limited)?\b|\bhits\s+limited\b|ヒッツ)", re.I)
HITS_SPECIFIC_CARD_CONTEXT_RE = re.compile(
    r"(?:\b(?:official\s+photo|official|photo|trading|collectible)\s*cards?\b|"
    r"トレカ|トレーディング\s*カード|オフィシャルカード|"
    r"(?:直筆)?サインカード|生写真カード|チェキカード|生キス(?:カード)?|特典カード)",
    re.I,
)
# "Best Hits"/"Greatest Hits" is a music descriptor, not the HITS card
# brand. Music listings can also contain incidental card wording such as
# 歌詞カード (lyrics card), so reject these title signals before checking for
# generic photo/trading-card context.
HITS_NON_CARD_TITLE_RE = re.compile(
    r"(?:\b(?:best|greatest|biggest|all[- ]time)\s+hits\b|"
    r"\bhits?\s+(?:volume|vol\.?)\b|"
    r"(?:グレイテスト|ベスト)[・･\s-]*(?:ヒッツ|hits?)|"
    r"\blyrics?\s+cards?\b|\blyric\s+sheet\b|歌詞\s*カード|歌詞付|ライナーノーツ|"
    r"\b(?:album|single|cd|dvd|blu[- ]?ray|soundtrack|music)\b|"
    r"\b(?:exile(?:\s+tribe)?|ldh)\b|\b(?:live[- ]?expo|concert|tour)\b)",
    re.I,
)
HITS_CARD_CONTEXT_RE = re.compile(
    r"(?:\b(?:trading|collectible|official|photo)\s*cards?\b|"
    r"\bcard(?:\s*(?:set|series|collection|no\.?|#|\d+))?\b|"
    r"トレカ|トレーディング\s*カード|オフィシャルカード|カード(?:セット|シリーズ|コレクション)?|"
    r"(?:直筆)?サインカード|生写真カード|チェキカード)",
    re.I,
)
HITS_NON_CARD_RE = re.compile(
    r"(?:\b(?:cd|dvd|blu[-\s]?ray|album|single|music|photo\s*book|poster|calendar|"
    r"figure|figurine|acrylic|plush)\b|"
    r"写真集|ポスター|カレンダー|フィギュア|アクスタ|アクリルスタンド|ぬいぐるみ|"
    r"抱き枕|タペストリー|カードケース|カードスリーブ|カードファイル|カードホルダー|"
    r"カードバインダー|バインダー|カード収納|カードゲーム)",
    re.I,
)
HITS_CARD_ACCESSORY_RE = re.compile(r"カード(?:ケース|スリーブ|ファイル|ホルダー|バインダー|収納|ゲーム)|バインダー", re.I)
HITS_FOREIGN_CARD_RE = re.compile(
    r"(?:\b(?:sports?|baseball|soccer|football|basketball|nba|nfl|mlb|wwe|"
    r"topps|panini|upper\s*deck|bowman|fleer|donruss|prizm|pokemon|"
    r"yu[-\s]?gi[-\s]?oh|mtg|one\s*piece|athlete|jockey|horse\s+racing|racing|trading\s+card\s+game|"
    r"collectible\s+card\s+game)\b|"
    r"野球|サッカー|フットボール|バスケットボール|アスリート|騎手|競馬|競輪|"
    r"ボートレース|オートレース|ゴルフ|テニス|ラグビー|相撲|ポケモン|ポケカ|遊戯王|"
    r"デュエルマスターズ|ヴァイスシュヴァルツ|ワンピースカード)",
    re.I,
)


class SearchPageRenderError(RuntimeError):
    """The browser navigated but did not expose a usable DOM document."""


def log_progress(platform: str, message: str) -> None:
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    print(f"[{timestamp}] [{platform}] {message}", file=sys.stderr, flush=True)


def resolve_pagination(request: dict) -> tuple[int, int, range | list[int]]:
    """Return page size, progress limit, and the page numbers to visit."""
    page_size = max(1, min(int(request.get("pageSize") or 50), 100))
    requested_page = max(0, int(request.get("pageNumber") or 0))
    if requested_page > 0:
        # The backend uses one worker invocation per page so it can persist
        # and notify each page before asking the browser for the next one.
        return page_size, 1, [requested_page]
    if bool(request.get("untilEnd")):
        # Keep an emergency ceiling in case a marketplace ignores pagination
        # parameters or never exposes an empty page.
        max_pages = max(1, min(int(request.get("maxPages") or 1000), 1000))
        return page_size, max_pages, range(1, max_pages + 1)

    max_pages = max(1, min(int(request.get("maxPages") or 1), 10))
    return page_size, max_pages, range(1, max_pages + 1)


MIXED_LISTING_PLATFORMS = {"mercari-jp", "rakuma", "yahoo-furima-jp"}


def merge_mixed_diagnostics(
    target: dict[str, int],
    active: dict[str, int],
    sold: dict[str, int],
    rendered_count: int | None = None,
) -> None:
    """Merge two classification passes without counting each card twice."""
    if rendered_count is None:
        rendered_count = max(
            active.get("renderedCandidates", 0), sold.get("renderedCandidates", 0)
        )
    target["renderedCandidates"] = target.get("renderedCandidates", 0) + rendered_count
    for key, value in active.items():
        if key in {"renderedCandidates", "soldCandidates", "accepted"}:
            continue
        target[key] = target.get(key, 0) + value
    for key, value in sold.items():
        # A mixed page is expected to contain active cards, so a missing sold
        # badge is a classification result rather than a rejected listing.
        if key in {"renderedCandidates", "missingSoldEvidence", "accepted"}:
            continue
        target[key] = target.get(key, 0) + value


def collect_marketplace_mixed_items(
    page,
    platform: str,
    page_size: int,
    query: str = "",
    from_bound: datetime | None = None,
    to_bound: datetime | None = None,
    diagnostics: dict[str, int] | None = None,
    model_aliases: list[str] | None = None,
    active_page_url: str = "",
    sold_page_url: str = "",
) -> tuple[list[dict], list[str]]:
    """Load and classify active/sold surfaces inside one browser worker."""
    if platform not in MIXED_LISTING_PLATFORMS:
        raise ValueError(f"mixed scrape mode is not supported for {platform}")
    active_diagnostics: dict[str, int] = {}
    sold_diagnostics: dict[str, int] = {}
    if active_page_url:
        load_search_page(page, active_page_url, platform, mode="active")
    active_urls = collect_result_urls(page, platform)
    active_items = collect_marketplace_active_items(
        page,
        platform,
        page_size,
        query=query,
        from_bound=from_bound,
        to_bound=to_bound,
        model_aliases=model_aliases,
        diagnostics=active_diagnostics,
    )
    # Yahoo Flea active title cleanup can visit a detail page. Restore the
    # result page before the sold classifier reads the same rendered cards.
    # The sold surface is supplemental for an active scan: if it times out or
    # loses its browser context, keep the active rows already classified
    # instead of discarding the whole mixed page.
    sold_urls = []
    sold_items = []
    try:
        if sold_page_url and (
            sold_page_url != active_page_url
            or active_diagnostics.get("detailNavigations", 0) > 0
        ):
            load_search_page(page, sold_page_url, platform, mode="sold")
        sold_urls = collect_result_urls(page, platform)
        sold_items = collect_marketplace_completed_items(
            page,
            platform,
            page_size,
            query=query,
            from_bound=from_bound,
            to_bound=to_bound,
            diagnostics=sold_diagnostics,
            model_aliases=model_aliases,
        )
    except Exception as exc:
        diagnostics["soldSurfaceErrors"] = diagnostics.get("soldSurfaceErrors", 0) + 1
        log_progress(
            platform,
            f"query={query} sold surface unavailable; keeping active results: {exc}",
        )
    rendered_urls = list(dict.fromkeys(active_urls + sold_urls))
    if diagnostics is not None:
        merge_mixed_diagnostics(
            diagnostics,
            active_diagnostics,
            sold_diagnostics,
            rendered_count=len(rendered_urls),
        )
    return active_items + sold_items, rendered_urls


def stream_active_query_pages(
    search_page,
    request: dict,
    platform: str,
    query_spec: dict,
    mode: str,
    page_size: int,
    max_pages: int,
    emit,
) -> None:
    """Stream one query; the caller can replace the page after a failure."""
    query = query_spec["query"]
    remote_query = marketplace_search_query(platform, query)
    search_url = build_search_url(platform, query, page_size, mode=mode)
    active_search_url = build_search_url(platform, query, page_size, mode="active")
    sold_search_url = build_search_url(platform, query, page_size, mode="sold")
    from_bound = parse_request_bound(request.get("from"), "from")
    to_bound = parse_request_bound(request.get("to"), "to")
    log_progress(
        platform,
        f'stream query="{remote_query}" match_query="{query}" '
        f"page_limit={max_pages} page_size={page_size}",
    )
    seen_fingerprints = set()
    page_numbers = range(1, max_pages + 1) if request.get("untilEnd") else [1]
    page_number = 0
    try:
        for page_number in page_numbers:
            log_progress(platform, f"query={query} page {page_number}/{max_pages} loading")
            page_url = with_marketplace_page(platform, search_url, page_number, page_size)
            active_page_url = with_marketplace_page(
                platform, active_search_url, page_number, page_size
            )
            sold_page_url = with_marketplace_page(
                platform, sold_search_url, page_number, page_size
            )
            navigation_started = time.monotonic()
            if mode != "mixed":
                load_search_page(search_page, page_url, platform, mode=mode)
            navigation_ms = int((time.monotonic() - navigation_started) * 1000)
            if is_doorzo_platform(platform):
                expand_doorzo_result_window(search_page, page_number, page_size)

            diagnostics = {}
            rendered_urls = (
                [] if mode == "mixed" else collect_result_urls(search_page, platform)
            )
            collection_started = time.monotonic()
            if mode == "mixed":
                completed_items, rendered_urls = collect_marketplace_mixed_items(
                    search_page,
                    platform,
                    page_size,
                    query=query,
                    from_bound=from_bound,
                    to_bound=to_bound,
                    model_aliases=query_spec["modelAliases"],
                    diagnostics=diagnostics,
                    active_page_url=active_page_url,
                    sold_page_url=sold_page_url,
                )
            elif is_doorzo_platform(platform):
                completed_items = collect_doorzo_active_items(
                    search_page,
                    platform,
                    page_size,
                    query=query,
                    from_bound=from_bound,
                    to_bound=to_bound,
                    model_aliases=query_spec["modelAliases"],
                    diagnostics=diagnostics,
                    page_number=page_number,
                )
            else:
                completed_items = collect_marketplace_active_items(
                    search_page,
                    platform,
                    page_size,
                    query=query,
                    from_bound=from_bound,
                    to_bound=to_bound,
                    model_aliases=query_spec["modelAliases"],
                    diagnostics=diagnostics,
                )
            diagnostics["searchNavigationMs"] = navigation_ms
            diagnostics["resultRenderingMs"] = int(
                (time.monotonic() - collection_started) * 1000
            )
            diagnostics["accepted"] = len(completed_items)
            page_empty = len(rendered_urls) == 0
            page_fingerprint = (
                hashlib.sha256(
                    json.dumps(rendered_urls, ensure_ascii=False).encode("utf-8")
                ).hexdigest()
                if rendered_urls
                else ""
            )
            if page_fingerprint and page_fingerprint in seen_fingerprints:
                log_progress(
                    platform,
                    f"query={query} repeated page fingerprint at page {page_number}; stopping",
                )
                emit({
                    "type": "stop",
                    "query": query_spec,
                    "pageNumber": page_number,
                    "stopReason": "repeated_page_fingerprint",
                })
                break
            if page_fingerprint:
                seen_fingerprints.add(page_fingerprint)

            content_hash = hashlib.sha256(
                json.dumps(completed_items, sort_keys=True, ensure_ascii=False).encode("utf-8")
            ).hexdigest()
            batch = {
                "platform": platform,
                "sourceUrl": search_url,
                "contentHash": content_hash,
                "pageEmpty": page_empty,
                "pageFingerprint": page_fingerprint,
                "items": completed_items,
                "warnings": [],
                "diagnostics": diagnostics,
            }
            emit({
                "type": "page",
                "query": query_spec,
                "pageNumber": page_number,
                "batch": batch,
            })
            log_progress(
                platform,
                f"query={query} page={page_number} candidates={len(rendered_urls)} "
                f"accepted={len(completed_items)} navigation_ms={navigation_ms} "
                f"rendering_ms={diagnostics['resultRenderingMs']} "
                f"cycle_ms={int((time.monotonic() - navigation_started) * 1000)}",
            )
            if page_empty:
                log_progress(platform, f"query={query} has no result cards; stopping")
                break
        else:
            if request.get("untilEnd"):
                log_progress(
                    platform,
                    f"query={query} reached configured page limit {max_pages}",
                )
                emit({
                    "type": "stop",
                    "query": query_spec,
                    "pageNumber": max_pages,
                    "stopReason": "max_pages",
                })
    except Exception as exc:
        raise RuntimeError(f"query={query} page={page_number}: {exc}") from exc


def stream_active_pages(request: dict, platform: str) -> None:
    """Run all active or mixed queries in one browser and stream each page."""
    query_specs = request.get("queries") or [{
        "productLineSlug": request.get("productLineSlug", ""),
        "modelName": request.get("modelName", ""),
        "modelAliases": request.get("modelAliases") or [],
        "query": request.get("query", ""),
    }]
    query_specs = [
        {
            "productLineSlug": str(value.get("productLineSlug") or ""),
            "modelName": str(value.get("modelName") or ""),
            "modelAliases": [str(alias).strip() for alias in (value.get("modelAliases") or []) if str(alias).strip()],
            "query": str(value.get("query") or "").strip(),
        }
        for value in query_specs
        if isinstance(value, dict) and str(value.get("query") or "").strip()
    ]
    if not query_specs:
        raise ValueError("at least one marketplace query is required")
    mode = str(request.get("mode") or "active").strip().lower()
    if mode not in {"active", "mixed"}:
        raise ValueError("streamPages is supported only for active or mixed mode")
    if mode == "mixed" and platform not in MIXED_LISTING_PLATFORMS:
        raise ValueError(f"mixed scrape mode is not supported for {platform}")
    page_size, max_pages, _ = resolve_pagination(request)
    json_stdout = sys.stdout

    def emit(event: dict) -> None:
        print(json.dumps(event, ensure_ascii=False), file=json_stdout, flush=True)

    with redirect_stdout(sys.stderr):
        browser_started = time.monotonic()
        with browser_launch_lock():
            browser = launch(headless=True, timeout=browser_launch_timeout_ms())
        log_progress(platform, f"browser startup_ms={int((time.monotonic() - browser_started) * 1000)}")
        try:
            search_page = browser.new_page()
            for query_spec in query_specs:
                try:
                    stream_active_query_pages(
                        search_page, request, platform, query_spec, mode,
                        page_size, max_pages, emit,
                    )
                except Exception as exc:
                    query = query_spec["query"]
                    log_progress(
                        platform,
                        f"query={query} failed; continuing with next query: {exc}",
                    )
                    emit({
                        "type": "stop",
                        "query": query_spec,
                        "stopReason": "query_error",
                    })
                    close_page = getattr(search_page, "close", None)
                    if close_page is not None:
                        try:
                            close_page()
                        except Exception:
                            pass
                    search_page = browser.new_page()
        finally:
            browser.close()


def main() -> None:
    request = json.load(sys.stdin)
    requested_platform = request.get("platform", "").lower().strip()
    platform = SUPPORTED_PLATFORM_ALIASES.get(requested_platform, "")
    if not platform:
        raise ValueError(
            "unsupported browser platform: "
            f"{requested_platform}; supported platforms: "
            + ", ".join(sorted(set(SUPPORTED_PLATFORM_ALIASES.values())))
        )
    query = request.get("query", "").strip()
    if not query and not request.get("queries"):
        raise ValueError("query is required")
    model_aliases = [
        str(value).strip()
        for value in (request.get("modelAliases") or [])
        if str(value).strip()
    ]
    mode = str(request.get("mode") or "sold").strip().lower()
    if mode not in {"sold", "active", "mixed", "active_check"}:
        raise ValueError(f"unsupported scrape mode: {mode}")
    if mode == "mixed" and platform not in MIXED_LISTING_PLATFORMS:
        raise ValueError(f"mixed scrape mode is not supported for {platform}")
    from_bound = parse_request_bound(request.get("from"), "from")
    to_bound = parse_request_bound(request.get("to"), "to")
    if from_bound and to_bound and from_bound > to_bound:
        raise ValueError("from must be earlier than or equal to to")
    if bool(request.get("streamPages")):
        if mode not in {"active", "mixed"}:
            raise ValueError("streamPages is supported only for active or mixed mode")
        stream_active_pages(request, platform)
        return

    page_size, max_pages, page_numbers = resolve_pagination(request)
    remote_query = marketplace_search_query(platform, query)
    search_url = request.get("searchUrl") or build_search_url(platform, query, page_size, mode=mode)
    if mode == "active_check" and not request.get("searchUrl"):
        raise ValueError("searchUrl is required for active_check mode")
    log_progress(
        platform,
        f'mode={mode} query="{remote_query}" match_query="{query}" '
        f'page_limit={max_pages} page_size={page_size}',
    )

    # Keep stdout machine-readable. CloakBrowser/browser dependencies may
    # print startup diagnostics; redirect those diagnostics to stderr so the
    # Go adapter receives exactly one JSON document on stdout.
    with redirect_stdout(sys.stderr):
        with browser_launch_lock():
            browser = launch(headless=True, timeout=browser_launch_timeout_ms())
        try:
            search_page = browser.new_page()
            items = []
            seen = set()
            candidate_count = 0
            sold_candidate_count = 0
            processed_count = 0
            rejection_counts: dict[str, int] = {}
            diagnostics: dict[str, int] = {}
            page_empty = False
            page_fingerprint = ""

            # Lifecycle reconciliation opens one stored detail URL at a time.
            # Keep this path separate from search pagination so it cannot
            # accidentally import a row or emit an active-listing alert.
            if mode == "active_check":
                checked_items = collect_active_listing_check(
                    search_page, platform, search_url, query
                )
                if checked_items:
                    items.extend(checked_items)
                    processed_count = len(checked_items)
                    diagnostics["renderedCandidates"] = 1
                    diagnostics["accepted"] = len(checked_items)
                page_empty = not checked_items
                page_numbers = []

            for page_number in page_numbers:
                log_progress(platform, f"page {page_number}/{max_pages} loading")
                page_url = with_marketplace_page(platform, search_url, page_number, page_size)
                if mode != "mixed":
                    load_search_page(search_page, page_url, platform, mode=mode)
                if is_doorzo_platform(platform):
                    expand_doorzo_result_window(
                        search_page, page_number, page_size
                    )
                rendered_urls = (
                    []
                    if mode == "mixed"
                    else collect_result_urls(search_page, platform)
                )
                if mode == "mixed":
                    active_page_url = with_marketplace_page(
                        platform,
                        build_search_url(platform, query, page_size, mode="active"),
                        page_number,
                        page_size,
                    )
                    sold_page_url = with_marketplace_page(
                        platform,
                        build_search_url(platform, query, page_size, mode="sold"),
                        page_number,
                        page_size,
                    )
                    completed_items, rendered_urls = collect_marketplace_mixed_items(
                        search_page,
                        platform,
                        page_size,
                        query=query,
                        from_bound=from_bound,
                        to_bound=to_bound,
                        model_aliases=model_aliases,
                        diagnostics=diagnostics,
                        active_page_url=active_page_url,
                        sold_page_url=sold_page_url,
                    )
                elif mode == "active" and is_doorzo_platform(platform):
                    completed_items = collect_doorzo_active_items(
                        search_page,
                        platform,
                        page_size,
                        query=query,
                        from_bound=from_bound,
                        to_bound=to_bound,
                        model_aliases=model_aliases,
                        diagnostics=diagnostics,
                        page_number=page_number,
                    )
                elif mode == "active":
                    completed_items = collect_marketplace_active_items(
                        search_page,
                        platform,
                        page_size,
                        query=query,
                        from_bound=from_bound,
                        to_bound=to_bound,
                        model_aliases=model_aliases,
                        diagnostics=diagnostics,
                    )
                elif is_doorzo_platform(platform):
                    rendered_urls = doorzo_page_slice(
                        rendered_urls, page_number, page_size
                    )
                page_empty = len(rendered_urls) == 0
                page_fingerprint = hashlib.sha256(
                    json.dumps(rendered_urls, ensure_ascii=False).encode("utf-8")
                ).hexdigest() if rendered_urls else ""
                if page_empty:
                    log_progress(
                        platform,
                        f"page {page_number}/{max_pages} has no result cards; stopping",
                    )
                    break
                if mode == "sold":
                    if is_doorzo_platform(platform):
                        completed_items = collect_doorzo_completed_items(
                            search_page,
                            platform,
                            page_size,
                            query=query,
                            from_bound=from_bound,
                            to_bound=to_bound,
                            diagnostics=diagnostics,
                            page_number=page_number,
                        )
                    elif platform == "yahoo-auctions-jp":
                        completed_items = collect_yahoo_completed_items(
                            search_page,
                            page_size,
                            query=query,
                            from_bound=from_bound,
                            to_bound=to_bound,
                            diagnostics=diagnostics,
                        )
                    elif platform == "yahoo-furima-jp":
                        completed_items = collect_yahoo_furima_completed_items(
                            search_page,
                            page_size,
                            query=query,
                            from_bound=from_bound,
                            to_bound=to_bound,
                            diagnostics=diagnostics,
                        )
                    else:
                        completed_items = collect_marketplace_completed_items(
                            search_page,
                            platform,
                            page_size,
                            query=query,
                            from_bound=from_bound,
                            to_bound=to_bound,
                            diagnostics=diagnostics,
                            model_aliases=model_aliases,
                        )
                candidate_count = diagnostics.get("renderedCandidates", 0)
                sold_candidate_count = diagnostics.get("soldCandidates", 0)
                new_items = [
                    item
                    for item in completed_items
                    if item["originalUrl"] not in seen
                ]
                if not new_items:
                    log_progress(
                        platform,
                        f"page {page_number}/{max_pages} has no new items; continuing",
                    )
                    # A non-empty page can contain only active, retail, or
                    # otherwise unqualified cards. Keep paginating until the
                    # marketplace returns no cards; the backend fingerprint
                    # guard stops a source that repeats the same page.
                    continue
                for item in new_items:
                    seen.add(item["originalUrl"])
                    processed_count += 1
                    items.append(item)
                    log_progress(
                        platform,
                        f"listing {processed_count}/{candidate_count} accepted "
                        f"accepted_total={len(items)}",
                    )
            candidate_count = diagnostics.get("renderedCandidates", 0)
            sold_candidate_count = diagnostics.get("soldCandidates", 0)
            rejection_counts = {
                key: value
                for key, value in diagnostics.items()
                if key not in {"renderedCandidates", "soldCandidates", "accepted"}
                and value > 0
            }
            diagnostics["accepted"] = len(items)
            content_hash = hashlib.sha256(
                json.dumps(items, sort_keys=True, ensure_ascii=False).encode("utf-8")
            ).hexdigest()
        finally:
            browser.close()

    warnings = build_diagnostic_warnings(
        platform,
        candidate_count,
        sold_candidate_count,
        rejection_counts,
    )
    log_progress(
        platform,
        f"finished processed={processed_count}/{candidate_count} "
        f"sold_candidates={sold_candidate_count} accepted={len(items)}",
    )

    print(json.dumps({
        "platform": platform,
        "sourceUrl": search_url,
        "contentHash": content_hash,
        "pageEmpty": page_empty,
        "pageFingerprint": page_fingerprint,
        "items": items,
        "warnings": warnings,
        "diagnostics": diagnostics,
    }, ensure_ascii=False))


def build_search_url(platform: str, query: str, page_size: int, mode: str = "sold") -> str:
    search_query = marketplace_search_query(platform, query)
    encoded_query = quote(search_query, safe="")
    normalized_mode = str(mode or "sold").lower()
    active_mode = normalized_mode == "active"
    if is_doorzo_platform(platform):
        website = doorzo_website_for_platform(platform)
        # Doorzo treats any isStock query-string value (including the literal
        # string "false") as truthy and checks its In Stock filter. The browser
        # must turn that rendered control off after hydration; no URL value can
        # reliably represent the unchecked state across a fresh navigation.
        return (
            "https://www.doorzo.com/en/search?"
            f"keywords={encoded_query}&website={quote(website, safe='')}"
        )
    if platform in {"yahoo-auctions-jp", "jdirectmarket"} and active_mode:
        return f"https://auctions.yahoo.co.jp/search/search?p={encoded_query}"
    if platform in {"yahoo-auctions-jp", "jdirectmarket"}:
        # Yahoo Auctions' closed-search surface contains completed auction
        # records. Do not fall back to an active-search URL.
        return (
            "https://auctions.yahoo.co.jp/closedsearch/closedsearch/"
            f"{encoded_query}/0/"
        )
    if platform == "aucfan" and active_mode:
        return f"https://aucfan.com/search1/q-{encoded_query}/"
    if platform == "aucfan":
        # Select Yahoo! Auctions sold history explicitly. The unsuffixed MIX
        # page also contains shopping/active results and is not safe input for
        # a completed-sale importer.
        return f"https://aucfan.com/search1/q-{encoded_query}/s-ya/"
    if platform == "mercari-jp":
        # Mercari currently uses on_sale for purchasable inventory. The older
        # trading value represents items already in a transaction and renders
        # sold/unavailable cards, so it must not drive active ingestion.
        if active_mode:
            status_value = "on_sale"
        elif normalized_mode == "mixed":
            status_value = "sold_out|on_sale"
        else:
            status_value = "sold_out"
        status = quote(status_value, safe="")
        category = "&category_id=7325" if search_query.casefold() == "juicy honey" else ""
        return (
            f"https://jp.mercari.com/search?keyword={encoded_query}"
            f"&status={status}{category}"
        )
    if platform == "rakuma":
        return f"https://fril.jp/s?query={encoded_query}"
    if platform == "yahoo-furima-jp":
        # Yahoo! Flea search mixes active and sold cards. The collector below
        # verifies each card/detail page's sold marker and purchase timestamp.
        return f"https://paypayfleamarket.yahoo.co.jp/search/{encoded_query}"
    if platform == "surugaya":
        return f"https://www.suruga-ya.jp/search?keyword={encoded_query}"
    if platform == "mandarake":
        return f"https://order.mandarake.co.jp/order/listPage/list?keyword={encoded_query}&lang=en"
    if platform == "ebay" and active_mode:
        return f"https://www.ebay.com/sch/i.html?_nkw={encoded_query}"
    if platform == "ebay":
        return (
            "https://www.ebay.com/sch/i.html?"
            f"_nkw={encoded_query}&LH_Complete=1&LH_Sold=1"
        )
    if platform == "tcgplayer":
        return f"https://www.tcgplayer.com/search/all/product?q={encoded_query}"
    if platform == "ruten-tw":
        return f"https://www.ruten.com.tw/find/?q={encoded_query}"
    if platform == "shopee-tw":
        return f"https://shopee.tw/search?keyword={encoded_query}"
    if platform == "bunjang-kr":
        return f"https://m.bunjang.co.kr/search/products?q={encoded_query}"
    if platform == "naver-shopping-kr":
        return f"https://search.shopping.naver.com/search/all?query={encoded_query}"
    if platform == "karrot-kr":
        return f"https://www.daangn.com/search/{quote(query, safe='')}"
    else:
        raise ValueError(f"unsupported marketplace platform: {platform}")


def taiwan_marketplace_search_query(query: str) -> str:
    """Use the Chinese release wording indexed by Taiwan marketplaces.

    The registry keeps an English query for cross-market identity and eBay,
    while Ruten/Shopee generally index the Chinese product title. Only the
    Rakuten Girls family is translated here so unrelated Taiwan series keep
    their existing search wording.
    """
    value = str(query or "")
    if not re.search(r"rakuten\s+girls|樂天女孩|\brkg\b", value, re.I):
        return value
    value = re.sub(
        r"\brakuten\s+girls(?:\s+(?:trading|collectible|collection|official))?\s+cards?\b",
        "樂天女孩卡",
        value,
        flags=re.I,
    )
    value = re.sub(r"\brakuten\s+girls\b", "樂天女孩", value, flags=re.I)
    value = re.sub(r"\brakuten\b", "樂天", value, flags=re.I)
    value = re.sub(
        r"\b(?:trading|collectible|collection|official)\s+cards?\b",
        "卡",
        value,
        flags=re.I,
    )
    return re.sub(r"\s+", " ", value).strip()


def marketplace_search_query(platform: str, query: str) -> str:
    """Translate the internal match query into the marketplace's search syntax.

    Quotes remain in the internal query so title matching knows which release
    and person phrases are important. Mercari and the Japanese retail/search
    sites treat those quote characters literally, however, which produced an
    empty result page for otherwise valid searches. Generic category hints are
    also removed from the remote query because they unnecessarily hide items
    whose title omits the category name.
    """
    value = query or ""
    if platform in {"ruten-tw", "shopee-tw"}:
        value = taiwan_marketplace_search_query(value)
    if platform == "mercari-jp":
        # The direct Mercari search is intentionally started with the enabled
        # stable public series spellings. Release/person constraints remain in
        # the internal card_set job for attribution, but sending every quoted
        # term to Mercari makes its AND search unnecessarily sparse.
        value = mercari_default_series_query(value)
    elif is_doorzo_platform(platform):
        website = doorzo_website_for_platform(platform)
        if website in {"surugaya", "rakuten"}:
            # Retail indexes commonly omit the English category hint. Keep the
            # release/edition/model terms from card_sets instead of sending
            # only ``<person> trading cards``.
            value = doorzo_catalog_query(value)
        else:
            # Flea-market and auction tabs use the broad reference-collector
            # query; exact release/person matching remains post-filter logic.
            value = doorzo_discovery_query(value)
    value = re.sub(
        r'"(?:card|cards|trading\s+card|trading\s+cards|トレカ|トレーディングカード)"',
        " ",
        value,
        flags=re.I,
    )
    if platform not in {"yahoo-auctions-jp", "jdirectmarket", "ebay"}:
        value = value.replace('"', " ")
    return re.sub(r"\s+", " ", value).strip()


def mercari_default_series_query(query: str) -> str:
    """Return the initial direct-Mercari wording for the enabled series."""
    normalized = normalize_search_text(query)
    if any(term in normalized for term in ("juicy honey", "ジューシーハニー")):
        return "juicy honey"
    if any(term in normalized for term in (
        "cj sexy", "cj sexy card", "cj トレカ", "cj オフィシャルカードコレクション",
    )):
        return "cj sexy"
    if any(term in normalized for term in (
        "woohoo", "woohoo girls", "woohoo トレーディングカード", "ウーフーガールズ",
    )):
        return "woohoo"
    if any(term in normalized for term in ("hits", "hit's", "ヒッツ")):
        if "ヒッツ" in normalized:
            return "ヒッツ"
        if "hit's" in normalized:
            return "HIT'S"
        return "HITS"
    return query


def doorzo_discovery_query(query: str) -> str:
    """Build the broad Doorzo query used by the Japan alias collector.

    The internal query is intentionally more precise because it is used to
    attribute a returned sold listing to a card_set. Doorzo receives a compact
    model/series discovery query instead, matching the reference rules:
    ``<model> trading cards``. The last non-series quoted term is treated as
    the model; release subtitles and years are never sent as mandatory Doorzo
    terms.
    """
    normalized = normalize_search_text(query)
    quoted = [normalize_search_text(value) for value in re.findall(r'"([^"]+)"', query)]
    series_terms = (
        "juicy honey", "ジューシーハニー", "cj sexy", "cj sexy card",
        "cj トレカ", "cj オフィシャルカードコレクション", "woohoo",
        "woohoo girls", "woohoo トレーディングカード", "ウーフーガールズ",
        "hits", "hit's", "hits limited", "ヒッツ",
    )
    release_terms = (
        "plus", "luxury", "deluxe", "exquisite", "anniversary", "edition",
        "vol", "volume",
    )
    subtitle_markers = ("~", "～", "natural body", "infinity", "series")
    model = ""
    for value in reversed(quoted):
        if not value or any(term in value for term in series_terms):
            continue
        if is_generic_query_hint(value) or re.fullmatch(r"(?:19|20)\d{2}", value):
            continue
        if re.fullmatch(r"(?:vol(?:ume)?\.?\s*)?\d{1,3}", value, re.I):
            continue
        if any(term == value or term in value.split() for term in release_terms):
            continue
        if any(marker in value for marker in subtitle_markers):
            continue
        model = value
        break

    if not model:
        if any(term in normalized for term in ("juicy honey", "ジューシーハニー")):
            model = "JUICY HONEY"
        elif any(term in normalized for term in ("cj sexy", "cj トレカ", "cj オフィシャルカードコレクション")):
            model = "CJ SEXY"
        elif any(term in normalized for term in ("woohoo", "ウーフー")):
            model = "WooHoo"
        elif any(term in normalized for term in ("hits", "hit's", "ヒッツ")):
            model = "HITS"
        else:
            return query

    return f"{model} trading cards"


def doorzo_catalog_query(query: str) -> str:
    """Keep meaningful release terms for Doorzo's retail catalog tabs."""
    quoted = [
        normalize_search_text(value)
        for value in re.findall(r'"([^"]+)"', query)
    ]
    values = quoted or [normalize_search_text(query)]
    ignored = {
        "card", "cards", "trading card", "trading cards", "トレカ",
        "トレーディングカード",
    }
    cleaned = []
    for value in values:
        if not value:
            continue
        value = re.sub(
            r"\b(?:card|cards|trading\s+card|trading\s+cards)\b|"
            r"トレカ|トレーディングカード",
            " ",
            value,
            flags=re.I,
        )
        value = re.sub(r"\s+", " ", value).strip()
        if value and value not in ignored:
            cleaned.append(value)
    values = cleaned
    return re.sub(r"\s+", " ", " ".join(values)).strip()


def with_yahoo_page(url: str, page_number: int, page_size: int) -> str:
    start = ((page_number - 1) * page_size) + 1
    separator = "&" if "?" in url else "?"
    return f"{url}{separator}b={start}&n={page_size}"


def with_marketplace_page(platform: str, url: str, page_number: int, page_size: int) -> str:
    if platform == "yahoo-auctions-jp":
        return with_yahoo_page(url, page_number, page_size)
    separator = "&" if "?" in url else "?"
    if platform == "ebay":
        return f"{url}{separator}_pgn={page_number}&_ipg={page_size}"
    if platform == "aucfan":
        return f"{url}{separator}p={page_number}"
    if platform == "mercari-jp":
        # Current public search uses v1:N tokens where page two starts at
        # v1:1. The backend fingerprint guard still stops safely if Mercari
        # changes or ignores this token format.
        if page_number == 1:
            return url
        page_token = quote(f"v1:{page_number - 1}", safe="")
        return f"{url}{separator}page_token={page_token}"
    if platform == "ruten-tw":
        # Ruten's public search uses ``p`` for the one-based result page.
        # The generic ``page`` parameter is ignored and makes every backend
        # request return page one.
        return f"{url}{separator}p={page_number}"
    if platform == "naver-shopping-kr":
        # Naver Shopping names both pagination inputs explicitly. Supplying
        # generic page/limit parameters leaves the rendered result unchanged.
        return (
            f"{url}{separator}pagingIndex={page_number}"
            f"&pagingSize={page_size}"
        )
    if platform == "shopee-tw":
        # Shopee exposes a zero-based page number in its public search state.
        return f"{url}{separator}page={page_number - 1}"
    if is_doorzo_platform(platform):
        # Doorzo uses an infinite result grid. Guessed page/nextPageToken URL
        # parameters are ignored by the current SPA. Each backend page reloads
        # the search, expands the grid to the requested window, and slices that
        # window so the backend can persist/notify before requesting the next.
        return url
    return f"{url}{separator}page={page_number}&limit={page_size}"


def is_doorzo_platform(platform: str) -> bool:
    return str(platform or "").lower().startswith("doorzo-")


def doorzo_website_for_platform(platform: str) -> str:
    website = str(platform or "").lower().removeprefix("doorzo-")
    if website not in {
        "mercari", "rakuma", "yahoo", "paypay", "surugaya", "rakuten",
        "amazon", "lashinbang",
    }:
        raise ValueError(f"unsupported Doorzo source: {platform}")
    return website


def doorzo_source_platform(website: str) -> str:
    return {
        "mercari": "mercari-jp",
        "rakuma": "rakuma",
        "yahoo": "yahoo-auctions-jp",
        "paypay": "yahoo-furima-jp",
        "surugaya": "surugaya",
        "rakuten": "rakuten",
        "amazon": "amazon-jp",
        "lashinbang": "lashinbang",
    }.get(str(website or "").lower(), "")


def ensure_search_page_usable(page, platform: str) -> None:
    # domcontentloaded only means the initial HTML arrived. Doorzo (and
    # Mercari pages reached through it) hydrate a client-rendered app after
    # that event, and older CloakBrowser builds can expose an empty body for a
    # few seconds. Poll both evaluate and the locator instead of failing on a
    # single empty snapshot. The longer Doorzo window is still bounded so a
    # blocked page cannot hang a worker indefinitely.
    timeout_seconds = 60 if is_doorzo_platform(platform) else 30
    deadline = time.monotonic() + timeout_seconds
    body = ""
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            body = page.evaluate(
                "() => document.body?.innerText || document.documentElement?.innerText || "
                "document.body?.textContent || ''"
            )
        except Exception as exc:
            last_error = exc

        if not str(body or "").strip():
            wait_for_selector = getattr(page, "wait_for_selector", None)
            if wait_for_selector is not None:
                try:
                    wait_for_selector("body", state="attached", timeout=2000)
                except Exception as exc:
                    last_error = exc
                    body = ""
                    try:
                        page.wait_for_timeout(750)
                    except Exception:
                        pass
                    continue
            try:
                body = page.locator("body").inner_text(timeout=5000)
            except Exception as exc:
                last_error = exc
                body = ""

        if str(body or "").strip():
            break
        try:
            page.wait_for_timeout(1000)
        except Exception:
            pass

    body = str(body or "").lower()
    if not body:
        raise SearchPageRenderError(
            f"{platform} page body was empty after {timeout_seconds} seconds"
        ) from last_error
    blocked_markers = (
        "captcha",
        "verify you are human",
        "access denied",
        "too many requests",
        # Naver Shopping returns a localized restriction page rather than a
        # CAPTCHA. Without these markers the result wait expires and the
        # caller incorrectly records a successful empty page.
        "쇼핑 서비스 접속이 일시적으로 제한되었습니다",
        "비정상적인 접근이 감지",
        "접속이 일시적으로 제한되었습니다",
        "자동화된 접근",
    )
    if any(marker in body for marker in blocked_markers):
        raise RuntimeError(
            f"{platform} returned an access challenge; no listings were imported"
        )
    if platform == "yahoo-auctions-jp":
        # Yahoo occasionally changes the localized heading (or renders it
        # after the initial DOM snapshot). Trust the closed-search URL and
        # result markers instead of requiring one exact Japanese sentence.
        current_url = ""
        try:
            current_url = str(page.url or "").lower()
        except Exception:
            pass
        yahoo_closed_search = "closedsearch/closedsearch" in current_url
        yahoo_result_markers = (
            "落札された商品",
            "落札価格",
            "落札相場",
            "終了日時",
            "終了180日間",
        )
        if not yahoo_closed_search and not any(marker in body for marker in yahoo_result_markers):
            raise RuntimeError(
                "Yahoo Auctions completed-results page was not available; no listings were imported"
            )


def load_search_page(page, page_url: str, platform: str, attempts: int = 2, mode: str = "sold") -> None:
    """Navigate after response commit and wait for a usable DOM.

    Marketplace pages may keep ``domcontentloaded`` pending on analytics or
    streaming resources even after the document and result markup are usable.
    Waiting for the response commit keeps navigation bounded while the
    readiness checks below still reject blank, blocked, or incomplete pages.
    """
    last_error: Exception | None = None
    for attempt in range(1, max(1, attempts) + 1):
        try:
            page.goto(page_url, wait_until="commit", timeout=45000)
        except Exception as exc:
            # Navigation errors can also be transient on a small VPS. Retry
            # them once before returning the original browser error.
            last_error = exc
        else:
            try:
                page.wait_for_timeout(1500 if attempt == 1 else 2500)
                ensure_search_page_usable(page, platform)
                if is_doorzo_platform(platform):
                    if str(mode or "sold").lower() != "active":
                        disable_doorzo_stock_only(page)
                    wait_for_doorzo_results(page)
                elif platform == "mercari-jp":
                    wait_for_mercari_results(page)
                elif platform in REGIONAL_RESULT_SELECTORS:
                    wait_for_regional_results(page, platform)
                return
            except SearchPageRenderError as exc:
                last_error = exc
            except RuntimeError:
                # Access challenges and a missing Yahoo completed-results
                # heading are deterministic page-state errors; do not hide
                # them behind a second request.
                raise
        if attempt < max(1, attempts):
            log_progress(
                platform,
                f"page body unavailable; retrying navigation ({attempt + 1}/{attempts})",
            )
            try:
                page.wait_for_timeout(500)
            except Exception:
                pass
    raise last_error or SearchPageRenderError(
        f"{platform} page did not render after {attempts} navigation attempts"
    )


def wait_for_doorzo_results(page, timeout_seconds: int = 20) -> None:
    """Allow Doorzo's hydrated result grid to appear after body hydration."""
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        try:
            if page.locator("a.goods-item[href]").count() > 0:
                return
            body = page.evaluate(
                "() => document.body?.innerText || document.documentElement?.innerText || ''"
            )
        except Exception:
            body = ""
        normalized = normalize_search_text(str(body or ""))
        if re.search(r"no\s+(?:results?|items?)|not\s+found|該当(?:する商品|商品)がありません", normalized, re.I):
            return
        try:
            page.wait_for_timeout(1000)
        except Exception:
            return


def wait_for_mercari_results(page, timeout_seconds: int = 25) -> None:
    """Wait for Mercari's client-side result grid after the shell hydrates."""
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        try:
            result_count = page.locator(
                "a[href*='/item/'], a[href*='/shops/product/']"
            ).count()
        except Exception:
            result_count = 0
        if result_count > 0:
            return
        try:
            body = normalize_search_text(page.locator("body").inner_text(timeout=5000))
        except Exception:
            body = ""
        if re.search(
            r"該当(?:する商品|商品)がありません|商品が見つかりません|no results?",
            body,
            re.I,
        ):
            return
        try:
            page.wait_for_timeout(750)
        except Exception:
            return


REGIONAL_RESULT_SELECTORS = {
    "ruten-tw": "a[href*='/item/'], a[href*='/product/']",
    # Shopee's current product links use ``...-i.<shop_id>.<item_id>``.
    "shopee-tw": "a[href*='-i.'], a[href*='/product/']",
    "bunjang-kr": "a[href*='/products/'], a[href*='/product/']",
    "naver-shopping-kr": "a[href*='/catalog/'], a[href*='/products/'], a[href*='/main/products/'], a[href*='/window-products/']",
    # Daangn/Karrot currently exposes locality-scoped listings under
    # /kr/buy-sell/, while older pages used /articles/ and /used/.
    "karrot-kr": "a[href*='/kr/buy-sell/'], a[href*='/articles/'], a[href*='/used/']",
}


def wait_for_regional_results(page, platform: str, timeout_seconds: int = 20) -> None:
    """Wait for Taiwan/Korea marketplace result cards after client hydration."""
    selector = REGIONAL_RESULT_SELECTORS.get(platform)
    if not selector:
        return
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        try:
            if page.locator(selector).count() > 0:
                return
        except Exception:
            pass
        try:
            body = normalize_search_text(page.locator("body").inner_text(timeout=5000))
        except Exception:
            body = ""
        if re.search(
            r"no\s+(?:results?|items?)|not\s+found|該当(?:する商品|商品)がありません|"
            r"找不到|沒有(?:商品|結果)|無(?:商品|結果)|검색\s*결과가\s*없습니다|"
            r"상품이\s*없습니다|검색된\s*상품이\s*없습니다",
            body,
            re.I,
        ):
            return
        try:
            page.wait_for_timeout(750)
        except Exception:
            return


def disable_doorzo_stock_only(page, timeout_seconds: int = 20) -> None:
    """Turn off Doorzo's default In Stock filter in the rendered UI.

    Live Doorzo inspection on 2026-08-15 confirmed that ``isStock=false`` and
    ``isStock=0`` both render the checkbox as checked. Only interacting with
    the hydrated control exposes cards bearing Doorzo's sold overlay.
    """
    deadline = time.monotonic() + timeout_seconds
    checkbox = page.locator(
        "input.el-checkbox__original[type='checkbox'][value='In Stock']"
    ).first
    while time.monotonic() < deadline:
        try:
            if checkbox.count() > 0:
                if not checkbox.is_checked():
                    return
                try:
                    checkbox.uncheck(force=True, timeout=10000)
                except Exception:
                    checkbox.locator("xpath=ancestor::label").click(
                        force=True, timeout=10000
                    )
                page.wait_for_timeout(1500)
                if not checkbox.is_checked():
                    return
        except Exception:
            pass
        try:
            page.wait_for_timeout(500)
        except Exception:
            break
    raise RuntimeError(
        "Doorzo In Stock filter could not be disabled; refusing to inspect active-only results"
    )


def expand_doorzo_result_window(
    page, page_number: int, page_size: int, max_scrolls: int = 40
) -> int:
    """Load enough of Doorzo's infinite grid for one backend page window."""
    target = max(1, page_number) * max(1, page_size)
    selector = "a.goods-item[href]"
    previous_count = -1
    stable_rounds = 0
    for _ in range(max_scrolls):
        count = page.locator(selector).count()
        if count >= target:
            return count
        try:
            body = page.locator("body").inner_text(timeout=5000)
        except Exception:
            body = ""
        if re.search(r"no\s+more\s+data\s+available|no\s+more\s+(?:items?|results?)", body, re.I):
            return count
        stable_rounds = stable_rounds + 1 if count == previous_count else 0
        if stable_rounds >= 3:
            return count
        previous_count = count
        try:
            page.evaluate("() => window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(1000)
        except Exception:
            return count
    return page.locator(selector).count()


def doorzo_page_slice(values: list, page_number: int, page_size: int) -> list:
    start = (max(1, page_number) - 1) * max(1, page_size)
    return values[start:start + max(1, page_size)]


def collect_result_urls(page, platform: str) -> list[str]:
    links = page.eval_on_selector_all(
        "a[href]",
        "els => els.map(a => a.href).filter(Boolean)",
    )
    result = []
    seen = set()
    for link in links:
        if link in seen or not is_marketplace_result_url(link, platform):
            continue
        seen.add(link)
        result.append(link)
    return result


def is_marketplace_result_url(link: str, platform: str) -> bool:
    parsed = urlparse(link)
    host = (parsed.hostname or "").lower()
    path = parsed.path.lower()
    if is_doorzo_platform(platform):
        expected_source = doorzo_website_for_platform(platform)
        path_parts = [part for part in path.split("/") if part]
        return (
            host.endswith("doorzo.com")
            and len(path_parts) >= 4
            and path_parts[-3] == expected_source
            and path_parts[-2] == "detail"
        )
    if platform == "aucfan":
        return (
            (host == "aucview.aucfan.com" or host.endswith("aucview.com"))
            and path not in {"", "/"}
        ) or (
            host.endswith("aucfan.com") and ("/item/" in path or "/auction/" in path)
        )
    if platform == "mercari-jp":
        return host.endswith("mercari.com") and (
            "/item/" in path or "/items/" in path or "/shops/product/" in path
        )
    if platform == "yahoo-auctions-jp":
        return host.endswith("auctions.yahoo.co.jp") and "/jp/auction/" in path
    if platform == "rakuma":
        return (
            (host == "item.fril.jp" and path not in {"", "/"})
            or (host.endswith("fril.jp") and ("/item/" in path or "/product/" in path))
        )
    if platform == "yahoo-furima-jp":
        return host.endswith("paypayfleamarket.yahoo.co.jp") and "/item/" in path
    if platform == "surugaya":
        return host.endswith("suruga-ya.jp") and "/product/detail/" in path
    if platform == "mandarake":
        return "mandarake" in host and ("detail" in path or "/item" in path)
    if platform == "ebay":
        return host.endswith("ebay.com") and "/itm/" in path
    if platform == "tcgplayer":
        return host.endswith("tcgplayer.com") and "/product/" in path
    if platform == "ruten-tw":
        return host.endswith("ruten.com.tw") and ("/item/" in path or "/product/" in path)
    if platform == "shopee-tw":
        return host.endswith("shopee.tw") and (
            "/product/" in path
            or re.search(r"(?:^|/)[^/]+-i\.\d+\.\d+(?:/|$)", path) is not None
        )
    if platform == "bunjang-kr":
        return host.endswith("bunjang.co.kr") and ("/products/" in path or "/product/" in path)
    if platform == "naver-shopping-kr":
        return (host.endswith("naver.com") or host.endswith("smartstore.naver.com")) and (
            "/catalog/" in path or "/products/" in path or "/main/products/" in path
        )
    if platform == "karrot-kr":
        return host.endswith("daangn.com") and (
            "/kr/buy-sell/" in path or "/articles/" in path or "/used/" in path
        )
    return False


def collect_yahoo_completed_items(
    page,
    page_size: int,
    query: str = "",
    from_bound: datetime | None = None,
    to_bound: datetime | None = None,
    diagnostics: dict[str, int] | None = None,
) -> list[dict]:
    cards = page.eval_on_selector_all(
        'a[href*="/jp/auction/"]',
        """els => els.map(a => {
            const card = a.closest('li, .Product, [class*="Product"]') || a;
            const titleLink = card.querySelector('a.Product__titleLink, a[href*="/jp/auction/"]') || a;
            const image = card ? card.querySelector('img') : null;
            const imageCandidates = image ? [image.currentSrc, image.src, image.getAttribute('data-src'), image.getAttribute('data-original'), image.getAttribute('data-lazy-src'), ((image.getAttribute('srcset') || '').split(',')[0] || '').trim().split(' ')[0]] : [];
            const imageURL = imageCandidates.find(value => typeof value === 'string' && (value.startsWith('http://') || value.startsWith('https://'))) || '';
            return {
                url: a.href,
                title: titleLink.getAttribute('title') || (titleLink.innerText || a.innerText || '').trim(),
                text: card ? (card.innerText || '') : '',
                tracking: a.getAttribute('data-cl-params') || titleLink.getAttribute('data-cl-params') || '',
                image: imageURL
            };
        })""",
    )
    items = []
    seen_urls = set()
    for card in cards:
        link = card.get("url", "")
        if not link or link in seen_urls:
            continue
        hostname = (urlparse(link).hostname or "").lower()
        if hostname not in {"auctions.yahoo.co.jp", "page.auctions.yahoo.co.jp"}:
            continue
        seen_urls.add(link)
        increment_diagnostic(diagnostics, "renderedCandidates")
        tracking = card.get("tracking", "")
        text = card.get("text", "")
        title = card.get("title", "")
        if query:
            precise_query = mercari_query_has_explicit_constraints(query)
            if (precise_query and not title_matches_query(title, query)) or (
                not precise_query and not mercari_title_matches_series(title, query)
            ):
                increment_diagnostic(diagnostics, "queryMismatch")
                continue
        status = sold_evidence(text, "yahoo-auctions-jp", title)
        if not status:
            # The closed-search page can include ended-without-sale rows.  A
            # tracking end timestamp and price field alone do not prove a
            # winning bid, so require Yahoo's per-card 落札/Sold marker too.
            increment_diagnostic(diagnostics, "missingSoldEvidence")
            continue
        increment_diagnostic(diagnostics, "soldCandidates")
        end_match = re.search(r"(?:^|[;,])end:(\d{9,13})(?:[;,]|$)", tracking)
        # Yahoo's tracking payload often exposes ``p`` as the displayed
        # current/start price.  On a closed auction that value can be lower
        # than the winning bid, so never use it as the sale amount.  Require
        # the explicit per-card 落札 label rendered in the result card and
        # skip rows whose final amount is not publicly rendered.
        price_match = re.search(
            r"(?<!最低)落札(?:価格|額)?\s*([0-9][0-9,]*)\s*円", text
        )
        price_source = "visible sold price"
        end_unix = int(end_match.group(1)) if end_match else extract_yahoo_closed_end_epoch(text)
        if end_unix is None:
            increment_diagnostic(diagnostics, "missingSoldDate")
            continue
        if not price_match:
            increment_diagnostic(diagnostics, "missingFinalPrice")
            continue
        # Yahoo sometimes serializes epoch milliseconds in the tracking
        # attribute and sometimes serializes epoch seconds.
        if end_unix > 100_000_000_000:
            end_unix //= 1000
        price = float(price_match.group(1).replace(",", ""))
        sold_at = datetime.fromtimestamp(end_unix, tz=timezone.utc)
        if from_bound and sold_at < from_bound:
            increment_diagnostic(diagnostics, "outsideDateRange")
            continue
        if to_bound and sold_at > to_bound:
            increment_diagnostic(diagnostics, "outsideDateRange")
            continue
        condition = ""
        for label in (
            "未使用",
            "未使用に近い",
            "目立った傷や汚れなし",
            "やや傷や汚れあり",
            "傷や汚れあり",
            "全体的に状態が悪い",
        ):
            if label in text:
                condition = label
                break
        external_id = extract_external_id(link)
        raw = {
            "marketplaceCode": "yahoo-auctions-jp",
            "dataProviderCode": "yahoo-auctions-jp",
            "url": link,
            "status": "completed",
            "statusEvidence": status,
            "priceType": "auction_hammer",
            "sourceField": (
                "data-cl-params.end + " + price_source
                if end_match
                else "visible ended-at text + " + price_source
            ),
            "endUnix": end_unix,
            "title": title,
            "price": price,
            "currency": "JPY",
        }
        items.append({
            "externalListingId": external_id,
            "originalUrl": link,
            "retrievalUrl": link,
            "dataProviderCode": "yahoo-auctions-jp",
            "title": title,
            "soldAt": sold_at.isoformat().replace("+00:00", "Z"),
            "endedAt": sold_at.isoformat().replace("+00:00", "Z"),
            "sourceTimezone": "Asia/Tokyo",
            "sourceCapturedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "marketplaceRegion": "JP",
            "sellerCountryCode": "JP",
            "originalPriceAmount": price,
            "originalCurrencyCode": "JPY",
            "saleType": "completed",
            "statusEvidence": status,
            "priceType": "auction_hammer",
            "condition": condition,
            "imageReferences": json.dumps(
                [card.get("image")] if card.get("image") else []
            ),
            "rawPayload": json.dumps(raw, ensure_ascii=False),
        })
    return items


def extract_yahoo_closed_end_epoch(text: str) -> int | None:
    """Parse Yahoo's visible ``7/11 21:26 終了`` fallback timestamp."""
    match = re.search(
        r"(?:(20\d{2})[年/-])?(\d{1,2})[月/-](\d{1,2})日?"
        r"(?:\s*\([^)]*\))?\s+(\d{1,2}):(\d{2})\s*(?:終了|end)",
        text or "",
        re.I,
    )
    if not match:
        return None
    year, month, day, hour, minute = match.groups()
    now_local = datetime.now(source_timezone_value("Asia/Tokyo"))
    resolved_year = int(year or now_local.year)
    try:
        candidate = datetime(
            resolved_year,
            int(month),
            int(day),
            int(hour),
            int(minute),
            tzinfo=source_timezone_value("Asia/Tokyo"),
        )
    except ValueError:
        return None
    # Yahoo's closed history spans 180 days and omits the year for recent
    # cards. A future month/day belongs to the previous calendar year.
    if not year and candidate > now_local + timedelta(days=1):
        try:
            candidate = candidate.replace(year=candidate.year - 1)
        except ValueError:
            return None
    return int(candidate.timestamp())


def extract_yahoo_sold_price(text: str) -> float | None:
    """Return Yahoo Auctions' rendered winning amount, never its start price."""
    match = re.search(
        r"(?<!最低)落札(?:価格|額)?\s*([0-9][0-9,]*)\s*円", text or ""
    )
    if not match:
        return None
    return float(match.group(1).replace(",", ""))


def collect_yahoo_furima_completed_items(
    page,
    page_size: int,
    query: str = "",
    from_bound: datetime | None = None,
    to_bound: datetime | None = None,
    diagnostics: dict[str, int] | None = None,
) -> list[dict]:
    """Collect Yahoo! Flea sold cards using the origin detail page.

    Yahoo! Flea search cards expose a sold badge and price, but the reliable
    purchase/completion timestamp is rendered on the item detail page as
    ``購入日時``. This keeps the stored ``soldAt`` tied to the marketplace
    event instead of the scrape time.
    """
    cards = page.eval_on_selector_all(
        "a[href]",
        """els => els.map(a => {
            const card = a.closest('article, li, [data-testid], [class*="item"], [class*="card"]');
            const image = card ? card.querySelector('img') : null;
            const imageCandidates = image ? [image.currentSrc, image.src, image.getAttribute('data-src'), image.getAttribute('data-original'), image.getAttribute('data-lazy-src'), ((image.getAttribute('srcset') || '').split(',')[0] || '').trim().split(' ')[0]] : [];
            const imageURL = imageCandidates.find(value => typeof value === 'string' && (value.startsWith('http://') || value.startsWith('https://'))) || '';
            const root = card || a;
            return {
                url: a.href,
                title: (a.getAttribute('title') || a.innerText || '').trim(),
                text: card ? (card.innerText || '') : (a.innerText || ''),
                accessibleText: Array.from(root.querySelectorAll('[aria-label], img[alt]'))
                    .map(el => el.getAttribute('aria-label') || el.getAttribute('alt') || '')
                    .filter(Boolean).join(' '),
                image: imageURL
            };
        })""",
    )
    items = []
    seen_urls = set()
    for card in cards:
        link = str(card.get("url") or "").strip()
        if not link or link in seen_urls or not is_marketplace_result_url(link, "yahoo-furima-jp"):
            continue
        seen_urls.add(link)
        increment_diagnostic(diagnostics, "renderedCandidates")
        title = marketplace_card_title(card, "yahoo-furima-jp")
        card_text = marketplace_card_text(card)
        status = sold_evidence(card_text, "yahoo-furima-jp", title)
        if not status:
            increment_diagnostic(diagnostics, "missingSoldEvidence")
            continue
        increment_diagnostic(diagnostics, "soldCandidates")
        if query and not active_listing_is_relevant(title, card_text, query):
            increment_diagnostic(diagnostics, "queryMismatch")
            continue
        if not hasattr(page, "goto"):
            # Keep fixture/unit-test pages useful; live browser pages always
            # expose goto and therefore require the exact detail timestamp.
            increment_diagnostic(diagnostics, "missingSoldDate")
            continue
        try:
            page.goto(link, wait_until="domcontentloaded", timeout=60000)
            body = page.locator("body").inner_text(timeout=10000) or ""
        except Exception:
            increment_diagnostic(diagnostics, "detailErrors")
            continue
        detail_title = clean_marketplace_detail_title(
            str(extract_structured_product(page).get("name") or extract_title(page) or title),
            "yahoo-furima-jp",
        ) or title
        detail_status = sold_evidence(body, "yahoo-furima-jp", detail_title) or status
        sold_at = extract_sold_date(
            page, body, require_label=True, source_timezone="Asia/Tokyo"
        )
        if not sold_at:
            increment_diagnostic(diagnostics, "missingSoldDate")
            continue
        sold_datetime = datetime.fromisoformat(sold_at.replace("Z", "+00:00"))
        if from_bound and sold_datetime < from_bound:
            increment_diagnostic(diagnostics, "outsideDateRange")
            continue
        if to_bound and sold_datetime > to_bound:
            increment_diagnostic(diagnostics, "outsideDateRange")
            continue
        price, currency = extract_price(page, body, "yahoo-furima-jp")
        if price is None:
            increment_diagnostic(diagnostics, "missingFinalPrice")
            continue
        image_url = extract_image(page) or str(card.get("image") or "").strip()
        external_id = extract_marketplace_external_id(link, "yahoo-furima-jp")
        raw = {
            "marketplaceCode": "yahoo-furima-jp",
            "dataProviderCode": "yahoo-furima-jp",
            "url": link,
            "status": "completed",
            "statusEvidence": detail_status,
            "soldAtEvidence": "purchase_datetime",
            "sourceText": body[:5000],
            "title": detail_title,
            "price": price,
            "currency": currency,
        }
        items.append({
            "externalListingId": external_id,
            "originalUrl": link,
            "retrievalUrl": link,
            "dataProviderCode": "yahoo-furima-jp",
            "title": detail_title,
            "soldAt": sold_at,
            "endedAt": sold_at,
            "sourceTimezone": "Asia/Tokyo",
            "sourceCapturedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "marketplaceRegion": "JP",
            "sellerCountryCode": "JP",
            "originalPriceAmount": price,
            "originalCurrencyCode": currency,
            "saleType": "completed",
            "statusEvidence": detail_status,
            "priceType": "fixed_price_sold",
            "imageReferences": json.dumps([image_url] if image_url else []),
            "rawPayload": json.dumps(raw, ensure_ascii=False),
        })
    return items


def collect_active_listing_check(page, platform: str, url: str, title_hint: str = "") -> list[dict]:
    """Open one stored listing URL and classify its visible lifecycle state."""
    checked_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    # Yahoo's direct detail page is authoritative for the live current bid.
    # Search cards can lag behind the detail page, especially immediately after
    # a bid, so search is only used below as an exact-ID fallback when the detail
    # page is unavailable or does not expose a usable current price.
    body = ""
    structured = {}
    detail_image = ""
    title = str(title_hint or "").strip()
    navigation_error = ""
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        wait_for_marketplace_detail(page, platform)
        if platform == "yahoo-auctions-jp":
            try:
                page.wait_for_selector("text=終了日時", timeout=1500)
            except Exception:
                pass
        body = page.locator("body").inner_text(timeout=10000) or ""
        structured = extract_structured_product(page)
        detail_image = extract_image(page)
        detail_title = clean_marketplace_detail_title(
            str(structured.get("name") or extract_title(page) or ""),
            platform,
        )
        if detail_title:
            title = detail_title
    except Exception as exc:
        navigation_error = str(exc)[:500]

    source_timezone = platform_source_timezone(platform)
    # Yahoo! Flea is fixed-price. Its embedded page data can contain deadline
    # fields for recommendation widgets, which must not turn the origin detail
    # into an auction or override its sold purchase timestamp.
    auction_ends_at = extract_auction_end_date_from_page(
        page, body, source_timezone
    ) if body and platform != "yahoo-furima-jp" else None
    sold_status = sold_evidence(body, platform, title) if body else ""
    inactive_status = inactive_listing_evidence(body, platform, title) if body else ""
    if auction_ends_at and not sold_status and not inactive_status:
        try:
            parsed_auction_end = datetime.fromisoformat(
                auction_ends_at.replace("Z", "+00:00")
            )
            if parsed_auction_end <= datetime.now(timezone.utc):
                inactive_status = "auction_ended"
        except ValueError:
            pass
    status_evidence = sold_status or inactive_status
    is_auction = bool(
        body and (
            auction_ends_at
            or is_active_auction_text(body, platform)
            or status_evidence in {"ended_with_winner", "auction_ended", "auction_ended_without_winner"}
        )
    )
    state = "unknown"
    if body:
        if status_evidence:
            state = "inactive"
        else:
            detail_text = normalize_search_text(body)
            normalized_title = normalize_search_text(title)
            if normalized_title:
                detail_text = detail_text.replace(normalized_title, " ")
            if is_auction or re.search(
                r"販売中|出品中|在庫あり|購入手続き|カートに入れる|買い物かご|"
                r"available|in\s+stock|buy\s+now|add\s+to\s+cart|for\s+sale|"
                r"現在価格|即決|入札|残り|終了予定|time\s+left|auction|bid|"
                r"판매중|구매하기|장바구니|재고 있음|판매 중|"
                r"販售中|立即購買|加入購物車|有庫存",
                detail_text,
                re.I,
            ):
                state = "active"
                status_evidence = "active_detail"
            else:
                status_evidence = "check_unknown"
    else:
        status_evidence = "check_error" if navigation_error else "check_empty"

    listing_type = "auction" if is_auction else ("fixed_price" if body and state == "active" else "")
    current_price = None
    buy_now_price = None
    if body and state == "active":
        if platform == "yahoo-auctions-jp":
            current_price, buy_now_price = extract_yahoo_active_prices(body)
        else:
            current_price, _ = extract_price(page, body, platform, structured)
    if (
        platform == "yahoo-auctions-jp"
        and title_hint
        and state != "inactive"
        and (state == "unknown" or current_price is None)
    ):
        search_item = find_yahoo_active_search_item(page, url, title_hint)
        if search_item:
            return [search_item]
        completed_item = find_yahoo_completed_search_item(page, url, title_hint)
        if completed_item:
            return [completed_item]
    elif body and state == "inactive" and sold_status and not is_auction:
        # Fixed-price marketplaces usually render the final item amount on the
        # sold detail page. Preserve it for the lifecycle-created sold row;
        # this is still marked unverified when the source exposes only a sold
        # badge and no transaction timestamp.
        current_price, _ = extract_price(page, body, platform, structured)
    sold_at = None
    sold_price = None
    if platform == "yahoo-auctions-jp" and status_evidence == "ended_with_winner":
        sold_price = extract_yahoo_sold_price(body)
        sold_at = auction_ends_at
        if sold_at is None:
            end_unix = extract_yahoo_closed_end_epoch(body)
            if end_unix is not None:
                sold_at = datetime.fromtimestamp(end_unix, tz=timezone.utc).isoformat().replace("+00:00", "Z")
    elif sold_status and not is_auction:
        sold_at = extract_sold_date(
            page,
            body,
            require_label=platform in {"mercari-jp", "rakuma", "yahoo-furima-jp"},
            source_timezone=source_timezone,
        )
        if sold_at is None and platform == "mercari-jp":
            sold_at = extract_mercari_update_time(page, body)
    if sold_price is not None:
        price_type = "auction_hammer"
    elif sold_status:
        price_type = "fixed_price_sold" if current_price is not None else "sold_observed"
    else:
        price_type = "active_check"
    observed_price = sold_price if sold_price is not None else current_price
    raw = {
        "url": url,
        "platform": platform,
        "state": state,
        "statusEvidence": status_evidence,
        "checkedAt": checked_at,
        "listingType": listing_type,
        "auctionEndsAt": auction_ends_at or "",
        "currentPrice": current_price,
        "buyNowPrice": buy_now_price,
        "soldAt": sold_at or "",
        "soldPrice": sold_price,
        "priceType": price_type,
        "image": detail_image,
    }
    if navigation_error:
        raw["error"] = navigation_error
    currency = "TWD" if platform in {"ruten-tw", "shopee-tw"} else (
        "KRW" if platform in {"bunjang-kr", "naver-shopping-kr", "karrot-kr"} else (
            "USD" if platform in {"ebay", "tcgplayer"} else "JPY"
        )
    )
    return [{
        "externalListingId": extract_marketplace_external_id(url, platform),
        "originalUrl": url,
        "retrievalUrl": url,
        "dataProviderCode": platform,
        "title": title,
        "activeAt": checked_at,
        "auctionEndsAt": auction_ends_at,
        "soldAt": sold_at,
        "endedAt": sold_at,
        "sourceTimezone": source_timezone,
        "saleType": state,
        "listingType": listing_type,
        "statusEvidence": status_evidence,
        "priceType": price_type,
        "originalPriceAmount": observed_price,
        "buyNowPriceAmount": buy_now_price,
        "originalCurrencyCode": currency,
        "imageReferences": json.dumps([detail_image] if detail_image else []),
        "rawPayload": json.dumps(raw, ensure_ascii=False),
    }]


def wait_for_marketplace_detail(page, platform: str) -> None:
    """Wait for client-rendered detail content before reading its lifecycle."""
    if platform != "mercari-jp":
        return
    wait_for_selector = getattr(page, "wait_for_selector", None)
    if callable(wait_for_selector):
        try:
            wait_for_selector("main h1, h1", state="visible", timeout=15000)
        except TypeError:
            try:
                wait_for_selector("main h1, h1", timeout=15000)
            except Exception:
                pass
        except Exception:
            pass
    wait_for_timeout = getattr(page, "wait_for_timeout", None)
    if callable(wait_for_timeout):
        try:
            wait_for_timeout(250)
        except Exception:
            pass


def find_yahoo_active_search_item(
    page, original_url: str, title_hint: str
) -> dict | None:
    """Find one stored Yahoo lot in active search for reconciliation."""
    external_id = extract_marketplace_external_id(
        original_url, "yahoo-auctions-jp"
    )
    if not external_id or not str(title_hint or "").strip():
        return None
    try:
        search_url = build_search_url(
            "yahoo-auctions-jp", title_hint, 100, mode="active"
        )
        load_search_page(
            page, search_url, "yahoo-auctions-jp", mode="active"
        )
        candidates = collect_marketplace_active_items(
            page, "yahoo-auctions-jp", 100, query=""
        )
    except Exception:
        return None
    for candidate in candidates:
        if candidate.get("externalListingId") != external_id:
            continue
        candidate["originalUrl"] = original_url
        candidate["retrievalUrl"] = original_url
        candidate["saleType"] = "active"
        candidate["statusEvidence"] = "active_search_match"
        candidate["priceType"] = "active_check"
        try:
            raw = json.loads(candidate.get("rawPayload") or "{}")
        except (TypeError, ValueError, json.JSONDecodeError):
            raw = {}
        raw.update({
            "url": original_url,
            "state": "active",
            "statusEvidence": "active_search_match",
            "reconciliationEvidence": "exact_external_id_search_match",
        })
        candidate["rawPayload"] = json.dumps(raw, ensure_ascii=False)
        return candidate
    return None


def find_yahoo_completed_search_item(
    page, original_url: str, title_hint: str
) -> dict | None:
    """Find one stored Yahoo lot in closed search and require a final price."""
    external_id = extract_marketplace_external_id(
        original_url, "yahoo-auctions-jp"
    )
    if not external_id or not str(title_hint or "").strip():
        return None
    try:
        search_url = build_search_url(
            "yahoo-auctions-jp", title_hint, 100, mode="sold"
        )
        load_search_page(
            page, search_url, "yahoo-auctions-jp", mode="sold"
        )
        candidates = collect_yahoo_completed_items(
            page, 100, query=""
        )
    except Exception:
        return None
    for candidate in candidates:
        if candidate.get("externalListingId") != external_id:
            continue
        candidate["originalUrl"] = original_url
        candidate["retrievalUrl"] = original_url
        candidate["listingType"] = "auction"
        candidate["priceType"] = "auction_hammer"
        if candidate.get("endedAt") and not candidate.get("auctionEndsAt"):
            candidate["auctionEndsAt"] = candidate["endedAt"]
        try:
            raw = json.loads(candidate.get("rawPayload") or "{}")
        except (TypeError, ValueError, json.JSONDecodeError):
            raw = {}
        raw.update({
            "url": original_url,
            "state": "inactive",
            "statusEvidence": candidate.get("statusEvidence") or "ended_with_winner",
            "reconciliationEvidence": "exact_external_id_closed_search_match",
        })
        candidate["rawPayload"] = json.dumps(raw, ensure_ascii=False)
        return candidate
    return None


PLACEHOLDER_IMAGE_URL_RE = re.compile(
    r"(?:item_square_dummy|no[-_ ]?(?:image|photo)|image[-_ ]?not[-_ ]?found|placeholder)",
    re.I,
)


def first_usable_image_reference(*values) -> str:
    """Return the first HTTP image URL that is not a known UI placeholder."""
    candidates = []
    for value in values:
        if isinstance(value, (list, tuple)):
            candidates.extend(value)
        else:
            candidates.append(value)
    for value in candidates:
        candidate = str(value or "").strip()
        if not re.match(r"^https?://", candidate, re.I):
            continue
        if PLACEHOLDER_IMAGE_URL_RE.search(candidate):
            continue
        return candidate
    return ""


def collect_marketplace_active_items(
    page,
    platform: str,
    page_size: int,
    query: str = "",
    from_bound: datetime | None = None,
    to_bound: datetime | None = None,
    diagnostics: dict[str, int] | None = None,
    model_aliases: list[str] | None = None,
    rendered_urls: list[str] | None = None,
) -> list[dict]:
    """Collect currently available marketplace rows without sold markers."""
    cards = page.eval_on_selector_all(
        "a[href]",
        """els => els.map(a => {
            // eBay marks both its image and title anchors with ``s-card``.
            // Prefer the containing result <li> so the image anchor does not
            // become its own root before the title anchor in the DOM.
            const card = a.closest('li.s-card, li') || a.closest('article, [data-testid], .item-box, [class*="card"]');
            const root = card || a;
            const detailLinkSelector = 'a.Product__titleLink, a[href*="/jp/auction/"], a[href*="/auction/"], a[href*="/item/"], a[href*="/itm/"]';
            // Yahoo result cards contain several links (for example, a
            // separate "送料 無料" link).  Only use the auction-detail
            // anchor for the title/URL; never let an arbitrary child anchor
            // become the persisted listing title.
            const titleLink = (a.matches && a.matches(detailLinkSelector))
                ? a
                : (root.querySelector(detailLinkSelector) || a);
            const titleNode = root.querySelector('.Product__title, h3[class*="Product__title" i], .s-card__title, [class*="s-card__title" i]');
            const visibleTitle = titleNode
                ? (titleNode.innerText || titleNode.textContent || '').trim()
                : '';
            const metadataTitleNode = root.querySelector('[data-auction-title]');
            const metadataTitle = metadataTitleNode
                ? (metadataTitleNode.getAttribute('data-auction-title') || '').trim()
                : '';
            const time = root.querySelector('time[datetime]');
            // Rakuma/fril frequently keeps the image under the result link
            // itself, or lazy-loads it through data-* attributes/picture
            // sources rather than a normal src value.
            const image = root.querySelector('img');
            // Rakuma initially renders item_square_dummy in src/currentSrc and
            // keeps the seller photo in data-original until lazy loading has
            // completed. Prefer the lazy-source attributes and reject known
            // placeholders before considering the rendered src.
            const imageCandidates = image ? [
                image.getAttribute('data-original'),
                image.getAttribute('data-original-src'),
                image.getAttribute('data-src'),
                image.getAttribute('data-lazy-src'),
                image.getAttribute('data-image'),
                ...Array.from(root.querySelectorAll('source[srcset]')).flatMap(source =>
                    (source.getAttribute('srcset') || '').split(',').map(value => value.trim().split(' ')[0])
                ),
                ((image.getAttribute('srcset') || '').split(',')[0] || '').trim().split(' ')[0],
                image.currentSrc,
                image.src,
                image.getAttribute('src')
            ] : [];
            const imageURL = imageCandidates.map(value => {
                if (typeof value !== 'string' || !value.trim()) return '';
                try { return new URL(value.trim(), document.baseURI).href; } catch (_) { return ''; }
            }).find(value => (value.startsWith('http://') || value.startsWith('https://')) &&
                !/(?:item_square_dummy|no[-_ ]?(?:image|photo)|image[-_ ]?not[-_ ]?found|placeholder)/i.test(value)) || '';
            const accessibleText = Array.from(root.querySelectorAll('[aria-label], img[alt]'))
                .map(el => el.getAttribute('aria-label') || el.getAttribute('alt') || '')
                .filter(Boolean).join(' ');
            // Yahoo's active-result metadata contains the authoritative Unix
            // end timestamp (for example, ``...;end:1787236764;...``). The
            // direct detail page is not consistently available to the
            // worker, so retain this exact value from the listing card.
            const trackingMetadata = [root, titleLink, ...Array.from(root.querySelectorAll('[data-cl-params]'))]
                .map(el => el && el.getAttribute ? (el.getAttribute('data-cl-params') || '') : '')
                .filter(Boolean).join(';');
            const auctionEndMatch = trackingMetadata.match(/(?:^|;)end:([0-9]{10,13})(?:;|$)/);
            return {
                url: titleLink.href || a.href,
                title: (visibleTitle || metadataTitle || titleLink.getAttribute('data-auction-title') || titleLink.getAttribute('title') || titleLink.getAttribute('aria-label') || titleLink.getAttribute('data-title') || root.getAttribute('title') || titleLink.innerText || root.innerText || '').trim(),
                text: (root.innerText || a.innerText || ''),
                accessibleText,
                activeAt: time ? (time.getAttribute('datetime') || '') : '',
                auctionEndsAt: auctionEndMatch ? auctionEndMatch[1] : '',
                image: imageURL
            };
        })""",
    )
    items = []
    seen_urls = set()
    for card in cards:
        link = str(card.get("url") or "").strip()
        if not link or link in seen_urls or not is_marketplace_result_url(link, platform):
            continue
        seen_urls.add(link)
        if rendered_urls is not None:
            rendered_urls.append(link)
        increment_diagnostic(diagnostics, "renderedCandidates")
        title = marketplace_card_title(card, platform)
        text = marketplace_card_text(card)
        source_timezone = platform_source_timezone(platform)
        card_active_at = normalize_date(card.get("activeAt"), source_timezone=source_timezone)
        # Filter old timestamped cards before opening their detail page. Some
        # marketplaces do not publish an active/created timestamp; those cards
        # remain eligible and use first-observed time below.
        if not active_listing_date_in_range(card_active_at, from_bound, to_bound):
            increment_diagnostic(diagnostics, "outsideActiveDateRange")
            continue
        search_is_auction = is_active_auction_text(text, platform)
        search_auction_ends_at = (
            normalize_date(card.get("auctionEndsAt"), source_timezone)
            or extract_auction_end_date(text, source_timezone)
            if search_is_auction
            else None
        )
        detail_body = ""
        detail_structured = {}
        # Yahoo's search cards can expose the shipping link (送料 無料) as
        # the first auction anchor.  The auction detail page has the
        # authoritative title, so refresh it before persisting/notification.
        yahoo_title_needs_detail = (
            platform == "yahoo-furima-jp"
            and invalid_marketplace_listing_title(title)
        )
        auction_end_needs_detail = (
            platform in {"aucfan", "mandarake", "ebay"}
            and search_is_auction
            and not search_auction_ends_at
        )
        if (yahoo_title_needs_detail or auction_end_needs_detail) and hasattr(page, "goto"):
            try:
                increment_diagnostic(diagnostics, "detailNavigations")
                page.goto(link, wait_until="domcontentloaded", timeout=60000)
                if platform == "yahoo-auctions-jp":
                    try:
                        page.wait_for_selector("text=終了日時", timeout=1500)
                    except Exception:
                        pass
                detail_body = page.locator("body").inner_text(timeout=10000) or ""
                detail_structured = extract_structured_product(page)
                detail_title = clean_marketplace_detail_title(
                    str(detail_structured.get("name") or extract_title(page) or ""),
                    platform,
                )
                if detail_title:
                    title = detail_title
            except Exception:
                increment_diagnostic(diagnostics, "detailErrors")
        if invalid_marketplace_listing_title(title):
            increment_diagnostic(diagnostics, "invalidTitle")
            continue
        evidence_text = "\n".join(value for value in (text, detail_body) if value)
        if sold_evidence(evidence_text, platform, title):
            increment_diagnostic(diagnostics, "soldCandidates")
            continue
        if inactive_listing_evidence(evidence_text, platform, title):
            increment_diagnostic(diagnostics, "inactiveCandidates")
            continue
        if not active_listing_is_relevant(title, evidence_text, query, model_aliases):
            increment_diagnostic(diagnostics, "irrelevantActiveCandidates")
            continue
        status = active_evidence(evidence_text, platform, title)
        if not status:
            increment_diagnostic(diagnostics, "missingActiveEvidence")
            continue
        buy_now_price = None
        if platform == "yahoo-auctions-jp":
            # Yahoo renders several yen values on an auction card.  The
            # first number is often the starting bid, so only accept the
            # explicitly labelled current bid.  Never infer an auction price
            # from an unlabeled number, a starting bid, or a buy-now amount.
            current_price, buy_now_price = extract_yahoo_active_prices(evidence_text)
            price = current_price
            currency = "JPY"
        else:
            price, currency = extract_price(
                page if detail_body else None,
                evidence_text,
                platform,
                detail_structured,
            )
        if price is None:
            increment_diagnostic(diagnostics, "missingCurrentPrice")
            continue
        active_at = card_active_at
        if not active_at:
            active_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        if not active_listing_date_in_range(active_at, from_bound, to_bound):
            increment_diagnostic(diagnostics, "outsideActiveDateRange")
            continue
        is_auction = bool(
            search_is_auction
            or is_active_auction_text(evidence_text, platform)
            or search_auction_ends_at
        )
        auction_ends_at = search_auction_ends_at
        auction_end_evidence = (
            "search_metadata"
            if card.get("auctionEndsAt") and auction_ends_at
            else ("search_card" if auction_ends_at else "")
        )
        if is_auction and detail_body:
            detail_auction_end = extract_auction_end_date_from_page(
                page, detail_body, source_timezone
            )
            if detail_auction_end:
                auction_ends_at = detail_auction_end
                auction_end_evidence = "detail_page"
        listing_type = "auction" if is_auction else "fixed_price"
        if is_auction:
            if auction_ends_at:
                increment_diagnostic(diagnostics, "auctionEndDates")
            else:
                increment_diagnostic(diagnostics, "missingAuctionEndDate")
        region = platform_region(platform)
        external_id = extract_marketplace_external_id(link, platform)
        image_url = first_usable_image_reference(
            extract_image(page) if detail_body else "",
            card.get("image"),
        )
        raw = {
            "marketplaceCode": platform,
            "dataProviderCode": platform,
            "url": link,
            "status": "active",
            "statusEvidence": status,
            "listingType": listing_type,
            "activeAt": active_at,
            "auctionEndsAt": auction_ends_at or "",
            "auctionEndEvidence": auction_end_evidence,
            "sourceText": evidence_text[:5000],
            "title": title,
            "price": price,
            "buyNowPrice": buy_now_price,
            "currency": currency,
            "image": image_url,
        }
        items.append({
            "externalListingId": external_id,
            "originalUrl": link,
            "retrievalUrl": link,
            "dataProviderCode": platform,
            "title": title,
            "activeAt": active_at,
            "auctionEndsAt": auction_ends_at,
            "sourceTimezone": source_timezone,
            "sourceCapturedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "marketplaceRegion": region,
            "sellerCountryCode": region,
            "originalPriceAmount": price,
            "buyNowPriceAmount": buy_now_price,
            "originalCurrencyCode": currency,
            "saleType": "auction" if listing_type == "auction" else "active",
            "listingType": listing_type,
            "statusEvidence": status,
            "priceType": "auction_current" if listing_type == "auction" else "fixed_price_active",
            "imageReferences": json.dumps([image_url] if image_url else []),
            "rawPayload": json.dumps(raw, ensure_ascii=False),
        })
        increment_diagnostic(diagnostics, "activeCandidates")
        if listing_type == "auction":
            increment_diagnostic(diagnostics, "auctionCandidates")
    return items


def collect_doorzo_active_items(
    page,
    platform: str,
    page_size: int,
    query: str = "",
    from_bound: datetime | None = None,
    to_bound: datetime | None = None,
    diagnostics: dict[str, int] | None = None,
    page_number: int = 1,
    model_aliases: list[str] | None = None,
    rendered_urls: list[str] | None = None,
) -> list[dict]:
    """Collect in-stock Doorzo proxy rows and preserve the origin URL."""
    expected_website = doorzo_website_for_platform(platform)
    expected_source = doorzo_source_platform(expected_website)
    cards = page.eval_on_selector_all(
        "a.goods-item[href]",
        """els => els.map(a => ({
            url: a.href,
            title: (a.querySelector('.goods-name')?.innerText || a.getAttribute('title') || '').trim(),
            text: (a.innerText || '').trim(),
            image: a.querySelector('img.img')?.src || '',
            soldBadge: Boolean(a.querySelector('img.sold, img[src*="sold_icon"]'))
        }))""",
    )
    cards = doorzo_page_slice(cards, page_number, page_size)
    items = []
    seen_urls = set()
    for card in cards:
        detail_url = str(card.get("url") or "").strip()
        if not detail_url or detail_url in seen_urls or not is_marketplace_result_url(detail_url, platform):
            continue
        seen_urls.add(detail_url)
        if rendered_urls is not None:
            rendered_urls.append(detail_url)
        increment_diagnostic(diagnostics, "renderedCandidates")
        text = str(card.get("text") or "")
        title = str(card.get("title") or "").strip()
        if not title:
            increment_diagnostic(diagnostics, "missingTitle")
            continue
        if bool(card.get("soldBadge")) or sold_evidence(text, expected_source, title):
            increment_diagnostic(diagnostics, "soldCandidates")
            continue
        if inactive_listing_evidence(text, expected_source, title):
            increment_diagnostic(diagnostics, "inactiveCandidates")
            continue
        if active_listing_has_non_card_category(title, text):
            increment_diagnostic(diagnostics, "irrelevantActiveCandidates")
            continue
        detail_body = ""
        detail_structured = {}
        if hasattr(page, "goto"):
            try:
                increment_diagnostic(diagnostics, "detailNavigations")
                page.goto(detail_url, wait_until="domcontentloaded", timeout=60000)
                detail_body = page.locator("body").inner_text(timeout=10000) or ""
                detail_structured = extract_structured_product(page)
                title = extract_title(page) or title
            except Exception:
                increment_diagnostic(diagnostics, "detailErrors")
        evidence_text = detail_body or text
        if not active_listing_is_relevant(title, evidence_text, query, model_aliases):
            increment_diagnostic(diagnostics, "irrelevantActiveCandidates")
            continue
        price, currency = extract_price(page if detail_body else None, evidence_text, expected_source, detail_structured)
        if price is None:
            increment_diagnostic(diagnostics, "missingCurrentPrice")
            continue
        status = active_evidence(evidence_text, expected_source, title) or "active_stock"
        is_auction = is_active_auction_text(evidence_text, expected_source)
        auction_ends_at = extract_auction_end_date(evidence_text, "Asia/Tokyo") if is_auction else None
        listing_type = "auction" if is_auction else "fixed_price"
        source_url = extract_doorzo_origin_url(page, detail_url)
        if not source_url or (urlparse(source_url).hostname and "doorzo.com" in (urlparse(source_url).hostname or "").lower()):
            increment_diagnostic(diagnostics, "missingOriginalUrl")
            continue
        if not doorzo_source_url_matches(source_url, expected_source):
            increment_diagnostic(diagnostics, "sourceMismatch")
            continue
        external_id = extract_marketplace_external_id(source_url, expected_source)
        active_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        if not active_listing_date_in_range(active_at, from_bound, to_bound):
            increment_diagnostic(diagnostics, "outsideActiveDateRange")
            continue
        image_url = extract_image(page) or str(card.get("image") or "").strip()
        raw = {
            "marketplaceCode": expected_source,
            "dataProviderCode": "doorzo",
            "url": source_url,
            "retrievalUrl": detail_url,
            "doorzoWebsite": expected_website,
            "status": "active",
            "statusEvidence": status,
            "listingType": listing_type,
            "activeAt": active_at,
            "auctionEndsAt": auction_ends_at or "",
            "sourceText": evidence_text[:5000],
            "title": title,
            "price": price,
            "currency": currency,
        }
        items.append({
            "externalListingId": external_id,
            "originalUrl": source_url,
            "retrievalUrl": detail_url,
            "dataProviderCode": "doorzo",
            "title": title,
            "activeAt": active_at,
            "auctionEndsAt": auction_ends_at,
            "sourceTimezone": "Asia/Tokyo" if expected_source != "ebay" else "UTC",
            "sourceCapturedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "marketplaceRegion": "JP",
            "sellerCountryCode": "JP",
            "originalPriceAmount": price,
            "originalCurrencyCode": currency,
            "saleType": "auction" if listing_type == "auction" else "active",
            "listingType": listing_type,
            "statusEvidence": status,
            "priceType": "auction_current" if listing_type == "auction" else "fixed_price_active",
            "imageReferences": json.dumps([image_url] if image_url else []),
            "rawPayload": json.dumps(raw, ensure_ascii=False),
        })
        increment_diagnostic(diagnostics, "activeCandidates")
        if listing_type == "auction":
            increment_diagnostic(diagnostics, "auctionCandidates")
    return items


def collect_marketplace_completed_items(
    page,
    platform: str,
    page_size: int,
    query: str = "",
    from_bound: datetime | None = None,
    to_bound: datetime | None = None,
    diagnostics: dict[str, int] | None = None,
    model_aliases: list[str] | None = None,
) -> list[dict]:
    """Collect publicly rendered sold cards from non-Yahoo marketplaces.

    This intentionally requires both sold-state evidence and an exact source
    timestamp when the marketplace publishes one. Mercari's updateTime is the
    best public time signal for a sold card; it is preferred over the scrape
    time and marked as ``update_time`` provenance. Rakuma still falls back to
    first-observed only when its public page omits a labeled completion or
    purchase timestamp. Suruga-ya out-of-stock catalog pages and TCGplayer
    aggregate prices remain excluded.
    """
    page_confirms_aucfan_history = platform == "aucfan" and page_has_aucfan_sold_history(page)
    cards = page.eval_on_selector_all(
        "a[href]",
        """els => els.map(a => {
            const card = a.closest('article, li, [data-testid], .item-box, [class*="card"]');
            const time = card ? card.querySelector('time[datetime]') : null;
            const updateNode = card ? card.querySelector('[data-update-time], [data-updated-at], [data-testid*="update" i]') : null;
            const root = card || a;
            const image = root.querySelector('img');
            // Rakuma's search cards can expose a neutral square placeholder in
            // src/currentSrc while data-original already contains the seller
            // photo. Keep the lazy source ahead of the rendered placeholder.
            const imageCandidates = image ? [
                image.getAttribute('data-original'),
                image.getAttribute('data-original-src'),
                image.getAttribute('data-src'),
                image.getAttribute('data-lazy-src'),
                image.getAttribute('data-image'),
                ...Array.from(root.querySelectorAll('source[srcset]')).flatMap(source =>
                    (source.getAttribute('srcset') || '').split(',').map(value => value.trim().split(' ')[0])
                ),
                ((image.getAttribute('srcset') || '').split(',')[0] || '').trim().split(' ')[0],
                image.currentSrc,
                image.src,
                image.getAttribute('src')
            ] : [];
            const imageURL = imageCandidates.map(value => {
                if (typeof value !== 'string' || !value.trim()) return '';
                try { return new URL(value.trim(), document.baseURI).href; } catch (_) { return ''; }
            }).find(value => (value.startsWith('http://') || value.startsWith('https://')) &&
                !/(?:item_square_dummy|no[-_ ]?(?:image|photo)|image[-_ ]?not[-_ ]?found|placeholder)/i.test(value)) || '';
            const accessibleText = Array.from(root.querySelectorAll('[aria-label], img[alt]'))
                .map(el => el.getAttribute('aria-label') || el.getAttribute('alt') || '')
                .filter(Boolean)
                .join(' ');
            return {
                url: a.href,
                title: (a.getAttribute('title') || a.innerText || '').trim(),
                text: card ? (card.innerText || '') : (a.innerText || ''),
                accessibleText,
                // Mercari exposes the listing update timestamp on some
                // result/detail surfaces as a <time> value or data attribute.
                updateTime: (updateNode && (updateNode.getAttribute('data-update-time') || updateNode.getAttribute('data-updated-at'))) || (time ? (time.getAttribute('datetime') || '') : ''),
                soldAt: time ? (time.getAttribute('datetime') || '') : '',
                image: imageURL
            };
        })""",
    )
    items = []
    seen_urls = set()
    for card in cards:
        link = card.get("url", "")
        if not link or link in seen_urls or not is_marketplace_result_url(link, platform):
            continue
        seen_urls.add(link)
        increment_diagnostic(diagnostics, "renderedCandidates")
        title = marketplace_card_title(card, platform)
        text = marketplace_card_text(card)
        if not title:
            increment_diagnostic(diagnostics, "missingTitle")
            continue
        evidence_text = text
        if page_confirms_aucfan_history:
            evidence_text += "\n落札日 落札価格"
        status = sold_evidence(evidence_text, platform, title)
        if not status:
            increment_diagnostic(diagnostics, "missingSoldEvidence")
            continue
        increment_diagnostic(diagnostics, "soldCandidates")
        if active_listing_has_non_card_category(title, text):
            increment_diagnostic(diagnostics, "irrelevantSoldCandidates")
            continue
        if query and is_hits_series_query(query) and not hits_listing_has_card_context(title, text):
            increment_diagnostic(diagnostics, "queryMismatch")
            continue
        if query and platform in {
            "mercari-jp", "yahoo-auctions-jp", "aucfan", "rakuma"
        }:
            # The production searches are deliberately broad fixed terms, but
            # marketplaces also mix nearby products into those result pages.
            # Keep release codes and Japanese aliases (for example ``CJ137``)
            # while requiring the title to identify the searched series. This
            # prevents a CJ query from importing a generic official-card title
            # or a JUICY query from importing a model-only card.
            title_matches = mercari_title_matches_series(title, query)
            if not title_matches:
                increment_diagnostic(diagnostics, "queryMismatch")
                continue
        elif query and not (
            title_matches_query(title, query)
            or any(
                alias
                and not is_generic_query_hint(alias)
                and not is_series_query_hint(alias)
                and title_matches_query(title, alias)
                for alias in (model_aliases or [])
            )
        ):
            increment_diagnostic(diagnostics, "queryMismatch")
            continue
        # A bare date elsewhere in a result card can be a listing/review date,
        # not a transaction date. Mercari is the deliberate exception here:
        # its updateTime is the source timestamp the operator asked us to keep
        # for sold cards. Other flea-market surfaces require an explicit sale,
        # completion, purchase, or auction-end label.
        card_timestamp = None
        sold_at_evidence = "source_timestamp"
        if platform == "mercari-jp":
            card_timestamp = normalize_date(
                card.get("updateTime")
                or card.get("updatedAt")
                or card.get("updated")
                or card.get("soldAt"),
                source_timezone="Asia/Tokyo",
            )
            if card_timestamp:
                sold_at_evidence = "update_time"
        elif platform != "rakuma":
            card_timestamp = normalize_date(card.get("soldAt"))
        sold_at = card_timestamp or extract_sold_date(
            None,
            text,
            require_label=platform in {"mercari-jp", "rakuma"},
            source_timezone="Asia/Tokyo" if platform in {"mercari-jp", "rakuma"} else "UTC",
        )

        # Some Mercari and Rakuma result cards only expose the timestamp on the
        # item detail. Reuse the current browser page for a detail pass before
        # resorting to the explicitly marked first-observed fallback. The outer
        # pagination loop navigates back to the search page on the next page.
        detail_body = ""
        if not sold_at and platform in {"mercari-jp", "rakuma"} and hasattr(page, "goto"):
            try:
                page.goto(link, wait_until="domcontentloaded", timeout=60000)
                detail_body = page.locator("body").inner_text(timeout=10000) or ""
                if platform == "mercari-jp":
                    sold_at = extract_mercari_update_time(page, detail_body)
                    if sold_at:
                        sold_at_evidence = "update_time"
                else:
                    sold_at = extract_sold_date(
                        page, detail_body, require_label=True, source_timezone="Asia/Tokyo"
                    )
                    if sold_at:
                        sold_at_evidence = "completion_or_purchase_datetime"
                if detail_body:
                    status = sold_evidence(detail_body, platform, title) or status
            except Exception:
                increment_diagnostic(diagnostics, "detailErrors")

        if not sold_at and platform in {"mercari-jp", "rakuma"}:
            if from_bound or to_bound:
                increment_diagnostic(diagnostics, "missingSoldDate")
                continue
            sold_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
                "+00:00", "Z"
            )
            sold_at_evidence = "first_observed_sold"
            status = f"{status}_observed_at"
            increment_diagnostic(diagnostics, "observedSoldDate")
        if not sold_at:
            increment_diagnostic(diagnostics, "missingSoldDate")
            continue
        sold_datetime = datetime.fromisoformat(sold_at.replace("Z", "+00:00"))
        if from_bound and sold_datetime < from_bound:
            increment_diagnostic(diagnostics, "outsideDateRange")
            continue
        if to_bound and sold_datetime > to_bound:
            increment_diagnostic(diagnostics, "outsideDateRange")
            continue
        # Search cards often retain the final price in an accessible label
        # even when the detail body omits it. Keep both sources; putting the
        # card first also avoids mistaking an unrelated detail-page number for
        # the completed-sale price.
        price_text = "\n".join(value for value in (text, detail_body) if value)
        price, currency = extract_price(None, price_text, platform)
        if price is None:
            increment_diagnostic(diagnostics, "missingFinalPrice")
            continue
        external_id = extract_marketplace_external_id(link, platform)
        image_url = first_usable_image_reference(
            extract_image(page) if detail_body else "",
            card.get("image"),
        )
        source_timezone = "Asia/Tokyo" if platform in {
            "aucfan", "mercari-jp", "rakuma", "surugaya", "mandarake"
        } else "UTC"
        region = "JP" if source_timezone == "Asia/Tokyo" else "US"
        raw = {
            "marketplaceCode": platform,
            "dataProviderCode": platform,
            "url": link,
            "status": "completed",
            "statusEvidence": status,
            "soldAtEvidence": sold_at_evidence,
            "sourceTimestampField": sold_at_evidence,
            "sourceText": price_text[:4000],
            "title": title,
            "price": price,
            "currency": currency,
            "image": image_url,
        }
        if platform == "mercari-jp":
            raw["updateTime"] = (
                card.get("updateTime")
                or card.get("updatedAt")
                or card.get("updated")
                or (sold_at if sold_at_evidence == "update_time" else "")
            )
        items.append({
            "externalListingId": external_id,
            "originalUrl": link,
            "retrievalUrl": link,
            "dataProviderCode": platform,
            "title": title,
            "soldAt": sold_at,
            "endedAt": sold_at,
            "sourceTimezone": source_timezone,
            "sourceCapturedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "marketplaceRegion": region,
            "originalPriceAmount": price,
            "originalCurrencyCode": currency,
            "saleType": "completed",
            "statusEvidence": status,
            "soldAtEvidence": sold_at_evidence,
            "priceType": marketplace_price_type(platform, status, text, title),
            "imageReferences": json.dumps([image_url] if image_url else []),
            "rawPayload": json.dumps(raw, ensure_ascii=False),
        })
    return items


def collect_doorzo_completed_items(
    page,
    platform: str,
    page_size: int,
    query: str = "",
    from_bound: datetime | None = None,
    to_bound: datetime | None = None,
    diagnostics: dict[str, int] | None = None,
    page_number: int = 1,
) -> list[dict]:
    """Read Doorzo result cards, then verify each candidate on its detail page.

    Doorzo's search index mixes active and unavailable proxy records. A card's
    ``Second-hand`` tag is not a completed-sale marker, so only the origin
    detail page can qualify a row. The original marketplace URL is retained as
    ``originalUrl`` and Doorzo is recorded only as ``dataProviderCode``.
    """
    expected_website = doorzo_website_for_platform(platform)
    expected_source = doorzo_source_platform(expected_website)
    cards = page.eval_on_selector_all(
        "a.goods-item[href]",
        """els => els.map(a => ({
            url: a.href,
            title: (a.querySelector('.goods-name')?.innerText || a.getAttribute('title') || '').trim(),
            text: (a.innerText || '').trim(),
            image: a.querySelector('img.img')?.src || '',
            soldBadge: Boolean(a.querySelector('img.sold, img[src*="sold_icon"]'))
        }))""",
    )
    cards = doorzo_page_slice(cards, page_number, page_size)
    items = []
    seen_urls = set()
    for card in cards:
        detail_url = str(card.get("url") or "").strip()
        if (
            not detail_url
            or detail_url in seen_urls
            or not is_marketplace_result_url(detail_url, platform)
        ):
            continue
        seen_urls.add(detail_url)
        increment_diagnostic(diagnostics, "renderedCandidates")
        card_text = normalize_search_text(str(card.get("text") or ""))
        # Doorzo's sold state is an image overlay and therefore absent from
        # innerText. Require that rendered marker before following a detail;
        # ordinary Second-hand cards and Yahoo Current/Buyout cards are active.
        if not bool(card.get("soldBadge")) or re.search(
            r"\b(?:current|buyout|time\s+left)\b", card_text, re.I
        ):
            increment_diagnostic(diagnostics, "activeCandidates")
            continue
        if expected_source in {"surugaya", "rakuten"}:
            # Doorzo's retail sold overlay is an unavailable-stock marker. It
            # is useful for diagnostics, but no source transaction/price/date
            # exists to support a completed-sale row.
            increment_diagnostic(diagnostics, "inventoryUnavailableCandidates")
            continue
        try:
            page.goto(detail_url, wait_until="domcontentloaded", timeout=60000)
            body, structured, title, status = wait_for_doorzo_detail_state(
                page,
                expected_source,
                str(card.get("title") or "").strip(),
            )
        except Exception:
            increment_diagnostic(diagnostics, "detailErrors")
            continue
        body = str(body or "")
        if not title:
            increment_diagnostic(diagnostics, "missingTitle")
            continue
        if not status:
            increment_diagnostic(diagnostics, "missingSoldEvidence")
            continue
        increment_diagnostic(diagnostics, "soldCandidates")
        description = str(structured.get("description") or "").strip()
        match_text = "\n".join(value for value in (title, description) if value)
        if query and is_hits_series_query(query) and not hits_listing_has_card_context(title, description):
            increment_diagnostic(diagnostics, "queryMismatch")
            continue
        if query and not title_matches_query(match_text, query):
            increment_diagnostic(diagnostics, "queryMismatch")
            continue
        source_timezone = "Asia/Tokyo" if expected_source in {
            "yahoo-auctions-jp", "yahoo-furima-jp", "mercari-jp", "rakuma",
            "surugaya", "rakuten",
        } else "UTC"
        sold_at, sold_at_evidence = resolve_doorzo_sold_at(
            page, body, source_timezone, from_bound, to_bound
        )
        if not sold_at:
            increment_diagnostic(diagnostics, "missingSoldDate")
            continue
        if sold_at_evidence == "first_observed_sold":
            status = f"{status}_observed_at"
            increment_diagnostic(diagnostics, "observedSoldDate")
        sold_datetime = datetime.fromisoformat(sold_at.replace("Z", "+00:00"))
        if from_bound and sold_datetime < from_bound:
            increment_diagnostic(diagnostics, "outsideDateRange")
            continue
        if to_bound and sold_datetime > to_bound:
            increment_diagnostic(diagnostics, "outsideDateRange")
            continue
        price, currency = extract_price(page, body, expected_source, structured)
        if price is None:
            increment_diagnostic(diagnostics, "missingFinalPrice")
            continue
        # Doorzo cards often use a low-resolution thumbnail or lazy-loaded
        # placeholder. Prefer the origin detail's og:image, then retain the
        # rendered card image as a fallback for Telegram notifications.
        image_url = extract_image(page)
        if not image_url:
            structured_image = structured.get("image") if isinstance(structured, dict) else ""
            if isinstance(structured_image, list):
                structured_image = structured_image[0] if structured_image else ""
            image_url = str(structured_image or "").strip()
        image_url = image_url or str(card.get("image") or "").strip()
        source_url = extract_doorzo_origin_url(page, detail_url)
        source_parsed = urlparse(source_url)
        if source_parsed.hostname and "doorzo.com" in source_parsed.hostname.lower():
            increment_diagnostic(diagnostics, "missingOriginalUrl")
            continue
        if not doorzo_source_url_matches(source_url, expected_source):
            # A proxy detail page must not silently change marketplace identity
            # when its "View original page" link is missing, redirected, or
            # points at a different Doorzo source.
            increment_diagnostic(diagnostics, "sourceMismatch")
            continue
        external_id = extract_marketplace_external_id(source_url, expected_source)
        raw = {
            "marketplaceCode": expected_source,
            "dataProviderCode": "doorzo",
            "url": source_url,
            "retrievalUrl": detail_url,
            "doorzoWebsite": expected_website,
            "status": "completed",
            "statusEvidence": status,
            "soldAtEvidence": sold_at_evidence,
            "sourceText": body[:6000],
            "title": title,
            "description": description,
            "price": price,
            "currency": currency,
            "structuredProduct": structured,
        }
        items.append({
            "externalListingId": external_id,
            "originalUrl": source_url,
            "retrievalUrl": detail_url,
            "dataProviderCode": "doorzo",
            "title": title,
            "description": description,
            "soldAt": sold_at,
            "endedAt": sold_at,
            "sourceTimezone": source_timezone,
            "sourceCapturedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "marketplaceRegion": "JP",
            "sellerCountryCode": "JP",
            "originalPriceAmount": price,
            "originalCurrencyCode": currency,
            "saleType": "completed",
            "statusEvidence": status,
            "priceType": marketplace_price_type(expected_source, status, body, title),
            "imageReferences": json.dumps([image_url] if image_url else []),
            "rawPayload": json.dumps(raw, ensure_ascii=False),
        })
    return items


def wait_for_doorzo_detail_state(
    page,
    expected_source: str,
    fallback_title: str = "",
    timeout_seconds: int = 20,
) -> tuple[str, dict, str, str]:
    """Wait for Doorzo's item state instead of reading its early SPA shell."""
    deadline = time.monotonic() + timeout_seconds
    body = ""
    structured: dict = {}
    title = fallback_title
    status = ""
    while time.monotonic() < deadline:
        try:
            body = page.locator("body").inner_text(timeout=5000) or ""
        except Exception:
            body = ""
        structured = extract_structured_product(page)
        title = extract_title(page) or fallback_title
        status = sold_evidence(body, expected_source, title)
        if not status and expected_source in {
            "mercari-jp", "rakuma", "yahoo-furima-jp"
        }:
            availability = normalize_search_text(
                str(structured.get("availability") or "")
            )
            if re.search(r"(?:soldout|sold_out|outofstock|out_of_stock)$", availability):
                status = "doorzo_sold_out_badge"
        if status:
            return body, structured, title, status
        try:
            page.wait_for_timeout(1000)
        except Exception:
            break
    return body, structured, title, status


def extract_doorzo_origin_url(page, detail_url: str) -> str:
    links = page.eval_on_selector_all(
        "a[href]",
        """els => els.map(a => ({href: a.href, text: (a.innerText || '').trim()}))""",
    )
    for link in links:
        href = str(link.get("href") or "").strip()
        text = normalize_search_text(str(link.get("text") or ""))
        if not href or "doorzo.com" in (urlparse(href).hostname or "").lower():
            continue
        if "original" in text or "original" in href.lower():
            return href
    unwrapped = unwrap_doorzo_url(detail_url)
    return unwrapped


def doorzo_source_url_matches(source_url: str, platform: str) -> bool:
    """Ensure a Doorzo detail resolves back to the requested marketplace."""
    parsed = urlparse(unwrap_doorzo_url(source_url))
    host = (parsed.hostname or "").lower().removeprefix("www.")
    expected_hosts = {
        "mercari-jp": ("mercari.com",),
        "rakuma": ("fril.jp", "rakuma.rakuten.co.jp"),
        "yahoo-auctions-jp": ("auctions.yahoo.co.jp",),
        "yahoo-furima-jp": ("paypayfleamarket.yahoo.co.jp",),
        "surugaya": ("suruga-ya.jp",),
        "rakuten": ("item.rakuten.co.jp", "search.rakuten.co.jp"),
        "amazon-jp": ("amazon.co.jp", "amazon.com"),
        "lashinbang": ("lashinbang.com",),
    }.get(platform, ())
    return bool(parsed.scheme in {"http", "https"} and host and any(
        host == expected or host.endswith("." + expected)
        for expected in expected_hosts
    ))


def extract_doorzo_sold_date(
    page, body: str, source_timezone: str = "UTC"
) -> str | None:
    date_label = (
        r"(?:end\s*time|sold\s*(?:at|time)?|completed\s*(?:at|time)?|"
        r"落札日|取引完了)"
    )
    # Doorzo detail pages append dated shopping reviews after the product. A
    # generic first <time> selector can therefore assign another customer's
    # review time to this listing. Accept a datetime attribute only when its
    # immediate visible context is explicitly labelled as the sale/end time.
    if page is not None:
        try:
            times = page.locator("time[datetime]")
            for index in range(times.count()):
                value = times.nth(index).get_attribute("datetime")
                context = times.nth(index).locator("xpath=..").inner_text()
                if re.search(date_label, str(context or ""), re.I):
                    parsed = normalize_date(value)
                    if parsed:
                        return parsed
        except Exception:
            pass
    match = re.search(
        date_label + r"\s*[:\n ]+"
        r"([A-Z][a-z]{2,9})\.?\s+(\d{1,2}),?\s+(20\d{2})"
        r"(?:\s+(\d{1,2}):(\d{2})(?::(\d{2}))?)?",
        body,
        re.I,
    )
    if match:
        month_name, day, year, hour, minute, second = match.groups()
        try:
            month = datetime.strptime(month_name[:3], "%b").month
            local_zone = source_timezone_value(source_timezone)
            local_value = datetime(
                int(year), month, int(day), int(hour or 0), int(minute or 0),
                int(second or 0), tzinfo=local_zone,
            )
            return local_value.astimezone(timezone.utc).isoformat().replace(
                "+00:00", "Z"
            )
        except ValueError:
            pass
    numeric_match = re.search(
        date_label + r"\s*[:\n ]+(20\d{2})[/-](\d{1,2})[/-](\d{1,2})"
        r"(?:[ T]+(\d{1,2}):(\d{2})(?::(\d{2}))?)?",
        body,
        re.I,
    )
    if numeric_match:
        year, month, day, hour, minute, second = numeric_match.groups()
        local_zone = source_timezone_value(source_timezone)
        local_value = datetime(
            int(year), int(month), int(day), int(hour or 0), int(minute or 0),
            int(second or 0), tzinfo=local_zone,
        )
        return local_value.astimezone(timezone.utc).isoformat().replace(
            "+00:00", "Z"
        )
    return None


def resolve_doorzo_sold_at(
    page,
    body: str,
    source_timezone: str = "UTC",
    from_bound: datetime | None = None,
    to_bound: datetime | None = None,
) -> tuple[str | None, str]:
    """Return an exact source time or an explicitly marked observation time."""
    sold_at = extract_doorzo_sold_date(page, body, source_timezone)
    if sold_at:
        return sold_at, "source_timestamp"
    # Doorzo fixed-price details expose explicit Sold Out state and exact price
    # but may omit a transaction timestamp. An unbounded scheduled scan can
    # store when that state was first observed; a historical date query may not
    # substitute an observation timestamp for a requested source date.
    if from_bound or to_bound:
        return None, ""
    observed_at = datetime.now(timezone.utc).replace(microsecond=0)
    return observed_at.isoformat().replace("+00:00", "Z"), "first_observed_sold"


def source_timezone_value(source_timezone: str):
    """Return the small timezone set needed by the public marketplace pages."""
    if str(source_timezone or "").strip() == "Asia/Tokyo":
        return timezone(timedelta(hours=9))
    if str(source_timezone or "").strip() == "Asia/Taipei":
        return timezone(timedelta(hours=8))
    if str(source_timezone or "").strip() == "Asia/Seoul":
        return timezone(timedelta(hours=9))
    return timezone.utc


def platform_source_timezone(platform: str) -> str:
    if platform in {
        "ruten-tw", "shopee-tw",
    }:
        return "Asia/Taipei"
    if platform in {
        "bunjang-kr", "naver-shopping-kr", "karrot-kr",
    }:
        return "Asia/Seoul"
    if platform in {
        "aucfan", "mercari-jp", "rakuma", "surugaya", "mandarake", "rakuten",
        "yahoo-furima-jp", "yahoo-auctions-jp",
    }:
        return "Asia/Tokyo"
    return "UTC"


def platform_region(platform: str) -> str:
    if platform in {"ruten-tw", "shopee-tw"}:
        return "TW"
    if platform in {"bunjang-kr", "naver-shopping-kr", "karrot-kr"}:
        return "KR"
    if platform not in {"ebay", "tcgplayer"}:
        return "JP"
    return "US"


def increment_diagnostic(diagnostics: dict[str, int] | None, key: str) -> None:
    if diagnostics is not None:
        diagnostics[key] = diagnostics.get(key, 0) + 1


def page_has_aucfan_sold_history(page) -> bool:
    try:
        body = normalize_search_text(page.locator("body").inner_text(timeout=5000))
    except Exception:
        return False
    return bool(re.search(r"落札済み商品|落札相場|落札日\s*.*落札価格", body, re.I))


def marketplace_card_text(card: dict) -> str:
    """Combine visible and accessibility text from one search-result card."""
    values = [str(card.get("text") or ""), str(card.get("accessibleText") or "")]
    return "\n".join(value for value in values if value).strip()


def invalid_marketplace_listing_title(value: str) -> bool:
    """Reject price/status fragments and marketplace error-page headings."""
    title = re.sub(r"\s+", " ", html.unescape(str(value or ""))).strip()
    if not title:
        return True
    normalized = normalize_search_text(title)
    if any(fragment in normalized for fragment in (
        "ご覧になろうとしているページは現在表示できません",
        "一時的に利用を制限しています",
        "yahoo! japan - ヘルプ",
        "page is currently unavailable",
        "temporarily restricted",
        "access has been restricted",
    )):
        return True
    # Yahoo! Flea sometimes exposes the price/likes/promotion cluster as the
    # anchor's title. It is UI chrome, not the product name. Keep this check
    # deliberately narrow so a real listing title that merely mentions a
    # promotion is not rejected.
    ui_fragment = re.sub(
        r"^(?:(?:[¥￥]\s*)?[0-9][0-9,\.]*\s*円?\s*)?"
        r"(?:(?:いいね|ウォッチ)[!！]?\s*)?"
        r"(?:(?:購入|送料無料|送料\s*無料)\s*)?"
        r"(?:(?:最大\s*)?[0-9]+\s*%\s*(?:対象|還元|off)|"
        r"最大\s*[0-9]+\s*%\s*対象|クーポン(?:対象|利用可)?|キャンペーン対象)?$",
        "",
        title,
        flags=re.I,
    )
    if title and not ui_fragment.strip():
        return True
    return bool(re.fullmatch(
        r"(?:(?:[¥￥]\s*)?[0-9][0-9,\.]*\s*円?)?\s*"
        r"(?:(?:いいね|ウォッチ)[!！]?|購入|送料無料|送料\s*無料)?",
        title,
        re.I,
    ))


def yahoo_furima_title_is_descriptive(value: str) -> bool:
    """Require product-specific text beyond a bare series/card label."""
    normalized = normalize_search_text(value)
    if not (
        ACTIVE_CARD_SIGNAL_RE.search(value)
        or re.search(r"woohoo|juicy\s*honey|ジューシーハニー|cj\s*sexy|hit['’]?s|ヒッツ", normalized, re.I)
    ):
        # Some Yahoo! Flea cards omit both the series and the word "card".
        # Once price/likes/promotion chrome has been removed, a reasonably
        # long non-UI phrase is still a useful product-title fallback.
        product_text = re.sub(
            r"販売中|出品中|購入手続き|カートに入れる|送料無料|送料\s*無料|"
            r"いいね|ウォッチ|最大\s*[0-9]+\s*%\s*(?:対象|還元)|"
            r"クーポン(?:対象|利用可)?|キャンペーン対象",
            " ",
            normalized,
            flags=re.I,
        )
        product_text = re.sub(r"[^0-9a-z\u3040-\u30ff\u3400-\u9fff\uac00-\ud7af]+", "", product_text, flags=re.I)
        return len(product_text) >= 4
    remainder = re.sub(
        r"woohoo(?:\s*girls?)?|juicy\s*honey|ジューシーハニー|cj\s*sexy|"
        r"hit['’]?s(?:\s*limited)?|ヒッツ|"
        r"トレーディング\s*カード|トレカ|カード|trading\s*cards?|cards?|tcg",
        " ",
        normalized,
        flags=re.I,
    )
    remainder = re.sub(r"[^0-9a-z\u3040-\u30ff\u3400-\u9fff\uac00-\ud7af]+", "", remainder, flags=re.I)
    return len(remainder) >= 2


def yahoo_furima_card_title(card: dict) -> str:
    """Recover Yahoo Flea's title when the first item anchor is price/likes."""
    original = re.sub(
        r"\s+", " ", html.unescape(str(card.get("title") or ""))
    ).strip()
    candidates = []
    accessible = html.unescape(str(card.get("accessibleText") or ""))
    for match in re.finditer(r"(.+?)の画像(?:\s|$)", accessible, re.I):
        candidates.append(match.group(1))
    candidates.extend(str(card.get("text") or "").splitlines())
    if original:
        candidates.append(original)

    descriptive = []
    for value in candidates:
        candidate = re.sub(r"\s+", " ", str(value or "")).strip()
        candidate = re.sub(
            r"^(?:[¥￥]\s*)?[0-9][0-9,\.]*\s*円?\s*", "", candidate
        )
        candidate = re.sub(r"^(?:(?:いいね|ウォッチ)[!！]?\s*)+", "", candidate, flags=re.I)
        candidate = re.sub(r"\s*の画像$", "", candidate).strip()
        if invalid_marketplace_listing_title(candidate):
            continue
        if yahoo_furima_title_is_descriptive(candidate):
            descriptive.append(candidate)
    if descriptive:
        return max(descriptive, key=len)
    return original


def marketplace_card_title(card: dict, platform: str) -> str:
    """Extract the product title without status badges or localized prices."""
    title = str(card.get("title") or "").strip()
    accessible = re.sub(
        r"\s+", " ", html.unescape(str(card.get("accessibleText") or ""))
    ).strip()
    if platform == "mercari-jp" and accessible:
        # Current Mercari cards put the canonical title, sold badge, JPY
        # amount, and viewer-localized amount in a role=img aria-label.
        match = re.match(r"(.+?)の画像(?:\s|$)", accessible, re.I)
        if match and match.group(1).strip():
            return match.group(1).strip()
    if platform == "yahoo-furima-jp":
        return yahoo_furima_card_title(card)
    return title


def clean_marketplace_detail_title(value: str, platform: str) -> str:
    """Keep the product name when a detail page exposes a browser/price title."""
    title = re.sub(r"\s+", " ", html.unescape(str(value or ""))).strip()
    if invalid_marketplace_listing_title(title):
        return ""
    if platform == "yahoo-auctions-jp":
        title = re.sub(r"\s*(?:\||｜|-)\s*Yahoo!オークション.*$", "", title, flags=re.I)
    elif platform == "yahoo-furima-jp":
        title = re.sub(
            r"\s*(?:\||｜|-)\s*(?:Yahoo!フリマ|PayPayフリマ|Yahoo! Flea Market).*$",
            "",
            title,
            flags=re.I,
        )
        if invalid_marketplace_listing_title(title):
            return ""
    return title.strip()


def sold_evidence(text: str, platform: str, title: str = "") -> str:
    """Return a marketplace-specific proof that a listing actually sold.

    A page being closed, out of stock, or showing a price is not enough:
    marketplaces use different labels for a completed transaction.  The
    optional title is removed before matching status labels so phrases such as
    ``SOLD OUT`` in a product title cannot masquerade as a sold badge.
    """
    lowered = normalize_search_text(text)
    normalized_title = normalize_search_text(title)
    if normalized_title:
        lowered = lowered.replace(normalized_title, " ")

    if platform in {"surugaya", "tcgplayer"}:
        # These public surfaces expose retail stock/aggregate market prices,
        # not per-item completed-sale records.
        return ""

    if platform == "yahoo-furima-jp":
        # Yahoo! Flea Market/JDirectItems Flea is a fixed-price source. Its
        # origin detail must show a completed/unavailable transaction marker;
        # an auction winner label belongs to the separate Yahoo Auctions tab.
        # Some sold origin pages expose only the sold image and the purchase
        # timestamp in text, for example ``購入日時：2026年5月31日``.
        if re.search(
            r"売り切れ|売約済み|取引完了|この商品は[\s\S]{0,20}売れました|"
            r"購入\s*日時\s*[:：]?\s*20\d{2}\s*年|"
            r"sold\s*out\b|\bsold\b",
            lowered,
            re.I,
        ):
            return "platform_sold"
        return ""

    if platform in {"yahoo-auctions-jp", "jdirectmarket"}:
        # Yahoo's closed-search results can contain ended auctions without a
        # winning bid.  Require the per-card Japanese sold/winner marker.
        # Do not match ordinary active-page copy such as ``今すぐ落札``,
        # ``ご落札後`` or ``落札時``. Those phrases appear in seller
        # instructions and the active buy-now button, not in a completed-sale
        # marker. A Japanese match must include an explicit winner label or a
        # numeric winning amount.
        if re.search(
            r"(?<!最低)(?<!未)(?<!ご)(?<!お)落札(?:者あり|"
            r"(?:価格|額)\s*[:：]?\s*[0-9][0-9,]*(?:\s*円)?|"
            r"\s*[0-9][0-9,]*\s*円)|winning\s*(?:bid|price)|sold\b",
            lowered,
            re.I,
        ):
            return "ended_with_winner"
        return ""

    if platform in {"mercari-jp", "rakuma"}:
        # Mercari serves the same sold sticker as Japanese ``売り切れ`` or
        # English ``SOLD`` depending on the rendered locale. The title has
        # already been removed above, so a word such as ``SOLD OUT EDITION``
        # cannot satisfy this check by itself. Item pages can also retain only
        # the shipment confirmation after checkout; that is conclusive sold
        # evidence even when the sold sticker is not present in the hydrated
        # body text.
        if re.search(
            r"売り切れ|売約済み|ご売約済み|この商品は[\s\S]{0,80}配送されました|"
            r"sold\s*out\b|\bsold\b",
            lowered,
            re.I,
        ):
            return "sold_out_badge"
        return ""

    if platform == "aucfan":
        # Aucfan mixes current listings and historical price data.  Reserve
        # prices (最低落札価格) are not a winning-bid result, so remove that
        # phrase before checking for an actual sold amount/date.
        auction_text = re.sub(r"最低落札(?:価格|額)", " ", lowered)
        if re.search(
            r"落札(?:日|額|価格)|(?<!最低)落札(?:\s|$|[0-9])|"
            r"落札者あり|winning\s*(?:bid|price)|auction\s*result",
            auction_text,
            re.I,
        ):
            return "aucfan_winning_bid"
        return ""

    if platform == "mandarake":
        # Mandarake's ordinary catalogue is a retail stock surface.  Only
        # accept explicit auction-winner wording when an auction result is
        # actually rendered.
        auction_text = re.sub(r"最低落札(?:価格|額)", " ", lowered)
        if re.search(
            r"落札(?:日|額|価格)|(?<!最低)落札(?:\s|$|[0-9])|"
            r"落札者あり|winning\s*(?:bid|price)|auction\s*result",
            auction_text,
            re.I,
        ):
            return "mandarake_winning_bid"
        return ""

    if platform == "ebay":
        # eBay distinguishes a completed/ended listing from one that sold;
        # the URL filter requests both, but the card still needs its Sold
        # marker to prevent ended-without-sale items from being imported.
        if re.search(r"\bsold\b", lowered, re.I):
            return "ebay_sold_label"
        return ""
    return ""


def is_active_auction_text(text: str, platform: str) -> bool:
    lowered = normalize_search_text(text)
    # These marketplaces expose fixed-price listings.  Their detail pages can
    # contain generic countdown/stock words from recommendations, footers, or
    # delivery copy; those words must not turn a fixed-price item into an
    # auction and suppress its final sold-price extraction.
    if platform in {
        "mercari-jp",
        "rakuma",
        "yahoo-furima-jp",
        "surugaya",
        "rakuten",
        "tcgplayer",
        "ruten-tw",
        "shopee-tw",
        "bunjang-kr",
        "naver-shopping-kr",
        "karrot-kr",
    }:
        return False
    if platform in {"yahoo-auctions-jp", "aucfan", "mandarake"}:
        return bool(re.search(r"現在価格|入札|即決|残り|終了予定|auction|bid|time\s+left|ends?", lowered, re.I))
    return bool(re.search(r"auction|bid|入札|現在価格|残り|終了予定|time\s+left|ends?", lowered, re.I))


def active_evidence(text: str, platform: str, title: str = "") -> str:
    """Return evidence that a rendered row is still purchasable/listed."""
    lowered = normalize_search_text(text)
    normalized_title = normalize_search_text(title)
    if normalized_title:
        lowered = lowered.replace(normalized_title, " ")
    if sold_evidence(text, platform, title):
        return ""
    if is_active_auction_text(lowered, platform):
        return "auction_active"
    if re.search(
        r"販売中|出品中|在庫あり|購入手続き|カートに入れる|買い物かご|available|in\s+stock|buy\s+now|add\s+to\s+cart|for\s+sale",
        lowered,
        re.I,
    ):
        return "active_available"
    # Mercari/Rakuma/Furima active searches are explicitly scoped by their
    # URL status filter; a priced result without a sold marker is therefore a
    # valid active row even when the card hides its stock label.
    if platform in {
        "mercari-jp", "rakuma", "yahoo-auctions-jp", "yahoo-furima-jp", "aucfan",
        "surugaya", "rakuten", "mandarake", "tcgplayer", "ebay",
        "ruten-tw", "shopee-tw", "bunjang-kr", "naver-shopping-kr", "karrot-kr",
    }:
        return "active_search_result"
    return ""


def inactive_listing_evidence(text: str, platform: str, title: str = "") -> str:
    """Return a marker that proves a result is no longer purchasable."""
    lowered = normalize_search_text(text)
    normalized_title = normalize_search_text(title)
    if normalized_title:
        lowered = lowered.replace(normalized_title, " ")
    if re.search(
        r"売り切れ|売約済み|取引完了|出品終了|掲載終了|販売終了|在庫切れ|在庫なし|完売|"
        r"sold\s*out\b|\bsold\b|out\s+of\s+stock|no\s+longer\s+available|"
        r"\bauction\s+ended\b|\bended\b|\bclosed\b|"
        r"已售完|售罄|完售|已下架|下架|商品已停售|缺貨|無庫存|"
        r"판매\s*(?:완료|종료)|거래\s*(?:완료|종료)|품절|판매\s*중지|판매중지",
        lowered,
        re.I,
    ):
        return "inactive_status"
    # Yahoo/auction cards use a bare 終了 label for a closed lot, while an
    # auction that is still live uses 終了予定/終了日時. Do not reject those
    # published deadline labels.
    if platform in {"yahoo-auctions-jp", "aucfan", "mandarake"} and re.search(
        r"未落札|落札(?:者)?(?:なし|無し)|入札者?(?:なし|無し)|"
        r"(?<!予定)(?<!日時)(?<!日)終了(?:\s|$|[：:])", lowered
    ):
        if re.search(r"未落札|落札(?:者)?(?:なし|無し)|入札者?(?:なし|無し)", lowered):
            return "auction_ended_without_winner"
        return "auction_ended"
    return ""


def extract_auction_end_date(body: str, source_timezone: str = "UTC") -> str | None:
    """Extract a published auction end timestamp when the marketplace shows one."""
    body = html.unescape(str(body or "")).replace("\xa0", " ")
    label = r"(?:オークション)?(?:終了予定|終了日時|終了日|終了時刻|終了)"
    japanese_pattern = (
        rf"{label}\s*[：:]?\s*[\s\S]{{0,80}}?"
        r"(20\d{2})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日"
        r"(?:\s*[（(][^）)]*[）)])?(?:\s*(\d{1,2})\s*(?:[:：]|時)\s*(\d{1,2})\s*分?)?"
    )
    match = re.search(japanese_pattern, body, re.I)
    if match:
        year, month, day, hour, minute = match.groups()
        return format_source_datetime(int(year), int(month), int(day), int(hour or 0), int(minute or 0), source_timezone)
    numeric_pattern = (
        rf"(?:{label}|auction\s+ends?|ends?)\s*[：:]?\s*[\s\S]{{0,80}}?"
        r"(20\d{2})[/-](\d{1,2})[/-](\d{1,2})(?:[T\s]+(\d{1,2}):(\d{2}))?"
    )
    match = re.search(numeric_pattern, body, re.I)
    if match:
        year, month, day, hour, minute = match.groups()
        return format_source_datetime(int(year), int(month), int(day), int(hour or 0), int(minute or 0), source_timezone)
    english_pattern = (
        r"(?:auction\s+ends?|ends?)\s*(?:on\s+)?"
        r"([A-Z][a-z]{2,8})\s+(\d{1,2}),\s*(20\d{2})"
        r"(?:\s+(?:at\s+)?(\d{1,2}):(\d{2})\s*(AM|PM)?)?"
    )
    match = re.search(english_pattern, body, re.I)
    if match:
        month_name, day, year, hour, minute, meridiem = match.groups()
        try:
            month = datetime.strptime(month_name[:3], "%b").month
        except ValueError:
            month = 0
        if month:
            parsed_hour = int(hour or 0)
            if meridiem and meridiem.lower() == "pm" and parsed_hour < 12:
                parsed_hour += 12
            if meridiem and meridiem.lower() == "am" and parsed_hour == 12:
                parsed_hour = 0
            return format_source_datetime(int(year), month, int(day), parsed_hour, int(minute or 0), source_timezone)

    # Yahoo often omits the year on active-result cards, for example
    # ``終了日時 8/18 21:30`` or ``8/18 21:30終了``. Resolve that short form
    # against the next plausible occurrence in the marketplace timezone.
    short_labeled_patterns = (
        rf"{label}\s*[：:]?\s*[\s\S]{{0,80}}?"
        r"(\d{1,2})\s*月\s*(\d{1,2})\s*日(?:\s*[（(][^）)]*[）)])?"
        r"(?:\s*(\d{1,2})\s*(?:[:：]|時)\s*(\d{1,2})\s*分?)?",
        rf"(?:{label}|auction\s+ends?|ends?)\s*[：:]?\s*[\s\S]{{0,80}}?"
        r"(\d{1,2})[/-](\d{1,2})(?:\s*\([^)]*\))?\s+(\d{1,2}):(\d{2})",
    )
    for pattern in short_labeled_patterns:
        match = re.search(pattern, body, re.I)
        if match:
            month, day, hour, minute = match.groups()
            return format_inferred_source_datetime(
                int(month), int(day), int(hour or 0), int(minute or 0), source_timezone
            )

    short_suffix_patterns = (
        r"(\d{1,2})\s*月\s*(\d{1,2})\s*日"
        r"(?:\s*[（(][^）)]*[）)])?"
        r"\s*(\d{1,2})\s*(?:[:：]|時)\s*(\d{1,2})\s*分?"
        r"\s*(?:終了予定|終了|end)",
        r"(\d{1,2})[/-](\d{1,2})(?:\s*\([^)]*\))?\s+(\d{1,2}):(\d{2})\s*(?:終了|end)",
    )
    for pattern in short_suffix_patterns:
        match = re.search(pattern, body, re.I)
        if match:
            month, day, hour, minute = match.groups()
            return format_inferred_source_datetime(
                int(month), int(day), int(hour or 0), int(minute or 0), source_timezone
            )

    # Auction cards often publish only a relative clock (for example
    # ``残り1日 3時間`` or ``2h 15m left``). Preserve that countdown as an
    # approximate UTC end instant so the active-auction bot can still notify
    # with a useful deadline. Absolute dates above always take precedence.
    relative_patterns = (
        r"(?:残り|あと)\s*(?:(\d+)\s*日)?\s*(?:(\d+)\s*(?:時間|時))?\s*(?:(\d+)\s*分)?\s*(?:(\d+)\s*秒)?",
        r"(?:(\d+)\s*d(?:ays?)?)?\s*(?:(\d+)\s*h(?:ours?)?)?\s*(?:(\d+)\s*m(?:in(?:utes?)?)?)?\s*(?:(\d+)\s*s(?:ec(?:onds?)?)?)?\s*(?:left|remaining|to\s*go)",
        # Yahoo Auctions active cards commonly render the remaining time as
        # an unlabeled value after the bid/watch count, for example
        # ``現在 12,988円 ... 0 3日`` or ``現在 299円 ... 0 9分15秒``.
        r"(?:現在(?:価格)?|即決|入札|ウォッチ)[\s\S]{0,400}?\b\d+\s+"
        r"(?:(\d+)\s*日)?\s*(?:(\d+)\s*(?:時間|時))?\s*"
        r"(?:(\d+)\s*分)?\s*(?:(\d+)\s*秒)?",
    )
    for pattern in relative_patterns:
        match = re.search(pattern, body, re.I)
        if not match or not any(match.groups()):
            continue
        days, hours, minutes, seconds = (int(value or 0) for value in match.groups())
        if days == 0 and hours == 0 and minutes == 0 and seconds == 0:
            continue
        now_local = datetime.now(source_timezone_value(source_timezone))
        approximate_end = now_local + timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
        return approximate_end.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    return None


def extract_auction_end_date_from_page(
    page, body: str, source_timezone: str = "UTC"
) -> str | None:
    """Read an auction deadline from visible text or labeled page JSON."""
    visible_end = extract_auction_end_date(body, source_timezone)
    if visible_end:
        return visible_end
    if page is None:
        return None
    embedded_sources = []
    try:
        scripts = page.locator("script")
        for index in range(min(scripts.count(), 100)):
            embedded_sources.append(str(scripts.nth(index).inner_text() or ""))
    except Exception:
        pass
    field_pattern = re.compile(
        r'''["'](?:auctionEndTime|auctionEndsAt|endTime|endAt|endDate|closingTime)["']\s*:\s*(?:["']([^"']+)["']|(\d{10,13}))''',
        re.I,
    )
    for source in embedded_sources:
        for match in field_pattern.finditer(source):
            value = match.group(1) or match.group(2)
            normalized = normalize_date(value, source_timezone=source_timezone)
            if normalized:
                return normalized
    return None


def format_inferred_source_datetime(
    month: int, day: int, hour: int, minute: int, source_timezone: str
) -> str | None:
    """Resolve a month/day auction deadline without a published year."""
    zone = source_timezone_value(source_timezone)
    now_local = datetime.now(zone)
    year = now_local.year
    try:
        candidate = datetime(year, month, day, hour, minute, tzinfo=zone)
    except ValueError:
        return None
    if candidate < now_local - timedelta(days=1):
        try:
            candidate = candidate.replace(year=year + 1)
        except ValueError:
            return None
    return candidate.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def marketplace_price_type(
    platform: str, status_evidence: str, text: str, title: str = ""
) -> str:
    """Classify the completed price without assuming every site is auctioned."""
    if platform in {"yahoo-auctions-jp", "jdirectmarket", "aucfan"}:
        return "auction_hammer"
    if platform == "mandarake" and status_evidence == "mandarake_winning_bid":
        return "auction_hammer"
    normalized_text = normalize_search_text(text)
    normalized_title = normalize_search_text(title)
    if normalized_title:
        normalized_text = normalized_text.replace(normalized_title, " ")
    if platform == "ebay" and re.search(r"auction|bid|bids|入札", normalized_text, re.I):
        return "auction_hammer"
    return "fixed_price_sold"


# Compatibility for callers and tests that still use the pre-rename helper.
collect_jdirect_completed_items = collect_yahoo_completed_items


def parse_request_bound(value: str | None, field_name: str) -> datetime | None:
    if value in (None, ""):
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field_name} must be an ISO-8601 timestamp") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def active_listing_date_in_range(
    active_at: str | None,
    from_bound: datetime | None,
    to_bound: datetime | None,
) -> bool:
    """Check an active-card timestamp without rejecting undated cards."""
    if not active_at or (from_bound is None and to_bound is None):
        return True
    try:
        parsed = datetime.fromisoformat(str(active_at).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return True
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    parsed = parsed.astimezone(timezone.utc)
    if from_bound and parsed < from_bound:
        return False
    if to_bound and parsed > to_bound:
        return False
    return True


def title_matches_query(title: str, query: str) -> bool:
    """Require every release/person phrase to survive in the title.

    Yahoo's closed-search page can broaden multi-term queries. The worker is
    a price-history importer, so precision is more important than accepting a
    related model-name result that omits the requested release. Numbered
    JUICY/CJ queries intentionally use an unquoted volume token because Yahoo
    returns no cards for the punctuation-heavy ``Vol. N`` phrase.
    """
    normalized_title = normalize_search_text(title)
    compact_title = compact_search_text(title)
    all_quoted = [normalize_search_text(value) for value in re.findall(r'"([^"]+)"', query)]
    # Marketplace-specific discovery hints improve search recall but are not
    # required to be printed in the listing title (for example, Mercari often
    # omits the Japanese ``トレカ`` category word). Keep the series, release,
    # and person phrases strict while ignoring those generic hints.
    quoted = [
        value
        for value in all_quoted
        if value and not is_generic_query_hint(value) and not is_series_query_hint(value)
    ]
    if quoted and not all(
        quoted_query_phrase_matches(normalized_title, compact_title, value)
        for value in quoted
    ):
        return False

    # Only numeric tokens outside quoted phrases are release constraints.
    # This avoids treating years or numbers embedded in a quoted card title as
    # a volume while still rejecting e.g. Vol. 29 for a requested Vol. 9.
    unquoted_numbers = []
    for match in re.finditer(r'"[^"]*"|(?<!\w)(\d{1,3})(?!\w)', query):
        if match.group(1):
            unquoted_numbers.append(match.group(1))
    if any(not title_matches_release_number(normalized_title, number) for number in unquoted_numbers):
        return False

    if quoted or unquoted_numbers:
        return True
    series_hints = [value for value in all_quoted if is_series_query_hint(value)]
    if series_hints:
        return any(series_query_hint_matches(normalized_title, value) for value in series_hints)
    normalized_query = normalize_search_text(query)
    return bool(normalized_query) and (
        normalized_query in normalized_title
        or compact_search_text(normalized_query) in compact_title
    )


def title_matches_active_model(title: str, query: str, aliases: list[str] | None = None) -> bool:
    """Match the series query or any canonical/Japanese model alias."""
    if query and (title_matches_query(title, query) or mercari_title_matches_series(title, query)):
        return True
    # The default active searches are deliberately broad, just like the sold
    # searches. A marketplace can surface a valid card whose title contains
    # only the model or release code, so the rendered series search is the
    # authority when no model-specific alias filter was requested.
    if not aliases and is_broad_active_series_query(query):
        return True
    return any(alias and title_matches_query(title, alias) for alias in (aliases or []))


def active_listing_has_non_card_category(title: str, text: str = "") -> bool:
    """Return true for inventory categories outside this card archive."""
    haystack = "\n".join(value for value in (title, text) if value)
    if ACTIVE_NON_CARD_RE.search(haystack) and not ACTIVE_COLLECTIBLE_RE.search(haystack):
        return True
    return bool(ACTIVE_APPAREL_RE.search(haystack)) and not ACTIVE_COLLECTIBLE_RE.search(haystack)


def active_listing_is_relevant(
    title: str,
    text: str,
    query: str = "",
    aliases: list[str] | None = None,
) -> bool:
    """Require the item title itself to prove series and card relevance.

    ``text`` is still useful for marketplace status and price extraction, but
    it can contain result-page/card chrome (including the broad search label).
    Letting that text satisfy the identity or collectible checks causes an
    unrelated product to inherit the active query's series.
    """
    normalized_title = normalize_search_text(title)
    if not normalized_title:
        return False
    if query and is_hits_series_query(query) and not hits_listing_has_card_context(title):
        return False
    if query and not title_matches_active_model(title, query, aliases):
        return False
    if active_listing_has_non_card_category(title):
        return False
    return bool(ACTIVE_CARD_SIGNAL_RE.search(title))


def is_broad_active_series_query(query: str) -> bool:
    normalized = normalize_search_text(query)
    return normalized in {
        "woohoo",
        "juicy honey",
        "cj sexy",
        "hits",
        "hit's",
        "ヒッツ",
    }


def is_hits_series_query(query: str) -> bool:
    return bool(HITS_SERIES_RE.search(normalize_search_text(query)))


def hits_listing_has_card_context(title: str, text: str = "") -> bool:
    """Require HITS branding and card-specific context for broad HITS searches."""
    normalized_title = normalize_search_text(title)
    if not HITS_SERIES_RE.search(normalized_title):
        return False
    normalized_text = normalize_search_text("\n".join(value for value in (title, text) if value))
    if not HITS_EXPLICIT_BRAND_RE.search(normalized_title) and not HITS_SPECIFIC_CARD_CONTEXT_RE.search(
        normalized_text
    ):
        return False
    if HITS_NON_CARD_TITLE_RE.search(normalized_title):
        return False
    if HITS_FOREIGN_CARD_RE.search(normalized_title):
        return False
    if HITS_CARD_ACCESSORY_RE.search(normalized_title) or (
        HITS_NON_CARD_RE.search(normalized_title) and not HITS_CARD_CONTEXT_RE.search(normalized_title)
    ):
        return False
    return bool(HITS_CARD_CONTEXT_RE.search(normalized_text))


def mercari_title_matches_series(title: str, query: str) -> bool:
    """Match one of the enabled default series without requiring DB aliases."""
    # A precise card_set query may identify the release/person even when a
    # seller omits the series name from the title. Preserve that strict match
    # before falling back to the default series spelling.
    precise_query = mercari_query_has_explicit_constraints(query)
    if precise_query:
        return title_matches_query(title, query)
    normalized_query = normalize_search_text(query)
    normalized_title = normalize_search_text(title)
    if any(term in normalized_query for term in ("juicy honey", "ジューシーハニー")):
        return bool(re.search(r"juicy\s*honey|ジューシーハニー", normalized_title, re.I))
    if any(term in normalized_query for term in (
        "cj sexy", "cj sexy card", "cj トレカ", "cj オフィシャルカードコレクション",
    )):
        return bool(re.search(
            r"\bcj[\s-]*(?:sexy|\d{2,3})\b|\bcj\b(?=.{0,80}(?:card|cards|collection|カード|トレカ))|ジュートク|jyutoku|"
            r"cj\s*(?:card|series)",
            normalized_title,
            re.I,
        ))
    if any(term in normalized_query for term in (
        "woohoo", "woohoo girls", "woohoo トレーディングカード", "ウーフーガールズ",
    )):
        return bool(re.search(r"\bwoohoo(?:\s+girls)?\b|ウーフー", normalized_title, re.I))
    if any(term in normalized_query for term in ("hits", "hit's", "hits limited", "ヒッツ")):
        return hits_listing_has_card_context(title)
    return title_matches_query(title, query)


def mercari_query_has_explicit_constraints(query: str) -> bool:
    """Whether a query carries release/person constraints beyond a series word."""
    return bool(re.search(r'"[^"]+"|(?<!\w)\d{1,3}(?!\w)', query or ""))


def is_generic_query_hint(value: str) -> bool:
    return normalize_search_text(value) in {
        "card",
        "cards",
        "trading card",
        "trading cards",
        "トレカ",
        "トレーディングカード",
        "交易卡",
        "收藏卡",
        "集換式卡牌",
        "卡牌",
        "卡片",
        "트레이딩 카드",
        "컬렉션 카드",
        "포토카드",
        "포카",
        "카드",
    }


def is_series_query_hint(value: str) -> bool:
    return normalize_search_text(value) in {
        "woohoo girls",
        "woohoo girls series",
        "woohoo トレーディングカード",
        "ウーフーガールズ",
        "cj sexy",
        "cj sexy card",
        "cj sexy card series",
        "cj トレカ",
        "cj オフィシャルカードコレクション",
        "juicy honey",
        "ジューシーハニー",
        "hits",
        "hit's",
        "hits limited",
        "ヒッツ",
    }


def series_query_hint_matches(normalized_title: str, value: str) -> bool:
    hint = normalize_search_text(value)
    if "juicy honey" in hint or "ジューシーハニー" in hint:
        return "juicy honey" in normalized_title or "ジューシーハニー" in normalized_title
    if "cj sexy" in hint or hint.startswith("cj "):
        return "cj sexy" in normalized_title or "ジュートク" in normalized_title
    if "woohoo" in hint or "ウーフー" in hint:
        return "woohoo" in normalized_title or "ウーフー" in normalized_title
    if "hits" in hint or "ヒッツ" in hint:
        return bool(re.search(r"\bhit['’]?s(?:\s*limited)?\b|ヒッツ", normalized_title, re.I))
    return hint in normalized_title


def quoted_query_phrase_matches(
    normalized_title: str, compact_title: str, phrase: str
) -> bool:
    volume_match = re.search(r"(?:\bvol(?:ume)?\s*\.?|#)\s*0*(\d{1,3})\b", phrase, re.I)
    if volume_match:
        return title_matches_release_number(normalized_title, volume_match.group(1))
    return phrase in normalized_title or compact_search_text(phrase) in compact_title


def title_matches_release_number(normalized_title: str, number: str) -> bool:
    """Match a volume marker without confusing Vol. 9 with Vol. 29."""
    number = str(int(number))
    escaped = re.escape(number)
    patterns = (
        rf"\bvol(?:ume)?\s*\.?\s*0*{escaped}\b",
        rf"#\s*0*{escaped}\b",
        rf"\b(?:card\s+series|juicy\s+honey(?:\s+collection\s+cards?)?|cj\s+sexy)\s*0*{escaped}\b",
    )
    return any(re.search(pattern, normalized_title, re.I) for pattern in patterns)


def normalize_search_text(value: str) -> str:
    # Normalize full-width Latin spellings such as ＨＩＴ'Ｓ, while retaining
    # the Japanese wave-dash used in release subtitles as visible punctuation.
    value = html.unescape(value or "").replace("～", "\ue000")
    value = unicodedata.normalize("NFKC", value).replace("\ue000", "～").lower()
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def compact_search_text(value: str) -> str:
    return "".join(character for character in normalize_search_text(value) if character.isalnum())


def build_diagnostic_warnings(
    platform: str,
    candidate_count: int,
    sold_candidate_count: int,
    rejection_counts: dict[str, int],
) -> list[str]:
    warnings = [
        f"rendered candidates: {candidate_count}",
        f"sold candidates: {sold_candidate_count}",
    ]
    for reason, count in sorted(rejection_counts.items()):
        warnings.append(f"{reason}: {count}")
    return warnings


def extract_title(page) -> str:
    for selector in ("h1", "meta[property='og:title']"):
        locator = page.locator(selector).first
        if locator.count() == 0:
            continue
        if selector.startswith("meta"):
            value = locator.get_attribute("content")
        else:
            value = locator.inner_text()
        if value:
            return value.strip()
    return ""


def extract_image(page) -> str:
    if page is None:
        return ""
    for selector in (
        "meta[property='og:image']",
        "meta[name='twitter:image']",
    ):
        try:
            locator = page.locator(selector).first
            if locator.count() > 0:
                image = first_usable_image_reference(locator.get_attribute("content"))
                if image:
                    return image
        except Exception:
            continue

    # Rakuma publishes the same product image in JSON-LD even on detail
    # revisions where the social meta tag is absent.
    try:
        structured = extract_structured_product(page)
        image = structured.get("image") if isinstance(structured, dict) else ""
        image = first_usable_image_reference(image)
        if image:
            return image
    except Exception:
        pass

    # Last-resort DOM fallback for pages that omit both metadata surfaces.
    for selector in (
        "main img",
        "[class*='item-slider'] img",
        "img[src*='img.fril.jp']",
    ):
        try:
            images = page.locator(selector)
            for index in range(images.count()):
                image = images.nth(index)
                candidate = first_usable_image_reference(
                    image.get_attribute("data-original"),
                    image.get_attribute("data-original-src"),
                    image.get_attribute("data-src"),
                    image.get_attribute("data-lazy-src"),
                    image.get_attribute("src"),
                )
                if candidate:
                    return candidate
        except Exception:
            continue
    return ""


def extract_structured_product(page) -> dict:
    scripts = page.locator("script[type='application/ld+json']")
    for index in range(scripts.count()):
        try:
            payload = json.loads(scripts.nth(index).inner_text())
        except (json.JSONDecodeError, TypeError):
            continue
        values = payload if isinstance(payload, list) else [payload]
        # Doorzo and Mercari wrap Product in a schema.org @graph. The previous
        # reader inspected only the wrapper and silently lost the exact JPY
        # price, availability, image, and item description.
        expanded = []
        for value in values:
            expanded.append(value)
            if isinstance(value, dict) and isinstance(value.get("@graph"), list):
                expanded.extend(value["@graph"])
        for value in expanded:
            if not isinstance(value, dict):
                continue
            offers = value.get("offers") or {}
            if isinstance(offers, list):
                offers = offers[0] if offers else {}
            if not isinstance(offers, dict):
                offers = {}
            if value.get("@type") == "Product" or offers:
                return {
                    "name": value.get("name", ""),
                    "description": value.get("description", ""),
                    "sku": value.get("sku") or value.get("productID") or "",
                    "image": value.get("image", ""),
                    "price": offers.get("price"),
                    "currency": offers.get("priceCurrency", ""),
                    "availability": offers.get("availability", ""),
                }
    return {}


def extract_yahoo_active_prices(text: str) -> tuple[float | None, float | None]:
    """Read Yahoo active-auction current and buy-now prices by their labels.

    Search cards can show the starting bid before the current bid.  Returning
    only labelled values prevents that starting amount from being persisted as
    the current price.
    """
    value = html.unescape(text or "").replace("\xa0", " ")
    amount = r"(?:JPY\s*|¥\s*|￥\s*)?([0-9][0-9,]*(?:\.\d{1,2})?)\s*(?:円|JPY)?"

    def find_price(labels: str) -> float | None:
        match = re.search(
            rf"(?:{labels})\s*[:：]?\s*{amount}", value, re.I
        )
        if not match:
            return None
        try:
            return float(match.group(1).replace(",", ""))
        except ValueError:
            return None

    current = find_price(
        r"現在価格|現在|current\s*price|current\s*bid|current"
    )
    buy_now = find_price(r"即決価格|即決|buy\s*now|buy-now")
    return current, buy_now


def extract_price(
    page, body: str, platform: str, structured: dict | None = None
) -> tuple[float | None, str]:
    if platform in {"ruten-tw", "shopee-tw"}:
        currency = "TWD"
    elif platform in {"bunjang-kr", "naver-shopping-kr", "karrot-kr"}:
        currency = "KRW"
    elif platform in {
        "aucfan", "mercari", "mercari-jp", "rakuma", "surugaya", "mandarake",
        "rakuten", "jdirectmarket", "yahoo-furima-jp"
    }:
        currency = "JPY"
    else:
        currency = "USD"
    structured = structured or {}
    structured_price = structured.get("price")
    if structured_price not in (None, ""):
        try:
            return float(str(structured_price).replace(",", "")), (
                structured.get("currency") or currency
            )
        except ValueError:
            pass
    match = re.search(
        # Yen/won are commonly written as a suffix, while TWD and USD often
        # use a prefix. Keep the regional platform's known currency when a
        # generic dollar sign is rendered without an ISO code.
        r"(?:NT\$|NTD|US\$|KRW|JPY|¥|￥|₩|\$)\s*([0-9][0-9,]*(?:\.\d{1,2})?)",
        body,
        re.I,
    )
    if match:
        value = float(match.group(1).replace(",", ""))
        price_marker = match.group(0).lower()
        if platform in {"ruten-tw", "shopee-tw", "bunjang-kr", "naver-shopping-kr", "karrot-kr"}:
            return value, currency
        if any(marker in price_marker for marker in ("jpy", "¥", "￥", "円")):
            return value, "JPY"
        return value, "USD"
    suffix_match = re.search(r"([0-9][0-9,]*(?:\.\d{1,2})?)\s*(?:円|원|台幣|新台幣)", body)
    if suffix_match:
        return float(suffix_match.group(1).replace(",", "")), currency if platform in {
            "ruten-tw", "shopee-tw", "bunjang-kr", "naver-shopping-kr", "karrot-kr"
        } else "JPY"
    return None, currency


def extract_mercari_update_time(page, body: str) -> str | None:
    """Read Mercari's public listing update timestamp.

    Depending on the page revision, Mercari exposes this as a labeled
    ``更新日時`` value, a ``time[datetime]`` element, or an ``updateTime`` /
    ``updatedAt`` field inside the hydrated page JSON. The timestamp is a
    listing-update signal, not a claim that the exact checkout moment is
    public; callers record that distinction in ``soldAtEvidence``.
    """
    embedded_sources = [str(body or "")]
    try:
        scripts = page.locator("script") if page is not None else None
        if scripts is not None:
            for index in range(scripts.count()):
                embedded_sources.append(scripts.nth(index).inner_text() or "")
    except Exception:
        pass
    try:
        content = page.content() if page is not None else ""
        if content:
            embedded_sources.append(content)
    except Exception:
        pass
    for source in embedded_sources:
        match = re.search(
            r"[\"'](?:updateTime|updatedAt|updated|update_time|updated_time|lastUpdatedAt)[\"']\s*:\s*"
            r"(?:[\"']([^\"']+)[\"']|(\d{10,13}))",
            source,
            re.I,
        )
        if match:
            parsed = normalize_date(match.group(1) or match.group(2), source_timezone="Asia/Tokyo")
            if parsed:
                return parsed
    labeled = extract_sold_date(
        page, body, require_label=True, source_timezone="Asia/Tokyo"
    )
    if labeled:
        return labeled
    # On a Mercari item detail page the first datetime element is the listing
    # update time when no visible label is present. Search cards are handled by
    # the explicit updateTime field and never reach this fallback.
    if page is not None:
        try:
            times = page.locator("time[datetime]")
            for index in range(times.count()):
                parsed = normalize_date(
                    times.nth(index).get_attribute("datetime"),
                    source_timezone="Asia/Tokyo",
                )
                if parsed:
                    return parsed
        except Exception:
            pass
    return None


def extract_sold_date(
    page,
    body: str,
    require_label: bool = False,
    source_timezone: str = "UTC",
) -> str | None:
    if page is not None and not require_label:
        locator = page.locator("time[datetime]").first
        if locator.count() > 0:
            value = locator.get_attribute("datetime")
            parsed = normalize_date(value)
            if parsed:
                return parsed
    english_match = re.search(
        r"\b(?:sold|ended)\s+(?:on\s+)?"
        r"([A-Z][a-z]{2,8})\s+(\d{1,2}),\s+(20\d{2})"
        r"(?:\s+(?:at\s+)?(\d{1,2}):(\d{2})\s*(AM|PM)?)?",
        body,
        re.I,
    )
    if english_match:
        month_name, day, year, hour, minute, meridiem = english_match.groups()
        try:
            month = datetime.strptime(month_name[:3], "%b").month
        except ValueError:
            month = 0
        if month:
            parsed_hour = int(hour or 0)
            if meridiem:
                if meridiem.lower() == "pm" and parsed_hour < 12:
                    parsed_hour += 12
                elif meridiem.lower() == "am" and parsed_hour == 12:
                    parsed_hour = 0
            return format_source_datetime(
                int(year), month, int(day), parsed_hour, int(minute or 0), source_timezone
            )
    japanese_pattern = (
        r"(?:落札(?:日|日時)|終了(?:日|日時)|取引完了(?:日|日時)|"
        r"購入(?:日|日時)|売却(?:日|日時)|販売完了(?:日|日時)|"
        r"更新(?:日|日時)|最終更新(?:日|日時)|"
        r"sold\s+(?:on|at)|ended\s+(?:on|at))"
        r"[^\n]{0,40}?"
        if require_label
        else ""
    ) + r"(20\d{2})年(\d{1,2})月(\d{1,2})日(?:\s*(\d{1,2}):(\d{2}))?"
    japanese_match = re.search(japanese_pattern, body, re.I)
    if japanese_match:
        year, month, day, hour, minute = japanese_match.groups()
        return format_source_datetime(
            int(year), int(month), int(day), int(hour or 0), int(minute or 0), source_timezone
        )
    numeric_pattern = (
        r"(?:落札(?:日|日時)|終了(?:日|日時)|取引完了(?:日|日時)|"
        r"購入(?:日|日時)|売却(?:日|日時)|販売完了(?:日|日時)|"
        r"更新(?:日|日時)|最終更新(?:日|日時)|"
        r"sold\s+(?:on|at)|ended\s+(?:on|at))"
        r"[^\n]{0,40}?"
        if require_label
        else ""
    ) + r"(20\d{2})[/-](\d{1,2})[/-](\d{1,2})(?:\s+(\d{1,2}):(\d{2}))?"
    match = re.search(numeric_pattern, body, re.I)
    if not match:
        return None
    year, month, day, hour, minute = match.groups()
    return format_source_datetime(
        int(year), int(month), int(day), int(hour or 0), int(minute or 0), source_timezone
    )


def format_source_datetime(
    year: int, month: int, day: int, hour: int, minute: int, source_timezone: str
) -> str:
    """Convert a marketplace-local date into the UTC value stored in the DB."""
    local_value = datetime(
        year,
        month,
        day,
        hour,
        minute,
        tzinfo=source_timezone_value(source_timezone),
    )
    return local_value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def normalize_date(value: str | int | float | None, source_timezone: str = "UTC") -> str | None:
    """Normalize ISO, date-only, and Unix-second/millisecond timestamps to UTC."""
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)) or (
        isinstance(value, str) and re.fullmatch(r"\d{10,13}", value.strip())
    ):
        try:
            numeric = float(value)
            if numeric > 100_000_000_000:
                numeric /= 1000
            return datetime.fromtimestamp(numeric, tz=timezone.utc).isoformat().replace(
                "+00:00", "Z"
            )
        except (TypeError, ValueError, OverflowError, OSError):
            return None
    raw = str(value).strip()
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        try:
            parsed = datetime.strptime(raw, "%Y-%m-%d").replace(
                tzinfo=source_timezone_value(source_timezone)
            )
        except ValueError:
            return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=source_timezone_value(source_timezone))
    return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def extract_external_id(link: str) -> str:
    source_link = unwrap_doorzo_url(link)
    parts = [part for part in source_link.rstrip("/").split("/") if part]
    return parts[-1] if parts else source_link


def extract_marketplace_external_id(link: str, platform: str) -> str:
    parsed = urlparse(unwrap_doorzo_url(link))
    path_parts = [part for part in parsed.path.rstrip("/").split("/") if part]
    if platform == "ebay" and "itm" in path_parts:
        index = path_parts.index("itm")
        if index + 1 < len(path_parts):
            return path_parts[index + 1]
    if platform == "tcgplayer" and "product" in path_parts:
        index = path_parts.index("product")
        if index + 1 < len(path_parts):
            return path_parts[index + 1]
    if platform == "mandarake":
        item_code = parse_qs(parsed.query).get("itemCode", [])
        if item_code and item_code[0]:
            return item_code[0]
    return extract_external_id(link)


def unwrap_doorzo_url(link: str) -> str:
    """Return the source marketplace URL embedded in a Doorzo card URL."""
    try:
        parsed_link = urlparse(link)
        values = parse_qs(parsed_link.query).get("url", [])
        target = unquote(values[0]) if values else ""
        if not target:
            parts = [part for part in parsed_link.path.split("/") if part]
            if parts:
                candidate = parts[-1]
                try:
                    decoded = bytes.fromhex(candidate).decode("utf-8")
                    if decoded.startswith("http"):
                        target = decoded
                except (ValueError, UnicodeDecodeError):
                    pass
        if not target:
            return link
        # Doorzo also uses hexadecimal-encoded source URLs in some links.
        if not target.startswith("http"):
            try:
                decoded = bytes.fromhex(target).decode("utf-8")
                if decoded.startswith("http"):
                    target = decoded
            except (ValueError, UnicodeDecodeError):
                pass
        return target if target.startswith("http") else link
    except Exception:
        return link


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
