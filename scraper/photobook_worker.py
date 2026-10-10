"""Browser-only photobook collector used by the MuseBooks regional workers.

The worker reads one JSON request from stdin and writes one normalized batch to
stdout. It deliberately has no marketplace SDKs, API clients, or direct HTTP
request code: every marketplace read is a rendered-page navigation through
CloakBrowser. The Go service is used separately by ``run_api_worker.py`` only
for job leasing and normalized batch ingestion.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import time
import unicodedata
from contextlib import contextmanager, redirect_stdout
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from urllib.parse import urljoin, urlparse

from cloakbrowser import launch
from cover_policy import bookwalker_product_cover, select_cover_url
from digital_storefronts import EXTRA_DIGITAL_SOURCES, MIXED_DIGITAL_SOURCES, selected_book_schema
from marketplace_adapters import (
    AdapterConfigurationError,
    MarketplaceAdapter,
    resolve_adapter,
)


PARSER_VERSION = "python-photobook-browser-v6"
DEFAULT_BROWSER_TIMEOUT_MS = 90_000
MAX_PAGES = 20
MAX_CANDIDATES = 400
MAX_DETAIL_PAGES = 80
DEFAULT_PAGE_SIZE = 40
DEFAULT_MAX_DETAIL_PAGES = 20
MAX_BATCH_ITEMS = 450


class SourceBlockedError(RuntimeError):
    """The rendered page is a challenge/login/access-denied surface."""


class RenderedPageError(RuntimeError):
    """The browser did not produce a usable rendered page."""


class DetailSnapshotError(RuntimeError):
    """A product detail page could not be inspected reliably."""

PHOTBOOK_SIGNAL_RE = re.compile(
    r"(?:\bphoto\s*book\b|\bphotobook\b|\bphotography\s*book\b|"
    r"\bphoto(?:graphic)?\s+(?:essay|monograph|album)\b|"
    r"写真集|フォトブック|寫真集|寫真書|數位寫真|数字写真|數字寫真|攝影集|摄影集|攝影書|摄影书|"
    r"照片集|写真本|写真帖|寫真帖|写真フォトブック|写真画集|(?<!生)写真|寫真|攝影畫冊|摄影画册|"
    r"攝影作品集|摄影作品集|影像集|影像作品集|相冊|相簿|画册|畫冊)",
    re.IGNORECASE,
)
STRONG_PHOTOBOOK_SIGNAL_RE = re.compile(
    r"(?:\bphoto\s*book\b|\bphotobook\b|\bphotography\s*book\b|"
    r"\bphoto(?:graphic)?\s+(?:essay|monograph|album)\b|"
    r"写真集|フォトブック|寫真集|寫真書|數位寫真|数字写真|數字寫真|攝影集|摄影集|攝影書|摄影书|照片集|"
    r"写真本|写真帖|寫真帖|写真フォトブック|写真画集|攝影畫冊|摄影画册|"
    r"攝影作品集|摄影作品集|影像集|影像作品集)",
    re.IGNORECASE,
)
NON_PHOTOBOOK_RE = re.compile(
    r"(?:\b(?:trading\s*card|photo\s*card|photocard|figure|figurine|doll|plush|"
    r"acrylic|keychain|merch|goods|custom\s*album|empty\s*album|"
    r"photo\s*book\s*printing|printing\s*service|voucher)\b|"
    r"トレカ|トレーディングカード|フォトカード|生写真カード|チェキ|"
    r"フィギュア|ぬいぐるみ|アクリル|グッズ|周邊|周辺|寫真卡|照片卡|收藏卡|交易卡|"
    r"相簿內頁|空白相簿|空白相冊|自製相冊|定制相冊|立牌|印刷服務|印刷服务|兌換碼|兑换码)",
    re.IGNORECASE,
)
NON_HUMAN_MODEL_RE = re.compile(
    r"(?:\b(?:car\s+model|aircraft\s+model|vehicle\s+model|scale\s+model|"
    r"model\s+kit|model\s+train|plastic\s+model|model\s+number)\b|"
    r"モデルカー|模型玩具|模型套件|模型車|模型车)",
    re.IGNORECASE,
)
POSTCARD_OR_CARD_RE = re.compile(
    r"(?:\b(?:postcard|poster|calendar|sticker|card|photo\s*card)\b|"
    r"ポストカード|ポスター|カレンダー|カード|海報|日曆|明信片|卡片)",
    re.IGNORECASE,
)
GENERIC_ALBUM_RE = re.compile(r"(?:相冊|相簿|相册|相簿內頁|空白相簿|空白相冊)", re.IGNORECASE)
GENERIC_ARTBOOK_RE = re.compile(r"(?:\bart\s*book\b|artbook|画册|畫冊)", re.IGNORECASE)
BONUS_CARD_RE = re.compile(
    r"(?:"
    r"(?:bonus|with|includes?|including|特典|付録|附贈|附赠|贈品|赠品|付き|付属|附送|含)"
    r".{0,50}(?:postcard|poster|calendar|sticker|card|photo\s*card|"
    r"トレカ|トレーディングカード|寫真卡|照片卡|收藏卡|交易卡|"
    r"ポストカード|ポスター|カレンダー|カード|海報|日曆|明信片|卡片)|"
    r"(?:postcard|poster|calendar|sticker|card|photo\s*card|トレカ|"
    r"トレーディングカード|寫真卡|照片卡|收藏卡|交易卡|ポストカード|ポスター|"
    r"カレンダー|カード|海報|日曆|明信片|卡片).{0,30}(?:bonus|特典|付き|付属|附贈|附赠|贈品|赠品)"
    r")",
    re.IGNORECASE,
)
DIGITAL_RE = re.compile(
    r"(?:\be[- ]?book\b|\bebook\b|\bdigital\b|\bpdf\b|\bepub\b|"
    r"電子書|电子书|電子版|电子版|數碼版|数码版|デジタル写真集|電子写真集|"
    r"다운로드|웹툰|digital\s+edition)",
    re.IGNORECASE,
)
PHYSICAL_RE = re.compile(
    r"(?:\bpaperback\b|\bhardcover\b|\bprinted\b|\bprint\s+copy\b|"
    r"\breal\s+copy\b|\bphysical\b|\bbook\b|紙本|纸本|實體|实体|印刷|"
    r"ハードカバー|ソフトカバー|書籍|本体)",
    re.IGNORECASE,
)
EXPLICIT_PHYSICAL_RE = re.compile(
    r"(?:\b(?:paperback|hardcover|printed|print\s+copy|real\s+copy|physical|paper)\b|"
    r"紙本|纸本|實體|实体|印刷|ハードカバー|ソフトカバー|書籍|本体)",
    re.IGNORECASE,
)
ACTIVE_RE = re.compile(
    r"(?:\bin\s*stock\b|\bcurrently\s+available\b|\bavailable\s+for\s+purchase\b|"
    r"\bavailable\s+now\b|\bavailable\s+to\s+buy\b|\bbuy\s+(?:it\s+)?now\b|"
    r"\badd\s*to\s*cart\b|\bcurrent\s+bid\b|"
    r"\btime\s+left\b|\bends?\s+in\b|\bplace\s+bid\b|"
    r"販売中|出品中|在庫あり|有貨|有货|現貨|现货|立即購買|立即购买|"
    r"可購買|可购买|可下單|可下单|可訂購|可订购|加入購物車|放入購物車|在售|入札受付中|即決)",
    re.IGNORECASE,
)
SOLD_RE = re.compile(
    r"(?:\bbest\s+offer\s+accepted\b|\b(?:this\s+)?(?:item|listing|lot)\s+"
    r"(?:was\s+)?sold\b|\bsold\s+(?:for|at|price)\b|\bwinning\s+bid\b|"
    r"\bauction\s+won\b|\bfinal\s+price\b|\bsold\s+price\b|\bhammer\s+price\b|"
    r"落札(?:価格|金額|済み|者決定|者あり)|成交(?:价|價|价格|價格)|已成交|"
    r"交易完成|交易成功)",
    re.IGNORECASE,
)
ENDED_RE = re.compile(
    r"(?:\bunavailable\b|\bnot\s+available\b|\bout\s+of\s+stock\b|\bsold\s*out\b|"
    r"\bauction\s+ended\b|\bended\b|終了|競標已結束|竞标已结束|已結標|已结标|拍賣結束|拍卖结束|已售|"
    r"售出|售罄|完售|已下架|商品已停售|無貨|无货|缺貨|缺货|無庫存|販売終了|在庫なし)",
    re.IGNORECASE,
)
AUCTION_CURRENT_RE = re.compile(
    r"(?:\bauction\b|\bbid\b|\bcurrent\s+bid\b|入札|最高入札|競標|竞标|出價|出价)",
    re.IGNORECASE,
)
AUCTION_HAMMER_RE = re.compile(
    r"(?:\bhammer\s+price\b|\bwinning\s+bid\b|\bauction\s+won\b|"
    r"落札(?:価格|金額|済み|者決定|者あり)|成交(?:价|價|价格|價格)|已成交|"
    r"交易完成|交易成功)",
    re.IGNORECASE,
)
NEXT_RE = re.compile(
    r"(?:^|\s)(?:next|next\s+page|older|下一頁|下一页|下頁|下页|次へ|次のページ|もっと見る|查看更多)(?:\s|$)",
    re.IGNORECASE,
)
CHALLENGE_MARKERS = (
    "performing security verification",
    "verifies you are not a bot",
    "captcha",
    "recaptcha",
    "verify you are human",
    "verify human",
    "人機驗證",
    "人机验证",
    "請完成驗證",
    "请完成验证",
    "需要验证",
    "アクセスが集中",
    "不正なアクセス",
    "access denied",
    "too many requests",
    "temporarily blocked",
    "rate limit exceeded",
    "unusual traffic",
    "請登入以繼續",
    "请登录以继续",
    "我未滿18歲，禁止進入",
    "露天首頁> 進入成人專區",
)
DETAIL_NOT_FOUND_MARKERS = (
    "お探しのページは見つかりませんでした",
    "page not found",
    "item not found",
    "product not found",
    "商品が見つかりません",
    "商品不存在",
    "商品不存在或已下架",
    "頁面不存在",
    "页面不存在",
)
TAIWAN_DIGITAL_RETAIL_SOURCES = {"bookwalker-tw", "readmoo-tw", "books-com-tw", "pubu-tw", "kobo-tw"} | EXTRA_DIGITAL_SOURCES

VERIFIED_DIGITAL_SOURCES = {
    "bookwalker-jp",
    "bookwalker-tw",
    "readmoo-tw",
    "pubu-tw",
    "kobo-tw",
    "books-com-tw",
    "rakuten-books-jp",
}

CURRENCY_PATTERNS = (
    (re.compile(r"(?:JPY|¥|￥)\s*([0-9][0-9,]*(?:\.\d+)?)", re.IGNORECASE), "JPY"),
    (re.compile(r"([0-9][0-9,]*(?:\.\d+)?)\s*(?:円|JPY)", re.IGNORECASE), "JPY"),
    (re.compile(r"(?:NT\$|TWD)\s*([0-9][0-9,]*(?:\.\d+)?)", re.IGNORECASE), "TWD"),
    (re.compile(r"([0-9][0-9,]*(?:\.\d+)?)\s*(?:元|CNY|RMB)", re.IGNORECASE), "CNY"),
    (re.compile(r"(?:RM|MYR)\s*([0-9][0-9,]*(?:\.\d+)?)", re.IGNORECASE), "MYR"),
    (re.compile(r"(?:US\$|USD|\$)\s*([0-9][0-9,]*(?:\.\d+)?)", re.IGNORECASE), "USD"),
)

JAPAN_SOURCE_IDS = {"yahoo-auctions-jp", "mercari-jp", "rakuma", "rakuma-jp",
                    "yahoo-furima-jp", "surugaya", "surugaya-jp", "mandarake",
                    "mandarake-jp", "rakuten-books-jp", "bookwalker-jp"}


def browser_timeout_ms() -> int:
    raw = os.environ.get("CLOAKBROWSER_LAUNCH_TIMEOUT_MS", "").strip()
    try:
        value = int(raw) if raw else DEFAULT_BROWSER_TIMEOUT_MS
    except ValueError:
        value = DEFAULT_BROWSER_TIMEOUT_MS
    return max(1_000, min(value, 300_000))


@contextmanager
def browser_launch_lock():
    """Serialize Chromium startup when several regional workers share a host."""
    if os.name != "posix":
        yield
        return
    import fcntl

    lock_path = os.environ.get(
        "CLOAKBROWSER_LAUNCH_LOCK_PATH", "/tmp/musebooks-cloakbrowser-launch.lock"
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
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stdin, "reconfigure"):
    sys.stdin.reconfigure(encoding="utf-8", errors="replace")


def compact(value: object, limit: int = 4_000) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    return text[:limit]


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def iso_utc(value: datetime | None = None) -> str:
    return (value or now_utc()).isoformat().replace("+00:00", "Z")


def source_hosts(source: dict) -> set[str]:
    configured = source.get("allowedHosts") or []
    if isinstance(configured, str):
        configured = configured.split(",")
    hosts = {str(item).strip().lower().lstrip(".") for item in configured if str(item).strip()}
    base_url = str(source.get("baseUrl") or "").strip()
    if base_url:
        hostname = urlparse(base_url).hostname
        if hostname:
            hosts.add(hostname.lower())
    return hosts


def is_allowed_url(value: str, hosts: set[str]) -> bool:
    parsed = urlparse(value)
    hostname = (parsed.hostname or "").lower()
    if parsed.scheme not in {"http", "https"} or not hostname or not hosts:
        return False
    return hostname in hosts or any(hostname.endswith("." + host) for host in hosts)


def requested_page_url(
    search_url: str,
    request: dict,
    page_number: int,
    adapter: MarketplaceAdapter,
    page_size: int,
    cursor: str = "",
) -> str:
    """Resolve an exact page URL first, then apply the adapter's rule."""

    page_urls = request.get("pageUrls") or []
    if isinstance(page_urls, list) and 1 <= page_number <= len(page_urls):
        return str(page_urls[page_number - 1])
    cursor_url = resume_url_from_cursor(cursor)
    if cursor_url:
        return cursor_url
    return adapter.page_url(search_url, page_number, page_size, cursor=cursor)


