#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Webhook URL Replacer - Replace webhook URLs in Git history
Uses git filter-branch (built-in Git command)
"""

import subprocess
import tempfile
import os
import shutil
from datetime import datetime

def create_backup():
    """Create backup of repository"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"git_backup_{timestamp}"
    
    try:
        # Clone current repo as backup
        subprocess.run(['git', 'clone', '.', f'../{backup_name}'], check=True)
        print(f"SUCCESS: Backup created at ../{backup_name}")
        return backup_name
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Could not create backup: {e}")
        return None

def create_filter_script():
    """Create sed script to replace webhook URLs"""
    
    script_content = '''#!/bin/bash
# Replace Discord webhook URLs with placeholder text

# Process all files in the commit
find . -type f -name "*.json" -o -name "*.py" -o -name "*.md" | while read file; do
    if [ -f "$file" ]; then
        # Replace webhook URLs
        sed -i.bak 's|https://discord\.com/api/webhooks/[0-9]*/[A-Za-z0-9_-]*|[WEBHOOK_REMOVED_FOR_SECURITY]|g' "$file"
        sed -i.bak 's|https://discordapp\.com/api/webhooks/[0-9]*/[A-Za-z0-9_-]*|[WEBHOOK_REMOVED_FOR_SECURITY]|g' "$file"
        
        # Remove backup files
        rm -f "$file.bak"
    fi
done

# Handle specific webhook config files
if [ -f "webhook_config.json" ]; then
    cat > webhook_config.json << 'EOF'
{
  "webhooks": {
    "overview": "[WEBHOOK_REMOVED_FOR_SECURITY]",
    "dev-blog": "[WEBHOOK_REMOVED_FOR_SECURITY]", 
    "deployments": "[WEBHOOK_REMOVED_FOR_SECURITY]",
    "signals": "[WEBHOOK_REMOVED_FOR_SECURITY]"
  },
  "note": "Webhooks removed for security. Configure locally as needed."
}
EOF
fi
'''
    
    # Create temporary script file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
        f.write(script_content)
        script_path = f.name
    
    # Make executable (Windows compatible)
    os.chmod(script_path, 0o755)
    return script_path

def execute_filter_branch(script_path):
    """Execute git filter-branch to rewrite history"""
    
    print("Executing git filter-branch to clean webhook URLs...")
    print("This may take several minutes...")
    
    try:
        # Run git filter-branch
        cmd = [
            'git', 'filter-branch', 
            '--tree-filter', f'bash {script_path}',
            '--all'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, 
                              encoding='utf-8', errors='ignore')
        
        if result.returncode == 0:
            print("SUCCESS: git filter-branch completed")
            
            # Clean up Git references
            print("Cleaning up Git references...")
            
            # Remove original refs
            subprocess.run(['git', 'for-each-ref', '--format=delete %(refname)', 
                          'refs/original/'], capture_output=True)
            
            # Expire reflog
            subprocess.run(['git', 'reflog', 'expire', '--expire=now', '--all'], 
                         capture_output=True)
            
            # Garbage collect
            subprocess.run(['git', 'gc', '--prune=now'], capture_output=True)
            
            return True
        else:
            print(f"ERROR: git filter-branch failed")
            print(f"STDERR: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"ERROR: Filter branch execution failed: {e}")
        return False

def verify_cleanup():
    """Verify webhook URLs were removed"""
    print("\nVerifying webhook cleanup...")
    
    try:
        # Search for remaining webhook URLs
        result = subprocess.run([
            'git', 'log', '--all', '-S', 'discord.com/api/webhooks', '--oneline'
        ], capture_output=True, text=True, encoding='utf-8', errors='ignore')
        
        if result.stdout.strip():
            remaining_commits = result.stdout.strip().split('\n')
            print(f"WARNING: {len(remaining_commits)} commits still contain webhooks")
            for commit in remaining_commits[:5]:  # Show first 5
                if commit.strip():
                    parts = commit.split(' ', 1)
                    if len(parts) >= 2:
                        safe_message = ''.join(c for c in parts[1] if ord(c) < 128)[:40]
                        print(f"   {parts[0]}: {safe_message}...")
            return False
        else:
            print("SUCCESS: No webhook URLs found in Git history")
            return True
            
    except Exception as e:
        print(f"ERROR during verification: {e}")
        return False

def main():
    """Main execution"""
    print("Discord Webhook History Cleaner")
    print("=" * 40)
    
    # Check Git repo
    try:
        subprocess.run(['git', 'rev-parse', '--git-dir'], 
                      capture_output=True, check=True)
    except subprocess.CalledProcessError:
        print("ERROR: Not in a Git repository!")
        return
    
    print("WARNING: This will rewrite Git history!")
    print("WARNING: All team members will need to re-clone the repository!")
    
    # Create backup
    backup_name = create_backup()
    if not backup_name:
        print("ERROR: Could not create backup. Aborting.")
        return
    
    # Get user confirmation
    confirm = input("\nType 'YES' to proceed with history rewriting: ")
    if confirm != 'YES':
        print("Aborted.")
        return
    
    # Create filter script
    script_path = create_filter_script()
    
    try:
        # Execute filter-branch
        success = execute_filter_branch(script_path)
        
        if success:
            # Verify results
            if verify_cleanup():
                print("\nSUCCESS: Webhook URLs removed from Git history!")
                print(f"Backup available at: ../{backup_name}")
                print("\nNext steps:")
                print("1. git push --force-with-lease origin main")
                print("2. Notify team about history rewrite") 
                print("3. Team members need to re-clone repository")
            else:
                print("WARNING: Some webhook URLs may still remain")
        else:
            print("ERROR: History cleaning failed")
            
    finally:
        # Clean up script file
        try:
            os.unlink(script_path)
        except:
            pass

if __name__ == "__main__":
    main()