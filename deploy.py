#!/usr/bin/env python3
"""
🚀 TrenchCoat Pro - Unified Deployment System
Single script for all deployment needs - replaces 28+ scripts
"""

import os
import sys
import time
import subprocess
import requests
import json
from datetime import datetime
from typing import Optional, Dict, Tuple

class TrenchCoatDeployer:
    """Simple, reliable deployment for TrenchCoat Pro"""
    
    def __init__(self):
        self.app_url = "https://trenchdemo.streamlit.app"
        self.github_repo = "JLORep/ProjectTrench"
        self.main_file = "streamlit_app.py"
        self.webhook_url = self._get_webhook_url()
        
    def _get_webhook_url(self) -> Optional[str]:
        """Get Discord webhook URL from config"""
        try:
            with open('webhook_config.json', 'r') as f:
                config = json.load(f)
                return config.get('discord_webhook_url')
        except:
            return None
    
    def deploy(self, 
               environment: str = 'production',
               validate: bool = True,
               notify: bool = True) -> bool:
        """
        Main deployment function
        
        Args:
            environment: Target environment (production/staging)
            validate: Run validation checks
            notify: Send Discord notifications
            
        Returns:
            bool: True if deployment successful
        """
        print(f"\n🚀 TrenchCoat Pro Deployment - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📍 Environment: {environment}")
        print(f"✅ Validation: {'Enabled' if validate else 'Disabled'}")
        print(f"🔔 Notifications: {'Enabled' if notify else 'Disabled'}")
        print("-" * 60)
        
        # Step 1: Pre-deployment checks
        if not self._pre_deployment_checks():
            return False
            
        # Step 2: Git operations
        if not self._git_operations():
            return False
            
        # Step 3: Deploy to Streamlit Cloud
        if not self._deploy_to_streamlit():
            return False
            
        # Step 4: Post-deployment validation
        if validate:
            if not self._validate_deployment():
                self._rollback()
                return False
                
        # Step 5: Send notifications
        if notify:
            self._send_notification("success")
            
        print("\n✅ Deployment completed successfully!")
        return True
        
    def _pre_deployment_checks(self) -> bool:
        """Run pre-deployment checks"""
        print("\n🔍 Running pre-deployment checks...")
        
        # Check if main file exists
        if not os.path.exists(self.main_file):
            print(f"❌ Main file not found: {self.main_file}")
            return False
            
        # Check if database exists
        if not os.path.exists("data/trench.db"):
            print("❌ Database not found: data/trench.db")
            return False
            
        # Check git status
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Git status check failed")
            return False
            
        print("✅ Pre-deployment checks passed")
        return True
        
    def _git_operations(self) -> bool:
        """Handle git operations"""
        print("\n📤 Handling git operations...")
        
        # Check for uncommitted changes
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        
        if result.stdout.strip():
            print("📝 Uncommitted changes detected")
            # Add all changes
            subprocess.run(['git', 'add', '-A'])
            
            # Create commit message
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            commit_msg = f"Deploy: Automated deployment - {timestamp}"
            
            # Commit changes
            result = subprocess.run(['git', 'commit', '-m', commit_msg],
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print(f"❌ Git commit failed: {result.stderr}")
                return False
                
        # Push to GitHub
        print("🚀 Pushing to GitHub...")
        result = subprocess.run(['git', 'push', 'origin', 'main'],
                              capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Git push failed: {result.stderr}")
            return False
            
        print("✅ Git operations completed")
        return True
        
    def _deploy_to_streamlit(self) -> bool:
        """Deploy to Streamlit Cloud (via GitHub webhook)"""
        print("\n☁️ Deploying to Streamlit Cloud...")
        print("⏳ Waiting for Streamlit to detect changes...")
        
        # Streamlit Cloud automatically deploys from GitHub
        # We just need to wait for it to pick up the changes
        time.sleep(10)
        
        print("✅ Deployment triggered")
        return True
        
    def _validate_deployment(self) -> bool:
        """Validate the deployment"""
        print("\n🔍 Validating deployment...")
        
        # Wait for deployment to complete
        print("⏳ Waiting for deployment to complete (60 seconds)...")
        time.sleep(60)
        
        # Check if app is accessible
        try:
            response = requests.get(self.app_url, timeout=30)
            if response.status_code == 200:
                print(f"✅ App is accessible: {self.app_url}")
                
                # Check for key elements
                if "TrenchCoat Pro" in response.text:
                    print("✅ App content verified")
                else:
                    print("⚠️ App content may be incorrect")
                    
                return True
            else:
                print(f"❌ App returned status code: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to access app: {e}")
            return False
            
    def _rollback(self):
        """Rollback to previous version"""
        print("\n⏮️ Rolling back deployment...")
        
        # Reset to previous commit
        subprocess.run(['git', 'reset', '--hard', 'HEAD~1'])
        subprocess.run(['git', 'push', '--force', 'origin', 'main'])
        
        print("✅ Rollback completed")
        
    def _send_notification(self, status: str):
        """Send Discord notification"""
        if not self.webhook_url:
            return
            
        print(f"\n📢 Sending {status} notification...")
        
        emoji = "✅" if status == "success" else "❌"
        color = 0x00ff00 if status == "success" else 0xff0000
        
        embed = {
            "embeds": [{
                "title": f"{emoji} TrenchCoat Pro Deployment",
                "description": f"Deployment {status}",
                "color": color,
                "fields": [
                    {"name": "Environment", "value": "Production", "inline": True},
                    {"name": "URL", "value": self.app_url, "inline": True},
                    {"name": "Time", "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "inline": True}
                ]
            }]
        }
        
        try:
            requests.post(self.webhook_url, json=embed)
            print("✅ Notification sent")
        except:
            print("⚠️ Failed to send notification")

def main():
    """Main entry point"""
    deployer = TrenchCoatDeployer()
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--no-validate":
            deployer.deploy(validate=False)
        elif sys.argv[1] == "--no-notify":
            deployer.deploy(notify=False)
        elif sys.argv[1] == "--quick":
            deployer.deploy(validate=False, notify=False)
        else:
            print("Usage: python deploy.py [--no-validate] [--no-notify] [--quick]")
            sys.exit(1)
    else:
        # Default: full deployment with validation and notifications
        deployer.deploy()

if __name__ == "__main__":
    main()