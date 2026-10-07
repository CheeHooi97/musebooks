package database

import (
	"musebooks/model"

	"gorm.io/gorm"
)

func Migrate(db *gorm.DB) error {
	return db.Transaction(func(db *gorm.DB) error {
		if err := db.Exec("SELECT pg_advisory_xact_lock(hashtext(?))", CatalogSchemaVersion).Error; err != nil {
			return err
		}
		if err := renameLegacyAccountTables(db); err != nil {
			return err
		}
		models := []any{
			&model.Company{},
			&model.Market{},
			&model.Person{},
			&model.ProductLine{},
			&model.Marketplace{},
			&model.User{},
			&model.Admin{},
			&model.Origin{},
			&model.Source{},
			&model.Work{},
			&model.Edition{},
			&model.Listing{},
			&model.ListingObservation{},
			&model.ScrapeJob{},
			&model.ScrapeRun{},
			&model.WorkPerson{},
			&model.CatalogMedia{},
			&model.ListingMatch{},
			&model.ActiveListing{},
			&model.SoldListing{},
		}
		err := db.AutoMigrate(models...)
		if err != nil {
			return err
		}
		return MigrateCatalogStructure(db)
	})
}
