package handler

import (
	"github.com/labstack/echo/v4"
	"net/http/httptest"
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
