package handler

import (
	"context"
	"encoding/json"
	"io"
	"net/http"
	"net/http/httptest"
	"net/url"
	"strings"
	"testing"
	"time"

	"github.com/labstack/echo/v4"
	"musebooks/config"
	"musebooks/model"
	"musebooks/service"
)

type authRoundTrip func(*http.Request) (*http.Response, error)

func (f authRoundTrip) RoundTrip(r *http.Request) (*http.Response, error) { return f(r) }

func TestGoogleStartRequiresProofAndBindsStateAndPKCE(t *testing.T) {
	h := &Handler{OAuth: NewGoogleOAuth("client", "secret", "https://musebooks.my/v1/auth/oauth/google/callback")}
	for _, query := range []string{"?mobile=1", "?mobile=1&challenge=bad"} {
		r := httptest.NewRecorder()
		c := echo.New().NewContext(httptest.NewRequest("GET", "/v1/auth/oauth/google"+query, nil), r)
		if err := h.GoogleStart(c); err != nil {
			t.Fatal(err)
		}
		if r.Code != 400 || r.Header().Get("Location") != "" {
			t.Fatalf("invalid native proof accepted: %d", r.Code)
		}
	}
	r := httptest.NewRecorder()
	c := echo.New().NewContext(httptest.NewRequest("GET", "/v1/auth/oauth/google", nil), r)
	if err := h.GoogleStart(c); err != nil {
		t.Fatal(err)
	}
	destination, _ := url.Parse(r.Header().Get("Location"))
	cookies := r.Result().Cookies()
	if destination.Host != "accounts.google.com" || len(cookies) != 1 {
		t.Fatal("Google redirect or state cookie missing")
	}
	cookie := cookies[0]
	parts := strings.Split(cookie.Value, ".")
	if !cookie.HttpOnly || !cookie.Secure || cookie.SameSite != http.SameSiteLaxMode || cookie.Domain != "" {
		t.Fatalf("insecure state cookie: %+v", cookie)
	}
	if destination.Query().Get("state") != parts[0] || destination.Query().Get("code_challenge") != oauthChallenge(parts[1]) || destination.Query().Get("code_challenge_method") != "S256" {
		t.Fatal("state/PKCE binding missing")
	}
}

func TestGoogleCallbackRejectsMissingOrMismatchedStateBeforeExchange(t *testing.T) {
	h := &Handler{OAuth: NewGoogleOAuth("client", "secret", "https://musebooks.my/v1/auth/oauth/google/callback")}
	for _, cookie := range []string{"", strings.Repeat("a", 43) + "." + strings.Repeat("b", 43) + "."} {
		req := httptest.NewRequest("GET", "/v1/auth/oauth/google/callback?state=wrong&code=code", nil)
		if cookie != "" {
			req.AddCookie(&http.Cookie{Name: googleStateCookie, Value: cookie})
		}
		r := httptest.NewRecorder()
		if err := h.GoogleCallback(echo.New().NewContext(req, r)); err != nil {
			t.Fatal(err)
		}
		if !strings.Contains(r.Header().Get("Location"), "oauth_state_invalid") {
			t.Fatal("invalid state accepted")
		}
	}
}

func TestGoogleProfileOnlyAcceptsVerifiedEmailAndSubject(t *testing.T) {
	for _, body := range []string{`{"sub":"google-user","email":"owner@example.com","email_verified":true}`, `{"sub":"google-user","email":"owner@example.com","email_verified":false}`, `{"email":"owner@example.com","email_verified":true}`} {
		s := NewGoogleOAuth("client", "secret", "https://musebooks.my/v1/auth/oauth/google/callback")
		s.client.Transport = authRoundTrip(func(req *http.Request) (*http.Response, error) {
			response := body
			if req.URL.Host == "oauth2.googleapis.com" {
				if err := req.ParseForm(); err != nil {
					t.Fatal(err)
				}
				if req.Form.Get("client_secret") != "secret" || req.Form.Get("code_verifier") != "verifier" {
					t.Fatal("server exchange omitted its credentials or PKCE")
				}
				response = `{"access_token":"provider-token"}`
			} else if req.URL.Host != "openidconnect.googleapis.com" || req.Header.Get("Authorization") != "Bearer provider-token" {
				t.Fatal("untrusted profile request")
			}
			return &http.Response{StatusCode: 200, Body: io.NopCloser(strings.NewReader(response)), Header: make(http.Header)}, nil
		})
		_, err := s.profile(context.Background(), "code", "verifier")
		if (err == nil) != strings.Contains(body, `"sub":"google-user","email":"owner@example.com","email_verified":true`) {
			t.Fatalf("incorrect profile acceptance: %s, %v", body, err)
		}
	}
}

func TestNativeExchangeIsBoundSingleUseAndExpires(t *testing.T) {
	s := NewGoogleOAuth("client", "secret", "callback")
	verifier := strings.Repeat("v", 43)
	now := time.Now()
	code, _ := s.issueExchange("private-session", oauthChallenge(verifier), now)
	if token, ok := s.redeemExchange(code, strings.Repeat("x", 43), now); ok || token != "" {
		t.Fatal("wrong verifier accepted")
	}
	if _, ok := s.redeemExchange(code, verifier, now); ok {
		t.Fatal("failed code replayed")
	}
	code, _ = s.issueExchange("private-session", oauthChallenge(verifier), now)
	if token, ok := s.redeemExchange(code, verifier, now); !ok || token != "private-session" {
		t.Fatal("valid proof rejected")
	}
	if _, ok := s.redeemExchange(code, verifier, now); ok {
		t.Fatal("successful code replayed")
	}
	code, _ = s.issueExchange("private-session", oauthChallenge(verifier), now)
	if _, ok := s.redeemExchange(code, verifier, now.Add(time.Minute)); ok {
		t.Fatal("expired exchange accepted")
	}
}

