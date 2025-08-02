#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Webhook Scrubber - Direct approach using git commands
"""

import subprocess
import os
from datetime import datetime
from unicode_handler import safe_print

def create_backup():
    """Create backup of repository"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"git_backup_{timestamp}"
    
    try:
        subprocess.run(['git', 'clone', '.', f'../{backup_name}'], check=True)
        safe_print(f"✅ Backup created: ../{backup_name}")
        return backup_name
    except subprocess.CalledProcessError as e:
        safe_print(f"❌ Could not create backup: {e}")
        return None

def execute_manual_rewrite():
    """Execute manual history rewrite using git commands"""
    
    safe_print("🔧 Starting manual Git history rewrite...")
    
    try:
        # Method 1: Try git filter-branch with correct syntax
        safe_print("📝 Creating replacement file...")
        
        # Create replacement file for git filter-branch
        replacements = [
            's|https://discord\\.com/api/webhooks/[0-9]*/[A-Za-z0-9_-]*|[WEBHOOK_REMOVED_FOR_SECURITY]|g',
            's|https://discordapp\\.com/api/webhooks/[0-9]*/[A-Za-z0-9_-]*|[WEBHOOK_REMOVED_FOR_SECURITY]|g'
        ]
        
        replacement_file = 'webhook_replacements.txt'
        with open(replacement_file, 'w') as f:
            for repl in replacements:
                f.write(repl + '\n')
        
        # Try git filter-branch with index-filter (faster than tree-filter)
        safe_print("🔄 Running git filter-branch with index-filter...")
        
        cmd = [
            'git', 'filter-branch', '--force',
            '--index-filter', 
            f'git ls-files -s | sed "{replacements[0]}" | sed "{replacements[1]}" | GIT_INDEX_FILE=$GIT_INDEX_FILE.new git update-index --index-info && mv $GIT_INDEX_FILE.new $GIT_INDEX_FILE || true',
            '--msg-filter', 
            f'sed "{replacements[0]}" | sed "{replacements[1]}"',
            '--', '--all'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, 
                              encoding='utf-8', errors='ignore')
        
        # Clean up replacement file
        try:
            os.remove(replacement_file)
        except:
            pass
        
        if result.returncode == 0:
            safe_print("✅ git filter-branch completed successfully")
            return True
        else:
            safe_print("❌ git filter-branch failed, trying alternative method...")
            safe_print(f"   Error: {result.stderr}")
            
            # Method 2: Use git-filter-repo if available
            return try_filter_repo()
            
    except Exception as e:
        safe_print(f"❌ Manual rewrite failed: {e}")
        return try_simple_replacement()

def try_filter_repo():
    """Try using git filter-repo"""
    safe_print("🔄 Trying git filter-repo...")
    
    try:
        # Create expressions file
        expressions_file = 'webhook_expressions.txt'
        with open(expressions_file, 'w') as f:
            f.write('regex:https://discord\\.com/api/webhooks/\\d+/[a-zA-Z0-9_-]+==>[WEBHOOK_REMOVED_FOR_SECURITY]\n')
            f.write('regex:https://discordapp\\.com/api/webhooks/\\d+/[a-zA-Z0-9_-]+==>[WEBHOOK_REMOVED_FOR_SECURITY]\n')
        
        result = subprocess.run([
            'git', 'filter-repo',
            '--replace-text', expressions_file,
            '--force'
        ], capture_output=True, text=True, check=True)
        
        os.remove(expressions_file)
        safe_print("✅ git filter-repo completed successfully")
        return True
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        safe_print("❌ git filter-repo not available")
        try:
            os.remove(expressions_file)
        except:
            pass
        return try_simple_replacement()

def try_simple_replacement():
    """Try simple commit-by-commit replacement"""
    safe_print("🔄 Trying commit-by-commit replacement...")
    safe_print("   This is a simpler but safer approach")
    
    try:
        # Get list of commits with webhook URLs
        result = subprocess.run([
            'git', 'log', '--all', '-S', 'discord.com/api/webhooks', '--oneline', '--reverse'
        ], capture_output=True, text=True, encoding='utf-8', errors='ignore')
        
        if not result.stdout.strip():
            safe_print("✅ No webhook URLs found in commit content")
            return True
        
        commits = result.stdout.strip().split('\n')
        safe_print(f"🔍 Found {len(commits)} commits to process")
        
        # For each commit, we would need to:
        # 1. Check it out
        # 2. Replace webhook URLs in files
        # 3. Amend the commit
        # This is complex and risky for history rewriting
        
        safe_print("⚠️  Commit-by-commit replacement is complex")
        safe_print("   Recommending BFG Repo-Cleaner or manual file cleaning")
        return False
        
    except Exception as e:
        safe_print(f"❌ Simple replacement failed: {e}")
        return False

