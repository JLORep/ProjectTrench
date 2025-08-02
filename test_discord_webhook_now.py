#!/usr/bin/env python3
"""
Test Discord webhook immediately
"""

import requests
from datetime import datetime, timezone

webhook_url = "https://discord.com/api/webhooks/1400433499210780757/5WI6rtQhw6DinB4GJaXuwcRPXU6e2JEqq6VC58u9rFdw8bLDKr-8wsfpG7lGH8Ortc5K"

# Send test message
test_message = {
    "content": "🎉 **TrenchCoat Pro Blog System is NOW CONNECTED!**",
    "embeds": [{
        "title": "📰 Blog → Discord Integration Active",
        "description": "All blog posts will now be automatically sent to this channel.",
        "color": 0x10b981,  # Green
        "fields": [
            {"name": "✅ Status", "value": "Connected", "inline": True},
            {"name": "📊 Blog Posts (24h)", "value": "52", "inline": True},
            {"name": "🚀 Integration", "value": "Active", "inline": True},
            {"name": "📡 Queue System", "value": "Enabled", "inline": True},
            {"name": "♻️ Auto-Retry", "value": "3 attempts", "inline": True},
            {"name": "⏱️ Rate Limit", "value": "Protected", "inline": True}
        ],
        "footer": {
            "text": "TrenchCoat Pro • Blog System v2.0",
            "icon_url": "https://cdn.discordapp.com/embed/avatars/0.png"
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }]
}

print("📡 Sending test message to Discord...")
response = requests.post(webhook_url, json=test_message)

if response.status_code == 204:
    print("✅ SUCCESS! Message sent to Discord #trading-signals channel")
    print("\n📋 What happens next:")
    print("  • All new blog posts auto-sent to Discord")
    print("  • Git commits with keywords create blog posts")
    print("  • Queue system prevents rate limit errors")
    print("  • Check Blog tab (Tab 8) to see all posts")
else:
    print(f"❌ Failed: {response.status_code}")
    print(f"Response: {response.text}")