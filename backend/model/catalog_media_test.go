package model

import (
	"gorm.io/gorm/schema"
	"sync"
	"testing"
	"time"
)

func TestBrowseResponseGalleryIsNotDatabaseAssociation(t *testing.T) {
	for _, response := range []any{&MarketEntry{}, &ListingResponse{}} {
		if _, err := schema.Parse(response, &sync.Map{}, schema.NamingStrategy{}); err != nil {
			t.Fatalf("browse response schema rejected: %v", err)
		}
	}
}

func TestPublicGalleryRequiresExactAssetPermission(t *testing.T) {
	reviewedAt := time.Date(2026, time.November, 1, 0, 0, 0, 0, time.UTC)
	assets := []CatalogMedia{
		{EntityType: "edition", EntityID: "book", StorageURL: "https://publisher.example/sample.jpg", OriginalURL: "https://publisher.example/sample.jpg", SourceURL: "https://publisher.example/book", PermissionScope: MediaPermissionRemoteDisplay, PermissionEvidenceURL: "https://publisher.example/terms", PermissionBasis: "Terms permit remote product image display", PermissionReviewedAt: &reviewedAt, MediaType: "publisher_sample_001"},
		{EntityType: "edition", EntityID: "book", StorageURL: "https://publisher.example/unreviewed.jpg", OriginalURL: "https://publisher.example/unreviewed.jpg", SourceURL: "https://publisher.example/book", MediaType: "publisher_sample_002"},
		{StorageURL: "javascript:alert(1)", SourceURL: "https://publisher.example/book"},
		{StorageURL: "https://publisher.example/other.jpg", SourceURL: ""},
	}
	gallery := (Edition{Media: assets}).Response().Gallery
	if len(gallery) != 1 || gallery[0].SourceURL != assets[0].SourceURL || gallery[0].MediaType != "publisher_sample_001" {
		t.Fatalf("unexpected public gallery: %+v", gallery)
	}
	if gallery[0].StorageURL != assets[0].OriginalURL {
		t.Fatalf("remote display scope changed the image URL: %+v", gallery[0])
	}
	if got := (Listing{Media: assets}).Response().Gallery; len(got) != 1 {
		t.Fatalf("listing gallery lost or unsafe assets included: %+v", got)
	}
}

func TestPublicDisplayAndCopyUsesApprovedStorageAndCover(t *testing.T) {
	reviewedAt := time.Date(2026, time.November, 1, 0, 0, 0, 0, time.UTC)
	asset := CatalogMedia{EntityType: "edition", EntityID: "book", MediaType: "publisher_cover", IsPrimary: true,
		OriginalURL: "https://publisher.example/cover.jpg", StorageURL: "https://media.musebooks.example/covers/book.jpg", SourceURL: "https://publisher.example/book",
		PermissionScope: MediaPermissionDisplayAndCopy, PermissionEvidenceURL: "https://publisher.example/terms", PermissionBasis: "Written approval allows storage and public display", PermissionReviewedAt: &reviewedAt}
	if got := PublicMediaURL(asset); got != asset.StorageURL {
		t.Fatalf("PublicMediaURL() = %q, want approved storage URL %q", got, asset.StorageURL)
	}
	if got := permittedPrimaryCover([]CatalogMedia{asset}, asset.StorageURL); got != asset.StorageURL {
		t.Fatalf("permittedPrimaryCover() = %q, want %q", got, asset.StorageURL)
	}
	if got := permittedPrimaryCover([]CatalogMedia{asset}, "https://publisher.example/other.jpg"); got != "" {
		t.Fatalf("mismatched canonical cover was exposed: %q", got)
	}
	asset.PermissionScope = MediaPermissionRemoteDisplay
	asset.StorageURL = "https://media.musebooks.example/covers/changed.jpg"
	if got := PublicMediaURL(asset); got != "" {
		t.Fatalf("remote-only scope permitted a copied URL: %q", got)
	}
}
