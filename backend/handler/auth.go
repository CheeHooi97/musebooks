package handler

import (
	"crypto/subtle"
	"errors"
	"net/http"
	"net/url"
	"strings"
	"time"

	"github.com/labstack/echo/v4"
	"musebooks/config"
	"musebooks/model"
	"musebooks/service"
)

const authSessionCookieName = "musebooks_session"

// Auth mutations accept JSON from explicitly trusted app origins. Cookies are
// host-only, HttpOnly and SameSite=Lax; native clients use bearer tokens.
func AuthRequest(next echo.HandlerFunc) echo.HandlerFunc {
	return func(c echo.Context) error {
		c.Response().Header().Set("Cache-Control", "no-store")
		if c.Request().Method == http.MethodPost {
			if strings.Split(c.Request().Header.Get("Content-Type"), ";")[0] != "application/json" {
				return authFailure(c, 415, "Use a JSON request.", "invalid_request")
			}
			origin := c.Request().Header.Get("Origin")
			if origin != "" {
				allowed := false
				for _, trusted := range strings.Split(config.CORSOrigins+","+config.SiteURL, ",") {
					if origin == strings.TrimSpace(trusted) {
						allowed = true
						break
					}
				}
				if !allowed {
					return authFailure(c, 403, "This sign-in request is not allowed.", "invalid_origin")
				}
			} else if c.Request().Header.Get("Sec-Fetch-Site") == "cross-site" {
				return authFailure(c, 403, "This sign-in request is not allowed.", "invalid_origin")
			}
		}
		return next(c)
	}
}

func authFailure(c echo.Context, status int, message, code string) error {
	return c.JSON(status, map[string]any{"error": true, "errmsg": message, "code": code})
}

func authError(c echo.Context, err error) error {
	switch {
	case errors.Is(err, service.ErrInvalidCredentials), errors.Is(err, service.ErrSessionInvalid):
		return authFailure(c, 401, "Email or password is incorrect.", "invalid_credentials")
	case errors.Is(err, service.ErrEmailNotVerified):
		return authFailure(c, 403, "Verify your email before signing in.", "email_not_verified")
	case errors.Is(err, service.ErrEmailVerificationUnavailable):
		return authFailure(c, 503, "Email verification is unavailable. Please try again later.", "email_unavailable")
	case errors.Is(err, service.ErrEmailDelivery):
		return authFailure(c, 503, "We could not send the email. Please try again shortly.", "email_delivery_failed")
	case errors.Is(err, service.ErrVerificationResendTooSoon):
		c.Response().Header().Set("Retry-After", "60")
		return authFailure(c, 429, "Wait a minute before requesting another code.", "resend_too_soon")
	case errors.Is(err, service.ErrVerificationAttemptsExceeded):
		return authFailure(c, 429, "Too many attempts. Request a new code.", "attempts_exceeded")
	case errors.Is(err, service.ErrVerificationCodeExpired):
		return authFailure(c, 400, "This code has expired. Request a new code.", "code_expired")
	case errors.Is(err, service.ErrInvalidVerificationCode):
		return authFailure(c, 400, "This code is invalid. Check the email and try again.", "invalid_code")
	case errors.Is(err, service.ErrInvalidEmail), errors.Is(err, service.ErrPasswordTooShort), errors.Is(err, service.ErrPasswordTooLong):
		return authFailure(c, 400, err.Error(), "invalid_credentials_format")
	default:
		c.Logger().Error("account request failed")
		return authFailure(c, 500, "We could not complete this request. Please try again.", "auth_failed")
	}
}

type authInput struct {
	Email    string `json:"email"`
	Password string `json:"password"`
	Code     string `json:"code"`
}

func (h *Handler) Register(c echo.Context) error {
	var input authInput
	if err := c.Bind(&input); err != nil {
		return authFailure(c, 400, "Enter your email and password.", "invalid_request")
	}
	user, _, err := h.Auth.Register(c.Request().Context(), input.Email, input.Password)
	if errors.Is(err, service.ErrEmailDelivery) && user != nil {
		return responseJSON(c, map[string]any{"verificationRequired": true, "email": user.Email, "sent": false})
	}
	if err != nil {
		return authError(c, err)
	}
	return responseJSON(c, map[string]any{"verificationRequired": true, "email": user.Email, "sent": true})
}

func (h *Handler) Login(c echo.Context) error {
	var input authInput
	if err := c.Bind(&input); err != nil {
		return authFailure(c, 400, "Enter your email and password.", "invalid_request")
	}
	user, token, err := h.Auth.Login(c.Request().Context(), input.Email, input.Password)
	if err != nil {
		return authError(c, err)
	}
	return h.authSession(c, user, token)
}

