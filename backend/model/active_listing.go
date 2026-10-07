package model

import "time"

// ListingRecord is shared storage shape, not a shared active/sold lifecycle.
// SourceListingID retains the canonical ingestion identity and existing links.
type ListingRecord struct {
	ID                   int64       `gorm:"primaryKey;autoIncrement" json:"id"`
	SourceListingID      string      `gorm:"size:180;uniqueIndex;not null" json:"sourceListingId"`
	MarketplaceID        int64       `gorm:"index;not null" json:"marketplaceId"`
	SourceID             string      `gorm:"size:80;index;not null" json:"sourceId"`
	ExternalListingID    string      `gorm:"size:180;not null" json:"externalListingId"`
	EditionID            *string     `gorm:"size:100;index" json:"editionId,omitempty"`
	OriginalURL          string      `gorm:"type:text" json:"originalUrl"`
	Title                string      `gorm:"type:text" json:"title"`
	Format               string      `gorm:"size:16;index" json:"format"`
	PriceMinor           *int64      `json:"priceMinor,omitempty"`
	OriginalCurrencyCode string      `gorm:"size:8" json:"originalCurrencyCode"`
	PriceType            string      `gorm:"size:24" json:"priceType"`
	Condition            string      `gorm:"size:80" json:"condition"`
	SellerLocation       string      `gorm:"size:120" json:"sellerLocation"`
	ShippingText         string      `gorm:"size:240" json:"shippingText"`
	ObservedAt           time.Time   `gorm:"index;not null" json:"observedAt"`
	LastSeenAt           time.Time   `json:"lastSeenAt"`
	Source               Source      `gorm:"foreignKey:SourceID" json:"source"`
	Marketplace          Marketplace `gorm:"foreignKey:MarketplaceID" json:"marketplace"`
	CreatedAt            time.Time   `json:"createdAt"`
	UpdatedAt            time.Time   `json:"updatedAt"`
}
type ActiveListing struct {
	ListingRecord  `gorm:"embedded;embeddedPrefix:"`
	IsActive       bool       `gorm:"index;not null;default:true" json:"isActive"`
	ActiveAt       time.Time  `gorm:"index;not null" json:"activeAt"`
	InactiveAt     *time.Time `json:"inactiveAt,omitempty"`
	InactiveReason string     `gorm:"size:32" json:"inactiveReason"`
}
