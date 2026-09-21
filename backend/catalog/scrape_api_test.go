package catalog

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
		if err := validateSourceURL(source, raw); err != nil {
			t.Fatalf("expected URL %q to be allowed: %v", raw, err)
		}
	}
	for _, raw := range []string{
		"http://169.254.169.254/latest/meta-data",
		"https://example.com.evil.test/item",
		"javascript:alert(1)",
	} {
		if err := validateSourceURL(source, raw); err == nil {
			t.Fatalf("expected URL %q to be rejected", raw)
		}
	}
}

func TestScrapeObservationIDIsStable(t *testing.T) {
	first := scrapeObservationID("ebay", "item-1", "job-1", "")
	second := scrapeObservationID("ebay", "item-1", "job-1", "")
	if first == "" || first != second {
		t.Fatalf("observation key is not stable: %q %q", first, second)
	}
	if first == scrapeObservationID("ebay", "item-1", "job-2", "") {
		t.Fatal("different jobs should produce different fallback observation keys")
	}
}

func TestRetryDelayIsBounded(t *testing.T) {
	if retryDelay(1) != 15*time.Second {
		t.Fatalf("unexpected first retry delay: %s", retryDelay(1))
	}
	if retryDelay(20) != 960*time.Second {
		t.Fatalf("unexpected capped retry delay: %s", retryDelay(20))
	}
}

func TestValidateObservationFormat(t *testing.T) {
	physicalSource := Source{DefaultFormat: "physical", AllowedFormats: "physical"}
	format, access, err := validateObservationFormat(physicalSource, "", "")
	if err != nil || format != "physical" || access != "" {
		t.Fatalf("unexpected physical result: format=%q access=%q err=%v", format, access, err)
	}

	digitalSource := Source{Kind: "digital_store", AllowedFormats: "digital"}
	format, access, err = validateObservationFormat(digitalSource, "digital", "authorized_store")
	if err != nil || format != "digital" || access != "authorized_store" {
		t.Fatalf("unexpected digital result: format=%q access=%q err=%v", format, access, err)
	}
	if _, _, err := validateObservationFormat(Source{Kind: "marketplace"}, "digital", "pirated"); err == nil {
		t.Fatal("expected unauthorized digital content to be rejected")
	}
}

func TestSourceSupportsOperation(t *testing.T) {
	source := Source{Capabilities: "catalog_discovery,active_discovery,sold_discovery,listing_detail"}
	for _, operation := range []string{"catalog_discovery", "active_discovery", "sold_discovery", "listing_detail"} {
		if !sourceSupportsOperation(source, operation) {
			t.Fatalf("expected source to support %s", operation)
		}
	}
	if sourceSupportsOperation(source, "listing_reconcile") {
		t.Fatal("did not expect unsupported operation")
	}
	if !sourceSupportsOperation(Source{}, "sold_discovery") {
		t.Fatal("legacy source without capabilities should remain usable")
	}
}
