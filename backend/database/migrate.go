package database

import (
	"musebooks/catalog"
	"musebooks/model"

	"gorm.io/gorm"
)

func Migrate(db *gorm.DB) error {
	models := []any{
		&model.User{},
		&model.Admin{},
		&catalog.Origin{},
		&catalog.Source{},
		&catalog.Work{},
		&catalog.Edition{},
		&catalog.Listing{},
		&catalog.ListingObservation{},
		&catalog.ScrapeJob{},
		&catalog.ScrapeRun{},
	}
	err := db.AutoMigrate(models...)
	if err != nil {
		return err
	}
	return nil
}
