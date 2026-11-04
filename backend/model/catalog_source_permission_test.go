package model

import (
	"testing"
	"time"
)

func TestSourcePermissionRequiresActiveEvidenceAndExactUse(t *testing.T) {
	now := time.Date(2026, 11, 1, 12, 0, 0, 0, time.UTC)
	reviewed := now.Add(-time.Hour)
	effective := now.Add(-time.Hour)
	expires := now.Add(time.Hour)
	source := Source{ID: "kolis-net", Region: "KR", AccessMethod: "api", RatePerMinute: 8}
	grant := SourcePermission{
		SourceID: source.ID, Scope: SourcePermissionScopeBibliography, Status: SourcePermissionApproved,
		AccessMethod: "API", AllowedFields: "title,url,format", Purpose: "MuseBooks bibliographic indexing",
		AllowedUses: "collect,retain,catalog_display", RetentionMode: "permanent", RetentionPolicy: "retain verified bibliography",
		PublicDisplayMode: "attributed", AttributionRequired: true, AttributionText: "Source: KOLIS-NET",
		Rightsholder: "National Library of Korea", Territory: "Global",
		EvidenceURL:   "https://data.go.kr/data/3036346/openapi.do",
		RatePerMinute: 6, EffectiveAt: &effective, ExpiresAt: &expires, ReviewedAt: &reviewed,
	}
	if !grant.Allows(source, SourcePermissionScopeBibliography, []string{"title", "url"}, []string{"collect", "catalog_display"}, now) {
		t.Fatal("active grant should allow its reviewed bibliography fields and uses")
	}
	if grant.Allows(source, SourcePermissionScopeBibliography, []string{"title", "cover_image"}, []string{"collect"}, now) {
		t.Fatal("grant allowed a field outside its scope")
	}
	if grant.Allows(source, SourcePermissionScopeBibliography, []string{"title"}, []string{"collect", "redistribute"}, now) {
		t.Fatal("grant allowed redistribution without permission")
	}
	if grant.Allows(source, SourcePermissionScopeBibliography, []string{"title"}, []string{"collect"}, expires) {
		t.Fatal("expired grant remained active")
	}
	grant.RetentionMode = "temporary"
	grant.RetentionDays = 30
	if grant.Allows(source, SourcePermissionScopeBibliography, []string{"title"}, []string{"collect", "retain"}, now) {
		t.Fatal("temporary-cache grant authorized durable catalog retention")
	}
	grant.RetentionMode = "permanent"
	grant.Status = SourcePermissionPending
	if grant.Allows(source, SourcePermissionScopeBibliography, []string{"title"}, []string{"collect"}, now) {
		t.Fatal("pending grant authorized collection")
	}
}

func TestKoreanSourcePermissionScopes(t *testing.T) {
	if !RequiresSourcePermission(Source{Region: "kr"}) || RequiresSourcePermission(Source{Region: "JP"}) {
		t.Fatal("Korean-source gate did not distinguish source regions")
	}
	for _, test := range []struct {
		operation string
		scope     string
	}{
		{"catalog_discovery", SourcePermissionScopeBibliography},
		{"active_discovery", SourcePermissionScopeCurrentPrices},
		{"listing_detail", SourcePermissionScopeCurrentPrices},
		{"sold_discovery", SourcePermissionScopeUsedPrices},
	} {
		got, fields := SourcePermissionForOperation(test.operation)
		if got != test.scope || len(fields) == 0 {
			t.Errorf("%s maps to %q with %d fields, want %q and an explicit field set", test.operation, got, len(fields), test.scope)
		}
	}
}

func TestObservationPermissionsSeparateCurrentUsedAndImageScopes(t *testing.T) {
	item := ObservationInput{Status: "active", Title: "Catalog record", URL: "https://example.test/product", PriceMinor: 9600, Currency: "KRW", ImageURL: "https://image.example/cover.jpg"}
	if got := ObservationPermissionScope(item); got != SourcePermissionScopeCurrentPrices {
		t.Fatalf("current offer mapped to scope %q", got)
	}
	if scopes := ObservationPermissionScopes(item); len(scopes) != 2 || scopes[1] != SourcePermissionScopeProductImages {
		t.Fatalf("image scope was not isolated: %v", scopes)
	}
	item.Status = "completed"
	if got := ObservationPermissionScope(item); got != SourcePermissionScopeUsedPrices {
		t.Fatalf("completed offer mapped to scope %q", got)
	}
	item.Status = "active"
	item.PriceBasis = "used_asking"
	if got := ObservationPermissionScope(item); got != SourcePermissionScopeUsedPrices {
		t.Fatalf("active used offer mapped to scope %q", got)
	}
	item.PriceBasis = ""
	item.PriceMinor = 0
	item.PriceComponents = []PriceComponent{{Basis: "used_asking", PriceMinor: 9600, Currency: "KRW"}}
	if got := ObservationPermissionScope(item); got != SourcePermissionScopeUsedPrices {
		t.Fatalf("used price component mapped to scope %q", got)
	}
}
