#!/usr/bin/env bash
set -Eeuo pipefail

release_id="${1:-}"
archive="${2:-}"

if [[ ! "$release_id" =~ ^[0-9a-f]{40}-[0-9]+-[0-9]+$ ]]; then
  echo "Invalid release identifier." >&2
  exit 2
fi
if [[ "$EUID" -ne 0 ]]; then
  echo "Run this deployment as root (the GitHub deploy user needs non-interactive sudo)." >&2
  exit 2
fi
if [[ ! -f "$archive" ]]; then
  echo "Release archive not found: $archive" >&2
  exit 2
fi

work_dir="$(mktemp -d /tmp/musebooks-deploy.XXXXXX)"
cleanup() {
  rm -rf -- "$work_dir"
  rm -f -- "$archive"
}
trap cleanup EXIT

if tar -tzf "$archive" | grep -Eq '(^/|(^|/)\.\.(/|$))'; then
  echo "Release archive contains an unsafe path." >&2
  exit 2
fi
tar -xzf "$archive" -C "$work_dir"

for path in \
  "$work_dir/website/index.html" \
  "$work_dir/musebooks-api" \
  "$work_dir/musebooks-api.service" \
  "$work_dir/musebooks-site.conf"; do
  if [[ ! -f "$path" ]]; then
    echo "Release is missing $path" >&2
    exit 2
  fi
done
if ! grep -Fq 'MuseBooks' "$work_dir/website/index.html" || grep -Fq 'MuseCards' "$work_dir/website/index.html"; then
  echo "The packaged index does not look like the MuseBooks website." >&2
  exit 2
fi

api_root=/opt/musebooks/backend
api_releases="$api_root/releases"
api_current="$api_root/current"
web_root=/var/www/musebooks
web_releases="$web_root/releases"
web_current="$web_root/current"
service_file=/etc/systemd/system/musebooks-api.service
site_file=/etc/nginx/sites-available/musebooks.my
site_enabled=/etc/nginx/sites-enabled/musebooks.my

for command in nginx systemctl curl tar install; do
  command -v "$command" >/dev/null || { echo "Required server command not found: $command" >&2; exit 2; }
done
id musebooks >/dev/null 2>&1 || { echo "Create the musebooks service account first; see DEPLOYMENT.md." >&2; exit 2; }
id www-data >/dev/null 2>&1 || { echo "Nginx www-data account is missing." >&2; exit 2; }
[[ -r "$api_root/.env" ]] || { echo "Create $api_root/.env before deploying; see DEPLOYMENT.md." >&2; exit 2; }
[[ -r /etc/letsencrypt/live/musebooks.my/fullchain.pem ]] || { echo "Issue the musebooks.my Let's Encrypt certificate before deploying; see DEPLOYMENT.md." >&2; exit 2; }
[[ -r /etc/letsencrypt/live/musebooks.my/privkey.pem ]] || { echo "Let's Encrypt private key is missing; see DEPLOYMENT.md." >&2; exit 2; }

if [[ -L "$site_file" ]]; then
  echo "$site_file must be a regular Nginx config file, not a symlink." >&2
  exit 2
fi
if [[ -e "$site_enabled" && ! -L "$site_enabled" ]]; then
  echo "$site_enabled exists and is not a symlink; inspect the active Nginx config before deploying." >&2
  exit 2
fi

