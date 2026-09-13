package database

import (
	"musebooks/model"

	"gorm.io/gorm"
)

func Migrate(db *gorm.DB) error {
	models := []any{
		&model.User{},
		&model.Admin{},
	}
	err := db.AutoMigrate(models...)
	if err != nil {
		return err
	}
	return nil
}
