#!/usr/bin/env python3
"""
TrenchCoat Pro - Mandatory Deployment System
ALWAYS deploy every change - no exceptions
"""
import subprocess
import sys
import os
from datetime import datetime
from enhanced_auto_deploy import EnhancedAutoDeployer

class MandatoryDeploymentEnforcer:
    """Enforces mandatory deployment for every change"""
    
    def __init__(self):
        self.deployer = EnhancedAutoDeployer()
        self.force_deploy = True  # ALWAYS deploy
        
    def check_for_changes(self) -> bool:
        """Check if there are any uncommitted changes"""
        try:
            # Check working directory
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True, text=True, check=True
            )
            
            has_changes = bool(result.stdout.strip())
            
            if has_changes:
                print("[MANDATORY] 🚨 Uncommitted changes detected!")
                print("[MANDATORY] 📋 Changed files:")
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        print(f"   {line}")
                
                return True
            else:
                print("[MANDATORY] ✅ No uncommitted changes")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to check git status: {e}")
            return False
    
    def check_unpushed_commits(self) -> bool:
        """Check if there are unpushed commits"""
        try:
            # Check if ahead of origin
            result = subprocess.run(
                ["git", "rev-list", "--count", "origin/main..HEAD"],
                capture_output=True, text=True, check=True
            )
            
            unpushed_count = int(result.stdout.strip())
            
            if unpushed_count > 0:
                print(f"[MANDATORY] 🚨 {unpushed_count} unpushed commits detected!")
                
                # Show unpushed commits
                result = subprocess.run(
                    ["git", "log", "--oneline", f"origin/main..HEAD"],
                    capture_output=True, text=True, check=True
                )
                
                print("[MANDATORY] 📋 Unpushed commits:")
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        print(f"   {line}")
                
                return True
            else:
                print("[MANDATORY] ✅ No unpushed commits")
                return False
                
        except subprocess.CalledProcessError:
            # If we can't check, assume we need to deploy
            print("[MANDATORY] ⚠️ Cannot check unpushed commits - assuming deployment needed")
            return True
    
    def auto_commit_changes(self) -> bool:
        """Auto-commit any uncommitted changes"""
        try:
            print("[MANDATORY] 🔄 Auto-committing changes...")
            
            # Add all tracked files
            subprocess.run(["git", "add", "-u"], check=True)
            
            # Check if there are actually staged changes
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                capture_output=True, text=True, check=True
            )
            
            if result.stdout.strip():
                # Create auto-commit message
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M UTC')
                commit_msg = f"Auto-commit: Mandatory deployment - {timestamp}\n\n🤖 Generated with [Claude Code](https://claude.ai/code)\n\nCo-Authored-By: Claude <noreply@anthropic.com>"
                
                subprocess.run(["git", "commit", "-m", commit_msg], check=True)
                print("[MANDATORY] ✅ Changes auto-committed successfully")
                return True
            else:
                print("[MANDATORY] ℹ️ No staged changes to commit")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Auto-commit failed: {e}")
            return False
    
    def enforce_mandatory_deployment(self) -> bool:
        """Main enforcement method - ALWAYS deploy if needed"""
        print("=" * 70)
        print("🚨 MANDATORY DEPLOYMENT ENFORCER 🚨")
        print("EVERY CHANGE MUST BE DEPLOYED - NO EXCEPTIONS")
        print("=" * 70)
        
        needs_deployment = False
        
        # Check for uncommitted changes
        if self.check_for_changes():
            needs_deployment = True
            print("[MANDATORY] 🔄 Auto-committing changes...")
            if not self.auto_commit_changes():
                print("[ERROR] Failed to auto-commit changes")
                return False
        
        # Check for unpushed commits
        if self.check_unpushed_commits():
            needs_deployment = True
        
        # Force deployment if any changes detected
        if needs_deployment or self.force_deploy:
            print("[MANDATORY] 🚀 INITIATING MANDATORY DEPLOYMENT...")
            print("[MANDATORY] ⚠️  This is MANDATORY - deployment cannot be skipped!")
            
            success = self.deployer.run_enhanced_deployment()
            
            if success:
                print("\n[MANDATORY] ✅ MANDATORY DEPLOYMENT COMPLETED SUCCESSFULLY!")
                print("[MANDATORY] 🎯 All changes are now live in production")
                return True
            else:
                print("\n[MANDATORY] ❌ MANDATORY DEPLOYMENT FAILED!")
                print("[MANDATORY] 🚨 This is a CRITICAL issue - must be resolved immediately")
                return False
        else:
            print("[MANDATORY] ✅ No deployment needed - repository is up to date")
            return True

def main():
    """Run mandatory deployment enforcement"""
    enforcer = MandatoryDeploymentEnforcer()
    success = enforcer.enforce_mandatory_deployment()
    
    if not success:
        print("\n🚨 CRITICAL: MANDATORY DEPLOYMENT FAILED!")
        print("🚨 ALL DEVELOPMENT MUST STOP UNTIL THIS IS RESOLVED!")
        sys.exit(1)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())