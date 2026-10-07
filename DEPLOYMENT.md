# MuseBooks production deployment

The `Deploy MuseBooks` GitHub Actions workflow builds the website and Linux API on every push to `main`, then deploys them to the same server as MuseCards. It publishes an independent MuseBooks web root, installs its Nginx host config, restarts the API, and checks the public website and API.

The live `musebooks.my` page was inspected and currently serves MuseCards content. The MuseBooks export in this repository is branded MuseBooks. That points to the shared server routing `musebooks.my` to its MuseCards/default site. The deployment installs a specific `musebooks.my` Nginx host so the domain uses MuseBooks' own document root. If another active Nginx config already claims that host, deployment stops and reports the conflicting file rather than altering MuseCards' configuration.

Cloudflare DNS for `musebooks.my` and `www.musebooks.my` is already proxied to the MuseCards server address, `157.245.200.202`.

## One-time server setup

The shared Ubuntu/Debian server needs Nginx, PostgreSQL, and Certbot. The MuseBooks API listens on `127.0.0.1:2002`; port `2001` is already used by Picklah on this server. Nginx proxies MuseBooks API requests to its own port, leaving MuseCards and Picklah services intact. Allow inbound ports 80 and 443 in the server and provider firewalls.

The production server already has a MuseBooks database with catalog data. Setup preserves that database and changes ownership only within MuseBooks. Do not recreate or restore over it. These PostgreSQL commands are for a fresh server with no MuseBooks database; the current server already has its dedicated `musebooks` PostgreSQL role and Linux service account:

~~~sh
sudo -u postgres createuser --pwprompt musebooks
sudo -u postgres createdb --owner=musebooks musebooks
sudo adduser --system --group --no-create-home musebooks
sudo install -d -o root -g musebooks -m 0750 /opt/musebooks/backend/releases
sudo install -d -o www-data -g www-data -m 0755 /var/www/musebooks/releases
sudo install -d -o www-data -g www-data -m 0755 /var/www/letsencrypt/.well-known/acme-challenge
~~~

Create `/opt/musebooks/backend/.env` on the server with production values. Keep the database password from `createuser` private, generate the AES key with `openssl rand -base64 32`, and generate the scraper token with `openssl rand -hex 32`:

~~~dotenv
ENV=production
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
POSTGRES_USER=musebooks
POSTGRES_PASSWORD=replace-with-the-database-password
POSTGRES_DATABASE=musebooks
POSTGRES_SSLMODE=disable
POSTGRES_TIMEZONE=Asia/Singapore
SYSTEM_AES_KEY=replace-with-base64-encoded-32-byte-key
SCRAPER_INGEST_TOKEN=replace-with-a-long-random-token
MUSEBOOKS_API_ADDR=127.0.0.1:2002
MUSEBOOKS_SEED_DEMO=false
~~~

Set the file permissions:

~~~sh
sudo chown root:musebooks /opt/musebooks/backend/.env
sudo chmod 0640 /opt/musebooks/backend/.env
~~~

Before adding the temporary HTTP config, inspect `/etc/nginx/sites-enabled` for any other active file declaring `musebooks.my` or `www.musebooks.my`. Keep MuseCards' host entries intact; remove only a duplicate MuseBooks host entry or split it into its own site config. The GitHub deployment performs the same conflict check.

Issue the origin certificate. Replace the email with an address for expiry notices:

~~~sh
sudo install -m 0644 deploy/musebooks-acme.conf /etc/nginx/sites-available/musebooks.my
sudo ln -sfn /etc/nginx/sites-available/musebooks.my /etc/nginx/sites-enabled/musebooks.my
sudo nginx -t && sudo systemctl reload nginx
sudo certbot certonly --webroot -w /var/www/letsencrypt -d musebooks.my -d www.musebooks.my --email you@example.com --agree-tos --no-eff-email
~~~

The deploy workflow installs the final Nginx site config and API systemd service. Install the certificate-renewal reload hook once:

~~~sh
sudo install -d -m 0755 /etc/letsencrypt/renewal-hooks/deploy
sudo install -m 0755 deploy/reload-nginx-on-cert-renew.sh /etc/letsencrypt/renewal-hooks/deploy/musebooks-reload-nginx
~~~

## GitHub Actions secrets

In the MuseBooks GitHub repository, add these repository secrets using the same server connection values as the MuseCards deployment:

| Secret | Value |
| --- | --- |
| `DEPLOY_HOST` | Shared server hostname or IP (`157.245.200.202`) |
| `DEPLOY_PORT` | SSH port, usually `22` |
| `DEPLOY_USER` | SSH deployment account |
| `DEPLOY_SSH_KEY` | Private key for that account |
| `DEPLOY_KNOWN_HOSTS` | Verified SSH host-key line for that server and port |

That SSH account needs non-interactive `sudo -n` access for the deployment script. Keep the private key in GitHub Secrets; do not put it in the repository. GitHub Actions uses the official checkout, setup-node, and setup-go actions.

## Deploy and verify

After the one-time server setup and secrets are in place, every push to `main` runs the workflow. You can also run it from **GitHub → Actions → Deploy MuseBooks → Run workflow**. It builds the Next.js static export and Linux amd64 Go API, uploads an immutable release, activates the MuseBooks Nginx virtual host and API, and checks:

- `https://musebooks.my/` contains MuseBooks and does not contain MuseCards.
- `https://musebooks.my/v1/origins` responds successfully.

The deploy script rolls the active release links and configs back if the local API check or Nginx reload fails. A separate catalog import is still needed if the production MuseBooks database should contain records; the website does not substitute demo data.
