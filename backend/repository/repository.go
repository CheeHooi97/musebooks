package repository

import "gorm.io/gorm"

type Repositories struct {
	CatalogRepo *CatalogRepository
	UserRepo    UserRepository
	AdminRepo   AdminRepository
}

func InitializeRepository(db *gorm.DB) *Repositories {
	return &Repositories{
		CatalogRepo: NewCatalogRepository(db),
		UserRepo:    NewUserRepository(db),
		AdminRepo:   NewAdminRepository(db),
	}
}
