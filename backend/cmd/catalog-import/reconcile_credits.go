package main

import (
	"fmt"
	"strings"

	"gorm.io/gorm"
	"gorm.io/gorm/clause"
	"musebooks/model"
)

func validateCoverOnlyCorrection(r Record) error {
	if !r.UseCoverCreditsOnly {
		return nil
	}
	if r.Work.PublicationType != model.PublicationTypeMagazineIssue || r.Work.OriginCode != "KR" || r.Work.IssueMonth == "" || r.Work.FeaturedNames != "" || r.FeaturedPerson != nil || r.CoverPerson == nil || len(r.Batch.Items) != 0 {
		return fmt.Errorf("cover-only correction requires a metadata-only Korean magazine with explicit cover credits and no featured names")
	}
	return nil
}

// Clearing the legacy text lets the existing synchronization trigger remove
// its generated featured rows. Explicit cover credits and people remain intact.
func guardCoverOnlyCorrection(tx *gorm.DB, r Record) error {
	if err := validateCoverOnlyCorrection(r); err != nil {
		return err
	}
	var work model.Work
	if err := tx.Clauses(clause.Locking{Strength: "UPDATE"}).First(&work, "id = ?", r.Work.ID).Error; err != nil {
		return err
	}
	if work.PublicationType != model.PublicationTypeMagazineIssue || work.OriginCode != "KR" || work.IssueMonth != r.Work.IssueMonth || work.Status != "published" {
		return fmt.Errorf("cover-only correction conflicts with the existing issue")
	}
	var credits []model.WorkPerson
	if err := tx.Preload("Person").Where("work_id = ?", work.ID).Find(&credits).Error; err != nil {
		return err
	}
	covered, names, slugs := map[int64]bool{}, map[string]bool{}, map[string]bool{}
	for _, c := range credits {
		if c.Role == "cover_model" && c.CreditSource == "verified_cover_credit" {
			covered[c.PersonID] = true
			slugs[c.Person.Slug] = true
			for _, name := range []string{c.CreditedName, c.Person.CanonicalPublicName, c.Person.OriginalName} {
				names[strings.TrimSpace(name)] = true
			}
		}
	}
	if len(covered) == 0 {
		return fmt.Errorf("cover-only correction requires existing verified cover credits")
	}
	requested := append([]model.Person{*r.CoverPerson}, r.AdditionalCoverPeople...)
	for _, person := range requested {
		if !slugs[person.Slug] {
			return fmt.Errorf("cover-only correction cannot introduce a new cover identity")
		}
	}
	for _, c := range credits {
		if c.Role == "featured" && (c.CreditSource != "legacy_credit" || !covered[c.PersonID]) {
			return fmt.Errorf("cover-only correction would remove an independent featured credit")
		}
		if c.CreditSource == "legacy_credit" && c.Role != "featured" {
			return fmt.Errorf("cover-only correction has an unexpected legacy role")
		}
	}
	for _, name := range strings.Split(work.FeaturedNames, ",") {
		if name = strings.TrimSpace(name); name != "" && !names[name] {
			return fmt.Errorf("cover-only correction has an unverified name: %s", name)
		}
	}
	return nil
}
