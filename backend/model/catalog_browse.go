package model

type DirectoryEntry struct {
	ID           string `json:"id"`
	Name         string `json:"name"`
	WorkCount    int    `json:"workCount"`
	EditionCount int    `json:"editionCount"`
	CoverURL     string `json:"coverUrl,omitempty"`
}
type MarketEntry struct {
	ListingResponse   `gorm:"embedded"`
	WorkID            string   `json:"workId"`
	WorkSlug          string   `json:"workSlug"`
	WorkTitle         string   `json:"workTitle"`
	FeaturedNames     []string `gorm:"-" json:"featuredNames"`
	FeaturedNamesText string   `json:"-"`
	EditionID         string   `json:"editionId"`
	EditionLabel      string   `json:"editionLabel"`
	Publisher         string   `json:"publisher,omitempty"`
	CoverURL          string   `json:"coverUrl,omitempty"`
}
type CatalogBrowseQuery struct {
	Query, Kind, ID, Status, Format, Source, Person, Publisher string
	Page, PageSize                                             int
}

func (entry *MarketEntry) SetFeaturedNames() {
	entry.FeaturedNames = splitNames(entry.FeaturedNamesText)
}