def read_attribute(locator, name: str) -> str:
    try:
        if locator.count() == 0:
            return ""
        return compact(locator.get_attribute(name), 1_000)
    except Exception:
        return ""


def read_text(locator, timeout: int = 2_000) -> str:
    try:
        return compact(locator.inner_text(timeout=timeout))
    except Exception:
        return ""


def current_page_url(page) -> str:
    try:
        value = getattr(page, "url", "")
        return str(value() if callable(value) else value)
    except Exception:
        return ""


def page_body(page, timeout: int = 10_000, limit: int = 30_000) -> str:
    try:
        return compact(page.locator("body").inner_text(timeout=timeout), limit)
    except Exception:
        return ""


def challenge_reason(body: str) -> str:
    lowered = str(body or "").casefold()
    for marker in CHALLENGE_MARKERS:
        if marker.casefold() in lowered:
            return marker
    return ""


def ensure_rendered_page(body: str, source_id: str, *, allow_empty: bool = False) -> None:
    reason = challenge_reason(body)
    if reason:
        raise SourceBlockedError(f"BLOCKED_SOURCE: {source_id}: rendered page contains {reason!r}")
    if not allow_empty and not body.strip():
        raise RenderedPageError(f"empty rendered page for source {source_id}")


class NavigationRateLimiter:
    """Throttle all search and detail navigations for one claimed job."""

    def __init__(self, source: dict, request: dict) -> None:
        try:
            rate_per_minute = int(source.get("ratePerMinute") or 0)
        except (TypeError, ValueError):
            rate_per_minute = 0
        try:
            configured_delay = max(0.0, float(request.get("minDelayMs") or 0) / 1_000)
        except (TypeError, ValueError):
            configured_delay = 0.0
        source_delay = 60.0 / rate_per_minute if rate_per_minute > 0 else 0.0
        self.interval = max(configured_delay, source_delay)
        self.last_navigation = 0.0

    def wait(self) -> None:
        if self.interval <= 0:
            self.last_navigation = time.monotonic()
            return
        now = time.monotonic()
        remaining = self.last_navigation + self.interval - now
        if remaining > 0:
            time.sleep(remaining)
        self.last_navigation = time.monotonic()


def navigate_page(page, url: str, hosts: set[str], source_id: str, limiter: NavigationRateLimiter) -> str:
    limiter.wait()
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=60_000)
    except Exception as first_error:
        try:
            page.goto(url, wait_until="commit", timeout=60_000)
        except Exception as second_error:
            raise RenderedPageError(
                f"navigation failed for {url}: {type(second_error).__name__}"
            ) from first_error
    redirected_url = current_page_url(page)
    if (urlparse(redirected_url).hostname or "").startswith("login.") or re.search(r"/(?:verify/|buyer/login|member/login|login)(?:/|$)", urlparse(redirected_url).path):
        raise SourceBlockedError(f"BLOCKED_SOURCE: {source_id}: login or traffic verification required")
    if redirected_url and not is_allowed_url(redirected_url, hosts):
        raise RenderedPageError(f"source redirected outside the allow-list: {redirected_url}")
    try:
        page.wait_for_timeout(750)
    except Exception:
        pass
    body = page_body(page)
    if not body.strip() and source_id in {"books-com-tw", "ruten-tw", "shopee-tw", "yahoo-tw", "bookwalker-tw", "readmoo-tw"}:
        for _ in range(20 if source_id in {"mercari-jp", "mandarake", "mandarake-jp"} else 10):
            page.wait_for_timeout(500)
            body = page_body(page)
            if body.strip():
                break
    redirected_url = current_page_url(page)
    if (urlparse(redirected_url).hostname or "").startswith("login.") or re.search(r"/(?:verify/|buyer/login|member/login|login)(?:/|$)", urlparse(redirected_url).path):
        raise SourceBlockedError(f"BLOCKED_SOURCE: {source_id}: login or traffic verification required")
    if redirected_url and not is_allowed_url(redirected_url, hosts):
        raise RenderedPageError(f"source redirected outside the allow-list: {redirected_url}")
    ensure_rendered_page(body, source_id)
    return body


def image_from_locator(locator) -> str:
    try:
        images = locator.locator("img")
        for index in range(min(images.count(), 3)):
            image = images.nth(index)
            for attribute in ("data-src", "data-original", "src"):
                value = read_attribute(image, attribute)
                if value.startswith("http"):
                    return value
    except Exception:
        pass
    return ""


def collect_anchor_candidates(
    page,
    search_url: str,
    hosts: set[str],
    adapter: MarketplaceAdapter,
    limit: int,
) -> list[dict]:
    candidates: list[dict] = []
    seen: set[str] = set()
    try:
        anchors = page.locator("a")
        # Navigation and footer anchors are interleaved with product cards on
        # several SPAs. Scan a wider window, but cap the number of accepted
        # product links that can reach detail navigation.
        count = min(anchors.count(), 5_000)
    except Exception:
        return candidates
    for index in range(count):
        anchor = anchors.nth(index)
        href = read_attribute(anchor, "href")
        if not href:
            continue
        link = adapter.canonical_result_url(urljoin(search_url, href).split("#", 1)[0])
        if link in seen or not is_allowed_url(link, hosts) or not adapter.is_result_url(link):
            continue
        title = read_attribute(anchor, "aria-label") or read_attribute(anchor, "title")
        if not title:
            try:
                title = read_attribute(anchor.locator("img").first, "alt")
            except Exception:
                pass
        text = read_text(anchor, timeout=1_000)
        label = compact(title or text, 800)
        if len(label) < 4:
            continue
        seen.add(link)
        candidates.append({"url": link, "title": label, "text": text, "imageUrl": image_from_locator(anchor)})
        if len(candidates) >= limit:
            break
    return candidates


def ruten_sold_candidates(candidates: list[dict], request: dict, limit: int) -> list[dict]:
    """Filter a public auction index before spending detail-navigation budget."""
    query = compact(request.get("query"), 500)
    # Generic photobook terms are checked through the existing relevance gate;
    # any remaining names/title words must occur in the selected card.
    terms = re.sub(r"photobooks?|photo\s*books?|寫真集|写真集|寫真書|写真书", " ", query, flags=re.I).split()
    result = []
    for candidate in candidates:
        text = compact(candidate.get("text") or candidate.get("title"), 4000)
        if not re.search(r"競標(?:已)?結束|已結標", text):
            continue
        title = re.sub(r"^(?:競標(?:已)?結束|已結標)\s*(?:\d+\s*天\s*\d{2}:\d{2}:\d{2})?\s*", "", candidate.get("title", ""))
        title = re.sub(r"\s*(?:目前出價\s*)?\$\s*[0-9,]+\s*$", "", title).strip()
        candidate = {**candidate, "title": title}
        if not looks_like_photobook(title) and not known_photobook_match(request, title, "", {}):
            continue
        if any(normalized_match_text(term) not in normalized_match_text(title) for term in terms):
            continue
        if not matches_target_scope(request, title, {**candidate, "text": title}, {}, False):
            continue
        result.append(candidate)
        if len(result) >= limit:
            break
    return result


def digital_retail_candidates(candidates: list[dict], request: dict, limit: int) -> list[dict]:
    # Retail search can match individual query characters and include unrelated
    # recommendations. Filter before those consume the detail budget.
    query = normalized_match_text(compact(request.get("query"), 500))
    generic = query in {normalized_match_text(value) for value in ("寫真集", "寫真", "photobook", "写真集")}
    model_query = query in {normalized_match_text(value) for value in request_keywords(request, "humanModelKeywords", "modelKeywords")}
    selected = []
    if model_query:
        names = [normalized_match_text(value) for value in request_keywords(request, "humanModelKeywords", "modelKeywords")]
        def priority(candidate):
            text = normalized_match_text(candidate.get("title", "") + " " + candidate.get("text", ""))
            return (any(name and name in text for name in names), bool(STRONG_PHOTOBOOK_SIGNAL_RE.search(candidate.get("title", ""))))
        candidates = sorted(candidates, key=priority, reverse=True)
    for candidate in candidates:
        text = normalized_match_text(candidate.get("title", "") + " " + candidate.get("text", ""))
        if query and not generic and not model_query and query not in text:
            continue
        selected.append(candidate)
        if len(selected) >= limit:
            break
    return selected


def next_page_url(page, search_url: str, hosts: set[str]) -> str:
    """Return a rendered source-local Next link, if one exists."""

    try:
        anchors = page.locator("a")
        count = min(anchors.count(), 5_000)
    except Exception:
        return ""
    current = search_url.split("#", 1)[0].rstrip("/")
    for index in range(count):
        anchor = anchors.nth(index)
        rel = read_attribute(anchor, "rel").casefold()
        aria = read_attribute(anchor, "aria-label")
        title = read_attribute(anchor, "title")
        text = read_text(anchor, timeout=100)
        label = compact(" ".join((rel, aria, title, text)), 500)
        if rel != "next" and not NEXT_RE.search(label):
            continue
        href = read_attribute(anchor, "href")
        if not href:
            # A button without an href needs a marketplace-specific click
            # adapter. Do not treat it as a page cursor, because reloading the
            # same URL would otherwise produce an endless job loop.
            continue
        link = urljoin(search_url, href).split("#", 1)[0]
        if is_allowed_url(link, hosts) and link.rstrip("/") != current:
            return link
    return ""


