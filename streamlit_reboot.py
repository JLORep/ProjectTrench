#!/usr/bin/env python3
"""
Streamlit App Reboot Utility
Triggers app restart via Streamlit Cloud API when needed
"""
import requests
import json
import time
from datetime import datetime
from unicode_handler import safe_print

class StreamlitRebooter:
    """Handles Streamlit app rebooting via API calls"""
    
    def __init__(self):
        # These would need to be configured with actual Streamlit Cloud API details
        self.app_url = "https://trenchdemo.streamlit.app"
        self.github_repo = "JLORep/ProjectTrench"
        self.branch = "main"
        
    def check_app_health(self) -> dict:
        """Check if the Streamlit app is responding properly"""
        try:
            response = requests.get(self.app_url, timeout=10, allow_redirects=False)
            
            return {
                'status_code': response.status_code,
                'is_healthy': response.status_code == 200,
                'needs_reboot': response.status_code in [303, 502, 503, 504],
                'response_time': response.elapsed.total_seconds(),
                'timestamp': datetime.now().isoformat()
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'status_code': 0,
                'is_healthy': False,
                'needs_reboot': True,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def trigger_github_commit_hook(self) -> bool:
        """Trigger Streamlit reboot by making a dummy commit"""
        try:
            # This is a workaround - Streamlit Cloud watches GitHub commits
            # A empty commit can trigger a rebuild/restart
            import subprocess
            
            result = subprocess.run([
                'git', 'commit', '--allow-empty', '-m', 'Trigger: Streamlit app reboot via deployment pipeline'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                # Push the commit
                push_result = subprocess.run([
                    'git', 'push', 'origin', 'main'
                ], capture_output=True, text=True, timeout=30)
                
                if push_result.returncode == 0:
                    safe_print("✅ Triggered Streamlit reboot via GitHub commit")
                    return True
                else:
                    safe_print(f"❌ Failed to push reboot commit: {push_result.stderr}")
                    return False
            else:
                safe_print(f"❌ Failed to create reboot commit: {result.stderr}")
                return False
                
        except Exception as e:
            safe_print(f"❌ Error triggering reboot: {e}")
            return False
    
    def wait_for_app_recovery(self, max_wait_time: int = 120) -> bool:
        """Wait for the app to come back online after reboot"""
        safe_print("⏳ Waiting for Streamlit app to recover...")
        
        start_time = time.time()
        while time.time() - start_time < max_wait_time:
            health = self.check_app_health()
            
            if health['is_healthy']:
                recovery_time = time.time() - start_time
                safe_print(f"✅ App recovered in {recovery_time:.1f}s")
                return True
            
            if health['status_code'] == 200:
                safe_print("✅ App is responding (200 OK)")
                return True
                
            # Wait before next check
            time.sleep(10)
            safe_print(f"⏳ Still waiting... Status: {health.get('status_code', 'unknown')}")
        
        safe_print(f"⏰ Timeout waiting for app recovery after {max_wait_time}s")
        return False
    
    def reboot_if_needed(self) -> dict:
        """Check app health and reboot if necessary"""
        safe_print("🔍 Checking Streamlit app health...")
        
        health = self.check_app_health()
        
        result = {
            'initial_health': health,
            'reboot_triggered': False,
            'recovery_successful': False,
            'timestamp': datetime.now().isoformat()
        }
        
        if health['needs_reboot']:
            safe_print(f"🚨 App needs reboot (Status: {health['status_code']})")
            
            if self.trigger_github_commit_hook():
                result['reboot_triggered'] = True
                
                # Wait for recovery
                if self.wait_for_app_recovery():
                    result['recovery_successful'] = True
                    safe_print("🎉 Streamlit app successfully rebooted and recovered!")
                else:
                    safe_print("❌ App reboot triggered but recovery failed")
            else:
                safe_print("❌ Failed to trigger app reboot")
        else:
            safe_print(f"✅ App is healthy (Status: {health['status_code']})")
            result['recovery_successful'] = True
        
        return result

def main():
    """Main reboot utility function"""
    rebooter = StreamlitRebooter()
    result = rebooter.reboot_if_needed()
    
    # Return appropriate exit code
    if result['recovery_successful']:
        return 0
    else:
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())