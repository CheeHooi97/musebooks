package main

import (
	"fmt"
	"strings"

	"gorm.io/gorm"
)

// reportPairs lists people still credited on exactly the same works (two or
// more), with the credit lists on those works, for manual review.
func reportPairs(db *gorm.DB) error {
	var pairs []struct {
		P1, P2       int64
		Name1, Name2 string
		Slug1, Slug2 string
		Shared       int64
	}
	err := db.Raw(`WITH pw AS (` + publishedCredits + `),
 cnt AS (SELECT person_id, count(*) AS n FROM pw GROUP BY person_id),
 shared AS (SELECT a.person_id AS p1, b.person_id AS p2, count(*) AS shared FROM pw a JOIN pw b ON a.work_id=b.work_id AND a.person_id<b.person_id GROUP BY 1,2)
 SELECT s.p1, s.p2, s.shared, x.canonical_public_name AS name1, y.canonical_public_name AS name2, x.slug AS slug1, y.slug AS slug2
 FROM shared s JOIN cnt c1 ON c1.person_id=s.p1 JOIN cnt c2 ON c2.person_id=s.p2 JOIN people x ON x.id=s.p1 JOIN people y ON y.id=s.p2
 WHERE s.shared=c1.n AND s.shared=c2.n AND s.shared>=2 ORDER BY s.shared DESC, x.canonical_public_name`).Scan(&pairs).Error
	if err != nil {
		return err
	}
	for _, p := range pairs {
		var lists []struct {
			FeaturedNames string
			Works         int64
			Sample        string
		}
		if err := db.Raw(`SELECT w.featured_names, count(*) AS works, min(w.original_title) AS sample FROM works w
 WHERE w.status='published' AND EXISTS (SELECT 1 FROM work_people wp WHERE wp.work_id=w.id AND wp.person_id=?) AND EXISTS (SELECT 1 FROM work_people wp WHERE wp.work_id=w.id AND wp.person_id=?)
 GROUP BY w.featured_names ORDER BY works DESC`, p.P1, p.P2).Scan(&lists).Error; err != nil {
			return err
		}
		fmt.Printf("%s  <->  %s   (%d shared works)\n   %s / %s\n", p.Name1, p.Name2, p.Shared, p.Slug1, p.Slug2)
		for _, l := range lists {
			fmt.Printf("   %3d × [%s]  e.g. %s\n", l.Works, strings.TrimSpace(l.FeaturedNames), l.Sample)
		}
	}
	fmt.Printf("\n%d pairs\n", len(pairs))
	return nil
}

// reportPerson lists the works credited to a person (by display name), grouped
// by credit list, with sample titles.
func reportPerson(db *gorm.DB, name string) error {
	var rows []struct {
		FeaturedNames string
		Works         int64
		Titles        string
	}
	err := db.Raw(`SELECT w.featured_names, count(*) AS works, string_agg(w.original_title, ' | ' ORDER BY w.original_title) AS titles
 FROM works w JOIN work_people wp ON wp.work_id=w.id JOIN people p ON p.id=wp.person_id
 WHERE w.status='published' AND p.canonical_public_name=? GROUP BY w.featured_names ORDER BY works DESC`, name).Scan(&rows).Error
	fmt.Printf("== %s\n", name)
	for _, r := range rows {
		titles := []rune(r.Titles)
		if len(titles) > 400 {
			titles = append(titles[:400], '…')
		}
		fmt.Printf("  %3d × [%s]\n      %s\n", r.Works, r.FeaturedNames, string(titles))
	}
	return err
}
