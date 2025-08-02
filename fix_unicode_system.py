#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Permanent Unicode Fix for TrenchCoat Pro
Fixes all encoding issues in Git hooks and Python scripts
"""

import os
import sys
import subprocess
import locale

def fix_git_hooks():
    """Fix encoding in Git hooks"""
    print("🔧 Fixing Git hooks...")
    
    hooks_dir = os.path.join(".git", "hooks")
    
    # Fix pre-commit hook
    pre_commit_path = os.path.join(hooks_dir, "pre-commit")
    if os.path.exists(pre_commit_path):
        with open(pre_commit_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        # Add UTF-8 encoding fixes
        if 'PYTHONIOENCODING' not in content:
            lines = content.split('\n')
            import_index = next((i for i, line in enumerate(lines) if 'import' in line), 0)
            
            encoding_fix = """
# Force UTF-8 encoding
import locale
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'
if sys.platform == 'win32':
    # Set Windows console to UTF-8
    import ctypes
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleCP(65001)
    kernel32.SetConsoleOutputCP(65001)
"""
            lines.insert(import_index + 4, encoding_fix)
            
            # Fix subprocess calls
            for i, line in enumerate(lines):
                if 'subprocess.run' in line and 'encoding=' not in line:
                    lines[i] = line.replace('capture_output=True, text=True', 
                                          'capture_output=True, text=True, encoding="utf-8", errors="replace"')
            
            with open(pre_commit_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
        
        print("✅ Pre-commit hook fixed")
    
    # Fix post-commit hook
    post_commit_path = os.path.join(hooks_dir, "post-commit")
    if os.path.exists(post_commit_path):
        with open(post_commit_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        # Add encoding to subprocess calls
        content = content.replace('capture_output=True, text=True', 
                                'capture_output=True, text=True, encoding="utf-8", errors="replace"')
        
        with open(post_commit_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Post-commit hook fixed")

def fix_validate_code():
    """Fix encoding in validate_code.py"""
    print("🔧 Fixing validate_code.py...")
    
    if os.path.exists('validate_code.py'):
        with open('validate_code.py', 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        # Add UTF-8 header if not present
        if '# -*- coding: utf-8 -*-' not in content:
            content = '# -*- coding: utf-8 -*-\n' + content
        
        # Fix subprocess calls
        content = content.replace('capture_output=True, text=True', 
                                'capture_output=True, text=True, encoding="utf-8", errors="replace"')
        
        with open('validate_code.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ validate_code.py fixed")

def set_environment_variables():
    """Set system environment variables for UTF-8"""
    print("🔧 Setting environment variables...")
    
    try:
        # Windows specific
        if sys.platform == 'win32':
            subprocess.run(['setx', 'PYTHONIOENCODING', 'utf-8'], capture_output=True)
            subprocess.run(['setx', 'PYTHONUTF8', '1'], capture_output=True)
            subprocess.run(['chcp', '65001'], shell=True, capture_output=True)
        
        # Git configuration
        subprocess.run(['git', 'config', '--global', 'core.autocrlf', 'true'], capture_output=True)
        subprocess.run(['git', 'config', '--global', 'i18n.commitencoding', 'utf-8'], capture_output=True)
        subprocess.run(['git', 'config', '--global', 'i18n.logoutputencoding', 'utf-8'], capture_output=True)
        
        print("✅ Environment variables set")
    except Exception as e:
        print(f"⚠️ Warning setting environment variables: {e}")

def create_env_file():
    """Create .env file with UTF-8 settings"""
    print("🔧 Creating .env file...")
    
    env_content = """# UTF-8 Encoding Settings
PYTHONIOENCODING=utf-8
PYTHONUTF8=1
LANG=en_US.UTF-8
LC_ALL=en_US.UTF-8
"""
    
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("✅ .env file created")

def main():
    print("=" * 50)
    print("PERMANENT UNICODE FIX FOR TRENCHCOAT PRO")
    print("=" * 50)
    print()
    
    # Set current process encoding
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'
    
    # Run fixes
    fix_git_hooks()
    fix_validate_code()
    set_environment_variables()
    create_env_file()
    
    print()
    print("=" * 50)
    print("✅ UNICODE FIX COMPLETE!")
    print("=" * 50)
    print()
    print("Changes made:")
    print("✓ Git hooks updated with UTF-8 encoding")
    print("✓ validate_code.py updated")
    print("✓ Environment variables set")
    print("✓ .env file created")
    print()
    print("🔄 Please close and reopen your terminal for changes to take effect!")
    print()

if __name__ == "__main__":
    main()