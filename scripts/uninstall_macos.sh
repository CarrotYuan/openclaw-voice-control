#!/bin/bash
set -euo pipefail

LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
SERVICE_LABEL="ai.openclaw.voice-control"
OVERLAY_LABEL="ai.openclaw.overlay"
SERVICE_DST="$LAUNCH_AGENTS_DIR/$SERVICE_LABEL.plist"
OVERLAY_DST="$LAUNCH_AGENTS_DIR/$OVERLAY_LABEL.plist"

launchctl bootout "gui/$(id -u)/$SERVICE_LABEL" 2>/dev/null || true
launchctl bootout "gui/$(id -u)/$OVERLAY_LABEL" 2>/dev/null || true

rm -f "$SERVICE_DST" "$OVERLAY_DST"

echo
echo "Uninstall complete."
echo "Removed service plist: $SERVICE_DST"
echo "Removed overlay plist: $OVERLAY_DST"
