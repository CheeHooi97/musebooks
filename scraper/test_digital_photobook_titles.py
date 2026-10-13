import unittest
from digital_photobook_titles import digital_title_exclusion, pending_title_reviews, reopen_title_reviews


class DigitalPhotobookTitleTests(unittest.TestCase):
    def test_standalone_magazine_branded_photobooks_are_accepted(self):
        for title in ('EX大衆デジタル写真集 ：87 南みゆか「二十歳の夜」',
                      '高橋凛 週刊現代デジタル写真集',
                      '漫画アクションデジタル写真集 モデルの休日'):
            self.assertEqual(digital_title_exclusion(title), '')

    def test_whole_magazines_and_attached_photo_supplements_stay_excluded(self):
        for title in ('週刊現代2026年10月号', 'EX大衆デジタル写真集付き雑誌',
                      '特典デジタル写真集付き 漫画アクション'):
            self.assertTrue(digital_title_exclusion(title))

    def test_brand_exception_does_not_hide_other_exclusions(self):
        for title in ('EX大衆デジタル写真集 Moecco', '週刊現代デジタル写真集 女子高生',
                      'EX大衆デジタル写真集 イラスト', '週刊現代デジタル写真集 AI生成'):
            self.assertTrue(digital_title_exclusion(title))

    def test_reopen_only_obsolete_magazine_rejections(self):
        state = dict(items={}, rejected={'photo': 'magazine_only', 'magazine': 'magazine_only', 'junior': 'junior_gravure'},
            candidates={'photo': 'EX大衆デジタル写真集 モデルの休日', 'magazine': '週刊現代2026年10月号',
                        'junior': 'Moecco デジタル写真集'})
        self.assertEqual(pending_title_reviews(state), ['photo'])
        reopen_title_reviews(state)
        self.assertNotIn('photo', state['rejected'])
        self.assertEqual(state['previouslyRejected']['photo'], 'magazine_only')
        self.assertIn('junior', state['rejected'])


if __name__ == '__main__':
    unittest.main()
