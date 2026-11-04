package repository

import (
	"context"
	"gorm.io/gorm"
	"musebooks/model"
	"strings"
)

func mediaPermissionPredicate(alias string, primaryOnly bool) string {
	primary := ""
	if primaryOnly {
		primary = " AND " + alias + ".is_primary = TRUE"
	}
	return alias + ".permission_scope IN ('remote_display','display_and_copy')" +
		" AND " + alias + ".permission_reviewed_at IS NOT NULL" +
		" AND " + alias + ".permission_evidence_url LIKE 'https://%'" +
		" AND " + alias + ".source_url LIKE 'https://%'" +
		" AND " + alias + ".original_url LIKE 'https://%'" +
		" AND " + alias + ".storage_url LIKE 'https://%'" +
		" AND (" + alias + ".permission_scope = 'display_and_copy' OR " + alias + ".original_url = " + alias + ".storage_url)" + primary
}

func mediaURLValueSQL(alias string) string {
	return "CASE WHEN " + alias + ".permission_scope = 'remote_display' THEN " + alias + ".original_url ELSE " + alias + ".storage_url END"
}

func approvedMediaSQL(entityType, entityID, field string, primaryOnly bool) string {
	value := mediaURLValueSQL("cm")
	if field == "permission_scope" {
		value = "cm.permission_scope"
	}
	return "(SELECT " + value + " FROM catalog_media cm WHERE cm.entity_type = '" + entityType + "' AND cm.entity_id = " + entityID +
		" AND " + mediaPermissionPredicate("cm", primaryOnly) + " ORDER BY cm.is_primary DESC, cm.id ASC LIMIT 1)"
}

func directoryMediaSQL(kind, field string) string {
	eligibleWorks := "SELECT wp.work_id FROM work_people wp JOIN works w ON w.id=wp.work_id WHERE wp.person_id=directory.id AND wp.role IN ('featured','cover_model') AND w.status='published'"
	eligibleEditions := "SELECT e.id FROM editions e WHERE e.work_id IN (" + eligibleWorks + ") AND e.status<>'superseded'"
	if kind == "publisher" {
		eligibleWorks = "SELECT e.work_id FROM editions e JOIN works w ON w.id=e.work_id WHERE e.publisher_company_id=directory.id AND e.status<>'superseded' AND w.status='published'"
		eligibleEditions = "SELECT e.id FROM editions e WHERE e.publisher_company_id=directory.id AND e.work_id IN (" + eligibleWorks + ") AND e.status<>'superseded'"
	}
	value := mediaURLValueSQL("cm")
	if field == "permission_scope" {
		value = "cm.permission_scope"
	}
	return "(SELECT " + value + " FROM catalog_media cm WHERE ((cm.entity_type='work' AND cm.entity_id IN (" + eligibleWorks + ")) OR (cm.entity_type='edition' AND cm.entity_id IN (" + eligibleEditions + "))) AND " +
		mediaPermissionPredicate("cm", true) + " ORDER BY CASE WHEN cm.entity_type='edition' THEN 0 ELSE 1 END,cm.entity_id ASC,cm.id ASC LIMIT 1)"
}

// canonicalPersonSlug maps a merged alias profile (e.g. an old /models link for
// a romanised name) to the person it was merged into. A slug that still has its
// own credits, or an alias claimed by several people, is returned unchanged.
func (r *CatalogRepository) canonicalPersonSlug(ctx context.Context, slug string) string {
	if slug == "" {
		return slug
	}
	var targets []string
	err := r.db.WithContext(ctx).Raw(`SELECT p.slug FROM person_aliases pa JOIN people p ON p.id=pa.person_id
 WHERE pa.alias_slug=? AND NOT EXISTS (SELECT 1 FROM people d JOIN work_people wp ON wp.person_id=d.id WHERE d.slug=?)`, slug, slug).Scan(&targets).Error
	if err != nil || len(targets) != 1 {
		return slug
	}
	return targets[0]
}

