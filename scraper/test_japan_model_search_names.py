import unittest

from japan_model_search_names import physical_model_search_names
from photobook_worker import marketplace_subject_matches


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


if __name__ == '__main__':
    unittest.main()
