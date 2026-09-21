"""Offline marketplace contract dry run.

This command deliberately does not launch a browser and does not make network
requests. It checks the URL/identity contract that must be true before a live
browser job is allowed to run: search route construction, exact rendered URL
fallbacks, source host boundaries, detail-link classification, and stable IDs.
"""

from __future__ import annotations

import json
import sys
from urllib.parse import urlparse

try:
    from marketplace_adapters import AdapterConfigurationError, resolve_adapter
except ModuleNotFoundError:  # Run from the repository root.
    from scraper.marketplace_adapters import AdapterConfigurationError, resolve_adapter


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


CASES = (
    {
        "source_id": "ebay",
        "query": "photobook",
        "formats": ("physical",),
        "operations": ("active_discovery", "sold_discovery"),
        "allowed_hosts": ("www.ebay.com",),
        "records": (
            {"url": "https://www.ebay.com/itm/277274225321", "format": "physical"},
            {"url": "https://www.ebay.com/itm/146539915626", "format": "physical"},
            {"url": "https://www.ebay.com/itm/406187793066", "format": "physical"},
        ),
    },
    {
        "source_id": "yahoo-auctions-jp",
        "query": "写真集",
        "formats": ("physical",),
        "operations": ("active_discovery", "sold_discovery"),
        "allowed_hosts": ("auctions.yahoo.co.jp",),
        "records": (
            {"url": "https://auctions.yahoo.co.jp/jp/auction/1098741404", "format": "physical"},
            {"url": "https://auctions.yahoo.co.jp/jp/auction/n1175846740", "format": "physical"},
            {"url": "https://auctions.yahoo.co.jp/jp/auction/m1035879659", "format": "physical"},
        ),
    },
    {
        "source_id": "yahoo-tw",
        "query": "寫真集",
        "formats": ("physical",),
        "operations": ("active_discovery", "sold_discovery"),
        "allowed_hosts": ("tw.bid.yahoo.com",),
        "records": (
            {"url": "https://tw.bid.yahoo.com/item/101620286146", "format": "physical"},
            {"url": "https://tw.bid.yahoo.com/item/101686572334", "format": "physical"},
            {"url": "https://tw.bid.yahoo.com/item/100280449431", "format": "physical"},
        ),
    },
    {
        "source_id": "kongfz-cn",
        "query": "写真集",
        "formats": ("physical",),
        "operations": ("active_discovery", "sold_discovery"),
        "allowed_hosts": (
            "www.kongfz.com",
            "search.kongfz.com",
            "shop.kongfz.com",
            "book.kongfz.com",
        ),
        # Kongfz search is rendered/form-driven. This is a captured public
        # category/list surface, not an invented keyword query.
        "rendered_search_urls": {
            "active_discovery": "https://shop.kongfz.com/20091/type_15/",
        },
        "records": (
            {"url": "https://book.kongfz.com/441424/7738446386/", "format": "physical"},
            {"url": "https://book.kongfz.com/285774/1824563994/", "format": "physical"},
            {"url": "https://book.kongfz.com/264608/6635198755/", "format": "physical"},
        ),
    },
    {
        "source_id": "mudah-my",
        "query": "photobook",
        "formats": ("physical",),
        "operations": ("active_discovery", "sold_discovery"),
        "allowed_hosts": ("www.mudah.my", "mudah.my"),
        "records": (
            {"url": "https://www.mudah.my/straykids-official-album-rock-ver-115658230.htm", "format": "physical"},
            {"url": "https://www.mudah.my/kang-hyewon-iz-one-beauty-cut-type-a-photobook-114344526.htm", "format": "physical"},
            {"url": "https://www.mudah.my/girls-generation-snsd-snsd-holiday-photobook-115627025.htm", "format": "physical"},
        ),
    },
    {
        "source_id": "books-com-tw",
        "query": "寫真集",
        "formats": ("physical", "digital"),
        "operations": ("catalog_discovery",),
        "allowed_hosts": ("www.books.com.tw", "search.books.com.tw"),
        "records": (
            {"url": "https://www.books.com.tw/products/E050121645", "format": "digital"},
            {"url": "https://www.books.com.tw/products/M010163044", "format": "physical"},
            {"url": "https://www.books.com.tw/products/M010169315", "format": "physical"},
        ),
    },
    {
        "source_id": "rakuten-books-jp",
        "query": "写真集",
        "formats": ("physical", "digital"),
        "operations": ("catalog_discovery",),
        "allowed_hosts": ("books.rakuten.co.jp",),
        "records": (
            {"url": "https://books.rakuten.co.jp/rb/17332219/", "format": "physical"},
            {"url": "https://books.rakuten.co.jp/rb/17493881/", "format": "physical"},
            {
                "url": "https://books.rakuten.co.jp/rk/e5df2ef2b5b531e9a66d469d99abae6e/",
                "format": "digital",
            },
        ),
    },
)