def structured_value_text(value: object, limit: int = 1_000) -> str:
    """Flatten JSON-LD author/creator/category fields for relevance checks."""

    if isinstance(value, dict):
        pieces = []
        for key in ("name", "alternateName", "description", "url"):
            if value.get(key) not in (None, ""):
                pieces.append(structured_value_text(value.get(key), limit))
        return compact(" ".join(pieces), limit)
    if isinstance(value, (list, tuple)):
        return compact(" ".join(structured_value_text(item, limit) for item in value), limit)
    return compact(value, limit)


def structured_product(page) -> dict:
    try:
        scripts = page.locator("script[type='application/ld+json']")
        count = scripts.count()
    except Exception:
        return {}
    for index in range(count):
        try:
            payload = json.loads(scripts.nth(index).inner_text())
        except (TypeError, ValueError, json.JSONDecodeError):
            continue
        values = payload if isinstance(payload, list) else [payload]
        queue = list(values)
        while queue:
            value = queue.pop(0)
            if not isinstance(value, dict):
                continue
            graph = value.get("@graph")
            if isinstance(graph, list):
                queue.extend(graph)
            offers = value.get("offers") or {}
            if isinstance(offers, list):
                offers = offers[0] if offers else {}
            if not isinstance(offers, dict):
                offers = {}
            type_value = value.get("@type")
            is_product = type_value == "Product" or (
                isinstance(type_value, list) and "Product" in type_value
            )
            if is_product or offers:
                return {
                    "name": compact(value.get("name"), 500),
                    "description": compact(value.get("description"), 4_000),
                    "author": structured_value_text(value.get("author"), 1_000),
                    "creator": structured_value_text(value.get("creator"), 1_000),
                    "brand": structured_value_text(value.get("brand"), 500),
                    "category": structured_value_text(value.get("category"), 500),
                    "isbn": compact(value.get("isbn"), 32),
                    "publisher": structured_value_text(value.get("publisher"), 180),
                    "numberOfPages": value.get("numberOfPages"),
                    "datePublished": value.get("datePublished"),
                    "isPartOf": value.get("isPartOf"),
                    "sku": compact(value.get("sku") or value.get("productID"), 180),
                    "productID": compact(value.get("productID"), 180),
                    "image": value.get("image") or "",
                    "price": offers.get("price"),
                    "currency": compact(offers.get("priceCurrency"), 12),
                    "availability": compact(offers.get("availability"), 100),
                }
    return {}


def page_metadata(page) -> dict:
    result: dict[str, str] = {}
    for selector, key in (
        ("meta[property='og:title']", "name"),
        ("meta[name='twitter:title']", "name"),
        ("meta[property='og:image']", "image"),
        ("meta[name='twitter:image']", "image"),
    ):
        try:
            locator = page.locator(selector).first
            if locator.count() > 0:
                result.setdefault(key, read_attribute(locator, "content"))
        except Exception:
            continue
    try:
        heading = read_text(page.locator("h1").first, timeout=2_000)
        if len(heading) >= 4:
            result.setdefault("name", heading)
    except Exception:
        pass
    try:
        document_title = compact(page.title(), 500)
        if len(document_title) >= 4 and not document_title.casefold().startswith("loading "):
            result.setdefault("name", document_title)
    except Exception:
        pass
    return result


def bookwalker_photo_category(body: str) -> str:
    """Return BOOK☆WALKER's selected-product genre when the title is generic."""
    match = re.search(
        r"(?:類型標籤|類別)\s+(.+?)\s+(?=出版社|系列|EPUB格式|價格|發售日|頁數)",
        body,
    )
    return compact(match.group(1), 120) if match else ""


def taaze_product_category(body: str, title: str) -> str:
    """Return the selected ebook's last TAAZE breadcrumb before its heading."""
    if not title:
        return ""
    match = re.search(
        r"(?:首頁\s*>\s*)?(?:中文電子書|電子書)\s*>(?P<crumbs>.*?)>\s*"
        + re.escape(title),
        body,
        re.IGNORECASE,
    )
    if not match:
        return ""
    crumbs = [compact(part, 100) for part in match.group("crumbs").split(">")]
    return crumbs[-1] if crumbs else ""


def selected_digital_format_evidence(
    source_id: str, title: str, body: str, structured: dict
) -> bool:
    """Require digital evidence tied to the selected product on mixed stores."""
    book_format = str(structured.get("bookFormat") or "")
    if DIGITAL_RE.search(title) or DIGITAL_RE.search(book_format) or book_format.rsplit("/", 1)[-1].casefold() == "ebook":
        return True
    if source_id != "taaze-books-tw" or not title:
        return False
    # TAAZE renders a clean h1 without the format suffix, while the selected
    # product heading reads "<title>（電子書）". Check only text adjacent to
    # that exact title so the site's general ebook navigation cannot label a
    # paper edition as digital.
    for match in re.finditer(re.escape(title), body, re.IGNORECASE):
        context = body[max(0, match.start() - 80) : match.end() + 100]
        if DIGITAL_RE.search(context):
            return True
    return False


def detail_snapshot(
    page,
    url: str,
    hosts: set[str],
    source_id: str,
    limiter: NavigationRateLimiter,
) -> dict:
    try:
        body = navigate_page(page, url, hosts, source_id, limiter)
    except SourceBlockedError:
        raise
    except Exception as exc:
        raise DetailSnapshotError(f"detail navigation failed for {url}: {exc}") from exc
    lowered_body = body.casefold()
    if any(marker.casefold() in lowered_body for marker in DETAIL_NOT_FOUND_MARKERS):
        raise DetailSnapshotError(f"detail page reports that the product is not found: {url}")
    structured = structured_product(page)
    metadata = page_metadata(page)
    if source_id == "bookwalker-tw":
        category = bookwalker_photo_category(body)
        if category:
            structured["category"] = category
    elif source_id == "taaze-books-tw":
        title = structured.get("name") or metadata.get("name", "")
        category = taaze_product_category(body, title)
        if category:
            structured["category"] = category
    if source_id in EXTRA_DIGITAL_SOURCES:
        adapter = resolve_adapter(source_id)
        redirected = current_page_url(page)
        if redirected and adapter.extract_external_id(redirected) != adapter.extract_external_id(url):
            raise DetailSnapshotError(f"digital detail redirected away from the selected book: {url}")
    if source_id == "rakuten-books-jp" and not structured.get("name"):
        structured["name"] = metadata.get("name", "")
    if source_id in JAPAN_SOURCE_IDS | TAIWAN_DIGITAL_RETAIL_SOURCES | {"ruten-tw", "yahoo-tw"}:
        for _ in range(20 if source_id in {"mercari-jp", "mandarake", "mandarake-jp"} else 10):
            offer_evidence = ACTIVE_RE.search(body) or ENDED_RE.search(body) or structured.get("availability")
            if offer_evidence and (structured.get("name") or source_id not in JAPAN_SOURCE_IDS):
                break
            page.wait_for_timeout(500)
            body = page_body(page)
            ensure_rendered_page(body, source_id)
            if re.search(r"/(?:member/login|login)(?:/|$)", urlparse(current_page_url(page)).path):
                raise SourceBlockedError(f"BLOCKED_SOURCE: {source_id}: login required")
            structured = structured_product(page)
        if source_id in JAPAN_SOURCE_IDS and not structured.get("name"):
            title = metadata.get("name", "")
            if not title:
                headings = page.locator("h1")
                for index in range(min(headings.count(), 5)):
                    title = read_text(headings.nth(index))
                    if title:
                        break
            if not title:
                raise DetailSnapshotError(f"{source_id}: selected product did not render")
            structured["name"] = title
    metadata = page_metadata(page)
    if source_id == "bookwalker-tw":
        try:
            cover = bookwalker_product_cover(read_attribute(page.locator('#app[data-page]').first, 'data-page'), url)
            if cover:
                metadata['image'] = cover
        except Exception:
            pass
    transaction = {}
    if source_id in JAPAN_SOURCE_IDS:
        title = structured.get("name", "")
        if source_id == "yahoo-furima-jp":
            category = re.search(r"商品の情報\s*カテゴリ\s*(.*?)\s*商品の状態", body)
            if category:
                structured["category"] = category.group(1)
        if source_id == "yahoo-auctions-jp" and title and title in body:
            # The page repeats its title above recommendations before the
            # actual auction panel. Use the last title preceding its fields.
            body = body[body.rfind(title):]
        # Keep selected offer controls, excluding seller prose and related items.
        body = re.split(r"「[^」]+」に近い商品|商品説明|商品の説明|こちらの商品もおすすめ|この商品をみている人にオススメ|この商品を見ている人におすすめ|見た目が似ている商品|お探しの商品からのおすすめ", body, maxsplit=1)[0]
        if source_id == "yahoo-furima-jp":
            if page.locator('img[alt="sold"], img[alt="SOLD"]').count():
                body += " SOLD"
    if source_id == "yahoo-tw":
        # Read the selected item's fields separately: innerText joins the
        # price and bid count into "$1501 次出價" on completed auctions.
        transaction = page.locator("body").evaluate("""el => {
            const result = {};
            for (const label of el.querySelectorAll('span')) {
                if (!label.checkVisibility()) continue;
                const name = label.textContent.trim();
                if (name !== '結標價格' && name !== '得標者') continue;
                const row = label.parentElement.parentElement;
                if (name === '結標價格') {
                    const price = row.querySelector('em');
                    if (price) result.closingPrice = price.textContent.trim();
                } else {
                    const content = label.parentElement.nextElementSibling;
                    if (content) result.winner = content.innerText.trim();
                }
            }
            result.category = [...el.querySelectorAll('li[class*="breadcrumbListItem"]')]
                .map(x => x.innerText.trim()).join(' ');
            return result;
        }""")
        if transaction.get("category"):
            structured["category"] = transaction["category"]
    if source_id in TAIWAN_DIGITAL_RETAIL_SOURCES:
        if source_id in EXTRA_DIGITAL_SOURCES | {"books-com-tw"}:
            selected_schema = selected_book_schema(page.locator("script[type='application/ld+json']").all_text_contents())
            structured.update({key: value for key, value in selected_schema.items() if value not in (None, "")})
            # Sanmin's JSON-LD `isbn` field is sometimes only its 222... vendor
            # SKU. The selected-book schema sanitizer intentionally returns
            # an empty ISBN for that value; preserve the clearing signal.
            if "isbn" in selected_schema:
                structured["isbn"] = selected_schema["isbn"]
        heading = read_text(page.locator("h1").first, timeout=2000)
        structured["name"] = heading or structured.get("name") or metadata.get("name", "")
        selected = re.split(r"Related Product|相關推薦|相關商品|其他人也買|您可能喜歡", body, maxsplit=1)[0]
        if source_id == "books-com-tw":
            selected = re.split(r"買了此商品的人|瀏覽此商品的人|同類商品新上架|本類暢銷榜", selected, maxsplit=1)[0]
        # Native buy-panel prices precede coupon discounts and recommendations.
        patterns = {
            "bookwalker-tw": r"價格\s*\$\s*([0-9,]+)",
            "pubu-tw": r"(?:EBook|eBook|電子書)\s*NT\$\s*([0-9,]+(?:\.\d+)?)",
            "kobo-tw": r"購買電子書\s*價格[：:]?\s*NT\$\s*([0-9,]+(?:\.\d+)?)",
            "hami-tw": r"(?:促銷價|電子書價)\s*[:：]\s*([0-9,]+)\s*元",
            "momo-books-tw": r"(?:限時折後價|促銷價)\s*([0-9,]+)\s*元",
            "hyread-tw": r"(?:優惠價|電子書)\s*NT\$\s*([0-9,]+)",
            "taaze-books-tw": r"特價\s*[:：]\s*(?:[0-9.]+\s*折\s*)?([0-9,]+)\s*元",
        }
        if source_id == "momo-books-tw" and structured.get("name") in selected:
            selected = selected[selected.rfind(structured["name"]):]
        default_pattern = r"(?!)" if source_id in EXTRA_DIGITAL_SOURCES | {"books-com-tw"} else r"(?:優惠價|電子書售價)\s*(?:NT\$)?\s*([0-9,]+)"
        match = re.search(patterns.get(source_id, default_pattern), selected, re.I)
        if match:
            structured["price"], structured["currency"] = match.group(1), "TWD"
        if source_id == "hami-tw":
            author = re.search(r"作\s*者[：:]\s*(.+?)\s*出版社[：:]", selected, re.S)
            publisher = re.search(r"出版社[：:]\s*(.+?)\s*類\s*別[：:]", selected, re.S)
            if author: structured["author"] = compact(author.group(1), 1000)
            if publisher: structured["publisher"] = compact(publisher.group(1), 500)
        if source_id == "taaze-books-tw":
            author = re.search(r"作者\s*[:：]\s*(.+?)\s*出版社\s*[:：]", selected, re.S)
            publisher = re.search(r"出版社\s*[:：]\s*(.+?)\s*出版日期\s*[:：]", selected, re.S)
            if author: structured["author"] = compact(author.group(1), 1000)
            if publisher: structured["publisher"] = compact(publisher.group(1), 500)
        isbn = re.search(r"ISBN\s*[:：]?\s*(97[89][0-9-]{10,14})(?!\d)", selected, re.I)
        if isbn:
            structured["isbn"] = isbn.group(1).replace("-", "")
        structured["editionVariant"] = digital_edition_variant(structured.get("name", ""))
        if source_id == "bookwalker-tw":
            author = re.search(r"作者\s+(.+?)\s+(?:類型標籤|攝影|出版社)", selected)
            publisher = re.search(r"出版社\s+(.+?)\s+(?:EPUB格式|發售日|頁數|優惠活動|系列)", selected)
            if author:
                structured["author"] = author.group(1)
            if publisher:
                structured["publisher"] = publisher.group(1)
        if source_id == "pubu-tw":
            author = re.search(r"Author\s+(.+?)\s+Follow", selected)
            if author:
                structured["author"] = author.group(1)
            publisher = re.search(r"Publisher\s+(.+?)\s+Follow", selected)
            if publisher:
                structured["publisher"] = publisher.group(1)
        if source_id == "kobo-tw":
            description = re.search(r"簡介\s+(.+?)\s+購買電子書", selected, re.S)
            if description:
                structured["description"] = compact(description.group(1), 4000)
            author = re.search(r"由\s+(.+?)\s+(?:簡介|系列|購買電子書)", selected)
            if author:
                structured["author"] = author.group(1)
            publisher = re.search(r"電子書詳細資料\s+(.+?)\s+發布日期", selected)
            if publisher:
                structured["publisher"] = publisher.group(1)
    if source_id in TAIWAN_DIGITAL_RETAIL_SOURCES:
        try:
            controls = page.locator("#button_book" if source_id == "pubu-tw" else "button, a").filter(has_text=re.compile(r"^(?:購買|直接購買|立即結帳|立即購買|加入購物車|放進購物車|放入購物車|新增至購物車|Buy|Add To Cart)$", re.I))
            for index in range(min(controls.count(), 5)):
                control = controls.nth(index)
                if control.is_visible() and control.is_enabled() and read_attribute(control, "aria-disabled") != "true":
                    structured["availability"] = "https://schema.org/InStock"
                    break
        except Exception:
            pass
    return {
        "body": body,
        "structured": structured,
        "metadata": metadata,
        "transaction": transaction,
        "imageUrl": select_cover_url(metadata.get("image"), structured.get("image")),
    }


