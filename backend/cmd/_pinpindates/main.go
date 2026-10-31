package main

import (
	"fmt"
	"musebooks/config"
	"musebooks/database"
	"os"

	"github.com/joho/godotenv"
	"gorm.io/gorm"
)

const person = "model-5a07c41fad41c705b36a7002a28cb1cb129cf93a78ddef22371150f18eb2920c"

var dates = []struct{ title, date, precision string }{
	{"一蘋的海岸線", "2022-12-01", "month"},
	{"雪妹的交換日記", "2023-01-01", "year"},
	{"轉生到蘋行世界", "2023-11-01", "month"},
	{"讓世界和蘋的純欲姊姊", "2024-01-01", "year"},
	{"純・欲双子", "2025-11-01", "month"},
	{"家有雙生女友", "2025-01-01", "year"},
	{"2026「純·欲姊姊特休中」寫真單書", "2026-06-01", "month"},
}

func main() {
	_ = godotenv.Load()
	config.LoadConfig()
	db, err := database.Open(false, false)
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
	apply := len(os.Args) > 1 && os.Args[1] == "apply"
	err = db.Transaction(func(tx *gorm.DB) error {
		for _, d := range dates {
			res := tx.Exec(`UPDATE editions e SET release_date=?::timestamptz, release_precision=?, updated_at=now()
 FROM works w JOIN work_people wp ON wp.work_id=w.id JOIN people p ON p.id=wp.person_id
 WHERE e.work_id=w.id AND e.status<>'superseded' AND e.release_date IS NULL AND w.original_title=? AND p.slug=? AND wp.role='featured'`,
				d.date+"T00:00:00Z", d.precision, d.title, person)
			if res.Error != nil {
				return res.Error
			}
			fmt.Printf("%-40s %s (%s): %d edition(s)\n", d.title, d.date, d.precision, res.RowsAffected)
			if res.RowsAffected != 1 {
				return fmt.Errorf("expected exactly 1 edition for %s", d.title)
			}
		}
		if !apply {
			return fmt.Errorf("dry run: rolled back")
		}
		return nil
	})
	fmt.Println("result:", err)
}
