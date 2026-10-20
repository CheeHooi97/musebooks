// Command people-merge reports, and with -apply repairs, people records that are
// one model credited under several names.
//
// The Japan model importer writes a model's canonical name followed by its other
// recorded names into works.featured_names ("岸明日香,Asuka Kishi"), and the
// credit trigger turned every name into its own person. The plan is derived only
// from MuseBooks catalog credit lists (see plan.go). Applying it records each
// alias against the canonical person in person_aliases; the updated trigger then
// resolves an alias only when its canonical name is credited on the same work.
package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"musebooks/config"
	"musebooks/database"
	"musebooks/model"
	"os"
	"sort"
	"strings"

	"gorm.io/gorm"
)

type alias struct {
	Slug      string `json:"slug"`
	Name      string `json:"name"`
	OwnerSlug string `json:"ownerSlug"`
	OwnerName string `json:"ownerName"`
}

type report struct {
	Segments      []segment           `json:"segments"`
	Aliases       []alias             `json:"aliases"`
	Conflicts     []string            `json:"conflicts"`
	SharedAliases map[string][]string `json:"sharedAliases"`
	LeftoverNames map[string]int      `json:"leftoverNames"`
	MultiWorks    int                 `json:"multiNameWorks"`
}

func splitNames(value string) []string {
	seen := map[string]bool{}
	names := []string{}
	for _, part := range strings.Split(value, ",") {
		name := strings.TrimSpace(part)
		key := strings.ToLower(name)
		if name == "" || seen[key] {
			continue
		}
		seen[key] = true
		names = append(names, name)
	}
	return names
}

func buildPlan(db *gorm.DB) (report, error) {
	var works []struct{ ID, FeaturedNames string }
	if err := db.Raw(`SELECT id, featured_names FROM works WHERE featured_names LIKE '%,%'`).Scan(&works).Error; err != nil {
		return report{}, err
	}
	lists := map[string][]string{}
	counts := map[string]int{}
	for _, work := range works {
		names := splitNames(work.FeaturedNames)
		key := strings.Join(names, ",")
		lists[key] = names
		counts[key]++
	}
	segs := segments(lists, counts)
	owners := map[string]string{} // owner slug -> owner name
	bySegmentKey := map[string]segment{}
	for _, seg := range segs {
		owners[seg.owner()] = seg.Names[0]
		bySegmentKey[normalizedKey(seg.Names)] = seg
	}
	r := report{Segments: segs, SharedAliases: map[string][]string{}, LeftoverNames: map[string]int{}, MultiWorks: len(works)}
	seen := map[string]bool{}
	for _, seg := range segs {
		for _, name := range seg.Names[1:] {
			slug := model.CatalogIdentity("model", name)
			if slug == seg.owner() {
				continue
			}
			if other, ok := owners[slug]; ok {
				// Never fold one model's canonical person into another.
				r.Conflicts = append(r.Conflicts, fmt.Sprintf("%s lists %s, which is itself a model's main name", seg.Names[0], other))
				continue
			}
			r.SharedAliases[name] = append(r.SharedAliases[name], seg.Names[0])
			if key := slug + "\x00" + seg.owner(); !seen[key] {
				seen[key] = true
				r.Aliases = append(r.Aliases, alias{Slug: slug, Name: name, OwnerSlug: seg.owner(), OwnerName: seg.Names[0]})
			}
		}
	}
	for name, ownersOf := range r.SharedAliases {
		if len(ownersOf) < 2 {
			delete(r.SharedAliases, name)
		}
	}
	for key, names := range lists {
		_, singles := decompose(names, bySegmentKey)
		for _, name := range singles {
			r.LeftoverNames[name] += counts[key]
		}
	}
	return r, nil
}

func main() {
	apply := flag.Bool("apply", false, "record the planned aliases and rebuild credits (writes to the database)")
	evidence := flag.String("evidence", "", "read-only: write review evidence for unconfirmed credits on bucket models to this path")
	audit := flag.String("audit", "", "read-only: audit credited titles against model names; write JSON to this path (- for none)")
	personName := flag.String("person", "", "read-only: list works credited to this display name")
	pairs := flag.Bool("pairs", false, "read-only: list people still credited on exactly the same works")
	check := flag.Bool("check", false, "read-only: report current credit counts, aliases and top models")
	rehearse := flag.Bool("rehearse", false, "run the migration and merge in a transaction, report, then roll back")
	out := flag.String("out", "", "write the plan as JSON to this path")
	flag.Parse()
	config.LoadConfig()
	db, err := database.Open(!*apply && !*rehearse, *apply || *rehearse)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	var applied []string
	db.Raw(`SELECT version FROM schema_migrations ORDER BY version`).Scan(&applied)
	fmt.Printf("Applied catalog migrations: %s\n\n", strings.Join(applied, ", "))
	if *evidence != "" {
		if err := reviewEvidence(db, *evidence); err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}
		return
	}
	if *audit != "" {
		path := *audit
		if path == "-" {
			path = ""
		}
		if err := runAudit(db, path); err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}
		return
	}
	if *personName != "" {
		if err := reportPerson(db, *personName); err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}
		return
	}
	if *pairs {
		if err := reportPairs(db); err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}
		return
	}
	if *check {
		if err := reportCurrent(db); err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}
		return
	}
	r, err := buildPlan(db)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	for _, seg := range r.Segments {
		fmt.Printf("%4d works  %s  <-  %s\n", seg.Works, seg.Names[0], strings.Join(seg.Names[1:], " · "))
	}
	shared := []string{}
	for name, ownersOf := range r.SharedAliases {
		shared = append(shared, fmt.Sprintf("%s (%s)", name, strings.Join(ownersOf, ", ")))
	}
	sort.Strings(shared)
	leftovers := []string{}
	for name, count := range r.LeftoverNames {
		leftovers = append(leftovers, fmt.Sprintf("%s ×%d", name, count))
	}
	sort.Strings(leftovers)
	fmt.Printf("\nShared aliases (resolved per work by the co-credited main name): %s\n", strings.Join(shared, "; "))
	fmt.Printf("\nConflicts skipped: %s\n", strings.Join(r.Conflicts, "; "))
	fmt.Printf("\nNames kept as separate people: %s\n", strings.Join(leftovers, ", "))
	fmt.Printf("\n%d models · %d aliases · %d multi-name works · %d conflicts · %d separate names\n", len(r.Segments), len(r.Aliases), r.MultiWorks, len(r.Conflicts), len(r.LeftoverNames))
	if *out != "" {
		data, _ := json.MarshalIndent(r, "", "  ")
		if err := os.WriteFile(*out, data, 0o644); err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}
	}
	if !*apply && !*rehearse {
		fmt.Println("\nDry run only. Re-run with -rehearse to test or -apply to merge.")
		return
	}
	before, after, missing, err := applyPlan(db, r, *rehearse)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	if len(missing) > 0 {
		fmt.Printf("Skipped aliases whose main person was not found: %s\n", strings.Join(missing, ", "))
	}
	fmt.Printf("Before: %d credited people, %d duplicate pairs, %d credits\n", before.CreditedPeople, before.DuplicatePairs, before.Credits)
	fmt.Printf("After:  %d credited people, %d duplicate pairs, %d credits\n", after.CreditedPeople, after.DuplicatePairs, after.Credits)
	if *rehearse {
		fmt.Println("Rehearsal only: every change was rolled back.")
	}
}
