#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="apps/api/.venv/bin/python"

if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "API virtualenv not found at $PYTHON_BIN" >&2
  exit 1
fi

"$PYTHON_BIN" -m unittest discover -s apps/api/tests -p "test_*.py" -v
