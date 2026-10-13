package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"musebooks/config"
	"musebooks/database"
	"os"
	"time"
)

func main() {
	manifest := flag.String("manifest", "../scraper/japan-models/verification-manifest.json", "Applied model-offer manifest")
	output := flag.String("output", "../scraper/japan-models/import-verification.json", "Read-only verification report")
	exclusions := flag.String("exclusions", "../scraper/japan-models/excluded-listings.json", "Reviewed out-of-scope offers whose catalog links must remain empty")
	flag.Parse()
	raw, err := os.ReadFile(*manifest)
	if err != nil {
		panic(err)
	}
	var records []struct {
		Source struct {
			ID string `json:"id"`
		} `json:"source"`
		Edition struct {
			ID     string `json:"id"`
			WorkID string `json:"workId"`
		} `json:"edition"`
		Batch struct {
			Items []struct {
				ExternalID string `json:"externalId"`
				PriceMinor int64  `json:"priceMinor"`
				Currency   string `json:"currency"`
				Format     string `json:"format"`
			} `json:"items"`
		} `json:"batch"`
		Media          []json.RawMessage `json:"media"`
		PublisherMedia []json.RawMessage `json:"publisherMedia"`
	}
	if err := json.Unmarshal(raw, &records); err != nil {
		panic(err)
	}
	var excluded []struct {
		SourceID   string `json:"sourceId"`
		ExternalID string `json:"externalId"`
	}
	exclusionData, err := os.ReadFile(*exclusions)
	if err != nil {
		panic(err)
	}
	if err := json.Unmarshal(exclusionData, &excluded); err != nil {
		panic(err)
	}
	excludedKeys := map[string]bool{}
	for _, e := range excluded {
		excludedKeys[e.SourceID+":"+e.ExternalID] = true
	}
	expected := []map[string]any{}
	for _, r := range records {
		for _, i := range r.Batch.Items {
			expected = append(expected, map[string]any{"source_id": r.Source.ID, "external_id": i.ExternalID,
				"excluded":    excludedKeys[r.Source.ID+":"+i.ExternalID],
				"price_minor": i.PriceMinor, "currency": i.Currency, "format": i.Format,
				"media_count": len(r.Media), "publisher_count": len(r.PublisherMedia),
				"edition_id": r.Edition.ID, "work_id": r.Edition.WorkID})
		}
	}
	if len(expected) == 0 {
		panic("No applied offers to verify")
	}
	payload, err := json.Marshal(expected)
	if err != nil {
		panic(err)
	}
	config.LoadConfig()
	db, err := database.Open(true, false)
	if err != nil {
		panic(err)
	}
	var result struct {
		Expected              int64 `json:"expected"`
		Present               int64 `json:"present"`
		PriceMismatches       int64 `json:"priceMismatches"`
		FormatMismatches      int64 `json:"formatMismatches"`
		MissingMedia          int64 `json:"missingMedia"`
		MissingPublisherMedia int64 `json:"missingPublisherMedia"`
		LinkedEditions        int64 `json:"linkedEditions"`
		WorkMismatches        int64 `json:"workMismatches"`
		ExclusionMismatches   int64 `json:"exclusionMismatches"`
	}
	query := `WITH expected AS (SELECT * FROM jsonb_to_recordset(?::jsonb) AS x(source_id text,external_id text,price_minor bigint,currency text,format text,media_count int,publisher_count int,edition_id text,work_id text,excluded boolean))
 SELECT count(*) AS expected,count(l.id) AS present,
 count(*) FILTER(WHERE l.id IS NOT NULL AND (l.price_minor IS DISTINCT FROM x.price_minor OR l.currency IS DISTINCT FROM x.currency)) AS price_mismatches,
 count(*) FILTER(WHERE l.id IS NOT NULL AND l.format_candidate IS DISTINCT FROM x.format) AS format_mismatches,
 count(*) FILTER(WHERE l.id IS NOT NULL AND (SELECT count(*) FROM catalog_media m WHERE m.entity_type='listing' AND m.entity_id=l.id AND m.media_type LIKE 'listing_image%')<x.media_count) AS missing_media,
 count(*) FILTER(WHERE x.publisher_count>0 AND (SELECT count(*) FROM catalog_media m WHERE m.entity_type='edition' AND m.entity_id=x.edition_id AND m.media_type LIKE 'publisher_%')<x.publisher_count) AS missing_publisher_media,
 count(*) FILTER(WHERE l.edition_id IS NOT NULL AND l.edition_id<>'') AS linked_editions,
	 count(*) FILTER(WHERE NOT x.excluded AND x.edition_id<>'' AND (l.edition_id IS DISTINCT FROM x.edition_id OR e.work_id IS DISTINCT FROM x.work_id)) AS work_mismatches,
	 count(*) FILTER(WHERE x.excluded AND (l.status IS DISTINCT FROM 'excluded' OR COALESCE(l.edition_id,'')<>'')) AS exclusion_mismatches
 FROM expected x LEFT JOIN listings l ON l.source_id=x.source_id AND l.external_id=x.external_id LEFT JOIN editions e ON e.id=l.edition_id`
	if err := db.Raw(query, string(payload)).Scan(&result).Error; err != nil {
		panic(err)
	}
	var issues []struct {
		SourceID        string `json:"sourceId"`
		ExternalID      string `json:"externalId"`
		ExpectedEdition string `json:"expectedEdition"`
		ActualEdition   string `json:"actualEdition"`
		ExpectedWork    string `json:"expectedWork"`
		ActualWork      string `json:"actualWork"`
	}
	if result.WorkMismatches > 0 {
		query := `WITH expected AS (SELECT * FROM jsonb_to_recordset(?::jsonb) AS x(source_id text,external_id text,edition_id text,work_id text,excluded boolean))
		 SELECT x.source_id,x.external_id,x.edition_id AS expected_edition,l.edition_id AS actual_edition,x.work_id AS expected_work,e.work_id AS actual_work
		 FROM expected x LEFT JOIN listings l ON l.source_id=x.source_id AND l.external_id=x.external_id LEFT JOIN editions e ON e.id=l.edition_id
		 WHERE NOT x.excluded AND x.edition_id<>'' AND (l.edition_id IS DISTINCT FROM x.edition_id OR e.work_id IS DISTINCT FROM x.work_id)`
		if err := db.Raw(query, string(payload)).Scan(&issues).Error; err != nil {
			panic(err)
		}
	}
	report, err := json.MarshalIndent(map[string]any{"checkedAt": time.Now().UTC().Format(time.RFC3339), "mode": "read_only_database", "result": result, "workIdentityIssues": issues}, "", "  ")
	if err != nil {
		panic(err)
	}
	if err := os.WriteFile(*output, report, 0644); err != nil {
		panic(err)
	}
	fmt.Printf("Verified %d/%d records; price mismatches=%d format mismatches=%d missing galleries=%d missing publisher media=%d work mismatches=%d\n", result.Present, result.Expected, result.PriceMismatches, result.FormatMismatches, result.MissingMedia, result.MissingPublisherMedia, result.WorkMismatches)
	if result.Present != result.Expected || result.PriceMismatches+result.FormatMismatches+result.MissingMedia+result.MissingPublisherMedia+result.WorkMismatches+result.ExclusionMismatches > 0 {
		os.Exit(1)
	}
}
