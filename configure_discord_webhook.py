#!/usr/bin/env python3
"""
Configure Discord webhook for blog system
"""

import json
import os

def configure_discord_webhook():
    """Configure the Discord webhook for blog posts"""
    
    # The actual Discord webhook URL from CREDENTIALS.md
    webhook_url = "https://discord.com/api/webhooks/1400433499210780757/5WI6rtQhw6DinB4GJaXuwcRPXU6e2JEqq6VC58u9rFdw8bLDKr-8wsfpG7lGH8Ortc5K"
    
    print("🔧 Configuring Discord webhook for blog system...")
    
    # Update webhook_config.json
    config_path = "webhook_config.json"
    
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
    else:
        config = {"webhooks": {}}
    
    # Update the webhooks that need configuration
    channels_to_update = ['dev-blog', 'announcements', 'system-updates']
    
    for channel in channels_to_update:
        config['webhooks'][channel] = webhook_url
        print(f"✅ Updated webhook for #{channel}")
    
    # Save updated config
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\n✅ Webhook configuration updated in {config_path}")
    
    # Also create a direct config for the blog system
    blog_config = {
        "discord_webhook_url": webhook_url,
        "channel": "#trading-signals",
        "enabled": True,
        "rate_limit_safe": True
    }
    
    with open("blog_discord_webhook.json", 'w') as f:
        json.dump(blog_config, f, indent=2)
    
    print("✅ Created blog_discord_webhook.json for direct access")
    
    # Update the comprehensive blog system's webhook
    try:
        # Update the blog system database
        import sqlite3
        conn = sqlite3.connect('comprehensive_dev_blog.db')
        cursor = conn.cursor()
        
        # Create webhook config table if not exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS webhook_config (
                channel TEXT PRIMARY KEY,
                webhook_url TEXT NOT NULL,
                enabled INTEGER DEFAULT 1
            )
        ''')
        
        # Insert/update webhook URLs
        cursor.execute('''
            INSERT OR REPLACE INTO webhook_config (channel, webhook_url, enabled)
            VALUES (?, ?, ?)
        ''', ('discord', webhook_url, 1))
        
        conn.commit()
        conn.close()
        
        print("✅ Updated database with webhook configuration")
        
    except Exception as e:
        print(f"⚠️  Could not update database: {e}")
    
    print("\n🎯 Next Steps:")
    print("1. Restart the Streamlit app to load new configuration")
    print("2. Go to Blog tab and test sending a message")
    print("3. Check #trading-signals channel in Discord")
    
    return webhook_url

def test_webhook(webhook_url):
    """Test the webhook by sending a test message"""
    print("\n🧪 Testing Discord webhook...")
    
    try:
        import requests
        
        test_message = {
            "content": "🎉 TrenchCoat Pro Blog System Connected!",
            "embeds": [{
                "title": "Blog → Discord Integration Active",
                "description": "All blog posts will now be automatically sent to this channel.",
                "color": 0x10b981,  # Green color
                "fields": [
                    {"name": "Status", "value": "✅ Connected", "inline": True},
                    {"name": "Integration", "value": "✅ Active", "inline": True},
                    {"name": "Queue", "value": "✅ Enabled", "inline": True}
                ],
                "footer": {"text": "TrenchCoat Pro Blog System"},
                "timestamp": datetime.now(timezone.utc).isoformat()
            }]
        }
        
        response = requests.post(webhook_url, json=test_message)
        
        if response.status_code == 204:
            print("✅ Test message sent successfully!")
            print("🎯 Check #trading-signals channel in Discord")
            return True
        else:
            print(f"❌ Failed to send test message: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing webhook: {e}")
        return False

if __name__ == "__main__":
    from datetime import datetime, timezone
    
    # Configure webhook
    webhook_url = configure_discord_webhook()
    
    # Test it
    if input("\n🧪 Send test message to Discord? (y/n): ").lower() == 'y':
        test_webhook(webhook_url)