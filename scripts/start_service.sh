#!/bin/bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CONFIG_PATH="${VOICE_CONTROL_CONFIG:-$PROJECT_DIR/config/default.yaml}"
ENV_FILE="${VOICE_CONTROL_ENV_FILE:-$PROJECT_DIR/.env}"

cd "$PROJECT_DIR"

if [ -f "$ENV_FILE" ]; then
  while IFS= read -r raw_line || [ -n "$raw_line" ]; do
    line="${raw_line#"${raw_line%%[![:space:]]*}"}"
    line="${line%"${line##*[![:space:]]}"}"
    [ -z "$line" ] && continue
    case "$line" in
      \#*) continue ;;
    esac
    case "$line" in
      *=*)
        key="${line%%=*}"
        value="${line#*=}"
        key="${key#"${key%%[![:space:]]*}"}"
        key="${key%"${key##*[![:space:]]}"}"
        value="${value#"${value%%[![:space:]]*}"}"
        value="${value%"${value##*[![:space:]]}"}"
        value="${value%\"}"
        value="${value#\"}"
        value="${value%\'}"
        value="${value#\'}"
        export "$key=$value"
        ;;
    esac
  done < "$ENV_FILE"
fi

PYTHON_BIN_OVERRIDE="${VOICE_CONTROL_PYTHON_BIN:-}"

if [ -n "$PYTHON_BIN_OVERRIDE" ] && [ -x "$PYTHON_BIN_OVERRIDE" ]; then
  echo "[start_service] env_file=$ENV_FILE"
  echo "[start_service] python_bin=$PYTHON_BIN_OVERRIDE"
  exec "$PYTHON_BIN_OVERRIDE" -m openclaw_voice_control --config "$CONFIG_PATH" --env-file "$ENV_FILE"
fi

if [ -x "$PROJECT_DIR/.venv/bin/python" ]; then
  echo "[start_service] env_file=$ENV_FILE"
  echo "[start_service] python_bin=$PROJECT_DIR/.venv/bin/python"
  exec "$PROJECT_DIR/.venv/bin/python" -m openclaw_voice_control --config "$CONFIG_PATH" --env-file "$ENV_FILE"
fi

if [ -x "$PROJECT_DIR/.venv/bin/openclaw-voice-control" ]; then
  echo "[start_service] env_file=$ENV_FILE"
  echo "[start_service] console_script=$PROJECT_DIR/.venv/bin/openclaw-voice-control"
  exec "$PROJECT_DIR/.venv/bin/openclaw-voice-control" --config "$CONFIG_PATH" --env-file "$ENV_FILE"
fi

echo "[start_service] env_file=$ENV_FILE"
echo "[start_service] python_bin=python3"
exec python3 -m openclaw_voice_control --config "$CONFIG_PATH" --env-file "$ENV_FILE"
