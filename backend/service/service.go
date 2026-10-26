package service

import "musebooks/repository"

type Services struct {
	CatalogService *CatalogService
	UserService    *UserService
	AdminService   *AdminService
	AuthService    *AuthService
}

func InitializeService(repos *repository.Repositories) *Services {
	return &Services{
		CatalogService: NewCatalogService(repos.CatalogRepo),
		UserService:    NewUserService(repos.UserRepo),
		AdminService:   NewAdminService(repos.AdminRepo),
		AuthService:    NewAuthService(repos.UserRepo, repos.AuthSessionRepo, 0),
	}
}
