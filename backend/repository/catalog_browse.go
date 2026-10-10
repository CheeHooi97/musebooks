package repository

import (
	"context"
	"gorm.io/gorm"
	"musebooks/model"
	"strings"
)

func (r *CatalogRepository) Directory(ctx context.Context, p model.CatalogBrowseQuery) ([]model.DirectoryEntry, int64, error) {
	query := r.db.WithContext(ctx).Table("people AS directory")
	columns := `directory.slug AS id, directory.canonical_public_name AS name,directory.original_name,directory.english_name,directory.verification_source_url AS official_url,
 (SELECT COUNT(DISTINCT w.id) FROM work_people wp JOIN works w ON w.id=wp.work_id WHERE wp.person_id=directory.id AND wp.role='featured' AND w.status='published') AS work_count,
 (SELECT COUNT(DISTINCT e.id) FROM work_people wp JOIN works w ON w.id=wp.work_id JOIN editions e ON e.work_id=w.id WHERE wp.person_id=directory.id AND wp.role='featured' AND w.status='published' AND e.status<>'superseded') AS edition_count,
 (SELECT COALESCE(NULLIF(e.cover_url,''),w.cover_url) FROM work_people wp JOIN works w ON w.id=wp.work_id LEFT JOIN editions e ON e.work_id=w.id AND e.status<>'superseded' WHERE wp.person_id=directory.id AND wp.role='featured' AND w.status='published' ORDER BY w.id,e.id LIMIT 1) AS cover_url`
	query = query.Where("EXISTS (SELECT 1 FROM work_people wp JOIN works w ON w.id=wp.work_id WHERE wp.person_id=directory.id AND wp.role='featured' AND w.status='published')")
	name := "directory.canonical_public_name"
	if p.Kind == "publisher" {
		query = r.db.WithContext(ctx).Table("companies AS directory").Where("EXISTS (SELECT 1 FROM editions e JOIN works w ON w.id=e.work_id WHERE e.publisher_company_id=directory.id AND e.status<>'superseded' AND w.status='published')")
		name = "directory.canonical_name"
		columns = `directory.slug AS id,directory.canonical_name AS name,directory.official_url,
 (SELECT COUNT(DISTINCT w.id) FROM editions e JOIN works w ON w.id=e.work_id WHERE e.publisher_company_id=directory.id AND e.status<>'superseded' AND w.status='published') AS work_count,
 (SELECT COUNT(*) FROM editions e JOIN works w ON w.id=e.work_id WHERE e.publisher_company_id=directory.id AND e.status<>'superseded' AND w.status='published') AS edition_count,
 (SELECT COALESCE(NULLIF(e.cover_url,''),w.cover_url) FROM editions e JOIN works w ON w.id=e.work_id WHERE e.publisher_company_id=directory.id AND e.status<>'superseded' AND w.status='published' ORDER BY w.id,e.id LIMIT 1) AS cover_url`
	}
	if p.ID != "" {
		query = query.Where("directory.slug = ?", p.ID)
	}
	if p.Query != "" && p.Kind == "model" {
		term := "%" + p.Query + "%"
		query = query.Where("directory.canonical_public_name ILIKE ? OR directory.original_name ILIKE ? OR directory.english_name ILIKE ? OR directory.traditional_chinese_name ILIKE ? OR directory.simplified_chinese_name ILIKE ?", term, term, term, term, term)
	} else if p.Query != "" {
		query = query.Where(name+" ILIKE ?", "%"+p.Query+"%")
	}
	var total int64
	if err := query.Session(&gorm.Session{}).Count(&total).Error; err != nil {
		return nil, 0, err
	}
	entries := []model.DirectoryEntry{}
	err := query.Select(columns).Order(name + " ASC,directory.id ASC").Offset((p.Page - 1) * p.PageSize).Limit(p.PageSize).Scan(&entries).Error
	for i := range entries {
		entries[i].CoverURL = model.PublicCoverURL(entries[i].CoverURL)
	}
	return entries, total, err
}
func (r *CatalogRepository) DirectoryBooks(ctx context.Context, p model.CatalogBrowseQuery) ([]model.Work, int64, error) {
	query := r.db.WithContext(ctx).Model(&model.Work{}).Where("works.status = ?", "published")
	if p.Kind == "publisher" {
		query = query.Where("EXISTS (SELECT 1 FROM editions e JOIN companies c ON c.id=e.publisher_company_id WHERE e.work_id=works.id AND e.status<>'superseded' AND c.slug=?)", p.ID)
	} else {
		query = query.Where("EXISTS (SELECT 1 FROM work_people wp JOIN people p ON p.id=wp.person_id WHERE wp.work_id=works.id AND wp.role='featured' AND p.slug=?)", p.ID)
	}
	if p.Query != "" {
		term := "%" + p.Query + "%"
		query = query.Where("works.original_title ILIKE ? OR works.english_title ILIKE ? OR works.featured_names ILIKE ?", term, term, term)
	}
	if p.Person != "" {
		query = query.Where("EXISTS (SELECT 1 FROM work_people wp JOIN people p ON p.id=wp.person_id WHERE wp.work_id=works.id AND wp.role='featured' AND (p.slug=? OR p.canonical_public_name ILIKE ?))", p.Person, "%"+p.Person+"%")
	}
	editionFilter := "e.work_id=works.id AND e.status<>'superseded'"
	args := []any{}
	if p.Kind == "publisher" {
		editionFilter += " AND e.publisher_company_id IN (SELECT id FROM companies WHERE slug=?)"
		args = append(args, p.ID)
	}
	if p.Format != "" {
		editionFilter += " AND e.format=?"
		args = append(args, p.Format)
	}
	if p.Language != "" {
		editionFilter += " AND e.language ILIKE ?"
		args = append(args, "%"+p.Language+"%")
	}
	if p.Year != "" {
		editionFilter += " AND EXTRACT(YEAR FROM e.release_date)=?"
		args = append(args, p.Year)
	}
	query = query.Where("EXISTS (SELECT 1 FROM editions e WHERE "+editionFilter+")", args...)
	var total int64
	if err := query.Session(&gorm.Session{}).Count(&total).Error; err != nil {
		return nil, 0, err
	}
	works := []model.Work{}
	query = query.Preload("Origin").Preload("Editions", func(db *gorm.DB) *gorm.DB {
		db = db.Where("status <> ?", "superseded")
		if p.Kind == "publisher" {
			db = db.Where("publisher_company_id IN (SELECT id FROM companies WHERE slug=?)", p.ID)
		}
		if p.Format != "" {
			db = db.Where("format=?", p.Format)
		}
		if p.Language != "" {
			db = db.Where("language ILIKE ?", "%"+p.Language+"%")
		}
		if p.Year != "" {
			db = db.Where("EXTRACT(YEAR FROM release_date)=?", p.Year)
		}
		return db.Order("release_date DESC NULLS LAST,id")
	}).Preload("Credits.Person").Preload("Editions.PublisherCompany").Preload("Editions.Listings").Preload("Editions.Listings.Source")
	err := query.Order("works.original_title,works.id").Offset((p.Page - 1) * p.PageSize).Limit(p.PageSize).Find(&works).Error
	return works, total, err
}
func (r *CatalogRepository) Listings(ctx context.Context, p model.CatalogBrowseQuery) ([]model.MarketEntry, int64, error) {
	table, status := "active_listings", "active"
	if p.Status == "completed" {
		table, status = "sold_listings", "completed"
	}
	query := r.db.WithContext(ctx).Table(table + " AS feed").Joins("JOIN editions e ON e.id=feed.edition_id AND e.status<>'superseded' AND e.format=feed.format").Joins("JOIN works w ON w.id=e.work_id AND w.status='published'").Joins("JOIN sources s ON s.id=feed.source_id")
	if status == "active" {
		query = query.Where("feed.is_active = ?", true)
	} else {
		query = query.Where("feed.review_status = ?", "linked")
	}
	if p.Format != "" {
		query = query.Where("feed.format = ?", p.Format)
	}
	if p.Source != "" {
		query = query.Where("feed.source_id = ?", p.Source)
	}
	if p.Person != "" {
		query = query.Where("EXISTS (SELECT 1 FROM work_people wp JOIN people p ON p.id=wp.person_id WHERE wp.work_id=w.id AND wp.role='featured' AND p.slug=?)", p.Person)
	}
	if p.Publisher != "" {
		query = query.Where("e.publisher_company_id IN (SELECT id FROM companies WHERE slug=?)", p.Publisher)
	}
	if p.Query != "" {
		term := "%" + p.Query + "%"
		query = query.Where("feed.title ILIKE ? OR w.original_title ILIKE ? OR w.featured_names ILIKE ? OR e.publisher ILIKE ?", term, term, term, term)
	}
	var total int64
	if err := query.Session(&gorm.Session{}).Count(&total).Error; err != nil {
		return nil, 0, err
	}
	columns := `feed.source_listing_id AS id,feed.external_listing_id AS external_id,feed.original_url AS url,feed.title,
 feed.seller_location,feed.condition,feed.format,feed.price_minor,feed.original_currency_code AS currency,feed.price_type,
 feed.shipping_text,feed.observed_at,feed.last_seen_at,
 s.id AS source_id,s.name AS source_name,s.region AS source_region,s.kind AS source_kind,feed.format AS source_photobook_format,
 w.id AS work_id,w.slug AS work_slug,w.original_title AS work_title,w.featured_names AS featured_names_text,
 e.id AS edition_id,e.edition_label,e.publisher,COALESCE(NULLIF(e.cover_url,''),w.cover_url) AS cover_url,
 CASE WHEN feed.format='digital' THEN 'digital_retail' WHEN s.kind='bookstore' THEN 'physical_retail' WHEN ` + "'" + status + "'" + `='completed' THEN 'marketplace_sold' ELSE 'marketplace_asking' END AS price_category,` + "'" + status + "' AS status"
	entries := []model.MarketEntry{}
	err := query.Select(columns).Order("feed.observed_at DESC,feed.source_listing_id ASC").Offset((p.Page - 1) * p.PageSize).Limit(p.PageSize).Scan(&entries).Error
	for i := range entries {
		entries[i].SetFeaturedNames()
		entries[i].CoverURL = model.PublicCoverURL(entries[i].CoverURL)
	}
	return entries, total, err
}

