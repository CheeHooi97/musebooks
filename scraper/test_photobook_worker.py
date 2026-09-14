"""Regression tests for the human-model-only Python scraper gate."""

import unittest

try:
    from photobook_worker import collect, make_observation
except ModuleNotFoundError:  # Run from the repository root as a unittest module.
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
        "sourceId": "rakuten-books-jp",
        "source": fixed_source,
        "operation": "active_discovery",
        "query": "model 写真集",
    }

    try:
        collect(with_error)
    except ValueError as exc:
        assert "resale/auction marketplace" in str(exc)
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
