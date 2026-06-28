#Requires -Version 5.1

<#
.SYNOPSIS
    Ghost Engineer - Windows one-click install
.DESCRIPTION
    Checks prerequisites, installs dependencies, creates a desktop shortcut/app.
#>

$Host.UI.RawUI.WindowTitle = "Ghost Engineer - Install"

function Write-Step($text)  { Write-Host "`n>>> $text" -ForegroundColor Cyan }
function Write-Ok($text)    { Write-Host "  [OK] $text" -ForegroundColor Green }
function Write-Warn($text)  { Write-Host "  [!] $text" -ForegroundColor Yellow }
function Write-Err($text)   { Write-Host "  [X] $text" -ForegroundColor Red }

$REPO_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$GHOST_DATA = Join-Path $env:USERPROFILE ".ghost-engineer"

# ── Header ──
Write-Host @"

  ╔══════════════════════════════════════╗
  ║        Ghost Engineer - Install      ║
  ╚══════════════════════════════════════╝

"@ -ForegroundColor Magenta

# ── 1. Check Python ──
Write-Step "Checking Python..."
$python = $null
foreach ($cmd in @("python", "py")) {
    try {
        $ver = & $cmd --version 2>&1
        if ($LASTEXITCODE -eq 0 -and $ver -match "(\d+)\.(\d+)") {
            $major = [int]$Matches[1]
            $minor = [int]$Matches[2]
            if ($major -ge 3 -and $minor -ge 10) {
                $python = $cmd
                Write-Ok "$ver"
                break
            }
        }
    } catch {}
}
if (-not $python) {
    Write-Err "Python 3.10+ is required but not found."
    Write-Host "  Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "  Make sure to check 'Add Python to PATH' during installation." -ForegroundColor Yellow
    Read-Host "`nPress Enter after installing Python, or Ctrl+C to quit"
}

# ── 2. Check Git ──
Write-Step "Checking Git..."
try {
    $gitVer = & git --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Ok "$gitVer"
    } else { throw }
} catch {
    Write-Err "Git is not installed."
    Write-Host "  Download from: https://git-scm.com/download/win" -ForegroundColor Yellow
    Read-Host "`nPress Enter after installing Git, or Ctrl+C to quit"
}

# ── 3. Install customtkinter ──
Write-Step "Installing Python dependencies..."
& $python -m pip install --upgrade customtkinter 2>&1 | ForEach-Object {
    if ($_ -match "^(Requirement already satisfied|Successfully installed|Collecting)") {
        Write-Ok $_
    }
}
if ($LASTEXITCODE -ne 0) {
    Write-Err "Failed to install dependencies."
    Write-Host "  Try manually: pip install customtkinter" -ForegroundColor Yellow
    exit 1
}
Write-Ok "customtkinter installed"

# ── 4. Create desktop shortcut ──
Write-Step "Creating desktop shortcut..."
$desktop = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktop "Ghost Engineer.lnk"

$wshell = New-Object -ComObject WScript.Shell
$shortcut = $wshell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = Join-Path $REPO_DIR "run_windows.bat"
$shortcut.WorkingDirectory = $REPO_DIR
$shortcut.Description = "Ghost Engineer - Generate realistic git commit histories"
$shortcut.IconLocation = "$env:SystemRoot\System32\shell32.dll,21"
$shortcut.Save()

Write-Ok "Shortcut created on desktop: Ghost Engineer.lnk"

# ── 5. Create data directory ──
Write-Step "Setting up data directory..."
if (-not (Test-Path $GHOST_DATA)) {
    New-Item -ItemType Directory -Path $GHOST_DATA -Force | Out-Null
    Write-Ok "Created $GHOST_DATA"
} else {
    Write-Ok "Already exists: $GHOST_DATA"
}

# ── 6. Offer .exe build ──
Write-Step "Optional: Build standalone .exe (no Python needed to run)"
Write-Host "  This creates a single .exe file using PyInstaller."
$buildChoice = Read-Host "  Build .exe now? (y/N)"
if ($buildChoice -eq "y" -or $buildChoice -eq "Y") {
    Write-Host "  Installing PyInstaller..." -ForegroundColor Yellow
    & $python -m pip install pyinstaller 2>&1 | Out-Null
    Write-Host "  Building GhostEngineer.exe (this may take a minute)..." -ForegroundColor Yellow
    & $python -m PyInstaller --onefile --windowed --name "GhostEngineer" `
        --add-data "ui;ui" `
        --hidden-import "customtkinter" `
        --hidden-import "tkinter" `
        --hidden-import "tkinter.filedialog" `
        --hidden-import "ui.dashboard" `
        --hidden-import "ui.settings" `
        --hidden-import "ui.dialogs" `
        (Join-Path $REPO_DIR "main.py") 2>&1

    if ($LASTEXITCODE -eq 0) {
        $exeDest = Join-Path $desktop "GhostEngineer.exe"
        Copy-Item (Join-Path $REPO_DIR "dist\GhostEngineer.exe") $exeDest -Force
        Write-Ok ".exe built and copied to desktop: GhostEngineer.exe"

        # Also update shortcut to point to .exe
        $shortcut2 = $wshell.CreateShortcut($shortcutPath)
        $shortcut2.TargetPath = $exeDest
        $shortcut2.WorkingDirectory = Split-Path $exeDest
        $shortcut2.Description = "Ghost Engineer"
        $shortcut2.Save()
        Write-Ok "Desktop shortcut now points to standalone .exe"
    } else {
        Write-Warn ".exe build failed. You can still use run_windows.bat"
    }
}

# ── Done ──
Write-Host @"

  ╔══════════════════════════════════════╗
  ║        Installation Complete!        ║
  ╚══════════════════════════════════════╝

"@ -ForegroundColor Green
Write-Host "  Double-click 'Ghost Engineer' on your desktop to start." -ForegroundColor White
Write-Host "`n  First time? Open Settings and:" -ForegroundColor Gray
Write-Host "    1. Enter your GitHub username & email" -ForegroundColor Gray
Write-Host "    2. Generate or paste an SSH key / GitHub token" -ForegroundColor Gray
Write-Host "    3. Add a repository to ghost" -ForegroundColor Gray

Read-Host "`nPress Enter to exit"
