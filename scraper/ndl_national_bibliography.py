"""Collect NDL national-bibliography metadata as dated identity candidates.

This route is deliberately metadata-only: its records are not marketplace
offers, its titles are not verified model credits, and it never downloads images.
MuseCards person IDs are stored as external references only.
"""
import argparse
import json
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUEUE_PATH = ROOT / "scraper/japan-models/queue.json"
OUTPUT_ROOT = ROOT / "research_notes/japan-ndl-national-bibliography"
ENDPOINT = "https://ndlsearch.ndl.go.jp/api/opensearch"
DPID = "iss-ndl-opac-national"
MAX_RECORDS_PER_QUERY = 500
USER_AGENT = "MuseBooks bibliography metadata research/1.0"
NS = {
    "opensearch": "http://a9.com/-/spec/opensearchrss/1.0/",
    "dc": "http://purl.org/dc/elements/1.1/",
    "dcndl": "http://ndl.go.jp/dcndl/terms/",
    "dcterms": "http://purl.org/dc/terms/",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
}
PHOTOBOOK_TERMS = (
    "写真集", "フォトブック", "photo book", "photobook", "photo album",
)
NONBOOK_TERMS = ("dvd", "blu-ray", "ブルーレイ", "cd", "dvd-video", "映像資料")


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def read_json(path, default=None):
    path = Path(path)
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8-sig"))


def normalized(value):
    return "".join(ch for ch in unicodedata.normalize("NFKC", value).casefold() if ch.isalnum())


def identity_terms(row, profile):
    """Return full canonical/native/English names and verified full aliases."""
    terms = []
    positions = {}

    def add(value, kind, evidence_url=""):
        value = (value or "").strip()
        key = normalized(value)
        if not value or not key:
            return
        if key in positions:
            existing = terms[positions[key]]
            if kind not in existing["nameTypes"]:
                existing["nameTypes"].append(kind)
            if evidence_url and evidence_url not in existing["evidenceUrls"]:
                existing["evidenceUrls"].append(evidence_url)
                existing["evidenceUrl"] = existing["evidenceUrl"] or evidence_url
            return
        positions[key] = len(terms)
        terms.append({"name": value, "nameType": kind, "nameTypes": [kind],
                      "evidenceUrl": evidence_url,
                      "evidenceUrls": [evidence_url] if evidence_url else []})

    profile_url = profile.get("verification_source_url") or row.get("verificationSourceUrl", "")
    add(profile.get("canonical_public_name") or row.get("name"), "canonical", profile_url)
    add(profile.get("original_name") or row.get("originalName"), "native", profile_url)
    add(profile.get("english_name") or row.get("englishName"), "english", profile_url)

    # Alternate career names are searched only when the MuseCards snapshot has
    # source evidence for them; they are not used to merge identities.
    for evidence in profile.get("careerNameEvidence", []):
        if evidence.get("sourceUrl"):
            add(evidence.get("name"), "verified_alias", evidence.get("sourceUrl", ""))
    return terms


def _values(item, path, namespaces=None):
    return [value for element in item.findall(path, namespaces or NS)
            if (value := "".join(element.itertext()).strip())]


