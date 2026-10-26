package repository

import (
	"context"
	"errors"
	"musebooks/model"

	"gorm.io/gorm"
)

// Serialize code consumption, resend cooldowns and account creation across
// API processes. All auth mutations for an address take the same DB lock.
func (r *userRepository) WithAuthLock(ctx context.Context, email string, run func(UserRepository, AuthSessionRepository) error) error {
	return r.db.WithContext(ctx).Transaction(func(tx *gorm.DB) error {
		if err := tx.Exec("SELECT pg_advisory_xact_lock(hashtextextended(?, 0))", "auth:"+email).Error; err != nil {
			return err
		}
		return run(NewUserRepository(tx), NewAuthSessionRepository(tx))
	})
}

type UserRepository interface {
	CreateUser(user *model.User) error
	GetUserById(id string) (*model.User, error)
	GetUserByUserName(username string) (*model.User, error)
	GetUserByEmail(email string) (*model.User, error)
	GetUserByOAuthSubject(provider, subject string) (*model.User, error)
	UpdateUser(user *model.User) error
	DeleteUser(id string) error
}

type userRepository struct {
	db *gorm.DB
}

func NewUserRepository(db *gorm.DB) UserRepository {
	return &userRepository{db: db}
}

func (r *userRepository) CreateUser(user *model.User) error {
	result := r.db.Create(user)
	if result.Error != nil {
		return result.Error
	}
	return nil
}

func (r *userRepository) GetUserById(id string) (*model.User, error) {
	var user model.User
	result := r.db.Where("id = ?", id).First(&user)
	if result.Error != nil {
		if errors.Is(result.Error, gorm.ErrRecordNotFound) {
			return nil, nil
		}
		return nil, result.Error
	}
	return &user, nil
}

func (r *userRepository) GetUserByEmail(email string) (*model.User, error) {
	var user model.User
	result := r.db.Where("lower(trim(email)) = lower(trim(?))", email).First(&user)

	if result.Error != nil {
		if errors.Is(result.Error, gorm.ErrRecordNotFound) {
			return nil, nil
		}
		return nil, result.Error
	}

	return &user, nil
}

func (r *userRepository) GetUserByUserName(username string) (*model.User, error) {
	var user model.User
	result := r.db.Where("username = ?", username).First(&user)

	if result.Error != nil {
		if !errors.Is(result.Error, gorm.ErrRecordNotFound) {
			return nil, result.Error
		}
	}

	return &user, nil
}

func (r *userRepository) GetUserByOAuthSubject(provider, subject string) (*model.User, error) {
	if provider != "google" || subject == "" {
		return nil, nil
	}
	var user model.User
	err := r.db.Where("google_subject = ?", subject).First(&user).Error
	if errors.Is(err, gorm.ErrRecordNotFound) {
		return nil, nil
	}
	if err != nil {
		return nil, err
	}
	return &user, nil
}

func (r *userRepository) UpdateUser(user *model.User) error {
	result := r.db.Save(user)
	if result.Error != nil {
		return result.Error
	}
	return nil
}

func (r *userRepository) DeleteUser(id string) error {
	result := r.db.Model(&model.User{}).Where("id = ?", id).Update("status", false)
	return result.Error
}
