#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_FILE="$ROOT_DIR/deploy/cloudflared-propscrap.yml"

cloudflared tunnel --config "$CONFIG_FILE" run
