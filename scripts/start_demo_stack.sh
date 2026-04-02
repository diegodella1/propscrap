#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API_DIR="$ROOT_DIR/apps/api"
WEB_DIR="$ROOT_DIR/apps/web"

API_PORT="${API_PORT:-8001}"
WEB_PORT="${WEB_PORT:-3000}"

API_LOG="${API_LOG:-/tmp/licitaciones_ia_api.log}"
WEB_LOG="${WEB_LOG:-/tmp/licitaciones_ia_web.log}"
API_PID_FILE="${API_PID_FILE:-/tmp/licitaciones_ia_api.pid}"
WEB_PID_FILE="${WEB_PID_FILE:-/tmp/licitaciones_ia_web.pid}"

start_detached() {
  local workdir="$1"
  local pid_file="$2"
  local log_file="$3"
  shift 3

  (
    cd "$workdir"
    rm -f "$pid_file"
    setsid "$@" >"$log_file" 2>&1 < /dev/null &
    echo $! >"$pid_file"
  )
}

if fuser "${API_PORT}/tcp" >/dev/null 2>&1; then
  echo "API port ${API_PORT} already in use. Skipping backend start."
else
  start_detached \
    "$API_DIR" \
    "$API_PID_FILE" \
    "$API_LOG" \
    .venv/bin/uvicorn app.main:app --host 127.0.0.1 --port "$API_PORT"
  echo "Backend started on 127.0.0.1:${API_PORT}"
fi

if fuser "${WEB_PORT}/tcp" >/dev/null 2>&1; then
  echo "Web port ${WEB_PORT} already in use. Skipping frontend start."
else
  start_detached \
    "$WEB_DIR" \
    "$WEB_PID_FILE" \
    "$WEB_LOG" \
    env INTERNAL_API_BASE_URL="http://127.0.0.1:${API_PORT}" \
      INTERNAL_WEB_BASE_URL="http://127.0.0.1:${WEB_PORT}" \
      NEXT_PUBLIC_SITE_URL="http://127.0.0.1:${WEB_PORT}" \
      NEXT_PUBLIC_API_BASE_URL="" \
      npm run start -- --hostname 127.0.0.1 --port "$WEB_PORT"
  echo "Frontend started on 127.0.0.1:${WEB_PORT}"
fi

echo "Logs:"
echo "  API: $API_LOG"
echo "  WEB: $WEB_LOG"
