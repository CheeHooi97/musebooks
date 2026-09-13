package config

import (
	"log"
	"os"

	"github.com/joho/godotenv"
)

var (
	Env          string
	DBHost       string
	DBPort       string
	DBUser       string
	DBPassword   string
	DBName       string
	DBSSLMode    string
	DBTimeZone   string
	SystemAesKey string
)

// LoadConfig
func LoadConfig() {
	_ = godotenv.Load()

	Env = GetEnv("ENV")
	DBHost = GetEnv("POSTGRES_HOST")
	DBPort = GetEnv("POSTGRES_PORT")
	DBUser = GetEnv("POSTGRES_USER")
	DBPassword = GetEnv("POSTGRES_PASSWORD")
	DBName = GetEnv("POSTGRES_DATABASE")
	DBSSLMode = GetEnv("POSTGRES_SSLMODE")
	DBTimeZone = GetEnv("POSTGRES_TIMEZONE")
	SystemAesKey = GetEnv("SYSTEM_AES_KEY")
}

func GetEnv(key string) string {
	value, exists := os.LookupEnv(key)
	if !exists {
		log.Fatalf("%s environment variable not set", key)
	}
	return value
}
