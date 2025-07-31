#!/usr/bin/env python3
"""
TrenchCoat Pro - Fast Deployment System
Quick deployment without extensive validation to prevent timeouts
"""
import subprocess
import sys
import os
import time
import json
import requests
from datetime import datetime
from pathlib import Path
from unicode_handler import safe_print

class FastDeployer:
    """Fast deployment system without extensive validation"""
    
    def __init__(self):
        self.repo_url = "https://github.com/JLORep/ProjectTrench"
        self.streamlit_url = "https://trenchdemo.streamlit.app"
        self.webhook_url = "https://discord.com/api/webhooks/1400577499225657404/x3eRkhbp84bA_3f3AuyUIrBhDtozTGnVbxVrPg3ewLWIL3eO0s_GZoiW0lRQr6Kb5jQ3"
        
    def run_git_cmd(self, cmd, timeout=30):
        """Run git command with timeout and hidden window"""
        return subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=timeout,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
            check=True
        )
    
    def deploy(self):
        """Fast deployment process"""
        start_time = time.time()
        
        try:
            safe_print("🚀 Starting fast deployment...")
            
            # Get commit info
            result = self.run_git_cmd(["git", "log", "--oneline", "-1"])
            commit_info = result.stdout.strip()
            commit_hash = commit_info.split()[0]
            
            safe_print(f"Deploying: {commit_info}")
            
            # Check for uncommitted changes
            result = self.run_git_cmd(["git", "status", "--porcelain"])
            if result.stdout.strip():
                safe_print("Found uncommitted changes, staging...")
                self.run_git_cmd(["git", "add", "-u"])
                
                # Check if there are staged changes
                result = self.run_git_cmd(["git", "diff", "--cached", "--name-only"])
                if result.stdout.strip():
                    commit_msg = f"Auto-deploy sync - {datetime.now().strftime('%H:%M:%S')}"
                    self.run_git_cmd(["git", "commit", "-m", commit_msg])
                    safe_print("✅ Committed changes")
            
            # Push to GitHub  
            safe_print("Pushing to GitHub...")
            self.run_git_cmd(["git", "push", "origin", "main"], timeout=60)
            safe_print("✅ Pushed to GitHub")
            
            # Quick health check (no waiting)
            safe_print("Quick Streamlit health check...")
            try:
                response = requests.get(self.streamlit_url, timeout=10)
                health_status = "healthy" if response.status_code == 200 else "error"
                safe_print(f"Streamlit: {health_status} ({response.status_code})")
            except:
                health_status = "unknown"
                safe_print("Streamlit: status unknown")
            
            # Send success notification
            elapsed = time.time() - start_time
            self.send_notification(
                title="✅ Fast Deployment Success",
                description=f"Deployment completed successfully in {elapsed:.1f}s",
                color=0x10b981,
                commit_info=commit_info,
                duration=elapsed,
                streamlit_status=health_status
            )
            
            safe_print(f"🎉 Fast deployment completed in {elapsed:.1f}s")
            return True
            
        except subprocess.TimeoutExpired as e:
            elapsed = time.time() - start_time
            safe_print(f"❌ Deployment timed out after {elapsed:.1f}s: {e}")
            self.send_notification(
                title="⏰ Fast Deployment Timeout", 
                description=f"Deployment timed out after {elapsed:.1f}s",
                color=0xef4444,
                commit_info=commit_info if 'commit_info' in locals() else 'unknown',
                duration=elapsed
            )
            return False
            
        except Exception as e:
            elapsed = time.time() - start_time
            safe_print(f"❌ Deployment failed after {elapsed:.1f}s: {e}")
            self.send_notification(
                title="❌ Fast Deployment Failed",
                description=f"Deployment failed: {str(e)[:100]}",
                color=0xef4444,
                commit_info=commit_info if 'commit_info' in locals() else 'unknown',
                duration=elapsed
            )
            return False
    
    def send_notification(self, title, description, color, commit_info="", duration=0, streamlit_status="unknown"):
        """Send Discord notification"""
        try:
            payload = {
                "embeds": [{
                    "title": title,
                    "description": description,
                    "color": color,
                    "timestamp": datetime.now().isoformat(),
                    "fields": [
                        {
                            "name": "Commit",
                            "value": commit_info[:100] if commit_info else "Unknown",
                            "inline": False
                        },
                        {
                            "name": "Duration", 
                            "value": f"{duration:.1f}s",
                            "inline": True
                        },
                        {
                            "name": "Streamlit",
                            "value": streamlit_status,
                            "inline": True
                        }
                    ],
                    "footer": {
                        "text": "TrenchCoat Pro Fast Deploy"
                    }
                }]
            }
            
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            if response.status_code == 204:
                safe_print("✅ Discord notification sent")
            else:
                safe_print(f"Discord notification failed: {response.status_code}")
                
        except Exception as e:
            safe_print(f"Discord notification error: {e}")

def main():
    """Main deployment function"""
    deployer = FastDeployer()
    return deployer.deploy()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)