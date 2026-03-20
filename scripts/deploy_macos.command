#!/bin/bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

cd "$PROJECT_DIR"
chmod +x scripts/*.sh

echo "== OpenClaw Voice Control: Deploy =="
echo "project: $PROJECT_DIR"
echo

./scripts/deploy_macos.sh

echo
echo "Deployment finished."
echo "Press Enter to close this window."
read -r _
