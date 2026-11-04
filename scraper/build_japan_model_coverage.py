"""Build a read-only per-model/source report from saved capture and import files."""
import argparse
import csv
import hashlib
import json
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent.parent
QUEUE_ROOT = ROOT / "scraper/japan-models"
STATE_FILES = {
    "yahoo-auctions-jp": ("physical-state.json", "physical"),
    "yahoo-furima-jp": ("physical-state.json", "physical"),
    "rakuma": ("physical-state.json", "physical"),
    "grajapa-jp": ("digital-state.json", "digital"),
    "rakuten-kobo-jp": ("kobo-state.json", "kobo"),
    "wani-books-jp": ("publisher-wani-state.json", "wani"),
}
COVERAGE_KEYS = {
    "grajapa-jp": "grajapa",
    "rakuten-kobo-jp": "kobo",
    "wani-books-jp": "wani",
}


def read_json(path, default=None):
    path = Path(path)
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8-sig"))


def stable_json(value):
    if isinstance(value, list):
        return "[" + ", ".join(stable_json(item) for item in value) + "]"
    if isinstance(value, dict):
        fields = sorted(value.items())
        return "{" + ", ".join(
            json.dumps(key, ensure_ascii=False) + ": " + stable_json(item)
            for key, item in fields
        ) + "}"
    return json.dumps(value, ensure_ascii=False)


def item_rows(value):
    if isinstance(value, dict):
        return list(value.values())
    return value if isinstance(value, list) else []


def set_observation_range(result, items, source_id):
    observed = sorted(
        item.get("observedAt", "") for item in item_rows(items)
        if item.get("observedAt") and item.get("sourceId", source_id) == source_id
    )
    if observed:
        result["earliestObservedAt"] = observed[0]
        result["latestObservedAt"] = observed[-1]


def imported_associations(person_id, records, checkpoint):
    imported = 0
    for record in records:
        items = record.get("batch", {}).get("items", [])
        if not items:
            continue
        digest = hashlib.sha256(stable_json(record).encode("utf-8")).hexdigest()
        if all(checkpoint.get(f"{person_id}:{record.get('source', {}).get('id', '')}:{item.get('externalId', '')}") == digest for item in items):
            imported += len(items)
    return imported


def normalized_name(value):
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", str(value or "")).lower())


def name_values(value):
    values = []
    for item in value if isinstance(value, list) else str(value or "").split(","):
        values.extend(item if isinstance(item, list) else [item])
    return {normalized_name(item) for item in values if normalized_name(item)}


def audit_missing_associations(queue_row, model_data, homepage_model):
    """Classify saved gaps using exact verified names, without changing credits."""
    verified_names = name_values([
        queue_row.get("name", ""), queue_row.get("originalName", ""), queue_row.get("englishName", ""),
        model_data.get("canonical_public_name", ""), model_data.get("original_name", ""),
        model_data.get("english_name", ""), model_data.get("aliases", ""),
        *[item.get("name", "") for item in (model_data.get("careerNameEvidence") or [])],
        *[
            name
            for evidence in (model_data.get("japan_release_evidence") or [])
            for name in (evidence.get("credited_name", ""), evidence.get("credited_english_name", ""))
        ],
    ])
    categories = ("noLiveCreditEvidence", "liveCreditNoVerifiedNameMatch", "verifiedNameInLiveCredit")
    result = {"total": 0, **{key: 0 for key in categories}, "bySource": {}}
    for item in homepage_model.get("missingImportedManifestOffers", []):
        live_credits = name_values(item.get("liveCredits", ""))
        if not live_credits and not item.get("liveWorkSlug"):
            category = "noLiveCreditEvidence"
        elif verified_names.intersection(live_credits):
            category = "verifiedNameInLiveCredit"
        else:
            category = "liveCreditNoVerifiedNameMatch"
        source = item.get("sourceId") or "unknown"
        source_counts = result["bySource"].setdefault(source, {key: 0 for key in categories})
        result["total"] += 1
        result[category] += 1
        source_counts[category] += 1
    return result


def aggregate_association_audits(audits):
    totals = {"total": 0, "noLiveCreditEvidence": 0,
              "liveCreditNoVerifiedNameMatch": 0, "verifiedNameInLiveCredit": 0, "bySource": {}}
    for audit in audits:
        for key in ("total", "noLiveCreditEvidence", "liveCreditNoVerifiedNameMatch", "verifiedNameInLiveCredit"):
            totals[key] += audit.get(key, 0)
        for source, counts in audit.get("bySource", {}).items():
            source_totals = totals["bySource"].setdefault(source, {
                "noLiveCreditEvidence": 0, "liveCreditNoVerifiedNameMatch": 0, "verifiedNameInLiveCredit": 0,
            })
            for key, count in counts.items():
                source_totals[key] += count
    return totals


