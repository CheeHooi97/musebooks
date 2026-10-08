package database

import (
	"context"
	"fmt"
	"github.com/joho/godotenv"
	"musebooks/config"
	"musebooks/model"
	"musebooks/repository"
	"os"
	"strings"
	"testing"
	"time"
)

// This opt-in test creates its own database, owned by the configured role. It
// never changes the configured application's tables, grants, or records.
func TestCatalogPostgresIntegration(t *testing.T) {
	if os.Getenv("MUSEBOOKS_POSTGRES_INTEGRATION") != "1" {
		t.Skip("set MUSEBOOKS_POSTGRES_INTEGRATION=1 to create an isolated PostgreSQL test database")
	}
	_ = godotenv.Load("../.env")
	config.LoadConfig()
	originalName := config.DBName
	admin, err := Open(false, false)
	if err != nil {
		t.Fatal(err)
	}
	adminPool, _ := admin.DB()
	t.Cleanup(func() { adminPool.Close() })
	testName := fmt.Sprintf("musebooks_structure_test_%d", time.Now().UnixNano())
	if err = admin.Exec(`CREATE DATABASE "` + testName + `"`).Error; err != nil {
		t.Fatal("could not create isolated test database: ", err)
	}
	config.DBName = testName
	t.Cleanup(func() {
		config.DBName = originalName
		if strings.HasPrefix(testName, "musebooks_structure_test_") {
			if err := admin.Exec(`DROP DATABASE "` + testName + `"`).Error; err != nil {
				t.Errorf("could not remove isolated test database %s: %v", testName, err)
			}
		}
	})
	db, err := Open(false, false)
	if err != nil {
		t.Fatal(err)
	}
	pool, _ := db.DB()
	t.Cleanup(func() { pool.Close() })
	// Populate the original catalog contract before the normalization/backfill.
	must(t, db.AutoMigrate(&model.Origin{}, &model.Source{}, &model.Work{}, &model.Edition{}, &model.Listing{}, &model.ListingObservation{}, &model.ScrapeJob{}, &model.ScrapeRun{}))
	must(t, db.Exec(`CREATE TABLE "user" (id text PRIMARY KEY, name text); INSERT INTO "user"(id,name) VALUES('legacy-user','Preserved user')`).Error)
	origin := model.Origin{Code: "JP", Name: "Japan"}
	must(t, db.Create(&origin).Error)
	source := model.Source{ID: "test-market", Name: "Test marketplace", Kind: "marketplace", DefaultFormat: "physical", Region: "JP", Enabled: true}
	must(t, db.Create(&source).Error)
	digitalSource := model.Source{ID: "test-digital", Name: "Test digital store", Kind: "digital_store", DefaultFormat: "digital", Region: "JP", Enabled: true}
	must(t, db.Create(&digitalSource).Error)
	work := model.Work{ID: "preserved-work", Slug: "preserved-work", OriginalTitle: "Integration photobook", OriginCode: "JP", FeaturedNames: "Alice, Alice, Bob", Status: "published"}
	must(t, db.Create(&work).Error)
	paper := model.Edition{ID: "paper", WorkID: work.ID, Format: "physical", Publisher: "Test Press", EditionLabel: "Paperback", SeriesName: "Test Series", Status: "published"}
	must(t, db.Create(&paper).Error)
	digital := model.Edition{ID: "digital", WorkID: work.ID, Format: "digital", Publisher: "Test Press", EditionLabel: "Digital", Status: "published"}
	must(t, db.Create(&digital).Error)
	now := time.Now().UTC().Truncate(time.Second)
	offer := model.Listing{ID: "preserved-listing", SourceID: source.ID, ExternalID: "item-1", EditionID: paper.ID, URL: "https://example.test/item", Title: "Physical offer", FormatCandidate: "physical", Status: "active", PriceMinor: 2500, Currency: "JPY", PriceType: "fixed", ObservedAt: now, LastSeenAt: now}
	must(t, db.Create(&offer).Error)
	must(t, Migrate(db))
	must(t, Migrate(db))
	must(t, CheckCatalogSchema(db))
	var preservedUsers int64
	must(t, db.Table("users").Where("id = ?", "legacy-user").Count(&preservedUsers).Error)
	if preservedUsers != 1 {
		t.Fatal("legacy account was not preserved")
	}
	repo := repository.NewCatalogRepository(db)
	ctx := context.Background()
	query := model.CatalogBrowseQuery{Kind: "model", Page: 1, PageSize: 24}
	people, total, err := repo.Directory(ctx, query)
	must(t, err)
	if total != 2 || len(people) != 2 || people[0].WorkCount != 1 || people[0].EditionCount != 2 {
		t.Fatalf("invalid people directory: %+v total %d", people, total)
	}
	query.Kind = "publisher"
	publishers, total, err := repo.Directory(ctx, query)
	must(t, err)
	if total != 1 || publishers[0].EditionCount != 2 {
		t.Fatalf("invalid publisher directory: %+v", publishers)
	}
	query.Kind = "model"
	query.ID = model.CatalogIdentity("model", "Alice")
	books, total, err := repo.DirectoryBooks(ctx, query)
	must(t, err)
	if total != 1 || len(books) != 1 || books[0].ID != work.ID {
		t.Fatal("person relationship lost")
	}
	response := books[0].Response()
	if len(response.Models) != 2 || response.Editions[0].PublisherProfile == nil {
		t.Fatalf("canonical profile links missing: %+v", response)
	}
	query = model.CatalogBrowseQuery{Kind: "publisher", ID: publishers[0].ID, Page: 1, PageSize: 24, Format: "digital"}
	books, total, err = repo.DirectoryBooks(ctx, query)
	must(t, err)
	if total != 1 || len(books) != 1 || len(books[0].Editions) != 1 || books[0].Editions[0].Format != "digital" {
		t.Fatalf("publisher format filter mixed editions: %+v", books)
	}
	query.Person = "Bob"
	_, total, err = repo.DirectoryBooks(ctx, query)
	must(t, err)
	if total != 1 {
		t.Fatal("publisher model filter lost featured person")
	}
	query.Year = "1900"
	_, total, err = repo.DirectoryBooks(ctx, query)
	must(t, err)
	if total != 0 {
		t.Fatal("empty publisher filter returned unrelated books")
	}
	query = model.CatalogBrowseQuery{Kind: "publisher", ID: publishers[0].ID, Page: 1, PageSize: 1}
	profiles, total, err := repo.Directory(ctx, query)
	must(t, err)
	if total != 1 || len(profiles) != 1 || profiles[0].WorkCount != 1 {
		t.Fatal("publisher profile duplicated a work across editions")
	}
	query = model.CatalogBrowseQuery{Status: "active", Page: 1, PageSize: 24}
	active, total, err := repo.Listings(ctx, query)
	must(t, err)
	if total != 1 || active[0].ID != offer.ID || active[0].Source.ID != source.ID || len(active[0].FeaturedNames) != 3 {
		t.Fatalf("active contract mismatch: %+v", active)
	}
	must(t, db.Model(&offer).Updates(map[string]any{"status": "ended", "observed_at": now.Add(time.Minute)}).Error)
	active, total, err = repo.Listings(ctx, query)
	must(t, err)
	if total != 0 {
		t.Fatal("ended offer remained active")
	}
	query.Status = "completed"
	_, total, err = repo.Listings(ctx, query)
	must(t, err)
	if total != 0 {
		t.Fatal("ended offer was misclassified as a sale")
	}
	must(t, db.Model(&offer).Updates(map[string]any{"status": "completed", "price_minor": 2800, "observed_at": now.Add(2 * time.Minute)}).Error)
	sold, total, err := repo.Listings(ctx, query)
	must(t, err)
	if total != 1 || sold[0].PriceMinor != 2800 || sold[0].PriceCategory != "marketplace_sold" {
		t.Fatalf("sold contract mismatch: %+v", sold)
	}
	// A reactivated listing must not erase its earlier completed-sale record.
	must(t, db.Model(&offer).Updates(map[string]any{"status": "active", "price_minor": 3100, "observed_at": now.Add(3 * time.Minute)}).Error)
	sold, total, err = repo.Listings(ctx, query)
	must(t, err)
	if total != 1 || sold[0].PriceMinor != 2800 {
		t.Fatal("sale history was overwritten by a current asking price")
	}
	ebookOffer := model.Listing{ID: "ebook-offer", SourceID: digitalSource.ID, ExternalID: "ebook-1", EditionID: digital.ID, URL: "https://example.test/ebook", Title: "Digital retail", FormatCandidate: "digital", Status: "active", PriceMinor: 1200, Currency: "JPY", PriceType: "digital", ObservedAt: now, LastSeenAt: now}
	must(t, db.Create(&ebookOffer).Error)
	query.Status = "active"
	query.Format = "digital"
	rows, total, err := repo.Listings(ctx, query)
	must(t, err)
	if total != 1 || rows[0].PriceCategory != "digital_retail" {
		t.Fatal("digital retail was lost")
	}
	must(t, db.Model(&ebookOffer).Update("status", "completed").Error)
	query.Status = "completed"
	query.Format = ""
	_, total, err = repo.Listings(ctx, query)
	must(t, err)
	if total != 1 {
		t.Fatal("digital retail entered sold history")
	}
	must(t, db.Model(&offer).Update("status", "excluded").Error)
	_, total, err = repo.Listings(ctx, query)
	must(t, err)
	if total != 0 {
		t.Fatal("excluded listing remained publicly sold")
	}
	var works, editions, observations int64
	must(t, db.Model(&model.Work{}).Count(&works).Error)
	must(t, db.Model(&model.Edition{}).Count(&editions).Error)
	must(t, db.Model(&model.ListingObservation{}).Count(&observations).Error)
	if works != 1 || editions != 2 || observations != 0 {
		t.Fatal("normalization altered canonical catalog identity/history")
	}
}
func must(t *testing.T, err error) {
	t.Helper()
	if err != nil {
		t.Fatal(err)
	}
}
