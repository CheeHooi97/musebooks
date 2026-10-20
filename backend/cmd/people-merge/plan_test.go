package main

import (
	"reflect"
	"strings"
	"testing"
)

func catalogLists(rows map[string]int) (map[string][]string, map[string]int) {
	lists := map[string][]string{}
	counts := map[string]int{}
	for value, count := range rows {
		names := splitNames(value)
		key := strings.Join(names, ",")
		lists[key] = names
		counts[key] = count
	}
	return lists, counts
}

func segmentKeys(segs []segment) []string {
	keys := []string{}
	for _, seg := range segs {
		keys = append(keys, seg.key())
	}
	return keys
}

func TestSegmentsKeepOnlyOneModelsNames(t *testing.T) {
	lists, counts := catalogLists(map[string]int{
		"岸明日香,Asuka Kishi":                  252,
		"未梨一花,Miri Ichika":                  46,
		"藤乃あおい,Aoi Fujino":                  50,
		"未梨一花,Miri Ichika,藤乃あおい,Aoi Fujino": 3, // collaboration
		"葉月あや,Aya Hazuki":                   78,
		"葉月あや,Aya Hazuki,橋本梨菜":              3, // co-credited separate model
		"高梨瑞樹,浅野こころ,Kokoro Asano,歌野こころ":     2, // separate model listed first
		"浅野こころ,Kokoro Asano,歌野こころ":          107,
		"益田アンナ,霧島聖子,名取くるみ,高槻実穂":             2, // different people, no romanised names
		"이미진,임민경,조남숙":                       1,
	})
	got := segmentKeys(segments(lists, counts))
	want := []string{"岸明日香,Asuka Kishi", "浅野こころ,Kokoro Asano,歌野こころ", "葉月あや,Aya Hazuki", "藤乃あおい,Aoi Fujino", "未梨一花,Miri Ichika"}
	if !reflect.DeepEqual(got, want) {
		t.Fatalf("segments = %v, want %v", got, want)
	}
}

func TestDecomposeLeavesSeparatePeopleAlone(t *testing.T) {
	lists, counts := catalogLists(map[string]int{"葉月あや,Aya Hazuki": 78, "浅野こころ,Kokoro Asano": 10})
	bySegmentKey := map[string]segment{}
	for _, seg := range segments(lists, counts) {
		bySegmentKey[normalizedKey(seg.Names)] = seg
	}
	parts, singles := decompose(splitNames("葉月あや,Aya Hazuki,橋本梨菜,浅野こころ,Kokoro Asano"), bySegmentKey)
	if len(parts) != 2 || !reflect.DeepEqual(singles, []string{"橋本梨菜"}) {
		t.Fatalf("parts=%v singles=%v", segmentKeys(parts), singles)
	}
}
