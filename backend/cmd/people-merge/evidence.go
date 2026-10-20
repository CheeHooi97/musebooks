package main

import (
	"encoding/json"
	"fmt"
	"os"
	"strings"

	"gorm.io/gorm"
)

// reviewEvidence gathers, for every credited work the audit could not confirm
// from its title (weak or absent) on models that also carried other people's
// books, all catalog evidence beyond the title: summaries, publishers, every
// store listing title and the source links. Read-only.
type reviewItem struct {
	Model         string   `json:"model"`
	ModelNames    []string `json:"modelNames"`
	Class         string   `json:"class"`
	WorkID        string   `json:"workId"`
	Title         string   `json:"title"`
	FeaturedNames string   `json:"featuredNames"`
	Summary       string   `json:"summary,omitempty"`
	Editions      []string `json:"editions"`
	ListingTitles []string `json:"listingTitles"`
	SourceURLs    []string `json:"sourceUrls"`
}

// Models whose credits came from name-search buckets (docs/model-bucket-audit-2026-10-20.md).
var reviewModels = map[string]bool{"葵": true, "もも": true, "浅野こころ": true, "兒玉七海": true, "神木麗": true, "初美沙希": true, "めぐり": true, "寧々": true, "つぼみ": true, "金子みひろ": true, "ティア": true}

func reviewEvidence(db *gorm.DB, out string) error {
	var people []struct {
		ID                                       int64
		Name, OriginalName, EnglishName, Aliases string
	}
	if err := db.Raw(`SELECT p.id, p.canonical_public_name AS name, COALESCE(p.original_name,'') AS original_name, COALESCE(p.english_name,'') AS english_name,
 COALESCE((SELECT string_agg(pa.alias_name, ',') FROM person_aliases pa WHERE pa.person_id=p.id),'') AS aliases
 FROM people p WHERE EXISTS (SELECT 1 FROM work_people wp JOIN works w ON w.id=wp.work_id WHERE wp.person_id=p.id AND w.status='published' AND wp.role='featured')`).Scan(&people).Error; err != nil {
		return err
	}
	items := []reviewItem{}
	for _, p := range people {
		names := splitNames(strings.Join([]string{p.Name, p.OriginalName, p.EnglishName, p.Aliases}, ","))
		var works []struct{ ID, Title, FeaturedNames, Summary string }
		if err := db.Raw(`SELECT w.id, w.original_title AS title, COALESCE(w.featured_names,'') AS featured_names, COALESCE(w.summary,'') AS summary
 FROM works w JOIN work_people wp ON wp.work_id=w.id WHERE wp.person_id=? AND wp.role='featured' AND w.status='published' ORDER BY w.original_title`, p.ID).Scan(&works).Error; err != nil {
			return err
		}
		// Only models that are search buckets: some credited title names someone else.
		bucket := false
		classes := make([]string, len(works))
		for i, w := range works {
			classes[i], _ = classifyTitle(w.Title, names)
			bucket = bucket || classes[i] == "other"
		}
		if !bucket && !shortName(p.Name) && !reviewModels[p.Name] {
			continue
		}
		for i, w := range works {
			if classes[i] == "named" {
				continue
			}
			item := reviewItem{Model: p.Name, ModelNames: names, Class: classes[i], WorkID: w.ID, Title: w.Title, FeaturedNames: w.FeaturedNames, Summary: w.Summary}
			var editions []struct{ Label, Publisher, ContentSummary, MetadataSourceURL string }
			db.Raw(`SELECT edition_label AS label, COALESCE(publisher,'') AS publisher, COALESCE(content_summary,'') AS content_summary, COALESCE(metadata_source_url,'') AS metadata_source_url
 FROM editions WHERE work_id=? AND status<>'superseded'`, w.ID).Scan(&editions)
			for _, e := range editions {
				item.Editions = append(item.Editions, strings.TrimSpace(e.Label+" | "+e.Publisher+" | "+e.ContentSummary))
				if e.MetadataSourceURL != "" {
					item.SourceURLs = append(item.SourceURLs, e.MetadataSourceURL)
				}
			}
			var listings []struct{ Title, URL string }
			db.Raw(`SELECT DISTINCT l.title, COALESCE(l.url,'') AS url FROM listings l JOIN editions e ON e.id=l.edition_id WHERE e.work_id=?`, w.ID).Scan(&listings)
			for _, l := range listings {
				item.ListingTitles = append(item.ListingTitles, l.Title)
				if l.URL != "" {
					item.SourceURLs = append(item.SourceURLs, l.URL)
				}
			}
			items = append(items, item)
		}
	}
	fmt.Printf("%d works to review\n", len(items))
	data, err := json.MarshalIndent(items, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(out, data, 0o644)
}
