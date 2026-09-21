#!/usr/bin/env python3
"""Split checklist images already referenced by the catalog and import the cards.

The catalog stores checklist image references in ``catalog_media``. This helper
uses the local catalog API to read an existing release, downloads every unique
``checklist_sheet`` image, runs the image splitter, merges the detected tiles,
and sends the reviewed-manifest shape back to the checklist import endpoint.

It intentionally keeps the database operation behind the API instead of
requiring PostgreSQL credentials on the server shell. The generated card codes
remain inferred until an operator reviews them.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from checklist_splitter import split_checklist_image


DEFAULT_TIMEOUT_SECONDS = 1800
MAX_DOWNLOAD_BYTES = 100 * 1024 * 1024


class ChecklistProcessorError(RuntimeError):
    """Raised when a DB-driven checklist processing step cannot continue."""


def api_url(api_base_url: str, path: str) -> str:
    return api_base_url.rstrip("/") + "/" + path.lstrip("/")


def unwrap_api_result(payload: Any) -> Any:
    if isinstance(payload, dict) and "result" in payload:
        if payload.get("error"):
            message = payload.get("errmsg") or "catalog API returned an error"
            raise ChecklistProcessorError(str(message))
        return payload["result"]
    return payload


def request_json(
    url: str,
    *,
    method: str = "GET",
    body: bytes | None = None,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> Any:
    headers = {"Accept": "application/json"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    request = Request(url, data=body, headers=headers, method=method)
    try:
        with urlopen(request, timeout=timeout) as response:
            raw = response.read()
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise ChecklistProcessorError(f"HTTP {exc.code} from {url}: {detail}") from exc
    except URLError as exc:
        raise ChecklistProcessorError(f"request failed for {url}: {exc.reason}") from exc
    try:
        return unwrap_api_result(json.loads(raw.decode("utf-8")))
    except json.JSONDecodeError as exc:
        raise ChecklistProcessorError(f"API returned invalid JSON from {url}") from exc


def media_urls(media: dict[str, Any]) -> list[str]:
    urls: list[str] = []
    for key in ("storageUrl", "originalUrl", "discoveredUrl"):
        value = str(media.get(key) or "").strip()
        if value.startswith(("http://", "https://")) and value not in urls:
            urls.append(value)
    return urls


def media_url(media: dict[str, Any]) -> str:
    urls = media_urls(media)
    return urls[0] if urls else ""


def unique_checklist_media(series: dict[str, Any]) -> list[dict[str, Any]]:
    media = series.get("media") or []
    candidates = [
        item
        for item in media
        if isinstance(item, dict) and item.get("mediaType") == "checklist_sheet"
    ]
    candidates.sort(
        key=lambda item: (
            not bool(item.get("isPrimary")),
            int(item.get("sequence") or 0),
            int(item.get("id") or 0),
        )
    )
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in candidates:
        url = media_url(item)
        if not url or url in seen:
            continue
        seen.add(url)
        result.append(item)
    return result


def source_url(series: dict[str, Any], media: dict[str, Any]) -> str:
    return str(
        series.get("officialChecklistUrl")
        or media.get("sourceUrl")
        or series.get("officialProductUrl")
        or ""
    ).strip()


def safe_slug(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9._-]+", "-", value.strip())
    return value.strip("-.") or "checklist"


def crop_image_base_url(release_slug: str, sheet_index: int) -> str:
    return f"/v1/catalog/media/checklist/{safe_slug(release_slug)}/sheet-{sheet_index:02d}"


def group_key(label: str) -> str:
    key = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
    return key or "checklist"


def download_image(url: str, destination: Path, timeout: int) -> None:
    request = Request(url, headers={"User-Agent": "MuseCards checklist processor/1.0"})
    try:
        with urlopen(request, timeout=timeout) as response:
            content_length = response.headers.get("Content-Length")
            if content_length and int(content_length) > MAX_DOWNLOAD_BYTES:
                raise ChecklistProcessorError(
                    f"checklist image is larger than {MAX_DOWNLOAD_BYTES} bytes: {url}"
                )
            destination.parent.mkdir(parents=True, exist_ok=True)
            total = 0
            with destination.open("wb") as output:
                while chunk := response.read(1024 * 1024):
                    total += len(chunk)
                    if total > MAX_DOWNLOAD_BYTES:
                        raise ChecklistProcessorError(
                            f"checklist image is larger than {MAX_DOWNLOAD_BYTES} bytes: {url}"
                        )
                    output.write(chunk)
    except HTTPError as exc:
        raise ChecklistProcessorError(f"HTTP {exc.code} downloading checklist image {url}") from exc
    except URLError as exc:
        raise ChecklistProcessorError(f"download failed for {url}: {exc.reason}") from exc


def merge_manifests(
    *,
    release_slug: str,
    source_url: str,
    manifests: list[dict[str, Any]],
    source_image_urls: list[str],
) -> dict[str, Any]:
    cards: list[dict[str, Any]] = []
    groups: dict[str, dict[str, Any]] = {}
    group_order: list[str] = []

    for manifest, source_image_url in zip(manifests, source_image_urls):
        for raw_card in manifest.get("cards") or []:
            card = dict(raw_card)
            label = str(card.get("checklistGroup") or "Checklist").strip() or "Checklist"
            key = group_key(label)
            group = groups.get(key)
            if group is None:
                group = {
                    "key": key,
                    "label": label,
                    "designCount": 0,
                    "sequence": len(group_order) + 1,
                    "sourceConfidence": "official_image",
                }
                groups[key] = group
                group_order.append(key)

            group["designCount"] += 1
            ordinal = int(group["designCount"])
            sequence = len(cards) + 1
            card["cardCode"] = f"{key.upper()}-{ordinal:03d}"
            card["normalizedCardCode"] = card["cardCode"]
            card["checklistGroup"] = label
            card["checklistImageUrl"] = source_image_url
            card["title"] = f"{label} {ordinal:03d}"
            card["checklistSequence"] = sequence
            card["sourceUrl"] = str(card.get("sourceUrl") or source_url).strip()
            card["sourceConfidence"] = str(card.get("sourceConfidence") or "inferred")
            cards.append(card)

    if not cards:
        raise ChecklistProcessorError("the splitter detected no checklist tiles")

    return {
        "sourceUrl": source_url,
        "sourceImageUrl": source_image_urls[0] if source_image_urls else "",
        "releaseSlug": release_slug,
        "groups": [groups[key] for key in group_order],
        "cards": cards,
        "detectedPanels": sum(int(item.get("detectedPanels") or 0) for item in manifests),
        "detectedCards": len(cards),
    }


def process_release(
    *,
    api_base_url: str,
    release_slug: str,
    work_dir: Path,
    replace_existing: bool,
    dry_run: bool,
    timeout: int,
) -> dict[str, Any]:
    encoded_slug = quote(release_slug, safe="")
    series_result = request_json(
        api_url(api_base_url, f"/sets/{encoded_slug}"), timeout=timeout
    )
    series = series_result.get("series") if isinstance(series_result, dict) else None
    if not isinstance(series, dict):
        raise ChecklistProcessorError(f"release was not found: {release_slug}")

    checklist_media = unique_checklist_media(series)
    if not checklist_media:
        raise ChecklistProcessorError(
            f"no checklist_sheet media URL found for release {release_slug}; "
            "the database stores references, not image bytes"
        )

    work_dir.mkdir(parents=True, exist_ok=True)
    crop_dir = work_dir / "crops"
    manifests: list[dict[str, Any]] = []
    source_image_urls: list[str] = []
    for index, media in enumerate(checklist_media, start=1):
        image_url = ""
        image_path = work_dir / f"source-{index:02d}.image"
        download_error: ChecklistProcessorError | None = None
        for candidate_url in media_urls(media):
            print(f"Downloading checklist image {index}/{len(checklist_media)}: {candidate_url}")
            try:
                download_image(candidate_url, image_path, timeout)
                image_url = candidate_url
                break
            except ChecklistProcessorError as exc:
                download_error = exc
        if not image_url:
            raise download_error or ChecklistProcessorError(
                f"no downloadable URL found for checklist image {index}"
            )
        print(f"Splitting checklist image {index}/{len(checklist_media)}")
        manifest = split_checklist_image(
            image_path,
            release_slug=release_slug,
            source_url=source_url(series, media),
            source_image_url=image_url,
            output_dir=crop_dir / f"sheet-{index:02d}",
            image_base_url=crop_image_base_url(release_slug, index),
        )
        manifests.append(manifest)
        source_image_urls.append(image_url)

    official_source_url = str(series.get("officialChecklistUrl") or "").strip()
    if not official_source_url:
        official_source_url = source_url(series, checklist_media[0])
    merged = merge_manifests(
        release_slug=release_slug,
        source_url=official_source_url,
        manifests=manifests,
        source_image_urls=source_image_urls,
    )
    manifest_path = work_dir / f"{safe_slug(release_slug)}.checklist.json"
    manifest_path.write_text(
        json.dumps(merged, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Wrote {merged['detectedCards']} cards to {manifest_path}")

    if dry_run:
        return {"manifest": str(manifest_path), "detectedCards": merged["detectedCards"], "dryRun": True}

    payload = dict(merged)
    payload["replaceExisting"] = replace_existing
    import_result = request_json(
        api_url(api_base_url, f"/sets/{encoded_slug}/checklist/import"),
        method="POST",
        body=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        timeout=timeout,
    )
    print(json.dumps(import_result, ensure_ascii=False, indent=2))
    return {
        "manifest": str(manifest_path),
        "detectedCards": merged["detectedCards"],
        "import": import_result,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Process checklist_sheet images from an existing catalog release"
    )
    parser.add_argument("--release-slug", required=True)
    parser.add_argument("--api-base-url", default="http://127.0.0.1:1314/v1/catalog")
    parser.add_argument("--work-dir", default="")
    parser.add_argument("--replace-existing", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    work_dir = Path(args.work_dir) if args.work_dir else Path("/tmp") / "musecards-checklist" / safe_slug(args.release_slug)
    try:
        result = process_release(
            api_base_url=args.api_base_url,
            release_slug=args.release_slug,
            work_dir=work_dir,
            replace_existing=args.replace_existing,
            dry_run=args.dry_run,
            timeout=args.timeout,
        )
    except ChecklistProcessorError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
