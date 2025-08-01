#!/usr/bin/env python3
"""
TrenchCoat Pro - Simple Async Hook
Triggers complete async deployment pipeline with full notifications
"""
import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path
from unicode_handler import safe_print

def should_deploy(commit_msg: str) -> bool:
    """Check if commit should trigger deployment"""
    msg_lower = commit_msg.lower()
    
    # Keywords that trigger deployment
    deploy_keywords = ['fix', 'bug', 'feature', 'add', 'implement', 'enhance', 'major', 'update', 'redesign', 'complete', 'deploy', 'deployment', 'coin', 'card', 'display', 'beautiful', 'runners']
    
    # Skip keywords  
    skip_keywords = ['wip', 'temp', 'draft', 'test:']
    
    # Check if should deploy
    should = any(keyword in msg_lower for keyword in deploy_keywords)
    
    # Check if should skip
    should_skip = any(keyword in msg_lower for keyword in skip_keywords)
    
    return should and not should_skip

def main():
    """Main hook execution"""
    try:
        # Get commit info
        git_result = subprocess.run(
            ['git', 'log', '-1', '--pretty=format:%h|%s'],
            capture_output=True, text=True, check=True, timeout=5
        )
        
        commit_hash, commit_msg = git_result.stdout.split('|', 1)
        
        # Check if should deploy
        if should_deploy(commit_msg):
            safe_print(f"ASYNC HOOK: Triggering complete deployment for {commit_hash}")
            
            # Start the complete async deployment system immediately (hidden window)
            if os.name == 'nt':  # Windows
                subprocess.Popen([
                    sys.executable, 'complete_async_deploy.py', commit_hash, commit_msg
                ], 
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS
                )
            else:  # Unix
                subprocess.Popen([
                    'nohup', sys.executable, 'complete_async_deploy.py', commit_hash, commit_msg
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            safe_print("ASYNC HOOK: Complete deployment pipeline launched in background")
        else:
            safe_print("ASYNC HOOK: Skipping deployment")
        
        # Exit immediately - this is critical!
        return 0
        
    except Exception as e:
        safe_print(f"ASYNC HOOK ERROR: {e}")
        return 0  # Don't fail the commit

if __name__ == "__main__":
    sys.exit(main())