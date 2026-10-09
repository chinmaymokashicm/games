param(
    [string]$AppName,
    [switch]$Install,
    [switch]$InstallPython,
    [switch]$ListApps
)

$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $Root

$PythonExe = $null
$PythonPrefixArgs = @()

function Set-PythonCommand {
    if ($env:PYTHON_BIN) {
        $script:PythonExe = $env:PYTHON_BIN
        $script:PythonPrefixArgs = @()
        return
    }

    $localVenvPython = Join-Path $Root ".venv\Scripts\python.exe"
    if (Test-Path $localVenvPython) {
        $script:PythonExe = $localVenvPython
        $script:PythonPrefixArgs = @()
        return
    }

    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCmd) {
        $script:PythonExe = $pythonCmd.Source
        $script:PythonPrefixArgs = @()
        return
    }

    $pyCmd = Get-Command py -ErrorAction SilentlyContinue
    if ($pyCmd) {
        $script:PythonExe = $pyCmd.Source
        $script:PythonPrefixArgs = @("-3.11")
        return
    }

    $script:PythonExe = "python"
    $script:PythonPrefixArgs = @()
}

function Invoke-Python {
    param(
        [string[]]$PythonArgs
    )

    if ($script:PythonPrefixArgs.Count -gt 0) {
        & $script:PythonExe @script:PythonPrefixArgs @PythonArgs
    }
    else {
        & $script:PythonExe @PythonArgs
    }
}

function Test-Python311 {
    $null = Invoke-Python -PythonArgs @("-c", "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)")
    return ($LASTEXITCODE -eq 0)
}

Set-PythonCommand

if ($ListApps) {
    $Apps = Invoke-Python -PythonArgs @("-c", "from scripts.app_registry import list_app_names; print('\\n'.join(list_app_names()))")
    if ($Apps) {
        $Apps.TrimEnd().Split([Environment]::NewLine) | ForEach-Object { Write-Host $_ }
    }
    return
}

if (-not $AppName) {
    $AppName = Invoke-Python -PythonArgs @("-c", "from scripts.app_registry import DEFAULT_APP_NAME; print(DEFAULT_APP_NAME)")
}

$AppSpecJson = Invoke-Python -PythonArgs @(
    "-c",
    "import json, sys; from scripts.app_registry import resolve_app_spec; print(json.dumps(resolve_app_spec(sys.argv[1])))",
    $AppName
)
$AppSpec = $AppSpecJson | ConvertFrom-Json

$DisplayName = $AppSpec.display_name
$EntryScript = $AppSpec.entry_script
$AssetDir = $AppSpec.asset_dir
$IconPath = Join-Path $Root (Join-Path $AssetDir "logo.ico")
$DistDir = Join-Path $Root "dist_windows"
$WorkDir = Join-Path $Root "build_windows"
$AppFolder = Join-Path $DistDir $DisplayName
$GeneratedSpecPath = Join-Path $Root ("$DisplayName.spec")

if (Test-Path $AppFolder) {
    Remove-Item -Recurse -Force $AppFolder
}
if (Test-Path $DistDir) {
    Remove-Item -Recurse -Force $DistDir
}
if (Test-Path $WorkDir) {
    Remove-Item -Recurse -Force $WorkDir
}
if (Test-Path $GeneratedSpecPath) {
    Remove-Item -Force $GeneratedSpecPath
}

if (-not (Test-Python311)) {
    if ($InstallPython) {
        if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
            throw "Python 3.11+ is required and winget is unavailable. Install Python 3.11 manually or set PYTHON_BIN."
        }

        Write-Host "Installing Python 3.11 with winget..."
        winget install --id Python.Python.3.11 -e --source winget --scope user --accept-source-agreements --accept-package-agreements

        Set-PythonCommand
    }
}

if (-not (Test-Python311)) {
    throw "Python 3.11+ is required. Set PYTHON_BIN to a Python 3.11 interpreter, or rerun with -InstallPython."
}

Invoke-Python -PythonArgs @("-m", "pip", "install", "--upgrade", "pip")
Invoke-Python -PythonArgs @("-m", "pip", "install", "pyinstaller", "pygame")

$IconArgs = @()
if (Test-Path $IconPath) {
    $IconArgs = @("--icon", $IconPath)
}

$PyInstallerArgs = @(
    "-m", "PyInstaller",
    "--noconfirm",
    "--clean",
    "--windowed",
    "--name", $DisplayName,
    "--add-data", "$AssetDir;$AssetDir",
    "--distpath", $DistDir,
    "--workpath", $WorkDir
) + $IconArgs + @($EntryScript)

Invoke-Python -PythonArgs $PyInstallerArgs

$AppFolder = Join-Path $DistDir $DisplayName
$ExePath = Join-Path $AppFolder "$DisplayName.exe"
$ZipPath = Join-Path $DistDir "$DisplayName-windows.zip"
$StageDir = Join-Path $DistDir "$DisplayName-stage"

if (Test-Path $ZipPath) {
    Remove-Item $ZipPath -Force
}

if (Test-Path $StageDir) {
    Remove-Item -Recurse -Force $StageDir
}

Copy-Item -Recurse -Force $AppFolder $StageDir
Compress-Archive -Path (Join-Path $StageDir "*") -DestinationPath $ZipPath -Force
Remove-Item -Recurse -Force $StageDir

Write-Host "Build complete: $ExePath"
Write-Host "Shareable zip: $ZipPath"

if ($Install) {
    $InstallDir = Join-Path $env:LOCALAPPDATA ("Programs\" + $DisplayName)
    if (Test-Path $InstallDir) {
        Remove-Item -Recurse -Force $InstallDir
    }
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
    Copy-Item -Recurse -Force (Join-Path $AppFolder "*") $InstallDir

    $ShortcutPath = Join-Path $env:APPDATA ("Microsoft\Windows\Start Menu\Programs\" + $DisplayName + ".lnk")
    $Wsh = New-Object -ComObject WScript.Shell
    $Shortcut = $Wsh.CreateShortcut($ShortcutPath)
    $Shortcut.TargetPath = Join-Path $InstallDir ("$DisplayName.exe")
    $Shortcut.WorkingDirectory = $InstallDir
    $Shortcut.IconLocation = Join-Path $InstallDir ("$DisplayName.exe")
    $Shortcut.Description = $DisplayName
    $Shortcut.Save()

    Write-Host "Installed to: $InstallDir"
    Write-Host "Start Menu shortcut: $ShortcutPath"
}
