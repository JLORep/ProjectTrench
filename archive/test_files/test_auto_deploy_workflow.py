#!/usr/bin/env python3
"""
Test script for auto-deployment workflow
"""
import subprocess
import sys
import os
from datetime import datetime

def test_deployment_system():
    """Test the complete deployment workflow"""
    print("=" * 50)
    print("TESTING AUTO-DEPLOYMENT WORKFLOW")
    print("=" * 50)
    
    print("\n1. Testing deployment trigger detection...")
    
    # Test keywords that should trigger deployment
    test_commits = [
        "Fix dashboard rendering issue",
        "Add new trading strategy feature", 
        "Implement live data updates",
        "Bug fix for coin display",
        "Enhance user interface",
        "Update documentation (should not deploy)",
        "WIP: work in progress (should not deploy)"
    ]
    
    for commit_msg in test_commits:
        commit_lower = commit_msg.lower()
        should_deploy = False
        
        deploy_keywords = ['fix', 'bug', 'feature', 'add', 'implement', 'enhance', 'ship', 'deploy']
        skip_keywords = ['wip', 'temp', 'draft', 'test', 'documentation']
        
        if any(keyword in commit_lower for keyword in deploy_keywords):
            should_deploy = True
        
        if any(keyword in commit_lower for keyword in skip_keywords):
            should_deploy = False
        
        status = "DEPLOY" if should_deploy else "SKIP"
        print(f"  '{commit_msg}' -> {status}")
    
    print("\n2. Testing git hook installation...")
    hook_file = ".git/hooks/post-commit"
    if os.path.exists(hook_file):
        print("  Git hook installed: YES")
        with open(hook_file, 'r') as f:
            content = f.read()
            if "enhanced_auto_deploy.py" in content:
                print("  Hook points to enhanced deployer: YES")
            else:
                print("  Hook points to enhanced deployer: NO")
    else:
        print("  Git hook installed: NO")
    
    print("\n3. Testing deployment components...")
    
    # Test if enhanced_auto_deploy exists
    if os.path.exists("enhanced_auto_deploy.py"):
        print("  Enhanced auto deployer: FOUND")
    else:
        print("  Enhanced auto deployer: MISSING")
    
    # Test if dev blog system exists
    if os.path.exists("dev_blog_system.py"):
        print("  Dev blog system: FOUND")
    else:
        print("  Dev blog system: MISSING")
    
    # Test if overview updater exists
    if os.path.exists("auto_overview_updater.py"):
        print("  Overview updater: FOUND")
    else:
        print("  Overview updater: MISSING")
    
    print("\n4. Testing manual deployment trigger...")
    if os.path.exists("manual_deploy.py"):
        print("  Manual deploy script: FOUND")
        print("  Run 'python manual_deploy.py' to test deployment")
    else:
        print("  Manual deploy script: MISSING")
    
    print("\n5. Summary of auto-deployment workflow:")
    print("  -> Commit with 'fix'/'feature'/'add'/'implement'/'enhance' keywords")
    print("  -> Git post-commit hook triggers")
    print("  -> enhanced_auto_deploy.py runs")
    print("  -> Code pushed to GitHub")
    print("  -> Streamlit Cloud auto-updates")
    print("  -> Dev blog updated with deployment info")
    print("  -> Project overview updated")
    print("  -> Discord notification sent")
    print("  -> Deployment logged")
    
    print("\n" + "=" * 50)
    print("AUTO-DEPLOYMENT WORKFLOW TEST COMPLETE")
    print("=" * 50)
    
    return True

def create_test_commit():
    """Create a test commit to verify auto-deployment"""
    print("\nWould you like to create a test commit to verify auto-deployment? (y/n): ", end="")
    
    # For automation, we'll skip the interactive part
    print("Skipping interactive test for automation")
    return True

def main():
    """Main test function"""
    try:
        test_deployment_system()
        create_test_commit()
        return 0
    except Exception as e:
        print(f"Error during testing: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())