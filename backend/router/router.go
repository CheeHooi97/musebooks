package router

import (
	"musebooks/catalog"
	"musebooks/handler"
	"musebooks/middleware"
	"musebooks/utils"
	"os"

	"github.com/labstack/echo/v4"
	"gorm.io/gorm"
)

func SetupRoutes(h *handler.Handler, db *gorm.DB) *echo.Echo {
	e := echo.New()
	e.Validator = utils.NewValidator()

	v := e.Group("/v1", middleware.Authenticate(db))
	catalogHandler := catalog.NewHandler(db)
	v.GET("/books", catalogHandler.ListBooks)
	v.GET("/books/:id", catalogHandler.GetBook)
	v.GET("/editions/:id", catalogHandler.GetEdition)
	v.GET("/origins", catalogHandler.ListOrigins)
	v.GET("/sources", catalogHandler.ListSources)
	v.POST("/internal/scrape/jobs", catalogHandler.CreateScrapeJob, requireScraperToken(os.Getenv("SCRAPER_INGEST_TOKEN")))
	v.POST("/internal/scrape/jobs/claim", catalogHandler.ClaimScrapeJob, requireScraperToken(os.Getenv("SCRAPER_INGEST_TOKEN")))
	v.POST("/internal/scrape/jobs/:id/heartbeat", catalogHandler.HeartbeatScrapeJob, requireScraperToken(os.Getenv("SCRAPER_INGEST_TOKEN")))
	v.POST("/internal/scrape/jobs/:id/complete", catalogHandler.CompleteScrapeJob, requireScraperToken(os.Getenv("SCRAPER_INGEST_TOKEN")))
	v.POST("/internal/scrape/batches", catalogHandler.IngestBatch, requireScraperToken(os.Getenv("SCRAPER_INGEST_TOKEN")))

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

func requireScraperToken(token string) echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			if token != "" && c.Request().Header.Get("X-Scraper-Token") != token {
				return echo.NewHTTPError(401, "invalid scraper token")
			}
			return next(c)
		}
	}
}
