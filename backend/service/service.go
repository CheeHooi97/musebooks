package service

import "musebooks/repository"

type Services struct {
	CatalogService *CatalogService
	UserService    *UserService
	AdminService   *AdminService
}

func InitializeService(repos *repository.Repositories) *Services {
	return &Services{
		CatalogService: NewCatalogService(repos.CatalogRepo),
		UserService:    NewUserService(repos.UserRepo),
		AdminService:   NewAdminService(repos.AdminRepo),
	}
}
