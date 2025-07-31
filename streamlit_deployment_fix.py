#!/usr/bin/env python3
"""
Comprehensive Streamlit deployment fix strategy
Analyzes and attempts to resolve deployment issues
"""
import requests
import os
import subprocess
from datetime import datetime
from unicode_handler import safe_print

class StreamlitDeploymentFixer:
    """Diagnose and fix Streamlit deployment issues"""
    
    def __init__(self):
        self.streamlit_url = "https://trenchcoat-pro.streamlit.app/"
        self.alternative_urls = [
            "https://projecttrench.streamlit.app/",
            "https://jlorep-projecttrench.streamlit.app/",
            "https://trenchcoat.streamlit.app/"
        ]
        
    def diagnose_deployment_issue(self):
        """Comprehensive diagnosis of deployment issues"""
        safe_print("🔍 STREAMLIT DEPLOYMENT DIAGNOSIS")
        safe_print("=" * 50)
        
        results = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'primary_url_status': None,
            'alternative_urls': {},
            'github_status': None,
            'local_files': {},
            'recommendations': []
        }
        
        # 1. Test primary URL
        safe_print("1. Testing primary Streamlit URL...")
        try:
            response = requests.get(self.streamlit_url, timeout=10)
            results['primary_url_status'] = {
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'content_length': len(response.text),
                'redirect_url': response.url if response.url != self.streamlit_url else None
            }
            safe_print(f"   Status: HTTP {response.status_code}")
            if response.status_code == 303:
                safe_print(f"   Redirect detected: {response.headers.get('location', 'Unknown')}")
        except Exception as e:
            results['primary_url_status'] = {'error': str(e)}
            safe_print(f"   Error: {e}")
        
        # 2. Test alternative URLs
        safe_print("2. Testing alternative URLs...")
        for url in self.alternative_urls:
            try:
                response = requests.get(url, timeout=5)
                results['alternative_urls'][url] = {
                    'status_code': response.status_code,
                    'accessible': response.status_code == 200
                }
                status = "✅ Working" if response.status_code == 200 else f"❌ HTTP {response.status_code}"
                safe_print(f"   {url}: {status}")
            except Exception as e:
                results['alternative_urls'][url] = {'error': str(e)}
                safe_print(f"   {url}: ❌ Error - {e}")
        
        # 3. Check GitHub repository status
        safe_print("3. Checking GitHub repository...")
        try:
            # Check if we can access the repo
            result = subprocess.run(['git', 'remote', 'get-url', 'origin'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                repo_url = result.stdout.strip()
                results['github_status'] = {'repo_url': repo_url, 'accessible': True}
                safe_print(f"   ✅ Repository: {repo_url}")
                
                # Check if we can push
                result = subprocess.run(['git', 'push', '--dry-run'], 
                                      capture_output=True, text=True, timeout=10)
                results['github_status']['push_accessible'] = result.returncode == 0
                push_status = "✅ Can push" if result.returncode == 0 else "❌ Cannot push"
                safe_print(f"   {push_status}")
            else:
                results['github_status'] = {'error': 'No git remote found'}
                safe_print("   ❌ No git remote configured")
        except Exception as e:
            results['github_status'] = {'error': str(e)}
            safe_print(f"   ❌ Error: {e}")
        
        # 4. Check local files
        safe_print("4. Checking critical local files...")
        critical_files = [
            'streamlit_app.py',
            'ultra_premium_dashboard.py', 
            'requirements.txt',
            'src/data/database.py'
        ]
        
        for file_path in critical_files:
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                results['local_files'][file_path] = {'exists': True, 'size': size}
                safe_print(f"   ✅ {file_path} ({size} bytes)")
            else:
                results['local_files'][file_path] = {'exists': False}
                safe_print(f"   ❌ {file_path} missing")
        
        # 5. Generate recommendations
        safe_print("5. Generating recommendations...")
        recommendations = []
        
        if results['primary_url_status'] and results['primary_url_status'].get('status_code') == 404:
            recommendations.append("PRIMARY ISSUE: Streamlit app returns 404 - app not deployed or deleted")
            recommendations.append("ACTION: Recreate Streamlit Cloud app from GitHub repository")
        
        if results['primary_url_status'] and results['primary_url_status'].get('status_code') == 303:
            recommendations.append("AUTHENTICATION ISSUE: App requires login or has access restrictions")
            recommendations.append("ACTION: Check Streamlit Cloud app settings and make public")
        
        working_alternatives = [url for url, data in results['alternative_urls'].items() 
                              if data.get('accessible', False)]
        if working_alternatives:
            recommendations.append(f"ALTERNATIVE FOUND: {working_alternatives[0]} is accessible")
            recommendations.append("ACTION: Update DNS or use working URL")
        
        if not results['local_files'].get('streamlit_app.py', {}).get('exists', False):
            recommendations.append("CRITICAL: streamlit_app.py missing - required for Streamlit deployment")
            recommendations.append("ACTION: Ensure streamlit_app.py exists in repository root")
        
        results['recommendations'] = recommendations
        
        safe_print("\n📋 RECOMMENDATIONS:")
        for i, rec in enumerate(recommendations, 1):
            safe_print(f"   {i}. {rec}")
        
        return results
    
    def create_deployment_guide(self, results):
        """Create a step-by-step deployment guide"""
        guide = f"""
# Streamlit Deployment Fix Guide
Generated: {results['timestamp']}

## Issue Summary
Primary URL: {self.streamlit_url} returns HTTP {results['primary_url_status'].get('status_code', 'Unknown')}

## Step-by-Step Fix

### 1. Streamlit Cloud Setup
1. Go to https://share.streamlit.io/
2. Sign in with GitHub account
3. Click "New app"
4. Connect to repository: JLORep/ProjectTrench
5. Set branch: main
6. Set main file path: streamlit_app.py
7. Choose app URL: trenchcoat-pro

### 2. Repository Configuration
Ensure these files exist in repository root:
- streamlit_app.py (entry point)
- requirements.txt (dependencies)
- ultra_premium_dashboard.py (main dashboard)

### 3. Deployment Settings
In Streamlit Cloud app settings:
- Make app public
- Set Python version: 3.11
- Add any required secrets/environment variables

### 4. Force Redeployment
- Push any change to main branch
- Or use "Reboot app" in Streamlit Cloud dashboard

## Alternative Solutions
"""
        
        working_alternatives = [url for url, data in results['alternative_urls'].items() 
                              if data.get('accessible', False)]
        if working_alternatives:
            guide += f"- Use working alternative: {working_alternatives[0]}\n"
        else:
            guide += "- No working alternatives found\n"
            
        guide += "\n## Contact Support\nIf issues persist, contact Streamlit support with this diagnostic report.\n"
        
        return guide
    
    def save_diagnostic_report(self, results):
        """Save diagnostic results to file"""
        import json
        
        # Save detailed results
        with open('streamlit_deployment_diagnosis.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Save human-readable guide
        guide = self.create_deployment_guide(results)
        with open('streamlit_deployment_fix_guide.md', 'w') as f:
            f.write(guide)
        
        safe_print(f"\n💾 Diagnostic report saved:")
        safe_print(f"   - streamlit_deployment_diagnosis.json")
        safe_print(f"   - streamlit_deployment_fix_guide.md")
    
    def send_urgent_notification(self, results):
        """Send urgent notification to Discord about deployment failure"""
        webhook_url = 'https://discord.com/api/webhooks/1400577499225657404/x3eRkhbp84bA_3f3AuyUIrBhDtozTGnVbxVrPg3ewLWIL3eO0s_GZoiW0lRQr6Kb5jQ3'
        
        status_code = results['primary_url_status'].get('status_code', 'Unknown')
        working_alternatives = [url for url, data in results['alternative_urls'].items() 
                              if data.get('accessible', False)]
        
        notification = {
            "embeds": [{
                "title": "🚨 CRITICAL: Streamlit Deployment FAILED",
                "description": f"Primary app URL returns HTTP {status_code} - Manual intervention required",
                "color": 0xFF0000,  # Red
                "fields": [
                    {
                        "name": "🌐 App Status",
                        "value": f"URL: {self.streamlit_url}\nStatus: HTTP {status_code}\nAlternatives: {len(working_alternatives)} working",
                        "inline": False
                    },
                    {
                        "name": "🔧 Required Actions",
                        "value": "1. Recreate Streamlit Cloud app\n2. Connect to GitHub repository\n3. Configure app settings\n4. Make app public",
                        "inline": False
                    },
                    {
                        "name": "📊 Repository Status",
                        "value": f"GitHub: {'✅ Accessible' if results['github_status'].get('accessible') else '❌ Issues'}\nFiles: {'✅ Present' if results['local_files'].get('streamlit_app.py', {}).get('exists') else '❌ Missing'}",
                        "inline": True
                    }
                ],
                "footer": {
                    "text": f"Diagnosis completed at {results['timestamp']}"
                }
            }]
        }
        
        try:
            response = requests.post(webhook_url, json=notification, timeout=10)
            if response.status_code == 204:
                safe_print("✅ Urgent notification sent to Discord")
            else:
                safe_print(f"❌ Discord notification failed: {response.status_code}")
        except Exception as e:
            safe_print(f"❌ Discord notification error: {e}")

def main():
    """Run comprehensive Streamlit deployment diagnosis"""
    fixer = StreamlitDeploymentFixer()
    results = fixer.diagnose_deployment_issue()
    fixer.save_diagnostic_report(results)
    fixer.send_urgent_notification(results)
    
    safe_print("\n" + "=" * 50)
    safe_print("STREAMLIT DEPLOYMENT DIAGNOSIS COMPLETE")
    safe_print("=" * 50)
    safe_print("🔍 Review saved diagnostic files for detailed analysis")
    safe_print("📋 Follow fix guide to restore Streamlit deployment")
    
    return results

if __name__ == "__main__":
    main()