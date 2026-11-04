package model

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"net/url"
	"strings"
	"time"
)

const (
	jobQueued      = "queued"
	jobRunning     = "running"
	jobSuccess     = "succeeded"
	jobFailed      = "failed"
	jobBlocked     = "blocked"
	jobLeaseSec    = 300
	formatPhysical = "physical"
	formatDigital  = "digital"
)

func (job ScrapeJob) Response() ScrapeJobResponse {
	request := map[string]any{}
	if strings.TrimSpace(job.RequestJSON) != "" {
		_ = json.Unmarshal([]byte(job.RequestJSON), &request)
	}
	return ScrapeJobResponse{
		ID:              job.ID,
		SourceID:        job.SourceID,
		Operation:       job.Operation,
		Request:         request,
		Status:          job.Status,
		Priority:        job.Priority,
		PageCursor:      job.PageCursor,
		WorkerID:        job.WorkerID,
		LeaseToken:      job.LeaseToken,
		AttemptCount:    job.AttemptCount,
		MaxAttempts:     job.MaxAttempts,
		AvailableAt:     job.AvailableAt,
		LeasedUntil:     job.LeasedUntil,
		LastHeartbeatAt: job.LastHeartbeatAt,
		StartedAt:       job.StartedAt,
		CompletedAt:     job.CompletedAt,
		LastError:       job.LastError,
	}
}

func (source Source) ResponseForScraper() ScrapeSourceResponse {
	return ScrapeSourceResponse{
		ID:             source.ID,
		Name:           source.Name,
		Region:         source.Region,
		Locale:         source.Locale,
		Timezone:       source.Timezone,
		Kind:           source.Kind,
		Adapter:        source.Adapter,
		AccessMethod:   source.AccessMethod,
		BaseURL:        source.BaseURL,
		DefaultFormat:  source.DefaultFormat,
		AllowedFormats: SplitCSV(source.AllowedFormats),
		AllowedHosts:   SplitCSV(source.AllowedHosts),
		Capabilities:   SplitCSV(source.Capabilities),
		AccessStatus:   source.AccessStatus,
		TermsURL:       source.TermsURL,
		RatePerMinute:  source.RatePerMinute,
	}
}

func ValidateSourceURL(source Source, raw string) error {
	parsed, err := url.Parse(strings.TrimSpace(raw))
	if err != nil || (parsed.Scheme != "http" && parsed.Scheme != "https") || parsed.Hostname() == "" {
		return errors.New("request url must be an absolute http(s) URL")
	}
	allowed := SplitCSV(source.AllowedHosts)
	if len(allowed) == 0 && source.BaseURL != "" {
		if base, baseErr := url.Parse(source.BaseURL); baseErr == nil && base.Hostname() != "" {
			allowed = []string{base.Hostname()}
		}
	}
	for _, host := range allowed {
		host = strings.ToLower(strings.TrimSpace(host))
		if host != "" && (strings.EqualFold(parsed.Hostname(), host) || strings.HasSuffix(strings.ToLower(parsed.Hostname()), "."+host)) {
			return nil
		}
	}
	return errors.New("request url host is not allowed for this source")
}

func NormalizeFormat(value string) string {
	switch strings.ToLower(strings.TrimSpace(value)) {
	case "physical", "print", "printed", "hardcopy", "paper":
		return formatPhysical
	case "digital", "ebook", "e-book", "epub", "pdf":
		return formatDigital
	default:
		return ""
	}
}

func ValidateObservationFormat(source Source, value, digitalAccess string) (string, string, error) {
	format := NormalizeFormat(value)
	if strings.TrimSpace(value) != "" && format == "" {
		return "", "", errors.New("format must be physical or digital")
	}
	if format == "" {
		format = SourcePhotobookFormat(source)
		if format == "" {
			format = NormalizeFormat(source.DefaultFormat)
		}
	}
	if format == "" {
		return "", "", errors.New("format must be physical or digital")
	}
	if expected := SourcePhotobookFormat(source); expected != "" && expected != format {
		return "", "", errors.New("marketplaces accept physical books; digital platforms accept digital editions")
	}
	allowed := SplitCSV(source.AllowedFormats)
	if len(allowed) > 0 {
		allowedFormat := false
		for _, candidate := range allowed {
			if NormalizeFormat(candidate) == format {
				allowedFormat = true
				break
			}
		}
		if !allowedFormat {
			return "", "", errors.New("format is not allowed for this source")
		}
	}

	access := strings.ToLower(strings.TrimSpace(digitalAccess))
	if format != formatDigital {
		// Physical offers never carry digital provenance. Drop any accidental
		// value from an adapter instead of persisting a misleading access claim.
		return format, "", nil
	}
	switch access {
	case "unauthorized", "pirated", "file_resale", "unofficial", "torrent", "unknown":
		return "", "", errors.New("unauthorized digital content is not accepted")
	case "":
		if source.Kind != "digital_store" && source.Kind != "bookstore" {
			return "", "", errors.New("digital listings require authorized digital-access evidence")
		}
		access = "authorized_store"
	case "authorized", "authorized_store", "publisher", "official", "ebook_store":
		access = "authorized_store"
	default:
		return "", "", errors.New("digitalAccess must identify an authorized store or publisher")
	}
	return format, access, nil
}

