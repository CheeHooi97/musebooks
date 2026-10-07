package model

import (
	"crypto/sha256"
	"fmt"
	"strings"
	"time"
)

// CatalogIdentity preserves the directory links issued before normalization.
func CatalogIdentity(kind, name string) string {
	return fmt.Sprintf("%s-%x", kind, sha256.Sum256([]byte(strings.ToLower(strings.TrimSpace(name)))))
}

type Market struct {
	ID                  int64     `gorm:"primaryKey;autoIncrement" json:"id"`
	CountryCode         string    `gorm:"size:32;uniqueIndex;not null" json:"countryCode"`
	Slug                string    `gorm:"size:80;uniqueIndex;not null" json:"slug"`
	DefaultLocale       string    `gorm:"size:32" json:"defaultLocale"`
	DefaultCurrencyCode string    `gorm:"size:8" json:"defaultCurrencyCode"`
	PrimaryTimezone     string    `gorm:"size:64" json:"primaryTimezone"`
	CatalogStatus       string    `gorm:"size:24;index;default:active" json:"catalogStatus"`
	CreatedAt           time.Time `json:"createdAt"`
	UpdatedAt           time.Time `json:"updatedAt"`
}
type Person struct {
	ID                      int64     `gorm:"primaryKey;autoIncrement" json:"id"`
	Slug                    string    `gorm:"size:100;uniqueIndex;not null" json:"slug"`
	CanonicalPublicName     string    `gorm:"type:text;index;not null" json:"canonicalPublicName"`
	OriginalName            string    `gorm:"type:text" json:"originalName"`
	EnglishName             string    `gorm:"type:text" json:"englishName"`
	TraditionalChineseName  string    `gorm:"type:text" json:"traditionalChineseName"`
	SimplifiedChineseName   string    `gorm:"type:text" json:"simplifiedChineseName"`
	PersonType              string    `gorm:"size:32;index" json:"personType"`
	VerificationSourceURL   string    `gorm:"type:text" json:"verificationSourceUrl"`
	ProfileSourceConfidence string    `gorm:"size:40" json:"profileSourceConfidence"`
	CreatedAt               time.Time `json:"createdAt"`
	UpdatedAt               time.Time `json:"updatedAt"`
}
type WorkPerson struct {
	WorkID       string    `gorm:"primaryKey;size:100" json:"workId"`
	PersonID     int64     `gorm:"primaryKey" json:"personId"`
	Role         string    `gorm:"primaryKey;size:32" json:"role"`
	CreditedName string    `gorm:"type:text" json:"creditedName"`
	CreditSource string    `gorm:"size:32;not null;default:legacy_credit" json:"creditSource"`
	Work         Work      `gorm:"foreignKey:WorkID" json:"-"`
	Person       Person    `gorm:"foreignKey:PersonID" json:"person"`
	CreatedAt    time.Time `json:"createdAt"`
	UpdatedAt    time.Time `json:"updatedAt"`
}
type ProductLine struct {
	ID                 int64     `gorm:"primaryKey;autoIncrement" json:"id"`
	Slug               string    `gorm:"size:100;uniqueIndex;not null" json:"slug"`
	CanonicalName      string    `gorm:"type:text;index;not null" json:"canonicalName"`
	PublisherCompanyID *string   `gorm:"size:100;index" json:"publisherCompanyId"`
	PublisherCompany   *Company  `gorm:"foreignKey:PublisherCompanyID" json:"publisherCompany,omitempty"`
	CreatedAt          time.Time `json:"createdAt"`
	UpdatedAt          time.Time `json:"updatedAt"`
}
type Marketplace struct {
	ID        int64     `gorm:"primaryKey;autoIncrement" json:"id"`
	Code      string    `gorm:"size:80;uniqueIndex;not null" json:"code"`
	Name      string    `gorm:"size:120;not null" json:"name"`
	Region    string    `gorm:"size:32;index" json:"region"`
	CreatedAt time.Time `json:"createdAt"`
	UpdatedAt time.Time `json:"updatedAt"`
}
type CatalogMedia struct {
	ID          int64     `gorm:"primaryKey;autoIncrement" json:"id"`
	EntityType  string    `gorm:"size:24;uniqueIndex:ux_catalog_media_entity,priority:1;not null" json:"entityType"`
	EntityID    string    `gorm:"size:100;uniqueIndex:ux_catalog_media_entity,priority:2;not null" json:"entityId"`
	MediaType   string    `gorm:"size:32;uniqueIndex:ux_catalog_media_entity,priority:3;not null" json:"mediaType"`
	OriginalURL string    `gorm:"type:text" json:"originalUrl"`
	StorageURL  string    `gorm:"type:text" json:"storageUrl"`
	SourceURL   string    `gorm:"type:text" json:"sourceUrl"`
	IsPrimary   bool      `json:"isPrimary"`
	CreatedAt   time.Time `json:"createdAt"`
	UpdatedAt   time.Time `json:"updatedAt"`
}

func (CatalogMedia) TableName() string { return "catalog_media" }

type ListingMatch struct {
	ID              int64     `gorm:"primaryKey;autoIncrement" json:"id"`
	SourceListingID string    `gorm:"size:180;uniqueIndex;not null" json:"sourceListingId"`
	EditionID       string    `gorm:"size:100;index;not null" json:"editionId"`
	Edition         Edition   `gorm:"foreignKey:EditionID" json:"edition"`
	MatchMethod     string    `gorm:"size:40" json:"matchMethod"`
	ReviewStatus    string    `gorm:"size:24;index" json:"reviewStatus"`
	CreatedAt       time.Time `json:"createdAt"`
	UpdatedAt       time.Time `json:"updatedAt"`
}
