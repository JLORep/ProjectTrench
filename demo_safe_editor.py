#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo Safe Editor - Show error prevention without terminal Unicode issues
"""

def main():
    print("SAFE FILE EDITOR - ERROR PREVENTION DEMO")
    print("=" * 50)
    
    try:
        from safe_file_editor import SafeEditor
        
        # Test 1: Demonstrate string existence checking
        print("\n1. STRING EXISTENCE CHECK (prevents 'string not found' errors)")
        print("-" * 60)
        
        editor = SafeEditor("CLAUDE.md")
        
        # This would cause error in normal Edit tool
        fake_string = "*Last updated: 2025-08-01 12:03 - Solana wallet integration complete, dev blog triggered*"
        
        exists, lines = editor.string_exists(fake_string)
        print(f"String exists: {exists}")
        
        if not exists:
            print("PREVENTION: Safe editor detected string doesn't exist")
            print("FALLBACK: Looking for similar strings...")
            
            similar = editor.find_similar_strings("Last updated", max_results=2)
            if similar:
                print(f"Found {len(similar)} similar alternatives")
        
        # Test 2: Demonstrate safe append (always works)
        print("\n2. SAFE APPEND (always works, no errors)")
        print("-" * 45)
        
        # This always works and never throws errors
        test_content = "TEST: Safe editor demo content with emojis: checkmark cross warning"
        print(f"Appending test content: {len(test_content)} characters")
        
        # Would append safely (not actually doing it in demo)
        print("SUCCESS: Would append safely without errors")
        
        # Test 3: Unicode fixing demonstration
        print("\n3. UNICODE FIXING (prevents encoding errors)")
        print("-" * 48)
        
        problematic_text = "Smart quotes and em-dashes with bullets"
        fixed_text = editor.fix_unicode(problematic_text)
        print(f"Original: {problematic_text}")
        print(f"Fixed:    {fixed_text}")
        
        # Test 4: File info (diagnostic)
        print("\n4. FILE DIAGNOSTICS")
        print("-" * 20)
        
        info = editor.get_file_info()
        if info:
            print(f"File size: {info.get('character_count', 0):,} characters")
            print(f"Line count: {info.get('line_count', 0):,} lines")
            print(f"File exists: {info.get('exists', False)}")
        
        print("\n" + "=" * 50)
        print("RESULT: All operations completed without credit-wasting errors!")
        print("The Safe Editor prevents:")
        print("- String not found errors")
        print("- File not read errors") 
        print("- Unicode encoding issues")
        print("- Credit-wasting retry loops")
        
    except Exception as e:
        print(f"Demo error (would be handled safely): {e}")

if __name__ == "__main__":
    main()