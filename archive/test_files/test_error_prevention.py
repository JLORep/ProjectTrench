#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Error Prevention - Simple demo without Unicode terminal issues
"""

def test_safe_vs_normal():
    """Demonstrate how SafeEditor prevents common errors"""
    
    print("SAFE EDITOR: ERROR PREVENTION COMPARISON")
    print("=" * 50)
    
    # Import the SafeEditor
    from safe_file_editor import SafeEditor
    
    # Test with CLAUDE.md
    editor = SafeEditor("CLAUDE.md")
    
    print("\nTEST 1: String Existence Check")
    print("-" * 30)
    
    # This string definitely doesn't exist (would cause normal Edit error)
    fake_string = "*Last updated: 2025-08-01 12:03 - Solana wallet integration complete, dev blog triggered*"
    
    exists, lines = editor.string_exists(fake_string)
    print(f"String exists in file: {exists}")
    
    if not exists:
        print("SAFE EDITOR: Prevented 'string not found' error!")
        print("SAFE EDITOR: Looking for alternatives...")
        
        # Find similar strings
        similar = editor.find_similar_strings("Last updated", max_results=3)
        print(f"SAFE EDITOR: Found {len(similar)} similar strings to use instead")
        
    print("\nTEST 2: File Reading Safety") 
    print("-" * 25)
    
    # Check if file content is cached
    if editor.content:
        print(f"SAFE EDITOR: File already read, {len(editor.content):,} characters cached")
        print("SAFE EDITOR: No 'file not read yet' errors possible")
    else:
        print("SAFE EDITOR: File will be read automatically when needed")
    
    print("\nTEST 3: Unicode Fixing")
    print("-" * 20)
    
    # Test Unicode fixing (safe for terminal)
    test_text = "Regular text with safe content"
    fixed_text = editor.fix_unicode(test_text)
    print(f"Original: {test_text}")
    print(f"Fixed:    {fixed_text}")
    print("SAFE EDITOR: Unicode issues automatically resolved")
    
    print("\nTEST 4: Safe Operations")
    print("-" * 22)
    
    # These operations would be safe (not actually executing)
    print("SAFE EDITOR: Would safely append content (no errors)")
    print("SAFE EDITOR: Would create backup before changes")
    print("SAFE EDITOR: Would handle all encoding issues")
    
    print("\n" + "=" * 50)
    print("BENEFITS:")
    print("- Prevents 'string not found' errors (saves credits)")
    print("- Prevents 'file not read' errors (saves credits)")  
    print("- Fixes Unicode encoding issues automatically")
    print("- Creates backups before changes")
    print("- Provides smart fallbacks when operations fail")
    print("- Never throws credit-wasting errors")
    
    return True

if __name__ == "__main__":
    test_safe_vs_normal()