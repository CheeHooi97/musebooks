package main

import (
	"errors"
	"fmt"
	"sort"
	"strings"
	"time"

	"musebooks/model"

	"gorm.io/gorm"
	"gorm.io/gorm/clause"
)

type SourceEvidenceInput struct {
	EntityType string    `json:"entityType"`
	EntityID   string    `json:"entityId"`
	Fields     []string  `json:"fields"`
	SourceID   string    `json:"sourceId"`
	Scope      string    `json:"scope"`
	SourceURL  string    `json:"sourceUrl"`
	CapturedAt time.Time `json:"capturedAt"`
}

type expectedEvidence struct {
	entityType string
	entityID   string
	fieldKey   string
	grantField string
	scope      string
	sourceURL  string
}

func sourceEvidenceKey(entityType, entityID, fieldKey string) string {
	return entityType + "\x00" + entityID + "\x00" + fieldKey
}

func expectedSourceEvidence(record Record) (map[string]expectedEvidence, error) {
	expected := map[string]expectedEvidence{}
	if record.Work.ID == "" && record.Edition.ID == "" {
		return expected, nil
	}
	if record.Work.ID == "" || record.Edition.ID == "" || record.Edition.WorkID != record.Work.ID {
		return nil, fmt.Errorf("source evidence requires a linked work and edition")
	}
	metadataURL := strings.TrimSpace(record.Edition.MetadataSourceURL)
	featuredCreditURL := strings.TrimSpace(record.FeaturedCreditSourceURL)
	if featuredCreditURL == "" {
		featuredCreditURL = metadataURL
	}
	coverCreditURL := strings.TrimSpace(record.CoverCreditSourceURL)
	if coverCreditURL == "" {
		coverCreditURL = metadataURL
	}
	add := func(entityType, entityID, fieldKey, grantField, scope, sourceURL string) error {
		if strings.TrimSpace(entityID) == "" || !validHTTPSURL(sourceURL) {
			return fmt.Errorf("source evidence for %s requires an entity and HTTPS field source", fieldKey)
		}
		key := sourceEvidenceKey(entityType, entityID, fieldKey)
		value := expectedEvidence{entityType, entityID, fieldKey, grantField, scope, sourceURL}
		if previous, exists := expected[key]; exists {
			if previous == value {
				return nil
			}
			return fmt.Errorf("conflicting expected source evidence field %s", fieldKey)
		}
		expected[key] = value
		return nil
	}
	addMetadata := func(entityType, entityID, fieldKey, grantField string) error {
		return add(entityType, entityID, fieldKey, grantField, model.SourcePermissionScopeBibliography, metadataURL)
	}

	if err := addMetadata("work", record.Work.ID, "title", "title"); err != nil {
		return nil, err
	}
	if err := addMetadata("work", record.Work.ID, "origin", "origin"); err != nil {
		return nil, err
	}
	if err := addMetadata("edition", record.Edition.ID, "metadata_source_url", "url"); err != nil {
		return nil, err
	}
	if err := addMetadata("edition", record.Edition.ID, "format", "format"); err != nil {
		return nil, err
	}
	workFields := []struct{ value, key, grantField string }{
		{record.Work.EnglishTitle, "english_title", "english_title"},
		{record.Work.Summary, "summary", "summary"},
		{record.Work.Photographer, "photographer", "photographer"},
		{record.Work.PublicationType, "publication_type", "publication_type"},
		{record.Work.IssueMonth, "issue_month", "issue_month"},
		{record.Work.IssueNumber, "issue_number", "issue_number"},
	}
	for _, field := range workFields {
		if strings.TrimSpace(field.value) == "" {
			continue
		}
		if err := addMetadata("work", record.Work.ID, field.key, field.grantField); err != nil {
			return nil, err
		}
	}
	if strings.TrimSpace(record.Work.FeaturedNames) != "" {
		if err := add("work", record.Work.ID, "featured_names", "model_credit", model.SourcePermissionScopeBibliography, featuredCreditURL); err != nil {
			return nil, err
		}
	}
	editionFields := []struct{ value, key, grantField string }{
		{record.Edition.EditionLabel, "edition_label", "edition_label"},
		{record.Edition.Language, "language", "language"},
		{record.Edition.EditionMarket, "edition_market", "edition_market"},
		{record.Edition.Publisher, "publisher", "publisher"},
		{record.Edition.ISBN, "isbn", "isbn"},
		{record.Edition.EditionVariant, "edition_variant", "edition_variant"},
		{record.Edition.ContentSummary, "content_summary", "content_summary"},
		{record.Edition.SeriesName, "series_name", "series_name"},
		{record.Edition.Dimensions, "dimensions", "dimensions"},
	}
	for _, field := range editionFields {
		if strings.TrimSpace(field.value) == "" {
			continue
		}
		if err := addMetadata("edition", record.Edition.ID, field.key, field.grantField); err != nil {
			return nil, err
		}
	}
	if record.Edition.PageCount != 0 {
		if err := addMetadata("edition", record.Edition.ID, "page_count", "page_count"); err != nil {
			return nil, err
		}
	}
	if record.Edition.ReleaseDate != nil {
		if err := addMetadata("edition", record.Edition.ID, "release_date", "release_date"); err != nil {
			return nil, err
		}
		if err := addMetadata("edition", record.Edition.ID, "release_precision", "release_precision"); err != nil {
			return nil, err
		}
	}
	if strings.TrimSpace(record.Work.CoverURL) != "" {
		if err := add("work_image", record.Work.ID, "cover_url", "image_url", model.SourcePermissionScopeProductImages, metadataURL); err != nil {
			return nil, err
		}
	}
	if strings.TrimSpace(record.Edition.CoverURL) != "" {
		if err := add("edition_image", record.Edition.ID, "cover_url", "image_url", model.SourcePermissionScopeProductImages, metadataURL); err != nil {
			return nil, err
		}
	}
	if strings.TrimSpace(record.Edition.OriginalCoverURL) != "" {
		if err := add("edition_image", record.Edition.ID, "original_cover_url", "image_url", model.SourcePermissionScopeProductImages, metadataURL); err != nil {
			return nil, err
		}
	}
	if strings.TrimSpace(record.Edition.CoverObjectKey) != "" {
		if err := add("edition_image", record.Edition.ID, "cover_object_key", "image_url", model.SourcePermissionScopeProductImages, metadataURL); err != nil {
			return nil, err
		}
	}
	dateFields := []struct {
		entityType, entityID, key, grantField, sourceURL string
		value                                            *time.Time
		precision                                        string
	}{
		{"work", record.Work.ID, "issue_date", "issue_date", record.Work.IssueDateSourceURL, record.Work.IssueDate, record.Work.IssueDatePrecision},
		{"edition", record.Edition.ID, "publication_date", "publication_date", record.Edition.PublicationDateSourceURL, record.Edition.PublicationDate, record.Edition.PublicationDatePrecision},
		{"edition", record.Edition.ID, "store_release_date", "store_release_date", record.Edition.StoreReleaseDateSourceURL, record.Edition.StoreReleaseDate, record.Edition.StoreReleaseDatePrecision},
	}
	for _, date := range dateFields {
		if date.value == nil {
			continue
		}
		if err := add(date.entityType, date.entityID, date.key, date.grantField, model.SourcePermissionScopeBibliography, date.sourceURL); err != nil {
			return nil, err
		}
		if err := add(date.entityType, date.entityID, date.key+"_precision", date.key+"_precision", model.SourcePermissionScopeBibliography, date.sourceURL); err != nil {
			return nil, err
		}
	}
	addPerson := func(person *model.Person, role string) error {
		if person == nil {
			return nil
		}
		if err := add("person", person.Slug, "identity", "model_identity", model.SourcePermissionScopeBibliography, person.VerificationSourceURL); err != nil {
			return err
		}
		field := "model_credit"
		creditURL := featuredCreditURL
		if role == "cover" {
			field = "cover_credit"
			creditURL = coverCreditURL
		}
		return add("work_credit", record.Work.ID, role+":"+person.Slug, field, model.SourcePermissionScopeBibliography, creditURL)
	}
	if err := addPerson(record.FeaturedPerson, "featured"); err != nil {
		return nil, err
	}
	for i := range record.AdditionalFeaturedPeople {
		if err := addPerson(&record.AdditionalFeaturedPeople[i], "featured"); err != nil {
			return nil, err
		}
	}
	if err := addPerson(record.CoverPerson, "cover"); err != nil {
		return nil, err
	}
	for i := range record.AdditionalCoverPeople {
		if err := addPerson(&record.AdditionalCoverPeople[i], "cover"); err != nil {
			return nil, err
		}
	}
	for _, image := range record.PublisherMedia {
		if err := add("edition_image", record.Edition.ID, image.MediaType, "image_url", model.SourcePermissionScopeProductImages, image.SourceURL); err != nil {
			return nil, err
		}
	}
	for _, image := range record.WorkMedia {
		if err := add("work_image", record.Work.ID, image.MediaType, "image_url", model.SourcePermissionScopeProductImages, image.SourceURL); err != nil {
			return nil, err
		}
	}
	return expected, nil
}

