import unittest

from ndl_national_bibliography import (
    _merge_records,
    identity_terms,
    parse_response,
)


class NdlNationalBibliographyTests(unittest.TestCase):
    def test_preserves_bibliographic_dates_and_does_not_treat_feed_update_as_publication(self):
        xml = '''<?xml version="1.0" encoding="UTF-8"?>
        <rss xmlns:dc="http://purl.org/dc/elements/1.1/"
             xmlns:dcndl="http://ndl.go.jp/dcndl/terms/"
             xmlns:dcterms="http://purl.org/dc/terms/"
             xmlns:openSearch="http://a9.com/-/spec/opensearchrss/1.0/"
             xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
          <channel>
            <openSearch:totalResults>1</openSearch:totalResults>
            <openSearch:startIndex>1</openSearch:startIndex>
            <openSearch:itemsPerPage>1</openSearch:itemsPerPage>
            <item>
              <title>写真集 鈴木ふみ奈</title>
              <link>https://ndlsearch.ndl.go.jp/books/R100000002-I123456789</link>
              <description>Publisher, 2020-03-04</description>
              <category>紙</category>
              <pubDate>Tue, 1 Sep 2026 09:00:00 +0900</pubDate>
              <dc:title>写真集 鈴木ふみ奈</dc:title>
              <dc:date xsi:type="dcterms:W3CDTF">2020-03</dc:date>
              <dcterms:issued>2020-03-04</dcterms:issued>
              <dc:identifier xsi:type="dcndl:NDLBibID">123456789</dc:identifier>
            </item>
          </channel>
        </rss>'''.encode("utf-8")

        result = parse_response(xml, "https://ndlsearch.ndl.go.jp/api/opensearch?title=test")
        record = result["records"][0]

        self.assertEqual(record["publicationDatesRaw"], [
            {"field": "date", "precisionOrType": "dcterms:W3CDTF", "value": "2020-03"},
            {"field": "issued", "precisionOrType": "", "value": "2020-03-04"},
        ])
        self.assertEqual(record["recordUpdatedAtRaw"], ["Tue, 1 Sep 2026 09:00:00 +0900"])
        self.assertEqual(record["photobookCandidateStatus"], "keyword_candidate_requires_credit_and_edition_review")
        self.assertEqual(record["identityReviewStatus"], "candidate_only_not_a_verified_model_credit")
        self.assertNotIn("images", record)

    def test_marks_provider_result_cap_as_truncated_and_keeps_nonbook_excluded(self):
        xml = '''<rss xmlns:dc="http://purl.org/dc/elements/1.1/"
             xmlns:openSearch="http://a9.com/-/spec/opensearchrss/1.0/">
          <channel><openSearch:totalResults>501</openSearch:totalResults>
            <openSearch:startIndex>1</openSearch:startIndex><openSearch:itemsPerPage>1</openSearch:itemsPerPage>
            <item><title>Model DVD</title><link>https://ndlsearch.ndl.go.jp/books/video</link>
              <category>DVD</category></item>
          </channel></rss>'''.encode("utf-8")

        result = parse_response(xml)

        self.assertTrue(result["truncatedAtProviderLimit"])
        self.assertEqual(result["paginationStatus"], "provider_cap_truncated")
        self.assertEqual(result["records"][0]["photobookCandidateStatus"], "excluded_non_photobook_medium")

    def test_searches_identity_names_and_only_verified_aliases(self):
        terms = identity_terms({
            "name": "Model Canonical", "originalName": "モデル原名", "englishName": "Model English",
        }, {
            "verification_source_url": "https://publisher.test/profile",
            "careerNameEvidence": [
                {"name": "Verified Stage Name", "sourceUrl": "https://publisher.test/name"},
                {"name": "Unverified Alias"},
                {"name": "Model English", "sourceUrl": "https://publisher.test/duplicate"},
            ]
        })

        self.assertEqual([term["nameType"] for term in terms], ["canonical", "native", "english", "verified_alias"])
        self.assertEqual(terms[-1]["evidenceUrl"], "https://publisher.test/name")
        self.assertEqual(terms[0]["evidenceUrls"], ["https://publisher.test/profile"])

    def test_collapses_duplicate_native_and_canonical_query_without_losing_both_name_types(self):
        terms = identity_terms({"name": "鈴木ふみ奈", "originalName": "鈴木ふみ奈", "englishName": "Fumina Suzuki"}, {
            "verification_source_url": "https://publisher.test/fumina",
        })

        self.assertEqual(len(terms), 2)
        self.assertEqual(terms[0]["nameTypes"], ["canonical", "native"])
        self.assertEqual(terms[0]["evidenceUrls"], ["https://publisher.test/fumina"])

    def test_record_deduplication_keeps_distinct_ndl_record_pages_and_terms(self):
        queries = [
            {"term": "Native Name", "records": [
                {"sourcePageUrl": "https://ndl.test/physical", "format": "紙"},
                {"sourcePageUrl": "https://ndl.test/digital", "format": "電子資料"},
            ]},
            {"term": "English Name", "records": [
                {"sourcePageUrl": "https://ndl.test/physical", "format": "紙"},
            ]},
        ]

        merged = _merge_records(queries)

        self.assertEqual(len(merged), 2)
        self.assertEqual(merged[0]["matchedTerms"], ["Native Name", "English Name"])
        self.assertEqual(merged[1]["sourcePageUrl"], "https://ndl.test/digital")


if __name__ == "__main__":
    unittest.main()
