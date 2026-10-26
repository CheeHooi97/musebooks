package database

import (
	"embed"
	"fmt"
	"gorm.io/gorm"
	"musebooks/config"
	"strings"
	"time"
)

//go:embed migrations/*.sql
var catalogMigrations embed.FS

type SchemaMigration struct {
	Version   string `gorm:"primaryKey;size:100"`
	AppliedAt time.Time
}

const CatalogSchemaVersion = "20261023_accounts_v1"

var catalogMigrationSteps = []struct {
	version string
	file    string
}{
	{version: "20261007_musecards_structure_v1", file: "migrations/20261007_musecards_structure.sql"},
	{version: "20261019_publication_type_v1", file: "migrations/20261019_publication_type.sql"},
	{version: "20261020_person_aliases_v1", file: "migrations/20261020_person_aliases.sql"},
	{version: CatalogSchemaVersion, file: "migrations/20261023_accounts.sql"},
}

func renameLegacyAccountTables(db *gorm.DB) error {
	for _, pair := range [][2]string{{"user", "users"}, {"admin", "admins"}, {"company", "companies"}} {
		old, new := pair[0], pair[1]
		if db.Migrator().HasTable(old) {
			if db.Migrator().HasTable(new) {
				return fmt.Errorf("both legacy %s and normalized %s exist; reconcile them before migrating", old, new)
			}
			if err := db.Migrator().RenameTable(old, new); err != nil {
				return err
			}
		}
	}
	return nil
}
func MigrateCatalogStructure(db *gorm.DB) error {
	if err := db.AutoMigrate(&SchemaMigration{}); err != nil {
		return err
	}
	for _, migration := range catalogMigrationSteps {
		if err := db.Transaction(func(tx *gorm.DB) error {
			if err := tx.Exec("SELECT pg_advisory_xact_lock(hashtext(?))", migration.version).Error; err != nil {
				return err
			}
			var count int64
			if err := tx.Model(&SchemaMigration{}).Where("version = ?", migration.version).Count(&count).Error; err != nil {
				return err
			}
			if count > 0 {
				return nil
			}
			sql, err := catalogMigrations.ReadFile(migration.file)
			if err != nil {
				return err
			}
			if err := tx.Exec(string(sql)).Error; err != nil {
				return err
			}
			return tx.Create(&SchemaMigration{Version: migration.version, AppliedAt: time.Now().UTC()}).Error
		}); err != nil {
			return err
		}
	}
	return nil
}
func CheckCatalogSchema(db *gorm.DB) error {
	if !db.Migrator().HasTable(&SchemaMigration{}) {
		return fmt.Errorf("catalog schema is not prepared; run go run ./cmd/catalog-migrate -apply with the database owner")
	}
	var count int64
	if err := db.Model(&SchemaMigration{}).Where("version = ?", CatalogSchemaVersion).Count(&count).Error; err != nil {
		return fmt.Errorf("catalog schema is unreadable; check the API role grants")
	}
	if count != 1 {
		return fmt.Errorf("catalog structure migration %s is required", CatalogSchemaVersion)
	}
	return nil
}
func GrantApplicationAccess(db *gorm.DB, role string) error {
	if strings.TrimSpace(role) == "" {
		return fmt.Errorf("application role is required")
	}
	var databaseName string
	if err := db.Raw("SELECT current_database()").Scan(&databaseName).Error; err != nil {
		return err
	}
	if databaseName != config.DefaultDatabaseName {
		return fmt.Errorf("grants are restricted to the dedicated musebooks database")
	}
	quoted := "\"" + strings.ReplaceAll(role, "\"", "\"\"") + "\""
	tables := "companies, users, auth_sessions, admins, markets, people, person_aliases, product_lines, marketplaces, origins, sources, works, editions, work_people, catalog_media, listing_matches, active_listings, sold_listings, listings, listing_observations, scrape_jobs, scrape_runs"
	return db.Transaction(func(tx *gorm.DB) error {
		for _, sql := range []string{"GRANT USAGE ON SCHEMA public TO " + quoted, "GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE " + tables + " TO " + quoted, "GRANT SELECT ON TABLE schema_migrations TO " + quoted, "GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO " + quoted} {
			if err := tx.Exec(sql).Error; err != nil {
				return err
			}
		}
		return nil
	})
}
