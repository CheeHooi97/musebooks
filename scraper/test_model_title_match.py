import unittest
from model_title_match import classify_title, credits_model


class ModelTitleMatchTests(unittest.TestCase):
    # Same cases as backend/cmd/people-merge/audit_test.go.
    def test_classifies_titles_like_the_catalog_audit(self):
        cases = [
            ('MOMO 藤田もも写真集', ['もも', 'Momo'], 'other', '藤田もも'),
            ('FLASHデジタル写真集　鈴もも　永遠少女', ['もも', 'Momo'], 'other', '鈴もも'),
            ('A-collection 萌木七海（１）', ['兒玉七海', '七海', 'Nanami'], 'other', '萌木七海'),
            ('PHOTO SHOT　〜レースクイーン〜　七海ひより', ['兒玉七海', '七海'], 'other', '七海ひより'),
            ('LOVEPOP デラックス　美ノ嶋めぐり　001', ['めぐり', 'Meguri'], 'other', '美ノ嶋めぐり'),
            ('Exciting Girls 橋本梨菜デジタル写真集 Vol.1', ['橋本梨菜'], 'named', ''),
            ('志田音々ファースト写真集『nene』', ['志田音々'], 'named', ''),
            ('Nanami「Departure」', ['兒玉七海', 'Nanami'], 'weak', ''),
            ('[ハレム]もも from 63ANGEL', ['もも'], 'weak', ''),
            ('12th Birthday Party!', ['もも', 'Momo'], 'absent', ''),
            ('Momoka Collection', ['Momo'], 'absent', ''),
        ]
        for title, names, expected, proposed in cases:
            with self.subTest(title=title):
                self.assertEqual(classify_title(title, names), (expected, proposed))

    def test_only_named_titles_credit_the_model(self):
        model = dict(canonical_public_name='兒玉七海', english_name='Nanami Kodama', aliases=['小倉七海', '七海', 'Nanami'])
        self.assertTrue(credits_model('兒玉七海 写真集', model))
        self.assertTrue(credits_model('Nanami Kodama Photo Book', model))
        self.assertFalse(credits_model('A-collection 萌木七海（１）', model))
        self.assertFalse(credits_model('VIVID GIRL 七海 Chapter1', model))


if __name__ == '__main__':
    unittest.main()
