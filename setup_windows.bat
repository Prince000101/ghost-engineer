@echo off
chcp 65001 >nul
title Ghost Engineer — Windows Setup
echo ============================================
echo   Ghost Engineer — Windows Setup
echo ============================================
echo.

REM --- Check Python ---
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed.
    echo Download it from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)
echo [OK] Python found

REM --- Check Git ---
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Git is not installed.
    echo Download from: https://git-scm.com/download/win
    pause
    exit /b 1
)
echo [OK] Git found

REM --- Install dependencies ---
echo.
echo Installing Python dependencies...
pip install customtkinter pyinstaller
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)
echo [OK] Dependencies installed

REM --- Build standalone executable ---
echo.
echo Building standalone executable (this may take a minute)...
pyinstaller --onefile --windowed --name "GhostEngineer.exe" ^
    --add-data "ui;ui" ^
    --hidden-import customtkinter ^
    --hidden-import tkinter ^
    --hidden-import tkinter.filedialog ^
    --hidden-import ui.dashboard ^
    --hidden-import ui.settings ^
    --hidden-import ui.dialogs main.py
if %errorlevel% neq 0 (
    echo [ERROR] Build failed.
    pause
    exit /b 1
)
echo [OK] Executable built

REM --- Copy to desktop ---
echo.
set DESKTOP=%USERPROFILE%\Desktop
copy /Y "dist\GhostEngineer.exe" "%DESKTOP%\GhostEngineer.exe" >nul
echo [OK] Copied to desktop: %DESKTOP%\GhostEngineer.exe

REM --- Pre-populate data folder ---
if exist "data\" (
    mkdir "%USERPROFILE%\.ghost-engineer" >nul 2>&1
    xcopy /E /I /Y "data\*" "%USERPROFILE%\.ghost-engineer\" >nul
    echo [OK] Data copied to %USERPROFILE%\.ghost-engineer\
)

echo.
echo ============================================
echo   Setup complete!
echo.
echo   Double-click GhostEngineer.exe on your
echo   desktop to run the app.
echo ============================================
pause
