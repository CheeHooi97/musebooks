import unittest

from listing_images import listing_image_urls


class ListingImageTests(unittest.TestCase):
    def test_cover_and_detail_gallery_are_deduplicated_with_cover_first(self):
        item = {'imageUrl': 'https://img.example/cover.jpg',
            'imageUrls': ['https://img.example/cover.jpg', 'https://img.example/back.jpg']}
        detail = {'metadata': {'image': 'https://img.example/cover.jpg'},
            'structured': {'image': ['https://img.example/cover.jpg', 'https://img.example/page-1.jpg']}}
        self.assertEqual(listing_image_urls(item, detail), [
            'https://img.example/cover.jpg', 'https://img.example/back.jpg', 'https://img.example/page-1.jpg'])

    def test_schema_image_objects_and_nonsecure_urls(self):
        item = {'imageUrl': 'http://img.example/cover.jpg'}
        detail = {'structured': {'image': [
            {'url': 'https://img.example/cover.jpg'},
            {'contentUrl': 'https://img.example/page.jpg'},
            'http://img.example/page-2.jpg']}}
        self.assertEqual(listing_image_urls(item, detail), [
            'https://img.example/cover.jpg', 'https://img.example/page.jpg'])

    def test_yahoo_original_photo_replaces_thumbnail_proxy(self):
        item = {'imageUrl': 'https://auc-pctr.c.yimg.jp/i/auctions.c.yimg.jp/images/cover.jpg?size=small'}
        detail = {'structured': {'image': [
            'https://auctions.c.yimg.jp/images/cover.jpg',
            'https://auctions.c.yimg.jp/images/page-1.jpg']}}
        self.assertEqual(listing_image_urls(item, detail), [
            'https://auctions.c.yimg.jp/images/cover.jpg',
            'https://auctions.c.yimg.jp/images/page-1.jpg'])


if __name__ == '__main__':
    unittest.main()
