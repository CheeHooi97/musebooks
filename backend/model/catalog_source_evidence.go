package model

import "time"

// CatalogSourceEvidence preserves which registered route supplied each
// directly imported bibliographic, credit, or product-image field.
type CatalogSourceEvidence struct {
	ID         int64     `gorm:"primaryKey;autoIncrement" json:"id"`
	EntityType string    `gorm:"size:24;uniqueIndex:ux_catalog_source_evidence_capture,priority:1;not null" json:"entityType"`
	EntityID   string    `gorm:"size:240;uniqueIndex:ux_catalog_source_evidence_capture,priority:2;not null" json:"entityId"`
	FieldKey   string    `gorm:"size:180;uniqueIndex:ux_catalog_source_evidence_capture,priority:3;not null" json:"fieldKey"`
	SourceID   string    `gorm:"size:80;uniqueIndex:ux_catalog_source_evidence_capture,priority:4;not null" json:"sourceId"`
	CapturedAt time.Time `gorm:"uniqueIndex:ux_catalog_source_evidence_capture,priority:5;not null" json:"capturedAt"`
	GrantField string    `gorm:"size:64;not null" json:"grantField"`
	Scope      string    `gorm:"size:32;not null" json:"scope"`
	SourceURL  string    `gorm:"type:text;not null" json:"sourceUrl"`
	CreatedAt  time.Time `json:"createdAt"`
	UpdatedAt  time.Time `json:"updatedAt"`
}

func (CatalogSourceEvidence) TableName() string { return "catalog_source_evidence" }
