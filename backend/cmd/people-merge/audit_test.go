package main

import "testing"

func TestClassifyTitle(t *testing.T) {
	cases := []struct {
		title    string
		names    []string
		class    string
		proposed string
	}{
		{"MOMO 藤田もも写真集", []string{"もも", "Momo"}, "other", "藤田もも"},
		{"FLASHデジタル写真集　鈴もも　永遠少女", []string{"もも", "Momo"}, "other", "鈴もも"},
		{"A-collection 萌木七海（１）", []string{"兒玉七海", "七海", "Nanami"}, "other", "萌木七海"},
		{"PHOTO SHOT　〜レースクイーン〜　七海ひより", []string{"兒玉七海", "七海"}, "other", "七海ひより"},
		{"LOVEPOP デラックス　美ノ嶋めぐり　001", []string{"めぐり", "Meguri"}, "other", "美ノ嶋めぐり"},
		{"Exciting Girls 橋本梨菜デジタル写真集 Vol.1", []string{"橋本梨菜"}, "named", ""},
		{"志田音々ファースト写真集『nene』", []string{"志田音々"}, "named", ""},
		{"Nanami「Departure」", []string{"兒玉七海", "Nanami"}, "weak", ""},
		{"[ハレム]もも from 63ANGEL", []string{"もも"}, "weak", ""},
		{"12th Birthday Party!", []string{"もも", "Momo"}, "absent", ""},
		{"Momoka Collection", []string{"Momo"}, "absent", ""},
	}
	for _, c := range cases {
		class, proposed := classifyTitle(c.title, c.names)
		if class != c.class || proposed != c.proposed {
			t.Errorf("%s: got %s %q, want %s %q", c.title, class, proposed, c.class, c.proposed)
		}
	}
}
