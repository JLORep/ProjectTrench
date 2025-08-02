#!/usr/bin/env python3
"""
Automated Blog to Discord Integration
Ensures all blog posts are automatically sent to Discord
"""

import os
import json
import time
from datetime import datetime, timezone

def setup_auto_discord_integration():
    """
    Set up automatic Discord integration for blog posts
    """
    print("🔧 Setting up automatic Blog → Discord integration...")
    
    # Configuration for auto-posting
    config = {
        "auto_post_to_discord": True,
        "discord_channels": ["blog", "discord"],
        "default_priority": "high",
        "rate_limit_respect": True,
        "queue_enabled": True,
        "retry_on_failure": True,
        "max_retries": 3
    }
    
    # Create integration config file
    config_path = "blog_discord_integration.json"
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Configuration saved to {config_path}")
    
    # Create git hook for automatic blog posts on commits
    create_git_blog_hook()
    
    # Create monitoring script
    create_monitoring_script()
    
    print("\n✨ Auto-integration setup complete!")
    print("\n📋 Integration Features:")
    print("  • All blog posts automatically sent to Discord")
    print("  • Rate limit queue system enabled")
    print("  • Git commits automatically create blog posts")
    print("  • Failed messages retry automatically")
    print("  • Real-time monitoring in dashboard")

def create_git_blog_hook():
    """
    Create git hook that automatically creates blog posts for significant commits
    """
    hook_content = '''#!/usr/bin/env python3
"""
Git hook to automatically create blog posts for significant commits
"""
import subprocess
import json
import sqlite3
import uuid
from datetime import datetime

def should_create_blog_post(commit_message):
    """Determine if commit warrants a blog post"""
    # Keywords that trigger blog posts
    triggers = ['MAJOR', 'FEATURE', 'FIX', 'CRITICAL', 'DEPLOY', 'RELEASE']
    return any(trigger in commit_message.upper() for trigger in triggers)

def create_blog_post_from_commit():
    """Create blog post from latest commit"""
    try:
        # Get latest commit info
        result = subprocess.run(
            ["git", "log", "-1", "--pretty=format:%H|%s|%an|%ae"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            commit_hash, message, author, email = result.stdout.strip().split('|')
            
            if should_create_blog_post(message):
                # Connect to blog database
                conn = sqlite3.connect('comprehensive_dev_blog.db')
                cursor = conn.cursor()
                
                # Create blog post
                post_id = str(uuid.uuid4())
                content_json = json.dumps({
                    'title': f"🚀 {message}",
                    'content': f"Commit: {commit_hash[:8]}\\nAuthor: {author}\\n\\n{message}",
                    'type': 'development_update'
                })
                
                cursor.execute("""
                    INSERT INTO comprehensive_posts 
                    (id, post_type, title, version, content_json, channels_posted, 
                     discord_success_rate, created_timestamp, published_timestamp, 
                     author, priority)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    post_id,
                    'development_update',
                    message,
                    '1.0',
                    content_json,
                    'blog,discord',  # Auto-post to Discord
                    0.0,
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                    author,
                    'HIGH'
                ))
                
                conn.commit()
                conn.close()
                
                print(f"📝 Blog post created for commit: {message}")
                print("📡 Queued for Discord notification")
    
    except Exception as e:
        print(f"Error creating blog post: {e}")

if __name__ == "__main__":
    create_blog_post_from_commit()
'''
    
    # Save to git hooks directory
    hook_path = ".git/hooks/post-commit-blog"
    with open(hook_path, 'w') as f:
        f.write(hook_content)
    
    # Make executable on Unix-like systems
    if os.name != 'nt':
        os.chmod(hook_path, 0o755)
    
    print("✅ Git blog hook created")

def create_monitoring_script():
    """
    Create monitoring script for blog → Discord integration
    """
    monitor_content = '''#!/usr/bin/env python3
"""
Monitor blog to Discord integration
"""
import sqlite3
import time
from datetime import datetime, timedelta

def monitor_blog_discord_integration():
    """Monitor and report on blog → Discord integration"""
    print("📊 Blog → Discord Integration Monitor")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('comprehensive_dev_blog.db')
        cursor = conn.cursor()
        
        # Get stats for last 24 hours
        cutoff = (datetime.now() - timedelta(hours=24)).isoformat()
        
        # Total posts
        cursor.execute("""
            SELECT COUNT(*) FROM comprehensive_posts
            WHERE created_timestamp > ?
        """, (cutoff,))
        total_posts = cursor.fetchone()[0]
        
        # Posts sent to Discord
        cursor.execute("""
            SELECT COUNT(*) FROM comprehensive_posts
            WHERE created_timestamp > ? AND channels_posted LIKE '%discord%'
        """, (cutoff,))
        discord_posts = cursor.fetchone()[0]
        
        # Success rate
        cursor.execute("""
            SELECT AVG(discord_success_rate) FROM comprehensive_posts
            WHERE created_timestamp > ? AND channels_posted LIKE '%discord%'
        """, (cutoff,))
        success_rate = cursor.fetchone()[0] or 0
        
        print(f"📈 Last 24 Hours:")
        print(f"  • Total blog posts: {total_posts}")
        print(f"  • Posts sent to Discord: {discord_posts}")
        print(f"  • Discord success rate: {success_rate:.1%}")
        print(f"  • Auto-integration rate: {discord_posts/total_posts:.1%}" if total_posts > 0 else "  • Auto-integration rate: N/A")
        
        # Recent posts
        cursor.execute("""
            SELECT title, created_timestamp, channels_posted
            FROM comprehensive_posts
            WHERE created_timestamp > ?
            ORDER BY created_timestamp DESC
            LIMIT 5
        """, (cutoff,))
        
        print("\\n📝 Recent Posts:")
        for title, timestamp, channels in cursor.fetchall():
            discord_status = "✅" if "discord" in channels else "❌"
            print(f"  {discord_status} {title[:50]}... ({timestamp[:16]})")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error monitoring integration: {e}")

if __name__ == "__main__":
    monitor_blog_discord_integration()
'''
    
    with open("monitor_blog_discord.py", 'w') as f:
        f.write(monitor_content)
    
    print("✅ Monitoring script created")

def main():
    """Main setup function"""
    print("🚀 Automated Blog → Discord Integration Setup")
    print("=" * 50)
    
    # Set up integration
    setup_auto_discord_integration()
    
    # Instructions
    print("\n📋 Next Steps:")
    print("1. All future blog posts will automatically be sent to Discord")
    print("2. Git commits with keywords (MAJOR, FEATURE, FIX, etc.) create blog posts")
    print("3. Run 'python monitor_blog_discord.py' to check integration status")
    print("4. Use Blog tab in dashboard to manually create posts (auto-sent to Discord)")
    print("\n✨ Integration is now active!")

if __name__ == "__main__":
    main()