package worker

import (
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"strings"
	"time"

	"github.com/playwright-community/playwright-go"
)

const parserVersion = "generic-anchor-v1"

func Run(request Request) (Batch, error) {
	if strings.TrimSpace(request.URL) == "" {
		return Batch{}, errors.New("url is required")
	}
	if request.PageSize <= 0 || request.PageSize > 100 {
		request.PageSize = 30
	}
	if request.MaxPages <= 0 || request.MaxPages > 20 {
		request.MaxPages = 1
	}
	if request.JobID == "" {
		request.JobID = fmt.Sprintf("scrape-%d", time.Now().UnixNano())
	}
	if request.SourceID == "" {
		request.SourceID = request.Source
	}

	batch := Batch{
		JobID:         request.JobID,
		WorkerID:      request.WorkerID,
		LeaseToken:    request.LeaseToken,
		SourceID:      request.SourceID,
		ParserVersion: parserVersion,
		RetrievedAt:   time.Now().UTC(),
		Items:         make([]Observation, 0),
		Diagnostics: map[string]any{
			"requestedPages": request.MaxPages,
			"source":         request.SourceID,
		},
	}

	pw, err := playwright.Run()
	if err != nil {
		return batch, fmt.Errorf("start playwright: %w", err)
	}
	defer pw.Stop()

	browser, err := pw.Chromium.Launch(playwright.BrowserTypeLaunchOptions{
		Headless: playwright.Bool(true),
	})
	if err != nil {
		return batch, fmt.Errorf("launch chromium: %w", err)
	}
	defer browser.Close()

	page, err := browser.NewPage()
	if err != nil {
		return batch, fmt.Errorf("create page: %w", err)
	}

	seen := make(map[string]struct{})
	for pageNumber := 1; pageNumber <= request.MaxPages; pageNumber++ {
		pageURL := addPageParam(request.URL, pageNumber)
		if _, err := page.Goto(pageURL); err != nil {
			batch.Warnings = append(batch.Warnings, fmt.Sprintf("page %d: %v", pageNumber, err))
			continue
		}

		anchors, err := page.Locator("a").All()
		if err != nil {
			batch.Warnings = append(batch.Warnings, fmt.Sprintf("page %d anchors: %v", pageNumber, err))
			continue
		}
		pageItems := 0
		for _, anchor := range anchors {
			href, err := anchor.GetAttribute("href")
			if err != nil || href == "" {
				continue
			}
			text, err := anchor.InnerText()
			if err != nil {
				continue
			}
			item, ok := normalizeAnchor(href, pageURL, text, batch.RetrievedAt)
			if !ok {
				continue
			}
			if format := normalizeFormat(request.Format); format != "" {
				item.Format = format
			} else if isDigitalSource(request.SourceID) {
				item.Format = "digital"
			}
			if request.DigitalAccess != "" {
				item.DigitalAccess = request.DigitalAccess
			}
			if _, exists := seen[item.ExternalID]; exists {
				continue
			}
			seen[item.ExternalID] = struct{}{}
			batch.Items = append(batch.Items, item)
			pageItems++
			if pageItems >= request.PageSize {
				break
			}
		}
		batch.Diagnostics[fmt.Sprintf("page_%d_items", pageNumber)] = pageItems
	}
	batch.Diagnostics["items"] = len(batch.Items)

	if request.IngestURL != "" && len(batch.Items) > 0 {
		if err := ingest(request.IngestURL, request.IngestToken, batch); err != nil {
			return batch, err
		}
	}
	return batch, nil
}

func ingest(endpoint, token string, batch Batch) error {
	payload, err := json.Marshal(batch)
	if err != nil {
		return fmt.Errorf("encode ingest batch: %w", err)
	}
	req, err := http.NewRequest(http.MethodPost, endpoint, bytes.NewReader(payload))
	if err != nil {
		return fmt.Errorf("create ingest request: %w", err)
	}
	req.Header.Set("Content-Type", "application/json")
	if token != "" {
		req.Header.Set("X-Scraper-Token", token)
	}
	response, err := http.DefaultClient.Do(req)
	if err != nil {
		return fmt.Errorf("send ingest batch: %w", err)
	}
	defer response.Body.Close()
	if response.StatusCode < 200 || response.StatusCode >= 300 {
		return fmt.Errorf("ingest returned status %s", response.Status)
	}
	return nil
}

func addPageParam(rawURL string, page int) string {
	separator := "?"
	if strings.Contains(rawURL, "?") {
		separator = "&"
	}
	return fmt.Sprintf("%s%spage=%d", rawURL, separator, page)
}

func normalizeFormat(value string) string {
	switch strings.ToLower(strings.TrimSpace(value)) {
	case "physical", "print", "printed", "hardcopy", "paper":
		return "physical"
	case "digital", "ebook", "e-book", "epub", "pdf":
		return "digital"
	default:
		return ""
	}
}

func isDigitalSource(sourceID string) bool {
	lower := strings.ToLower(sourceID)
	return strings.Contains(lower, "bookwalker") || strings.Contains(lower, "digital")
}
