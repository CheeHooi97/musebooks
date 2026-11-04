import hashlib
import json
import csv
import tempfile
import unittest
from pathlib import Path

from build_japan_model_coverage import build, stable_json


class JapanModelCoverageTests(unittest.TestCase):
    def test_exports_saved_coverage_and_keeps_unattempted_sources_explicit(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            queue_root = root / "scraper/japan-models"
            model_dir = queue_root / "1"
            model_dir.mkdir(parents=True)
            row = {
                "musecardsPersonId": 1,
                "name": "Model",
                "nativeName": "モデル",
                "englishName": "Model Example",
                "verificationSourceUrl": "https://publisher.test/model",
                "careerNameCount": 1,
                "relationshipEvidenceCount": 2,
                "identitySnapshotRetrievedAt": "2026-11-01T05:02:30Z",
                "directory": "scraper/japan-models/1",
                "status": "pending",
            }
            (queue_root / "queue.json").write_text(json.dumps([row]), encoding="utf-8")
            (root / "scraper/japan-model-source-policy.json").write_text(json.dumps({
                "sources": [
                    {"id": "ndl-national-bibliography-jp", "automationStatus": "metadata_reuse_permitted_with_attribution"},
                    {"id": "yahoo-auctions-jp", "automationStatus": "permission_unverified"},
                    {"id": "grajapa-jp", "automationStatus": "permission_unverified"},
                    {"id": "rakuten-kobo-jp", "automationStatus": "blocked_by_terms"},
                ]
            }), encoding="utf-8")
            (queue_root / "musecards-models-20261101.json").write_text(json.dumps({
                "retrieved_at": "2026-11-01T05:02:30Z",
                "models": [{
                    "id": 1, "canonical_public_name": "Model", "original_name": "モデル",
                    "english_name": "Model Example", "verification_source_url": "https://publisher.test/profile",
                    "japan_release_evidence": [{
                        "card_set_id": 10, "card_set_slug": "model-photobook", "canonical_title": "Model Book",
                        "release_date": "2025-03-04T08:00:00+08:00", "official_product_url": "https://publisher.test/book",
                        "relationship_kind": "book_people", "role": "featured_subject", "credited_name": "モデル",
                        "credited_english_name": "Model Example",
                    }],
                }],
                "careerNames": [{"person_id": 1, "name": "Model Example", "name_type": "romanized", "source_url": "https://publisher.test/name", "verified_at": "2026-01-02T00:00:00Z"}],
            }), encoding="utf-8")
            record = {"source": {"id": "yahoo-auctions-jp"}, "batch": {"items": [{"externalId": "a1"}]}}
            digest = hashlib.sha256(stable_json(record).encode("utf-8")).hexdigest()
            (model_dir / "home-import.json").write_text(json.dumps([record]), encoding="utf-8")
            (queue_root / "import-checkpoint.json").write_text(json.dumps({
                "records": {"1:yahoo-auctions-jp:a1": digest}
            }), encoding="utf-8")
            offer = {
                "sourceId": "yahoo-auctions-jp", "externalId": "a1", "format": "physical",
                "status": "unknown", "priceMinor": 1200, "currency": "JPY", "priceType": "auction_current",
                "imageUrl": "https://img.test/a1.jpg", "url": "https://auction.test/a1", "platform": "Yahoo Auctions",
                "publicationDate": "", "images": [{"url": "https://img.test/a1.jpg", "sourceUrl": "https://auction.test/a1"}],
                "storeReleaseDate": "2025-03-15",
            }
            (model_dir / "listings.json").write_text(json.dumps({
                "items": [offer],
                "coverage": {"grajapa": {
                    "status": "public_search_exhausted", "pages": ["https://store.test/search?p=1", "https://store.test/search?p=2"],
                    "searchedNameQueries": ["モデル"], "pendingNameQueries": [], "pendingTitleReviews": [], "errors": {},
                }},
            }), encoding="utf-8")
            (model_dir / "model.json").write_text(json.dumps({"models": [{"aliases": ["Model Alias"], "careerNameEvidence": [], "japan_release_evidence": []}]}), encoding="utf-8")
            ndl_dir = root / "research_notes/japan-ndl-national-bibliography"
            ndl_dir.mkdir(parents=True)
            (ndl_dir / "1.json").write_text(json.dumps({
                "status": "complete_for_selected_verified_name_terms",
                "queryCount": 3,
                "pagesObserved": 2,
                "requestErrors": 2,
                "truncatedQueries": 0,
                "bibliographicRecordsUnique": 1,
                "photobookKeywordCandidates": 1,
                "observedAt": "2026-11-01T06:00:00Z",
                "metadataLicense": "CC BY 4.0",
                "identityNamesSearched": [{"name": "Model"}, {"name": "Model Example"}],
                "queries": [
                    {"term": "Model", "status": "ok", "totalResults": 1,
                     "paginationStatus": "complete_within_accessible_limit"},
                    {"term": "Model Example", "status": "http_error", "httpStatus": 429,
                     "requestUrl": "https://ndlsearch.ndl.go.jp/api/opensearch?q=Model%20Example",
                     "error": "HTTP Error 429: Too Many Requests"},
                    {"term": "Model Alias", "status": "request_or_parse_error",
                     "requestUrl": "https://ndlsearch.ndl.go.jp/api/opensearch?q=Model%20Alias",
                     "error": "The read operation timed out"},
                ],
                "records": [{"sourcePageUrl": "https://ndlsearch.ndl.go.jp/books/example"}],
            }), encoding="utf-8")
            (model_dir / "physical-state.json").write_text(json.dumps({
                "runs": {"yahoo-auctions-jp:Model": {
                    "sourceId": "yahoo-auctions-jp", "status": "public_search_exhausted",
                    "batches": [{"diagnostics": {"pagesLoaded": 2, "detailErrors": 1}}],
                }},
                "items": {"a1": offer},
            }), encoding="utf-8")
            (queue_root / "homepage-models-verification.json").write_text(json.dumps({
                "excludedListings": 2,
                "excludedOfferAssociations": 3,
                "results": [{
                    "musecardsPersonIdExternalReference": 1,
                    "name": "Model",
                    "missingImportedManifestOffers": [
                        {"sourceId": "rakuten-kobo-jp", "liveCredits": "Model Alias", "liveWorkSlug": "model-work"},
                        {"sourceId": "grajapa-jp", "liveCredits": "Other Model", "liveWorkSlug": "other-work"},
                        {"sourceId": "yahoo-auctions-jp", "liveCredits": "", "liveWorkSlug": ""},
                    ],
                }],
            }), encoding="utf-8")
            capture_before = (model_dir / "physical-state.json").read_bytes()

            result = build(root, root / "reports", checked_at="2026-11-01T06:00:00Z")

            model = result["models"][0]
            self.assertEqual(result["modelCount"], 1)
            self.assertEqual(model["importedOfferAssociations"], 1)
            self.assertEqual(model["capturedPhysicalOffers"], 1)
            self.assertEqual(model["unknownOriginalPublicationDates"], 1)
            self.assertEqual(model["unknownStoreReleaseDatePrecision"], 1)
            self.assertEqual(model["unknownAvailability"], 1)
            self.assertEqual(model["sourceCoverage"]["yahoo-auctions-jp"]["pagesObserved"], 2)
            self.assertEqual(model["sourceCoverage"]["yahoo-auctions-jp"]["detailErrors"], 1)
            self.assertEqual(model["sourceCoverage"]["yahoo-auctions-jp"]["pendingDetails"], 1)
            self.assertEqual(model["sourceCoverage"]["rakuten-kobo-jp"]["searchStatus"], "not_attempted")
            self.assertEqual(model["sourceCoverage"]["rakuten-kobo-jp"]["automationStatus"], "blocked_by_terms")
            self.assertEqual(model["sourceCoverage"]["grajapa-jp"]["pagesObserved"], 2)
            self.assertEqual(model["sourceCoverage"]["grajapa-jp"]["searchStatus"], "public_search_exhausted")
            self.assertEqual(model["sourceCoverage"]["ndl-national-bibliography-jp"]["bibliographicRecords"], 1)
            self.assertEqual(model["sourceCoverage"]["ndl-national-bibliography-jp"]["offersCaptured"], 0)
            ndl_coverage = model["sourceCoverage"]["ndl-national-bibliography-jp"]
            self.assertEqual(ndl_coverage["failureStatusCounts"], {"http_429": 1, "request_or_parse_error": 1})
            self.assertEqual(ndl_coverage["queryRuns"][1]["requestUrl"], "https://ndlsearch.ndl.go.jp/api/opensearch?q=Model%20Example")
            self.assertEqual(ndl_coverage["failureSamples"][0]["httpStatus"], 429)
            self.assertEqual(result["sourceCoverageSummary"][0]["failureStatusCounts"], {"http_429": 1, "request_or_parse_error": 1})
            self.assertEqual(result["sourceCoverageSummary"][0]["id"], "ndl-national-bibliography-jp")
            self.assertEqual(result["sourceCoverageSummary"][0]["bibliographicRecords"], 1)
            self.assertEqual(result["offerEvidenceRows"], 1)
            self.assertEqual(result["identityEvidenceRows"], 3)
            self.assertEqual(result["homepageVerification"]["excludedListings"], 2)
            self.assertEqual(result["homepageVerification"]["excludedOfferAssociations"], 3)
            self.assertEqual(model["missingAssociationCreditAudit"]["verifiedNameInLiveCredit"], 1)
            self.assertEqual(model["missingAssociationCreditAudit"]["liveCreditNoVerifiedNameMatch"], 1)
            self.assertEqual(model["missingAssociationCreditAudit"]["noLiveCreditEvidence"], 1)
            self.assertEqual(result["homepageVerification"]["missingAssociationCreditAudit"]["bySource"]["grajapa-jp"]["liveCreditNoVerifiedNameMatch"], 1)
            self.assertEqual((model_dir / "physical-state.json").read_bytes(), capture_before)
            self.assertTrue((root / "reports/Japan Model Coverage 2026-11-01.json").exists())
            self.assertTrue((root / "reports/Japan Model Coverage 2026-11-01.csv").exists())
            evidence_path = root / "reports/Japan Model Offer Evidence 2026-11-01.csv"
            with evidence_path.open(encoding="utf-8-sig", newline="") as handle:
                evidence = next(csv.DictReader(handle))
            self.assertEqual(evidence["availability"], "unknown")
            self.assertEqual(evidence["priceType"], "auction_current")
            self.assertEqual(evidence["publicationDate"], "")
            self.assertEqual(evidence["storeReleaseDate"], "2025-03-15")
            self.assertEqual(evidence["storeReleasePrecision"], "")
            self.assertEqual(evidence["sourceUrl"], "https://auction.test/a1")
            identity_path = root / "reports/Japan Model Identity Evidence 2026-11-01.csv"
            with identity_path.open(encoding="utf-8-sig", newline="") as handle:
                identities = list(csv.DictReader(handle))
            release_credit = next(row for row in identities if row["evidenceType"] == "japan_market_credit")
            self.assertEqual(release_credit["musecardsCardSetId"], "10")
            self.assertEqual(release_credit["sourceUrl"], "https://publisher.test/book")


if __name__ == "__main__":
    unittest.main()
