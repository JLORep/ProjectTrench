@echo off
echo Starting TrenchCoat Pro - Local Development Environment
echo =====================================================

REM Activate virtual environment
call venv\Scripts\activate

REM Set environment variables for development
set ENVIRONMENT=development
set LIVE_TRADING_ENABLED=False
set DEBUG=True

echo.
echo Virtual environment activated.
echo Starting application in DEVELOPMENT mode...
echo.

REM Start the main application
python app.py

pause