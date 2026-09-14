"""Browser-page rules for the photobook marketplace workers.

The adapters in this module only construct and classify public, rendered
consumer URLs.  They intentionally do not contain SDK calls, marketplace API
clients, or direct HTTP requests.  A job may still provide an exact
``searchUrl`` when a marketplace's current search form is dynamic or requires
an operator-selected filter.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any
from urllib.parse import parse_qsl, quote, urlencode, urlparse, urlunparse


class AdapterConfigurationError(ValueError):
    """Raised when a source needs an exact rendered search URL."""


def _host(url: str) -> str:
    return (urlparse(url).hostname or "").lower()


def _path(url: str) -> str:
    return urlparse(url).path.lower()


def _query(url: str) -> dict[str, str]:
    return dict(parse_qsl(urlparse(url).query, keep_blank_values=True))


def _with_query(url: str, **updates: str | None) -> str:
    """Replace or remove query keys without changing the page host/path."""

    parsed = urlparse(url)
    pairs = parse_qsl(parsed.query, keep_blank_values=True)
    result: list[tuple[str, str]] = []
    seen: set[str] = set()
    for key, value in pairs:
        if key in updates:
            seen.add(key)
            replacement = updates[key]
            if replacement is not None:
                result.append((key, str(replacement)))
            continue
        result.append((key, value))
    for key, value in updates.items():
        if key not in seen and value is not None:
            result.append((key, str(value)))
    return urlunparse(parsed._replace(query=urlencode(result, doseq=True)))


def _clean_query(value: str) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _numeric_id(value: str) -> str:
    value = _clean_query(value)
    return value[:180] if value else ""


def _last_path_id(url: str) -> str:
    parts = [part for part in urlparse(url).path.rstrip("/").split("/") if part]
    if not parts:
        return ""
    value = parts[-1]
    if value.lower() in {
        "search",
        "find",
        "catalog",
        "product",
        "products",
        "item",
        "detail",
        "list",
        "listing",
    }:
        return ""
    return _numeric_id(value)


@dataclass(frozen=True)
class MarketplaceAdapter:
    """Source-specific URL and identity behavior used by the worker."""

    key: str
    aliases: tuple[str, ...]

    def build_search_url(
        self,
        query: str,
        operation: str,
        format_value: str,
    ) -> str:
        query = _clean_query(query)
        operation = _clean_query(operation).lower()
        format_value = _clean_query(format_value).lower()
        encoded = quote(query, safe="")

        if self.key == "ebay":
            if not query:
                raise AdapterConfigurationError("eBay requires request.query or request.searchUrl")
            url = f"https://www.ebay.com/sch/i.html?_nkw={encoded}"
            if operation == "sold_discovery":
                url = _with_query(url, LH_Complete="1", LH_Sold="1")
            return url

        if self.key == "yahoo-auctions-jp":
            if not query:
                raise AdapterConfigurationError("Yahoo! JAPAN Auctions requires request.query or request.searchUrl")
            if operation == "sold_discovery":
                return f"https://auctions.yahoo.co.jp/closedsearch/closedsearch/{encoded}/0/"
            return f"https://auctions.yahoo.co.jp/search/search?p={encoded}"

        if self.key == "mercari-jp":
            if not query:
                raise AdapterConfigurationError("Mercari Japan requires request.query or request.searchUrl")
            status = "sold_out" if operation == "sold_discovery" else "on_sale"
            return f"https://jp.mercari.com/search?keyword={encoded}&status={quote(status, safe='')}"

        if self.key == "rakuten-books-jp":
            if not query:
                raise AdapterConfigurationError("Rakuten Books requires request.query or request.searchUrl")
            # Rakuten's category pages separate paper books (001013) and
            # electronic books (101915). Keep that distinction in the URL.
            category = "101915" if format_value == "digital" else "001013"
            return _with_query(
                f"https://books.rakuten.co.jp/search?g={category}",
                sitem=query,
            )

        if self.key == "bookwalker-jp":
            if not query:
                return "https://bookwalker.jp/new/?qcat=8"
            raise AdapterConfigurationError(
                "BOOK☆WALKER Japan search is form-driven; submit the exact rendered searchUrl"
            )

        if self.key == "books-com-tw":
            if not query:
                raise AdapterConfigurationError("Books.com.tw requires request.query or request.searchUrl")
            return f"https://search.books.com.tw/search/query/key/{encoded}/cat/all"

        if self.key == "ruten-tw":
            if not query:
                raise AdapterConfigurationError("Ruten requires request.query or request.searchUrl")
            return f"https://www.ruten.com.tw/find/?q={encoded}"

        if self.key == "shopee-tw":
            if not query:
                raise AdapterConfigurationError("Shopee Taiwan requires request.query or request.searchUrl")
            return f"https://shopee.tw/search?keyword={encoded}"

        if self.key == "bookwalker-tw":
            raise AdapterConfigurationError(
                "BOOK☆WALKER Taiwan search is form-driven; submit the exact rendered searchUrl"
            )

        if self.key == "readmoo-tw":
            raise AdapterConfigurationError(
                "Readmoo search is form-driven; submit the exact rendered searchUrl"
            )

        if self.key == "jd-cn":
            if not query:
                raise AdapterConfigurationError("JD.com requires request.query or request.searchUrl")
            return f"https://search.jd.com/Search?keyword={encoded}&enc=utf-8"

        if self.key == "taobao-cn":
            if not query:
                raise AdapterConfigurationError("Taobao/Tmall requires request.query or request.searchUrl")
            return f"https://s.taobao.com/search?q={encoded}"

        if self.key == "xianyu-cn":
            raise AdapterConfigurationError(
                "Goofish/Xianyu search is SPA-driven; submit the exact rendered searchUrl"
            )

        if self.key == "dangdang-cn":
            raise AdapterConfigurationError(
                "Dangdang search is form-driven; submit the exact rendered searchUrl"
            )

        if self.key == "carousell-my":
            raise AdapterConfigurationError(
                "Carousell search is dynamic; submit the exact rendered searchUrl"
            )

        if self.key == "shopee-my":
            if not query:
                raise AdapterConfigurationError("Shopee Malaysia requires request.query or request.searchUrl")
            return f"https://shopee.com.my/search?keyword={encoded}"

        if self.key == "lazada-my":
            if not query:
                raise AdapterConfigurationError("Lazada Malaysia requires request.query or request.searchUrl")
            return f"https://www.lazada.com.my/catalog/?q={encoded}"

        if self.key == "rakuma-jp":
            if not query:
                raise AdapterConfigurationError("Rakuma requires request.query or request.searchUrl")
            return f"https://fril.jp/s?query={encoded}"

        if self.key == "yahoo-furima-jp":
            if not query:
                raise AdapterConfigurationError("Yahoo! Flea requires request.query or request.searchUrl")
            return f"https://paypayfleamarket.yahoo.co.jp/search/{encoded}"

        if self.key == "surugaya-jp":
            if not query:
                raise AdapterConfigurationError("Suruga-ya requires request.query or request.searchUrl")
            return f"https://www.suruga-ya.jp/search?category=70008&search_word={encoded}"

        if self.key == "mandarake-jp":
            if not query:
                raise AdapterConfigurationError("Mandarake requires request.query or request.searchUrl")
            return f"https://order.mandarake.co.jp/order/listPage/list?keyword={encoded}&lang=en"

        if self.key == "generic":
            raise AdapterConfigurationError(
                "this source has no verified default search route; submit request.searchUrl"
            )

        raise AdapterConfigurationError(f"no search builder is registered for adapter {self.key}")

    def page_url(
        self,
        url: str,
        page_number: int,
        page_size: int,
        cursor: str = "",
    ) -> str:
        """Apply the marketplace's known pagination state to a rendered URL."""

        page_number = max(1, int(page_number or 1))
        page_size = max(1, int(page_size or 1))
        if "{page}" in url:
            return url.replace("{page}", str(page_number))

        if self.key == "yahoo-auctions-jp":
            start = ((page_number - 1) * page_size) + 1
            return _with_query(url, b=str(start), n=str(page_size))
        if self.key == "ebay":
            return _with_query(url, _pgn=str(page_number), _ipg=str(page_size))
        if self.key == "mercari-jp":
            if page_number == 1 and not cursor:
                return url
            token = cursor or f"v1:{page_number - 1}"
            return _with_query(url, page_token=token)
        if self.key == "ruten-tw":
            return _with_query(url, p=str(page_number))
        if self.key in {"shopee-tw", "shopee-my"}:
            return _with_query(url, page=str(page_number - 1))
        if self.key == "jd-cn":
            # JD's public search uses page and pageSize in its rendered URL.
            return _with_query(url, page=str(page_number), pageSize=str(page_size))
        if self.key in {"rakuma-jp", "yahoo-furima-jp", "surugaya-jp", "mandarake-jp"}:
            # These surfaces expose their own next links; adding a guessed
            # parameter can silently repeat page one. The worker detects those
            # links and will use an explicit pageUrls list when supplied.
            return url
        if self.key == "lazada-my":
            return _with_query(url, page=str(page_number))
        if self.key == "generic":
            return url
        return url

    def is_result_url(self, url: str) -> bool:
        """Return true only for a likely product/listing detail link."""

        host = _host(url)
        path = _path(url)
        query = _query(url)

        if self.key == "ebay":
            return host.endswith("ebay.com") and "/itm/" in path
        if self.key == "yahoo-auctions-jp":
            return host.endswith("auctions.yahoo.co.jp") and "/jp/auction/" in path
        if self.key == "mercari-jp":
            return host.endswith("mercari.com") and (
                "/item/" in path or "/items/" in path or "/shops/product/" in path
            )
        if self.key == "rakuten-books-jp":
            return host.endswith("books.rakuten.co.jp") and (
                path.startswith("/rb/") or "/product/" in path or "/book/" in path
            )
        if self.key == "bookwalker-jp":
            return host.endswith("bookwalker.jp") and not self._is_navigation_path(path)
        if self.key == "books-com-tw":
            return host.endswith("books.com.tw") and "/products/" in path
        if self.key == "ruten-tw":
            return host.endswith("ruten.com.tw") and ("/item/" in path or "/product/" in path)
        if self.key == "shopee-tw":
            return host.endswith("shopee.tw") and self._is_shopee_path(path)
        if self.key == "bookwalker-tw":
            return host.endswith("bookwalker.com.tw") and not self._is_navigation_path(path)
        if self.key == "readmoo-tw":
            return host.endswith("readmoo.com") and not self._is_navigation_path(path)
        if self.key == "jd-cn":
            return host == "item.jd.com" and bool(re.search(r"/[^/]+\.html$", path))
        if self.key == "taobao-cn":
            return (
                (host.endswith("taobao.com") or host.endswith("tmall.com"))
                and path.endswith("/item.htm")
                and bool(query.get("id") or query.get("item_id") or query.get("itemId"))
            )
        if self.key == "xianyu-cn":
            return host.endswith("goofish.com") and (
                "/item" in path or bool(query.get("id") or query.get("itemId"))
            )
        if self.key == "dangdang-cn":
            return host.endswith("dangdang.com") and (
                "product.aspx" in path or bool(query.get("product_id") or query.get("productId"))
            )
        if self.key == "carousell-my":
            return host.endswith("carousell.com.my") and "/p/" in path
        if self.key == "shopee-my":
            return host.endswith("shopee.com.my") and self._is_shopee_path(path)
        if self.key == "lazada-my":
            return host.endswith("lazada.com.my") and (
                path.startswith("/products/") or (path.endswith(".html") and "/catalog" not in path)
            )
        if self.key == "rakuma-jp":
            return host.endswith("fril.jp") and (host == "item.fril.jp" or "/item/" in path or "/product/" in path)
        if self.key == "yahoo-furima-jp":
            return host.endswith("paypayfleamarket.yahoo.co.jp") and "/item/" in path
        if self.key == "surugaya-jp":
            return host.endswith("suruga-ya.jp") and "/product/detail/" in path
        if self.key == "mandarake-jp":
            return "mandarake" in host and ("detail" in path or "/item" in path)
        if self.key == "generic":
            return self._generic_detail_path(path, query)
        return False

    def extract_external_id(self, url: str, structured: dict[str, Any] | None = None) -> str:
        """Extract a source item ID; return empty when identity is not explicit."""

        structured = structured if isinstance(structured, dict) else {}
        host = _host(url)
        path = urlparse(url).path
        query = _query(url)

        if self.key == "ebay":
            match = re.search(r"/itm/(?:[^/]+/)?([0-9]+)(?:/|$)", path)
            if match:
                return _numeric_id(match.group(1))
        elif self.key == "yahoo-auctions-jp":
            match = re.search(r"/jp/auction/([^/?#]+)", path, re.IGNORECASE)
            if match:
                return _numeric_id(match.group(1))
        elif self.key == "mercari-jp":
            match = re.search(r"/(?:item|items|shops/product)/([^/?#]+)", path, re.IGNORECASE)
            if match:
                return _numeric_id(match.group(1))
        elif self.key == "rakuten-books-jp":
            match = re.search(r"/rb/([0-9]+)", path, re.IGNORECASE)
            if match:
                return _numeric_id(match.group(1))
        elif self.key == "books-com-tw":
            match = re.search(r"/products/([^/?#]+)", path, re.IGNORECASE)
            if match:
                return _numeric_id(match.group(1))
        elif self.key == "ruten-tw":
            match = re.search(r"/(?:item|product)/([^/?#]+)", path, re.IGNORECASE)
            if match:
                return _numeric_id(match.group(1))
        elif self.key in {"shopee-tw", "shopee-my"}:
            match = re.search(r"-i\.([0-9]+)\.([0-9]+)(?:/|$)", path, re.IGNORECASE)
            if match:
                return f"{match.group(1)}:{match.group(2)}"
            match = re.search(r"/product/([0-9]+)/([0-9]+)", path, re.IGNORECASE)
            if match:
                return f"{match.group(1)}:{match.group(2)}"
        elif self.key == "jd-cn":
            match = re.search(r"/([0-9]+)\.html$", path, re.IGNORECASE)
            if match:
                return _numeric_id(match.group(1))
        elif self.key == "taobao-cn":
            for key in ("id", "item_id", "itemId"):
                if query.get(key):
                    return _numeric_id(query[key])
        elif self.key == "xianyu-cn":
            for key in ("id", "itemId", "item_id"):
                if query.get(key):
                    return _numeric_id(query[key])
            match = re.search(r"/item/([^/?#]+)", path, re.IGNORECASE)
            if match:
                return _numeric_id(match.group(1))
        elif self.key == "dangdang-cn":
            for key in ("product_id", "productId", "id"):
                if query.get(key):
                    return _numeric_id(query[key])
        elif self.key == "carousell-my":
            match = re.search(r"/p/[^/]*-([0-9]+)(?:/|$)", path, re.IGNORECASE)
            if match:
                return _numeric_id(match.group(1))
        elif self.key == "lazada-my":
            match = re.search(r"-i([0-9]+)\.html$", path, re.IGNORECASE)
            if match:
                return _numeric_id(match.group(1))
        elif self.key == "rakuma-jp":
            match = re.search(r"(?:item\.fril\.jp/|/(?:item|product)/)([^/?#]+)", url, re.IGNORECASE)
            if match:
                return _numeric_id(match.group(1))
        elif self.key == "yahoo-furima-jp":
            match = re.search(r"/item/([^/?#]+)", path, re.IGNORECASE)
            if match:
                return _numeric_id(match.group(1))
        elif self.key == "surugaya-jp":
            for key in ("jan", "itemCode", "product_id"):
                if query.get(key):
                    return _numeric_id(query[key])
            match = re.search(r"/product/detail/([^/?#]+)", path, re.IGNORECASE)
            if match:
                return _numeric_id(match.group(1))
        elif self.key == "mandarake-jp":
            for key in ("itemCode", "itemcode", "product_id"):
                if query.get(key):
                    return _numeric_id(query[key])
        elif self.key in {"bookwalker-jp", "bookwalker-tw", "readmoo-tw"}:
            for key in ("id", "book_id", "bookId", "product_id"):
                if query.get(key):
                    return _numeric_id(query[key])

        # Do not fall back to JSON-LD ``sku``: book retailers commonly use the
        # ISBN as SKU, while ISBN identifies an edition rather than a source
        # offer. Prefer explicit product/item IDs only.
        for key in ("productID", "productId", "product_id", "itemId", "item_id", "id"):
            value = structured.get(key)
            if value not in (None, ""):
                return _numeric_id(str(value))
        for key in ("sku", "productID", "productId", "product_id", "id"):
            value = query.get(key)
            if value:
                return _numeric_id(value)

        if self.key in {"bookwalker-jp", "bookwalker-tw", "readmoo-tw"} and host:
            return _last_path_id(url)
        if self.key == "generic":
            return _last_path_id(url)
        return ""

    @staticmethod
    def _is_navigation_path(path: str) -> bool:
        return path in {"", "/"} or any(
            marker in path
            for marker in ("/search", "/new", "/category", "/catalog", "/list", "/tcl")
        )

    @staticmethod
    def _is_shopee_path(path: str) -> bool:
        return "/product/" in path or re.search(r"(?:^|/)[^/]+-i\.[0-9]+\.[0-9]+(?:/|$)", path) is not None

    @staticmethod
    def _generic_detail_path(path: str, query: dict[str, str]) -> bool:
        if query.get("id") or query.get("itemId") or query.get("product_id") or query.get("productId"):
            return True
        if path in {"", "/"}:
            return False
        return not any(
            marker in path
            for marker in ("/search", "/find", "/catalog", "/category", "/list", "/page", "/query")
        )


