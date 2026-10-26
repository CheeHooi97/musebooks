package model

import "testing"

func TestStoreSeriesName(t *testing.T) {
	for _, tc := range []struct{ title, base, series string }{
		{"漫画アクションデジタル写真集　紫藤るい「Healing」　（漫画アクションデジタル写真集）", "漫画アクションデジタル写真集　紫藤るい「Healing」", "漫画アクションデジタル写真集"},
		{"ＪＯＳＨＵＡ　（幻冬舎単行本）", "ＪＯＳＨＵＡ", "幻冬舎単行本"},
		{"MoeMiデジタル写真集「Sunny Side」　（MoeMiデジタル写真集「Sunny Side」）", "MoeMiデジタル写真集「Sunny Side」", ""},
		{"A-collection 萌木七海（１）", "A-collection 萌木七海（１）", ""},
		{"【デジタル限定】三上悠亜写真集「Your DOLL」（全年齢版）", "【デジタル限定】三上悠亜写真集「Your DOLL」（全年齢版）", ""},
		{"霧島聖子 あ～ん、止められない！", "霧島聖子 あ～ん、止められない！", ""},
	} {
		base, series := StoreSeriesName(tc.title)
		if base != tc.base || series != tc.series {
			t.Errorf("StoreSeriesName(%q) = %q, %q; want %q, %q", tc.title, base, series, tc.base, tc.series)
		}
	}
}

func TestTitleWithoutSeriesOnlyDropsRecordedLabels(t *testing.T) {
	title := "紫藤るい「Iの旋律」 BUBKAデジタル写真集　（BUBKAデジタル写真集）"
	if got := TitleWithoutSeries(title, "BUBKAデジタル写真集"); got != "紫藤るい「Iの旋律」 BUBKAデジタル写真集" {
		t.Fatalf("recorded series kept in title: %q", got)
	}
	if got := TitleWithoutSeries(title); got != title {
		t.Fatalf("unrecorded label dropped: %q", got)
	}
	if got := TitleWithoutSeries("らすとしーん　（らすとしーん）"); got != "らすとしーん" {
		t.Fatalf("repeated title kept: %q", got)
	}
}

func TestResponsesShowSeriesSeparately(t *testing.T) {
	work := Work{ID: "w", OriginalTitle: "ＪＯＳＨＵＡ　（幻冬舎単行本）", Editions: []Edition{{ID: "e", EditionLabel: "ＪＯＳＨＵＡ　（幻冬舎単行本）", SeriesName: "幻冬舎単行本"}}}
	response := work.Response()
	if response.OriginalTitle != "ＪＯＳＨＵＡ" || response.Editions[0].EditionLabel != "ＪＯＳＨＵＡ" || response.Editions[0].SeriesName != "幻冬舎単行本" {
		t.Fatalf("unexpected response: %q / %q / %q", response.OriginalTitle, response.Editions[0].EditionLabel, response.Editions[0].SeriesName)
	}
}
