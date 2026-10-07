package repository

import (
	"gorm.io/gorm"
	"musebooks/model"
)

func applyWorkFilters(query *gorm.DB, params model.ListBooksQuery) *gorm.DB {
	if params.Query != "" {
		pattern := "%" + params.Query + "%"
		query = query.Where("works.original_title ILIKE ? OR works.english_title ILIKE ? OR works.featured_names ILIKE ?", pattern, pattern, pattern)
	}
	if params.Origin != "" {
		query = query.Where("works.origin_code = ?", params.Origin)
	}
	if params.Format != "" || params.Language != "" || params.Year != "" || params.Availability != "" {
		query = query.Joins("JOIN editions AS filter_editions ON filter_editions.work_id = works.id AND filter_editions.status <> 'superseded'")
		if params.Format != "" {
			query = query.Where("filter_editions.format = ?", params.Format)
		}
		if params.Language != "" {
			query = query.Where("filter_editions.language = ?", params.Language)
		}
		if params.Year != "" {
			query = query.Where("EXTRACT(YEAR FROM filter_editions.release_date) = ?", params.Year)
		}
		if params.Availability != "" {
			query = query.Joins("JOIN listings AS availability_listings ON availability_listings.edition_id = filter_editions.id").
				Where("availability_listings.status = ?", params.Availability).
				Where("availability_listings.format_candidate = filter_editions.format OR (COALESCE(availability_listings.format_candidate, '') = '' AND ((filter_editions.format = 'digital' AND availability_listings.price_type = 'digital') OR (filter_editions.format = 'physical' AND availability_listings.price_type <> 'digital')))")
		}
	}
	return query
}
