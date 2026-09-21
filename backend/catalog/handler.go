package catalog

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"os"
	"strconv"
	"strings"
	"time"

	"github.com/labstack/echo/v4"
	"gorm.io/gorm"
	"gorm.io/gorm/clause"
)

type Handler struct {
	db           *gorm.DB
	ingestSecret string
}

func NewHandler(db *gorm.DB) *Handler {
	return &Handler{db: db, ingestSecret: strings.TrimSpace(os.Getenv("SCRAPER_INGEST_TOKEN"))}
}

func (h *Handler) ListBooks(c echo.Context) error {
	params := ListBooksQuery{
		Query:        strings.TrimSpace(c.QueryParam("q")),
		Origin:       strings.TrimSpace(c.QueryParam("origin")),
		Format:       strings.TrimSpace(c.QueryParam("format")),
		Language:     strings.TrimSpace(c.QueryParam("language")),
		Availability: strings.TrimSpace(c.QueryParam("availability")),
		Year:         strings.TrimSpace(c.QueryParam("year")),
		Page:         parsePositiveInt(c.QueryParam("page"), 1),
		PageSize:     min(parsePositiveInt(c.QueryParam("pageSize"), 24), 50),
	}

	query := h.db.Model(&Work{}).Where("works.status = ?", "published")
	query = applyWorkFilters(query, params)

	var total int64
	if err := query.Session(&gorm.Session{}).Distinct("works.id").Count(&total).Error; err != nil {
		return echo.NewHTTPError(http.StatusInternalServerError, "failed to count books")
	}

	var works []Work
	offset := (params.Page - 1) * params.PageSize
	err := query.
		Distinct("works.*").
		Preload("Origin").
		Preload("Editions", func(db *gorm.DB) *gorm.DB {
			return db.Order("release_date DESC NULLS LAST, edition_label ASC")
		}).
		Preload("Editions.Listings", func(db *gorm.DB) *gorm.DB {
			return db.Where("listings.status IN ?", []string{"active", "unknown"}).Order("last_seen_at DESC")
		}).
		Preload("Editions.Listings.Source").
		Order("works.updated_at DESC, works.id ASC").
		Offset(offset).Limit(params.PageSize).
		Find(&works).Error
	if err != nil {
		return echo.NewHTTPError(http.StatusInternalServerError, "failed to load books")
	}

	items := make([]BookResponse, 0, len(works))
	for _, work := range works {
		items = append(items, work.Response())
	}
	totalPages := 0
	if total > 0 {
		totalPages = int((total + int64(params.PageSize) - 1) / int64(params.PageSize))
	}
	return c.JSON(http.StatusOK, ListBooksResponse{
		Items: items, Page: params.Page, PageSize: params.PageSize, Total: total, TotalPages: totalPages,
	})
}

func (h *Handler) GetBook(c echo.Context) error {
	key := strings.TrimSpace(c.Param("id"))
	var work Work
	query := h.db.Preload("Origin").Preload("Editions", func(db *gorm.DB) *gorm.DB {
		return db.Order("release_date DESC NULLS LAST, edition_label ASC")
	}).Preload("Editions.Listings").Preload("Editions.Listings.Source")
	result := query.Where("works.id = ? OR works.slug = ?", key, key).First(&work)
	if errors.Is(result.Error, gorm.ErrRecordNotFound) {
		return echo.NewHTTPError(http.StatusNotFound, "book not found")
	}
	if result.Error != nil {
		return echo.NewHTTPError(http.StatusInternalServerError, "failed to load book")
	}
	return c.JSON(http.StatusOK, work.Response())
}

func (h *Handler) GetEdition(c echo.Context) error {
	var edition Edition
	result := h.db.Preload("Listings").Preload("Listings.Source").First(&edition, "id = ?", c.Param("id"))
	if errors.Is(result.Error, gorm.ErrRecordNotFound) {
		return echo.NewHTTPError(http.StatusNotFound, "edition not found")
	}
	if result.Error != nil {
		return echo.NewHTTPError(http.StatusInternalServerError, "failed to load edition")
	}
	return c.JSON(http.StatusOK, edition.Response())
}