def infer_format(text: str, source: dict) -> str:
    value = compact(text, 12_000)
    digital_match = DIGITAL_RE.search(value)
    physical_match = PHYSICAL_RE.search(value)
    if digital_match:
        # A printed edition often advertises a digital bonus or a QR code. A
        # nearby explicit paper/print signal wins in that case; otherwise the
        # selected product is an electronic edition.
        nearby = value[max(0, digital_match.start() - 100) : digital_match.end() + 100]
        if physical_match and re.search(
            r"(?:bonus|特典|付録|附贈|附赠|贈品|赠品|qr|code|碼|码)", nearby, re.IGNORECASE
        ):
            return "physical"
        return "digital"
    if source.get("kind") == "digital_store" and not EXPLICIT_PHYSICAL_RE.search(value):
        return "digital"
    return "physical"


def digital_edition_variant(title: str) -> str:
    if re.search(r"無影片|不含影片|無寫真MV|不含影音", title, re.I):
        return "without_video"
    if re.search(r"含影音|含影片|APP含影音|(?:附|送|贈)\s*(?:有\s*)?(?:寫真\s*)?(?:影片|影音)", title, re.I):
        return "with_video"
    return "unspecified"


def digital_access(source_id: str, source: dict, url: str) -> str:
    """Authorize only configured first-party/e-book storefront sources.

    Words such as ``official`` or ``publisher`` in a seller description are
    not provenance. The source ID and its allowed host are the trust boundary;
    the Go API applies the same allow-list before persistence.
    """

    if source_id not in VERIFIED_DIGITAL_SOURCES | EXTRA_DIGITAL_SOURCES:
        return ""
    if not is_allowed_url(url, source_hosts(source)):
        return ""
    return "authorized_store"


def looks_like_photobook(text: str) -> bool:
    value = compact(text, 12_000)
    if not PHOTBOOK_SIGNAL_RE.search(value):
        return False
    # Bonus postcards/cards are allowed when the selected product is a book;
    # remove that phrase before applying the non-book guard. A card-only item
    # still fails because it has no remaining strong photobook evidence.
    without_bonus = BONUS_CARD_RE.sub(" ", value)
    if NON_PHOTOBOOK_RE.search(without_bonus):
        return False
    if NON_HUMAN_MODEL_RE.search(without_bonus):
        return False
    if POSTCARD_OR_CARD_RE.search(without_bonus) and not STRONG_PHOTOBOOK_SIGNAL_RE.search(without_bonus):
        return False
    if GENERIC_ALBUM_RE.search(without_bonus) and not STRONG_PHOTOBOOK_SIGNAL_RE.search(without_bonus):
        return False
    if GENERIC_ARTBOOK_RE.search(without_bonus) and not re.search(
        r"(?:写真|寫真|摄影|攝影|photo|photography)", without_bonus, re.IGNORECASE
    ):
        return False
    return True


def normalized_match_text(value: object) -> str:
    return re.sub(r"[^0-9a-z\u3040-\u30ff\u3400-\u9fff]+", "", str(value or "").casefold())


PEOPLE_PHOTOBOOK_RE = re.compile(
    r"(?:\b(?:model|fashion\s+model|cover\s+model|female\s+model|male\s+model|"
    r"supermodel|idol|celebrity|actor|actress|singer|talent|gravure|gravure\s+idol|"
    r"glamour|influencer|entertainer|performer|beauty\s+queen|swimsuit)\b|"
    r"アイドル|モデル|女優|俳優|歌手|タレント|グラビア|グラドル|女子アナ|芸能人|水着|"
    r"レースクイーン|偶像|模特(?:兒|儿)?|女模|男模|明星|演員|演员|歌手|藝人|艺人|"
    r"網紅|网红|實況主播|實況主|直播主|寫真女星|写真女優|水著)",
    re.IGNORECASE,
)


def target_scope(request: dict) -> str:
    """Return the enforced subject scope.

    The product only collects human-model/person photobooks. Older callers may
    still send ``all`` or ``photography``; those values are intentionally
    narrowed here rather than allowing a photographer-led monograph through.
    """

    return "people"


def requested_scope_is_people(request: dict) -> bool:
    """Whether a caller explicitly requested the only supported scope."""

    raw = request.get("targetScope") or request.get("photobookScope")
    if raw in (None, ""):
        return True
    value = re.sub(r"[\s_-]+", "", str(raw).casefold())
    return value in {"people", "person", "idol", "celebrity", "model", "talent"}


def request_keywords(request: dict, *fields: str) -> list[str]:
    values: list[object] = []
    for field in fields:
        raw = request.get(field)
        if isinstance(raw, (list, tuple)):
            values.extend(raw)
        elif raw not in (None, ""):
            values.append(raw)
    return [compact(value, 180) for value in values if compact(value, 180)]


def selected_product_detail(title: str, detail_body: str = "") -> str:
    """Return detail-page copy attached to the selected product title only."""

    detail = compact(detail_body, 30_000)
    title_position = detail.find(title) if title else -1
    if title_position < 0:
        return ""
    selected = detail[title_position + len(title):]
    return compact(
        re.split(
            r"Related Product|相關推薦|相關商品|其他人也買|您可能喜歡|更多最新寫真資訊|更多推薦|You might also like|Related books|Related titles",
            selected,
            maxsplit=1,
            flags=re.I,
        )[0],
        8_000,
    )


def subject_evidence_text(title: str, candidate: dict, structured: dict, detail_body: str = "") -> str:
    structured = structured if isinstance(structured, dict) else {}
    # A search card's full inner text can contain recommendations. Use its
    # selected title, product schema, and detail copy tied to that title.
    selected_detail = selected_product_detail(title, detail_body)
    return compact(
        " ".join(
            (
                title,
                candidate.get("title", ""),
                structured.get("description", ""),
                selected_detail,
                structured.get("author", ""),
                structured.get("creator", ""),
                structured.get("brand", ""),
                structured.get("category", ""),
            )
        ),
        8_000,
    )


def explicit_human_model_keyword_match(request: dict, subject_text: str) -> bool:
    """Match only caller-supplied, verified human model/person names.

    ``personKeywords`` is deliberately not trusted here: it was previously
    used for photographer names and could turn an artist monograph into a
    model photobook. Callers that know the target is a model/person should use
    ``humanModelKeywords`` (or its short alias ``modelKeywords``).
    """

    subject_key = normalized_match_text(subject_text)
    if not subject_key:
        return False
    for keyword in request_keywords(request, "humanModelKeywords", "modelKeywords"):
        keyword_key = normalized_match_text(keyword)
        if keyword_key and keyword_key in subject_key:
            return True
    return False


def matches_target_scope(
    request: dict,
    title: str,
    candidate: dict,
    structured: dict,
    known_match: bool,
    detail_body: str = "",
) -> bool:
    """Allow only human-model/person photobooks.

    Exact-title ``knownPhotobook`` matching only relaxes the generic
    photobook-word check. It must never bypass the human-model subject gate.
    """

    scope = target_scope(request)
    subject = subject_evidence_text(title, candidate, structured, detail_body)
    if scope != "people":
        return False
    return (
        PEOPLE_PHOTOBOOK_RE.search(subject) is not None
        or explicit_human_model_keyword_match(request, subject)
    )


