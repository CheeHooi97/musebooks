package model

import (
	"net/url"
	"strings"
	"time"
)

const (
	SourcePermissionScopeBibliography  = "bibliography"
	SourcePermissionScopeCurrentPrices = "current_prices"
	SourcePermissionScopeUsedPrices    = "used_prices"
	SourcePermissionScopeProductImages = "product_images"

	SourcePermissionPending  = "pending"
	SourcePermissionApproved = "approved"
	SourcePermissionDenied   = "denied"
	SourcePermissionRevoked  = "revoked"
	SourcePermissionExpired  = "expired"

	SourcePermissionUseCollect      = "collect"
	SourcePermissionUseRetain       = "retain"
	SourcePermissionUseCatalogView  = "catalog_display"
	SourcePermissionUseRedistribute = "redistribute"
)

// SourcePermission is a reviewed grant for one source and one data-use scope.
// AccessStatus on Source remains an operational switch and is not a grant.
type SourcePermission struct {
	ID                    int64      `gorm:"primaryKey;autoIncrement" json:"id"`
	SourceID              string     `gorm:"size:80;uniqueIndex:ux_source_permission_scope,priority:1;not null" json:"sourceId"`
	Scope                 string     `gorm:"size:32;uniqueIndex:ux_source_permission_scope,priority:2;not null" json:"scope"`
	Status                string     `gorm:"size:24;index;not null;default:pending" json:"status"`
	AccessMethod          string     `gorm:"size:32;not null" json:"accessMethod"`
	AllowedFields         string     `gorm:"type:text;not null" json:"allowedFields"`
	Purpose               string     `gorm:"type:text;not null" json:"purpose"`
	AllowedUses           string     `gorm:"type:text;not null" json:"allowedUses"`
	RetentionMode         string     `gorm:"size:24;not null" json:"retentionMode"`
	RetentionDays         int        `gorm:"not null;default:0" json:"retentionDays"`
	RetentionPolicy       string     `gorm:"size:80;not null" json:"retentionPolicy"`
	PublicDisplayMode     string     `gorm:"size:32;not null" json:"publicDisplayMode"`
	AttributionRequired   bool       `gorm:"not null;default:false" json:"attributionRequired"`
	AttributionText       string     `gorm:"type:text" json:"attributionText,omitempty"`
	RedistributionAllowed bool       `gorm:"not null;default:false" json:"redistributionAllowed"`
	RatePerMinute         int        `gorm:"not null;default:0" json:"ratePerMinute"`
	Rightsholder          string     `gorm:"size:180" json:"rightsholder,omitempty"`
	Territory             string     `gorm:"size:120" json:"territory,omitempty"`
	EvidenceURL           string     `gorm:"type:text;not null" json:"evidenceUrl"`
	EffectiveAt           *time.Time `json:"effectiveAt,omitempty"`
	ExpiresAt             *time.Time `json:"expiresAt,omitempty"`
	ReviewedAt            *time.Time `json:"reviewedAt,omitempty"`
	CreatedAt             time.Time  `json:"createdAt"`
	UpdatedAt             time.Time  `json:"updatedAt"`
}

func (SourcePermission) TableName() string { return "source_permissions" }

func RequiresSourcePermission(source Source) bool {
	return strings.EqualFold(strings.TrimSpace(source.Region), "KR")
}

// Allows verifies that a reviewed grant is active for this exact source scope,
// method, field set, and use. Missing or incomplete evidence always denies.
func (p SourcePermission) Allows(source Source, scope string, fields, uses []string, now time.Time) bool {
	if p.Status != SourcePermissionApproved || p.Scope != scope || p.SourceID != source.ID ||
		!strings.EqualFold(strings.TrimSpace(p.AccessMethod), strings.TrimSpace(source.AccessMethod)) ||
		p.ReviewedAt == nil || p.ReviewedAt.IsZero() || p.EffectiveAt == nil || p.EffectiveAt.After(now) ||
		(p.ExpiresAt != nil && !p.ExpiresAt.After(now)) || strings.TrimSpace(p.Purpose) == "" || p.RatePerMinute <= 0 ||
		strings.TrimSpace(p.RetentionPolicy) == "" || strings.TrimSpace(p.Rightsholder) == "" ||
		strings.TrimSpace(p.Territory) == "" || !validPublicDisplayMode(p.PublicDisplayMode) || !validSourcePermissionURL(p.EvidenceURL) {
		return false
	}
	allowedFields := stringSet(SplitCSV(p.AllowedFields))
	allowedUses := stringSet(SplitCSV(p.AllowedUses))
	for _, field := range fields {
		if _, ok := allowedFields[strings.ToLower(strings.TrimSpace(field))]; !ok {
			return false
		}
	}
	for _, use := range uses {
		if _, ok := allowedUses[strings.ToLower(strings.TrimSpace(use))]; !ok {
			return false
		}
	}
	if containsString(uses, SourcePermissionUseCatalogView) {
		switch strings.ToLower(strings.TrimSpace(p.PublicDisplayMode)) {
		case "source_linked", "attributed", "integrated":
		default:
			return false
		}
	}
	if containsString(uses, SourcePermissionUseRedistribute) && !p.RedistributionAllowed {
		return false
	}
	if containsString(uses, SourcePermissionUseRetain) && strings.ToLower(strings.TrimSpace(p.RetentionMode)) != "permanent" {
		return false
	}
	if strings.EqualFold(strings.TrimSpace(p.RetentionMode), "temporary") && p.RetentionDays <= 0 {
		return false
	}
	if p.AttributionRequired && strings.TrimSpace(p.AttributionText) == "" {
		return false
	}
	if strings.EqualFold(strings.TrimSpace(p.PublicDisplayMode), "attributed") && (!p.AttributionRequired || strings.TrimSpace(p.AttributionText) == "") {
		return false
	}
	return true
}

