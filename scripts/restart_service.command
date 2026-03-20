#!/bin/bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

cd "$PROJECT_DIR"
chmod +x scripts/*.sh

echo "== OpenClaw Voice Control: Restart Service =="
echo "project: $PROJECT_DIR"
echo

./scripts/restart_service.sh

echo
echo "Restart finished."
echo "Press Enter to close this window."
read -r _
