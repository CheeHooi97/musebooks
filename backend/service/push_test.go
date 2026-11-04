package service

import (
	"context"
	"crypto/ecdh"
	"crypto/rand"
	"encoding/base64"
	"io"
	"net/http"
	"strings"
	"testing"
	"time"

	webpush "github.com/SherClockHolmes/webpush-go"

	"musebooks/model"
)

func TestPushEndpointsAreLimitedToBrowserPushServices(t *testing.T) {
	for _, endpoint := range []string{
		"https://fcm.googleapis.com/fcm/send/abc",
		"https://updates.push.services.mozilla.com/wpush/v2/abc",
		"https://web.push.apple.com/QAbc",
		"https://wns2-par02p.notify.windows.com/w/?token=abc",
	} {
		if !ValidPushEndpoint(endpoint) {
			t.Errorf("rejected %s", endpoint)
		}
	}
	for _, endpoint := range []string{
		"http://fcm.googleapis.com/fcm/send/abc",
		"https://fcm.googleapis.com:8443/fcm/send/abc",
		"https://user@fcm.googleapis.com/fcm/send/abc",
		"https://storage.googleapis.com/bucket",
		"https://evil.example/push.apple.com",
		"https://push.apple.com.evil.example/x",
		"https://127.0.0.1/x",
		"https://localhost/x",
		"https://169.254.169.254/latest/meta-data",
		"https://fcm.googleapis.com/" + strings.Repeat("a", 1000),
	} {
		if ValidPushEndpoint(endpoint) {
			t.Errorf("accepted %s", endpoint)
		}
	}
}

func browserKeys(t *testing.T) (string, string) {
	t.Helper()
	key, err := ecdh.P256().GenerateKey(rand.Reader)
	if err != nil {
		t.Fatal(err)
	}
	secret := make([]byte, 16)
	rand.Read(secret)
	return base64.RawURLEncoding.EncodeToString(key.PublicKey().Bytes()), base64.RawURLEncoding.EncodeToString(secret)
}

func TestPushKeysMustBeABrowserKeyAndSecret(t *testing.T) {
	p256dh, auth := browserKeys(t)
	if !validPushKeys(p256dh, auth) || !validPushKeys(p256dh+"=", auth+"==") {
		t.Fatal("valid browser keys rejected")
	}
	if validPushKeys(auth, auth) || validPushKeys(p256dh, p256dh) || validPushKeys("", "") || validPushKeys("not base64!", auth) {
		t.Fatal("invalid keys accepted")
	}
}

func TestDigestMessageIsLocalizedAndCountsTheRest(t *testing.T) {
	titles := []pushTitle{{OriginalTitle: "写真集A", EnglishTitle: "Photobook A"}, {OriginalTitle: "写真集B"}}
	en := digestMessage("en", 5, titles)
	if en.Title != "New on MuseBooks" || en.Body != "5 new publications: Photobook A, 写真集B and 3 more" || en.URL != "/" {
		t.Fatalf("en: %+v", en)
	}
	if one := digestMessage("en", 1, titles[:1]); one.Body != "1 new publication: Photobook A" {
		t.Fatalf("singular: %q", one.Body)
	}
	if ja := digestMessage("ja", 5, titles); ja.Body != "新着5件：写真集A、写真集B ほか3件" {
		t.Fatalf("ja: %q", ja.Body)
	}
	if zh := digestMessage("zh-Hant", 2, titles); zh.Body != "新增 2 本：写真集A、写真集B" {
		t.Fatalf("zh-Hant: %q", zh.Body)
	}
	long := digestMessage("en", 1, []pushTitle{{OriginalTitle: strings.Repeat("長", 80)}})
	if !strings.HasSuffix(long.Body, "…") || len([]rune(long.Body)) > 90 {
		t.Fatalf("long title not shortened: %q", long.Body)
	}
}

func TestNextPushDigestIsTenInTheMorningMalaysiaTime(t *testing.T) {
	before := time.Date(2026, 11, 4, 1, 30, 0, 0, time.UTC)
	if got := NextPushDigest(before); !got.Equal(time.Date(2026, 11, 4, 2, 0, 0, 0, time.UTC)) {
		t.Fatalf("before 10:00 MYT: %s", got)
	}
	if got := NextPushDigest(time.Date(2026, 11, 4, 2, 0, 0, 0, time.UTC)); !got.Equal(time.Date(2026, 11, 5, 2, 0, 0, 0, time.UTC)) {
		t.Fatalf("at 10:00 MYT: %s", got)
	}
}

type pushRoundTrip func(*http.Request) (*http.Response, error)

func (f pushRoundTrip) Do(r *http.Request) (*http.Response, error) { return f(r) }

func TestSendSignsAndEncryptsForThePushService(t *testing.T) {
	private, public, err := webpush.GenerateVAPIDKeys()
	if err != nil {
		t.Fatal(err)
	}
	p256dh, auth := browserKeys(t)
	var seen *http.Request
	var body []byte
	s := &PushService{cfg: PushConfig{PublicKey: public, PrivateKey: private, Subject: "https://musebooks.my"}, now: time.Now,
		client: pushRoundTrip(func(r *http.Request) (*http.Response, error) {
			seen = r
			body, _ = io.ReadAll(r.Body)
			return &http.Response{StatusCode: http.StatusCreated, Body: io.NopCloser(strings.NewReader(""))}, nil
		})}
	sub := model.PushSubscription{ID: "x", Endpoint: "https://fcm.googleapis.com/fcm/send/abc", P256dh: p256dh, Auth: auth}
	if !s.send(context.Background(), sub, []byte(`{"title":"New on MuseBooks"}`)) {
		t.Fatal("delivery not counted")
	}
	if seen.URL.Host != "fcm.googleapis.com" || seen.Header.Get("Content-Encoding") != "aes128gcm" || seen.Header.Get("Topic") != pushTopic || seen.Header.Get("TTL") != "86400" {
		t.Fatalf("unexpected request: %s %v", seen.URL, seen.Header)
	}
	if !strings.HasPrefix(seen.Header.Get("Authorization"), "vapid t=") || !strings.Contains(seen.Header.Get("Authorization"), "k="+public) {
		t.Fatalf("missing VAPID signature: %q", seen.Header.Get("Authorization"))
	}
	if strings.Contains(string(body), "MuseBooks") {
		t.Fatal("payload was sent unencrypted")
	}
}

func TestPushStaysOffWithoutKeys(t *testing.T) {
	var none *PushService
	if none.Enabled() || none.PublicKey() != "" || NewPushService(nil, PushConfig{PublicKey: "a", PrivateKey: "b"}).Enabled() {
		t.Fatal("push enabled without keys or database")
	}
	if err := NewPushService(nil, PushConfig{}).Subscribe(context.Background(), "u", "https://fcm.googleapis.com/x", "", "", "en"); err != ErrPushUnavailable {
		t.Fatalf("subscribe without keys: %v", err)
	}
}
