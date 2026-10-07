package repository

import (
	"context"
	"gorm.io/gorm"
	"gorm.io/gorm/clause"
	"musebooks/model"
	"time"
)

// Result exposes operation errors without giving HTTP handlers a query builder.
type CatalogResult struct{ Error error }

func result(db *gorm.DB) CatalogResult { return CatalogResult{Error: db.Error} }
func (r *CatalogRepository) Transaction(fn func(*CatalogRepository) error) error {
	return r.db.Transaction(func(tx *gorm.DB) error { return fn(NewCatalogRepository(tx)) })
}
func (r *CatalogRepository) ListBooks(ctx context.Context, params model.ListBooksQuery) ([]model.Work, int64, error) {
	query := applyWorkFilters(r.db.WithContext(ctx).Model(&model.Work{}).Where("works.status = ?", "published"), params)
	var total int64
	if err := query.Session(&gorm.Session{}).Distinct("works.id").Count(&total).Error; err != nil {
		return nil, 0, err
	}
	works := []model.Work{}
	err := query.Distinct("works.*").Preload("Origin").Preload("Editions", func(db *gorm.DB) *gorm.DB {
		return db.Where("status <> ?", "superseded").Order("release_date DESC NULLS LAST, edition_label ASC")
	}).Preload("Editions.Listings").Preload("Editions.Listings.Source").Order("works.updated_at DESC, works.id ASC").Offset((params.Page - 1) * params.PageSize).Limit(params.PageSize).Find(&works).Error
	return works, total, err
}
func (r *CatalogRepository) GetBook(work *model.Work, key string) CatalogResult {
	return result(r.db.Where("works.status = ?", "published").Where("works.id = ? OR works.slug = ?", key, key).Preload("Origin").Preload("Editions", "status <> ?", "superseded").Preload("Editions.Listings").Preload("Editions.Listings.Source").First(work))
}
func (r *CatalogRepository) GetEdition(edition *model.Edition, id string) CatalogResult {
	return result(r.db.Joins("JOIN works ON works.id = editions.work_id AND works.status = 'published'").Preload("Listings").Preload("Listings.Source").Where("editions.status <> ?", "superseded").Where("editions.id = ?", id).First(edition))
}
func (r *CatalogRepository) GetEditionIdentity(edition *model.Edition, id string) CatalogResult {
	return result(r.db.Select("id", "format").First(edition, "id = ?", id))
}
func (r *CatalogRepository) ListOrigins(ctx context.Context) ([]model.OriginResponse, error) {
	items := []model.OriginResponse{}
	err := r.db.WithContext(ctx).Table("origins").Select("origins.code, origins.name, origins.native_name, COUNT(works.id) AS count").Joins("LEFT JOIN works ON works.origin_code = origins.code AND works.status = 'published'").Group("origins.code").Order("origins.sort_order ASC, origins.name ASC").Scan(&items).Error
	return items, err
}
func (r *CatalogRepository) ListSources(sources *[]model.Source) CatalogResult {
	return result(r.db.Where("enabled = ?", true).Order("name ASC").Find(sources))
}
func (r *CatalogRepository) GetSource(source *model.Source, id string) CatalogResult {
	return result(r.db.First(source, "id = ?", id))
}
func (r *CatalogRepository) GetJob(job *model.ScrapeJob, id string) CatalogResult {
	return result(r.db.First(job, "id = ?", id))
}
func (r *CatalogRepository) CreateJob(job *model.ScrapeJob) CatalogResult {
	return result(r.db.Create(job))
}
func (r *CatalogRepository) UpdateJob(job *model.ScrapeJob, updates map[string]any) CatalogResult {
	return result(r.db.Model(job).Updates(updates))
}
func (r *CatalogRepository) CreateRun(run *model.ScrapeRun) CatalogResult {
	return result(r.db.Create(run))
}
func (r *CatalogRepository) UpdateRun(run *model.ScrapeRun, updates map[string]any) CatalogResult {
	return result(r.db.Model(run).Updates(updates))
}
func (r *CatalogRepository) GetRunningRun(run *model.ScrapeRun, jobID, workerID string) CatalogResult {
	return result(r.db.Where("job_id = ? AND worker_id = ? AND status = ?", jobID, workerID, "running").Order("started_at DESC").First(run))
}
func (r *CatalogRepository) LockClaimableJob(job *model.ScrapeJob, now time.Time, sources []string) CatalogResult {
	query := r.db.Clauses(clause.Locking{Strength: "UPDATE", Options: "SKIP LOCKED"}).Where("available_at <= ?", now).Where("attempt_count < max_attempts").Where("status = ? OR (status IN ? AND (leased_until IS NULL OR leased_until <= ?))", "queued", []string{"leased", "running"}, now)
	if len(sources) > 0 {
		query = query.Where("source_id IN ?", sources)
	}
	return result(query.Order("priority DESC, available_at ASC, created_at ASC").First(job))
}
func (r *CatalogRepository) LockListing(listing *model.Listing, sourceID, externalID string) CatalogResult {
	return result(r.db.Clauses(clause.Locking{Strength: "UPDATE"}).Where("source_id = ? AND external_id = ?", sourceID, externalID).First(listing))
}
func (r *CatalogRepository) SaveListing(listing *model.Listing) CatalogResult {
	write := r.db
	if listing.EditionID == "" {
		write = write.Omit("EditionID")
	}
	if err := write.Save(listing).Error; err != nil {
		return CatalogResult{Error: err}
	}
	if listing.EditionID == "" {
		return result(r.db.Model(listing).Update("edition_id", nil))
	}
	return CatalogResult{}
}
func (r *CatalogRepository) GetObservation(key string) CatalogResult {
	return result(r.db.Where("observation_key = ?", key).First(&model.ListingObservation{}))
}
func (r *CatalogRepository) CreateObservation(observation *model.ListingObservation) CatalogResult {
	return result(r.db.Create(observation))
}
