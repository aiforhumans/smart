@echo off
setlocal enabledelayedexpansion

echo ============================================
echo 🧠 AI User Learning System - Test Suite
echo ============================================
echo.

REM Check if Python is available
echo [1/7] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo 💡 Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% detected

echo.
echo [2/7] Installing dependencies...
pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Failed to install dependencies
    echo 💡 Try: pip install --upgrade pip
    pause
    exit /b 1
)
echo ✅ Dependencies installed

echo.
echo [3/7] Initializing database...
python -c "from database import db_manager; db_manager.create_tables() if not db_manager.health_check() else print('DB exists')" >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Database initialization failed
    pause
    exit /b 1
)
echo ✅ Database ready

echo.
echo [4/7] Starting Flask app in background...
start /MIN /B python app.py
timeout /t 5 /nobreak >nul
echo ✅ Flask app started

echo.
echo [5/7] Testing health endpoint...
python -c "import requests; resp = requests.get('http://localhost:5000/health', timeout=5); print('✅ Health check: OK' if resp.status_code == 200 else '❌ Health check: FAILED')" 2>nul
if errorlevel 1 (
    echo ❌ Health check failed - Flask app may not be running properly
    echo 💡 Check if port 5000 is available
)

echo.
echo [6/7] Testing webhook endpoint...
python test_webhook.py
if errorlevel 1 (
    echo ❌ Webhook test failed
    echo 💡 Check webhook authentication and endpoint availability
) else (
    echo ✅ Webhook test passed
)

echo.
echo [7/7] Running full integration demo...
python examples/webhook_demo.py
if errorlevel 1 (
    echo ❌ Integration demo failed
    echo 💡 Check that the learning system is running properly
) else (
    echo ✅ Integration demo completed successfully
)

echo.
echo ============================================
echo 🎉 Test Suite Complete!
echo ============================================
echo.
echo 🔗 Available Services:
echo    Main Dashboard: http://localhost:5000
echo    API Endpoints:  http://localhost:5000/api
echo    Webhook URLs:   http://localhost:5000/webhook
echo    Health Check:   http://localhost:5000/health
echo.
echo 🚀 Next Steps:
echo    1. Open dashboard: start http://localhost:5000
echo    2. Try Gradio chat: python examples/integrations/gradio_example.py
echo    3. Test OpenAI integration: python examples/integrations/openai_example.py
echo    4. Read documentation: docs/WEBHOOK_SDK_GUIDE.md
echo.
echo 🛑 To stop all services: taskkill /F /IM python.exe
echo ⚡ To restart quickly: python start.py
echo.

REM Ask if user wants to open dashboard
set /p OPEN_DASHBOARD="Open web dashboard now? (y/n): "
if /i "!OPEN_DASHBOARD!"=="y" (
    start http://localhost:5000
    echo 🌐 Dashboard opened in browser
)

echo.
pause