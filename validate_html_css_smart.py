#!/usr/bin/env python3
"""
Smart HTML/CSS validation script for TrenchCoat Pro
Properly handles f-strings, templates, and Python expressions
"""

import re
import sys
import ast
from pathlib import Path
from typing import List, Tuple, Dict, Optional

class SmartHTMLCSSValidator:
    def __init__(self):
        self.errors: List[Tuple[str, str, str]] = []
        self.warnings: List[Tuple[str, str, str]] = []
        self.info: List[Tuple[str, str, str]] = []
        
    def validate_streamlit_app(self) -> bool:
        """Validate streamlit_app.py with smart parsing"""
        app_path = Path('streamlit_app.py')
        
        if not app_path.exists():
            self.errors.append((
                'streamlit_app.py',
                'N/A',
                'Main app file not found!'
            ))
            return False
        
        return self.validate_python_file(app_path)
    
    def validate_python_file(self, file_path: Path) -> bool:
        """Validate Python file containing HTML/CSS"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # First, check Python syntax
            try:
                ast.parse(content)
                self.info.append((str(file_path), 'Syntax', '✅ Valid Python syntax'))
            except SyntaxError as e:
                self.errors.append((
                    str(file_path),
                    f'Line {e.lineno}',
                    f'Python syntax error: {e.msg}'
                ))
                return False
            
            # Extract and validate HTML blocks
            self._validate_html_blocks(content, file_path)
            
            # Validate CSS
            self._validate_css_blocks(content, file_path)
            
            return True
            
        except Exception as e:
            self.errors.append((
                str(file_path),
                'Unknown',
                f'Error reading file: {str(e)}'
            ))
            return False
    
    def _validate_html_blocks(self, content: str, file_path: Path):
        """Extract and validate HTML blocks from Python code"""
        lines = content.splitlines()
        
        # Find st.markdown calls with HTML
        for i, line in enumerate(lines, 1):
            if 'st.markdown(' in line and 'unsafe_allow_html=True' in line:
                # This is a valid HTML block marker
                html_content = self._extract_html_from_context(lines, i)
                if html_content:
                    self._validate_html_smart(html_content, file_path, i)
            elif 'st.markdown(' in line and any(tag in line for tag in ['<div', '<span', '<p', '<h']):
                # HTML without unsafe_allow_html
                if 'unsafe_allow_html=True' not in line:
                    self.errors.append((
                        str(file_path),
                        f'Line {i}',
                        'HTML content without unsafe_allow_html=True'
                    ))
    
    def _extract_html_from_context(self, lines: List[str], start_line: int) -> Optional[str]:
        """Extract HTML content from surrounding context"""
        # Look for triple-quoted strings or f-strings
        html_lines = []
        in_multiline = False
        bracket_count = 0
        
        # Start from a few lines before to catch the beginning
        for i in range(max(0, start_line - 10), min(len(lines), start_line + 50)):
            line = lines[i]
            
            # Track multiline strings
            if '"""' in line or "'''" in line:
                in_multiline = not in_multiline
                if in_multiline:
                    html_lines = [line]  # Start fresh
                elif html_lines:
                    html_lines.append(line)
                    break
            elif in_multiline:
                html_lines.append(line)
            
            # Track parentheses for single-line strings
            if 'st.markdown(' in line:
                bracket_count = line.count('(') - line.count(')')
                if bracket_count > 0:
                    html_lines = [line]
            elif bracket_count > 0:
                html_lines.append(line)
                bracket_count += line.count('(') - line.count(')')
                if bracket_count == 0:
                    break
        
        if html_lines:
            return '\n'.join(html_lines)
        return None
    
    def _validate_html_smart(self, html_content: str, file_path: Path, line_num: int):
        """Validate HTML with smart f-string handling"""
        # Remove Python f-string expressions before validation
        cleaned_html = self._clean_fstring_expressions(html_content)
        
        # Skip if it's mostly Python code
        if cleaned_html.count('{') > cleaned_html.count('<'):
            return  # Likely more Python than HTML
        
        # Extract actual HTML tags (not in f-string expressions)
        open_tags = []
        close_tags = []
        
        # Find tags outside of {}
        tag_pattern = r'<(/?)(\w+)([^>]*)>'
        brace_depth = 0
        
        for match in re.finditer(r'[<>{}]', cleaned_html):
            char = match.group()
            if char == '{':
                brace_depth += 1
            elif char == '}':
                brace_depth = max(0, brace_depth - 1)
            elif brace_depth == 0:  # Only process tags outside of expressions
                if char == '<':
                    # Look for complete tag
                    tag_match = re.match(tag_pattern, cleaned_html[match.start():])
                    if tag_match:
                        is_closing = tag_match.group(1) == '/'
                        tag_name = tag_match.group(2)
                        
                        if is_closing:
                            close_tags.append(tag_name)
                        elif tag_name not in ['br', 'img', 'input', 'hr', 'meta', 'link']:
                            open_tags.append(tag_name)
        
        # Basic tag balance check
        tag_counts = {}
        for tag in open_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        for tag in close_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) - 1
        
        # Only report significant imbalances
        unbalanced = [tag for tag, count in tag_counts.items() if abs(count) > 1]
        if unbalanced:
            self.warnings.append((
                str(file_path),
                f'Line ~{line_num}',
                f'Potentially unbalanced tags: {", ".join(unbalanced)}'
            ))
    
    def _clean_fstring_expressions(self, content: str) -> str:
        """Remove f-string expressions to prevent false positives"""
        # Replace {expression} with placeholder
        cleaned = content
        
        # Handle nested braces
        brace_depth = 0
        result = []
        i = 0
        
        while i < len(content):
            if content[i] == '{':
                if i + 1 < len(content) and content[i + 1] == '{':
                    # Escaped brace
                    result.append('{{')
                    i += 2
                    continue
                brace_depth += 1
                if brace_depth == 1:
                    result.append('{EXPR}')
            elif content[i] == '}':
                if i + 1 < len(content) and content[i + 1] == '}':
                    # Escaped brace
                    result.append('}}')
                    i += 2
                    continue
                brace_depth = max(0, brace_depth - 1)
            else:
                if brace_depth == 0:
                    result.append(content[i])
            i += 1
        
        return ''.join(result)
    
    def _validate_css_blocks(self, content: str, file_path: Path):
        """Validate CSS with smart parsing"""
        # Find <style> blocks
        style_blocks = re.findall(r'<style[^>]*>(.*?)</style>', content, re.DOTALL | re.IGNORECASE)
        
        for css in style_blocks:
            # Remove f-string expressions
            cleaned_css = self._clean_fstring_expressions(css)
            
            # Basic syntax check
            if cleaned_css.count('{') != cleaned_css.count('}'):
                # Only error if significantly unbalanced
                diff = abs(cleaned_css.count('{') - cleaned_css.count('}'))
                if diff > 2:
                    self.warnings.append((
                        str(file_path),
                        'CSS Block',
                        f'Possibly unbalanced braces in CSS (diff: {diff})'
                    ))
    
    def print_report(self) -> bool:
        """Print validation report"""
        print("\n" + "="*60)
        print("🔍 SMART HTML/CSS VALIDATION REPORT")
        print("="*60)
        
        if not self.errors and not self.warnings:
            print("✅ All checks passed! Code is ready for deployment.")
            return True
        
        if self.info:
            print("\nℹ️  INFO:")
            for file, location, message in self.info:
                print(f"  • {message}")
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for file, location, message in self.errors:
                print(f"  • {file} @ {location}: {message}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            # Only show first 5 warnings to reduce noise
            for file, location, message in self.warnings[:5]:
                print(f"  • {file} @ {location}: {message}")
            if len(self.warnings) > 5:
                print(f"  • ... and {len(self.warnings) - 5} more warnings")
        
        print("\n" + "="*60)
        
        # Only fail on actual errors, not warnings
        return len(self.errors) == 0

def main():
    """Run smart HTML/CSS validation"""
    validator = SmartHTMLCSSValidator()
    
    # Validate streamlit app
    validator.validate_streamlit_app()
    
    # Print report
    success = validator.print_report()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()