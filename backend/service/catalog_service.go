package service

import (
	"context"
	"musebooks/model"
	"musebooks/repository"
)

type CatalogService struct{ repo *repository.CatalogRepository }

func NewCatalogService(repo *repository.CatalogRepository) *CatalogService {
	return &CatalogService{repo: repo}
}
func (s *CatalogService) PublishedWorks(ctx context.Context) ([]model.Work, error) {
	return s.repo.PublishedWorks(ctx)
}

func (s *CatalogService) Directory(ctx context.Context, p model.CatalogBrowseQuery) ([]model.DirectoryEntry, int64, error) {
	return s.repo.Directory(ctx, p)
}
func (s *CatalogService) DirectoryBooks(ctx context.Context, p model.CatalogBrowseQuery) ([]model.Work, int64, error) {
	return s.repo.DirectoryBooks(ctx, p)
}
func (s *CatalogService) Listings(ctx context.Context, p model.CatalogBrowseQuery) ([]model.MarketEntry, int64, error) {
	return s.repo.Listings(ctx, p)
}
func (s *CatalogService) MarketplaceListings(ctx context.Context, p model.CatalogBrowseQuery) ([]model.MarketplaceListingEntry, int64, error) {
	return s.repo.MarketplaceListings(ctx, p)
}
