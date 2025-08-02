#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Improved HTML/CSS validation script for TrenchCoat Pro
More accurate validation that handles f-strings and multiline HTML
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict, Set
import ast

class ImprovedHTMLCSSValidator:
    def __init__(self):
        self.errors: List[Tuple[str, str, str]] = []
        self.warnings: List[Tuple[str, str, str]] = []
        self.void_tags = {'br', 'hr', 'img', 'input', 'link', 'meta', 'area', 'base', 'col', 'embed', 'source', 'track', 'wbr'}
        
    def validate_project(self) -> bool:
        """Validate all Python files in the project"""
        print("=" * 60)
        print("🔍 IMPROVED HTML/CSS VALIDATION")
        print("=" * 60)
        
        python_files = list(Path('.').rglob('*.py'))
        
        for file_path in python_files:
            if 'venv' in str(file_path) or '__pycache__' in str(file_path):
                continue
            self._validate_file(file_path)
        
        # Report results
        print("\n" + "=" * 60)
        print("📊 VALIDATION RESULTS")
        print("=" * 60)
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for file, line, msg in self.errors[:10]:  # Show max 10 errors
                print(f"  • {Path(file).name} @ Line {line}: {msg}")
            if len(self.errors) > 10:
                print(f"  ... and {len(self.errors) - 10} more errors")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for file, line, msg in self.warnings[:10]:  # Show max 10 warnings
                print(f"  • {Path(file).name} @ Line {line}: {msg}")
            if len(self.warnings) > 10:
                print(f"  ... and {len(self.warnings) - 10} more warnings")
        
        if not self.errors and not self.warnings:
            print("\n✅ All HTML/CSS validation passed!")
        
        print("\n" + "=" * 60)
        print()
        
        return len(self.errors) == 0
    
    def _validate_file(self, file_path: Path):
        """Validate a single Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find all st.markdown calls with HTML
            pattern = r'st\.markdown\s*\(\s*[rf]?["\']([^"\']+)["\'].*?unsafe_allow_html\s*=\s*True'
            matches = re.finditer(pattern, content, re.DOTALL)
            
            for match in matches:
                html_content = match.group(1)
                # Skip if it's a template with variables
                if '{' in html_content and '}' in html_content:
                    continue
                self._validate_html_string(html_content, file_path, match.start())
            
            # Find multiline HTML strings
            multiline_pattern = r'[rf]?"""\s*<[^>]+>.*?</[^>]+>\s*"""'
            multiline_matches = re.finditer(multiline_pattern, content, re.DOTALL)
            
            for match in multiline_matches:
                html_content = match.group(0).strip('rf"""')
                # Skip if it's a template with variables
                if '{' in html_content and '}' in html_content:
                    continue
                line_num = content[:match.start()].count('\n') + 1
                self._validate_html_content(html_content, file_path, line_num)
                
        except Exception as e:
            self.warnings.append((str(file_path), '0', f'Could not parse file: {e}'))
    
    def _validate_html_string(self, html: str, file_path: Path, char_pos: int):
        """Validate HTML content from a string"""
        # Convert character position to line number
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        line_num = content[:char_pos].count('\n') + 1
        
        self._validate_html_content(html, file_path, line_num)
    
    def _validate_html_content(self, html: str, file_path: Path, line_num: int):
        """Validate HTML content for tag balance"""
        # Clean up escaped quotes
        html = html.replace(r'\"', '"').replace(r"\'", "'")
        
        # Count tags
        tag_counts = {}
        
        # Find all opening tags
        open_pattern = r'<(\w+)(?:\s[^>]*)?>'
        for match in re.finditer(open_pattern, html):
            tag = match.group(1).lower()
            if tag not in self.void_tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # Find all closing tags
        close_pattern = r'</(\w+)>'
        for match in re.finditer(close_pattern, html):
            tag = match.group(1).lower()
            if tag in tag_counts:
                tag_counts[tag] -= 1
            else:
                self.warnings.append((
                    str(file_path),
                    str(line_num),
                    f'Closing tag </{tag}> without opening tag'
                ))
        
        # Report unclosed tags
        unclosed = [tag for tag, count in tag_counts.items() if count > 0]
        if unclosed:
            self.errors.append((
                str(file_path),
                str(line_num),
                f'Unclosed tags: {", ".join(unclosed)}'
            ))
        
        # Check for basic style syntax
        style_pattern = r'style\s*=\s*["\']([^"\']*)["\']'
        for match in re.finditer(style_pattern, html):
            style = match.group(1)
            # Basic CSS validation
            if style and not style.strip().endswith(';') and ':' in style:
                # Allow single property without semicolon
                if style.count(':') == 1:
                    continue
                self.warnings.append((
                    str(file_path),
                    str(line_num),
                    'CSS style should end with semicolon'
                ))

def main():
    validator = ImprovedHTMLCSSValidator()
    is_valid = validator.validate_project()
    sys.exit(0 if is_valid else 1)

if __name__ == "__main__":
    main()