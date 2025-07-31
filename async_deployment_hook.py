#!/usr/bin/env python3
"""
TrenchCoat Pro - Truly Async Deployment Hook
Exits immediately after triggering background deployment
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
    deploy_keywords = ['fix', 'bug', 'feature', 'add', 'implement', 'enhance']
    
    # Skip keywords
    skip_keywords = ['wip', 'temp', 'draft', 'test:', 'deployment hook']
    
    # Check if should deploy
    should = any(keyword in msg_lower for keyword in deploy_keywords)
    
    # Check if should skip
    should_skip = any(keyword in msg_lower for keyword in skip_keywords)
    
    return should and not should_skip

def trigger_async_deployment(commit_hash: str, commit_msg: str):
    """Trigger deployment in completely separate process"""
    project_dir = Path.cwd()
    log_file = project_dir / "async_deployment.log"
    
    # Log the trigger
    with open(log_file, 'a') as f:
        f.write(f"[{datetime.now().isoformat()}] ASYNC TRIGGER: {commit_hash} - {commit_msg}\n")
    
    # Create deployment script that runs independently
    deploy_script = f'''
import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path

# Change to project directory
os.chdir(r"{project_dir}")

# Log start
log_file = Path(r"{log_file}")
with open(log_file, 'a') as f:
    f.write(f"[{{datetime.now().isoformat()}}] ASYNC START: Background deployment for {commit_hash}\\n")

try:
    # Run deployment with timeout
    result = subprocess.run([
        sys.executable, "enhanced_auto_deploy.py"
    ], timeout=300, capture_output=True, text=True)
    
    # Log result
    with open(log_file, 'a') as f:
        if result.returncode == 0:
            f.write(f"[{{datetime.now().isoformat()}}] ASYNC SUCCESS: Deployment completed for {commit_hash}\\n")
        else:
            f.write(f"[{{datetime.now().isoformat()}}] ASYNC FAILED: Deployment failed for {commit_hash} (exit {result.returncode})\\n")
            f.write(f"STDERR: {{result.stderr[:500]}}\\n")
            
except subprocess.TimeoutExpired:
    with open(log_file, 'a') as f:
        f.write(f"[{{datetime.now().isoformat()}}] ASYNC TIMEOUT: Deployment timed out for {commit_hash}\\n")
except Exception as e:
    with open(log_file, 'a') as f:
        f.write(f"[{{datetime.now().isoformat()}}] ASYNC ERROR: {{e}}\\n")
'''
    
    # Write deployment script to temp file
    temp_script = project_dir / "temp_async_deploy.py"
    temp_script.write_text(deploy_script)
    
    # Start completely independent process
    if os.name == 'nt':  # Windows
        # Use start command to detach process
        subprocess.Popen([
            'cmd', '/c', 'start', '/b', 
            sys.executable, str(temp_script)
        ], creationflags=subprocess.DETACHED_PROCESS)
    else:  # Unix
        # Use nohup to detach process
        subprocess.Popen([
            'nohup', sys.executable, str(temp_script)
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

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
            safe_print(f"ASYNC DEPLOY: Triggering for {commit_hash}")
            trigger_async_deployment(commit_hash, commit_msg)
            safe_print("ASYNC DEPLOY: Background process started")
        else:
            safe_print("ASYNC DEPLOY: Skipping deployment")
        
        # Exit immediately - this is key!
        return 0
        
    except Exception as e:
        safe_print(f"ASYNC DEPLOY ERROR: {e}")
        return 0  # Don't fail the commit

if __name__ == "__main__":
    sys.exit(main())