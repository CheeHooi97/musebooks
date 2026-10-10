package model

import "testing"

func TestWarningCoverPolicy(t *testing.T) {
	for _, raw := range []string{"https://cdn.kingstone.com.tw/images/restricted.jpg?cache=1", "https://img.musecards.my/musebooks/covers/" + KingstoneWarningHash + ".jpg", "r2://bucket/musebooks/covers/" + KingstoneWarningHash + ".jpg", "https://taiwan-image.bookwalker.com.tw/product/12/12_1_mask.jpg"} {
		if !IsWarningCover(raw) || PublicCoverURL(raw) != "" {
			t.Fatalf("warning cover accepted: %s", raw)
		}
	}
	for _, raw := range []string{"", "https://cdn.kingstone.com.tw/book/images/product-cover.jpg", "https://taiwan-image.bookwalker.com.tw/product/12/12_1.jpg", "https://example.com/18-plus-photobook.jpg"} {
		if IsWarningCover(raw) || PublicCoverURL(raw) != raw {
			t.Fatalf("genuine cover rejected: %s", raw)
		}
	}
}
