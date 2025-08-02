@echo off
REM Permanent Unicode fix for Windows development environment
echo Applying permanent Unicode fixes...

REM Set console code page to UTF-8
chcp 65001 >nul

REM Set environment variables for UTF-8
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

REM Configure git for UTF-8
git config --global core.quotepath false
git config --global i18n.commitencoding utf-8
git config --global i18n.logoutputencoding utf-8
git config --global core.autocrlf true

REM Add environment variables to Windows registry for persistence
reg add "HKCU\Environment" /v PYTHONIOENCODING /t REG_SZ /d "utf-8" /f >nul 2>&1
reg add "HKCU\Environment" /v PYTHONUTF8 /t REG_SZ /d "1" /f >nul 2>&1

echo ✅ Unicode fixes applied permanently
echo ℹ️  Please restart your terminal for environment variables to take effect