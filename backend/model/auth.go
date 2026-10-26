package model

import "time"

// AuthSession stores a revocable, opaque browser session. Only the SHA-256
// digest is persisted; the raw token is sent once to the browser in a cookie.
type AuthSession struct {
	TokenHash string    `gorm:"primaryKey;size:64" json:"-"`
	UserID    string    `gorm:"index;not null" json:"userId"`
	ExpiresAt time.Time `gorm:"index;not null" json:"expiresAt"`
	CreatedAt time.Time `json:"createdAt"`
}
