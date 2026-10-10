// catalog-match links explicit reviewed marketplace identities to verified editions.
package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"gorm.io/gorm"
	"gorm.io/gorm/clause"
	"musebooks/config"
	"musebooks/database"
	"musebooks/model"
	"os"
)

type Match struct {
	SourceID      string `json:"sourceId"`
	ExternalID    string `json:"externalId"`
	ExpectedTitle string `json:"expectedTitle"`
	EditionID     string `json:"editionId"`
	EvidenceURL   string `json:"evidenceUrl"`
	MatchMethod   string `json:"matchMethod"`
	Evidence      string `json:"evidence"`
}

func main() {
	manifest := flag.String("manifest", "", "reviewed exact listing/edition matches")
	apply := flag.Bool("apply", false, "commit reviewed links")
	flag.Parse()
	content, err := os.ReadFile(*manifest)
	if err != nil {
		fail(err)
	}
	var matches []Match
	if err = json.Unmarshal(content, &matches); err != nil {
		fail(err)
	}
	config.LoadConfig()
	db, err := database.Open(!*apply, false)
	if err != nil {
		fail(err)
	}
	err = db.Transaction(func(tx *gorm.DB) error {
		for _, match := range matches {
			if match.SourceID == "" || match.ExternalID == "" || match.ExpectedTitle == "" || match.Evidence == "" ||
				(match.MatchMethod != "reviewed_isbn" && match.MatchMethod != "reviewed_title_cover") {
				return fmt.Errorf("incomplete reviewed match")
			}
			var edition model.Edition
			if err := tx.Where("id = ? AND status = 'published' AND metadata_source_url = ? AND metadata_source_url <> ''", match.EditionID, match.EvidenceURL).First(&edition).Error; err != nil {
				return err
			}
			var listing model.Listing
			query := tx.Where("source_id = ? AND external_id = ? AND title = ? AND status <> 'excluded'", match.SourceID, match.ExternalID, match.ExpectedTitle)
			if *apply {
				query = query.Clauses(clause.Locking{Strength: "UPDATE"})
			}
			if err := query.First(&listing).Error; err != nil {
				return err
			}
			if listing.EditionID != "" && listing.EditionID != match.EditionID {
				return fmt.Errorf("listing %s already links to another edition", match.ExternalID)
			}
			if listing.FormatCandidate != edition.Format {
				return fmt.Errorf("listing format does not match edition")
			}
			if *apply {
				if err := tx.Model(&listing).Update("edition_id", match.EditionID).Error; err != nil {
					return err
				}
				if err := tx.Model(&model.ListingMatch{}).Where("source_listing_id = ?", listing.ID).Update("match_method", match.MatchMethod).Error; err != nil {
					return err
				}
			}
			fmt.Printf("%s/%s -> %s (%s)\n", match.SourceID, match.ExternalID, match.EditionID, match.MatchMethod)
		}
		return nil
	})
	if err != nil {
		fail(err)
	}
	fmt.Printf("Reviewed %d matches; committed=%t\n", len(matches), *apply)
}
func fail(err error) { fmt.Fprintln(os.Stderr, err); os.Exit(1) }
