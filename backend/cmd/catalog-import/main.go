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
	"regexp"
	"strings"
	"time"
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
	ReplaceLegacyFeaturedAlias string                 `json:"replaceLegacyFeaturedAlias,omitempty"`
	UseCoverCreditsOnly        bool                   `json:"useCoverCreditsOnly,omitempty"`
	SupersedesEditionID        string                 `json:"supersedesEditionId,omitempty"`
	ReassignEditionFromWorkID  string                 `json:"reassignEditionFromWorkId,omitempty"`
	Origin                     *model.Origin          `json:"origin,omitempty"`
	Work                       model.Work             `json:"work"`
	FeaturedPerson             *model.Person          `json:"featuredPerson,omitempty"`
	FeaturedCreditSource       string                 `json:"featuredCreditSource,omitempty"`
	AdditionalFeaturedPeople   []model.Person         `json:"additionalFeaturedPeople,omitempty"`
	CoverPerson                *model.Person          `json:"coverPerson,omitempty"`
	AdditionalCoverPeople      []model.Person         `json:"additionalCoverPeople,omitempty"`
	Edition                    model.Edition          `json:"edition"`
	Source                     model.Source           `json:"source"`
	Batch                      model.ObservationBatch `json:"batch"`
	Media                      []ListingMediaInput    `json:"media,omitempty"`
	PublisherMedia             []ListingMediaInput    `json:"publisherMedia,omitempty"`
}

func validHTTPSURL(value string) bool {
	parsed, err := url.Parse(strings.TrimSpace(value))
	return err == nil && parsed.Scheme == "https" && parsed.Host != "" && parsed.User == nil
}

func validCatalogOrigin(code string) bool {
	switch strings.ToUpper(strings.TrimSpace(code)) {
	case "JP", "TW", "CN", "MY", "KR":
		return true
	default:
		return false
	}
}

func validExclusionReason(reason string) bool {
	switch reason {
	case "calendar_only", "illustrated_book", "disc_only", "magazine_only", "magazine_or_supplement", "junior_gravure", "artist_monograph", "synthetic_subject", "download_resale", "free_preview", "nonbook_product", "subject_publication_age_unverified", "nonhuman_subject", "reference_book", "incorrect_model_association":
		return true
	default:
		return false
	}
}

func validPersonIdentity(person *model.Person) bool {
	return person != nil && person.ID == 0 && person.Slug == model.CatalogIdentity("model", person.CanonicalPublicName) && strings.TrimSpace(person.CanonicalPublicName) != ""
}

func upsertFeaturedCredit(tx *gorm.DB, workID string, input model.Person, people map[string]model.Person, creditSource string) error {
	if strings.TrimSpace(creditSource) == "" {
		creditSource = "verified_model_capture"
	}
	person := input
	if known, ok := people[person.Slug]; ok {
		person = known
	} else {
		personUpdates := map[string]interface{}{}
		for column, value := range map[string]string{
			"canonical_public_name":     person.CanonicalPublicName,
			"original_name":             person.OriginalName,
			"english_name":              person.EnglishName,
			"traditional_chinese_name":  person.TraditionalChineseName,
			"simplified_chinese_name":   person.SimplifiedChineseName,
			"person_type":               person.PersonType,
			"verification_source_url":   person.VerificationSourceURL,
			"profile_source_confidence": person.ProfileSourceConfidence,
		} {
			if strings.TrimSpace(value) != "" {
				personUpdates[column] = value
			}
		}
		if err := tx.Clauses(clause.OnConflict{Columns: []clause.Column{{Name: "slug"}}, DoUpdates: clause.Assignments(personUpdates)}).Create(&person).Error; err != nil {
			return err
		}
		if err := tx.Where("slug = ?", person.Slug).First(&person).Error; err != nil {
			return err
		}
		people[person.Slug] = person
	}
	credit := model.WorkPerson{WorkID: workID, PersonID: person.ID, Role: "featured", CreditedName: person.CanonicalPublicName, CreditSource: creditSource}
	return tx.Omit("Work", "Person").Clauses(clause.OnConflict{Columns: []clause.Column{{Name: "work_id"}, {Name: "person_id"}, {Name: "role"}}, DoUpdates: clause.AssignmentColumns([]string{"credited_name", "credit_source", "updated_at"})}).Create(&credit).Error
}

