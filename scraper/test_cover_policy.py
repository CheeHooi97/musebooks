import json
import unittest
from unittest.mock import patch
from cover_policy import bookwalker_product_cover, validate_cover_url, select_cover_url, validate_cover_bytes


class CoverPolicyTests(unittest.TestCase):
    def test_selected_product_image(self):
        image = 'https://taiwan-image.bookwalker.com.tw/product/236738/236738_1.jpg'
        data = json.dumps({'props': {'productData': {'product_image': image}}})
        self.assertEqual(bookwalker_product_cover(data, 'https://www.bookwalker.com.tw/product/236738'), image)
        self.assertEqual(bookwalker_product_cover(data, 'https://www.bookwalker.com.tw/product/236737'), '')

    def test_warning_image_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_cover_url('https://taiwan-image.bookwalker.com.tw/product/236738/236738_1_mask.jpg')
        with self.assertRaises(ValueError):
            validate_cover_url('https://cdn.kingstone.com.tw/images/restricted.jpg')

    def test_missing_or_invalid_product_metadata(self):
        for data in ('', '{}', 'null', '{"props":null}'):
            self.assertEqual(bookwalker_product_cover(data, 'https://www.bookwalker.com.tw/product/236738'), '')

    def test_mirrored_warning_and_selection_fallback(self):
        mirrored = 'https://img.musecards.my/musebooks/covers/3c1ce976516c44566b414484ce00a85bd0da127555d7d9ff3e115c34816583c5.jpg'
        with self.assertRaises(ValueError):
            validate_cover_url(mirrored)
        actual = 'https://example.com/18-plus-photobook-cover.jpg'
        self.assertEqual(select_cover_url(mirrored, actual), actual)
        self.assertEqual(select_cover_url('https://cdn.kingstone.com.tw/images/restricted.jpg', mirrored), '')

    def test_warning_content_is_rejected_under_a_different_url(self):
        with patch('cover_policy.hashlib.sha256') as digest:
            digest.return_value.hexdigest.return_value = '3c1ce976516c44566b414484ce00a85bd0da127555d7d9ff3e115c34816583c5'
            with self.assertRaises(ValueError):
                validate_cover_bytes(b'warning bytes served under another URL')
