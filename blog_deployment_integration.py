#!/usr/bin/env python3
"""
Blog Deployment Integration - Automatic blog posting after deployments
Includes intelligent Discord routing
"""

import sqlite3
import json
import subprocess
import requests
from datetime import datetime
from typing import Dict, List, Optional

class BlogDeploymentIntegration:
    """Handles automatic blog posting after deployments"""
    
    def __init__(self):
        self.db_path = "comprehensive_dev_blog.db"
        
        # Discord webhooks for intelligent routing
        self.webhooks = {
            'bug_fix': 'https://discord.com/api/webhooks/1400567015089115177/dtKTrDobQMgXRMTdXfvDMai33SWYFTmqqIDSxlLnJDJwQPHt80zLkV_mqltD_wqq37wc',
            'feature': 'https://discord.com/api/webhooks/1400491407550058610/Q59NIxt5lSvFgpwckXOv_P9TF8uWjudOTJxEw5hZ3fL61Dg2-WgSwrpIb110UiG4Z1f7',
            'deployment': 'https://discord.com/api/webhooks/1400577499225657404/x3eRkhbp84bA_3f3AuyUIrBhDtozTGnVbxVrPg3ewLWIL3eO0s_GZoiW0lRQr6Kb5jQ3',
            'system_update': 'https://discord.com/api/webhooks/1400577499225657404/x3eRkhbp84bA_3f3AuyUIrBhDtozTGnVbxVrPg3ewLWIL3eO0s_GZoiW0lRQr6Kb5jQ3',
            'default': 'https://discord.com/api/webhooks/1400491407550058610/Q59NIxt5lSvFgpwckXOv_P9TF8uWjudOTJxEw5hZ3fL61Dg2-WgSwrpIb110UiG4Z1f7'
        }
    
    def get_deployment_details(self) -> Dict:
        """Get details about the current deployment"""
        try:
            # Get commit info
            commit_hash = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True, text=True, encoding='utf-8'
            ).stdout.strip()[:8]
            
            commit_msg = subprocess.run(
                ["git", "log", "-1", "--pretty=%s"],
                capture_output=True, text=True, encoding='utf-8'
            ).stdout.strip()
            
            author = subprocess.run(
                ["git", "log", "-1", "--pretty=%an"],
                capture_output=True, text=True, encoding='utf-8'
            ).stdout.strip()
            
            # Get changed files
            files = subprocess.run(
                ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"],
                capture_output=True, text=True, encoding='utf-8'
            ).stdout.strip().split('\n')
            
            # Get stats
            stats = subprocess.run(
                ["git", "diff", "--shortstat", "HEAD~1", "HEAD"],
                capture_output=True, text=True, encoding='utf-8'
            ).stdout.strip()
            
            return {
                'hash': commit_hash,
                'message': commit_msg,
                'author': author,
                'files': [f for f in files if f],
                'stats': stats,
                'timestamp': datetime.now()
            }
        except Exception as e:
            print(f"Error getting deployment details: {e}")
            return {}
    
    def determine_post_type(self, commit_msg: str, files: List[str]) -> str:
        """Determine the type of deployment based on commit and files"""
        msg_lower = commit_msg.lower()
        
        # Check commit message
        if any(word in msg_lower for word in ['fix', 'bug', 'error', 'issue']):
            return 'bug_fix'
        elif any(word in msg_lower for word in ['feature', 'add', 'new', 'implement']):
            return 'feature'
        elif any(word in msg_lower for word in ['deploy', 'release']):
            return 'deployment'
        elif any(word in msg_lower for word in ['update', 'upgrade', 'dependency']):
            return 'system_update'
        elif any(word in msg_lower for word in ['ui', 'ux', 'interface']):
            return 'ui_update'
        
        # Check files
        if any('requirements.txt' in f for f in files):
            return 'system_update'
        elif any(f.endswith('.md') for f in files):
            return 'documentation'
            
        return 'update'
    
    def create_blog_post(self, details: Dict, validation_passed: bool) -> Dict:
        """Create a blog post from deployment details"""
        post_type = self.determine_post_type(
            details.get('message', ''),
            details.get('files', [])
        )
        
        # Build content
        content = f"""**🚀 Automated Deployment Update**

**Commit:** `{details.get('hash', 'unknown')}`
**Author:** {details.get('author', 'Unknown')}
**Status:** {"✅ Validation Passed" if validation_passed else "⚠️ Deployed with warnings"}
**Time:** {details.get('timestamp', datetime.now()).strftime('%Y-%m-%d %H:%M:%S')}

**Message:** {details.get('message', 'No commit message')}

"""
        
        if details.get('stats'):
            content += f"**Changes:** {details['stats']}\n\n"
        
        # Add file changes (limit to 10)
        if details.get('files'):
            content += "**Files Changed:**\n"
            for file in details['files'][:10]:
                content += f"- `{file}`\n"
            if len(details['files']) > 10:
                content += f"- ... and {len(details['files']) - 10} more files\n"
            content += "\n"
        
        # Add deployment notes
        if post_type == 'bug_fix':
            content += "🐛 This fix improves system stability and reliability.\n"
        elif post_type == 'feature':
            content += "✨ New functionality has been added to enhance the platform.\n"
        elif post_type == 'system_update':
            content += "🔧 System dependencies or configuration have been updated.\n"
        
        content += "\n*This post was automatically generated by the deployment system.*"
        
        return {
            'title': details.get('message', 'Deployment Update'),
            'content': content,
            'type': post_type,
            'author': details.get('author', 'Deployment Bot'),
            'commit_hash': details.get('hash', ''),
            'priority': 'high' if post_type in ['bug_fix', 'deployment'] else 'normal'
        }
    
    def save_to_blog(self, post: Dict) -> bool:
        """Save the blog post to the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            post_id = f"deploy_{post['commit_hash']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            content_json = json.dumps({
                'content': post['content'],
                'type': post['type'],
                'commit_hash': post['commit_hash'],
                'auto_generated': True
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
                post['title'],
                '1.0',
                content_json,
                '["dev-blog", "system-updates"]',
                0.0,
                datetime.now().isoformat(),
                datetime.now().isoformat(),
                post['author'],
                post['priority']
            ))
            
            conn.commit()
            conn.close()
            
            print(f"✅ Blog post saved: {post_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving blog post: {e}")
            return False
    
    def send_to_discord(self, post: Dict) -> bool:
        """Send the blog post to Discord with intelligent routing"""
        try:
            # Get appropriate webhook
            webhook_url = self.webhooks.get(post['type'], self.webhooks['default'])
            
            # Create embed
            color_map = {
                'bug_fix': 0xFF6B6B,
                'feature': 0x4ECDC4,
                'deployment': 0x45B7D1,
                'system_update': 0x9400D3,
                'ui_update': 0x1E90FF,
                'documentation': 0xF7DC6F
            }
            
            embed = {
                "title": f"🚀 {post['title']}",
                "description": post['content'][:2000],  # Discord limit
                "color": color_map.get(post['type'], 0x10b981),
                "fields": [
                    {"name": "Type", "value": post['type'].replace('_', ' ').title(), "inline": True},
                    {"name": "Priority", "value": post['priority'].title(), "inline": True},
                    {"name": "Author", "value": post['author'], "inline": True}
                ],
                "footer": {"text": "TrenchCoat Pro • Automated Deployment"},
                "timestamp": datetime.utcnow().isoformat()
            }
            
            response = requests.post(
                webhook_url,
                json={"embeds": [embed]},
                timeout=10
            )
            
            if response.status_code == 204:
                print(f"✅ Sent to Discord (#{post['type']} channel)")
                return True
            else:
                print(f"⚠️ Discord returned: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending to Discord: {e}")
            return False
    
    def post_deployment_update(self, validation_passed: bool = True):
        """Main method to create and post deployment update"""
        print("📝 Creating deployment blog post...")
        
        # Get deployment details
        details = self.get_deployment_details()
        if not details:
            print("❌ Could not get deployment details")
            return False
        
        # Create blog post
        post = self.create_blog_post(details, validation_passed)
        
        # Save to blog
        if self.save_to_blog(post):
            # Send to Discord
            self.send_to_discord(post)
            return True
        
        return False

def integrate_with_post_commit():
    """Generate integration code for post-commit hook"""
    integration_code = '''
# Add this to the post-commit hook after validation:

# Trigger blog system
try:
    from blog_deployment_integration import BlogDeploymentIntegration
    blog_integration = BlogDeploymentIntegration()
    blog_integration.post_deployment_update(validation_passed=result.returncode == 0)
except Exception as e:
    log(f"⚠️ Blog integration error (non-blocking): {e}")
'''
    
    print("\n📋 Integration Instructions:")
    print(integration_code)
    print("\n✅ The system will now automatically:")
    print("   • Create blog posts for every deployment")
    print("   • Route to appropriate Discord channels")
    print("   • Track deployment history in the blog")
    print("   • Show validation status")

if __name__ == "__main__":
    # Test the system
    print("🧪 Testing Blog Deployment Integration...")
    
    integration = BlogDeploymentIntegration()
    
    # Get current deployment details
    details = integration.get_deployment_details()
    print(f"\n📊 Current deployment:")
    print(f"   • Commit: {details.get('hash', 'unknown')}")
    print(f"   • Message: {details.get('message', 'none')}")
    print(f"   • Author: {details.get('author', 'unknown')}")
    
    # Test blog post creation
    if input("\n🚀 Create test blog post? (y/n): ").lower() == 'y':
        integration.post_deployment_update(validation_passed=True)
    
    # Show integration instructions
    integrate_with_post_commit()