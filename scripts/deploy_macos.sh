#!/bin/bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
SERVICE_LABEL="ai.openclaw.voice-control"
OVERLAY_LABEL="ai.openclaw.overlay"
SERVICE_SRC="$PROJECT_DIR/launchagents/$SERVICE_LABEL.plist"
OVERLAY_SRC="$PROJECT_DIR/launchagents/$OVERLAY_LABEL.plist"
SERVICE_DST="$LAUNCH_AGENTS_DIR/$SERVICE_LABEL.plist"
OVERLAY_DST="$LAUNCH_AGENTS_DIR/$OVERLAY_LABEL.plist"

mkdir -p "$LAUNCH_AGENTS_DIR" "$PROJECT_DIR/logs" "$PROJECT_DIR/runtime"

if [ ! -f "$PROJECT_DIR/.env" ]; then
  echo "Missing $PROJECT_DIR/.env"
  echo "Copy .env.example to .env and fill required values first."
  exit 1
fi

if [ ! -x "$PROJECT_DIR/scripts/start_service.sh" ] || [ ! -x "$PROJECT_DIR/scripts/start_overlay.sh" ]; then
  echo "Expected executable scripts are missing or not executable."
  echo "Run: chmod +x scripts/*.sh"
  exit 1
fi

sed "s#__PROJECT_DIR__#$PROJECT_DIR#g" "$SERVICE_SRC" > "$SERVICE_DST"
sed "s#__PROJECT_DIR__#$PROJECT_DIR#g" "$OVERLAY_SRC" > "$OVERLAY_DST"

launchctl bootout "gui/$(id -u)/$SERVICE_LABEL" 2>/dev/null || true
launchctl bootout "gui/$(id -u)/$OVERLAY_LABEL" 2>/dev/null || true

bootstrap_one() {
  local label="$1"
  local plist_path="$2"

  echo
  echo "== Bootstrapping $label =="
  if ! plutil -lint "$plist_path" >/dev/null; then
    echo "[error] plist validation failed: $plist_path"
    plutil -lint "$plist_path" || true
    return 1
  fi

  if ! launchctl bootstrap "gui/$(id -u)" "$plist_path"; then
    echo "[error] launchctl bootstrap failed for $label"
    echo "plist: $plist_path"
    echo
    echo "Try these checks:"
    echo "  launchctl print-disabled \"gui/\$(id -u)\" | grep '$label' || true"
    echo "  launchctl print \"gui/\$(id -u)/$label\" | sed -n '1,80p'"
    return 1
  fi

  if ! launchctl kickstart -k "gui/$(id -u)/$label"; then
    echo "[error] launchctl kickstart failed for $label"
    echo "Try:"
    echo "  launchctl print \"gui/\$(id -u)/$label\" | sed -n '1,80p'"
    return 1
  fi

  echo "[ok] $label"
}

bootstrap_one "$SERVICE_LABEL" "$SERVICE_DST"
bootstrap_one "$OVERLAY_LABEL" "$OVERLAY_DST"

echo
echo "Deployment complete."
echo "Service plist: $SERVICE_DST"
echo "Overlay plist: $OVERLAY_DST"
