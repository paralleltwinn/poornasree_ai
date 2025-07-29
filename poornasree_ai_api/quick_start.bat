@echo off
echo ================================================================
echo 🚀 POORNASREE AI - QUICK STARTUP
echo ================================================================
echo This script will run all tests and start the API server
echo.

REM Change to the script directory
cd /d "%~dp0"

REM Run the comprehensive startup script
echo Running comprehensive startup script...
python startup.py

REM Pause if there's an error
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Startup failed. Press any key to exit...
    pause >nul
) else (
    echo.
    echo ✅ Startup completed successfully!
)
