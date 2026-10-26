package main

import (
	"database/sql"
	"encoding/json"
	"flag"
	"fmt"
	"github.com/joho/godotenv"
	"gorm.io/gorm"
	"musebooks/config"
	"musebooks/database"
	"musebooks/model"
	"os"
	"sort"
	"strings"
	"time"
)

func must(e error) {
	if e != nil {
		panic(e)
	}
}

type Media struct {
	ExternalID  string `json:"externalId"`
	MediaType   string `json:"mediaType"`
	OriginalURL string `json:"originalUrl"`
	StorageURL  string `json:"storageUrl"`
	SourceURL   string `json:"sourceUrl"`
}
type Record struct {
	Work           model.Work             `json:"work"`
	Edition        model.Edition          `json:"edition"`
	Source         model.Source           `json:"source"`
	Batch          model.ObservationBatch `json:"batch"`
	Media          []Media                `json:"media"`
	PublisherMedia []Media                `json:"publisherMedia"`
}

func main() {
	manifestPath := flag.String("manifest", "../docs/korean-maxim-issue-review.json", "Reviewed Korean source ledger")
	outputPath := flag.String("output", "../docs/korean-catalog-coverage-audit-"+time.Now().Format("2006-01-02")+".json", "JSON audit output path")
	flag.Parse()
	_ = godotenv.Load()
	config.LoadConfig()
	if config.DBName != "musebooks" {
		panic("database")
	}
	b, e := os.ReadFile(*manifestPath)
	must(e)
	var records []Record
	must(json.Unmarshal(b, &records))
	worksExpected := map[string]model.Work{}
	edExpected := map[string]model.Edition{}
	obsKeys := []string{}
	for _, r := range records {
		worksExpected[r.Work.ID] = r.Work
		edExpected[r.Edition.ID] = r.Edition
		for _, i := range r.Batch.Items {
			obsKeys = append(obsKeys, model.ScrapeObservationID(r.Batch.SourceID, i.ExternalID, r.Batch.JobID, i.ObservationID))
		}
	}
	wids, eids := []string{}, []string{}
	for id := range worksExpected {
		wids = append(wids, id)
	}
	for id := range edExpected {
		eids = append(eids, id)
	}
	sort.Strings(wids)
	sort.Strings(eids)
	var works []model.Work
	var editions []model.Edition
	var listings []model.Listing
	var observations []model.ListingObservation
	var assets []model.CatalogMedia
	var credits []model.WorkPerson
	db, e := database.Open(true, false)
	must(e)
	pool, e := db.DB()
	must(e)
	defer pool.Close()
	must(db.Transaction(func(tx *gorm.DB) error {
		must(tx.Where("id IN ?", wids).Order("id").Find(&works).Error)
		must(tx.Where("id IN ?", eids).Order("id").Find(&editions).Error)
		must(tx.Preload("Source").Where("edition_id IN ?", eids).Order("id").Find(&listings).Error)
		must(tx.Where("observation_key IN ?", obsKeys).Find(&observations).Error)
		must(tx.Preload("Person").Where("work_id IN ?", wids).Order("work_id,person_id,role").Find(&credits).Error)
		lids := []string{}
		for _, l := range listings {
			lids = append(lids, l.ID)
		}
		must(tx.Where("(entity_type='edition' AND entity_id IN ?) OR (entity_type='listing' AND entity_id IN ?)", eids, lids).Find(&assets).Error)
		return nil
	}, &sql.TxOptions{ReadOnly: true, Isolation: sql.LevelRepeatableRead}))
	wm := map[string]model.Work{}
	em := map[string]model.Edition{}
	lm := map[string]model.Listing{}
	om := map[string]model.ListingObservation{}
	am := map[string]model.CatalogMedia{}
	for _, w := range works {
		wm[w.ID] = w
	}
	for _, ed := range editions {
		em[ed.ID] = ed
	}
	for _, l := range listings {
		lm[l.SourceID+"\x00"+l.ExternalID] = l
	}
	for _, o := range observations {
		om[o.ObservationKey] = o
	}
	for _, a := range assets {
		am[a.EntityType+"\x00"+a.EntityID+"\x00"+a.MediaType] = a
	}
	failures := []map[string]any{}
	fail := func(kind string, data map[string]any) { data["kind"] = kind; failures = append(failures, data) }
	for id, expected := range worksExpected {
		w, ok := wm[id]
		if !ok || w.Status != "published" || w.OriginCode != "KR" || w.PublicationType != expected.PublicationType || (w.PublicationType == "photobook" && w.IssueMonth != "") || (w.PublicationType == "magazine_issue" && w.IssueMonth == "") {
			fail("work_identity", map[string]any{"workId": id})
		}
	}
	for id, expected := range edExpected {
		ed, ok := em[id]
		if !ok || ed.Status == "superseded" || ed.WorkID != expected.WorkID || ed.Format != expected.Format {
			fail("edition_identity", map[string]any{"editionId": id})
		}
	}
	seenObs := map[string]string{}
	itemRefs, mediaRefs := 0, 0
	for _, r := range records {
		for _, i := range r.Batch.Items {
			itemRefs++
			key := r.Batch.SourceID + "\x00" + i.ExternalID
			l, ok := lm[key]
			if !ok || l.EditionID != i.EditionID {
				fail("listing_link", map[string]any{"sourceId": r.Batch.SourceID, "externalId": i.ExternalID, "editionId": i.EditionID})
				continue
			}
			obsKey := model.ScrapeObservationID(r.Batch.SourceID, i.ExternalID, r.Batch.JobID, i.ObservationID)
			if prev, ok := seenObs[obsKey]; ok && prev != key {
				fail("observation_key_collision", map[string]any{"sourceId": r.Batch.SourceID, "externalId": i.ExternalID, "observationKey": obsKey, "previousListingKey": strings.ReplaceAll(prev, "\x00", "/")})
			}
			seenObs[obsKey] = key
			o, ok := om[obsKey]
			if !ok || o.ListingID != l.ID || o.PriceMinor != i.PriceMinor || o.Currency != i.Currency || o.Status != i.Status || o.StatusEvidence != i.StatusEvidence {
				fail("observation_evidence", map[string]any{"sourceId": r.Batch.SourceID, "externalId": i.ExternalID, "editionId": i.EditionID, "observationKey": obsKey, "exists": ok, "expectedListingId": l.ID, "actualListingId": o.ListingID, "expectedPriceMinor": i.PriceMinor, "actualPriceMinor": o.PriceMinor, "expectedStatus": i.Status, "actualStatus": o.Status})
			}
		}
		checkMedia := func(m Media, entity, id string) {
			mediaRefs++
			a, ok := am[entity+"\x00"+id+"\x00"+m.MediaType]
			if !ok || a.StorageURL != m.StorageURL || a.OriginalURL != m.OriginalURL || a.SourceURL != m.SourceURL {
				fail("media_provenance", map[string]any{"entityType": entity, "entityId": id, "mediaType": m.MediaType, "expectedUrl": m.StorageURL, "actualUrl": a.StorageURL})
			}
		}
		for _, m := range r.PublisherMedia {
			checkMedia(m, "edition", r.Edition.ID)
		}
		for _, m := range r.Media {
			l := lm[r.Source.ID+"\x00"+m.ExternalID]
			checkMedia(m, "listing", l.ID)
		}
	}
	coverage := []map[string]any{}
	totals := map[string]int{}
	sources := map[string]bool{}
	people := map[int64]model.Person{}
	missingPersonSource := []model.Person{}
	for _, c := range credits {
		people[c.PersonID] = c.Person
	}
	for _, p := range people {
		if p.VerificationSourceURL == "" {
			missingPersonSource = append(missingPersonSource, p)
		}
	}
	sort.Slice(missingPersonSource, func(i, j int) bool { return missingPersonSource[i].ID < missingPersonSource[j].ID })
	for _, ed := range editions {
		w := wm[ed.WorkID]
		gaps := []string{}
		if ed.ReleaseDate == nil {
			gaps = append(gaps, "release_date_unknown")
			totals["missingReleaseDate"]++
		} else if ed.ReleasePrecision != "day" {
			totals["releaseDateNotDayPrecision"]++
		}
		if ed.PageCount == 0 {
			gaps = append(gaps, "page_count_unknown")
			totals["missingPageCount"]++
		}
		if ed.CoverURL == "" {
			gaps = append(gaps, "cover_unknown")
			totals["missingCover"]++
		}
		lc, active, used, retail := 0, 0, 0, 0
		for _, l := range listings {
			if l.EditionID != ed.ID {
				continue
			}
			lc++
			sources[l.SourceID] = true
			if l.Status == "active" {
				active++
			}
			isUsed := l.Source.Kind != "bookstore" && ed.Format == "physical" || strings.HasPrefix(strings.TrimSpace(l.Title), "[중고]")
			if isUsed {
				used++
			} else {
				retail++
			}
		}
		if lc == 0 {
			gaps = append(gaps, "no_listing")
			totals["editionsWithoutListing"]++
		}
		if active == 0 {
			totals["editionsWithoutActiveListing"]++
		}
		totals[w.PublicationType+"_"+ed.Format]++
		coverage = append(coverage, map[string]any{"workId": w.ID, "title": w.OriginalTitle, "publicationType": w.PublicationType, "issueMonth": w.IssueMonth, "editionId": ed.ID, "format": ed.Format, "variant": ed.EditionVariant, "metadataSourceUrl": ed.MetadataSourceURL, "releaseDate": ed.ReleaseDate, "releasePrecision": ed.ReleasePrecision, "pageCount": ed.PageCount, "coverUrl": ed.CoverURL, "listingCount": lc, "activeListingCount": active, "usedListingCount": used, "retailListingCount": retail, "gaps": gaps})
	}
	report := map[string]any{"auditedAt": time.Now().UTC(), "method": "Repeatable-read PostgreSQL transaction with READ ONLY; exact ledger work/edition identities, listing links, observation payloads and explicit image provenance", "goalComplete": false, "ledgerIntegrityPassed": len(failures) == 0, "scope": map[string]int{"records": len(records), "works": len(works), "editions": len(editions), "linkedListings": len(listings), "listingItemReferences": itemRefs, "distinctObservationKeys": len(seenObs), "explicitMediaReferences": mediaRefs, "people": len(people), "sources": len(sources)}, "integrityFailures": failures, "coverageTotals": totals, "editionCoverage": coverage, "peopleWithoutVerificationSource": missingPersonSource, "rights": "No captured exact image has confirmed reuse permission in the source guide; URL provenance is not a license. This audit does not approve any asset or automation route.", "limits": "No source availability refreshed; active status is historical at its stored observation timestamp. Unknown dates/pages/prices can be legitimate source limitations. Used classification is a coverage heuristic, not a public response assertion. Scope is the ledger cohort, not every Korean publication or all database records."}
	out, e := json.MarshalIndent(report, "", "  ")
	must(e)
	must(os.WriteFile(*outputPath, append(out, '\n'), 0644))
	fmt.Printf("Audited %d works/%d editions/%d item references/%d media references: %d integrity findings\n", len(works), len(editions), itemRefs, mediaRefs, len(failures))
	fmt.Printf("Coverage gaps: %+v; %d people missing provenance source\n", totals, len(missingPersonSource))
}
