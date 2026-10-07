package repository

import (
	"context"
	"gorm.io/gorm"
	"musebooks/model"
)

// CatalogRepository reads the existing canonical records; it never invents
// separate person or publisher identities from marketplace titles.
type CatalogRepository struct{ db *gorm.DB }

func NewCatalogRepository(db *gorm.DB) *CatalogRepository { return &CatalogRepository{db: db} }
func (r *CatalogRepository) PublishedWorks(ctx context.Context) ([]model.Work, error) {
	works := []model.Work{}
	err := r.db.WithContext(ctx).Where("works.status = ?", "published").
		Preload("Origin").Preload("Editions", "status <> ?", "superseded").
		Preload("Editions.Listings").Preload("Editions.Listings.Source").
		Order("works.original_title ASC, works.id ASC").Find(&works).Error
	return works, err
}
