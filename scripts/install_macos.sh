#!/bin/bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
PLIST_SRC="$PROJECT_DIR/launchagents/ai.openclaw.voice-control.plist"
PLIST_DST="$LAUNCH_AGENTS_DIR/ai.openclaw.voice-control.plist"

mkdir -p "$LAUNCH_AGENTS_DIR"

if [ ! -f "$PROJECT_DIR/.env" ]; then
  echo "Missing $PROJECT_DIR/.env"
  echo "Copy .env.example to .env and fill required values first."
  exit 1
fi

if [ ! -f "$PLIST_SRC" ]; then
  echo "Missing launch agent template: $PLIST_SRC"
  exit 1
fi

sed "s#__PROJECT_DIR__#$PROJECT_DIR#g" "$PLIST_SRC" > "$PLIST_DST"

launchctl bootout "gui/$(id -u)" "$PLIST_DST" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST_DST"
launchctl kickstart -k "gui/$(id -u)/ai.openclaw.voice-control"

echo
echo "Installed launch agent:"
echo "  $PLIST_DST"
