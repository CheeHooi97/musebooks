"""Split image-only trading-card checklists into an importable manifest.

The official WooHoo checklist is a blue sheet containing many small card
thumbnails.  It is evidence for real card designs, but it is not an HTML table
that the normal checklist worker can parse.  This utility detects the sheet
panels and card-like rectangles, writes optional crops for review, and emits
the JSON accepted by ``POST /v1/catalog/sets/:slug/checklist/import``.

The generated card codes are intentionally marked as inferred.  They are
stable for the same sheet ordering, but they are not claimed to be printed
publisher codes unless an operator edits the manifest before importing it.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import cv2
import numpy as np


RIGHT_SECTION_BANDS = (
    (0.00, 0.13, "Rare Card"),
    (0.13, 0.23, "Photogenic / Costume Card"),
    (0.23, 0.45, "Super Rare Card"),
    (0.45, 0.60, "Premium Rare Card"),
    (0.60, 0.70, "Double Rare Card"),
    (0.70, 0.82, "Triple Rare Card"),
    (0.82, 0.91, "Masterpiece Rare Card"),
    (0.91, 1.01, "Privilege Card"),
)


def slug_key(value: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", str(value or "").lower()).strip("-")
    return value or "checklist"


def _panel_components(
    mask: np.ndarray, image: np.ndarray
) -> list[tuple[int, int, int, int]]:
    """Turn a color mask into large, vertically oriented panel rectangles."""
    height, width = image.shape[:2]
    mask = (mask.astype(np.uint8) * 255) if mask.max() <= 1 else mask.astype(np.uint8)
    close_size = max(3, round(min(height, width) * 0.004))
    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_CLOSE,
        np.ones((close_size, close_size), dtype=np.uint8),
    )
    count, _, stats, _ = cv2.connectedComponentsWithStats(mask, 8)
    min_area = height * width * 0.012
    panels: list[tuple[int, int, int, int]] = []
    for x, y, panel_width, panel_height, area in stats[1:]:
        if area < min_area or panel_height < height * 0.35 or panel_width < width * 0.06:
            continue
        # Some WooHoo special-card sheets are intentionally wide. Do not
        # reject those panels before their horizontal card tiles are found.
        if panel_width / max(panel_height, 1) > 5.0:
            continue
        panels.append((int(x), int(y), int(panel_width), int(panel_height)))
    return sorted(panels, key=lambda item: (item[1], item[0]))


def _corner_contrast_mask(image: np.ndarray) -> np.ndarray:
    """Find panels whose color is distinct from the outer image background."""
    height, width = image.shape[:2]
    size = max(4, round(min(height, width) * 0.025))
    corners = np.concatenate(
        [
            image[:size, :size],
            image[:size, max(0, width - size) : width],
            image[max(0, height - size) : height, :size],
            image[max(0, height - size) : height, max(0, width - size) : width],
        ],
        axis=0,
    )
    background = np.median(corners, axis=(0, 1)).astype(np.float32)
    distance = np.sqrt(((image.astype(np.float32) - background) ** 2).sum(axis=2))
    corner_distance = np.sqrt(((corners.astype(np.float32) - background) ** 2).sum(axis=2))
    threshold = max(24.0, float(np.percentile(corner_distance, 99)) + 12.0)
    return distance > threshold


def find_panels(image: np.ndarray) -> list[tuple[int, int, int, int]]:
    """Find large checklist panels without assuming one exact blue color.

    Publisher images vary between source PNGs, compressed JPGs, screenshots,
    and color profiles. The first mask keeps the original blue-sheet behavior;
    the later masks handle hue shifts, muted panels, and non-blue checklists.
    """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    blue = image[:, :, 0].astype(np.int16)
    green = image[:, :, 1].astype(np.int16)
    red = image[:, :, 2].astype(np.int16)
    masks = (
        (blue > 55) & (blue > red * 1.15) & (blue > green * 1.15),
        (hsv[:, :, 1] > 35) & (hsv[:, :, 2] > 35),
        _corner_contrast_mask(image),
    )
    for mask in masks:
        panels = _panel_components(mask, image)
        if panels:
            return panels
    return []


def _panel_background(panel: np.ndarray) -> np.ndarray:
    border = np.concatenate(
        [panel[0, :, :], panel[-1, :, :], panel[:, 0, :], panel[:, -1, :]],
        axis=0,
    )
    return np.median(border, axis=0).astype(np.float32)


def _tile_components(panel: np.ndarray) -> list[tuple[int, int, int, int, int]]:
    background = _panel_background(panel)
    distance = np.sqrt(((panel.astype(np.float32) - background) ** 2).sum(axis=2))
    mask = (distance > 30).astype(np.uint8) * 255
    close_kernel = max(1, round(min(panel.shape[:2]) * 0.003))
    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_CLOSE,
        np.ones((close_kernel, close_kernel), dtype=np.uint8),
    )
    count, _, stats, _ = cv2.connectedComponentsWithStats(mask, 8)
    return [tuple(int(value) for value in row) for row in stats[1:]]


def _is_three_by_three_grid(
    width: int,
    height: int,
    area: int,
    panel_width: int,
    panel_height: int,
) -> bool:
    """Recognize a regular-card 3x3 block embedded in the checklist sheet."""
    aspect = width / max(height, 1)
    return (
        width >= panel_width * 0.15
        and height >= panel_height * 0.10
        and 0.55 <= aspect <= 0.95
        and area >= width * height * 0.55
    )


def _looks_like_regular_sheet(panel: np.ndarray) -> bool:
    panel_height, panel_width = panel.shape[:2]
    return any(
        _is_three_by_three_grid(width, height, area, panel_width, panel_height)
        for _, _, width, height, area in _tile_components(panel)
    )


def find_tiles(panel: np.ndarray) -> list[tuple[int, int, int, int]]:
    """Find card thumbnails while ignoring small text and divider lines."""
    panel_height, panel_width = panel.shape[:2]
    min_width = max(8, round(panel_width * 0.025))
    max_width = max(min_width + 1, round(panel_width * 0.16))
    min_height = max(12, round(panel_height * 0.025))
    min_tile_width = max(min_width + 1, round(min_width * 1.25))
    min_tile_height = max(min_height + 1, round(min_height * 1.25))
    # Low-resolution screenshots compress a 3x3 block into a small panel, so
    # each card can occupy roughly a quarter of the panel height. The original
    # limit is still preferable for the larger official sheets because it
    # avoids treating headings as card tiles.
    max_height_ratio = 0.30 if panel_height < 500 else 0.12
    max_height = max(min_height + 1, round(panel_height * max_height_ratio))
    min_area = max(100, round(panel_width * panel_height * 0.0012))
    horizontal_max_width = max(min_width + 1, round(panel_width * 0.30))
    horizontal_min_height = max(18, round(panel_height * 0.04))
    horizontal_max_height = max(max_height + 1, round(panel_height * 0.35))
    # A low-contrast card can lose part of its connected component against the
    # sheet background. Keep a small margin below the normal area floor so the
    # tile is still accepted by its portrait dimensions and aspect ratio.
    min_tile_area = round(max(min_area, min_width * min_height * 1.4) * 0.90)
    tiles: list[tuple[int, int, int, int]] = []
    for x, y, width, height, area in _tile_components(panel):
        if _is_three_by_three_grid(width, height, area, panel_width, panel_height):
            for row in range(3):
                for column in range(3):
                    left = x + round(column * width / 3)
                    top = y + round(row * height / 3)
                    right = x + round((column + 1) * width / 3)
                    bottom = y + round((row + 1) * height / 3)
                    tiles.append((left, top, right - left, bottom - top))
            continue
        aspect = width / max(height, 1)
        portrait_tile = (
            min_tile_width <= width <= max_width
            and min_tile_height <= height <= max_height
            and 0.35 <= aspect <= 1.7
        )
        horizontal_tile = (
            min_tile_width <= width <= horizontal_max_width
            and max(horizontal_min_height, min_tile_height) <= height <= horizontal_max_height
            and 1.15 <= aspect <= 3.2
        )
        if area < min_tile_area or not (portrait_tile or horizontal_tile):
            continue
        tiles.append((int(x), int(y), int(width), int(height)))
    # JPEG compression and soft card borders can move the detected top edge by
    # a few pixels. Cluster nearby y positions into visual rows before sorting
    # by x; exact-coordinate sorting can otherwise move the third card behind
    # the first two and corrupt the checklist sequence.
    if len(tiles) < 2:
        return tiles
    median_height = float(np.median([item[3] for item in tiles]))
    row_tolerance = max(4, round(median_height * 0.15))
    rows: list[list[tuple[int, int, int, int]]] = []
    for tile in sorted(tiles, key=lambda item: (item[1], item[0])):
        if not rows or tile[1] - min(item[1] for item in rows[-1]) > row_tolerance:
            rows.append([tile])
        else:
            rows[-1].append(tile)
    return [tile for row in rows for tile in sorted(row, key=lambda item: item[0])]


def right_section(relative_y: float, relative_x: float) -> str:
    for start, end, label in RIGHT_SECTION_BANDS:
        if start <= relative_y < end:
            if label == "Photogenic / Costume Card":
                return "Photogenic Card" if relative_x < 0.25 else "Costume Card"
            return label
    return "Rare / Special Card"


def card_type_for_tile(
    checklist_group: str, relative_x: float, relative_y: float
) -> tuple[str, str]:
    """Return the display label and stable key for one WooHoo tile.

    WooHoo publishes the card types as fixed visual blocks rather than text
    attached to every thumbnail.  The parent section comes from
    ``right_section``; the finer x/y bands below identify the sub-type inside
    the Super Rare and Privilege sections.
    """
    group = str(checklist_group or "").strip()
    if group == "Regular Card":
        return "Regular", "regular"
    if group == "Rare Card":
        return "Photo", "photo_card"
    if group == "Photogenic Card":
        return "Photogenic", "photogenic_card"
    if group == "Costume Card":
        return "Costume", "costume_card"

    if group == "Super Rare Card":
        local_y = (relative_y - 0.23) / 0.22
        if local_y < 0.34:
            return ("Autograph", "autograph") if relative_x < 0.55 else ("Nail", "nail")
        if local_y < 0.68:
            return ("Kiss", "kiss_card") if relative_x < 0.55 else ("Bikini Strap", "bikini_strap")
        return ("Real Cheki", "real_cheki") if relative_x < 0.30 else ("Stockings", "stockings")
    if group == "Premium Rare Card":
        return "Pin-spot Bikini", "pin_spot_bikini"
    if group == "Double Rare Card":
        return "Autograph & Kiss", "autograph_kiss"
    if group == "Triple Rare Card":
        return "Pin-spot Bikini All", "pin_spot_bikini_all"
    if group == "Masterpiece Rare Card":
        return "1of1 Bikini Hook", "one_of_one_bikini_hook"
    if group == "Privilege Card":
        return (
            ("Shop Campaign Privilege", "shop_campaign_privilege")
            if relative_x < 0.55
            else ("Event Privilege", "event_privilege")
        )
    return "", ""


def trim_warm_checklist_frame(tile: np.ndarray) -> np.ndarray:
    """Remove a warm brown/orange frame left around a checklist thumbnail.

    Some WooHoo sheets render each thumbnail on a warm panel and the connected
    component includes that panel color around the actual card image. Only
    trim consecutive edge rows/columns that are overwhelmingly warm, which
    avoids cutting normal image content or blue/white card borders.
    """
    if tile.size == 0 or tile.shape[0] < 12 or tile.shape[1] < 12:
        return tile

    hsv = cv2.cvtColor(tile, cv2.COLOR_BGR2HSV)
    warm = (
        (hsv[:, :, 0] <= 28)
        & (hsv[:, :, 1] >= 42)
        & (hsv[:, :, 2] >= 70)
    )
    height, width = warm.shape
    max_trim_y = max(1, round(height * 0.14))
    max_trim_x = max(1, round(width * 0.14))

    def leading_depth(axis: int, limit: int) -> int:
        depth = 0
        for index in range(limit):
            line = warm[index, :] if axis == 0 else warm[:, index]
            if float(line.mean()) < 0.78:
                break
            depth += 1
        return depth

    top = leading_depth(0, max_trim_y)
    bottom = leading_depth(0, max_trim_y)
    left = leading_depth(1, max_trim_x)
    right = leading_depth(1, max_trim_x)

    # Scan the opposite edges from the correct direction.
    bottom = 0
    for index in range(1, max_trim_y + 1):
        if float(warm[-index, :].mean()) < 0.78:
            break
        bottom += 1
    right = 0
    for index in range(1, max_trim_x + 1):
        if float(warm[:, -index].mean()) < 0.78:
            break
        right += 1

    if top + bottom >= height - 8 or left + right >= width - 8:
        return tile
    return tile[top : height - bottom, left : width - right]


def split_checklist_image(
    image_path: str | Path,
    *,
    release_slug: str,
    source_url: str = "",
    source_image_url: str = "",
    output_dir: str | Path | None = None,
    image_base_url: str = "",
    only_sequence: int | None = None,
    only_group: str | None = None,
    only_ordinal: int | None = None,
) -> dict[str, Any]:
    if only_sequence is not None and only_sequence <= 0:
        raise ValueError("only_sequence must be a positive checklist sequence")
    if (only_group is None) != (only_ordinal is None):
        raise ValueError("only_group and only_ordinal must be provided together")
    if only_ordinal is not None and only_ordinal <= 0:
        raise ValueError("only_ordinal must be a positive group position")

    only_group_key = slug_key(only_group) if only_group else None

    image = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"cannot read checklist image: {image_path}")
    panels = find_panels(image)
    if not panels:
        raise ValueError(
            "no checklist panels were detected; verify the downloaded image is a checklist sheet"
        )

    crop_dir = Path(output_dir) if output_dir else None
    if crop_dir:
        crop_dir.mkdir(parents=True, exist_ok=True)

    groups: list[dict[str, Any]] = []
    cards: list[dict[str, Any]] = []
    group_ordinals: dict[str, int] = {}
    selected_group_ordinals: dict[str, int] = {}
    global_sequence = 0
    for panel_index, (x, y, width, height) in enumerate(panels):
        panel = image[y : y + height, x : x + width]
        tiles = find_tiles(panel)
        regular_panel = panel_index == 0 and (
            len(panels) > 1
            or _looks_like_regular_sheet(panel)
            # A compact screenshot may not contain one connected 3x3 block,
            # but a regular front/back sheet still has a dense 18-tile grid.
            or (height < 500 and len(tiles) >= 14)
            # Full regular checklists contain many repeated [n-n] blocks in a
            # single tall panel rather than one connected 3x3 component.
            or (height > width and len(tiles) >= 100)
        )
        for tile_x, tile_y, tile_width, tile_height in tiles:
            global_sequence += 1
            relative_x = tile_x / max(width, 1)
            relative_y = tile_y / max(height, 1)
            group = "Regular Card" if regular_panel else right_section(relative_y, relative_x)
            card_type, card_type_key = card_type_for_tile(group, relative_x, relative_y)
            group_key = slug_key(group)
            group_ordinals[group_key] = group_ordinals.get(group_key, 0) + 1
            ordinal = group_ordinals[group_key]
            selected = True
            if only_sequence is not None:
                selected = global_sequence == only_sequence
            if only_group_key is not None:
                selected = group_key == only_group_key and ordinal == only_ordinal
            if not selected:
                continue

            selected_group_ordinals[group_key] = selected_group_ordinals.get(group_key, 0) + 1
            card_code = f"{group_key.upper()}-{ordinal:03d}"
            crop_path = ""
            image_url = ""
            if crop_dir:
                # A small padding keeps the colored border in the evidence
                # crop without pulling in the adjacent checklist label.
                padding = max(1, round(min(width, height) * 0.004))
                left = max(0, x + tile_x - padding)
                top = max(0, y + tile_y - padding)
                right = min(image.shape[1], x + tile_x + tile_width + padding)
                bottom = min(image.shape[0], y + tile_y + tile_height + padding)
                crop_name = f"{global_sequence:03d}-{slug_key(group)}-{ordinal:03d}.jpg"
                crop_path = str(crop_dir / crop_name)
                crop = trim_warm_checklist_frame(image[top:bottom, left:right])
                cv2.imwrite(crop_path, crop, [cv2.IMWRITE_JPEG_QUALITY, 94])
                if image_base_url:
                    image_url = image_base_url.rstrip("/") + "/" + crop_name

            cards.append(
                {
                    "cardCode": card_code,
                    "checklistGroup": group,
                    "checklistImageUrl": source_image_url,
                    "title": f"{group} {ordinal:03d}",
                    "description": "Generated from an official checklist tile; printed card code not exposed.",
                    "rarityLabel": group,
                    "cardType": card_type,
                    "cardTypeKey": card_type_key,
                    "checklistSequence": global_sequence,
                    "imageUrl": image_url,
                    "sourceUrl": source_url,
                    "sourceConfidence": "inferred",
                    "cropPath": crop_path,
                    "panel": panel_index + 1,
                    "crop": {"x": tile_x, "y": tile_y, "width": tile_width, "height": tile_height},
                }
            )

    if only_sequence is not None and not cards:
        raise ValueError(f"checklist sequence {only_sequence} was not detected")
    if only_group_key is not None and not cards:
        raise ValueError(
            f"checklist group {only_group!r} position {only_ordinal} was not detected"
        )

    for sequence, (key, count) in enumerate(selected_group_ordinals.items(), start=1):
        label = next(card["checklistGroup"] for card in cards if slug_key(card["checklistGroup"]) == key)
        groups.append(
            {
                "key": key,
                "label": label,
                "designCount": count,
                "sequence": sequence,
                "sourceConfidence": "official_image",
            }
        )

    return {
        "sourceUrl": source_url,
        "sourceImageUrl": source_image_url,
        "cards": cards,
        "groups": groups,
        "detectedPanels": len(panels),
        "detectedCards": len(cards),
        "releaseSlug": release_slug,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", help="combined checklist screenshot or source image")
    parser.add_argument("--release-slug", required=True)
    parser.add_argument("--source-url", default="")
    parser.add_argument("--source-image-url", default="")
    parser.add_argument("--output-dir", default="")
    parser.add_argument("--manifest", default="")
    parser.add_argument("--image-base-url", default="")
    parser.add_argument(
        "--only-sequence",
        type=int,
        default=None,
        help="write only one detected tile, using its original checklist sequence",
    )
    parser.add_argument(
        "--only-group",
        default=None,
        help="write one tile from a detected checklist group, for example 'Regular Card'",
    )
    parser.add_argument(
        "--only-ordinal",
        type=int,
        default=None,
        help="1-based position within --only-group, sorted left-to-right then top-to-bottom",
    )
    args = parser.parse_args()
    manifest = split_checklist_image(
        args.image,
        release_slug=args.release_slug,
        source_url=args.source_url,
        source_image_url=args.source_image_url,
        output_dir=args.output_dir or None,
        image_base_url=args.image_base_url,
        only_sequence=args.only_sequence,
        only_group=args.only_group,
        only_ordinal=args.only_ordinal,
    )
    output = Path(args.manifest) if args.manifest else Path(args.image).with_suffix(".checklist.json")
    output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"manifest": str(output), "detectedPanels": manifest["detectedPanels"], "detectedCards": manifest["detectedCards"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
