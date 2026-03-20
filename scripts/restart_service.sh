#!/bin/bash
set -euo pipefail

LABEL="${VOICE_CONTROL_LAUNCHD_LABEL:-ai.openclaw.voice-control}"
SERVICE="gui/$(id -u)/$LABEL"

echo "Restarting $SERVICE"
launchctl kickstart -k "$SERVICE"
echo
launchctl print "$SERVICE" | sed -n '1,40p'
