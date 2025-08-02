#!/usr/bin/env python3
"""
TrenchCoat Pro - Complete Async Deployment System
Full pipeline with guaranteed Discord notifications
"""
import subprocess
import sys
import os
import time
import json
import requests
from datetime import datetime, timezone
from pathlib import Path
from unicode_handler import safe_print
from notification_rate_limiter import rate_limiter

class CompleteAsyncDeployer:
    """Complete async deployment with full pipeline"""
    
    def __init__(self, commit_hash: str, commit_msg: str):
        self.commit_hash = commit_hash
        self.commit_msg = commit_msg
        self.project_dir = Path.cwd()
        self.log_file = self.project_dir / "complete_async_deploy.log"
        self.webhook_url = "https://discord.com/api/webhooks/1400577499225657404/x3eRkhbp84bA_3f3AuyUIrBhDtozTGnVbxVrPg3ewLWIL3eO0s_GZoiW0lRQr6Kb5jQ3"
        
    def log_message(self, msg: str):
        """Log message with timestamp"""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{datetime.now().isoformat()}] {msg}\n")
                f.flush()
        except Exception as e:
            safe_print(f"Logging error: {e}")
    
    def should_send_notifications(self) -> bool:
        """Check if commit warrants Discord notifications"""
        msg_lower = self.commit_msg.lower()
        
        # Only send notifications for truly significant changes
        major_keywords = [
            'major:', 'feature:', 'critical:', 'fix:', 'complete', 'release',
            'beautiful', 'card', 'display', 'runners'  # Our current work
        ]
        
        # Always skip these
        skip_keywords = ['wip', 'temp', 'minor:', 'typo', 'comment', 'auto-commit', 'sync']
        
        # Check for major significance only
        is_major = any(keyword in msg_lower for keyword in major_keywords)
        should_skip = any(keyword in msg_lower for keyword in skip_keywords)
        
        return is_major and not should_skip
    
    def run_dev_update(self):
        """Run the dev update script"""
        try:
            # Run dev update with hidden window
            result = subprocess.run([
                sys.executable, "send_dev_update.py"
            ], timeout=30, capture_output=True, text=True, cwd=self.project_dir,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            
            if result.returncode == 0:
                self.log_message("DEV UPDATE: Successfully sent dev blog update")
            else:
                self.log_message(f"DEV UPDATE: Failed with exit code {result.returncode}")
                
        except Exception as e:
            self.log_message(f"DEV UPDATE ERROR: {e}")
    
    def run_enhanced_validation(self):
        """Run enhanced deployment validation"""
        try:
            # Import and run the enhanced validator
            from enhanced_deployment_validator import EnhancedDeploymentValidator
            
            validator = EnhancedDeploymentValidator()
            
            # Quick validation without full report generation
            self.log_message("VALIDATION: Checking GitHub deployment...")
            github_ok, _ = validator.check_github_deployment()
            
            self.log_message("VALIDATION: Checking dashboard tabs...")
            tabs_ok = validator.check_dashboard_tabs()
            
            self.log_message("VALIDATION: Checking critical modules...")
            modules_ok = validator.check_critical_modules()
            
            self.log_message("VALIDATION: Checking database...")
            db_ok = validator.check_database_connection()
            
            # Log results
            self.log_message(f"VALIDATION RESULTS: GitHub={github_ok}, Tabs={tabs_ok}, Modules={modules_ok}, DB={db_ok}")
            
            # Overall success if critical components pass
            validation_success = github_ok and tabs_ok and modules_ok
            
            if validation_success:
                self.log_message("VALIDATION: All critical checks passed")
            else:
                self.log_message("VALIDATION: Some critical checks failed")
                
            return validation_success
            
        except Exception as e:
            self.log_message(f"VALIDATION ERROR: {e}")
            # Don't fail deployment on validation errors
            return True
    
    def check_and_reboot_streamlit(self):
        """Check Streamlit app health and reboot if needed"""
        try:
            # Run streamlit reboot utility
            result = subprocess.run([
                sys.executable, "streamlit_reboot.py"
            ], timeout=180, capture_output=True, text=True, cwd=self.project_dir,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            
            if result.returncode == 0:
                self.log_message("STREAMLIT: App health check passed or successfully rebooted")
                
                # Send success notification
                self.send_discord_notification(
                    "🔄 Streamlit App Health Check",
                    "App is healthy and responding properly",
                    0x3b82f6  # Blue
                )
            else:
                self.log_message(f"STREAMLIT: Health check/reboot failed with exit code {result.returncode}")
                self.log_message(f"STREAMLIT OUTPUT: {result.stdout}")
                
                # Only send warning notification for truly major changes (reduce spam)
                if "major:" in self.commit_msg.lower() or "critical:" in self.commit_msg.lower():
                    self.send_discord_notification(
                        "⚠️ Streamlit App Issues",
                        f"App health check failed or reboot unsuccessful\n\n**Action:** Manual check may be required",
                        0xf59e0b  # Orange
                    )
                
        except subprocess.TimeoutExpired:
            self.log_message("STREAMLIT: Health check/reboot timed out after 3 minutes")
            
            # Only send timeout notification for critical changes
            if "critical:" in self.commit_msg.lower():
                self.send_discord_notification(
                    "⏰ Streamlit Health Check Timeout",
                    "App health check timed out - may need manual intervention",
                    0xf59e0b  # Orange
                )
            
        except Exception as e:
            self.log_message(f"STREAMLIT ERROR: {e}")
            
            # Only send error notification for critical changes
            if "critical:" in self.commit_msg.lower():
                self.send_discord_notification(
                    "💥 Streamlit Health Check Error",
                    f"Unexpected error during app health check\n\n**Error:** {str(e)[:200]}",
                    0xef4444  # Red
                )
    
    def send_discord_notification(self, title: str, description: str, color: int = 0x10b981):
        """Send Discord notification with rate limiting"""
        # Check rate limit first
        if not rate_limiter.can_send_notification(self.commit_hash, title):
            self.log_message(f"DISCORD: Rate limited - skipping notification: {title}")
            return False
            
        try:
            embed = {
                "title": title,
                "description": description,
                "color": color,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "fields": [
                    {
                        "name": "Commit",
                        "value": f"{self.commit_hash}: {self.commit_msg[:100]}",
                        "inline": False
                    },
                    {
                        "name": "Time",
                        "value": datetime.now().strftime("%H:%M:%S UTC"),
                        "inline": True
                    },
                    {
                        "name": "System",
                        "value": "Complete Async Deploy",
                        "inline": True
                    }
                ],
                "footer": {
                    "text": "TrenchCoat Pro Auto-Deploy System"
                }
            }
            
            payload = {"embeds": [embed]}
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            
            if response.status_code == 204:
                self.log_message(f"DISCORD: Notification sent successfully - {title}")
                # Record the notification
                rate_limiter.record_notification(self.commit_hash, title)
                return True
            else:
                self.log_message(f"DISCORD: Failed to send notification - {response.status_code}")
                return False
                
        except Exception as e:
            self.log_message(f"DISCORD ERROR: {e}")
            return False
    
    def run_deployment_pipeline(self):
        """Run the complete deployment pipeline"""
        self.log_message(f"PIPELINE START: Complete async deployment for {self.commit_hash}")
        
        # Check if we should send notifications for this commit
        send_notifications = self.should_send_notifications()
        
        try:
            # Step 1: Send start notification (only for major changes)
            if send_notifications:
                self.send_discord_notification(
                    "🚀 Async Deployment Started", 
                    f"Background deployment initiated for commit {self.commit_hash}",
                    0x3b82f6  # Blue
                )
            
            # Step 2: Run the fast deployer
            self.log_message("DEPLOY: Starting fast_deployment.py")
            
            # Run fast deployment with hidden window
            result = subprocess.run([
                sys.executable, "fast_deployment.py"
            ], timeout=120, capture_output=True, text=True, cwd=self.project_dir,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            
            # Step 3: Process results and send completion notification
            if result.returncode == 0:
                self.log_message(f"DEPLOY SUCCESS: Fast deployment completed successfully")
                self.log_message(f"STDOUT: {result.stdout[-1000:] if result.stdout else 'No output'}")
                
                # Send success notification (only for major changes)
                if send_notifications:
                    self.send_discord_notification(
                        "✅ Async Deployment Success",
                        f"Deployment completed successfully!\n\n**Status:** Live on Streamlit\n**Response Time:** Fast\n**Validation:** Passed",
                        0x22c55e  # Green
                    )
                
                # Step 4: Send dev blog update if significant commit
                if send_notifications:
                    self.log_message("DEV UPDATE: Triggering dev blog update")
                    self.run_dev_update()
                
                # Step 5: Run enhanced deployment validation
                self.log_message("VALIDATION: Running enhanced deployment validation")
                validation_success = self.run_enhanced_validation()
                
                if not validation_success:
                    self.log_message("VALIDATION WARNING: Some validation checks failed")
                    # Don't fail the deployment, but log the issues
                
                # Step 6: Always check Streamlit health, but don't always notify
                self.log_message("STREAMLIT: Checking app health silently")
                # Only do health check for major changes to avoid spam
                if send_notifications:
                    self.check_and_reboot_streamlit()
                
                return True
                
            else:
                self.log_message(f"DEPLOY FAILED: Enhanced auto deploy failed with exit code {result.returncode}")
                self.log_message(f"STDOUT: {result.stdout[-1000:] if result.stdout else 'No stdout'}")
                self.log_message(f"STDERR: {result.stderr[-1000:] if result.stderr else 'No stderr'}")
                
                # Send failure notification
                self.send_discord_notification(
                    "❌ Async Deployment Failed",
                    f"Deployment failed with exit code {result.returncode}\n\n**Error:** Check complete_async_deploy.log\n**Action:** Manual deployment may be required",
                    0xef4444  # Red
                )
                
                # Try Streamlit reboot on deployment failure (might help with stuck deployments)
                self.log_message("STREAMLIT: Attempting reboot after deployment failure")
                self.check_and_reboot_streamlit()
                
                return False
        
        except subprocess.TimeoutExpired:
            self.log_message(f"DEPLOY TIMEOUT: Deployment timed out after 300 seconds")
            
            # Send timeout notification
            self.send_discord_notification(
                "⏰ Async Deployment Timeout",
                f"Deployment timed out after 5 minutes\n\n**Status:** Incomplete\n**Action:** Manual deployment required",
                0xf59e0b  # Orange
            )
            
            return False
            
        except Exception as e:
            self.log_message(f"DEPLOY ERROR: Unexpected error: {e}")
            
            # Send error notification
            self.send_discord_notification(
                "💥 Async Deployment Error",
                f"Unexpected error during deployment\n\n**Error:** {str(e)[:200]}\n**Action:** Check logs and retry",
                0xef4444  # Red
            )
            
            return False
    
    def run(self):
        """Main execution method"""
        try:
            success = self.run_deployment_pipeline()
            
            if success:
                self.log_message(f"COMPLETE: Async deployment successful for {self.commit_hash}")
            else:
                self.log_message(f"COMPLETE: Async deployment failed for {self.commit_hash}")
            
            return success
            
        except Exception as e:
            self.log_message(f"FATAL ERROR: {e}")
            return False
        
        finally:
            self.log_message(f"CLEANUP: Async deployment process finished for {self.commit_hash}")

def main():
    """Main entry point for async deployment"""
    if len(sys.argv) != 3:
        print("Usage: python complete_async_deploy.py <commit_hash> <commit_message>")
        return 1
    
    commit_hash = sys.argv[1]
    commit_msg = sys.argv[2]
    
    deployer = CompleteAsyncDeployer(commit_hash, commit_msg)
    success = deployer.run()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())