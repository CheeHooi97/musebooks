package main

import (
	"encoding/json"
	"musebooks/config"
	"musebooks/database"
	"os"
)

func main() {
	config.LoadConfig()
	db, e := database.Open(true, false)
	if e != nil {
		panic(e)
	}
	queries := map[string]string{
		"summary":          `SELECT e.format, count(*) total, count(*) FILTER(WHERE NOT EXISTS(SELECT 1 FROM listings l WHERE l.edition_id=e.id AND l.price_minor>0 AND l.currency<>'')) missing_any_price FROM editions e JOIN works w ON w.id=e.work_id WHERE e.status<>'superseded' AND w.status='published' GROUP BY e.format`,
		"missing":          `SELECT e.id,e.format,e.isbn,e.metadata_source_url,w.original_title,w.featured_names, (SELECT count(*) FROM listings l WHERE l.edition_id=e.id) listing_count FROM editions e JOIN works w ON w.id=e.work_id WHERE e.status<>'superseded' AND w.status='published' AND NOT EXISTS(SELECT 1 FROM listings l WHERE l.edition_id=e.id AND l.price_minor>0 AND l.currency<>'') ORDER BY e.format,w.original_title`,
		"invalid_listings": `SELECT id,edition_id,title,url,source_id,status,price_minor,currency FROM listings WHERE price_minor<=0 OR currency=''`,
		"sources":          `SELECT s.id,s.kind,count(*) total,count(*) FILTER(WHERE l.price_minor<=0 OR l.currency='') missing FROM listings l JOIN sources s ON s.id=l.source_id GROUP BY s.id,s.kind ORDER BY total DESC`}
	out := map[string]any{}
	for k, q := range queries {
		var rows []map[string]any
		if e = db.Raw(q).Scan(&rows).Error; e != nil {
			panic(e)
		}
		out[k] = rows
	}
	enc := json.NewEncoder(os.Stdout)
	enc.SetIndent("", "  ")
	enc.Encode(out)
}
