package middleware

import (
	"github.com/labstack/echo/v4"
	"gorm.io/gorm"
)

// Authenticate
func Authenticate(db *gorm.DB) echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			return next(c)
		}
	}
}
