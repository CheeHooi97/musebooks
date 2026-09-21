package catalog

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"net/url"
	"strings"
	"time"

	"github.com/labstack/echo/v4"
	"gorm.io/gorm"
	"gorm.io/gorm/clause"
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

var supportedScrapeOperations = map[string]struct{}{
	"catalog_discovery": {},
	"active_discovery":  {},
	"listing_detail":    {},
	"listing_reconcile": {},
	"sold_discovery":    {},
}

type CreateScrapeJobRequest struct {
	ID          string         `json:"id,omitempty"`
	SourceID    string         `json:"sourceId"`
	Operation   string         `json:"operation"`
	Request     map[string]any `json:"request"`
	Priority    int            `json:"priority,omitempty"`
	AvailableAt *time.Time     `json:"availableAt,omitempty"`
	MaxAttempts int            `json:"maxAttempts,omitempty"`
}

type ClaimScrapeJobRequest struct {
	WorkerID     string   `json:"workerId"`
	SourceIDs    []string `json:"sourceIds,omitempty"`
	LeaseSeconds int      `json:"leaseSeconds,omitempty"`
}

type HeartbeatScrapeJobRequest struct {
	WorkerID     string `json:"workerId"`
	LeaseToken   string `json:"leaseToken"`
	LeaseSeconds int    `json:"leaseSeconds,omitempty"`
}

type CompleteScrapeJobRequest struct {
	WorkerID      string   `json:"workerId"`
	LeaseToken    string   `json:"leaseToken"`
	Status        string   `json:"status"`
	NextCursor    string   `json:"nextCursor,omitempty"`
	Requeue       bool     `json:"requeue,omitempty"`
	ItemsReceived int      `json:"itemsReceived,omitempty"`
	ItemsAccepted int      `json:"itemsAccepted,omitempty"`
	ItemsRejected int      `json:"itemsRejected,omitempty"`
	Warnings      []string `json:"warnings,omitempty"`
	Error         string   `json:"error,omitempty"`
}

type ScrapeJobResponse struct {
	ID              string         `json:"id"`
	SourceID        string         `json:"sourceId"`
	Operation       string         `json:"operation"`
	Request         map[string]any `json:"request"`
	Status          string         `json:"status"`
	Priority        int            `json:"priority"`
	PageCursor      string         `json:"pageCursor,omitempty"`
	WorkerID        string         `json:"workerId,omitempty"`
	LeaseToken      string         `json:"leaseToken,omitempty"`
	AttemptCount    int            `json:"attemptCount"`
	MaxAttempts     int            `json:"maxAttempts"`
	AvailableAt     time.Time      `json:"availableAt"`
	LeasedUntil     *time.Time     `json:"leasedUntil,omitempty"`
	LastHeartbeatAt *time.Time     `json:"lastHeartbeatAt,omitempty"`
	StartedAt       *time.Time     `json:"startedAt,omitempty"`
	CompletedAt     *time.Time     `json:"completedAt,omitempty"`
	LastError       string         `json:"lastError,omitempty"`
}

type ScrapeSourceResponse struct {
	ID             string   `json:"id"`
	Name           string   `json:"name"`
	Region         string   `json:"region"`
	Locale         string   `json:"locale,omitempty"`
	Timezone       string   `json:"timezone,omitempty"`
	Kind           string   `json:"kind"`
	Adapter        string   `json:"adapter"`
	AccessMethod   string   `json:"accessMethod"`
	BaseURL        string   `json:"baseUrl"`
	DefaultFormat  string   `json:"defaultFormat,omitempty"`
	AllowedFormats []string `json:"allowedFormats,omitempty"`
	AllowedHosts   []string `json:"allowedHosts,omitempty"`
	Capabilities   []string `json:"capabilities,omitempty"`
	AccessStatus   string   `json:"accessStatus"`
	TermsURL       string   `json:"termsUrl,omitempty"`
	RatePerMinute  int      `json:"ratePerMinute"`
}

type ClaimScrapeJobResponse struct {
	Job    ScrapeJobResponse    `json:"job"`
	Source ScrapeSourceResponse `json:"source"`
}

