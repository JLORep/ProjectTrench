#!/usr/bin/env python3
"""
TrenchCoat Pro - WhatsApp Integration
Send Runner alerts to WhatsApp groups and contacts
"""

import requests
import json
from datetime import datetime
import logging

class WhatsAppBot:
    """TrenchCoat Pro WhatsApp notification system"""
    
    def __init__(self):
        # WhatsApp API options (choose one)
        self.api_provider = None  # Will be set based on chosen service
        self.api_key = None
        self.phone_number = None  # Your WhatsApp Business number
        
        # Group and contact management
        self.contacts = {
            "james": "+44_YOUR_NUMBER",  # Your number
            "bravo": None,  # Will add when provided
            "spangle": None  # Will add when provided
        }
        
        self.groups = {
            "trenchcoat_signals": None,  # Group chat ID
            "trading_team": None  # Additional group if needed
        }
        
    def setup_twilio_whatsapp(self, account_sid: str, auth_token: str, from_number: str):
        """Setup Twilio WhatsApp Business API"""
        self.api_provider = "twilio"
        self.twilio_config = {
            "account_sid": account_sid,
            "auth_token": auth_token,
            "from_number": from_number  # whatsapp:+14155238886 (Twilio sandbox)
        }
        
    def setup_360dialog(self, api_key: str, channel_id: str):
        """Setup 360Dialog WhatsApp Business API"""
        self.api_provider = "360dialog"
        self.dialog_config = {
            "api_key": api_key,
            "channel_id": channel_id,
            "base_url": "https://waba.360dialog.io"
        }
        
    def setup_whatsapp_cloud_api(self, access_token: str, phone_number_id: str):
        """Setup Meta WhatsApp Cloud API (Official)"""
        self.api_provider = "meta"
        self.meta_config = {
            "access_token": access_token,
            "phone_number_id": phone_number_id,
            "base_url": "https://graph.facebook.com/v18.0"
        }
        
    def add_contact(self, name: str, phone_number: str):
        """Add contact for notifications"""
        # Format: +44xxxxxxxxxx or +1xxxxxxxxxx
        self.contacts[name] = phone_number
        print(f"Added {name} to WhatsApp notifications: {phone_number}")
        
    def add_group(self, group_name: str, group_id: str):
        """Add WhatsApp group for notifications"""
        self.groups[group_name] = group_id
        print(f"Added WhatsApp group: {group_name}")
        
    def send_runner_alert_to_all(self, coin_data: dict) -> dict:
        """Send Runner alert to all WhatsApp contacts and groups"""
        
        symbol = coin_data.get('symbol', 'Unknown')
        price = coin_data.get('current_price', 0)
        change_24h = coin_data.get('price_change_24h', 0)
        volume = coin_data.get('volume_24h', 0)
        confidence = coin_data.get('runner_confidence', 0)
        
        # Format WhatsApp message (no rich formatting)
        message = f"""🚀 *TRENCHCOAT PRO SIGNAL* 🚀

💰 *Coin:* {symbol}
💵 *Price:* ${price:.6f}
📈 *24h Change:* {change_24h:+.2f}%
📊 *Volume:* ${volume:,.0f}
🎯 *Confidence:* {confidence:.1f}%

⚡ *RUNNER IDENTIFIED*
⏰ {datetime.now().strftime('%H:%M:%S')}

📱 Dashboard: https://demo.trenchcoat.pro

_Signal by TrenchCoat Pro AI_"""
        
        results = {}
        
        # Send to individual contacts
        for name, phone in self.contacts.items():
            if phone:
                success = self.send_message(phone, message)
                results[f"contact_{name}"] = success
                print(f"WhatsApp to {name}: {'✅' if success else '❌'}")
                
        # Send to groups
        for group_name, group_id in self.groups.items():
            if group_id:
                success = self.send_message(group_id, message)
                results[f"group_{group_name}"] = success
                print(f"WhatsApp group {group_name}: {'✅' if success else '❌'}")
                
        return results
        
    def send_message(self, recipient: str, message: str) -> bool:
        """Send WhatsApp message based on configured provider"""
        
        if self.api_provider == "twilio":
            return self._send_twilio_message(recipient, message)
        elif self.api_provider == "360dialog":
            return self._send_360dialog_message(recipient, message)
        elif self.api_provider == "meta":
            return self._send_meta_message(recipient, message)
        else:
            print("No WhatsApp API provider configured")
            return False
            
    def _send_twilio_message(self, recipient: str, message: str) -> bool:
        """Send via Twilio WhatsApp API"""
        
        try:
            import base64
            
            # Twilio credentials
            account_sid = self.twilio_config["account_sid"]
            auth_token = self.twilio_config["auth_token"]
            from_number = self.twilio_config["from_number"]
            
            # Prepare recipient number
            to_number = f"whatsapp:{recipient}"
            
            # API call
            url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
            
            auth_string = f"{account_sid}:{auth_token}"
            auth_bytes = auth_string.encode('ascii')
            auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
            
            headers = {
                "Authorization": f"Basic {auth_b64}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            data = {
                "From": from_number,
                "To": to_number,
                "Body": message
            }
            
            response = requests.post(url, headers=headers, data=data, timeout=10)
            return response.status_code == 201
            
        except Exception as e:
            logging.error(f"Twilio WhatsApp error: {e}")
            return False
            
    def _send_360dialog_message(self, recipient: str, message: str) -> bool:
        """Send via 360Dialog WhatsApp API"""
        
        try:
            url = f"{self.dialog_config['base_url']}/v1/messages"
            
            headers = {
                "D360-API-KEY": self.dialog_config["api_key"],
                "Content-Type": "application/json"
            }
            
            payload = {
                "to": recipient,
                "type": "text",
                "text": {
                    "body": message
                }
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            logging.error(f"360Dialog WhatsApp error: {e}")
            return False
            
    def _send_meta_message(self, recipient: str, message: str) -> bool:
        """Send via Meta WhatsApp Cloud API"""
        
        try:
            phone_number_id = self.meta_config["phone_number_id"]
            url = f"{self.meta_config['base_url']}/{phone_number_id}/messages"
            
            headers = {
                "Authorization": f"Bearer {self.meta_config['access_token']}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "messaging_product": "whatsapp",
                "to": recipient,
                "type": "text",
                "text": {
                    "body": message
                }
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            logging.error(f"Meta WhatsApp error: {e}")
            return False
            
    def send_test_message(self, recipient: str = None):
        """Send test message to verify WhatsApp integration"""
        
        test_message = f"""🎯 *TrenchCoat Pro WhatsApp Test*

✅ WhatsApp integration is working!
✅ Ready for Runner alerts
✅ Professional trading signals

Your instant WhatsApp notifications are now active!

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

_Powered by TrenchCoat Pro AI_ 🚀"""
        
        if recipient:
            return self.send_message(recipient, test_message)
        else:
            # Send to all configured contacts/groups
            results = {}
            for name, phone in self.contacts.items():
                if phone:
                    results[name] = self.send_message(phone, test_message)
            return results

def create_whatsapp_group_guide():
    """Generate guide for creating WhatsApp groups"""
    
    guide = """
# 📱 WhatsApp Group Setup Guide

## 🎯 **CREATE TRENCHCOAT PRO SIGNALS GROUP**

### **Step 1: Create Group**
1. Open WhatsApp
2. Tap "New Group" 
3. Add contacts: You, Bravo, Spangle
4. Group name: "TrenchCoat Pro Signals"
5. Description: "Professional crypto trading signals powered by AI"

### **Step 2: Group Settings**
- **Admin only messages:** Enable (only you can send signals)
- **Group info:** Add TrenchCoat Pro description
- **Group icon:** Use TrenchCoat Pro logo if available

### **Step 3: Get Group ID**
For WhatsApp Business API, you'll need the group chat ID.
This is typically provided by your WhatsApp Business API provider.

### **Step 4: Invite Message**
Send this to Bravo and Spangle:

```
🎯 Join TrenchCoat Pro Signals WhatsApp Group!

Get instant Runner alerts directly to your phone:
• High-confidence trading signals
• Real-time price analysis  
• AI-powered market insights
• Professional trading community

Powered by TrenchCoat Pro 🚀

[Group Invite Link]
```

## 📊 **SIGNAL FORMAT**
WhatsApp signals will look like:

```
🚀 TRENCHCOAT PRO SIGNAL 🚀

💰 Coin: PEPE
💵 Price: $0.00001234
📈 24h Change: +67.5%
📊 Volume: $2,500,000
🎯 Confidence: 92.1%

⚡ RUNNER IDENTIFIED
⏰ 14:23:47

📱 Dashboard: https://demo.trenchcoat.pro

Signal by TrenchCoat Pro AI
```

## 🔧 **API SETUP OPTIONS**

### **Option 1: Twilio (Easiest)**
- Cost: $0.005 per message
- Setup: 15 minutes
- Sandbox available for testing

### **Option 2: Meta WhatsApp Cloud API (Official)**
- Cost: $0.005-0.009 per message  
- Setup: 30 minutes
- Requires business verification

### **Option 3: 360Dialog**
- Cost: €0.009 per message
- Setup: 20 minutes
- European provider

**Recommended: Start with Twilio for immediate setup**
    """
    
    return guide

# Usage example
if __name__ == "__main__":
    print("TrenchCoat Pro WhatsApp Integration")
    print("=" * 40)
    
    # Create WhatsApp bot instance
    whatsapp_bot = WhatsAppBot()
    
    print("\n📱 WhatsApp Features:")
    print("• Send Runner alerts to individual contacts")
    print("• Send alerts to WhatsApp groups") 
    print("• Support for multiple API providers")
    print("• Professional message formatting")
    print("• Group and contact management")
    
    print("\n🔧 Setup Required:")
    print("1. Choose API provider (Twilio recommended)")
    print("2. Get API credentials") 
    print("3. Add phone numbers/group IDs")
    print("4. Test integration")
    
    print("\n📋 Group Setup Guide saved to file")
    
    # Save group setup guide
    with open("whatsapp_group_guide.md", "w", encoding="utf-8") as f:
        f.write(create_whatsapp_group_guide())
    
    print("\n🚀 WhatsApp integration ready for configuration!")