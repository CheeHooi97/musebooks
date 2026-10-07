package model

import (
	"testing"
	"time"
)

func TestValidateSourceURL(t *testing.T) {
	source := Source{
		BaseURL:      "https://www.example.com",
		AllowedHosts: "www.example.com,api.example.com",
	}
	for _, raw := range []string{
		"https://www.example.com/search?q=photobook",
		"https://api.example.com/v1/items",
	} {
		if err := ValidateSourceURL(source, raw); err != nil {
			t.Fatalf("expected URL %q to be allowed: %v", raw, err)
		}
	}
	for _, raw := range []string{
		"http://169.254.169.254/latest/meta-data",
		"https://example.com.evil.test/item",
		"javascript:alert(1)",
	} {
		if err := ValidateSourceURL(source, raw); err == nil {
			t.Fatalf("expected URL %q to be rejected", raw)
		}
	}
}

func TestSoldRequestsRequireAnExplicitPublicSurface(t *testing.T) {
	for _, sourceID := range []string{"yahoo-tw", "rakuma", "yahoo-furima-jp"} {
		if err := ValidateExplicitSoldRequest(sourceID, "sold_discovery", map[string]any{"query": "寫真集"}); err == nil {
			t.Fatalf("%s accepted an unverified keyword sold-history route", sourceID)
		}
		for _, field := range []string{"url", "searchUrl"} {
			if err := ValidateExplicitSoldRequest(sourceID, "sold_discovery", map[string]any{field: "https://example.test/closed"}); err != nil {
				t.Fatalf("explicit %s should proceed to the existing source URL validation: %v", field, err)
			}
		}
	}
	if err := ValidateExplicitSoldRequest("ruten-tw", "sold_discovery", map[string]any{"query": "寫真集"}); err != nil {
		t.Fatal(err)
	}
	if err := ValidateExplicitSoldRequest("ebay", "sold_discovery", map[string]any{"query": "photobook"}); err != nil {
		t.Fatal(err)
	}
}

func TestScrapeObservationIDIsStable(t *testing.T) {
	first := ScrapeObservationID("ebay", "item-1", "job-1", "")
	second := ScrapeObservationID("ebay", "item-1", "job-1", "")
	if first == "" || first != second {
		t.Fatalf("observation key is not stable: %q %q", first, second)
	}
	if first == ScrapeObservationID("ebay", "item-1", "job-2", "") {
		t.Fatal("different jobs should produce different fallback observation keys")
	}
}

func TestRetryDelayIsBounded(t *testing.T) {
	if RetryDelay(1) != 15*time.Second {
		t.Fatalf("unexpected first retry delay: %s", RetryDelay(1))
	}
	if RetryDelay(20) != 960*time.Second {
		t.Fatalf("unexpected capped retry delay: %s", RetryDelay(20))
	}
}

func TestValidateObservationFormat(t *testing.T) {
	physicalSource := Source{DefaultFormat: "physical", AllowedFormats: "physical"}
	format, access, err := ValidateObservationFormat(physicalSource, "", "")
	if err != nil || format != "physical" || access != "" {
		t.Fatalf("unexpected physical result: format=%q access=%q err=%v", format, access, err)
	}

	digitalSource := Source{Kind: "digital_store", AllowedFormats: "digital"}
	format, access, err = ValidateObservationFormat(digitalSource, "digital", "authorized_store")
	if err != nil || format != "digital" || access != "authorized_store" {
		t.Fatalf("unexpected digital result: format=%q access=%q err=%v", format, access, err)
	}
	if _, _, err := ValidateObservationFormat(Source{Kind: "marketplace"}, "digital", "pirated"); err == nil {
		t.Fatal("expected unauthorized digital content to be rejected")
	}

	physicalBookstore := Source{Kind: "bookstore", DefaultFormat: "physical", AllowedFormats: "physical"}
	format, _, err = ValidateObservationFormat(physicalBookstore, "physical", "")
	if err != nil || format != "physical" {
		t.Fatalf("physical bookstore should accept print listings: format=%q err=%v", format, err)
	}
	if _, _, err := ValidateObservationFormat(physicalBookstore, "digital", "authorized_store"); err == nil {
		t.Fatal("physical-only bookstore should reject digital listings")
	}
	if got := SourcePhotobookFormat(Source{Kind: "bookstore", AllowedFormats: "physical"}); got != "physical" {
		t.Fatalf("expected physical format from bookstore allowedFormats, got %q", got)
	}
}

func TestSourceSupportsOperation(t *testing.T) {
	source := Source{Capabilities: "catalog_discovery,active_discovery,sold_discovery,listing_detail"}
	for _, operation := range []string{"catalog_discovery", "active_discovery", "sold_discovery", "listing_detail"} {
		if !SourceSupportsOperation(source, operation) {
			t.Fatalf("expected source to support %s", operation)
		}
	}
	if SourceSupportsOperation(source, "listing_reconcile") {
		t.Fatal("did not expect unsupported operation")
	}
	if !SourceSupportsOperation(Source{}, "sold_discovery") {
		t.Fatal("legacy source without capabilities should remain usable")
	}
}

func TestDigitalRetailPolicy(t *testing.T) {
	for _, id := range []string{"bookwalker-tw", "readmoo-tw", "books-com-tw", "pubu-tw", "kobo-tw", "hami-tw", "google-play-books-tw", "apple-books-tw", "apple-books-us", "hyread-tw", "momo-books-tw", "pchome-books-tw", "yahoo-shopping-books-tw", "kingstone-books-tw", "taaze-books-tw", "sanmin-books-tw", "rakuten-kobo-tw", "fan520-tw"} {
		source := Source{ID: id, Kind: "digital_store"}
		if IsRetailScrapeSource(source) {
			t.Fatalf("digital store %s is excluded", id)
		}
		if err := ValidateDigitalRetailRequest(source, "active_discovery", map[string]any{"format": "digital"}); err != nil {
			t.Fatal(err)
		}
		for _, request := range []struct {
			op     string
			format string
		}{{"sold_discovery", "digital"}, {"active_discovery", "physical"}} {
			if ValidateDigitalRetailRequest(source, request.op, map[string]any{"format": request.format}) == nil {
				t.Fatalf("accepted unsupported retail request: %+v", request)
			}
		}
	}
	if !IsRetailScrapeSource(Source{ID: "rakuten-books-jp", Kind: "bookstore"}) {
		t.Fatal("physical retail exclusion was lost")
	}
}