def known_photobook_match(request: dict, title: str, body: str, structured: dict) -> bool:
    """Allow exact-title/ISBN jobs to match products whose title omits 写真集."""

    if not bool_option(request.get("knownPhotobook"), False):
        return False
    structured = structured if isinstance(structured, dict) else {}
    # ``body`` is selected-product detail copy, not the surrounding search
    # card, so its ISBN cannot be borrowed from a neighboring result.
    evidence_text = compact(" ".join((title, body, structured.get("description", ""))), 12_000)
    without_bonus = BONUS_CARD_RE.sub(" ", evidence_text)
    if NON_PHOTOBOOK_RE.search(without_bonus):
        return False
    if NON_HUMAN_MODEL_RE.search(without_bonus):
        return False
    if POSTCARD_OR_CARD_RE.search(without_bonus) and not STRONG_PHOTOBOOK_SIGNAL_RE.search(without_bonus):
        return False
    title_key = normalized_match_text(title)
    expected_titles = request.get("expectedTitles") or request.get("titleAliases") or []
    if isinstance(expected_titles, str):
        expected_titles = [expected_titles]
    expected_title = request.get("expectedTitle") or request.get("title")
    if expected_title:
        expected_titles = [*expected_titles, expected_title]
    for expected in expected_titles:
        expected_key = normalized_match_text(expected)
        if expected_key and (expected_key in title_key or title_key in expected_key):
            return True
    isbn = re.sub(r"[^0-9Xx]", "", compact(request.get("isbn"), 32))
    if isbn:
        product_text = " ".join(
            (title, body, compact(structured.get("sku"), 180), compact(structured.get("productID"), 180))
        )
        if isbn in re.sub(r"[^0-9Xx]", "", product_text):
            return True
    return False


def currency_from_source(source: dict) -> str:
    locale = str(source.get("locale") or "").lower()
    region = str(source.get("region") or "").upper()
    if region == "JP" or "ja-" in locale:
        return "JPY"
    if region == "TW" or "zh-tw" in locale:
        return "TWD"
    if region == "CN" or "zh-cn" in locale:
        return "CNY"
    if region in {"MY", "MLS"} or "en-my" in locale:
        return "MYR"
    return ""


def normalize_currency(value: str, source: dict) -> str:
    currency = compact(value, 12).upper()
    if currency in {"¥", "￥", "JPY", "円"}:
        return "CNY" if str(source.get("region")).upper() == "CN" and currency in {"¥", "￥"} else "JPY"
    if currency in {"NT$", "NTD", "TWD"}:
        return "TWD"
    if currency in {"元", "RMB", "CNY"}:
        if currency == "元" and str(source.get("region")).upper() == "TW":
            return "TWD"
        return "CNY"
    if currency in {"RM", "MYR"}:
        return "MYR"
    if currency == "$":
        regional_currency = currency_from_source(source)
        if regional_currency in {"TWD", "MYR"}:
            return regional_currency
        return "USD"
    if currency in {"US$", "USD"}:
        return "USD"
    return currency


def parse_price(text: str, structured: dict, source: dict) -> tuple[int, str]:
    raw_price = structured.get("price") if isinstance(structured, dict) else None
    raw_currency = compact(structured.get("currency"), 12) if isinstance(structured, dict) else ""
    numeric: Decimal | None = None
    if raw_price not in (None, ""):
        try:
            candidate = Decimal(str(raw_price).replace(",", "").strip())
            if candidate.is_finite() and candidate >= 0:
                numeric = candidate
        except (InvalidOperation, ValueError):
            numeric = None
    currency = normalize_currency(raw_currency, source)
    if numeric is None and str(source.get("region")).upper() == "TW":
        labelled = re.search(r"(?:電子書售價|电子书售价|直購價|直购价|優惠價|优惠价|售價|售价|目前出價|成交價)\s*[:：]?\s*(?:NT\$|TWD|NTD|\$)?\s*([0-9][0-9,]*(?:\.\d{1,2})?)", text, re.I)
        if not labelled:
            labelled = re.search(r"(?:定價|定价)\s*[:：]?\s*(?:NT\$|TWD|NTD|\$)?\s*([0-9][0-9,]*(?:\.\d{1,2})?)", text, re.I)
        if labelled:
            numeric = Decimal(labelled.group(1).replace(",", ""))
            currency = "TWD"
    if numeric is None:
        for pattern, code in CURRENCY_PATTERNS:
            match = pattern.search(text)
            if not match:
                continue
            try:
                candidate = Decimal(match.group(1).replace(",", "").strip())
            except (InvalidOperation, ValueError):
                continue
            if not candidate.is_finite() or candidate < 0:
                continue
            numeric = candidate
            # The same yen symbol is commonly rendered for CNY on Chinese
            # storefronts. Prefer the source region when the symbol is
            # ambiguous; explicit CNY/RMB text remains CNY.
            currency = "CNY" if code == "JPY" and str(source.get("region")).upper() == "CN" else code
            if code == "CNY" and str(source.get("region")).upper() == "TW" and match.group(0).rstrip().endswith("元"):
                currency = "TWD"
            if code == "USD" and match.group(0).lstrip().startswith("$"):
                regional_currency = currency_from_source(source)
                if regional_currency in {"TWD", "MYR"}:
                    currency = regional_currency
            break
    if numeric is None:
        bare = re.search(
            r"(?:price|amount|価格|售價|售价|價錢|价钱|金額|金额)\s*[:：]?\s*"
            r"([0-9][0-9,]*(?:\.\d{1,2})?)",
            text,
            re.IGNORECASE,
        )
        if bare:
            try:
                candidate = Decimal(bare.group(1).replace(",", "").strip())
                numeric = candidate if candidate.is_finite() and candidate >= 0 else None
            except (InvalidOperation, ValueError):
                numeric = None
    currency = currency or currency_from_source(source)
    if numeric is None or not numeric.is_finite() or numeric < 0:
        return 0, currency
    multiplier = Decimal("1") if currency in {"JPY", "KRW"} else Decimal("100")
    minor = (numeric * multiplier).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return int(minor), currency


def status_for(text: str, operation: str, source_id: str = "") -> tuple[str, str]:
    value = compact(text, 30_000)
    value = re.sub(r"(?:已售出?|銷售|销量|銷量)\s*\d[\d,]*\s*(?:件|個|个|本)?", " ", value)
    if source_id in {"ruten-tw", "yahoo-tw", "shopee-tw"}:
        # Seller instructions and recommendations are not the selected item's
        # current transaction state. Keep status checks above those sections.
        value = re.split(r"商品說明|商品说明|商品詳情|賣場佈告欄|賣場公告|猜你喜歡|您可能喜歡", value, maxsplit=1)[0]
    if source_id in JAPAN_SOURCE_IDS:
        value = re.split(r"商品説明|商品の説明|こちらの商品もおすすめ|この商品をみている人にオススメ", value, maxsplit=1)[0]
        sold = re.search(r"\bSOLD\s*OUT\b|\bSOLD\b|売り切れ(?:ました)?|この商品は.{0,20}売れました|購入日時\s*[:：]", value, re.I)
        ended = re.search(r"オークションは終了|オークション終了|終了(?:しました)?(?:\s|$)|在庫なし|品切れ|販売終了", value)
        if source_id == "yahoo-auctions-jp":
            if operation == "sold_discovery":
                bid = re.search(r"([1-9][0-9,]*)件", value)
                if ended and bid and not re.search(r"落札者なし|入札者なし|落札されません|取り消され|取消|中止", value):
                    return "completed", "ended auction with " + bid.group(0)
                return "unknown", "no successful completed auction evidence"
        if operation == "sold_discovery" and source_id in {"mercari-jp", "rakuma", "rakuma-jp", "yahoo-furima-jp"}:
            return ("completed", compact(sold.group(0))) if sold else ("unknown", "no selected-item sold evidence")
        if operation in {"active_discovery", "listing_reconcile"}:
            if sold or ended:
                return "ended", compact((sold or ended).group(0))
            active = re.search(r"入札する|購入手続きへ|購入に進む|購入手続き|カートに入れる|買い物かごに入れる|予約受付中|在庫あり", value)
            if active:
                return "active", active.group(0)
    if operation in {"active_discovery", "listing_reconcile"}:
        evidence = ENDED_RE.search(value)
        if evidence:
            return "ended", compact(evidence.group(0))
        evidence = ACTIVE_RE.search(value)
        if evidence:
            return "active", compact(evidence.group(0))
        return "unknown", "no explicit availability evidence"
    if operation == "sold_discovery":
        if source_id in {"ruten-tw", "yahoo-tw", "shopee-tw"}:
            # Taiwan uses the same public item page for active stock, ended
            # stock and completed transactions. Require a sale-specific label;
            # an ended auction or units-sold counter is insufficient.
            if re.search(r"交易(?:已)?取消|已取消交易|訂單(?:已)?取消|未成交|尚未成交", value):
                return "unknown", "transaction cancelled or not completed"
            if re.search(r"得標者\s*[:：]?\s*(?:無|无|沒有|暂无)(?:\s|$)", value):
                return "unknown", "auction ended without a winner"
            if source_id == "ruten-tw" and re.search(r"競標結束|競標已結束", value):
                winner = re.search(r"得標者\s*[:：]?\s*([A-Za-z0-9_][A-Za-z0-9_*.-]*\*+[A-Za-z0-9_*.-]*)", value)
                if winner:
                    return "completed", "ended auction with masked winner"
            evidence = re.search(r"已成交|交易完成|交易成功|成交(?:價|价格|價錢)\s*[:：]?\s*(?:NT\$|\$)?\s*\d|得標者\s*[:：]?\s*Y\d+", value)
            if evidence:
                return "completed", compact(evidence.group(0))
            return "unknown", "no explicit completed-transaction evidence"
        evidence = SOLD_RE.search(value)
        if evidence:
            return "completed", compact(evidence.group(0))
        # eBay and similar pages often render a standalone uppercase SOLD
        # badge. Do not mistake a seller counter such as "4 items sold" for
        # the selected listing's completed-sale state.
        for badge in re.finditer(r"\bSOLD\b", value):
            prefix = value[max(0, badge.start() - 12) : badge.start()].casefold()
            if re.search(r"(?:\b\d+\s+)?items?\s*$", prefix):
                continue
            return "completed", compact(badge.group(0))
        return "unknown", "no explicit sold evidence"
    return "unknown", "rendered product/listing page"


FIXED_PRICE_SOURCE_IDS = {
    "bookwalker-jp",
    "bookwalker-tw",
    "books-com-tw",
    "dangdang-cn",
    "jd-cn",
    "mandarake",
    "mandarake-jp",
    "rakuten-books-jp",
    "readmoo-tw",
    "surugaya",
    "surugaya-jp",
}


def is_marketplace_price_source(source_id: str, source: dict) -> bool:
    """Return whether the source is suitable for resale/auction price jobs."""

    kind = compact(source.get("kind"), 40).casefold()
    if kind not in {"marketplace", "marketplace_c2c", "auction", "flea_market"}:
        return False
    return source_id not in FIXED_PRICE_SOURCE_IDS | TAIWAN_DIGITAL_RETAIL_SOURCES


