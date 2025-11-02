#Requires -Version 5.0

<#
.SYNOPSIS
    Build a standalone Windows executable of ElectroSim using PyInstaller.

.DESCRIPTION
    Creates a clean virtual environment, installs runtime dependencies plus
    PyInstaller, and then bundles `main.py` into `dist/ElectroSim/ElectroSim.exe`.

.NOTES
    Run from the repository root:

        powershell -ExecutionPolicy Bypass -File scripts/build_windows_exe.ps1

#>

param(
    [string]$Python = "python",
    [string]$VenvPath = ".venv-build"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Step($Message) {
    Write-Host "[build] $Message" -ForegroundColor Cyan
}

Write-Step "Creating virtual environment at $VenvPath"
if (Test-Path $VenvPath) {
    Remove-Item $VenvPath -Recurse -Force
}
& $Python -m venv $VenvPath

$venvPython = Join-Path $VenvPath "Scripts\python.exe"
$venvPip = Join-Path $VenvPath "Scripts\pip.exe"

Write-Step "Upgrading pip"
& $venvPython -m pip install --upgrade pip

Write-Step "Installing project requirements"
& $venvPip install -r requirements.txt

Write-Step "Installing PyInstaller"
& $venvPip install pyinstaller

Write-Step "Running PyInstaller"
& $venvPython -m PyInstaller `
    --noconfirm `
    --onefile `
    --windowed `
    --name ElectroSim `
    --add-data "assets;assets" `
    main.py

Write-Step "Executable created at dist/ElectroSim/ElectroSim.exe"
Write-Step "Build finished"