func (h *Handler) ListOrigins(c echo.Context) error {
	var origins []Origin
	if err := h.db.Order("sort_order ASC, name ASC").Find(&origins).Error; err != nil {
		return echo.NewHTTPError(http.StatusInternalServerError, "failed to load origins")
	}
	type originCount struct {
		Code  string
		Count int64
	}
	var counts []originCount
	if err := h.db.Model(&Work{}).
		Select("origin_code AS code, COUNT(*) AS count").
		Where("status = ?", "published").
		Group("origin_code").
		Scan(&counts).Error; err != nil {
		return echo.NewHTTPError(http.StatusInternalServerError, "failed to count origins")
	}
	countByCode := make(map[string]int64, len(counts))
	for _, item := range counts {
		countByCode[item.Code] = item.Count
	}
	result := make([]OriginResponse, 0, len(origins))
	for _, origin := range origins {
		result = append(result, origin.Response(countByCode[origin.Code]))
	}
	return c.JSON(http.StatusOK, result)
}

func (h *Handler) ListSources(c echo.Context) error {
	var sources []Source
	if err := h.db.Where("enabled = ?", true).Order("name ASC").Find(&sources).Error; err != nil {
		return echo.NewHTTPError(http.StatusInternalServerError, "failed to load sources")
	}
	result := make([]SourceResponse, 0, len(sources))
	for _, source := range sources {
		result = append(result, SourceResponse{ID: source.ID, Name: source.Name, Region: source.Region, Kind: source.Kind})
	}
	return c.JSON(http.StatusOK, result)
}

type ObservationBatch struct {
	JobID         string             `json:"jobId"`
	WorkerID      string             `json:"workerId,omitempty"`
	LeaseToken    string             `json:"leaseToken,omitempty"`
	SourceID      string             `json:"sourceId"`
	ParserVersion string             `json:"parserVersion"`
	RetrievedAt   time.Time          `json:"retrievedAt"`
	PageNumber    int                `json:"pageNumber,omitempty"`
	NextCursor    string             `json:"nextCursor,omitempty"`
	HasMore       bool               `json:"hasMore,omitempty"`
	Items         []ObservationInput `json:"items"`
	Warnings      []string           `json:"warnings,omitempty"`
	Diagnostics   map[string]any     `json:"diagnostics,omitempty"`
}

type ObservationInput struct {
	ObservationID      string     `json:"observationId,omitempty"`
	ExternalID         string     `json:"externalId"`
	EditionID          string     `json:"editionId,omitempty"`
	URL                string     `json:"url"`
	Title              string     `json:"title"`
	SellerLocation     string     `json:"sellerLocation,omitempty"`
	Condition          string     `json:"condition,omitempty"`
	Status             string     `json:"status"`
	PriceMinor         int64      `json:"priceMinor,omitempty"`
	Currency           string     `json:"currency,omitempty"`
	PriceType          string     `json:"priceType,omitempty"`
	Format             string     `json:"format"`
	DigitalAccess      string     `json:"digitalAccess,omitempty"`
	ShippingText       string     `json:"shippingText,omitempty"`
	ImageURL           string     `json:"imageUrl,omitempty"`
	ObservedAt         time.Time  `json:"observedAt"`
	StatusEvidence     string     `json:"statusEvidence,omitempty"`
	SourceTimestamp    *time.Time `json:"sourceTimestamp,omitempty"`
	TimestampPrecision string     `json:"timestampPrecision,omitempty"`
}

