package main

import (
	"musebooks/model"
	"testing"
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