def photobook_title_exclusion(title: str) -> str:
    title = unicodedata.normalize("NFKC", title)
    if re.search(r"雑誌付録DVD|写真集SE\s*DVD", title, re.I):
        return "disc_only"
    if re.search(r"^DVD\s*写真集|DVD写真集\[", title, re.I):
        return "disc_only"
    if re.search(r"\[中古[^\]]*DVD\]|写真集.*メイキングDVD.*枚セット", title, re.I):
        return "disc_only"
    if re.search(r"L判写真\s*\d+枚", title, re.I):
        return "nonbook_product"
    if "ボールマーカー" in title:
        return "nonbook_product"
    if re.search(r"田村りおん.*まぶしいあの夏の日", title):
        return "subject_publication_age_unverified"
    if re.search(r"石田未来.*sugar\s*time|sugar\s*time.*石田未来|浅川梨奈.*なないろ|なないろ.*浅川梨奈|新関亜希.*HEAT\s*UP|河合美果.*風がおしえて", title, re.I):
        return "subject_publication_age_unverified"
    if re.search(r"ミニ写真集付き.*漫画アクション", title):
        return "magazine_or_supplement"
    if re.search(r"アート\s*ポスター|\[(?:中古(?:\s*セル版)?|新品\s*未開封)\s*DVD\]|カレンダーブック|フォトCD|Photo\s*CD|額入り|舞台.*パンフレット|振袖カタログ", title, re.I):
        return "nonbook_product"
    if re.search(r"\d{4}年\s*\d{1,2}月(?:\d{1,2}日)?号|週刊現代|週刊プレイボーイ|TVガイド\s*Stage\s*Stars|EX大衆|UTB.*アップ|ヤングチャンピオン.*袋とじ|Cream\s*クリーム|映画ファン.*臨時増刊", title, re.I):
        return "magazine_only"
    if re.search(r"制コレ.*水着|石川佳奈.*kana|前田愛.*眠り姫|宮沢ゆうな.*Pretty\s*Peach|菅谷梨沙子.*梨想|かわいい同級生|石川花.*写真集|写真集.*石川花|新原里彩.*学校なう", title, re.I):
        return "subject_publication_age_unverified"
    if re.search(r"Moecco|モエッコ", title, re.I):
        return "junior_gravure"
    if re.search(r"学校なう.*水着|水着.*学校なう", title):
        return "junior_gravure"
    if re.search(r"宮脇咲良.*さくら.*水着|水谷果穂.*写真集3冊", title):
        return "subject_publication_age_unverified"
    if re.search(r"宝生舞.*17歳|外岡えりか.*ひまわり|山中知恵.*花鳥風月|咲坂あいり.*Colorful", title, re.I):
        return "subject_publication_age_unverified"
    if re.search(r"グラビアチャンピオン|月刊(?:ザ・)?テンメイ", title):
        return "magazine_only"
    if re.search(r"透けパイ.*青山裕企", title):
        return "artist_monograph"
    if re.search(r"写真集クオリティ|グラビアザテレビジョン|特別付録.*MINIブック", title, re.I):
        return "magazine_or_supplement"
    if re.search(r"ギュンター.?ブルム|G[uü]nter\s+Blum|村田\s*兼一写真集", title, re.I):
        return "artist_monograph"
    if re.search(r"染色体.*野川イサム|野川イサム.*染色体|快楽の館", title):
        return "artist_monograph"
    if re.search(r"(?:CD|BD|Blu[ -]?ray|ブルーレイ)\s*写真集|^アイドルDVD", title, re.I):
        return "disc_only"
    if re.search(r"DVD|Blu[ -]?ray|ブルーレイ", title, re.I) and not STRONG_PHOTOBOOK_SIGNAL_RE.search(title):
        return "disc_only"
    if re.search(r"増刊|FRIDAY\s*GOLD", title, re.I) and not STRONG_PHOTOBOOK_SIGNAL_RE.search(title):
        return "magazine_only"
    if re.search(r"\bJK\b|女子高生|制服なう|エンジェルプロダクション|エンプロ|お菓子系|大倉梓|折山みゆ", title, re.I):
        return "junior_gravure"
    if re.search(r"AI[\s・_-]*(?:アート|美女|生成|グラビア)|生成AI|AI-generated", title, re.I):
        return "synthetic_subject"
    if re.search(r"写真データ|画像データ|ダウンロード販売", title):
        return "download_resale"
    if re.search(r"(?:ジュニア|Jr\.).*(?:グラビア|水着)|(?:グラビア|水着).*(?:ジュニア|Jr\.)", title, re.I):
        return "junior_gravure"
    if re.search(r"Chu[→\s-]*Boh|チューボー|ホイップ", title, re.I):
        return "junior_gravure"
    if re.search(r"\d{4}年\d{1,2}月号|特集号|(?:熱烈投稿|雑誌)", title) and not STRONG_PHOTOBOOK_SIGNAL_RE.search(title):
        return "magazine_only"
    if re.search(r"插畫|插画|イラスト|illustrat(?:ed|ion)", title, re.I):
        return "illustrated_book"
    if re.search(r"月曆|月历|桌曆|桌历|日曆|日历|掛曆|挂历|年曆|年历|カレンダー|\bcalendar\b", title, re.I) and not STRONG_PHOTOBOOK_SIGNAL_RE.search(title):
        return "calendar_only"
    return ""


def marketplace_subject_matches(request: dict, title: str) -> bool:
    names = request_keywords(request, "humanModelKeywords", "modelKeywords")
    if not names: return True
    prefix = re.split(r"寫真書|寫真集|數位寫真|写真集|photobook|photo\s*book", title, maxsplit=1, flags=re.I)[0]
    verified_subjects = request_keywords(request, "catalogModelNames")
    # Seller SEO strings often append unrelated names after the actual subject.
    prefix_key = normalized_match_text(prefix)
    if any(normalized_match_text(name) in prefix_key for name in verified_subjects):
        return any(normalized_match_text(name) in prefix_key for name in names)
    # A listing that omits every requested subject cannot be safely linked to
    # a person's photobook merely because it appeared in a broad search.
    return any(normalized_match_text(name) in prefix_key for name in names)


def make_observation(
    request: dict,
    source: dict,
    candidate: dict,
    detail: dict,
    operation: str,
    detail_required: bool | None = None,
) -> tuple[dict | None, str]:
    if detail_required is None:
        detail_required = bool_option(request.get("detailRequired"), True)
    if detail.get("detailError") and detail_required:
        return None, "detail_unavailable"
    structured = detail.get("structured") or {}
    metadata = detail.get("metadata") or {}
    body = compact(
        " ".join((candidate.get("text", ""), detail.get("body", ""), structured.get("description", ""))),
        30_000,
    )
    title = compact(structured.get("name") or metadata.get("name") or candidate.get("title") or body, 300)
    if (request.get("sourceId") or source.get("id")) in JAPAN_SOURCE_IDS and re.search(r"切り抜き|ラミネート加工", title):
        return None, "not_a_photobook"
    # Navigation and recommendation modules often mention a different
    # photobook or format. Only selected-product evidence determines scope.
    selected_detail = selected_product_detail(title, detail.get("body", ""))
    subject_text = subject_evidence_text(title, candidate, structured, detail.get("body", ""))
    relevance_text = subject_text
    source_id = compact(request.get("sourceId") or source.get("id"), 80)
    title_exclusion = photobook_title_exclusion(title)
    if title_exclusion: return None, title_exclusion
    if is_marketplace_price_source(source_id, source) and not marketplace_subject_matches(request,title):
        return None, "marketplace_subject_mismatch"

    digital_retail = source_id in TAIWAN_DIGITAL_RETAIL_SOURCES
    physical_marketplace = is_marketplace_price_source(source_id, source)
    if digital_retail and operation not in {"catalog_discovery", "active_discovery", "listing_detail"}:
        return None, "digital_sold_unsupported"
    if source_id in MIXED_DIGITAL_SOURCES and not selected_digital_format_evidence(
        source_id, title, compact(" ".join((title, selected_detail)), 12_000), structured
    ):
        return None, "digital_product_unverified"
    if (request.get("sourceId") or source.get("id")) in {"yahoo-tw", "yahoo-furima-jp"}:
        relevance_text = compact(relevance_text + " " + structured.get("category", ""), 10_000)
    known_match = known_photobook_match(request, title, selected_detail, structured)
    if not looks_like_photobook(relevance_text) and not known_match:
        return None, "not_a_photobook"
    if not matches_target_scope(request, title, candidate, structured, known_match, detail.get("body", "")):
        return None, f"not_in_{target_scope(request)}_scope"
    if (request.get("sourceId") or source.get("id")) in TAIWAN_DIGITAL_RETAIL_SOURCES and request_keywords(request, "humanModelKeywords", "modelKeywords"):
        if not explicit_human_model_keyword_match(request, subject_text):
            return None, "digital_model_mismatch"
    # Format evidence is product-local; page navigation and recommendations
    # must not flip a paper book to digital.
    requested_format = compact(
        request.get("format") or source.get("defaultFormat"), 16
    ).lower()
    format_text = relevance_text
    if str(structured.get("bookFormat") or "").rsplit("/", 1)[-1].casefold() == "ebook":
        format_text += " EBook"
    format_value = infer_format(format_text, source)
    if digital_retail and format_value != "digital":
        return None, "digital_product_unverified"
    if physical_marketplace and format_value != "physical":
        return None, "physical_marketplace_required"
    if (
        format_value == "digital"
        and source.get("kind") != "digital_store"
        and requested_format != "digital"
        and not DIGITAL_RE.search(relevance_text)
    ):
        return None, "digital_format_unverified"
    allowed_formats = source.get("allowedFormats") or []
    if isinstance(allowed_formats, str):
        allowed_formats = [part.strip() for part in allowed_formats.split(",") if part.strip()]
    if allowed_formats and format_value not in allowed_formats:
        return None, "format_not_allowed"
    if requested_format in {"physical", "digital"} and format_value != requested_format:
        return None, "format_filter"
    source_id = compact(request.get("sourceId") or source.get("id"), 80)
    access = digital_access(source_id, source, candidate["url"]) if format_value == "digital" else ""
    if format_value == "digital" and not access:
        return None, "digital_access_unverified"
    status_body = detail.get("body", "") if source_id in JAPAN_SOURCE_IDS | {"ruten-tw", "yahoo-tw", "shopee-tw"} else body
    status, status_evidence = status_for(status_body.replace(title, " "), operation, source_id)
    if source_id in TAIWAN_DIGITAL_RETAIL_SOURCES:
        # Ebook-format restrictions and related products can say "unavailable".
        # Selected native purchase controls/schema establish store availability.
        availability = str(structured.get("availability") or "").rsplit("/", 1)[-1].casefold()
        if availability in {"instock", "preorder", "presale", "limitedavailability", "onlineonly"}:
            status, status_evidence = "active", "selected digital retail offer"
        elif availability in {"outofstock", "soldout", "discontinued"}:
            status, status_evidence = "ended", "selected digital offer unavailable"
        else:
            status, status_evidence = "unknown", "digital availability unverified"
    if source_id == "mercari-jp" and operation == "sold_discovery" and str(structured.get("availability", "")).rsplit("/", 1)[-1].casefold() == "soldout":
        status, status_evidence = "completed", "schema.org/SoldOut"
    if source_id in JAPAN_SOURCE_IDS:
        body = status_body
    if operation in {"active_discovery", "listing_reconcile"} and status == "unknown":
        availability = str(structured.get("availability") or "").rsplit("/", 1)[-1].casefold()
        if availability in {"instock", "preorder", "presale", "limitedavailability", "onlineonly"}:
            status, status_evidence = "active", f"schema.org/{availability}"
        elif availability in {"outofstock", "soldout", "discontinued"}:
            status, status_evidence = "ended", f"schema.org/{availability}"
    require_status = bool_option(
        request.get("requireStatusEvidence"),
        operation in {"active_discovery", "sold_discovery"},
    )
    if require_status:
        if operation == "active_discovery" and status != "active":
            return None, "active_status_unverified"
        if operation == "sold_discovery" and status != "completed":
            return None, "sold_status_unverified"
    price_structured = structured
    if operation == "sold_discovery" and source_id == "yahoo-auctions-jp":
        final_price = re.search(r"(?:落札価格|現在)\s*([0-9][0-9,]*)\s*円", body)
        if not final_price:
            return None, "sold_price_unverified"
        price_structured = {"price": final_price.group(1), "currency": "JPY"}
    if operation == "sold_discovery" and source_id in {"ruten-tw", "yahoo-tw", "shopee-tw"}:
        # Candidate cards and seller descriptions cannot establish a final price.
        price_body = detail.get("body", "")
        price_body = re.split(r"商品說明|商品说明|商品詳情|賣場佈告欄|賣場公告|猜你喜歡|您可能喜歡", price_body, maxsplit=1)[0]
        closing_price = (detail.get("transaction") or {}).get("closingPrice", "")
        if source_id == "yahoo-tw" and closing_price:
            price_body = "結標價格 " + closing_price
        elif source_id == "yahoo-tw" and re.search(r"\d\s*次出價", price_body):
            return None, "sold_price_unverified"
        final_price = re.search(r"(?:成交價|成交价格|得標價|結標價格?)\s*[:：]?\s*(?:NT\$|TWD|NTD|\$)?\s*([0-9][0-9,]*(?:\.\d{1,2})?)", price_body)
        if not final_price and source_id == "ruten-tw" and status_evidence == "ended auction with masked winner":
            # On verified ended auctions, the displayed current bid is the
            # closing bid. Fixed-price asking offers never use this fallback.
            final_price = re.search(r"目前出價\s*[:：]?\s*(?:NT\$|TWD|NTD|\$)\s*([0-9][0-9,]*(?:\.\d{1,2})?)", price_body)
        if not final_price:
            return None, "sold_price_unverified"
        price_structured = {"price": final_price.group(1), "currency": "TWD"}
    expected_currency = "USD" if source_id == "apple-books-us" else "TWD"
    if source_id in {"pubu-tw", "kobo-tw", "books-com-tw"} | EXTRA_DIGITAL_SOURCES and (structured.get("price") in (None, "") or structured.get("currency") != expected_currency):
        return None, "digital_retail_price_unverified"
    price_minor, currency = parse_price(body, price_structured, source)
    adapter = resolve_adapter(source_id, source.get("adapter", ""))
    external_id = adapter.extract_external_id(candidate["url"], structured)
    if not external_id:
        return None, "missing_external_id"
    observation_id = hashlib.sha256(
        "\x00".join((source.get("id", ""), external_id, format_value, status, str(price_minor))).encode("utf-8")
    ).hexdigest()[:40]
    if format_value == "digital":
        price_type = "digital"
    elif source_id == "yahoo-auctions-jp":
        price_type = "auction_hammer" if status == "completed" else "auction_current"
    elif source_id in {"ruten-tw", "yahoo-tw", "shopee-tw"}:
        is_auction = bool(re.search(r"競標|目前出價|得標者|得標價|結標價", body))
        price_type = "auction_hammer" if status == "completed" and is_auction else "auction_current" if is_auction else "fixed"
    elif status == "completed" and AUCTION_HAMMER_RE.search(body):
        price_type = "auction_hammer"
    elif AUCTION_CURRENT_RE.search(body):
        price_type = "auction_current"
    else:
        price_type = "fixed"
    return {
        "observationId": observation_id,
        "externalId": external_id,
        "url": candidate["url"],
        "title": title,
        "sellerLocation": compact(request.get("sellerLocation"), 120),
        "condition": "Digital" if format_value == "digital" else "",
        "status": status,
        "priceMinor": price_minor,
        "currency": currency,
        "priceType": price_type,
        "format": format_value,
        "digitalAccess": access,
        "isbn": compact(structured.get("isbn"), 32),
        "publisher": compact(structured.get("publisher"), 180),
        "contentSummary": compact(structured.get("description"), 1000),
        "pageCount": int(structured.get("numberOfPages")) if str(structured.get("numberOfPages", "")).isdigit() else 0,
        "releaseDate": compact(structured.get("datePublished"), 32),
        "seriesName": compact(structured.get("isPartOf", {}).get("name"), 180) if isinstance(structured.get("isPartOf"), dict) else "",
        "editionVariant": digital_edition_variant(title) if format_value == "digital" else "",
        "shippingText": "",
        "imageUrl": compact(select_cover_url(detail.get("imageUrl"), candidate.get("imageUrl")) if source_id == "bookwalker-tw" else select_cover_url(candidate.get("imageUrl"), detail.get("imageUrl")), 500),
        "observedAt": iso_utc(),
        "statusEvidence": status_evidence,
        "timestampPrecision": "observed",
    }, "accepted"


