import unittest
from photobook_worker import has_explicit_empty_results, ensure_rendered_page, SourceBlockedError


class EmptyResultTests(unittest.TestCase):
    def test_observed_yahoo_empty_result_is_recognized(self):
        body = '「aika-yamagishi」の商品一覧 すべて 0件 条件に一致する商品は見つかりませんでした。 同じ条件であいまい検索'
        self.assertTrue(has_explicit_empty_results(body))

    def test_loading_shell_and_generic_missing_page_are_not_empty_searches(self):
        for body in ('Yahoo!オークション 検索', 'Loading products...',
                     '指定されたページは見つかりませんでした。', 'カートに商品はありません。'):
            self.assertFalse(has_explicit_empty_results(body))

    def test_access_gate_is_rejected_before_empty_result_classification(self):
        body = 'Verify you are human captcha. No results'
        with self.assertRaises(SourceBlockedError):
            ensure_rendered_page(body, 'yahoo-auctions-jp')

    def test_yahoo_temporary_access_restriction_is_not_a_no_results_page(self):
        body = 'お客様から弊社システムへ大量のアクセスが確認できたため、一時的に利用を制限しています。'
        with self.assertRaises(SourceBlockedError) as caught:
            ensure_rendered_page(body, 'yahoo-furima-jp')
        self.assertIn('大量のアクセスが確認', caught.exception.evidence['body'])


if __name__ == '__main__':
    unittest.main()
