package main

import (
	"musebooks/model"
	"sort"
	"strings"
	"unicode"
)

// A segment is one model's name list as the importer wrote it: the canonical
// name first, then that model's other recorded names. Segments are taken from
// the catalog itself — credit lists that occur on their own and do not extend a
// shorter observed list. Longer lists are segments joined for collaborations,
// or a segment followed by separately credited people.
type segment struct {
	Names []string `json:"names"`
	Works int      `json:"works"`
}

func (s segment) key() string { return strings.Join(s.Names, ",") }
func (s segment) owner() string {
	return model.CatalogIdentity("model", s.Names[0])
}

func hasLatin(names []string) bool {
	for _, name := range names {
		for _, r := range name {
			if r < unicode.MaxASCII && unicode.IsLetter(r) {
				return true
			}
		}
	}
	return false
}

func normalizedKey(names []string) string {
	keys := make([]string, len(names))
	for i, name := range names {
		keys[i] = strings.ToLower(name)
	}
	return strings.Join(keys, ",")
}

// segments returns the atomic alias lists. Importer lists always pair a native
// name with a romanised one, so lists with no Latin name (e.g. Korean issue
// credits naming many different people) are never treated as aliases.
func segments(lists map[string][]string, counts map[string]int) []segment {
	observed := map[string]bool{}
	for key, names := range lists {
		if len(names) > 1 {
			observed[normalizedKey(names)] = true
		}
		_ = key
	}
	result := []segment{}
	for key, names := range lists {
		if len(names) < 2 || !hasLatin(names) {
			continue
		}
		atomic := true
		for end := 2; end < len(names); end++ {
			if observed[normalizedKey(names[:end])] {
				atomic = false
				break
			}
		}
		if atomic {
			result = append(result, segment{Names: names, Works: counts[key]})
		}
	}
	// A candidate that contains another model's main name after its own is a
	// collaboration credit: only the part before that name is this model's list.
	for changed := true; changed; {
		changed = false
		mains := map[string]bool{}
		for _, seg := range result {
			mains[strings.ToLower(seg.Names[0])] = true
		}
		next := []segment{}
		have := map[string]bool{}
		for _, seg := range result {
			cut := 0
			for i := 1; i < len(seg.Names); i++ {
				if mains[strings.ToLower(seg.Names[i])] && !strings.EqualFold(seg.Names[i], seg.Names[0]) {
					cut = i
					break
				}
			}
			if cut > 0 {
				changed = true
				seg.Names = seg.Names[:cut]
				if len(seg.Names) < 2 || !hasLatin(seg.Names) {
					continue
				}
			}
			if key := normalizedKey(seg.Names); !have[key] {
				have[key] = true
				next = append(next, seg)
			}
		}
		result = next
	}
	sort.Slice(result, func(i, j int) bool {
		if result[i].Works != result[j].Works {
			return result[i].Works > result[j].Works
		}
		return result[i].key() < result[j].key()
	})
	return result
}

// decompose splits a credit list into segments (longest match first) and the
// names left over, which stay separately credited people.
func decompose(names []string, bySegmentKey map[string]segment) (parts []segment, singles []string) {
	for i := 0; i < len(names); {
		matched := false
		for end := len(names); end > i+1; end-- {
			if seg, ok := bySegmentKey[normalizedKey(names[i:end])]; ok {
				parts = append(parts, seg)
				i = end
				matched = true
				break
			}
		}
		if !matched {
			singles = append(singles, names[i])
			i++
		}
	}
	return parts, singles
}