func (r *CatalogRepository) Directory(ctx context.Context, p model.CatalogBrowseQuery) ([]model.DirectoryEntry, int64, error) {
	if p.Kind != "publisher" {
		p.ID = r.canonicalPersonSlug(ctx, p.ID)
	}
	query := r.db.WithContext(ctx).Table("people AS directory")
	columns := `directory.slug AS id, directory.canonical_public_name AS name,directory.original_name,directory.english_name,directory.verification_source_url AS official_url,
 (SELECT COUNT(DISTINCT w.id) FROM work_people wp JOIN works w ON w.id=wp.work_id WHERE wp.person_id=directory.id AND wp.role IN ('featured','cover_model') AND w.status='published') AS work_count,
 (SELECT COUNT(DISTINCT e.id) FROM work_people wp JOIN works w ON w.id=wp.work_id JOIN editions e ON e.work_id=w.id WHERE wp.person_id=directory.id AND wp.role IN ('featured','cover_model') AND w.status='published' AND e.status<>'superseded') AS edition_count,
 (SELECT string_agg(pa.alias_name, ',' ORDER BY pa.alias_name) FROM person_aliases pa WHERE pa.person_id=directory.id) AS aliases`
	columns += "," + directoryMediaSQL("model", "url") + " AS cover_url," + directoryMediaSQL("model", "permission_scope") + " AS cover_permission_scope"
	query = query.Where("EXISTS (SELECT 1 FROM work_people wp JOIN works w ON w.id=wp.work_id WHERE wp.person_id=directory.id AND wp.role IN ('featured','cover_model') AND w.status='published')")
	name := "directory.canonical_public_name"
	if p.Kind == "publisher" {
		query = r.db.WithContext(ctx).Table("companies AS directory").Where("EXISTS (SELECT 1 FROM editions e JOIN works w ON w.id=e.work_id WHERE e.publisher_company_id=directory.id AND e.status<>'superseded' AND w.status='published')")
		name = "directory.canonical_name"
		columns = `directory.slug AS id,directory.canonical_name AS name,directory.official_url,
 (SELECT COUNT(DISTINCT w.id) FROM editions e JOIN works w ON w.id=e.work_id WHERE e.publisher_company_id=directory.id AND e.status<>'superseded' AND w.status='published') AS work_count,
			(SELECT COUNT(*) FROM editions e JOIN works w ON w.id=e.work_id WHERE e.publisher_company_id=directory.id AND e.status<>'superseded' AND w.status='published') AS edition_count`
		columns += "," + directoryMediaSQL("publisher", "url") + " AS cover_url," + directoryMediaSQL("publisher", "permission_scope") + " AS cover_permission_scope"
	}
	if p.ID != "" {
		query = query.Where("directory.slug = ?", p.ID)
	}
	if p.Query != "" && p.Kind == "model" {
		term := "%" + p.Query + "%"
		query = query.Where("directory.canonical_public_name ILIKE ? OR directory.original_name ILIKE ? OR directory.english_name ILIKE ? OR directory.traditional_chinese_name ILIKE ? OR directory.simplified_chinese_name ILIKE ? OR EXISTS (SELECT 1 FROM person_aliases pa WHERE pa.person_id=directory.id AND pa.alias_name ILIKE ?)", term, term, term, term, term, term)
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
		entries[i].CoverURL = model.ApprovedImageURL(entries[i].CoverURL, entries[i].CoverPermissionScope)
	}
	return entries, total, err
}
func (r *CatalogRepository) DirectoryBooks(ctx context.Context, p model.CatalogBrowseQuery) ([]model.Work, int64, error) {
	if p.Kind != "publisher" {
		p.ID = r.canonicalPersonSlug(ctx, p.ID)
	}
	query := r.db.WithContext(ctx).Model(&model.Work{}).Where("works.status = ?", "published")
	if p.Kind == "publisher" {
		query = query.Where("EXISTS (SELECT 1 FROM editions e JOIN companies c ON c.id=e.publisher_company_id WHERE e.work_id=works.id AND e.status<>'superseded' AND c.slug=?)", p.ID)
	} else {
		query = query.Where("EXISTS (SELECT 1 FROM work_people wp JOIN people p ON p.id=wp.person_id WHERE wp.work_id=works.id AND wp.role IN ('featured','cover_model') AND p.slug=?)", p.ID)
	}
	if p.PublicationType != "" {
		query = query.Where("works.publication_type = ?", p.PublicationType)
	}
	if p.Query != "" {
		term := "%" + p.Query + "%"
		query = query.Where("works.original_title ILIKE ? OR works.english_title ILIKE ? OR works.featured_names ILIKE ? OR EXISTS (SELECT 1 FROM work_people wp JOIN people p ON p.id=wp.person_id WHERE wp.work_id=works.id AND wp.role IN ('featured','cover_model') AND p.canonical_public_name ILIKE ?)", term, term, term, term)
	}
	if p.Person != "" {
		query = query.Where("EXISTS (SELECT 1 FROM work_people wp JOIN people p ON p.id=wp.person_id WHERE wp.work_id=works.id AND wp.role IN ('featured','cover_model') AND (p.slug=? OR p.canonical_public_name ILIKE ?))", p.Person, "%"+p.Person+"%")
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
		editionFilter += " AND EXTRACT(YEAR FROM COALESCE(CASE WHEN e.format='digital' THEN e.store_release_date ELSE e.publication_date END,e.publication_date,e.store_release_date,e.release_date,works.issue_date,CASE WHEN works.issue_month ~ '^[0-9]{4}-(0[1-9]|1[0-2])$' THEN to_date(works.issue_month || '-01','YYYY-MM-DD') END))=?"
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
			db = db.Where("EXTRACT(YEAR FROM COALESCE(CASE WHEN editions.format='digital' THEN editions.store_release_date ELSE editions.publication_date END,editions.publication_date,editions.store_release_date,editions.release_date,(SELECT COALESCE(issue_date,CASE WHEN issue_month ~ '^[0-9]{4}-(0[1-9]|1[0-2])$' THEN to_date(issue_month || '-01','YYYY-MM-DD') END) FROM works WHERE works.id=editions.work_id)))=?", p.Year)
		}
		return db.Order("COALESCE(CASE WHEN editions.format='digital' THEN editions.store_release_date ELSE editions.publication_date END,editions.publication_date,editions.store_release_date,editions.release_date,(SELECT COALESCE(issue_date,CASE WHEN issue_month ~ '^[0-9]{4}-(0[1-9]|1[0-2])$' THEN to_date(issue_month || '-01','YYYY-MM-DD') END) FROM works WHERE works.id=editions.work_id)) DESC NULLS LAST,id")
	}).Preload("Credits.Person").Preload("Editions.PublisherCompany").Preload("Editions.Listings").Preload("Editions.Listings.Source")
	// Newest typed publication/release date first; undated works follow, by title.
	err := query.Order("COALESCE((SELECT MAX(COALESCE(CASE WHEN e.format='digital' THEN e.store_release_date ELSE e.publication_date END,e.publication_date,e.store_release_date,e.release_date)) FROM editions e WHERE e.work_id=works.id AND e.status<>'superseded'),works.issue_date,CASE WHEN works.issue_month ~ '^[0-9]{4}-(0[1-9]|1[0-2])$' THEN to_date(works.issue_month || '-01','YYYY-MM-DD') END) DESC NULLS LAST,works.original_title,works.id").Offset((p.Page - 1) * p.PageSize).Limit(p.PageSize).Find(&works).Error
	if err == nil {
		err = r.loadBookMedia(ctx, works)
	}
	return works, total, err
}
func (r *CatalogRepository) Listings(ctx context.Context, p model.CatalogBrowseQuery) ([]model.MarketEntry, int64, error) {
	p.Person = r.canonicalPersonSlug(ctx, p.Person)
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
	if p.PublicationType != "" {
		query = query.Where("w.publication_type = ?", p.PublicationType)
	}
	if p.Source != "" {
		query = query.Where("feed.source_id = ?", p.Source)
	}
	if p.Person != "" {
		query = query.Where("EXISTS (SELECT 1 FROM work_people wp JOIN people p ON p.id=wp.person_id WHERE wp.work_id=w.id AND wp.role IN ('featured','cover_model') AND p.slug=?)", p.Person)
	}
	if p.Publisher != "" {
		query = query.Where("e.publisher_company_id IN (SELECT id FROM companies WHERE slug=?)", p.Publisher)
	}
	if p.Query != "" {
		term := "%" + p.Query + "%"
		query = query.Where("feed.title ILIKE ? OR w.original_title ILIKE ? OR w.featured_names ILIKE ? OR e.publisher ILIKE ? OR EXISTS (SELECT 1 FROM work_people wp JOIN people p ON p.id=wp.person_id WHERE wp.work_id=w.id AND wp.role IN ('featured','cover_model') AND p.canonical_public_name ILIKE ?)", term, term, term, term, term)
	}
	var total int64
	if err := query.Session(&gorm.Session{}).Count(&total).Error; err != nil {
		return nil, 0, err
	}
	columns := `feed.source_listing_id AS id,feed.external_listing_id AS external_id,feed.original_url AS url,feed.title,
 feed.seller_location,feed.condition,feed.format,feed.price_minor,feed.original_currency_code AS currency,feed.price_type,feed.price_basis,feed.price_components,
 feed.shipping_text,feed.observed_at,feed.last_seen_at,
 s.id AS source_id,s.name AS source_name,s.region AS source_region,s.kind AS source_kind,feed.format AS source_photobook_format,
	 w.id AS work_id,w.slug AS work_slug,w.original_title AS work_title,COALESCE(NULLIF(w.featured_names,''),(SELECT string_agg(DISTINCT wp.credited_name, ', ') FROM work_people wp WHERE wp.work_id=w.id AND wp.role='cover_model')) AS featured_names_text,
	 e.id AS edition_id,e.edition_label,e.publisher,e.publication_date,e.publication_date_precision,e.store_release_date,e.store_release_date_precision,w.issue_date,w.issue_date_precision,
	 COALESCE(` + approvedMediaSQL("edition", "e.id", "url", true) + "," + approvedMediaSQL("work", "w.id", "url", true) + `) AS cover_url,
	 COALESCE(` + approvedMediaSQL("edition", "e.id", "permission_scope", true) + "," + approvedMediaSQL("work", "w.id", "permission_scope", true) + `) AS cover_permission_scope,
 CASE WHEN feed.format='digital' THEN 'digital_retail' WHEN s.kind='bookstore' THEN 'physical_retail' WHEN ` + "'" + status + "'" + `='completed' THEN 'marketplace_sold' ELSE 'marketplace_asking' END AS price_category,` + "'" + status + "' AS status"
	entries := []model.MarketEntry{}
	err := query.Select(columns).Order("feed.observed_at DESC,feed.source_listing_id ASC").Offset((p.Page - 1) * p.PageSize).Limit(p.PageSize).Scan(&entries).Error
	for i := range entries {
		entries[i].SetFeaturedNames()
		entries[i].CoverURL = model.ApprovedImageURL(entries[i].CoverURL, entries[i].CoverPermissionScope)
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
		Where("listing.status <> ?", "excluded")
	if p.Kind == "offers" {
		query = query.Where("lower(source.kind) = ? OR (lower(source.kind) IN ? AND listing.digital_access = ? AND listing.format_candidate = ?)", "marketplace", []string{"bookstore", "digital_store"}, "authorized_store", "digital")
	} else {
		query = query.Where("lower(source.kind)=?", "marketplace")
	}
	if p.Status == "active" || p.Status == "completed" {
		query = query.Where("listing.status = ?", p.Status)
	}
	if p.Format != "" {
		query = query.Where("listing.format_candidate = ?", p.Format)
	}
	if p.PublicationType != "" {
		query = query.Where("work.publication_type = ?", p.PublicationType)
	}
	if p.Source != "" {
		query = query.Where("listing.source_id = ?", p.Source)
	}
	if len(p.ModelSlugs) > 0 {
		query = query.Where(`EXISTS (
 SELECT 1 FROM work_people model_wp JOIN people model_person ON model_person.id=model_wp.person_id
 WHERE model_wp.work_id=work.id AND model_wp.role IN ('featured','cover_model') AND model_person.slug IN ?
 )`, p.ModelSlugs)
	}
	if p.Query != "" {
		term := "%" + p.Query + "%"
		query = query.Where("listing.title ILIKE ? OR work.original_title ILIKE ? OR work.featured_names ILIKE ? OR edition.publisher ILIKE ? OR EXISTS (SELECT 1 FROM work_people wp JOIN people p ON p.id=wp.person_id LEFT JOIN person_aliases pa ON pa.person_id=p.id WHERE wp.work_id=work.id AND wp.role IN ('featured','cover_model') AND (p.canonical_public_name ILIKE ? OR p.original_name ILIKE ? OR p.english_name ILIKE ? OR pa.alias_name ILIKE ?))", term, term, term, term, term, term, term, term)
	}
	var total int64
	if err := query.Session(&gorm.Session{}).Count(&total).Error; err != nil {
		return nil, 0, err
	}
	if p.CursorMode && p.CursorID != "" {
		if p.Sort == "title" {
			title := "COALESCE(NULLIF(work.original_title,''),listing.title,'')"
			query = query.Where("(("+title+" > ?) OR ("+title+" = ? AND (listing.observed_at < ? OR (listing.observed_at = ? AND listing.id > ?))))", p.CursorTitle, p.CursorTitle, *p.CursorObservedAt, *p.CursorObservedAt, p.CursorID)
		} else if p.CursorObservedAt != nil {
			query = query.Where("(listing.observed_at < ? OR (listing.observed_at = ? AND listing.id > ?))", *p.CursorObservedAt, *p.CursorObservedAt, p.CursorID)
		}
	}
	columns := `listing.id,listing.external_id,listing.url,listing.title,listing.seller_location,listing.condition,
	 listing.format_candidate AS format,listing.status,listing.price_minor,listing.currency,listing.price_type,listing.price_basis,listing.price_components,
 listing.shipping_text,listing.observed_at,listing.last_seen_at,` + approvedMediaSQL("listing", "listing.id", "url", true) + ` AS image_url,
 ` + approvedMediaSQL("listing", "listing.id", "permission_scope", true) + ` AS image_permission_scope,
 source.id AS source_id,source.name AS source_name,source.region AS source_region,source.kind AS source_kind,
 listing.format_candidate AS source_photobook_format,
 CASE WHEN listing.format_candidate='digital' THEN 'digital_retail' WHEN source.kind='bookstore' THEN 'physical_retail'
 WHEN listing.status='completed' THEN 'marketplace_sold' ELSE 'marketplace_asking' END AS price_category,
	 (work.id IS NOT NULL) AS catalog_matched,work.original_title AS work_title,work.slug AS work_slug,COALESCE(NULLIF(work.featured_names,''),(SELECT string_agg(DISTINCT wp.credited_name, ', ') FROM work_people wp WHERE wp.work_id=work.id AND wp.role='cover_model')) AS featured_names,
	 edition.edition_label,edition.publisher,edition.release_date,edition.release_precision,
	 edition.publication_date,edition.publication_date_precision,edition.publication_date_source_url,
	 edition.store_release_date,edition.store_release_date_precision,edition.store_release_date_source_url,
	 work.issue_date,work.issue_date_precision,work.issue_date_source_url`
	selectArgs := []any{}
	if len(p.ModelSlugs) > 0 {
		columns += `,(SELECT string_agg(DISTINCT matched_person.canonical_public_name, ',')
 FROM work_people matched_wp JOIN people matched_person ON matched_person.id=matched_wp.person_id
 WHERE matched_wp.work_id=work.id AND matched_wp.role IN ('featured','cover_model') AND matched_person.slug IN ?) AS matched_model_names`
		selectArgs = append(selectArgs, p.ModelSlugs)
	} else {
		columns += `,'' AS matched_model_names`
	}
	entries := []model.MarketplaceListingEntry{}
	order := "listing.observed_at DESC,listing.id ASC"
	if p.Sort == "title" {
		order = "COALESCE(NULLIF(work.original_title,''),listing.title,'') ASC,listing.observed_at DESC,listing.id ASC"
	}
	query = query.Select(columns, selectArgs...).Order(order)
	if !p.CursorMode {
		query = query.Offset((p.Page - 1) * p.PageSize)
	}
	err := query.Limit(p.PageSize).Scan(&entries).Error
	for i := range entries {
		entries[i].ImageURL = model.ApprovedImageURL(entries[i].ImageURL, entries[i].ImagePermissionScope)
	}
	return entries, total, err
}
