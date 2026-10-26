package handler

import (
	"context"
	"crypto/rand"
	"crypto/sha256"
	"crypto/subtle"
	"encoding/base64"
	"encoding/json"
	"errors"
	"io"
	"net/http"
	"net/url"
	"strings"
	"sync"
	"time"

	"github.com/labstack/echo/v4"
)

const googleStateCookie = "musebooks_google_state"
const mobileAuthCallback = "my.musebooks.app://auth/callback"

type GoogleOAuth struct {
	clientID, clientSecret, redirectURL string
	client                              *http.Client
	exchangesMu                         sync.Mutex
	exchanges                           map[string]oauthExchange
}

type oauthExchange struct {
	token, challenge string
	expiresAt        time.Time
}

func NewGoogleOAuth(clientID, clientSecret, redirectURL string) *GoogleOAuth {
	return &GoogleOAuth{clientID: strings.TrimSpace(clientID), clientSecret: strings.TrimSpace(clientSecret), redirectURL: strings.TrimSpace(redirectURL), client: &http.Client{Timeout: 15 * time.Second}}
}

func (s *GoogleOAuth) configured() bool {
	return s != nil && s.clientID != "" && s.clientSecret != "" && s.redirectURL != ""
}

func randomAuthToken() (string, error) {
	raw := make([]byte, 32)
	if _, err := rand.Read(raw); err != nil {
		return "", err
	}
	return base64.RawURLEncoding.EncodeToString(raw), nil
}

func oauthChallenge(verifier string) string {
	hash := sha256.Sum256([]byte(verifier))
	return base64.RawURLEncoding.EncodeToString(hash[:])
}

func (h *Handler) GoogleStart(c echo.Context) error {
	mobileChallenge := c.QueryParam("challenge")
	if c.QueryParam("mobile") == "1" {
		raw, err := base64.RawURLEncoding.DecodeString(mobileChallenge)
		if err != nil || len(raw) != sha256.Size {
			return authFailure(c, 400, "Restart Google sign-in.", "invalid_challenge")
		}
	} else {
		mobileChallenge = ""
	}
	if h.OAuth == nil || !h.OAuth.configured() {
		return googleRedirect(c, "oauth_unavailable", mobileChallenge != "")
	}
	state, err := randomAuthToken()
	if err != nil {
		return googleRedirect(c, "oauth_unavailable", mobileChallenge != "")
	}
	verifier, err := randomAuthToken()
	if err != nil {
		return googleRedirect(c, "oauth_unavailable", mobileChallenge != "")
	}
	c.SetCookie(&http.Cookie{Name: googleStateCookie, Value: state + "." + verifier + "." + mobileChallenge, Path: "/v1/auth/oauth/google", HttpOnly: true, Secure: strings.HasPrefix(h.OAuth.redirectURL, "https://"), SameSite: http.SameSiteLaxMode, Expires: time.Now().Add(10 * time.Minute), MaxAge: 600})
	values := url.Values{"client_id": {h.OAuth.clientID}, "redirect_uri": {h.OAuth.redirectURL}, "response_type": {"code"}, "scope": {"openid email profile"}, "state": {state}, "code_challenge": {oauthChallenge(verifier)}, "code_challenge_method": {"S256"}}
	return c.Redirect(302, "https://accounts.google.com/o/oauth2/v2/auth?"+values.Encode())
}

func googleRedirect(c echo.Context, result string, mobile bool) error {
	base := trustedSiteURL() + "/login"
	if mobile {
		base = mobileAuthCallback
	}
	return c.Redirect(302, base+"?"+url.Values{"oauth_error": {result}}.Encode())
}

func (h *Handler) GoogleCallback(c echo.Context) error {
	cookie, err := c.Cookie(googleStateCookie)
	secure := h.OAuth != nil && strings.HasPrefix(h.OAuth.redirectURL, "https://")
	c.SetCookie(&http.Cookie{Name: googleStateCookie, Path: "/v1/auth/oauth/google", Value: "", HttpOnly: true, Secure: secure, SameSite: http.SameSiteLaxMode, MaxAge: -1, Expires: time.Unix(1, 0)})
	if err != nil {
		return googleRedirect(c, "oauth_state_invalid", false)
	}
	parts := strings.Split(cookie.Value, ".")
	if len(parts) != 3 || len(parts[0]) != 43 || len(parts[1]) != 43 || subtle.ConstantTimeCompare([]byte(parts[0]), []byte(c.QueryParam("state"))) != 1 {
		return googleRedirect(c, "oauth_state_invalid", false)
	}
	mobile := parts[2] != ""
	if c.QueryParam("error") != "" {
		return googleRedirect(c, "oauth_cancelled", mobile)
	}
	if h.OAuth == nil || !h.OAuth.configured() || c.QueryParam("code") == "" {
		return googleRedirect(c, "oauth_unavailable", mobile)
	}
	profile, err := h.OAuth.profile(c.Request().Context(), c.QueryParam("code"), parts[1])
	if err != nil {
		return googleRedirect(c, "oauth_failed", mobile)
	}
	user, token, err := h.Auth.OAuthLogin(c.Request().Context(), "google", profile.Subject, profile.Email, profile.Picture)
	if err != nil {
		return googleRedirect(c, "oauth_failed", mobile)
	}
	if mobile {
		code, err := h.OAuth.issueExchange(token, parts[2], time.Now())
		if err != nil {
			_ = h.Auth.Logout(c.Request().Context(), token)
			return googleRedirect(c, "oauth_failed", true)
		}
		return c.Redirect(302, mobileAuthCallback+"?"+url.Values{"exchange_code": {code}}.Encode())
	}
	_ = user
	now := time.Now()
	expires := h.Auth.SessionExpiresAt(now)
	setAuthCookie(c, token, expires, int(expires.Sub(now)/time.Second))
	return c.Redirect(302, trustedSiteURL()+"/account")
}

