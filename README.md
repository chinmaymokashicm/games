# games
Play games

## Python version requirement

Use Python `3.11` for local builds and runtime.

- The local build scripts now enforce `>=3.11`.
- GitHub Actions workflows also verify Python `3.11` explicitly.
- The apps now show a friendly startup error if run with an older Python interpreter.

## Push this repo to GitHub

1. Create a new empty repository on GitHub.
2. In this project root, run:
	- `git remote add origin <your-github-repo-url>`
	- `git branch -M main`
	- `git add .`
	- `git commit -m "Add cross-platform build scripts and workflows"`
	- `git push -u origin main`

If `origin` already exists, update it with:

- `git remote set-url origin <your-github-repo-url>`

## Dynamic app registry

The project now uses a shared app registry in `scripts/app_registry.py`.
This lets us define a human-friendly game name once and reuse the same Windows/macOS build flow for any game.

Example entries:

- `Wordle by Chinmay Mokashi` -> `wordle_ui.py`
- `Sudoku by Chinmay Mokashi` -> `sudoku.py`

To add a new game, update `APP_REGISTRY` in `scripts/app_registry.py` with:

- the display name
- the entry script
- the asset folder for the game logo and icons

## Build a specific app

### Local build (Windows)

1. List apps:
	- `powershell -ExecutionPolicy Bypass -File scripts/build_windows_app.ps1 -ListApps`
2. Build a specific app:
	- `powershell -ExecutionPolicy Bypass -File scripts/build_windows_app.ps1 -AppName "Sudoku by Chinmay Mokashi"`
	- `powershell -ExecutionPolicy Bypass -File scripts/build_windows_app.ps1 -AppName "Wordle by Chinmay Mokashi"`
	- Optional explicit interpreter: `$env:PYTHON_BIN='C:\Path\To\Python311\python.exe'; powershell -ExecutionPolicy Bypass -File scripts/build_windows_app.ps1 -AppName "Sudoku by Chinmay Mokashi"`
	- Optional auto-install Python 3.11 (winget): `powershell -ExecutionPolicy Bypass -File scripts/build_windows_app.ps1 -AppName "Sudoku by Chinmay Mokashi" -InstallPython`
3. Outputs:
	- `dist_windows/Sudoku by Chinmay Mokashi/Sudoku by Chinmay Mokashi.exe`
	- `dist_windows/Sudoku by Chinmay Mokashi-windows.zip`
4. Optional Start Menu install:
	- `powershell -ExecutionPolicy Bypass -File scripts/build_windows_app.ps1 -AppName "Sudoku by Chinmay Mokashi" -Install`

### Local build (macOS)

1. List apps:
	- `./scripts/build_macos_app.sh --list-apps`
2. Build a specific app:
	- `APP_NAME="Sudoku by Chinmay Mokashi" ./scripts/build_macos_app.sh --app "Sudoku by Chinmay Mokashi"`
	- `APP_NAME="Wordle by Chinmay Mokashi" ./scripts/build_macos_app.sh --app "Wordle by Chinmay Mokashi"`
	- Optional explicit interpreter: `PYTHON_BIN=python3.11 ./scripts/build_macos_app.sh --app "Sudoku by Chinmay Mokashi"`
	- Optional auto-install Python 3.11 (Homebrew): `AUTO_INSTALL_PYTHON=1 ./scripts/build_macos_app.sh --app "Sudoku by Chinmay Mokashi"`
	- Optional architecture override: `TARGET_ARCH=universal2 ./scripts/build_macos_app.sh --app "Sudoku by Chinmay Mokashi"`
3. Output:
	- `dist/Sudoku by Chinmay Mokashi.app`
	- `dist/Sudoku by Chinmay Mokashi-macOS.zip`

## GitHub Actions builds

### Windows

1. Open Actions in GitHub.
2. Run workflow: `Build Windows App`.
3. Download the built artifact for the named app.

### macOS

The workflow builds architecture-specific artifacts for each app so you can share with modern Mac users.

- Intel build: `*-macos-x86_64`
- Apple Silicon build: `*-macos-arm64`

Run steps:

1. Open Actions in GitHub.
2. Run workflow: `Build macOS App`.
3. Download the correct artifact by CPU type.

## macOS signing and notarization (recommended)

Signed + notarized apps reduce Gatekeeper warnings and are best for sharing broadly.

### Required secrets in GitHub repository settings

Add these under Settings -> Secrets and variables -> Actions:

1. `MACOS_CERTIFICATE_P12_BASE64`
2. `MACOS_CERTIFICATE_PASSWORD`
3. `APPLE_DEVELOPER_ID_APPLICATION`
4. `APPLE_ID`
5. `APPLE_APP_SPECIFIC_PASSWORD`
6. `APPLE_TEAM_ID`

Secret details:

1. `MACOS_CERTIFICATE_P12_BASE64`: Base64-encoded Developer ID Application certificate file.
2. `MACOS_CERTIFICATE_PASSWORD`: Password used when exporting the `.p12` file.
3. `APPLE_DEVELOPER_ID_APPLICATION`: Signing identity text. Example: `Developer ID Application: Your Name (TEAMID)`.
4. `APPLE_ID`: Apple ID email used for notarization.
5. `APPLE_APP_SPECIFIC_PASSWORD`: App-specific password created at appleid.apple.com.
6. `APPLE_TEAM_ID`: Apple Developer Team ID.

If any secret is missing, the macOS workflow still completes and uploads unsigned artifacts.

## Notes for end users on macOS

1. Unsigned app: may show Gatekeeper warning. Use Control-click -> Open.
2. Signed + notarized app: expected to open normally for most users.
