package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"

	"musebooks/scraper/internal/worker"
)

func main() {
	request := worker.Request{}
	flag.StringVar(&request.URL, "url", "", "public listing/search URL")
	flag.StringVar(&request.WorkerID, "worker-id", "", "worker identifier when running a leased API job")
	flag.StringVar(&request.LeaseToken, "lease-token", "", "lease token when running a leased API job")
	flag.StringVar(&request.Format, "format", "", "listing format: physical or digital")
	flag.StringVar(&request.DigitalAccess, "digital-access", "", "digital authorization evidence, e.g. authorized_store")
	flag.StringVar(&request.SourceID, "source-id", "", "catalog source identifier")
	flag.StringVar(&request.Source, "source", "", "source name or identifier")
	flag.StringVar(&request.Query, "query", "", "search query for adapters that support it")
	flag.IntVar(&request.PageSize, "page-size", 30, "maximum accepted listings per page")
	flag.IntVar(&request.MaxPages, "max-pages", 1, "maximum pages to visit")
	flag.StringVar(&request.JobID, "job-id", "", "job identifier")
	flag.StringVar(&request.IngestURL, "ingest-url", "", "backend batch ingest endpoint")
	flag.Parse()

	if request.URL == "" {
		if err := json.NewDecoder(os.Stdin).Decode(&request); err != nil {
			fmt.Fprintln(os.Stderr, "provide -url or a JSON request on stdin:", err)
			os.Exit(2)
		}
	}
	request.IngestToken = os.Getenv("SCRAPER_INGEST_TOKEN")

	batch, err := worker.Run(request)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	if err := json.NewEncoder(os.Stdout).Encode(batch); err != nil {
		fmt.Fprintln(os.Stderr, "encode batch:", err)
		os.Exit(1)
	}
}