type googleProfile struct {
	Subject       string `json:"sub"`
	Email         string `json:"email"`
	EmailVerified bool   `json:"email_verified"`
	Picture       string `json:"picture"`
}

// Profile data comes only from Google's authenticated userinfo endpoint.
// No browser-supplied email, profile or unverified identity token is trusted.
func (s *GoogleOAuth) profile(ctx context.Context, code, verifier string) (googleProfile, error) {
	values := url.Values{"client_id": {s.clientID}, "client_secret": {s.clientSecret}, "redirect_uri": {s.redirectURL}, "code": {code}, "code_verifier": {verifier}, "grant_type": {"authorization_code"}}
	req, err := http.NewRequestWithContext(ctx, "POST", "https://oauth2.googleapis.com/token", strings.NewReader(values.Encode()))
	if err != nil {
		return googleProfile{}, err
	}
	req.Header.Set("Content-Type", "application/x-www-form-urlencoded")
	response, err := s.client.Do(req)
	if err != nil {
		return googleProfile{}, err
	}
	defer response.Body.Close()
	var token struct {
		AccessToken string `json:"access_token"`
	}
	if response.StatusCode != 200 || json.NewDecoder(io.LimitReader(response.Body, 1<<20)).Decode(&token) != nil || token.AccessToken == "" {
		return googleProfile{}, errors.New("Google sign-in failed")
	}
	req, err = http.NewRequestWithContext(ctx, "GET", "https://openidconnect.googleapis.com/v1/userinfo", nil)
	if err != nil {
		return googleProfile{}, err
	}
	req.Header.Set("Authorization", "Bearer "+token.AccessToken)
	response, err = s.client.Do(req)
	if err != nil {
		return googleProfile{}, err
	}
	defer response.Body.Close()
	var profile googleProfile
	if response.StatusCode != 200 || json.NewDecoder(io.LimitReader(response.Body, 1<<20)).Decode(&profile) != nil || !profile.EmailVerified || strings.TrimSpace(profile.Email) == "" || strings.TrimSpace(profile.Subject) == "" {
		return googleProfile{}, errors.New("Google did not verify this email")
	}
	return profile, nil
}

func (s *GoogleOAuth) issueExchange(token, challenge string, now time.Time) (string, error) {
	code, err := randomAuthToken()
	if err != nil {
		return "", err
	}
	s.exchangesMu.Lock()
	defer s.exchangesMu.Unlock()
	if s.exchanges == nil {
		s.exchanges = map[string]oauthExchange{}
	}
	for key, pending := range s.exchanges {
		if !pending.expiresAt.After(now) {
			delete(s.exchanges, key)
		}
	}
	if len(s.exchanges) >= 10000 {
		return "", errors.New("too many pending sign-ins")
	}
	s.exchanges[oauthChallenge(code)] = oauthExchange{token: token, challenge: challenge, expiresAt: now.Add(time.Minute)}
	return code, nil
}

func (s *GoogleOAuth) redeemExchange(code, verifier string, now time.Time) (string, bool) {
	if s == nil || len(code) != 43 || len(verifier) != 43 {
		return "", false
	}
	key := oauthChallenge(code)
	s.exchangesMu.Lock()
	pending, ok := s.exchanges[key]
	delete(s.exchanges, key)
	s.exchangesMu.Unlock()
	if !ok || !pending.expiresAt.After(now) || subtle.ConstantTimeCompare([]byte(oauthChallenge(verifier)), []byte(pending.challenge)) != 1 {
		return "", false
	}
	return pending.token, true
}

func (h *Handler) MobileOAuthExchange(c echo.Context) error {
	var input struct {
		Code     string `json:"code"`
		Verifier string `json:"verifier"`
	}
	if err := c.Bind(&input); err != nil {
		return authFailure(c, 400, "Restart Google sign-in.", "invalid_request")
	}
	token, ok := h.OAuth.redeemExchange(input.Code, input.Verifier, time.Now())
	if !ok {
		return authFailure(c, 401, "Google sign-in expired. Please try again.", "oauth_expired")
	}
	user, err := h.Auth.CurrentUser(c.Request().Context(), token)
	if err != nil {
		return authError(c, err)
	}
	return h.authSession(c, user, token)
}
