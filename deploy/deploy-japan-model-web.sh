#!/usr/bin/env bash
set -Eeuo pipefail
archive=${1:?Pass the reviewed website archive}
web=/var/www/musebooks
test -L "$web/current"
old_web=$(readlink -f "$web/current")
[[ "$old_web" == "$web/releases/"* ]]
release="japan-model-search-$(date -u +%Y%m%dT%H%M%SZ)"
target="$web/releases/$release"
install -d "$target"
tar -xzf "$archive" -C "$target"
test -f "$target/index.html"
chown -R www-data:www-data "$target"
rollback() { ln -sfn "$old_web" "$web/current"; }
trap rollback ERR
ln -sfn "$target" "$web/current"
curl --fail --silent --resolve musebooks.my:443:127.0.0.1 \
  'https://musebooks.my/' -o /tmp/musebooks-japan-model-search-health.html
grep -q MuseBooks /tmp/musebooks-japan-model-search-health.html
trap - ERR
printf 'Activated %s; previous website %s retained\n' "$release" "$old_web"
