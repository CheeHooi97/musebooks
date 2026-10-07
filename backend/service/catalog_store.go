package service

import (
	"context"
	"gorm.io/gorm"
	"musebooks/model"
	"musebooks/repository"
	"time"
)

var ErrRecordNotFound = gorm.ErrRecordNotFound

type CatalogResult = repository.CatalogResult

func (s *CatalogService) ListBooks(ctx context.Context, params model.ListBooksQuery) ([]model.Work, int64, error) {
	return s.repo.ListBooks(ctx, params)
}
func (s *CatalogService) GetBook(work *model.Work, key string) CatalogResult {
	return s.repo.GetBook(work, key)
}
func (s *CatalogService) GetEdition(edition *model.Edition, id string) CatalogResult {
	return s.repo.GetEdition(edition, id)
}
func (s *CatalogService) GetEditionIdentity(edition *model.Edition, id string) CatalogResult {
	return s.repo.GetEditionIdentity(edition, id)
}
func (s *CatalogService) ListOrigins(ctx context.Context) ([]model.OriginResponse, error) {
	return s.repo.ListOrigins(ctx)
}
func (s *CatalogService) ListSources(sources *[]model.Source) CatalogResult {
	return s.repo.ListSources(sources)
}
func (s *CatalogService) GetSource(source *model.Source, id string) CatalogResult {
	return s.repo.GetSource(source, id)
}
func (s *CatalogService) GetJob(job *model.ScrapeJob, id string) CatalogResult {
	return s.repo.GetJob(job, id)
}
func (s *CatalogService) CreateJob(job *model.ScrapeJob) CatalogResult { return s.repo.CreateJob(job) }
func (s *CatalogService) UpdateJob(job *model.ScrapeJob, updates map[string]any) CatalogResult {
	return s.repo.UpdateJob(job, updates)
}
func (s *CatalogService) CreateRun(run *model.ScrapeRun) CatalogResult { return s.repo.CreateRun(run) }
func (s *CatalogService) UpdateRun(run *model.ScrapeRun, updates map[string]any) CatalogResult {
	return s.repo.UpdateRun(run, updates)
}
func (s *CatalogService) GetRunningRun(run *model.ScrapeRun, jobID, workerID string) CatalogResult {
	return s.repo.GetRunningRun(run, jobID, workerID)
}
func (s *CatalogService) LockClaimableJob(job *model.ScrapeJob, now time.Time, sources []string) CatalogResult {
	return s.repo.LockClaimableJob(job, now, sources)
}
func (s *CatalogService) LockListing(listing *model.Listing, sourceID, externalID string) CatalogResult {
	return s.repo.LockListing(listing, sourceID, externalID)
}
func (s *CatalogService) SaveListing(listing *model.Listing) CatalogResult {
	return s.repo.SaveListing(listing)
}
func (s *CatalogService) GetObservation(key string) CatalogResult { return s.repo.GetObservation(key) }
func (s *CatalogService) CreateObservation(observation *model.ListingObservation) CatalogResult {
	return s.repo.CreateObservation(observation)
}
func (s *CatalogService) Transaction(fn func(*CatalogService) error) error {
	return s.repo.Transaction(func(tx *repository.CatalogRepository) error { return fn(NewCatalogService(tx)) })
}
