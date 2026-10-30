package router

import (
	"crypto/subtle"
	"net"
	"net/http"

	"github.com/labstack/echo/v4"
)

// clientIP is the visitor address, as in MuseCards. Only the local nginx may
// supply it (X-Real-IP, which nginx sets from Cloudflare's CF-Connecting-IP);
// Internet-supplied X-Forwarded-For is never trusted, so a client cannot
// spoof its way around the sign-in rate limits.
func clientIP(r *http.Request) string {
	ip, _, err := net.SplitHostPort(r.RemoteAddr)
	if err != nil {
		ip = r.RemoteAddr
	}
	if peer := net.ParseIP(ip); peer != nil && peer.IsLoopback() {
		if forwarded := net.ParseIP(r.Header.Get("X-Real-IP")); forwarded != nil {
			return forwarded.String()
		}
	}
	return ip
}

// rateLimitClient returns the key a budget is charged to. IPv6 clients
// usually control a whole /64, so they share one budget per /64.
func rateLimitClient(c echo.Context) (string, error) {
	ip := c.RealIP()
	if parsed := net.ParseIP(ip); parsed != nil && parsed.To4() == nil {
		return parsed.Mask(net.CIDRMask(64, 128)).String() + "/64", nil
	}
	return ip, nil
}

// requireScraperToken fails closed: with no token configured, internal
// endpoints are unavailable rather than open.
func requireScraperToken(token string) echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			if token == "" || subtle.ConstantTimeCompare([]byte(token), []byte(c.Request().Header.Get("X-Scraper-Token"))) != 1 {
				return echo.NewHTTPError(http.StatusUnauthorized, "invalid scraper token")
			}
			return next(c)
		}
	}
}
