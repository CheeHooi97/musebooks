package service

import "musebooks/repository"

type Services struct {
	UserService  *UserService
	AdminService *AdminService
}

func InitializeService(repos *repository.Repositories) *Services {
	return &Services{
		UserService:  NewUserService(repos.UserRepo),
		AdminService: NewAdminService(repos.AdminRepo),
	}
}
