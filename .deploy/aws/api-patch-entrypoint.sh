#!/bin/sh
set -e

if [ -f /srv/gauzy/patches/patch_api.js ]; then
  node /srv/gauzy/patches/patch_api.js
fi

if [ -f /srv/gauzy/patches/rebrand_database.js ]; then
  node /srv/gauzy/patches/rebrand_database.js || true
fi

exec ./entrypoint.compose.sh "$@"
