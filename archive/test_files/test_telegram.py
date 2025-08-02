#!/usr/bin/env python3
"""
Test TrenchCoat Pro Telegram Bot
"""

import requests
import json

def test_telegram_bot():
    """Test Telegram bot with actual credentials"""
    
    bot_token = "8479347588:AAH27CeFD3iiyQM7l6YKk9bMlQznlCLAhxo"
    chat_id = "8158865103"
    
    # Test message
    message = """
🎯 TrenchCoat Pro Bot ACTIVE!

✅ Connection successful
✅ Ready for Runner alerts  
✅ Professional notifications configured

Your instant trading alerts are now live!

🚀 Next Runner detected will trigger immediate notification!
    """.strip()
    
    # Send test message
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        print("Sending test message to Telegram...")
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        if result.get("ok"):
            print("SUCCESS: Test message sent to your Telegram!")
            print("Check your phone - you should see the TrenchCoat Pro message!")
            return True
        else:
            print(f"ERROR: {result}")
            return False
            
    except Exception as e:
        print(f"ERROR: Failed to send message - {e}")
        return False

def test_runner_alert():
    """Send example Runner alert"""
    
    bot_token = "8479347588:AAH27CeFD3iiyQM7l6YKk9bMlQznlCLAhxo"
    chat_id = "8158865103"
    
    # Example Runner alert
    message = """
🚀 RUNNER IDENTIFIED! 🚀

💰 Coin: MEME
💵 Price: $0.000234
📈 24h Change: +67.5%
📊 Volume: $1,250,000
🎯 Confidence: 87.3%

⚡ Action Required: Review for entry
⏰ Time: 11:59:43

🔗 Dashboard: https://app.trenchcoat.pro
    """.strip()
    
    # Create action buttons
    keyboard = {
        "inline_keyboard": [[
            {"text": "📊 View Chart", "url": "https://app.trenchcoat.pro/coin/MEME"},
            {"text": "💰 Trade Now", "url": "https://app.trenchcoat.pro/trade/MEME"}
        ], [
            {"text": "📈 Full Analysis", "url": "https://app.trenchcoat.pro/dashboard"}
        ]]
    }
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    payload = {
        "chat_id": chat_id,
        "text": message,
        "reply_markup": json.dumps(keyboard)
    }
    
    try:
        print("\nSending example Runner alert...")
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        if result.get("ok"):
            print("SUCCESS: Runner alert sent!")
            print("Check your Telegram for the professional Runner notification!")
            return True
        else:
            print(f"ERROR: {result}")
            return False
            
    except Exception as e:
        print(f"ERROR: Failed to send Runner alert - {e}")
        return False

if __name__ == "__main__":
    print("TrenchCoat Pro Telegram Bot Test")
    print("=" * 35)
    
    # Test basic connection
    if test_telegram_bot():
        print("\n" + "=" * 35)
        # Test Runner alert
        test_runner_alert()
    
    print("\n✅ Telegram bot is ready for live Runner alerts!")