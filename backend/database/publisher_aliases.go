package database

import "gorm.io/gorm"

// RepairPublisherAliases installs normalization and repairs existing edition links atomically.
func RepairPublisherAliases(db *gorm.DB) error {
	sql, err := catalogMigrations.ReadFile("migrations/20261010_publisher_aliases.sql")
	if err != nil {
		return err
	}
	return db.Transaction(func(tx *gorm.DB) error {
		if err := tx.Exec("SELECT pg_advisory_xact_lock(hashtext('musebooks_publisher_aliases'))").Error; err != nil {
			return err
		}
		return tx.Exec(string(sql)).Error
	})
}
