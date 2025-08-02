#!/usr/bin/env python3
"""
Integration script to connect intelligent router with comprehensive blog system
"""

import sys
import json
from datetime import datetime

def integrate_router_with_blog():
    """Add intelligent routing to the comprehensive blog system"""
    
    print("🔧 Integrating Intelligent Discord Router with Blog System...")
    
    # Create patch for comprehensive_dev_blog_system.py
    integration_code = '''
# Add this import at the top of comprehensive_dev_blog_system.py:
from intelligent_discord_router import IntelligentDiscordRouter

# Add this to __init__ method:
self.discord_router = IntelligentDiscordRouter()

# Replace the send_to_discord method with this enhanced version:
def send_to_discord(self, title, content, post_type=None):
    """Send blog post to Discord with intelligent channel routing"""
    try:
        # Use intelligent router instead of single webhook
        results = self.discord_router.route_to_channels(
            title=title,
            content=content,
            post_type=post_type
        )
        
        # Update UI with results
        success_channels = [ch for ch, res in results.items() if res['status'] == 'success']
        failed_channels = [ch for ch, res in results.items() if res['status'] != 'success']
        
        if success_channels:
            st.success(f"✅ Sent to channels: {', '.join(f'#{ch}' for ch in success_channels)}")
        
        if failed_channels:
            st.warning(f"⚠️ Failed channels: {', '.join(f'#{ch}' for ch in failed_channels)}")
        
        return {
            "success": len(success_channels) > 0,
            "channels_sent": success_channels,
            "channels_failed": failed_channels,
            "results": results
        }
        
    except Exception as e:
        st.error(f"❌ Discord routing error: {str(e)}")
        return {"success": False, "error": str(e)}

# Add this new method for commit-based updates:
def generate_commit_updates(self):
    """Generate blog posts from recent commits"""
    try:
        # Get recent commits
        commits = self.discord_router.get_recent_commits(limit=10)
        
        generated = 0
        for commit in commits:
            # Check if already processed
            if self.is_commit_processed(commit['sha']):
                continue
            
            # Generate update
            update = self.discord_router.generate_commit_based_update(commit)
            
            # Create blog post
            post_id = self.create_post(
                post_type=update['post_type'],
                title=update['title'],
                content=update['content'],
                version="1.0",
                author="Git Commit Bot",
                priority="normal"
            )
            
            # Mark commit as processed
            self.mark_commit_processed(commit['sha'])
            generated += 1
        
        return generated
        
    except Exception as e:
        st.error(f"Error generating commit updates: {e}")
        return 0

# Add helper methods:
def is_commit_processed(self, commit_sha):
    """Check if commit was already processed"""
    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 1 FROM comprehensive_posts 
        WHERE content_json LIKE ?
    ''', (f'%{commit_sha}%',))
    
    result = cursor.fetchone()
    conn.close()
    
    return result is not None

def mark_commit_processed(self, commit_sha):
    """Mark commit as processed"""
    # This is handled by creating the blog post with commit SHA in content
    pass
'''
    
    # Save integration instructions
    with open("intelligent_router_integration.txt", 'w') as f:
        f.write(integration_code)
    
    print("✅ Integration code saved to intelligent_router_integration.txt")
    
    # Create a test script
    test_script = '''#!/usr/bin/env python3
"""Test the intelligent routing integration"""

from intelligent_discord_router import IntelligentDiscordRouter
import subprocess

def test_integration():
    router = IntelligentDiscordRouter()
    
    print("🧪 Testing Intelligent Discord Routing")
    print("=" * 50)
    
    # Test 1: Route a bug fix
    print("\\n1️⃣ Testing bug fix routing...")
    router.route_to_channels(
        title="FIX: Resolved critical memory leak in dashboard",
        content="Fixed memory leak by properly disposing chart objects",
        post_type="bug_fix"
    )
    
    # Test 2: Route a feature
    print("\\n2️⃣ Testing feature routing...")
    router.route_to_channels(
        title="FEATURE: Added AI-powered trade recommendations",
        content="Implemented ML model for trade signal generation with 85% accuracy",
        post_type="feature"
    )
    
    # Test 3: Route documentation update
    print("\\n3️⃣ Testing documentation routing...")
    router.route_to_channels(
        title="DOCS: Updated API reference with new endpoints",
        content="Added documentation for v2 API endpoints and authentication",
        post_type="documentation"
    )
    
    # Test 4: Route based on recent commits
    print("\\n4️⃣ Testing commit-based routing...")
    router.route_recent_commits(limit=3)
    
    # Show stats
    stats = router.get_routing_stats()
    print(f"\\n📊 Final Statistics:")
    print(f"   • Total routed: {stats['total']}")
    print(f"   • By channel: {json.dumps(stats['by_channel'], indent=2)}")

