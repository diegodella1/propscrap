#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WEB_DIR="$ROOT_DIR/apps/web"

cd "$WEB_DIR"
export INTERNAL_API_BASE_URL="${INTERNAL_API_BASE_URL:-http://127.0.0.1:8001}"
export INTERNAL_WEB_BASE_URL="${INTERNAL_WEB_BASE_URL:-http://127.0.0.1:3000}"
export NEXT_PUBLIC_SITE_URL="${NEXT_PUBLIC_SITE_URL:-https://propscrap.diegodella.ar}"
export NEXT_PUBLIC_API_BASE_URL="${NEXT_PUBLIC_API_BASE_URL:-}"
export PROPSCRAP_WEB_BUILD_ON_START="${PROPSCRAP_WEB_BUILD_ON_START:-1}"
export PROPSCRAP_WEB_CLEAN_BUILD_ON_START="${PROPSCRAP_WEB_CLEAN_BUILD_ON_START:-1}"

if [[ "$PROPSCRAP_WEB_CLEAN_BUILD_ON_START" == "1" ]]; then
  rm -rf .next
fi

if [[ "$PROPSCRAP_WEB_BUILD_ON_START" == "1" || ! -f .next/BUILD_ID ]]; then
  npm run build
fi

exec npm run start -- --hostname 127.0.0.1 --port 3000
