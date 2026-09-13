package router

import (
	"musebooks/handler"
	"musebooks/middleware"
	"musebooks/utils"

	"github.com/labstack/echo/v4"
	"gorm.io/gorm"
)

func SetupRoutes(h *handler.Handler, db *gorm.DB) *echo.Echo {
	e := echo.New()
	e.Validator = utils.NewValidator()

	v := e.Group("/v1", middleware.Authenticate(db))

	// User
	user := v.Group("/user")
	user.GET("", h.GetUser)
	user.POST("/search", h.SearchUserWithoutCheckUserId)
	user.POST("", h.CreateUser)
	user.POST("/update/:id", h.UpdateUser)
	user.DELETE("/delete/:id", h.DeleteUser)

	// Admin
	admin := v.Group("/admin")
	admin.GET("", h.GetAdmin)
	admin.GET("/admins", h.GetAllAdmins)
	admin.POST("", h.CreateAdmin)
	admin.POST("/update/:id", h.UpdateAdmin)
	admin.DELETE("/delete/:id", h.DeleteAdmin)

	return e
}
