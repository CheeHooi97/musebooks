package model

import (
	"net/url"
	"strings"
)

const (
	MediaPermissionUnreviewed     = "unreviewed"
	MediaPermissionRevoked        = "revoked"
	MediaPermissionRemoteDisplay  = "remote_display"
	MediaPermissionDisplayAndCopy = "display_and_copy"
)

func validPublicMediaURL(raw string) bool {
	parsed, err := url.Parse(strings.TrimSpace(raw))
	return err == nil && parsed.Scheme == "https" && parsed.Host != "" && parsed.User == nil
}

// PublicMediaURL returns an image only when its exact asset has a reviewed
// permission record covering the delivery method MuseBooks will use.
func PublicMediaURL(asset CatalogMedia) string {
	if asset.PermissionReviewedAt == nil || asset.PermissionReviewedAt.IsZero() ||
		!validPublicMediaURL(asset.SourceURL) || !validPublicMediaURL(asset.PermissionEvidenceURL) ||
		!validPublicMediaURL(asset.OriginalURL) || !validPublicMediaURL(asset.StorageURL) {
		return ""
	}
	switch asset.PermissionScope {
	case MediaPermissionRemoteDisplay:
		// This scope permits displaying only the exact remote image. It cannot
		// authorize a mirrored copy, resized Worker response, or thumbnail. A
		// configured R2 URL may still be signed for direct delivery of that URL.
		if asset.OriginalURL != asset.StorageURL {
			return ""
		}
		return ApprovedImageURL(asset.OriginalURL, asset.PermissionScope)
	case MediaPermissionDisplayAndCopy:
		return ApprovedImageURL(asset.StorageURL, asset.PermissionScope)
	default:
		return ""
	}
}

// ApprovedImageURL applies response-time URL handling after a repository has
// selected an asset whose permission scope and evidence passed its query.
func ApprovedImageURL(raw, scope string) string {
	if !validPublicMediaURL(raw) || IsWarningCover(raw) {
		return ""
	}
	switch scope {
	case MediaPermissionRemoteDisplay:
		return PublicCoverURL(raw)
	case MediaPermissionDisplayAndCopy:
		return PublicCoverURL(raw)
	default:
		return ""
	}
}

func permittedPrimaryCover(media []CatalogMedia, canonicalURL string) string {
	for _, asset := range media {
		if !asset.IsPrimary || (asset.MediaType != "cover" && asset.MediaType != "publisher_cover") {
			continue
		}
		if canonicalURL != "" && canonicalURL != asset.StorageURL && canonicalURL != asset.OriginalURL {
			continue
		}
		if imageURL := PublicMediaURL(asset); imageURL != "" {
			return imageURL
		}
	}
	return ""
}