// normalizeReleaseDate stores precision-limited dates as calendar dates at UTC
// midnight. The API serializes time values, while clients render the first ten
// characters as a date; retaining a source timezone offset here can shift the
// displayed publication day for readers in another timezone.
func normalizeReleaseDate(edition *model.Edition) {
	if edition == nil || edition.ReleaseDate == nil {
		return
	}
	displayedDate := *edition.ReleaseDate
	year, month, day := displayedDate.Date()
	switch edition.ReleasePrecision {
	case "day":
		// Keep the calendar date encoded in the reviewed source timestamp.
	case "month":
		day = 1
	case "year":
		month, day = time.January, 1
	default:
		return
	}
	normalized := time.Date(year, month, day, 0, 0, 0, 0, time.UTC)
	edition.ReleaseDate = &normalized
}

func validateMediaInput(record Record) error {
	for _, media := range record.PublisherMedia {
		if record.Edition.ID == "" || !validHTTPSURL(media.OriginalURL) || !validHTTPSURL(media.StorageURL) || media.SourceURL != record.Edition.MetadataSourceURL || !validHTTPSURL(media.SourceURL) || !regexp.MustCompile(`^publisher_(cover|sample_[0-9]{3})$`).MatchString(media.MediaType) || (media.IsPrimary && (media.MediaType != "publisher_cover" || media.StorageURL != record.Edition.CoverURL)) {
			return fmt.Errorf("publisher image provenance does not match the reviewed edition")
		}
	}
	if len(record.Media) == 0 {
		return nil
	}
	items := make(map[string]model.ObservationInput, len(record.Batch.Items))
	for _, item := range record.Batch.Items {
		items[item.ExternalID] = item
	}
	for _, media := range record.Media {
		item, ok := items[media.ExternalID]
		gallery := regexp.MustCompile(`^listing_image_[0-9]{3}$`).MatchString(media.MediaType)
		if !ok || strings.TrimSpace(media.ExternalID) == "" || (media.MediaType != "listing_image" && !gallery) ||
			strings.TrimSpace(media.OriginalURL) == "" || strings.TrimSpace(media.StorageURL) == "" ||
			!validHTTPSURL(media.OriginalURL) || !validHTTPSURL(media.StorageURL) ||
			(media.IsPrimary && media.StorageURL != item.ImageURL) || media.SourceURL != item.URL {
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
	var db *gorm.DB
	needsDatabase := *manifest == "" || *apply || *exclude != "" || *verify || *create
	if needsDatabase {
		var err error
		db, err = connect(name)
		if err != nil {
			fail(fmt.Errorf("cannot connect to database %s; check name and server access", name))
		}
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
		if err := validateFeaturedAliasCorrection(r); err != nil {
			fail(err)
		}
		if r.FeaturedPerson != nil && !validPersonIdentity(r.FeaturedPerson) {
			fail(fmt.Errorf("record %d has invalid featured person identity", i))
		}
		seenFeaturedPeople := map[string]bool{}
		if r.FeaturedPerson != nil {
			seenFeaturedPeople[r.FeaturedPerson.Slug] = true
		}
		for _, person := range r.AdditionalFeaturedPeople {
			if !validPersonIdentity(&person) || seenFeaturedPeople[person.Slug] {
				fail(fmt.Errorf("record %d has invalid or duplicate additional featured person identity", i))
			}
			seenFeaturedPeople[person.Slug] = true
		}
		if r.FeaturedCreditSource != "" && r.FeaturedCreditSource != "verified_model_capture" && r.FeaturedCreditSource != "verified_press_source" && r.FeaturedCreditSource != "verified_publisher_source" {
			fail(fmt.Errorf("record %d has invalid featured credit source", i))
		}
		if r.CoverPerson != nil && !validPersonIdentity(r.CoverPerson) {
			fail(fmt.Errorf("record %d has invalid cover person identity", i))
		}
		seenCoverPeople := map[string]bool{}
		if r.CoverPerson != nil {
			seenCoverPeople[r.CoverPerson.Slug] = true
		}
		for _, person := range r.AdditionalCoverPeople {
			if !validPersonIdentity(&person) || seenCoverPeople[person.Slug] {
				fail(fmt.Errorf("record %d has invalid or duplicate additional cover person identity", i))
			}
			seenCoverPeople[person.Slug] = true
		}
		if r.Origin != nil && (!validCatalogOrigin(r.Origin.Code) || strings.TrimSpace(r.Origin.Name) == "") {
			fail(fmt.Errorf("record %d has an invalid origin", i))
		}
		if err := validateMediaInput(r); err != nil {
			fail(fmt.Errorf("record %d: %w", i, err))
		}
		if err := validateIssueReassignment(r); err != nil {
			fail(fmt.Errorf("record %d: %w", i, err))
		}
		if err := validateCoverOnlyCorrection(r); err != nil {
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

		if r.Work.PublicationType == "" {
			r.Work.PublicationType = model.PublicationTypePhotobook
		}
		if r.Work.PublicationType != model.PublicationTypePhotobook && r.Work.PublicationType != model.PublicationTypeMagazineIssue {
			fail(fmt.Errorf("record %d has invalid publication type", i))
		}
		if r.Work.PublicationType == model.PublicationTypeMagazineIssue {
			if !regexp.MustCompile(`^\d{4}-(0[1-9]|1[0-2])$`).MatchString(r.Work.IssueMonth) || !validPersonIdentity(r.CoverPerson) {
				fail(fmt.Errorf("record %d magazine issue requires an issue month and verified cover model", i))
			}
		} else if strings.TrimSpace(r.Work.FeaturedNames) == "" || r.Work.IssueMonth != "" {
			fail(fmt.Errorf("record %d photobook requires a featured model and cannot carry an issue month", i))
		}
		if r.Work.ID == "" || r.Work.OriginalTitle == "" || strings.Contains(r.Work.OriginalTitle, "??") || !validCatalogOrigin(r.Work.OriginCode) || r.Edition.ID == "" || r.Edition.WorkID != r.Work.ID || r.Edition.MetadataSourceURL == "" {
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
		// A lost network connection must not leave an abandoned import holding locks.
		if err := tx.Exec("SET LOCAL idle_in_transaction_session_timeout = '120s'").Error; err != nil {
			return err
		}
		featuredPeople := map[string]model.Person{}
		coverPeople := map[string]model.Person{}
		knownSources := map[string]bool{}
		if err := tx.Clauses(clause.OnConflict{DoNothing: true}).Create(&model.Origin{Code: "TW", Name: "Taiwan", NativeName: "台灣"}).Error; err != nil {
			return err
		}
		for recordIndex, r := range records {
			normalizeReleaseDate(&r.Edition)
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
				if r.ReassignEditionFromWorkID != "" {
					if found.Error != nil {
						return fmt.Errorf("cannot reassign missing edition %s: %w", r.Edition.ID, found.Error)
					}
					if err := reassignMagazineEdition(tx, r, &existingEdition); err != nil {
						return err
					}
				}
				if found.Error == nil && existingEdition.WorkID != r.Edition.WorkID {
					return fmt.Errorf("edition identity conflicts with existing work: %s", r.Edition.ID)
				}
				if found.Error != nil && found.Error != gorm.ErrRecordNotFound {
					return found.Error
				}
				workUpdates := []string{"original_title", "featured_names", "summary", "photographer", "publication_type", "issue_month", "issue_number", "updated_at"}
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

				var existingWork model.Work
				previous := tx.Select("featured_names").Where("id = ?", r.Work.ID).Find(&existingWork)
				if previous.Error != nil {
					return previous.Error
				}
				if r.UseCoverCreditsOnly {
					if err := guardCoverOnlyCorrection(tx, r); err != nil {
						return err
					}
				}
				if r.ReplaceLegacyFeaturedAlias != "" {
					if err := guardFeaturedAliasCorrection(tx, r); err != nil {
						return err
					}
				}
				if !r.UseCoverCreditsOnly && r.ReplaceLegacyFeaturedAlias == "" && previous.RowsAffected > 0 && existingWork.FeaturedNames != "" {
					names, seen := []string{}, map[string]bool{}
					for _, name := range strings.Split(existingWork.FeaturedNames+","+r.Work.FeaturedNames, ",") {
						name = strings.TrimSpace(name)
						if name != "" && !seen[name] {
							names = append(names, name)
							seen[name] = true
						}
					}
					r.Work.FeaturedNames = strings.Join(names, ",")
				}
				if err := tx.Omit("Origin", "Editions").Clauses(clause.OnConflict{Columns: []clause.Column{{Name: "id"}}, DoUpdates: clause.AssignmentColumns(workUpdates)}).Create(&r.Work).Error; err != nil {
					return err
				}
				if err := tx.Omit("Listings").Clauses(clause.OnConflict{Columns: []clause.Column{{Name: "id"}}, DoUpdates: clause.AssignmentColumns(editionUpdates)}).Create(&r.Edition).Error; err != nil {
					return err
				}
				if r.FeaturedPerson != nil {
					if err := upsertFeaturedCredit(tx, r.Work.ID, *r.FeaturedPerson, featuredPeople, r.FeaturedCreditSource); err != nil {
						return err
					}
				}
				for _, person := range r.AdditionalFeaturedPeople {
					if err := upsertFeaturedCredit(tx, r.Work.ID, person, featuredPeople, r.FeaturedCreditSource); err != nil {
						return err
					}
				}
				if r.CoverPerson != nil {
					person := *r.CoverPerson
					if known, ok := coverPeople[person.Slug]; ok {
						person = known
					} else {
						if err := tx.Clauses(clause.OnConflict{Columns: []clause.Column{{Name: "slug"}}, DoNothing: true}).Create(&person).Error; err != nil {
							return err
						}
						if err := tx.Where("slug = ?", person.Slug).First(&person).Error; err != nil {
							return err
						}
						coverPeople[person.Slug] = person
					}
					credit := model.WorkPerson{WorkID: r.Work.ID, PersonID: person.ID, Role: "cover_model", CreditedName: person.CanonicalPublicName, CreditSource: "verified_cover_credit"}
					if err := tx.Omit("Work", "Person").Clauses(clause.OnConflict{Columns: []clause.Column{{Name: "work_id"}, {Name: "person_id"}, {Name: "role"}}, DoUpdates: clause.AssignmentColumns([]string{"credited_name", "credit_source", "updated_at"})}).Create(&credit).Error; err != nil {
						return err
					}
				}
				for _, additional := range r.AdditionalCoverPeople {
					person := additional
					if known, ok := coverPeople[person.Slug]; ok {
						person = known
					} else {
						if err := tx.Clauses(clause.OnConflict{Columns: []clause.Column{{Name: "slug"}}, DoNothing: true}).Create(&person).Error; err != nil {
							return err
						}
						if err := tx.Where("slug = ?", person.Slug).First(&person).Error; err != nil {
							return err
						}
						coverPeople[person.Slug] = person
					}
					credit := model.WorkPerson{WorkID: r.Work.ID, PersonID: person.ID, Role: "cover_model", CreditedName: person.CanonicalPublicName, CreditSource: "verified_cover_credit"}
					if err := tx.Omit("Work", "Person").Clauses(clause.OnConflict{Columns: []clause.Column{{Name: "work_id"}, {Name: "person_id"}, {Name: "role"}}, DoUpdates: clause.AssignmentColumns([]string{"credited_name", "credit_source", "updated_at"})}).Create(&credit).Error; err != nil {
						return err
					}
				}
				for _, image := range r.PublisherMedia {
					asset := model.CatalogMedia{EntityType: "edition", EntityID: r.Edition.ID, MediaType: image.MediaType, OriginalURL: image.OriginalURL, StorageURL: image.StorageURL, SourceURL: image.SourceURL, IsPrimary: image.IsPrimary}
					if err := tx.Clauses(clause.OnConflict{Columns: []clause.Column{{Name: "entity_type"}, {Name: "entity_id"}, {Name: "media_type"}}, DoUpdates: clause.AssignmentColumns([]string{"original_url", "storage_url", "source_url", "is_primary", "updated_at"})}).Create(&asset).Error; err != nil {
						return err
					}
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
			if !knownSources[r.Source.ID] {
				manualSourceDisabled := r.Source.Adapter == "manual_page_capture" && !r.Source.Enabled
				var source model.Source
				if result := tx.First(&source, "id = ?", r.Source.ID); result.Error == gorm.ErrRecordNotFound {
					if err := tx.Create(&r.Source).Error; err != nil {
						return err
					}
				} else if result.Error != nil {
					return result.Error
				}
				// Preserve an explicit disabled state; GORM applies the field's true default to false on Create.
				if manualSourceDisabled {
					if err := tx.Model(&model.Source{}).Where("id = ?", r.Source.ID).Update("enabled", false).Error; err != nil {
						return err
					}
				}
				knownSources[r.Source.ID] = true
			}
			payload, _ := json.Marshal(r.Batch)
			req := httptest.NewRequest("POST", "/internal/import", strings.NewReader(string(payload)))
			req.Header.Set("Content-Type", "application/json")
			req.Header.Set("X-Scraper-Token", os.Getenv("SCRAPER_INGEST_TOKEN"))
			rec := httptest.NewRecorder()
			ctx := echo.New().NewContext(req, rec)
			if err := handler.NewCatalogHandler(service.NewCatalogService(repository.NewCatalogRepository(tx))).IngestBatch(ctx); err != nil {
				if failure, ok := err.(*echo.HTTPError); ok && failure.Internal != nil {
					return fmt.Errorf("record %d source %s observation ingestion failed: %w", recordIndex, r.Batch.SourceID, failure.Internal)
				}
				return err
			}
			var result struct {
				Rejected int `json:"rejected"`
			}
			if err := json.Unmarshal(rec.Body.Bytes(), &result); err != nil {
				return err
			}
			if result.Rejected != 0 {
				externalIDs := make([]string, 0, len(r.Batch.Items))
				for _, item := range r.Batch.Items {
					externalIDs = append(externalIDs, item.ExternalID)
				}
				return fmt.Errorf("record %d (work %s, source %s, external IDs %s) ingestion rejected %d of %d items; rollback", recordIndex, r.Work.ID, r.Batch.SourceID, strings.Join(externalIDs, ","), result.Rejected, len(r.Batch.Items))
			}
			listingImages := map[string]model.Listing{}
			assets := []model.CatalogMedia{}
			for _, image := range r.Media {
				var listing model.Listing
				if known, ok := listingImages[image.ExternalID]; ok {
					listing = known
				} else {
					if err := tx.Where("source_id = ? AND external_id = ?", r.Batch.SourceID, image.ExternalID).First(&listing).Error; err != nil {
						return fmt.Errorf("could not resolve imported listing image %s", image.ExternalID)
					}
					listingImages[image.ExternalID] = listing
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
				assets = append(assets, asset)
				listingMediaCount++
			}
			if len(assets) > 0 {
				if err := tx.Clauses(clause.OnConflict{
					Columns:   []clause.Column{{Name: "entity_type"}, {Name: "entity_id"}, {Name: "media_type"}},
					DoUpdates: clause.AssignmentColumns([]string{"original_url", "storage_url", "source_url", "is_primary", "updated_at"}),
				}).Create(&assets).Error; err != nil {
					return err
				}
			}
		}
		return nil
	})
	if e != nil {
		fail(e)
	}
	fmt.Printf("Catalog records and price observations committed; listing image provenance records: %d\n", listingMediaCount)
}
