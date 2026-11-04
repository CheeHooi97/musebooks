package handler

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
	"time"

	"github.com/labstack/echo/v4"

	"musebooks/service"
)

func TestPushNeedsASignedInAccountLikeMuseCardsAlerts(t *testing.T) {
	h := &Handler{Auth: service.NewAuthService(nil, nil, time.Hour), Push: service.NewPushService(nil, service.PushConfig{PublicKey: "pub", PrivateKey: "priv"})}
	e := echo.New()
	for _, call := range []struct {
		method, path string
		run          func(echo.Context) error
	}{
		{http.MethodGet, "/v1/push/subscription", h.PushStatus},
		{http.MethodPost, "/v1/push/subscription", h.PushSubscribe},
		{http.MethodPost, "/v1/push/subscription/remove", h.PushUnsubscribe},
	} {
		req := httptest.NewRequest(call.method, call.path, strings.NewReader(`{"endpoint":"https://fcm.googleapis.com/fcm/send/x","keys":{"p256dh":"a","auth":"b"}}`))
		req.Header.Set("Content-Type", "application/json")
		rec := httptest.NewRecorder()
		if err := call.run(e.NewContext(req, rec)); err != nil {
			t.Fatal(err)
		}
		if rec.Code != http.StatusUnauthorized {
			t.Fatalf("%s %s without a session: %d", call.method, call.path, rec.Code)
		}
	}
}

func TestPushConfigIsPublicAndOffWithoutKeys(t *testing.T) {
	for _, tc := range []struct {
		push    *service.PushService
		enabled bool
	}{{nil, false}, {service.NewPushService(nil, service.PushConfig{}), false}} {
		h := &Handler{Push: tc.push}
		rec := httptest.NewRecorder()
		if err := h.PushConfig(echo.New().NewContext(httptest.NewRequest(http.MethodGet, "/v1/push/config", nil), rec)); err != nil {
			t.Fatal(err)
		}
		var got struct{ Result struct{ Enabled bool } }
		if json.Unmarshal(rec.Body.Bytes(), &got) != nil || got.Result.Enabled != tc.enabled {
			t.Fatalf("config = %s", rec.Body.String())
		}
	}
}

func TestPushRejectsCrossSitePosts(t *testing.T) {
	req := httptest.NewRequest(http.MethodPost, "/v1/push/subscription", strings.NewReader(`{}`))
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Origin", "https://evil.example")
	rec := httptest.NewRecorder()
	called := false
	if err := AuthRequest(func(echo.Context) error { called = true; return nil })(echo.New().NewContext(req, rec)); err != nil {
		t.Fatal(err)
	}
	if called || rec.Code != http.StatusForbidden {
		t.Fatalf("cross-site subscribe reached the handler: %d", rec.Code)
	}
}
