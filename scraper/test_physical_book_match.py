import unittest
from physical_book_match import match_physical_book


class PrintAssociationTests(unittest.TestCase):
    def setUp(self):
        self.books = [dict(id='asuka', titleAlias='Asuka', isbn='9784847046476'),
                      dict(id='trajectory', titleAlias='Trajectory', isbn='9784847086731')]

    def match(self, title, **fields):
        return match_physical_book(dict(format='physical', title=title, **fields), self.books)

    def test_model_name_and_other_titles_do_not_identify_short_book_title(self):
        self.assertEqual(self.match('Asuka Kishi 写真集'), (None, None))
        self.assertEqual(self.match('岸明日香 EXCITING ASUKA 写真集')[0], None)
        self.assertEqual(self.match('岸明日香写真集「Asuka」')[0]['id'], 'asuka')

    def test_conflicting_isbn_and_bundles_do_not_receive_single_book_date(self):
        self.assertEqual(self.match('岸明日香 Trajectory', isbn='9784910528120'), (None, None))
        self.assertEqual(self.match('岸明日香 Trajectory 2冊セット'), (None, None))
        self.assertEqual(self.match('岸明日香 写真集', isbn='978-4-8470-8673-1'),
                         (self.books[1], 'reviewed_publisher_isbn_physical'))

    def test_spacing_and_case_variations_match_distinct_book_title(self):
        self.assertEqual(self.match('岸明日香 写真集 Ｔｒａｊｅｃｔｏｒｙ')[0]['id'], 'trajectory')


if __name__ == '__main__':
    unittest.main()
