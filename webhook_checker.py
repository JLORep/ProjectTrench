#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Webhook Checker - Simple scan for Discord webhooks in Git history
Windows-compatible version without Unicode issues
"""

import subprocess
import os

def main():
    """Main function"""
    print("Discord Webhook History Scanner")
    print("=" * 40)
    
    # Check if we're in a Git repo
    try:
        subprocess.run(['git', 'rev-parse', '--git-dir'], 
                      capture_output=True, check=True)
        print("Git repository detected")
    except subprocess.CalledProcessError:
        print("ERROR: Not in a Git repository!")
        return
    
    print("\nScanning Git history for Discord webhook URLs...")
    
    # Search for webhook URLs in Git history
    try:
        result = subprocess.run([
            'git', 'log', '--all', '-S', 'discord.com/api/webhooks', '--oneline'
        ], capture_output=True, text=True, encoding='utf-8', errors='ignore')
        
        if result.stdout.strip():
            commits = result.stdout.strip().split('\n')
            print(f"\nFOUND {len(commits)} commits with webhook URLs:")
            for commit_line in commits:
                if commit_line.strip():
                    parts = commit_line.split(' ', 1)
                    if len(parts) >= 2:
                        # Remove emojis and special chars for safe printing
                        safe_message = ''.join(c for c in parts[1] if ord(c) < 128)[:50]
                        print(f"   {parts[0]}: {safe_message}...")
            
            print("\nWARNING: Webhook URLs found in Git history!")
            print("RECOMMENDATION: Use git filter-repo to clean history")
        else:
            print("SUCCESS: No webhook URLs found in Git history")
    
    except Exception as e:
        print(f"ERROR scanning history: {e}")
    
    # Check current files
    print("\nChecking current files for webhooks...")
    
    webhook_files = ['webhook_config.json', 'discord_webhooks.json', 'webhooks.json']
    found_files = []
    
    for filename in webhook_files:
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'discord.com/api/webhooks' in content:
                        found_files.append(filename)
                        print(f"WARNING: {filename} contains webhook URLs")
                    else:
                        print(f"OK: {filename} is clean")
            except Exception as e:
                print(f"ERROR reading {filename}: {e}")
        else:
            print(f"INFO: {filename} not found")
    
    print("\n" + "=" * 40)
    if found_files:
        print("RESULT: Webhook files found in current directory")
    else:
        print("RESULT: No webhook files in current directory")

if __name__ == "__main__":
    main()