func validPublicDisplayMode(value string) bool {
	switch strings.ToLower(strings.TrimSpace(value)) {
	case "none", "source_linked", "attributed", "integrated", "separate_source_labeled":
		return true
	default:
		return false
	}
}

func validSourcePermissionURL(raw string) bool {
	parsed, err := url.Parse(strings.TrimSpace(raw))
	return err == nil && parsed.Scheme == "https" && parsed.Host != "" && parsed.User == nil
}

func stringSet(values []string) map[string]struct{} {
	result := make(map[string]struct{}, len(values))
	for _, value := range values {
		result[strings.ToLower(strings.TrimSpace(value))] = struct{}{}
	}
	return result
}

func containsString(values []string, wanted string) bool {
	for _, value := range values {
		if strings.EqualFold(strings.TrimSpace(value), wanted) {
			return true
		}
	}
	return false
}

func SourcePermissionForOperation(operation string) (string, []string) {
	switch strings.ToLower(strings.TrimSpace(operation)) {
	case "catalog_discovery":
		return SourcePermissionScopeBibliography, []string{"title", "url", "format"}
	case "active_discovery", "listing_detail", "listing_reconcile":
		return SourcePermissionScopeCurrentPrices, []string{"title", "url", "format", "price", "currency", "availability", "observed_at"}
	case "sold_discovery":
		return SourcePermissionScopeUsedPrices, []string{"title", "url", "format", "price", "currency", "condition", "seller_location", "shipping", "availability", "observed_at"}
	default:
		return "", nil
	}
}

func ObservationPermissionScope(item ObservationInput) string {
	status := strings.ToLower(strings.TrimSpace(item.Status))
	basis := strings.ToLower(strings.TrimSpace(item.PriceBasis))
	if status == "completed" || status == "sold" || basis == "used_asking" || basis == "completed_sale" {
		return SourcePermissionScopeUsedPrices
	}
	for _, component := range item.PriceComponents {
		componentBasis := strings.ToLower(strings.TrimSpace(component.Basis))
		if componentBasis == "used_asking" || componentBasis == "completed_sale" {
			return SourcePermissionScopeUsedPrices
		}
	}
	if item.PriceMinor != 0 || len(item.PriceComponents) > 0 || strings.TrimSpace(item.PriceType) != "" || strings.TrimSpace(item.Currency) != "" {
		return SourcePermissionScopeCurrentPrices
	}
	return SourcePermissionScopeBibliography
}

func ObservationPermissionFields(item ObservationInput) []string {
	fields := []string{"title", "url", "format", "observed_at"}
	if strings.TrimSpace(item.Status) != "" {
		fields = append(fields, "availability")
	}
	if strings.TrimSpace(item.ISBN) != "" {
		fields = append(fields, "isbn")
	}
	if strings.TrimSpace(item.Publisher) != "" {
		fields = append(fields, "publisher")
	}
	if strings.TrimSpace(item.EditionVariant) != "" {
		fields = append(fields, "edition_variant")
	}
	if item.PriceMinor != 0 || len(item.PriceComponents) > 0 {
		fields = append(fields, "price", "currency", "price_basis")
		if len(item.PriceComponents) > 0 {
			fields = append(fields, "price_components")
		}
	}
	if strings.TrimSpace(item.Condition) != "" {
		fields = append(fields, "condition")
	}
	if strings.TrimSpace(item.SellerLocation) != "" {
		fields = append(fields, "seller_location")
	}
	if strings.TrimSpace(item.ShippingText) != "" {
		fields = append(fields, "shipping")
	}
	if strings.TrimSpace(item.ImageURL) != "" {
		fields = append(fields, "image_url")
	}
	return fields
}

func ObservationPermissionScopes(item ObservationInput) []string {
	scopes := []string{ObservationPermissionScope(item)}
	if strings.TrimSpace(item.ImageURL) != "" {
		scopes = append(scopes, SourcePermissionScopeProductImages)
	}
	return scopes
}
