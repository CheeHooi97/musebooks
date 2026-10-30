package handler

import (
	"encoding/base64"
	"encoding/json"
	"errors"
	"github.com/labstack/echo/v4"
	"musebooks/model"
	"musebooks/service"
	"musebooks/storage"
	"net/http"
	"strconv"
	"strings"
	"time"
)

type CatalogBrowseHandler struct {
	service     *service.CatalogService
	ImageSigner *storage.MediaSigner
}

func NewCatalogBrowseHandler(s *service.CatalogService) *CatalogBrowseHandler {
	return &CatalogBrowseHandler{service: s}
}
func browseQuery(c echo.Context) model.CatalogBrowseQuery {
	return model.CatalogBrowseQuery{Query: strings.TrimSpace(c.QueryParam("q")), ID: c.Param("id"), Page: parsePositiveInt(c.QueryParam("page"), 1), PageSize: min(parsePositiveInt(c.QueryParam("pageSize"), 24), 50)}
}
func parsePublicationType(c echo.Context) (string, error) {
	value := strings.TrimSpace(c.QueryParam("publicationType"))
	if value != "" && value != model.PublicationTypePhotobook && value != model.PublicationTypeMagazineIssue {
		return "", echo.NewHTTPError(400, "publicationType must be photobook or magazine_issue")
	}
	return value, nil
}
func catalogPage[T any](c echo.Context, items []T, total int64, p model.CatalogBrowseQuery) error {
	pages := (total + int64(p.PageSize) - 1) / int64(p.PageSize)
	return c.JSON(http.StatusOK, map[string]any{"items": items, "total": total, "totalPages": pages, "page": p.Page, "pageSize": p.PageSize})
}
func (h *CatalogBrowseHandler) directory(c echo.Context, kind string) error {
	p := browseQuery(c)
	p.Kind = kind
	if p.Page > 1000000 {
		return echo.NewHTTPError(400, "page is too large")
	}
	entries, total, err := h.service.Directory(c.Request().Context(), p)
	if err != nil {
		return echo.NewHTTPError(500, "failed to load catalog directory")
	}
	return catalogPage(c, entries, total, p)
}
func (h *CatalogBrowseHandler) Models(c echo.Context) error     { return h.directory(c, "model") }
func (h *CatalogBrowseHandler) Publishers(c echo.Context) error { return h.directory(c, "publisher") }
func (h *CatalogBrowseHandler) DirectoryBooks(c echo.Context) error {
	p := browseQuery(c)
	p.Kind = "model"
	if strings.HasPrefix(c.Path(), "/v1/publishers") {
		p.Kind = "publisher"
	}
	if p.Page > 1000000 {
		return echo.NewHTTPError(400, "page is too large")
	}
	p.Format = c.QueryParam("format")
	publicationType, err := parsePublicationType(c)
	if err != nil {
		return err
	}
	p.PublicationType = publicationType
	p.Language = strings.TrimSpace(c.QueryParam("language"))
	p.Year = c.QueryParam("year")
	p.Person = c.QueryParam("model")
	if p.Format != "" && p.Format != "physical" && p.Format != "digital" {
		return echo.NewHTTPError(400, "format must be physical or digital")
	}
	if p.Year != "" {
		year, err := strconv.Atoi(p.Year)
		if err != nil || year < 1000 || year > 9999 {
			return echo.NewHTTPError(400, "year must be a four-digit year")
		}
	}
	profile, _, err := h.service.Directory(c.Request().Context(), model.CatalogBrowseQuery{Kind: p.Kind, ID: p.ID, Page: 1, PageSize: 1})
	if err != nil {
		return echo.NewHTTPError(500, "failed to load catalog profile")
	}
	if len(profile) == 0 {
		return echo.NewHTTPError(404, "directory entry not found")
	}
	works, total, err := h.service.DirectoryBooks(c.Request().Context(), p)
	if err != nil {
		return echo.NewHTTPError(500, "failed to load directory books")
	}
	items := make([]model.BookResponse, 0, len(works))
	for _, work := range works {
		items = append(items, work.Response())
	}
	return catalogPage(c, items, total, p)
}
func (h *CatalogBrowseHandler) Listings(c echo.Context) error {
	p := browseQuery(c)
	p.Status = c.QueryParam("status")
	if p.Status == "" {
		p.Status = "active"
	}
	if p.Status == "sold" {
		p.Status = "completed"
	}
	if p.Status != "active" && p.Status != "completed" {
		return echo.NewHTTPError(400, "status must be active or sold")
	}
	p.Format = c.QueryParam("format")
	publicationType, err := parsePublicationType(c)
	if err != nil {
		return err
	}
	p.PublicationType = publicationType
	if p.Format != "" && p.Format != "physical" && p.Format != "digital" {
		return echo.NewHTTPError(400, "format must be physical or digital")
	}
	if p.Page > 1000000 {
		return echo.NewHTTPError(400, "page is too large")
	}
	p.Source = c.QueryParam("source")
	p.Person = c.QueryParam("model")
	p.Publisher = c.QueryParam("publisher")
	items, total, err := h.service.Listings(c.Request().Context(), p)
	if err != nil {
		return echo.NewHTTPError(500, "failed to load listings")
	}
	return catalogPage(c, items, total, p)
}

