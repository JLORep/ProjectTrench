#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Safe File Editor - Prevents common file editing errors that waste credits

This utility prevents:
1. "String to replace not found in file" errors
2. "File has not been read yet" errors  
3. Overwrites of files without confirmation
4. Credit-wasting retry loops

Usage:
    from safe_file_editor import SafeEditor
    
    editor = SafeEditor("CLAUDE.md")
    success = editor.append_to_end("New content to add")
    success = editor.safe_replace("old text", "new text", confirm_exists=True)
"""

import os
import re
import unicodedata
from typing import Optional, Tuple, List
from datetime import datetime


class SafeEditor:
    """Safe file editing with error prevention and validation"""
    
    def __init__(self, file_path: str):
        # Parameter validation
        if not isinstance(file_path, str):
            raise ValueError(f"file_path must be string, got {type(file_path)}")
        if not file_path or not file_path.strip():
            raise ValueError("file_path cannot be empty")
        
        self.file_path = file_path.strip()
        self.content = None
        self.last_read = None
        self.backup_created = False
        
    def fix_unicode(self, text: str) -> str:
        """Fix Unicode issues that cause deployment errors"""
        try:
            # Normalize Unicode to NFC form (canonical composition)
            normalized = unicodedata.normalize('NFC', text)
            
            # Replace problematic Unicode characters with safe alternatives
            replacements = {
                # Smart quotes
                '\u2018': "'",  # Left single quotation mark
                '\u2019': "'",  # Right single quotation mark  
                '\u201C': '"',  # Left double quotation mark
                '\u201D': '"',  # Right double quotation mark
                
                # Dashes
                '\u2013': '-',  # En dash
                '\u2014': '--', # Em dash
                '\u2015': '--', # Horizontal bar
                
                # Spaces
                '\u00A0': ' ',  # Non-breaking space
                '\u2000': ' ',  # En quad
                '\u2001': ' ',  # Em quad
                '\u2002': ' ',  # En space
                '\u2003': ' ',  # Em space
                '\u2009': ' ',  # Thin space
                
                # Arrows and symbols
                '\u2192': '->',  # Right arrow
                '\u2190': '<-',  # Left arrow
                '\u2022': '*',   # Bullet
                '\u2026': '...', # Horizontal ellipsis
                
                # Mathematical symbols
                '\u00D7': 'x',   # Multiplication sign
                '\u00F7': '/',   # Division sign
                '\u2260': '!=',  # Not equal to
                '\u2264': '<=',  # Less than or equal to
                '\u2265': '>=',  # Greater than or equal to
            }
            
            # Apply replacements
            for unicode_char, replacement in replacements.items():
                normalized = normalized.replace(unicode_char, replacement)
            
            # Keep all common emojis used in this project (extensive list)
            safe_emojis = {
                # Status indicators
                '✅', '❌', '⚠️', '⭐', '🎯', '🔧', '🛠️', '🔄', '📊', '📈', '📉', '💡',
                
                # Dashboard & UI
                '🚀', '💎', '📝', '🗄️', '🗃️', '🔔', '📡', '🧠', '🤖', '⚙️', '💰', '📱', '🎨', '💾',
                
                # Trading & Finance  
                '💵', '💰', '💸', '📊', '📈', '📉', '🎯', '⚡', '🔥', '💹', '🏆', '🎲', '💎', '🌟',
                
                # Communication & Social
                '📱', '💬', '📨', '📧', '📤', '📥', '🔗', '🌐', '📺', '📻', '📡', '📢', '📣',
                
                # Development & Tech
                '🔧', '🛠️', '⚙️', '🔩', '🔨', '🖥️', '💻', '📱', '⌚', '🖨️', '💾', '💿', '💽', '💻',
                
                # Data & Analytics
                '📊', '📈', '📉', '📋', '📄', '📃', '📑', '📜', '📰', '🗞️', '📚', '📖', '📗', '📘',
                
                # Alerts & Notifications
                '🔔', '🔕', '🚨', '⏰', '⏲️', '⏱️', '🕐', '🕑', '🕒', '🕓', '🕔', '🕕', '🕖',
                
                # Progress & Status
                '🟢', '🟡', '🔴', '🟠', '🟣', '🔵', '⚫', '⚪', '🟤', '🔘', '🔳', '🔲', '◻️', '◼️',
                
                # Actions & Controls
                '▶️', '⏸️', '⏹️', '⏭️', '⏮️', '⏫', '⏬', '🔼', '🔽', '↗️', '↘️', '↙️', '↖️',
                
                # Success & Achievement
                '🏆', '🥇', '🥈', '🥉', '🎖️', '🏅', '🎗️', '🎀', '🎁', '🎊', '🎉', '🎈', '🎆',
                
                # Security & Protection
                '🔒', '🔓', '🔐', '🗝️', '🛡️', '⚔️', '🔫', '💣', '🧨', '🔪', '⚰️', '🗡️',
                
                # Food & Lifestyle (for fun context)
                '🚀', '🌙', '⭐', '✨', '💫', '🌟', '☄️', '🌠', '🌈', '☀️', '🌞', '🌝', '🌛',
                
                # Additional common ones
                '📍', '📌', '📎', '🔗', '📏', '📐', '✂️', '📌', '📍', '🗺️', '🧭', '⛰️', '🏔️'
            }
            
            # Remove any remaining non-ASCII characters that might cause issues
            # Keep printable ASCII characters plus our extensive emoji whitelist
            safe_text = ''
            for char in normalized:
                if ord(char) < 128 or char in safe_emojis:
                    safe_text += char
                else:
                    # For other Unicode characters, try to convert to ASCII equivalent
                    try:
                        ascii_equiv = unicodedata.normalize('NFKD', char).encode('ascii', 'ignore').decode('ascii')
                        if ascii_equiv:
                            safe_text += ascii_equiv
                        else:
                            # For emojis/symbols not in our safe list, try to preserve them
                            # but log that they might cause issues
                            if unicodedata.category(char).startswith('S'):  # Symbol
                                safe_text += char  # Keep symbols (might be new emojis)
                            # Skip other problematic characters
                    except:
                        pass  # Remove problematic character
            
            return safe_text
            
        except Exception as e:
            print(f"⚠️ Unicode fix error: {e}")
            # Fallback: encode to ASCII and ignore errors
            try:
                return text.encode('ascii', 'ignore').decode('ascii')
            except:
                return text  # Return original if all else fails
        
    def read_file(self, force_refresh: bool = False) -> bool:
        """Safely read file content with caching"""
        try:
            if self.content is None or force_refresh:
                if not os.path.exists(self.file_path):
                    print(f"[ERROR] File not found: {self.file_path}")
                    return False
                    
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    self.content = f.read()
                    self.last_read = datetime.now()
                    print(f"[OK] File read successfully: {len(self.content)} characters")
                    return True
            else:
                print(f"[OK] Using cached content from {self.last_read}")
                return True
                
        except Exception as e:
            print(f"[ERROR] Error reading file: {e}")
            return False
    
    def create_backup(self) -> bool:
        """Create backup before making changes"""
        if self.backup_created:
            return True
            
        try:
            backup_path = f"{self.file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r', encoding='utf-8') as src:
                    with open(backup_path, 'w', encoding='utf-8') as dst:
                        dst.write(src.read())
                self.backup_created = True
                print(f"✅ Backup created: {backup_path}")
                return True
        except Exception as e:
            print(f"⚠️ Backup failed: {e}")
            return False
    
    def string_exists(self, search_string: str) -> Tuple[bool, List[int]]:
        """Check if string exists and return line numbers"""
        # ALWAYS read file first (force refresh to ensure current content)
        if not self.read_file(force_refresh=True):
            print(f"[ERROR] Could not read file: {self.file_path}")
            return False, []
            
        lines = self.content.split('\n')
        matches = []
        
        for i, line in enumerate(lines):
            if search_string in line:
                matches.append(i + 1)
                
        exists = len(matches) > 0
        if exists:
            print(f"✅ String found on lines: {matches}")
        else:
            print(f"❌ String not found: '{search_string[:50]}...'")
            
        return exists, matches
    
    def safe_replace(self, old_string: str, new_string: str, confirm_exists: bool = True) -> bool:
        """Safely replace string with existence confirmation"""
        
        # Parameter validation
        if not isinstance(old_string, str):
            raise ValueError(f"old_string must be string, got {type(old_string)}")
        if not isinstance(new_string, str):
            raise ValueError(f"new_string must be string, got {type(new_string)}")
        if not isinstance(confirm_exists, bool):
            raise ValueError(f"confirm_exists must be boolean, got {type(confirm_exists)}")
        
        # Step 1: ALWAYS read file first (force refresh to ensure current content)
        if not self.read_file(force_refresh=True):
            print(f"[ERROR] Could not read file: {self.file_path}")
            return False
            
        # Step 2: Check if string exists (if requested)
        if confirm_exists:
            exists, line_numbers = self.string_exists(old_string)
            if not exists:
                print(f"❌ PREVENTED ERROR: String '{old_string[:50]}...' not found in file")
                print("🔧 Suggestion: Use append_to_end() or find_similar_strings() instead")
                return False
                
        # Step 3: Create backup
        self.create_backup()
        
        # Step 4: Perform replacement
        try:
            # Fix Unicode in both old and new strings
            old_string_fixed = self.fix_unicode(old_string)
            new_string_fixed = self.fix_unicode(new_string)
            
            new_content = self.content.replace(old_string_fixed, new_string_fixed)
            
            if new_content == self.content:
                print("⚠️ No changes made - strings identical")
                return False
            
            # Fix Unicode in entire content before writing    
            new_content_fixed = self.fix_unicode(new_content)
                
            with open(self.file_path, 'w', encoding='utf-8') as f:
                f.write(new_content_fixed)
                
            self.content = new_content_fixed  # Update cache
            print(f"✅ Successfully replaced string in {self.file_path} (Unicode fixed)")
            return True
            
        except Exception as e:
            print(f"❌ Error during replacement: {e}")
            return False
    
    def append_to_end(self, new_content: str, separator: str = "\n\n") -> bool:
        """Safely append content to end of file"""
        
        # Parameter validation
        if not isinstance(new_content, str):
            raise ValueError(f"new_content must be string, got {type(new_content)}")
        if not isinstance(separator, str):
            raise ValueError(f"separator must be string, got {type(separator)}")
        
        # Step 1: ALWAYS read file first (force refresh to ensure current content)
        if not self.read_file(force_refresh=True):
            print(f"[ERROR] Could not read file: {self.file_path}")
            return False
            
        # Step 2: Create backup
        self.create_backup()
        
        # Step 3: Append content
        try:
            # Fix Unicode in new content
            new_content_fixed = self.fix_unicode(new_content)
            separator_fixed = self.fix_unicode(separator)
            
            final_content = self.content + separator_fixed + new_content_fixed
            
            # Fix Unicode in entire final content
            final_content_fixed = self.fix_unicode(final_content)
            
            with open(self.file_path, 'w', encoding='utf-8') as f:
                f.write(final_content_fixed)
                
            self.content = final_content_fixed  # Update cache
            print(f"✅ Successfully appended {len(new_content_fixed)} characters to {self.file_path} (Unicode fixed)")
            return True
            
        except Exception as e:
            print(f"❌ Error during append: {e}")
            return False
    
    def find_similar_strings(self, target: str, max_results: int = 5) -> List[Tuple[str, int]]:
        """Find similar strings in file to help with replacements"""
        # ALWAYS read file first (force refresh to ensure current content)
        if not self.read_file(force_refresh=True):
            print(f"[ERROR] Could not read file: {self.file_path}")
            return []
            
        lines = self.content.split('\n')
        matches = []
        
        # Look for lines containing key words from target
        target_words = target.lower().split()
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            word_matches = sum(1 for word in target_words if word in line_lower)
            
            if word_matches > 0:
                similarity = word_matches / len(target_words)
                matches.append((line.strip(), i + 1, similarity))
        
        # Sort by similarity and return top matches
        matches.sort(key=lambda x: x[2], reverse=True)
        
        print(f"🔍 Found {len(matches)} similar strings:")
        for line, line_num, similarity in matches[:max_results]:
            print(f"  Line {line_num} ({similarity:.1%}): {line[:80]}...")
            
        return [(line, line_num) for line, line_num, _ in matches[:max_results]]
    
    def replace_last_updated(self, new_update: str) -> bool:
        """Specifically handle 'Last updated' pattern replacements"""
        
        # ALWAYS read file first (force refresh to ensure current content)
        if not self.read_file(force_refresh=True):
            print(f"[ERROR] Could not read file: {self.file_path}")
            return False
            
        # Look for common last updated patterns
        patterns = [
            r'\*Last updated:.*?\*',
            r'Last updated:.*',
            r'\*Last Updated:.*?\*',
            r'Last Updated:.*'
        ]
        
        new_line = f"*Last updated: {new_update}*"
        
        for pattern in patterns:
            matches = re.findall(pattern, self.content, re.IGNORECASE)
            if matches:
                print(f"✅ Found last updated pattern: {matches[-1]}")
                return self.safe_replace(matches[-1], new_line, confirm_exists=True)
        
        # If no pattern found, append to end
        print("ℹ️ No 'Last updated' pattern found, appending to end")
        return self.append_to_end(f"---\n\n{new_line}")
    
    def smart_claude_md_update(self, session_title: str, content: str) -> bool:
        """Smart update specifically for CLAUDE.md files"""
        
        # ALWAYS read file first (force refresh to ensure current content)
        if not self.read_file(force_refresh=True):
            print(f"[ERROR] Could not read file: {self.file_path}")
            return False
            
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        # Create the new section
        new_section = f"""
