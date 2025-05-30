@echo off
echo 🚀 Starting Enhanced Selenium Automation System with LangChain...
echo.

echo 📦 Installing Python dependencies...
cd worker
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install Python dependencies
    pause
    exit /b 1
)

echo 📦 Installing Node.js dependencies...
cd ..\frontend
npm install
if errorlevel 1 (
    echo ❌ Failed to install Node.js dependencies
    pause
    exit /b 1
)

echo.
echo 🎯 Starting services...
echo.

echo 🐍 Starting Python Worker (Enhanced LangChain Agent)...
start "Worker" cmd /k "cd /d %~dp0worker && python main.py"

echo ⏳ Waiting for worker to start...
timeout /t 5 /nobreak >nul

echo 🌐 Starting Next.js Frontend...
start "Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ✅ System Started!
echo.
echo 📱 Frontend: http://localhost:3000
echo 🔧 Worker API: http://localhost:8000
echo.
echo 🎯 Features Available:
echo   - Enhanced Automation with LangChain AI
echo   - Dynamic Page Analysis
echo   - Complete Project Generation
echo   - StackBlitz-like File Explorer
echo   - Real-time Code Viewer
echo.
echo Press any key to exit...
pause >nul 