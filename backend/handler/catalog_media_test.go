package handler

import (
	"musebooks/storage"
	"net/http"
	"net/http/httptest"
	"net/url"
	"strings"
	"testing"

	"github.com/labstack/echo/v4"
)

func redirectMedia(t *testing.T, h *MediaRedirectHandler, source string) *httptest.ResponseRecorder {
	t.Helper()
	request := httptest.NewRequest(http.MethodGet, "/v1/catalog/media/redirect?"+url.Values{"source": {source}}.Encode(), nil)
	recorder := httptest.NewRecorder()
	if err := h.Redirect(echo.New().NewContext(request, recorder)); err != nil {
		t.Fatalf("Redirect() error = %v", err)
	}
	return recorder
}

func TestMediaRedirectRequiresCatalogPermission(t *testing.T) {
	signer, err := storage.NewMediaSigner(storage.MediaConfig{
		LegacyBaseURLs: []string{"https://img.example.test"},
		MediaBaseURL:   "https://media.example.test",
		SigningSecret:  strings.Repeat("s", 32),
	})
	if err != nil {
		t.Fatal(err)
	}
	h := &MediaRedirectHandler{Signer: signer}

	if response := redirectMedia(t, h, "https://img.example.test/musebooks/covers/a.jpg"); response.Code != http.StatusNotFound {
		t.Fatalf("source with no catalog permission record got %d", response.Code)
	}

	if response := redirectMedia(t, h, "https://evil.example/a.jpg"); response.Code != http.StatusNotFound {
		t.Fatalf("foreign source got %d, want 404", response.Code)
	}
	if response := redirectMedia(t, &MediaRedirectHandler{}, "https://img.example.test/musebooks/covers/a.jpg"); response.Code != http.StatusNotFound {
		t.Fatalf("unconfigured signer got %d, want 404", response.Code)
	}
}
