@echo off
echo =========================================
echo   TrenchCoat Pro - Lightweight Deploy
echo   CPU-friendly deployment (no heavy tools)
echo =========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found
    echo Please install Python from python.org
    pause
    exit /b 1
)

echo Python found - running lightweight setup...
echo.

REM Run the lightweight setup
python lightweight_setup.py

echo.
echo =========================================
echo Alternative Manual Steps:
echo.
echo 1. Create GitHub Personal Access Token:
echo    https://github.com/settings/tokens
echo.
echo 2. Push to GitHub:
echo    git push -u origin master
echo    Username: JLORep
echo    Password: [your token]
echo.
echo 3. Deploy to Streamlit Cloud:
echo    https://share.streamlit.io
echo    Repository: JLORep/ProjectTrench
echo    Main file: streamlit_app.py
echo.
echo 4. Test locally first:
echo    streamlit run ultra_premium_dashboard.py
echo =========================================
pause