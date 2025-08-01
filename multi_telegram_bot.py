#!/usr/bin/env python3
"""
TrenchCoat Pro - Multi-User Telegram Bot
Share Runner signals with multiple contacts
"""

import requests
import json
import asyncio
from datetime import datetime
import logging

class MultiTelegramBot:
    """TrenchCoat Pro multi-user Telegram bot"""
    
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        
        # Define your signal recipients
        self.recipients = {
            "james": "8158865103",  # Your Chat ID
            "bravo": None,  # Will get Chat ID when they message bot
            "spangle": None  # Will get Chat ID when they message bot
        }
        
    def add_recipient(self, name: str, chat_id: str):
        """Add new recipient for signals"""
        self.recipients[name] = chat_id
        print(f"Added {name} to signal recipients: {chat_id}")
        
    def send_runner_alert_to_all(self, coin_data: dict) -> dict:
        """Send Runner alert to all recipients"""
        
        symbol = coin_data.get('symbol', 'Unknown')
        price = coin_data.get('current_price', 0)
        change_24h = coin_data.get('price_change_24h', 0)
        volume = coin_data.get('volume_24h', 0)
        confidence = coin_data.get('runner_confidence', 0)
        
        # Format signal message
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
        
        # Create action buttons
        keyboard = {
            "inline_keyboard": [[
                {"text": "📊 View Chart", "url": f"https://app.trenchcoat.pro/coin/{symbol}"},
                {"text": "💰 Trade", "url": f"https://app.trenchcoat.pro/trade/{symbol}"}
            ], [
                {"text": "🤖 TrenchCoat Pro", "url": "https://demo.trenchcoat.pro"}
            ]]
        }
        
        # Send to all recipients
        results = {}
        for name, chat_id in self.recipients.items():
            if chat_id:
                success = self.send_message(chat_id, message, keyboard)
                results[name] = success
                print(f"Signal sent to {name}: {'✅' if success else '❌'}")
            else:
                results[name] = False
                print(f"No Chat ID for {name} - skipped")
                
        return results
        
    def send_group_message(self, custom_message: str) -> dict:
        """Send custom message to all recipients"""
        
        results = {}
        for name, chat_id in self.recipients.items():
            if chat_id:
                success = self.send_message(chat_id, custom_message)
                results[name] = success
                print(f"Message sent to {name}: {'✅' if success else '❌'}")
            else:
                results[name] = False
                print(f"No Chat ID for {name} - skipped")
                
        return results
        
    def send_message(self, chat_id: str, text: str, keyboard: dict = None) -> bool:
        """Send message to specific chat ID"""
        
        url = f"{self.base_url}/sendMessage"
        
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        
        if keyboard:
            payload["reply_markup"] = json.dumps(keyboard)
            
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            return result.get("ok", False)
            
        except Exception as e:
            logging.error(f"Failed to send message to {chat_id}: {e}")
            return False
            
    def get_chat_updates(self) -> list:
        """Get recent updates to find new Chat IDs"""
        
        url = f"{self.base_url}/getUpdates"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            updates = result.get("result", [])
            
            # Extract unique chat IDs and usernames
            contacts = {}
            for update in updates:
                if "message" in update:
                    msg = update["message"]
                    chat_id = str(msg["from"]["id"])
                    first_name = msg["from"].get("first_name", "Unknown")
                    last_name = msg["from"].get("last_name", "")
                    username = msg["from"].get("username", "")
                    
                    full_name = f"{first_name} {last_name}".strip()
                    if username:
                        full_name += f" (@{username})"
                        
                    contacts[chat_id] = full_name
                    
            return contacts
            
        except Exception as e:
            logging.error(f"Failed to get updates: {e}")
            return {}
            
    def show_contacts(self):
        """Show all contacts who have messaged the bot"""
        
        print("\n📱 CONTACTS WHO HAVE MESSAGED YOUR BOT:")
        print("=" * 45)
        
        contacts = self.get_chat_updates()
        
        if not contacts:
            print("No contacts found. Ask Bravo and Spangle to:")
            print("1. Go to: https://t.me/trenchcoat_pro_bot")
            print("2. Click START")
            print("3. Send any message (like 'hello')")
            return
            
        for chat_id, name in contacts.items():
            print(f"Chat ID: {chat_id}")
            print(f"Name: {name}")
            print("-" * 30)
            
        print("\nTo add someone as a signal recipient:")
        print("bot.add_recipient('bravo', 'THEIR_CHAT_ID')")
        print("bot.add_recipient('spangle', 'THEIR_CHAT_ID')")

def setup_multi_bot():
    """Setup multi-user bot for signal sharing"""
    
    bot_token = "8479347588:AAH27CeFD3iiyQM7l6YKk9bMlQznlCLAhxo"
    bot = MultiTelegramBot(bot_token)
    
    print("TrenchCoat Pro Multi-User Signal Bot")
    print("=" * 40)
    
    # Show current recipients
    print("\nCURRENT SIGNAL RECIPIENTS:")
    for name, chat_id in bot.recipients.items():
        status = "✅ Ready" if chat_id else "⏳ Waiting for Chat ID"
        print(f"- {name.title()}: {status}")
        
    # Show all contacts
    bot.show_contacts()
    
    return bot

# Test signal sharing
def test_signal_sharing():
    """Test sending signals to multiple users"""
    
    bot = setup_multi_bot()
    
    # Example Runner data
    runner_data = {
        "symbol": "PEPE",
        "current_price": 0.00001234,
        "price_change_24h": 45.7,
        "volume_24h": 2500000,
        "runner_confidence": 92.1
    }
    
    print("\n🚀 TESTING SIGNAL SHARING...")
    print("=" * 30)
    
    # Send test signal
    results = bot.send_runner_alert_to_all(runner_data)
    
    print(f"\nSignal sent to {sum(results.values())} recipients")
    
    return bot

if __name__ == "__main__":
    bot = test_signal_sharing()
    
    print("\n📋 NEXT STEPS:")
    print("1. Ask Bravo and Spangle to message @trenchcoat_pro_bot")
    print("2. Get their Chat IDs from bot.show_contacts()")
    print("3. Add them: bot.add_recipient('bravo', 'CHAT_ID')")
    print("4. Test signal sharing!")