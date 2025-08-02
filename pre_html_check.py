#!/usr/bin/env python3
"""
Pre-commit HTML check using HTML Guard System
Prevents HTML rendering errors before they reach production
"""

import sys
import re
from pathlib import Path
from html_guard_system import HTMLGuardSystem

def check_file_for_html_issues(filepath: Path) -> list:
    """Check a Python file for potential HTML rendering issues"""
    issues = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all potential HTML strings (triple quoted strings with HTML tags)
    html_patterns = re.findall(r'(""".*?<[^>]+>.*?"""|\'\'\'.*?<[^>]+>.*?\'\'\')', content, re.DOTALL)
    
    guard = HTMLGuardSystem()
    
    for i, html_string in enumerate(html_patterns):
        # Check for common problematic patterns
        
        # 1. ${value or 0:,.0f} pattern
        if re.search(r'\$\{[^}]*\sor\s[^}]*:[^}]*\}', html_string):
            issues.append(f"{filepath}:{i+1} - Found 'or' operator in f-string format spec")
        
        # 2. Complex onerror handlers
        if 'onerror=' in html_string and 'outerHTML' in html_string:
            issues.append(f"{filepath}:{i+1} - Complex onerror handler with nested quotes")
        
        # 3. Direct dictionary access without .get()
        if re.search(r'\{coin\[[\'"][^\'"]+[\'"]\]', html_string):
            issues.append(f"{filepath}:{i+1} - Direct dictionary access without .get()")
        
        # 4. Inline .get() with format spec
        if re.search(r'\{[^}]*\.get\([^)]*\)[^}]*:[^}]*\}', html_string):
            # This is actually problematic if combined with 'or'
            if ' or ' in html_string:
                issues.append(f"{filepath}:{i+1} - Complex .get() with 'or' in f-string")
    
    # Check for st.markdown with unsafe_allow_html
    markdown_calls = re.findall(r'st\.markdown\([^)]+unsafe_allow_html=True[^)]*\)', content)
    for call in markdown_calls:
        # Check if the HTML content has been validated
        if 'HTMLGuardSystem' not in content[:content.find(call)]:
            issues.append(f"{filepath} - st.markdown with unsafe HTML not using HTMLGuardSystem")
    
    return issues

def main():
    """Main pre-commit check"""
    print("🛡️ Running HTML Guard Pre-Commit Check...")
    
    # Files to check
    files_to_check = [
        'streamlit_app.py',
        'memecoin_hunt_hub_ui.py',
        'ultra_premium_dashboard.py'
    ]
    
    all_issues = []
    
    for filename in files_to_check:
        filepath = Path(filename)
        if filepath.exists():
            issues = check_file_for_html_issues(filepath)
            all_issues.extend(issues)
    
    if all_issues:
        print("\n❌ HTML Guard Check FAILED!")
        print("\nIssues found:")
        for issue in all_issues:
            print(f"  - {issue}")
        
        print("\n💡 Recommendations:")
        print("  1. Use HTMLGuardSystem.create_coin_card_html() for coin cards")
        print("  2. Pre-calculate values before using in f-strings")
        print("  3. Use .get(key, default) instead of 'or' in format specs")
        print("  4. Avoid complex onerror handlers with nested quotes")
        
        return 1
    else:
        print("✅ HTML Guard Check PASSED!")
        return 0

if __name__ == "__main__":
    sys.exit(main())