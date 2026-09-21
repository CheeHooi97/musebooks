package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"

	"musebooks/config"
	"musebooks/database"
	"musebooks/handler"
	"musebooks/repository"
	"musebooks/router"
	service "musebooks/service"
	"time"

	"github.com/labstack/echo/v4"
	echoMiddleware "github.com/labstack/echo/v4/middleware"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
	"gorm.io/gorm/schema"
)

func main() {
	// Load config
	config.LoadConfig()

	dsn := fmt.Sprintf("host=%s user=%s password=%s dbname=%s port=%s sslmode=%s TimeZone=%s",
		config.DBHost, config.DBUser, config.DBPassword, config.DBName, config.DBPort,
		config.DBSSLMode, config.DBTimeZone)

	// Connect to the database
	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{
		NamingStrategy: schema.NamingStrategy{
			TablePrefix:   "",
			SingularTable: true,
		},
	})
	if err != nil {
		log.Fatal("Failed to connect to the database:", err)
	}

	// Auto-migrate
	err = database.Migrate(db)
	if err != nil {
		log.Fatal("Failed to migrate database:", err)
	}
	if err := database.SeedCatalog(db); err != nil {
		log.Fatal("Failed to seed catalog:", err)
	}

	// Initialize repository
	repos := repository.InitializeRepository(db)

	// Initialize services
	services := service.InitializeService(repos)

	// Initialize message handler
	h := handler.NewHandler(services)

	// Setup API routes
	api := router.SetupRoutes(h, db)

	e := echo.New()
	e.Use(echoMiddleware.CORSWithConfig(echoMiddleware.CORSConfig{
		AllowOrigins: []string{"http://localhost:3000", "http://127.0.0.1:3000"},
		AllowHeaders: []string{echo.HeaderOrigin, echo.HeaderContentType, echo.HeaderAccept, echo.HeaderAuthorization, "X-Scraper-Token"},
	}))
	e.HTTPErrorHandler = func(err error, c echo.Context) {
		if !c.Response().Committed {
			c.JSON(http.StatusInternalServerError, map[string]any{
				"error": map[string]any{
					"code":    "INTERNAL_ERROR",
					"message": "Internal error",
					"debug":   err.Error(),
				},
			})
		}
	}

	e.Any("/*", func(c echo.Context) (err error) {
		req := c.Request()
		res := c.Response()
		api.ServeHTTP(res, req)
		return
	})
	if err := e.Start(":2001"); err != nil && err != http.ErrServerClosed {
		log.Fatalf("Failed to start server: %v", err)
	}

	quit := make(chan os.Signal, 1)
	signal.Notify(quit, os.Interrupt, syscall.SIGTERM)
	<-quit

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	if err := e.Shutdown(ctx); err != nil {
		log.Fatalf("Server forced to shutdown: %v", err)
	}
}
