package main

import (
	"musebooks/model"
	"testing"
	"time"
)

func TestGalleryProvenanceAndPrimaryCover(t *testing.T) {
	record := Record{Batch: model.ObservationBatch{Items: []model.ObservationInput{{ExternalID: "book", URL: "https://store.example/book", ImageURL: "https://store.example/cover.jpg"}}}, Media: []ListingMediaInput{
		{ExternalID: "book", MediaType: "listing_image", OriginalURL: "https://store.example/cover.jpg", StorageURL: "https://store.example/cover.jpg", SourceURL: "https://store.example/book", IsPrimary: true},
		{ExternalID: "book", MediaType: "listing_image_001", OriginalURL: "https://store.example/sample.jpg", StorageURL: "https://store.example/sample.jpg", SourceURL: "https://store.example/book"},
	}}
	if err := validateMediaInput(record); err != nil {
		t.Fatal(err)
	}
	record.Media[1].SourceURL = "https://store.example/other"
	if validateMediaInput(record) == nil {
		t.Fatal("unrelated source attribution accepted")
	}
	record.Media[1].SourceURL = record.Batch.Items[0].URL
	record.Media[1].IsPrimary = true
	if validateMediaInput(record) == nil {
		t.Fatal("gallery incorrectly accepted as primary cover")
	}
}

func TestPublisherSamplesRequireReviewedEditionProvenance(t *testing.T) {
	record := Record{Edition: model.Edition{ID: "edition", MetadataSourceURL: "https://publisher.example/book", CoverURL: "https://publisher.example/cover.jpg"}, PublisherMedia: []ListingMediaInput{
		{MediaType: "publisher_cover", OriginalURL: "https://publisher.example/cover.jpg", StorageURL: "https://publisher.example/cover.jpg", SourceURL: "https://publisher.example/book", IsPrimary: true},
		{MediaType: "publisher_sample_001", OriginalURL: "https://publisher.example/sample.jpg", StorageURL: "https://publisher.example/sample.jpg", SourceURL: "https://publisher.example/book"},
	}}
	if err := validateMediaInput(record); err != nil {
		t.Fatal(err)
	}
	record.PublisherMedia[1].SourceURL = "https://publisher.example/other-book"
	if validateMediaInput(record) == nil {
		t.Fatal("sample from a different publisher book accepted")
	}
}

func TestWorkCoverMediaRequiresItsExactReviewedProductSource(t *testing.T) {
	record := Record{
		Work:      model.Work{ID: "work", CoverURL: "https://publisher.example/cover.jpg"},
		Edition:   model.Edition{MetadataSourceURL: "https://publisher.example/product"},
		WorkMedia: []ListingMediaInput{{MediaType: "publisher_cover", OriginalURL: "https://publisher.example/cover.jpg", StorageURL: "https://publisher.example/cover.jpg", SourceURL: "https://publisher.example/product", IsPrimary: true}},
	}
	if err := validateMediaInput(record); err != nil {
		t.Fatal(err)
	}
	record.WorkMedia[0].StorageURL = "https://publisher.example/other.jpg"
	if validateMediaInput(record) == nil {
		t.Fatal("work cover with different asset URL was accepted")
	}
}

func TestMediaPermissionScopeNeedsEvidenceAndRemoteDisplayCannotUseCopies(t *testing.T) {
	reviewedAt := time.Date(2026, time.November, 1, 0, 0, 0, 0, time.UTC)
	media := ListingMediaInput{
		MediaType: "publisher_cover", OriginalURL: "https://publisher.example/cover.jpg", StorageURL: "https://publisher.example/cover.jpg",
		SourceURL: "https://publisher.example/book", PermissionScope: model.MediaPermissionRemoteDisplay,
		PermissionEvidenceURL: "https://publisher.example/terms", PermissionBasis: "Terms permit direct image display", PermissionReviewedAt: &reviewedAt,
	}
	if err := validateMediaPermission(media); err != nil {
		t.Fatalf("valid remote-display evidence rejected: %v", err)
	}
	asset := catalogMediaFromInput("edition", "edition", media)
	if asset.PermissionScope != model.MediaPermissionRemoteDisplay || asset.PermissionEvidenceURL != media.PermissionEvidenceURL {
		t.Fatalf("permission evidence not mapped into CatalogMedia: %+v", asset)
	}
	media.StorageURL = "https://media.example/cover.jpg"
	if err := validateMediaPermission(media); err == nil {
		t.Fatal("remote-display scope accepted a different stored image URL")
	}
	media.PermissionScope = model.MediaPermissionDisplayAndCopy
	media.PermissionEvidenceURL = ""
	if err := validateMediaPermission(media); err == nil {
		t.Fatal("copy scope accepted missing permission evidence")
	}
}

func TestVerifiedFreePreviewCanBeExcludedWithoutDeletingItsObservation(t *testing.T) {
	if !validExclusionReason("free_preview") {
		t.Fatal("verified free preview should be a supported exclusion reason")
	}
	if validExclusionReason("free") {
		t.Fatal("unreviewed exclusion reason should not be accepted")
	}
}

func TestIncorrectModelAssociationIsAReviewedExclusionReason(t *testing.T) {
	if !validExclusionReason("incorrect_model_association") {
		t.Fatal("verified wrong-model marketplace capture should be excludable")
	}
}

func TestTypedCatalogDatesRequirePrecisionAndFieldSource(t *testing.T) {
	value := time.Date(2024, time.July, 19, 0, 0, 0, 0, time.UTC)
	if err := validateSourcedDate(&value, "month", "https://publisher.example/item", "publication date"); err != nil {
		t.Fatal(err)
	}
	if err := validateSourcedDate(&value, "month", "", "publication date"); err == nil {
		t.Fatal("typed date without field-level source URL accepted")
	}
	if err := validateSourcedDate(&value, "week", "https://publisher.example/item", "publication date"); err == nil {
		t.Fatal("unsupported date precision accepted")
	}
	value = time.Date(2024, time.July, 1, 0, 0, 0, 0, time.UTC)
	normalized := normalizeSourcedDate(&value, "year")
	if normalized.Format("2006-01-02") != "2024-01-01" {
		t.Fatalf("year-precision date not normalized: %s", normalized)
	}
}
