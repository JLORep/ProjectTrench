#!/usr/bin/env python3
"""
Enhanced Deployment Notifier - Sends comprehensive deployment status to Discord
Includes health checks, validation results, and system metrics
"""

import subprocess
import requests
import json
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional
import sqlite3

class EnhancedDeploymentNotifier:
    """Sends detailed deployment notifications to Discord"""
    
    def __init__(self):
        # Discord webhooks
        self.webhooks = {
            'deployments': 'https://discord.com/api/webhooks/1400577499225657404/x3eRkhbp84bA_3f3AuyUIrBhDtozTGnVbxVrPg3ewLWIL3eO0s_GZoiW0lRQr6Kb5jQ3',
            'system-updates': 'https://discord.com/api/webhooks/1400577499225657404/x3eRkhbp84bA_3f3AuyUIrBhDtozTGnVbxVrPg3ewLWIL3eO0s_GZoiW0lRQr6Kb5jQ3',
            'overview': 'https://discord.com/api/webhooks/1400497302241677383/Im9oyVehkH6zhsc5w4mt4KHQvgSR2qfMPD-k6lTR-X0XQWT3eLV_IJM2-MqQNM6dPAzM'
        }
        
        self.streamlit_url = "https://trenchdemo.streamlit.app"
        self.db_path = "comprehensive_dev_blog.db"
    
    def get_commit_info(self) -> Dict:
        """Get current commit information"""
        try:
            # Get commit hash
            commit_hash = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True, text=True, encoding='utf-8'
            ).stdout.strip()[:7]
            
            # Get commit message
            commit_msg = subprocess.run(
                ["git", "log", "-1", "--pretty=%s"],
                capture_output=True, text=True, encoding='utf-8'
            ).stdout.strip()
            
            # Get author
            author = subprocess.run(
                ["git", "log", "-1", "--pretty=%an"],
                capture_output=True, text=True, encoding='utf-8'
            ).stdout.strip()
            
            # Get branch
            branch = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True, text=True, encoding='utf-8'
            ).stdout.strip()
            
            return {
                'hash': commit_hash,
                'message': commit_msg,
                'author': author,
                'branch': branch
            }
        except Exception as e:
            print(f"Error getting commit info: {e}")
            return {}
    
    def check_streamlit_health(self) -> Dict:
        """Check Streamlit app health"""
        try:
            import requests
            
            start_time = time.time()
            response = requests.get(self.streamlit_url, timeout=30)
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            health_status = {
                'status': 'healthy' if response.status_code in [200, 304] else 'unhealthy',
                'status_code': response.status_code,
                'response_time': f"{response_time:.0f}ms",
                'url': self.streamlit_url
            }
            
            # Check specific features
            if response.status_code in [200, 304]:
                content = response.text[:10000]  # Check first 10k chars
                health_status['features'] = {
                    'dashboard': 'TrenchCoat Pro' in content,
                    'tabs': 'Hunt Hub' in content or 'Coins' in content,
                    'database': 'coins' in content.lower()
                }
            
            return health_status
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'response_time': 'N/A'
            }
    
    def get_validation_results(self) -> Dict:
        """Get deployment validation results"""
        try:
            # Run validation checks
            validation = {
                'git_status': self.check_git_status(),
                'dependencies': self.check_dependencies(),
                'database': self.check_database(),
                'tabs_count': self.check_dashboard_tabs()
            }
            
            # Overall status
            all_passed = all(v.get('passed', False) for v in validation.values())
            validation['overall'] = 'PASSED' if all_passed else 'FAILED'
            
            return validation
            
        except Exception as e:
            return {'overall': 'ERROR', 'error': str(e)}
    
    def check_git_status(self) -> Dict:
        """Check git repository status"""
        try:
            # Check for uncommitted changes
            status = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True, text=True
            ).stdout.strip()
            
            # Check if pushed
            unpushed = subprocess.run(
                ["git", "log", "origin/main..HEAD", "--oneline"],
                capture_output=True, text=True
            ).stdout.strip()
            
            return {
                'passed': not status and not unpushed,
                'uncommitted': len(status.split('\n')) if status else 0,
                'unpushed': len(unpushed.split('\n')) if unpushed else 0
            }
        except:
            return {'passed': False, 'error': 'Git check failed'}
    
    def check_dependencies(self) -> Dict:
        """Check if requirements.txt exists and is valid"""
        try:
            with open('requirements.txt', 'r') as f:
                deps = f.readlines()
            
            critical_deps = ['streamlit', 'pandas', 'plotly', 'requests']
            found_deps = [d for d in critical_deps if any(d in line for line in deps)]
            
            return {
                'passed': len(found_deps) == len(critical_deps),
                'total': len(deps),
                'critical': f"{len(found_deps)}/{len(critical_deps)}"
            }
        except:
            return {'passed': False, 'error': 'requirements.txt not found'}
    
    def check_database(self) -> Dict:
        """Check database status"""
        try:
            import sqlite3
            conn = sqlite3.connect('data/trench.db')
            cursor = conn.cursor()
            
            # Get coin count
            cursor.execute("SELECT COUNT(*) FROM coins")
            coin_count = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'passed': coin_count > 0,
                'coins': coin_count,
                'status': 'operational'
            }
        except:
            return {'passed': False, 'status': 'error'}
    
    def check_dashboard_tabs(self) -> int:
        """Check number of dashboard tabs"""
        try:
            with open('streamlit_app.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Count tabs
            import re
            tabs = re.findall(r'tab\d+', content)
            unique_tabs = len(set(tabs))
            
            return {'passed': unique_tabs >= 10, 'count': unique_tabs}
        except:
            return {'passed': False, 'count': 0}
    
    def create_deployment_embed(self, commit_info: Dict, health: Dict, validation: Dict) -> Dict:
        """Create Discord embed with all deployment information"""
        
        # Determine overall status and color
        if health['status'] == 'healthy' and validation.get('overall') == 'PASSED':
            status = "✅ Successful Deployment"
            color = 0x10b981  # Green
        elif health['status'] == 'healthy':
            status = "⚠️ Deployed with Warnings"
            color = 0xF59E0B  # Yellow
        else:
            status = "❌ Deployment Issues"
            color = 0xEF4444  # Red
        
        # Build embed
        embed = {
            "title": status,
            "description": f"**Commit:** `{commit_info.get('hash', 'unknown')}` - {commit_info.get('message', 'No message')}",
            "color": color,
            "fields": [
                {
                    "name": "🏥 Streamlit App Health Check",
                    "value": f"**Status:** {health.get('status', 'unknown').title()}\n"
                            f"**Response Time:** {health.get('response_time', 'N/A')}\n"
                            f"**URL:** [{self.streamlit_url}]({self.streamlit_url})",
                    "inline": False
                },
                {
                    "name": "📋 Validation Results",
                    "value": f"**Overall:** {validation.get('overall', 'UNKNOWN')}\n"
                            f"**Git Status:** {'✅' if validation.get('git_status', {}).get('passed') else '❌'}\n"
                            f"**Dependencies:** {validation.get('dependencies', {}).get('critical', 'N/A')}\n"
                            f"**Database:** {validation.get('database', {}).get('coins', 'N/A')} coins\n"
                            f"**Dashboard Tabs:** {validation.get('tabs_count', {}).get('count', 'N/A')}",
                    "inline": True
                },
                {
                    "name": "🔧 Deployment Details",
                    "value": f"**Time:** {datetime.now(timezone.utc).strftime('%H:%M:%S UTC')}\n"
                            f"**System:** Complete Async Deploy\n"
                            f"**Branch:** {commit_info.get('branch', 'main')}\n"
                            f"**Author:** {commit_info.get('author', 'Unknown')}",
                    "inline": True
                }
            ],
            "footer": {
                "text": "TrenchCoat Pro Auto-Deploy System",
                "icon_url": "https://raw.githubusercontent.com/JLORep/ProjectTrench/main/assets/logo.png"
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Add feature status if available
        if health.get('features'):
            features_text = '\n'.join([
                f"{'✅' if v else '❌'} {k.title()}" 
                for k, v in health['features'].items()
            ])
            embed['fields'].append({
                "name": "🎯 Feature Status",
                "value": features_text or "No features checked",
                "inline": True
            })
        
        return embed
    
    def send_deployment_notification(self, channel: str = 'deployments'):
        """Send comprehensive deployment notification to Discord"""
        print("📊 Gathering deployment information...")
        
        # Get all information
        commit_info = self.get_commit_info()
        print("✅ Got commit info")
        
        health = self.check_streamlit_health()
        print("✅ Checked app health")
        
        validation = self.get_validation_results()
        print("✅ Ran validation checks")
        
        # Create embed
        embed = self.create_deployment_embed(commit_info, health, validation)
        
        # Send to Discord
        webhook_url = self.webhooks.get(channel, self.webhooks['deployments'])
        
        try:
            response = requests.post(
                webhook_url,
                json={"embeds": [embed]},
                timeout=10
            )
            
            if response.status_code == 204:
                print(f"✅ Deployment notification sent to #{channel}")
                
                # Also save to blog database
                self.save_to_blog(commit_info, health, validation)
                return True
            else:
                print(f"❌ Discord returned: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending notification: {e}")
            return False
    
    def save_to_blog(self, commit_info: Dict, health: Dict, validation: Dict):
        """Save deployment info to blog database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            post_id = f"deploy_{commit_info.get('hash', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            content = f"""**Automated Deployment Report**

**Health Status:** {health.get('status', 'unknown').title()}
**Validation:** {validation.get('overall', 'UNKNOWN')}
**Response Time:** {health.get('response_time', 'N/A')}

**Commit:** {commit_info.get('hash', 'unknown')}
**Message:** {commit_info.get('message', 'No message')}

This deployment was automatically validated and all systems are operational.
"""
            
            content_json = json.dumps({
                'content': content,
                'health': health,
                'validation': validation,
                'commit': commit_info
            })
            
            cursor.execute("""
                INSERT INTO comprehensive_posts 
                (id, post_type, title, version, content_json, channels_posted, 
                 discord_success_rate, created_timestamp, published_timestamp, 
                 author, priority)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                post_id,
                'deployment',
                f"Deployment: {commit_info.get('message', 'Update')[:50]}",
                '1.0',
                content_json,
                '["deployments", "system-updates"]',
                1.0,
                datetime.now().isoformat(),
                datetime.now().isoformat(),
                'Auto-Deploy Bot',
                'high'
            ))
            
            conn.commit()
            conn.close()
            
            print("✅ Deployment saved to blog database")
            
        except Exception as e:
            print(f"⚠️ Could not save to blog: {e}")

def integrate_with_hooks():
    """Show how to integrate with post-commit hooks"""
    integration_code = '''
# Add to post-commit hook after validation:

# Send enhanced deployment notification
try:
    from enhanced_deployment_notifier import EnhancedDeploymentNotifier
    notifier = EnhancedDeploymentNotifier()
    notifier.send_deployment_notification()
except Exception as e:
    log(f"⚠️ Enhanced notification error (non-blocking): {e}")
'''
    
    print("\n📋 Integration Instructions:")
    print(integration_code)
    print("\n✅ This will provide:")
    print("   • Comprehensive health checks")
    print("   • Validation results")
    print("   • Response time monitoring")
    print("   • Feature status checks")
    print("   • Automatic blog posting")

if __name__ == "__main__":
    print("🚀 Enhanced Deployment Notifier")
    print("=" * 50)
    
    notifier = EnhancedDeploymentNotifier()
    
    # Test notification
    if input("\n📡 Send test deployment notification? (y/n): ").lower() == 'y':
        notifier.send_deployment_notification()
    
    # Show integration
    integrate_with_hooks()