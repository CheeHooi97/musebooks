package model

import "time"

type User struct {
	Id                         string     `gorm:"primaryKey" json:"id"`
	CompanyId                  string     `json:"companyId"`
	Username                   string     `json:"username"`
	Email                      string     `json:"email"`
	EmailVerified              *bool      `gorm:"not null;default:false" json:"emailVerified"`
	PasswordHash               string     `gorm:"type:text" json:"-"`
	GoogleSubject              string     `gorm:"type:text" json:"-"`
	EmailVerificationCodeHash  string     `gorm:"type:text" json:"-"`
	EmailVerificationExpiresAt *time.Time `json:"-"`
	EmailVerificationSentAt    *time.Time `json:"-"`
	EmailVerificationAttempts  int        `gorm:"not null;default:0" json:"-"`
	PasswordResetCodeHash      string     `gorm:"type:text" json:"-"`
	PasswordResetExpiresAt     *time.Time `json:"-"`
	PasswordResetSentAt        *time.Time `json:"-"`
	PasswordResetAttempts      int        `gorm:"not null;default:0" json:"-"`
	PhotoURL                   string     `json:"photoUrl" sqlike:",longtext"`
	FcmToken                   string     `json:"fcmToken"`
	Status                     bool       `json:"status"`
	BaseModel
}

func (m *User) DateTime() {
	m.CreatedDateTime = time.Now().UTC()
	m.UpdatedDateTime = time.Now().UTC()
}

func (m *User) UpdateDt() {
	m.UpdatedDateTime = time.Now().UTC()
}
