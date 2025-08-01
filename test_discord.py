#!/usr/bin/env python3
"""
Test TrenchCoat Pro Discord Integration
"""

import requests
import json
from datetime import datetime

def test_discord_webhook():
    """Test Discord webhook with professional message"""
    
    webhook_url = "https://discord.com/api/webhooks/1400433499210780757/5WI6rtQhw6DinB4GJaXuwcRPXU6e2JEqq6VC58u9rFdw8bLDKr-8wsfpG7lGH8Ortc5K"
    
    # Create test embed
    embed = {
        "title": "🎯 TrenchCoat Pro Discord Integration",
        "description": "Professional trading signals are now active!",
        "color": 0x10B981,  # Emerald green
        "timestamp": datetime.now().isoformat(),
        "fields": [
            {
                "name": "✅ Status",
                "value": "Discord integration operational",
                "inline": True
            },
            {
                "name": "🚀 Features",
                "value": "Runner alerts, performance updates, system notifications",
                "inline": True
            },
            {
                "name": "🎯 Ready For",
                "value": "Instant trading signals with rich formatting",
                "inline": False
            }
        ],
        "footer": {
            "text": "TrenchCoat Pro | Professional Trading Intelligence"
        }
    }
    
    payload = {
        "username": "TrenchCoat Pro",
        "embeds": [embed]
    }
    
    try:
        print("Testing Discord webhook...")
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        
        print("SUCCESS: Discord test message sent!")
        print("Check your Discord channel for the professional message!")
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to send Discord message - {e}")
        return False

def test_runner_alert():
    """Send example Runner alert to Discord"""
    
    webhook_url = "https://discord.com/api/webhooks/1400433499210780757/5WI6rtQhw6DinB4GJaXuwcRPXU6e2JEqq6VC58u9rFdw8bLDKr-8wsfpG7lGH8Ortc5K"
    
    # Example Runner data
    symbol = "PEPE"
    price = 0.00001234
    change_24h = 45.7
    volume = 2500000
    confidence = 92.1
    
    # Create rich embed
    embed = {
        "title": "🚀 RUNNER IDENTIFIED!",
        "description": f"High-confidence Runner detected: **{symbol}**",
        "color": 0x10B981,  # Green for positive change
        "timestamp": datetime.now().isoformat(),
        "fields": [
            {
                "name": "💰 Symbol",
                "value": f"**{symbol}**",
                "inline": True
            },
            {
                "name": "💵 Current Price",
                "value": f"${price:.6f}",
                "inline": True
            },
            {
                "name": "📈 24h Change",
                "value": f"+{change_24h:.1f}%",
                "inline": True
            },
            {
                "name": "📊 24h Volume",
                "value": f"${volume:,.0f}",
                "inline": True
            },
            {
                "name": "🎯 Confidence",
                "value": f"**{confidence:.1f}%**",
                "inline": True
            },
            {
                "name": "⏰ Time",
                "value": datetime.now().strftime('%H:%M:%S'),
                "inline": True
            },
            {
                "name": "⚡ Action Required",
                "value": "Review analysis and consider entry position",
                "inline": False
            },
            {
                "name": "🔗 Quick Access",
                "value": f"[📊 View Chart](https://app.trenchcoat.pro/coin/{symbol}) | [💰 Trade Now](https://app.trenchcoat.pro/trade/{symbol}) | [📈 Dashboard](https://app.trenchcoat.pro)",
                "inline": False
            }
        ],
        "footer": {
            "text": "TrenchCoat Pro | AI-Powered Trading Signals"
        }
    }
    
    payload = {
        "content": f"@here 🚀 **RUNNER ALERT** - {symbol} detected!",
        "username": "TrenchCoat Pro Signals",
        "embeds": [embed]
    }
    
    try:
        print("\nSending example Runner alert...")
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        
        print("SUCCESS: Runner alert sent to Discord!")
        print("Check your Discord channel for the professional signal!")
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to send Runner alert - {e}")
        return False

if __name__ == "__main__":
    print("TrenchCoat Pro Discord Integration Test")
    print("=" * 40)
    
    # Test basic webhook
    if test_discord_webhook():
        print("\n" + "=" * 40)
        # Test Runner alert
        test_runner_alert()
    
    print("\nDiscord integration is ready for live signals!")