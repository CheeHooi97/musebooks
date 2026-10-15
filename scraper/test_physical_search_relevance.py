import tempfile
import unittest
from pathlib import Path

from physical_search_relevance import (
    IRRELEVANT_PAGE_LIMIT,
    has_photobook_title_signal,
    matching_candidate_count,
    next_irrelevant_page_count,
    trailing_irrelevant_page_count,
)


class PhysicalSearchRelevanceTests(unittest.TestCase):
    def setUp(self):
        self.names = ["虹咲カリナ", "Karina Nijisaki"]
        self.count_matches = lambda candidates: matching_candidate_count(
            candidates, self.names,
            lambda request, title: any(name in title.split("写真集", 1)[0] for name in request["humanModelKeywords"]),
            lambda title: "dvd" in title.lower(),
        )

    def test_unrelated_photo_books_do_not_count_as_model_matches(self):
        cards = [
            {"title": "乃木坂46写真集 乃木撮 VOL.02"},
            {"title": "吉田由莉写真集 Feti doll"},
        ]
        self.assertEqual(self.count_matches(cards), 0)
        self.assertEqual(self.count_matches([{"title": "虹咲カリナ 写真集"}]), 1)
        self.assertEqual(self.count_matches([{"title": "虹咲カリナ DVD"}]), 0)
        self.assertEqual(has_photobook_title_signal("虹咲カリナ photobook"), True)
        self.assertEqual(has_photobook_title_signal("虹咲カリナ DVD"), False)

    def test_irrelevance_streak_resets_after_a_matching_card(self):
        streak = 0
        for _ in range(IRRELEVANT_PAGE_LIMIT - 1):
            streak = next_irrelevant_page_count(streak, 0)
        self.assertLess(streak, IRRELEVANT_PAGE_LIMIT)
        streak = next_irrelevant_page_count(streak, 1)
        self.assertEqual(streak, 0)
        for _ in range(IRRELEVANT_PAGE_LIMIT):
            streak = next_irrelevant_page_count(streak, 0)
        self.assertEqual(streak, IRRELEVANT_PAGE_LIMIT)

    def test_relevance_can_be_decided_from_the_primary_title(self):
        cards = [
            {"title": "七海ひろき 写真集", "text": "seller keywords include 兒玉七海"},
            {"title": "兒玉七海 写真集", "text": "seller keywords include 七海ひろき"},
        ]
        self.assertEqual(
            matching_candidate_count(
                cards, self.names, lambda _request, _title: True,
                lambda _title: "",
                lambda card: card["title"].startswith("兒玉七海"),
            ),
            1,
        )

    def test_resume_recovers_the_streak_from_saved_candidate_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            batches = []
            for index in range(IRRELEVANT_PAGE_LIMIT + 1):
                name = f"page-{index}.json"
                (root / name).write_text(
                    '{"candidateEvidence":[{"title":"乃木坂46写真集 乃木撮"}]}',
                    encoding="utf-8",
                )
                batches.append({"file": name})
            (root / "matching-page.json").write_text(
                '{"candidateEvidence":[{"title":"虹咲カリナ 写真集"}]}',
                encoding="utf-8",
            )
            batches.append({"file": "matching-page.json"})
            self.assertEqual(
                trailing_irrelevant_page_count(
                    {"batches": batches}, root, self.count_matches
                ),
                0,
            )
            self.assertEqual(
                trailing_irrelevant_page_count(
                    {"batches": batches[:-1]}, root, self.count_matches
                ),
                IRRELEVANT_PAGE_LIMIT + 1,
            )


if __name__ == "__main__":
    unittest.main()
