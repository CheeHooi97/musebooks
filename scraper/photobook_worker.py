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
from contextlib import contextmanager, redirect_stdout
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from urllib.parse import urljoin, urlparse

from cloakbrowser import launch
from marketplace_adapters import (
    AdapterConfigurationError,
    MarketplaceAdapter,
    resolve_adapter,
)


PARSER_VERSION = "python-photobook-browser-v3"
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
    r"写真集|フォトブック|寫真集|寫真書|攝影集|摄影集|攝影書|摄影书|"
    r"照片集|写真本|写真帖|寫真帖|写真フォトブック|写真画集|攝影畫冊|摄影画册|"
    r"攝影作品集|摄影作品集|影像集|影像作品集|相冊|相簿|画册|畫冊)",
    re.IGNORECASE,
)
STRONG_PHOTOBOOK_SIGNAL_RE = re.compile(
    r"(?:\bphoto\s*book\b|\bphotobook\b|\bphotography\s*book\b|"
    r"\bphoto(?:graphic)?\s+(?:essay|monograph|album)\b|"
    r"写真集|フォトブック|寫真集|寫真書|攝影集|摄影集|攝影書|摄影书|照片集|"
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
    r"可購買|可购买|可下單|可下单|可訂購|可订购|在售|入札受付中|即決)",
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
    r"\bauction\s+ended\b|\bended\b|終了|已結標|已结标|拍賣結束|拍卖结束|已售|"
    r"售出|下架|無貨|无货|缺貨|缺货|販売終了|在庫なし)",
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
)
DETAIL_NOT_FOUND_MARKERS = (
    "page not found",
    "item not found",
    "product not found",
    "商品が見つかりません",
    "商品不存在",
    "商品不存在或已下架",
    "頁面不存在",
    "页面不存在",
)
VERIFIED_DIGITAL_SOURCES = {
    "bookwalker-jp",
    "bookwalker-tw",
    "readmoo-tw",
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
    if redirected_url and not is_allowed_url(redirected_url, hosts):
        raise RenderedPageError(f"source redirected outside the allow-list: {redirected_url}")
    try:
        page.wait_for_timeout(750)
    except Exception:
        pass
    body = page_body(page)
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
        count = min(anchors.count(), max(limit * 5, limit))
    except Exception:
        return candidates
    for index in range(count):
        anchor = anchors.nth(index)
        href = read_attribute(anchor, "href")
        if not href:
            continue
        link = urljoin(search_url, href).split("#", 1)[0]
        if link in seen or not is_allowed_url(link, hosts) or not adapter.is_result_url(link):
            continue
        title = read_attribute(anchor, "aria-label") or read_attribute(anchor, "title")
        text = read_text(anchor, timeout=1_000)
        label = compact(title or text, 800)
        if len(label) < 4:
            continue
        seen.add(link)
        candidates.append({"url": link, "title": label, "text": text, "imageUrl": image_from_locator(anchor)})
        if len(candidates) >= limit:
            break
    return candidates


def next_page_url(page, search_url: str, hosts: set[str]) -> str:
    """Return a rendered source-local Next link, if one exists."""

    try:
        anchors = page.locator("a")
        count = min(anchors.count(), 300)
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
                    "sku": compact(value.get("sku") or value.get("productID"), 180),
                    "productID": compact(value.get("productID"), 180),
                    "image": value.get("image") or "",
                    "price": offers.get("price"),
                    "currency": compact(offers.get("priceCurrency"), 12),
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
    return {
        "body": body,
        "structured": structured,
        "metadata": metadata,
        "imageUrl": metadata.get("image") or structured.get("image") or "",
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


def digital_access(source_id: str, source: dict, url: str) -> str:
    """Authorize only configured first-party/e-book storefront sources.

    Words such as ``official`` or ``publisher`` in a seller description are
    not provenance. The source ID and its allowed host are the trust boundary;
    the Go API applies the same allow-list before persistence.
    """

    if source_id not in VERIFIED_DIGITAL_SOURCES:
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
    r"網紅|网红|寫真女星|写真女優|水著)",
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


def subject_evidence_text(title: str, candidate: dict, structured: dict) -> str:
    structured = structured if isinstance(structured, dict) else {}
    return compact(
        " ".join(
            (
                title,
                candidate.get("title", ""),
                candidate.get("text", ""),
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
) -> bool:
    """Allow only human-model/person photobooks.

    Exact-title ``knownPhotobook`` matching only relaxes the generic
    photobook-word check. It must never bypass the human-model subject gate.
    """

    scope = target_scope(request)
    subject = subject_evidence_text(title, candidate, structured)
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


def status_for(text: str, operation: str) -> tuple[str, str]:
    value = compact(text, 30_000)
    if operation in {"active_discovery", "listing_reconcile"}:
        evidence = ACTIVE_RE.search(value)
        if evidence:
            return "active", compact(evidence.group(0))
        evidence = ENDED_RE.search(value)
        if evidence:
            return "ended", compact(evidence.group(0))
        return "unknown", "no explicit availability evidence"
    if operation == "sold_discovery":
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
    return source_id not in FIXED_PRICE_SOURCE_IDS


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
    # Navigation and recommendation modules on detail pages often contain
    # unrelated merchandise. Use the candidate title/description as the
    # relevance decision, while retaining the full rendered body for price
    # and availability evidence.
    relevance_text = compact(" ".join((title, candidate.get("text", ""), structured.get("description", ""))), 10_000)
    known_match = known_photobook_match(request, title, body, structured)
    if not looks_like_photobook(relevance_text) and not known_match:
        return None, "not_a_photobook"
    if not matches_target_scope(request, title, candidate, structured, known_match):
        return None, f"not_in_{target_scope(request)}_scope"
    # Format evidence is product-local whenever possible. Only use a bounded
    # prefix of the rendered body as a fallback; the footer may advertise
    # unrelated e-book categories and must not flip a paper book to digital.
    requested_format = compact(
        request.get("format") or source.get("defaultFormat"), 16
    ).lower()
    # On bookstore detail pages the rendered body can contain unrelated
    # e-book navigation, recommendations, or a paper/e-book counterpart. Keep
    # physical jobs product-local; digital jobs and first-party digital stores
    # need the detail body to expose the selected electronic edition.
    format_text = relevance_text
    if source.get("kind") == "digital_store" or requested_format == "digital":
        format_text = compact(" ".join((relevance_text, body[:4_000])), 14_000)
    format_value = infer_format(format_text, source)
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
    status, status_evidence = status_for(body, operation)
    require_status = bool_option(
        request.get("requireStatusEvidence"),
        operation in {"active_discovery", "sold_discovery"},
    )
    if require_status:
        if operation == "active_discovery" and status != "active":
            return None, "active_status_unverified"
        if operation == "sold_discovery" and status != "completed":
            return None, "sold_status_unverified"
    price_minor, currency = parse_price(body, structured, source)
    adapter = resolve_adapter(source_id, source.get("adapter", ""))
    external_id = adapter.extract_external_id(candidate["url"], structured)
    if not external_id:
        return None, "missing_external_id"
    observation_id = hashlib.sha256(
        "\x00".join((source.get("id", ""), external_id, format_value, status, str(price_minor))).encode("utf-8")
    ).hexdigest()[:40]
    if format_value == "digital":
        price_type = "digital"
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
        "shippingText": "",
        "imageUrl": compact(candidate.get("imageUrl") or detail.get("imageUrl"), 500),
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
    marketplace_only = bool_option(
        request.get("marketplaceOnly") or request.get("resaleOnly"),
        operation in {"active_discovery", "sold_discovery"},
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
    if not is_allowed_url(search_url, hosts):
        raise ValueError("search URL is outside the source allow-list")
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
    detail_required = bool_option(request.get("detailRequired"), fetch_details)
    if fetch_details and max_details == 0:
        raise ValueError("fetchDetails requires maxDetailPages greater than zero")

    page_urls = request.get("pageUrls") or []
    if not isinstance(page_urls, list):
        page_urls = []
    limiter = NavigationRateLimiter(source, request)
    items: list[dict] = []
    seen_ids: set[str] = set()
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
                    if (operation == "listing_detail" or direct_listing) and page_number == page_start:
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
                            search_page, page_url, hosts, adapter, candidate_limit
                        )
                        rendered_next_url = next_page_url(search_page, page_url, hosts)
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
                    page_full = len(candidates) >= candidate_limit
                    numbered_pagination = adapter.key in {
                        "yahoo-auctions-jp",
                        "ebay",
                        "mercari-jp",
                        "ruten-tw",
                        "shopee-tw",
                        "shopee-my",
                        "jd-cn",
                        "lazada-my",
                    } or "{page}" in search_url or (
                        bool(page_urls) and page_number < len(page_urls)
                    )
                    next_page_possible = bool(rendered_next_url) or (page_full and numbered_pagination)
                    start_index = candidate_offset if offset == 0 else 0
                    start_index = min(start_index, len(candidates))
                    for candidate_index in range(start_index, len(candidates)):
                        candidate = candidates[candidate_index]
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
                                except SourceBlockedError:
                                    raise
                                except DetailSnapshotError as exc:
                                    detail = {"detailError": str(exc)}
                                    diagnostics["detailErrors"] = int(diagnostics["detailErrors"]) + 1
                                diagnostics["detailPages"] = int(diagnostics["detailPages"]) + 1
                        item, reason = make_observation(
                            request, source, candidate, detail, operation, detail_required
                        )
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
    for reason, count in sorted(rejection_counts.items()):
        diagnostics[f"rejected_{reason}"] = count
    if int(diagnostics["detailErrors"]) > 0:
        warnings.append("some product detail pages could not be verified")
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
