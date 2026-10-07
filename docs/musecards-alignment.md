# MuseCards alignment

MuseBooks was compared directly with `D:/Workspace/Go/gravure-model`, including its live systemd configuration.

| Area | MuseCards | MuseBooks after alignment |
| --- | --- | --- |
| Application frontend | React JavaScript/JSX under `src` | Same |
| Vite configuration | `vite.config.js` | Same |
| Build and output | `vite build`, `dist` | Same |
| Development | Port 4173, `VITE_API_PROXY` | Same; API target is MuseBooks port 2002 |
| Mobile | Vite `mobile` mode and Capacitor | Same build mode and tooling |
| TypeScript | Capacitor configuration and tooling | Same; no TypeScript application files |
| Backend | Go/Echo/GORM; model, repository, service, handler, router | Same layers, adapted to photobooks |
| Server configuration | Backend working directory `.env` loaded by systemd | Same |
| Runtime variables | `HTTP_ADDR`, `CORS_ALLOWED_ORIGINS`, `POSTGRES_*` | Same |
| PostgreSQL role | `tcguser` | Same, with ownership of MuseBooks tables |
| Production database | `gravure_model` | Dedicated `musebooks` database |

Removed the obsolete Next.js app, Next.js configuration, duplicate root libraries, TypeScript application sources, application type-check configuration, React type dependencies, and custom Next-style build wrappers. Prior file contents were preserved in the ignored `.tmp/removed-frontend` backup.

The server PostgreSQL settings were copied directly from MuseCards without printing secrets. MuseBooks keeps its own database, Linux service account, service name, port, and deployment paths. It does not copy MuseCards billing, ads, OAuth, or trading-card features into the photobook product.

The server API was rebuilt, updated with rollback backups, and restarted successfully. MuseCards remains active. Models, publishers, and sold listings were verified through the running MuseBooks API. Browser regression checks cover all four directory/listing screens, error recovery, and mobile layout with no runtime errors. Browser plugin not available; validation used the existing Playwright installation.

Native Android/iOS compilation and device testing were not run.
