package worker

import (
	"testing"
	"time"
)

func TestNormalizeAnchor(t *testing.T) {
	item, ok := normalizeAnchor(
		"/listing/123",
		"https://example.com/search?q=photobook",
		"Alice Smith model photobook JPY 12,800",
		time.Date(2026, 9, 13, 10, 0, 0, 0, time.UTC),
	)
	if !ok {
		t.Fatal("expected photobook listing to be accepted")
	}
	if item.URL != "https://example.com/listing/123" {
		t.Fatalf("unexpected URL: %s", item.URL)
	}
	if item.Currency != "JPY" || item.PriceMinor != 12800 {
		t.Fatalf("unexpected price: %s %d", item.Currency, item.PriceMinor)
	}
	if item.Format != "physical" {
		t.Fatalf("expected physical format, got %q", item.Format)
	}
}

func TestNormalizeAnchorRejectsNonBooks(t *testing.T) {
	if _, ok := normalizeAnchor(
		"https://example.com/item",
		"https://example.com",
		"Vintage camera JPY 12,800",
		time.Now(),
	); ok {
		t.Fatal("expected non-photobook listing to be rejected")
	}
}

func TestNormalizeAnchorDetectsDigitalAndRejectsMerchandise(t *testing.T) {
	digital, ok := normalizeAnchor(
		"/ebook/123",
		"https://example.com",
		"Alice Smith model authorized digital photobook PDF JPY 880",
		time.Now(),
	)
	if !ok || digital.Format != "digital" {
		t.Fatalf("expected digital photobook, got ok=%v format=%q", ok, digital.Format)
	}
	if _, ok := normalizeAnchor(
		"/item/card-123",
		"https://example.com",
		"Photobook trading card set JPY 880",
		time.Now(),
	); ok {
		t.Fatal("expected trading-card merchandise to be rejected")
	}
}

func TestNormalizeAnchorRejectsPhotographerBooks(t *testing.T) {
	if _, ok := normalizeAnchor(
		"https://example.com/item/photographer-book",
		"https://example.com",
		"Rare photographer photobook JPY 12,800",
		time.Now(),
	); ok {
		t.Fatal("expected photographer-led photobook to be rejected")
	}
}

func TestNormalizeAnchorRejectsNonHumanModelCatalogs(t *testing.T) {
	if _, ok := normalizeAnchor(
		"https://example.com/item/scale-model",
		"https://example.com",
		"Scale model photobook catalog JPY 12,800",
		time.Now(),
	); ok {
		t.Fatal("expected scale-model catalog to be rejected")
	}
}
