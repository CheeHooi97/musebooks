import unittest
from unittest.mock import patch

import cv2
import numpy as np

from checklist_splitter import (
    card_type_for_tile,
    find_panels,
    find_tiles,
    right_section,
    split_checklist_image,
    trim_warm_checklist_frame,
)


class ChecklistSplitterTest(unittest.TestCase):
    def test_detects_panels_and_card_tiles(self):
        image = np.zeros((420, 820, 3), dtype=np.uint8)
        image[:, :] = (30, 30, 30)
        image[20:390, 40:280] = (149, 58, 49)
        image[20:390, 540:780] = (149, 58, 49)
        for x in (58, 82, 106):
            for y in (75, 105, 135):
                cv2.rectangle(image, (x, y), (x + 15, y + 24), (210, 120, 80), -1)
        for x in (558, 590):
            cv2.rectangle(image, (x, 110), (x + 25, 130), (80, 180, 220), -1)

        panels = find_panels(image)

        self.assertEqual(2, len(panels))
        self.assertEqual(9, len(find_tiles(image[20:390, 40:280])))
        self.assertEqual(2, len(find_tiles(image[20:390, 540:780])))

    def test_manifest_is_stable_and_writes_optional_crops(self):
        image = np.zeros((420, 820, 3), dtype=np.uint8)
        image[:, :] = (30, 30, 30)
        image[20:390, 40:280] = (149, 58, 49)
        image[20:390, 540:780] = (149, 58, 49)
        cv2.rectangle(image, (58, 75), (73, 99), (210, 120, 80), -1)
        cv2.rectangle(image, (558, 110), (583, 130), (80, 180, 220), -1)

        with patch("checklist_splitter.cv2.imread", return_value=image):
            manifest = split_checklist_image(
                "synthetic-checklist.png",
                release_slug="woohoo-girls-vol-1",
                source_url="https://gain-p.jp/user_data/check_list",
            )

            self.assertEqual(2, manifest["detectedCards"])
            self.assertEqual("REGULAR-CARD-001", manifest["cards"][0]["cardCode"])
            self.assertEqual("inferred", manifest["cards"][0]["sourceConfidence"])

    def test_detects_muted_non_blue_panels_with_background_contrast_fallback(self):
        image = np.zeros((420, 820, 3), dtype=np.uint8)
        image[:, :] = (18, 18, 18)
        image[20:390, 40:280] = (92, 88, 84)
        image[20:390, 540:780] = (92, 88, 84)

        panels = find_panels(image)

        self.assertEqual(2, len(panels))
        self.assertEqual((40, 20, 240, 370), panels[0])
        self.assertEqual((540, 20, 240, 370), panels[1])

    def test_detects_horizontal_cards_and_ignores_checklist_checkbox(self):
        image = np.zeros((240, 620, 3), dtype=np.uint8)
        image[:, :] = (149, 86, 48)
        for row_y in (20, 130):
            for column in range(4):
                left = 36 + column * 114
                cv2.rectangle(image, (left, row_y), (left + 101, row_y + 71), (235, 235, 235), -1)
                cv2.rectangle(image, (left + 5, row_y + 5), (left + 48, row_y + 66), (80, 160, 220), -1)
        cv2.rectangle(image, (38, 104), (53, 119), (255, 255, 255), -1)

        tiles = find_tiles(image)

        self.assertEqual(8, len(tiles))
        self.assertTrue(all(width > height for _, _, width, height in tiles))

    def test_splits_regular_three_by_three_blocks_and_preserves_row_order(self):
        image = np.zeros((900, 600, 3), dtype=np.uint8)
        image[:, :] = (196, 170, 220)
        for block_x in (60, 330):
            for row in range(3):
                for column in range(3):
                    left = block_x + column * 42
                    top = 120 + row * 60
                    cv2.rectangle(image, (left, top), (left + 42, top + 60), (80 + row * 20, 100 + column * 15, 180), -1)

        tiles = find_tiles(image)

        self.assertEqual(18, len(tiles))
        first_row = tiles[:6]
        self.assertEqual(6, len(first_row))
        self.assertEqual(1, len({y for _, y, _, _ in first_row}))
        self.assertEqual(sorted(x for x, _, _, _ in first_row), [x for x, _, _, _ in first_row])
        self.assertLess(first_row[2][0], first_row[3][0])

    def test_detects_compact_front_back_regular_sheet(self):
        image = np.zeros((329, 428, 3), dtype=np.uint8)
        image[:, :] = (210, 180, 195)
        for block_x in (32, 226):
            for row in range(3):
                for column in range(3):
                    left = block_x + column * 64
                    top = 42 + row * 84
                    cv2.rectangle(image, (left, top), (left + 54, top + 77), (235, 235, 235), -1)

        self.assertEqual(18, len(find_tiles(image)))

    def test_can_select_one_original_checklist_sequence(self):
        image = np.zeros((420, 820, 3), dtype=np.uint8)
        image[:, :] = (30, 30, 30)
        image[20:390, 40:280] = (149, 58, 49)
        image[20:390, 540:780] = (149, 58, 49)
        cv2.rectangle(image, (58, 75), (73, 99), (210, 120, 80), -1)
        cv2.rectangle(image, (558, 110), (583, 130), (80, 180, 220), -1)

        with patch("checklist_splitter.cv2.imread", return_value=image):
            manifest = split_checklist_image(
                "synthetic-checklist.png",
                release_slug="woohoo-girls-vol-1",
                only_sequence=2,
            )

        self.assertEqual(1, manifest["detectedCards"])
        self.assertEqual(2, manifest["cards"][0]["checklistSequence"])

    def test_can_select_one_tile_by_group_position(self):
        image = np.zeros((420, 820, 3), dtype=np.uint8)
        image[:, :] = (30, 30, 30)
        image[20:390, 40:280] = (149, 58, 49)
        image[20:390, 540:780] = (149, 58, 49)
        cv2.rectangle(image, (58, 75), (73, 99), (210, 120, 80), -1)
        cv2.rectangle(image, (558, 110), (583, 130), (80, 180, 220), -1)

        with patch("checklist_splitter.cv2.imread", return_value=image):
            manifest = split_checklist_image(
                "synthetic-checklist.png",
                release_slug="woohoo-girls-vol-1",
                only_group="Regular Card",
                only_ordinal=1,
            )

        self.assertEqual(1, manifest["detectedCards"])
        self.assertEqual("REGULAR-CARD-001", manifest["cards"][0]["cardCode"])

    def test_special_sheet_bands_assign_premium_and_later_groups(self):
        self.assertEqual("Photogenic Card", right_section(0.18, 0.1))
        self.assertEqual("Costume Card", right_section(0.18, 0.4))
        self.assertEqual("Premium Rare Card", right_section(0.50, 0.1))
        self.assertEqual("Double Rare Card", right_section(0.65, 0.1))
        self.assertEqual("Triple Rare Card", right_section(0.72, 0.1))
        self.assertEqual("Masterpiece Rare Card", right_section(0.85, 0.1))
        self.assertEqual("Privilege Card", right_section(0.95, 0.1))

    def test_special_tiles_get_database_type_keys(self):
        self.assertEqual(("Photo", "photo_card"), card_type_for_tile("Rare Card", 0.1, 0.05))
        self.assertEqual(("Photogenic", "photogenic_card"), card_type_for_tile("Photogenic Card", 0.1, 0.18))
        self.assertEqual(("Costume", "costume_card"), card_type_for_tile("Costume Card", 0.4, 0.18))
        self.assertEqual(("Autograph", "autograph"), card_type_for_tile("Super Rare Card", 0.1, 0.25))
        self.assertEqual(("Nail", "nail"), card_type_for_tile("Super Rare Card", 0.7, 0.25))
        self.assertEqual(("Kiss", "kiss_card"), card_type_for_tile("Super Rare Card", 0.1, 0.32))
        self.assertEqual(("Bikini Strap", "bikini_strap"), card_type_for_tile("Super Rare Card", 0.7, 0.32))
        self.assertEqual(("Real Cheki", "real_cheki"), card_type_for_tile("Super Rare Card", 0.1, 0.42))
        self.assertEqual(("Stockings", "stockings"), card_type_for_tile("Super Rare Card", 0.7, 0.42))
        self.assertEqual(("Shop Campaign Privilege", "shop_campaign_privilege"), card_type_for_tile("Privilege Card", 0.1, 0.95))
        self.assertEqual(("Event Privilege", "event_privilege"), card_type_for_tile("Privilege Card", 0.7, 0.95))

    def test_trims_warm_frame_without_cutting_card_image(self):
        tile = np.zeros((120, 90, 3), dtype=np.uint8)
        tile[:, :] = (64, 120, 189)
        tile[8:-8, 8:-8] = (220, 230, 240)
        tile[25:90, 25:65] = (90, 160, 220)

        trimmed = trim_warm_checklist_frame(tile)

        self.assertEqual((104, 74), trimmed.shape[:2])
        self.assertEqual([90, 160, 220], trimmed[25 - 8, 25 - 8].tolist())


if __name__ == "__main__":
    unittest.main()
