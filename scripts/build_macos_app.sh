#!/usr/bin/env bash
set -euo pipefail

APP_NAME="Wordle by Chinmay Mokashi"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_DIR="$ROOT_DIR/.venv-mac"
ICON_PNG="$ROOT_DIR/assets/wordle/logo.png"
ICON_ICNS="$ROOT_DIR/assets/wordle/logo.icns"
TARGET_ARCH="${TARGET_ARCH:-$(uname -m)}"

if [[ "$TARGET_ARCH" != "x86_64" && "$TARGET_ARCH" != "arm64" && "$TARGET_ARCH" != "universal2" ]]; then
  echo "Unsupported TARGET_ARCH: $TARGET_ARCH"
  echo "Use one of: x86_64, arm64, universal2"
  exit 1
fi

cd "$ROOT_DIR"

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
  --name "$APP_NAME" \
  --target-architecture "$TARGET_ARCH" \
  --add-data "assets/wordle:assets/wordle" \
  "${ICON_ARG[@]}" \
  wordle_ui.py

pushd dist >/dev/null
zip -r "$APP_NAME-macOS.zip" "$APP_NAME.app" >/dev/null
popd >/dev/null

echo "Build complete."
echo "Architecture: $TARGET_ARCH"
echo "App bundle: $ROOT_DIR/dist/$APP_NAME.app"
echo "Shareable zip: $ROOT_DIR/dist/$APP_NAME-macOS.zip"