func (h *Handler) CreateScrapeJob(c echo.Context) error {
	if err := h.checkScraperToken(c); err != nil {
		return err
	}
	var request CreateScrapeJobRequest
	if err := json.NewDecoder(c.Request().Body).Decode(&request); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, "invalid scrape job")
	}
	request.SourceID = strings.TrimSpace(request.SourceID)
	request.Operation = strings.ToLower(strings.TrimSpace(request.Operation))
	if request.SourceID == "" || request.Operation == "" {
		return echo.NewHTTPError(http.StatusBadRequest, "sourceId and operation are required")
	}
	if _, ok := supportedScrapeOperations[request.Operation]; !ok {
		return echo.NewHTTPError(http.StatusBadRequest, "unsupported scrape operation")
	}

	var source Source
	result := h.db.First(&source, "id = ?", request.SourceID)
	if errors.Is(result.Error, gorm.ErrRecordNotFound) {
		return echo.NewHTTPError(http.StatusBadRequest, "unknown sourceId")
	}
	if result.Error != nil {
		return echo.NewHTTPError(http.StatusInternalServerError, "failed to load source")
	}
	if !source.Enabled {
		return echo.NewHTTPError(http.StatusConflict, "source is disabled")
	}
	if source.AccessStatus == jobBlocked {
		return echo.NewHTTPError(http.StatusConflict, "source access is blocked")
	}
	if strings.ToLower(strings.TrimSpace(source.AccessMethod)) != "browser" {
		return echo.NewHTTPError(http.StatusConflict, "only browser sources are supported")
	}
	if !sourceSupportsOperation(source, request.Operation) {
		return echo.NewHTTPError(http.StatusConflict, "source does not support this scrape operation")
	}
	if request.Request == nil {
		request.Request = map[string]any{}
	}
	for _, field := range []string{"url", "searchUrl"} {
		if rawURL, ok := request.Request[field].(string); ok && strings.TrimSpace(rawURL) != "" {
			if err := validateSourceURL(source, rawURL); err != nil {
				return echo.NewHTTPError(http.StatusBadRequest, err.Error())
			}
		}
	}
	if pageURLs, ok := request.Request["pageUrls"].([]any); ok {
		if len(pageURLs) > 50 {
			return echo.NewHTTPError(http.StatusBadRequest, "pageUrls may contain at most 50 URLs")
		}
		for _, value := range pageURLs {
			rawURL, ok := value.(string)
			if !ok || strings.TrimSpace(rawURL) == "" {
				return echo.NewHTTPError(http.StatusBadRequest, "pageUrls must contain absolute http(s) URLs")
			}
			if err := validateSourceURL(source, rawURL); err != nil {
				return echo.NewHTTPError(http.StatusBadRequest, err.Error())
			}
		}
	}
	requestJSON, err := json.Marshal(request.Request)
	if err != nil || len(requestJSON) > 64*1024 {
		return echo.NewHTTPError(http.StatusBadRequest, "request must be valid JSON no larger than 64 KiB")
	}

	now := time.Now().UTC()
	availableAt := now
	if request.AvailableAt != nil && request.AvailableAt.After(now) {
		availableAt = request.AvailableAt.UTC()
	}
	maxAttempts := request.MaxAttempts
	if maxAttempts < 1 || maxAttempts > 10 {
		maxAttempts = 3
	}
	jobID := strings.TrimSpace(request.ID)
	if jobID == "" {
		jobID = fmt.Sprintf("scrape-job-%d", now.UnixNano())
	}
	job := ScrapeJob{
		ID:          jobID,
		SourceID:    request.SourceID,
		Operation:   request.Operation,
		RequestJSON: string(requestJSON),
		Status:      jobQueued,
		Priority:    request.Priority,
		MaxAttempts: maxAttempts,
		AvailableAt: availableAt,
	}
	if err := h.db.Create(&job).Error; err != nil {
		if strings.Contains(strings.ToLower(err.Error()), "duplicate") {
			return echo.NewHTTPError(http.StatusConflict, "scrape job id already exists")
		}
		return echo.NewHTTPError(http.StatusInternalServerError, "failed to create scrape job")
	}
	return c.JSON(http.StatusAccepted, job.Response())
}

