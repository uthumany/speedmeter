#Requires -Version 5.1
#=============================================================================
# SpeedMeter — Installation Script for Windows (PowerShell)
#=============================================================================
# This script installs SpeedMeter and all dependencies on Windows.
# Usage:
#   powershell -ExecutionPolicy Bypass -File install.ps1
#   iex "& { $(irm https://raw.githubusercontent.com/fameux/speedmeter/main/install.ps1) }"
#=============================================================================

param(
    [string]$InstallDir = "$env:USERPROFILE\.speedmeter",
    [string]$PythonPath = "python",
    [switch]$AddToPath = $false,
    [switch]$Silent = $false
)

$ProjectName = "speedmeter"
$VenvDir = "$InstallDir\venv"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition

# ---- Colors via Write-Host ----
function Write-ColorHost($Text, $Color = "White") {
    if (-not $Silent) { Write-Host $Text -ForegroundColor $Color }
}

# ---- Banner ----
Write-ColorHost ""
Write-ColorHost "  ╔═══════════════════════════════════════════╗" "Cyan"
Write-ColorHost "  ║     SpeedMeter — Internet Speed Meter     ║" "Cyan"
Write-ColorHost "  ║     Interactive Terminal TUI Tool         ║" "Cyan"
Write-ColorHost "  ╚═══════════════════════════════════════════╝" "Cyan"
Write-ColorHost ""

# ---- Check Python ----
Write-ColorHost "Checking prerequisites..." "Bold"
try {
    $pyVersion = & $PythonPath --version 2>&1
    Write-ColorHost "  Python: $pyVersion" "Green"
} catch {
    Write-ColorHost "  Error: Python not found. Please install Python 3.10+." "Red"
    Write-ColorHost "  Download: https://www.python.org/downloads/windows/" "Yellow"
    Write-ColorHost "  Make sure to check 'Add Python to PATH' during installation." "Yellow"
    exit 1
}

# Check Python version
if ($pyVersion -match "(\d+)\.(\d+)") {
    $major = [int]$Matches[1]
    $minor = [int]$Matches[2]
    if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 10)) {
        Write-ColorHost "  Warning: Python 3.10+ recommended (found $major.$minor)" "Yellow"
    }
}

# ---- Create virtual environment ----
Write-ColorHost "Creating virtual environment..." "Bold"
if (-not (Test-Path $InstallDir)) {
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
}

if (-not (Test-Path "$VenvDir\Scripts\python.exe")) {
    & $PythonPath -m venv $VenvDir
    Write-ColorHost "  Virtual environment created at $VenvDir" "Green"
} else {
    Write-ColorHost "  Virtual environment already exists" "Yellow"
}

$PythonExe = "$VenvDir\Scripts\python.exe"
$PipExe = "$VenvDir\Scripts\pip.exe"

# ---- Upgrade pip ----
Write-ColorHost "Upgrading pip..." "Bold"
& $PipExe install --upgrade pip setuptools wheel 2>&1 | Out-Null
Write-ColorHost "  pip upgraded" "Green"

# ---- Install dependencies ----
Write-ColorHost "Installing dependencies..." "Bold"
$dependencies = @(
    "speedtest-cli>=2.1.3"
    "rich>=13.7.0"
    "textual>=0.52.0"
    "prompt_toolkit>=3.0.43"
    "psutil>=5.9.8"
    "colorama>=0.4.6"
    "platformdirs>=4.2.0"
    "requests>=2.31.0"
)

foreach ($dep in $dependencies) {
    Write-ColorHost "  Installing $dep ... " "None" -NoNewline
    $result = & $PipExe install $dep 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-ColorHost "OK" "Green"
    } else {
        Write-ColorHost "FAILED" "Red"
        Write-ColorHost "  $result" "Red"
    }
}

# ---- Install SpeedMeter package ----
Write-ColorHost "Installing SpeedMeter..." "Bold"
if (Test-Path "$ScriptDir\setup.py") {
    & $PipExe install -e "$ScriptDir" 2>&1 | Out-Null
    Write-ColorHost "  SpeedMeter installed from local source" "Green"
} else {
    # Try installing from current directory
    $currentDir = Get-Location
    & $PipExe install -e "$currentDir" 2>&1 | Out-Null
    Write-ColorHost "  SpeedMeter installed from $currentDir" "Green"
}

# ---- Create launcher script ----
Write-ColorHost "Creating launcher scripts..." "Bold"

# PowerShell launcher
$psLauncher = @"
# SpeedMeter PowerShell Launcher
`$VenvDir = "$VenvDir"
`$PythonExe = Join-Path `$VenvDir "Scripts\python.exe"
if (-not (Test-Path `$PythonExe)) {
    Write-Host "Error: Virtual environment not found at `$VenvDir" -ForegroundColor Red
    Write-Host "Please run install.ps1 first." -ForegroundColor Red
    exit 1
}
& `$PythonExe -m speedmeter `@args
"@
$psLauncherPath = "$InstallDir\speedmeter.ps1"
Set-Content -Path $psLauncherPath -Value $psLauncher

# Batch launcher (for cmd.exe)
$batLauncher = @"
@echo off
"%~dp0venv\Scripts\python.exe" -m speedmeter %*
"@
$batLauncherPath = "$InstallDir\speedmeter.bat"
Set-Content -Path $batLauncherPath -Value $batLauncher

Write-ColorHost "  Launcher: $psLauncherPath" "Green"
Write-ColorHost "  Launcher: $batLauncherPath" "Green"

# ---- Add to PATH (optional) ----
if ($AddToPath) {
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
    if ($currentPath -notlike "*$InstallDir*") {
        [Environment]::SetEnvironmentVariable("Path", "$currentPath;$InstallDir", "User")
        Write-ColorHost "  Added $InstallDir to user PATH" "Green"
    } else {
        Write-ColorHost "  $InstallDir already in PATH" "Yellow"
    }
}

# ---- Summary ----
Write-ColorHost ""
Write-ColorHost "Installation Complete!" "Bold" "Green"
Write-ColorHost ""
Write-ColorHost "  Run:" "Bold"
Write-ColorHost "    $InstallDir\speedmeter.bat" "Cyan"
Write-ColorHost "    speedmeter (if added to PATH)" "Cyan"
Write-ColorHost ""
Write-ColorHost "  Quick test:" "Bold"
Write-ColorHost "    $InstallDir\speedmeter.bat --quick" "Cyan"
Write-ColorHost ""
Write-ColorHost "  To add to PATH manually:" "Yellow"
Write-ColorHost "    [Environment]::SetEnvironmentVariable('Path'," "Yellow"
Write-ColorHost "      [Environment]::GetEnvironmentVariable('Path','User') + ';$InstallDir'," "Yellow"
Write-ColorHost "      'User')" "Yellow"
Write-ColorHost ""
Write-ColorHost "  SpeedMeter v1.0.0 — Happy speed testing!" "Cyan"
Write-ColorHost ""

# ---- Uninstall Instructions ----
Write-ColorHost "Uninstall Instructions:" "Yellow"
Write-ColorHost "  To remove SpeedMeter, run:" "Yellow"
Write-ColorHost "    Remove-Item -Recurse -Force $InstallDir" "Cyan"
Write-ColorHost "  Or run the uninstall script:" "Yellow"
Write-ColorHost "    & `"$InstallDir\uninstall.ps1`"" "Cyan"
Write-ColorHost ""