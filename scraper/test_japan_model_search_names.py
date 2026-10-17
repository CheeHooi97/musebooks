import unittest

from japan_model_search_names import physical_model_search_names
from photobook_worker import marketplace_subject_matches, normalized_match_text


class JapanModelSearchNameTests(unittest.TestCase):
    def test_keeps_full_alternate_names_and_drops_partial_collisions(self):
        names = physical_model_search_names({
            'original_name': '兒玉七海',
            'canonical_public_name': '兒玉七海',
            'english_name': 'Nanami Kodama',
            'aliases': [
                '小倉七海', '兒玉七海', '七海', 'おぐらななみ',
                'Nanami Ogura', 'Nanami',
            ],
        })

        self.assertEqual(names, [
            '兒玉七海', 'Nanami Kodama', '小倉七海', 'おぐらななみ', 'Nanami Ogura'
        ])
        self.assertNotIn('七海', names)
        self.assertNotIn('Nanami', names)
        request = {'humanModelKeywords': names}
        self.assertFalse(marketplace_subject_matches(request, '七海ひろき 写真集'))
        self.assertFalse(marketplace_subject_matches(request, '浅井七海 1st写真集'))
        self.assertTrue(marketplace_subject_matches(request, '小倉七海 写真集'))

    def test_normalizes_fullwidth_latin_names_without_empty_string_matches(self):
        request = {'humanModelKeywords': ['ＡＩＫＡ']}

        self.assertEqual(normalized_match_text('ＡＩＫＡ'), 'aika')
        self.assertTrue(marketplace_subject_matches(request, 'ＡＩＫＡ エアフォース・ボディ 写真集'))
        self.assertFalse(marketplace_subject_matches(request, '写真集1'))
        self.assertFalse(marketplace_subject_matches(
            request, 'サイン 飯田里穂 ファースト写真集『プール』 写真集'
        ))
        self.assertFalse(marketplace_subject_matches(
            request, '小林愛香 1st写真集「愛香」 Aika Kobayashi'
        ))
        self.assertFalse(marketplace_subject_matches(
            request, '愛華みれ さよなら写真集 VIVO Mire Aika'
        ))

    def test_keywords_removed_by_normalization_never_match_every_title(self):
        self.assertFalse(marketplace_subject_matches(
            {'humanModelKeywords': ['😀']}, '任意の写真集'
        ))


if __name__ == '__main__':
    unittest.main()
