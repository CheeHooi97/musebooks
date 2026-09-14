package worker

import "time"

type Request struct {
	JobID         string `json:"jobId"`
	WorkerID      string `json:"workerId,omitempty"`
	LeaseToken    string `json:"leaseToken,omitempty"`
	SourceID      string `json:"sourceId"`
	Source        string `json:"source"`
	URL           string `json:"url"`
	Query         string `json:"query"`
	PageSize      int    `json:"pageSize"`
	MaxPages      int    `json:"maxPages"`
	Format        string `json:"format,omitempty"`
	DigitalAccess string `json:"digitalAccess,omitempty"`
	IngestURL     string `json:"ingestUrl"`
	IngestToken   string `json:"-"`
}

type Batch struct {
	JobID         string         `json:"jobId"`
	WorkerID      string         `json:"workerId,omitempty"`
	LeaseToken    string         `json:"leaseToken,omitempty"`
	SourceID      string         `json:"sourceId"`
	ParserVersion string         `json:"parserVersion"`
	RetrievedAt   time.Time      `json:"retrievedAt"`
	NextCursor    string         `json:"nextCursor,omitempty"`
	HasMore       bool           `json:"hasMore,omitempty"`
	Items         []Observation  `json:"items"`
	Warnings      []string       `json:"warnings,omitempty"`
	Diagnostics   map[string]any `json:"diagnostics,omitempty"`
}

type Observation struct {
	ObservationID  string    `json:"observationId,omitempty"`
	ExternalID     string    `json:"externalId"`
	URL            string    `json:"url"`
	Title          string    `json:"title"`
	SellerLocation string    `json:"sellerLocation,omitempty"`
	Condition      string    `json:"condition,omitempty"`
	Status         string    `json:"status,omitempty"`
	PriceMinor     int64     `json:"priceMinor,omitempty"`
	Currency       string    `json:"currency,omitempty"`
	PriceType      string    `json:"priceType,omitempty"`
	Format         string    `json:"format"`
	DigitalAccess  string    `json:"digitalAccess,omitempty"`
	ShippingText   string    `json:"shippingText,omitempty"`
	ImageURL       string    `json:"imageUrl,omitempty"`
	ObservedAt     time.Time `json:"observedAt"`
}
