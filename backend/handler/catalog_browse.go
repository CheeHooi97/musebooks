package handler

import (
	"github.com/labstack/echo/v4"
	"musebooks/model"
	"musebooks/service"
	"net/http"
	"strconv"
	"strings"
)

type CatalogBrowseHandler struct{ service *service.CatalogService }

func NewCatalogBrowseHandler(s *service.CatalogService) *CatalogBrowseHandler {
	return &CatalogBrowseHandler{service: s}
}
func browseQuery(c echo.Context) model.CatalogBrowseQuery {
	return model.CatalogBrowseQuery{Query: strings.TrimSpace(c.QueryParam("q")), ID: c.Param("id"), Page: parsePositiveInt(c.QueryParam("page"), 1), PageSize: min(parsePositiveInt(c.QueryParam("pageSize"), 24), 50)}
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