func validateSourceEvidence(record Record) ([]model.CatalogSourceEvidence, error) {
	expected, err := expectedSourceEvidence(record)
	if err != nil {
		return nil, err
	}
	provided := make(map[string]SourceEvidenceInput, len(record.SourceEvidence))
	for _, input := range record.SourceEvidence {
		if strings.TrimSpace(input.SourceID) == "" || !validHTTPSURL(input.SourceURL) || input.CapturedAt.IsZero() || len(input.Fields) == 0 {
			return nil, fmt.Errorf("source evidence requires a route, HTTPS source URL, capture time, and field list")
		}
		for _, fieldKey := range input.Fields {
			key := sourceEvidenceKey(input.EntityType, input.EntityID, strings.TrimSpace(fieldKey))
			if _, duplicate := provided[key]; duplicate {
				return nil, fmt.Errorf("duplicate source evidence for %s", fieldKey)
			}
			provided[key] = input
		}
	}
	if len(provided) != len(expected) {
		return nil, fmt.Errorf("source evidence covers %d fields; expected %d", len(provided), len(expected))
	}
	rows := make([]model.CatalogSourceEvidence, 0, len(expected))
	for key, requirement := range expected {
		input, ok := provided[key]
		if !ok || input.SourceURL != requirement.sourceURL || input.Scope != requirement.scope {
			return nil, fmt.Errorf("source evidence is missing or mismatched for %s.%s", requirement.entityType, requirement.fieldKey)
		}
		rows = append(rows, model.CatalogSourceEvidence{
			EntityType: requirement.entityType,
			EntityID:   requirement.entityID,
			FieldKey:   requirement.fieldKey,
			SourceID:   strings.TrimSpace(input.SourceID),
			CapturedAt: input.CapturedAt.UTC().Truncate(time.Microsecond),
			GrantField: requirement.grantField,
			Scope:      requirement.scope,
			SourceURL:  requirement.sourceURL,
		})
	}
	return rows, nil
}