def parse_response(xml_bytes, request_url=""):
    root = ET.fromstring(xml_bytes)
    channel = root.find("channel")
    if channel is None:
        raise ValueError("NDL OpenSearch response did not contain an RSS channel")
    total_element = channel.find("opensearch:totalResults", NS)
    start_element = channel.find("opensearch:startIndex", NS)
    count_element = channel.find("opensearch:itemsPerPage", NS)
    total = int(total_element.text or "0") if total_element is not None else None
    start = int(start_element.text or "1") if start_element is not None else 1
    returned = int(count_element.text or "0") if count_element is not None else None
    records = []
    for item in channel.findall("item"):
        title = _values(item, "title")
        link = _values(item, "link")
        category = _values(item, "category")
        identifier_values = []
        for element in item.findall("dc:identifier", NS):
            value = "".join(element.itertext()).strip()
            if value:
                identifier_values.append({
                    "type": element.attrib.get("{" + NS["xsi"] + "}type", ""),
                    "value": value,
                })
        dates = []
        for path in ("dc:date", "dcterms:issued"):
            for element in item.findall(path, NS):
                value = "".join(element.itertext()).strip()
                if value:
                    dates.append({
                        "field": path.split(":", 1)[1],
                        "precisionOrType": element.attrib.get("{" + NS["xsi"] + "}type", ""),
                        "value": value,
                    })
        description = _values(item, "dc:description")
        summary = " ".join([title[0] if title else "", *description]).casefold()
        has_keyword = any(term in summary for term in PHOTOBOOK_TERMS)
        has_nonbook_marker = any(term in summary for term in NONBOOK_TERMS)
        is_magazine = any("雑誌" in value for value in category)
        is_book_media = not has_nonbook_marker and not is_magazine
        if has_keyword and is_book_media:
            candidate_status = "keyword_candidate_requires_credit_and_edition_review"
        elif has_nonbook_marker or is_magazine:
            candidate_status = "excluded_non_photobook_medium"
        else:
            candidate_status = "not_a_photobook_keyword_match"
        records.append({
            "title": title[0] if title else "",
            "sourcePageUrl": (link[0] if link else ""),
            "recordIdentifiers": identifier_values,
            "creators": _values(item, "dc:creator"),
            "rssAuthors": _values(item, "author"),
            "publishers": _values(item, "dc:publisher"),
            "subjects": _values(item, "dc:subject"),
            "mediaCategories": category,
            "publicationDatesRaw": dates,
            "descriptions": description,
            "recordUpdatedAtRaw": _values(item, "pubDate"),
            "photobookCandidateStatus": candidate_status,
            "identityReviewStatus": "candidate_only_not_a_verified_model_credit",
            "requestUrl": request_url,
        })
    truncated = total is not None and total > MAX_RECORDS_PER_QUERY
    return {
        "totalResults": total,
        "startIndex": start,
        "itemsPerPage": returned,
        "recordsReturned": len(records),
        "paginationStatus": "provider_cap_truncated" if truncated else "complete_within_accessible_limit",
        "truncatedAtProviderLimit": truncated,
        "records": records,
    }


def request_url(term):
    return ENDPOINT + "?" + urllib.parse.urlencode({
        "cnt": MAX_RECORDS_PER_QUERY,
        "title": term,
        "dpid": DPID,
    })


def query_title(term, timeout=45):
    url = request_url(term)
    observed_at = utc_now()
    request = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.8",
    })
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = response.read()
            parsed = parse_response(payload, url)
            return {
                "term": term,
                "requestUrl": url,
                "observedAt": observed_at,
                "httpStatus": response.status,
                "status": "ok",
                **{key: value for key, value in parsed.items() if key != "records"},
                "records": parsed["records"],
            }
    except urllib.error.HTTPError as error:
        return {"term": term, "requestUrl": url, "observedAt": observed_at,
                "httpStatus": error.code, "status": "http_error", "error": str(error)}
    except (urllib.error.URLError, TimeoutError, OSError, ET.ParseError, ValueError) as error:
        return {"term": term, "requestUrl": url, "observedAt": observed_at,
                "httpStatus": None, "status": "request_or_parse_error",
                "error": str(error)[:500]}


def _merge_records(queries):
    records = {}
    for query in queries:
        for record in query.get("records", []):
            key = record.get("sourcePageUrl") or json.dumps(record, ensure_ascii=False, sort_keys=True)
            if key not in records:
                records[key] = {**record, "matchedTerms": [query["term"]]}
            elif query["term"] not in records[key]["matchedTerms"]:
                records[key]["matchedTerms"].append(query["term"])
    return list(records.values())