func (h *CatalogBrowseHandler) MarketplaceListings(c echo.Context) error {
	p := browseQuery(c)
	p.CursorMode = c.QueryParams().Has("limit")
	p.Kind = strings.TrimSpace(c.QueryParam("scope"))
	if p.Kind != "" && p.Kind != "offers" {
		return echo.NewHTTPError(400, "scope must be offers")
	}
	p.Region = strings.ToUpper(strings.TrimSpace(c.QueryParam("region")))
	if p.Region == "" {
		p.Region = "JP"
	}
	if len(p.Region) != 2 {
		return echo.NewHTTPError(400, "region must be a two-letter country code")
	}
	p.Status = strings.ToLower(strings.TrimSpace(c.QueryParam("status")))
	if p.Status == "" {
		p.Status = "all"
	}
	if p.Status == "sold" {
		p.Status = "completed"
	}
	if p.Status != "all" && p.Status != "active" && p.Status != "completed" {
		return echo.NewHTTPError(400, "status must be all, active, or completed")
	}
	p.Format = strings.TrimSpace(c.QueryParam("format"))
	publicationType, err := parsePublicationType(c)
	if err != nil {
		return err
	}
	p.PublicationType = publicationType
	if p.Format != "" && p.Format != "physical" && p.Format != "digital" {
		return echo.NewHTTPError(400, "format must be physical or digital")
	}
	if p.Page > 1000000 {
		return echo.NewHTTPError(400, "page is too large")
	}
	p.Source = strings.TrimSpace(c.QueryParam("source"))
	if p.CursorMode {
		p.Sort = strings.TrimSpace(c.QueryParam("sort"))
		if p.Sort == "" {
			p.Sort = "observed"
		}
		if p.Sort != "observed" && p.Sort != "title" {
			return echo.NewHTTPError(400, "sort must be observed or title")
		}
		cursor, err := decodeMarketplaceListingsCursor(c.QueryParam("cursor"), p.Sort)
		if err != nil {
			return echo.NewHTTPError(400, "cursor must be a valid marketplace cursor")
		}
		if cursor != nil {
			p.CursorID = cursor.ID
			p.CursorTitle = cursor.Title
			p.CursorObservedAt = &cursor.ObservedAt
		}
		limit := min(parsePositiveInt(c.QueryParam("limit"), 24), 50)
		p.PageSize = limit + 1
	}
	items, total, err := h.service.MarketplaceListings(c.Request().Context(), p)
	if err != nil {
		return echo.NewHTTPError(500, "failed to load marketplace listings")
	}
	if h.ImageSigner != nil {
		for i := range items {
			items[i].ImageURL = h.ImageSigner.ListingImageURL(items[i].ImageURL)
		}
	}
	if p.CursorMode {
		limit := p.PageSize - 1
		hasMore := len(items) > limit
		if hasMore {
			items = items[:limit]
		}
		var nextCursor any
		if hasMore {
			last := items[len(items)-1]
			title := last.Title
			if last.WorkTitle != "" {
				title = last.WorkTitle
			}
			nextCursor = encodeMarketplaceListingsCursor(marketplaceListingsCursor{Sort: p.Sort, ID: last.ID, Title: title, ObservedAt: last.ObservedAt})
		}
		return c.JSON(http.StatusOK, map[string]any{"items": items, "total": total, "hasMore": hasMore, "nextCursor": nextCursor})
	}
	return catalogPage(c, items, total, p)
}

type marketplaceListingsCursor struct {
	Sort       string    `json:"sort"`
	ID         string    `json:"id"`
	Title      string    `json:"title,omitempty"`
	ObservedAt time.Time `json:"observedAt,omitempty"`
}

func decodeMarketplaceListingsCursor(raw, sort string) (*marketplaceListingsCursor, error) {
	if strings.TrimSpace(raw) == "" {
		return nil, nil
	}
	if len(raw) > 2048 {
		return nil, errors.New("invalid cursor")
	}
	data, err := base64.RawURLEncoding.DecodeString(raw)
	if err != nil {
		return nil, err
	}
	var cursor marketplaceListingsCursor
	if err := json.Unmarshal(data, &cursor); err != nil || cursor.ID == "" || cursor.Sort != sort || cursor.ObservedAt.IsZero() {
		return nil, errors.New("invalid cursor")
	}
	return &cursor, nil
}

func encodeMarketplaceListingsCursor(cursor marketplaceListingsCursor) string {
	data, _ := json.Marshal(cursor)
	return base64.RawURLEncoding.EncodeToString(data)
}

func (h *CatalogBrowseHandler) Profile(c echo.Context) error {
	p := browseQuery(c)
	p.Page = 1
	p.PageSize = 1
	p.Kind = "model"
	if strings.HasPrefix(c.Path(), "/v1/publishers") {
		p.Kind = "publisher"
	}
	entries, _, err := h.service.Directory(c.Request().Context(), p)
	if err != nil {
		return echo.NewHTTPError(500, "failed to load catalog profile")
	}
	if len(entries) == 0 {
		return echo.NewHTTPError(404, "directory entry not found")
	}
	return c.JSON(http.StatusOK, entries[0])
}