func (h *Handler) IngestBatch(c echo.Context) error {
	if err := h.checkScraperToken(c); err != nil {
		return err
	}
	var batch ObservationBatch
	if err := json.NewDecoder(c.Request().Body).Decode(&batch); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, "invalid observation batch")
	}
	batch.SourceID = strings.TrimSpace(batch.SourceID)
	batch.JobID = strings.TrimSpace(batch.JobID)
	batch.WorkerID = strings.TrimSpace(batch.WorkerID)
	batch.LeaseToken = strings.TrimSpace(batch.LeaseToken)
	if batch.SourceID == "" || len(batch.Items) > 500 {
		return echo.NewHTTPError(http.StatusBadRequest, "sourceId is required and a batch may contain at most 500 items")
	}
	var source Source
	if result := h.db.First(&source, "id = ?", batch.SourceID); errors.Is(result.Error, gorm.ErrRecordNotFound) {
		return echo.NewHTTPError(http.StatusBadRequest, "unknown sourceId")
	} else if result.Error != nil {
		return echo.NewHTTPError(http.StatusInternalServerError, "failed to validate sourceId")
	}
	if !source.Enabled || source.AccessStatus == jobBlocked || strings.ToLower(strings.TrimSpace(source.AccessMethod)) != "browser" {
		return echo.NewHTTPError(http.StatusConflict, "source access is disabled or blocked")
	}
	var job ScrapeJob
	if batch.JobID != "" {
		result := h.db.First(&job, "id = ?", batch.JobID)
		if result.Error == nil {
			if job.SourceID != batch.SourceID {
				return echo.NewHTTPError(http.StatusBadRequest, "job source does not match sourceId")
			}
			if batch.WorkerID == "" || batch.LeaseToken == "" || job.WorkerID != batch.WorkerID || job.LeaseToken != batch.LeaseToken || job.Status != jobRunning {
				return echo.NewHTTPError(http.StatusConflict, "scrape job is not owned by this worker")
			}
		} else if !errors.Is(result.Error, gorm.ErrRecordNotFound) {
			return echo.NewHTTPError(http.StatusInternalServerError, "failed to validate scrape job")
		} else if batch.WorkerID != "" {
			return echo.NewHTTPError(http.StatusConflict, "scrape job was not found")
		}
	}
	observedAt := batch.RetrievedAt
	if observedAt.IsZero() {
		observedAt = time.Now().UTC()
	}
	created, updated, observationCreated, observationDuplicate, rejected := 0, 0, 0, 0, 0
	err := h.db.Transaction(func(tx *gorm.DB) error {
		for _, item := range batch.Items {
			if strings.TrimSpace(item.ExternalID) == "" || strings.TrimSpace(item.URL) == "" || strings.TrimSpace(item.Title) == "" {
				rejected++
				continue
			}
			if len([]rune(item.ExternalID)) > 180 || validateSourceURL(source, item.URL) != nil {
				rejected++
				continue
			}
			format, digitalAccess, formatErr := validateObservationFormat(source, item.Format, item.DigitalAccess)
			if formatErr != nil {
				rejected++
				continue
			}
			seenAt := item.ObservedAt
			if seenAt.IsZero() {
				seenAt = observedAt
			}
			status := strings.ToLower(strings.TrimSpace(item.Status))
			if status == "" {
				status = "unknown"
			}
			id := listingID(batch.SourceID, item.ExternalID)
			var listing Listing
			result := tx.Clauses(clause.Locking{Strength: "UPDATE"}).
				Where("source_id = ? AND external_id = ?", batch.SourceID, item.ExternalID).First(&listing)
			if errors.Is(result.Error, gorm.ErrRecordNotFound) {
				listing = Listing{ID: id, SourceID: batch.SourceID, ExternalID: item.ExternalID, CreatedAt: observedAt}
				created++
			} else if result.Error != nil {
				return result.Error
			} else {
				updated++
			}
			listing.EditionID = item.EditionID
			listing.URL = item.URL
			listing.Title = item.Title
			listing.SellerLocation = item.SellerLocation
			listing.Condition = item.Condition
			listing.FormatCandidate = format
			listing.DigitalAccess = digitalAccess
			listing.Status = status
			listing.PriceMinor = item.PriceMinor
			listing.Currency = item.Currency
			listing.PriceType = item.PriceType
			listing.ShippingText = item.ShippingText
			listing.ImageURL = item.ImageURL
			listing.ObservedAt = seenAt
			listing.LastSeenAt = seenAt
			if err := tx.Save(&listing).Error; err != nil {
				return err
			}

			observationKey := scrapeObservationID(batch.SourceID, item.ExternalID, batch.JobID, item.ObservationID)
			observation := ListingObservation{
				ID:                 observationKey,
				ObservationKey:     observationKey,
				ListingID:          listing.ID,
				JobID:              batch.JobID,
				ParserVersion:      batch.ParserVersion,
				ObservedAt:         seenAt,
				Status:             status,
				Format:             format,
				DigitalAccess:      digitalAccess,
				PriceMinor:         item.PriceMinor,
				Currency:           item.Currency,
				PriceType:          item.PriceType,
				ShippingText:       item.ShippingText,
				StatusEvidence:     item.StatusEvidence,
				SourceTimestamp:    item.SourceTimestamp,
				TimestampPrecision: item.TimestampPrecision,
			}
			result = tx.Where("observation_key = ?", observationKey).First(&ListingObservation{})
			if errors.Is(result.Error, gorm.ErrRecordNotFound) {
				if err := tx.Create(&observation).Error; err != nil {
					return err
				}
				observationCreated++
			} else if result.Error != nil {
				return result.Error
			} else {
				observationDuplicate++
			}
		}
		if batch.JobID != "" && job.ID != "" {
			updates := map[string]any{
				"page_cursor":       batch.NextCursor,
				"last_heartbeat_at": time.Now().UTC(),
			}
			if err := tx.Model(&job).Updates(updates).Error; err != nil {
				return err
			}
		}
		return nil
	})
	if err != nil {
		return echo.NewHTTPError(http.StatusInternalServerError, "failed to ingest observation batch")
	}
	return c.JSON(http.StatusAccepted, map[string]any{
		"jobId": batch.JobID, "sourceId": batch.SourceID, "created": created, "updated": updated,
		"observationsCreated": observationCreated, "observationsDuplicate": observationDuplicate,
		"rejected": rejected, "nextCursor": batch.NextCursor, "hasMore": batch.HasMore, "receivedAt": observedAt,
	})
}

