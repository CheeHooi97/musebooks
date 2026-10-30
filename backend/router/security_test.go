package router

import (
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/labstack/echo/v4"
)

func TestClientIPTrustsOnlyLoopbackProxy(t *testing.T) {
	for _, tc := range []struct {
		name, remote, realIP, forwarded, want string
	}{
		{"nginx supplies visitor", "127.0.0.1:5000", "203.0.113.7", "198.51.100.1", "203.0.113.7"},
		{"direct client cannot claim an address", "198.51.100.9:5000", "203.0.113.7", "203.0.113.8", "198.51.100.9"},
		{"invalid header falls back to peer", "127.0.0.1:5000", "not-an-ip", "", "127.0.0.1"},
	} {
		req := httptest.NewRequest(http.MethodGet, "/", nil)
		req.RemoteAddr = tc.remote
		req.Header.Set("X-Real-IP", tc.realIP)
		req.Header.Set("X-Forwarded-For", tc.forwarded)
		if got := clientIP(req); got != tc.want {
			t.Errorf("%s: clientIP = %q, want %q", tc.name, got, tc.want)
		}
	}
}

func TestRateLimitClientGroupsIPv6By64(t *testing.T) {
	e := echo.New()
	e.IPExtractor = clientIP
	key := func(remote string) string {
		req := httptest.NewRequest(http.MethodGet, "/", nil)
		req.RemoteAddr = remote
		got, _ := rateLimitClient(e.NewContext(req, httptest.NewRecorder()))
		return got
	}
	if a, b := key("[2001:db8:1:2::1]:443"), key("[2001:db8:1:2:ffff::9]:443"); a != b || a != "2001:db8:1:2::/64" {
		t.Fatalf("IPv6 keys = %q, %q; want one /64 budget", a, b)
	}
	if got := key("198.51.100.9:443"); got != "198.51.100.9" {
		t.Fatalf("IPv4 key = %q", got)
	}
}

func TestScraperTokenFailsClosed(t *testing.T) {
	e := echo.New()
	ok := func(c echo.Context) error { return c.NoContent(http.StatusNoContent) }
	for _, tc := range []struct {
		configured, sent string
		want             int
	}{
		{"", "", http.StatusUnauthorized},
		{"", "anything", http.StatusUnauthorized},
		{"secret", "wrong", http.StatusUnauthorized},
		{"secret", "secret", http.StatusNoContent},
	} {
		req := httptest.NewRequest(http.MethodPost, "/", nil)
		req.Header.Set("X-Scraper-Token", tc.sent)
		rec := httptest.NewRecorder()
		err := requireScraperToken(tc.configured)(ok)(e.NewContext(req, rec))
		status := rec.Code
		if he, isHTTP := err.(*echo.HTTPError); isHTTP {
			status = he.Code
		}
		if status != tc.want {
			t.Errorf("configured %q, sent %q: status %d, want %d", tc.configured, tc.sent, status, tc.want)
		}
	}
}