func (h *Handler) ClaimScrapeJob(c echo.Context) error {
	if err := h.checkScraperToken(c); err != nil {
		return err
	}
	var request ClaimScrapeJobRequest
	if err := json.NewDecoder(c.Request().Body).Decode(&request); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, "invalid claim request")
	}
	request.WorkerID = strings.TrimSpace(request.WorkerID)
	if request.WorkerID == "" {
		return echo.NewHTTPError(http.StatusBadRequest, "workerId is required")
	}
	leaseSeconds := clampLeaseSeconds(request.LeaseSeconds)
	now := time.Now().UTC()
	var job ScrapeJob
	var source Source
	claimed := false
	err := h.db.Transaction(func(tx *gorm.DB) error {
		query := tx.Clauses(clause.Locking{Strength: "UPDATE", Options: "SKIP LOCKED"}).
			Where("available_at <= ?", now).
			Where("attempt_count < max_attempts").
			Where("status = ? OR (status IN ? AND (leased_until IS NULL OR leased_until <= ?))", jobQueued, []string{"leased", jobRunning}, now)
		if len(request.SourceIDs) > 0 {
			query = query.Where("source_id IN ?", request.SourceIDs)
		}
		result := query.Order("priority DESC, available_at ASC, created_at ASC").First(&job)
		if errors.Is(result.Error, gorm.ErrRecordNotFound) {
			return nil
		}
		if result.Error != nil {
			return result.Error
		}
		if err := tx.First(&source, "id = ?", job.SourceID).Error; err != nil {
			return err
		}
		if !source.Enabled || strings.ToLower(strings.TrimSpace(source.AccessMethod)) != "browser" {
			finished := now
			if err := tx.Model(&job).Updates(map[string]any{
				"status":       jobBlocked,
				"completed_at": finished,
				"last_error":   "source is disabled or not browser-only",
			}).Error; err != nil {
				return err
			}
			return nil
		}
		leaseUntil := now.Add(time.Duration(leaseSeconds) * time.Second)
		leaseToken := scrapeLeaseToken(job.ID, request.WorkerID, now)
		updates := map[string]any{
			"status":            jobRunning,
			"worker_id":         request.WorkerID,
			"attempt_count":     job.AttemptCount + 1,
			"leased_until":      leaseUntil,
			"last_heartbeat_at": now,
			"lease_token":       leaseToken,
			"last_error":        "",
		}
		if job.StartedAt == nil {
			updates["started_at"] = now
		}
		if err := tx.Model(&job).Updates(updates).Error; err != nil {
			return err
		}
		job.Status = jobRunning
		job.WorkerID = request.WorkerID
		job.AttemptCount++
		job.LeasedUntil = &leaseUntil
		job.LastHeartbeatAt = &now
		job.LeaseToken = leaseToken
		if job.StartedAt == nil {
			job.StartedAt = &now
		}
		if err := tx.Create(&ScrapeRun{
			ID:        fmt.Sprintf("scrape-run-%d", now.UnixNano()),
			JobID:     job.ID,
			WorkerID:  request.WorkerID,
			Status:    jobRunning,
			StartedAt: now,
		}).Error; err != nil {
			return err
		}
		claimed = true
		return nil
	})
	if err != nil {
		return echo.NewHTTPError(http.StatusInternalServerError, "failed to claim scrape job")
	}
	if !claimed {
		return c.NoContent(http.StatusNoContent)
	}
	return c.JSON(http.StatusOK, ClaimScrapeJobResponse{
		Job:    job.Response(),
		Source: source.ResponseForScraper(),
	})
}

