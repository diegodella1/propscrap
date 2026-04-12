#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WEB_DIR="$ROOT_DIR/apps/web"

BASE_WEB="${BASE_WEB:-http://127.0.0.1:3000}"
BASE_API_HEALTH="${BASE_API_HEALTH:-http://127.0.0.1:8001/health}"

echo "[release] health"
curl -fsS "$BASE_API_HEALTH" >/dev/null
curl -fsS "$BASE_WEB/" >/dev/null

echo "[release] backend unit tests"
bash "$ROOT_DIR/scripts/test_api.sh"

echo "[release] web production build"
(
  cd "$WEB_DIR"
  npm run build
)

echo "[release] end-to-end smoke"
bash "$ROOT_DIR/scripts/smoke_easytaciones.sh"

echo "[release] READY"
