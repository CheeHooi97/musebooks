// cover-repair applies reviewed cover-only corrections with optimistic guards.
package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"gorm.io/gorm"
	"log"
	"musebooks/config"
	"musebooks/database"
	"musebooks/model"
	"net/url"
	"os"
	"strings"
)

type repair struct {
	EditionID   string `json:"editionId"`
	WorkID      string `json:"workId"`
	OldURL      string `json:"oldUrl"`
	URL         string `json:"url"`
	OriginalURL string `json:"originalUrl"`
	Key         string `json:"key"`
}

func main() {
	manifest := flag.String("manifest", "", "reviewed replacement manifest")
	apply := flag.Bool("apply", false, "apply cover-only corrections in one transaction")
	flag.Parse()
	data, err := os.ReadFile(*manifest)
	if err != nil {
		log.Fatal("could not read replacement manifest")
	}
	var repairs []repair
	if err = json.Unmarshal(data, &repairs); err != nil || len(repairs) == 0 {
		log.Fatal("invalid replacement manifest")
	}
	seen := map[string]bool{}
	for _, r := range repairs {
		if r.EditionID == "" || r.WorkID == "" || seen[r.EditionID] || !model.IsWarningCover(r.OldURL) || model.IsWarningCover(r.URL) || model.IsWarningCover(r.OriginalURL) || r.Key == "" {
			log.Fatal("invalid cover replacement identity")
		}
		for _, raw := range []string{r.URL, r.OriginalURL} {
			u, e := url.Parse(raw)
			if e != nil || u.Scheme != "https" || u.Hostname() == "" || u.User != nil {
				log.Fatal("replacement must use public HTTPS cover URLs")
			}
		}
		if !strings.HasPrefix(r.Key, "musebooks/covers/") || !strings.HasSuffix(r.URL, "/"+r.Key) {
			log.Fatal("replacement storage key mismatch")
		}
		seen[r.EditionID] = true
	}
	config.LoadConfig()
	if config.DBName != "musebooks" {
		log.Fatal("repair is restricted to musebooks")
	}
	db, err := database.Open(!*apply, false)
	if err != nil {
		log.Fatal("database unavailable")
	}
	err = db.Transaction(func(tx *gorm.DB) error {
		for _, r := range repairs {
			var count int64
			if err := tx.Table("editions").Where("id=? AND work_id=? AND cover_url IN (?,?)", r.EditionID, r.WorkID, r.OldURL, r.URL).Count(&count).Error; err != nil {
				return err
			}
			if count != 1 {
				return fmt.Errorf("edition %s changed since review", r.EditionID)
			}
			if !*apply {
				continue
			}
			updated := tx.Table("editions").Where("id=? AND work_id=? AND cover_url IN (?,?)", r.EditionID, r.WorkID, r.OldURL, r.URL).Updates(map[string]any{"cover_url": r.URL, "original_cover_url": r.OriginalURL, "cover_object_key": r.Key})
			if updated.Error != nil {
				return updated.Error
			}
			if updated.RowsAffected != 1 {
				return fmt.Errorf("edition changed during repair")
			}
			if err := tx.Table("works").Where("id=? AND cover_url=?", r.WorkID, r.OldURL).Update("cover_url", r.URL).Error; err != nil {
				return err
			}
			if err := tx.Table("listings").Where("edition_id=? AND image_url=?", r.EditionID, r.OldURL).Update("image_url", r.URL).Error; err != nil {
				return err
			}
			if err := tx.Table("catalog_media").Where("storage_url=? AND ((entity_type='edition' AND entity_id=?) OR (entity_type='work' AND entity_id=?))", r.OldURL, r.EditionID, r.WorkID).Updates(map[string]any{"storage_url": r.URL, "original_url": r.OriginalURL}).Error; err != nil {
				return err
			}
		}
		return nil
	})
	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf("Validated %d cover replacements; applied=%t\n", len(repairs), *apply)
}
