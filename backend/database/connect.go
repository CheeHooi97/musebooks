package database

import (
	"context"
	"errors"
	"fmt"
	"github.com/jackc/pgx/v5/pgconn"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
	"musebooks/config"
	"regexp"
	"strings"
	"time"
)

var timeZoneName = regexp.MustCompile(`^[A-Za-z0-9_+/-]+$`)

func quoteDSN(value string) string {
	return "'" + strings.ReplaceAll(strings.ReplaceAll(value, "\\", "\\\\"), "'", "\\'") + "'"
}
// The GORM postgres driver reads timezone= from the DSN text itself and would
// send quotes to the server as part of the value, so it stays bare.
func connectionDSN(host, port, user, password, name, sslMode, timeZone string, readOnly bool) (string, error) {
	if !timeZoneName.MatchString(timeZone) {
		return "", fmt.Errorf("POSTGRES_TIMEZONE must be a time zone name such as UTC")
	}
	dsn := fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s sslmode=%s timezone=%s connect_timeout=10", quoteDSN(host), quoteDSN(port), quoteDSN(user), quoteDSN(password), quoteDSN(name), quoteDSN(sslMode), timeZone)
	if readOnly {
		dsn += " default_transaction_read_only=on"
	}
	return dsn, nil
}

func Open(readOnly bool, migration bool) (*gorm.DB, error) {
	user, password := config.DBUser, config.DBPassword
	if migration && config.DBMigrationUser != "" {
		user, password = config.DBMigrationUser, config.DBMigrationPassword
	}
	dsn, err := connectionDSN(config.DBHost, config.DBPort, user, password, config.DBName, config.DBSSLMode, config.DBTimeZone, readOnly)
	if err != nil {
		return nil, err
	}
	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{Logger: logger.Default.LogMode(logger.Silent)})
	if err != nil {
		var pgErr *pgconn.PgError
		if errors.As(err, &pgErr) {
			return nil, fmt.Errorf("PostgreSQL rejected the connection (SQLSTATE %s)", pgErr.Code)
		}
		return nil, fmt.Errorf("cannot connect to configured PostgreSQL database (%T)", err)
	}
	pool, err := db.DB()
	if err != nil {
		return nil, err
	}
	pool.SetMaxOpenConns(20)
	pool.SetMaxIdleConns(10)
	pool.SetConnMaxIdleTime(5 * time.Minute)
	pool.SetConnMaxLifetime(30 * time.Minute)
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	if err = pool.PingContext(ctx); err != nil {
		pool.Close()
		return nil, fmt.Errorf("PostgreSQL connection check failed")
	}
	return db, nil
}