func (h *Handler) VerifyEmail(c echo.Context) error {
	var input authInput
	if err := c.Bind(&input); err != nil {
		return authFailure(c, 400, "Enter your email and verification code.", "invalid_request")
	}
	user, token, err := h.Auth.VerifyEmail(c.Request().Context(), input.Email, strings.TrimSpace(input.Code))
	if err != nil {
		return authError(c, err)
	}
	return h.authSession(c, user, token)
}

func (h *Handler) ResendVerification(c echo.Context) error {
	var input authInput
	if err := c.Bind(&input); err != nil {
		return authFailure(c, 400, "Enter your email address.", "invalid_request")
	}
	if err := h.Auth.ResendEmailVerification(c.Request().Context(), input.Email); err != nil {
		return authError(c, err)
	}
	return responseJSON(c, map[string]any{"sent": true})
}

func (h *Handler) ForgotPassword(c echo.Context) error {
	var input authInput
	if err := c.Bind(&input); err != nil {
		return authFailure(c, 400, "Enter your email address.", "invalid_request")
	}
	if err := h.Auth.RequestPasswordReset(c.Request().Context(), input.Email); err != nil {
		return authError(c, err)
	}
	return responseJSON(c, map[string]any{"sent": true})
}

func (h *Handler) ResetPassword(c echo.Context) error {
	var input authInput
	if err := c.Bind(&input); err != nil {
		return authFailure(c, 400, "Enter your email, reset code and new password.", "invalid_request")
	}
	user, token, err := h.Auth.ResetPassword(c.Request().Context(), input.Email, input.Code, input.Password)
	if err != nil {
		return authError(c, err)
	}
	return h.authSession(c, user, token)
}

func authToken(c echo.Context) string {
	parts := strings.Fields(c.Request().Header.Get("Authorization"))
	if len(parts) == 2 && strings.EqualFold(parts[0], "Bearer") {
		return parts[1]
	}
	// Native endpoints never fall back to cookies.
	if strings.HasPrefix(c.Path(), "/v1/mobile/") {
		return ""
	}
	if cookie, err := c.Cookie(authSessionCookieName); err == nil {
		return cookie.Value
	}
	return ""
}

func (h *Handler) CurrentAuthUser(c echo.Context) error {
	user, err := h.Auth.CurrentUser(c.Request().Context(), authToken(c))
	if err != nil {
		if errors.Is(err, service.ErrSessionInvalid) {
			return authFailure(c, 401, "Sign in to continue.", "session_expired")
		}
		return authError(c, err)
	}
	return responseJSON(c, map[string]any{"user": user})
}

func (h *Handler) Logout(c echo.Context) error {
	if err := h.Auth.Logout(c.Request().Context(), authToken(c)); err != nil {
		return authError(c, err)
	}
	if !strings.HasPrefix(c.Path(), "/v1/mobile/") {
		setAuthCookie(c, "", time.Unix(1, 0), -1)
	}
	return responseJSON(c, map[string]any{"signedOut": true})
}

func setAuthCookie(c echo.Context, token string, expires time.Time, maxAge int) {
	secure := strings.HasPrefix(config.SiteURL, "https://") || c.Request().TLS != nil
	c.SetCookie(&http.Cookie{Name: authSessionCookieName, Value: token, Path: "/", HttpOnly: true, Secure: secure, SameSite: http.SameSiteLaxMode, Expires: expires, MaxAge: maxAge})
}

func (h *Handler) authSession(c echo.Context, user *model.User, token string) error {
	now := time.Now().UTC()
	result := map[string]any{"user": user}
	if strings.HasPrefix(c.Path(), "/v1/mobile/") {
		result["sessionToken"] = token
		result["expiresAt"] = h.Auth.SessionExpiresAt(now)
	} else {
		expires := h.Auth.SessionExpiresAt(now)
		setAuthCookie(c, token, expires, int(expires.Sub(now)/time.Second))
	}
	return responseJSON(c, result)
}

// Legacy account management endpoints must never be public once passwords
// and verified identities exist. Keep them available only to internal tools.
func RequireAccountManagementToken(next echo.HandlerFunc) echo.HandlerFunc {
	return func(c echo.Context) error {
		token := config.GetEnvOrDefault("SCRAPER_INGEST_TOKEN", "")
		if token == "" || subtle.ConstantTimeCompare([]byte(token), []byte(c.Request().Header.Get("X-Scraper-Token"))) != 1 {
			return authFailure(c, 401, "Internal access required.", "unauthorized")
		}
		return next(c)
	}
}

func (h *Handler) AuthProviders(c echo.Context) error {
	return responseJSON(c, map[string]any{"google": h.OAuth != nil && h.OAuth.configured(), "email": h.Auth.EmailVerificationConfigured()})
}

func trustedSiteURL() string {
	parsed, err := url.Parse(config.SiteURL)
	if err != nil || parsed.Host == "" {
		return ""
	}
	return strings.TrimRight(config.SiteURL, "/")
}
