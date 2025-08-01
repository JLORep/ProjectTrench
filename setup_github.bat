@echo off
echo ========================================
echo   TrenchCoat Pro - GitHub CLI Setup
echo   Complete automation with all features
echo ========================================
echo.

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

echo Running GitHub CLI setup with all features...
echo.

python github_cli_setup.py

echo.
echo ========================================
echo Setup complete! Check the output above.
echo ========================================
pause