def allowed_url(url: str, hosts: tuple[str, ...]) -> bool:
    parsed = urlparse(url)
    hostname = (parsed.hostname or "").lower()
    return (
        parsed.scheme in {"http", "https"}
        and bool(hostname)
        and any(hostname == host or hostname.endswith("." + host) for host in hosts)
    )


def run_case(case: dict) -> dict:
    source_id = str(case["source_id"])
    adapter = resolve_adapter(source_id)
    allowed_hosts = tuple(case["allowed_hosts"])
    errors: list[str] = []
    probes: list[dict] = []
    rendered_search_urls = case.get("rendered_search_urls", {})

    for operation in case["operations"]:
        for format_value in case["formats"]:
            key = f"{operation}:{format_value}"
            exact_url = rendered_search_urls.get(operation)
            if exact_url:
                url = str(exact_url)
                if not allowed_url(url, allowed_hosts):
                    errors.append(f"{key}: exact rendered URL is outside the allow-list")
                probes.append({"probe": key, "status": "exact_rendered_url", "url": url})
                continue
            try:
                url = adapter.build_search_url(case["query"], operation, format_value)
            except AdapterConfigurationError as exc:
                message = str(exc)
                if operation == "sold_discovery" and source_id in {
                    "yahoo-tw",
                    "kongfz-cn",
                    "mudah-my",
                }:
                    status = "unsupported_public_history" if source_id == "mudah-my" else "requires_exact_rendered_url"
                    probes.append({"probe": key, "status": status, "reason": message})
                    continue
                errors.append(f"{key}: {message}")
                continue
            if not allowed_url(url, allowed_hosts):
                errors.append(f"{key}: built URL is outside the allow-list")
            probes.append({"probe": key, "status": "built", "url": url})

    records: list[dict] = []
    for record in case["records"]:
        url = str(record["url"])
        if not allowed_url(url, allowed_hosts):
            errors.append(f"record outside allow-list: {url}")
        if not adapter.is_result_url(url):
            errors.append(f"detail URL not recognized by adapter: {url}")
        external_id = adapter.extract_external_id(url)
        if not external_id:
            errors.append(f"detail URL has no stable external ID: {url}")
        records.append(
            {
                "url": url,
                "format": record["format"],
                "externalId": external_id,
                "recognized": adapter.is_result_url(url) and bool(external_id),
            }
        )

    return {
        "sourceId": source_id,
        "adapter": adapter.key,
        "status": "pass" if not errors else "fail",
        "probes": probes,
        "records": records,
        "errors": errors,
    }


def main() -> int:
    report = {
        "dryRun": True,
        "network": False,
        "browserLaunched": False,
        "description": "Offline URL and identity contract only; no marketplace records were fetched.",
        "marketplaces": [run_case(case) for case in CASES],
    }
    report["status"] = "pass" if all(item["status"] == "pass" for item in report["marketplaces"]) else "fail"
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
