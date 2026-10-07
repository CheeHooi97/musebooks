package handler

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"github.com/labstack/echo/v4"
	"musebooks/model"
	"musebooks/service"
	"net/http"
	"os"
	"strconv"
	"strings"
	"time"
)

type CatalogHandler struct {
	service      *service.CatalogService
	ingestSecret string
}

func NewCatalogHandler(s *service.CatalogService) *CatalogHandler {
	return &CatalogHandler{service: s, ingestSecret: strings.TrimSpace(os.Getenv("SCRAPER_INGEST_TOKEN"))}
}
func (h *CatalogHandler) ListBooks(c echo.Context) error {
	params := model.ListBooksQuery{
		Query:        strings.TrimSpace(c.QueryParam("q")),
		Origin:       strings.TrimSpace(c.QueryParam("origin")),
		Format:       strings.TrimSpace(c.QueryParam("format")),
		Language:     strings.TrimSpace(c.QueryParam("language")),
		Availability: strings.TrimSpace(c.QueryParam("availability")),
		Year:         strings.TrimSpace(c.QueryParam("year")),
		Page:         parsePositiveInt(c.QueryParam("page"), 1),
		PageSize:     min(parsePositiveInt(c.QueryParam("pageSize"), 24), 50),
	}

	works, total, err := h.service.ListBooks(c.Request().Context(), params)
	if err != nil {
		return echo.NewHTTPError(500, "failed to load books")
	}

	items := make([]model.BookResponse, 0, len(works))
	for _, work := range works {
		items = append(items, work.Response())
	}
	totalPages := 0
	if total > 0 {
		totalPages = int((total + int64(params.PageSize) - 1) / int64(params.PageSize))
	}
	return c.JSON(http.StatusOK, model.ListBooksResponse{
		Items: items, Page: params.Page, PageSize: params.PageSize, Total: total, TotalPages: totalPages,
	})
}

func (h *CatalogHandler) GetBook(c echo.Context) error {
	key := strings.TrimSpace(c.Param("id"))
	var work model.Work
	result := h.service.GetBook(&work, key)
	if errors.Is(result.Error, service.ErrRecordNotFound) {
		return echo.NewHTTPError(http.StatusNotFound, "book not found")
	}
	if result.Error != nil {
		return echo.NewHTTPError(http.StatusInternalServerError, "failed to load book")
	}
	return c.JSON(http.StatusOK, work.Response())
}

func (h *CatalogHandler) GetEdition(c echo.Context) error {
	var edition model.Edition
	result := h.service.GetEdition(&edition, c.Param("id"))
	if errors.Is(result.Error, service.ErrRecordNotFound) {
		return echo.NewHTTPError(http.StatusNotFound, "edition not found")
	}
	if result.Error != nil {
		return echo.NewHTTPError(http.StatusInternalServerError, "failed to load edition")
	}
	return c.JSON(http.StatusOK, edition.Response())
}

func (h *CatalogHandler) ListOrigins(c echo.Context) error {
	origins, err := h.service.ListOrigins(c.Request().Context())
	if err != nil {
		return echo.NewHTTPError(500, "failed to load origins")
	}
	return c.JSON(http.StatusOK, origins)
}

func (h *CatalogHandler) ListSources(c echo.Context) error {
	var sources []model.Source
	if err := h.service.ListSources(&sources).Error; err != nil {
		return echo.NewHTTPError(http.StatusInternalServerError, "failed to load sources")
	}
	result := make([]model.SourceResponse, 0, len(sources))
	for _, source := range sources {
		result = append(result, model.SourceResponse{ID: source.ID, Name: source.Name, Region: source.Region, Kind: source.Kind, PhotobookFormat: model.SourcePhotobookFormat(source)})
	}
	return c.JSON(http.StatusOK, result)
}

