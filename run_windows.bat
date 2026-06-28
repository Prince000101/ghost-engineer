@echo off
chcp 65001 >nul
title Ghost Engineer
echo Starting Ghost Engineer...

:: Try python, then py launcher, then fallback
python "%~dp0main.py" 2>nul
if %errorlevel% neq 0 (
    py "%~dp0main.py" 2>nul
)
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Python not found. Install Python 3.10+ from:
    echo   https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation.
    echo Then install the dependency:
    echo   pip install customtkinter
    pause
    exit /b 1
)
