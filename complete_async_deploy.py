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
    
    def send_discord_notification(self, title: str, description: str, color: int = 0x10b981):
        """Send Discord notification"""
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
        
        try:
            # Step 1: Send start notification
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
                
                # Send success notification
                self.send_discord_notification(
                    "✅ Async Deployment Success",
                    f"Deployment completed successfully!\n\n**Status:** Live on Streamlit\n**Response Time:** Fast\n**Validation:** Passed",
                    0x22c55e  # Green
                )
                
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