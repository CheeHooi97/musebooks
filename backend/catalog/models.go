package catalog

import "time"

type Origin struct {
	Code       string    `gorm:"primaryKey;size:32" json:"code"`
	Name       string    `gorm:"size:80;not null" json:"name"`
	NativeName string    `gorm:"size:80" json:"nativeName,omitempty"`
	SortOrder  int       `json:"sortOrder"`
	CreatedAt  time.Time `json:"createdAt"`
	UpdatedAt  time.Time `json:"updatedAt"`
}

type Source struct {
	ID             string     `gorm:"primaryKey;size:80" json:"id"`
	Name           string     `gorm:"size:120;not null" json:"name"`
	Region         string     `gorm:"size:32;index" json:"region"`
	Locale         string     `gorm:"size:32" json:"locale"`
	Timezone       string     `gorm:"size:64" json:"timezone"`
	Kind           string     `gorm:"size:32" json:"kind"`
	Adapter        string     `gorm:"size:64" json:"adapter"`
	AccessMethod   string     `gorm:"size:32" json:"accessMethod"`
	DefaultFormat  string     `gorm:"size:16" json:"defaultFormat"`
	AllowedFormats string     `gorm:"size:64" json:"allowedFormats"`
	BaseURL        string     `gorm:"size:255" json:"baseUrl"`
	AllowedHosts   string     `gorm:"type:text" json:"allowedHosts,omitempty"`
	Capabilities   string     `gorm:"type:text" json:"capabilities,omitempty"`
	AccessStatus   string     `gorm:"size:24;index;default:pending" json:"accessStatus"`
	TermsURL       string     `gorm:"size:500" json:"termsUrl,omitempty"`
	RatePerMinute  int        `gorm:"default:30" json:"ratePerMinute"`
	Enabled        bool       `gorm:"index;default:true" json:"enabled"`
	LastCheckedAt  *time.Time `json:"lastCheckedAt,omitempty"`
	CreatedAt      time.Time  `json:"createdAt"`
	UpdatedAt      time.Time  `json:"updatedAt"`
}

type Work struct {
	ID            string    `gorm:"primaryKey;size:100" json:"id"`
	Slug          string    `gorm:"uniqueIndex;size:140;not null" json:"slug"`
	OriginalTitle string    `gorm:"size:240;not null" json:"originalTitle"`
	EnglishTitle  string    `gorm:"size:240" json:"englishTitle,omitempty"`
	Summary       string    `gorm:"type:text" json:"summary,omitempty"`
	OriginCode    string    `gorm:"size:32;index;not null" json:"originCode"`
	FeaturedNames string    `gorm:"type:text" json:"featuredNames,omitempty"`
	Photographer  string    `gorm:"size:160" json:"photographer,omitempty"`
	CoverURL      string    `gorm:"size:500" json:"coverUrl,omitempty"`
	Status        string    `gorm:"size:24;index;default:published" json:"status"`
	Origin        Origin    `gorm:"foreignKey:OriginCode;references:Code" json:"origin"`
	Editions      []Edition `gorm:"foreignKey:WorkID" json:"editions,omitempty"`
	CreatedAt     time.Time `json:"createdAt"`
	UpdatedAt     time.Time `json:"updatedAt"`
}

type Edition struct {
	ID               string     `gorm:"primaryKey;size:100" json:"id"`
	WorkID           string     `gorm:"size:100;index;not null" json:"workId"`
	Format           string     `gorm:"size:32;index;not null" json:"format"`
	Language         string     `gorm:"size:32;index" json:"language"`
	EditionMarket    string     `gorm:"size:32;index" json:"editionMarket"`
	Publisher        string     `gorm:"size:160" json:"publisher,omitempty"`
	ReleaseDate      *time.Time `gorm:"index" json:"releaseDate,omitempty"`
	ReleasePrecision string     `gorm:"size:16" json:"releasePrecision,omitempty"`
	ISBN             string     `gorm:"size:32;index" json:"isbn,omitempty"`
	PageCount        int        `json:"pageCount,omitempty"`
	Dimensions       string     `gorm:"size:80" json:"dimensions,omitempty"`
	EditionLabel     string     `gorm:"size:180" json:"editionLabel"`
	CoverURL         string     `gorm:"size:500" json:"coverUrl,omitempty"`
	Status           string     `gorm:"size:24;index;default:published" json:"status"`
	Listings         []Listing  `gorm:"foreignKey:EditionID" json:"listings,omitempty"`
	CreatedAt        time.Time  `json:"createdAt"`
	UpdatedAt        time.Time  `json:"updatedAt"`
}

