#!/usr/bin/env python3
"""
TrenchCoat Pro - Discord Integration
Professional signals via Discord webhooks
"""

import requests
import json
from datetime import datetime
import logging

class DiscordBot:
    """TrenchCoat Pro Discord webhook integration"""
    
    def __init__(self, webhook_url: str = None):
        self.webhook_url = webhook_url
        
    def setup_webhook(self, webhook_url: str):
        """Configure Discord webhook"""
        self.webhook_url = webhook_url
        print(f"Discord webhook configured: {webhook_url[:50]}...")
        
    def send_test_message(self) -> bool:
        """Send test message to verify webhook"""
        
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
                "text": "TrenchCoat Pro | Professional Trading Intelligence",
                "icon_url": "https://app.trenchcoat.pro/favicon.ico"
            },
            "thumbnail": {
                "url": "https://app.trenchcoat.pro/logo.png"
            }
        }
        
        payload = {
            "username": "TrenchCoat Pro",
            "avatar_url": "https://app.trenchcoat.pro/avatar.png",
            "embeds": [embed]
        }
        
        return self._send_webhook(payload)
        
    def send_runner_alert(self, coin_data: dict) -> bool:
        """Send professional Runner alert to Discord"""
        
        symbol = coin_data.get('symbol', 'Unknown')
        price = coin_data.get('current_price', 0)
        change_24h = coin_data.get('price_change_24h', 0)
        volume = coin_data.get('volume_24h', 0)
        confidence = coin_data.get('runner_confidence', 0)
        
        # Color based on performance
        color = 0x10B981 if change_24h > 0 else 0xEF4444  # Green or Red
        
        # Create rich embed
        embed = {
            "title": "🚀 RUNNER IDENTIFIED!",
            "description": f"High-confidence Runner detected: **{symbol}**",
            "color": color,
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
                    "value": f"{change_24h:+.2f}%",
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
                "text": "TrenchCoat Pro | AI-Powered Trading Signals",
                "icon_url": "https://app.trenchcoat.pro/favicon.ico"
            },
            "thumbnail": {
                "url": f"https://assets.coingecko.com/coins/images/1/large/{symbol.lower()}.png"
            }
        }
        
        payload = {
            "content": f"@here 🚀 **RUNNER ALERT** - {symbol} detected!",
            "username": "TrenchCoat Pro Signals",
            "avatar_url": "https://app.trenchcoat.pro/avatar.png",
            "embeds": [embed]
        }
        
        return self._send_webhook(payload)
        
    def send_performance_update(self, performance_data: dict) -> bool:
        """Send performance summary to Discord"""
        
        total_profit = performance_data.get('total_profit', 0)
        win_rate = performance_data.get('win_rate', 0)
        total_trades = performance_data.get('total_trades', 0)
        best_performer = performance_data.get('best_performer', 'N/A')
        
        # Color based on profit
        color = 0x10B981 if total_profit > 0 else 0xEF4444
        
        embed = {
            "title": "📊 TrenchCoat Pro Performance Report",
            "description": f"Daily trading summary for {datetime.now().strftime('%Y-%m-%d')}",
            "color": color,
            "timestamp": datetime.now().isoformat(),
            "fields": [
                {
                    "name": "💰 Total P&L",
                    "value": f"${total_profit:,.2f}",
                    "inline": True
                },
                {
                    "name": "🎯 Win Rate",
                    "value": f"{win_rate:.1f}%",
                    "inline": True
                },
                {
                    "name": "📈 Total Trades",
                    "value": f"{total_trades}",
                    "inline": True
                },
                {
                    "name": "🏆 Best Performer",
                    "value": f"{best_performer}",
                    "inline": False
                },
                {
                    "name": "📈 Dashboard",
                    "value": "[View Full Report](https://app.trenchcoat.pro/reports)",
                    "inline": False
                }
            ],
            "footer": {
                "text": "TrenchCoat Pro | Automated Performance Tracking"
            }
        }
        
        payload = {
            "username": "TrenchCoat Pro Reports",
            "avatar_url": "https://app.trenchcoat.pro/avatar.png",
            "embeds": [embed]
        }
        
        return self._send_webhook(payload)
        
    def send_system_alert(self, alert_type: str, message: str) -> bool:
        """Send system alerts to Discord"""
        
        embed = {
            "title": f"⚠️ System Alert: {alert_type}",
            "description": message,
            "color": 0xF59E0B,  # Amber
            "timestamp": datetime.now().isoformat(),
            "fields": [
                {
                    "name": "🔧 Action Required",
                    "value": "Review system status and take appropriate action",
                    "inline": False
                },
                {
                    "name": "📞 Support",
                    "value": "[Contact Support](mailto:support@trenchcoat.pro) | [Dashboard](https://app.trenchcoat.pro)",
                    "inline": False
                }
            ],
            "footer": {
                "text": "TrenchCoat Pro | System Monitoring"
            }
        }
        
        payload = {
            "content": f"@here ⚠️ **SYSTEM ALERT** - {alert_type}",
            "username": "TrenchCoat Pro Alerts",
            "avatar_url": "https://app.trenchcoat.pro/avatar.png",
            "embeds": [embed]
        }
        
        return self._send_webhook(payload)
        
    def send_custom_message(self, title: str, message: str, color: int = 0x10B981) -> bool:
        """Send custom message to Discord"""
        
        embed = {
            "title": title,
            "description": message,
            "color": color,
            "timestamp": datetime.now().isoformat(),
            "footer": {
                "text": "TrenchCoat Pro"
            }
        }
        
        payload = {
            "username": "TrenchCoat Pro",
            "avatar_url": "https://app.trenchcoat.pro/avatar.png",
            "embeds": [embed]
        }
        
        return self._send_webhook(payload)
        
    def _send_webhook(self, payload: dict) -> bool:
        """Send webhook request to Discord"""
        
        if not self.webhook_url:
            logging.error("Discord webhook URL not configured")
            return False
            
        try:
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            
            logging.info("Discord message sent successfully")
            return True
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to send Discord message: {e}")
            return False

