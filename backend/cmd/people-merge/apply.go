package main

import (
	"errors"
	"fmt"
	"musebooks/database"
	"os"
	"unicode"

	"gorm.io/gorm"
)

type snapshot struct {
	CreditedPeople int64 `json:"creditedPeople"`
	DuplicatePairs int64 `json:"duplicatePairs"`
	Credits        int64 `json:"credits"`
}

const publishedCredits = `SELECT DISTINCT wp.person_id, wp.work_id FROM work_people wp JOIN works w ON w.id=wp.work_id
 WHERE w.status='published' AND wp.role IN ('featured','cover_model')`

func takeSnapshot(db *gorm.DB) (snapshot, error) {
	var s snapshot
	err := db.Raw(`WITH pw AS (` + publishedCredits + `),
 cnt AS (SELECT person_id, count(*) AS n FROM pw GROUP BY person_id),
 shared AS (SELECT a.person_id AS p1, b.person_id AS p2, count(*) AS shared FROM pw a JOIN pw b ON a.work_id=b.work_id AND a.person_id<b.person_id GROUP BY 1,2)
 SELECT (SELECT count(*) FROM cnt) AS credited_people,
  (SELECT count(*) FROM shared s JOIN cnt c1 ON c1.person_id=s.p1 JOIN cnt c2 ON c2.person_id=s.p2 WHERE s.shared=c1.n AND s.shared=c2.n AND s.shared>=2) AS duplicate_pairs,
  (SELECT count(*) FROM pw) AS credits`).Scan(&s).Error
	return s, err
}

func latinName(names []string) string {
	for _, name := range names[1:] {
		latin := true
		for _, r := range name {
			if r > unicode.MaxASCII {
				latin = false
				break
			}
		}
		if latin && hasLatin([]string{name}) {
			return name
		}
	}
	return ""
}

// applyPlan records aliases and rebuilds legacy credits in one transaction.
// People rows for merged aliases are kept (no credits remain on them), so
// old profile links resolve through person_aliases.
// With rehearse, the alias migration is applied inside the same transaction and
// everything is rolled back after the results are measured.
func applyPlan(db *gorm.DB, r report, rehearse bool) (before, after snapshot, missing []string, err error) {
	if !rehearse {
		var count int64
		if err = db.Model(&database.SchemaMigration{}).Where("version = ?", database.CatalogSchemaVersion).Count(&count).Error; err != nil {
			return
		}
		if count != 1 {
			err = fmt.Errorf("migration %s is not applied; run go run ./cmd/catalog-migrate -apply first", database.CatalogSchemaVersion)
			return
		}
	}
	if before, err = takeSnapshot(db); err != nil {
		return
	}
	errRehearsal := errors.New("rehearsal rolled back")
	err = db.Transaction(func(tx *gorm.DB) error {
		if rehearse {
			migration, err := os.ReadFile("database/migrations/20261020_person_aliases.sql")
			if err != nil {
				return err
			}
			if err := tx.Exec(string(migration)).Error; err != nil {
				return err
			}
		}
		ids := map[string]int64{}
		for _, a := range r.Aliases {
			id, ok := ids[a.OwnerSlug]
			if !ok {
				if err := tx.Raw(`SELECT id FROM people WHERE slug=?`, a.OwnerSlug).Scan(&id).Error; err != nil {
					return err
				}
				ids[a.OwnerSlug] = id
			}
			if id == 0 {
				missing = append(missing, a.OwnerName)
				continue
			}
			if err := tx.Exec(`INSERT INTO person_aliases(alias_slug,person_id,alias_name,source) VALUES(?,?,?,'credit_list') ON CONFLICT DO NOTHING`, a.Slug, id, a.Name).Error; err != nil {
				return err
			}
		}
		for _, seg := range r.Segments {
			if english := latinName(seg.Names); english != "" {
				if err := tx.Exec(`UPDATE people SET english_name=?, updated_at=now() WHERE slug=? AND COALESCE(english_name,'') IN ('', canonical_public_name)`, english, seg.owner()).Error; err != nil {
					return err
				}
			}
		}
		// Re-run the credit trigger on every multi-name credit list.
		if err := tx.Exec(`UPDATE works SET featured_names=featured_names WHERE featured_names LIKE '%,%'`).Error; err != nil {
			return err
		}
		var measureErr error
		after, measureErr = takeSnapshot(tx)
		if measureErr != nil {
			return measureErr
		}
		if err := printTopModels(tx); err != nil {
			return err
		}
		if rehearse {
			return errRehearsal
		}
		return nil
	})
	if errors.Is(err, errRehearsal) {
		err = nil
	}
	return
}

func printTopModels(tx *gorm.DB) error {
	var rows []struct {
		Name    string
		English string
		Works   int64
	}
	err := tx.Raw(`SELECT p.canonical_public_name AS name, COALESCE(p.english_name,'') AS english, count(*) AS works FROM (` + publishedCredits + `) pw JOIN people p ON p.id=pw.person_id
 GROUP BY p.id ORDER BY works DESC, name LIMIT 15`).Scan(&rows).Error
	for _, row := range rows {
		fmt.Printf("  %4d  %s %s\n", row.Works, row.Name, row.English)
	}
	return err
}

func reportCurrent(db *gorm.DB) error {
	s, err := takeSnapshot(db)
	if err != nil {
		return err
	}
	var aliases, owners int64
	db.Raw(`SELECT count(*) FROM person_aliases`).Scan(&aliases)
	db.Raw(`SELECT count(DISTINCT person_id) FROM person_aliases`).Scan(&owners)
	var orphanWorks int64
	db.Raw(`SELECT count(*) FROM works w WHERE w.status='published' AND COALESCE(btrim(w.featured_names),'')<>'' AND NOT EXISTS (SELECT 1 FROM work_people wp WHERE wp.work_id=w.id)`).Scan(&orphanWorks)
	fmt.Printf("Now: %d credited people, %d duplicate pairs, %d credits\n", s.CreditedPeople, s.DuplicatePairs, s.Credits)
	fmt.Printf("person_aliases: %d aliases for %d models\n", aliases, owners)
	fmt.Printf("Published works with names but no credits: %d\n", orphanWorks)
	return printTopModels(db)
}
