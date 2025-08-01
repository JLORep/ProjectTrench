#!/usr/bin/env python3
"""
TrenchCoat Pro - Telegram Bot Integration
Instant Runner alerts via Telegram
"""

import requests
import json
import asyncio
from datetime import datetime
import logging

class TelegramBot:
    """TrenchCoat Pro Telegram notification bot"""
    
    def __init__(self, bot_token: str = None, chat_id: str = None):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        
    def setup_credentials(self, bot_token: str, chat_id: str):
        """Configure bot credentials"""
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        
    def send_test_message(self) -> bool:
        """Send test message to verify connection"""
        
        message = """
🎯 TrenchCoat Pro Bot Online!

✅ Connection successful
✅ Ready for Runner alerts
✅ Professional notifications active

Your instant trading alerts are now configured!
        """.strip()
        
        return self.send_message(message)
        
    def send_runner_alert(self, coin_data: dict) -> bool:
        """Send instant Runner alert with action buttons"""
        
        symbol = coin_data.get('symbol', 'Unknown')
        price = coin_data.get('current_price', 0)
        change_24h = coin_data.get('price_change_24h', 0)
        volume = coin_data.get('volume_24h', 0)
        confidence = coin_data.get('runner_confidence', 0)
        
        # Format message
        message = f"""
🚀 RUNNER IDENTIFIED! 🚀

💰 Coin: {symbol}
💵 Price: ${price:.6f}
📈 24h Change: {change_24h:+.2f}%
📊 Volume: ${volume:,.0f}
🎯 Confidence: {confidence:.1f}%

⚡ Action Required: Review for entry
⏰ Time: {datetime.now().strftime('%H:%M:%S')}

🔗 Dashboard: https://app.trenchcoat.pro
        """.strip()
        
        # Create inline keyboard for quick actions
        keyboard = {
            "inline_keyboard": [[
                {"text": "📊 View Chart", "url": f"https://app.trenchcoat.pro/coin/{symbol}"},
                {"text": "💰 Trade Now", "url": f"https://app.trenchcoat.pro/trade/{symbol}"}
            ], [
                {"text": "📈 Full Analysis", "url": "https://app.trenchcoat.pro/dashboard"}
            ]]
        }
        
        return self.send_message(message, keyboard)
        
    def send_performance_update(self, performance_data: dict) -> bool:
        """Send daily performance summary"""
        
        total_profit = performance_data.get('total_profit', 0)
        win_rate = performance_data.get('win_rate', 0)
        total_trades = performance_data.get('total_trades', 0)
        best_performer = performance_data.get('best_performer', 'N/A')
        
        message = f"""
📊 TrenchCoat Pro Daily Report

💰 Total P&L: ${total_profit:,.2f}
🎯 Win Rate: {win_rate:.1f}%
📈 Trades: {total_trades}
🏆 Best: {best_performer}

Date: {datetime.now().strftime('%Y-%m-%d')}
        """.strip()
        
        keyboard = {
            "inline_keyboard": [[
                {"text": "📊 Full Report", "url": "https://app.trenchcoat.pro/reports"},
                {"text": "⚙️ Settings", "url": "https://app.trenchcoat.pro/settings"}
            ]]
        }
        
        return self.send_message(message, keyboard)
        
    def send_system_alert(self, alert_type: str, message: str) -> bool:
        """Send system alerts and warnings"""
        
        alert_message = f"""
⚠️ TrenchCoat Pro Alert

🔥 {alert_type}

{message}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """.strip()
        
        keyboard = {
            "inline_keyboard": [[
                {"text": "🔧 Dashboard", "url": "https://app.trenchcoat.pro"},
                {"text": "📞 Support", "url": "mailto:support@trenchcoat.pro"}
            ]]
        }
        
        return self.send_message(alert_message, keyboard)
        
    def send_message(self, text: str, keyboard: dict = None) -> bool:
        """Send message to Telegram"""
        
        if not self.bot_token or not self.chat_id:
            logging.error("Bot token or chat ID not configured")
            return False
            
        url = f"{self.base_url}/sendMessage"
        
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        
        if keyboard:
            payload["reply_markup"] = json.dumps(keyboard)
            
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            if result.get("ok"):
                logging.info("Telegram message sent successfully")
                return True
            else:
                logging.error(f"Telegram API error: {result}")
                return False
                
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to send Telegram message: {e}")
            return False
            
    def get_bot_info(self) -> dict:
        """Get bot information"""
        
        if not self.bot_token:
            return {}
            
        url = f"{self.base_url}/getMe"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to get bot info: {e}")
            return {}
            
    def get_chat_updates(self) -> list:
        """Get recent chat updates (for finding chat ID)"""
        
        if not self.bot_token:
            return []
            
        url = f"{self.base_url}/getUpdates"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            return result.get("result", [])
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to get updates: {e}")
            return []

# Configuration helper
def setup_telegram_bot():
    """Interactive setup for Telegram bot"""
    
    print("TrenchCoat Pro Telegram Bot Setup")
    print("=" * 35)
    
    bot_token = input("Enter your bot token (from @BotFather): ").strip()
    chat_id = input("Enter your chat ID: ").strip()
    
    if not bot_token or not chat_id:
        print("❌ Bot token and chat ID are required!")
        return None
        
    # Test connection
    bot = TelegramBot(bot_token, chat_id)
    
    print("\nTesting connection...")
    if bot.send_test_message():
        print("✅ Telegram bot configured successfully!")
        print("Check your Telegram for the test message.")
        
        # Save credentials
        with open("telegram_config.json", "w") as f:
            json.dump({
                "bot_token": bot_token,
                "chat_id": chat_id
            }, f)
            
        return bot
    else:
        print("❌ Failed to send test message. Check your credentials.")
        return None

# Usage example
if __name__ == "__main__":
    # Interactive setup
    bot = setup_telegram_bot()
    
    if bot:
        # Example runner alert
        runner_data = {
            "symbol": "MEME",
            "current_price": 0.000234,
            "price_change_24h": 67.5,
            "volume_24h": 1250000,
            "runner_confidence": 87.3
        }
        
        print("\nSending example Runner alert...")
        bot.send_runner_alert(runner_data)