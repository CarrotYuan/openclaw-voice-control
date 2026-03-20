#!/bin/bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
SERVICE_LABEL="ai.openclaw.voice-control"
OVERLAY_LABEL="ai.openclaw.overlay"
SERVICE_DST="$LAUNCH_AGENTS_DIR/$SERVICE_LABEL.plist"
OVERLAY_DST="$LAUNCH_AGENTS_DIR/$OVERLAY_LABEL.plist"
HOST_APPS_DIR="$PROJECT_DIR/runtime/host_apps"
SERVICE_HOST_EXEC="$HOST_APPS_DIR/OpenClawVoiceControlServiceHost.app/Contents/MacOS/OpenClawVoiceControlServiceHost"
OVERLAY_HOST_EXEC="$HOST_APPS_DIR/OpenClawVoiceControlOverlayHost.app/Contents/MacOS/OpenClawVoiceControlOverlayHost"

bootout_label() {
  local label="$1"
  launchctl bootout "gui/$(id -u)/$label" 2>/dev/null || true
  launchctl remove "$label" 2>/dev/null || true
}

kill_matching() {
  local pattern="$1"
  pkill -if "$pattern" 2>/dev/null || true
}

bootout_label "$SERVICE_LABEL"
bootout_label "$OVERLAY_LABEL"

kill_matching "$SERVICE_HOST_EXEC"
kill_matching "$OVERLAY_HOST_EXEC"
kill_matching "python.*-m openclaw_voice_control( |$)"
kill_matching "python.*-m openclaw_voice_control\\.overlay_app( |$)"
kill_matching "python.*openclaw-voice-control/.venv/bin/python.*openclaw_voice_control"
kill_matching "OpenClawVoiceControlServiceHost"
kill_matching "OpenClawVoiceControlOverlayHost"

rm -f "$SERVICE_DST" "$OVERLAY_DST"
rm -rf "$HOST_APPS_DIR"

echo
echo "Uninstall complete."
echo "Removed service plist: $SERVICE_DST"
echo "Removed overlay plist: $OVERLAY_DST"
echo "Removed generated host apps: $HOST_APPS_DIR"