func SplitCSV(value string) []string {
	parts := strings.Split(value, ",")
	result := make([]string, 0, len(parts))
	for _, part := range parts {
		if value := strings.TrimSpace(part); value != "" {
			result = append(result, value)
		}
	}
	return result
}

func ValidateExplicitSoldRequest(sourceID, operation string, request map[string]any) error {
	if operation != "sold_discovery" || (sourceID != "yahoo-tw" && sourceID != "rakuma" && sourceID != "yahoo-furima-jp") {
		return nil
	}
	for _, field := range []string{"url", "searchUrl"} {
		if value, ok := request[field].(string); ok && strings.TrimSpace(value) != "" {
			return nil
		}
	}
	return fmt.Errorf("%s sold discovery requires an exact public completed-listing url or closed-listing searchUrl; public keyword sold-history search is unverified", sourceID)
}

func SourceSupportsOperation(source Source, operation string) bool {
	capabilities := SplitCSV(source.Capabilities)
	if len(capabilities) == 0 {
		// Keep manually-created legacy sources usable until their capabilities
		// are populated. Seeded sources are explicit and are checked strictly.
		return true
	}
	for _, capability := range capabilities {
		if strings.EqualFold(strings.TrimSpace(capability), operation) {
			return true
		}
	}
	return false
}

func ClampLeaseSeconds(value int) int {
	if value <= 0 {
		return jobLeaseSec
	}
	if value > 3600 {
		return 3600
	}
	return value
}

func RetryDelay(attempt int) time.Duration {
	if attempt < 1 {
		attempt = 1
	}
	seconds := 15 * (1 << MinInt(attempt-1, 6))
	return time.Duration(seconds) * time.Second
}

func MinInt(a, b int) int {
	if a < b {
		return a
	}
	return b
}

func ScrapeObservationID(sourceID, externalID, jobID, observationID string) string {
	value := strings.TrimSpace(observationID)
	if value == "" {
		value = jobID + "\x00" + externalID
	}
	hash := sha256.Sum256([]byte(sourceID + "\x00" + value))
	return "observation-" + hex.EncodeToString(hash[:])[:40]
}

func ScrapeLeaseToken(jobID, workerID string, now time.Time) string {
	hash := sha256.Sum256([]byte(jobID + "\x00" + workerID + "\x00" + now.Format(time.RFC3339Nano)))
	return "lease-" + hex.EncodeToString(hash[:])[:40]
}

func IsDigitalRetailSource(source Source) bool {
	switch source.ID {
	case "books-com-tw", "bookwalker-tw", "readmoo-tw", "pubu-tw", "kobo-tw", "hami-tw", "google-play-books-tw", "apple-books-tw", "apple-books-us", "hyread-tw", "momo-books-tw", "pchome-books-tw", "yahoo-shopping-books-tw", "kingstone-books-tw", "taaze-books-tw", "sanmin-books-tw", "rakuten-kobo-tw", "fan520-tw":
		return true
	}
	return false
}

func ValidateDigitalRetailRequest(source Source, operation string, request map[string]any) error {
	if format, supplied := request["format"]; supplied {
		value, ok := format.(string)
		if !ok || (value != "" && NormalizeFormat(value) == "") {
			return errors.New("format must be physical or digital")
		}
		if expected := SourcePhotobookFormat(source); value != "" && expected != "" && NormalizeFormat(value) != expected {
			return errors.New("scrape format does not match the source: physical marketplace or digital platform")
		}
	}
	if !IsDigitalRetailSource(source) {
		return nil
	}
	switch operation {
	case "catalog_discovery", "active_discovery", "listing_detail":
	default:
		return errors.New("digital retail sources do not support sold transactions")
	}
	format, _ := request["format"].(string)
	if format != "" && NormalizeFormat(format) != formatDigital {
		return errors.New("retail scraping is allowed for digital editions only")
	}
	return nil
}

func IsPhysicalMarketplaceSource(source Source) bool {
	switch strings.ToLower(strings.TrimSpace(source.Kind)) {
	case "marketplace", "marketplace_c2c", "auction", "flea_market":
		return !IsDigitalRetailSource(source)
	}
	return false
}

func SourcePhotobookFormat(source Source) string {
	if IsDigitalRetailSource(source) {
		return formatDigital
	}
	if IsPhysicalMarketplaceSource(source) {
		return formatPhysical
	}
	switch strings.ToLower(strings.TrimSpace(source.Kind)) {
	case "digital_store":
		return formatDigital
	case "bookstore":
		// A bookstore can sell print or digital editions. Use its explicit
		// source configuration instead of treating every bookstore as digital.
		if format := NormalizeFormat(source.DefaultFormat); format != "" {
			return format
		}
		allowed := SplitCSV(source.AllowedFormats)
		if len(allowed) == 1 {
			return NormalizeFormat(allowed[0])
		}
	}
	return ""
}