def setup_discord_integration():
    """Interactive Discord webhook setup"""
    
    print("TrenchCoat Pro Discord Integration Setup")
    print("=" * 40)
    print()
    print("First, create your Discord webhook:")
    print("1. Right-click your Discord channel")
    print("2. Select 'Edit Channel'")
    print("3. Go to 'Integrations' tab")
    print("4. Click 'Create Webhook'")
    print("5. Copy the webhook URL")
    print()
    
    webhook_url = input("Enter your Discord webhook URL: ").strip()
    
    if not webhook_url:
        print("Webhook URL is required!")
        return None
        
    # Test webhook
    discord_bot = DiscordBot(webhook_url)
    
    print("\nTesting Discord webhook...")
    if discord_bot.send_test_message():
        print("SUCCESS: Discord integration working!")
        print("Check your Discord channel for the test message.")
        
        # Save webhook URL
        with open("discord_config.json", "w") as f:
            json.dump({"webhook_url": webhook_url}, f)
            
        return discord_bot
    else:
        print("FAILED: Could not send test message.")
        print("Check your webhook URL and try again.")
        return None

# Usage example
if __name__ == "__main__":
    # Interactive setup
    discord_bot = setup_discord_integration()
    
    if discord_bot:
        # Test Runner alert
        runner_data = {
            "symbol": "PEPE",
            "current_price": 0.00001234,
            "price_change_24h": 45.7,
            "volume_24h": 2500000,
            "runner_confidence": 92.1
        }
        
        print("\nSending example Runner alert...")
        discord_bot.send_runner_alert(runner_data)
        
        print("\nDiscord integration ready!")
        print("Your Discord channel will now receive professional trading signals!")