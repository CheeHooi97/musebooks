// japan-audit verifies Japan marketplace price observations and image provenance.
package main

import (
	"encoding/json"
	"fmt"
	"musebooks/config"
	"musebooks/database"
	"os"
)

func main() {
	config.LoadConfig()
	db, err := database.Open(true, false)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	var rows []struct {
		Source           string `json:"source"`
		Listings         int64  `json:"listings"`
		Active           int64  `json:"active"`
		Completed        int64  `json:"completed"`
		Observations     int64  `json:"observations"`
		AttributedImages int64  `json:"attributedImages"`
		Unlinked         int64  `json:"unlinked"`
	}
	err = db.Raw(`SELECT s.id AS source, count(*) AS listings,
 count(*) FILTER (WHERE l.status='active') AS active,
 count(*) FILTER (WHERE l.status='completed') AS completed,
 sum((SELECT count(*) FROM listing_observations o WHERE o.listing_id=l.id)) AS observations,
 count(*) FILTER (WHERE EXISTS (SELECT 1 FROM catalog_media m WHERE m.entity_type='listing'
 AND m.entity_id=l.id AND m.media_type='listing_image' AND m.storage_url=l.image_url
 AND m.source_url=l.url AND m.original_url<>'')) AS attributed_images,
 count(*) FILTER (WHERE l.edition_id IS NULL OR l.edition_id='') AS unlinked
 FROM listings l JOIN sources s ON s.id=l.source_id WHERE upper(s.region)='JP'
 AND l.status<>'excluded' GROUP BY s.id ORDER BY s.id`).Scan(&rows).Error
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	out, _ := json.MarshalIndent(rows, "", "  ")
	fmt.Println(string(out))
}
