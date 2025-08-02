@echo off
echo Setting up Git Hygiene Schedule...

REM Create scheduled task for weekly git hygiene
schtasks /create /tn "TrenchCoatGitHygiene" /tr "python %~dp0git_hygiene_manager.py" /sc weekly /d SUN /st 02:00 /f

REM Also create a startup task to check on boot
schtasks /create /tn "TrenchCoatGitCheck" /tr "python %~dp0git_hygiene_manager.py --check-only" /sc onstart /f

echo.
echo ✅ Git hygiene scheduled!
echo.
echo 📅 Schedule:
echo    - Full hygiene: Every Sunday at 2:00 AM
echo    - Health check: On system startup
echo.
echo To run manually:
echo    python git_hygiene_manager.py
echo.
echo To force immediate cleanup:
echo    python git_hygiene_manager.py --force
echo.
pause