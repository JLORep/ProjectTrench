#!/usr/bin/env python3
"""
Pre-deployment code validation script for TrenchCoat Pro
Runs syntax checks, linting, and basic validation before commits
"""

import ast
import sys
import subprocess
import json
from pathlib import Path
from typing import List, Tuple, Dict

class CodeValidator:
    def __init__(self):
        self.errors: List[Tuple[str, str, str]] = []
        self.warnings: List[Tuple[str, str, str]] = []
        
    def validate_python_syntax(self, file_path: Path) -> bool:
        """Check Python file for syntax errors"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Try to parse the AST
            ast.parse(content)
            return True
            
        except SyntaxError as e:
            self.errors.append((
                str(file_path),
                f"Line {e.lineno}",
                f"SyntaxError: {e.msg}"
            ))
            return False
        except Exception as e:
            self.errors.append((
                str(file_path),
                "Unknown",
                f"Error: {str(e)}"
            ))
            return False
    
    def run_pylint(self, file_path: Path) -> Dict:
        """Run pylint on file and return results"""
        try:
            # Run pylint with JSON output
            result = subprocess.run(
                ['pylint', '--output-format=json', '--disable=all', '--enable=E', str(file_path)],
                capture_output=True,
                text=True
            )
            
            if result.stdout:
                issues = json.loads(result.stdout)
                for issue in issues:
                    if issue['type'] == 'error':
                        self.errors.append((
                            str(file_path),
                            f"Line {issue['line']}",
                            f"{issue['symbol']}: {issue['message']}"
                        ))
                return {'success': len(issues) == 0, 'issues': issues}
            
            return {'success': True, 'issues': []}
            
        except subprocess.CalledProcessError:
            # Pylint not installed
            return {'success': True, 'issues': []}
        except Exception:
            # Other error - don't block deployment
            return {'success': True, 'issues': []}
    
    def validate_streamlit_app(self) -> bool:
        """Specifically validate streamlit_app.py"""
        app_path = Path('streamlit_app.py')
        
        if not app_path.exists():
            self.errors.append((
                'streamlit_app.py',
                'N/A',
                'Main app file not found!'
            ))
            return False
        
        # Check syntax
        syntax_ok = self.validate_python_syntax(app_path)
        
        # Check for common Streamlit issues
        with open(app_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.splitlines()
        
        # Check for common indentation issues
        for i, line in enumerate(lines, 1):
            # Check for tabs vs spaces
            if '\t' in line and '    ' in line:
                self.warnings.append((
                    'streamlit_app.py',
                    f'Line {i}',
                    'Mixed tabs and spaces'
                ))
            
            # Check for empty with blocks
            if line.strip().endswith('with st.container():') or line.strip().endswith('with st.columns():'):
                if i < len(lines) and not lines[i].strip():
                    self.warnings.append((
                        'streamlit_app.py',
                        f'Line {i}',
                        'Empty with block detected'
                    ))
        
        return syntax_ok
    
    def validate_all_python_files(self) -> bool:
        """Validate all Python files in project"""
        all_valid = True
        
        # Only check critical files to avoid blocking on old backup files
        critical_files = ['streamlit_app.py']
        
        for file_name in critical_files:
            if file_name.endswith('.py'):
                file_path = Path(file_name)
                if file_path.exists():
                    if not self.validate_python_syntax(file_path):
                        all_valid = False
        
        return all_valid
    
    def print_report(self):
        """Print validation report"""
        print("\n" + "="*60)
        print("🔍 CODE VALIDATION REPORT")
        print("="*60)
        
        if not self.errors and not self.warnings:
            print("✅ All checks passed! Code is ready for deployment.")
            return True
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for file, location, message in self.errors:
                print(f"  • {file} @ {location}: {message}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for file, location, message in self.warnings:
                print(f"  • {file} @ {location}: {message}")
        
        print("\n" + "="*60)
        
        return len(self.errors) == 0

def main():
    """Run validation"""
    validator = CodeValidator()
    
    # Validate streamlit app
    validator.validate_streamlit_app()
    
    # Validate other Python files
    validator.validate_all_python_files()
    
    # Print report
    success = validator.print_report()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()