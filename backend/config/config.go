package config

import (
	"log"
	"os"
	"strconv"
	"strings"
	"time"

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
	SiteURL                 string
	GoogleClientID          string
	GoogleClientSecret      string
	GoogleRedirectURL       string
	ResendAPIKey            string
	EmailFrom               string
	EmailVerificationSecret string
	// Cloudflare R2 media Worker (deploy/media-worker).
	CloudflareR2PublicBaseURL      string
	CloudflareR2MediaBaseURL       string
	CloudflareR2MediaSigningSecret string
	CloudflareR2MediaURLWindow     time.Duration
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
	SiteURL = strings.TrimRight(GetEnvOrDefault("SITE_URL", "https://musebooks.my"), "/")
	GoogleClientID = GetEnvOrDefault("GOOGLE_CLIENT_ID", "")
	GoogleClientSecret = GetEnvOrDefault("GOOGLE_CLIENT_SECRET", "")
	GoogleRedirectURL = GetEnvOrDefault("GOOGLE_REDIRECT_URL", SiteURL+"/v1/auth/oauth/google/callback")
	ResendAPIKey = GetEnvOrDefault("RESEND_API_KEY", "")
	EmailFrom = GetEnvOrDefault("EMAIL_FROM", "")
	EmailVerificationSecret = GetEnvOrDefault("EMAIL_VERIFICATION_SECRET", "")
	CloudflareR2PublicBaseURL = GetEnvOrDefault("CLOUDFLARE_R2_PUBLIC_BASE_URL", "")
	CloudflareR2MediaBaseURL = GetEnvOrDefault("CLOUDFLARE_R2_MEDIA_BASE_URL", "")
	CloudflareR2MediaSigningSecret = GetEnvOrDefault("CLOUDFLARE_R2_MEDIA_SIGNING_SECRET", "")
	CloudflareR2MediaURLWindow = time.Duration(GetEnvIntOrDefault("CLOUDFLARE_R2_MEDIA_URL_WINDOW_SECONDS", 86400)) * time.Second
}

func GetEnvIntOrDefault(key string, fallback int) int {
	value := strings.TrimSpace(GetEnvOrDefault(key, ""))
	if value == "" {
		return fallback
	}
	parsed, err := strconv.Atoi(value)
	if err != nil {
		log.Fatalf("%s must be an integer", key)
	}
	return parsed
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
