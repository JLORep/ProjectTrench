#!/usr/bin/env python3
"""
TrenchCoat Pro - Automated Deployment System
Automatically deploys when bugs are fixed or new features are added
"""
import subprocess
import sys
import time
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional

class AutoDeploymentSystem:
    """Automated deployment system for TrenchCoat Pro"""
    
    def __init__(self):
        self.repo_url = "https://github.com/JLORep/ProjectTrench"
        self.app_name = "trenchcoat-pro"
        self.streamlit_url = None
        self.deployment_log = []
        
    def detect_changes(self) -> Dict[str, List[str]]:
        """Detect what types of changes were made"""
        try:
            # Get the last commit message and files changed
            result = subprocess.run(
                ["git", "log", "--oneline", "-1"], 
                capture_output=True, text=True, check=True
            )
            commit_message = result.stdout.strip()
            
            # Get files changed in last commit
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
                capture_output=True, text=True, check=True
            )
            changed_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            changes = {
                'bug_fixes': [],
                'new_features': [],
                'core_changes': [],
                'config_changes': []
            }
            
            # Categorize changes based on commit message and files
            message_lower = commit_message.lower()
            
            if any(word in message_lower for word in ['fix', 'bug', 'error', 'issue', 'resolve']):
                changes['bug_fixes'].append(commit_message)
            
            if any(word in message_lower for word in ['add', 'feature', 'new', 'implement', 'enhance']):
                changes['new_features'].append(commit_message)
            
            # Categorize file changes
            for file in changed_files:
                if file.endswith('.py') and any(core in file for core in ['dashboard', 'app', 'main']):
                    changes['core_changes'].append(file)
                elif file in ['requirements.txt', 'config.toml', '.streamlit/config.toml']:
                    changes['config_changes'].append(file)
            
            return changes
            
        except subprocess.CalledProcessError as e:
            print(f"Error detecting changes: {e}")
            return {'bug_fixes': [], 'new_features': [], 'core_changes': [], 'config_changes': []}
    
    def should_auto_deploy(self, changes: Dict[str, List[str]]) -> bool:
        """Determine if changes warrant automatic deployment"""
        
        # Auto-deploy conditions:
        # 1. Bug fixes (always deploy)
        # 2. New features (always deploy) 
        # 3. Core dashboard changes (always deploy)
        # 4. Config changes (deploy if critical)
        
        auto_deploy_reasons = []
        
        if changes['bug_fixes']:
            auto_deploy_reasons.append("[BUG] Bug fixes detected")
        
        if changes['new_features']:
            auto_deploy_reasons.append("[FEATURE] New features added")
            
        if changes['core_changes']:
            auto_deploy_reasons.append("[CORE] Core system updates")
            
        if changes['config_changes']:
            auto_deploy_reasons.append("[CONFIG] Configuration updates")
        
        if auto_deploy_reasons:
            print("[DEPLOY] Auto-deployment triggered:")
            for reason in auto_deploy_reasons:
                print(f"   {reason}")
            return True
        
        return False
    
    def run_pre_deployment_tests(self) -> bool:
        """Run tests before deployment"""
        print("[TEST] Running pre-deployment tests...")
        
        try:
            # Test imports
            result = subprocess.run(
                [sys.executable, "test_imports.py"],
                capture_output=True, text=True, timeout=60
            )
            
            if "Dashboard initialized successfully" in result.stdout:
                print("   [OK] Import tests passed")
                return True
            else:
                print("   [FAIL] Import tests failed")
                print(f"   Output: {result.stdout}")
                return False
                
        except Exception as e:
            print(f"   [ERROR] Test failed: {e}")
            return False
    
    def deploy_to_streamlit_cloud(self) -> bool:
        """Deploy to Streamlit Cloud automatically"""
        print("[DEPLOY] Deploying to Streamlit Cloud...")
        
        try:
            # Check if already deployed by trying to access
            potential_urls = [
                "https://trenchcoat-pro.streamlit.app",
                "https://projecttrench.streamlit.app", 
                "https://trenchcoat.streamlit.app",
                "https://jlorep-projecttrench.streamlit.app"
            ]
            
            for url in potential_urls:
                try:
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        print(f"   [FOUND] Existing deployment: {url}")
                        self.streamlit_url = url
                        
                        # The deployment will auto-update from GitHub
                        print("   [UPDATE] Streamlit Cloud will auto-update from GitHub push")
                        time.sleep(5)  # Give it time to start updating
                        
                        return True
                except:
                    continue
            
            # If no existing deployment found, provide instructions
            print("\n[MANUAL] Manual Deployment Required:")
            print("1. Go to https://share.streamlit.io/")
            print("2. Click 'New app'")
            print(f"3. Repository: {self.repo_url}")
            print("4. Branch: main")
            print("5. Main file path: streamlit_app.py")
            print("6. App URL (optional): trenchcoat-pro")
            
            return False
            
        except Exception as e:
            print(f"   [ERROR] Deployment error: {e}")
            return False
    
    def notify_deployment_status(self, success: bool, changes: Dict[str, List[str]]):
        """Send deployment notification"""
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        
        if success:
            status_msg = "[SUCCESS] TrenchCoat Pro - Deployment Successful"
            color = "[OK]"
        else:
            status_msg = "[FAILED] TrenchCoat Pro - Deployment Failed"
            color = "[ERROR]"
        
        # Create deployment summary
        summary_parts = []
        
        if changes['bug_fixes']:
            summary_parts.append(f"[BUG] Bug Fixes: {len(changes['bug_fixes'])} resolved")
            
        if changes['new_features']:
            summary_parts.append(f"[FEATURE] New Features: {len(changes['new_features'])} added")
            
        if changes['core_changes']:
            summary_parts.append(f"[CORE] Core Updates: {len(changes['core_changes'])} files")
        
        summary = "\n".join(summary_parts) if summary_parts else "[CONFIG] Configuration updates"
        
        # Log deployment
        log_entry = {
            'timestamp': timestamp,
            'success': success,
            'changes': changes,
            'url': self.streamlit_url
        }
        self.deployment_log.append(log_entry)
        
        # Save deployment log
        try:
            with open('deployment_log.json', 'w') as f:
                json.dump(self.deployment_log, f, indent=2)
        except:
            pass
        
        print(f"\n{status_msg}")
        print(f"[TIME] {timestamp}")
        print(f"[CHANGES]\n{summary}")
        
        if success and self.streamlit_url:
            print(f"[URL] {self.streamlit_url}")
        
        print(f"[REPO] {self.repo_url}")
    
    def run_auto_deployment(self) -> bool:
        """Run the complete auto-deployment process"""
        
        print(">> TrenchCoat Pro Auto-Deployment System")
        print("=" * 50)
        
        # Step 1: Detect changes
        print("1. Detecting changes...")
        changes = self.detect_changes()
        
        # Step 2: Check if should deploy
        if not self.should_auto_deploy(changes):
            print("[INFO] No deployment-worthy changes detected")
            return False
        
        # Step 3: Run tests
        print("\n2. Running pre-deployment tests...")
        if not self.run_pre_deployment_tests():
            print("[ERROR] Tests failed - deployment aborted")
            self.notify_deployment_status(False, changes)
            return False
        
        # Step 4: Deploy
        print("\n3. Deploying to Streamlit Cloud...")
        deployment_success = self.deploy_to_streamlit_cloud()
        
        # Step 5: Notify
        print("\n4. Sending notifications...")
        self.notify_deployment_status(deployment_success, changes)
        
        return deployment_success

if __name__ == "__main__":
    # This can be called automatically after git commits
    deployer = AutoDeploymentSystem()
    success = deployer.run_auto_deployment()
    
    if success:
        print("\n[SUCCESS] Auto-deployment completed successfully!")
    else:
        print("\n[WARNING] Auto-deployment completed with issues - check logs above")