func applyWorkFilters(query *gorm.DB, params ListBooksQuery) *gorm.DB {
	if params.Query != "" {
		pattern := "%" + params.Query + "%"
		query = query.Where("works.original_title ILIKE ? OR works.english_title ILIKE ? OR works.featured_names ILIKE ?", pattern, pattern, pattern)
	}
	if params.Origin != "" {
		query = query.Where("works.origin_code = ?", params.Origin)
	}
	if params.Format != "" || params.Language != "" || params.Year != "" {
		query = query.Joins("JOIN editions AS filter_editions ON filter_editions.work_id = works.id")
		if params.Format != "" {
			query = query.Where("filter_editions.format = ?", params.Format)
		}
		if params.Language != "" {
			query = query.Where("filter_editions.language = ?", params.Language)
		}
		if params.Year != "" {
			query = query.Where("EXTRACT(YEAR FROM filter_editions.release_date) = ?", params.Year)
		}
	}
	if params.Availability != "" {
		query = query.Joins("JOIN editions AS availability_editions ON availability_editions.work_id = works.id").
			Joins("JOIN listings AS availability_listings ON availability_listings.edition_id = availability_editions.id").
			Where("availability_listings.status = ?", params.Availability)
	}
	return query
}

func listingID(sourceID, externalID string) string {
	hash := sha256.Sum256([]byte(sourceID + "\x00" + externalID))
	return fmt.Sprintf("listing-%s", hex.EncodeToString(hash[:])[:32])
}

func parsePositiveInt(value string, fallback int) int {
	parsed, err := strconv.Atoi(value)
	if err != nil || parsed < 1 {
		return fallback
	}
	return parsed
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}
