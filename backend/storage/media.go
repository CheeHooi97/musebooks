package storage

import (
	"crypto/hmac"
	"crypto/sha256"
	"encoding/base64"
	"errors"
	"fmt"
	"net/url"
	"path"
	"strconv"
	"strings"
	"time"
)

const (
	defaultMediaURLWindow = 24 * time.Hour
	minMediaURLWindow     = time.Hour
	maxMediaURLWindow     = 7 * 24 * time.Hour
	minMediaSigningSecret = 32
)

// MediaConfig points R2 cover URLs at the media Worker (deploy/media-worker).
// Catalog rows store URLs on the old public R2 hostname, which no longer
// serves objects, so every R2 URL is re-signed for the Worker at response time.
type MediaConfig struct {
	// LegacyBaseURLs are R2 hostnames already written into the database,
	// such as https://img.musecards.my.
	LegacyBaseURLs []string
	MediaBaseURL   string
	SigningSecret  string
	Window         time.Duration
}

// MediaSigner turns R2 object URLs into media Worker URLs that stay identical
// for a whole window, so browsers, the app and Cloudflare's edge can cache them.
type MediaSigner struct {
	baseURL string
	hosts   map[string]bool
	secret  []byte
	window  time.Duration
}

// NewMediaSigner returns nil when the Worker is not configured, in which case
// URLs are served unchanged.
func NewMediaSigner(cfg MediaConfig) (*MediaSigner, error) {
	base := strings.TrimRight(strings.TrimSpace(cfg.MediaBaseURL), "/")
	secret := strings.TrimSpace(cfg.SigningSecret)
	if base == "" && secret == "" {
		return nil, nil
	}
	if base == "" || secret == "" {
		return nil, errors.New("CLOUDFLARE_R2_MEDIA_BASE_URL and CLOUDFLARE_R2_MEDIA_SIGNING_SECRET must be set together")
	}
	if parsed, err := url.Parse(base); err != nil || parsed.Scheme != "https" || parsed.Host == "" || parsed.Path != "" {
		return nil, errors.New("CLOUDFLARE_R2_MEDIA_BASE_URL must be an https origin such as https://media.example.com")
	}
	if len(secret) < minMediaSigningSecret {
		return nil, fmt.Errorf("CLOUDFLARE_R2_MEDIA_SIGNING_SECRET must be at least %d characters", minMediaSigningSecret)
	}
	window := cfg.Window
	if window <= 0 {
		window = defaultMediaURLWindow
	}
	if window < minMediaURLWindow || window > maxMediaURLWindow {
		return nil, fmt.Errorf("CLOUDFLARE_R2_MEDIA_URL_WINDOW_SECONDS must be between %d and %d seconds", int(minMediaURLWindow/time.Second), int(maxMediaURLWindow/time.Second))
	}
	hosts := map[string]bool{hostname(base): true}
	for _, legacy := range cfg.LegacyBaseURLs {
		if host := hostname(legacy); host != "" {
			hosts[host] = true
		}
	}
	return &MediaSigner{baseURL: base, hosts: hosts, secret: []byte(secret), window: window}, nil
}

// Window reports the shortest time a signed URL stays valid.
func (s *MediaSigner) Window() time.Duration {
	if s == nil {
		return 0
	}
	return s.window
}

// URL signs raw when it names an object on a known R2 or Worker hostname and
// returns any other value unchanged.
func (s *MediaSigner) URL(raw string) string {
	signed, ok := s.Sign(raw, time.Now())
	if !ok {
		return raw
	}
	return signed
}

// Sign reports whether raw is a media URL this signer owns, and if so returns
// the Worker URL for the window containing now.
func (s *MediaSigner) Sign(raw string, now time.Time) (string, bool) {
	if s == nil {
		return "", false
	}
	key, ok := s.objectKey(raw)
	if !ok {
		return "", false
	}
	// Aligning the expiry to a window boundary gives every request in one
	// window the same URL; landing a full window past the current one means a
	// URL is never handed out with less than a window of life left.
	exp := now.UTC().Truncate(s.window).Add(2 * s.window).Unix()
	segments := strings.Split(key, "/")
	for index, segment := range segments {
		segments[index] = url.PathEscape(segment)
	}
	query := url.Values{"exp": {strconv.FormatInt(exp, 10)}, "sig": {mediaSignature(s.secret, key, exp)}}
	return s.baseURL + "/" + strings.Join(segments, "/") + "?" + query.Encode(), true
}

func (s *MediaSigner) objectKey(raw string) (string, bool) {
	parsed, err := url.Parse(strings.TrimSpace(raw))
	if err != nil || parsed.Scheme != "https" || parsed.User != nil || !s.hosts[strings.ToLower(parsed.Hostname())] {
		return "", false
	}
	key := cleanObjectKey(parsed.Path)
	return key, key != ""
}

// mediaSignature must match verifySignature in deploy/media-worker/src/index.js.
func mediaSignature(secret []byte, key string, exp int64) string {
	mac := hmac.New(sha256.New, secret)
	mac.Write([]byte(key + "\n" + strconv.FormatInt(exp, 10)))
	return base64.RawURLEncoding.EncodeToString(mac.Sum(nil))
}

func hostname(rawURL string) string {
	parsed, err := url.Parse(strings.TrimSpace(rawURL))
	if err != nil {
		return ""
	}
	return strings.ToLower(parsed.Hostname())
}

func cleanObjectKey(value string) string {
	value = strings.Trim(strings.TrimSpace(value), "/")
	if value == "" || value == "." || value == ".." || strings.Contains(value, "\\") {
		return ""
	}
	cleaned := path.Clean("/" + value)
	if cleaned == "/" || strings.HasPrefix(cleaned, "/../") {
		return ""
	}
	return strings.TrimPrefix(cleaned, "/")
}
