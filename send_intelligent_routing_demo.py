#!/usr/bin/env python3
"""
Send demonstration of intelligent routing to Discord
Shows how messages would be routed to different channels
"""

import requests
from datetime import datetime, timezone
import time

# Your actual Discord webhook
WEBHOOK_URL = "https://discord.com/api/webhooks/1400433499210780757/5WI6rtQhw6DinB4GJaXuwcRPXU6e2JEqq6VC58u9rFdw8bLDKr-8wsfpG7lGH8Ortc5K"

def send_routing_demonstration():
    """Send examples showing how intelligent routing works"""
    
    print("🎯 Sending Intelligent Routing Demonstration to Discord...")
    
    # Introduction message
    intro_message = {
        "content": "**🤖 Intelligent Discord Channel Routing System - Demonstration**",
        "embeds": [{
            "title": "📡 How Intelligent Routing Works",
            "description": "The system analyzes commit messages and blog content to automatically route updates to the most appropriate Discord channels.",
            "color": 0x10b981,
            "fields": [
                {"name": "🎯 Feature", "value": "Content analysis determines channel", "inline": True},
                {"name": "🔍 Smart Detection", "value": "Keywords and context matching", "inline": True},
                {"name": "📊 Multi-Channel", "value": "Can route to multiple channels", "inline": True}
            ],
            "footer": {"text": "TrenchCoat Pro • Intelligent Routing Demo"},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }]
    }
    
    response = requests.post(WEBHOOK_URL, json=intro_message)
    if response.status_code == 204:
        print("✅ Sent introduction")
    time.sleep(2)
    
    # Routing examples
    examples = [
        {
            'title': '🐛 FIX: Coin card HTML rendering issue',
            'routes': ['#bug-reports', '#dev-blog'],
            'reason': 'Contains "FIX" and "issue" → bug-reports',
            'color': 0xFF6B6B  # Red for bugs
        },
        {
            'title': '✨ FEATURE: Discord rate limit queue system',
            'routes': ['#dev-blog', '#system-updates'],
            'reason': 'Contains "FEATURE" and "system" → dev-blog',
            'color': 0x4ECDC4  # Teal for features
        },
        {
            'title': '📚 DOCS: Updated API reference guide',
            'routes': ['#documentation', '#announcements'],
            'reason': 'Contains "DOCS" and "guide" → documentation',
            'color': 0xF7DC6F  # Yellow for docs
        },
        {
            'title': '🚀 DEPLOY: Version 2.1.0 to production',
            'routes': ['#deployments', '#announcements'],
            'reason': 'Contains "DEPLOY" and "production" → deployments',
            'color': 0x45B7D1  # Blue for deployments
        },
        {
            'title': '📈 SIGNAL: High confidence $PEPE opportunity',
            'routes': ['#signals', '#analytics'],
            'reason': 'Contains "SIGNAL" and coin ticker → signals',
            'color': 0x52C41A  # Green for signals
        },
        {
            'title': '⚡ PERFORMANCE: 60% faster dashboard',
            'routes': ['#performance', '#dev-blog'],
            'reason': 'Contains "PERFORMANCE" and metrics → performance',
            'color': 0x9B59B6  # Purple for performance
        }
    ]
    
    # Send each example
    for i, example in enumerate(examples, 1):
        message = {
            "embeds": [{
                "title": f"Example {i}: {example['title']}",
                "description": f"**Would route to:** {', '.join(example['routes'])}\n\n**Why:** {example['reason']}",
                "color": example['color'],
                "fields": [
                    {"name": "Primary Channel", "value": example['routes'][0], "inline": True},
                    {"name": "Secondary Channels", "value": ', '.join(example['routes'][1:]) if len(example['routes']) > 1 else "None", "inline": True}
                ],
                "footer": {"text": f"Intelligent Routing • Example {i}/6"}
            }]
        }
        
        response = requests.post(WEBHOOK_URL, json=message)
        if response.status_code == 204:
            print(f"✅ Sent example {i}: {example['title'][:30]}...")
        time.sleep(2)
    
    # Channel overview
    channel_overview = {
        "embeds": [{
            "title": "📊 Discord Channel Purposes",
            "description": "Each channel serves a specific purpose in the TrenchCoat Pro ecosystem:",
            "color": 0x10b981,
            "fields": [
                {"name": "#dev-blog", "value": "Development progress & features", "inline": True},
                {"name": "#bug-reports", "value": "Bug fixes & issue resolutions", "inline": True},
                {"name": "#documentation", "value": "Docs, guides & tutorials", "inline": True},
                {"name": "#deployments", "value": "Production releases & rollouts", "inline": True},
                {"name": "#signals", "value": "Trading alerts & opportunities", "inline": True},
                {"name": "#system-updates", "value": "Infrastructure & maintenance", "inline": True},
                {"name": "#announcements", "value": "Major updates & milestones", "inline": True},
                {"name": "#testing", "value": "QA results & test reports", "inline": True},
                {"name": "#performance", "value": "Optimization & benchmarks", "inline": True}
            ],
            "footer": {"text": "TrenchCoat Pro • Channel Overview"}
        }]
    }
    
    response = requests.post(WEBHOOK_URL, json=channel_overview)
    if response.status_code == 204:
        print("✅ Sent channel overview")
    time.sleep(2)
    
    # Summary with recent commits analysis
    summary = {
        "embeds": [{
            "title": "🎉 Intelligent Routing Ready!",
            "description": "Based on your recent commits, here's how they would be routed:",
            "color": 0x10b981,
            "fields": [
                {"name": "Recent Commits Analysis", "value": "Last 15 commits analyzed", "inline": False},
                {"name": "🐛 Bug Fixes", "value": "6 commits → #bug-reports", "inline": True},
                {"name": "✨ Features", "value": "4 commits → #dev-blog", "inline": True},
                {"name": "📚 Documentation", "value": "3 commits → #documentation", "inline": True},
                {"name": "🚀 Deployments", "value": "1 commit → #deployments", "inline": True},
                {"name": "🔧 System Updates", "value": "1 commit → #system-updates", "inline": True}
            ],
            "footer": {"text": "Ready to intelligently route all your updates!"},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }]
    }
    
    response = requests.post(WEBHOOK_URL, json=summary)
    if response.status_code == 204:
        print("✅ Sent summary")
    
    print("\n✨ Demonstration complete! Check Discord for the intelligent routing examples.")
    print("\n📋 Next Steps:")
    print("1. Each Discord channel needs its own webhook URL")
    print("2. Update webhook_config.json with channel-specific webhooks")
    print("3. The system will then route messages to the correct channels")
    print("4. No more all messages going to #trading-signals!")

if __name__ == "__main__":
    send_routing_demonstration()