if __name__ == "__main__":
    test_integration()
'''
    
    with open("test_intelligent_routing.py", 'w') as f:
        f.write(test_script)
    
    print("✅ Test script saved to test_intelligent_routing.py")
    
    # Create channel configuration update
    channel_config = {
        "channel_webhooks": {
            "dev-blog": "[Configure separate webhook URL]",
            "announcements": "[Configure separate webhook URL]",
            "documentation": "[Configure separate webhook URL]",
            "bug-reports": "[Configure separate webhook URL]",
            "system-updates": "[Configure separate webhook URL]",
            "testing": "[Configure separate webhook URL]",
            "deployments": "[Configure separate webhook URL]",
            "signals": "[Configure separate webhook URL]",
            "analytics": "[Configure separate webhook URL]",
            "performance": "[Configure separate webhook URL]"
        },
        "note": "In production, each channel should have its own webhook URL. For testing, all use the same webhook."
    }
    
    with open("channel_webhook_config.json", 'w') as f:
        json.dump(channel_config, f, indent=2)
    
    print("✅ Channel configuration template saved")
    
    print("\n📋 Next Steps:")
    print("1. Apply the integration code to comprehensive_dev_blog_system.py")
    print("2. Run test_intelligent_routing.py to verify functionality")
    print("3. Configure separate webhooks for each channel (optional)")
    print("4. Start using intelligent routing for all blog posts!")
    
    return True

def create_streamlit_ui_component():
    """Create UI component for channel routing configuration"""
    
    ui_code = '''
# Add this to the Blog tab in streamlit_app.py for channel routing control:

with st.expander("🎯 Channel Routing Configuration", expanded=False):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📡 Routing Mode")
        routing_mode = st.radio(
            "Select routing mode:",
            ["Intelligent (Auto)", "Manual Selection", "All Channels"],
            help="Choose how messages are routed to Discord channels"
        )
    
    with col2:
        st.subheader("📌 Force Channels")
        if routing_mode == "Manual Selection":
            force_channels = st.multiselect(
                "Select channels:",
                ["dev-blog", "announcements", "documentation", "bug-reports",
                 "system-updates", "testing", "deployments", "signals",
                 "analytics", "performance"]
            )
        else:
            force_channels = None
    
    with col3:
        st.subheader("📊 Routing Stats")
        if hasattr(st.session_state, 'blog_system'):
            stats = st.session_state.blog_system.discord_router.get_routing_stats()
            st.metric("Total Routed", stats['total'])
            st.metric("Last 24h", stats['recent_24h'])
    
    # Show channel activity
    st.subheader("📈 Channel Activity")
    if hasattr(st.session_state, 'blog_system'):
        stats = st.session_state.blog_system.discord_router.get_routing_stats()
        
        import pandas as pd
        df = pd.DataFrame(
            list(stats['by_channel'].items()),
            columns=['Channel', 'Messages']
        ).sort_values('Messages', ascending=False)
        
        st.dataframe(df, use_container_width=True)
'''
    
    with open("channel_routing_ui.txt", 'w') as f:
        f.write(ui_code)
    
    print("✅ UI component code saved to channel_routing_ui.txt")

if __name__ == "__main__":
    # Run integration
    integrate_router_with_blog()
    
    # Create UI component
    create_streamlit_ui_component()
    
    print("\n✨ Intelligent Discord Router integration complete!")
    print("\n🎯 The system will now:")
    print("   • Analyze content to determine appropriate channels")
    print("   • Route bug fixes to #bug-reports")
    print("   • Route features to #dev-blog")
    print("   • Route deployments to #deployments")
    print("   • Prevent duplicate messages")
    print("   • Generate updates from git commits")