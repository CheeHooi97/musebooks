package model

import "testing"

func TestPhotobookPriceBoundary(t *testing.T) {
	market := Source{ID: "ruten-tw", Kind: "marketplace", AllowedFormats: "physical,digital"}
	store := Source{ID: "readmoo-tw", Kind: "digital_store"}
	physicalStore := Source{ID: "sanmin-print-tw", Kind: "bookstore", DefaultFormat: "physical", AllowedFormats: "physical"}
	for _, tc := range []struct {
		source Source
		format string
	}{{market, "digital"}, {store, "physical"}} {
		if _, _, err := ValidateObservationFormat(tc.source, tc.format, "authorized_store"); err == nil {
			t.Fatal("accepted cross-format observation")
		}
		if err := ValidateDigitalRetailRequest(tc.source, "active_discovery", map[string]any{"format": tc.format}); err == nil {
			t.Fatal("accepted cross-format job")
		}
	}
	if _, err := ValidateObservationPrice("digital", "completed", "digital"); err == nil {
		t.Fatal("accepted a digital sold transaction")
	}
	if _, err := ValidateObservationPrice("physical", "active", "digital"); err == nil {
		t.Fatal("accepted a retail price for paper")
	}
	listings := []Listing{
		{ID: "asking", Source: market, FormatCandidate: "physical", Status: "active", PriceType: "fixed"},
		{ID: "sold", Source: market, FormatCandidate: "physical", Status: "completed", PriceType: "fixed"},
		{ID: "retail", Source: store, FormatCandidate: "digital", Status: "active", PriceType: "digital"},
		{ID: "wrong-source", Source: store, FormatCandidate: "physical", Status: "active", PriceType: "fixed"},
		{ID: "false-sold", Source: store, FormatCandidate: "digital", Status: "completed", PriceType: "digital"},
		{ID: "print-retail", Source: physicalStore, FormatCandidate: "physical", Status: "active", PriceType: "fixed"},
	}
	physical := (Edition{Format: "physical", Listings: listings}).Response()
	digital := (Edition{Format: "digital", Listings: listings}).Response()
	if len(physical.Listings) != 3 || len(physical.ActiveListings) != 1 || len(physical.SoldListings) != 1 || len(physical.RetailOffers) != 1 {
		t.Fatalf("mixed physical response: %+v", physical)
	}
	if physical.RetailOffers[0].PriceCategory != "physical_retail" || physical.RetailOffers[0].Source.ID != "sanmin-print-tw" {
		t.Fatalf("physical retailer was misclassified: %+v", physical.RetailOffers[0])
	}
	if len(digital.Listings) != 1 || len(digital.RetailOffers) != 1 || len(digital.SoldListings) != 0 || len(digital.ActiveListings) != 0 {
		t.Fatalf("mixed digital response: %+v", digital)
	}
}
