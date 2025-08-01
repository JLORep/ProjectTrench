#!/usr/bin/env python3
"""
Check for new contacts who have messaged TrenchCoat Pro bot
"""

import requests
import json

def check_new_contacts():
    """Check who has messaged the bot"""
    
    bot_token = "8479347588:AAH27CeFD3iiyQM7l6YKk9bMlQznlCLAhxo"
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        updates = result.get("result", [])
        
        print("TrenchCoat Pro Bot - Contact Check")
        print("=" * 35)
        
        if not updates:
            print("No messages yet. Bravo and Spangle need to:")
            print("1. Go to: https://t.me/trenchcoat_pro_bot")
            print("2. Click START")
            print("3. Send any message")
            return
            
        # Extract unique contacts
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
                
        print(f"Found {len(contacts)} contacts:")
        print()
        
        known_james = "8158865103"
        
        for chat_id, name in contacts.items():
            if chat_id == known_james:
                print(f"James (You): {chat_id}")
            else:
                print(f"NEW {name}: {chat_id}")
                print(f"   -> Could be Bravo or Spangle!")
                
        print()
        print("To add them to signal sharing:")
        print("bot.add_recipient('bravo', 'THEIR_CHAT_ID')")
        print("bot.add_recipient('spangle', 'THEIR_CHAT_ID')")
        
    except Exception as e:
        print(f"Error checking contacts: {e}")

if __name__ == "__main__":
    check_new_contacts()