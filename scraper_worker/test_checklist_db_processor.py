import json
import unittest
from pathlib import Path
from unittest.mock import patch

from process_checklist_from_db import (
    crop_image_base_url,
    merge_manifests,
    process_release,
    unique_checklist_media,
)


class ChecklistDatabaseProcessorTest(unittest.TestCase):
    def test_crop_image_base_url_is_stable_and_server_relative(self):
        self.assertEqual(
            "/v1/catalog/media/checklist/woohoo-girls-vol-1/sheet-02",
            crop_image_base_url("woohoo girls vol 1", 2),
        )

    def test_unique_checklist_media_prefers_primary_and_deduplicates_urls(self):
        series = {
            "media": [
                {"id": 2, "mediaType": "checklist_sheet", "originalUrl": "https://example.test/two.jpg"},
                {"id": 1, "mediaType": "checklist_sheet", "isPrimary": True, "originalUrl": "https://example.test/one.jpg"},
                {"id": 3, "mediaType": "checklist_sheet", "originalUrl": "https://example.test/two.jpg"},
                {"id": 4, "mediaType": "release_image", "originalUrl": "https://example.test/cover.jpg"},
            ]
        }

        result = unique_checklist_media(series)

        self.assertEqual(
            ["https://example.test/one.jpg", "https://example.test/two.jpg"],
            [item["originalUrl"] for item in result],
        )

    def test_merge_manifests_resequences_duplicate_groups(self):
        result = merge_manifests(
            release_slug="woohoo-girls-vol-1",
            source_url="https://gain-p.jp/user_data/check_list",
            manifests=[
                {
                    "detectedPanels": 2,
                    "cards": [
                        {"checklistGroup": "Regular Card", "title": "old 001"},
                    ],
                },
                {
                    "detectedPanels": 2,
                    "cards": [
                        {"checklistGroup": "Regular Card", "title": "old 001"},
                        {"checklistGroup": "Rare Card", "title": "old 001"},
                    ],
                },
            ],
            source_image_urls=["https://example.test/one.jpg", "https://example.test/two.jpg"],
        )

        self.assertEqual(4, result["detectedPanels"])
        self.assertEqual(3, result["detectedCards"])
        self.assertEqual(
            ["REGULAR-CARD-001", "REGULAR-CARD-002", "RARE-CARD-001"],
            [card["cardCode"] for card in result["cards"]],
        )
        self.assertEqual([2, 1], [group["designCount"] for group in result["groups"]])

    def test_process_release_reads_db_media_splits_and_imports_manifest(self):
        calls = []
        series = {
            "slug": "woohoo-girls-vol-1",
            "officialChecklistUrl": "https://gain-p.jp/user_data/check_list",
            "media": [
                {
                    "id": 1,
                    "mediaType": "checklist_sheet",
                    "isPrimary": True,
                    "originalUrl": "https://example.test/checklist.jpg",
                    "sourceUrl": "https://gain-p.jp/user_data/check_list",
                }
            ],
        }

        def fake_request(url, *, method="GET", body=None, timeout=0):
            calls.append((url, method, body))
            if method == "GET":
                return {"series": series}
            return {"releaseSlug": "woohoo-girls-vol-1", "cardsSaved": 1}

        work_dir = Path("test-checklist-work")
        with patch("process_checklist_from_db.request_json", side_effect=fake_request), patch(
            "process_checklist_from_db.download_image"
        ), patch(
            "process_checklist_from_db.split_checklist_image",
            return_value={
                "detectedPanels": 1,
                "cards": [{
                    "checklistGroup": "Regular Card",
                    "title": "Regular Card 001",
                    "cardType": "Regular",
                    "cardTypeKey": "regular",
                    "imageUrl": "/v1/catalog/media/checklist/woohoo-girls-vol-1/sheet-01/001-regular-card-001.jpg",
                }],
            },
        ), patch.object(Path, "mkdir"), patch.object(Path, "write_text") as write_text:
            result = process_release(
                api_base_url="http://127.0.0.1:1314/v1/catalog",
                release_slug="woohoo-girls-vol-1",
                work_dir=work_dir,
                replace_existing=False,
                dry_run=False,
                timeout=1800,
            )

        self.assertEqual(1, result["detectedCards"])
        self.assertEqual(2, len(calls))
        self.assertEqual("POST", calls[1][1])
        payload = json.loads(calls[1][2])
        self.assertEqual("woohoo-girls-vol-1", payload["releaseSlug"])
        self.assertFalse(payload["replaceExisting"])
        self.assertEqual(1, len(payload["cards"]))
        self.assertEqual(
            "/v1/catalog/media/checklist/woohoo-girls-vol-1/sheet-01/001-regular-card-001.jpg",
            payload["cards"][0]["imageUrl"],
        )
        self.assertEqual("regular", payload["cards"][0]["cardTypeKey"])
        write_text.assert_called_once()
        self.assertIn('"cards"', write_text.call_args.args[0])


if __name__ == "__main__":
    unittest.main()
