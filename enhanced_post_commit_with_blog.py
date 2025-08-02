#!/usr/bin/env python3
"""
TrenchCoat Pro - Enhanced Post-Commit Hook with Dev Blog Integration
Automatically deploys, validates, and creates dev blog posts after each commit
"""
import subprocess
import sys
import time
import os
import json
from datetime import datetime
from typing import Dict, List, Optional

def log(message):
    """Log with timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

def suppress_gc_error():
    """Suppress git gc errors by disabling auto gc"""
    try:
        subprocess.run(["git", "config", "gc.auto", "0"], capture_output=True)
    except:
        pass

def get_commit_details() -> Dict:
    """Get details of the current commit"""
    try:
        # Get commit hash
        hash_result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        commit_hash = hash_result.stdout.strip()[:8]
        
        # Get commit message
        msg_result = subprocess.run(
            ["git", "log", "-1", "--pretty=%s"],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        commit_message = msg_result.stdout.strip()
        
        # Get author
        author_result = subprocess.run(
            ["git", "log", "-1", "--pretty=%an"],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        author = author_result.stdout.strip()
        
        # Get changed files
        files_result = subprocess.run(
            ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        changed_files = files_result.stdout.strip().split('\n') if files_result.stdout.strip() else []
        
        # Get stats
        stats_result = subprocess.run(
            ["git", "diff", "--shortstat", "HEAD~1", "HEAD"],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        stats = stats_result.stdout.strip()
        
        return {
            'hash': commit_hash,
            'message': commit_message,
            'author': author,
            'files': changed_files,
            'stats': stats,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        log(f"Error getting commit details: {e}")
        return {}

def determine_update_type(commit_message: str, changed_files: List[str]) -> str:
    """Determine the type of update based on commit message and files"""
    msg_lower = commit_message.lower()
    
    # Check commit message patterns
    if any(word in msg_lower for word in ['fix', 'bug', 'error', 'issue']):
        return 'bug_fix'
    elif any(word in msg_lower for word in ['feature', 'add', 'new', 'implement']):
        return 'feature'
    elif any(word in msg_lower for word in ['deploy', 'release']):
        return 'deployment'
    elif any(word in msg_lower for word in ['docs', 'documentation', 'readme']):
        return 'documentation'
    elif any(word in msg_lower for word in ['test', 'testing']):
        return 'testing'
    elif any(word in msg_lower for word in ['refactor', 'optimize', 'performance']):
        return 'performance'
    elif any(word in msg_lower for word in ['ui', 'ux', 'interface', 'design']):
        return 'ui_update'
    
    # Check file patterns
    if any('test' in f for f in changed_files):
        return 'testing'
    elif any('doc' in f.lower() or f.endswith('.md') for f in changed_files):
        return 'documentation'
    
    return 'update'

def create_blog_post(commit_details: Dict, validation_success: bool) -> Dict:
    """Create a dev blog post from commit details"""
    update_type = determine_update_type(
        commit_details.get('message', ''),
        commit_details.get('files', [])
    )
    
    # Build content
    content = f"**Commit:** `{commit_details.get('hash', 'unknown')}`\n\n"
    content += f"**Author:** {commit_details.get('author', 'Unknown')}\n\n"
    
    if commit_details.get('stats'):
        content += f"**Changes:** {commit_details.get('stats')}\n\n"
    
    # Add deployment status
    if validation_success:
        content += "✅ **Deployment Status:** Successfully deployed and validated\n\n"
    else:
        content += "⚠️ **Deployment Status:** Deployed with validation warnings\n\n"
    
    # List changed files (limit to 10)
    if commit_details.get('files'):
        content += "**Files Changed:**\n"
        for file in commit_details.get('files', [])[:10]:
            content += f"- `{file}`\n"
        if len(commit_details.get('files', [])) > 10:
            content += f"- ... and {len(commit_details['files']) - 10} more files\n"
    
    return {
        'title': commit_details.get('message', 'Deployment Update'),
        'content': content,
        'type': update_type,
        'priority': 'high' if update_type in ['bug_fix', 'deployment'] else 'normal',
        'author': commit_details.get('author', 'TrenchCoat Pro Bot'),
        'commit_hash': commit_details.get('hash', '')
    }

def post_to_dev_blog(blog_post: Dict) -> bool:
    """Post update to dev blog system"""
    try:
        # Create a Python script to interact with the blog system
        blog_script = '''
import sys
import json
import sqlite3
from datetime import datetime

# Get blog post data from stdin
post_data = json.loads(sys.argv[1])

# Connect to blog database
conn = sqlite3.connect('comprehensive_dev_blog.db')
cursor = conn.cursor()

# Insert blog post
post_id = f"deploy_{post_data['commit_hash']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

content_json = json.dumps({
    'content': post_data['content'],
    'type': post_data['type'],
    'commit_hash': post_data['commit_hash']
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
    post_data['title'],
    '1.0',
    content_json,
    '["dev-blog", "system-updates"]',
    0.0,
    datetime.now().isoformat(),
    datetime.now().isoformat(),
    post_data['author'],
    post_data['priority']
))

conn.commit()
conn.close()

print(f"Blog post created: {post_id}")
'''
        
        # Save the script temporarily
        with open('temp_blog_post.py', 'w', encoding='utf-8') as f:
            f.write(blog_script)
        
        # Run the script
        result = subprocess.run(
            [sys.executable, 'temp_blog_post.py', json.dumps(blog_post)],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if result.returncode == 0:
            log(f"✅ Dev blog post created: {blog_post['title']}")
            return True
        else:
            log(f"❌ Failed to create blog post: {result.stderr}")
            return False
            
    except Exception as e:
        log(f"❌ Error posting to dev blog: {e}")
        return False
    finally:
        # Clean up temp file
        try:
            os.remove('temp_blog_post.py')
        except:
            pass

def send_to_discord_webhook(blog_post: Dict):
    """Send blog post to Discord via webhook"""
    try:
        import requests
        
        # Determine webhook based on post type
        webhooks = {
            'bug_fix': 'https://discord.com/api/webhooks/1400567015089115177/dtKTrDobQMgXRMTdXfvDMai33SWYFTmqqIDSxlLnJDJwQPHt80zLkV_mqltD_wqq37wc',
            'deployment': 'https://discord.com/api/webhooks/1400577499225657404/x3eRkhbp84bA_3f3AuyUIrBhDtozTGnVbxVrPg3ewLWIL3eO0s_GZoiW0lRQr6Kb5jQ3',
            'feature': 'https://discord.com/api/webhooks/1400491407550058610/Q59NIxt5lSvFgpwckXOv_P9TF8uWjudOTJxEw5hZ3fL61Dg2-WgSwrpIb110UiG4Z1f7',
            'default': 'https://discord.com/api/webhooks/1400491407550058610/Q59NIxt5lSvFgpwckXOv_P9TF8uWjudOTJxEw5hZ3fL61Dg2-WgSwrpIb110UiG4Z1f7'
        }
        
        webhook_url = webhooks.get(blog_post['type'], webhooks['default'])
        
        # Create Discord embed
        color_map = {
            'bug_fix': 0xFF6B6B,
            'feature': 0x4ECDC4,
            'deployment': 0x45B7D1,
            'documentation': 0xF7DC6F,
            'performance': 0x9B59B6,
            'ui_update': 0x1E90FF
        }
        
        embed = {
            "title": f"🚀 {blog_post['title']}",
            "description": blog_post['content'][:2000],  # Discord limit
            "color": color_map.get(blog_post['type'], 0x10b981),
            "fields": [
                {"name": "Type", "value": blog_post['type'].replace('_', ' ').title(), "inline": True},
                {"name": "Priority", "value": blog_post['priority'].title(), "inline": True},
                {"name": "Author", "value": blog_post['author'], "inline": True}
            ],
            "footer": {"text": "TrenchCoat Pro • Automated Deployment Update"},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        response = requests.post(webhook_url, json={"embeds": [embed]}, timeout=10)
        
        if response.status_code == 204:
            log("✅ Deployment update sent to Discord")
            return True
        else:
            log(f"⚠️ Discord webhook returned: {response.status_code}")
            return False
            
    except Exception as e:
        log(f"⚠️ Could not send to Discord: {e}")
        return False

def main():
    log("🚀 Enhanced post-commit hook triggered")
    
    # Suppress gc errors
    suppress_gc_error()
    
    # Get commit details first
    commit_details = get_commit_details()
    validation_success = False
    
    try:
        # Push to GitHub
        log("Pushing to GitHub...")
        result = subprocess.run(
            ["git", "push", "origin", "main"],
            capture_output=True,
            text=True,
            timeout=60,
            encoding='utf-8',
            errors='replace',
            env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"}
        )
        
        if result.returncode != 0:
            error_msg = result.stderr
            if "unable to read" not in error_msg and "failed to run repack" not in error_msg:
                log(f"❌ Push failed: {error_msg}")
                return 1
            
        log("✅ Push successful")
        
        # Wait for Streamlit to pick up changes
        log("Waiting 20 seconds for Streamlit deployment...")
        time.sleep(20)
        
        # Run validation
        log("Running post-deployment validation...")
        result = subprocess.run(
            [sys.executable, "post_deploy_validator.py"],
            capture_output=True,
            text=True,
            timeout=120,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.stdout:
            print(result.stdout)
            
        if result.returncode == 0:
            log("✅ Deployment validation passed")
            validation_success = True
        else:
            log("⚠️ Deployment validation failed (non-blocking)")
            
        # Create and post dev blog update
        if commit_details:
            log("📝 Creating dev blog post...")
            blog_post = create_blog_post(commit_details, validation_success)
            
            # Post to blog system
            if post_to_dev_blog(blog_post):
                # Also send to Discord
                send_to_discord_webhook(blog_post)
            
    except Exception as e:
        log(f"❌ Hook error: {e}")
        
        # Still try to create blog post about the error
        if commit_details:
            error_post = {
                'title': f"Deployment Error: {commit_details.get('message', 'Unknown')}",
                'content': f"Deployment encountered an error:\n\n```\n{str(e)}\n```\n\nCommit: {commit_details.get('hash', 'unknown')}",
                'type': 'bug_fix',
                'priority': 'high',
                'author': 'TrenchCoat Pro Bot',
                'commit_hash': commit_details.get('hash', '')
            }
            post_to_dev_blog(error_post)
        
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main()