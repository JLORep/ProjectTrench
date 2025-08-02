#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Webhook Scanner - Check Git history for Discord webhooks
Handles Unicode and Windows encoding issues
"""

import subprocess
import re
import os

def scan_git_history_for_webhooks():
    """Simple scan for webhook URLs in Git history"""
    print("🔍 Scanning Git history for Discord webhook URLs...")
    
    webhook_patterns = [
        r'https://discord\.com/api/webhooks/\d+/[a-zA-Z0-9_-]+',
        r'https://discordapp\.com/api/webhooks/\d+/[a-zA-Z0-9_-]+',
    ]
    
    found_webhooks = []
    
    try:
        # Search for webhook URLs in all commits
        for pattern in webhook_patterns:
            result = subprocess.run([
                'git', 'log', '--all', '--grep=' + pattern, '--oneline'
            ], capture_output=True, text=True, encoding='utf-8', errors='ignore')
            
            if result.stdout.strip():
                commits = result.stdout.strip().split('\n')
                for commit_line in commits:
                    if commit_line.strip():
                        parts = commit_line.split(' ', 1)
                        if len(parts) >= 2:
                            found_webhooks.append({
                                'hash': parts[0],
                                'message': parts[1][:50] + "..." if len(parts[1]) > 50 else parts[1]
                            })
        
        # Also search file content in history
        result = subprocess.run([
            'git', 'log', '--all', '-S', 'discord.com/api/webhooks', '--oneline'
        ], capture_output=True, text=True, encoding='utf-8', errors='ignore')
        
        if result.stdout.strip():
            commits = result.stdout.strip().split('\n')
            for commit_line in commits:
                if commit_line.strip():
                    parts = commit_line.split(' ', 1)
                    if len(parts) >= 2:
                        # Avoid duplicates
                        if not any(w['hash'] == parts[0] for w in found_webhooks):
                            found_webhooks.append({
                                'hash': parts[0],
                                'message': parts[1][:50] + "..." if len(parts[1]) > 50 else parts[1]
                            })
        
        return found_webhooks
        
    except Exception as e:
        print(f"❌ Error scanning: {e}")
        return []

def check_current_files():
    """Check current working directory for webhook files"""
    print("\n🔍 Checking current files for webhooks...")
    
    webhook_files = ['webhook_config.json', 'discord_webhooks.json', 'webhooks.json']
    found_files = []
    
    for filename in webhook_files:
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'discord.com/api/webhooks' in content:
                        found_files.append(filename)
                        print(f"⚠️  {filename} contains webhook URLs")
                    else:
                        print(f"✅ {filename} is clean")
            except Exception as e:
                print(f"❌ Error reading {filename}: {e}")
        else:
            print(f"ℹ️  {filename} not found")
    
    return found_files

def main():
    """Main function"""
    print("Discord Webhook History Scanner")
    print("=" * 40)
    
    # Check if we're in a Git repo
    try:
        subprocess.run(['git', 'rev-parse', '--git-dir'], 
                      capture_output=True, check=True)
    except subprocess.CalledProcessError:
        print("❌ Not in a Git repository!")
        return
    
    # Scan Git history
    webhook_commits = scan_git_history_for_webhooks()
    
    if webhook_commits:
        print(f"\n🚨 FOUND {len(webhook_commits)} commits with webhook URLs:")
        for commit in webhook_commits:
            print(f"   {commit['hash']}: {commit['message']}")
        print("\n❌ Webhook URLs found in Git history!")
        print("🧹 Run git filter-repo or BFG to clean history")
    else:
        print("\n✅ No webhook URLs found in Git history")
    
    # Check current files
    webhook_files = check_current_files()
    
    if webhook_files:
        print(f"\n⚠️  Current files with webhooks: {', '.join(webhook_files)}")
    else:
        print("\n✅ No webhook files in current directory")

if __name__ == "__main__":
    main()