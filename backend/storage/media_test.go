package storage

import (
	"encoding/base64"
	"net/url"
	"strconv"
	"strings"
	"testing"
	"time"
)

func newTestSigner(t *testing.T) *MediaSigner {
	t.Helper()
	signer, err := NewMediaSigner(MediaConfig{
		LegacyBaseURLs: []string{"https://img.example.test"},
		MediaBaseURL:   "https://media.example.test",
		SigningSecret:  "test-media-signing-secret-0123456789abcdef",
	})
	if err != nil {
		t.Fatalf("NewMediaSigner() error = %v", err)
	}
	return signer
}

// The vector is shared with deploy/media-worker/src/index.test.js.
func TestMediaSignatureMatchesWorkerVector(t *testing.T) {
	got := mediaSignature([]byte("test-media-signing-secret-0123456789abcdef"), "musebooks/sample cover.jpg", 1800000000)
	if got != "z87t2-ZSbCgeeJ2JsNFsygvc_9PEXBineRN6ZkjD3jA" {
		t.Fatalf("mediaSignature() = %q", got)
	}
}

func TestSignIsStableWithinWindow(t *testing.T) {
	signer := newTestSigner(t)
	windowStart := time.Date(2026, 10, 20, 0, 0, 0, 0, time.UTC)
	first, ok := signer.Sign("https://img.example.test/musebooks/sample%20cover.jpg", windowStart.Add(time.Minute))
	if !ok {
		t.Fatal("legacy URL was not signed")
	}
	second, _ := signer.Sign("https://img.example.test/musebooks/sample%20cover.jpg", windowStart.Add(23*time.Hour))
	if first != second {
		t.Fatalf("URLs differ within one window:\n%s\n%s", first, second)
	}
	want := "https://media.example.test/musebooks/sample%20cover.jpg?exp=" + "1792627200"
	if !strings.HasPrefix(first, want) {
		t.Fatalf("URL = %q, want prefix %q", first, want)
	}
	next, _ := signer.Sign("https://img.example.test/musebooks/sample%20cover.jpg", windowStart.Add(24*time.Hour))
	if next == first {
		t.Fatal("URL did not rotate in the next window")
	}
}

func TestSignResignsWorkerURLs(t *testing.T) {
	signer := newTestSigner(t)
	now := time.Date(2026, 10, 20, 1, 0, 0, 0, time.UTC)
	fromLegacy, _ := signer.Sign("https://img.example.test/musebooks/a.jpg", now)
	fromWorker, ok := signer.Sign("https://media.example.test/musebooks/a.jpg?exp=1&sig=old", now)
	if !ok || fromWorker != fromLegacy {
		t.Fatalf("worker URL re-sign = %q, %v; want %q", fromWorker, ok, fromLegacy)
	}
}

func TestSignListingImageCreatesWorkerThumbnailURL(t *testing.T) {
	signer := newTestSigner(t)
	now := time.Date(2026, 10, 20, 1, 0, 0, 0, time.UTC)
	source := "https://auctions.c.yimg.jp/images/sample.jpg?width=1200"
	got, ok := signer.SignListingImage(source, now)
	if !ok {
		t.Fatal("supported marketplace image was not signed")
	}
	parsed, err := url.Parse(got)
	if err != nil {
		t.Fatal(err)
	}
	key := listingImageKeyPrefix + base64.RawURLEncoding.EncodeToString([]byte(source))
	wantPrefix := "https://media.example.test/" + key + "?"
	if !strings.HasPrefix(got, wantPrefix) {
		t.Fatalf("URL = %q, want prefix %q", got, wantPrefix)
	}
	exp, err := strconv.ParseInt(parsed.Query().Get("exp"), 10, 64)
	if err != nil || parsed.Query().Get("sig") != mediaSignature(signer.secret, key, exp) {
		t.Fatalf("URL signature was not valid: %q", got)
	}
}

func TestListingImageURLOnlyWrapsSupportedHosts(t *testing.T) {
	signer := newTestSigner(t)
	for _, source := range []string{
		"https://auctions.c.yimg.jp/images/sample.jpg",
		"https://shop.r10s.jp/store/image.png",
		"https://img.fril.jp/item/image.webp",
	} {
		got := signer.ListingImageURL(source)
		if got == source || !strings.HasPrefix(got, "https://media.example.test/"+listingImageKeyPrefix) {
			t.Errorf("ListingImageURL(%q) = %q, want signed Worker URL", source, got)
		}
	}
	for _, source := range []string{
		"https://evil.example/image.jpg",
		"http://auctions.c.yimg.jp/images/sample.jpg",
		"https://auctions.c.yimg.jp:8443/images/sample.jpg",
		"https://auctions.c.yimg.jp/images/sample.svg",
	} {
		if got := signer.ListingImageURL(source); got != source {
			t.Errorf("ListingImageURL(%q) = %q, want unchanged", source, got)
		}
	}
}

func TestURLLeavesOtherSourcesUnchanged(t *testing.T) {
	signer := newTestSigner(t)
	for _, source := range []string{
		"",
		"https://cdn.publisher.example/cover.jpg",
		"http://img.example.test/musebooks/a.jpg",
		"https://img.example.test/",
		"https://user@img.example.test/musebooks/a.jpg",
	} {
		if got := signer.URL(source); got != source {
			t.Errorf("URL(%q) = %q, want unchanged", source, got)
		}
	}
	var disabled *MediaSigner
	if got := disabled.URL("https://img.example.test/musebooks/a.jpg"); got != "https://img.example.test/musebooks/a.jpg" {
		t.Errorf("nil signer changed URL: %q", got)
	}
}

func TestNewMediaSignerValidatesConfig(t *testing.T) {
	if signer, err := NewMediaSigner(MediaConfig{}); signer != nil || err != nil {
		t.Fatalf("empty config = %v, %v; want nil, nil", signer, err)
	}
	secret := strings.Repeat("s", 32)
	for name, cfg := range map[string]MediaConfig{
		"missing secret": {MediaBaseURL: "https://media.example.test"},
		"missing base":   {SigningSecret: secret},
		"short secret":   {MediaBaseURL: "https://media.example.test", SigningSecret: "short"},
		"http base":      {MediaBaseURL: "http://media.example.test", SigningSecret: secret},
		"base with path": {MediaBaseURL: "https://media.example.test/x", SigningSecret: secret},
		"short window":   {MediaBaseURL: "https://media.example.test", SigningSecret: secret, Window: time.Minute},
	} {
		if _, err := NewMediaSigner(cfg); err == nil {
			t.Errorf("%s: expected error", name)
		}
	}
}
