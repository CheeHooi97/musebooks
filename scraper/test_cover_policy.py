import json
import unittest
from cover_policy import bookwalker_product_cover, validate_cover_url


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
