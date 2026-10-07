package model

import "time"

type ObservationBatch struct {
	JobID         string             `json:"jobId"`
	WorkerID      string             `json:"workerId,omitempty"`
	LeaseToken    string             `json:"leaseToken,omitempty"`
	SourceID      string             `json:"sourceId"`
	ParserVersion string             `json:"parserVersion"`
	RetrievedAt   time.Time          `json:"retrievedAt"`
	PageNumber    int                `json:"pageNumber,omitempty"`
	NextCursor    string             `json:"nextCursor,omitempty"`
	HasMore       bool               `json:"hasMore,omitempty"`
	Items         []ObservationInput `json:"items"`
	Warnings      []string           `json:"warnings,omitempty"`
	Diagnostics   map[string]any     `json:"diagnostics,omitempty"`
}

type ObservationInput struct {
	ObservationID      string     `json:"observationId,omitempty"`
	ExternalID         string     `json:"externalId"`
	EditionID          string     `json:"editionId,omitempty"`
	URL                string     `json:"url"`
	Title              string     `json:"title"`
	SellerLocation     string     `json:"sellerLocation,omitempty"`
	Condition          string     `json:"condition,omitempty"`
	Status             string     `json:"status"`
	PriceMinor         int64      `json:"priceMinor,omitempty"`
	Currency           string     `json:"currency,omitempty"`
	PriceType          string     `json:"priceType,omitempty"`
	Format             string     `json:"format"`
	DigitalAccess      string     `json:"digitalAccess,omitempty"`
	ISBN               string     `json:"isbn,omitempty"`
	Publisher          string     `json:"publisher,omitempty"`
	EditionVariant     string     `json:"editionVariant,omitempty"`
	ShippingText       string     `json:"shippingText,omitempty"`
	ImageURL           string     `json:"imageUrl,omitempty"`
	ObservedAt         time.Time  `json:"observedAt"`
	StatusEvidence     string     `json:"statusEvidence,omitempty"`
	SourceTimestamp    *time.Time `json:"sourceTimestamp,omitempty"`
	TimestampPrecision string     `json:"timestampPrecision,omitempty"`
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
