@echo off
echo Starting Automation Project...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
python -m pip install -r requirements.txt

REM Create directories
if not exist "logs" mkdir logs
if not exist "screenshots" mkdir screenshots
if not exist "results" mkdir results

REM Run automation
echo.
echo Starting automation...
python src/main_automation.py

echo.
echo Automation completed. Check the results directory for output.
pause
