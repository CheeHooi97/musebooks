package worker

import (
	"crypto/sha256"
	"encoding/hex"
	"net/url"
	"regexp"
	"strconv"
	"strings"
	"time"
)

var pricePattern = regexp.MustCompile("(?i)(JPY|TWD|CNY|MYR|USD|RM)\\s*([0-9][0-9,]*[.][0-9]+|[0-9][0-9,]*)")

func normalizeAnchor(rawURL, baseURL, text string, observedAt time.Time) (Observation, bool) {
	parsed, err := url.Parse(strings.TrimSpace(rawURL))
	if err != nil || (parsed.IsAbs() && parsed.Scheme != "http" && parsed.Scheme != "https") {
		return Observation{}, false
	}
	base, err := url.Parse(baseURL)
	if err != nil {
		return Observation{}, false
	}
	resolved := base.ResolveReference(parsed)
	if resolved.Scheme != "http" && resolved.Scheme != "https" {
		return Observation{}, false
	}

	title := strings.Join(strings.Fields(text), " ")
	if len([]rune(title)) < 8 || !looksLikePhotobook(title) || !looksLikeHumanModelPhotobook(title) {
		return Observation{}, false
	}

	item := Observation{
		ExternalID: externalID(resolved.String()),
		URL:        resolved.String(),
		Title:      title,
		ObservedAt: observedAt,
		Status:     "active",
		Format:     inferFormat(title),
	}
	priceText := title
	currencyHint := ""
	switch {
	case strings.Contains(title, "\u00a5"):
		priceText = strings.ReplaceAll(title, "\u00a5", "JPY")
		currencyHint = "JPY"
	case strings.Contains(strings.ToUpper(title), "NT$"):
		priceText = strings.ReplaceAll(strings.ToUpper(title), "NT$", "TWD")
		currencyHint = "TWD"
	}
	if match := pricePattern.FindStringSubmatch(priceText); len(match) == 3 {
		item.Currency = normalizeCurrency(match[1])
		if currencyHint != "" {
			item.Currency = currencyHint
		}
		item.PriceMinor = parseMinor(match[2], item.Currency)
		item.PriceType = "asking"
	}
	return item, true
}

func looksLikePhotobook(value string) bool {
	lower := strings.ToLower(value)
	for _, marker := range []string{
		"trading card", "photo card", "photocard", "calendar", "poster",
		"custom album", "empty album", "空白相簿", "空白相冊", "收藏卡", "交易卡",
	} {
		if strings.Contains(lower, marker) {
			return false
		}
	}
	for _, marker := range []string{
		"photobook", "photo book", "photo-book",
		"\u5199\u771f\u96c6", "\u5beb\u771f\u96c6", "\u6444\u5f71\u96c6", "\u6444\u5f71\u4e66", "\u5beb\u771f\u66f8",
	} {
		if strings.Contains(lower, marker) {
			return true
		}
	}
	return false
}

func looksLikeHumanModelPhotobook(value string) bool {
	lower := strings.ToLower(value)
	for _, marker := range []string{
		"car model", "aircraft model", "vehicle model", "scale model", "model kit",
		"model train", "plastic model", "model number", "モデルカー", "模型玩具",
		"模型套件", "模型車", "模型车",
	} {
		if strings.Contains(lower, marker) {
			return false
		}
	}
	for _, marker := range []string{
		"model", "fashion model", "cover model", "supermodel", "idol", "celebrity",
		"actor", "actress", "singer", "talent", "gravure", "glamour",
		"influencer", "performer", "beauty queen", "swimsuit",
		"アイドル", "モデル", "女優", "俳優", "歌手", "タレント", "グラビア",
		"女子アナ", "芸能人", "水着", "模特", "女模", "男模", "偶像", "明星",
		"演員", "演员", "藝人", "艺人", "網紅", "网红",
	} {
		if strings.Contains(lower, marker) {
			return true
		}
	}
	return false
}

func inferFormat(value string) string {
	lower := strings.ToLower(value)
	for _, marker := range []string{
		"digital", "e-book", "ebook", "pdf", "epub", "電子書", "電子版", "電子写真集", "电子书", "电子版", "数码版",
	} {
		if strings.Contains(lower, marker) {
			return "digital"
		}
	}
	return "physical"
}

func externalID(value string) string {
	hash := sha256.Sum256([]byte(value))
	return hex.EncodeToString(hash[:])[:24]
}

func normalizeCurrency(value string) string {
	switch strings.ToUpper(strings.TrimSpace(value)) {
	case "\u00a5", "JPY":
		return "JPY"
	case "NT$", "TWD":
		return "TWD"
	case "CNY":
		return "CNY"
	case "RM", "MYR":
		return "MYR"
	default:
		return "USD"
	}
}

func parseMinor(raw, currency string) int64 {
	clean := strings.ReplaceAll(raw, ",", "")
	value, err := strconv.ParseFloat(clean, 64)
	if err != nil || value <= 0 {
		return 0
	}
	if currency == "JPY" || currency == "TWD" || currency == "CNY" || currency == "MYR" {
		return int64(value)
	}
	return int64(value * 100)
}
