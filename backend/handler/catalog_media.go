package handler

import (
	"fmt"
	"musebooks/storage"
	"net/http"
	"strings"
	"time"

	"github.com/labstack/echo/v4"
)

// MediaRedirectHandler gives prerendered pages and social previews an image
// URL that never expires: each request is redirected to the media Worker URL
// signed for the current window.
type MediaRedirectHandler struct{ Signer *storage.MediaSigner }

func (h *MediaRedirectHandler) Redirect(c echo.Context) error {
	var signer *storage.MediaSigner
	if h != nil {
		signer = h.Signer
	}
	target, ok := signer.Sign(strings.TrimSpace(c.QueryParam("source")), time.Now())
	if !ok {
		// Only R2 sources are accepted, so this is never an open redirect.
		return c.NoContent(http.StatusNotFound)
	}
	// A cached redirect must never outlive the signature it points to.
	c.Response().Header().Set("Cache-Control", fmt.Sprintf("public, max-age=%d", int(signer.Window().Seconds())/3))
	return c.Redirect(http.StatusTemporaryRedirect, target)
}
