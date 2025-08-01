#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BFG Webhook Cleaner - Use BFG Repo-Cleaner for webhook URL removal
"""

import subprocess
import os
import tempfile
import shutil
from datetime import datetime
from unicode_handler import safe_print

def download_bfg():
    """Download BFG Repo-Cleaner if not available"""
    bfg_url = "https://repo1.maven.org/maven2/com/madgag/bfg/1.14.0/bfg-1.14.0.jar"
    bfg_file = "bfg.jar"
    
    if os.path.exists(bfg_file):
        safe_print("✅ BFG Repo-Cleaner found")
        return bfg_file
    
    safe_print("📥 Downloading BFG Repo-Cleaner...")
    try:
        import urllib.request
        urllib.request.urlretrieve(bfg_url, bfg_file)
        safe_print("✅ BFG Repo-Cleaner downloaded")
        return bfg_file
    except Exception as e:
        safe_print(f"❌ Could not download BFG: {e}")
        return None

def create_replacements_file():
    """Create replacements file for BFG"""
    replacements_content = """
https://discord.com/api/webhooks/*/[A-Za-z0-9_-]*==>[WEBHOOK_REMOVED_FOR_SECURITY]
https://discordapp.com/api/webhooks/*/[A-Za-z0-9_-]*==>[WEBHOOK_REMOVED_FOR_SECURITY]
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(replacements_content.strip())
        return f.name

def run_bfg_cleaner():
    """Run BFG Repo-Cleaner to remove webhook URLs"""
    
    # Check for Java
    try:
        result = subprocess.run(['java', '-version'], capture_output=True, text=True)
        safe_print("✅ Java runtime found")
    except FileNotFoundError:
        safe_print("❌ Java not found. BFG requires Java to run.")
        return False
    
    # Download BFG
    bfg_file = download_bfg()
    if not bfg_file:
        return False
    
    # Create replacements file
    replacements_file = create_replacements_file()
    
    try:
        safe_print("🧹 Running BFG Repo-Cleaner...")
        safe_print("   This will remove webhook URLs from entire Git history")
        
        # Run BFG with replace-text
        cmd = [
            'java', '-jar', bfg_file,
            '--replace-text', replacements_file,
            '--no-blob-protection',
            '.'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            safe_print("✅ BFG Repo-Cleaner completed successfully")
            safe_print("📋 BFG Output:")
            # Show relevant output lines
            output_lines = result.stdout.split('\n')
            for line in output_lines:
                if 'Cleaning' in line or 'Found' in line or 'Deleting' in line:
                    safe_print(f"   {line}")
            
            # Clean up Git references as recommended by BFG
            safe_print("🧹 Cleaning up Git references...")
            subprocess.run(['git', 'reflog', 'expire', '--expire=now', '--all'], 
                         capture_output=True)
            subprocess.run(['git', 'gc', '--prune=now', '--aggressive'], 
                         capture_output=True)
            
            return True
        else:
            safe_print("❌ BFG Repo-Cleaner failed:")
            safe_print(f"   {result.stderr}")
            return False
            
    except Exception as e:
        safe_print(f"❌ BFG execution failed: {e}")
        return False
    finally:
        # Clean up
        try:
            os.unlink(replacements_file)
        except:
            pass

def verify_bfg_cleanup():
    """Verify BFG cleanup was successful"""
    safe_print("")
    safe_print("🔍 VERIFYING BFG CLEANUP...")
    safe_print("=" * 30)
    
    try:
        # Check Git history for remaining webhooks
        result = subprocess.run([
            'git', 'log', '--all', '-S', 'discord.com/api/webhooks', '--oneline'
        ], capture_output=True, text=True, encoding='utf-8', errors='ignore')
        
        if result.stdout.strip():
            remaining = result.stdout.strip().split('\n')
            safe_print(f"⚠️  {len(remaining)} commits still contain webhooks")
            return False
        else:
            safe_print("✅ SUCCESS: No webhook URLs found in Git history")
            
            # Double-check with grep
            result2 = subprocess.run([
                'git', 'log', '--all', '--grep=discord.com/api/webhooks', '--oneline'
            ], capture_output=True, text=True, encoding='utf-8', errors='ignore')
            
            if result2.stdout.strip():
                safe_print("ℹ️  Some commit messages still reference webhooks (metadata only)")
            
            return True
            
    except Exception as e:
        safe_print(f"❌ Verification failed: {e}")
        return False

def main():
    """Main execution for BFG cleaning"""
    safe_print("🔥 BFG REPO-CLEANER WEBHOOK REMOVAL")
    safe_print("=" * 40)
    safe_print("⚠️  This will rewrite entire Git history!")
    
    # Check Git repo
    try:
        subprocess.run(['git', 'rev-parse', '--git-dir'], 
                      capture_output=True, check=True)
        safe_print("✅ Git repository confirmed")
    except subprocess.CalledProcessError:
        safe_print("❌ ERROR: Not in a Git repository!")
        return
    
    # Create backup
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"git_backup_bfg_{timestamp}"
    
    safe_print("")
    safe_print("📦 Creating backup before BFG operation...")
    try:
        subprocess.run(['git', 'clone', '.', f'../{backup_name}'], check=True)
        safe_print(f"✅ Backup created: ../{backup_name}")
    except subprocess.CalledProcessError:
        safe_print("❌ Could not create backup - continuing anyway")
        backup_name = None
    
    # Run BFG cleaner
    safe_print("")
    success = run_bfg_cleaner()
    
    if success:
        # Verify results
        if verify_bfg_cleanup():
            safe_print("")
            safe_print("🎉 SUCCESS: BFG webhook removal completed!")
            if backup_name:
                safe_print(f"📦 Backup: ../{backup_name}")
            safe_print("")
            safe_print("📋 NEXT STEPS:")
            safe_print("1. git push --force-with-lease origin main")
            safe_print("2. Team members need to re-clone repository")
            safe_print("3. Webhook URLs removed from entire Git history")
        else:
            safe_print("⚠️  BFG completed but some webhooks may remain")
    else:
        safe_print("❌ BFG webhook removal failed")
        if backup_name:
            safe_print(f"   Backup available: ../{backup_name}")

if __name__ == "__main__":
    main()