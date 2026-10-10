// catalog-import inspects a database or atomically imports an explicit reviewed manifest.
package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"github.com/joho/godotenv"
	"github.com/labstack/echo/v4"
	"gorm.io/gorm"
	"gorm.io/gorm/clause"
	"musebooks/config"
	"musebooks/database"
	"musebooks/handler"
	"musebooks/model"
	"musebooks/repository"
	"musebooks/service"
	"net/http/httptest"
	"net/url"
	"os"
	"strings"
)

type ListingMediaInput struct {
	ExternalID  string `json:"externalId"`
	MediaType   string `json:"mediaType"`
	OriginalURL string `json:"originalUrl"`
	StorageURL  string `json:"storageUrl"`
	SourceURL   string `json:"sourceUrl"`
	IsPrimary   bool   `json:"isPrimary"`
}

type Record struct {
	SupersedesEditionID string                 `json:"supersedesEditionId,omitempty"`
	Origin              *model.Origin          `json:"origin,omitempty"`
	Work                model.Work             `json:"work"`
	Edition             model.Edition          `json:"edition"`
	Source              model.Source           `json:"source"`
	Batch               model.ObservationBatch `json:"batch"`
	Media               []ListingMediaInput    `json:"media,omitempty"`
}

func validHTTPSURL(value string) bool {
	parsed, err := url.Parse(strings.TrimSpace(value))
	return err == nil && parsed.Scheme == "https" && parsed.Host != "" && parsed.User == nil
}

func validCatalogOrigin(code string) bool {
	switch strings.ToUpper(strings.TrimSpace(code)) {
	case "JP", "TW", "CN", "MY":
		return true
	default:
		return false
	}
}

func validExclusionReason(reason string) bool {
	switch reason {
	case "calendar_only", "illustrated_book", "disc_only", "magazine_only", "magazine_or_supplement", "junior_gravure", "artist_monograph", "synthetic_subject", "download_resale":
		return true
	default:
		return false
	}
}

func validateMediaInput(record Record) error {
	if len(record.Media) == 0 {
		return nil
	}
	items := make(map[string]model.ObservationInput, len(record.Batch.Items))
	for _, item := range record.Batch.Items {
		items[item.ExternalID] = item
	}
	for _, media := range record.Media {
		item, ok := items[media.ExternalID]
		if !ok || strings.TrimSpace(media.ExternalID) == "" || media.MediaType != "listing_image" ||
			strings.TrimSpace(media.OriginalURL) == "" || strings.TrimSpace(media.StorageURL) == "" ||
			!validHTTPSURL(media.OriginalURL) || !validHTTPSURL(media.StorageURL) ||
			media.StorageURL != item.ImageURL || media.SourceURL != item.URL {
			return fmt.Errorf("listing image provenance does not match an imported item")
		}
	}
	return nil
}

