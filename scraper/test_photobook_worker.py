"""Regression tests for the human-model-only Python scraper gate."""

import unittest
from contextlib import nullcontext
from unittest.mock import MagicMock, patch

try:
    import photobook_worker as worker
    from photobook_worker import collect, make_observation
except ModuleNotFoundError:  # Run from the repository root as a unittest module.
    from scraper import photobook_worker as worker
    from scraper.photobook_worker import collect, make_observation


SOURCE = {
    "id": "ebay",
    "kind": "marketplace",
    "adapter": "ebay_browser",
    "defaultFormat": "physical",
    "allowedFormats": ["physical"],
    "accessMethod": "browser",
    "baseUrl": "https://www.ebay.com",
    "allowedHosts": ["www.ebay.com"],
    "region": "global",
    "locale": "en-US",
}


def candidate(title: str) -> dict:
    return {
        "url": "https://www.ebay.com/itm/123456789012",
        "title": title,
        "text": title,
        "imageUrl": "",
    }


def detail(body: str, *, author: str = "", category: str = "") -> dict:
    return {
        "body": body,
        "structured": {
            "author": author,
            "category": category,
        },
        "metadata": {},
    }


def detail_with_title(body: str, title: str) -> dict:
    value = detail(body)
    value["metadata"]["name"] = title
    return value


def request(**overrides: object) -> dict:
    value = {
        "sourceId": "ebay",
        "format": "physical",
        "requireStatusEvidence": True,
    }
    value.update(overrides)
    return value


def load_tests(loader: unittest.TestLoader, tests: unittest.TestSuite, pattern: str | None):
    """Expose the lightweight function tests without requiring pytest."""

    functions = (
        test_default_scope_accepts_a_model_photobook,
        test_photographer_monograph_is_rejected_even_when_marked_known,
        test_person_keyword_alone_cannot_bypass_model_scope,
        test_non_human_model_merchandise_is_rejected,
        test_fixed_price_source_is_not_allowed_for_resale_jobs,
        test_verified_model_keyword_allows_a_name_only_title,
        test_detail_metadata_title_is_used_for_scope_matching,
        test_ended_listing_is_not_active,
        test_seller_sales_counter_is_not_a_completed_sale,
        test_sold_listing_requires_sale_evidence,
        test_pre_detail_candidate_skip_is_not_a_detail_error,
    )
    return unittest.TestSuite(unittest.FunctionTestCase(function) for function in functions)


def test_default_scope_accepts_a_model_photobook() -> None:
    item, reason = make_observation(
        request(),
        SOURCE,
        candidate("Alice Smith Model Photobook"),
        detail("Buy It Now USD 49.99 Hardcover"),
        "active_discovery",
    )

    assert reason == "accepted"
    assert item is not None
    assert item["status"] == "active"


def test_photographer_monograph_is_rejected_even_when_marked_known() -> None:
    item, reason = make_observation(
        request(
            knownPhotobook=True,
            expectedTitle="Hong Kong Street Trilogy",
            personKeywords=["Photographer Name"],
            targetScope="photography",
        ),
        SOURCE,
        candidate("Hong Kong Street Trilogy Photobook"),
        detail("Buy It Now USD 169.99 Hardcover", author="Photographer Name", category="Photography"),
        "active_discovery",
    )

    assert item is None
    assert reason == "not_in_people_scope"


def test_person_keyword_alone_cannot_bypass_model_scope() -> None:
    item, reason = make_observation(
        request(personKeywords=["Photographer Name"]),
        SOURCE,
        candidate("Hong Kong Street Trilogy Photobook"),
        detail("Buy It Now USD 169.99 Hardcover", author="Photographer Name", category="Photography"),
        "active_discovery",
    )

    assert item is None
    assert reason == "not_in_people_scope"


def test_non_human_model_merchandise_is_rejected() -> None:
    item, reason = make_observation(
        request(),
        SOURCE,
        candidate("Scale Model Photobook Catalog"),
        detail("Buy It Now USD 29.99 Hardcover"),
        "active_discovery",
    )

    assert item is None
    assert reason == "not_a_photobook"


