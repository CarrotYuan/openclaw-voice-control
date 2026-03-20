#!/bin/bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
FAILED=0

check_file() {
  local file="$1"
  if [ -f "$file" ]; then
    echo "[ok] file exists: $file"
  else
    echo "[warn] missing file: $file"
    FAILED=1
  fi
}

check_cmd() {
  local cmd="$1"
  if command -v "$cmd" >/dev/null 2>&1; then
    echo "[ok] command available: $cmd"
  else
    echo "[warn] command not found: $cmd"
    FAILED=1
  fi
}

echo "== OpenClaw Voice Control doctor =="
echo "project: $PROJECT_DIR"
echo

check_file "$PROJECT_DIR/.env"
check_file "$PROJECT_DIR/config/default.yaml"
check_file "$PROJECT_DIR/scripts/start_service.sh"
check_file "$PROJECT_DIR/scripts/start_overlay.sh"
check_file "$PROJECT_DIR/launchagents/ai.openclaw.voice-control.plist"
check_file "$PROJECT_DIR/launchagents/ai.openclaw.overlay.plist"

echo
check_cmd python3
check_cmd launchctl
check_cmd say
check_cmd afplay

echo
SCAN_TARGETS=(
  "$PROJECT_DIR/src"
  "$PROJECT_DIR/launchagents"
  "$PROJECT_DIR/config"
)

LEGACY_PATTERN='/Users/[^/]+/|com\.[^.]+\.openclaw|com\.openclaw\.overlay'

if rg -n -P "$LEGACY_PATTERN" "${SCAN_TARGETS[@]}" >/dev/null 2>&1; then
  echo "[warn] found absolute user-path or legacy-label residue in public runtime files"
  rg -n -P "$LEGACY_PATTERN" "${SCAN_TARGETS[@]}" || true
  FAILED=1
else
  echo "[ok] no private-path or legacy-label residue in runtime files"
fi

echo
if [ -d "$PROJECT_DIR/.venv" ]; then
  echo "[ok] local virtual environment present: $PROJECT_DIR/.venv"
else
  echo "[info] no .venv found yet; deploy scripts can still fall back to python3"
fi

echo
if [ "$FAILED" -eq 0 ]; then
  echo "doctor result: PASS"
else
  echo "doctor result: CHECK WARNINGS"
fi
