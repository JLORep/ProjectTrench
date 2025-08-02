#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive syntax checker for TrenchCoat Pro
Always run this before committing changes!
"""

import ast
import sys
import os
from pathlib import Path

def check_syntax(file_path):
    """Check syntax of Python file"""
    try:
        with open(file_path, encoding='utf-8') as f:
            content = f.read()
        
        # Parse AST
        ast.parse(content)
        
        # Check for common f-string issues
        if 'f"' in content or "f'" in content:
            # Basic check for nested f-strings
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                if 'f"' in line or "f'" in line:
                    # Count braces
                    brace_count = line.count('{') - line.count('}')
                    if abs(brace_count) > 3:  # Likely nested f-string
                        print(f"⚠️  Line {i}: Possible complex f-string (review for nesting)")
        
        return True, None
        
    except SyntaxError as e:
        return False, f"Line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, str(e)

def main():
    """Main syntax checking function"""
    files_to_check = [
        'streamlit_app.py',
        'complete_async_deploy.py',
        'enhanced_deployment_validator.py'
    ]
    
    print("TrenchCoat Pro Syntax Checker")
    print("=" * 40)
    
    all_passed = True
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"Checking {file_path}...")
            passed, error = check_syntax(file_path)
            
            if passed:
                print(f"[OK] {file_path}: Syntax OK")
            else:
                print(f"[ERROR] {file_path}: {error}")
                all_passed = False
        else:
            print(f"[SKIP] {file_path}: File not found (skipping)")
    
    print("=" * 40)
    if all_passed:
        print("[SUCCESS] All syntax checks PASSED - Safe to commit!")
        return 0
    else:
        print("[FAILED] Syntax errors found - Fix before committing!")
        return 1

if __name__ == "__main__":
    sys.exit(main())