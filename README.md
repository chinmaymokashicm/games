# games
Play games

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

## Build Windows app

### Local build (Windows)

1. Run:
	- `powershell -ExecutionPolicy Bypass -File scripts/build_windows_app.ps1`
2. Outputs:
	- `dist_windows/Wordle by Chinmay Mokashi/Wordle by Chinmay Mokashi.exe`
	- `dist_windows/Wordle by Chinmay Mokashi-windows.zip`
3. Optional Start Menu install:
	- `powershell -ExecutionPolicy Bypass -File scripts/build_windows_app.ps1 -Install`

### GitHub Actions build (Windows)

1. Open Actions in GitHub.
2. Run workflow: `Build Windows App`.
3. Download artifact: `wordle-by-chinmay-mokashi-windows`.

## Build macOS app

### Local build (Mac)

1. Copy this repository to a Mac.
2. Run:
	- `chmod +x scripts/build_macos_app.sh`
	- `./scripts/build_macos_app.sh`
	- Optional architecture override: `TARGET_ARCH=universal2 ./scripts/build_macos_app.sh`
3. Output:
	- `dist/Wordle by Chinmay Mokashi.app`
	- `dist/Wordle by Chinmay Mokashi-macOS.zip`

### GitHub Actions build (macOS for Intel and Apple Silicon)

The workflow builds two architecture-specific artifacts so you can share with all modern Mac users:

- `wordle-by-chinmay-mokashi-macos-x86_64`
- `wordle-by-chinmay-mokashi-macos-arm64`

Run steps:

1. Open Actions in GitHub.
2. Run workflow: `Build macOS App`.
3. Download both artifacts and distribute the right one by CPU type.

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
