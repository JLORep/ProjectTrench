#!/usr/bin/env python3
"""
Add new Telegram contact to signal sharing
"""

from multi_telegram_bot import MultiTelegramBot

def add_chris_to_signals():
    """Add Chris G to signal recipients"""
    
    bot_token = "8479347588:AAH27CeFD3iiyQM7l6YKk9bMlQznlCLAhxo"
    bot = MultiTelegramBot(bot_token)
    
    # Add Chris G (could be Bravo or Spangle)
    bot.add_recipient('chris', '1645467117')
    
    print("Added Chris G to signal recipients!")
    print("Chat ID: 1645467117")
    
    # Test sending a welcome message
    test_message = """
🎯 Welcome to TrenchCoat Pro Signals!

You've been added to our exclusive Runner alert system.

🚀 You'll now receive:
• High-confidence trading signals
• Real-time Runner detection alerts  
• AI-powered market analysis
• Professional trading insights

Next Runner detected will trigger an instant alert!

Powered by TrenchCoat Pro AI 🤖
    """.strip()
    
    success = bot.send_message('1645467117', test_message)
    
    if success:
        print("Welcome message sent successfully!")
    else:
        print("Failed to send welcome message")
    
    return bot

if __name__ == "__main__":
    add_chris_to_signals()