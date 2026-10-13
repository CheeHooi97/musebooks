package main

import (
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"gorm.io/gorm"
	"musebooks/config"
	"musebooks/database"
	"musebooks/model"
	"os"
	"strings"
)

type member struct {
	WorkID    string `json:"workId"`
	EditionID string `json:"editionId"`
	Title     string `json:"title"`
	Publisher string `json:"publisher"`
	Format    string `json:"format"`
}
type group struct {
	WorkID     string   `json:"workId"`
	Title      string   `json:"title"`
	PersonSlug string   `json:"personSlug"`
	Members    []member `json:"members"`
}

type reviewedMember struct {
	member  member
	work    model.Work
	edition model.Edition
}

func mergeFeaturedNames(values ...string) string {
	seen := map[string]struct{}{}
	merged := make([]string, 0)
	for _, value := range values {
		for _, name := range strings.Split(value, ",") {
			name = strings.TrimSpace(name)
			if name == "" {
				continue
			}
			if _, exists := seen[name]; exists {
				continue
			}
			seen[name] = struct{}{}
			merged = append(merged, name)
		}
	}
	return strings.Join(merged, ",")
}

func moveWorkMediaToEdition(tx *gorm.DB, sourceWorkID, editionID string) (int, error) {
	var assets []model.CatalogMedia
	if err := tx.Where("entity_type = ? AND entity_id = ?", "work", sourceWorkID).Find(&assets).Error; err != nil {
		return 0, err
	}
	moved := 0
	for _, asset := range assets {
		mediaType := asset.MediaType
		var collision model.CatalogMedia
		err := tx.Where("entity_type = ? AND entity_id = ? AND media_type = ?", "edition", editionID, mediaType).First(&collision).Error
		if err != nil && !errors.Is(err, gorm.ErrRecordNotFound) {
			return moved, err
		}
		if err == nil {
			mediaType = fmt.Sprintf("work_%x", asset.ID)
			for suffix := 0; suffix < 12; suffix++ {
				var alternate model.CatalogMedia
				check := tx.Where("entity_type = ? AND entity_id = ? AND media_type = ?", "edition", editionID, mediaType).First(&alternate).Error
				if errors.Is(check, gorm.ErrRecordNotFound) {
					break
				}
				if check != nil {
					return moved, check
				}
				mediaType += "x"
			}
		}
		if err := tx.Model(&model.CatalogMedia{}).Where("id = ?", asset.ID).Updates(map[string]any{
			"entity_type": "edition",
			"entity_id":   editionID,
			"media_type":  mediaType,
		}).Error; err != nil {
			return moved, err
		}
		moved++
	}
	return moved, nil
}