type sourceGrantKey struct {
	sourceID string
	scope    string
}

type sourceGrantCaptureKey struct {
	sourceGrantKey
	capturedAt time.Time
}

func authorizeSourceEvidence(tx *gorm.DB, rows []model.CatalogSourceEvidence, now time.Time) error {
	sources := map[string]model.Source{}
	permissionsByGrant := map[sourceGrantKey]model.SourcePermission{}
	fieldsByGrant := map[sourceGrantKey]map[string]bool{}
	fieldsByCapture := map[sourceGrantCaptureKey]map[string]bool{}
	for _, row := range rows {
		source, ok := sources[row.SourceID]
		if !ok {
			if err := tx.Clauses(clause.Locking{Strength: "SHARE"}).First(&source, "id = ?", row.SourceID).Error; err != nil {
				if errors.Is(err, gorm.ErrRecordNotFound) {
					return fmt.Errorf("source evidence references unregistered route %s", row.SourceID)
				}
				return fmt.Errorf("failed to read source evidence route %s: %w", row.SourceID, err)
			}
			sources[row.SourceID] = source
		}
		if err := model.ValidateSourceURL(source, row.SourceURL); err != nil || !validHTTPSURL(row.SourceURL) {
			return fmt.Errorf("source evidence URL is outside registered route %s", row.SourceID)
		}
		if !model.RequiresSourcePermission(source) {
			continue
		}
		key := sourceGrantKey{source.ID, row.Scope}
		if fieldsByGrant[key] == nil {
			fieldsByGrant[key] = map[string]bool{}
		}
		fieldsByGrant[key][row.GrantField] = true
		captureKey := sourceGrantCaptureKey{sourceGrantKey: key, capturedAt: row.CapturedAt}
		if fieldsByCapture[captureKey] == nil {
			fieldsByCapture[captureKey] = map[string]bool{}
		}
		fieldsByCapture[captureKey][row.GrantField] = true
	}
	uses := []string{model.SourcePermissionUseCollect, model.SourcePermissionUseRetain, model.SourcePermissionUseCatalogView}
	keys := make([]sourceGrantKey, 0, len(fieldsByGrant))
	for key := range fieldsByGrant {
		keys = append(keys, key)
	}
	sort.Slice(keys, func(i, j int) bool {
		if keys[i].sourceID == keys[j].sourceID {
			return keys[i].scope < keys[j].scope
		}
		return keys[i].sourceID < keys[j].sourceID
	})
	for _, key := range keys {
		var permission model.SourcePermission
		if err := tx.Clauses(clause.Locking{Strength: "SHARE"}).Where("source_id = ? AND scope = ?", key.sourceID, key.scope).First(&permission).Error; err != nil {
			if errors.Is(err, gorm.ErrRecordNotFound) {
				return fmt.Errorf("source %s has no reviewed %s grant", key.sourceID, key.scope)
			}
			return fmt.Errorf("failed to read source %s %s grant: %w", key.sourceID, key.scope, err)
		}
		fields := make([]string, 0, len(fieldsByGrant[key]))
		for field := range fieldsByGrant[key] {
			fields = append(fields, field)
		}
		sort.Strings(fields)
		if !permission.Allows(sources[key.sourceID], key.scope, fields, uses, now) {
			return fmt.Errorf("source %s grant does not authorize %s fields: %s", key.sourceID, key.scope, strings.Join(fields, ","))
		}
		permissionsByGrant[key] = permission
	}
	captureKeys := make([]sourceGrantCaptureKey, 0, len(fieldsByCapture))
	for key := range fieldsByCapture {
		captureKeys = append(captureKeys, key)
	}
	sort.Slice(captureKeys, func(i, j int) bool {
		if captureKeys[i].sourceID != captureKeys[j].sourceID {
			return captureKeys[i].sourceID < captureKeys[j].sourceID
		}
		if captureKeys[i].scope != captureKeys[j].scope {
			return captureKeys[i].scope < captureKeys[j].scope
		}
		return captureKeys[i].capturedAt.Before(captureKeys[j].capturedAt)
	})
	for _, key := range captureKeys {
		permission := permissionsByGrant[key.sourceGrantKey]
		fields := make([]string, 0, len(fieldsByCapture[key]))
		for field := range fieldsByCapture[key] {
			fields = append(fields, field)
		}
		sort.Strings(fields)
		if key.capturedAt.After(now.Add(time.Minute)) || permission.ReviewedAt == nil || permission.ReviewedAt.After(key.capturedAt) ||
			!permission.Allows(sources[key.sourceID], key.scope, fields, uses, key.capturedAt) {
			return fmt.Errorf("source %s %s grant did not authorize fields %s when captured at %s", key.sourceID, key.scope, strings.Join(fields, ","), key.capturedAt.Format(time.RFC3339))
		}
	}
	return nil
}

func validateAndAuthorizeSourceEvidence(tx *gorm.DB, records []Record, now time.Time) (map[int][]model.CatalogSourceEvidence, error) {
	rowsByRecord := make(map[int][]model.CatalogSourceEvidence, len(records))
	allRows := []model.CatalogSourceEvidence{}
	for i, record := range records {
		requiresKoreanGate := strings.EqualFold(strings.TrimSpace(record.Work.OriginCode), "KR") || model.RequiresSourcePermission(record.Source)
		if !requiresKoreanGate && len(record.SourceEvidence) == 0 {
			continue
		}
		rows, err := validateSourceEvidence(record)
		if err != nil {
			return nil, fmt.Errorf("record %d: %w", i, err)
		}
		for _, row := range rows {
			if row.CapturedAt.After(now.Add(time.Minute)) {
				return nil, fmt.Errorf("record %d has future source evidence capture time for %s", i, row.FieldKey)
			}
		}
		rowsByRecord[i] = rows
		allRows = append(allRows, rows...)
	}
	if err := authorizeSourceEvidence(tx, allRows, now); err != nil {
		return nil, err
	}
	return rowsByRecord, nil
}