func (h *Handler) HeartbeatScrapeJob(c echo.Context) error {
	if err := h.checkScraperToken(c); err != nil {
		return err
	}
	var request HeartbeatScrapeJobRequest
	if err := json.NewDecoder(c.Request().Body).Decode(&request); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, "invalid heartbeat request")
	}
	request.WorkerID = strings.TrimSpace(request.WorkerID)
	request.LeaseToken = strings.TrimSpace(request.LeaseToken)
	if request.WorkerID == "" {
		return echo.NewHTTPError(http.StatusBadRequest, "workerId is required")
	}
	var job ScrapeJob
	result := h.db.First(&job, "id = ?", c.Param("id"))
	if errors.Is(result.Error, gorm.ErrRecordNotFound) {
		return echo.NewHTTPError(http.StatusNotFound, "scrape job not found")
	}
	if result.Error != nil {
		return echo.NewHTTPError(http.StatusInternalServerError, "failed to load scrape job")
	}
	if job.WorkerID != request.WorkerID || job.LeaseToken != request.LeaseToken || request.LeaseToken == "" {
		return echo.NewHTTPError(http.StatusConflict, "scrape job is owned by another worker")
	}
	if job.Status != jobRunning {
		return echo.NewHTTPError(http.StatusConflict, "scrape job is not running")
	}
	now := time.Now().UTC()
	if job.LeasedUntil != nil && job.LeasedUntil.Before(now) {
		return echo.NewHTTPError(http.StatusConflict, "scrape job lease expired")
	}
	leaseUntil := now.Add(time.Duration(clampLeaseSeconds(request.LeaseSeconds)) * time.Second)
	if err := h.db.Model(&job).Updates(map[string]any{
		"leased_until":      leaseUntil,
		"last_heartbeat_at": now,
	}).Error; err != nil {
		return echo.NewHTTPError(http.StatusInternalServerError, "failed to heartbeat scrape job")
	}
	job.LeasedUntil = &leaseUntil
	job.LastHeartbeatAt = &now
	return c.JSON(http.StatusOK, job.Response())
}

func (h *Handler) CompleteScrapeJob(c echo.Context) error {
	if err := h.checkScraperToken(c); err != nil {
		return err
	}
	var request CompleteScrapeJobRequest
	if err := json.NewDecoder(c.Request().Body).Decode(&request); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, "invalid completion request")
	}
	request.WorkerID = strings.TrimSpace(request.WorkerID)
	request.LeaseToken = strings.TrimSpace(request.LeaseToken)
	request.Status = strings.ToLower(strings.TrimSpace(request.Status))
	if request.WorkerID == "" || request.LeaseToken == "" || request.Status == "" {
		return echo.NewHTTPError(http.StatusBadRequest, "workerId, leaseToken, and status are required")
	}
	if request.Status != jobSuccess && request.Status != jobFailed && request.Status != jobBlocked {
		return echo.NewHTTPError(http.StatusBadRequest, "status must be succeeded, failed, or blocked")
	}
	var job ScrapeJob
	result := h.db.First(&job, "id = ?", c.Param("id"))
	if errors.Is(result.Error, gorm.ErrRecordNotFound) {
		return echo.NewHTTPError(http.StatusNotFound, "scrape job not found")
	}
	if result.Error != nil {
		return echo.NewHTTPError(http.StatusInternalServerError, "failed to load scrape job")
	}
	if job.WorkerID != request.WorkerID || job.LeaseToken != request.LeaseToken {
		return echo.NewHTTPError(http.StatusConflict, "scrape job is owned by another worker")
	}
	if job.Status != jobRunning {
		return echo.NewHTTPError(http.StatusConflict, "scrape job is not running")
	}

	now := time.Now().UTC()
	warningsJSON, _ := json.Marshal(request.Warnings)
	jobStatus := request.Status
	availableAt := now
	var completedAt *time.Time = &now
	if request.Requeue || (request.Status == jobFailed && job.AttemptCount < job.MaxAttempts) {
		jobStatus = jobQueued
		completedAt = nil
		if request.Status == jobFailed {
			availableAt = now.Add(retryDelay(job.AttemptCount))
		}
	}
	updates := map[string]any{
		"status":       jobStatus,
		"page_cursor":  request.NextCursor,
		"leased_until": nil,
		"lease_token":  "",
		"completed_at": completedAt,
		"available_at": availableAt,
		"last_error":   strings.TrimSpace(request.Error),
	}
	if request.Requeue && request.Status == jobSuccess {
		// A successful page is a checkpoint, not another failed attempt. Reset
		// the per-page retry budget so a multi-page crawl is not capped at
		// maxAttempts after the first few successful pages.
		updates["attempt_count"] = 0
	}
	if err := h.db.Transaction(func(tx *gorm.DB) error {
		if err := tx.Model(&job).Updates(updates).Error; err != nil {
			return err
		}
		var run ScrapeRun
		runResult := tx.Where("job_id = ? AND worker_id = ? AND status = ?", job.ID, request.WorkerID, jobRunning).
			Order("started_at DESC").First(&run)
		if !errors.Is(runResult.Error, gorm.ErrRecordNotFound) {
			if runResult.Error != nil {
				return runResult.Error
			}
			if err := tx.Model(&run).Updates(map[string]any{
				"status":         request.Status,
				"items_received": request.ItemsReceived,
				"items_accepted": request.ItemsAccepted,
				"items_rejected": request.ItemsRejected,
				"next_cursor":    request.NextCursor,
				"warnings":       string(warningsJSON),
				"error":          strings.TrimSpace(request.Error),
				"finished_at":    now,
			}).Error; err != nil {
				return err
			}
		}
		return nil
	}); err != nil {
		return echo.NewHTTPError(http.StatusInternalServerError, "failed to complete scrape job")
	}
	job.Status = jobStatus
	job.PageCursor = request.NextCursor
	if request.Requeue && request.Status == jobSuccess {
		job.AttemptCount = 0
	}
	job.LeasedUntil = nil
	job.LeaseToken = ""
	job.CompletedAt = completedAt
	job.AvailableAt = availableAt
	job.LastError = strings.TrimSpace(request.Error)
	return c.JSON(http.StatusOK, job.Response())
}

