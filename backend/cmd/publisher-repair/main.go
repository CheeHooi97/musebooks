package main

import (
	"flag"
	"fmt"
	"musebooks/config"
	"musebooks/database"
	"os"
)

func main() {
	apply := flag.Bool("apply", false, "normalize verified publisher aliases")
	flag.Parse()
	config.LoadConfig()
	db, err := database.Open(!*apply, *apply)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	if *apply {
		if err = database.RepairPublisherAliases(db); err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}
	}
	var rows []struct {
		Publisher string
		Editions  int64
		Works     int64
	}
	err = db.Raw("SELECT publisher, count(*) AS editions, count(DISTINCT work_id) AS works FROM editions WHERE publisher LIKE '尖端%' AND status <> 'superseded' GROUP BY publisher ORDER BY publisher").Scan(&rows).Error
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	for _, row := range rows {
		fmt.Printf("%s: %d editions, %d works\n", row.Publisher, row.Editions, row.Works)
	}
}
