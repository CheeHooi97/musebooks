package main

import (
	"flag"
	"fmt"
	"log"
	"musebooks/config"
	"musebooks/database"
)

func main() {
	apply := flag.Bool("apply", false, "apply additive catalog structure migrations")
	grant := flag.String("grant-app-role", "", "grant catalog access to an existing PostgreSQL API role")
	flag.Parse()
	config.LoadConfig()
	if config.DBName != config.DefaultDatabaseName {
		log.Fatal("Migration is restricted to the dedicated musebooks database")
	}
	db, err := database.Open(false, true)
	if err != nil {
		log.Fatal(err)
	}
	pool, _ := db.DB()
	defer pool.Close()
	var info struct {
		DatabaseName, RoleName                  string
		Superuser, CreateDatabase, SchemaCreate bool
		UnreadableTables                        int64
		ForeignOwnedTables                      int64
	}
	err = db.Raw(`SELECT current_database() AS database_name,current_user AS role_name,r.rolsuper AS superuser,r.rolcreatedb AS create_database,
 has_schema_privilege(current_user,'public','CREATE') AS schema_create,
 (SELECT COUNT(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='public' AND c.relkind='r' AND NOT has_table_privilege(c.oid,'SELECT')) AS unreadable_tables,
 (SELECT COUNT(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='public' AND c.relkind='r' AND NOT pg_has_role(c.relowner,'USAGE')) AS foreign_owned_tables
 FROM pg_roles r WHERE r.rolname=current_user`).Scan(&info).Error
	if err != nil {
		log.Fatal("Cannot inspect database ownership")
	}
	fmt.Printf("Database: %s\nRole: %s\nSuperuser: %t\nCan create test databases: %t\nSchema create: %t\nUnreadable tables: %d\nTables owned by other roles: %d\n", info.DatabaseName, info.RoleName, info.Superuser, info.CreateDatabase, info.SchemaCreate, info.UnreadableTables, info.ForeignOwnedTables)
	if !*apply && *grant == "" {
		fmt.Println("Inspection only; no schema or data was changed.")
		return
	}
	if !info.Superuser && (!info.SchemaCreate || info.ForeignOwnedTables > 0) {
		log.Fatal("Owner credentials are required. Configure POSTGRES_MIGRATION_USER and POSTGRES_MIGRATION_PASSWORD in the local environment; runtime credentials remain unchanged.")
	}
	if *apply {
		if err = database.Migrate(db); err != nil {
			log.Fatal("Catalog migration failed: ", err)
		}
		fmt.Println("Catalog structure migration applied.")
	}
	if *grant != "" {
		if err = database.GrantApplicationAccess(db, *grant); err != nil {
			log.Fatal("Application grants failed: ", err)
		}
		fmt.Println("Application catalog permissions configured.")
	}
}
