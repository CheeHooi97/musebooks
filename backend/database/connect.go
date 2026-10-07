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
	"strings"
	"time"
)

func quoteDSN(value string) string {
	return "'" + strings.ReplaceAll(strings.ReplaceAll(value, "\\", "\\\\"), "'", "\\'") + "'"
}
func Open(readOnly bool, migration bool) (*gorm.DB, error) {
	user, password := config.DBUser, config.DBPassword
	if migration && config.DBMigrationUser != "" {
		user, password = config.DBMigrationUser, config.DBMigrationPassword
	}
	dsn := fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s sslmode=%s timezone=%s connect_timeout=10", quoteDSN(config.DBHost), quoteDSN(config.DBPort), quoteDSN(user), quoteDSN(password), quoteDSN(config.DBName), quoteDSN(config.DBSSLMode), quoteDSN(config.DBTimeZone))
	if readOnly {
		dsn += " default_transaction_read_only=on"
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
