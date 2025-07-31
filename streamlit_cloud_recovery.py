#!/usr/bin/env python3
"""
Streamlit Cloud Recovery System
Complete diagnosis and recovery for Streamlit deployment issues
"""
import requests
import subprocess
import json
import time
from datetime import datetime
from unicode_handler import safe_print

class StreamlitCloudRecovery:
    """Comprehensive Streamlit Cloud recovery system"""
    
    def __init__(self):
        self.base_url = "https://trenchcoat-pro.streamlit.app"
        self.possible_urls = [
            "https://trenchcoat-pro.streamlit.app/",
            "https://trenchcoatpro.streamlit.app/",
            "https://app-trenchcoat-pro.streamlit.app/",
            "https://projecttrench.streamlit.app/",
            "https://trench.streamlit.app/"
        ]
        self.recovery_steps = []
        
    def log_step(self, step: str, success: bool, details: str):
        """Log recovery step"""
        status = "✅" if success else "❌"
        self.recovery_steps.append({
            'step': step,
            'success': success,
            'details': details,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })
        safe_print(f"{status} {step}: {details}")
        return success
        
    def check_app_existence(self) -> bool:
        """Check if Streamlit app exists at any URL"""
        safe_print("📡 Checking App Existence Across URLs...")
        
        working_urls = []
        for url in self.possible_urls:
            try:
                response = requests.get(url, timeout=10, allow_redirects=True)
                if response.status_code == 200:
                    working_urls.append(url)
                    self.log_step(f"App Found", True, f"Working URL: {url}")
                elif response.status_code in [303, 302]:
                    self.log_step(f"Redirect Detected", False, f"{url} -> {response.headers.get('location', 'Unknown')}")
                else:
                    self.log_step(f"URL Check", False, f"{url} returned {response.status_code}")
                    
            except Exception as e:
                self.log_step(f"URL Check", False, f"{url} failed: {e}")
        
        if working_urls:
            self.base_url = working_urls[0]
            return True
        else:
            return False
    
    def check_github_deployment_status(self) -> bool:
        """Check if GitHub repo is properly configured for Streamlit"""
        safe_print("\n🔍 Checking GitHub Repository Status...")
        
        try:
            # Check if we have a streamlit_app.py file
            result = subprocess.run(['git', 'ls-files', 'streamlit_app.py'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and result.stdout.strip():
                self.log_step("Streamlit Entry Point", True, "streamlit_app.py exists in repo")
            else:
                return self.log_step("Streamlit Entry Point", False, "streamlit_app.py not found in repo")
            
            # Check if requirements.txt exists
            result = subprocess.run(['git', 'ls-files', 'requirements.txt'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and result.stdout.strip():
                self.log_step("Dependencies", True, "requirements.txt exists")
            else:
                return self.log_step("Dependencies", False, "requirements.txt missing")
            
            # Check recent commits
            result = subprocess.run(['git', 'log', '--oneline', '-5'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                commits = result.stdout.strip().split('\n')[:3]
                self.log_step("Recent Commits", True, f"Latest: {commits[0][:60]}...")
                return True
            else:
                return self.log_step("Recent Commits", False, "Cannot access git history")
                
        except Exception as e:
            return self.log_step("GitHub Check", False, f"Error: {e}")
    
    def force_streamlit_redeploy(self) -> bool:
        """Force a complete Streamlit redeployment"""
        safe_print("\n🚀 Forcing Complete Streamlit Redeployment...")
        
        try:
            # Method 1: Modify streamlit_app.py with timestamp
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            with open('streamlit_app.py', 'r') as f:
                content = f.read()
            
            # Update deployment timestamp in file
            if 'DEPLOYMENT_TIMESTAMP' in content:
                # Replace existing timestamp
                import re
                pattern = r'# DEPLOYMENT_TIMESTAMP: .*\n'
                replacement = f'# DEPLOYMENT_TIMESTAMP: {timestamp} - Force redeploy\n'
                content = re.sub(pattern, replacement, content)
            else:
                # Add timestamp at top
                lines = content.split('\n')
                lines.insert(1, f'# DEPLOYMENT_TIMESTAMP: {timestamp} - Force redeploy')
                content = '\n'.join(lines)
            
            with open('streamlit_app.py', 'w') as f:
                f.write(content)
            
            self.log_step("App Modified", True, f"Added timestamp: {timestamp}")
            
            # Method 2: Force git commit and push
            result = subprocess.run(['git', 'add', 'streamlit_app.py'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                commit_msg = f"FORCE REDEPLOY: Streamlit app update - {timestamp}"
                result = subprocess.run(['git', 'commit', '-m', commit_msg], 
                                      capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    self.log_step("Git Commit", True, "Changes committed")
                    
                    # Push to GitHub
                    result = subprocess.run(['git', 'push', 'origin', 'main'], 
                                          capture_output=True, text=True, timeout=30)
                    
                    if result.returncode == 0:
                        self.log_step("Git Push", True, "Pushed to GitHub - Streamlit should redeploy")
                        return True
                    else:
                        return self.log_step("Git Push", False, f"Push failed: {result.stderr}")
                else:
                    return self.log_step("Git Commit", False, f"Commit failed: {result.stderr}")
            else:
                return self.log_step("Git Add", False, f"Add failed: {result.stderr}")
                
        except Exception as e:
            return self.log_step("Force Redeploy", False, f"Error: {e}")
    
    def wait_for_deployment(self, timeout: int = 300) -> bool:
        """Wait for Streamlit deployment to complete"""
        safe_print(f"\n⏰ Waiting for Deployment (timeout: {timeout}s)...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(self.base_url, timeout=10)
                
                if response.status_code == 200:
                    # Check if it has our content
                    content = response.text.lower()
                    if 'trenchcoat' in content and 'coin data' in content:
                        elapsed = int(time.time() - start_time)
                        return self.log_step("Deployment Complete", True, f"App is live with new content after {elapsed}s")
                    else:
                        safe_print(f"⏳ App responding but old content... ({int(time.time() - start_time)}s)")
                else:
                    safe_print(f"⏳ App still deploying... Status: {response.status_code} ({int(time.time() - start_time)}s)")
                
            except Exception as e:
                safe_print(f"⏳ Deployment in progress... ({int(time.time() - start_time)}s)")
            
            time.sleep(10)  # Check every 10 seconds
        
        return self.log_step("Deployment Timeout", False, f"No response after {timeout}s")
    
    def run_complete_recovery(self) -> bool:
        """Run complete recovery process"""
        safe_print("🔧 STREAMLIT CLOUD RECOVERY SYSTEM")
        safe_print("=" * 50)
        
        # Step 1: Check app existence
        if not self.check_app_existence():
            safe_print("\n❌ No working Streamlit app found at any URL")
            safe_print("💡 SOLUTION: Recreate app in Streamlit Cloud from GitHub repo")
            return False
        
        # Step 2: Check GitHub status
        if not self.check_github_deployment_status():
            safe_print("\n❌ GitHub repository issues detected")
            return False
        
        # Step 3: Force redeploy
        if not self.force_streamlit_redeploy():
            safe_print("\n❌ Failed to trigger redeployment")
            return False
        
        # Step 4: Wait for deployment
        if self.wait_for_deployment():
            safe_print("\n🎉 RECOVERY SUCCESSFUL!")
            safe_print(f"✅ App is live at: {self.base_url}")
            return True
        else:
            safe_print("\n⚠️ RECOVERY INCOMPLETE")
            safe_print("💡 Manual intervention may be required in Streamlit Cloud")
            return False
    
    def print_summary(self):
        """Print recovery summary"""
        safe_print("\n" + "=" * 50)
        safe_print("📋 RECOVERY SUMMARY")
        safe_print("=" * 50)
        
        success_count = sum(1 for step in self.recovery_steps if step['success'])
        total_count = len(self.recovery_steps)
        
        safe_print(f"Total Steps: {total_count}")
        safe_print(f"Successful: {success_count}")
        safe_print(f"Failed: {total_count - success_count}")
        
        if success_count == total_count:
            safe_print("\n🎉 ALL RECOVERY STEPS SUCCESSFUL!")
        else:
            safe_print("\n⚠️ Some recovery steps failed:")
            for step in self.recovery_steps:
                if not step['success']:
                    safe_print(f"  ❌ {step['step']}: {step['details']}")

def main():
    """Main recovery process"""
    recovery = StreamlitCloudRecovery()
    success = recovery.run_complete_recovery()
    recovery.print_summary()
    
    return 0 if success else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())