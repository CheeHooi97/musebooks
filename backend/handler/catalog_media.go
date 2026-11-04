package handler

import (
	"fmt"
	"musebooks/model"
	"musebooks/storage"
	"net/http"
	"net/url"
	"strings"
	"time"

	"github.com/labstack/echo/v4"
	"gorm.io/gorm"
)

// MediaRedirectHandler gives prerendered pages and social previews an image
// URL that never expires: each request is redirected to the media Worker URL
// signed for the current window.
type MediaRedirectHandler struct {
	Signer *storage.MediaSigner
	DB     *gorm.DB
}

func (h *MediaRedirectHandler) approvedStorageSource(raw string) bool {
	if h == nil || h.Signer == nil || h.DB == nil {
		return false
	}
	parsed, err := url.Parse(strings.TrimSpace(raw))
	if err != nil || parsed.Path == "" {
		return false
	}
	if _, ok := h.Signer.Sign(raw, time.Now()); !ok {
		return false
	}
	path := parsed.EscapedPath()
	assets := []model.CatalogMedia{}
	if err := h.DB.Where(`permission_scope IN ? AND permission_reviewed_at IS NOT NULL
	AND permission_evidence_url LIKE 'https://%' AND source_url LIKE 'https://%'
	AND original_url LIKE 'https://%' AND storage_url LIKE 'https://%'
	AND (permission_scope = ? OR original_url = storage_url)
	AND right(split_part(storage_url, '?', 1), char_length(?)) = ?`,
		[]string{model.MediaPermissionRemoteDisplay, model.MediaPermissionDisplayAndCopy}, model.MediaPermissionDisplayAndCopy, path, path).Find(&assets).Error; err != nil {
		return false
	}
	for _, asset := range assets {
		if model.PublicMediaURL(asset) == "" {
			continue
		}
		signedAsset, ok := h.Signer.Sign(asset.StorageURL, time.Now())
		if !ok {
			continue
		}
		assetURL, err := url.Parse(signedAsset)
		if err == nil && strings.EqualFold(assetURL.Host, parsed.Host) && assetURL.EscapedPath() == path {
			return true
		}
	}
	return false
}

func (h *MediaRedirectHandler) Redirect(c echo.Context) error {
	var signer *storage.MediaSigner
	if h != nil {
		signer = h.Signer
	}
	source := strings.TrimSpace(c.QueryParam("source"))
	if h == nil || !h.approvedStorageSource(source) {
		// The redirect is limited to exact media assets approved for display; a
		// valid Worker signature alone is not permission evidence.
		return c.NoContent(http.StatusNotFound)
	}
	target, ok := signer.Sign(source, time.Now())
	if !ok {
		return c.NoContent(http.StatusNotFound)
	}
	// A cached redirect must never outlive the signature it points to.
	c.Response().Header().Set("Cache-Control", fmt.Sprintf("public, max-age=%d", int(signer.Window().Seconds())/3))
	return c.Redirect(http.StatusTemporaryRedirect, target)
}
