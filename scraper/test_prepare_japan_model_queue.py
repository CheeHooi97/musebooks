import json
import tempfile
import unittest
from pathlib import Path

from prepare_japan_model_queue import prepare


class PrepareJapanModelQueueTests(unittest.TestCase):
    def test_refresh_preserves_capture_state_and_fumina_model_bytes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            queue_root = root / "scraper/japan-models"
            queue_root.mkdir(parents=True)
            fumina_dir = queue_root / "6"
            fumina_dir.mkdir()
            fumina_model = fumina_dir / "model.json"
            fumina_bytes = b'{"models":[{"id":6,"legacy":true}]}\r\n'
            fumina_model.write_bytes(fumina_bytes)
            (queue_root / "queue.json").write_text(json.dumps([
                {"musecardsPersonId": 6, "name": "Old Fumina", "status": "running",
                 "sources": {"yahoo-auctions-jp": "finished"}},
                {"musecardsPersonId": 9, "name": "Removed model", "status": "finished",
                 "sources": {"grajapa-jp": "public_search_exhausted"}},
            ]), encoding="utf-8")
            (queue_root / "retired-models.json").write_text(json.dumps([
                {"musecardsPersonId": 7, "name": "Reactivated", "retirementReason": "old"}
            ]), encoding="utf-8")
            snapshot = root / "snapshot.json"
            snapshot.write_text(json.dumps({
                "retrieved_at": "2026-11-01T05:02:30Z",
                "models": [
                    {"id": 6, "canonical_public_name": "鈴木ふみ奈", "original_name": "鈴木ふみ奈",
                     "english_name": "Fumina Suzuki", "verification_source_url": "https://publisher.test/fumina",
                     "japan_release_count": 2, "japan_release_evidence": [{"set_id": 1}]},
                    {"id": 7, "canonical_public_name": "Reactivated", "original_name": "原名",
                     "english_name": "English Name", "verification_source_url": "https://publisher.test/reactivated",
                     "japan_release_count": 1, "japan_release_evidence": []},
                ],
                "careerNames": [
                    {"person_id": 6, "name": "ふみにゃん", "name_type": "former",
                     "source_url": "https://publisher.test/alias", "verified_at": "2026-10-01"},
                    {"person_id": 7, "name": "Former Model Name", "name_type": "former",
                     "source_url": "https://publisher.test/reactivated-alias", "verified_at": "2026-10-02"}
                ],
            }, ensure_ascii=False), encoding="utf-8")

            result = prepare(snapshot, root)

            self.assertEqual(result["models"], 2)
            queue = json.loads((queue_root / "queue.json").read_text(encoding="utf-8"))
            fumina, reactivated = queue
            self.assertEqual(fumina["status"], "reuse_fumina_capture")
            self.assertEqual(fumina["sources"]["yahoo-auctions-jp"], "finished")
            self.assertEqual(fumina["sources"]["rakuten-kobo-jp"], "permission_review_required")
            self.assertEqual(fumina["sourceAuthorization"]["rakuten-kobo-jp"], "blocked_by_terms")
            self.assertEqual(fumina["sources"]["ndl-national-bibliography-jp"], "pending")
            self.assertEqual(fumina["sourceAuthorization"]["ndl-national-bibliography-jp"], "metadata_reuse_permitted_with_attribution")
            self.assertEqual(fumina["identitySnapshotRetrievedAt"], "2026-11-01T05:02:30Z")
            self.assertEqual(fumina["relationshipEvidenceCount"], 1)
            self.assertEqual(fumina_model.read_bytes(), fumina_bytes)
            self.assertEqual(reactivated["status"], "pending")
            retired = json.loads((queue_root / "retired-models.json").read_text(encoding="utf-8"))
            self.assertEqual([row["musecardsPersonId"] for row in retired], [9])
            model = json.loads((queue_root / "7/model.json").read_text(encoding="utf-8"))["models"][0]
            self.assertEqual(model["aliases"], ["Former Model Name"])
            self.assertEqual(model["careerNameEvidence"][0]["sourceUrl"], "https://publisher.test/reactivated-alias")

    def test_retired_capture_rows_are_archived_without_deleting_them(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            queue_root = root / "scraper/japan-models"
            queue_root.mkdir(parents=True)
            capture = queue_root / "99/physical-state.json"
            capture.parent.mkdir()
            capture.write_text('{"status":"source_failed"}', encoding="utf-8")
            (queue_root / "queue.json").write_text(json.dumps([
                {"musecardsPersonId": 99, "name": "Old model", "directory": "scraper/japan-models/99",
                 "status": "process_failed", "sources": {}}
            ]), encoding="utf-8")
            snapshot = root / "snapshot.json"
            snapshot.write_text(json.dumps({"retrieved_at": "2026-11-01T00:00:00Z", "models": [], "careerNames": []}), encoding="utf-8")

            prepare(snapshot, root)

            retired = json.loads((queue_root / "retired-models.json").read_text(encoding="utf-8"))
            self.assertEqual(retired[0]["musecardsPersonId"], 99)
            self.assertTrue(capture.exists())


if __name__ == "__main__":
    unittest.main()
