package model

import (
	"regexp"
	"strings"
)

// Rakuten Kobo appends a product's label or series to its title, set apart
// by whitespace: "紫藤るい「Healing」　（漫画アクションデジタル写真集）".
// Parentheses joined to the title, such as "萌木七海（１）", are part of it.
var storeSeriesSuffix = regexp.MustCompile(`[\s\x{3000}]+（([^（）]+)）[\s\x{3000}]*$`)

// StoreSeriesName splits a store-appended series label from a product title.
// A label that only repeats the title names no series.
func StoreSeriesName(title string) (base string, series string) {
	match := storeSeriesSuffix.FindStringSubmatchIndex(title)
	if match == nil {
		return title, ""
	}
	base = strings.TrimSpace(title[:match[0]])
	series = strings.TrimSpace(title[match[2]:match[3]])
	if base == "" {
		return title, ""
	}
	if series == base {
		return base, ""
	}
	return base, series
}

// TitleWithoutSeries drops a store-appended label once it is recorded as the
// edition's series, or when it only repeats the title.
func TitleWithoutSeries(title string, series ...string) string {
	match := storeSeriesSuffix.FindStringSubmatchIndex(title)
	if match == nil {
		return title
	}
	base := strings.TrimSpace(title[:match[0]])
	label := strings.TrimSpace(title[match[2]:match[3]])
	if base == "" {
		return title
	}
	if label == base {
		return base
	}
	for _, name := range series {
		if name != "" && strings.TrimSpace(name) == label {
			return base
		}
	}
	return title
}
