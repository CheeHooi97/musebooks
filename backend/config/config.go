package config

import (
	"log"
	"os"
	"strings"

	"github.com/joho/godotenv"
)

const DefaultDatabaseName = "musebooks"

var (
	Env                     string
	DBHost                  string
	DBPort                  string
	DBUser                  string
	DBPassword              string
	DBName                  string
	DBSSLMode               string
	DBTimeZone              string
	DBAutoMigrate           bool
	DBSkipStartupMigrations bool
	DBMigrationUser         string
	DBMigrationPassword     string
	HTTPAddr                string
	CORSOrigins             string
	SystemAesKey            string
)

// LoadConfig
func LoadConfig() {
	_ = godotenv.Load()

	Env = GetEnv("ENV")
	DBHost = GetEnv("POSTGRES_HOST")
	DBPort = GetEnv("POSTGRES_PORT")
	DBUser = GetEnv("POSTGRES_USER")
	DBPassword = GetEnv("POSTGRES_PASSWORD")
	DBName = strings.TrimSpace(GetEnvOrDefault("POSTGRES_DATABASE", DefaultDatabaseName))
	if DBName == "" {
		DBName = DefaultDatabaseName
	}
	DBSSLMode = GetEnvOrDefault("POSTGRES_SSLMODE", "disable")
	DBTimeZone = GetEnvOrDefault("POSTGRES_TIMEZONE", "UTC")
	DBAutoMigrate = strings.EqualFold(GetEnvOrDefault("POSTGRES_AUTO_MIGRATE", "false"), "true")
	DBSkipStartupMigrations = strings.EqualFold(GetEnvOrDefault("POSTGRES_SKIP_STARTUP_MIGRATIONS", "false"), "true")
	DBMigrationUser = GetEnvOrDefault("POSTGRES_MIGRATION_USER", "")
	DBMigrationPassword = GetEnvOrDefault("POSTGRES_MIGRATION_PASSWORD", "")
	HTTPAddr = GetEnvOrDefault("HTTP_ADDR", ":2002")
	CORSOrigins = GetEnvOrDefault("CORS_ALLOWED_ORIGINS", "http://localhost:4173,http://127.0.0.1:4173,capacitor://localhost,https://localhost,http://localhost")
	SystemAesKey = GetEnv("SYSTEM_AES_KEY")
}

func GetEnvOrDefault(key, fallback string) string {
	if value, exists := os.LookupEnv(key); exists && value != "" {
		return value
	}
	return fallback
}

func GetEnv(key string) string {
	value, exists := os.LookupEnv(key)
	if !exists {
		log.Fatalf("%s environment variable not set", key)
	}
	return value
}