def source_capture(root, model_dir, source_id, policy, listing_capture=None):
    location = STATE_FILES.get(source_id)
    result = {
        "automationStatus": policy.get("automationStatus", "permission_unverified"),
        "searchStatus": "not_attempted",
        "pagesObserved": 0,
        "queriesObserved": 0,
        "offersCaptured": 0,
        "errors": 0,
        "detailErrors": 0,
        "pendingDetails": 0,
        "earliestObservedAt": "",
        "latestObservedAt": "",
        "failureSamples": [],
        "searchTerms": [],
        "bibliographicRecords": 0,
        "photobookKeywordCandidates": 0,
        "truncatedQueries": 0,
        "failureStatusCounts": {},
    }
    if source_id == "ndl-national-bibliography-jp":
        ndl_capture = read_json(
            root / "research_notes/japan-ndl-national-bibliography" / (model_dir.name + ".json"),
            {},
        ) or {}
        if ndl_capture:
            result["searchStatus"] = ndl_capture.get("status", "unknown")
            result["queriesObserved"] = ndl_capture.get("queryCount", 0)
            result["pagesObserved"] = ndl_capture.get("pagesObserved", 0)
            result["errors"] = ndl_capture.get("requestErrors", 0)
            result["truncatedQueries"] = ndl_capture.get("truncatedQueries", 0)
            result["bibliographicRecords"] = ndl_capture.get("bibliographicRecordsUnique", 0)
            result["photobookKeywordCandidates"] = ndl_capture.get("photobookKeywordCandidates", 0)
            result["earliestObservedAt"] = ndl_capture.get("earliestObservedAt", ndl_capture.get("observedAt", ""))
            result["latestObservedAt"] = ndl_capture.get("latestObservedAt", ndl_capture.get("observedAt", ""))
            result["metadataLicense"] = ndl_capture.get("metadataLicense", "")
            result["searchTerms"] = [term.get("name", "") for term in ndl_capture.get("identityNamesSearched", [])]
            result["queryRuns"] = [
                {"query": query.get("term", ""), "status": query.get("status", "unknown"),
                 "pagesObserved": int(query.get("status") == "ok"),
                 "observedAt": query.get("observedAt", ""),
                 "httpStatus": query.get("httpStatus", ""),
                 "requestUrl": query.get("requestUrl", ""),
                 "error": query.get("error", ""),
                 "totalResults": query.get("totalResults", ""),
                 "paginationStatus": query.get("paginationStatus", ""),
                 "truncatedAtProviderLimit": bool(query.get("truncatedAtProviderLimit", False))}
                for query in ndl_capture.get("queries", [])
            ]
            for query in ndl_capture.get("queries", []):
                if query.get("status") == "ok":
                    continue
                failure_key = f"http_{query['httpStatus']}" if query.get("httpStatus") else query.get("status", "unknown")
                result["failureStatusCounts"][failure_key] = result["failureStatusCounts"].get(failure_key, 0) + 1
            result["pageUrlSamples"] = sorted({
                record.get("sourcePageUrl", "") for record in ndl_capture.get("records", [])
                if record.get("sourcePageUrl")
            })[:3]
            result["failureSamples"] = [
                {"query": query.get("term", ""), "status": query.get("status", "unknown"),
                 "httpStatus": query.get("httpStatus", ""), "error": query.get("error", "")}
                for query in ndl_capture.get("queries", []) if query.get("status") != "ok"
            ][:3]
        return result
    coverage = (listing_capture or {}).get("coverage", {})
    coverage_key = COVERAGE_KEYS.get(source_id)
    if source_id == "yahoo-auctions-jp" or source_id == "yahoo-furima-jp" or source_id == "rakuma":
        physical = coverage.get("physical", {})
        runs = [run for run in physical.get("runs", {}).values() if run.get("sourceId") == source_id]
        if runs:
            result["queriesObserved"] = len(runs)
            result["pagesObserved"] = sum(
                batch.get("diagnostics", {}).get("pagesLoaded", 0)
                for run in runs for batch in run.get("batches", [])
            )
            result["detailErrors"] = sum(
                batch.get("diagnostics", {}).get("detailErrors", 0)
                for run in runs for batch in run.get("batches", [])
            )
            statuses = {run.get("status", "unknown") for run in runs}
            if statuses.intersection({"source_failed", "pagination_stalled"}):
                result["searchStatus"] = "failed_or_stalled"
            elif statuses.intersection({"running", "pending", "interrupted"}):
                result["searchStatus"] = "incomplete"
            elif "source_blocked" in statuses:
                result["searchStatus"] = "source_blocked"
            elif "query_relevance_exhausted" in statuses:
                result["searchStatus"] = "relevance_limited"
            elif statuses.issubset({"public_search_exhausted", "ambiguous_alias_skipped"}):
                result["searchStatus"] = "public_search_exhausted"
            result["errors"] = sum(bool(run.get("error")) for run in runs)
            for run in runs:
                if run.get("error"):
                    result["failureSamples"].append({"query": run.get("query", ""), "error": str(run["error"])[:400]})
                failures = sum(batch.get("diagnostics", {}).get("detailErrors", 0) for batch in run.get("batches", []))
                if failures:
                    result["failureSamples"].append({"query": run.get("query", ""), "failedDetailPages": failures})
            result["searchTerms"] = sorted({run.get("query", "") for run in runs if run.get("query")})
            result["queryRuns"] = [
                {
                    "query": run.get("query", ""),
                    "status": run.get("status", "unknown"),
                    "pagesObserved": sum(batch.get("diagnostics", {}).get("pagesLoaded", 0) for batch in run.get("batches", [])),
                    "detailErrors": sum(batch.get("diagnostics", {}).get("detailErrors", 0) for batch in run.get("batches", [])),
                    "hasMoreAtStop": bool((run.get("batches") or [{}])[-1].get("hasMore", False)),
                    "nextCursorAtStop": (run.get("batches") or [{}])[-1].get("nextCursor", ""),
                }
                for run in runs
            ]
            result["offersCaptured"] = sum(
                1 for item in item_rows((listing_capture or {}).get("items", []))
                if item.get("sourceId") == source_id
            )
    if coverage_key:
        state = coverage.get(coverage_key)
        if state:
            pages = state.get("pages", [])
            result["pagesObserved"] = len(pages)
            queries = state.get("searchedNameQueries", [])
            result["queriesObserved"] = len(queries)
            result["searchTerms"] = sorted(set(queries))
            result["searchStatus"] = state.get("status", "unknown")
            errors = state.get("errors", {})
            result["errors"] = len(errors) + int(bool(state.get("error")))
            result["pendingDetails"] = len(state.get("pendingNameQueries", [])) + len(state.get("pendingTitleReviews", []))
            if isinstance(errors, dict):
                result["failureSamples"] = [
                    {"url": str(key)[:400], "error": str(value)[:400]}
                    for key, value in list(errors.items())[:3]
                ]
            elif isinstance(errors, list):
                result["failureSamples"] = [{"error": str(value)[:400]} for value in errors[:3]]
            if state.get("error"):
                result["failureSamples"].append({"error": str(state["error"])[:400]})
            result["offersCaptured"] = sum(
                1 for item in item_rows((listing_capture or {}).get("items", []))
                if item.get("sourceId") == source_id
            )
            if state.get("verifiedPrintEditions") is not None:
                result["verifiedPrintEditions"] = state.get("verifiedPrintEditions", 0)
            rejected = state.get("rejected", {})
            result["candidatesRejectedDuringVerification"] = len(rejected) if isinstance(rejected, (dict, list)) else 0
            result["queryRuns"] = [{"query": term, "status": result["searchStatus"], "pagesObserved": len(pages)} for term in result["searchTerms"]]
            result["pageUrlSamples"] = pages[:3]
            result["failureSamples"] = result["failureSamples"][:3]
            set_observation_range(result, (listing_capture or {}).get("items", []), source_id)
            return result
    if source_id == "publisher-bibliography-jp":
        editions = read_json(model_dir / "physical-books.json", {}) or {}
        books = editions.get("books", [])
        result["searchStatus"] = "manual_records_present" if books else "not_attempted"
        result["offersCaptured"] = 0
        result["verifiedBibliographicRecords"] = len(books)
        result["pageUrlSamples"] = sorted({book.get("metadataSourceUrl", "") for book in books if book.get("metadataSourceUrl")})[:3]
        result["bibliographicRecordSamples"] = [
            {"title": book.get("title", ""), "isbn": book.get("isbn", ""), "sourceUrl": book.get("metadataSourceUrl", "")}
            for book in books[:3]
        ]
        return result
    if not location:
        return result
    filename, kind = location
    state = read_json(model_dir / filename)
    if not state:
        return result
    if kind == "physical":
        runs = [run for run in state.get("runs", {}).values() if run.get("sourceId") == source_id]
        result["queriesObserved"] = len(runs)
        diagnostics = [batch.get("diagnostics", {}) for run in runs for batch in run.get("batches", [])]
        result["pagesObserved"] = sum(batch.get("pagesLoaded", 0) for batch in diagnostics)
        result["detailErrors"] = sum(batch.get("detailErrors", 0) for batch in diagnostics)
        statuses = {run.get("status", "unknown") for run in runs}
        if runs:
            if statuses.intersection({"source_failed", "pagination_stalled"}):
                result["searchStatus"] = "failed_or_stalled"
            elif statuses.intersection({"running", "pending", "interrupted"}):
                result["searchStatus"] = "incomplete"
            elif "source_blocked" in statuses:
                result["searchStatus"] = "source_blocked"
            elif "query_relevance_exhausted" in statuses:
                result["searchStatus"] = "relevance_limited"
            elif statuses.issubset({"public_search_exhausted", "ambiguous_alias_skipped"}):
                result["searchStatus"] = "public_search_exhausted"
        result["errors"] = sum(bool(run.get("error")) for run in runs)
        result["pendingDetails"] = sum(1 for detail in state.get("pendingDetails", {}).values()
                                        if detail.get("sourceId") == source_id)
        result["pendingDetails"] += result["detailErrors"]
        for run in runs:
            if run.get("error"):
                result["failureSamples"].append({"query": run.get("query", ""), "error": str(run["error"])[:400]})
        for run in runs:
            count = sum(batch.get("diagnostics", {}).get("detailErrors", 0) for batch in run.get("batches", []))
            if count:
                result["failureSamples"].append({"query": run.get("query", ""), "failedDetailPages": count})
        result["searchTerms"] = sorted({run.get("query", "") for run in runs if run.get("query")})
        result["offersCaptured"] = sum(
            1 for item in state.get("items", {}).values() if item.get("sourceId") == source_id
        )
    else:
        pages = state.get("pages", [])
        result["pagesObserved"] = len(pages)
        result["queriesObserved"] = len(state.get("pendingSearches", [])) + len({
            url.split("?", 1)[0] + "?" + url.split("?", 1)[1].split("&", 1)[0]
            for url in pages if "?" in url
        })
        parameter = {"digital": "keyword", "kobo": "pname", "wani": "tag"}[kind]
        result["searchTerms"] = sorted({
            value for url in pages for value in parse_qs(urlparse(url).query).get(parameter, [])
        })
        result["searchStatus"] = state.get("status", "unknown")
        result["errors"] = len(state.get("errors", {})) + int(bool(state.get("error")))
        result["pendingDetails"] = len(state.get("pendingDetails", {}))
        result["offersCaptured"] = len(state.get("items", {}))
        errors = state.get("errors", {})
        if isinstance(errors, dict):
            result["failureSamples"] = [
                {"url": str(key)[:400], "error": str(value)[:400]}
                for key, value in list(errors.items())[:3]
            ]
        elif isinstance(errors, list):
            result["failureSamples"] = [{"error": str(value)[:400]} for value in errors[:3]]
        if state.get("error"):
            result["failureSamples"].append({"error": str(state["error"])[:400]})
    observed = sorted(
        item.get("observedAt", "") for item in item_rows(state.get("items", {}))
        if item.get("observedAt") and item.get("sourceId", source_id) == source_id
    )
    if observed:
        result["earliestObservedAt"] = observed[0]
        result["latestObservedAt"] = observed[-1]
    result["failureSamples"] = result["failureSamples"][:3]
    return result