def page_number_from_cursor(value: str, fallback: int = 1) -> int:
    value = compact(value, 500)
    if value.isdigit():
        return max(1, int(value))
    if value.startswith("{"):
        try:
            payload = json.loads(value)
            if isinstance(payload, dict) and str(payload.get("page", "")).isdigit():
                return max(1, int(payload["page"]))
        except (TypeError, ValueError, json.JSONDecodeError):
            pass
    match = re.fullmatch(r"page:(\d+)(?::offset:\d+)?", value, re.IGNORECASE)
    if match:
        return max(1, int(match.group(1)))
    match = re.fullmatch(r"v1:(\d+)", value, re.IGNORECASE)
    if match:
        return max(1, int(match.group(1)) + 1)
    return max(1, int(fallback or 1))


def resume_offset_from_cursor(value: str) -> int:
    value = compact(value, 500)
    if value.startswith("{"):
        try:
            payload = json.loads(value)
            if isinstance(payload, dict) and str(payload.get("offset", "")).isdigit():
                return max(0, int(payload["offset"]))
        except (TypeError, ValueError, json.JSONDecodeError):
            return 0
    match = re.fullmatch(r"page:\d+:offset:(\d+)", value, re.IGNORECASE)
    return max(0, int(match.group(1))) if match else 0


def resume_url_from_cursor(value: str) -> str:
    value = compact(value, 500)
    if value.startswith("{"):
        try:
            payload = json.loads(value)
            if isinstance(payload, dict):
                url = compact(payload.get("url"), 2_000)
                if url.startswith(("http://", "https://")):
                    return url
        except (TypeError, ValueError, json.JSONDecodeError):
            return ""
    if value.startswith(("http://", "https://")):
        return value
    return ""


def resume_cursor(page_number: int, offset: int, url: str = "") -> str:
    payload: dict[str, object] = {"page": max(1, int(page_number)), "offset": max(0, int(offset))}
    if url:
        payload["url"] = url
    encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    if len(encoded) <= 480:
        return encoded
    return f"page:{max(1, int(page_number))}:offset:{max(0, int(offset))}"