def test_fixed_price_source_is_not_allowed_for_resale_jobs() -> None:
    fixed_source = {
        **SOURCE,
        "id": "rakuten-books-jp",
        "kind": "bookstore",
        "adapter": "rakuten_books_jp",
    }
    with_error = {
        "marketplaceOnly": True,
        "sourceId": "rakuten-books-jp",
        "source": fixed_source,
        "operation": "active_discovery",
        "query": "model 写真集",
    }

    try:
        collect(with_error)
    except ValueError as exc:
        assert "retail sources are excluded" in str(exc)
    else:
        raise AssertionError("expected fixed-price source to be rejected")


def test_verified_model_keyword_allows_a_name_only_title() -> None:
    item, reason = make_observation(
        request(
            humanModelKeywords=["Alice Smith"],
            knownPhotobook=True,
            expectedTitle="Alice Smith 2025 Collection",
        ),
        SOURCE,
        candidate("Alice Smith 2025 Collection"),
        detail("Buy It Now USD 29.99 Paperback", author="Alice Smith"),
        "active_discovery",
    )

    assert reason == "accepted"
    assert item is not None


def test_detail_metadata_title_is_used_for_scope_matching() -> None:
    item, reason = make_observation(
        request(),
        SOURCE,
        candidate(""),
        detail_with_title("Buy It Now USD 29.99 Paperback", "Alice Smith Model Photobook"),
        "active_discovery",
    )

    assert reason == "accepted"
    assert item is not None
    assert item["title"] == "Alice Smith Model Photobook"


def test_ended_listing_is_not_active() -> None:
    item, reason = make_observation(
        request(),
        SOURCE,
        candidate("Alice Smith Model Photobook"),
        detail("USD 49.99 Hardcover Auction ended"),
        "active_discovery",
    )

    assert item is None
    assert reason == "active_status_unverified"


def test_seller_sales_counter_is_not_a_completed_sale() -> None:
    item, reason = make_observation(
        request(),
        SOURCE,
        candidate("Alice Smith Model Photobook"),
        detail("Buy It Now USD 49.99 Hardcover 4 items sold by this seller"),
        "sold_discovery",
    )

    assert item is None
    assert reason == "sold_status_unverified"


def test_sold_listing_requires_sale_evidence() -> None:
    item, reason = make_observation(
        request(),
        SOURCE,
        candidate("Alice Smith Model Photobook"),
        detail("USD 49.99 Hardcover Auction ended"),
        "sold_discovery",
    )
    assert item is None
    assert reason == "sold_status_unverified"

    item, reason = make_observation(
        request(),
        SOURCE,
        candidate("Alice Smith Model Photobook"),
        detail("SOLD USD 49.99 Hardcover"),
        "sold_discovery",
    )
    assert reason == "accepted"
    assert item is not None
    assert item["status"] == "completed"


def test_pre_detail_candidate_skip_is_not_a_detail_error() -> None:
    browser = MagicMock()
    browser.new_page.side_effect = [MagicMock(), MagicMock()]
    request_data = {
        "sourceId": SOURCE["id"],
        "source": SOURCE,
        "format": "physical",
        "operation": "active_discovery",
        "query": "Alice Smith photobook",
        "humanModelKeywords": ["Alice Smith"],
        "maxPages": 1,
        "pageSize": 1,
        "maxCandidates": 1,
        "maxDetailPages": 1,
        "maxItems": 1,
    }

    with (
        patch.object(worker, "browser_launch_lock", return_value=nullcontext()),
        patch.object(worker, "launch", return_value=browser),
        patch.object(worker, "navigate_page"),
        patch.object(worker, "collect_anchor_candidates", return_value=[candidate("Unrelated card")]),
        patch.object(worker, "next_page_url", return_value=""),
        patch.object(
            worker,
            "detail_snapshot",
            side_effect=worker.CandidateSkippedBeforeDetail("filtered before navigation"),
        ),
    ):
        result = collect(request_data)

    assert result["diagnostics"]["detailPages"] == 0
    assert result["diagnostics"]["detailErrors"] == 0
    assert result["diagnostics"]["preDetailSkipped"] == 1
    assert result["diagnostics"]["rejected"] == 1
