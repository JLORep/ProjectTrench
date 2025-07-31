#!/usr/bin/env python3
"""
TrenchCoat Pro - Deployment Validation System
Validates Streamlit Cloud deployments and detects failures
"""
import requests
import time
import json
import subprocess
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import re

class DeploymentValidator:
    """Validates deployments and detects failures"""
    
    def __init__(self):
        self.streamlit_url = "https://trenchdemo.streamlit.app"
        self.timeout = 10
        self.max_retries = 3
        self.check_interval = 30  # seconds
        self.max_wait_time = 600  # 10 minutes
        
        # Discord webhook for failures
        self.failure_webhook = "https://discord.com/api/webhooks/1400577499225657404/x3eRkhbp84bA_3f3AuyUIrBhDtozTGnVbxVrPg3ewLWIL3eO0s_GZoiW0lRQr6Kb5jQ3"
        
    def check_streamlit_health(self) -> Dict[str, any]:
        """Check Streamlit app health and detect issues"""
        result = {
            'status': 'unknown',
            'response_time': None,
            'error': None,
            'content_check': False,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            start_time = time.time()
            response = requests.get(self.streamlit_url, timeout=self.timeout, headers={
                'User-Agent': 'TrenchCoat-Deployment-Validator/1.0'
            })
            result['response_time'] = round((time.time() - start_time) * 1000, 2)
            
            if response.status_code == 200:
                content = response.text.lower()
                
                # Check for critical content
                required_content = [
                    'trenchcoat pro',
                    'ultra-premium',
                    'dashboard'
                ]
                
                content_found = sum(1 for req in required_content if req in content)
                result['content_check'] = content_found >= 2
                
                # Check for error indicators
                error_indicators = [
                    'error',
                    'failed to load',
                    'something went wrong',
                    'streamlit error',
                    'internal server error',
                    'application error'
                ]
                
                has_errors = any(indicator in content for indicator in error_indicators)
                
                if result['content_check'] and not has_errors:
                    result['status'] = 'healthy'
                elif has_errors:
                    result['status'] = 'error'
                    result['error'] = 'Application errors detected in content'
                else:
                    result['status'] = 'degraded'
                    result['error'] = 'Missing expected content'
                    
            elif response.status_code == 502:
                result['status'] = 'deploying'
                result['error'] = 'Service temporarily unavailable (likely deploying)'
            elif response.status_code in [503, 504]:
                result['status'] = 'unavailable'
                result['error'] = f'Service unavailable (HTTP {response.status_code})'
            else:
                result['status'] = 'failed'
                result['error'] = f'HTTP {response.status_code}: {response.reason}'
                
        except requests.exceptions.Timeout:
            result['status'] = 'timeout'
            result['error'] = f'Request timeout after {self.timeout}s'
        except requests.exceptions.ConnectionError:
            result['status'] = 'connection_error'
            result['error'] = 'Cannot connect to Streamlit app'
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            
        return result
    
    def wait_for_deployment_completion(self) -> Dict[str, any]:
        """Wait for deployment to complete and validate success"""
        print(f"[VALIDATOR] Monitoring deployment status...")
        
        start_time = time.time()
        deployment_phases = []
        
        while (time.time() - start_time) < self.max_wait_time:
            health = self.check_streamlit_health()
            deployment_phases.append(health)
            
            print(f"[VALIDATOR] Status: {health['status']} ({health.get('response_time', 'N/A')}ms)")
            
            if health['status'] == 'healthy':
                elapsed = round(time.time() - start_time, 1)
                print(f"[VALIDATOR] ✅ Deployment successful after {elapsed}s")
                return {
                    'success': True,
                    'duration': elapsed,
                    'final_status': health,
                    'phases': deployment_phases[-5:]  # Keep last 5 checks
                }
            
            elif health['status'] == 'failed':
                elapsed = round(time.time() - start_time, 1)
                print(f"[VALIDATOR] ❌ Deployment failed after {elapsed}s")
                return {
                    'success': False,
                    'duration': elapsed,
                    'final_status': health,
                    'phases': deployment_phases[-5:],
                    'error': health.get('error', 'Unknown failure')
                }
            
            elif health['status'] in ['deploying', 'unavailable']:
                print(f"[VALIDATOR] 🔄 Still deploying... ({round(time.time() - start_time, 1)}s)")
            
            time.sleep(self.check_interval)
        
        # Timeout reached
        elapsed = round(time.time() - start_time, 1)
        final_health = self.check_streamlit_health()
        
        print(f"[VALIDATOR] ⏰ Timeout after {elapsed}s, final status: {final_health['status']}")
        
        return {
            'success': final_health['status'] == 'healthy',
            'duration': elapsed,
            'final_status': final_health,
            'phases': deployment_phases[-5:],
            'timeout': True,
            'error': 'Deployment monitoring timeout'
        }
    
    def get_deployment_info(self) -> Dict[str, any]:
        """Get current deployment information from git"""
        try:
            # Get last commit
            result = subprocess.run(
                ["git", "log", "--oneline", "-1"], 
                capture_output=True, text=True, check=True
            )
            commit_info = result.stdout.strip()
            
            # Get commit hash and message
            commit_parts = commit_info.split(' ', 1)
            commit_hash = commit_parts[0] if commit_parts else 'unknown'
            commit_message = commit_parts[1] if len(commit_parts) > 1 else 'No message'
            
            # Get changed files
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
                capture_output=True, text=True, check=True
            )
            changed_files = [f for f in result.stdout.strip().split('\n') if f]
            
            return {
                'commit_hash': commit_hash,
                'commit_message': commit_message,
                'changed_files': changed_files,
                'timestamp': datetime.now().isoformat()
            }
            
        except subprocess.CalledProcessError as e:
            return {
                'commit_hash': 'unknown',
                'commit_message': 'Failed to get commit info',
                'changed_files': [],
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def send_failure_notification(self, validation_result: Dict, deployment_info: Dict):
        """Send failure notification to Discord"""
        try:
            embed = {
                "title": "**TrenchCoat Pro - Deployment Failed**",
                "description": "Deployment validation detected failure",
                "color": 0xef4444,  # Red
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
                        "value": "Failed",
                        "inline": True
                    },
                    {
                        "name": "Environment",
                        "value": "Production",
                        "inline": True
                    },
                    {
                        "name": "Error",
                        "value": validation_result.get('error', 'Unknown error'),
                        "inline": False
                    },
                    {
                        "name": "Duration",
                        "value": f"{validation_result.get('duration', 0)}s",
                        "inline": True
                    }
                ],
                "footer": {
                    "text": "TrenchCoat Pro Auto-Deployment System"
                }
            }
            
            payload = {"embeds": [embed]}
            
            response = requests.post(self.failure_webhook, json=payload, timeout=10)
            if response.status_code == 204:
                print("[VALIDATOR] Failure notification sent to Discord")
            else:
                print(f"[VALIDATOR] Failed to send notification: {response.status_code}")
                
        except Exception as e:
            print(f"[VALIDATOR] Error sending failure notification: {e}")
    
    def send_success_notification(self, validation_result: Dict, deployment_info: Dict):
        """Send success notification to Discord"""
        try:
            embed = {
                "title": "**TrenchCoat Pro - Deployment Successful** ✅",
                "description": "Deployment validated and running successfully",
                "color": 0x22c55e,  # Green
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
                        "value": "Live & Validated",
                        "inline": True
                    },
                    {
                        "name": "Environment",
                        "value": "Production",
                        "inline": True
                    },
                    {
                        "name": "Response Time",
                        "value": f"{validation_result['final_status'].get('response_time', 'N/A')}ms",
                        "inline": True
                    },
                    {
                        "name": "Deployment Time",
                        "value": f"{validation_result.get('duration', 0)}s",
                        "inline": True
                    },
                    {
                        "name": "Live URL",
                        "value": f"[{self.streamlit_url}]({self.streamlit_url})",
                        "inline": False
                    }
                ],
                "footer": {
                    "text": "TrenchCoat Pro Auto-Deployment System"
                }
            }
            
            payload = {"embeds": [embed]}
            
            response = requests.post(self.failure_webhook, json=payload, timeout=10)
            if response.status_code == 204:
                print("[VALIDATOR] Success notification sent to Discord")
            else:
                print(f"[VALIDATOR] Failed to send notification: {response.status_code}")
                
        except Exception as e:
            print(f"[VALIDATOR] Error sending success notification: {e}")
    
    def validate_deployment(self, send_notifications: bool = True) -> Dict[str, any]:
        """Main validation method"""
        print("=" * 60)
        print("TrenchCoat Pro Deployment Validator")
        print("=" * 60)
        
        # Get deployment info
        deployment_info = self.get_deployment_info()
        print(f"Validating deployment: {deployment_info['commit_message']}")
        
        # Wait for deployment and validate
        validation_result = self.wait_for_deployment_completion()
        
        # Send notifications
        if send_notifications:
            if validation_result['success']:
                self.send_success_notification(validation_result, deployment_info)
            else:
                self.send_failure_notification(validation_result, deployment_info)
        
        # Final result
        result = {
            'deployment_info': deployment_info,
            'validation_result': validation_result,
            'timestamp': datetime.now().isoformat()
        }
        
        print("\n" + "=" * 60)
        print(f"VALIDATION {'SUCCESS' if validation_result['success'] else 'FAILED'}")
        print("=" * 60)
        
        return result

def main():
    """Run deployment validation"""
    validator = DeploymentValidator()
    result = validator.validate_deployment()
    
    if result['validation_result']['success']:
        print("\n✅ Deployment validation passed!")
        return 0
    else:
        print("\n❌ Deployment validation failed!")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())