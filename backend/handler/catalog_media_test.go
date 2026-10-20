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

func TestMediaRedirectSignsR2Sources(t *testing.T) {
	signer, err := storage.NewMediaSigner(storage.MediaConfig{
		LegacyBaseURLs: []string{"https://img.example.test"},
		MediaBaseURL:   "https://media.example.test",
		SigningSecret:  strings.Repeat("s", 32),
	})
	if err != nil {
		t.Fatal(err)
	}
	h := &MediaRedirectHandler{Signer: signer}

	response := redirectMedia(t, h, "https://img.example.test/musebooks/covers/a.jpg")
	if response.Code != http.StatusTemporaryRedirect || !strings.HasPrefix(response.Header().Get("Location"), "https://media.example.test/musebooks/covers/a.jpg?exp=") {
		t.Fatalf("got %d %q", response.Code, response.Header().Get("Location"))
	}
	if got := response.Header().Get("Cache-Control"); got != "public, max-age=28800" {
		t.Fatalf("Cache-Control = %q", got)
	}

	if response := redirectMedia(t, h, "https://evil.example/a.jpg"); response.Code != http.StatusNotFound {
		t.Fatalf("foreign source got %d, want 404", response.Code)
	}
	if response := redirectMedia(t, &MediaRedirectHandler{}, "https://img.example.test/musebooks/covers/a.jpg"); response.Code != http.StatusNotFound {
		t.Fatalf("unconfigured signer got %d, want 404", response.Code)
	}
}
