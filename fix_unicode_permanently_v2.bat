@echo off
echo ========================================
echo PERMANENT UNICODE FIX FOR TRENCHCOAT PRO
echo ========================================
echo.

REM Set system-wide UTF-8 encoding
echo Setting system-wide UTF-8 encoding...

REM Set Windows code page to UTF-8
chcp 65001 >nul 2>&1

REM Set Python environment variables
setx PYTHONIOENCODING "utf-8" >nul 2>&1
setx PYTHONUTF8 "1" >nul 2>&1

REM Set Git to use UTF-8
git config --global core.autocrlf true
git config --global i18n.commitencoding utf-8
git config --global i18n.logoutputencoding utf-8

REM Create a Python script to fix subprocess encoding
echo Creating Python subprocess fix...
(
echo import os
echo import sys
echo # Force UTF-8 encoding for all subprocesses
echo os.environ['PYTHONIOENCODING'] = 'utf-8'
echo os.environ['PYTHONUTF8'] = '1'
echo # For Windows console
echo if sys.platform == 'win32':
echo     import subprocess
echo     subprocess._USE_VENV = False
echo     os.system('chcp 65001 ^>nul')
) > C:\Trench\unicode_fix.py

REM Update pre-commit hook to use UTF-8
echo Updating pre-commit hook...
(
echo #!/usr/bin/env python3
echo # -*- coding: utf-8 -*-
echo """
echo Pre-commit hook for TrenchCoat Pro
echo Validates Python syntax before allowing commits
echo """
echo.
echo import sys
echo import subprocess
echo import os
echo import locale
echo.
echo # Force UTF-8 encoding
echo os.environ['PYTHONIOENCODING'] = 'utf-8'
echo os.environ['PYTHONUTF8'] = '1'
echo.
echo # Add project root to path
echo sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
echo.
echo print("🔍 Running pre-commit validation...")
echo.
echo # Run validation with UTF-8 encoding
echo env = os.environ.copy()
echo env['PYTHONIOENCODING'] = 'utf-8'
echo env['PYTHONUTF8'] = '1'
echo.
echo result = subprocess.run(
echo     [sys.executable, '-W', 'ignore', 'validate_code.py'],
echo     capture_output=True,
echo     text=True,
echo     encoding='utf-8',
echo     errors='replace',
echo     env=env
echo )
echo.
echo if result.returncode != 0:
echo     print("\n❌ Pre-commit validation failed!")
echo     print(result.stdout)
echo     print("Errors:", result.stderr)
echo     print("\n💡 Fix the errors above before committing.")
echo     sys.exit(1)
echo.
echo print("✅ Pre-commit validation passed!")
echo sys.exit(0)
) > C:\Trench\.git\hooks\pre-commit

REM Update post-commit hook
echo Updating post-commit hook...
powershell -Command "(Get-Content 'C:\Trench\.git\hooks\post-commit') -replace 'encoding=.*', 'encoding=\"utf-8\", errors=\"replace\"' | Set-Content 'C:\Trench\.git\hooks\post-commit'"

REM Create .env file with UTF-8 settings
echo Creating .env file with UTF-8 settings...
(
echo # UTF-8 Encoding Settings
echo PYTHONIOENCODING=utf-8
echo PYTHONUTF8=1
echo LANG=en_US.UTF-8
echo LC_ALL=en_US.UTF-8
) > C:\Trench\.env

REM Update validate_code.py to handle UTF-8
echo Updating validate_code.py...
powershell -Command "(Get-Content 'C:\Trench\validate_code.py') | ForEach-Object { if ($_ -match '^import') { \"# -*- coding: utf-8 -*-`n\" + $_ } else { $_ } } | Set-Content 'C:\Trench\validate_code.py'"

echo.
echo ========================================
echo UNICODE FIX COMPLETE!
echo ========================================
echo.
echo Changes made:
echo ✓ Windows code page set to UTF-8 (65001)
echo ✓ Python environment variables set
echo ✓ Git configured for UTF-8
echo ✓ Pre-commit hook updated
echo ✓ Post-commit hook updated
echo ✓ .env file created
echo ✓ validate_code.py updated
echo.
echo IMPORTANT: Close and reopen your terminal for changes to take effect!
echo.
pause