package main

import (
	"fmt"
	"gorm.io/gorm"
	"gorm.io/gorm/clause"
	"musebooks/model"
	"strings"
)

// This explicit correction removes only a trigger-generated duplicate work link.
// Both person rows survive; an existing verified canonical subject is required.
func validateFeaturedAliasCorrection(r Record) error {
	if r.ReplaceLegacyFeaturedAlias == "" {
		return nil
	}
	if r.Work.PublicationType != model.PublicationTypePhotobook || r.Work.OriginCode != "KR" || r.Work.IssueMonth != "" || r.FeaturedPerson == nil || !validPersonIdentity(r.FeaturedPerson) || r.Work.FeaturedNames != r.FeaturedPerson.CanonicalPublicName || r.ReplaceLegacyFeaturedAlias == r.Work.FeaturedNames || strings.Contains(r.ReplaceLegacyFeaturedAlias, ",") || !validHTTPSURL(r.Edition.MetadataSourceURL) || r.UseCoverCreditsOnly {
		return fmt.Errorf("featured alias correction requires one reviewed Korean photobook subject and a distinct legacy alias")
	}
	return nil
}

func guardFeaturedAliasCorrection(tx *gorm.DB, r Record) error {
	if err := validateFeaturedAliasCorrection(r); err != nil {
		return err
	}
	var work model.Work
	if err := tx.Clauses(clause.Locking{Strength: "UPDATE"}).First(&work, "id = ?", r.Work.ID).Error; err != nil {
		return err
	}
	if work.Status != "published" || work.PublicationType != model.PublicationTypePhotobook || work.OriginCode != "KR" || work.IssueMonth != "" {
		return fmt.Errorf("featured alias correction conflicts with existing work")
	}
	for _, name := range strings.Split(work.FeaturedNames, ",") {
		name = strings.TrimSpace(name)
		if name != r.ReplaceLegacyFeaturedAlias && name != r.Work.FeaturedNames {
			return fmt.Errorf("featured alias correction would discard another subject")
		}
	}
	var credits []model.WorkPerson
	if err := tx.Preload("Person").Where("work_id = ?", work.ID).Find(&credits).Error; err != nil {
		return err
	}
	canonicalFound := false
	var canonicalID int64
	for _, c := range credits {
		if c.Role != "featured" {
			return fmt.Errorf("featured alias correction has an unexpected role")
		}
		if c.Person.Slug == r.FeaturedPerson.Slug && c.CreditSource == "verified_model_capture" && c.Person.VerificationSourceURL != "" {
			canonicalFound = true
			canonicalID = c.PersonID
			continue
		}
		if c.CreditSource != "legacy_credit" || c.CreditedName != r.ReplaceLegacyFeaturedAlias || c.Person.CanonicalPublicName != r.ReplaceLegacyFeaturedAlias || c.Person.VerificationSourceURL != "" {
			return fmt.Errorf("featured alias correction would remove an independent verified credit")
		}
	}
	if !canonicalFound {
		return fmt.Errorf("featured alias correction requires an existing verified canonical subject")
	}
	aliasSlug := model.CatalogIdentity("model", r.ReplaceLegacyFeaturedAlias)
	var conflicts int64
	if err := tx.Table("person_aliases").Where("alias_slug = ? AND person_id <> ?", aliasSlug, canonicalID).Count(&conflicts).Error; err != nil {
		return err
	}
	if conflicts != 0 {
		return fmt.Errorf("featured alias correction conflicts with another alias mapping")
	}
	return tx.Exec("INSERT INTO person_aliases(alias_slug,person_id,alias_name,source) VALUES(?,?,?,?) ON CONFLICT(alias_slug,person_id) DO NOTHING", aliasSlug, canonicalID, r.ReplaceLegacyFeaturedAlias, "verified_model_capture").Error
}
