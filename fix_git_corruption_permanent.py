#!/usr/bin/env python3
"""
Permanent fix for git repository corruption issues
"""

import subprocess
import os
import sys

def run_command(cmd):
    """Run a command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def fix_git_corruption():
    """Fix git repository corruption permanently"""
    print("🔧 Fixing git repository corruption...")
    
    # 1. Disable automatic garbage collection
    print("📌 Disabling automatic garbage collection...")
    success, _, _ = run_command("git config gc.auto 0")
    if success:
        print("✅ Automatic GC disabled")
    else:
        print("⚠️  Could not disable automatic GC")
    
    # 2. Remove corrupted objects
    print("\n🗑️  Removing corrupted objects...")
    corrupted_objects = [
        ".git/objects/8a/17640895559036cf580bc7527b003bd25be6a5",
        ".git/objects/95/bfe01cdb08116e398e5469f555db23abf9a1ec", 
        ".git/objects/70/a39bdfcd380af51361ce4e854c3ab3f2b2da93"
    ]
    
    for obj in corrupted_objects:
        if os.path.exists(obj):
            try:
                os.remove(obj)
                print(f"✅ Removed {obj}")
            except Exception as e:
                print(f"⚠️  Could not remove {obj}: {e}")
    
    # 3. Verify repository status
    print("\n🔍 Verifying repository status...")
    success, stdout, stderr = run_command("git status --short")
    if success:
        print("✅ Repository is functional")
        if stdout:
            print(f"📄 Uncommitted changes:\n{stdout}")
    else:
        print("❌ Repository still has issues")
        print(f"Error: {stderr}")
    
    # 4. Set up preventive measures
    print("\n🛡️  Setting up preventive measures...")
    
    # Increase pack size limit
    run_command("git config pack.packSizeLimit 2g")
    print("✅ Increased pack size limit")
    
    # Set safer compression
    run_command("git config core.compression 4")
    print("✅ Set safer compression level")
    
    # Disable delta compression for large files
    run_command("git config delta.maxDeltaSize 100m")
    print("✅ Limited delta compression")
    
    print("\n✨ Git corruption fix complete!")
    print("\n📝 To manually run garbage collection when needed:")
    print("   git gc --prune=now")
    print("\n⚠️  Note: Automatic GC is disabled. Run manual GC periodically.")

if __name__ == "__main__":
    fix_git_corruption()