# Do not silently steal a MuseBooks host name from another active virtual host.
shopt -s nullglob
for config in /etc/nginx/sites-enabled/* /etc/nginx/conf.d/*.conf; do
  [[ -f "$config" ]] || continue
  resolved="$(readlink -f -- "$config" 2>/dev/null || true)"
  [[ "$resolved" == "$site_file" ]] && continue
  if grep -Eq '^[[:space:]]*server_name[^;]*([[:space:]]|^)(www[.])?musebooks[.]my([[:space:]]|;)' "$config"; then
    echo "Conflicting MuseBooks server_name found in $config. Remove or split that host entry, then rerun deployment." >&2
    exit 2
  fi
done

mkdir -p "$api_releases" "$web_releases" /etc/nginx/sites-available /etc/nginx/sites-enabled
api_release="$api_releases/$release_id"
web_release="$web_releases/$release_id"
rm -rf -- "$api_release" "$web_release"
install -d -o root -g musebooks -m 0750 "$api_release"
install -o root -g musebooks -m 0750 "$work_dir/musebooks-api" "$api_release/musebooks-api"
install -d -o www-data -g www-data -m 0755 "$web_release"
cp -a "$work_dir/website/." "$web_release/"
chown -R www-data:www-data "$web_release"

old_api_target="$(readlink "$api_current" 2>/dev/null || true)"
old_web_target="$(readlink "$web_current" 2>/dev/null || true)"
old_site_link="$(readlink "$site_enabled" 2>/dev/null || true)"
had_service=0
had_site=0
[[ -f "$service_file" ]] && had_service=1
[[ -f "$site_file" ]] && had_site=1
if (( had_service )); then cp -a "$service_file" "$work_dir/old-musebooks-api.service"; fi
if (( had_site )); then cp -a "$site_file" "$work_dir/old-musebooks-site.conf"; fi

unit_changed=0
api_link_changed=0
site_changed=0
enabled_changed=0
web_link_changed=0
committed=0
replace_link() {
  local target="$1"
  local link="$2"
  local temporary="${link}.new.$$"
  rm -f -- "$temporary"
  ln -s -- "$target" "$temporary"
  mv -Tf -- "$temporary" "$link"
}
restore_link() {
  local target="$1"
  local link="$2"
  if [[ -n "$target" ]]; then
    replace_link "$target" "$link"
  else
    rm -f -- "$link"
  fi
}
rollback() {
  local status=$?
  trap - ERR
  set +e
  if (( web_link_changed )); then restore_link "$old_web_target" "$web_current"; fi
  if (( enabled_changed )); then
    if [[ -n "$old_site_link" ]]; then
      replace_link "$old_site_link" "$site_enabled"
    else
      rm -f -- "$site_enabled"
    fi
  fi
  if (( site_changed )); then
    if (( had_site )); then cp -a "$work_dir/old-musebooks-site.conf" "$site_file"; else rm -f -- "$site_file"; fi
  fi
  if (( api_link_changed )); then restore_link "$old_api_target" "$api_current"; fi
  if (( unit_changed )); then
    if (( had_service )); then cp -a "$work_dir/old-musebooks-api.service" "$service_file"; else rm -f -- "$service_file"; fi
  fi
  systemctl daemon-reload
  if (( had_service )); then systemctl restart musebooks-api; else systemctl stop musebooks-api; fi
  if nginx -t; then systemctl reload nginx; fi
  echo "MuseBooks release $release_id failed and the previous active links/config were restored." >&2
  exit "$status"
}
trap rollback ERR

unit_changed=1
install -o root -g root -m 0644 "$work_dir/musebooks-api.service" "$service_file"
api_link_changed=1
replace_link "$api_release" "$api_current"
systemctl daemon-reload
systemctl enable musebooks-api
systemctl restart musebooks-api

api_ready=0
for attempt in $(seq 1 20); do
  if curl --fail --silent --show-error --max-time 3 http://127.0.0.1:2002/v1/origins >/dev/null; then
    api_ready=1
    break
  fi
  sleep 2
done
if (( ! api_ready )); then
  echo "MuseBooks API did not become healthy at http://127.0.0.1:2002/v1/origins." >&2
  false
fi

site_changed=1
install -o root -g root -m 0644 "$work_dir/musebooks-site.conf" "$site_file"
enabled_changed=1
replace_link "$site_file" "$site_enabled"
web_link_changed=1
replace_link "$web_release" "$web_current"
nginx -t
systemctl reload nginx

committed=1
trap - ERR
echo "Deployed MuseBooks release $release_id."
