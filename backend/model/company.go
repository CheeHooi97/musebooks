package model

import "time"

type Company struct {
	Id                 string `gorm:"primaryKey;size:100" json:"id"`
	Slug               string `gorm:"size:100;index" json:"slug"`
	CanonicalName      string `gorm:"size:240;index" json:"canonicalName"`
	CountryCode        string `gorm:"size:32;index" json:"countryCode"`
	OfficialURL        string `gorm:"type:text" json:"officialUrl"`
	VerificationStatus string `gorm:"size:32;index" json:"verificationStatus"`
	Name               string `json:"name"`
	Host               string `json:"host"`
	Status             bool   `json:"status"`
	AppId              string `json:"appId"`
	AppKey             string `json:"appKey"`
	BaseModel
}

func (m *Company) DateTime() {
	m.CreatedDateTime = time.Now().UTC()
	m.UpdatedDateTime = time.Now().UTC()
}

func (m *Company) UpdateDt() {
	m.UpdatedDateTime = time.Now().UTC()
}
