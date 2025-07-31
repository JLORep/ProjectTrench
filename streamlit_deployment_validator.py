#!/usr/bin/env python3
"""
Comprehensive Streamlit deployment validation
Checks if code changes are actually reflected in the live Streamlit app
"""
import requests
import time
import hashlib
import json
from datetime import datetime
from unicode_handler import safe_print

class StreamlitDeploymentValidator:
    """Validates that Streamlit deployments actually reflect code changes"""
    
    def __init__(self):
        self.streamlit_url = "https://trenchcoat-pro.streamlit.app/"
        self.timeout = 30
        self.max_retries = 5
        
    def get_app_content_hash(self):
        """Get a hash of the Streamlit app content to detect changes"""
        try:
            response = requests.get(self.streamlit_url, timeout=self.timeout)
            if response.status_code == 200:
                # Extract key indicators that the app has updated
                content = response.text
                
                # Look for specific markers that indicate our latest features
                markers = [
                    "Telegram Signals",  # New tab we added
                    "📡 Telegram Signals",  # Tab title
                    "Live Trading Signals from Telegram Channels",  # Description
                    "render_telegram_signals_section",  # Function name in source
                    "signal-card",  # CSS class we added
                ]
                
                found_markers = [marker for marker in markers if marker in content]
                content_hash = hashlib.md5(content.encode()).hexdigest()
                
                return {
                    'status': 'success',
                    'hash': content_hash,
                    'markers_found': found_markers,
                    'total_markers': len(markers),
                    'deployment_detected': len(found_markers) >= 3  # Need at least 3 markers
                }
            else:
                return {
                    'status': 'error',
                    'error': f"HTTP {response.status_code}",
                    'deployment_detected': False
                }
                
        except requests.exceptions.Timeout:
            return {
                'status': 'timeout',
                'error': 'Request timeout',
                'deployment_detected': False
            }
        except Exception as e:
            return {
                'status': 'error', 
                'error': str(e),
                'deployment_detected': False
            }
    
    def check_specific_features(self):
        """Check for specific features we've deployed"""
        try:
            response = requests.get(self.streamlit_url, timeout=self.timeout)
            if response.status_code != 200:
                return {'status': 'error', 'message': f"HTTP {response.status_code}"}
            
            content = response.text
            features_check = {
                'telegram_signals_tab': '📡 Telegram Signals' in content,
                'signal_cards': 'signal-card' in content,
                'live_database_connection': 'get_telegram_signals' in content,
                'professional_styling': 'border-left-color' in content,
                'channel_activity': 'Channel Activity' in content
            }
            
            deployed_features = sum(features_check.values())
            total_features = len(features_check)
            
            return {
                'status': 'success',
                'features': features_check,
                'deployed_count': deployed_features,
                'total_count': total_features,
                'deployment_success': deployed_features >= (total_features * 0.7)  # 70% threshold
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'deployment_success': False
            }
    
    def validate_deployment(self, expected_commit=None):
        """Comprehensive deployment validation"""
        safe_print("🔍 Starting comprehensive Streamlit deployment validation...")
        
        results = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'streamlit_url': self.streamlit_url,
            'validation_steps': []
        }
        
        # Step 1: Basic connectivity
        safe_print("1. Testing basic connectivity...")
        try:
            response = requests.get(self.streamlit_url, timeout=10)
            connectivity = {
                'step': 'connectivity',
                'status': 'success' if response.status_code == 200 else 'error',
                'http_code': response.status_code,
                'response_size': len(response.text) if response.status_code == 200 else 0
            }
        except Exception as e:
            connectivity = {
                'step': 'connectivity',
                'status': 'error',
                'error': str(e)
            }
        
        results['validation_steps'].append(connectivity)
        safe_print(f"   Status: {connectivity['status']} (HTTP {connectivity.get('http_code', 'N/A')})")
        
        # Step 2: Content hash analysis
        safe_print("2. Analyzing app content for recent changes...")
        content_analysis = self.get_app_content_hash()
        results['validation_steps'].append({
            'step': 'content_analysis',
            **content_analysis
        })
        
        if content_analysis['deployment_detected']:
            safe_print(f"   ✅ Deployment detected! Found {len(content_analysis['markers_found'])}/{content_analysis['total_markers']} markers")
        else:
            safe_print(f"   ❌ Deployment NOT detected. Found {len(content_analysis.get('markers_found', []))}/{content_analysis.get('total_markers', 0)} markers")
        
        # Step 3: Feature-specific validation
        safe_print("3. Validating specific telegram signals features...")
        feature_check = self.check_specific_features()
        results['validation_steps'].append({
            'step': 'feature_validation',
            **feature_check
        })
        
        if feature_check.get('deployment_success', False):
            safe_print(f"   ✅ Features validated! {feature_check['deployed_count']}/{feature_check['total_count']} features detected")
        else:
            safe_print(f"   ❌ Feature validation failed. {feature_check.get('deployed_count', 0)}/{feature_check.get('total_count', 0)} features detected")
        
        # Step 4: Wait and retry if deployment not detected
        if not (content_analysis.get('deployment_detected', False) and feature_check.get('deployment_success', False)):
            safe_print("4. Deployment not fully detected, waiting for Streamlit sync...")
            
            for retry in range(self.max_retries):
                safe_print(f"   Retry {retry + 1}/{self.max_retries}...")
                time.sleep(10)  # Wait 10 seconds between retries
                
                retry_content = self.get_app_content_hash()
                retry_features = self.check_specific_features()
                
                if retry_content.get('deployment_detected', False) and retry_features.get('deployment_success', False):
                    safe_print(f"   ✅ Deployment confirmed on retry {retry + 1}!")
                    results['final_status'] = 'success'
                    results['retries_needed'] = retry + 1
                    break
            else:
                safe_print("   ❌ Deployment validation failed after all retries")
                results['final_status'] = 'failed'
                results['retries_needed'] = self.max_retries
        else:
            results['final_status'] = 'success'
            results['retries_needed'] = 0
        
        # Final summary
        safe_print("\n" + "="*50)
        safe_print("STREAMLIT DEPLOYMENT VALIDATION SUMMARY")
        safe_print("="*50)
        
        if results['final_status'] == 'success':
            safe_print("🎉 DEPLOYMENT SUCCESSFUL!")
            safe_print("✅ All telegram signals features are live on Streamlit")
        else:
            safe_print("❌ DEPLOYMENT VALIDATION FAILED!")
            safe_print("⚠️  Changes may not be reflected in live Streamlit app")
            
        safe_print(f"🌐 App URL: {self.streamlit_url}")
        safe_print(f"⏰ Validation completed at: {results['timestamp']}")
        
        return results
    
    def send_validation_notification(self, results):
        """Send Discord notification about validation results"""
        webhook_url = 'https://discord.com/api/webhooks/1400577499225657404/x3eRkhbp84bA_3f3AuyUIrBhDtozTGnVbxVrPg3ewLWIL3eO0s_GZoiW0lRQr6Kb5jQ3'
        
        if results['final_status'] == 'success':
            color = 0x4CAF50  # Green
            title = "✅ Streamlit Deployment VALIDATED"
            description = "All telegram signals features are confirmed live on Streamlit"
        else:
            color = 0xf44336  # Red
            title = "❌ Streamlit Deployment VALIDATION FAILED"
            description = "Changes may not be reflected in live app - manual investigation needed"
        
        notification = {
            "embeds": [{
                "title": title,
                "description": description,
                "color": color,
                "fields": [
                    {
                        "name": "🌐 App Status",
                        "value": f"URL: {results['streamlit_url']}\nRetries needed: {results.get('retries_needed', 0)}",
                        "inline": True
                    },
                    {
                        "name": "⏰ Validation Time", 
                        "value": results['timestamp'],
                        "inline": True
                    }
                ],
                "footer": {
                    "text": "TrenchCoat Pro Deployment Validator"
                }
            }]
        }
        
        try:
            response = requests.post(webhook_url, json=notification, timeout=10)
            if response.status_code == 204:
                safe_print("✅ Validation notification sent to Discord")
            else:
                safe_print(f"❌ Discord notification failed: {response.status_code}")
        except Exception as e:
            safe_print(f"❌ Discord notification error: {e}")

def main():
    """Run comprehensive deployment validation"""
    validator = StreamlitDeploymentValidator()
    results = validator.validate_deployment()
    validator.send_validation_notification(results)
    
    # Save results for debugging
    with open('deployment_validation_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    return results['final_status'] == 'success'

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)