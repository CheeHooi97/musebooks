package handler

import (
	"github.com/labstack/echo/v4"
	"net/http/httptest"
	"strings"
	"testing"
)

func TestListingFiltersRejectInvalidInputsBeforePersistence(t *testing.T) {
	for _, query := range []string{"status=ended", "format=poster", "page=1000001"} {
		e := echo.New()
		c := e.NewContext(httptest.NewRequest("GET", "/v1/listings?"+query, nil), httptest.NewRecorder())
		err := NewCatalogBrowseHandler(nil).Listings(c)
		httpErr, ok := err.(*echo.HTTPError)
		if !ok || httpErr.Code != 400 {
			t.Fatalf("%s: expected 400, got %v", query, err)
		}
	}
}

func TestDirectoryFiltersRejectInvalidInputsBeforePersistence(t *testing.T) {
	for _, query := range []string{"format=poster", "year=abc", "year=999", "page=1000001"} {
		e := echo.New()
		c := e.NewContext(httptest.NewRequest("GET", "/v1/publishers/press/books?"+query, nil), httptest.NewRecorder())
		c.SetPath("/v1/publishers/:id/books")
		err := NewCatalogBrowseHandler(nil).DirectoryBooks(c)
		httpErr, ok := err.(*echo.HTTPError)
		if !ok || httpErr.Code != 400 {
			t.Fatalf("%s: expected 400, got %v", query, err)
		}
	}
}

func TestMarketplaceModelFiltersRejectInvalidInputsBeforePersistence(t *testing.T) {
	queries := []string{
		"model=",
		"model=" + strings.Repeat("x", 129),
		strings.Repeat("model=slug&", 101),
	}
	for _, query := range queries {
		e := echo.New()
		c := e.NewContext(httptest.NewRequest("GET", "/v1/marketplace-listings?"+query, nil), httptest.NewRecorder())
		err := NewCatalogBrowseHandler(nil).MarketplaceListings(c)
		httpErr, ok := err.(*echo.HTTPError)
		if !ok || httpErr.Code != 400 {
			t.Fatalf("%s: expected 400, got %v", query, err)
		}
	}
}
