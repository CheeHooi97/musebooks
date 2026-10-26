package repository

import (
	"context"
	"errors"
	"musebooks/model"
	"time"

	"gorm.io/gorm"
)

type AuthSessionRepository interface {
	CreateSession(ctx context.Context, session *model.AuthSession) error
	GetSession(ctx context.Context, tokenHash string) (*model.AuthSession, error)
	DeleteSession(ctx context.Context, tokenHash string) error
	DeleteExpiredSessions(ctx context.Context, now time.Time) error
}

type authSessionRepository struct {
	db *gorm.DB
}

func NewAuthSessionRepository(db *gorm.DB) AuthSessionRepository {
	return &authSessionRepository{db: db}
}

func (r *authSessionRepository) CreateSession(ctx context.Context, session *model.AuthSession) error {
	return r.db.WithContext(ctx).Create(session).Error
}

func (r *authSessionRepository) GetSession(ctx context.Context, tokenHash string) (*model.AuthSession, error) {
	var session model.AuthSession
	if err := r.db.WithContext(ctx).Where("token_hash = ? AND expires_at > ?", tokenHash, time.Now().UTC()).First(&session).Error; err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, nil
		}
		return nil, err
	}
	return &session, nil
}

func (r *authSessionRepository) DeleteSession(ctx context.Context, tokenHash string) error {
	return r.db.WithContext(ctx).Where("token_hash = ?", tokenHash).Delete(&model.AuthSession{}).Error
}

func (r *authSessionRepository) DeleteSessionsForUser(ctx context.Context, userID string) error {
	return r.db.WithContext(ctx).Where("user_id = ?", userID).Delete(&model.AuthSession{}).Error
}

func (r *authSessionRepository) DeleteExpiredSessions(ctx context.Context, now time.Time) error {
	return r.db.WithContext(ctx).Where("expires_at <= ?", now.UTC()).Delete(&model.AuthSession{}).Error
}
