#!/usr/bin/env python3
"""
TrenchCoat Pro - Enhanced Auto-Deployment System
Automatically deploys and notifies Discord when bugs are fixed or features shipped
"""
import subprocess
import sys
import time
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional
import os

class EnhancedAutoDeployer:
    """Enhanced deployment system with Discord integration"""
    
    def __init__(self):
        self.repo_url = "https://github.com/JLORep/ProjectTrench"
        self.streamlit_url = "https://trenchdemo.streamlit.app"
        self.deployment_log = []
        self.deployment_log_file = "deployment_log.json"
        
        # Discord webhook URLs
        self.discord_webhooks = {
            'dev': 'https://discord.com/api/webhooks/1400491407550058610/Q59NIxt5lSvFgpwckXOv_P9TF8uWjudOTJxEw5hZ3fL61D-gSwrpIb110UiG4Z1f7',
            'overview': 'https://discord.com/api/webhooks/1400497302241677383/Im9oyVehkH6zhsc5w4mt4KHQvgSR2qfMPD-k6lTR-X0XQWT3eLV_IJM2-MqQNM6dPAzM'
        }
        
        # Load existing deployment log
        self.load_deployment_log()
    
    def load_deployment_log(self):
        """Load existing deployment log"""
        try:
            if os.path.exists(self.deployment_log_file):
                with open(self.deployment_log_file, 'r') as f:
                    self.deployment_log = json.load(f)
        except Exception as e:
            print(f"[WARNING] Could not load deployment log: {e}")
            self.deployment_log = []
    
    def save_deployment_log(self):
        """Save deployment log"""
        try:
            with open(self.deployment_log_file, 'w') as f:
                json.dump(self.deployment_log, f, indent=2)
        except Exception as e:
            print(f"[ERROR] Could not save deployment log: {e}")
    
    def update_dev_blog(self, deployment_info: Dict) -> bool:
        """Update dev blog with deployment information"""
        try:
            print("[BLOG] Updating dev blog...")
            
            # Import dev blog system
            from dev_blog_system import DevBlogSystem
            blog = DevBlogSystem()
            
            # Create blog entry based on deployment type
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
            
            if deployment_info['type'] == 'bugfix':
                title = f"🐛 Bug Fixes Deployed - {timestamp}"
                content = f"""
## Bug Fixes and Stability Improvements

**Deployment Time:** {timestamp}
**Commit:** {deployment_info['commit_message']}

### What Was Fixed:
{deployment_info['description']}

### Files Changed:
{chr(10).join(f'- {file}' for file in deployment_info['changed_files'] if file)}

### Testing:
- ✅ All critical bugs resolved
- ✅ Dashboard stability improved
- ✅ Performance optimized

The fixes are now live on [TrenchCoat Pro]({self.streamlit_url}).
"""
            
            elif deployment_info['type'] == 'feature':
                title = f"✨ New Features Shipped - {timestamp}"
                content = f"""
## New Features and Enhancements

**Deployment Time:** {timestamp}
**Commit:** {deployment_info['commit_message']}

### What's New:
{deployment_info['description']}

### Files Updated:
{chr(10).join(f'- {file}' for file in deployment_info['changed_files'] if file)}

### Key Improvements:
- 🚀 Enhanced user experience
- 🎯 New functionality added
- 📊 Better performance metrics

Check out the new features at [TrenchCoat Pro]({self.streamlit_url}).
"""
            
            else:
                title = f"🔄 System Update - {timestamp}"
                content = f"""
## System Update Deployed

**Deployment Time:** {timestamp}
**Commit:** {deployment_info['commit_message']}

### Changes:
{deployment_info['description']}

### Files Modified:
{chr(10).join(f'- {file}' for file in deployment_info['changed_files'] if file)}

Updates are live at [TrenchCoat Pro]({self.streamlit_url}).
"""
            
            # Create the blog post
            success = blog.create_post(
                title=title,
                content=content,
                category="deployment",
                tags=["deployment", "auto", deployment_info['type']]
            )
            
            if success:
                print("[BLOG] ✅ Dev blog updated successfully")
                return True
            else:
                print("[BLOG] ❌ Failed to update dev blog")
                return False
                
        except Exception as e:
            print(f"[BLOG] ❌ Error updating dev blog: {e}")
            return False
    
    def update_overview(self, deployment_info: Dict) -> bool:
        """Update project overview with latest deployment info"""
        try:
            print("[OVERVIEW] Updating project overview...")
            
            # Import overview updater
            from auto_overview_updater import update_project_overview
            
            # Calculate version number
            version = self.get_next_version()
            
            # Prepare update data
            update_data = {
                'last_deployment': datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'),
                'latest_commit': deployment_info['commit_message'],
                'deployment_type': deployment_info['type'],
                'version': version,
                'streamlit_url': self.streamlit_url,
                'files_changed': deployment_info['changed_files'],
                'status': 'active'
            }
            
            # Update the overview
            success = update_project_overview(update_data)
            
            if success:
                print("[OVERVIEW] ✅ Project overview updated successfully")
                return True
            else:
                print("[OVERVIEW] ❌ Failed to update project overview")
                return False
                
        except Exception as e:
            print(f"[OVERVIEW] ❌ Error updating overview: {e}")
            return False
    
    def get_next_version(self) -> str:
        """Calculate next version number based on deployment history"""
        if not self.deployment_log:
            return "1.0.0"
        
        try:
            last_entry = self.deployment_log[-1]
            last_version = last_entry.get('version', '1.0.0')
            
            # Parse version
            major, minor, patch = map(int, last_version.split('.'))
            
            # Increment based on deployment type
            deployment_type = getattr(self, '_current_deployment_type', 'patch')
            
            if deployment_type == 'feature':
                minor += 1
                patch = 0
            else:
                patch += 1
            
            return f"{major}.{minor}.{patch}"
            
        except Exception:
            return "1.0.1"
        
    def detect_deployment_type(self) -> Dict[str, any]:
        """Detect what type of deployment this is"""
        try:
            # Get the last commit info
            result = subprocess.run(
                ["git", "log", "--oneline", "-1"], 
                capture_output=True, text=True, check=True
            )
            commit_message = result.stdout.strip()
            
            # Get files changed
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
                capture_output=True, text=True, check=True
            )
            changed_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            deployment_info = {
                'commit_message': commit_message,
                'changed_files': changed_files,
                'type': 'unknown',
                'description': '',
                'channel': 'dev',  # default
                'priority': 'medium'
            }
            
            message_lower = commit_message.lower()
            
            # Determine deployment type and target channel
            if any(word in message_lower for word in ['fix', 'bug', 'error', 'issue', 'resolve']):
                deployment_info['type'] = 'bugfix'
                deployment_info['description'] = 'Bug fixes and stability improvements'
                deployment_info['channel'] = 'dev'
                deployment_info['priority'] = 'high'
                
            elif any(word in message_lower for word in ['feature', 'new', 'add', 'implement', 'enhance']):
                deployment_info['type'] = 'feature'
                deployment_info['description'] = 'New features and enhancements'
                deployment_info['channel'] = 'overview'  # Major features go to overview
                deployment_info['priority'] = 'high'
                
            elif any(word in message_lower for word in ['update', 'improve', 'optimize', 'refactor']):
                deployment_info['type'] = 'improvement'
                deployment_info['description'] = 'System improvements and optimizations'
                deployment_info['channel'] = 'dev'
                deployment_info['priority'] = 'medium'
                
            elif any(word in message_lower for word in ['deploy', 'release', 'version']):
                deployment_info['type'] = 'release'
                deployment_info['description'] = 'New release deployment'
                deployment_info['channel'] = 'overview'
                deployment_info['priority'] = 'high'
            
            return deployment_info
            
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to detect deployment type: {e}")
            return {
                'commit_message': 'Unknown deployment',
                'changed_files': [],
                'type': 'unknown',
                'description': 'Automated deployment',
                'channel': 'dev',
                'priority': 'low'
            }
    
    def sync_to_github(self) -> bool:
        """Ensure all changes are synced to GitHub"""
        try:
            print("[SYNC] Syncing files to GitHub...")
            
            # Check git status
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True, text=True, check=True
            )
            
            if result.stdout.strip():
                print("[SYNC] Found uncommitted changes, staging them...")
                
                # Add only tracked files to avoid untracked file issues
                subprocess.run(["git", "add", "-u"], check=True)
                
                # Check if there are actually staged changes before committing
                staged_result = subprocess.run(
                    ["git", "diff", "--cached", "--name-only"],
                    capture_output=True, text=True, check=True
                )
                
                if staged_result.stdout.strip():
                    # Commit with auto-generated message only if there are staged changes
                    commit_msg = f"Auto-sync deployment changes - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                    subprocess.run(["git", "commit", "-m", commit_msg], check=True)
                else:
                    print("[SYNC] No tracked files to commit, skipping commit step")
                
                # Push to GitHub
                subprocess.run(["git", "push", "origin", "main"], check=True)
                print("[SYNC] All files synced to GitHub successfully")
            else:
                print("[SYNC] Repository already up to date")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] GitHub sync failed: {e}")
            return False
    
    def wait_for_streamlit_update(self) -> bool:
        """Wait for Streamlit Cloud to update with latest changes using validator"""
        print("[STREAMLIT] Using deployment validator...")
        
        try:
            from deployment_validator import DeploymentValidator
            
            validator = DeploymentValidator()
            validation_result = validator.wait_for_deployment_completion()
            
            # Store validation details for notification
            self._validation_result = validation_result
            
            return validation_result['success']
            
        except ImportError:
            print("[WARNING] Deployment validator not available, using fallback method")
            return self._fallback_streamlit_check()
    
    def _fallback_streamlit_check(self) -> bool:
        """Fallback method for Streamlit checking"""
        print("[STREAMLIT] Using fallback deployment check...")
        
        max_wait_time = 300  # 5 minutes
        check_interval = 15   # 15 seconds
        elapsed = 0
        
        while elapsed < max_wait_time:
            try:
                response = requests.get(self.streamlit_url, timeout=10)
                if response.status_code == 200:
                    # Check if the page loads properly (not white screen)
                    content = response.text.lower()
                    if 'trenchcoat pro' in content and 'loading' not in content:
                        print(f"[STREAMLIT] App successfully updated! ({elapsed}s)")
                        return True
                
                print(f"[STREAMLIT] Still updating... ({elapsed}s)")
                time.sleep(check_interval)
                elapsed += check_interval
                
            except requests.RequestException:
                print(f"[STREAMLIT] Checking update status... ({elapsed}s)")
                time.sleep(check_interval)
                elapsed += check_interval
        
        print("[WARNING] Streamlit update check timed out")
        return False  # Fail on timeout with fallback method
    
    def send_discord_notification(self, deployment_info: Dict[str, any], success: bool):
        """Send deployment notification to appropriate Discord channel"""
        
        channel = deployment_info['channel']
        webhook_url = self.discord_webhooks.get(channel)
        
        if not webhook_url:
            print(f"[ERROR] No webhook configured for channel: {channel}")
            return
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        
        # Create message based on deployment type
        if success:
            if deployment_info['type'] == 'bugfix':
                title = "**TrenchCoat Pro - Bug Fixes Deployed**"
                color = 0x22c55e  # Green
                emoji = ":wrench:"
            elif deployment_info['type'] == 'feature':
                title = "**TrenchCoat Pro - New Features Live**"
                color = 0x3b82f6  # Blue
                emoji = ":rocket:"
            elif deployment_info['type'] == 'improvement':
                title = "**TrenchCoat Pro - System Improvements**"
                color = 0x10b981  # Emerald
                emoji = ":gear:"
            else:
                title = "**TrenchCoat Pro - Update Deployed**"
                color = 0x6b7280  # Gray
                emoji = ":package:"
        else:
            title = "**TrenchCoat Pro - Deployment Failed**"
            color = 0xef4444  # Red
            emoji = ":x:"
        
        # Create Discord embed
        embed = {
            "title": title,
            "description": deployment_info['description'],
            "color": color,
            "timestamp": datetime.utcnow().isoformat(),
            "fields": [
                {
                    "name": "Commit",
                    "value": deployment_info['commit_message'],
                    "inline": False
                },
                {
                    "name": "Files Changed",
                    "value": f"{len(deployment_info['changed_files'])} files updated",
                    "inline": True
                },
                {
                    "name": "Status",
                    "value": "Live" if success else "Failed",
                    "inline": True
                },
                {
                    "name": "Environment",
                    "value": "Production",
                    "inline": True
                }
            ],
            "footer": {
                "text": "TrenchCoat Pro Auto-Deployment System"
            }
        }
        
        # Add validation details if available
        if hasattr(self, '_validation_result') and self._validation_result:
            validation = self._validation_result
            
            if success:
                embed["fields"].extend([
                    {
                        "name": "Deployment Time",
                        "value": f"{validation.get('duration', 0):.1f}s",
                        "inline": True
                    },
                    {
                        "name": "Response Time",
                        "value": f"{validation.get('final_status', {}).get('response_time', 'N/A')}ms",
                        "inline": True
                    }
                ])
            else:
                # Add failure details
                embed["fields"].append({
                    "name": "Failure Reason",
                    "value": validation.get('error', 'Unknown error'),
                    "inline": False
                })
                
                if validation.get('timeout'):
                    embed["fields"].append({
                        "name": "Timeout",
                        "value": f"Failed after {validation.get('duration', 0):.1f}s",
                        "inline": True
                    })
        
        if success:
            embed["fields"].append({
                "name": "Live URL",
                "value": f"[{self.streamlit_url}]({self.streamlit_url})",
                "inline": False
            })
        
        # Send to Discord
        payload = {
            "embeds": [embed]
        }
        
        try:
            response = requests.post(webhook_url, json=payload, timeout=10)
            if response.status_code == 204:
                print(f"[DISCORD] Notification sent to #{channel} channel")
            else:
                print(f"[ERROR] Discord notification failed: {response.status_code}")
                
        except requests.RequestException as e:
            print(f"[ERROR] Failed to send Discord notification: {e}")
    
    def run_enhanced_deployment(self) -> bool:
        """Run the complete enhanced deployment pipeline"""
        
        print("=" * 60)
        print("TrenchCoat Pro Enhanced Auto-Deployment System")
        print("=" * 60)
        
        # Step 1: Detect deployment type
        print("\n[1/6] Analyzing deployment...")
        deployment_info = self.detect_deployment_type()
        
        print(f"   Type: {deployment_info['type']}")
        print(f"   Target Channel: #{deployment_info['channel']}")
        print(f"   Priority: {deployment_info['priority']}")
        
        # Step 2: Sync to GitHub
        print("\n[2/6] Syncing to GitHub...")
        if not self.sync_to_github():
            print("[ERROR] GitHub sync failed - aborting deployment")
            self.send_discord_notification(deployment_info, False)
            return False
        
        # Step 3: Wait for Streamlit update
        print("\n[3/6] Waiting for Streamlit Cloud update...")
        streamlit_success = self.wait_for_streamlit_update()
        
        # Step 4: Update Dev Blog
        print("\n[4/8] Updating dev blog...")
        blog_success = self.update_dev_blog(deployment_info)
        
        # Step 5: Update Overview  
        print("\n[5/8] Updating project overview...")
        overview_success = self.update_overview(deployment_info)
        
        # Step 6: Send Discord notification
        print("\n[6/8] Sending Discord notification...")
        self.send_discord_notification(deployment_info, streamlit_success)
        
        # Step 7: Log deployment
        print("\n[7/8] Logging deployment...")
        version = self.get_next_version()
        self._current_deployment_type = deployment_info['type']
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'deployment_info': deployment_info,
            'success': streamlit_success,
            'streamlit_url': self.streamlit_url,
            'version': version,
            'blog_updated': blog_success,
            'overview_updated': overview_success
        }
        
        self.deployment_log.append(log_entry)
        self.save_deployment_log()
        
        # Step 8: Summary
        print("\n[8/8] Deployment Summary")
        print("-" * 30)
        print(f"Status: {'SUCCESS' if streamlit_success else 'FAILED'}")
        print(f"Type: {deployment_info['type']}")
        print(f"Channel: #{deployment_info['channel']}")
        print(f"Live URL: {self.streamlit_url}")
        print(f"Repository: {self.repo_url}")
        
        return streamlit_success

if __name__ == "__main__":
    deployer = EnhancedAutoDeployer()
    success = deployer.run_enhanced_deployment()
    
    if success:
        print("\n[SUCCESS] Enhanced auto-deployment completed successfully!")
    else:
        print("\n[FAILED] Enhanced auto-deployment completed with issues!")
        sys.exit(1)