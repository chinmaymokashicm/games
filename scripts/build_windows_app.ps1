param(
    [switch]$Install,
    [switch]$InstallPython
)

$ErrorActionPreference = "Stop"
$AppName = "Wordle by Chinmay Mokashi"
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

    if (Get-Command py -ErrorAction SilentlyContinue) {
        $script:PythonExe = "py"
        $script:PythonPrefixArgs = @("-3.11")
        return
    }

    $script:PythonExe = "python"
    $script:PythonPrefixArgs = @()
}

function Invoke-Python {
    param(
        [string[]]$Args
    )
    & $script:PythonExe @script:PythonPrefixArgs @Args
}

function Test-Python311 {
    Invoke-Python -Args @("-c", "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)") | Out-Null
    return ($LASTEXITCODE -eq 0)
}

Set-PythonCommand
$IconPath = Join-Path $Root "assets/wordle/logo.ico"
$DistDir = Join-Path $Root "dist_windows"
$WorkDir = Join-Path $Root "build_windows"

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

Invoke-Python -Args @("-m", "pip", "install", "--upgrade", "pip")
Invoke-Python -Args @("-m", "pip", "install", "pyinstaller", "pygame")

$IconArgs = @()
if (Test-Path $IconPath) {
    $IconArgs = @("--icon", $IconPath)
}

$PyInstallerArgs = @(
    "-m", "PyInstaller",
    "--noconfirm",
    "--clean",
    "--windowed",
    "--name", $AppName,
    "--add-data", "assets/wordle;assets/wordle",
    "--distpath", $DistDir,
    "--workpath", $WorkDir
) + $IconArgs + @("wordle_ui.py")

Invoke-Python -Args $PyInstallerArgs

$AppFolder = Join-Path $DistDir $AppName
$ExePath = Join-Path $AppFolder "$AppName.exe"
$ZipPath = Join-Path $DistDir "$AppName-windows.zip"

if (Test-Path $ZipPath) {
    Remove-Item $ZipPath -Force
}

Compress-Archive -Path "$AppFolder\*" -DestinationPath $ZipPath

Write-Host "Build complete: $ExePath"
Write-Host "Shareable zip: $ZipPath"

if ($Install) {
    $InstallDir = Join-Path $env:LOCALAPPDATA ("Programs\" + $AppName)
    if (Test-Path $InstallDir) {
        Remove-Item -Recurse -Force $InstallDir
    }
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
    Copy-Item -Recurse -Force (Join-Path $AppFolder "*") $InstallDir

    $ShortcutPath = Join-Path $env:APPDATA ("Microsoft\Windows\Start Menu\Programs\" + $AppName + ".lnk")
    $Wsh = New-Object -ComObject WScript.Shell
    $Shortcut = $Wsh.CreateShortcut($ShortcutPath)
    $Shortcut.TargetPath = Join-Path $InstallDir ("$AppName.exe")
    $Shortcut.WorkingDirectory = $InstallDir
    $Shortcut.IconLocation = Join-Path $InstallDir ("$AppName.exe")
    $Shortcut.Description = $AppName
    $Shortcut.Save()

    Write-Host "Installed to: $InstallDir"
    Write-Host "Start Menu shortcut: $ShortcutPath"
}