type Listing struct {
	ID              string    `gorm:"primaryKey;size:180" json:"id"`
	EditionID       string    `gorm:"size:100;index" json:"editionId,omitempty"`
	SourceID        string    `gorm:"size:80;index;uniqueIndex:idx_listing_source_external;not null" json:"sourceId"`
	ExternalID      string    `gorm:"size:180;uniqueIndex:idx_listing_source_external;not null" json:"externalId"`
	URL             string    `gorm:"size:1000;not null" json:"url"`
	Title           string    `gorm:"size:300;not null" json:"title"`
	SellerLocation  string    `gorm:"size:120" json:"sellerLocation,omitempty"`
	Condition       string    `gorm:"size:80" json:"condition,omitempty"`
	FormatCandidate string    `gorm:"size:16;index" json:"formatCandidate,omitempty"`
	DigitalAccess   string    `gorm:"size:24" json:"digitalAccess,omitempty"`
	Status          string    `gorm:"size:24;index;default:unknown" json:"status"`
	PriceMinor      int64     `json:"priceMinor,omitempty"`
	Currency        string    `gorm:"size:8" json:"currency,omitempty"`
	PriceType       string    `gorm:"size:24" json:"priceType,omitempty"`
	ShippingText    string    `gorm:"size:240" json:"shippingText,omitempty"`
	ImageURL        string    `gorm:"size:500" json:"imageUrl,omitempty"`
	ObservedAt      time.Time `gorm:"index" json:"observedAt"`
	LastSeenAt      time.Time `gorm:"index" json:"lastSeenAt"`
	Source          Source    `gorm:"foreignKey:SourceID;references:ID" json:"source"`
	CreatedAt       time.Time `json:"createdAt"`
	UpdatedAt       time.Time `json:"updatedAt"`
}

// ScrapeJob is the durable hand-off between the Go API and a marketplace
// adapter. RequestJSON is deliberately source-specific: the API validates the
// envelope and the worker owns the adapter payload.
type ScrapeJob struct {
	ID              string     `gorm:"primaryKey;size:120" json:"id"`
	SourceID        string     `gorm:"size:80;index;not null" json:"sourceId"`
	Operation       string     `gorm:"size:32;index;not null" json:"operation"`
	RequestJSON     string     `gorm:"type:jsonb;not null" json:"request"`
	Status          string     `gorm:"size:24;index;not null" json:"status"`
	Priority        int        `gorm:"index;default:0" json:"priority"`
	PageCursor      string     `gorm:"size:500" json:"pageCursor,omitempty"`
	WorkerID        string     `gorm:"size:120;index" json:"workerId,omitempty"`
	LeaseToken      string     `gorm:"size:100" json:"leaseToken,omitempty"`
	AttemptCount    int        `gorm:"default:0" json:"attemptCount"`
	MaxAttempts     int        `gorm:"default:3" json:"maxAttempts"`
	AvailableAt     time.Time  `gorm:"index" json:"availableAt"`
	LeasedUntil     *time.Time `gorm:"index" json:"leasedUntil,omitempty"`
	LastHeartbeatAt *time.Time `json:"lastHeartbeatAt,omitempty"`
	StartedAt       *time.Time `json:"startedAt,omitempty"`
	CompletedAt     *time.Time `json:"completedAt,omitempty"`
	LastError       string     `gorm:"type:text" json:"lastError,omitempty"`
	CreatedAt       time.Time  `json:"createdAt"`
	UpdatedAt       time.Time  `json:"updatedAt"`
	Source          Source     `gorm:"foreignKey:SourceID;references:ID" json:"source,omitempty"`
}

type ScrapeRun struct {
	ID            string     `gorm:"primaryKey;size:120" json:"id"`
	JobID         string     `gorm:"size:120;index;not null" json:"jobId"`
	WorkerID      string     `gorm:"size:120;index" json:"workerId"`
	Status        string     `gorm:"size:24;index;not null" json:"status"`
	ItemsReceived int        `json:"itemsReceived"`
	ItemsAccepted int        `json:"itemsAccepted"`
	ItemsRejected int        `json:"itemsRejected"`
	NextCursor    string     `gorm:"size:500" json:"nextCursor,omitempty"`
	Warnings      string     `gorm:"type:text" json:"warnings,omitempty"`
	Error         string     `gorm:"type:text" json:"error,omitempty"`
	StartedAt     time.Time  `json:"startedAt"`
	FinishedAt    *time.Time `json:"finishedAt,omitempty"`
	CreatedAt     time.Time  `json:"createdAt"`
	UpdatedAt     time.Time  `json:"updatedAt"`
}

// ListingObservation preserves price/status history while Listing remains the
// current projection used by the public catalog.
type ListingObservation struct {
	ID                 string     `gorm:"primaryKey;size:180" json:"id"`
	ObservationKey     string     `gorm:"size:220;uniqueIndex;not null" json:"observationKey"`
	ListingID          string     `gorm:"size:180;index;not null" json:"listingId"`
	JobID              string     `gorm:"size:120;index" json:"jobId,omitempty"`
	ParserVersion      string     `gorm:"size:64" json:"parserVersion,omitempty"`
	ObservedAt         time.Time  `gorm:"index;not null" json:"observedAt"`
	Status             string     `gorm:"size:24" json:"status"`
	Format             string     `gorm:"size:16;index" json:"format"`
	DigitalAccess      string     `gorm:"size:24" json:"digitalAccess,omitempty"`
	PriceMinor         int64      `json:"priceMinor,omitempty"`
	Currency           string     `gorm:"size:8" json:"currency,omitempty"`
	PriceType          string     `gorm:"size:24" json:"priceType,omitempty"`
	ShippingText       string     `gorm:"size:240" json:"shippingText,omitempty"`
	StatusEvidence     string     `gorm:"type:text" json:"statusEvidence,omitempty"`
	SourceTimestamp    *time.Time `json:"sourceTimestamp,omitempty"`
	TimestampPrecision string     `gorm:"size:16" json:"timestampPrecision,omitempty"`
	CreatedAt          time.Time  `json:"createdAt"`
	UpdatedAt          time.Time  `json:"updatedAt"`
}