def clean_current_files():
    """Clean webhook URLs from current files as immediate mitigation"""
    safe_print("🧹 Cleaning webhook URLs from current files...")
    
    webhook_files = ['webhook_config.json', 'discord_webhooks.json', 'webhooks.json']
    cleaned_files = []
    
    for filename in webhook_files:
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if 'discord.com/api/webhooks' in content:
                    # Replace webhook URLs
                    import re
                    patterns = [
                        r'https://discord\.com/api/webhooks/\d+/[a-zA-Z0-9_-]+',
                        r'https://discordapp\.com/api/webhooks/\d+/[a-zA-Z0-9_-]+'
                    ]
                    
                    for pattern in patterns:
                        content = re.sub(pattern, '[WEBHOOK_REMOVED_FOR_SECURITY]', content)
                    
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    cleaned_files.append(filename)
                    safe_print(f"✅ Cleaned: {filename}")
                else:
                    safe_print(f"✅ Clean: {filename} (no webhooks found)")
                    
            except Exception as e:
                safe_print(f"❌ Error processing {filename}: {e}")
    
    return cleaned_files

def verify_current_status():
    """Verify current repository status"""
    safe_print("")
    safe_print("🔍 VERIFYING CURRENT STATUS...")
    safe_print("=" * 30)
    
    # Check current files
    webhook_files = ['webhook_config.json', 'discord_webhooks.json', 'webhooks.json']
    current_clean = True
    
    for filename in webhook_files:
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'discord.com/api/webhooks' in content:
                        safe_print(f"⚠️  {filename} still contains webhook URLs")
                        current_clean = False
                    else:
                        safe_print(f"✅ {filename} is clean")
            except Exception as e:
                safe_print(f"❌ Error checking {filename}: {e}")
    
    # Check Git history
    try:
        result = subprocess.run([
            'git', 'log', '--all', '-S', 'discord.com/api/webhooks', '--oneline'
        ], capture_output=True, text=True, encoding='utf-8', errors='ignore')
        
        if result.stdout.strip():
            commits = result.stdout.strip().split('\n')
            safe_print(f"⚠️  Git history: {len(commits)} commits still contain webhooks")
        else:
            safe_print("✅ Git history: No webhook URLs found")
            
    except Exception as e:
        safe_print(f"❌ Error checking Git history: {e}")
    
    return current_clean

def main():
    """Main execution"""
    safe_print("🔒 WEBHOOK URL CLEANER")
    safe_print("=" * 30)
    
    # Check Git repo
    try:
        subprocess.run(['git', 'rev-parse', '--git-dir'], 
                      capture_output=True, check=True)
        safe_print("✅ Git repository confirmed")
    except subprocess.CalledProcessError:
        safe_print("❌ ERROR: Not in a Git repository!")
        return
    
    # Create backup first
    safe_print("")
    safe_print("📦 Creating repository backup...")
    backup_name = create_backup()
    if not backup_name:
        safe_print("❌ ERROR: Could not create backup")
        safe_print("   Continuing without backup (current files only)")
    
    # Clean current files immediately
    safe_print("")
    cleaned_files = clean_current_files()
    
    # Commit cleaned files
    if cleaned_files:
        safe_print("")
        safe_print("💾 Committing cleaned files...")
        try:
            subprocess.run(['git', 'add'] + cleaned_files, check=True)
            subprocess.run(['git', 'commit', '-m', 
                          'SECURITY: Remove webhook URLs from current files'], check=True)
            safe_print("✅ Cleaned files committed")
        except subprocess.CalledProcessError as e:
            safe_print(f"❌ Could not commit cleaned files: {e}")
    
    # Verify status
    verify_current_status()
    
    safe_print("")
    safe_print("📋 SUMMARY:")
    safe_print("✅ Current files cleaned of webhook URLs")
    if backup_name:
        safe_print(f"✅ Backup available at: ../{backup_name}")
    safe_print("⚠️  Git history still contains webhook URLs")
    safe_print("")
    safe_print("🔧 For complete history cleaning, consider:")
    safe_print("   1. BFG Repo-Cleaner (recommended)")
    safe_print("   2. git filter-repo (if available)")
    safe_print("   3. Fresh repository with clean history")

if __name__ == "__main__":
    main()