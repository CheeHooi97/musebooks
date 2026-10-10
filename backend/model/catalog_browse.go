package model

type DirectoryEntry struct {
	OfficialURL  string `json:"officialUrl,omitempty"`
	OriginalName string `json:"originalName,omitempty"`
	EnglishName  string `json:"englishName,omitempty"`
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
type MarketplaceListingEntry struct {
	ListingResponse `gorm:"embedded"`
	ImageURL        string `json:"imageUrl,omitempty"`
	CatalogMatched  bool   `json:"catalogMatched"`
	WorkTitle       string `json:"workTitle,omitempty"`
	WorkSlug        string `json:"workSlug,omitempty"`
	EditionLabel    string `json:"editionLabel,omitempty"`
	Publisher       string `json:"publisher,omitempty"`
}
type CatalogBrowseQuery struct {
	Query, Kind, ID, Status, Format, Source, Person, Publisher, Language, Year, Region string
	Page, PageSize                                                                     int
}

func (entry *MarketEntry) SetFeaturedNames() {
	entry.FeaturedNames = splitNames(entry.FeaturedNamesText)
}
