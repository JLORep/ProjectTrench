#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git History Scrubber - Remove sensitive data from all commits

CRITICAL SECURITY: Removes Discord webhook URLs and other sensitive data
from entire Git commit history.

⚠️ WARNING: This rewrites Git history. Make backup first!

Usage:
    python scrub_git_history.py --dry-run    # Preview changes
    python scrub_git_history.py --execute    # Actually clean history
"""

import os
import sys
import subprocess
import tempfile
import json
import re
from datetime import datetime

class GitHistoryScrubber:
    """Remove sensitive data from entire Git history"""
    
    def __init__(self):
        self.webhook_patterns = [
            r'https://discord\.com/api/webhooks/\d+/[a-zA-Z0-9_-]+',
            r'https://discordapp\.com/api/webhooks/\d+/[a-zA-Z0-9_-]+',
            r'"webhooks":\s*{[^}]*"[^"]*":\s*"https://discord[^"]*"[^}]*}',
        ]
        
        self.sensitive_patterns = [
            r'webhook_config\.json',
            r'"overview":\s*"https://discord\.com[^"]*"',
            r'"dev-blog":\s*"https://discord\.com[^"]*"',
            r'"deployments":\s*"https://discord\.com[^"]*"',
            r'"signals":\s*"https://discord\.com[^"]*"',
        ]
        
        self.files_to_scrub = [
            'webhook_config.json',
            'discord_webhooks.json',
            'webhooks.json',
        ]
    
    def check_git_repo(self) -> bool:
        """Verify we're in a Git repository"""
        try:
            result = subprocess.run(['git', 'rev-parse', '--git-dir'], 
                                 capture_output=True, text=True, check=True)
            return True
        except subprocess.CalledProcessError:
            print("❌ Not in a Git repository!")
            return False
    
    def backup_repository(self) -> str:
        """Create backup of repository before scrubbing"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"git_backup_{timestamp}"
        
        try:
            # Create backup directory
            subprocess.run(['git', 'clone', '.', f'../{backup_name}'], check=True)
            print(f"✅ Backup created: ../{backup_name}")
            return backup_name
        except subprocess.CalledProcessError as e:
            print(f"❌ Backup failed: {e}")
            return None
    
    def find_sensitive_commits(self) -> list:
        """Find all commits containing sensitive data"""
        sensitive_commits = []
        
        try:
            # Get all commits
            result = subprocess.run(['git', 'log', '--all', '--oneline', '--grep=webhook', '-i'], 
                                  capture_output=True, text=True)
            
            webhook_commits = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            # Also check for commits that modified sensitive files
            for filename in self.files_to_scrub:
                try:
                    result = subprocess.run(['git', 'log', '--all', '--oneline', '--', filename], 
                                          capture_output=True, text=True)
                    file_commits = result.stdout.strip().split('\n') if result.stdout.strip() else []
                    webhook_commits.extend(file_commits)
                except subprocess.CalledProcessError:
                    continue
            
            # Parse commit info
            for commit_line in webhook_commits:
                if commit_line and commit_line.strip():
                    parts = commit_line.split(' ', 1)
                    if len(parts) >= 2:
                        commit_hash = parts[0]
                        commit_msg = parts[1]
                        sensitive_commits.append({
                            'hash': commit_hash,
                            'message': commit_msg,
                            'short_hash': commit_hash[:8]
                        })
            
            # Remove duplicates
            seen = set()
            unique_commits = []
            for commit in sensitive_commits:
                if commit['hash'] not in seen:
                    seen.add(commit['hash'])
                    unique_commits.append(commit)
            
            return unique_commits
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error finding sensitive commits: {e}")
            return []
    
    def scan_commit_for_webhooks(self, commit_hash: str) -> dict:
        """Scan specific commit for webhook URLs"""
        found_webhooks = {
            'urls': [],
            'files': [],
            'patterns': []
        }
        
        try:
            # Get commit content
            result = subprocess.run(['git', 'show', commit_hash], 
                                  capture_output=True, text=True)
            commit_content = result.stdout
            
            # Find webhook URLs
            for pattern in self.webhook_patterns:
                matches = re.findall(pattern, commit_content)
                found_webhooks['urls'].extend(matches)
                if matches:
                    found_webhooks['patterns'].append(pattern)
            
            # Find sensitive files
            for filename in self.files_to_scrub:
                if filename in commit_content:
                    found_webhooks['files'].append(filename)
            
            return found_webhooks
            
        except subprocess.CalledProcessError:
            return found_webhooks
    
    def create_filter_script(self) -> str:
        """Create git filter script to remove sensitive data"""
        
        filter_script = '''#!/bin/bash
# Git filter script to remove Discord webhooks and sensitive data

# Input file
file="$1"

# Skip if file doesn't exist
if [ ! -f "$file" ]; then
    exit 0
fi

# Remove webhook URLs
sed -i 's|https://discord\.com/api/webhooks/[0-9]*/[A-Za-z0-9_-]*|[WEBHOOK_REMOVED_FOR_SECURITY]|g' "$file"
sed -i 's|https://discordapp\.com/api/webhooks/[0-9]*/[A-Za-z0-9_-]*|[WEBHOOK_REMOVED_FOR_SECURITY]|g' "$file"

# Remove sensitive file content
if [[ "$file" == *"webhook_config.json"* ]]; then
    # Replace entire webhook config with safe template
    cat > "$file" << 'EOF'
{
  "webhooks": {
    "overview": "[WEBHOOK_REMOVED_FOR_SECURITY]",
    "dev-blog": "[WEBHOOK_REMOVED_FOR_SECURITY]", 
    "deployments": "[WEBHOOK_REMOVED_FOR_SECURITY]",
    "signals": "[WEBHOOK_REMOVED_FOR_SECURITY]"
  },
  "note": "Webhooks removed for security. Use setup_discord_webhooks.py to configure locally."
}
EOF
fi

exit 0
'''
        
        # Create temporary filter script
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
            f.write(filter_script)
            script_path = f.name
        
        # Make executable
        os.chmod(script_path, 0o755)
        return script_path
    
    def dry_run_analysis(self) -> dict:
        """Analyze what would be removed (dry run)"""
        print("ANALYZING REPOSITORY FOR SENSITIVE DATA")
        print("=" * 50)
        
        analysis = {
            'sensitive_commits': [],
            'webhook_urls_found': 0,
            'files_affected': set(),
            'total_commits_to_rewrite': 0
        }
        
        # Find sensitive commits
        sensitive_commits = self.find_sensitive_commits()
        analysis['total_commits_to_rewrite'] = len(sensitive_commits)
        
        print(f"Found {len(sensitive_commits)} commits with potential sensitive data:")
        print()
        
        for commit in sensitive_commits:
            print(f"COMMIT {commit['short_hash']}: {commit['message'][:60]}...")
            
            # Scan commit for actual webhook content
            webhook_data = self.scan_commit_for_webhooks(commit['hash'])
            
            commit_analysis = {
                'hash': commit['hash'],
                'message': commit['message'],
                'webhook_urls': len(webhook_data['urls']),
                'sensitive_files': webhook_data['files']
            }
            
            analysis['sensitive_commits'].append(commit_analysis)
            analysis['webhook_urls_found'] += len(webhook_data['urls'])
            analysis['files_affected'].update(webhook_data['files'])
            
            if webhook_data['urls']:
                print(f"   ALERT: Found {len(webhook_data['urls'])} webhook URLs")
            if webhook_data['files']:
                print(f"   FILES: Affected files: {', '.join(webhook_data['files'])}")
            print()
        
        print("=" * 50)
        print("ANALYSIS SUMMARY:")
        print(f"Total commits to rewrite: {analysis['total_commits_to_rewrite']}")
        print(f"Total webhook URLs found: {analysis['webhook_urls_found']}")
        print(f"Affected files: {', '.join(analysis['files_affected']) if analysis['files_affected'] else 'None'}")
        
        return analysis
    
    def execute_scrubbing(self, backup_name: str) -> bool:
        """Execute the actual Git history rewriting"""
        print("🧹 EXECUTING GIT HISTORY SCRUBBING")
        print("=" * 40)
        print("⚠️  WARNING: This will rewrite Git history!")
        print("⚠️  Backup created at:", f"../{backup_name}")
        print()
        
        try:
            # Method 1: Use git filter-repo (preferred if available)
            print("Attempting git filter-repo...")
            
            # Create expressions file for git filter-repo
            expressions = [
                "regex:https://discord\\.com/api/webhooks/\\d+/[a-zA-Z0-9_-]+==>[WEBHOOK_REMOVED_FOR_SECURITY]",
                "regex:https://discordapp\\.com/api/webhooks/\\d+/[a-zA-Z0-9_-]+==>[WEBHOOK_REMOVED_FOR_SECURITY]"
            ]
            
            expressions_file = 'webhook_expressions.txt'
            with open(expressions_file, 'w') as f:
                for expr in expressions:
                    f.write(expr + '\n')
            
            try:
                # Try git filter-repo
                result = subprocess.run([
                    'git', 'filter-repo',
                    '--replace-text', expressions_file,
                    '--force'
                ], capture_output=True, text=True, check=True)
                
                print("✅ git filter-repo completed successfully")
                os.remove(expressions_file)
                return True
                
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("git filter-repo not available, trying git filter-branch...")
                os.remove(expressions_file)
                
                # Method 2: Use git filter-branch (fallback)
                return self.filter_branch_scrub()
                
        except Exception as e:
            print(f"❌ Scrubbing failed: {e}")
            return False
    
    def filter_branch_scrub(self) -> bool:
        """Use git filter-branch to scrub history"""
        try:
            # Create filter script
            script_path = self.create_filter_script()
            
            # Run git filter-branch
            cmd = [
                'git', 'filter-branch', 
                '--tree-filter', f'{script_path} "$GIT_COMMIT"',
                '--all'
            ]
            
            print("Running git filter-branch...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Clean up
            os.unlink(script_path)
            
            if result.returncode == 0:
                print("✅ git filter-branch completed")
                
                # Force garbage collection
                subprocess.run(['git', 'for-each-ref', '--format=delete %(refname)', 'refs/original/'], 
                             capture_output=True)
                subprocess.run(['git', 'update-ref', '-d', 'refs/original/refs/heads/main'], 
                             capture_output=True)
                subprocess.run(['git', 'reflog', 'expire', '--expire=now', '--all'], 
                             capture_output=True)
                subprocess.run(['git', 'gc', '--prune=now', '--aggressive'], 
                             capture_output=True)
                
                return True
            else:
                print(f"❌ git filter-branch failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ filter-branch scrubbing failed: {e}")
            return False
    
    def verify_scrubbing(self) -> bool:
        """Verify that scrubbing was successful"""
        print("\n🔍 VERIFYING SCRUBBING RESULTS")
        print("=" * 35)
        
        try:
            # Check if any webhook URLs remain
            result = subprocess.run(['git', 'log', '--all', '-S', 'discord.com/api/webhooks'], 
                                  capture_output=True, text=True)
            
            if result.stdout.strip():
                print("❌ Webhook URLs still found in history!")
                return False
            else:
                print("✅ No webhook URLs found in Git history")
                
            # Check current working directory
            webhook_files = ['webhook_config.json', 'discord_webhooks.json']
            for filename in webhook_files:
                if os.path.exists(filename):
                    with open(filename, 'r') as f:
                        content = f.read()
                        if 'discord.com/api/webhooks' in content:
                            print(f"⚠️  {filename} still contains webhook URLs")
                        else:
                            print(f"✅ {filename} is clean")
                
            return True
            
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            return False
    
    def run(self, dry_run: bool = True) -> bool:
        """Main execution function"""
        
        if not self.check_git_repo():
            return False
        
        if dry_run:
            print("DRY RUN MODE - No changes will be made")
            analysis = self.dry_run_analysis()
            
            if analysis['webhook_urls_found'] > 0:
                print("\nWEBHOOKS FOUND IN HISTORY!")
                print("Run with --execute to remove them")
                return False
            else:
                print("No webhook URLs found in Git history")
                return True
        else:
            # Create backup first
            backup_name = self.backup_repository()
            if not backup_name:
                print("❌ Could not create backup. Aborting.")
                return False
            
            # Execute scrubbing
            success = self.execute_scrubbing(backup_name)
            
            if success:
                # Verify results
                if self.verify_scrubbing():
                    print("\n🎉 GIT HISTORY SCRUBBING COMPLETED!")
                    print(f"Backup available at: ../{backup_name}")
                    print("\nNext steps:")
                    print("1. git push --force-with-lease origin main")
                    print("2. Notify team about history rewrite")
                    print("3. Team members need to re-clone repository")
                    return True
                else:
                    print("❌ Scrubbing verification failed")
                    return False
            else:
                print("❌ Scrubbing failed")
                return False

def main():
    """Main function"""
    
    scrubber = GitHistoryScrubber()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python scrub_git_history.py --dry-run     # Preview what will be removed")
        print("  python scrub_git_history.py --execute     # Actually clean the history")
        return
    
    if sys.argv[1] == '--dry-run':
        scrubber.run(dry_run=True)
    elif sys.argv[1] == '--execute':
        print("⚠️  This will rewrite Git history and cannot be undone!")
        confirm = input("Type 'CONFIRM' to proceed: ")
        if confirm == 'CONFIRM':
            scrubber.run(dry_run=False)
        else:
            print("Aborted.")
    else:
        print("Invalid argument. Use --dry-run or --execute")

if __name__ == "__main__":
    main()