func ValidateObservationPrice(format, status, priceType string) (string, error) {
	value := strings.ToLower(strings.TrimSpace(priceType))
	if format == formatDigital {
		if strings.EqualFold(strings.TrimSpace(status), "completed") {
			return "", errors.New("digital retail offers are not sold transactions")
		}
		if value != "" && value != "digital" {
			return "", errors.New("digital editions require a retail price")
		}
		return "digital", nil
	}
	if value == "digital" {
		return "", errors.New("physical listings cannot carry digital retail prices")
	}
	if value == "auction_hammer" && status != "completed" || value == "auction_current" && status == "completed" {
		return "", errors.New("auction price type conflicts with transaction status")
	}
	if value == "" {
		value = "fixed"
	}
	return value, nil
}

func ValidatePriceBasis(format, status, basis string) (string, error) {
	value := strings.ToLower(strings.TrimSpace(basis))
	status = strings.ToLower(strings.TrimSpace(status))
	if value == "" {
		return "", nil // legacy observations do not have a typed basis
	}
	switch value {
	case "list", "sale", "coupon":
		if status == "completed" || status == "sold" {
			return "", errors.New("retail price basis conflicts with completed-sale status")
		}
	case "used_asking":
		if NormalizeFormat(format) != formatPhysical || status == "completed" || status == "sold" {
			return "", errors.New("used asking price requires a physical offer that is not sold")
		}
	case "completed_sale":
		if status != "completed" {
			return "", errors.New("completed-sale price basis requires completed-sale status")
		}
	default:
		return "", errors.New("unsupported price basis")
	}
	return value, nil
}

// NormalizePriceComponents validates simultaneous seller quotes and chooses a
// generally available amount for legacy price fields, excluding coupon quotes.
func NormalizePriceComponents(format, status, currency, basis string, priceMinor int64, components []PriceComponent) (int64, string, string, []PriceComponent, error) {
	status = strings.ToLower(strings.TrimSpace(status))
	if components == nil {
		components = []PriceComponent{}
	}
	if priceMinor < 0 {
		return 0, "", "", nil, errors.New("price cannot be negative")
	}
	validatedBasis, err := ValidatePriceBasis(format, status, basis)
	if err != nil {
		return 0, "", "", nil, err
	}
	basis = validatedBasis
	if priceMinor == 0 && len(components) == 0 && basis != "" {
		return 0, "", "", nil, errors.New("price basis requires a price amount")
	}
	if basis == "coupon" && len(components) == 0 {
		return 0, "", "", nil, errors.New("coupon price requires a recorded eligibility condition")
	}
	seen := map[string]bool{}
	componentCurrency := ""
	for i := range components {
		component := &components[i]
		validated, err := ValidatePriceBasis(format, status, component.Basis)
		if err != nil || validated == "" || component.PriceMinor <= 0 || strings.TrimSpace(component.Currency) == "" || seen[validated] || validated == "coupon" && strings.TrimSpace(component.Condition) == "" {
			return 0, "", "", nil, errors.New("invalid or duplicate price component")
		}
		component.Basis = validated
		seen[validated] = true
		if componentCurrency != "" && componentCurrency != component.Currency {
			return 0, "", "", nil, errors.New("price components must use the same currency")
		}
		componentCurrency = component.Currency
	}
	if seen["used_asking"] && len(components) != 1 || seen["completed_sale"] && len(components) != 1 {
		return 0, "", "", nil, errors.New("used and completed-sale prices cannot be combined with retail quotes")
	}
	if len(components) > 0 {
		if priceMinor > 0 {
			matched := false
			for _, component := range components {
				if component.Basis == basis && component.PriceMinor == priceMinor && component.Currency == currency {
					matched = true
					break
				}
			}
			if !matched {
				return 0, "", "", nil, errors.New("primary price must match one price component")
			}
		} else {
			for _, preferred := range []string{"sale", "list", "used_asking", "completed_sale", "coupon"} {
				for _, component := range components {
					if component.Basis == preferred {
						priceMinor, basis, currency = component.PriceMinor, component.Basis, component.Currency
						break
					}
				}
				if priceMinor > 0 {
					break
				}
			}
		}
	}
	if priceMinor > 0 {
		validated, err := ValidatePriceBasis(format, status, basis)
		if err != nil {
			return 0, "", "", nil, err
		}
		basis = validated
	}
	return priceMinor, basis, currency, components, nil
}

func IsRetailScrapeSource(source Source) bool {
	if IsDigitalRetailSource(source) {
		return false
	}
	switch strings.ToLower(strings.TrimSpace(source.Kind)) {
	case "bookstore", "digital_store":
		return true
	}
	switch source.ID {
	case "books-com-tw", "bookwalker-tw", "readmoo-tw", "bookwalker-jp", "rakuten-books-jp", "surugaya", "surugaya-jp", "mandarake", "mandarake-jp", "dangdang-cn":
		return true
	}
	return false
}