func (h *CatalogHandler) IngestBatch(c echo.Context) error {
	if err := h.checkScraperToken(c); err != nil {
		return err
	}
	var batch model.ObservationBatch
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
	var source model.Source
	if result := h.service.GetSource(&source, batch.SourceID); errors.Is(result.Error, service.ErrRecordNotFound) {
		return echo.NewHTTPError(http.StatusBadRequest, "unknown sourceId")
	} else if result.Error != nil {
		return echo.NewHTTPError(http.StatusInternalServerError, "failed to validate sourceId")
	}
	if !source.Enabled || source.AccessStatus == jobBlocked || strings.ToLower(strings.TrimSpace(source.AccessMethod)) != "browser" {
		return echo.NewHTTPError(http.StatusConflict, "source access is disabled or blocked")
	}
	var job model.ScrapeJob
	if batch.JobID != "" {
		result := h.service.GetJob(&job, batch.JobID)
		if result.Error == nil {
			if job.SourceID != batch.SourceID {
				return echo.NewHTTPError(http.StatusBadRequest, "job source does not match sourceId")
			}
			if batch.WorkerID == "" || batch.LeaseToken == "" || job.WorkerID != batch.WorkerID || job.LeaseToken != batch.LeaseToken || job.Status != jobRunning {
				return echo.NewHTTPError(http.StatusConflict, "scrape job is not owned by this worker")
			}
		} else if !errors.Is(result.Error, service.ErrRecordNotFound) {
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
	err := h.service.Transaction(func(tx *service.CatalogService) error {
		for _, item := range batch.Items {
			if strings.TrimSpace(item.ExternalID) == "" || strings.TrimSpace(item.URL) == "" || strings.TrimSpace(item.Title) == "" {
				rejected++
				continue
			}
			if len([]rune(item.ExternalID)) > 180 || model.ValidateSourceURL(source, item.URL) != nil {
				rejected++
				continue
			}
			format, digitalAccess, formatErr := model.ValidateObservationFormat(source, item.Format, item.DigitalAccess)
			if formatErr != nil {
				rejected++
				continue
			}
			priceType, priceErr := model.ValidateObservationPrice(format, strings.ToLower(strings.TrimSpace(item.Status)), item.PriceType)
			if priceErr != nil {
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
			var listing model.Listing
			result := tx.LockListing(&listing, batch.SourceID, item.ExternalID)
			if errors.Is(result.Error, service.ErrRecordNotFound) {
				listing = model.Listing{ID: id, SourceID: batch.SourceID, ExternalID: item.ExternalID, CreatedAt: observedAt}
			} else if result.Error != nil {
				return result.Error
			}
			if existingFormat := model.NormalizeFormat(listing.FormatCandidate); existingFormat != "" && existingFormat != format {
				rejected++
				continue
			}
			// A source item has one format. Keep curated links only when they
			// refer to that format; never attach an ebook offer to a paper edition.
			if item.EditionID != "" {
				listing.EditionID = item.EditionID
			}
			if listing.EditionID != "" {
				var edition model.Edition
				editionResult := tx.GetEditionIdentity(&edition, listing.EditionID)
				if editionResult.Error != nil && !errors.Is(editionResult.Error, service.ErrRecordNotFound) {
					return editionResult.Error
				}
				if editionResult.Error != nil || model.NormalizeFormat(edition.Format) != format {
					if item.EditionID != "" {
						rejected++
						continue
					}
					listing.EditionID = ""
				}
			}
			if errors.Is(result.Error, service.ErrRecordNotFound) {
				created++
			} else {
				updated++
			}
			listing.ISBN = strings.TrimSpace(item.ISBN)
			listing.Publisher = strings.TrimSpace(item.Publisher)
			listing.EditionVariant = strings.TrimSpace(item.EditionVariant)
			listing.URL = item.URL
			listing.Title = item.Title
			listing.SellerLocation = item.SellerLocation
			listing.Condition = item.Condition
			listing.FormatCandidate = format
			listing.DigitalAccess = digitalAccess
			listing.Status = status
			listing.PriceMinor = item.PriceMinor
			listing.Currency = item.Currency
			listing.PriceType = priceType
			listing.ShippingText = item.ShippingText
			listing.ImageURL = item.ImageURL
			listing.ObservedAt = seenAt
			listing.LastSeenAt = seenAt
			if err := tx.SaveListing(&listing).Error; err != nil {
				return err
			}

			observationKey := model.ScrapeObservationID(batch.SourceID, item.ExternalID, batch.JobID, item.ObservationID)
			observation := model.ListingObservation{
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
				PriceType:          priceType,
				ShippingText:       item.ShippingText,
				StatusEvidence:     item.StatusEvidence,
				SourceTimestamp:    item.SourceTimestamp,
				TimestampPrecision: item.TimestampPrecision,
			}
			result = tx.GetObservation(observationKey)
			if errors.Is(result.Error, service.ErrRecordNotFound) {
				if err := tx.CreateObservation(&observation).Error; err != nil {
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
			if err := tx.UpdateJob(&job, updates).Error; err != nil {
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
