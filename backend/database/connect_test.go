package database

import (
	"regexp"
	"testing"

	"github.com/jackc/pgx/v5"
)

// The GORM postgres driver extracts timezone with this pattern and sends the
// match as the TimeZone runtime parameter; a quoted value is rejected by
// PostgreSQL with SQLSTATE 22023.
var driverTimeZone = regexp.MustCompile("(time_zone|TimeZone|timezone)=(.*?)($|&| )")

func TestConnectionDSNSendsABareTimeZone(t *testing.T) {
	dsn, err := connectionDSN("127.0.0.1", "5432", "user", `p'a ss\word`, "musebooks", "require", "Asia/Kuala_Lumpur", true)
	if err != nil {
		t.Fatal(err)
	}
	if got := driverTimeZone.FindStringSubmatch(dsn)[2]; got != "Asia/Kuala_Lumpur" {
		t.Fatalf("driver would send TimeZone %q", got)
	}
	parsed, err := pgx.ParseConfig(dsn)
	if err != nil {
		t.Fatal(err)
	}
	if parsed.Password != `p'a ss\word` || parsed.RuntimeParams["default_transaction_read_only"] != "on" {
		t.Fatalf("quoted fields were not preserved: %+v", parsed.RuntimeParams)
	}
	for _, bad := range []string{"", "'UTC'", "UTC sslmode=disable"} {
		if _, err := connectionDSN("h", "1", "u", "p", "d", "require", bad, false); err == nil {
			t.Errorf("accepted time zone %q", bad)
		}
	}
}
