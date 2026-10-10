package model

import (
	"net/url"
	"path"
	"strings"
)

const KingstoneWarningHash = "3c1ce976516c44566b414484ce00a85bd0da127555d7d9ff3e115c34816583c5"

// IsWarningCover identifies known store warning assets, including our old
// content-addressed mirror. It does not reject genuine covers with age labels.
func IsWarningCover(raw string) bool {
	parsed, err := url.Parse(raw)
	if err != nil {
		return false
	}
	name := strings.ToLower(path.Base(parsed.Path))
	if strings.TrimSuffix(name, path.Ext(name)) == KingstoneWarningHash {
		return true
	}
	if strings.EqualFold(parsed.Hostname(), "cdn.kingstone.com.tw") && strings.EqualFold(parsed.Path, "/images/restricted.jpg") {
		return true
	}
	return strings.EqualFold(parsed.Hostname(), "taiwan-image.bookwalker.com.tw") && strings.HasSuffix(strings.TrimSuffix(name, path.Ext(name)), "_mask")
}

func PublicCoverURL(raw string) string {
	if IsWarningCover(raw) {
		return ""
	}
	return raw
}
