#!/usr/bin/env python3
"""
HTML/CSS validation script for TrenchCoat Pro
Checks for common HTML/CSS issues before deployment
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict
import json

class HTMLCSSValidator:
    def __init__(self):
        self.errors: List[Tuple[str, str, str]] = []
        self.warnings: List[Tuple[str, str, str]] = []
        
    def validate_html_in_python(self, file_path: Path) -> bool:
        """Check Python files for HTML/CSS issues"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.splitlines()
            
            all_valid = True
            
            # Check for st.markdown with HTML
            for i, line in enumerate(lines, 1):
                # Check for unsafe_allow_html=True usage
                if 'unsafe_allow_html=True' in line:
                    # Look for the corresponding HTML content
                    html_start = self._find_html_start(lines, i)
                    if html_start:
                        html_content = self._extract_html_content(lines, html_start)
                        if html_content:
                            self._validate_html_content(html_content, file_path, html_start)
                
                # Check for missing unsafe_allow_html when HTML is present
                if 'st.markdown(' in line and any(tag in line for tag in ['<div', '<span', '<style']):
                    if 'unsafe_allow_html=True' not in line:
                        self.errors.append((
                            str(file_path),
                            f'Line {i}',
                            'HTML content without unsafe_allow_html=True'
                        ))
                        all_valid = False
            
            # Check CSS definitions
            self._validate_css_in_file(content, file_path)
            
            return all_valid
            
        except Exception as e:
            self.warnings.append((
                str(file_path),
                'Unknown',
                f'Error reading file: {str(e)}'
            ))
            return True
    
    def _find_html_start(self, lines: List[str], marker_line: int) -> int:
        """Find where HTML content starts before unsafe_allow_html marker"""
        # Look backwards for st.markdown or triple quotes
        for i in range(marker_line - 1, max(0, marker_line - 20), -1):
            if 'st.markdown(' in lines[i] or '"""' in lines[i]:
                return i
        return 0
    
    def _extract_html_content(self, lines: List[str], start_line: int) -> str:
        """Extract HTML content from Python string"""
        content = []
        in_string = False
        quote_type = None
        
        for i in range(start_line - 1, min(len(lines), start_line + 100)):
            line = lines[i]
            
            if '"""' in line:
                in_string = not in_string
                quote_type = '"""'
            elif "'''" in line:
                in_string = not in_string
                quote_type = "'''"
            elif 'st.markdown(' in line and ('"' in line or "'" in line):
                in_string = True
                quote_type = '"' if '"' in line else "'"
            
            if in_string:
                content.append(line)
            
            if not in_string and content:
                break
        
        return '\n'.join(content)
    
    def _validate_html_content(self, html: str, file_path: Path, line_num: int):
        """Validate HTML content for common issues"""
        # Check for unclosed tags
        open_tags = re.findall(r'<(\w+)[^>]*>', html)
        close_tags = re.findall(r'</(\w+)>', html)
        
        tag_stack = []
        for tag in open_tags:
            if tag not in ['br', 'img', 'input', 'hr', 'meta']:  # Self-closing tags
                tag_stack.append(tag)
        
        for tag in close_tags:
            if tag_stack and tag_stack[-1] == tag:
                tag_stack.pop()
            else:
                self.warnings.append((
                    str(file_path),
                    f'Line ~{line_num}',
                    f'Mismatched closing tag: </{tag}>'
                ))
        
        if tag_stack:
            self.errors.append((
                str(file_path),
                f'Line ~{line_num}',
                f'Unclosed tags: {", ".join(tag_stack)}'
            ))
        
        # Check for common HTML issues
        if '<script>' in html and '</script>' not in html:
            self.errors.append((
                str(file_path),
                f'Line ~{line_num}',
                'Unclosed <script> tag'
            ))
        
        # Check for style attribute issues
        style_attrs = re.findall(r'style="([^"]*)"', html)
        for style in style_attrs:
            if style.count(':') != style.count(';') + 1:
                self.warnings.append((
                    str(file_path),
                    f'Line ~{line_num}',
                    f'Possible CSS syntax error in style attribute'
                ))
    
    def _validate_css_in_file(self, content: str, file_path: Path):
        """Validate CSS content in file"""
        # Find CSS blocks
        css_blocks = re.findall(r'<style[^>]*>(.*?)</style>', content, re.DOTALL)
        
        for css in css_blocks:
            # Check for basic CSS syntax
            if css.count('{') != css.count('}'):
                self.errors.append((
                    str(file_path),
                    'CSS Block',
                    'Mismatched curly braces in CSS'
                ))
            
            # Check for missing semicolons (rough check)
            rules = re.findall(r'\{([^}]+)\}', css)
            for rule in rules:
                declarations = rule.strip().split('\n')
                for decl in declarations:
                    decl = decl.strip()
                    if decl and not decl.endswith(';') and not decl.endswith('}') and ':' in decl:
                        self.warnings.append((
                            str(file_path),
                            'CSS',
                            f'Missing semicolon after CSS declaration'
                        ))
            
            # Check for undefined CSS classes used in HTML
            css_classes = re.findall(r'\.([a-zA-Z0-9-_]+)\s*\{', css)
            html_classes = re.findall(r'class="([^"]*)"', content)
            
            used_classes = set()
            for class_attr in html_classes:
                used_classes.update(class_attr.split())
            
            # Don't warn about Streamlit built-in classes
            streamlit_classes = {'stTabs', 'stMarkdown', 'stContainer', 'main', 'block-container'}
            
            for used_class in used_classes:
                if (used_class not in css_classes and 
                    used_class not in streamlit_classes and
                    not used_class.startswith('st')):
                    self.warnings.append((
                        str(file_path),
                        'CSS',
                        f'CSS class ".{used_class}" used but not defined'
                    ))
    
    def validate_streamlit_app(self) -> bool:
        """Validate streamlit_app.py specifically"""
        app_path = Path('streamlit_app.py')
        
        if not app_path.exists():
            self.errors.append((
                'streamlit_app.py',
                'N/A',
                'Main app file not found!'
            ))
            return False
        
        return self.validate_html_in_python(app_path)
    
    def print_report(self):
        """Print validation report"""
        print("\n" + "="*60)
        print("🔍 HTML/CSS VALIDATION REPORT")
        print("="*60)
        
        if not self.errors and not self.warnings:
            print("✅ All HTML/CSS checks passed!")
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
    """Run HTML/CSS validation"""
    validator = HTMLCSSValidator()
    
    # Validate streamlit app
    validator.validate_streamlit_app()
    
    # Print report
    success = validator.print_report()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()