def model_capture(root, row):
    model_dir = root / row["directory"]
    if row.get("status") == "reuse_fumina_capture":
        path = root / "scraper/fumina-suzuki-expanded/listings.json"
    else:
        path = model_dir / "listings.json"
    capture = read_json(path, {}) or {}
    items = item_rows(capture.get("items", []))
    if not items:
        for filename in ("physical-state.json", "digital-state.json", "kobo-state.json"):
            state = read_json(model_dir / filename, {}) or {}
            items.extend(item_rows(state.get("items", {})))
    unique = {}
    for item in items:
        source_id = item.get("sourceId", "")
        external_id = item.get("externalId", "")
        if source_id and external_id:
            unique.setdefault((source_id, external_id), item)
    return capture, list(unique.values())


def build(project_root=ROOT, out_dir=None, checked_at=None):
    root = Path(project_root)
    queue_root = root / "scraper/japan-models"
    queue = read_json(queue_root / "queue.json", [])
    policy = read_json(root / "scraper/japan-model-source-policy.json", {"sources": []})
    source_policy = {item["id"]: item for item in policy.get("sources", [])}
    checkpoint = read_json(queue_root / "import-checkpoint.json", {"records": {}}).get("records", {})
    homepage_verification = read_json(queue_root / "homepage-models-verification.json", {}) or {}
    homepage_by_model = {
        str(row.get("musecardsPersonIdExternalReference", row.get("modelId", ""))): row
        for row in homepage_verification.get("results", [])
    }
    database_verification = read_json(root / "reports/Japan Model Database Verification 2026-11-01.json", {}) or {}
    raw_database_verification = read_json(root / "reports/Japan Model Database Verification Raw Manifest 2026-11-01.json", {}) or {}
    identity_plan = read_json(root / "scraper/japan-work-identities.json", {"groups": []}) or {"groups": []}
    planned_work_by_edition = {
        member["editionId"]: group["workId"]
        for group in identity_plan.get("groups", [])
        for member in group.get("members", [])
        if member.get("editionId") and group.get("workId")
    }
    report_rows = []
    offer_evidence_rows = []
    all_offer_ids = set()

    for row in queue:
        person_id = row["musecardsPersonId"]
        model_dir = root / row["directory"]
        model_data = read_json(model_dir / "model.json", {"models": [{}]}).get("models", [{}])[0]
        records_path = root / ("scraper/fumina-suzuki-expanded/home-import.json" if row.get("status") == "reuse_fumina_capture" else f"{row['directory']}/home-import.json")
        records = read_json(records_path, []) or []
        manifest_by_offer = {}
        for record in records:
            source_id = record.get("source", {}).get("id", "")
            for item in record.get("batch", {}).get("items", []):
                manifest_by_offer.setdefault((source_id, item.get("externalId", "")), record)
        capture, offers = model_capture(root, row)
        if row.get("status") == "reuse_fumina_capture":
            imported = sum(item.get("importStatus") == "already_imported" for item in offers)
        else:
            imported = imported_associations(person_id, records, checkpoint)
        all_offer_ids.update((item.get("sourceId"), item.get("externalId")) for item in offers)

        books = read_json(model_dir / "physical-books.json", {"books": []}) or {"books": []}
        editions = books.get("books", [])
        missing_verified_covers = 0
        missing_offer_images = 0
        missing_image_provenance = 0
        missing_publisher_image_provenance = 0
        unknown_publication_dates = 0
        unknown_publication_precision = 0
        unknown_store_release_dates = 0
        unknown_store_release_precision = 0
        for item in offers:
            source_id = item.get("sourceId", "")
            external_id = item.get("externalId", "")
            record = manifest_by_offer.get((source_id, external_id), {})
            edition = record.get("edition", {})
            publisher_media = record.get("publisherMedia", [])
            verified_cover = next((
                media for media in publisher_media
                if media.get("originalUrl") and media.get("sourceUrl")
            ), None)
            listing_images = item.get("images", []) if isinstance(item.get("images"), list) else []
            missing_verified_covers += int(verified_cover is None)
            missing_offer_images += int(not item.get("imageUrl"))
            missing_image_provenance += sum(
                bool(image.get("url")) and not image.get("sourceUrl")
                for image in listing_images if isinstance(image, dict)
            )
            missing_publisher_image_provenance += sum(
                bool(media.get("originalUrl")) and not media.get("sourceUrl")
                for media in publisher_media if isinstance(media, dict)
            )
            publication_date = item.get("publicationDate") or edition.get("releaseDate") or ""
            publication_precision = item.get("publicationPrecision") or edition.get("releasePrecision") or ""
            publication_source_url = (
                item.get("publicationDateSourceUrl") or edition.get("metadataSourceUrl") or ""
            )
            store_release_date = item.get("storeReleaseDate", "")
            store_release_precision = item.get("storeReleasePrecision", "")
            store_release_source_url = item.get("storeReleaseDateSourceUrl", "")
            unknown_publication_dates += int(not publication_date)
            unknown_publication_precision += int(bool(publication_date) and not publication_precision)
            unknown_store_release_dates += int(item.get("format") == "digital" and not store_release_date)
            unknown_store_release_precision += int(bool(store_release_date) and not store_release_precision)
            cover_media = verified_cover or {}
            offer_evidence_rows.append({
                "musecardsPersonId": person_id,
                "name": row.get("name", ""),
                "nativeName": row.get("originalName", ""),
                "englishName": row.get("englishName", ""),
                "sourceId": source_id,
                "platform": item.get("platform") or source_policy.get(source_id, {}).get("platform", source_id),
                "sourceUrl": item.get("url", ""),
                "externalId": external_id,
                "title": item.get("title", ""),
                "format": item.get("format", ""),
                "availability": item.get("status", "unknown"),
                "availabilityEvidence": item.get("statusEvidence", ""),
                "priceMinor": item.get("priceMinor", ""),
                "currency": item.get("currency", ""),
                "priceType": item.get("priceType", ""),
                "observedAt": item.get("observedAt", ""),
                "publicationDate": publication_date,
                "publicationPrecision": publication_precision,
                "publicationDateSourceUrl": publication_source_url,
                "storeReleaseDate": store_release_date,
                "storeReleasePrecision": store_release_precision,
                "storeReleaseDateSourceUrl": store_release_source_url,
                "editionId": edition.get("id") or item.get("editionId", ""),
                "isbn": edition.get("isbn") or item.get("isbn", ""),
                "publisher": edition.get("publisher") or item.get("publisher", ""),
                "editionMetadataSourceUrl": edition.get("metadataSourceUrl", ""),
                "verifiedCoverUrl": cover_media.get("originalUrl", ""),
                "verifiedCoverSourceUrl": cover_media.get("sourceUrl", ""),
                "offerImageUrl": item.get("imageUrl", ""),
                "offerImages": listing_images,
                "publisherImages": publisher_media,
                "condition": item.get("condition", ""),
                "shippingText": item.get("shippingText", ""),
                "timestampPrecision": item.get("timestampPrecision", ""),
            })
        coverage = {
            source_id: source_capture(root, model_dir, source_id, source_policy.get(source_id, {}), capture)
            for source_id in source_policy
        }
        homepage_model = homepage_by_model.get(str(person_id), {})
        homepage_counts = homepage_model.get("counts", {})
        missing_association_audit = audit_missing_associations(row, model_data, homepage_model)
        format_counts = {
            "physical": sum(item.get("format") == "physical" for item in offers),
            "digital": sum(item.get("format") == "digital" for item in offers),
        }
        missing_provenance = sum(
            1 for item in offers
            if item.get("imageUrl") and not any(
                image.get("sourceUrl") for image in item.get("images", []) if isinstance(image, dict)
            )
        )
        report_rows.append({
            "musecardsPersonId": person_id,
            "name": row.get("name", ""),
            "nativeName": row.get("originalName", ""),
            "englishName": row.get("englishName", ""),
            "identityVerificationUrl": row.get("verificationSourceUrl", ""),
            "verifiedCareerNameCount": row.get("careerNameCount", 0),
            "japanReleaseEvidenceCount": row.get("relationshipEvidenceCount", 0),
            "importedOfferAssociations": imported,
            "capturedPhysicalOffers": format_counts["physical"],
            "capturedDigitalOffers": format_counts["digital"],
            "capturedUniqueOffers": len(offers),
            "physicalEditionsWithBibliography": len(editions),
            "unknownOriginalPublicationDates": unknown_publication_dates,
            "unknownPublicationDatePrecision": unknown_publication_precision,
            "unknownStoreReleaseDates": unknown_store_release_dates,
            "unknownStoreReleaseDatePrecision": unknown_store_release_precision,
            "unknownAvailability": sum(item.get("status", "unknown") == "unknown" for item in offers),
            "missingVerifiedEditionCovers": missing_verified_covers,
            "missingOfferImages": missing_offer_images,
            "imagesMissingSourcePageProvenance": missing_image_provenance,
            "publisherImagesMissingSourcePageProvenance": missing_publisher_image_provenance,
            "missingPaidPriceOrCurrency": sum(not item.get("priceMinor") or not item.get("currency") for item in offers),
            "homepageLiveCreditOffers": homepage_counts.get("all", ""),
            "homepageLivePhysicalOffers": homepage_counts.get("physical", ""),
            "homepageLiveDigitalOffers": homepage_counts.get("digital", ""),
            "homepageFilterCheckPassed": homepage_model.get("filtersPassed", ""),
            "homepageSearchMode": homepage_model.get("searchMode", ""),
            "homepageExactModelMatchCount": homepage_model.get("modelMatchCount", ""),
            "homepageManifestCoveragePassed": homepage_model.get("manifestCoveragePassed", ""),
            "importedManifestExpected": homepage_counts.get("importedManifestExpected", ""),
            "importedManifestSearchable": homepage_counts.get("importedManifestSearchable", ""),
            "reviewedCreditAdjustments": homepage_counts.get("reviewedCreditAdjustments", ""),
            "missingImportedManifestOffers": homepage_counts.get("missingImportedManifestOffers", ""),
            "missingAssociationCreditAudit": missing_association_audit,
            "sourceCoverage": coverage,
            "captureStatus": {key: value.get("status", "unknown") for key, value in capture.get("coverage", {}).items() if isinstance(value, dict)},
            "identityEvidence": model_data.get("careerNameEvidence", []),
        })

    source_summary = []
    for source in policy.get("sources", []):
        source_id = source["id"]
        rows = [row["sourceCoverage"][source_id] for row in report_rows]
        status_counts = {}
        failure_status_counts = {}
        for row in rows:
            status = row["searchStatus"]
            status_counts[status] = status_counts.get(status, 0) + 1
            for failure_status, count in row.get("failureStatusCounts", {}).items():
                failure_status_counts[failure_status] = failure_status_counts.get(failure_status, 0) + count
        observed = sorted(row["latestObservedAt"] for row in rows if row["latestObservedAt"])
        source_summary.append({
            "id": source_id,
            "platform": source.get("platform", source_id),
            "formats": source.get("formats", []),
            "searchUrl": source.get("searchUrl", ""),
            "termsUrl": source.get("termsUrl", ""),
            "paginationObserved": source.get("paginationObserved", "unknown"),
            "automationStatus": source.get("automationStatus", "permission_unverified"),
            "imageReuseStatus": source.get("imageReuseStatus", "not_granted"),
            "modelsInScope": len(rows),
            "modelsAttempted": sum(row["searchStatus"] != "not_attempted" for row in rows),
            "pagesObserved": sum(row["pagesObserved"] for row in rows),
            "queriesObserved": sum(row["queriesObserved"] for row in rows),
            "offersCaptured": sum(row["offersCaptured"] for row in rows),
            "bibliographicRecords": sum(row["bibliographicRecords"] for row in rows),
            "photobookKeywordCandidates": sum(row["photobookKeywordCandidates"] for row in rows),
            "truncatedQueries": sum(row["truncatedQueries"] for row in rows),
            "errors": sum(row["errors"] for row in rows),
            "failureStatusCounts": failure_status_counts,
            "detailErrors": sum(row["detailErrors"] for row in rows),
            "pendingDetails": sum(row["pendingDetails"] for row in rows),
            "earliestObservedAt": min((row["earliestObservedAt"] for row in rows if row["earliestObservedAt"]), default=""),
            "latestObservedAt": observed[-1] if observed else "",
            "searchStatusCounts": status_counts,
        })

    identity_path = sorted(queue_root.glob("musecards-models-*.json"))[-1] if list(queue_root.glob("musecards-models-*.json")) else None
    identity_snapshot = read_json(identity_path, {}) if identity_path else {}
    identity_people = {item.get("id"): item for item in identity_snapshot.get("models", [])}
    career_names = {}
    for item in identity_snapshot.get("careerNames", []):
        career_names.setdefault(item.get("person_id"), []).append(item)
    identity_evidence_rows = []
    for row in queue:
        person_id = row["musecardsPersonId"]
        person = identity_people.get(person_id, {})
        name_values = {
            "musecardsPersonId": person_id,
            "canonicalName": person.get("canonical_public_name") or row.get("name", ""),
            "nativeName": person.get("original_name") or row.get("originalName", ""),
            "englishName": person.get("english_name") or row.get("englishName", ""),
        }
        if person.get("verification_source_url"):
            identity_evidence_rows.append({**name_values, "evidenceType": "person_profile", "evidenceName": name_values["canonicalName"], "evidenceDateRaw": "", "sourceUrl": person["verification_source_url"], "verifiedAt": ""})
        for evidence in career_names.get(person_id, []):
            identity_evidence_rows.append({**name_values, "evidenceType": "career_name", "evidenceName": evidence.get("name", ""), "evidenceDateRaw": "", "sourceUrl": evidence.get("source_url", ""), "verifiedAt": evidence.get("verified_at", "")})
        for evidence in person.get("japan_release_evidence", []):
            identity_evidence_rows.append({
                **name_values,
                "evidenceType": "japan_market_credit",
                "evidenceName": evidence.get("canonical_title", ""),
                "originalTitle": evidence.get("original_title", ""),
                "creditedName": evidence.get("credited_name", ""),
                "creditedEnglishName": evidence.get("credited_english_name", ""),
                "evidenceDateRaw": evidence.get("release_date", ""),
                "musecardsCardSetId": evidence.get("card_set_id", ""),
                "musecardsCardSetSlug": evidence.get("card_set_slug", ""),
                "relationshipKind": evidence.get("relationship_kind", ""),
                "creditRole": evidence.get("role", ""),
                "sourceUrl": evidence.get("official_product_url", ""),
                "verifiedAt": "",
            })

    work_issues = database_verification.get("workIdentityIssues") or []
    mapped_work_issue_count = sum(
        planned_work_by_edition.get(issue.get("expectedEdition")) == issue.get("actualWork")
        for issue in work_issues
    )
    database_result = database_verification.get("result", {})
    raw_work_issues = raw_database_verification.get("workIdentityIssues") or []
    raw_mapped_work_issue_count = sum(
        planned_work_by_edition.get(issue.get("expectedEdition")) == issue.get("actualWork")
        for issue in raw_work_issues
    )
    homepage_failures = [
        {"musecardsPersonIdExternalReference": row.get("musecardsPersonIdExternalReference", row.get("modelId")),
         "name": row["name"], "counts": row.get("counts", {}), "modelFilterError": row.get("modelFilterError", "")}
        for row in homepage_verification.get("results", []) if not row.get("filtersPassed", False)
    ]
    homepage_manifest_failures = [
        {"musecardsPersonIdExternalReference": row.get("musecardsPersonIdExternalReference", row.get("modelId")),
         "name": row["name"], "missingImportedManifestOffers": row.get("counts", {}).get("missingImportedManifestOffers", 0)}
        for row in homepage_verification.get("results", []) if not row.get("manifestCoveragePassed", False)
    ]
    homepage_results = homepage_verification.get("results", [])
    association_credit_audit = aggregate_association_audits(
        row["missingAssociationCreditAudit"] for row in report_rows
    )

    summary = {
        "checkedAt": checked_at or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "identitySnapshotRetrievedAt": queue[0].get("identitySnapshotRetrievedAt", "") if queue else "",
        "modelCount": len(report_rows),
        "distinctCapturedOfferIds": len(all_offer_ids),
        "importedOfferAssociations": sum(row["importedOfferAssociations"] for row in report_rows),
        "capturedPhysicalOffers": sum(row["capturedPhysicalOffers"] for row in report_rows),
        "capturedDigitalOffers": sum(row["capturedDigitalOffers"] for row in report_rows),
        "unknownOriginalPublicationDates": sum(row["unknownOriginalPublicationDates"] for row in report_rows),
        "unknownPublicationDatePrecision": sum(row["unknownPublicationDatePrecision"] for row in report_rows),
        "unknownStoreReleaseDates": sum(row["unknownStoreReleaseDates"] for row in report_rows),
        "unknownStoreReleaseDatePrecision": sum(row["unknownStoreReleaseDatePrecision"] for row in report_rows),
        "unknownAvailability": sum(row["unknownAvailability"] for row in report_rows),
        "missingVerifiedEditionCovers": sum(row["missingVerifiedEditionCovers"] for row in report_rows),
        "missingOfferImages": sum(row["missingOfferImages"] for row in report_rows),
        "imagesMissingSourcePageProvenance": sum(row["imagesMissingSourcePageProvenance"] for row in report_rows),
        "publisherImagesMissingSourcePageProvenance": sum(row["publisherImagesMissingSourcePageProvenance"] for row in report_rows),
        "missingPaidPriceOrCurrency": sum(row["missingPaidPriceOrCurrency"] for row in report_rows),
        "offerEvidenceFile": "Japan Model Offer Evidence 2026-11-01.csv",
        "offerEvidenceRows": len(offer_evidence_rows),
        "identityEvidenceFile": "Japan Model Identity Evidence 2026-11-01.csv",
        "identityEvidenceRows": len(identity_evidence_rows),
        "identityEvidenceSnapshot": identity_path.name if identity_path else "",
        "identityEvidenceRetrievedAt": identity_snapshot.get("retrieved_at", ""),
        "unknownValueConvention": "Blank offer-evidence cells preserve an unknown or unrecorded source value; dates and precision are copied from the capture or matched edition source without sharpening.",
        "sources": policy.get("sources", []),
        "sourceCoverageSummary": source_summary,
        "homepageVerification": {
            "checkedAt": homepage_verification.get("checkedAt", ""),
            "mode": homepage_verification.get("mode", "not_run"),
            "liveApiTotalOffers": (homepage_verification.get("liveApi") or {}).get("total", ""),
            "liveApiPages": (homepage_verification.get("liveApi") or {}).get("totalPages", ""),
            "importedUniqueOffers": homepage_verification.get("importedMarketplaceItems", ""),
            "importedModelAssociations": homepage_verification.get("importedModelAssociations", ""),
            "excludedListings": homepage_verification.get("excludedListings", 0),
            "excludedOfferAssociations": homepage_verification.get("excludedOfferAssociations", 0),
            "reviewedCreditAdjustments": len(homepage_verification.get("reviewedCreditAdjustments", [])),
            "missingImportedManifestAssociations": homepage_verification.get("missingImportedManifestAssociations", ""),
            "missingAssociationCreditAudit": association_credit_audit,
            "exactModelIdSearchProfiles": sum(row.get("searchMode") == "model_id" for row in homepage_results),
            "textFallbackProfiles": sum(row.get("searchMode") == "text_fallback" for row in homepage_results),
            "homepageFilterProfilesPassed": sum(bool(row.get("filtersPassed")) for row in homepage_results),
            "failedModelFilters": homepage_failures,
            "modelManifestCoverageFailureProfiles": homepage_manifest_failures,
            "catalogIdentityIssueCount": len(homepage_verification.get("catalogIdentityIssues", [])),
            "publicationGroupingIssueCount": len(homepage_verification.get("marketplaceGroupingIssues", [])),
            "reviewedCrossFormatGroupsPassed": sum(group.get("passed", False) for group in homepage_verification.get("reviewedCrossFormatGroups", [])),
            "reviewedCrossFormatGroupsTotal": len(homepage_verification.get("reviewedCrossFormatGroups", [])),
        },
        "databaseVerification": {
            "checkedAt": database_verification.get("checkedAt", ""),
            "mode": database_verification.get("mode", "not_run"),
            "result": database_result,
            "workIdentityIssueCount": len(work_issues),
            "workIdentityIssuesMatchingReviewedGrouping": mapped_work_issue_count,
            "rawManifestWorkMismatchCount": raw_database_verification.get("result", {}).get("workMismatches", ""),
            "rawManifestMismatchesMatchingReviewedGrouping": raw_mapped_work_issue_count,
            "reportFile": "Japan Model Database Verification 2026-11-01.json",
            "rawManifestReportFile": "Japan Model Database Verification Raw Manifest 2026-11-01.json",
            "note": "The original import manifest has per-edition work IDs that predate the reviewed grouping. A separate read-only verification manifest applies the reviewed edition-to-work map. One source-backed wrong-model association was marked excluded in a transaction; its listing and price observations remain preserved.",
        },
        "models": report_rows,
        "completeness": "Bounded to saved captures, current read-only MuseCards snapshot, and reviewed public source pages. Not globally complete; not every source was authorized or paginated for every model.",
    }

    output_root = Path(out_dir) if out_dir else root / "reports"
    output_root.mkdir(parents=True, exist_ok=True)
    json_path = output_root / "Japan Model Coverage 2026-11-01.json"
    csv_path = output_root / "Japan Model Coverage 2026-11-01.csv"
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    fields = [key for key in report_rows[0] if key not in ("sourceCoverage", "captureStatus", "identityEvidence")] if report_rows else []
    fields += ["sourceCoverage", "captureStatus"]
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in report_rows:
            writer.writerow({key: json.dumps(row[key], ensure_ascii=False, separators=(",", ":")) if isinstance(row.get(key), (dict, list)) else row.get(key, "") for key in fields})
    offer_fields = list(offer_evidence_rows[0]) if offer_evidence_rows else []
    offer_csv_path = output_root / "Japan Model Offer Evidence 2026-11-01.csv"
    with offer_csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=offer_fields, extrasaction="ignore")
        writer.writeheader()
        for row in offer_evidence_rows:
            writer.writerow({
                key: json.dumps(value, ensure_ascii=False, separators=(",", ":")) if isinstance(value, (dict, list)) else value
                for key, value in row.items()
            })
    identity_fields = [
        "musecardsPersonId", "canonicalName", "nativeName", "englishName", "evidenceType",
        "evidenceName", "originalTitle", "creditedName", "creditedEnglishName", "evidenceDateRaw",
        "musecardsCardSetId", "musecardsCardSetSlug", "relationshipKind", "creditRole", "sourceUrl", "verifiedAt",
    ]
    identity_csv_path = output_root / "Japan Model Identity Evidence 2026-11-01.csv"
    with identity_csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=identity_fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(identity_evidence_rows)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", help="Defaults to reports/ in the project")
    args = parser.parse_args()
    result = build(out_dir=args.output_dir)
    summary_keys = (
        "checkedAt", "identitySnapshotRetrievedAt", "modelCount", "distinctCapturedOfferIds",
        "importedOfferAssociations", "capturedPhysicalOffers", "capturedDigitalOffers",
        "unknownOriginalPublicationDates", "unknownPublicationDatePrecision", "unknownStoreReleaseDates",
        "unknownStoreReleaseDatePrecision",
        "unknownAvailability", "missingVerifiedEditionCovers", "missingOfferImages",
        "imagesMissingSourcePageProvenance", "publisherImagesMissingSourcePageProvenance",
        "missingPaidPriceOrCurrency", "offerEvidenceFile", "offerEvidenceRows",
        "homepageVerification", "databaseVerification", "completeness",
    )
    print(json.dumps({key: result[key] for key in summary_keys}, ensure_ascii=False))


if __name__ == "__main__":
    main()