## {session_title} ✅

{content}

---

*Last updated: {timestamp} - {session_title.split(' -')[0]} completed*"""
        
        # Try to find and replace existing last updated line
        if self.replace_last_updated(f"{timestamp} - {session_title.split(' -')[0]} completed"):
            # Then insert the new section before the last updated line
            last_updated_line = f"*Last updated: {timestamp} - {session_title.split(' -')[0]} completed*"
            section_with_timestamp = f"{new_section.replace('---', '').replace(last_updated_line, '').strip()}\n\n---\n\n{last_updated_line}"
            return self.safe_replace(last_updated_line, section_with_timestamp, confirm_exists=True)
        else:
            # Fallback: append to end
            return self.append_to_end(new_section)
    
    def get_file_info(self) -> dict:
        """Get comprehensive file information"""
        # ALWAYS read file first (force refresh to ensure current content)
        if not self.read_file(force_refresh=True):
            print(f"[ERROR] Could not read file: {self.file_path}")
            return {}
            
        lines = self.content.split('\n')
        
        return {
            'file_path': self.file_path,
            'exists': os.path.exists(self.file_path),
            'size_bytes': len(self.content.encode('utf-8')),
            'character_count': len(self.content),
            'line_count': len(lines),
            'last_read': self.last_read,
            'has_backup': self.backup_created
        }


def demonstrate_usage():
    """Demonstrate safe editing patterns"""
    
    print("🔧 SafeEditor Usage Examples:")
    print("=" * 50)
    
    # Example 1: Safe replacement
    editor = SafeEditor("CLAUDE.md")
    
    # Check if string exists first
    exists, lines = editor.string_exists("Last updated:")
    if exists:
        print(f"Found 'Last updated' on lines: {lines}")
    else:
        print("String not found - will append instead")
    
    # Example 2: Find similar strings
    similar = editor.find_similar_strings("Last updated", max_results=3)
    
    # Example 3: Safe append
    # editor.append_to_end("New content here")
    
    # Example 4: File info
    info = editor.get_file_info()
    print(f"File info: {info}")


if __name__ == "__main__":
    demonstrate_usage()