func main() {
	apply := flag.Bool("apply", false, "Apply reviewed work grouping atomically; retain all editions and offers")
	manifest := flag.String("manifest", "../scraper/japan-work-identities.json", "Reviewed work identity map")
	bindingsOutput := flag.String("bindings-output", "", "Export current work/edition bindings for the reviewed scope without changing the database")
	flag.Parse()
	data, err := os.ReadFile(*manifest)
	if err != nil {
		panic(err)
	}
	var plan struct {
		Model  string  `json:"model"`
		Groups []group `json:"groups"`
	}
	if err = json.Unmarshal(data, &plan); err != nil {
		panic(err)
	}
	if plan.Model != "Japan models" || len(plan.Groups) == 0 {
		panic("unexpected repair scope")
	}
	config.LoadConfig()
	db, err := database.Open(!*apply, false)
	if err != nil {
		panic(err)
	}
	if *bindingsOutput != "" {
		if *apply {
			panic("bindings export must be read-only")
		}
		ids, editionIDs := []string{}, []string{}
		for _, g := range plan.Groups {
			ids = append(ids, g.WorkID)
			for _, m := range g.Members {
				ids = append(ids, m.WorkID)
				editionIDs = append(editionIDs, m.EditionID)
			}
		}
		var editions []model.Edition
		if err := db.Where("id IN ?", editionIDs).Find(&editions).Error; err != nil {
			panic(err)
		}
		editionBindings := map[string]string{}
		for _, e := range editions {
			editionBindings[e.ID] = e.WorkID
			ids = append(ids, e.WorkID)
		}
		var works []model.Work
		if err := db.Where("id IN ?", ids).Find(&works).Error; err != nil {
			panic(err)
		}
		workBindings := map[string]map[string]string{}
		for _, w := range works {
			workBindings[w.ID] = map[string]string{"title": w.OriginalTitle, "status": w.Status}
		}
		data, err := json.MarshalIndent(map[string]any{"works": workBindings, "editions": editionBindings}, "", "  ")
		if err != nil {
			panic(err)
		}
		if err := os.WriteFile(*bindingsOutput, data, 0644); err != nil {
			panic(err)
		}
		fmt.Printf("Exported %d current work bindings and %d edition bindings\n", len(works), len(editions))
		return
	}
	deferred := 0
	validated := 0
	movedMedia := 0
	err = db.Transaction(func(tx *gorm.DB) error {
		if err := tx.Exec("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ").Error; err != nil {
			return err
		}
		// Validate the reviewed scope from a few snapshot reads rather than
		// thousands of round trips to the remote database on each resume.
		workIDs, editionIDs, personSlugs := []string{}, []string{}, []string{}
		for _, g := range plan.Groups {
			workIDs = append(workIDs, g.WorkID)
			personSlugs = append(personSlugs, g.PersonSlug)
			for _, m := range g.Members {
				workIDs = append(workIDs, m.WorkID)
				editionIDs = append(editionIDs, m.EditionID)
			}
		}
		var works []model.Work
		var editions []model.Edition
		var people []model.Person
		var credits []model.WorkPerson
		if err := tx.Where("id IN ?", workIDs).Find(&works).Error; err != nil {
			return err
		}
		if err := tx.Where("id IN ? OR work_id IN ?", editionIDs, workIDs).Find(&editions).Error; err != nil {
			return err
		}
		if err := tx.Where("slug IN ?", personSlugs).Find(&people).Error; err != nil {
			return err
		}
		if err := tx.Where("work_id IN ? AND role = ?", workIDs, "featured").Find(&credits).Error; err != nil {
			return err
		}
		workByID, editionByID := map[string]model.Work{}, map[string]model.Edition{}
		personBySlug := map[string]model.Person{}
		editionsByWork := map[string][]string{}
		credited := map[string]bool{}
		for _, w := range works {
			workByID[w.ID] = w
		}
		for _, e := range editions {
			editionByID[e.ID] = e
			editionsByWork[e.WorkID] = append(editionsByWork[e.WorkID], e.ID)
		}
		for _, p := range people {
			personBySlug[p.Slug] = p
		}
		for _, c := range credits {
			credited[fmt.Sprint(c.WorkID, ":", c.PersonID)] = true
		}
		for _, g := range plan.Groups {
			deferGroup := func(reason string) {
				deferred++
				fmt.Printf("Deferred %s: %s\n", g.Title, reason)
			}
			canonical, exists := workByID[g.WorkID]
			if !exists {
				deferGroup("canonical work has not been imported yet")
				continue
			}
			if canonical.OriginalTitle != g.Title || canonical.OriginCode != "JP" {
				return fmt.Errorf("canonical work changed: %s", g.WorkID)
			}
			if g.PersonSlug == "" {
				return fmt.Errorf("reviewed work group is missing its model identity: %s", g.Title)
			}
			person, exists := personBySlug[g.PersonSlug]
			if !exists {
				deferGroup("model identity has not been imported yet")
				continue
			}

			members := make([]reviewedMember, 0, len(g.Members))
			missing := ""
			for _, m := range g.Members {
				w, exists := workByID[m.WorkID]
				if !exists {
					bound, present := editionByID[m.EditionID]
					if present && bound.WorkID == g.WorkID {
						w = canonical
					} else if !present {
						missing = "source work has not been imported yet"
						continue
					} else {
						return fmt.Errorf("existing edition has unreviewed ownership: %s", m.EditionID)
					}
				}
				e, exists := editionByID[m.EditionID]
				if !exists {
					missing = "source edition has not been imported yet"
					continue
				}
				if (w.OriginalTitle != m.Title && !(w.ID == g.WorkID && e.EditionLabel == m.Title)) || w.OriginCode != "JP" || e.Publisher != m.Publisher || e.Format != m.Format || (e.WorkID != m.WorkID && e.WorkID != g.WorkID) {
					return fmt.Errorf("reviewed identity changed: %s", m.EditionID)
				}
				if !credited[fmt.Sprint(w.ID, ":", person.ID)] {
					return fmt.Errorf("model attribution changed for %s: %s", g.PersonSlug, m.WorkID)
				}
				if m.WorkID != g.WorkID {
					for _, id := range editionsByWork[m.WorkID] {
						if id != m.EditionID {
							return fmt.Errorf("work gained unreviewed editions: %s", m.WorkID)
						}
					}
				}
				members = append(members, reviewedMember{member: m, work: w, edition: e})
			}
			if missing != "" {
				deferGroup(missing)
			}

			for _, entry := range members {
				if entry.member.WorkID == g.WorkID || entry.work.ID == g.WorkID || (entry.edition.WorkID == g.WorkID && entry.work.Status == "superseded") {
					continue
				}
				if *apply {
					mediaCount, err := moveWorkMediaToEdition(tx, entry.member.WorkID, entry.edition.ID)
					if err != nil {
						return err
					}
					movedMedia += mediaCount
					mergedNames := mergeFeaturedNames(canonical.FeaturedNames, entry.work.FeaturedNames)
					if mergedNames != canonical.FeaturedNames {
						if err := tx.Model(&model.Work{}).Where("id = ?", canonical.ID).Update("featured_names", mergedNames).Error; err != nil {
							return err
						}
						canonical.FeaturedNames = mergedNames
					}
					if err := tx.Model(&model.Edition{}).Where("id = ?", entry.edition.ID).Update("work_id", g.WorkID).Error; err != nil {
						return err
					}
					if err := tx.Exec(`INSERT INTO work_people (work_id,person_id,role,credited_name,credit_source,created_at,updated_at) SELECT ?,person_id,role,credited_name,credit_source,created_at,updated_at FROM work_people WHERE work_id=? ON CONFLICT DO NOTHING`, g.WorkID, entry.member.WorkID).Error; err != nil {
						return err
					}
					if err := tx.Model(&model.Work{}).Where("id = ?", entry.member.WorkID).Update("status", "superseded").Error; err != nil {
						return err
					}
					entry.edition.WorkID = g.WorkID
					entry.work.Status = "superseded"
					editionByID[entry.edition.ID] = entry.edition
					workByID[entry.work.ID] = entry.work
				}
			}
			workByID[canonical.ID] = canonical
			validated++
			fmt.Printf("Reviewed %s (%d source records)\n", g.Title, len(g.Members))
		}
		return nil
	})
	if err != nil {
		panic(err)
	}
	fmt.Printf("Validated %d photobook groups; deferred %d not-yet-imported groups; applied=%v; editions, listings, observations and model credits retained; work images moved to edition galleries=%d\n", validated, deferred, *apply, movedMedia)
}
