@echo off
chcp 65001 >nul
title Ghost Engineer
echo Starting Ghost Engineer...
"C:\Users\Aryan\AppData\Local\Programs\Python\Python312\python.exe" "%~dp0main.py"
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Failed to start. Check that dependencies are installed:
    echo   pip install customtkinter
    pause
)
