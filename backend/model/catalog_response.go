package model

import (
	"strings"
	"time"
)

type CatalogLink struct {
	ID   string `json:"id"`
	Name string `json:"name"`
}

type BookResponse struct {
	Models        []CatalogLink     `json:"models"`
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
	PublisherProfile  *CatalogLink      `json:"publisherProfile,omitempty"`
	ID                string            `json:"id"`
	Format            string            `json:"format"`
	Language          string            `json:"language,omitempty"`
	EditionMarket     string            `json:"editionMarket,omitempty"`
	Publisher         string            `json:"publisher,omitempty"`
	ReleaseDate       *time.Time        `json:"releaseDate,omitempty"`
	ReleasePrecision  string            `json:"releasePrecision,omitempty"`
	ISBN              string            `json:"isbn,omitempty"`
	PageCount         int               `json:"pageCount,omitempty"`
	Dimensions        string            `json:"dimensions,omitempty"`
	EditionVariant    string            `json:"editionVariant,omitempty"`
	ContentSummary    string            `json:"contentSummary,omitempty"`
	MetadataSourceURL string            `json:"metadataSourceUrl,omitempty"`
	SeriesName        string            `json:"seriesName,omitempty"`
	EditionLabel      string            `json:"editionLabel"`
	CoverURL          string            `json:"coverUrl,omitempty"`
	Listings          []ListingResponse `json:"listings"`
	ActiveListings    []ListingResponse `json:"activeListings"`
	SoldListings      []ListingResponse `json:"soldListings"`
	RetailOffers      []ListingResponse `json:"retailOffers"`
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
	PriceCategory  string         `json:"priceCategory"`
	ShippingText   string         `json:"shippingText,omitempty"`
	ObservedAt     time.Time      `json:"observedAt"`
	LastSeenAt     time.Time      `json:"lastSeenAt"`
	Source         SourceResponse `gorm:"embedded;embeddedPrefix:source_" json:"source"`
}

type SourceResponse struct {
	ID              string `json:"id"`
	Name            string `json:"name"`
	Region          string `json:"region"`
	Kind            string `json:"kind"`
	PhotobookFormat string `json:"photobookFormat,omitempty"`
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
		CoverURL:      PublicCoverURL(w.CoverURL),
		Editions:      make([]EditionResponse, 0, len(w.Editions)),
	}
	result.Models = []CatalogLink{}
	for _, credit := range w.Credits {
		if credit.Role == "featured" && credit.Person.Slug != "" {
			result.Models = append(result.Models, CatalogLink{ID: credit.Person.Slug, Name: credit.Person.CanonicalPublicName})
		}
	}
	for _, edition := range w.Editions {
		if edition.Status == "superseded" {
			continue
		}
		result.Editions = append(result.Editions, edition.Response())
	}
	return result
}

func (e Edition) Response() EditionResponse {
	result := EditionResponse{
		ID:                e.ID,
		Format:            e.Format,
		Language:          e.Language,
		EditionMarket:     e.EditionMarket,
		Publisher:         e.Publisher,
		ReleaseDate:       e.ReleaseDate,
		ReleasePrecision:  e.ReleasePrecision,
		ISBN:              e.ISBN,
		PageCount:         e.PageCount,
		Dimensions:        e.Dimensions,
		EditionVariant:    e.EditionVariant,
		ContentSummary:    e.ContentSummary,
		MetadataSourceURL: e.MetadataSourceURL,
		SeriesName:        e.SeriesName,
		EditionLabel:      e.EditionLabel,
		CoverURL:          PublicCoverURL(e.CoverURL),
		Listings:          make([]ListingResponse, 0, len(e.Listings)),
		ActiveListings:    []ListingResponse{},
		SoldListings:      []ListingResponse{},
		RetailOffers:      []ListingResponse{},
	}
	if e.PublisherCompany != nil {
		result.PublisherProfile = &CatalogLink{ID: e.PublisherCompany.Slug, Name: e.PublisherCompany.CanonicalName}
	}
	for _, listing := range e.Listings {
		if !listingMatchesEdition(listing, e.Format) {
			continue
		}
		response := listing.Response()
		result.Listings = append(result.Listings, response)
		switch response.PriceCategory {
		case "digital_retail", "physical_retail":
			result.RetailOffers = append(result.RetailOffers, response)
		case "marketplace_asking":
			if response.Status == "active" {
				result.ActiveListings = append(result.ActiveListings, response)
			}
		case "marketplace_sold":
			result.SoldListings = append(result.SoldListings, response)
		}
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
		Format:         listingPhotobookFormat(l),
		DigitalAccess:  l.DigitalAccess,
		Status:         l.Status,
		PriceMinor:     l.PriceMinor,
		Currency:       l.Currency,
		PriceType:      l.PriceType,
		PriceCategory:  listingPriceCategory(l),
		ShippingText:   l.ShippingText,
		ObservedAt:     l.ObservedAt,
		LastSeenAt:     l.LastSeenAt,
		Source: SourceResponse{
			ID:              l.Source.ID,
			Name:            l.Source.Name,
			Region:          l.Source.Region,
			Kind:            l.Source.Kind,
			PhotobookFormat: SourcePhotobookFormat(l.Source),
		},
	}
}

func listingPhotobookFormat(listing Listing) string {
	if value := NormalizeFormat(listing.FormatCandidate); value != "" {
		return value
	}
	if strings.TrimSpace(listing.FormatCandidate) != "" {
		return ""
	}
	// Legacy records can be classified only from a compatible source/price.
	if listing.PriceType == "digital" {
		return formatDigital
	}
	if IsPhysicalMarketplaceSource(listing.Source) {
		return formatPhysical
	}
	if listing.PriceType == "" {
		return SourcePhotobookFormat(listing.Source)
	}
	return ""
}

func listingMatchesEdition(listing Listing, editionFormat string) bool {
	if listing.Status == "excluded" {
		return false
	}
	format := listingPhotobookFormat(listing)
	if format == "" || format != NormalizeFormat(editionFormat) {
		return false
	}
	if expected := SourcePhotobookFormat(listing.Source); expected == "" || expected != format {
		return false
	}
	_, err := ValidateObservationPrice(format, listing.Status, listing.PriceType)
	return err == nil
}

func listingPriceCategory(listing Listing) string {
	if listingPhotobookFormat(listing) == formatDigital {
		return "digital_retail"
	}
	if isPhysicalRetailSource(listing.Source) {
		return "physical_retail"
	}
	if listing.Status == "completed" {
		return "marketplace_sold"
	}
	return "marketplace_asking"
}

func isPhysicalRetailSource(source Source) bool {
	return strings.EqualFold(strings.TrimSpace(source.Kind), "bookstore") && SourcePhotobookFormat(source) == formatPhysical
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
