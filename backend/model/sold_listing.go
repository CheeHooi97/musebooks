package model

import "time"

type SoldListing struct {
	ListingRecord  `gorm:"embedded;embeddedPrefix:"`
	SoldAt         *time.Time `gorm:"index" json:"soldAt,omitempty"`
	StatusEvidence string     `gorm:"type:text" json:"statusEvidence"`
	ReviewStatus   string     `gorm:"size:24;index;not null;default:linked" json:"reviewStatus"`
}