def model_capture(row, root=ROOT, output_root=OUTPUT_ROOT, delay_seconds=1.0,
                  refresh=False, only_terms=None):
    output_root = Path(output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    person_id = row["musecardsPersonId"]
    profile_data = read_json(Path(root) / row["directory"] / "model.json", {}) or {}
    profile = (profile_data.get("models") or [{}])[0]
    terms = identity_terms(row, profile)
    if only_terms:
        allowed = set(only_terms)
        terms = [term for term in terms if term["name"] in allowed]
    path = output_root / (str(person_id) + ".json")
    old = read_json(path, {}) if not refresh else {}
    old_queries = {query.get("term"): query for query in (old or {}).get("queries", [])}
    queries = []
    for index, term_record in enumerate(terms):
        term = term_record["name"]
        old_query = old_queries.get(term)
        if old_query and old_query.get("status") == "ok":
            query = old_query
        else:
            if queries and delay_seconds > 0:
                time.sleep(delay_seconds)
            query = query_title(term)
        query = {**query, "nameType": term_record["nameType"],
                 "nameTypes": term_record.get("nameTypes", [term_record["nameType"]]),
                 "identityEvidenceUrl": term_record["evidenceUrl"],
                 "identityEvidenceUrls": term_record.get("evidenceUrls", [])}
        queries.append(query)

    merged = _merge_records(queries)
    errors = sum(query.get("status") != "ok" for query in queries)
    truncated = sum(bool(query.get("truncatedAtProviderLimit")) for query in queries)
    if errors:
        status = "incomplete_query_errors"
    elif truncated:
        status = "provider_cap_truncated"
    else:
        status = "complete_for_selected_verified_name_terms"
    first_observed = [q["observedAt"] for q in queries if q.get("observedAt")]
    result = {
        "schemaVersion": 1,
        "sourceId": "ndl-national-bibliography-jp",
        "sourcePlatform": "National Diet Library Search — National Bibliography",
        "dataProviderId": DPID,
        "dataProviderName": "National Diet Library National Bibliography",
        "metadataLicense": "CC BY 4.0",
        "metadataLicenseUrl": "https://creativecommons.org/licenses/by/4.0/",
        "apiUsageSourceUrl": "https://ndlsearch.ndl.go.jp/help/api",
        "sourcePolicy": "Bibliographic metadata only; not current offers, prices, stock, or store release dates. No images are downloaded or reused. NDL records are candidate evidence only and are not automatically merged into MuseBooks.",
        "musecardsPersonIdExternalReference": person_id,
        "identityNamesSearched": terms,
        "observedAt": max(first_observed, default=""),
        "status": status,
        "queryCount": len(queries),
        "queriesSucceeded": sum(query.get("status") == "ok" for query in queries),
        "requestErrors": errors,
        "truncatedQueries": truncated,
        "pagesObserved": sum(1 for query in queries if query.get("status") == "ok"),
        "bibliographicRecordsUnique": len(merged),
        "photobookKeywordCandidates": sum(record.get("photobookCandidateStatus", "").startswith("keyword_candidate") for record in merged),
        "earliestObservedAt": min((q["observedAt"] for q in queries if q.get("observedAt")), default=""),
        "latestObservedAt": max(first_observed, default=""),
        "queries": queries,
        "records": merged,
    }
    temp_path = path.with_suffix(".json.tmp")
    temp_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp_path.replace(path)
    return result


def collect(queue_path=QUEUE_PATH, output_root=OUTPUT_ROOT, model_ids=None,
            limit_models=None, delay_seconds=1.0, refresh=False, start_index=0):
    rows = read_json(queue_path, []) or []
    if model_ids:
        model_ids = {int(value) for value in model_ids}
        rows = [row for row in rows if int(row["musecardsPersonId"]) in model_ids]
    rows = rows[max(0, start_index):]
    if limit_models is not None:
        rows = rows[:limit_models]
    results = []
    for index, row in enumerate(rows, 1):
        if index > 1 and delay_seconds > 0:
            time.sleep(delay_seconds)
        result = model_capture(row, Path(queue_path).resolve().parents[2], output_root,
                               delay_seconds=delay_seconds, refresh=refresh)
        summary = {
            "progress": index,
            "modelsInRun": len(rows),
            "musecardsPersonIdExternalReference": result["musecardsPersonIdExternalReference"],
            "status": result["status"],
            "queriesSucceeded": result["queriesSucceeded"],
            "queryCount": result["queryCount"],
            "records": result["bibliographicRecordsUnique"],
            "candidates": result["photobookKeywordCandidates"],
        }
        results.append(summary)
        print(json.dumps(summary, ensure_ascii=False), flush=True)
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--queue", default=str(QUEUE_PATH))
    parser.add_argument("--output-dir", default=str(OUTPUT_ROOT))
    parser.add_argument("--model-id", action="append", type=int, dest="model_ids")
    parser.add_argument("--limit-models", type=int)
    parser.add_argument("--start-index", type=int, default=0,
                        help="Zero-based offset into the selected MuseCards model queue")
    parser.add_argument("--delay-seconds", type=float, default=1.0)
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    results = collect(args.queue, args.output_dir, args.model_ids, args.limit_models,
                      args.delay_seconds, args.refresh, args.start_index)
    print(json.dumps({
        "modelsAttempted": len(results),
        "complete": sum(result["status"] == "complete_for_selected_verified_name_terms" for result in results),
        "incomplete": sum(result["status"] != "complete_for_selected_verified_name_terms" for result in results),
        "records": sum(result["records"] for result in results),
        "photobookKeywordCandidates": sum(result["candidates"] for result in results),
        "outputDir": str(Path(args.output_dir)),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
