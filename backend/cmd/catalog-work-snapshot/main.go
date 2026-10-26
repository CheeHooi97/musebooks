// catalog-work-snapshot saves read-only evidence for one reviewed source batch.
package main

import (
	"database/sql"
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"time"

	"github.com/joho/godotenv"
	"gorm.io/gorm"
	"musebooks/config"
	"musebooks/database"
	"musebooks/model"
	"musebooks/repository"
)

func main() {
	workID := flag.String("work", "", "Exact existing work ID")
	output := flag.String("output", "", "JSON evidence path")
	flag.Parse()
	must := func(err error) {
		if err != nil {
			panic(err)
		}
	}
	if *workID == "" || *output == "" {
		panic("work and output are required")
	}
	_ = godotenv.Load()
	config.LoadConfig()
	if config.DBName != "musebooks" {
		panic("unexpected database")
	}
	db, err := database.Open(true, false)
	must(err)
	pool, err := db.DB()
	must(err)
	defer pool.Close()
	evidence := map[string]any{"capturedAt": time.Now().UTC(), "readOnly": true}
	must(db.Transaction(func(tx *gorm.DB) error {
		var work model.Work
		must(repository.NewCatalogRepository(tx).GetBook(&work, *workID).Error)
		evidence["publicBook"] = work.Response()
		evidence["work"] = work
		var credits []model.WorkPerson
		must(tx.Preload("Person").Where("work_id = ?", *workID).Order("person_id,role").Find(&credits).Error)
		evidence["credits"] = credits
		var aliases []map[string]any
		must(tx.Table("person_aliases").Where("person_id IN (SELECT person_id FROM work_people WHERE work_id = ?)", *workID).Order("alias_slug,person_id").Find(&aliases).Error)
		evidence["aliases"] = aliases
		var people []model.Person
		must(tx.Where("id IN (SELECT person_id FROM work_people WHERE work_id = ?) OR slug IN (SELECT alias_slug FROM person_aliases WHERE person_id IN (SELECT person_id FROM work_people WHERE work_id = ?))", *workID, *workID).Order("id").Find(&people).Error)
		evidence["peopleIncludingAliasRows"] = people
		var listings []model.Listing
		must(tx.Where("edition_id IN (SELECT id FROM editions WHERE work_id = ?)", *workID).Order("id").Find(&listings).Error)
		evidence["listings"] = listings
		var observations []model.ListingObservation
		must(tx.Where("listing_id IN (SELECT id FROM listings WHERE edition_id IN (SELECT id FROM editions WHERE work_id = ?))", *workID).Order("observation_key").Find(&observations).Error)
		evidence["observations"] = observations
		var media []model.CatalogMedia
		must(tx.Where("(entity_type = 'edition' AND entity_id IN (SELECT id FROM editions WHERE work_id = ?)) OR (entity_type = 'listing' AND entity_id IN (SELECT id FROM listings WHERE edition_id IN (SELECT id FROM editions WHERE work_id = ?)))", *workID, *workID).Order("id").Find(&media).Error)
		evidence["media"] = media
		return nil
	}, &sql.TxOptions{ReadOnly: true, Isolation: sql.LevelRepeatableRead}))
	data, err := json.MarshalIndent(evidence, "", "  ")
	must(err)
	file, err := os.OpenFile(*output, os.O_WRONLY|os.O_CREATE|os.O_EXCL, 0644)
	must(err)
	_, err = file.Write(append(data, '\n'))
	must(err)
	must(file.Close())
	fmt.Println("Saved read-only work snapshot:", *workID)
}