// MarketplaceListings returns current source records independently of catalog
// edition matching. This lets visitors inspect Japan marketplace evidence
// without presenting an unmatched listing as a verified catalog book.
func (r *CatalogRepository) MarketplaceListings(ctx context.Context, p model.CatalogBrowseQuery) ([]model.MarketplaceListingEntry, int64, error) {
	query := r.db.WithContext(ctx).Table("listings AS listing").
		Joins("JOIN sources AS source ON source.id=listing.source_id").
		Joins("LEFT JOIN editions AS edition ON edition.id=listing.edition_id AND edition.status<>'superseded'").
		Joins("LEFT JOIN works AS work ON work.id=edition.work_id AND work.status='published'").
		Where("upper(source.region)=?", strings.ToUpper(strings.TrimSpace(p.Region))).
		Where("lower(source.kind)=?", "marketplace").
		Where("listing.status <> ?", "excluded")
	if p.Status == "active" || p.Status == "completed" {
		query = query.Where("listing.status = ?", p.Status)
	}
	if p.Format != "" {
		query = query.Where("listing.format_candidate = ?", p.Format)
	}
	if p.Source != "" {
		query = query.Where("listing.source_id = ?", p.Source)
	}
	if p.Query != "" {
		term := "%" + p.Query + "%"
		query = query.Where("listing.title ILIKE ? OR work.original_title ILIKE ? OR work.featured_names ILIKE ? OR edition.publisher ILIKE ?", term, term, term, term)
	}
	var total int64
	if err := query.Session(&gorm.Session{}).Count(&total).Error; err != nil {
		return nil, 0, err
	}
	columns := `listing.id,listing.external_id,listing.url,listing.title,listing.seller_location,listing.condition,
 listing.format_candidate AS format,listing.status,listing.price_minor,listing.currency,listing.price_type,
 listing.shipping_text,listing.observed_at,listing.last_seen_at,listing.image_url,
 source.id AS source_id,source.name AS source_name,source.region AS source_region,source.kind AS source_kind,
 listing.format_candidate AS source_photobook_format,
 CASE WHEN listing.format_candidate='digital' THEN 'digital_retail' WHEN source.kind='bookstore' THEN 'physical_retail'
 WHEN listing.status='completed' THEN 'marketplace_sold' ELSE 'marketplace_asking' END AS price_category,
 (work.id IS NOT NULL) AS catalog_matched,work.original_title AS work_title,work.slug AS work_slug,
 edition.edition_label,edition.publisher`
	entries := []model.MarketplaceListingEntry{}
	err := query.Select(columns).Order("listing.observed_at DESC,listing.id ASC").Offset((p.Page - 1) * p.PageSize).Limit(p.PageSize).Scan(&entries).Error
	for i := range entries {
		entries[i].ImageURL = model.PublicCoverURL(entries[i].ImageURL)
	}
	return entries, total, err
}
