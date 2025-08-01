#!/usr/bin/env python3
"""
TrenchCoat Pro - Webhook Configuration Manager
Manages Discord webhook URLs for different channels
"""

import json
import requests
from typing import Dict
from pathlib import Path

class WebhookConfigManager:
    """Manages webhook configurations for Discord channels"""
    
    def __init__(self):
        self.config_file = Path.cwd() / "webhook_config.json"
        
        # Current webhook assignments (known working webhooks)
        self.webhooks = {
            "overview": "https://discord.com/api/webhooks/1400497302241677383/Im9oyVehkH6zhsc5w4mt4KHQvgSR2qfMPD-k6lTR-X0XQWT3eLV_IJM2-MqQNM6dPAzM",
            "dev-blog": "https://discord.com/api/webhooks/1400491407550058610/Q59NIxt5lSvFgpwckXOv_P9TF8uWjudOTJxEw5hZ3fL61Dg2-WgSwrpIb110UiG4Z1f7",
            
            # Placeholder webhooks - NEED TO BE CREATED IN DISCORD
            "announcements": "[NEEDS_WEBHOOK]",
            "documentation": "[NEEDS_WEBHOOK]",
            "bug-reports": "[NEEDS_WEBHOOK]", 
            "system-updates": "[NEEDS_WEBHOOK]",
            "testing": "[NEEDS_WEBHOOK]",
            "signals": "[NEEDS_WEBHOOK]",
            "analytics": "[NEEDS_WEBHOOK]",
            "live-trades": "[NEEDS_WEBHOOK]",
            "performance": "[NEEDS_WEBHOOK]"
        }
        
        self.channel_purposes = {
            "overview": "Project mission, feature status, and high-level updates",
            "dev-blog": "Development progress, feature development, and technical updates",
            "announcements": "Major releases, important updates, and official communications",
            "documentation": "Links to guides, API docs, tutorials, and help resources",
            "bug-reports": "Bug tracking, issue reports, and resolution updates",
            "system-updates": "Library updates, system maintenance, and infrastructure changes",
            "testing": "Testing results, performance metrics, and quality assurance",
            "signals": "Live trading signals, high-confidence opportunities",
            "analytics": "Market analysis, performance reports, and trading insights",
            "live-trades": "Real-time trade execution, P&L updates, position tracking",
            "performance": "Trading performance metrics, success rates, and statistics"
        }
        
        self.save_config()
    
    def save_config(self):
        """Save webhook configuration to file"""
        config = {
            "webhooks": self.webhooks,
            "channel_purposes": self.channel_purposes,
            "setup_instructions": {
                "step_1": "Create Discord channels as specified in DISCORD_SERVER_STRUCTURE.md",
                "step_2": "For each channel, go to Settings > Integrations > Webhooks",
                "step_3": "Create new webhook with name 'TrenchCoat Pro - [Channel Name]'",
                "step_4": "Copy webhook URL and update this config file",
                "step_5": "Run test_webhooks() to verify all webhooks work"
            }
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def load_config(self) -> Dict:
        """Load webhook configuration from file"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {}
    
    def get_webhook_url(self, channel: str) -> str:
        """Get webhook URL for specific channel"""
        return self.webhooks.get(channel, "[WEBHOOK_NOT_CONFIGURED]")
    
    def update_webhook(self, channel: str, webhook_url: str):
        """Update webhook URL for a channel"""
        if channel in self.webhooks:
            self.webhooks[channel] = webhook_url
            self.save_config()
            print(f"Updated webhook for #{channel}")
            return True
        else:
            print(f"Unknown channel: {channel}")
            return False
    
    def test_webhook(self, channel: str) -> bool:
        """Test a specific webhook"""
        webhook_url = self.get_webhook_url(channel)
        
        if webhook_url.startswith("["):
            print(f"#{channel}: Webhook not configured")
            return False
        
        test_message = f"""**Webhook Test - #{channel}**

This is a test message to verify the webhook is working correctly.

**Channel Purpose:** {self.channel_purposes.get(channel, 'Unknown')}

**Test Status:** Connection Successful
**Timestamp:** {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

#WebhookTest #TrenchCoatPro"""
        
        try:
            payload = {
                "content": test_message,
                "username": f"TrenchCoat Pro - {channel.title()}",
                "avatar_url": "https://via.placeholder.com/64x64/10b981/ffffff?text=TC"
            }
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            
            if response.status_code == 204:
                print(f"#{channel}: Webhook test successful")
                return True
            else:
                print(f"#{channel}: Webhook test failed ({response.status_code})")
                return False
                
        except Exception as e:
            print(f"#{channel}: Webhook test error - {e}")
            return False
    
    def test_all_webhooks(self):
        """Test all configured webhooks"""
        print("Testing all Discord webhooks...")
        print("=" * 50)
        
        working_webhooks = 0
        total_webhooks = len(self.webhooks)
        
        for channel in self.webhooks.keys():
            if self.test_webhook(channel):
                working_webhooks += 1
            
            # Wait between tests to avoid rate limiting
            import time
            time.sleep(2)
        
        print("\n" + "=" * 50)
        print(f"Test Results: {working_webhooks}/{total_webhooks} webhooks working")
        
        if working_webhooks < total_webhooks:
            print(f"\n{total_webhooks - working_webhooks} webhooks need to be configured")
            print("Please create the missing webhooks in Discord and update the URLs")
        else:
            print("\nAll webhooks are working correctly!")
    
    def generate_webhook_creation_guide(self):
        """Generate step-by-step webhook creation guide"""
        
        guide = """
# Discord Webhook Setup Guide

## Channels Needing Webhooks:

"""
        
        for channel, webhook_url in self.webhooks.items():
            status = "CONFIGURED" if not webhook_url.startswith("[") else "NEEDS WEBHOOK"
            purpose = self.channel_purposes.get(channel, "Unknown purpose")
            
            guide += f"""
### #{channel}
- **Status:** {status}
- **Purpose:** {purpose}
- **Webhook URL:** `{webhook_url}`

"""
        
        guide += """
## Step-by-Step Instructions:

1. **Go to Discord Server**
   - Open your TrenchCoat Pro Discord server
   - Make sure you have Administrator permissions

2. **For Each Channel Above:**
   - Right-click on the channel name
   - Select "Edit Channel"
   - Go to "Integrations" tab
   - Click "Webhooks" section

3. **Create New Webhook:**
   - Click "New Webhook"
   - Set name: "TrenchCoat Pro - [Channel Name]"
   - Copy the webhook URL
   - Save changes

4. **Update Configuration:**
   - Run the webhook config manager
   - Update each webhook URL
   - Test the webhooks

5. **Verify Setup:**
   - Run test_all_webhooks() to confirm all work
   - Check that messages appear in correct channels

## Important Notes:

WARNING: Keep webhook URLs secure - They allow posting to your channels
WARNING: Test webhooks before going live - Verify messages appear correctly
WARNING: Use different webhooks for each channel - This prevents message mixing

## Current Issue:

The system is currently using the same webhook URL for multiple channels, 
which causes all messages to go to the same place. Each channel needs its 
own unique webhook URL.

## After Setup:

Once all webhooks are configured and tested, the TrenchCoat Pro system will:
- Send overview updates to #overview
- Send development updates to #dev-blog  
- Send trading signals to #signals
- Send system updates to #system-updates
- And so on...

This ensures proper organization and prevents message mixing.
"""
        
        with open("WEBHOOK_SETUP_GUIDE.md", 'w') as f:
            f.write(guide)
        
        print("Webhook setup guide generated: WEBHOOK_SETUP_GUIDE.md")
        return guide
    
    def send_to_correct_channel(self, channel: str, message: str, username: str = None):
        """Send message to the correct channel webhook"""
        
        webhook_url = self.get_webhook_url(channel)
        
        if webhook_url.startswith("["):
            print(f"Cannot send to #{channel}: Webhook not configured")
            return False
        
        try:
            payload = {
                "content": message,
                "username": username or f"TrenchCoat Pro - {channel.title()}"
            }
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            
            if response.status_code == 204:
                print(f"Message sent to #{channel}")
                return True
            else:
                print(f"Failed to send to #{channel}: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Error sending to #{channel}: {e}")
            return False

def main():
    """Main function for webhook configuration management"""
    
    webhook_manager = WebhookConfigManager()
    
    print("TrenchCoat Pro Webhook Configuration Manager")
    print("=" * 50)
    
    print("1. Test all webhooks")
    print("2. Update webhook URL")
    print("3. Generate setup guide")
    print("4. Send test message")
    
    choice = input("\nSelect option (1-4): ").strip()
    
    if choice == "1":
        webhook_manager.test_all_webhooks()
        
    elif choice == "2":
        print("\nAvailable channels:")
        for channel in webhook_manager.webhooks.keys():
            status = "OK" if not webhook_manager.webhooks[channel].startswith("[") else "NEEDS_WEBHOOK"
            print(f"  {status} {channel}")
        
        channel = input("\nEnter channel name: ").strip()
        webhook_url = input("Enter webhook URL: ").strip()
        
        webhook_manager.update_webhook(channel, webhook_url)
        
    elif choice == "3":
        webhook_manager.generate_webhook_creation_guide()
        
    elif choice == "4":
        channel = input("Enter channel name: ").strip()
        message = input("Enter test message: ").strip()
        
        webhook_manager.send_to_correct_channel(channel, message)

if __name__ == "__main__":
    main()