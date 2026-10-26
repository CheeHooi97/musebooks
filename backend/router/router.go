package router

import (
	"musebooks/handler"
	"musebooks/middleware"
	"musebooks/utils"
	"os"
	"time"

	"github.com/labstack/echo/v4"
	echoMiddleware "github.com/labstack/echo/v4/middleware"
	"gorm.io/gorm"
)

func SetupRoutes(h *handler.Handler, db *gorm.DB) *echo.Echo {
	e := echo.New()
	e.Validator = utils.NewValidator()

	v := e.Group("/v1", middleware.Authenticate(db))
	for _, prefix := range []string{"/auth", "/mobile/auth"} {
		auth := v.Group(prefix, handler.AuthRequest, echoMiddleware.BodyLimit("8K"), echoMiddleware.RateLimiter(echoMiddleware.NewRateLimiterMemoryStoreWithConfig(echoMiddleware.RateLimiterMemoryStoreConfig{Rate: 0.5, Burst: 12, ExpiresIn: 3 * time.Minute})))
		auth.GET("/providers", h.AuthProviders)
		auth.GET("/me", h.CurrentAuthUser)
		auth.POST("/register", h.Register)
		auth.POST("/login", h.Login)
		auth.POST("/logout", h.Logout)
		auth.POST("/verify-email", h.VerifyEmail)
		auth.POST("/resend-verification", h.ResendVerification)
		auth.POST("/forgot-password", h.ForgotPassword)
		auth.POST("/reset-password", h.ResetPassword)
	}
	v.GET("/auth/oauth/google", h.GoogleStart, handler.AuthRequest)
	v.GET("/auth/oauth/google/callback", h.GoogleCallback, handler.AuthRequest)
	v.POST("/mobile/auth/oauth/exchange", h.MobileOAuthExchange, handler.AuthRequest, echoMiddleware.BodyLimit("8K"), echoMiddleware.RateLimiter(echoMiddleware.NewRateLimiterMemoryStore(1)))
	catalogHandler := h.Catalog
	browse := h.Browse
	v.GET("/models", browse.Models)
	v.GET("/models/:id", browse.Profile)
	v.GET("/models/:id/books", browse.DirectoryBooks)
	v.GET("/publishers", browse.Publishers)
	v.GET("/publishers/:id", browse.Profile)
	v.GET("/publishers/:id/books", browse.DirectoryBooks)
	v.GET("/listings", browse.Listings)
	v.GET("/marketplace-listings", browse.MarketplaceListings)
	v.GET("/books", catalogHandler.ListBooks)
	v.GET("/books/:id", catalogHandler.GetBook)
	v.GET("/editions/:id", catalogHandler.GetEdition)
	v.GET("/origins", catalogHandler.ListOrigins)
	v.GET("/sources", catalogHandler.ListSources)
	v.GET("/catalog/media/redirect", h.Media.Redirect)
	v.POST("/internal/scrape/jobs", catalogHandler.CreateScrapeJob, requireScraperToken(os.Getenv("SCRAPER_INGEST_TOKEN")))
	v.POST("/internal/scrape/jobs/claim", catalogHandler.ClaimScrapeJob, requireScraperToken(os.Getenv("SCRAPER_INGEST_TOKEN")))
	v.POST("/internal/scrape/jobs/:id/heartbeat", catalogHandler.HeartbeatScrapeJob, requireScraperToken(os.Getenv("SCRAPER_INGEST_TOKEN")))
	v.POST("/internal/scrape/jobs/:id/complete", catalogHandler.CompleteScrapeJob, requireScraperToken(os.Getenv("SCRAPER_INGEST_TOKEN")))
	v.POST("/internal/scrape/batches", catalogHandler.IngestBatch, requireScraperToken(os.Getenv("SCRAPER_INGEST_TOKEN")))

	// User
	user := v.Group("/user", handler.RequireAccountManagementToken)
	user.GET("", h.GetUser)
	user.POST("/search", h.SearchUserWithoutCheckUserId)
	user.POST("", h.CreateUser)
	user.POST("/update/:id", h.UpdateUser)
	user.DELETE("/delete/:id", h.DeleteUser)

	// Admin
	admin := v.Group("/admin", handler.RequireAccountManagementToken)
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