func (h *Handler) checkScraperToken(c echo.Context) error {
	if h.ingestSecret != "" && c.Request().Header.Get("X-Scraper-Token") != h.ingestSecret {
		return echo.NewHTTPError(http.StatusUnauthorized, "invalid scraper token")
	}
	return nil
}

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
		AllowedFormats: splitCSV(source.AllowedFormats),
		AllowedHosts:   splitCSV(source.AllowedHosts),
		Capabilities:   splitCSV(source.Capabilities),
		AccessStatus:   source.AccessStatus,
		TermsURL:       source.TermsURL,
		RatePerMinute:  source.RatePerMinute,
	}
}

func validateSourceURL(source Source, raw string) error {
	parsed, err := url.Parse(strings.TrimSpace(raw))
	if err != nil || (parsed.Scheme != "http" && parsed.Scheme != "https") || parsed.Hostname() == "" {
		return errors.New("request url must be an absolute http(s) URL")
	}
	allowed := splitCSV(source.AllowedHosts)
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

func normalizeFormat(value string) string {
	switch strings.ToLower(strings.TrimSpace(value)) {
	case "physical", "print", "printed", "hardcopy", "paper":
		return formatPhysical
	case "digital", "ebook", "e-book", "epub", "pdf":
		return formatDigital
	default:
		return ""
	}
}

func validateObservationFormat(source Source, value, digitalAccess string) (string, string, error) {
	format := normalizeFormat(value)
	if format == "" {
		format = normalizeFormat(source.DefaultFormat)
	}
	if format == "" {
		return "", "", errors.New("format must be physical or digital")
	}
	allowed := splitCSV(source.AllowedFormats)
	if len(allowed) > 0 {
		allowedFormat := false
		for _, candidate := range allowed {
			if normalizeFormat(candidate) == format {
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

func splitCSV(value string) []string {
	parts := strings.Split(value, ",")
	result := make([]string, 0, len(parts))
	for _, part := range parts {
		if value := strings.TrimSpace(part); value != "" {
			result = append(result, value)
		}
	}
	return result
}

func sourceSupportsOperation(source Source, operation string) bool {
	capabilities := splitCSV(source.Capabilities)
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

func clampLeaseSeconds(value int) int {
	if value <= 0 {
		return jobLeaseSec
	}
	if value > 3600 {
		return 3600
	}
	return value
}

func retryDelay(attempt int) time.Duration {
	if attempt < 1 {
		attempt = 1
	}
	seconds := 15 * (1 << minInt(attempt-1, 6))
	return time.Duration(seconds) * time.Second
}

func minInt(a, b int) int {
	if a < b {
		return a
	}
	return b
}

func scrapeObservationID(sourceID, externalID, jobID, observationID string) string {
	value := strings.TrimSpace(observationID)
	if value == "" {
		value = jobID + "\x00" + externalID
	}
	hash := sha256.Sum256([]byte(sourceID + "\x00" + value))
	return "observation-" + hex.EncodeToString(hash[:])[:40]
}

func scrapeLeaseToken(jobID, workerID string, now time.Time) string {
	hash := sha256.Sum256([]byte(jobID + "\x00" + workerID + "\x00" + now.Format(time.RFC3339Nano)))
	return "lease-" + hex.EncodeToString(hash[:])[:40]
}