GENERIC_ADAPTER = MarketplaceAdapter("generic", ("generic",))


_ADAPTERS = (
    MarketplaceAdapter("ebay", ("ebay", "ebay_browser")),
    MarketplaceAdapter(
        "yahoo-auctions-jp",
        (
            "yahoo-auctions-jp",
            "yahoo_auctions_jp",
            "jdirectitems-auction-jp",
            "jdirectitems_auction_jp",
            "jdirectmarket",
            "jdirect-market",
        ),
    ),
    MarketplaceAdapter("mercari-jp", ("mercari-jp", "mercari_jp")),
    MarketplaceAdapter("rakuten-books-jp", ("rakuten-books-jp", "rakuten_books_jp")),
    MarketplaceAdapter("bookwalker-jp", ("bookwalker-jp", "bookwalker_jp")),
    MarketplaceAdapter("books-com-tw", ("books-com-tw", "books_com_tw")),
    MarketplaceAdapter("ruten-tw", ("ruten-tw", "ruten_tw")),
    MarketplaceAdapter("shopee-tw", ("shopee-tw", "shopee_tw")),
    MarketplaceAdapter("bookwalker-tw", ("bookwalker-tw", "bookwalker_tw")),
    MarketplaceAdapter("readmoo-tw", ("readmoo-tw", "readmoo_tw")),
    MarketplaceAdapter("jd-cn", ("jd-cn", "jd_cn")),
    MarketplaceAdapter("taobao-cn", ("taobao-cn", "taobao_cn", "tmall-cn", "tmall_cn")),
    MarketplaceAdapter("xianyu-cn", ("xianyu-cn", "xianyu_cn", "goofish-cn", "goofish_cn")),
    MarketplaceAdapter("dangdang-cn", ("dangdang-cn", "dangdang_cn")),
    MarketplaceAdapter("carousell-my", ("carousell-my", "carousell_my")),
    MarketplaceAdapter("shopee-my", ("shopee-my", "shopee_my")),
    MarketplaceAdapter("lazada-my", ("lazada-my", "lazada_my")),
    MarketplaceAdapter("rakuma-jp", ("rakuma", "rakuma-jp", "rakuma_jp")),
    MarketplaceAdapter("yahoo-furima-jp", ("yahoo-furima-jp", "yahoo_furima_jp")),
    MarketplaceAdapter("surugaya-jp", ("surugaya", "surugaya-jp", "surugaya_jp")),
    MarketplaceAdapter("mandarake-jp", ("mandarake", "mandarake-jp", "mandarake_jp")),
)

ADAPTER_REGISTRY = {
    alias: adapter
    for adapter in _ADAPTERS
    for alias in adapter.aliases
}


def resolve_adapter(source_id: str, adapter_name: str = "") -> MarketplaceAdapter:
    """Resolve by stable source ID first, then by the configured adapter name."""

    for value in (source_id, adapter_name):
        key = _clean_query(value).lower()
        if key in ADAPTER_REGISTRY:
            return ADAPTER_REGISTRY[key]
    return GENERIC_ADAPTER