def bool_option(value: object, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    normalized = str(value).strip().casefold()
    if normalized in {"1", "true", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "no", "n", "off"}:
        return False
    return default


def collect(request: dict) -> dict:
    source = request.get("source") if isinstance(request.get("source"), dict) else {}
    source_id = compact(request.get("sourceId") or source.get("id"), 80)
    if not source_id:
        raise ValueError("sourceId is required")
    if str(source.get("accessMethod") or "browser").lower() != "browser":
        raise ValueError("photobook_worker accepts browser sources only; marketplace APIs are not supported")
    operation = compact(request.get("operation") or "catalog_discovery", 32).lower()
    digital_retail = source_id in TAIWAN_DIGITAL_RETAIL_SOURCES
    if digital_retail:
        if operation not in {"catalog_discovery", "active_discovery", "listing_detail"}:
            raise ValueError("digital retail scraping supports catalog, availability and current prices, not sold transactions")
        if compact(request.get("format") or source.get("defaultFormat") or "digital", 16).lower() != "digital":
            raise ValueError("retail scraping is allowed for digital editions only")
        request = {**request, "format": "digital"}
    elif is_marketplace_price_source(source_id, source):
        if compact(request.get("format") or "physical", 16).lower() != "physical":
            raise ValueError("marketplace scraping is allowed for physical photobooks only")
        request = {**request, "format": "physical"}
    retail_ids = {"books-com-tw", "bookwalker-tw", "readmoo-tw", "bookwalker-jp", "rakuten-books-jp", "surugaya", "surugaya-jp", "mandarake", "mandarake-jp", "dangdang-cn"}
    if not digital_retail and (source_id in retail_ids or str(source.get("kind", "")).strip().lower() in {"bookstore", "digital_store"}):
        raise ValueError(f"{source_id}: retail sources are excluded from scraping")
    marketplace_only = bool_option(
        request.get("marketplaceOnly", request.get("resaleOnly")),
        operation in {"active_discovery", "sold_discovery"} and not digital_retail,
    )
    if marketplace_only and not is_marketplace_price_source(source_id, source):
        raise ValueError(
            f"marketplaceOnly requires a resale/auction marketplace source; {source_id} is a fixed-price or bookstore source"
        )

    adapter = resolve_adapter(source_id, source.get("adapter", ""))
    requested_format = compact(request.get("format") or source.get("defaultFormat"), 16).lower()
    search_url = compact(request.get("searchUrl") or request.get("url"), 2_000)
    if not search_url:
        if operation == "listing_detail":
            raise ValueError("listing_detail requires request.url")
        try:
            search_url = adapter.build_search_url(
                compact(request.get("query"), 500), operation, requested_format
            )
        except AdapterConfigurationError as exc:
            raise ValueError(str(exc)) from exc

    hosts = source_hosts(source)
    ruten_auction_index = adapter.key == "ruten-tw" and operation == "sold_discovery" and urlparse(search_url).hostname == "pub.ruten.com.tw"
    if ruten_auction_index and search_url == "https://pub.ruten.com.tw/ruten20th/bid.html":
        # Exact trusted default also supports databases seeded before this host.
        hosts.add("pub.ruten.com.tw")
    if not is_allowed_url(search_url, hosts):
        raise ValueError("search URL is outside the source allow-list")
    if source_id in EXTRA_DIGITAL_SOURCES and request.get("url") and not adapter.is_result_url(search_url):
        raise ValueError("digital listing URL must identify a book in the configured storefront region")
    direct_listing = bool(request.get("url")) and adapter.is_result_url(search_url)

    page_cursor = compact(request.get("pageCursor"), 500)
    page_start = page_number_from_cursor(page_cursor, request.get("pageNumber") or 1)
    candidate_offset = resume_offset_from_cursor(page_cursor)
    try:
        max_pages = max(1, min(int(request.get("maxPages") or 1), MAX_PAGES))
        page_size = max(1, min(int(request.get("pageSize") or DEFAULT_PAGE_SIZE), MAX_CANDIDATES))
        candidate_limit = max(1, min(int(request.get("maxCandidates") or MAX_CANDIDATES), MAX_CANDIDATES))
        default_details = min(MAX_DETAIL_PAGES, DEFAULT_MAX_DETAIL_PAGES)
        max_details = max(0, min(int(request.get("maxDetailPages") or default_details), MAX_DETAIL_PAGES))
        max_items = max(1, min(int(request.get("maxItems") or MAX_BATCH_ITEMS), MAX_BATCH_ITEMS))
    except (TypeError, ValueError) as exc:
        raise ValueError("pagination and batch limits must be integers") from exc
    fetch_details = bool_option(request.get("fetchDetails"), True)
    skip_blocked_details = bool_option(request.get("skipBlockedDetails"), source_id in JAPAN_SOURCE_IDS | TAIWAN_DIGITAL_RETAIL_SOURCES | {"ruten-tw", "yahoo-tw", "shopee-tw"})
    detail_required = bool_option(request.get("detailRequired"), fetch_details)
    if fetch_details and max_details == 0:
        raise ValueError("fetchDetails requires maxDetailPages greater than zero")

    page_urls = request.get("pageUrls") or []
    if not isinstance(page_urls, list):
        page_urls = []
    limiter = NavigationRateLimiter(source, request)
    items: list[dict] = []
    seen_ids: set[str] = set()
    inspected_candidate_urls: set[str] = set()
    diagnostics: dict[str, int | str] = {
        "renderedCandidates": 0,
        "accepted": 0,
        "rejected": 0,
        "detailPages": 0,
        "detailErrors": 0,
        "pagesLoaded": 0,
        "sourceAccessMethod": "browser",
        "adapter": adapter.key,
        "targetScope": target_scope(request),
        "humanModelOnly": "true",
        "marketplaceOnly": "true" if marketplace_only else "false",
    }
    rejection_counts: dict[str, int] = {}
    warnings: list[str] = []
    if ruten_auction_index:
        diagnostics["soldDiscoveryMethod"] = "public_auction_index"
        warnings.append("Ruten sold discovery scans a public event auction index; coverage is limited to its linked lots, not all marketplace sales")
    if not requested_scope_is_people(request):
        warnings.append("human-model-only scope enforced; non-people targetScope was ignored")
    seen_fingerprints: set[str] = set()
    repeated_page = False
    next_page_possible = False
    pending_next_url = ""
    numbered_pagination = False
    resume_cursor_value = ""
    last_page_number = page_start
    started = time.monotonic()

    with redirect_stdout(sys.stderr):
        with browser_launch_lock():
            browser = launch(headless=True, timeout=browser_timeout_ms())
        try:
            search_page = browser.new_page()
            detail_page = browser.new_page() if fetch_details else None
            try:
                for offset in range(max_pages):
                    page_number = page_start + offset
                    if page_urls and page_number > len(page_urls):
                        break
                    if ruten_auction_index or ((operation == "listing_detail" or direct_listing) and page_number == page_start):
                        # An exact item URL is already a detail route. Do not
                        # append a search pagination token such as eBay's
                        # ``_pgn`` or Mercari's ``page_token`` to it.
                        page_url = search_url
                    else:
                        page_url = (
                            pending_next_url
                            if pending_next_url and not page_urls
                            else requested_page_url(
                                search_url,
                                request,
                                page_number,
                                adapter,
                                page_size,
                                cursor=page_cursor if offset == 0 else "",
                            )
                        )
                    pending_next_url = ""
                    if not is_allowed_url(page_url, hosts):
                        raise ValueError("generated page URL is outside the source allow-list")
                    navigate_page(search_page, page_url, hosts, source_id, limiter)
                    if operation == "listing_detail" or (direct_listing and page_number == page_start):
                        candidates = [{"url": page_url, "title": "", "text": "", "imageUrl": ""}]
                        rendered_next_url = ""
                    else:
                        candidates = collect_anchor_candidates(
                            search_page, page_url, hosts, adapter, MAX_CANDIDATES if (ruten_auction_index or digital_retail) else candidate_limit
                        )
                        if not candidates and adapter.key in JAPAN_SOURCE_IDS | TAIWAN_DIGITAL_RETAIL_SOURCES | {"ruten-tw", "shopee-tw", "yahoo-tw"}:
                            # The navigation shell arrives before the product
                            # grid or traffic/login redirect on these SPAs.
                            for _ in range(10):
                                search_page.wait_for_timeout(1_000)
                                ensure_rendered_page(page_body(search_page), source_id)
                                candidates = collect_anchor_candidates(search_page, page_url, hosts, adapter, MAX_CANDIDATES if (ruten_auction_index or digital_retail) else candidate_limit)
                                if candidates:
                                    break
                            if not candidates:
                                body = page_body(search_page)
                                if not re.search(r"沒有找到|找不到符合|查無|無搜尋結果|沒有符合|找到\s*0\s*筆|共\s*0\s*筆|検索結果.{0,10}0件|該当する商品.{0,10}(?:ありません|見つかりません)|no\s+(?:results|items|products)", body, re.I):
                                    raise RenderedPageError(f"{source_id}: product grid did not render and no explicit empty-results message was found")
                        rendered_next_url = next_page_url(search_page, page_url, hosts)
                    if digital_retail and not direct_listing:
                        diagnostics["retailSearchCandidates"] = int(diagnostics.get("retailSearchCandidates", 0)) + len(candidates)
                        candidates = digital_retail_candidates(candidates, request, candidate_limit)
                        if source_id == "pubu-tw" and re.search(r"Sensitive items are hidden|items hidden|隱藏敏感", page_body(search_page), re.I):
                            warnings.append("Pubu hides some sensitive search results from anonymous visitors; only public visible listings were inspected")
                    if ruten_auction_index:
                        diagnostics["auctionIndexCandidates"] = int(diagnostics.get("auctionIndexCandidates", 0)) + len(candidates)
                        candidates = ruten_sold_candidates(candidates, request, candidate_limit)
                        rendered_next_url = ""
                    diagnostics["pagesLoaded"] = int(diagnostics["pagesLoaded"]) + 1
                    diagnostics["renderedCandidates"] = int(diagnostics["renderedCandidates"]) + len(candidates)
                    fingerprint = hashlib.sha256(
                        json.dumps([candidate["url"] for candidate in candidates], sort_keys=True).encode("utf-8")
                    ).hexdigest()
                    if fingerprint in seen_fingerprints:
                        repeated_page = True
                        diagnostics["repeatedPage"] = page_number
                        warnings.append(f"repeated product-link page fingerprint at page {page_number}; stopped")
                        break
                    seen_fingerprints.add(fingerprint)
                    last_page_number = page_number
                    if not candidates:
                        # The page rendered successfully but contained no
                        # source-specific product links: a normal end-of-results
                        # condition, distinct from a challenge/empty document.
                        next_page_possible = False
                        break
                    page_full = len(candidates) >= min(candidate_limit, page_size)
                    numbered_pagination = adapter.key in {
                        "yahoo-auctions-jp",
                        "ebay",
                        "ruten-tw",
                        "yahoo-tw",
                        "shopee-tw",
                        "shopee-my",
                        "jd-cn",
                        "lazada-my",
                    } or "{page}" in search_url or (
                        bool(page_urls) and page_number < len(page_urls)
                    )
                    if ruten_auction_index:
                        numbered_pagination = False
                    next_page_possible = bool(rendered_next_url) or (page_full and numbered_pagination)
                    start_index = candidate_offset if offset == 0 else 0
                    start_index = min(start_index, len(candidates))
                    for candidate_index in range(start_index, len(candidates)):
                        candidate = candidates[candidate_index]
                        candidate_url = candidate.get("url", "")
                        if candidate_url and candidate_url in inspected_candidate_urls:
                            rejection_counts["duplicate_candidate"] = rejection_counts.get("duplicate_candidate", 0) + 1
                            continue
                        if len(items) >= max_items:
                            resume_cursor_value = resume_cursor(page_number, candidate_index, page_url)
                            next_page_possible = True
                            break
                        detail: dict = {}
                        if fetch_details:
                            if int(diagnostics["detailPages"]) >= max_details:
                                resume_cursor_value = resume_cursor(page_number, candidate_index, page_url)
                                next_page_possible = True
                                break
                            else:
                                try:
                                    detail = detail_snapshot(
                                        detail_page, candidate["url"], hosts, source_id, limiter
                                    )
                                except SourceBlockedError as exc:
                                    if not skip_blocked_details:
                                        raise
                                    diagnostics["detailPages"] = int(diagnostics["detailPages"]) + 1
                                    diagnostics["blockedDetails"] = int(diagnostics.get("blockedDetails", 0)) + 1
                                    diagnostics["rejected"] = int(diagnostics["rejected"]) + 1
                                    rejection_counts["detail_verification_required"] = rejection_counts.get("detail_verification_required", 0) + 1
                                    warnings.append(f"skipped verification-required detail: {candidate['url']}")
                                    continue
                                except DetailSnapshotError as exc:
                                    detail = {"detailError": str(exc)}
                                    diagnostics["detailErrors"] = int(diagnostics["detailErrors"]) + 1
                                diagnostics["detailPages"] = int(diagnostics["detailPages"]) + 1
                        item, reason = make_observation(
                            request, source, candidate, detail, operation, detail_required
                        )
                        if candidate_url and not detail.get("detailError"):
                            inspected_candidate_urls.add(candidate_url)
                        if item is None:
                            diagnostics["rejected"] = int(diagnostics["rejected"]) + 1
                            rejection_counts[reason] = rejection_counts.get(reason, 0) + 1
                            continue
                        if item["externalId"] in seen_ids:
                            rejection_counts["duplicate"] = rejection_counts.get("duplicate", 0) + 1
                            continue
                        seen_ids.add(item["externalId"])
                        items.append(item)
                    if resume_cursor_value:
                        warnings.append("detail or batch limit reached; the current page will be resumed")
                        break
                    if operation == "listing_detail" or direct_listing:
                        next_page_possible = False
                        break
                    if len(items) >= max_items:
                        next_page_possible = bool(rendered_next_url) or numbered_pagination
                        if rendered_next_url and not page_urls:
                            pending_next_url = rendered_next_url
                        warnings.append("batch item limit reached; the next page will be resumed")
                        break
                    if not rendered_next_url and not (page_full and numbered_pagination):
                        next_page_possible = False
                        break
                    if rendered_next_url and not page_urls:
                        pending_next_url = rendered_next_url
                    if offset + 1 >= max_pages:
                        break
            finally:
                for page in (detail_page, search_page):
                    if page is not None:
                        try:
                            page.close()
                        except Exception:
                            pass
        finally:
            try:
                browser.close()
            except Exception:
                pass

    diagnostics["accepted"] = len(items)
    if not items and int(diagnostics.get("blockedDetails", 0)):
        raise SourceBlockedError(f"BLOCKED_SOURCE: {source_id}: verification prevented qualifying detail collection; skipped restricted items")
    for reason, count in sorted(rejection_counts.items()):
        diagnostics[f"rejected_{reason}"] = count
    if int(diagnostics["detailErrors"]) > 0:
        warnings.append("some product detail pages could not be verified")
    if operation == "sold_discovery" and source_id == "ruten-tw":
        unverifiable = rejection_counts.get("sold_status_unverified", 0) + rejection_counts.get("sold_price_unverified", 0)
        diagnostics["soldVerification"] = "verified" if items else "unverified"
        if unverifiable:
            warnings.append("Ruten sold verification requires selected-listing transaction evidence and a final sale price; sales counts, purchase-history dates and current asking prices are insufficient")
    if not items:
        warnings.append("no qualifying physical or authorized digital photobooks were found")
    if rejection_counts.get("digital_access_unverified"):
        warnings.append("digital candidates without authorized store evidence were excluded")
    elapsed_ms = int((time.monotonic() - started) * 1000)
    diagnostics["runtimeMs"] = elapsed_ms
    has_more = bool(next_page_possible and not repeated_page)
    next_cursor = ""
    if has_more:
        next_cursor = (
            resume_cursor_value
            or (pending_next_url if pending_next_url and not numbered_pagination else str(last_page_number + 1))
        )
    return {
        "jobId": compact(request.get("jobId"), 120),
        "workerId": compact(request.get("workerId"), 120),
        "leaseToken": compact(request.get("leaseToken"), 100),
        "sourceId": source_id,
        "parserVersion": PARSER_VERSION,
        "retrievedAt": iso_utc(),
        "pageNumber": page_start,
        "nextCursor": next_cursor,
        "hasMore": has_more,
        "items": items,
        "warnings": warnings,
        "diagnostics": diagnostics,
    }


def main() -> None:
    request = json.load(sys.stdin)
    print(json.dumps(collect(request), ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
