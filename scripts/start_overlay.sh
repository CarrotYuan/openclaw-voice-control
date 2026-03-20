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

PYTHON_BIN_OVERRIDE="${VOICE_CONTROL_OVERLAY_PYTHON_BIN:-${VOICE_CONTROL_PYTHON_BIN:-}}"

configure_qt_plugin_env() {
  local python_bin="$1"
  local plugin_base=""
  local platform_base=""

  if [ ! -x "$python_bin" ]; then
    return
  fi

  plugin_base="$("$python_bin" - <<'PY'
from pathlib import Path
try:
    import PySide6
except Exception:
    raise SystemExit(0)
base = Path(PySide6.__file__).resolve().parent / "Qt" / "plugins"
print(base)
PY
)"

  if [ -n "$plugin_base" ] && [ -d "$plugin_base" ]; then
    platform_base="$plugin_base/platforms"
    export QT_PLUGIN_PATH="$plugin_base"
    if [ -d "$platform_base" ]; then
      export QT_QPA_PLATFORM_PLUGIN_PATH="$platform_base"
    fi
  fi
}

if [ -n "$PYTHON_BIN_OVERRIDE" ] && [ -x "$PYTHON_BIN_OVERRIDE" ]; then
  configure_qt_plugin_env "$PYTHON_BIN_OVERRIDE"
  echo "[start_overlay] env_file=$ENV_FILE"
  echo "[start_overlay] python_bin=$PYTHON_BIN_OVERRIDE"
  echo "[start_overlay] qt_plugin_path=${QT_PLUGIN_PATH:-}"
  echo "[start_overlay] qt_platform_plugin_path=${QT_QPA_PLATFORM_PLUGIN_PATH:-}"
  exec "$PYTHON_BIN_OVERRIDE" -m openclaw_voice_control.overlay_app --config "$CONFIG_PATH" --env-file "$ENV_FILE"
fi

if [ -x "$PROJECT_DIR/.venv/bin/python" ]; then
  configure_qt_plugin_env "$PROJECT_DIR/.venv/bin/python"
  echo "[start_overlay] env_file=$ENV_FILE"
  echo "[start_overlay] python_bin=$PROJECT_DIR/.venv/bin/python"
  echo "[start_overlay] qt_plugin_path=${QT_PLUGIN_PATH:-}"
  echo "[start_overlay] qt_platform_plugin_path=${QT_QPA_PLATFORM_PLUGIN_PATH:-}"
  exec "$PROJECT_DIR/.venv/bin/python" -m openclaw_voice_control.overlay_app --config "$CONFIG_PATH" --env-file "$ENV_FILE"
fi

if [ -x "$PROJECT_DIR/.venv/bin/openclaw-overlay" ]; then
  configure_qt_plugin_env "$PROJECT_DIR/.venv/bin/python"
  echo "[start_overlay] env_file=$ENV_FILE"
  echo "[start_overlay] console_script=$PROJECT_DIR/.venv/bin/openclaw-overlay"
  echo "[start_overlay] qt_plugin_path=${QT_PLUGIN_PATH:-}"
  echo "[start_overlay] qt_platform_plugin_path=${QT_QPA_PLATFORM_PLUGIN_PATH:-}"
  exec "$PROJECT_DIR/.venv/bin/openclaw-overlay" --config "$CONFIG_PATH" --env-file "$ENV_FILE"
fi

configure_qt_plugin_env "$(command -v python3 || true)"
echo "[start_overlay] env_file=$ENV_FILE"
echo "[start_overlay] python_bin=python3"
echo "[start_overlay] qt_plugin_path=${QT_PLUGIN_PATH:-}"
echo "[start_overlay] qt_platform_plugin_path=${QT_QPA_PLATFORM_PLUGIN_PATH:-}"
exec python3 -m openclaw_voice_control.overlay_app --config "$CONFIG_PATH" --env-file "$ENV_FILE"
