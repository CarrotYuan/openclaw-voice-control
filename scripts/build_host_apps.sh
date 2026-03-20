#!/bin/bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
RUNTIME_DIR="$PROJECT_DIR/runtime/host_apps"
LAUNCHER_SOURCE="$PROJECT_DIR/scripts/openclaw_host_launcher.m"

build_host_app() {
  local app_name="$1"
  local bundle_id="$2"
  local launch_script="$3"
  local usage_description="$4"
  local app_dir="$RUNTIME_DIR/$app_name.app"
  local contents_dir="$app_dir/Contents"
  local macos_dir="$contents_dir/MacOS"
  local plist_path="$contents_dir/Info.plist"
  local exec_path="$macos_dir/$app_name"

  mkdir -p "$macos_dir"

  cat > "$plist_path" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleDevelopmentRegion</key>
  <string>en</string>
  <key>CFBundleExecutable</key>
  <string>$app_name</string>
  <key>CFBundleIdentifier</key>
  <string>$bundle_id</string>
  <key>CFBundleInfoDictionaryVersion</key>
  <string>6.0</string>
  <key>CFBundleName</key>
  <string>$app_name</string>
  <key>CFBundlePackageType</key>
  <string>APPL</string>
  <key>CFBundleShortVersionString</key>
  <string>1.0</string>
  <key>CFBundleVersion</key>
  <string>1</string>
  <key>LSBackgroundOnly</key>
  <true/>
  <key>NSMicrophoneUsageDescription</key>
  <string>$usage_description</string>
</dict>
</plist>
EOF

  clang \
    -fobjc-arc \
    -framework Foundation \
    -DOPENCLAW_PROJECT_DIR="\"$PROJECT_DIR\"" \
    -DOPENCLAW_TARGET_SCRIPT="\"$PROJECT_DIR/$launch_script\"" \
    -DOPENCLAW_HOST_BUNDLE_ID="\"$bundle_id\"" \
    -DOPENCLAW_HOST_APP_PATH="\"$app_dir\"" \
    "$LAUNCHER_SOURCE" \
    -o "$exec_path"
}

mkdir -p "$RUNTIME_DIR"

build_host_app \
  "OpenClawVoiceControlServiceHost" \
  "ai.openclaw.voice-control.host" \
  "scripts/start_service.sh" \
  "OpenClaw Voice Control needs microphone access for wakeword detection and speech capture."

build_host_app \
  "OpenClawVoiceControlOverlayHost" \
  "ai.openclaw.overlay.host" \
  "scripts/start_overlay.sh" \
  "OpenClaw Voice Control needs microphone access while showing status overlays during voice control."

echo "Built host apps in $RUNTIME_DIR"
