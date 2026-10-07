package main

import (
	"context"
	"log"
	"net/http"
	"os"
	"os/signal"
	"strings"
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
)

func main() {
	// Load config
	config.LoadConfig()

	db, err := database.Open(false, false)
	if err != nil {
		log.Fatal(err)
	}
	pool, _ := db.DB()
	defer pool.Close()
	if config.DBAutoMigrate && !config.DBSkipStartupMigrations {
		if err := database.Migrate(db); err != nil {
			log.Fatal("Failed to migrate database: ", err)
		}
		if err := database.SeedCatalog(db); err != nil {
			log.Fatal("Failed to seed catalog: ", err)
		}
	}
	if err := database.CheckCatalogSchema(db); err != nil {
		log.Fatal(err)
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
		AllowOrigins: strings.Split(config.CORSOrigins, ","),
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
	listenAddr := config.HTTPAddr
	go func() {
		if err := e.Start(listenAddr); err != nil && err != http.ErrServerClosed {
			log.Fatalf("Failed to start server: %v", err)
		}
	}()

	quit := make(chan os.Signal, 1)
	signal.Notify(quit, os.Interrupt, syscall.SIGTERM)
	<-quit

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	if err := e.Shutdown(ctx); err != nil {
		log.Fatalf("Server forced to shutdown: %v", err)
	}
}
