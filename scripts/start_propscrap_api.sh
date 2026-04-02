#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API_DIR="$ROOT_DIR/apps/api"

cd "$API_DIR"
exec .venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8001
