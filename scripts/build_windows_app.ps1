param(
    [switch]$Install
)

$ErrorActionPreference = "Stop"
$AppName = "Wordle by Chinmay Mokashi"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $Root

$Python = "python"
$IconPath = Join-Path $Root "assets/wordle/logo.ico"
$DistDir = Join-Path $Root "dist_windows"
$WorkDir = Join-Path $Root "build_windows"

python -m pip install --upgrade pip
pip install pyinstaller pygame

$IconArgs = @()
if (Test-Path $IconPath) {
    $IconArgs = @("--icon", $IconPath)
}

pyinstaller `
    --noconfirm `
    --clean `
    --windowed `
    --name "$AppName" `
    --add-data "assets/wordle;assets/wordle" `
    --distpath "$DistDir" `
    --workpath "$WorkDir" `
    @IconArgs `
    wordle_ui.py

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
