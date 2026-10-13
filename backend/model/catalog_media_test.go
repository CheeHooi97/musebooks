package model

import (
	"gorm.io/gorm/schema"
	"sync"
	"testing"
)

func TestBrowseResponseGalleryIsNotDatabaseAssociation(t *testing.T) {
	for _, response := range []any{&MarketEntry{}, &ListingResponse{}} {
		if _, err := schema.Parse(response, &sync.Map{}, schema.NamingStrategy{}); err != nil {
			t.Fatalf("browse response schema rejected: %v", err)
		}
	}
}

func TestPublicGalleryPreservesAttributionAndRejectsUnsafeURLs(t *testing.T) {
	assets := []CatalogMedia{
		{EntityType: "edition", EntityID: "book", StorageURL: "https://publisher.example/sample.jpg", OriginalURL: "https://publisher.example/sample.jpg", SourceURL: "https://publisher.example/book", MediaType: "publisher_sample_001"},
		{StorageURL: "javascript:alert(1)", SourceURL: "https://publisher.example/book"},
		{StorageURL: "https://publisher.example/other.jpg", SourceURL: ""},
	}
	gallery := (Edition{Media: assets}).Response().Gallery
	if len(gallery) != 1 || gallery[0].SourceURL != assets[0].SourceURL || gallery[0].MediaType != "publisher_sample_001" {
		t.Fatalf("unexpected public gallery: %+v", gallery)
	}
	if got := (Listing{Media: assets}).Response().Gallery; len(got) != 1 {
		t.Fatalf("listing gallery lost or unsafe assets included: %+v", got)
	}
}