func TestAuthMutationRejectsForeignOriginsAndFormPosts(t *testing.T) {
	previous := config.SiteURL
	config.SiteURL = "https://musebooks.my"
	defer func() { config.SiteURL = previous }()
	for _, tc := range []struct {
		origin, contentType string
		status              int
	}{{"https://evil.example", "application/json", 403}, {"https://musebooks.my", "application/x-www-form-urlencoded", 415}, {"https://musebooks.my", "application/json", 204}} {
		req := httptest.NewRequest("POST", "/v1/auth/login", strings.NewReader(`{}`))
		req.Header.Set("Origin", tc.origin)
		req.Header.Set("Content-Type", tc.contentType)
		r := httptest.NewRecorder()
		if err := AuthRequest(func(c echo.Context) error { return c.NoContent(204) })(echo.New().NewContext(req, r)); err != nil {
			t.Fatal(err)
		}
		if r.Code != tc.status || r.Header().Get("Cache-Control") != "no-store" {
			t.Fatalf("status=%d, expected=%d", r.Code, tc.status)
		}
	}
}

func TestAuthCookiesAndNativeTokenIsolation(t *testing.T) {
	previous := config.SiteURL
	config.SiteURL = "https://musebooks.my"
	defer func() { config.SiteURL = previous }()
	r := httptest.NewRecorder()
	c := echo.New().NewContext(httptest.NewRequest("GET", "/", nil), r)
	setAuthCookie(c, "opaque-token", time.Now().Add(time.Hour), 3600)
	cookie := r.Result().Cookies()[0]
	if cookie.Name != "musebooks_session" || !cookie.HttpOnly || !cookie.Secure || cookie.Domain != "" || cookie.SameSite != http.SameSiteLaxMode {
		t.Fatalf("insecure session cookie: %+v", cookie)
	}
	req := httptest.NewRequest("GET", "/v1/mobile/auth/me", nil)
	req.AddCookie(cookie)
	c = echo.New().NewContext(req, httptest.NewRecorder())
	c.SetPath("/v1/mobile/auth/me")
	if authToken(c) != "" {
		t.Fatal("native route accepted browser cookie")
	}
	req.Header.Set("Authorization", "Bearer native-token")
	if authToken(c) != "native-token" {
		t.Fatal("native bearer rejected")
	}
}

func TestSessionResponsesKeepCredentialsPrivate(t *testing.T) {
	verified := true
	user := &model.User{Id: "account", Email: "reader@example.com", EmailVerified: &verified, PasswordHash: "private-password-hash", GoogleSubject: "private-provider-subject", EmailVerificationCodeHash: "private-otp-hash", PasswordResetCodeHash: "private-reset-hash"}
	h := &Handler{Auth: service.NewAuthService(nil, nil, time.Hour)}
	for _, path := range []string{"/v1/auth/login", "/v1/mobile/auth/login"} {
		r := httptest.NewRecorder()
		c := echo.New().NewContext(httptest.NewRequest("POST", path, nil), r)
		c.SetPath(path)
		if err := h.authSession(c, user, "opaque-session-secret"); err != nil {
			t.Fatal(err)
		}
		for _, secret := range []string{"private-password-hash", "private-provider-subject", "private-otp-hash", "private-reset-hash"} {
			if strings.Contains(r.Body.String(), secret) {
				t.Fatalf("response exposed %s", secret)
			}
		}
		var payload struct {
			Result map[string]any `json:"result"`
		}
		if err := json.Unmarshal(r.Body.Bytes(), &payload); err != nil {
			t.Fatal(err)
		}
		if strings.Contains(path, "/mobile/") {
			if payload.Result["sessionToken"] != "opaque-session-secret" || len(r.Result().Cookies()) != 0 {
				t.Fatal("native response must use a bearer session only")
			}
		} else if strings.Contains(r.Body.String(), "opaque-session-secret") || len(r.Result().Cookies()) != 1 {
			t.Fatal("website session must only be delivered in a cookie")
		}
	}
}

func TestLegacyAccountManagementRequiresAnInternalSecret(t *testing.T) {
	for _, secret := range []string{"", "configured-secret"} {
		t.Setenv("SCRAPER_INGEST_TOKEN", secret)
		for _, supplied := range []string{"", "wrong", "configured-secret"} {
			req := httptest.NewRequest("POST", "/v1/user/update/account", nil)
			req.Header.Set("X-Scraper-Token", supplied)
			r := httptest.NewRecorder()
			if err := RequireAccountManagementToken(func(c echo.Context) error { return c.NoContent(204) })(echo.New().NewContext(req, r)); err != nil {
				t.Fatal(err)
			}
			want := 401
			if secret != "" && secret == supplied {
				want = 204
			}
			if r.Code != want {
				t.Fatalf("internal access with configured=%t, supplied=%q gave %d", secret != "", supplied, r.Code)
			}
		}
	}
}
