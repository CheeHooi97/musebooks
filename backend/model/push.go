package model

import "time"

// PushSubscription is one browser's Web Push subscription for the daily
// new-publications notification. As with MuseCards alerts, it belongs to a
// signed-in account and goes away with it.
type PushSubscription struct {
	ID        string    `gorm:"primaryKey;size:64" json:"-"` // sha256 of the endpoint
	UserID    string    `gorm:"index;not null" json:"-"`
	User      *User     `gorm:"foreignKey:UserID;references:Id;constraint:OnDelete:CASCADE" json:"-"`
	Endpoint  string    `gorm:"size:1000;not null" json:"-"`
	P256dh    string    `gorm:"size:120;not null" json:"-"`
	Auth      string    `gorm:"size:40;not null" json:"-"`
	Language  string    `gorm:"size:16;not null;default:en" json:"-"`
	Failures  int       `gorm:"not null;default:0" json:"-"`
	CreatedAt time.Time `json:"-"`
	UpdatedAt time.Time `json:"-"`
}

func (PushSubscription) TableName() string { return "push_subscriptions" }

// PushDigest records each new-publications run. The latest Through is the
// watermark: the next run covers works published after it.
type PushDigest struct {
	ID        int64     `gorm:"primaryKey"`
	Through   time.Time `gorm:"index;not null"`
	Count     int       `gorm:"not null"`
	Delivered int       `gorm:"not null"`
	CreatedAt time.Time
}

func (PushDigest) TableName() string { return "push_digests" }
