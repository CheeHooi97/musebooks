package main

import (
	"encoding/json"
	"fmt"
	"os"
	"sort"
	"strings"
	"unicode"

	"golang.org/x/text/unicode/norm"
	"gorm.io/gorm"
)

// Bucket audit: a model built from a name search carries works whose titles
// name someone else whose name merely contains the model's (藤田もも for もも,
// 萌木七海 for 七海). Each credited work is classified against the model's
// recorded names:
//
//	named  – a name of the model (3+ characters, or its main name) stands alone
//	weak   – only a short alias stands alone (e.g. "Nanami", "七海")
//	other  – the name only appears inside a longer name; that name is proposed
//	absent – no name of the model appears in the title
type auditWork struct {
	Title         string `json:"title"`
	FeaturedNames string `json:"featuredNames"`
	Class         string `json:"class"`
	Proposed      string `json:"proposedName,omitempty"`
}

type auditModel struct {
	Name   string         `json:"name"`
	Names  []string       `json:"names"`
	Counts map[string]int `json:"counts"`
	Works  []auditWork    `json:"works"`
}

func normalize(value string) string {
	return strings.ToLower(norm.NFKC.String(value))
}

func isKana(r rune) bool {
	return unicode.In(r, unicode.Hiragana, unicode.Katakana) && r != 'ー'
}

// particles that commonly follow a name in titles without extending it.
var particles = map[rune]bool{'の': true, 'と': true, 'が': true, 'は': true, 'を': true, 'に': true, 'も': true, 'や': true, 'で': true}

// surnameRune reports characters that make up a Japanese surname before a
// given name (Han, plus ノ/ヶ as in 美ノ嶋).
func surnameRune(r rune) bool {
	return unicode.Is(unicode.Han, r) || r == 'ノ' || r == 'ヶ' || r == 'ケ'
}

// shortName is a name that is only a given name or single word: Han names of
// up to two characters, kana-only names, and single-word Latin names.
func shortName(name string) bool {
	n := []rune(normalize(name))
	han, kana := 0, 0
	for _, r := range n {
		if unicode.Is(unicode.Han, r) {
			han++
		} else if isKana(r) || r == 'ー' {
			kana++
		}
	}
	if hasLatin([]string{name}) {
		return !strings.Contains(strings.TrimSpace(name), " ")
	}
	return (han > 0 && kana == 0 && len(n) <= 2) || (han == 0 && kana > 0 && len(n) <= 4)
}

// classifyTitle decides how a title relates to one model's names.
func classifyTitle(title string, names []string) (string, string) {
	original := []rune(norm.NFKC.String(title))
	t := []rune(normalize(title))
	if len(t) != len(original) {
		original = t
	}
	best, proposed := "absent", ""
	for _, name := range names {
		n := []rune(normalize(name))
		if len(n) == 0 {
			continue
		}
		short := shortName(name)
		for i := 0; i+len(n) <= len(t); i++ {
			if string(t[i:i+len(n)]) != string(n) {
				continue
			}
			before, after := rune(0), rune(0)
			if i > 0 {
				before = t[i-1]
			}
			if i+len(n) < len(t) {
				after = t[i+len(n)]
			}
			first, last := n[0], n[len(n)-1]
			ascii := func(r rune) bool { return r < unicode.MaxASCII && (unicode.IsLetter(r) || unicode.IsDigit(r)) }
			if ascii(first) && ascii(before) || ascii(last) && ascii(after) {
				continue // inside a longer Latin word
			}
			if !short {
				return "named", ""
			}
			// A surname directly before a given name: someone else (藤田もも).
			if surnameRune(before) {
				start := i
				for start > 0 && i-start < 4 && surnameRune(t[start-1]) {
					start--
				}
				if best != "other" {
					best, proposed = "other", string(original[start:i+len(n)])
				}
				continue
			}
			// A Han surname-like name continued by a hiragana given name: someone else (七海ひより).
			if unicode.Is(unicode.Han, last) && unicode.Is(unicode.Hiragana, after) && !particles[after] {
				end := i + len(n)
				for end < len(t) && end-(i+len(n)) < 4 && unicode.Is(unicode.Hiragana, t[end]) {
					end++
				}
				if end-(i+len(n)) >= 2 && best != "other" {
					best, proposed = "other", string(original[i:end])
				}
				continue
			}
			if best == "absent" {
				best = "weak"
			}
		}
	}
	return best, proposed
}

func runAudit(db *gorm.DB, out string) error {
	var people []struct {
		ID           int64
		Name         string
		OriginalName string
		EnglishName  string
		Aliases      string
	}
	if err := db.Raw(`SELECT p.id, p.canonical_public_name AS name, COALESCE(p.original_name,'') AS original_name, COALESCE(p.english_name,'') AS english_name,
 COALESCE((SELECT string_agg(pa.alias_name, ',') FROM person_aliases pa WHERE pa.person_id=p.id),'') AS aliases
 FROM people p WHERE EXISTS (SELECT 1 FROM work_people wp JOIN works w ON w.id=wp.work_id WHERE wp.person_id=p.id AND w.status='published' AND wp.role='featured')`).Scan(&people).Error; err != nil {
		return err
	}
	models := []auditModel{}
	for _, p := range people {
		names := splitNames(strings.Join([]string{p.Name, p.OriginalName, p.EnglishName, p.Aliases}, ","))
		var works []struct{ Title, FeaturedNames string }
		if err := db.Raw(`SELECT w.original_title AS title, COALESCE(w.featured_names,'') AS featured_names FROM works w JOIN work_people wp ON wp.work_id=w.id
 WHERE wp.person_id=? AND wp.role='featured' AND w.status='published' ORDER BY w.original_title`, p.ID).Scan(&works).Error; err != nil {
			return err
		}
		m := auditModel{Name: p.Name, Names: names, Counts: map[string]int{}}
		for _, w := range works {
			class, proposed := classifyTitle(w.Title, names)
			m.Counts[class]++
			m.Works = append(m.Works, auditWork{Title: w.Title, FeaturedNames: w.FeaturedNames, Class: class, Proposed: proposed})
		}
		if m.Counts["other"] > 0 || m.Counts["weak"] > 0 {
			models = append(models, m)
		}
	}
	sort.Slice(models, func(i, j int) bool {
		a, b := models[i].Counts["other"]*2+models[i].Counts["weak"], models[j].Counts["other"]*2+models[j].Counts["weak"]
		if a != b {
			return a > b
		}
		return models[i].Name < models[j].Name
	})
	for _, m := range models {
		fmt.Printf("%-12s named=%3d weak=%3d other=%3d absent=%3d\n", m.Name, m.Counts["named"], m.Counts["weak"], m.Counts["other"], m.Counts["absent"])
	}
	fmt.Printf("\n%d models with works naming someone else or only a short alias\n", len(models))
	if out == "" {
		return nil
	}
	data, err := json.MarshalIndent(models, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(out, data, 0o644)
}
