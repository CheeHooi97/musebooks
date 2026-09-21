package repository

import "gorm.io/gorm"

type Repositories struct {
	UserRepo  UserRepository
	AdminRepo AdminRepository
}

func InitializeRepository(db *gorm.DB) *Repositories {
	return &Repositories{
		UserRepo:  NewUserRepository(db),
		AdminRepo: NewAdminRepository(db),
	}
}
