package handler

import (
	"encoding/json"
	"errors"
	"fmt"
	"github.com/labstack/echo/v4"
	"musebooks/model"
	"musebooks/service"
	"net/http"
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

var supportedScrapeOperations = map[string]struct{}{
	"catalog_discovery": {},
	"active_discovery":  {},
	"listing_detail":    {},
	"listing_reconcile": {},
	"sold_discovery":    {},
}

func (h *CatalogHandler) CreateScrapeJob(c echo.Context) error {
	if err := h.checkScraperToken(c); err != nil {
		return err
	}
	var request model.CreateScrapeJobRequest
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

	var source model.Source
	result := h.service.GetSource(&source, request.SourceID)
	if errors.Is(result.Error, service.ErrRecordNotFound) {
		return echo.NewHTTPError(http.StatusBadRequest, "unknown sourceId")
	}
	if result.Error != nil {
		return echo.NewHTTPError(http.StatusInternalServerError, "failed to load source")
	}
	if err := model.ValidateDigitalRetailRequest(source, request.Operation, request.Request); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, err.Error())
	}
	if expected := model.SourcePhotobookFormat(source); expected != "" {
		if request.Request == nil {
			request.Request = map[string]any{}
		}
		request.Request["format"] = expected
	}
	if model.IsRetailScrapeSource(source) {
		return echo.NewHTTPError(http.StatusConflict, "retail sources are excluded from scraping")
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
	if !model.SourceSupportsOperation(source, request.Operation) {
		return echo.NewHTTPError(http.StatusConflict, "source does not support this scrape operation")
	}
	if request.Request == nil {
		request.Request = map[string]any{}
	}
	if err := model.ValidateExplicitSoldRequest(request.SourceID, request.Operation, request.Request); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, err.Error())
	}
	for _, field := range []string{"url", "searchUrl"} {
		if rawURL, ok := request.Request[field].(string); ok && strings.TrimSpace(rawURL) != "" {
			if err := model.ValidateSourceURL(source, rawURL); err != nil {
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
			if err := model.ValidateSourceURL(source, rawURL); err != nil {
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
	job := model.ScrapeJob{
		ID:          jobID,
		SourceID:    request.SourceID,
		Operation:   request.Operation,
		RequestJSON: string(requestJSON),
		Status:      jobQueued,
		Priority:    request.Priority,
		MaxAttempts: maxAttempts,
		AvailableAt: availableAt,
	}
	if err := h.service.CreateJob(&job).Error; err != nil {
		if strings.Contains(strings.ToLower(err.Error()), "duplicate") {
			return echo.NewHTTPError(http.StatusConflict, "scrape job id already exists")
		}
		return echo.NewHTTPError(http.StatusInternalServerError, "failed to create scrape job")
	}
	return c.JSON(http.StatusAccepted, job.Response())
}

func (h *CatalogHandler) ClaimScrapeJob(c echo.Context) error {
	if err := h.checkScraperToken(c); err != nil {
		return err
	}
	var request model.ClaimScrapeJobRequest
	if err := json.NewDecoder(c.Request().Body).Decode(&request); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, "invalid claim request")
	}
	request.WorkerID = strings.TrimSpace(request.WorkerID)
	if request.WorkerID == "" {
		return echo.NewHTTPError(http.StatusBadRequest, "workerId is required")
	}
	leaseSeconds := model.ClampLeaseSeconds(request.LeaseSeconds)
	now := time.Now().UTC()
	var job model.ScrapeJob
	var source model.Source
	claimed := false
	err := h.service.Transaction(func(tx *service.CatalogService) error {
		result := tx.LockClaimableJob(&job, now, request.SourceIDs)
		if errors.Is(result.Error, service.ErrRecordNotFound) {
			return nil
		}
		if result.Error != nil {
			return result.Error
		}
		if err := tx.GetSource(&source, job.SourceID).Error; err != nil {
			return err
		}
		var jobRequest map[string]any
		json.Unmarshal([]byte(job.RequestJSON), &jobRequest)
		if model.ValidateDigitalRetailRequest(source, job.Operation, jobRequest) != nil || model.IsRetailScrapeSource(source) || !source.Enabled || strings.ToLower(strings.TrimSpace(source.AccessMethod)) != "browser" {
			finished := now
			if err := tx.UpdateJob(&job, map[string]any{
				"status":       jobBlocked,
				"completed_at": finished,
				"last_error":   "source is retail, disabled or not browser-only",
			}).Error; err != nil {
				return err
			}
			return nil
		}
		leaseUntil := now.Add(time.Duration(leaseSeconds) * time.Second)
		leaseToken := model.ScrapeLeaseToken(job.ID, request.WorkerID, now)
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
		if err := tx.UpdateJob(&job, updates).Error; err != nil {
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
		if err := tx.CreateRun(&model.ScrapeRun{
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
	return c.JSON(http.StatusOK, model.ClaimScrapeJobResponse{
		Job:    job.Response(),
		Source: source.ResponseForScraper(),
	})
}

func (h *CatalogHandler) HeartbeatScrapeJob(c echo.Context) error {
	if err := h.checkScraperToken(c); err != nil {
		return err
	}
	var request model.HeartbeatScrapeJobRequest
	if err := json.NewDecoder(c.Request().Body).Decode(&request); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, "invalid heartbeat request")
	}
	request.WorkerID = strings.TrimSpace(request.WorkerID)
	request.LeaseToken = strings.TrimSpace(request.LeaseToken)
	if request.WorkerID == "" {
		return echo.NewHTTPError(http.StatusBadRequest, "workerId is required")
	}
	var job model.ScrapeJob
	result := h.service.GetJob(&job, c.Param("id"))
	if errors.Is(result.Error, service.ErrRecordNotFound) {
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
	leaseUntil := now.Add(time.Duration(model.ClampLeaseSeconds(request.LeaseSeconds)) * time.Second)
	if err := h.service.UpdateJob(&job, map[string]any{
		"leased_until":      leaseUntil,
		"last_heartbeat_at": now,
	}).Error; err != nil {
		return echo.NewHTTPError(http.StatusInternalServerError, "failed to heartbeat scrape job")
	}
	job.LeasedUntil = &leaseUntil
	job.LastHeartbeatAt = &now
	return c.JSON(http.StatusOK, job.Response())
}

func (h *CatalogHandler) CompleteScrapeJob(c echo.Context) error {
	if err := h.checkScraperToken(c); err != nil {
		return err
	}
	var request model.CompleteScrapeJobRequest
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
	var job model.ScrapeJob
	result := h.service.GetJob(&job, c.Param("id"))
	if errors.Is(result.Error, service.ErrRecordNotFound) {
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
			availableAt = now.Add(model.RetryDelay(job.AttemptCount))
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
	if err := h.service.Transaction(func(tx *service.CatalogService) error {
		if err := tx.UpdateJob(&job, updates).Error; err != nil {
			return err
		}
		var run model.ScrapeRun
		runResult := tx.GetRunningRun(&run, job.ID, request.WorkerID)
		if !errors.Is(runResult.Error, service.ErrRecordNotFound) {
			if runResult.Error != nil {
				return runResult.Error
			}
			if err := tx.UpdateRun(&run, map[string]any{
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

func (h *CatalogHandler) checkScraperToken(c echo.Context) error {
	if h.ingestSecret != "" && c.Request().Header.Get("X-Scraper-Token") != h.ingestSecret {
		return echo.NewHTTPError(http.StatusUnauthorized, "invalid scraper token")
	}
	return nil
}
