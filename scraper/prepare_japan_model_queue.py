"""Prepare resumable model inputs from a read-only MuseCards export."""
import argparse
import json
from pathlib import Path

from capture_checkpoint import save_json


ROOT = Path(__file__).resolve().parent.parent
QUEUE_ROOT = ROOT / "scraper/japan-models"
DEFAULT_SOURCES = {
    "ndl-national-bibliography-jp": "pending",
    "yahoo-auctions-jp": "pending",
    "yahoo-furima-jp": "pending",
    "rakuma": "permission_review_required",
    "grajapa-jp": "pending",
    "rakuten-kobo-jp": "permission_review_required",
    "wani-books-jp": "permission_review_required",
    "mercari-jp": "permission_review_required",
    "suruga-ya-jp": "permission_review_required",
    "bookoff-jp": "permission_review_required",
    "mandarake-jp": "permission_review_required",
    "rakuten-books-jp": "permission_review_required",
    "kinokuniya-jp": "permission_review_required",
    "yodobashi-jp": "permission_review_required",
    "hmv-jp": "permission_review_required",
    "amazon-jp": "permission_review_required",
    "bookwalker-jp": "permission_review_required",
    "booklive-jp": "permission_review_required",
    "dmm-books-jp": "permission_review_required",
}
SOURCE_AUTHORIZATION = {
    "ndl-national-bibliography-jp": "metadata_reuse_permitted_with_attribution",
    "yahoo-auctions-jp": "permission_unverified",
    "yahoo-furima-jp": "permission_unverified",
    "rakuma": "blocked_by_terms",
    "mercari-jp": "permission_unverified",
    "suruga-ya-jp": "permission_unverified",
    "bookoff-jp": "permission_required",
    "mandarake-jp": "permission_unverified",
    "rakuten-books-jp": "permission_required",
    "rakuten-kobo-jp": "blocked_by_terms",
    "grajapa-jp": "permission_unverified",
    "wani-books-jp": "blocked_by_terms",
    "bookwalker-jp": "permission_unverified",
    "booklive-jp": "permission_unverified",
    "dmm-books-jp": "permission_unverified",
    "amazon-jp": "blocked_by_terms",
    "kinokuniya-jp": "permission_unverified",
    "yodobashi-jp": "permission_unverified",
    "hmv-jp": "permission_unverified",
    "publisher-bibliography-jp": "manual_verification_only_pending_permission",
    "tokyonews-publisher-catalog": "permission_required",
    "kodansha-publisher-catalog": "permission_unverified",
    "genkosha-publisher-catalog": "permission_unverified",
}


def newest_snapshot(queue_root=QUEUE_ROOT):
    """Prefer the latest dated export while keeping the archival base export."""
    snapshots = sorted(queue_root.glob("musecards-models-????????.json"))
    return snapshots[-1] if snapshots else queue_root / "musecards-models.json"


def prepare(snapshot_path, project_root=ROOT):
    project_root = Path(project_root)
    queue_root = project_root / "scraper/japan-models"
    queue_path = queue_root / "queue.json"
    snapshot = json.loads(Path(snapshot_path).read_text(encoding="utf-8-sig"))
    previous_rows = json.loads(queue_path.read_text(encoding="utf-8")) if queue_path.exists() else []
    previous = {row["musecardsPersonId"]: row for row in previous_rows}
    careers = {}
    for record in snapshot.get("careerNames", []):
        if record.get("person_id") and record.get("name"):
            careers.setdefault(record["person_id"], []).append(record)

    current_ids = set()
    queue = []
    alias_groups = []
    for source_person in snapshot["models"]:
        person = dict(source_person)
        person_id = person["id"]
        current_ids.add(person_id)
        career_records = careers.get(person_id, [])
        person["aliases"] = list(dict.fromkeys(record["name"] for record in career_records))
        person["careerNameEvidence"] = [
            {
                "name": record["name"],
                "nameType": record.get("name_type", ""),
                "sourceUrl": record.get("source_url", ""),
                "verifiedAt": record.get("verified_at", ""),
            }
            for record in career_records
        ]
        names = list(dict.fromkeys(
            name for name in [person.get("canonical_public_name"), person.get("original_name"),
                person.get("english_name"), *person["aliases"]] if name
        ))
        alias_groups.append(names)

        directory = queue_root / str(person_id)
        directory.mkdir(parents=True, exist_ok=True)
        model_path = directory / "model.json"
        # Fumina's model input sits beside the original captures; keep that
        # established file byte-for-byte and refresh only the current queue name.
        if person_id != 6 or not model_path.exists():
            save_json(model_path, {"models": [person]})

        old = previous.get(person_id, {})
        row = {
            **old,
            "musecardsPersonId": person_id,
            "name": person.get("canonical_public_name", ""),
            "originalName": person.get("original_name") or "",
            "englishName": person.get("english_name") or "",
            "verificationSourceUrl": person.get("verification_source_url") or "",
            "careerNameCount": len(career_records),
            "japanReleaseCount": person.get("japan_release_count", 0),
            "relationshipEvidenceCount": len(person.get("japan_release_evidence", [])),
            "identityEvidenceCount": int(bool(person.get("verification_source_url"))) + len(career_records),
            "identitySnapshotRetrievedAt": snapshot.get("retrieved_at", ""),
            "originalNameUnknown": not bool(person.get("original_name")),
            "englishNameUnknown": not bool(person.get("english_name")),
            "sourceAuthorization": dict(SOURCE_AUTHORIZATION),
            "directory": (Path("scraper/japan-models") / str(person_id)).as_posix(),
            "status": "reuse_fumina_capture" if person_id == 6 else old.get("status", "pending"),
            "sources": {**DEFAULT_SOURCES, **old.get("sources", {})},
        }
        queue.append(row)

    retired_path = queue_root / "retired-models.json"
    retired_rows = json.loads(retired_path.read_text(encoding="utf-8")) if retired_path.exists() else []
    retired = {row["musecardsPersonId"]: row for row in retired_rows}
    for person_id in current_ids:
        retired.pop(person_id, None)
    for row in previous_rows:
        person_id = row["musecardsPersonId"]
        if person_id not in current_ids:
            retired.setdefault(person_id, {
                **row,
                "retiredFromCurrentSnapshotAt": snapshot.get("retrieved_at", ""),
                "retirementReason": "MuseCards no longer links this person to a Japan-origin release.",
            })
    save_json(retired_path, sorted(retired.values(), key=lambda row: row["musecardsPersonId"]))
    save_json(queue_path, queue)

    alias_path = project_root / "frontend/src/lib/model-search-aliases.js"
    alias_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = alias_path.with_suffix(alias_path.suffix + ".new")
    temporary.write_text(
        "// Generated from the read-only MuseCards model export.\nexport default "
        + json.dumps(alias_groups, ensure_ascii=False, indent=2) + ";\n",
        encoding="utf-8",
    )
    temporary.replace(alias_path)
    return {"models": len(queue), "retired": len(retired), "aliasGroups": len(alias_groups)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", default=str(newest_snapshot()),
        help="Read-only MuseCards export; defaults to the latest dated snapshot")
    args = parser.parse_args()
    print(json.dumps(prepare(args.snapshot), ensure_ascii=False))


if __name__ == "__main__":
    main()
