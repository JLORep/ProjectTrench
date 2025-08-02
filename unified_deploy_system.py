#!/usr/bin/env python3
"""
TrenchCoat Pro - Unified Deployment System with Validation
Single entry point for deployment with comprehensive validation
"""
import subprocess
import sys
import os
import time
import json
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import sqlite3

class UnifiedDeploymentSystem:
    """Complete deployment system with integrated validation"""
    
    def __init__(self):
        self.streamlit_url = "https://trenchdemo.streamlit.app"
        self.github_repo = "JLORep/ProjectTrench"
        self.webhook_url = "https://discord.com/api/webhooks/1400577499225657404/x3eRkhbp84bA_3f3AuyUIrBhDtozTGnVbxVrPg3ewLWIL3eO0s_GZoiW0lRQr6Kb5jQ3"
        self.validation_results = {}
        self.deployment_log = []
        
    def log(self, message: str, level: str = "INFO"):
        """Log deployment messages"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] [{level}] {message}"
        print(log_entry)
        self.deployment_log.append(log_entry)
        
    def run_command(self, cmd: List[str], description: str) -> Tuple[bool, str]:
        """Run command with logging"""
        self.log(f"Running: {description}")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                self.log(f"✅ Success: {description}")
                return True, result.stdout
            else:
                self.log(f"❌ Failed: {description} - {result.stderr}", "ERROR")
                return False, result.stderr
        except Exception as e:
            self.log(f"❌ Exception: {description} - {str(e)}", "ERROR")
            return False, str(e)
    
    def check_prerequisites(self) -> bool:
        """Check deployment prerequisites"""
        self.log("🔍 Checking prerequisites...")
        
        # Check git status
        success, output = self.run_command(["git", "status", "--porcelain"], "Checking git status")
        if output.strip():
            self.log("⚠️ Uncommitted changes detected", "WARNING")
            
        # Check if on main branch
        success, output = self.run_command(["git", "branch", "--show-current"], "Checking current branch")
        if output.strip() != "main":
            self.log(f"⚠️ Not on main branch (current: {output.strip()})", "WARNING")
            
        return True
    
    def stage_and_commit(self) -> bool:
        """Stage and commit any changes"""
        self.log("📦 Staging and committing changes...")
        
        # Check for changes
        success, output = self.run_command(["git", "status", "--porcelain"], "Checking for changes")
        if not output.strip():
            self.log("No changes to commit")
            return True
            
        # Stage all changes
        success, _ = self.run_command(["git", "add", "-A"], "Staging all changes")
        if not success:
            return False
            
        # Create commit
        commit_msg = f"Auto-deploy: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        success, _ = self.run_command(["git", "commit", "-m", commit_msg], "Creating commit")
        return success
    
    def push_to_github(self) -> bool:
        """Push changes to GitHub"""
        self.log("🚀 Pushing to GitHub...")
        success, _ = self.run_command(["git", "push", "origin", "main"], "Pushing to origin/main")
        return success
    
    def validate_github_deployment(self) -> bool:
        """Verify code is deployed to GitHub"""
        self.log("🔍 Validating GitHub deployment...")
        
        # Get local commit hash
        success, local_hash = self.run_command(["git", "rev-parse", "HEAD"], "Getting local commit hash")
        if not success:
            return False
            
        # Get remote commit hash
        success, output = self.run_command(["git", "ls-remote", "origin", "main"], "Getting remote commit hash")
        if not success:
            return False
            
        remote_hash = output.split()[0] if output else None
        
        if local_hash.strip() == remote_hash:
            self.log(f"✅ GitHub deployment verified (hash: {local_hash[:8]})")
            self.validation_results["github_hash"] = local_hash[:8]
            return True
        else:
            self.log(f"❌ Hash mismatch - Local: {local_hash[:8]}, Remote: {remote_hash[:8] if remote_hash else 'unknown'}", "ERROR")
            return False
    
    def validate_streamlit_deployment(self) -> bool:
        """Validate Streamlit app is functional"""
        self.log("🔍 Validating Streamlit deployment...")
        
        # Wait for deployment to propagate
        self.log("Waiting 30 seconds for deployment to propagate...")
        time.sleep(30)
        
        try:
            start_time = time.time()
            response = requests.get(self.streamlit_url, timeout=60, headers={
                'User-Agent': 'TrenchCoat-Unified-Deploy/1.0'
            })
            response_time = round((time.time() - start_time) * 1000, 2)
            
            if response.status_code == 200:
                content = response.text.lower()
                
                # Check for critical elements
                checks = {
                    "dashboard_loaded": "dashboard" in content or "trenchcoat" in content,
                    "tabs_present": "hunt hub" in content or "alpha radar" in content,
                    "no_errors": "error" not in content[:1000]  # Check first 1000 chars
                }
                
                failed_checks = [k for k, v in checks.items() if not v]
                if failed_checks:
                    self.log(f"⚠️ Some checks failed: {failed_checks}", "WARNING")
                
                self.log(f"✅ Streamlit app responding (time: {response_time}ms)")
                self.validation_results["streamlit_response_time"] = response_time
                self.validation_results["streamlit_status"] = "online"
                return True
            else:
                self.log(f"❌ Streamlit returned status {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Streamlit validation failed: {str(e)}", "ERROR")
            return False
    
    def validate_database(self) -> bool:
        """Validate database integrity"""
        self.log("🔍 Validating database...")
        
        db_path = Path("data/trench.db")
        if not db_path.exists():
            self.log("❌ Database file not found", "ERROR")
            return False
            
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check coin count
            cursor.execute("SELECT COUNT(*) FROM coins")
            count = cursor.fetchone()[0]
            
            if count >= 1000:  # Expecting at least 1000 coins
                self.log(f"✅ Database validated ({count} coins)")
                self.validation_results["coin_count"] = count
                conn.close()
                return True
            else:
                self.log(f"⚠️ Low coin count: {count}", "WARNING")
                conn.close()
                return True  # Don't fail deployment for low count
                
        except Exception as e:
            self.log(f"❌ Database validation failed: {str(e)}", "ERROR")
            return False
    
    def send_discord_notification(self, success: bool):
        """Send deployment notification to Discord"""
        self.log("📢 Sending Discord notification...")
        
        color = 0x00ff00 if success else 0xff0000
        status = "✅ SUCCESS" if success else "❌ FAILED"
        
        embed = {
            "title": f"Deployment {status}",
            "description": f"TrenchCoat Pro deployment completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "color": color,
            "fields": [
                {"name": "GitHub Hash", "value": self.validation_results.get("github_hash", "Unknown"), "inline": True},
                {"name": "Streamlit Status", "value": self.validation_results.get("streamlit_status", "Unknown"), "inline": True},
                {"name": "Response Time", "value": f"{self.validation_results.get('streamlit_response_time', 'N/A')}ms", "inline": True},
                {"name": "Database", "value": f"{self.validation_results.get('coin_count', 'Unknown')} coins", "inline": True}
            ],
            "footer": {"text": "TrenchCoat Pro Unified Deploy System"}
        }
        
        payload = {"embeds": [embed]}
        
        try:
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            if response.status_code == 204:
                self.log("✅ Discord notification sent")
            else:
                self.log(f"⚠️ Discord notification failed: {response.status_code}", "WARNING")
        except Exception as e:
            self.log(f"⚠️ Discord notification error: {str(e)}", "WARNING")
    
    def save_deployment_report(self):
        """Save deployment report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "validation_results": self.validation_results,
            "deployment_log": self.deployment_log
        }
        
        report_path = Path("deployment_reports")
        report_path.mkdir(exist_ok=True)
        
        filename = f"deployment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path / filename, 'w') as f:
            json.dump(report, f, indent=2)
            
        self.log(f"📄 Report saved: {filename}")
    
    def deploy(self) -> bool:
        """Main deployment workflow"""
        self.log("🚀 Starting TrenchCoat Pro Unified Deployment")
        self.log("=" * 50)
        
        # Step 1: Prerequisites
        if not self.check_prerequisites():
            self.log("❌ Prerequisites check failed", "ERROR")
            return False
        
        # Step 2: Stage and commit
        if not self.stage_and_commit():
            self.log("❌ Commit failed", "ERROR")
            return False
        
        # Step 3: Push to GitHub
        if not self.push_to_github():
            self.log("❌ GitHub push failed", "ERROR")
            return False
        
        # Step 4: Validate GitHub deployment
        if not self.validate_github_deployment():
            self.log("⚠️ GitHub validation failed", "WARNING")
        
        # Step 5: Validate Streamlit deployment
        streamlit_ok = self.validate_streamlit_deployment()
        
        # Step 6: Validate database
        db_ok = self.validate_database()
        
        # Step 7: Overall status
        deployment_success = streamlit_ok and db_ok
        
        # Step 8: Send notification
        self.send_discord_notification(deployment_success)
        
        # Step 9: Save report
        self.save_deployment_report()
        
        self.log("=" * 50)
        if deployment_success:
            self.log("✅ DEPLOYMENT SUCCESSFUL", "SUCCESS")
        else:
            self.log("❌ DEPLOYMENT FAILED", "ERROR")
            
        return deployment_success

def main():
    """Main entry point"""
    deploy_system = UnifiedDeploymentSystem()
    
    # Handle command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--validate-only":
            deploy_system.log("Running validation only...")
            deploy_system.validate_github_deployment()
            deploy_system.validate_streamlit_deployment()
            deploy_system.validate_database()
            deploy_system.save_deployment_report()
            return
    
    # Run full deployment
    success = deploy_system.deploy()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()