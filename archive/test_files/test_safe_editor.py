#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Safe File Editor - Demonstrate error prevention

This shows how SafeEditor prevents the common errors:
1. "String to replace not found in file" 
2. "File has not been read yet"
"""

from safe_file_editor import SafeEditor

def test_claude_md_update():
    """Test updating CLAUDE.md safely"""
    
    print("Testing CLAUDE.md Update (Error Prevention)")
    print("=" * 55)
    
    editor = SafeEditor("CLAUDE.md")
    
    # This would normally cause "String to replace not found" error
    print("❌ BAD APPROACH (causes errors):")
    print("   Trying to replace: '*Last updated: 2025-08-01 12:03 - Solana wallet...'")
    
    # Show what the safe editor does instead
    exists, lines = editor.string_exists("*Last updated: 2025-08-01 12:03 - Solana wallet integration complete, dev blog triggered*")
    
    if not exists:
        print("✅ SAFE APPROACH: String not found, looking for alternatives...")
        
        # Find similar strings
        similar = editor.find_similar_strings("Last updated", max_results=3)
        
        if similar:
            print("✅ Found similar strings - can use these for replacement")
        else:
            print("✅ No similar strings - will append to end instead")
    
    # Demonstrate the smart CLAUDE.md update
    print("\nUsing smart_claude_md_update():")
    
    new_content = """### 🎯 USER ISSUE RESOLVED
**User Report**: "dev blog should actually contain dev blog entries there is coin data in there currently please move that to the coin data section"
**ROOT CAUSE**: Tab 6 labeled "📝 Dev Blog" but contained coin data instead of development updates
**SOLUTION APPLIED**: Replaced coin data with comprehensive development blog entries

### Result:
- ✅ **Tab 6**: Now contains actual development blog entries as requested
- ✅ **Tab 8**: Coin data remains properly placed in dedicated coin data section
- ✅ **User Experience**: Clear separation between development updates and coin analytics"""
    
    # This will safely add the content without causing errors
    success = editor.smart_claude_md_update("Session 2025-08-01 FINAL FIX - Dev Blog Content Correction", new_content)
    
    if success:
        print("✅ Successfully updated CLAUDE.md without errors!")
    else:
        print("❌ Update failed (but no credit-wasting errors thrown)")
    
    # Show file info
    info = editor.get_file_info()
    print(f"\n📊 File Info:")
    print(f"   Size: {info['character_count']:,} characters")
    print(f"   Lines: {info['line_count']:,}")
    print(f"   Backup created: {info['has_backup']}")

def test_error_prevention():
    """Show how common errors are prevented"""
    
    print("\nError Prevention Examples")
    print("=" * 35)
    
    editor = SafeEditor("CLAUDE.md")
    
    # Test 1: String not found (prevents error)
    print("Test 1: Non-existent string replacement")
    success = editor.safe_replace(
        "This string definitely does not exist in the file", 
        "New content", 
        confirm_exists=True
    )
    print(f"Result: {'Success' if success else 'Safely prevented error'}")
    
    # Test 2: File reading check
    print("\nTest 2: File reading verification")
    if editor.content is None:
        print("❌ File not read yet - would cause error in normal Edit tool")
    else:
        print("✅ File content cached - safe to proceed")
    
    # Test 3: Backup creation
    print("\nTest 3: Backup safety")
    editor.create_backup()
    print("✅ Backup created before any changes")

if __name__ == "__main__":
    test_claude_md_update()
    test_error_prevention()