package main

import (
	"flag"
	"fmt"
	"musebooks/config"
	"musebooks/database"
	"musebooks/model"
	"sort"

	"gorm.io/gorm"
)

// Rakuten Kobo stores a product's label in its title. Record that label as the
// edition series so pages show it apart from the title; titles stay as captured.
func main() {
	apply := flag.Bool("apply", false, "Record store series labels on editions in one transaction")
	flag.Parse()
	config.LoadConfig()
	db, err := database.Open(!*apply, false)
	if err != nil {
		panic(err)
	}
	updated := 0
	series := map[string]int{}
	err = db.Transaction(func(tx *gorm.DB) error {
		var editions []model.Edition
		if err := tx.Select("id", "edition_label", "series_name").
			Where("COALESCE(series_name,'') = '' AND metadata_source_url LIKE ?", "https://books.rakuten.co.jp/%").
			Find(&editions).Error; err != nil {
			return err
		}
		for _, edition := range editions {
			_, name := model.StoreSeriesName(edition.EditionLabel)
			if name == "" {
				continue
			}
			series[name]++
			updated++
			if *apply {
				if err := tx.Model(&model.Edition{}).Where("id = ? AND COALESCE(series_name,'') = ''", edition.ID).
					Update("series_name", name).Error; err != nil {
					return err
				}
			}
		}
		fmt.Printf("Checked %d Rakuten Kobo editions without a series\n", len(editions))
		return nil
	})
	if err != nil {
		panic(err)
	}
	names := make([]string, 0, len(series))
	for name := range series {
		names = append(names, name)
	}
	sort.Slice(names, func(i, j int) bool { return series[names[i]] > series[names[j]] })
	for i, name := range names {
		if i == 15 {
			fmt.Printf("  … %d more series\n", len(names)-i)
			break
		}
		fmt.Printf("  %4d %s\n", series[name], name)
	}
	fmt.Printf("Series labels for %d editions across %d series; applied=%v; titles and edition labels unchanged\n", updated, len(names), *apply)
}
