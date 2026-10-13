import unittest
from kobo_cover_match import selected_cover_images


class KoboCoverMatchTests(unittest.TestCase):
    def test_selected_cover_allows_store_suffix_and_punctuation_changes(self):
        images = [
            {'url': 'https://tshop.r10s.jp/rakutenkobo-ebooks/cabinet/1/cover.jpg', 'alt': 'むっちむち写真集'},
            {'url': 'https://thumbnail.image.rakuten.co.jp/@0_mall/rakutenkobo-ebooks/cabinet/2/other.jpg', 'alt': '別のモデル別写真集'},
        ]
        self.assertEqual(selected_cover_images(images, 'むっちむち写真集（一迅社ブックスDF）'), [images[0]['url']])
        self.assertEqual(selected_cover_images([
            {'url': 'https://shop.r10s.jp/rakutenkobo-ebooks/cabinet/1/cover.jpg', 'alt': '平嶋夏海聖夜の贈り物はワ・タ・シ?'}
        ], '平嶋夏海 聖夜の贈り物はワ・タ・シ♡ （アサ芸Secret！デジタル写真集）'),
            ['https://shop.r10s.jp/rakutenkobo-ebooks/cabinet/1/cover.jpg'])

    def test_other_images_and_unrelated_recommendations_are_rejected(self):
        images = [
            {'url': 'https://example.com/rakutenkobo-ebooks/cabinet/1/cover.jpg', 'alt': 'むっちむち写真集'},
            {'url': 'https://tshop.r10s.jp/rakutenkobo-ebooks/cabinet/2/other.jpg', 'alt': '原つむぎ写真集'},
        ]
        self.assertEqual(selected_cover_images(images, 'むっちむち写真集（一迅社ブックスDF）'), [])

    def test_short_product_title_requires_an_exact_kobo_image_label(self):
        cover = 'https://tshop.r10s.jp/rakutenkobo-ebooks/cabinet/7529/2000000237529.jpg'
        images = [
            {'url': cover, 'alt': '範田紗々'},
            {'url': 'https://tshop.r10s.jp/rakutenkobo-ebooks/cabinet/1/other.jpg', 'alt': '範田紗々 写真集'},
            {'url': 'https://tshop.r10s.jp/rakutenkobo-ebooks/cabinet/3/recommended.jpg', 'alt': '範田紗々'},
            {'url': 'https://example.com/rakutenkobo-ebooks/cabinet/2/fake.jpg', 'alt': '範田紗々'},
        ]
        self.assertEqual(selected_cover_images(images, '範田紗々'), [cover])

    def test_selected_cover_allows_image_alt_with_publisher_suffix(self):
        cover = 'https://tshop.r10s.jp/rakutenkobo-ebooks/cabinet/9468/cover.jpg'
        images = [
            {'url': cover, 'alt': '波崎天結魅惑のＶライン50PhotosDX[sabranete-Book]'},
            {'url': 'https://tshop.r10s.jp/rakutenkobo-ebooks/cabinet/2/other.jpg',
             'alt': '波崎天結 知的なカラダ vol.2 FRIDAYデジタル写真集'},
        ]
        self.assertEqual(selected_cover_images(
            images, '波崎天結 魅惑のＶライン 50PhotosDX[sabra net e-Book]'), [cover])

    def test_selected_cover_allows_fullwidth_edition_suffix(self):
        cover = 'https://tshop.r10s.jp/rakutenkobo-ebooks/cabinet/8933/cover.jpg'
        alt = '[ハレム]長澤茉里奈フェチグラビア「まりちゅうにカンパイ！」【美麗版35P】'
        images = [{'url': cover, 'alt': alt}]
        self.assertEqual(selected_cover_images(images, alt + '（ハレム）'), [cover])

    def test_selected_cover_tolerates_lost_leading_secret_mark(self):
        cover = 'https://shop.r10s.jp/rakutenkobo-ebooks/cabinet/3497/2000018243497.jpg'
        title = '㊙蔵出し　智美の絶対温度 金子智美PetitBEST　（必撮！まるごと☆）'
        images = [{'url': cover, 'alt': '?蔵出し智美の絶対温度金子智美PetitBEST'}]
        self.assertEqual(selected_cover_images(images, title), [cover])


if __name__ == '__main__':
    unittest.main()
