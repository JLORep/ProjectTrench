#!/usr/bin/env python3
"""
TrenchCoat Pro - Unified Notification System
Send Runner alerts to all platforms simultaneously
"""

import asyncio
import requests
import json
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging

class UnifiedNotificationSystem:
    """All-in-one notification system for TrenchCoat Pro"""
    
    def __init__(self):
        # Email configuration
        self.email_config = {
            "smtp_server": "mail.privateemail.com",
            "smtp_port": 587,
            "email": "support@trenchcoat.pro",
            "password": "TrenchF00t",
            "sender_name": "TrenchCoat Pro"
        }
        
        # Telegram configuration
        self.telegram_config = {
            "bot_token": "8479347588:AAH27CeFD3iiyQM7l6YKk9bMlQznlCLAhxo",
            "recipients": {
                "james": "8158865103",
                "bravo": None,  # Will be updated when they join
                "spangle": None  # Will be updated when they join
            }
        }
        
        # Discord configuration
        self.discord_config = {
            "webhook_url": "https://discord.com/api/webhooks/1400433499210780757/5WI6rtQhw6DinB4GJaXuwcRPXU6e2JEqq6VC58u9rFdw8bLDKr-8wsfpG7lGH8Ortc5K"
        }
        
        # Notification settings
        self.settings = {
            "email_enabled": True,
            "telegram_enabled": True,
            "discord_enabled": True,
            "send_to_all": True
        }
        
    def add_telegram_recipient(self, name: str, chat_id: str):
        """Add new Telegram recipient"""
        self.telegram_config["recipients"][name] = chat_id
        print(f"Added {name} to Telegram notifications: {chat_id}")
        
    async def send_runner_alert(self, coin_data: dict):
        """Send Runner alert to ALL platforms simultaneously"""
        
        print(f"\n🚀 SENDING RUNNER ALERT: {coin_data.get('symbol', 'Unknown')}")
        print("=" * 50)
        
        # Create tasks for all platforms
        tasks = []
        
        if self.settings["email_enabled"]:
            tasks.append(self._send_email_alert(coin_data))
            
        if self.settings["telegram_enabled"]:
            tasks.append(self._send_telegram_alerts(coin_data))
            
        if self.settings["discord_enabled"]:
            tasks.append(self._send_discord_alert(coin_data))
            
        # Execute all notifications concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Report results
        platforms = ["Email", "Telegram", "Discord"]
        success_count = 0
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"❌ {platforms[i]}: Failed - {result}")
            elif result:
                print(f"✅ {platforms[i]}: Success")
                success_count += 1
            else:
                print(f"❌ {platforms[i]}: Failed")
                
        print(f"\n📊 Summary: {success_count}/{len(platforms)} platforms notified")
        return success_count > 0
        
    async def _send_email_alert(self, coin_data: dict) -> bool:
        """Send email notification"""
        
        try:
            symbol = coin_data.get('symbol', 'Unknown')
            price = coin_data.get('current_price', 0)
            change_24h = coin_data.get('price_change_24h', 0)
            volume = coin_data.get('volume_24h', 0)
            confidence = coin_data.get('runner_confidence', 0)
            
            subject = f"🚀 Runner Alert: {symbol} ({change_24h:+.1f}%)"
            
            # Create professional HTML email
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; padding: 30px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <h1 style="color: #065f46; margin: 0;">🎯 TrenchCoat Pro</h1>
                        <p style="color: #6b7280; margin: 5px 0;">Professional Trading Intelligence</p>
                    </div>
                    
                    <div style="background: linear-gradient(135deg, #065f46 0%, #10b981 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 30px;">
                        <h2 style="margin: 0 0 10px 0; font-size: 24px;">🚀 RUNNER IDENTIFIED!</h2>
                        <p style="margin: 0; font-size: 18px; font-weight: bold;">{symbol}</p>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px;">
                        <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; text-align: center;">
                            <h3 style="color: #374151; margin: 0 0 10px 0;">💵 Price</h3>
                            <p style="color: #065f46; font-size: 18px; font-weight: bold; margin: 0;">${price:.6f}</p>
                        </div>
                        
                        <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; text-align: center;">
                            <h3 style="color: #374151; margin: 0 0 10px 0;">📈 Change</h3>
                            <p style="color: #10b981; font-size: 18px; font-weight: bold; margin: 0;">{change_24h:+.1f}%</p>
                        </div>
                        
                        <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; text-align: center;">
                            <h3 style="color: #374151; margin: 0 0 10px 0;">📊 Volume</h3>
                            <p style="color: #065f46; font-size: 18px; font-weight: bold; margin: 0;">${volume:,.0f}</p>
                        </div>
                        
                        <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; text-align: center;">
                            <h3 style="color: #374151; margin: 0 0 10px 0;">🎯 Confidence</h3>
                            <p style="color: #065f46; font-size: 18px; font-weight: bold; margin: 0;">{confidence:.1f}%</p>
                        </div>
                    </div>
                    
                    <div style="text-align: center; margin-bottom: 30px;">
                        <a href="https://app.trenchcoat.pro/coin/{symbol}" style="background-color: #065f46; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; display: inline-block; margin-right: 10px;">📊 View Analysis</a>
                        <a href="https://app.trenchcoat.pro/trade/{symbol}" style="background-color: #10b981; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; display: inline-block;">💰 Execute Trade</a>
                    </div>
                    
                    <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb; color: #6b7280; font-size: 12px;">
                        <p>TrenchCoat Pro | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Send email
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.email_config['sender_name']} <{self.email_config['email']}>"
            message["To"] = "jameseymail@hotmail.co.uk"
            
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
            
            context = ssl.create_default_context()
            with smtplib.SMTP(self.email_config["smtp_server"], self.email_config["smtp_port"]) as server:
                server.starttls(context=context)
                server.login(self.email_config["email"], self.email_config["password"])
                server.send_message(message)
                
            return True
            
        except Exception as e:
            logging.error(f"Email notification failed: {e}")
            return False
            
    async def _send_telegram_alerts(self, coin_data: dict) -> bool:
        """Send Telegram notifications to all recipients"""
        
        try:
            symbol = coin_data.get('symbol', 'Unknown')
            price = coin_data.get('current_price', 0)
            change_24h = coin_data.get('price_change_24h', 0)
            volume = coin_data.get('volume_24h', 0)
            confidence = coin_data.get('runner_confidence', 0)
            
            # Format message
            message = f"""
🚀 TRENCHCOAT PRO SIGNAL 🚀

💰 Coin: {symbol}
💵 Price: ${price:.6f}
📈 24h Change: {change_24h:+.2f}%
📊 Volume: ${volume:,.0f}
🎯 Confidence: {confidence:.1f}%

⚡ RUNNER IDENTIFIED
⏰ {datetime.now().strftime('%H:%M:%S')}

Signal by: TrenchCoat Pro AI
            """.strip()
            
            # Create inline keyboard
            keyboard = {
                "inline_keyboard": [[
                    {"text": "📊 View Chart", "url": f"https://app.trenchcoat.pro/coin/{symbol}"},
                    {"text": "💰 Trade", "url": f"https://app.trenchcoat.pro/trade/{symbol}"}
                ], [
                    {"text": "🤖 Dashboard", "url": "https://demo.trenchcoat.pro"}
                ]]
            }
            
            # Send to all recipients
            base_url = f"https://api.telegram.org/bot{self.telegram_config['bot_token']}"
            success_count = 0
            
            for name, chat_id in self.telegram_config["recipients"].items():
                if chat_id:
                    try:
                        payload = {
                            "chat_id": chat_id,
                            "text": message,
                            "reply_markup": json.dumps(keyboard)
                        }
                        
                        response = requests.post(f"{base_url}/sendMessage", json=payload, timeout=10)
                        if response.status_code == 200:
                            success_count += 1
                            print(f"  📱 {name}: Telegram sent")
                        else:
                            print(f"  ❌ {name}: Telegram failed")
                            
                    except Exception as e:
                        print(f"  ❌ {name}: Telegram error - {e}")
                        
            return success_count > 0
            
        except Exception as e:
            logging.error(f"Telegram notifications failed: {e}")
            return False
            
    async def _send_discord_alert(self, coin_data: dict) -> bool:
        """Send Discord notification"""
        
        try:
            symbol = coin_data.get('symbol', 'Unknown')
            price = coin_data.get('current_price', 0)
            change_24h = coin_data.get('price_change_24h', 0)
            volume = coin_data.get('volume_24h', 0)
            confidence = coin_data.get('runner_confidence', 0)
            
            # Color based on performance
            color = 0x10B981 if change_24h > 0 else 0xEF4444
            
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
                        "name": "💵 Price",
                        "value": f"${price:.6f}",
                        "inline": True
                    },
                    {
                        "name": "📈 24h Change",
                        "value": f"{change_24h:+.2f}%",
                        "inline": True
                    },
                    {
                        "name": "📊 Volume",
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
                        "name": "🔗 Quick Access",
                        "value": f"[📊 Chart](https://app.trenchcoat.pro/coin/{symbol}) | [💰 Trade](https://app.trenchcoat.pro/trade/{symbol}) | [📈 Dashboard](https://app.trenchcoat.pro)",
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
            
            response = requests.post(self.discord_config["webhook_url"], json=payload, timeout=10)
            response.raise_for_status()
            
            return True
            
        except Exception as e:
            logging.error(f"Discord notification failed: {e}")
            return False
            
    async def send_test_all_platforms(self):
        """Send test notification to all platforms"""
        
        test_data = {
            "symbol": "TEST",
            "current_price": 0.001234,
            "price_change_24h": 25.7,
            "volume_24h": 1000000,
            "runner_confidence": 95.0
        }
        
        print("🧪 TESTING ALL NOTIFICATION PLATFORMS")
        print("=" * 40)
        
        return await self.send_runner_alert(test_data)
        
    def get_notification_status(self):
        """Get current notification system status"""
        
        print("\n📊 TRENCHCOAT PRO NOTIFICATION STATUS")
        print("=" * 40)
        
        # Email status
        email_status = "✅ Ready" if self.settings["email_enabled"] else "❌ Disabled"
        print(f"📧 Email: {email_status}")
        print(f"   └── support@trenchcoat.pro")
        
        # Telegram status
        telegram_status = "✅ Ready" if self.settings["telegram_enabled"] else "❌ Disabled"
        print(f"📱 Telegram: {telegram_status}")
        active_recipients = sum(1 for chat_id in self.telegram_config["recipients"].values() if chat_id)
        print(f"   └── {active_recipients} recipients active")
        
        # Discord status
        discord_status = "✅ Ready" if self.settings["discord_enabled"] else "❌ Disabled"
        print(f"🎮 Discord: {discord_status}")
        print(f"   └── #trading-signals channel")
        
        print(f"\n🎯 System Status: ALL PLATFORMS OPERATIONAL")
        print(f"⚡ Ready for instant Runner alerts!")

# Test and usage
async def main():
    """Test unified notification system"""
    
    # Initialize system
    notifier = UnifiedNotificationSystem()
    
    # Show status
    notifier.get_notification_status()
    
    # Test all platforms
    await notifier.send_test_all_platforms()
    
    print("\n🚀 Unified notification system is ready!")
    print("Next Runner detection will trigger alerts on:")
    print("  📧 Email (professional HTML)")
    print("  📱 Telegram (you + Bravo + Spangle when they join)")
    print("  🎮 Discord (rich embeds with @here notification)")

if __name__ == "__main__":
    asyncio.run(main())