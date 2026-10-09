#!/usr/bin/env bash
set -euo pipefail

APP_NAME="${APP_NAME:-$(python3 -c 'from scripts.app_registry import DEFAULT_APP_NAME; print(DEFAULT_APP_NAME)')}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
AUTO_INSTALL_PYTHON="${AUTO_INSTALL_PYTHON:-0}"
VENV_DIR="$ROOT_DIR/.venv-mac"
TARGET_ARCH="${TARGET_ARCH:-$(uname -m)}"

for arg in "$@"; do
  case "$arg" in
    --app=*) APP_NAME="${arg#*=}" ;;
    --app) shift; APP_NAME="${1:-$APP_NAME}" ;;
    --list-apps) python3 -c 'from scripts.app_registry import list_app_names; print("\n".join(list_app_names()))'; exit 0 ;;
  esac
done

if [[ "$TARGET_ARCH" != "x86_64" && "$TARGET_ARCH" != "arm64" && "$TARGET_ARCH" != "universal2" ]]; then
  echo "Unsupported TARGET_ARCH: $TARGET_ARCH"
  echo "Use one of: x86_64, arm64, universal2"
  exit 1
fi

APP_SPEC_JSON="$(python3 -c 'import json, sys; from scripts.app_registry import resolve_app_spec; print(json.dumps(resolve_app_spec(sys.argv[1])))' "$APP_NAME")"
APP_DISPLAY_NAME="$(python3 -c 'import json, sys; print(json.loads(sys.argv[1])["display_name"])' "$APP_SPEC_JSON")"
ENTRY_SCRIPT="$(python3 -c 'import json, sys; print(json.loads(sys.argv[1])["entry_script"])' "$APP_SPEC_JSON")"
ASSET_DIR="$(python3 -c 'import json, sys; print(json.loads(sys.argv[1])["asset_dir"])' "$APP_SPEC_JSON")"
ICON_PNG="$ROOT_DIR/$ASSET_DIR/logo.png"
ICON_ICNS="$ROOT_DIR/$ASSET_DIR/logo.icns"

cd "$ROOT_DIR"

check_python_version() {
  local py_cmd="$1"
  "$py_cmd" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)' >/dev/null 2>&1
}

if ! check_python_version "$PYTHON_BIN"; then
  if [[ "$AUTO_INSTALL_PYTHON" == "1" ]]; then
    if ! command -v brew >/dev/null 2>&1; then
      echo "Python 3.11+ is required, and Homebrew is not available for auto-install."
      echo "Install Python 3.11 manually, or set PYTHON_BIN to a valid 3.11 interpreter."
      exit 1
    fi

    echo "Installing Python 3.11 via Homebrew..."
    brew install python@3.11

    if command -v python3.11 >/dev/null 2>&1; then
      PYTHON_BIN="$(command -v python3.11)"
    fi
  fi
fi

if ! check_python_version "$PYTHON_BIN"; then
  echo "Python 3.11+ is required."
  echo "Use: PYTHON_BIN=python3.11 ./scripts/build_macos_app.sh --app 'Sudoku by Chinmay Mokashi'"
  echo "Or auto-install: AUTO_INSTALL_PYTHON=1 ./scripts/build_macos_app.sh --app 'Sudoku by Chinmay Mokashi'"
  exit 1
fi

"$PYTHON_BIN" -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

python -m pip install --upgrade pip
pip install pyinstaller pygame

if [[ -f "$ICON_PNG" ]]; then
  ICONSET_DIR="$ROOT_DIR/build/icon.iconset"
  rm -rf "$ICONSET_DIR"
  mkdir -p "$ICONSET_DIR"

  sips -z 16 16     "$ICON_PNG" --out "$ICONSET_DIR/icon_16x16.png" >/dev/null
  sips -z 32 32     "$ICON_PNG" --out "$ICONSET_DIR/icon_16x16@2x.png" >/dev/null
  sips -z 32 32     "$ICON_PNG" --out "$ICONSET_DIR/icon_32x32.png" >/dev/null
  sips -z 64 64     "$ICON_PNG" --out "$ICONSET_DIR/icon_32x32@2x.png" >/dev/null
  sips -z 128 128   "$ICON_PNG" --out "$ICONSET_DIR/icon_128x128.png" >/dev/null
  sips -z 256 256   "$ICON_PNG" --out "$ICONSET_DIR/icon_128x128@2x.png" >/dev/null
  sips -z 256 256   "$ICON_PNG" --out "$ICONSET_DIR/icon_256x256.png" >/dev/null
  sips -z 512 512   "$ICON_PNG" --out "$ICONSET_DIR/icon_256x256@2x.png" >/dev/null
  sips -z 512 512   "$ICON_PNG" --out "$ICONSET_DIR/icon_512x512.png" >/dev/null
  sips -z 1024 1024 "$ICON_PNG" --out "$ICONSET_DIR/icon_512x512@2x.png" >/dev/null

  iconutil -c icns "$ICONSET_DIR" -o "$ICON_ICNS"
  ICON_ARG=(--icon "$ICON_ICNS")
else
  ICON_ARG=()
fi

pyinstaller \
  --noconfirm \
  --clean \
  --windowed \
  --name "$APP_DISPLAY_NAME" \
  --target-architecture "$TARGET_ARCH" \
  --add-data "$ASSET_DIR:$ASSET_DIR" \
  "${ICON_ARG[@]}" \
  "$ENTRY_SCRIPT"

pushd dist >/dev/null
zip -r "$APP_DISPLAY_NAME-macOS.zip" "$APP_DISPLAY_NAME.app" >/dev/null
popd >/dev/null

echo "Build complete."
echo "Architecture: $TARGET_ARCH"
echo "App bundle: $ROOT_DIR/dist/$APP_DISPLAY_NAME.app"
echo "Shareable zip: $ROOT_DIR/dist/$APP_DISPLAY_NAME-macOS.zip"