func connect(name string) (*gorm.DB, error) {
	config.LoadConfig()
	config.DBName = name
	return database.Open(false, false)
}
func fail(err error) { fmt.Fprintln(os.Stderr, err); os.Exit(1) }
func main() {
	verify := flag.Bool("verify", false, "read back public catalog responses")
	exclude := flag.String("exclude-listings", "", "verified out-of-scope source/external IDs to mark excluded")
	manifest := flag.String("manifest", "", "reviewed JSON manifest")
	apply := flag.Bool("apply", false, "write manifest transaction")
	create := flag.Bool("create-db", false, "explicitly create configured musebooks database")
	flag.Parse()
	_ = godotenv.Load()
	name := os.Getenv("POSTGRES_DATABASE")
	if *create {
		if name != "musebooks" {
			fail(fmt.Errorf("create-db is restricted to musebooks"))
		}
		admin, e := connect("postgres")
		if e != nil {
			fail(fmt.Errorf("cannot connect to maintenance database"))
		}
		var count int64
		admin.Raw("SELECT COUNT(*) FROM pg_database WHERE datname = ?", name).Scan(&count)
		if count == 0 {
			if e = admin.Exec("CREATE DATABASE musebooks").Error; e != nil {
				fail(e)
			}
			fmt.Println("Created musebooks database")
		}
	}
	db, e := connect(name)
	if e != nil {
		fail(fmt.Errorf("cannot connect to database %s; check name and server access", name))
	}

	if *exclude != "" {
		data, err := os.ReadFile(*exclude)
		if err != nil {
			fail(err)
		}
		var entries []struct {
			SourceID   string `json:"sourceId"`
			ExternalID string `json:"externalId"`
			Reason     string `json:"reason"`
		}
		if err = json.Unmarshal(data, &entries); err != nil {
			fail(err)
		}
		if err = db.Transaction(func(tx *gorm.DB) error {
			for _, entry := range entries {
				if entry.SourceID == "" || entry.ExternalID == "" || !validExclusionReason(entry.Reason) {
					return fmt.Errorf("invalid exclusion identity or reason")
				}
				if err := tx.Model(&model.Listing{}).Where("source_id = ? AND external_id = ?", entry.SourceID, entry.ExternalID).Updates(map[string]any{"status": "excluded", "edition_id": nil}).Error; err != nil {
					return err
				}
			}
			return nil
		}); err != nil {
			fail(err)
		}
		fmt.Println("Marked out-of-scope listings excluded; price observations preserved:", len(entries))
	}
	if *verify {
		for _, format := range []string{"physical", "digital"} {
			seen := map[string]bool{}
			for page := 1; ; page++ {
				req := httptest.NewRequest("GET", fmt.Sprintf("/v1/books?format=%s&pageSize=50&page=%d", format, page), nil)
				rec := httptest.NewRecorder()
				ctx := echo.New().NewContext(req, rec)
				if err := handler.NewCatalogHandler(service.NewCatalogService(repository.NewCatalogRepository(db))).ListBooks(ctx); err != nil {
					fail(err)
				}
				var response model.ListBooksResponse
				if err := json.Unmarshal(rec.Body.Bytes(), &response); err != nil {
					fail(err)
				}
				if page == 1 {
					fmt.Println("Verified public catalog", format, "works:", response.Total)
				}
				for _, work := range response.Items {
					if seen[work.ID] {
						fail(fmt.Errorf("repeated public catalog page"))
					}
					seen[work.ID] = true
					for _, edition := range work.Editions {
						if edition.Format == "digital" && len(edition.SoldListings) > 0 {
							fail(fmt.Errorf("digital sold leak"))
						}
						for _, listing := range edition.Listings {
							if listing.Format != edition.Format {
								fail(fmt.Errorf("cross-format listing leak"))
							}
						}
					}
				}
				if len(seen) >= int(response.Total) {
					break
				}
				if len(response.Items) == 0 {
					fail(fmt.Errorf("incomplete public catalog pagination"))
				}
			}
		}
	}

	if *verify {
		type modelCounts struct {
			FeaturedNames string
			Works         int64
			Physical      int64
			Digital       int64
		}
		var stats []modelCounts
		if err := db.Raw("SELECT w.featured_names, COUNT(DISTINCT w.id) AS works, COUNT(DISTINCT e.id) FILTER (WHERE e.format='physical') AS physical, COUNT(DISTINCT e.id) FILTER (WHERE e.format='digital') AS digital FROM works w JOIN editions e ON e.work_id=w.id AND e.status <> 'superseded' GROUP BY w.featured_names ORDER BY w.featured_names").Scan(&stats).Error; err != nil {
			fail(err)
		}
		for _, row := range stats {
			fmt.Printf("Model %s: works=%d physical=%d digital=%d\n", row.FeaturedNames, row.Works, row.Physical, row.Digital)
		}
		var unlinked, pending int64
		db.Model(&model.Listing{}).Where("edition_id IS NULL AND status <> 'excluded'").Count(&unlinked)
		db.Model(&model.Edition{}).Where("COALESCE(cover_url,'') = '' AND status <> 'superseded'").Count(&pending)
		fmt.Println("Unlinked verified listings:", unlinked, "; editions with pending covers:", pending)
	}
	if *manifest == "" {
		fmt.Println("Database:", name)
		for _, t := range []string{"works", "editions", "listings", "sources", "listing_observations", "work", "edition"} {
			if db.Migrator().HasTable(t) {
				var n int64
				db.Table(t).Count(&n)
				fmt.Println(t, n)
			} else {
				fmt.Println(t, "missing")
			}
		}
		return
	}
	data, e := os.ReadFile(*manifest)
	if e != nil {
		fail(e)
	}
	var records []Record
	if e = json.Unmarshal(data, &records); e != nil {
		fail(e)
	}
	listingMediaCount := 0
	for i, r := range records {
		if r.Origin != nil && (!validCatalogOrigin(r.Origin.Code) || strings.TrimSpace(r.Origin.Name) == "") {
			fail(fmt.Errorf("record %d has an invalid origin", i))
		}
		if err := validateMediaInput(r); err != nil {
			fail(fmt.Errorf("record %d: %w", i, err))
		}
		if r.Work.ID == "" && r.Edition.ID == "" && r.Source.ID != "" && r.Batch.SourceID == r.Source.ID && len(r.Batch.Items) > 0 {
			for _, item := range r.Batch.Items {
				if item.EditionID != "" {
					fail(fmt.Errorf("unlinked observation has an edition link"))
				}
			}
			continue
		}

		if r.Work.ID == "" || r.Work.OriginalTitle == "" || r.Work.FeaturedNames == "" || !validCatalogOrigin(r.Work.OriginCode) || r.Edition.ID == "" || r.Edition.WorkID != r.Work.ID || r.Edition.MetadataSourceURL == "" {
			fail(fmt.Errorf("record %d lacks verified catalog identity", i))
		}
		if r.Edition.Format != "physical" && r.Edition.Format != "digital" {
			fail(fmt.Errorf("record %d invalid format", i))
		}
		images := []string{r.Work.CoverURL, r.Edition.CoverURL, r.Edition.CoverObjectKey}
		if r.Edition.CoverURL != "" {
			images = append(images, r.Edition.OriginalCoverURL)
		}
		for _, image := range images {
			if model.IsWarningCover(image) {
				fail(fmt.Errorf("record %d contains a store warning image instead of a cover", i))
			}
		}
		if len(r.Batch.Items) > 0 && (r.Source.ID == "" || r.Batch.SourceID != r.Source.ID) {
			fail(fmt.Errorf("record %d source mismatch", i))
		}
		for _, item := range r.Batch.Items {
			if item.EditionID != r.Edition.ID || item.Format != r.Edition.Format {
				fail(fmt.Errorf("record %d mismatched listing", i))
			}
		}
	}
	fmt.Printf("Validated %d import records\n", len(records))
	if !*apply {
		return
	}
	if db.Migrator().HasTable("work") && !db.Migrator().HasTable("works") {
		fail(fmt.Errorf("legacy singular catalog tables need an explicit migration before import"))
	}
	if e = database.CheckCatalogSchema(db); e != nil {
		fail(e)
	}
	e = db.Transaction(func(tx *gorm.DB) error {
		if err := tx.Clauses(clause.OnConflict{DoNothing: true}).Create(&model.Origin{Code: "TW", Name: "Taiwan", NativeName: "台灣"}).Error; err != nil {
			return err
		}
		for _, r := range records {
			if r.Origin != nil {
				if err := tx.Clauses(clause.OnConflict{DoNothing: true}).Create(r.Origin).Error; err != nil {
					return err
				}
			}
			if r.Work.ID != "" {
				r.Work.Status = "published"
				r.Edition.Status = "published"
				var existingEdition model.Edition
				found := tx.First(&existingEdition, "id = ?", r.Edition.ID)
				if found.Error == nil && existingEdition.WorkID != r.Edition.WorkID {
					return fmt.Errorf("edition identity conflicts with existing work: %s", r.Edition.ID)
				}
				if found.Error != nil && found.Error != gorm.ErrRecordNotFound {
					return found.Error
				}
				workUpdates := []string{"original_title", "featured_names", "summary", "photographer", "updated_at"}
				if r.Work.CoverURL != "" {
					workUpdates = append(workUpdates, "cover_url")
				}
				editionUpdates := []string{"language", "publisher", "isbn", "edition_variant", "content_summary", "metadata_source_url", "series_name", "page_count", "dimensions", "release_date", "release_precision", "edition_label", "updated_at"}
				if r.Edition.CoverURL != "" || existingEdition.CoverURL == "" {
					editionUpdates = append(editionUpdates, "original_cover_url")
				}
				if r.Edition.CoverURL != "" {
					editionUpdates = append(editionUpdates, "cover_url", "cover_object_key")
				}

				if err := tx.Omit("Origin", "Editions").Clauses(clause.OnConflict{Columns: []clause.Column{{Name: "id"}}, DoUpdates: clause.AssignmentColumns(workUpdates)}).Create(&r.Work).Error; err != nil {
					return err
				}
				if err := tx.Omit("Listings").Clauses(clause.OnConflict{Columns: []clause.Column{{Name: "id"}}, DoUpdates: clause.AssignmentColumns(editionUpdates)}).Create(&r.Edition).Error; err != nil {
					return err
				}

				if r.SupersedesEditionID != "" && r.SupersedesEditionID != r.Edition.ID {
					var old model.Edition
					result := tx.First(&old, "id = ?", r.SupersedesEditionID)
					if result.Error != nil && result.Error != gorm.ErrRecordNotFound {
						return result.Error
					}
					if result.Error == nil {
						if old.WorkID != r.Edition.WorkID || old.Format != r.Edition.Format || old.EditionLabel != r.Edition.EditionLabel || old.EditionVariant != r.Edition.EditionVariant || old.MetadataSourceURL != r.Edition.MetadataSourceURL {
							return fmt.Errorf("cannot reconcile different edition identities")
						}
						if old.ISBN != "" && r.Edition.ISBN != "" && old.ISBN != r.Edition.ISBN {
							return fmt.Errorf("cannot reconcile conflicting ISBNs")
						}
						if err := tx.Model(&model.Listing{}).Where("edition_id = ?", old.ID).Update("edition_id", r.Edition.ID).Error; err != nil {
							return err
						}
						if err := tx.Model(&model.Edition{}).Where("id = ?", old.ID).Update("status", "superseded").Error; err != nil {
							return err
						}
					}
				}
			}
			if len(r.Batch.Items) == 0 {
				continue
			}
			var source model.Source
			if result := tx.First(&source, "id = ?", r.Source.ID); result.Error == gorm.ErrRecordNotFound {
				if err := tx.Create(&r.Source).Error; err != nil {
					return err
				}
			} else if result.Error != nil {
				return result.Error
			}
			payload, _ := json.Marshal(r.Batch)
			req := httptest.NewRequest("POST", "/internal/import", strings.NewReader(string(payload)))
			req.Header.Set("Content-Type", "application/json")
			req.Header.Set("X-Scraper-Token", os.Getenv("SCRAPER_INGEST_TOKEN"))
			rec := httptest.NewRecorder()
			ctx := echo.New().NewContext(req, rec)
			if err := handler.NewCatalogHandler(service.NewCatalogService(repository.NewCatalogRepository(tx))).IngestBatch(ctx); err != nil {
				return err
			}
			var result struct {
				Rejected int `json:"rejected"`
			}
			if err := json.Unmarshal(rec.Body.Bytes(), &result); err != nil {
				return err
			}
			if result.Rejected != 0 {
				return fmt.Errorf("ingestion rejected %d items; rollback", result.Rejected)
			}
			for _, image := range r.Media {
				var listing model.Listing
				if err := tx.Where("source_id = ? AND external_id = ?", r.Batch.SourceID, image.ExternalID).First(&listing).Error; err != nil {
					return fmt.Errorf("could not resolve imported listing image %s", image.ExternalID)
				}
				asset := model.CatalogMedia{
					EntityType:  "listing",
					EntityID:    listing.ID,
					MediaType:   image.MediaType,
					OriginalURL: image.OriginalURL,
					StorageURL:  image.StorageURL,
					SourceURL:   image.SourceURL,
					IsPrimary:   image.IsPrimary,
				}
				if err := tx.Clauses(clause.OnConflict{
					Columns:   []clause.Column{{Name: "entity_type"}, {Name: "entity_id"}, {Name: "media_type"}},
					DoUpdates: clause.AssignmentColumns([]string{"original_url", "storage_url", "source_url", "is_primary", "updated_at"}),
				}).Create(&asset).Error; err != nil {
					return err
				}
				listingMediaCount++
			}
		}
		return nil
	})
	if e != nil {
		fail(e)
	}
	fmt.Printf("Catalog records and price observations committed; R2 listing images with source attribution: %d\n", listingMediaCount)
}
