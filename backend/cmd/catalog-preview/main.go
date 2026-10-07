// catalog-preview serves catalog reads without running migrations or seeds.
package main

import (
	"github.com/labstack/echo/v4"
	"log"
	"musebooks/config"
	"musebooks/database"
	"musebooks/handler"
	"musebooks/repository"
	"musebooks/service"
)

func main() {
	config.LoadConfig()
	db, err := database.Open(true, false)
	if err != nil {
		log.Fatal("Catalog preview could not connect to the configured database")
	}
	e := echo.New()
	browse := handler.NewCatalogBrowseHandler(service.NewCatalogService(repository.NewCatalogRepository(db)))
	existing := handler.NewCatalogHandler(service.NewCatalogService(repository.NewCatalogRepository(db)))
	e.GET("/v1/models", browse.Models)
	e.GET("/v1/publishers", browse.Publishers)
	e.GET("/v1/models/:id/books", browse.DirectoryBooks)
	e.GET("/v1/publishers/:id/books", browse.DirectoryBooks)
	e.GET("/v1/listings", browse.Listings)
	e.GET("/v1/books", existing.ListBooks)
	e.GET("/v1/origins", existing.ListOrigins)
	e.GET("/v1/sources", existing.ListSources)
	log.Fatal(e.Start("127.0.0.1:2001"))
}
