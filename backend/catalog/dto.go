package catalog

import (
	"strings"
	"time"
)

type BookResponse struct {
	ID            string            `json:"id"`
	Slug          string            `json:"slug"`
	OriginalTitle string            `json:"originalTitle"`
	EnglishTitle  string            `json:"englishTitle,omitempty"`
	Summary       string            `json:"summary,omitempty"`
	Origin        OriginResponse    `json:"origin"`
	FeaturedNames []string          `json:"featuredNames,omitempty"`
	Photographer  string            `json:"photographer,omitempty"`
	CoverURL      string            `json:"coverUrl,omitempty"`
	Editions      []EditionResponse `json:"editions"`
}

type OriginResponse struct {
	Code       string `json:"code"`
	Name       string `json:"name"`
	NativeName string `json:"nativeName,omitempty"`
	Count      int64  `json:"count,omitempty"`
}

type EditionResponse struct {
	ID               string            `json:"id"`
	Format           string            `json:"format"`
	Language         string            `json:"language,omitempty"`
	EditionMarket    string            `json:"editionMarket,omitempty"`
	Publisher        string            `json:"publisher,omitempty"`
	ReleaseDate      *time.Time        `json:"releaseDate,omitempty"`
	ReleasePrecision string            `json:"releasePrecision,omitempty"`
	ISBN             string            `json:"isbn,omitempty"`
	PageCount        int               `json:"pageCount,omitempty"`
	Dimensions       string            `json:"dimensions,omitempty"`
	EditionLabel     string            `json:"editionLabel"`
	CoverURL         string            `json:"coverUrl,omitempty"`
	Listings         []ListingResponse `json:"listings"`
}

type ListingResponse struct {
	ID             string         `json:"id"`
	ExternalID     string         `json:"externalId"`
	URL            string         `json:"url"`
	Title          string         `json:"title"`
	SellerLocation string         `json:"sellerLocation,omitempty"`
	Condition      string         `json:"condition,omitempty"`
	Format         string         `json:"format,omitempty"`
	DigitalAccess  string         `json:"digitalAccess,omitempty"`
	Status         string         `json:"status"`
	PriceMinor     int64          `json:"priceMinor,omitempty"`
	Currency       string         `json:"currency,omitempty"`
	PriceType      string         `json:"priceType,omitempty"`
	ShippingText   string         `json:"shippingText,omitempty"`
	ObservedAt     time.Time      `json:"observedAt"`
	LastSeenAt     time.Time      `json:"lastSeenAt"`
	Source         SourceResponse `json:"source"`
}

type SourceResponse struct {
	ID     string `json:"id"`
	Name   string `json:"name"`
	Region string `json:"region"`
	Kind   string `json:"kind"`
}

type ListBooksResponse struct {
	Items      []BookResponse `json:"items"`
	Page       int            `json:"page"`
	PageSize   int            `json:"pageSize"`
	Total      int64          `json:"total"`
	TotalPages int            `json:"totalPages"`
}

type ListBooksQuery struct {
	Query        string
	Origin       string
	Format       string
	Language     string
	Availability string
	Year         string
	Page         int
	PageSize     int
}

func (w Work) Response() BookResponse {
	result := BookResponse{
		ID:            w.ID,
		Slug:          w.Slug,
		OriginalTitle: w.OriginalTitle,
		EnglishTitle:  w.EnglishTitle,
		Summary:       w.Summary,
		Origin: OriginResponse{
			Code:       w.Origin.Code,
			Name:       w.Origin.Name,
			NativeName: w.Origin.NativeName,
		},
		FeaturedNames: splitNames(w.FeaturedNames),
		Photographer:  w.Photographer,
		CoverURL:      w.CoverURL,
		Editions:      make([]EditionResponse, 0, len(w.Editions)),
	}
	for _, edition := range w.Editions {
		result.Editions = append(result.Editions, edition.Response())
	}
	return result
}

func (e Edition) Response() EditionResponse {
	result := EditionResponse{
		ID:               e.ID,
		Format:           e.Format,
		Language:         e.Language,
		EditionMarket:    e.EditionMarket,
		Publisher:        e.Publisher,
		ReleaseDate:      e.ReleaseDate,
		ReleasePrecision: e.ReleasePrecision,
		ISBN:             e.ISBN,
		PageCount:        e.PageCount,
		Dimensions:       e.Dimensions,
		EditionLabel:     e.EditionLabel,
		CoverURL:         e.CoverURL,
		Listings:         make([]ListingResponse, 0, len(e.Listings)),
	}
	for _, listing := range e.Listings {
		result.Listings = append(result.Listings, listing.Response())
	}
	return result
}

func (l Listing) Response() ListingResponse {
	return ListingResponse{
		ID:             l.ID,
		ExternalID:     l.ExternalID,
		URL:            l.URL,
		Title:          l.Title,
		SellerLocation: l.SellerLocation,
		Condition:      l.Condition,
		Format:         l.FormatCandidate,
		DigitalAccess:  l.DigitalAccess,
		Status:         l.Status,
		PriceMinor:     l.PriceMinor,
		Currency:       l.Currency,
		PriceType:      l.PriceType,
		ShippingText:   l.ShippingText,
		ObservedAt:     l.ObservedAt,
		LastSeenAt:     l.LastSeenAt,
		Source: SourceResponse{
			ID:     l.Source.ID,
			Name:   l.Source.Name,
			Region: l.Source.Region,
			Kind:   l.Source.Kind,
		},
	}
}

func (o Origin) Response(count int64) OriginResponse {
	return OriginResponse{Code: o.Code, Name: o.Name, NativeName: o.NativeName, Count: count}
}

func splitNames(value string) []string {
	parts := strings.Split(value, ",")
	result := make([]string, 0, len(parts))
	for _, part := range parts {
		if name := strings.TrimSpace(part); name != "" {
			result = append(result, name)
		}
	}
	return result
}
