#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Execute Webhook Scrubbing - Automated execution with backup
"""

import subprocess
import tempfile
import os
from datetime import datetime
from unicode_handler import safe_print

def create_backup():
    """Create backup of repository"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"git_backup_{timestamp}"
    
    try:
        # Clone current repo as backup
        subprocess.run(['git', 'clone', '.', f'../{backup_name}'], check=True)
        safe_print(f"✅ Backup created: ../{backup_name}")
        return backup_name
    except subprocess.CalledProcessError as e:
        safe_print(f"❌ Could not create backup: {e}")
        return None

def create_filter_script():
    """Create filter script for git filter-branch"""
    
    script_content = '''#!/bin/bash
# Replace Discord webhook URLs with security placeholder

# Process all files in the commit
find . -type f -name "*.json" -o -name "*.py" -o -name "*.md" | while read file; do
    if [ -f "$file" ]; then
        # Replace webhook URLs with sed
        sed -i 's|https://discord\\.com/api/webhooks/[0-9]*/[A-Za-z0-9_-]*|[WEBHOOK_REMOVED_FOR_SECURITY]|g' "$file"
        sed -i 's|https://discordapp\\.com/api/webhooks/[0-9]*/[A-Za-z0-9_-]*|[WEBHOOK_REMOVED_FOR_SECURITY]|g' "$file"
    fi
done

# Handle webhook config files specifically
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
    
    # Make executable
    os.chmod(script_path, 0o755)
    return script_path

def execute_git_filter_branch(script_path):
    """Execute git filter-branch to clean webhook URLs"""
    
    safe_print("🧹 Executing git filter-branch to remove webhook URLs...")
    safe_print("⚠️  This will rewrite all Git history!")
    
    try:
        # Run git filter-branch
        cmd = [
            'git', 'filter-branch', 
            '--tree-filter', f'bash {script_path}',
            '--all', '--force'
        ]
        
        safe_print("Running git filter-branch (this may take several minutes)...")
        result = subprocess.run(cmd, capture_output=True, text=True, 
                              encoding='utf-8', errors='ignore')
        
        if result.returncode == 0:
            safe_print("✅ git filter-branch completed successfully")
            
            # Clean up Git references
            safe_print("🧹 Cleaning up Git references...")
            
            # Remove original refs
            subprocess.run(['git', 'for-each-ref', '--format=delete %(refname)', 
                          'refs/original/'], capture_output=True)
            
            # Update ref to remove original
            subprocess.run(['git', 'update-ref', '-d', 'refs/original/refs/heads/main'], 
                         capture_output=True, errors='ignore')
            
            # Expire reflog
            subprocess.run(['git', 'reflog', 'expire', '--expire=now', '--all'], 
                         capture_output=True)
            
            # Garbage collect
            subprocess.run(['git', 'gc', '--prune=now', '--aggressive'], 
                         capture_output=True)
            
            return True
        else:
            safe_print(f"❌ git filter-branch failed:")
            safe_print(f"   Error: {result.stderr}")
            return False
            
    except Exception as e:
        safe_print(f"❌ Filter branch execution failed: {e}")
        return False

def verify_cleanup():
    """Verify webhook URLs were removed"""
    safe_print("")
    safe_print("🔍 VERIFYING WEBHOOK CLEANUP...")
    safe_print("=" * 35)
    
    try:
        # Search for remaining webhook URLs
        result = subprocess.run([
            'git', 'log', '--all', '-S', 'discord.com/api/webhooks', '--oneline'
        ], capture_output=True, text=True, encoding='utf-8', errors='ignore')
        
        if result.stdout.strip():
            remaining_commits = result.stdout.strip().split('\n')
            safe_print(f"⚠️  WARNING: {len(remaining_commits)} commits still contain webhooks")
            for commit in remaining_commits[:3]:  # Show first 3
                if commit.strip():
                    parts = commit.split(' ', 1)
                    if len(parts) >= 2:
                        safe_message = ''.join(c for c in parts[1] if ord(c) < 128)[:40]
                        safe_print(f"   {parts[0]}: {safe_message}...")
            return False
        else:
            safe_print("✅ SUCCESS: No webhook URLs found in Git history")
            return True
            
    except Exception as e:
        safe_print(f"❌ Verification error: {e}")
        return False

def main():
    """Main execution"""
    safe_print("🚨 DISCORD WEBHOOK HISTORY SCRUBBER")
    safe_print("=" * 40)
    safe_print("⚠️  WARNING: This WILL rewrite Git history!")
    safe_print("⚠️  All team members will need to re-clone!")
    safe_print("")
    
    # Check Git repo
    try:
        subprocess.run(['git', 'rev-parse', '--git-dir'], 
                      capture_output=True, check=True)
        safe_print("✅ Git repository confirmed")
    except subprocess.CalledProcessError:
        safe_print("❌ ERROR: Not in a Git repository!")
        return
    
    # Create backup
    safe_print("")
    safe_print("📦 Creating repository backup...")
    backup_name = create_backup()
    if not backup_name:
        safe_print("❌ ERROR: Could not create backup. ABORTING.")
        return
    
    # Create filter script
    safe_print("")
    safe_print("📝 Creating filter script...")
    script_path = create_filter_script()
    safe_print("✅ Filter script created")
    
    try:
        # Execute filter-branch
        safe_print("")
        success = execute_git_filter_branch(script_path)
        
        if success:
            # Verify results
            if verify_cleanup():
                safe_print("")
                safe_print("🎉 SUCCESS: Git history scrubbing completed!")
                safe_print(f"📦 Backup available at: ../{backup_name}")
                safe_print("")
                safe_print("📋 NEXT STEPS:")
                safe_print("1. git push --force-with-lease origin main")
                safe_print("2. Notify team about history rewrite") 
                safe_print("3. Team members need to re-clone repository")
                safe_print("")
                safe_print("🔒 All Discord webhook URLs have been removed from Git history!")
            else:
                safe_print("⚠️  WARNING: Some webhook URLs may still remain")
                safe_print("   Manual review recommended")
        else:
            safe_print("❌ ERROR: History scrubbing failed")
            safe_print(f"   Backup available at: ../{backup_name}")
            
    finally:
        # Clean up script file
        try:
            os.unlink(script_path)
        except:
            pass

if __name__ == "__main__":
    main()