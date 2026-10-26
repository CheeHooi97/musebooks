package main

import (
	"fmt"
	"gorm.io/gorm"
	"gorm.io/gorm/clause"
	"musebooks/model"
	"net/url"
)

// Reassignment is explicit and restricted to publisher-reviewed MAXIM cover
// variants. Ordinary imports still reject all cross-work edition conflicts.
func validateIssueReassignment(r Record) error {
	if r.ReassignEditionFromWorkID == "" {
		return nil
	}
	page, err := url.Parse(r.Edition.MetadataSourceURL)
	if err != nil || page.Scheme != "https" || (page.Host != "www.maximkorea.net" && page.Host != "maximkorea.net") || page.Path != "/magdb/magdb_view.php" || page.Query().Get("lib") != "M" || page.Query().Get("number") == "" {
		return fmt.Errorf("issue reassignment requires an exact MAXIM publisher product")
	}
	if r.Source.ID != "maxim-korea-manual" || r.Work.PublicationType != model.PublicationTypeMagazineIssue || r.Work.OriginCode != "KR" || r.Work.IssueMonth == "" || r.Work.ID == r.ReassignEditionFromWorkID || r.Edition.Format != "physical" || len(r.Batch.Items) != 1 || r.CoverPerson == nil {
		return fmt.Errorf("issue reassignment requires an explicit publisher-reviewed Korean magazine cover edition")
	}
	return nil
}

func reassignMagazineEdition(tx *gorm.DB, r Record, edition *model.Edition) error {
	if err := validateIssueReassignment(r); err != nil {
		return err
	}
	var source, target model.Work
	if err := tx.Clauses(clause.Locking{Strength: "UPDATE"}).First(&source, "id = ?", r.ReassignEditionFromWorkID).Error; err != nil {
		return err
	}
	if err := tx.Clauses(clause.Locking{Strength: "UPDATE"}).First(&target, "id = ?", r.Work.ID).Error; err != nil {
		return err
	}
	if source.PublicationType != model.PublicationTypeMagazineIssue || target.PublicationType != model.PublicationTypeMagazineIssue || source.OriginCode != "KR" || target.OriginCode != "KR" || source.IssueMonth != r.Work.IssueMonth || target.IssueMonth != r.Work.IssueMonth || target.Status != "published" || edition.Format != "physical" {
		return fmt.Errorf("cannot reconcile different magazine issue identities")
	}
	var remaining int64
	if err := tx.Model(&model.Edition{}).Where("work_id = ?", source.ID).Count(&remaining).Error; err != nil {
		return err
	}
	if edition.WorkID == target.ID {
		if source.Status != "superseded" || remaining != 0 {
			return fmt.Errorf("inconsistent completed issue reassignment")
		}
		return nil
	}
	if edition.WorkID != source.ID || source.Status != "published" || remaining != 1 {
		return fmt.Errorf("issue reassignment requires the source work's sole existing edition")
	}
	// Edition, listing and observation IDs stay unchanged. Retain the old work and
	// credits as superseded history rather than deleting any catalog evidence.
	moved := tx.Model(&model.Edition{}).Where("id = ? AND work_id = ?", edition.ID, source.ID).Update("work_id", target.ID)
	if moved.Error != nil {
		return moved.Error
	}
	if moved.RowsAffected != 1 {
		return fmt.Errorf("edition ownership changed during reassignment")
	}
	if err := tx.Model(&model.Work{}).Where("id = ?", source.ID).Update("status", "superseded").Error; err != nil {
		return err
	}
	edition.WorkID = target.ID
	return nil
}
